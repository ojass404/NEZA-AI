"""Human-review priority assignment for NEZA AI candidates."""


class PriorityAssigner:
    """Assign review priority without inventing hazard classes."""

    @staticmethod
    def assign(confidence: float, class_name: str = "shipwreck") -> str:
        del class_name

        if not 0 <= confidence <= 100:
            raise ValueError(
                "Confidence percentage must be between 0 and 100."
            )

        if confidence >= 60:
            return "HIGH"
        if confidence >= 20:
            return "MEDIUM"
        return "LOW"

    def assign_batch(self, detections: list[dict]) -> list[dict]:
        for detection in detections:
            detection["review_priority"] = self.assign(
                float(detection.get("confidence_percent", 0.0))
            )

        return detections
