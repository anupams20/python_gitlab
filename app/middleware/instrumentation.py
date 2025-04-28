from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, ConcurrentMultiSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from prometheus_client import start_http_server

from app.core.config import settings
from app.db.session import engine_async


def add_instrumentation(app):
    # Enable Tracing and Spans
    resource = Resource(attributes={"service.name": settings.PROJECT_NAME})

    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_exporter = OTLPSpanExporter(endpoint=f"{settings.JAEGER_URL}")

    console_exporter = ConsoleSpanExporter()
    jaeger_span_processor = SimpleSpanProcessor(otlp_exporter)
    console_span_processor = SimpleSpanProcessor(console_exporter)
    concurrent_span_processor = ConcurrentMultiSpanProcessor()
    concurrent_span_processor.add_span_processor(console_span_processor)
    concurrent_span_processor.add_span_processor(jaeger_span_processor)

    tracer_provider.add_span_processor(concurrent_span_processor)

    ThreadingInstrumentor().instrument()

    # Setup Prometheus for monitoring the application
    start_http_server(settings.PROMETHEUS_COLLECTION_PORT)
    metric_reader = PrometheusMetricReader()
    metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))

    FastAPIInstrumentor.instrument_app(app)

    RequestsInstrumentor().instrument()

    SQLAlchemyInstrumentor().instrument(engine=engine_async.sync_engine, enable_commenter=True, commenter_options={})
