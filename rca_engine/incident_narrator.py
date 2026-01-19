from typing import Dict, List


class IncidentNarrator:
    """
    Produces a human-readable incident narrative
    from RCA graph summary and timeline.
    """

    def generate(
        self,
        summary: Dict,
        timeline: List[Dict]
    ) -> Dict:
        """
        Returns a structured incident narrative.
        """

        if not summary.get("root_cause"):
            return {
                "title": "No Incident Detected",
                "narrative": "The trace completed successfully with no failures.",
                "impact": "none"
            }

        root = summary["root_cause"]
        blast_radius = summary["blast_radius"]
        affected = summary["affected_services"]

        lines = []

        # ---- Opening ----
        lines.append(
            f"Incident originated in service '{root}'."
        )

        # ---- Timeline narrative ----
        for event in timeline:
            role = event["role"]
            offset = event["offset_ms"]

            if role == "root_cause":
                lines.append(
                    f"+{offset}ms: Root failure occurred in "
                    f"{event['service']}."
                )
            elif role == "propagated_failure":
                lines.append(
                    f"+{offset}ms: Failure propagated to "
                    f"{event['service']}."
                )

        # ---- Impact summary ----
        lines.append(
            f"A total of {blast_radius} services were impacted: "
            f"{', '.join(affected)}."
        )

        return {
            "title": f"Incident affecting {root}",
            "narrative": " ".join(lines),
            "impact": self._impact_label(blast_radius),
        }

    def _impact_label(self, blast_radius: int) -> str:
        if blast_radius <= 1:
            return "low"
        if blast_radius == 2:
            return "medium"
        return "high"
