from typing import Dict, List
from collections import defaultdict


class RootCauseRanker:
    """
    Computes probabilistic ranking of root cause candidates.
    """

    ERROR_WEIGHTS = {
        "root": 1.0,
        "propagated": 0.4,
        None: 0.1,
    }

    DISTANCE_WEIGHTS = {
        0: 1.0,
        1: 0.7,
        2: 0.4,
    }

    def rank(
        self,
        root_cause: str,
        graph_edges: List[Dict],
        nodes: List[Dict],
        historical_occurrences: int,
    ) -> List[Dict]:
        """
        Returns ranked root cause candidates with probabilities.
        """

        # Build reverse dependency graph
        reverse_graph = defaultdict(list)
        for edge in graph_edges:
            reverse_graph[edge["to"]].append(edge["from"])

        # BFS to compute distance from root
        distances = {root_cause: 0}
        queue = [root_cause]

        while queue:
            current = queue.pop(0)
            for upstream in reverse_graph.get(current, []):
                if upstream not in distances:
                    distances[upstream] = distances[current] + 1
                    queue.append(upstream)

        scores = {}

        for node in nodes:
            service = node["service"]
            error_kind = node.get("error_kind")

            error_weight = self.ERROR_WEIGHTS.get(error_kind, 0.1)
            distance = distances.get(service, 3)
            distance_weight = self.DISTANCE_WEIGHTS.get(distance, 0.2)

            history_weight = min(1.0 + historical_occurrences * 0.1, 2.0)

            scores[service] = error_weight * distance_weight * history_weight

        # Normalize to probabilities
        total = sum(scores.values()) or 1.0
        ranked = sorted(
            [
                {
                    "service": svc,
                    "probability": round(score / total, 3),
                }
                for svc, score in scores.items()
            ],
            key=lambda x: x["probability"],
            reverse=True,
        )

        return ranked
