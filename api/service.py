from typing import List, Dict

from rca_engine.trace_normalizer import normalize_trace
from rca_engine.rca_graph import RCAGraph
from rca_engine.timeline_builder import IncidentTimeline
from rca_engine.rca_explainer import RCAExplainer
from rca_engine.incident_store import IncidentStore


class RCAService:
    """
    Core orchestration layer for Root Cause Analysis.
    """

    def __init__(self):
        self.timeline_builder = IncidentTimeline()
        self.explainer = RCAExplainer()

        # Phase A1: historical memory
        self.incident_store = IncidentStore()

    def analyze_trace(self, raw_spans: List[Dict]) -> Dict:
        """
        Executes full RCA pipeline on a trace.
        """

        # 1️⃣ Normalize raw spans
        spans = normalize_trace(raw_spans)

        # 2️⃣ Build RCA graph
        graph = RCAGraph()
        graph.build_from_spans(spans)
        graph_summary = graph.summary()

        # 3️⃣ Build incident timeline
        timeline = self.timeline_builder.build(spans)

        # 4️⃣ Generate explanation
        explanation = self.explainer.explain(graph_summary)

        # 5️⃣ Assemble result
        result = {
            "incident_id": graph_summary.get("incident_id"),
            "root_cause": graph_summary.get("root_cause"),
            "blast_radius": graph_summary.get("blast_radius"),
            "affected_services": graph_summary.get("affected_services"),
            "graph": {
                "nodes": graph_summary.get("nodes", []),
                "edges": graph_summary.get("edges", []),
            },
            "timeline": timeline,
            "explanation": explanation,
        }

        # 🔥 Phase A1: Learn from this incident
        self.incident_store.save(result)

        # Fetch historical occurrence count
        history = self.incident_store.similar_incidents(result)
        result["historical_occurrences"] = (
            history[0]["count"] if history else 1
        )

        return result
