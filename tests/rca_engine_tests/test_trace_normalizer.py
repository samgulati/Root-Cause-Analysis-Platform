"""
Unit tests for trace_normalizer.py

Purpose:
--------
These tests validate that raw OpenTelemetry spans from multiple services
(service-a, service-b, service-c) are correctly normalized into a
canonical RCA-friendly structure.
"""

import pytest
from rca_engine.trace_normalizer import normalize_span


# -------------------------------------------------------------------
# Test 1: Successful span normalization
# -------------------------------------------------------------------
def test_normalize_success_span():
    """
    Validates that a successful (non-error) span is normalized correctly.

    Why this test exists:
    ---------------------
    Most spans are successful.
    RCA systems must not mark these as incidents or errors.

    What it checks:
    ---------------
    - service name is extracted
    - error flag is False
    - incident_id is None
    - dependency information is preserved
    """

    raw_span = {
        "trace_id": "trace-123",
        "span_id": "span-abc",
        "attributes": {
            "service.name": "service-a",
            "rca.error": False,
            "rca.dependency.target": "service-b"
        }
    }

    normalized = normalize_span(raw_span)

    assert normalized.trace_id == "trace-123"
    assert normalized.span_id == "span-abc"
    assert normalized.service == "service-a"
    assert normalized.error is False
    assert normalized.incident_id is None
    assert normalized.dependency == "service-b"


# -------------------------------------------------------------------
# Test 2: Root failure span normalization
# -------------------------------------------------------------------
def test_normalize_root_failure_span():
    """
    Validates normalization of a root-cause failure.

    Why this test exists:
    ---------------------
    Root failures anchor the RCA graph.
    If this fails, RCA cannot identify the origin of an incident.

    What it checks:
    ---------------
    - error is True
    - error_kind is 'root'
    - incident_id is extracted
    - correct root_service is identified
    """

    raw_span = {
        "trace_id": "trace-456",
        "span_id": "span-root",
        "attributes": {
            "service.name": "service-b",
            "rca.error": True,
            "rca.error.kind": "root",
            "rca.root_service": "service-b",
            "rca.incident_id": "incident-1234"
        }
    }

    normalized = normalize_span(raw_span)

    assert normalized.error is True
    assert normalized.error_kind == "root"
    assert normalized.incident_id == "incident-1234"
    assert normalized.root_service == "service-b"


# -------------------------------------------------------------------
# Test 3: Propagated failure span normalization
# -------------------------------------------------------------------
def test_normalize_propagated_failure_span():
    """
    Validates normalization of a propagated failure.

    Why this test exists:
    ---------------------
    Most outages are not local.
    They propagate through dependencies.

    RCA graphs depend on this distinction.

    What it checks:
    ---------------
    - error_kind is 'propagated'
    - parent_service is captured
    - incident_id is preserved
    """

    raw_span = {
        "trace_id": "trace-789",
        "span_id": "span-prop",
        "attributes": {
            "service.name": "service-a",
            "rca.error": True,
            "rca.error.kind": "propagated",
            "rca.parent_service": "service-b",
            "rca.incident_id": "incident-9999"
        }
    }

    normalized = normalize_span(raw_span)

    assert normalized.error is True
    assert normalized.error_kind == "propagated"
    assert normalized.parent_service == "service-b"
    assert normalized.incident_id == "incident-9999"


# -------------------------------------------------------------------
# Test 4: Missing RCA attributes (defensive behavior)
# -------------------------------------------------------------------
def test_normalize_span_with_missing_attributes():
    """
    Validates graceful handling of spans missing RCA attributes.

    Why this test exists:
    ---------------------
    In real systems:
    - Not all services are instrumented equally
    - Some spans may be partial or malformed

    The RCA pipeline must NEVER crash on bad data.

    What it checks:
    ---------------
    - Defaults are applied
    - No KeyError or exception
    """

    raw_span = {
        "trace_id": "trace-000",
        "span_id": "span-missing",
        "attributes": {
            "service.name": "service-c"
        }
    }

    normalized = normalize_span(raw_span)

    assert normalized.service == "service-c"
    assert normalized.error is False
    assert normalized.incident_id is None
    assert normalized.dependency is None


# -------------------------------------------------------------------
# Test 5: Dependency extraction correctness
# -------------------------------------------------------------------
def test_dependency_extraction():
    """
    Ensures downstream dependency is correctly extracted.

    Why this test exists:
    ---------------------
    Dependency edges form the RCA graph.
    Incorrect dependency extraction = broken graph.

    What it checks:
    ---------------
    - dependency.target is mapped correctly
    """

    raw_span = {
        "trace_id": "trace-dep",
        "span_id": "span-dep",
        "attributes": {
            "service.name": "service-b",
            "rca.dependency.target": "service-c"
        }
    }

    normalized = normalize_span(raw_span)

    assert normalized.dependency == "service-c"
