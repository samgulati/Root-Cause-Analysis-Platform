from rca_engine.timeline_builder import IncidentTimeline
from rca_engine.trace_normalizer import NormalizedSpan


def make_span(service, start, error=False, error_kind=None):
    return NormalizedSpan(
        trace_id="trace-1",
        span_id=f"span-{service}",
        parent_span_id=None,
        service=service,
        operation="process",
        error=error,
        error_kind=error_kind,
        http_status=500 if error else None,
        start_time=start,
        end_time=start + 0.01
    )


def test_timeline_ordering():
    spans = [
        make_span("service-a", start=1.0, error=True, error_kind="propagated"),
        make_span("service-c", start=0.5, error=True, error_kind="root"),
        make_span("service-b", start=0.8, error=True, error_kind="propagated"),
    ]

    timeline = IncidentTimeline().build(spans)

    assert timeline[0]["service"] == "service-c"
    assert timeline[1]["service"] == "service-b"
    assert timeline[2]["service"] == "service-a"

    assert timeline[0]["offset_ms"] == 0
    assert timeline[1]["offset_ms"] > 0
