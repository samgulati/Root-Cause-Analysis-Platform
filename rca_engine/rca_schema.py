from typing import Dict, List, TypedDict, Optional


class TimelineEvent(TypedDict):
    service: str
    error_kind: Optional[str]
    offset_ms: int


class GraphNode(TypedDict):
    service: str
    error: bool
    error_kind: Optional[str]
    incident_id: Optional[str]


class GraphEdge(TypedDict):
    from_: str
    to: str
    type: str


class RCAExplanation(TypedDict):
    summary: str
    details: List[Dict]


class RCAReport(TypedDict):
    schema_version: str
    incident_id: Optional[str]
    severity: str
    root_cause: Optional[str]
    blast_radius: int
    affected_services: List[str]
    timeline: List[TimelineEvent]
    explanation: RCAExplanation
    graph: Dict[str, List[Dict]]
