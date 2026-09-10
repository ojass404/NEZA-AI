#!/usr/bin/env python3
"""Evaluate a trained NEZA AI YOLO model."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import torch
from ultralytics import YOLO


def select_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def main() -> None:
    script_path = Path(__file__).resolve()
    ml_root = script_path.parents[1]
    project_root = script_path.parents[2]

    default_model = (
        project_root
        / "runs"
        / "detect"
        / "ai4shipwrecks_v2_baseline"
        / "weights"
        / "best.pt"
    )

    default_dataset = (
        ml_root
        / "data"
        / "processed"
        / "ai4shipwrecks_yolo_v2"
        / "dataset.yaml"
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        type=Path,
        default=default_model,
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=default_dataset,
    )

    parser.add_argument(
        "--split",
        choices=("val", "test"),
        default="val",
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.10,
    )

    parser.add_argument(
        "--iou",
        type=float,
        default=0.50,
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
        "--name",
        default=None,
    )

    args = parser.parse_args()

    model_path = args.model.resolve()
    dataset_path = args.dataset.resolve()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found: "
            f"{dataset_path}"
        )

    if not 0.0 <= args.confidence <= 1.0:
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    if not 0.0 <= args.iou <= 1.0:
        raise ValueError(
            "IoU must be between 0 and 1."
        )

    device = select_device()

    run_name = args.name or (
        f"ai4shipwrecks_v2_"
        f"{args.split}_conf"
        f"{str(args.confidence).replace('.', '')}"
    )

    print("=" * 60)
    print("NEZA AI — YOLO EVALUATION")
    print("=" * 60)
    print(f"Model:      {model_path}")
    print(f"Dataset:    {dataset_path}")
    print(f"Split:      {args.split}")
    print(f"Confidence: {args.confidence}")
    print(f"IoU:        {args.iou}")
    print(f"Device:     {device}")
    print("=" * 60)

    model = YOLO(str(model_path))

    metrics = model.val(
        data=str(dataset_path),
        split=args.split,
        conf=args.confidence,
        iou=args.iou,
        imgsz=args.image_size,
        batch=args.batch,
        device=device,
        workers=0,
        amp=False,
        plots=True,
        project=str(project_root / "runs" / "evaluations"),
        name=run_name,
        exist_ok=False,
        verbose=True,
    )

    precision = float(metrics.box.mp)
    recall = float(metrics.box.mr)

    if precision + recall:
        f1_score = (
            2
            * precision
            * recall
            / (precision + recall)
        )
    else:
        f1_score = 0.0

    summary = {
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "model": str(model_path),
        "dataset": str(dataset_path),
        "split": args.split,
        "confidence_threshold": args.confidence,
        "iou_threshold": args.iou,
        "image_size": args.image_size,
        "device": device,
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "map50": float(metrics.box.map50),
            "map50_95": float(metrics.box.map),
        },
        "speed_ms_per_image": {
            key: float(value)
            for key, value in metrics.speed.items()
        },
    }

    save_directory = Path(metrics.save_dir)
    summary_path = (
        save_directory
        / "evaluation_summary.json"
    )

    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Precision:   {precision:.4f}")
    print(f"Recall:      {recall:.4f}")
    print(f"F1-score:    {f1_score:.4f}")
    print(f"mAP@50:      {metrics.box.map50:.4f}")
    print(f"mAP@50-95:   {metrics.box.map:.4f}")
    print(f"Results:     {save_directory}")
    print(f"JSON report: {summary_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()