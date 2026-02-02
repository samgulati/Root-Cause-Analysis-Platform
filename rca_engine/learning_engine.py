class LearningEngine:
    """
    Adjusts confidence based on historical correctness.
    """

    def adjust_confidence(self, base_confidence: float, accuracy: float) -> float:
        """
        accuracy ∈ [0,1]
        """

        # Smooth scaling to avoid wild swings
        learning_factor = 0.5 + accuracy / 2

        adjusted = base_confidence * learning_factor

        return round(min(adjusted, 1.0), 2)
