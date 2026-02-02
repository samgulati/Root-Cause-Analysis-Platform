from typing import Dict, List


class FeedbackStore:
    """
    Stores feedback on RCA predictions to enable adaptive learning.
    """

    def __init__(self):
        self._feedback: List[Dict] = []

    def record(
        self,
        incident_id: str,
        root_cause: str,
        confidence: float,
        correct: bool,
    ):
        self._feedback.append({
            "incident_id": incident_id,
            "root_cause": root_cause,
            "confidence": confidence,
            "correct": correct,
        })

    def stats_for_root(self, root_cause: str) -> Dict:
        records = [f for f in self._feedback if f["root_cause"] == root_cause]

        if not records:
            return {"total": 0, "accuracy": 1.0}

        correct = sum(1 for r in records if r["correct"])
        total = len(records)

        return {
            "total": total,
            "accuracy": correct / total
        }
