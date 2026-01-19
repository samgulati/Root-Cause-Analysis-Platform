from typing import Dict, List

from rca_engine.trace_normalizer import normalize_trace
from rca_engine.rca_graph import RCAGraph
from rca_engine.timeline_builder import IncidentTimeline
from rca_engine.rca_explainer import RCAExplainer
from rca_engine.rca_schema import RCAReport


class RCAAnalyzer:
    """
    Single entrypoint for Root Cause Analysis.

    This class orchestrates:
    - Trace normalization
    - Causal graph construction
    - Blast radius calculation
    - Incident timeline generation
    - Human-readable explanation
    """

    def analyze_trace(self, raw_spans: List[Dict]) -> Dict:
        """
        Perform end-to-end RCA on a single trace.

        Input:
        ------
        raw_spans : List[Dict]
            Raw OTEL / Jaeger spans for ONE trace

        Output:
        -------
        Dict
            Canonical RCA report
        """

        # 1️⃣ Normalize raw spans
        normalized_spans = normalize_trace(raw_spans)

        # 2️⃣ Build RCA graph
        graph = RCAGraph()
        graph.build_from_spans(normalized_spans)
        graph_summary = graph.summary()

        # 3️⃣ Build incident timeline
        timeline = IncidentTimeline().build(normalized_spans)

        # 4️⃣ Generate human-readable explanation
        explanation = RCAExplainer().explain(graph_summary)

        # 5️⃣ Final RCA report (single contract)
        return RCAReport(
            schema_version="1.0",
            incident_id=graph_summary.get("incident_id"),
            severity=explanation.get("severity"),
            root_cause=graph_summary.get("root_cause"),
            blast_radius=graph_summary.get("blast_radius", 0),
            affected_services=graph_summary.get("affected_services", []),
            timeline=timeline,
            explanation=explanation,
            graph={
                "nodes": graph_summary.get("nodes", []),
                "edges": graph_summary.get("edges", []),
            },
        )
