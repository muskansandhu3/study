"""
Gradio Chat Interface with multimodal moderation.
"""
import os
import uuid
import asyncio
import gradio as gr
from typing import List, Tuple, Optional
from agents import moderate_text, moderate_image, moderate_audio, moderate_video, customer_agent
from moderation_types import ModerationResult
from tracing import get_tracer

# Get tracer for observability
tracer = get_tracer()


# Global conversation state
conversations = {}


async def moderate_content(message: str, files: Optional[List[str]] = None, session_id: str = None) -> Tuple[bool, str]:
    """
    Moderate text message and any attached files.
    
    Args:
        message: Text message to moderate
        files: List of file paths (if any)
        session_id: Session identifier for tracing
        
    Returns:
        Tuple of (is_flagged, flagged_reason)
    """
    with tracer.start_as_current_span("moderate_text") as span:
        if session_id:
            span.set_attribute("session.id", session_id)
        
        # Moderate text message
        text_result = await moderate_text(message)
        
        if text_result.is_flagged():
            flags = []
            if text_result.contains_pii:
                flags.append("PII")
            if text_result.is_unfriendly:
                flags.append("unfriendly")
            if text_result.is_unprofessional:
                flags.append("unprofessional")
            
            reason = f"Message flagged: {', '.join(flags)}. {text_result.rationale}"
            return True, reason
        
        # Moderate attached files if any
        if files:
            for file_path in files:
                file_ext = file_path.lower().split('.')[-1]
                
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                
                # Determine moderation type based on file extension
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    result = await moderate_image(file_bytes)
                elif file_ext in ['mp4', 'avi', 'mov', 'webm']:
                    result = await moderate_video(file_bytes)
                elif file_ext in ['wav', 'mp3', 'ogg', 'm4a']:
                    result = await moderate_audio(file_bytes)
                else:
                    continue
                
                if result.is_flagged():
                    flags = []
                    if result.contains_pii:
                        flags.append("PII")
                    if result.is_unfriendly:
                        flags.append("disturbing content")
                    if result.is_unprofessional:
                        flags.append("unprofessional")
                    
                    reason = f"File flagged: {', '.join(flags)}. {result.rationale}"
                    return True, reason
        
        return False, ""


async def chat_function(message: dict, history: List, session_id: str = None):
    """
    Process chat messages with moderation and customer agent responses.

    Args:
        message: Dictionary containing 'text' and optional 'files'
        history: Conversation history
        session_id: Session identifier for this conversation

    Returns:
        Updated history
    """
    if history is None:
        history = []

    if session_id is None:
        session_id = str(uuid.uuid4())

    with tracer.start_as_current_span("chat_turn") as span:
        span.set_attribute("session.id", session_id)

        # Extract message components
        text = message.get("text", "")
        files = message.get("files", [])
        user_display = text if text else "[Attachment]"

        # Moderate the message
        is_flagged, flag_reason = await moderate_content(text, files, session_id)
        span.set_attribute("moderation.flagged", is_flagged)

        if is_flagged:
            warning_msg = f"Moderation Alert: {flag_reason}"
            history.append({"role": "user", "content": user_display})
            history.append({"role": "assistant", "content": warning_msg})
            return history

        history.append({"role": "user", "content": user_display})

        with tracer.start_as_current_span("customer_response"):
            conv_context = "Conversation so far:\n"
            for h in history:
                role = h.get("role")
                content = h.get("content", "")
                if role == "user" and content:
                    conv_context += f"AGENT: {content}\n"
                if role == "assistant" and content:
                    conv_context += f"CUSTOMER: {content}\n"

            customer_response = await customer_agent.run(conv_context)
            history.append({"role": "assistant", "content": customer_response})

        return history

def create_interface():
    """Create and configure the Gradio ChatInterface."""
    
    # Create session storage
    session_state = {}
    
    def chat_wrapper(message, history):
        """Synchronous wrapper for async chat function."""
        # Get or create session ID
        if 'session_id' not in session_state:
            session_state['session_id'] = str(uuid.uuid4())
        
        session_id = session_state['session_id']
        
        with tracer.start_as_current_span("conversation") as span:
            span.set_attribute("session.id", session_id)
            
            # Run async chat function
            result = asyncio.run(chat_function(message, history, session_id))
            return result
    
    def end_conversation():
        """End the current conversation and start a new one."""
        if 'session_id' in session_state:
            old_session = session_state['session_id']
            with tracer.start_as_current_span("conversation_end") as span:
                span.set_attribute("session.id", old_session)
                span.set_attribute("event", "conversation_ended")
        
        # Generate new session ID
        session_state['session_id'] = str(uuid.uuid4())
        return []
    
    def submit_feedback(feedback_text):
        """Submit user feedback."""
        if 'session_id' in session_state:
            with tracer.start_as_current_span("feedback") as span:
                span.set_attribute("session.id", session_state['session_id'])
                span.set_attribute("feedback.content", feedback_text)
                span.set_attribute("feedback.type", "user_feedback")
        
        return "Thank you for your feedback!"
    
    # Create the chat interface
    with gr.Blocks(title="ACME Customer Service - Moderated Chat") as demo:
        gr.Markdown("# 🛡️ ACME Customer Service - Moderated Chat")
        gr.Markdown("Customer service chat with real-time content moderation for safety and professionalism.")
        
        chatbot = gr.Chatbot(label="Conversation", height=500)
        
        with gr.Row():
            with gr.Column(scale=4):
                chat_input = gr.MultimodalTextbox(
                    file_types=["image", "audio", "video"],
                    placeholder="Type your message or attach files...",
                    show_label=False
                )
            
        with gr.Row():
            send_btn = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")
            end_btn = gr.Button("End Conversation", variant="secondary")
        
        gr.Markdown("### Feedback")
        with gr.Row():
            feedback_input = gr.Textbox(
                placeholder="Share your feedback about the moderation system...",
                label="Feedback",
                lines=2
            )
            feedback_btn = gr.Button("Submit Feedback")
        
        feedback_output = gr.Textbox(label="", visible=True, interactive=False)
        
        # Event handlers
        def handle_send(message, history):
            history = history or []
            if message:
                return chat_wrapper(message, history)
            return history
        
        send_btn.click(
            handle_send,
            inputs=[chat_input, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: None,
            outputs=[chat_input]
        )
        
        chat_input.submit(
            handle_send,
            inputs=[chat_input, chatbot],
            outputs=[chatbot]
        ).then(
            lambda: None,
            outputs=[chat_input]
        )
        
        clear_btn.click(lambda: [], outputs=[chatbot])
        end_btn.click(end_conversation, outputs=[chatbot])
        feedback_btn.click(submit_feedback, inputs=[feedback_input], outputs=[feedback_output])
    
    return demo


def main():
    """Launch the Gradio app."""
    demo = create_interface()
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    demo.launch(server_name=server_name, server_port=server_port)


if __name__ == "__main__":
    main()


