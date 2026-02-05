from typing import Dict


class FeatureExtractor:
    """
    Converts an RCA result into an ML-ready feature vector.

    IMPORTANT:
    - Features are inputs to a model
    - Labels are targets the model learns to predict
    """

    def extract(self, result: Dict) -> Dict:
        graph = result.get("graph", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        timeline = result.get("timeline", [])
        explanation = result.get("explanation", {})

        features = {
            # -------------------------
            # Graph-based features
            # -------------------------
            "blast_radius": result.get("blast_radius", 0),
            "num_services": len(nodes),
            "num_dependencies": len(edges),

            # -------------------------
            # Temporal features
            # -------------------------
            "timeline_length": len(timeline),

            # -------------------------
            # Learning signals
            # -------------------------
            "historical_occurrences": result.get("historical_occurrences", 1),
            "confidence": result.get("confidence", 0.0),
        }

        labels = {
            # Ground-truth targets (NOT model inputs)
            "root_cause": result.get("root_cause"),
            "severity": explanation.get("severity"),
        }

        return {
            "features": features,
            "labels": labels,
        }
