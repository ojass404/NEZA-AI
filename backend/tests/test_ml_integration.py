"""Automated checks for the NEZA AI ML/backend integration."""

from pathlib import Path
import sys
import unittest

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIRECTORY = PROJECT_ROOT / "backend"

if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.core.detection.unet_segmentor import UNetSegmentor
from app.core.detection.yolo_detector import YOLODetector
from app.core.verification.confidence import ConfidenceScorer
from app.core.verification.priority import PriorityAssigner
from app.services.inference_service import InferenceService


PYTORCH_MODEL = PROJECT_ROOT / "backend/models/yolov8n_sss.pt"
ONNX_MODEL = PROJECT_ROOT / "backend/models/yolov8n_sss.onnx"
SAMPLE_IMAGE = (
    PROJECT_ROOT
    / "ml_pipeline/data/processed/ai4shipwrecks_yolo_v2/"
    / "images/val/wreck_DM_Wilson_03.jpg"
)


class TestMLSafetyChecks(unittest.TestCase):
    def test_missing_model_fails_closed(self) -> None:
        with self.assertRaises(FileNotFoundError):
            YOLODetector("/definitely/missing/neza_model.pt")

    def test_unverified_segmentation_is_disabled(self) -> None:
        with self.assertRaises(RuntimeError):
            UNetSegmentor("unverified_weights.pth")

    def test_confidence_uses_raw_model_score(self) -> None:
        result = ConfidenceScorer().calculate(
            0.419154,
            mask_coverage=0.9,
            shadow_score=0.9,
        )
        self.assertEqual(result, 41.92)

    def test_review_priority(self) -> None:
        assigner = PriorityAssigner()
        self.assertEqual(assigner.assign(80), "HIGH")
        self.assertEqual(assigner.assign(41.92), "MEDIUM")
        self.assertEqual(assigner.assign(8.49), "LOW")


@unittest.skipUnless(
    PYTORCH_MODEL.is_file() and SAMPLE_IMAGE.is_file(),
    "Local PyTorch model or sample image is unavailable.",
)
class TestRealPyTorchInference(unittest.TestCase):
    def test_pytorch_backend_detection(self) -> None:
        image = cv2.imread(str(SAMPLE_IMAGE))
        self.assertIsNotNone(image)

        service = InferenceService(
            model_path=PYTORCH_MODEL,
            confidence_threshold=0.20,
        )
        result = service.process_image(
            image,
            {
                "latitude": 18.5204,
                "longitude": 73.8567,
            },
        )

        self.assertEqual(result["summary"]["total_detections"], 1)
        detection = result["detections"][0]
        self.assertEqual(
            detection["classification"],
            "possible_shipwreck",
        )
        self.assertTrue(
            detection["human_verification_required"]
        )
        self.assertEqual(detection["latitude"], 18.5204)
        self.assertEqual(detection["longitude"], 73.8567)


@unittest.skipUnless(
    ONNX_MODEL.is_file() and SAMPLE_IMAGE.is_file(),
    "Local ONNX model or sample image is unavailable.",
)
class TestRealONNXInference(unittest.TestCase):
    def test_onnx_backend_detection(self) -> None:
        image = cv2.imread(str(SAMPLE_IMAGE))
        self.assertIsNotNone(image)

        service = InferenceService(
            model_path=ONNX_MODEL,
            confidence_threshold=0.20,
        )
        result = service.process_image(image)

        self.assertEqual(result["model"]["device"], "cpu")
        self.assertEqual(result["summary"]["total_detections"], 1)


if __name__ == "__main__":
    unittest.main()
