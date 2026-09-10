"""Compare raw and preprocessed YOLO inference on the validation set."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIRECTORY = PROJECT_ROOT / "backend"

if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.core.detection.yolo_detector import YOLODetector
from app.core.preprocessing.noise_filter import SonarPreprocessor


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=(
            PROJECT_ROOT
            / "ml_pipeline/data/processed/ai4shipwrecks_yolo_v2"
        ),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=PROJECT_ROOT / "backend/models/yolov8n_sss.pt",
    )
    parser.add_argument("--confidence", type=float, default=0.10)
    parser.add_argument("--match-iou", type=float, default=0.50)
    return parser.parse_args()


def intersection_over_union(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> float:
    x_left = max(first[0], second[0])
    y_top = max(first[1], second[1])
    x_right = min(first[2], second[2])
    y_bottom = min(first[3], second[3])

    intersection_width = max(0.0, x_right - x_left)
    intersection_height = max(0.0, y_bottom - y_top)
    intersection = intersection_width * intersection_height

    first_area = max(0.0, first[2] - first[0]) * max(
        0.0,
        first[3] - first[1],
    )
    second_area = max(0.0, second[2] - second[0]) * max(
        0.0,
        second[3] - second[1],
    )

    union = first_area + second_area - intersection
    return intersection / union if union > 0 else 0.0


def load_ground_truth(
    label_path: Path,
    image_width: int,
    image_height: int,
) -> list[tuple[float, float, float, float]]:
    boxes = []

    if not label_path.is_file():
        return boxes

    for line in label_path.read_text(encoding="utf-8").splitlines():
        content = line.strip()

        if not content:
            continue

        values = content.split()

        if len(values) != 5:
            raise ValueError(
                f"Invalid YOLO annotation in {label_path}: {content}"
            )

        _, x_center, y_center, width, height = map(float, values)

        box_width = width * image_width
        box_height = height * image_height
        center_x = x_center * image_width
        center_y = y_center * image_height

        boxes.append(
            (
                center_x - box_width / 2,
                center_y - box_height / 2,
                center_x + box_width / 2,
                center_y + box_height / 2,
            )
        )

    return boxes


def prediction_boxes(
    detections: list[dict],
) -> list[tuple[float, float, float, float]]:
    boxes = []

    for detection in detections:
        box = detection["bbox"]
        boxes.append(
            (
                float(box["x_min"]),
                float(box["y_min"]),
                float(box["x_max"]),
                float(box["y_max"]),
            )
        )

    return boxes


def update_counts(
    counts: dict[str, int],
    predictions: list[tuple[float, float, float, float]],
    ground_truth: list[tuple[float, float, float, float]],
    match_iou: float,
) -> None:
    matched_truth: set[int] = set()

    for prediction in predictions:
        best_index = None
        best_iou = 0.0

        for index, truth in enumerate(ground_truth):
            if index in matched_truth:
                continue

            score = intersection_over_union(prediction, truth)

            if score > best_iou:
                best_iou = score
                best_index = index

        if best_index is not None and best_iou >= match_iou:
            counts["true_positive"] += 1
            matched_truth.add(best_index)
        else:
            counts["false_positive"] += 1

    counts["false_negative"] += (
        len(ground_truth) - len(matched_truth)
    )


def calculate_metrics(counts: dict[str, int]) -> dict[str, float | int]:
    true_positive = counts["true_positive"]
    false_positive = counts["false_positive"]
    false_negative = counts["false_negative"]

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative

    precision = (
        true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )
    recall = (
        true_positive / recall_denominator
        if recall_denominator
        else 0.0
    )
    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        **counts,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1_score, 4),
    }


def main() -> None:
    args = parse_arguments()
    dataset = args.dataset.expanduser().resolve()
    images_directory = dataset / "images/val"
    labels_directory = dataset / "labels/val"

    image_paths = sorted(
        path
        for path in images_directory.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No validation images found in {images_directory}"
        )

    detector = YOLODetector(
        str(args.model),
        confidence_threshold=args.confidence,
    )
    preprocessor = SonarPreprocessor()

    raw_counts = {
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
    }
    enhanced_counts = {
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
    }

    raw_time = 0.0
    enhanced_time = 0.0

    for index, image_path in enumerate(image_paths, start=1):
        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(f"Unreadable image: {image_path}")

        height, width = image.shape[:2]
        truth = load_ground_truth(
            labels_directory / f"{image_path.stem}.txt",
            width,
            height,
        )

        started = time.perf_counter()
        raw_detections = detector.detect(image)
        raw_time += time.perf_counter() - started

        enhanced = preprocessor.pipeline(image)

        started = time.perf_counter()
        enhanced_detections = detector.detect(enhanced)
        enhanced_time += time.perf_counter() - started

        update_counts(
            raw_counts,
            prediction_boxes(raw_detections),
            truth,
            args.match_iou,
        )
        update_counts(
            enhanced_counts,
            prediction_boxes(enhanced_detections),
            truth,
            args.match_iou,
        )

        print(f"Processed {index}/{len(image_paths)}", end="\r")

    raw_metrics = calculate_metrics(raw_counts)
    enhanced_metrics = calculate_metrics(enhanced_counts)

    raw_metrics["mean_inference_ms"] = round(
        raw_time / len(image_paths) * 1000,
        2,
    )
    enhanced_metrics["mean_inference_ms"] = round(
        enhanced_time / len(image_paths) * 1000,
        2,
    )

    report = {
        "dataset": str(dataset),
        "model": str(args.model.expanduser().resolve()),
        "images": len(image_paths),
        "confidence_threshold": args.confidence,
        "matching_iou": args.match_iou,
        "raw": raw_metrics,
        "preprocessed": enhanced_metrics,
    }

    output_directory = PROJECT_ROOT / "runs/preprocessing_evaluation"
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = output_directory / "comparison.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(" " * 50, end="\r")
    print("=" * 64)
    print("NEZA AI — PREPROCESSING VALIDATION COMPARISON")
    print("=" * 64)

    for name, metrics in (
        ("RAW IMAGES", raw_metrics),
        ("PREPROCESSED IMAGES", enhanced_metrics),
    ):
        print(f"\n{name}")
        print(f"True positives:   {metrics['true_positive']}")
        print(f"False positives:  {metrics['false_positive']}")
        print(f"False negatives:  {metrics['false_negative']}")
        print(f"Precision:        {metrics['precision']:.4f}")
        print(f"Recall:           {metrics['recall']:.4f}")
        print(f"F1-score:         {metrics['f1_score']:.4f}")
        print(
            "Mean inference:   "
            f"{metrics['mean_inference_ms']:.2f} ms"
        )

    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
