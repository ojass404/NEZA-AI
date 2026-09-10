"""YOLO detector used by the NEZA AI backend."""

from pathlib import Path
import logging

import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


def select_device(model_path: Path) -> str:
    """Select the best supported inference device."""
    if model_path.suffix.lower() == ".onnx":
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return "mps"

    return "cpu"


class YOLODetector:
    """Run the trained NEZA AI shipwreck detector."""

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.20,
        iou_threshold: float = 0.30,
    ) -> None:
        self.model_path = Path(model_path).expanduser().resolve()
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        if not 0 <= confidence_threshold <= 1:
            raise ValueError(
                "confidence_threshold must be between 0 and 1."
            )

        if not 0 <= iou_threshold <= 1:
            raise ValueError("iou_threshold must be between 0 and 1.")

        if not self.model_path.is_file():
            raise FileNotFoundError(
                "Trained NEZA AI model not found: "
                f"{self.model_path}"
            )

        self.device = select_device(self.model_path)
        self.model = YOLO(str(self.model_path))

        logger.info(
            "Loaded NEZA AI detector from %s using %s",
            self.model_path,
            self.device,
        )

    def detect(
        self,
        image: np.ndarray,
        confidence_threshold: float | None = None,
    ) -> list[dict]:
        """Detect possible shipwreck candidates in a BGR image."""
        if image is None:
            raise ValueError("Input image cannot be None.")

        if not isinstance(image, np.ndarray):
            raise TypeError("Input image must be a NumPy array.")

        if image.size == 0:
            raise ValueError("Input image cannot be empty.")

        confidence = (
            self.confidence_threshold
            if confidence_threshold is None
            else confidence_threshold
        )

        if not 0 <= confidence <= 1:
            raise ValueError(
                "confidence threshold must be between 0 and 1."
            )

        results = self.model.predict(
            source=image,
            conf=confidence,
            iou=self.iou_threshold,
            imgsz=640,
            device=self.device,
            verbose=False,
        )

        detections: list[dict] = []

        for result in results:
            if result.boxes is None:
                continue

            for box in result.boxes:
                class_id = int(box.cls.item())
                model_class = str(self.model.names[class_id])
                score = float(box.conf.item())
                x_min, y_min, x_max, y_max = (
                    float(value)
                    for value in box.xyxy[0].cpu().tolist()
                )

                detections.append(
                    {
                        "class_id": class_id,
                        "model_class": model_class,
                        "classification": "possible_shipwreck",
                        "confidence": round(score, 6),
                        "confidence_percent": round(score * 100, 2),
                        "bbox": {
                            "x_min": round(x_min, 2),
                            "y_min": round(y_min, 2),
                            "x_max": round(x_max, 2),
                            "y_max": round(y_max, 2),
                            "width": round(x_max - x_min, 2),
                            "height": round(y_max - y_min, 2),
                        },
                        "human_verification_required": True,
                        "verification_status": "pending",
                    }
                )

        return detections

    def get_class_names(self) -> dict | list:
        """Return the class mapping stored in the trained model."""
        return self.model.names
