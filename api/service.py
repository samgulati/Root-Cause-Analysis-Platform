from typing import Dict, List

from rca_engine.trace_normalizer import normalize_trace
from rca_engine.rca_graph import RCAGraph
from rca_engine.timeline_builder import IncidentTimeline
from rca_engine.rca_explainer import RCAExplainer


class RCAService:
    """
    Orchestrates the complete RCA pipeline.
    This is the SINGLE entrypoint for RCA computation.
    """

    def analyze_trace(self, raw_spans: List[Dict]) -> Dict:
        """
        Runs full RCA analysis on a list of raw spans.

        Input:
        ------
        raw_spans: List of OTEL / Jaeger span dicts

        Output:
        -------
        Structured RCA result
        """

        # 1️⃣ Normalize spans
        normalized_spans = normalize_trace(raw_spans)

        # 2️⃣ Build RCA graph
        graph = RCAGraph()
        graph.build_from_spans(normalized_spans)
        graph_summary = graph.summary()

        # 3️⃣ Build incident timeline
        timeline = IncidentTimeline().build(normalized_spans)

        # 4️⃣ Generate human-readable explanation
        explanation = RCAExplainer().explain(graph_summary)

        # 5️⃣ Final response
        return {
            "incident_id": graph_summary.get("incident_id"),
            "root_cause": graph_summary.get("root_cause"),
            "blast_radius": graph_summary.get("blast_radius"),
            "affected_services": graph_summary.get("affected_services"),
            "timeline": timeline,
            "graph": {
                "nodes": graph_summary.get("nodes"),
                "edges": graph_summary.get("edges"),
            },
            "explanation": explanation,
        }
