#!/usr/bin/env python3
"""Train the NEZA AI UATD underwater-object detector."""

from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_YAML = (
    PROJECT_ROOT
    / "ml_pipeline"
    / "data"
    / "processed"
    / "uatd_yolo"
    / "dataset.yaml"
)

BASE_MODEL = PROJECT_ROOT / "yolov8n.pt"
OUTPUT_DIRECTORY = PROJECT_ROOT / "runs" / "detect"
RUN_NAME = "uatd_yolov8n_v1"


def select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def main() -> None:
    if not DATASET_YAML.is_file():
        raise FileNotFoundError(
            f"Dataset configuration not found: {DATASET_YAML}"
        )

    if not BASE_MODEL.is_file():
        raise FileNotFoundError(
            f"Base YOLO model not found: {BASE_MODEL}"
        )

    device = select_device()

    print("=" * 72)
    print("NEZA AI — UATD OBJECT-DETECTION TRAINING")
    print("=" * 72)
    print(f"Dataset:    {DATASET_YAML}")
    print(f"Base model: {BASE_MODEL}")
    print(f"Device:     {device}")
    print("Classes:    10")
    print("Image size: 512")
    print("Batch size: 4")
    print("Epochs:     40")
    print("=" * 72)

    model = YOLO(str(BASE_MODEL))

    results = model.train(
        data=str(DATASET_YAML),
        epochs=40,
        patience=10,
        imgsz=512,
        batch=4,
        device=device,
        workers=0,
        cache=False,
        amp=False,
        pretrained=True,
        optimizer="auto",
        seed=42,
        deterministic=True,
        plots=True,
        save=True,
        project=str(OUTPUT_DIRECTORY),
        name=RUN_NAME,
        exist_ok=False,
        verbose=True,
    )

    run_directory = Path(results.save_dir)

    print("\n" + "=" * 72)
    print("UATD TRAINING COMPLETED")
    print("=" * 72)
    print(f"Results:    {run_directory}")
    print(f"Best model: {run_directory / 'weights' / 'best.pt'}")
    print(f"Last model: {run_directory / 'weights' / 'last.pt'}")


if __name__ == "__main__":
    main()
