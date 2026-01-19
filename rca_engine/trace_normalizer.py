from typing import Dict, List, Optional


class NormalizedSpan:
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str],
        service: str,
        operation: str,
        error: bool,
        error_kind: Optional[str],
        http_status: Optional[int],

        # ---- Timing (Phase 6A) ----
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,

        # ---- RCA fields ----
        incident_id: Optional[str] = None,
        root_service: Optional[str] = None,
        parent_service: Optional[str] = None,
        dependency: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id

        self.service = service
        self.operation = operation

        self.error = error
        self.error_kind = error_kind
        self.http_status = http_status

        # Timing
        self.start_time = start_time
        self.end_time = end_time

        # RCA context
        self.incident_id = incident_id
        self.root_service = root_service
        self.parent_service = parent_service
        self.dependency = dependency

    def __repr__(self):
        return (
            f"NormalizedSpan(service={self.service}, "
            f"op={self.operation}, error={self.error}, "
            f"kind={self.error_kind}, incident={self.incident_id})"
        )


def normalize_span(raw_span: Dict) -> NormalizedSpan:
    """
    Converts a raw OTEL / Jaeger span into a NormalizedSpan
    compatible with RCA graph construction and timelines.
    """

    trace_id = raw_span.get("trace_id")
    span_id = raw_span.get("span_id")
    parent_span_id = raw_span.get("parent_span_id")

    # ---- Attributes ----
    attrs = raw_span.get("attributes", {})

    # ---- Service name (support BOTH OTEL styles) ----
    resource_attrs = raw_span.get("resource", {}).get("attributes", {})
    service = (
        attrs.get("service.name")
        or resource_attrs.get("service.name")
        or "unknown"
    )

    # ---- Operation name ----
    operation = raw_span.get("name", "unknown")

    # ---- HTTP status ----
    http_status = attrs.get("http.status_code")

    # ---- Error detection ----
    status = raw_span.get("status", {})
    status_code = status.get("code")

    error = False
    if status_code == "ERROR":
        error = True
    if attrs.get("rca.error") is True:
        error = True
    if isinstance(http_status, int) and http_status >= 500:
        error = True

    # ---- Error kind ----
    error_kind = None
    if error:
        error_kind = attrs.get("rca.error.kind", "unknown")

    # ---- RCA fields ----
    incident_id = attrs.get("rca.incident_id")
    root_service = attrs.get("rca.root_service")
    parent_service = attrs.get("rca.parent_service")
    dependency = attrs.get("rca.dependency.target")

    # ---- Timing (OTEL standard fields) ----
    start_time = raw_span.get("start_time", 0.0)
    end_time = raw_span.get("end_time", start_time)

    return NormalizedSpan(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        service=service,
        operation=operation,
        error=error,
        error_kind=error_kind,
        http_status=http_status,

        incident_id=incident_id,
        root_service=root_service,
        parent_service=parent_service,
        dependency=dependency,

        start_time=start_time,
        end_time=end_time,
    )


def normalize_trace(raw_spans: List[Dict]) -> List[NormalizedSpan]:
    """
    Normalize all spans of a single trace.
    """
    return [normalize_span(span) for span in raw_spans]
