#!/usr/bin/env python3
"""Run submarine-pipeline detection on a side-scan sonar image."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "backend/models/subpipe_pipeline_detector.onnx"
)

DEFAULT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "runs/subpipe_inference"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Detect possible submarine pipelines in "
            "side-scan sonar imagery."
        )
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Input side-scan sonar image.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="PyTorch or ONNX SubPipe detection model.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="Minimum detection confidence.",
    )
    parser.add_argument(
        "--iou",
        type=float,
        default=0.50,
        help="Non-maximum suppression IoU threshold.",
    )
    parser.add_argument(
        "--latitude",
        type=float,
        default=None,
        help="Optional image latitude.",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        default=None,
        help="Optional image longitude.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="Root output directory.",
    )

    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()

    return (PROJECT_ROOT / path).resolve()


def validate_arguments(args: argparse.Namespace) -> None:
    if not args.image.is_file():
        raise FileNotFoundError(
            f"Input image not found: {args.image}"
        )

    if not args.model.is_file():
        raise FileNotFoundError(
            f"Model not found: {args.model}"
        )

    if not 0.0 < args.confidence <= 1.0:
        raise ValueError(
            "--confidence must be greater than 0 and at most 1."
        )

    if not 0.0 < args.iou <= 1.0:
        raise ValueError(
            "--iou must be greater than 0 and at most 1."
        )

    if (
        args.latitude is not None
        and not -90.0 <= args.latitude <= 90.0
    ):
        raise ValueError(
            "--latitude must be between -90 and 90."
        )

    if (
        args.longitude is not None
        and not -180.0 <= args.longitude <= 180.0
    ):
        raise ValueError(
            "--longitude must be between -180 and 180."
        )


def select_device(model_path: Path) -> str:
    if model_path.suffix.lower() == ".onnx":
        return "cpu"

    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda:0"

    return "cpu"


def create_detection_records(result) -> list[dict]:
    records = []

    if result.boxes is None:
        return records

    boxes = result.boxes.xyxy.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    for index, (box, confidence, class_id) in enumerate(
        zip(boxes, confidences, class_ids),
        start=1,
    ):
        x_min, y_min, x_max, y_max = map(float, box)
        width = max(0.0, x_max - x_min)
        height = max(0.0, y_max - y_min)

        model_class = result.names.get(
            int(class_id),
            "submarine_pipeline",
        )

        records.append(
            {
                "id": f"det_{index:04d}",
                "classification": (
                    "possible_submarine_pipeline"
                ),
                "model_class": model_class,
                "class_id": int(class_id),
                "confidence": round(float(confidence), 6),
                "confidence_percent": round(
                    float(confidence) * 100.0,
                    2,
                ),
                "bounding_box_pixels": {
                    "x_min": round(x_min, 2),
                    "y_min": round(y_min, 2),
                    "x_max": round(x_max, 2),
                    "y_max": round(y_max, 2),
                    "width": round(width, 2),
                    "height": round(height, 2),
                    "area": round(width * height, 2),
                },
                "human_verification_required": True,
                "verification_status": "pending",
            }
        )

    return records


def write_csv(
    csv_path: Path,
    detections: list[dict],
    latitude: float | None,
    longitude: float | None,
) -> None:
    fieldnames = [
        "id",
        "classification",
        "model_class",
        "class_id",
        "confidence",
        "confidence_percent",
        "x_min",
        "y_min",
        "x_max",
        "y_max",
        "width",
        "height",
        "area",
        "latitude",
        "longitude",
        "human_verification_required",
        "verification_status",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for detection in detections:
            box = detection["bounding_box_pixels"]

            writer.writerow(
                {
                    "id": detection["id"],
                    "classification": (
                        detection["classification"]
                    ),
                    "model_class": detection["model_class"],
                    "class_id": detection["class_id"],
                    "confidence": detection["confidence"],
                    "confidence_percent": (
                        detection["confidence_percent"]
                    ),
                    "x_min": box["x_min"],
                    "y_min": box["y_min"],
                    "x_max": box["x_max"],
                    "y_max": box["y_max"],
                    "width": box["width"],
                    "height": box["height"],
                    "area": box["area"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "human_verification_required": True,
                    "verification_status": (
                        detection["verification_status"]
                    ),
                }
            )


def main() -> None:
    args = parse_arguments()

    args.image = resolve_path(args.image)
    args.model = resolve_path(args.model)
    args.output = resolve_path(args.output)

    validate_arguments(args)

    image = cv2.imread(str(args.image))

    if image is None:
        raise ValueError(
            f"OpenCV could not read image: {args.image}"
        )

    image_height, image_width = image.shape[:2]
    device = select_device(args.model)

    timestamp = datetime.now(timezone.utc)
    timestamp_text = timestamp.strftime("%Y%m%dT%H%M%SZ")

    result_directory = (
        args.output
        / f"{args.image.stem}_{timestamp_text}"
    )
    result_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    print("=" * 72)
    print("NEZA AI — SUBMARINE PIPELINE INFERENCE")
    print("=" * 72)
    print(f"Image:      {args.image}")
    print(
        f"Dimensions: {image_width} x {image_height}"
    )
    print(f"Model:      {args.model}")
    print(f"Device:     {device}")
    print(f"Confidence: {args.confidence}")
    print(f"IoU:        {args.iou}")
    print("=" * 72)

    model = YOLO(str(args.model))

    result = model.predict(
        source=str(args.image),
        imgsz=640,
        conf=args.confidence,
        iou=args.iou,
        device=device,
        verbose=False,
    )[0]

    detections = create_detection_records(result)

    for detection in detections:
        detection["latitude"] = args.latitude
        detection["longitude"] = args.longitude

    class_counts = Counter(
        detection["model_class"]
        for detection in detections
    )

    annotated_path = (
        result_directory
        / f"{args.image.stem}_annotated.jpg"
    )
    json_path = (
        result_directory
        / f"{args.image.stem}_report.json"
    )
    csv_path = (
        result_directory
        / f"{args.image.stem}_report.csv"
    )

    annotated_image = result.plot()
    written = cv2.imwrite(
        str(annotated_path),
        annotated_image,
    )

    if not written:
        raise RuntimeError(
            f"Could not write annotated image: {annotated_path}"
        )

    report = {
        "system": "NEZA AI",
        "task": (
            "Detection of possible submarine pipelines "
            "in side-scan sonar imagery"
        ),
        "created_at_utc": timestamp.isoformat(),
        "source_image": {
            "filename": args.image.name,
            "path": str(args.image),
            "width_pixels": image_width,
            "height_pixels": image_height,
            "latitude": args.latitude,
            "longitude": args.longitude,
        },
        "model": {
            "path": str(args.model),
            "dataset": "SubPipeMini side-scan sonar",
            "confidence_threshold": args.confidence,
            "iou_threshold": args.iou,
            "device": device,
        },
        "summary": {
            "total_detections": len(detections),
            "class_counts": dict(class_counts),
            "human_verification_required": True,
        },
        "detections": detections,
        "limitations": [
            (
                "The model was trained on the SubPipeMini "
                "side-scan sonar dataset."
            ),
            (
                "Predictions indicate possible submarine "
                "pipeline locations."
            ),
            (
                "The model does not estimate pipeline depth, "
                "diameter or structural condition."
            ),
            (
                "The model was not trained to identify "
                "ghost nets or general marine debris."
            ),
            "All predictions require human verification.",
        ],
    }

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    write_csv(
        csv_path,
        detections,
        args.latitude,
        args.longitude,
    )

    print()
    print("=" * 72)
    print("SUBPIPE INFERENCE COMPLETED")
    print("=" * 72)
    print(f"Detections:      {len(detections)}")
    print(f"Classes:         {dict(class_counts)}")
    print(f"Annotated image: {annotated_path}")
    print(f"JSON report:     {json_path}")
    print(f"CSV report:      {csv_path}")


if __name__ == "__main__":
    main()
