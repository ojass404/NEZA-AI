#!/usr/bin/env python3
"""Compare NEZA AI PyTorch and ONNX inference."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


def synchronize(device: str) -> None:
    if device == "mps":
        torch.mps.synchronize()
    elif device == "cuda":
        torch.cuda.synchronize()


def extract_detections(result) -> list[dict]:
    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        detections.append(
            {
                "confidence": float(box.conf[0].cpu()),
                "bbox": [
                    float(value)
                    for value in box.xyxy[0].cpu().tolist()
                ],
            }
        )

    return sorted(
        detections,
        key=lambda item: item["confidence"],
        reverse=True,
    )


def benchmark(
    model: YOLO,
    image,
    device: str,
    confidence: float,
    iterations: int,
) -> tuple[list[float], list[dict]]:
    # Warm-up runs are excluded from timing.
    for _ in range(3):
        model.predict(
            source=image,
            conf=confidence,
            iou=0.30,
            imgsz=640,
            device=device,
            verbose=False,
        )

    synchronize(device)

    timings = []
    final_detections = []

    for _ in range(iterations):
        synchronize(device)
        start = time.perf_counter()

        result = model.predict(
            source=image,
            conf=confidence,
            iou=0.30,
            imgsz=640,
            device=device,
            verbose=False,
        )[0]

        synchronize(device)
        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        timings.append(elapsed_ms)
        final_detections = extract_detections(result)

    return timings, final_detections


def timing_summary(values: list[float]) -> dict:
    ordered = sorted(values)
    percentile_index = min(
        len(ordered) - 1,
        int(len(ordered) * 0.95),
    )

    return {
        "mean_ms": statistics.mean(values),
        "median_ms": statistics.median(values),
        "minimum_ms": min(values),
        "maximum_ms": max(values),
        "p95_ms": ordered[percentile_index],
    }


def main() -> None:
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]
    ml_root = script_path.parents[1]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image",
        type=Path,
        default=(
            ml_root
            / "data"
            / "processed"
            / "ai4shipwrecks_yolo_v2"
            / "images"
            / "val"
            / "wreck_DM_Wilson_03.jpg"
        ),
    )

    parser.add_argument(
        "--pytorch-model",
        type=Path,
        default=(
            project_root
            / "backend"
            / "models"
            / "yolov8n_sss.pt"
        ),
    )

    parser.add_argument(
        "--onnx-model",
        type=Path,
        default=(
            project_root
            / "backend"
            / "models"
            / "yolov8n_sss.onnx"
        ),
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.20,
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=20,
    )

    args = parser.parse_args()

    image_path = args.image.resolve()
    pytorch_path = args.pytorch_model.resolve()
    onnx_path = args.onnx_model.resolve()

    for required_path in (
        image_path,
        pytorch_path,
        onnx_path,
    ):
        if not required_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {required_path}"
            )

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    pytorch_device = (
        "mps"
        if torch.backends.mps.is_available()
        else "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("Loading PyTorch model...")
    pytorch_model = YOLO(str(pytorch_path))

    print("Loading ONNX model...")
    onnx_model = YOLO(str(onnx_path))

    print("Benchmarking PyTorch...")
    pytorch_times, pytorch_detections = benchmark(
        model=pytorch_model,
        image=image,
        device=pytorch_device,
        confidence=args.confidence,
        iterations=args.iterations,
    )

    print("Benchmarking ONNX...")
    onnx_times, onnx_detections = benchmark(
        model=onnx_model,
        image=image,
        device="cpu",
        confidence=args.confidence,
        iterations=args.iterations,
    )

    pytorch_summary = timing_summary(pytorch_times)
    onnx_summary = timing_summary(onnx_times)

    comparison = {
        "detection_count_equal": (
            len(pytorch_detections)
            == len(onnx_detections)
        ),
        "pytorch_detection_count": len(
            pytorch_detections
        ),
        "onnx_detection_count": len(
            onnx_detections
        ),
        "top_confidence_difference": None,
        "maximum_bbox_difference_pixels": None,
    }

    if pytorch_detections and onnx_detections:
        comparison["top_confidence_difference"] = abs(
            pytorch_detections[0]["confidence"]
            - onnx_detections[0]["confidence"]
        )

        comparison[
            "maximum_bbox_difference_pixels"
        ] = max(
            abs(first - second)
            for first, second in zip(
                pytorch_detections[0]["bbox"],
                onnx_detections[0]["bbox"],
            )
        )

    report = {
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "image": str(image_path),
        "confidence_threshold": args.confidence,
        "iterations": args.iterations,
        "pytorch": {
            "model": str(pytorch_path),
            "device": pytorch_device,
            "timing": pytorch_summary,
            "detections": pytorch_detections,
        },
        "onnx": {
            "model": str(onnx_path),
            "device": "cpu",
            "timing": onnx_summary,
            "detections": onnx_detections,
        },
        "comparison": comparison,
    }

    output_directory = (
        project_root
        / "runs"
        / "benchmarks"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        output_directory
        / "pytorch_onnx_benchmark.json"
    )

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nPYTORCH")
    print(f"Device:      {pytorch_device}")
    print(
        f"Mean time:   "
        f"{pytorch_summary['mean_ms']:.2f} ms"
    )
    print(
        f"Detections:  {len(pytorch_detections)}"
    )

    print("\nONNX")
    print("Device:      cpu")
    print(
        f"Mean time:   "
        f"{onnx_summary['mean_ms']:.2f} ms"
    )
    print(f"Detections:  {len(onnx_detections)}")

    print("\nPARITY")
    print(
        f"Same detection count: "
        f"{comparison['detection_count_equal']}"
    )
    print(
        "Confidence difference: "
        f"{comparison['top_confidence_difference']}"
    )
    print(
        "Maximum box difference: "
        f"{comparison['maximum_bbox_difference_pixels']}"
    )
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()