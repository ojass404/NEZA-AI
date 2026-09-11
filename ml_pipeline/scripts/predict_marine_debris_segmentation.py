#!/usr/bin/env python3
"""Marine-debris detection and pixel-mask inference for NEZA AI."""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_MODEL = (
    PROJECT_ROOT
    / "backend"
    / "models"
    / "marine_debris_fls_seg.onnx"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "segmentation_inference"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Detect and segment possible marine-debris objects "
            "in forward-looking sonar images."
        )
    )

    parser.add_argument(
        "--image",
        required=True,
        type=Path,
        help="Input forward-looking sonar image.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="YOLO segmentation .pt or .onnx model.",
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

    if args.latitude is not None:
        if not -90.0 <= args.latitude <= 90.0:
            raise ValueError(
                "--latitude must be between -90 and 90."
            )

    if args.longitude is not None:
        if not -180.0 <= args.longitude <= 180.0:
            raise ValueError(
                "--longitude must be between -180 and 180."
            )


def model_class_name(
    names: dict[int, str] | list[str],
    class_id: int,
) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, f"class_{class_id}"))

    if 0 <= class_id < len(names):
        return str(names[class_id])

    return f"class_{class_id}"


def polygon_area(points: np.ndarray) -> float:
    if len(points) < 3:
        return 0.0

    contour = points.astype(np.float32).reshape(-1, 1, 2)
    return float(cv2.contourArea(contour))


def serializable_polygon(
    points: np.ndarray,
) -> list[dict[str, float]]:
    return [
        {
            "x": round(float(point[0]), 2),
            "y": round(float(point[1]), 2),
        }
        for point in points
    ]


def create_csv(
    output_path: Path,
    detections: list[dict[str, Any]],
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
        "mask_area_pixels",
        "polygon_point_count",
        "latitude",
        "longitude",
        "human_verification_required",
        "verification_status",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
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
                    "mask_area_pixels": (
                        detection["mask"]["area_pixels"]
                    ),
                    "polygon_point_count": (
                        detection["mask"][
                            "polygon_point_count"
                        ]
                    ),
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

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"OpenCV could not read the image: {image_path}"
        )

    image_height, image_width = image.shape[:2]

    timestamp = datetime.now(timezone.utc)
    timestamp_name = timestamp.strftime("%Y%m%dT%H%M%SZ")

    output_directory = (
        OUTPUT_ROOT
        / f"{image_path.stem}_{timestamp_name}"
    )
    output_directory.mkdir(parents=True, exist_ok=False)

    print("=" * 72)
    print("NEZA AI — MARINE DEBRIS PIXEL-MASK INFERENCE")
    print("=" * 72)
    print(f"Image:      {image_path}")
    print(f"Dimensions: {image_width} x {image_height}")
    print(f"Model:      {model_path}")
    print(f"Device:     {device}")
    print(f"Confidence: {args.confidence}")
    print(f"IoU:        {args.iou}")
    print("=" * 72)

    model = YOLO(str(model_path))

    results = model.predict(
        source=str(image_path),
        imgsz=480,
        conf=args.confidence,
        iou=args.iou,
        device=device,
        verbose=False,
        save=False,
    )

    result = results[0]
    detections: list[dict[str, Any]] = []

    boxes = result.boxes
    mask_polygons = (
        result.masks.xy
        if result.masks is not None
        else []
    )

    if boxes is not None:
        for index, box in enumerate(boxes):
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            coordinates = (
                box.xyxy[0]
                .detach()
                .cpu()
                .numpy()
                .astype(float)
            )

            x_min, y_min, x_max, y_max = coordinates
            width = max(0.0, x_max - x_min)
            height = max(0.0, y_max - y_min)

            class_name = model_class_name(
                result.names,
                class_id,
            )

            if index < len(mask_polygons):
                polygon = np.asarray(
                    mask_polygons[index],
                    dtype=np.float32,
                )
            else:
                polygon = np.empty(
                    (0, 2),
                    dtype=np.float32,
                )

            area = polygon_area(polygon)

            detections.append(
                {
                    "id": f"det_{index + 1:04d}",
                    "classification": (
                        f"possible_{class_name}"
                    ),
                    "model_class": class_name,
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
                        "width": round(width, 2),
                        "height": round(height, 2),
                    },
                    "mask": {
                        "area_pixels": round(area, 2),
                        "image_coverage_percent": round(
                            area
                            / (image_width * image_height)
                            * 100,
                            4,
                        ),
                        "polygon_point_count": len(polygon),
                        "polygon_pixels": (
                            serializable_polygon(polygon)
                        ),
                    },
                    "latitude": args.latitude,
                    "longitude": args.longitude,
                    "human_verification_required": True,
                    "verification_status": "pending",
                }
            )

    annotated_image = result.plot(
        boxes=True,
        masks=True,
        labels=True,
        conf=True,
    )

    annotated_path = (
        output_directory
        / f"{image_path.stem}_segmented.jpg"
    )
    json_path = (
        output_directory
        / f"{image_path.stem}_report.json"
    )
    csv_path = (
        output_directory
        / f"{image_path.stem}_report.csv"
    )

    if not cv2.imwrite(
        str(annotated_path),
        annotated_image,
    ):
        raise RuntimeError(
            f"Could not save annotated image: {annotated_path}"
        )

    report = {
        "system": "NEZA AI",
        "task": (
            "Detection and pixel-level segmentation of "
            "possible marine-debris objects in "
            "forward-looking sonar imagery"
        ),
        "created_at_utc": timestamp.isoformat(),
        "source_image": {
            "filename": image_path.name,
            "path": str(image_path),
            "width_pixels": image_width,
            "height_pixels": image_height,
            "latitude": args.latitude,
            "longitude": args.longitude,
        },
        "model": {
            "path": str(model_path),
            "task": "instance_segmentation",
            "confidence_threshold": args.confidence,
            "iou_threshold": args.iou,
            "device": device,
        },
        "summary": {
            "total_detections": len(detections),
            "detections_with_pixel_masks": sum(
                detection["mask"]["polygon_point_count"] > 0
                for detection in detections
            ),
            "human_verification_required": True,
        },
        "detections": detections,
        "limitations": [
            (
                "This model was trained on controlled "
                "forward-looking sonar watertank imagery."
            ),
            (
                "Its results do not establish performance "
                "on side-scan sonar or open-ocean surveys."
            ),
            (
                "The model was not trained to identify "
                "ghost nets."
            ),
            (
                "Every detected object requires human "
                "verification."
            ),
        ],
    }

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    create_csv(csv_path, detections)

    print("\n" + "=" * 72)
    print("SEGMENTATION INFERENCE COMPLETED")
    print("=" * 72)
    print(f"Detections:     {len(detections)}")
    print(
        "Pixel masks:    "
        f"{report['summary']['detections_with_pixel_masks']}"
    )
    print(f"Annotated image: {annotated_path}")
    print(f"JSON report:     {json_path}")
    print(f"CSV report:      {csv_path}")


if __name__ == "__main__":
    main()
