"""
Unit tests for rca_graph.py

Purpose:
--------
These tests validate that normalized spans are correctly transformed
into a causal RCA graph.

This graph is the foundation for:
- root cause detection
- blast radius calculation
- automated incident explanations
"""

from rca_engine.rca_graph import RCAGraph
from rca_engine.trace_normalizer import NormalizedSpan


# -------------------------------------------------------------------
# Helper function to create spans correctly (CANONICAL)
# -------------------------------------------------------------------
def make_span(
    service,
    dependency=None,
    error=False,
    error_kind=None,
    incident_id=None,
):
    return NormalizedSpan(
        trace_id="trace-1",
        span_id=f"span-{service}",
        parent_span_id=None,
        service=service,
        operation="process",
        error=error,
        error_kind=error_kind,
        http_status=None,
        incident_id=incident_id,
        root_service=service if error_kind == "root" else None,
        parent_service=None,
        dependency=dependency,
    )


# -------------------------------------------------------------------
# Test 1: Graph with no failures
# -------------------------------------------------------------------
def test_rca_graph_no_failures():
    """
    Ensures that a healthy trace produces a graph with:
    - nodes
    - edges
    - no root cause
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span("service-b", dependency="service-c"),
        make_span("service-c"),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    summary = graph.summary()

    assert summary["root_cause"] is None
    assert len(summary["nodes"]) == 3
    assert len(summary["edges"]) == 2


# -------------------------------------------------------------------
# Test 2: Root failure in service-c
# -------------------------------------------------------------------
def test_rca_graph_root_failure():
    """
    Validates correct identification of root cause.

    Scenario:
    service-a -> service-b -> service-c (FAILS)
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span("service-b", dependency="service-c"),
        make_span(
            "service-c",
            error=True,
            error_kind="root",
            incident_id="incident-123",
        ),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    summary = graph.summary()

    assert summary["root_cause"] == "service-c"
    assert summary["incident_id"] == "incident-123"
    assert len(summary["nodes"]) == 3
    assert len(summary["edges"]) == 2


# -------------------------------------------------------------------
# Test 3: Propagated failure chain
# -------------------------------------------------------------------
def test_rca_graph_propagated_failure():
    """
    Validates propagation across services.

    Scenario:
    service-a (propagated)
      ↓
    service-b (propagated)
      ↓
    service-c (root)
    """

    spans = [
        make_span(
            "service-a",
            dependency="service-b",
            error=True,
            error_kind="propagated",
            incident_id="incident-999",
        ),
        make_span(
            "service-b",
            dependency="service-c",
            error=True,
            error_kind="propagated",
            incident_id="incident-999",
        ),
        make_span(
            "service-c",
            error=True,
            error_kind="root",
            incident_id="incident-999",
        ),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    summary = graph.summary()

    assert summary["root_cause"] == "service-c"
    assert summary["incident_id"] == "incident-999"
    assert len(summary["nodes"]) == 3
    assert len(summary["edges"]) == 2


# -------------------------------------------------------------------
# Test 4: Dependency edge correctness
# -------------------------------------------------------------------
def test_rca_graph_edges():
    """
    Ensures dependency edges are built correctly.
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span("service-b", dependency="service-c"),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    summary = graph.summary()

    edges = summary["edges"]

    assert {"from": "service-a", "to": "service-b", "type": "dependency"} in edges
    assert {"from": "service-b", "to": "service-c", "type": "dependency"} in edges

def test_blast_radius_no_root_cause():
    """
    If there is no root cause, blast radius should be zero.
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span("service-b", dependency="service-c"),
        make_span("service-c"),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    impact = graph.compute_blast_radius()

    assert impact["blast_radius"] == 0
    assert impact["affected_services"] == []

def test_blast_radius_single_root():
    """
    Root failure with no downstream impact.
    """

    spans = [
        make_span(
            "service-c",
            error=True,
            error_kind="root",
            incident_id="incident-1"
        )
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    impact = graph.compute_blast_radius()

    assert impact["blast_radius"] == 1
    assert impact["affected_services"] == ["service-c"]

def test_blast_radius_multiple_services():
    """
    Root failure propagates upstream through dependencies.
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span("service-b", dependency="service-c"),
        make_span(
            "service-c",
            error=True,
            error_kind="root",
            incident_id="incident-999"
        ),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    impact = graph.compute_blast_radius()

    assert impact["blast_radius"] == 3
    assert set(impact["affected_services"]) == {
        "service-a",
        "service-b",
        "service-c",
    }

def test_summary_includes_blast_radius():
    """
    Summary output must include blast radius and affected services.
    """

    spans = [
        make_span("service-a", dependency="service-b"),
        make_span(
            "service-b",
            error=True,
            error_kind="root",
            incident_id="incident-42"
        ),
    ]

    graph = RCAGraph()
    graph.build_from_spans(spans)
    summary = graph.summary()

    assert summary["root_cause"] == "service-b"
    assert summary["blast_radius"] == 2
    assert set(summary["affected_services"]) == {
        "service-b",
        "service-a",
    }
