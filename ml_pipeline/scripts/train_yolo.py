#!/usr/bin/env python3
"""
Train the NEZA AI shipwreck-detection baseline.

Designed for Apple Silicon with limited memory.
"""

from pathlib import Path
import argparse

import torch
from ultralytics import YOLO


def select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--batch",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--image-size",
        type=int,
        default=640,
    )

    parser.add_argument(
        "--patience",
        type=int,
        default=12,
    )

    parser.add_argument(
        "--model",
        default="yolov8n.pt",
    )

    parser.add_argument(
        "--name",
        default="ai4shipwrecks_v2_baseline",
    )

    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    ml_root = script_path.parents[1]
    project_root = script_path.parents[2]

    dataset_yaml = (
        ml_root
        / "data"
        / "processed"
        / "ai4shipwrecks_yolo_v2"
        / "dataset.yaml"
    )

    output_directory = (
        project_root
        / "runs"
        / "detect"
    )

    if not dataset_yaml.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found: {dataset_yaml}"
        )

    device = select_device()

    print("=" * 60)
    print("NEZA AI — YOLO BASELINE TRAINING")
    print("=" * 60)
    print(f"Dataset:   {dataset_yaml}")
    print(f"Model:     {args.model}")
    print(f"Device:    {device}")
    print(f"Epochs:    {args.epochs}")
    print(f"Batch:     {args.batch}")
    print(f"Image size:{args.image_size}")
    print(f"Output:    {output_directory}")
    print("=" * 60)

    model = YOLO(args.model)

    results = model.train(
        data=str(dataset_yaml),
        epochs=args.epochs,
        patience=args.patience,
        imgsz=args.image_size,
        batch=args.batch,
        device=device,
        workers=0,
        cache=False,
        amp=False,

        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        weight_decay=0.0005,

        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.15,
        degrees=10.0,
        translate=0.10,
        scale=0.20,
        fliplr=0.5,
        flipud=0.5,
        mosaic=0.20,
        close_mosaic=10,

        seed=42,
        deterministic=True,

        project=str(output_directory),
        name=args.name,
        exist_ok=False,
        plots=True,
        save=True,
        verbose=True,
    )

    print("\nTraining completed.")
    print(f"Results: {results.save_dir}")
    print(f"Best model: {results.save_dir / 'weights' / 'best.pt'}")
    print(f"Last model: {results.save_dir / 'weights' / 'last.pt'}")


if __name__ == "__main__":
    main()