from typing import List, Dict, Set
from rca_engine.trace_normalizer import NormalizedSpan


class RCAGraph:
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.root_cause: str | None = None
        self.incident_id: str | None = None

        # Phase 6A: retain spans
        self.spans: List[NormalizedSpan] = []

    # ------------------------
    # Graph Construction
    # ------------------------
    def add_node(self, span: NormalizedSpan):
        if span.service not in self.nodes:
            self.nodes[span.service] = {
                "service": span.service,
                "error": span.error,
                "error_kind": span.error_kind,
                "incident_id": span.incident_id,
            }

    def add_edge(self, from_service: str, to_service: str):
        self.edges.append({
            "from": from_service,
            "to": to_service,
            "type": "dependency"
        })

    def build_from_spans(self, spans: List[NormalizedSpan]):
        # Persist spans (important for timeline & explanation)
        self.spans = spans

        # Step 1: Add nodes
        for span in spans:
            self.add_node(span)

        # Step 2: Identify root cause
        for span in spans:
            if span.error and span.error_kind == "root":
                self.root_cause = span.service
                self.incident_id = span.incident_id

        # Step 3: Add dependency edges
        for span in spans:
            if span.dependency:
                self.add_edge(span.service, span.dependency)

    # ------------------------
    # Phase 5A – Blast Radius
    # ------------------------
    def compute_blast_radius(self) -> Dict:
        if not self.root_cause:
            return {
                "blast_radius": 0,
                "affected_services": []
            }

        affected: Set[str] = set()
        queue = [self.root_cause]

        while queue:
            current = queue.pop(0)
            if current in affected:
                continue

            affected.add(current)

            # Reverse dependency traversal (upstream)
            for edge in self.edges:
                if edge["to"] == current:
                    queue.append(edge["from"])

        return {
            "blast_radius": len(affected),
            "affected_services": list(affected)
        }

    # ------------------------
    # Public API
    # ------------------------
    def summary(self) -> Dict:
        impact = self.compute_blast_radius()

        return {
            "incident_id": self.incident_id,
            "root_cause": self.root_cause,
            "blast_radius": impact["blast_radius"],
            "affected_services": impact["affected_services"],
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }
