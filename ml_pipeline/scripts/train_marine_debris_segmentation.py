"""Train the NEZA AI Marine Debris FLS segmentation model."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATASET = (
    PROJECT_ROOT
    / "ml_pipeline/data/processed/"
    / "marine_debris_fls_yolo_seg/dataset.yaml"
)

DEFAULT_OUTPUT = PROJECT_ROOT / "runs/segment"


def select_device() -> str:
    if torch.cuda.is_available():
        return "cuda"

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return "mps"

    return "cpu"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET,
    )
    parser.add_argument(
        "--model",
        default="yolov8n-seg.pt",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=480,
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=12,
    )
    parser.add_argument(
        "--name",
        default="marine_debris_fls_seg_v1",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    dataset = args.data.expanduser().resolve()

    if not dataset.is_file():
        raise FileNotFoundError(
            f"Dataset YAML not found: {dataset}"
        )

    device = select_device()

    print("=" * 68)
    print("NEZA AI — MARINE DEBRIS PIXEL SEGMENTATION TRAINING")
    print("=" * 68)
    print(f"Dataset:    {dataset}")
    print(f"Model:      {args.model}")
    print(f"Device:     {device}")
    print(f"Epochs:     {args.epochs}")
    print(f"Image size: {args.image_size}")
    print(f"Batch size: {args.batch}")
    print(f"Patience:   {args.patience}")
    print("=" * 68)

    model = YOLO(args.model)

    results = model.train(
        task="segment",
        data=str(dataset),
        epochs=args.epochs,
        imgsz=args.image_size,
        batch=args.batch,
        patience=args.patience,
        device=device,
        workers=0,
        amp=False,
        cache=False,
        pretrained=True,
        optimizer="auto",
        seed=42,
        deterministic=True,
        project=str(DEFAULT_OUTPUT),
        name=args.name,
        exist_ok=False,
        plots=True,
        verbose=True,
        hsv_h=0.0,
        hsv_s=0.0,
        hsv_v=0.10,
        degrees=5.0,
        translate=0.05,
        scale=0.20,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.20,
        close_mosaic=10,
    )

    output_directory = Path(results.save_dir)
    best_model = output_directory / "weights/best.pt"
    last_model = output_directory / "weights/last.pt"

    print("\n" + "=" * 68)
    print("SEGMENTATION TRAINING COMPLETED")
    print("=" * 68)
    print(f"Results:    {output_directory}")
    print(f"Best model: {best_model}")
    print(f"Last model: {last_model}")


if __name__ == "__main__":
    main()
