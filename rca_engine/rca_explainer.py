from typing import Dict, List


class RCAExplainer:
    """
    Converts an RCA graph summary into a human-readable explanation.
    """

    def explain(self, summary: Dict) -> Dict:
        """
        Generates a structured RCA explanation.
        """

        root = summary.get("root_cause")
        incident_id = summary.get("incident_id")
        blast_radius = summary.get("blast_radius", 0)
        affected = summary.get("affected_services", [])

        if not root:
            return {
                "incident_id": None,
                "severity": "none",
                "summary": "No failures detected in the trace.",
                "details": []
            }

        # Determine severity
        severity = self._severity_from_blast_radius(blast_radius)

        # Construct explanation sentence
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

        # Detailed breakdown
        details = [
            {
                "root_service": root,
                "affected_services": affected,
                "blast_radius": blast_radius
            }
        ]

        return {
            "incident_id": incident_id,
            "severity": severity,
            "summary": summary_text,
            "details": details
        }

    def _severity_from_blast_radius(self, blast_radius: int) -> str:
        """
        Simple severity classification based on blast radius.
        """
        if blast_radius <= 1:
            return "low"
        if blast_radius == 2:
            return "medium"
        return "high"
