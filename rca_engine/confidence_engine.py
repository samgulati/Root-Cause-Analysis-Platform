from typing import Dict


class ConfidenceEngine:
    """
    Computes confidence score for an RCA result.

    Confidence is based on:
    - Root cause detection
    - Blast radius size
    - Historical recurrence
    - Similar incident match strength
    """

    def compute(self, rca_result: Dict) -> Dict:
        """
        Returns confidence score, level, and explanation.
        """

        # -----------------------------
        # Extract signals
        # -----------------------------
        root_cause = rca_result.get("root_cause")
        blast_radius = rca_result.get("blast_radius", 0)
        historical_occurrences = rca_result.get("historical_occurrences", 1)

        probable_causes = rca_result.get("probable_root_causes", [])
        similarity_score = (
            probable_causes[0]["probability"]
            if probable_causes
            else 0.0
        )

        # -----------------------------
        # Normalize signals (0 → 1)
        # -----------------------------
        root_detected_signal = 1.0 if root_cause else 0.0

        blast_radius_signal = min(blast_radius / 5, 1.0)
        historical_signal = min(historical_occurrences / 10, 1.0)
        similarity_signal = min(similarity_score, 1.0)

        # -----------------------------
        # Weighted confidence formula
        # -----------------------------
        confidence_score = round(
            0.35 * root_detected_signal +
            0.25 * blast_radius_signal +
            0.20 * historical_signal +
            0.20 * similarity_signal,
            2
        )

        # -----------------------------
        # Confidence level
        # -----------------------------
        if confidence_score >= 0.75:
            level = "high"
        elif confidence_score >= 0.4:
            level = "medium"
        else:
            level = "low"

        # -----------------------------
        # Explainability
        # -----------------------------
        confidence_factors = {
            "root_detected": bool(root_cause),
            "blast_radius": blast_radius,
            "historical_occurrences": historical_occurrences,
            "similarity_score": round(similarity_score, 2),
        }

        return {
            "confidence_score": confidence_score,
            "confidence_level": level,
            "confidence_factors": confidence_factors,
        }
