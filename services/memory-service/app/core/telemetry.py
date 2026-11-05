from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
import structlog
from typing import Optional
from app.config import settings

logger = structlog.get_logger(__name__)

def setup_telemetry(app) -> None:
    """Configures OpenTelemetry tracer provider and Prometheus instrumentator."""
    try:
        resource = Resource.create({
            "service.name": settings.OTEL_SERVICE_NAME,
            "service.instance.id": f"{settings.APP_NAME}:{settings.PORT}",
            "deployment.environment": settings.APP_ENV
        })
        provider = TracerProvider(resource=resource)
        
        # OTLP exporter to local Collector (Jaeger)
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=True
        )
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(provider)
        
        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        logger.info("opentelemetry_initialized", endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
    except Exception as e:
        logger.warn("opentelemetry_init_warning", error=str(e))

    # Prometheus Metrics Instrumentator
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
        logger.info("prometheus_metrics_exposed", endpoint="/metrics")
    except Exception as e:
        logger.warn("prometheus_instrumentation_failed", error=str(e))

def get_current_trace_id() -> Optional[str]:
    """Retrieves current 32-character hex trace ID from active span context."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return f"{span.get_span_context().trace_id:032x}"
    return None

