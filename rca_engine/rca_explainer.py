from typing import Dict, List


class RCAExplainer:
    """
    Converts an RCA graph summary into a human-readable explanation,
    enriched with confidence signals.
    """

    def explain(self, summary: Dict) -> Dict:
        root = summary.get("root_cause")
        incident_id = summary.get("incident_id")
        blast_radius = summary.get("blast_radius", 0)
        affected = summary.get("affected_services", [])

        confidence = summary.get("confidence", {})
        confidence_score = confidence.get("score", 0.0)
        confidence_level = confidence.get("level", "unknown")
        signals = confidence.get("signals", {})

        if not root:
            return {
                "incident_id": None,
                "severity": "none",
                "confidence_level": "none",
                "summary": "No failures detected in the trace.",
                "details": []
            }

        severity = self._severity_from_blast_radius(blast_radius)

        # ---- Base summary ----
        if blast_radius == 1:
            summary_text = (
                f"Service '{root}' failed without impacting downstream services."
            )
        else:
            impacted = ", ".join(s for s in affected if s != root)
            summary_text = (
                f"Service '{root}' experienced a root failure which "
                f"propagated to {impacted}, impacting {blast_radius} services."
            )

        # ---- Confidence reasoning ----
        confidence_reasons = []

        if signals.get("historical_occurrences", 0) > 1:
            confidence_reasons.append(
                f"Root cause has occurred {signals['historical_occurrences']} times historically"
            )

        if blast_radius > 1:
            confidence_reasons.append(
                f"Failure propagated across {blast_radius} services"
            )

        if signals.get("similar_incident_count", 0) > 0:
            confidence_reasons.append(
                f"Strong similarity to {signals['similar_incident_count']} previous incidents"
            )

        if not confidence_reasons:
            confidence_reasons.append("Limited historical data available")

        return {
            "incident_id": incident_id,
            "severity": severity,
            "confidence_level": confidence_level,
            "confidence_score": confidence_score,
            "confidence_reasoning": confidence_reasons,
            "summary": summary_text,
            "details": [
                {
                    "root_service": root,
                    "affected_services": affected,
                    "blast_radius": blast_radius,
                }
            ],
        }

    def _severity_from_blast_radius(self, blast_radius: int) -> str:
        if blast_radius <= 1:
            return "low"
        if blast_radius == 2:
            return "medium"
        return "high"
