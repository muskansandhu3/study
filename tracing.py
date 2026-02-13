"""OpenTelemetry tracing setup for observability with Arize Phoenix."""
import os
import sys

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


# Initialize tracer provider
provider = TracerProvider()
trace.set_tracer_provider(provider)


def _is_truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# Disable noisy network exports during pytest by default.
enable_tracing = _is_truthy(os.getenv("PHOENIX_TRACING_ENABLED", "1"))
if "pytest" in sys.modules and not _is_truthy(os.getenv("PHOENIX_TRACING_IN_TESTS", "0")):
    enable_tracing = False

if enable_tracing:
    phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
    otlp_exporter = OTLPSpanExporter(endpoint=phoenix_endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

# Create tracer
tracer = trace.get_tracer(__name__)


def get_tracer():
    """Get the configured tracer instance."""
    return tracer