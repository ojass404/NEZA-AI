"""Evaluate Marine Debris segmentation on the untouched test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "runs/segment/marine_debris_fls_seg_v1/weights/best.pt"
)

DEFAULT_DATASET = (
    PROJECT_ROOT
    / "ml_pipeline/data/processed/"
    / "marine_debris_fls_yolo_seg/dataset.yaml"
)


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
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET,
    )
    parser.add_argument(
        "--split",
        choices=("val", "test"),
        default="test",
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
        "--name",
        default="marine_debris_fls_seg_test",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    model_path = args.model.expanduser().resolve()
    dataset_path = args.data.expanduser().resolve()

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Dataset YAML not found: {dataset_path}"
        )

    device = select_device()
    output_directory = (
        PROJECT_ROOT / "runs/segment_evaluations"
    )

    print("=" * 68)
    print("NEZA AI — UNTOUCHED SEGMENTATION EVALUATION")
    print("=" * 68)
    print(f"Model:   {model_path}")
    print(f"Dataset: {dataset_path}")
    print(f"Split:   {args.split}")
    print(f"Device:  {device}")
    print("=" * 68)

    model = YOLO(str(model_path))

    metrics = model.val(
        task="segment",
        data=str(dataset_path),
        split=args.split,
        imgsz=args.image_size,
        batch=args.batch,
        conf=0.001,
        iou=0.60,
        device=device,
        workers=0,
        amp=False,
        plots=True,
        project=str(output_directory),
        name=args.name,
        exist_ok=False,
        verbose=True,
    )

    report = {
        "model": str(model_path),
        "dataset": str(dataset_path),
        "split": args.split,
        "device": device,
        "images": int(metrics.box.nt_per_image.shape[0])
        if hasattr(metrics.box, "nt_per_image")
        else None,
        "box": {
            "precision": round(float(metrics.box.mp), 6),
            "recall": round(float(metrics.box.mr), 6),
            "map50": round(float(metrics.box.map50), 6),
            "map50_95": round(float(metrics.box.map), 6),
        },
        "mask": {
            "precision": round(float(metrics.seg.mp), 6),
            "recall": round(float(metrics.seg.mr), 6),
            "map50": round(float(metrics.seg.map50), 6),
            "map50_95": round(float(metrics.seg.map), 6),
        },
        "results_directory": str(metrics.save_dir),
    }

    report_path = (
        Path(metrics.save_dir)
        / "segmentation_evaluation_summary.json"
    )
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 68)
    print("UNTOUCHED TEST RESULTS")
    print("=" * 68)
    print(
        f"Box precision:    {report['box']['precision']:.4f}"
    )
    print(
        f"Box recall:       {report['box']['recall']:.4f}"
    )
    print(
        f"Box mAP@50:       {report['box']['map50']:.4f}"
    )
    print(
        "Box mAP@50–95:    "
        f"{report['box']['map50_95']:.4f}"
    )
    print(
        f"Mask precision:   {report['mask']['precision']:.4f}"
    )
    print(
        f"Mask recall:      {report['mask']['recall']:.4f}"
    )
    print(
        f"Mask mAP@50:      {report['mask']['map50']:.4f}"
    )
    print(
        "Mask mAP@50–95:   "
        f"{report['mask']['map50_95']:.4f}"
    )
    print(f"Results:          {metrics.save_dir}")
    print(f"JSON report:      {report_path}")


if __name__ == "__main__":
    main()
