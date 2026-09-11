#!/usr/bin/env python3
"""Run UATD underwater-object inference for NEZA AI."""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "backend"
    / "models"
    / "uatd_detector.onnx"
)

OUTPUT_ROOT = PROJECT_ROOT / "runs" / "uatd_inference"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Detect UATD underwater objects and generate "
            "annotated, JSON and CSV outputs."
        )
    )

    parser.add_argument(
        "--image",
        required=True,
        type=Path,
        help="Input underwater sonar image.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="UATD YOLO .pt or .onnx model.",
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

    return parser.parse_args()


def select_device(model_path: Path) -> str:
    if model_path.suffix.lower() == ".onnx":
        return "cpu"

    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def validate_arguments(args: argparse.Namespace) -> None:
    if not args.image.expanduser().resolve().is_file():
        raise FileNotFoundError(
            f"Input image not found: {args.image}"
        )

    if not args.model.expanduser().resolve().is_file():
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


def create_csv(
    path: Path,
    detections: list[dict[str, Any]],
) -> None:
    fields = [
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
        "latitude",
        "longitude",
        "human_verification_required",
        "verification_status",
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
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
                    "latitude": detection["latitude"],
                    "longitude": detection["longitude"],
                    "human_verification_required": (
                        detection[
                            "human_verification_required"
                        ]
                    ),
                    "verification_status": (
                        detection["verification_status"]
                    ),
                }
            )


def main() -> None:
    args = parse_arguments()
    validate_arguments(args)

    image_path = args.image.expanduser().resolve()
    model_path = args.model.expanduser().resolve()
    device = select_device(model_path)

    source_image = cv2.imread(str(image_path))

    if source_image is None:
        raise ValueError(
            f"OpenCV could not read the image: {image_path}"
        )

    height, width = source_image.shape[:2]
    created_at = datetime.now(timezone.utc)
    timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")

    output_directory = (
        OUTPUT_ROOT
        / f"{image_path.stem}_{timestamp}"
    )
    output_directory.mkdir(parents=True, exist_ok=False)

    print("=" * 72)
    print("NEZA AI — UATD UNDERWATER-OBJECT INFERENCE")
    print("=" * 72)
    print(f"Image:      {image_path}")
    print(f"Dimensions: {width} x {height}")
    print(f"Model:      {model_path}")
    print(f"Device:     {device}")
    print(f"Confidence: {args.confidence}")
    print(f"IoU:        {args.iou}")
    print("=" * 72)

    model = YOLO(str(model_path))

    result = model.predict(
        source=str(image_path),
        imgsz=512,
        conf=args.confidence,
        iou=args.iou,
        device=device,
        verbose=False,
        save=False,
    )[0]

    detections: list[dict[str, Any]] = []

    if result.boxes is not None:
        for index, box in enumerate(result.boxes):
            class_id = int(box.cls[0].item())
            model_class = str(result.names[class_id])
            confidence = float(box.conf[0].item())

            coordinates = (
                box.xyxy[0]
                .detach()
                .cpu()
                .numpy()
                .astype(float)
            )

            x_min, y_min, x_max, y_max = coordinates

            detections.append(
                {
                    "id": f"det_{index + 1:04d}",
                    "classification": (
                        f"possible_{model_class}"
                    ),
                    "model_class": model_class,
                    "class_id": class_id,
                    "confidence": round(confidence, 6),
                    "confidence_percent": round(
                        confidence * 100,
                        2,
                    ),
                    "bounding_box_pixels": {
                        "x_min": round(x_min, 2),
                        "y_min": round(y_min, 2),
                        "x_max": round(x_max, 2),
                        "y_max": round(y_max, 2),
                        "width": round(
                            max(0.0, x_max - x_min),
                            2,
                        ),
                        "height": round(
                            max(0.0, y_max - y_min),
                            2,
                        ),
                    },
                    "latitude": args.latitude,
                    "longitude": args.longitude,
                    "human_verification_required": True,
                    "verification_status": "pending",
                }
            )

    annotated_path = (
        output_directory
        / f"{image_path.stem}_annotated.jpg"
    )
    json_path = (
        output_directory
        / f"{image_path.stem}_report.json"
    )
    csv_path = (
        output_directory
        / f"{image_path.stem}_report.csv"
    )

    annotated_image = result.plot()

    if not cv2.imwrite(
        str(annotated_path),
        annotated_image,
    ):
        raise RuntimeError(
            f"Could not save annotated image: {annotated_path}"
        )

    class_counts: dict[str, int] = {}

    for detection in detections:
        class_name = detection["model_class"]
        class_counts[class_name] = (
            class_counts.get(class_name, 0) + 1
        )

    report = {
        "system": "NEZA AI",
        "task": (
            "Detection of possible underwater objects "
            "in multibeam forward-looking sonar imagery"
        ),
        "created_at_utc": created_at.isoformat(),
        "source_image": {
            "filename": image_path.name,
            "path": str(image_path),
            "width_pixels": width,
            "height_pixels": height,
            "latitude": args.latitude,
            "longitude": args.longitude,
        },
        "model": {
            "path": str(model_path),
            "dataset": "UATD object detection",
            "confidence_threshold": args.confidence,
            "iou_threshold": args.iou,
            "device": device,
        },
        "summary": {
            "total_detections": len(detections),
            "class_counts": class_counts,
            "human_verification_required": True,
        },
        "detections": detections,
        "limitations": [
            (
                "The model was trained on UATD multibeam "
                "forward-looking sonar imagery."
            ),
            (
                "It was not trained on side-scan sonar "
                "imagery."
            ),
            (
                "It supports only the ten labelled UATD "
                "classes."
            ),
            (
                "It was not trained to identify ghost nets."
            ),
            "All predictions require human verification.",
        ],
    }

    report["source_image"]["filename"] = image_path.name

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    create_csv(csv_path, detections)

    print("\n" + "=" * 72)
    print("UATD INFERENCE COMPLETED")
    print("=" * 72)
    print(f"Detections:      {len(detections)}")
    print(f"Classes:         {class_counts}")
    print(f"Annotated image: {annotated_path}")
    print(f"JSON report:     {json_path}")
    print(f"CSV report:      {csv_path}")


if __name__ == "__main__":
    main()
