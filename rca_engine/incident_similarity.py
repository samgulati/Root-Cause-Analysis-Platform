from typing import Dict, List, Tuple


class IncidentSimilarityEngine:
    """
    Computes similarity between incidents using structural features.
    """

    def similarity_score(self, current: Dict, past: Dict) -> float:
        score = 0.0

        # 1️⃣ Same root cause
        if current.get("root_cause") == past.get("root_cause"):
            score += 3.0

        # 2️⃣ Overlapping affected services
        curr_services = set(current.get("affected_services", []))
        past_services = set(past.get("affected_services", []))

        if curr_services and past_services:
            overlap = len(curr_services & past_services)
            union = len(curr_services | past_services)
            score += 2.0 * (overlap / union)

        # 3️⃣ Blast radius similarity
        br_curr = current.get("blast_radius", 0)
        br_past = past.get("blast_radius", 0)

        if br_curr and br_past:
            score += 1.5 * (1 - abs(br_curr - br_past) / max(br_curr, br_past))

        # 4️⃣ Error pattern similarity
        if current.get("root_cause") and past.get("root_cause"):
            score += 1.0

        return round(score, 2)

    def find_similar(
        self,
        current: Dict,
        history: List[Dict],
        threshold: float = 2.5
    ) -> List[Dict]:
        """
        Returns similar incidents above a similarity threshold.
        """

        matches: List[Tuple[float, Dict]] = []

        for past in history:
            score = self.similarity_score(current, past)
            if score >= threshold:
                matches.append((score, past))

        # Sort by similarity score descending
        matches.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                "similarity": score,
                "incident": incident,
            }
            for score, incident in matches
        ]
