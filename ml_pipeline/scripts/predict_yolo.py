#!/usr/bin/env python3
"""Run NEZA AI inference on one sonar image or image crop."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
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
    project_root = script_path.parents[2]

    default_model = (
        project_root
        / "runs"
        / "detect"
        / "ai4shipwrecks_v2_baseline"
        / "weights"
        / "best.pt"
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--model",
        type=Path,
        default=default_model,
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.20,
    )

    parser.add_argument(
        "--iou",
        type=float,
        default=0.30,
    )

    parser.add_argument(
        "--latitude",
        type=float,
        default=None,
    )

    parser.add_argument(
        "--longitude",
        type=float,
        default=None,
    )

    args = parser.parse_args()

    image_path = args.image.resolve()
    model_path = args.model.resolve()

    if not image_path.exists():
        raise FileNotFoundError(
            f"Input image not found: {image_path}"
        )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"OpenCV could not read: {image_path}"
        )

    if not 0.0 <= args.confidence <= 1.0:
        raise ValueError(
            "Confidence must be between 0 and 1."
        )

    if not 0.0 <= args.iou <= 1.0:
        raise ValueError(
            "IoU must be between 0 and 1."
        )

    if model_path.suffix.lower() == ".onnx":
        device = "cpu"
    else:
        device = select_device()

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    output_directory = (
        project_root
        / "runs"
        / "inference"
        / f"{image_path.stem}_{timestamp}"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    print("=" * 60)
    print("NEZA AI — SONAR IMAGE INFERENCE")
    print("=" * 60)
    print(f"Image:      {image_path}")
    print(f"Model:      {model_path}")
    print(f"Device:     {device}")
    print(f"Confidence: {args.confidence}")
    print(f"IoU:        {args.iou}")
    print("=" * 60)

    model = YOLO(str(model_path))

    result = model.predict(
        source=image,
        conf=args.confidence,
        iou=args.iou,
        imgsz=640,
        device=device,
        verbose=False,
    )[0]

    detections = []

    if result.boxes is not None:
        for index, box in enumerate(
            result.boxes,
            start=1,
        ):
            class_id = int(box.cls[0].cpu())
            raw_class = model.names[class_id]
            confidence = float(box.conf[0].cpu())

            x1, y1, x2, y2 = [
                round(float(value), 2)
                for value in box.xyxy[0].cpu().tolist()
            ]

            detection = {
                "id": f"det_{index:04d}",
                "classification": (
                    f"possible_{raw_class}"
                ),
                "model_class": raw_class,
                "class_id": class_id,
                "confidence": round(
                    confidence,
                    4,
                ),
                "confidence_percent": round(
                    confidence * 100,
                    2,
                ),
                "bounding_box_pixels": {
                    "x_min": x1,
                    "y_min": y1,
                    "x_max": x2,
                    "y_max": y2,
                    "width": round(x2 - x1, 2),
                    "height": round(y2 - y1, 2),
                },
                "human_verification_required": True,
                "verification_status": "pending",
            }

            detections.append(detection)

    annotated_image = result.plot()

    annotated_path = (
        output_directory
        / f"{image_path.stem}_annotated.jpg"
    )

    cv2.imwrite(
        str(annotated_path),
        annotated_image,
    )

    report = {
        "system": "NEZA AI",
        "task": (
            "Detection of possible shipwreck or "
            "artificial anomaly in side-scan sonar imagery"
        ),
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_image": {
            "filename": image_path.name,
            "path": str(image_path),
            "width_pixels": int(image.shape[1]),
            "height_pixels": int(image.shape[0]),
            "latitude": args.latitude,
            "longitude": args.longitude,
        },
        "model": {
            "path": str(model_path),
            "confidence_threshold": args.confidence,
            "iou_threshold": args.iou,
            "device": device,
        },
        "summary": {
            "total_detections": len(detections),
            "human_verification_required": True,
        },
        "detections": detections,
        "limitations": [
            (
                "The current model was trained only on "
                "AI4Shipwrecks side-scan sonar imagery."
            ),
            (
                "Predictions are possible shipwreck or "
                "artificial-anomaly candidates."
            ),
            (
                "The model has not been trained to reliably "
                "identify ghost nets, pipes, cylinders or "
                "general marine debris."
            ),
        ],
    }

    report_path = (
        output_directory
        / f"{image_path.stem}_report.json"
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    csv_path = (
        output_directory
        / f"{image_path.stem}_report.csv"
    )

    csv_fields = [
        "detection_id",
        "classification",
        "confidence_percent",
        "x_min_pixels",
        "y_min_pixels",
        "x_max_pixels",
        "y_max_pixels",
        "width_pixels",
        "height_pixels",
        "source_latitude",
        "source_longitude",
        "verification_status",
        "human_verification_required",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=csv_fields,
        )

        writer.writeheader()

        for detection in detections:
            box = detection["bounding_box_pixels"]

            writer.writerow(
                {
                    "detection_id": detection["id"],
                    "classification": detection[
                        "classification"
                    ],
                    "confidence_percent": detection[
                        "confidence_percent"
                    ],
                    "x_min_pixels": box["x_min"],
                    "y_min_pixels": box["y_min"],
                    "x_max_pixels": box["x_max"],
                    "y_max_pixels": box["y_max"],
                    "width_pixels": box["width"],
                    "height_pixels": box["height"],
                    "source_latitude": args.latitude,
                    "source_longitude": args.longitude,
                    "verification_status": detection[
                        "verification_status"
                    ],
                    "human_verification_required": detection[
                        "human_verification_required"
                    ],
                }
            )

    print(f"\nDetections:      {len(detections)}")
    print(f"Annotated image: {annotated_path}")
    print(f"JSON report:     {report_path}")
    print(f"CSV report:      {csv_path}")


if __name__ == "__main__":
    main()