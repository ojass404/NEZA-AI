#!/usr/bin/env python3
"""Train the SubPipe Mini side-scan-sonar pipeline detector."""

from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_YAML = (
    PROJECT_ROOT
    / "ml_pipeline"
    / "data"
    / "processed"
    / "subpipe_mini_yolo"
    / "dataset.yaml"
)

BASE_MODEL = PROJECT_ROOT / "yolov8n.pt"

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "detect"
)

RUN_NAME = "subpipe_mini_pipeline_v1"


def select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def main() -> None:
    if not DATASET_YAML.is_file():
        raise FileNotFoundError(
            f"Dataset configuration missing: {DATASET_YAML}"
        )

    if not BASE_MODEL.is_file():
        raise FileNotFoundError(
            f"Base model missing: {BASE_MODEL}"
        )

    device = select_device()

    print("=" * 72)
    print("NEZA AI — SUBPIPE MINI PROTOTYPE TRAINING")
    print("=" * 72)
    print(f"Dataset:    {DATASET_YAML}")
    print(f"Base model: {BASE_MODEL}")
    print(f"Device:     {device}")
    print("Class:      submarine_pipeline")
    print("Epochs:     12")
    print("Image size: 640")
    print("Batch size: 4")
    print("Cache:      disabled")
    print("=" * 72)

    model = YOLO(str(BASE_MODEL))

    results = model.train(
        data=str(DATASET_YAML),
        epochs=12,
        patience=4,
        imgsz=640,
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
        project=str(OUTPUT_ROOT),
        name=RUN_NAME,
        exist_ok=False,
        verbose=True,
    )

    result_directory = Path(results.save_dir)

    print("\n" + "=" * 72)
    print("SUBPIPE PROTOTYPE TRAINING COMPLETED")
    print("=" * 72)
    print(f"Results:    {result_directory}")
    print(
        "Best model: "
        f"{result_directory / 'weights' / 'best.pt'}"
    )
    print(
        "Last model: "
        f"{result_directory / 'weights' / 'last.pt'}"
    )


if __name__ == "__main__":
    main()
