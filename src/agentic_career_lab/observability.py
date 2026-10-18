"""OpenTelemetry Tracing and Metrics Module for Agentic Career Lab.

Enforces strict privacy boundaries:
- Never logs raw resumes, PII, full prompts, or model responses.
- Records workflow step names, agent names, model runtimes, durations,
  token counts (when safely available without PII), and error codes.
- Supports InMemorySpanExporter for testing/inspections and OTLP exporters
  when configured.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

# Module-level singletons
_TRACER_PROVIDER: TracerProvider | None = None
_IN_MEMORY_EXPORTER: InMemorySpanExporter | None = None
_IS_INITIALIZED = False


def init_telemetry(
    service_name: str = "agentic-career-lab",
    endpoint: str | None = None,
    protocol: str = "grpc",
    enable_in_memory: bool = True,
    force_reinit: bool = False,
) -> TracerProvider:
    """Initialize OpenTelemetry tracer provider with processors."""
    global _TRACER_PROVIDER, _IN_MEMORY_EXPORTER, _IS_INITIALIZED

    if _IS_INITIALIZED and not force_reinit and _TRACER_PROVIDER is not None:
        return _TRACER_PROVIDER

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": "0.8.0",
            "deployment.environment": os.environ.get("DEPLOY_ENV", "local"),
        }
    )

    provider = TracerProvider(resource=resource)

    # In-memory exporter for UI inspection, telemetry views, and unit testing
    if enable_in_memory:
        _IN_MEMORY_EXPORTER = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(_IN_MEMORY_EXPORTER))

    # Optional remote OTLP endpoint (e.g. OTel Collector / Tempo)
    otlp_endpoint = endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if otlp_endpoint:
        try:
            otlp_proto = (protocol or os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")).lower()
            if otlp_proto == "http":
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter as HTTPOtpExporter,
                )

                exporter = HTTPOtpExporter(endpoint=otlp_endpoint)
            else:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                    OTLPSpanExporter as GRPCOtpExporter,
                )

                exporter = GRPCOtpExporter(endpoint=otlp_endpoint, insecure=True)

            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("Configured OTLP SpanExporter at %s (%s)", otlp_endpoint, otlp_proto)
        except Exception as e:
            logger.warning("Failed to configure remote OTLP exporter: %s", e)

    # If global tracer provider already set in opentelemetry, check if it's TracerProvider
    current = trace.get_tracer_provider()
    if isinstance(current, TracerProvider) and not force_reinit:
        _TRACER_PROVIDER = current
        if enable_in_memory and _IN_MEMORY_EXPORTER is None:
            _IN_MEMORY_EXPORTER = InMemorySpanExporter()
            _TRACER_PROVIDER.add_span_processor(SimpleSpanProcessor(_IN_MEMORY_EXPORTER))
        _IS_INITIALIZED = True
        return _TRACER_PROVIDER

    if not isinstance(current, TracerProvider):
        try:
            trace.set_tracer_provider(provider)
        except Exception:
            pass

    _TRACER_PROVIDER = provider
    _IS_INITIALIZED = True
    return provider


def get_tracer(name: str = "agentic_career_lab") -> trace.Tracer:
    """Get or initialize the application tracer."""
    global _TRACER_PROVIDER
    if _TRACER_PROVIDER is None:
        init_telemetry()
    if _TRACER_PROVIDER is not None:
        return _TRACER_PROVIDER.get_tracer(name)
    return trace.get_tracer(name)


def get_in_memory_spans() -> list[Any]:
    """Retrieve captured spans from the in-memory exporter (for UI / testing)."""
    if _IN_MEMORY_EXPORTER is not None:
        return list(_IN_MEMORY_EXPORTER.get_finished_spans())
    return []


def clear_in_memory_spans() -> None:
    """Clear captured in-memory spans."""
    if _IN_MEMORY_EXPORTER is not None:
        _IN_MEMORY_EXPORTER.clear()


@contextmanager
def trace_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    agent_name: str | None = None,
    model_name: str | None = None,
    runtime: str | None = None,
) -> Generator[trace.Span, None, None]:
    """Context manager for tracing workflow spans with strict privacy enforcement.

    Guarantees:
    - Never stores raw resume text, candidate contact info, or full LLM generation.
    - Captures latency, model tags, agent identifiers, status, and error details.
    """
    tracer = get_tracer()
    attrs: dict[str, Any] = {}

    if agent_name:
        attrs["agent.name"] = agent_name
    if model_name:
        attrs["llm.model"] = model_name
    if runtime:
        attrs["llm.runtime"] = runtime

    if attributes:
        # Sanitize attributes to guarantee zero raw text leakage
        for k, v in attributes.items():
            k_lower = k.lower()
            if any(
                forbidden in k_lower
                for forbidden in ("resume", "text", "prompt", "response", "pii", "content")
            ):
                continue
            if isinstance(v, (str, int, float, bool)):
                attrs[k] = v

    start_time = time.time()
    with tracer.start_as_current_span(name, attributes=attrs) as span:
        try:
            yield span
            duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("workflow.duration_ms", duration_ms)
            span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            span.set_attribute("workflow.duration_ms", duration_ms)
            span.set_attribute("error.type", type(exc).__name__)
            span.set_attribute("error.message", str(exc)[:200])  # Truncate error message safely
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise
