#!/usr/bin/env python3
"""Evaluate the trained UATD detector on the untouched test split."""

import json
from datetime import datetime, timezone
from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "runs"
    / "detect"
    / "uatd_yolov8n_v1"
    / "weights"
    / "best.pt"
)

DATASET_YAML = (
    PROJECT_ROOT
    / "ml_pipeline"
    / "data"
    / "processed"
    / "uatd_yolo"
    / "dataset.yaml"
)

OUTPUT_ROOT = PROJECT_ROOT / "runs" / "detect_evaluations"
RUN_NAME = "uatd_yolov8n_v1_test"


def select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def main() -> None:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained UATD model not found: {MODEL_PATH}"
        )

    if not DATASET_YAML.is_file():
        raise FileNotFoundError(
            f"Dataset configuration not found: {DATASET_YAML}"
        )

    device = select_device()

    print("=" * 72)
    print("NEZA AI — UNTOUCHED UATD TEST EVALUATION")
    print("=" * 72)
    print(f"Model:   {MODEL_PATH}")
    print(f"Dataset: {DATASET_YAML}")
    print("Split:   test")
    print(f"Device:  {device}")
    print("=" * 72)

    model = YOLO(str(MODEL_PATH))

    metrics = model.val(
        data=str(DATASET_YAML),
        split="test",
        imgsz=512,
        batch=4,
        device=device,
        workers=0,
        amp=False,
        plots=True,
        project=str(OUTPUT_ROOT),
        name=RUN_NAME,
        exist_ok=True,
        verbose=True,
    )

    precision = float(metrics.box.mp)
    recall = float(metrics.box.mr)
    map50 = float(metrics.box.map50)
    map50_95 = float(metrics.box.map)

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    report = {
        "system": "NEZA AI",
        "dataset": "UATD",
        "task": "underwater_object_detection",
        "split": "test",
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "model": str(MODEL_PATH),
        "dataset_yaml": str(DATASET_YAML),
        "device": device,
        "image_size": 512,
        "test_images": 796,
        "test_instances": 1152,
        "metrics": {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1_score": round(f1_score, 6),
            "map50": round(map50, 6),
            "map50_95": round(map50_95, 6),
        },
        "limitations": [
            (
                "UATD contains multibeam forward-looking "
                "sonar imagery, not side-scan sonar."
            ),
            (
                "The model was trained only on the ten "
                "labelled UATD object classes."
            ),
            (
                "The model does not identify ghost nets."
            ),
            "Predictions require human verification.",
        ],
    }

    save_directory = Path(metrics.save_dir)
    report_path = (
        save_directory
        / "uatd_test_evaluation_summary.json"
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("UNTOUCHED UATD TEST RESULTS")
    print("=" * 72)
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1-score:    {f1_score:.4f}")
    print(f"mAP@50:      {map50:.4f}")
    print(f"mAP@50–95:   {map50_95:.4f}")
    print(f"Results:     {save_directory}")
    print(f"JSON report: {report_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
