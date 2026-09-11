"""Confidence handling for verified NEZA AI detections."""


class ConfidenceScorer:
    """Convert raw detector confidence into a percentage."""

    @staticmethod
    def calculate(
        yolo_confidence: float,
        mask_coverage: float | None = None,
        shadow_score: float | None = None,
    ) -> float:
        del mask_coverage
        del shadow_score

        if not 0 <= yolo_confidence <= 1:
            raise ValueError(
                "YOLO confidence must be between 0 and 1."
            )

        return round(yolo_confidence * 100, 2)

    def calculate_batch(self, detections: list[dict]) -> list[dict]:
        for detection in detections:
            raw_confidence = detection.get(
                "yolo_confidence",
                detection.get("confidence", 0.0),
            )

            if raw_confidence > 1:
                raw_confidence /= 100

            detection["confidence"] = self.calculate(raw_confidence)

        return detections

    @staticmethod
    def get_confidence_level(confidence: float) -> str:
        if confidence >= 60:
            return "HIGH"
        if confidence >= 20:
            return "MEDIUM"
        return "LOW"
