from typing import List, Dict

from rca_engine.trace_normalizer import normalize_trace
from rca_engine.rca_graph import RCAGraph
from rca_engine.timeline_builder import IncidentTimeline
from rca_engine.rca_explainer import RCAExplainer
from rca_engine.incident_store import IncidentStore
from rca_engine.root_cause_ranker import RootCauseRanker
from rca_engine.incident_similarity import IncidentSimilarityEngine
from rca_engine.confidence_engine import ConfidenceEngine


class RCAService:
    """
    Core orchestration layer for Root Cause Analysis.
    """

    def __init__(self):
        self.timeline_builder = IncidentTimeline()
        self.explainer = RCAExplainer()

        # Phase A1: historical memory
        self.incident_store = IncidentStore()

        # Phase A2: probabilistic ranking
        self.root_cause_ranker = RootCauseRanker()

        # Phase A3: incident similarity & recall
        self.similarity_engine = IncidentSimilarityEngine()

        # Phase A4: confidence engine
        self.confidence_engine = ConfidenceEngine()

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

        # 4️⃣ Assemble base result (WITHOUT explanation yet)
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
        }

        # -----------------------------
        # 🔥 Phase A1: Learn incident
        # -----------------------------
        self.incident_store.save(result)

        history = self.incident_store.similar_incidents(result)
        historical_occurrences = history[0]["count"] if history else 1
        result["historical_occurrences"] = historical_occurrences

        # -----------------------------
        # 🎯 Phase A2: Probabilistic RCA
        # -----------------------------
        if result["root_cause"]:
            result["probable_root_causes"] = self.root_cause_ranker.rank(
                root_cause=result["root_cause"],
                graph_edges=result["graph"]["edges"],
                nodes=result["graph"]["nodes"],
                historical_occurrences=historical_occurrences,
            )
        else:
            result["probable_root_causes"] = []

        # -----------------------------
        # 🧠 Phase A3: Similar incidents
        # -----------------------------
        past_incidents = self.incident_store.all()

        similar_incidents = self.similarity_engine.find_similar(
            current=result,
            history=past_incidents,
        )
        result["similar_incidents"] = similar_incidents

        # -----------------------------
        # ✅ Phase A4: Confidence score
        # -----------------------------
        result["confidence"] = self.confidence_engine.compute(
            result=result,
            similar_incidents=similar_incidents,
        )

        # -----------------------------
        # 🗣️ Phase A4.3: Confidence-aware explanation
        # -----------------------------
        explanation_input = {
            **graph_summary,
            "confidence": result["confidence"],
        }

        result["explanation"] = self.explainer.explain(explanation_input)

        return result
