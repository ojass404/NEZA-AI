"""Backend integration service for the trained NEZA AI detector."""

from pathlib import Path
from typing import Any
import logging

import numpy as np

from app.core.detection.yolo_detector import YOLODetector

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL = PROJECT_ROOT / "backend/models/yolov8n_sss.pt"


class InferenceService:
    """Run verified YOLO detection without simulated ML components."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        confidence_threshold: float = 0.20,
        iou_threshold: float = 0.30,
    ) -> None:
        selected_model = (
            Path(model_path).expanduser().resolve()
            if model_path is not None
            else DEFAULT_MODEL
        )

        self.detector = YOLODetector(
            model_path=str(selected_model),
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
        )

        logger.info(
            "InferenceService initialized with %s",
            selected_model,
        )

    def process_image(
        self,
        image: np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Detect candidates and return a backend-safe result."""
        metadata = dict(metadata or {})
        detections = self.detector.detect(image)

        for index, detection in enumerate(detections, start=1):
            detection["id"] = f"det_{index:04d}"
            detection["latitude"] = metadata.get("latitude")
            detection["longitude"] = metadata.get("longitude")

        return {
            "task": (
                "Detection of possible shipwreck or artificial-anomaly "
                "candidates in side-scan sonar imagery"
            ),
            "model": {
                "path": str(self.detector.model_path),
                "device": self.detector.device,
                "confidence_threshold": (
                    self.detector.confidence_threshold
                ),
                "iou_threshold": self.detector.iou_threshold,
            },
            "detections": detections,
            "summary": {
                "total_detections": len(detections),
                "human_verification_required": True,
            },
            "metadata": metadata,
            "limitations": [
                (
                    "The current model was trained only on "
                    "AI4Shipwrecks imagery."
                ),
                (
                    "The model does not reliably identify ghost nets, "
                    "pipes, cylinders or general marine debris."
                ),
                (
                    "Every detection requires human verification."
                ),
                (
                    "Semantic segmentation is not enabled because no "
                    "verified trained segmentation model is available."
                ),
            ],
        }
