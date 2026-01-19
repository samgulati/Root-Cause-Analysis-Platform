from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# =====================================================
# Incoming Trace Schemas (Input)
# =====================================================

class RawSpan(BaseModel):
    """
    Represents a raw OpenTelemetry / Jaeger span
    as received by the RCA API.
    """

    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None

    name: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    attributes: Dict[str, Any] = Field(default_factory=dict)
    resource: Dict[str, Any] = Field(default_factory=dict)
    status: Dict[str, Any] = Field(default_factory=dict)


class RCARequest(BaseModel):
    """
    API request payload for RCA analysis.

    Supports:
    - raw spans (manual testing, replay)
    - otel_payload (real OpenTelemetry ingestion)
    """

    spans: Optional[List[RawSpan]] = None
    otel_payload: Optional[Dict[str, Any]] = None


# =====================================================
# RCA Timeline Schemas
# =====================================================

class TimelineEvent(BaseModel):
    """
    Human-readable timeline event for an incident.
    """

    service: str
    operation: Optional[str]

    role: str  # root_cause | propagated_failure
    error: bool
    error_kind: Optional[str]

    incident_id: Optional[str]
    offset_ms: int

    explanation: str


# =====================================================
# RCA Graph Schemas
# =====================================================

class GraphNode(BaseModel):
    """
    Represents a service node in the RCA graph.
    """

    service: str
    error: bool
    error_kind: Optional[str]
    incident_id: Optional[str]


class GraphEdge(BaseModel):
    """
    Represents a dependency edge between services.
    """

    from_service: str = Field(..., alias="from")
    to_service: str = Field(..., alias="to")
    type: str


class RCAGraphSchema(BaseModel):
    """
    RCA dependency graph.
    """

    nodes: List[GraphNode]
    edges: List[GraphEdge]


# =====================================================
# RCA Explanation Schema
# =====================================================

class RCAExplanation(BaseModel):
    """
    Structured RCA explanation output.
    """

    incident_id: Optional[str]
    severity: str
    summary: str
    details: List[Dict[str, Any]]


# =====================================================
# Final RCA API Response
# =====================================================

class RCAResponse(BaseModel):
    """
    Final response returned by the RCA API.
    """

    incident_id: Optional[str]
    root_cause: Optional[str]

    blast_radius: int
    affected_services: List[str]

    graph: RCAGraphSchema
    timeline: List[TimelineEvent]
    explanation: RCAExplanation
