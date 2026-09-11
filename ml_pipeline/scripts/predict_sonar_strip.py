#!/usr/bin/env python3
"""Run tiled NEZA AI inference on a full-resolution sonar image."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import torch
from torchvision.ops import nms
from ultralytics import YOLO


def select_device(model_path: Path) -> str:
    if model_path.suffix.lower() == ".onnx":
        return "cpu"

    if torch.backends.mps.is_available():
        return "mps"

    if torch.cuda.is_available():
        return "cuda"

    return "cpu"


def tile_positions(
    length: int,
    tile_size: int,
    stride: int,
) -> list[int]:
    if length <= tile_size:
        return [0]

    positions = list(
        range(0, length - tile_size + 1, stride)
    )

    final_position = length - tile_size

    if positions[-1] != final_position:
        positions.append(final_position)

    return positions


def create_tile(
    image: np.ndarray,
    x: int,
    y: int,
    tile_size: int,
) -> np.ndarray:
    tile = image[
        y:y + tile_size,
        x:x + tile_size,
    ]

    if tile.shape[:2] == (tile_size, tile_size):
        return tile

    padded = np.zeros(
        (tile_size, tile_size, 3),
        dtype=image.dtype,
    )

    padded[
        :tile.shape[0],
        :tile.shape[1],
    ] = tile

    return padded


def apply_global_nms(
    detections: list[dict],
    iou_threshold: float,
) -> list[dict]:
    if not detections:
        return []

    boxes = torch.tensor(
        [
            [
                detection["x1"],
                detection["y1"],
                detection["x2"],
                detection["y2"],
            ]
            for detection in detections
        ],
        dtype=torch.float32,
    )

    scores = torch.tensor(
        [
            detection["confidence"]
            for detection in detections
        ],
        dtype=torch.float32,
    )

    kept_indices = nms(
        boxes,
        scores,
        iou_threshold,
    ).tolist()

    return [
        detections[index]
        for index in kept_indices
    ]


def main() -> None:
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]

    default_model = (
        project_root
        / "backend"
        / "models"
        / "yolov8n_sss.pt"
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
        default=0.05,
    )

    parser.add_argument(
        "--tile-size",
        type=int,
        default=640,
    )

    parser.add_argument(
        "--stride",
        type=int,
        default=512,
    )

    parser.add_argument(
        "--tile-iou",
        type=float,
        default=0.30,
    )

    parser.add_argument(
        "--global-iou",
        type=float,
        default=0.30,
    )

    parser.add_argument(
        "--minimum-box-area",
        type=float,
        default=5000.0,
        help=(
            "Discard tiny full-image detections below "
            "this pixel area."
        ),
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
            f"Image not found: {image_path}"
        )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    if args.stride > args.tile_size:
        raise ValueError(
            "Stride cannot be greater than tile size."
        )

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    image_height, image_width = image.shape[:2]
    device = select_device(model_path)

    x_positions = tile_positions(
        image_width,
        args.tile_size,
        args.stride,
    )

    y_positions = tile_positions(
        image_height,
        args.tile_size,
        args.stride,
    )

    total_tiles = len(x_positions) * len(y_positions)

    print("=" * 65)
    print("NEZA AI — FULL SONAR IMAGE INFERENCE")
    print("=" * 65)
    print(f"Image:       {image_path}")
    print(f"Dimensions:  {image_width} x {image_height}")
    print(f"Model:       {model_path}")
    print(f"Device:      {device}")
    print(f"Tile size:   {args.tile_size}")
    print(f"Stride:      {args.stride}")
    print(f"Total tiles: {total_tiles}")
    print("=" * 65)

    model = YOLO(str(model_path))
    tile_detections = []

    completed_tiles = 0

    for y in y_positions:
        for x in x_positions:
            tile = create_tile(
                image=image,
                x=x,
                y=y,
                tile_size=args.tile_size,
            )

            result = model.predict(
                source=tile,
                conf=args.confidence,
                iou=args.tile_iou,
                imgsz=args.tile_size,
                device=device,
                verbose=False,
            )[0]

            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0].cpu())
                    confidence = float(
                        box.conf[0].cpu()
                    )

                    local_x1, local_y1, local_x2, local_y2 = [
                        float(value)
                        for value in box.xyxy[0].cpu().tolist()
                    ]

                    global_x1 = max(
                        0.0,
                        min(
                            image_width,
                            local_x1 + x,
                        ),
                    )

                    global_y1 = max(
                        0.0,
                        min(
                            image_height,
                            local_y1 + y,
                        ),
                    )

                    global_x2 = max(
                        0.0,
                        min(
                            image_width,
                            local_x2 + x,
                        ),
                    )

                    global_y2 = max(
                        0.0,
                        min(
                            image_height,
                            local_y2 + y,
                        ),
                    )

                    if (
                        global_x2 <= global_x1
                        or global_y2 <= global_y1
                    ):
                        continue

                    box_area = (
                        (global_x2 - global_x1)
                        * (global_y2 - global_y1)
                    )

                    if box_area < args.minimum_box_area:
                        continue

                    tile_detections.append(
                        {
                            "class_id": class_id,
                            "model_class": model.names[
                                class_id
                            ],
                            "confidence": confidence,
                            "x1": global_x1,
                            "y1": global_y1,
                            "x2": global_x2,
                            "y2": global_y2,
                            "tile_x": x,
                            "tile_y": y,
                        }
                    )

            completed_tiles += 1

            if completed_tiles % 10 == 0:
                print(
                    f"Processed "
                    f"{completed_tiles}/{total_tiles} tiles"
                )

    merged_detections = apply_global_nms(
        detections=tile_detections,
        iou_threshold=args.global_iou,
    )

    annotated = image.copy()
    final_detections = []

    for index, detection in enumerate(
        merged_detections,
        start=1,
    ):
        x1 = int(round(detection["x1"]))
        y1 = int(round(detection["y1"]))
        x2 = int(round(detection["x2"]))
        y2 = int(round(detection["y2"]))

        confidence = detection["confidence"]

        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            4,
        )

        cv2.putText(
            annotated,
            f"possible shipwreck {confidence:.2f}",
            (x1, max(25, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 0, 255),
            2,
        )

        final_detections.append(
            {
                "id": f"det_{index:04d}",
                "classification": "possible_shipwreck",
                "model_class": detection["model_class"],
                "class_id": detection["class_id"],
                "confidence": round(confidence, 4),
                "confidence_percent": round(
                    confidence * 100,
                    2,
                ),
                "bounding_box_pixels": {
                    "x_min": x1,
                    "y_min": y1,
                    "x_max": x2,
                    "y_max": y2,
                    "width": x2 - x1,
                    "height": y2 - y1,
                },
                "source_tile": {
                    "x": detection["tile_x"],
                    "y": detection["tile_y"],
                    "size": args.tile_size,
                },
                "verification_status": "pending",
                "human_verification_required": True,
            }
        )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    output_directory = (
        project_root
        / "runs"
        / "sonar_inference"
        / f"{image_path.stem}_{timestamp}"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    annotated_path = (
        output_directory
        / f"{image_path.stem}_annotated.jpg"
    )

    cv2.imwrite(
        str(annotated_path),
        annotated,
        [cv2.IMWRITE_JPEG_QUALITY, 95],
    )

    report = {
        "system": "NEZA AI",
        "task": (
            "Tiled detection of possible shipwrecks or "
            "artificial anomalies in side-scan sonar imagery"
        ),
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_image": {
            "filename": image_path.name,
            "width_pixels": image_width,
            "height_pixels": image_height,
            "latitude": args.latitude,
            "longitude": args.longitude,
        },
        "inference": {
            "model": str(model_path),
            "device": device,
            "confidence_threshold": args.confidence,
            "tile_size": args.tile_size,
            "stride": args.stride,
            "tiles_processed": total_tiles,
            "detections_before_global_nms": len(
                tile_detections
            ),
            "detections_after_global_nms": len(
                final_detections
            ),
            "global_nms_iou": args.global_iou,
            "minimum_box_area_pixels": (
                args.minimum_box_area
            ),
        },
        "summary": {
            "total_detections": len(final_detections),
            "human_verification_required": True,
        },
        "detections": final_detections,
        "limitations": [
            (
                "The current model is trained only on "
                "AI4Shipwrecks imagery."
            ),
            (
                "Detections require human verification."
            ),
            (
                "The model is not validated for ghost nets, "
                "pipes, cylinders or general marine debris."
            ),
        ],
    }

    json_path = (
        output_directory
        / f"{image_path.stem}_report.json"
    )

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    csv_path = (
        output_directory
        / f"{image_path.stem}_report.csv"
    )

    fields = [
        "detection_id",
        "classification",
        "confidence_percent",
        "x_min_pixels",
        "y_min_pixels",
        "x_max_pixels",
        "y_max_pixels",
        "width_pixels",
        "height_pixels",
        "source_tile_x",
        "source_tile_y",
        "source_latitude",
        "source_longitude",
        "verification_status",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for detection in final_detections:
            box = detection["bounding_box_pixels"]
            tile = detection["source_tile"]

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
                    "source_tile_x": tile["x"],
                    "source_tile_y": tile["y"],
                    "source_latitude": args.latitude,
                    "source_longitude": args.longitude,
                    "verification_status": detection[
                        "verification_status"
                    ],
                }
            )

    print("\n" + "=" * 65)
    print("INFERENCE COMPLETED")
    print("=" * 65)
    print(
        f"Detections before NMS: "
        f"{len(tile_detections)}"
    )
    print(
        f"Detections after NMS:  "
        f"{len(final_detections)}"
    )
    print(f"Annotated image:       {annotated_path}")
    print(f"JSON report:           {json_path}")
    print(f"CSV report:            {csv_path}")


if __name__ == "__main__":
    main()