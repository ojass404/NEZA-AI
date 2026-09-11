"""Validate the prepared Marine Debris YOLO segmentation dataset."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATASET = (
    PROJECT_ROOT
    / "ml_pipeline/data/processed/marine_debris_fls_yolo_seg"
)

DEFAULT_SOURCE_MASKS = (
    PROJECT_ROOT
    / "ml_pipeline/data/raw/marine-debris-fls-datasets/"
    / "md_fls_dataset/data/watertank-segmentation/Masks"
)

CLASS_NAMES = {
    0: "bottle",
    1: "can",
    2: "chain",
    3: "drink_carton",
    4: "hook",
    5: "propeller",
    6: "shampoo_bottle",
    7: "standing_bottle",
    8: "tire",
    9: "valve",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    parser.add_argument(
        "--source-masks",
        type=Path,
        default=DEFAULT_SOURCE_MASKS,
    )
    return parser.parse_args()


def parse_label(
    label_path: Path,
    image_width: int,
    image_height: int,
) -> tuple[list[tuple[int, np.ndarray]], list[str]]:
    polygons = []
    problems = []

    for line_number, line in enumerate(
        label_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        content = line.strip()

        if not content:
            continue

        values = content.split()

        if len(values) < 7:
            problems.append(
                f"{label_path}:{line_number}: "
                "polygon has fewer than three points"
            )
            continue

        if (len(values) - 1) % 2 != 0:
            problems.append(
                f"{label_path}:{line_number}: "
                "coordinate count is not even"
            )
            continue

        try:
            class_id = int(values[0])
            coordinates = [
                float(value)
                for value in values[1:]
            ]
        except ValueError:
            problems.append(
                f"{label_path}:{line_number}: "
                "contains a non-numeric value"
            )
            continue

        if class_id not in CLASS_NAMES:
            problems.append(
                f"{label_path}:{line_number}: "
                f"invalid class ID {class_id}"
            )
            continue

        if any(
            coordinate < 0 or coordinate > 1
            for coordinate in coordinates
        ):
            problems.append(
                f"{label_path}:{line_number}: "
                "coordinate outside 0–1"
            )
            continue

        points = np.array(
            [
                [
                    round(coordinates[index] * image_width),
                    round(coordinates[index + 1] * image_height),
                ]
                for index in range(0, len(coordinates), 2)
            ],
            dtype=np.int32,
        )

        points[:, 0] = np.clip(
            points[:, 0],
            0,
            image_width - 1,
        )
        points[:, 1] = np.clip(
            points[:, 1],
            0,
            image_height - 1,
        )

        if cv2.contourArea(points) <= 0:
            problems.append(
                f"{label_path}:{line_number}: "
                "polygon has zero area"
            )
            continue

        polygons.append((class_id, points))

    return polygons, problems


def load_manifest(
    manifest_path: Path,
) -> dict[str, dict[str, str]]:
    with manifest_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return {
            row["filename"]: row
            for row in csv.DictReader(file)
        }


def main() -> None:
    args = parse_arguments()
    dataset = args.dataset.expanduser().resolve()
    source_masks = args.source_masks.expanduser().resolve()

    manifest_path = dataset / "manifest.csv"
    dataset_yaml = dataset / "dataset.yaml"

    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    if not dataset_yaml.is_file():
        raise FileNotFoundError(dataset_yaml)

    manifest = load_manifest(manifest_path)

    all_image_names = set()
    all_label_names = set()
    split_frame_indices = {}
    split_statistics = {}
    problems = []

    global_intersections = Counter()
    global_unions = Counter()

    for split in ("train", "val", "test"):
        images_directory = dataset / "images" / split
        labels_directory = dataset / "labels" / split

        image_paths = sorted(images_directory.glob("*.png"))
        label_paths = sorted(labels_directory.glob("*.txt"))

        image_stems = {
            path.stem
            for path in image_paths
        }
        label_stems = {
            path.stem
            for path in label_paths
        }

        missing_labels = sorted(image_stems - label_stems)
        missing_images = sorted(label_stems - image_stems)

        for stem in missing_labels:
            problems.append(
                f"{split}: missing label for {stem}"
            )

        for stem in missing_images:
            problems.append(
                f"{split}: missing image for {stem}"
            )

        instance_counts = Counter()
        positive_images = 0
        negative_images = 0
        frame_indices = set()

        for position, image_path in enumerate(
            image_paths,
            start=1,
        ):
            if image_path.name in all_image_names:
                problems.append(
                    f"Image appears in multiple splits: "
                    f"{image_path.name}"
                )

            all_image_names.add(image_path.name)

            manifest_row = manifest.get(image_path.name)

            if manifest_row is None:
                problems.append(
                    f"Missing manifest row: {image_path.name}"
                )
                continue

            if manifest_row["split"] != split:
                problems.append(
                    f"Manifest split mismatch: {image_path.name}"
                )

            frame_index = int(manifest_row["frame_index"])
            frame_indices.add(frame_index)

            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if image is None:
                problems.append(
                    f"Unreadable image: {image_path}"
                )
                continue

            image_height, image_width = image.shape
            label_path = (
                labels_directory
                / f"{image_path.stem}.txt"
            )

            if not label_path.is_file():
                continue

            all_label_names.add(label_path.name)

            polygons, label_problems = parse_label(
                label_path,
                image_width,
                image_height,
            )
            problems.extend(label_problems)

            if polygons:
                positive_images += 1
            else:
                negative_images += 1

            reconstructed = {
                class_id: np.zeros(
                    (image_height, image_width),
                    dtype=np.uint8,
                )
                for class_id in CLASS_NAMES
            }

            for class_id, points in polygons:
                instance_counts[class_id] += 1
                cv2.fillPoly(
                    reconstructed[class_id],
                    [points],
                    1,
                )

            source_mask_path = (
                source_masks / image_path.name
            )
            source_mask = cv2.imread(
                str(source_mask_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if source_mask is None:
                problems.append(
                    f"Missing source mask: {source_mask_path}"
                )
                continue

            if source_mask.shape != image.shape:
                problems.append(
                    f"Source mask size mismatch: "
                    f"{image_path.name}"
                )
                continue

            for class_id in CLASS_NAMES:
                source_class_id = class_id + 1
                truth = source_mask == source_class_id
                prediction = reconstructed[class_id] > 0

                global_intersections[class_id] += int(
                    np.logical_and(
                        truth,
                        prediction,
                    ).sum()
                )
                global_unions[class_id] += int(
                    np.logical_or(
                        truth,
                        prediction,
                    ).sum()
                )

            if position % 250 == 0:
                print(
                    f"{split}: validated "
                    f"{position}/{len(image_paths)}...",
                    flush=True,
                )

        split_frame_indices[split] = frame_indices

        split_statistics[split] = {
            "images": len(image_paths),
            "labels": len(label_paths),
            "positive_images": positive_images,
            "negative_images": negative_images,
            "minimum_frame": (
                min(frame_indices)
                if frame_indices
                else None
            ),
            "maximum_frame": (
                max(frame_indices)
                if frame_indices
                else None
            ),
            "instances": {
                CLASS_NAMES[class_id]: instance_counts[class_id]
                for class_id in CLASS_NAMES
            },
        }

    leakage = {}

    for first, second in (
        ("train", "val"),
        ("train", "test"),
        ("val", "test"),
    ):
        overlap = (
            split_frame_indices[first]
            & split_frame_indices[second]
        )
        leakage[f"{first}_vs_{second}"] = sorted(overlap)

        if overlap:
            problems.append(
                f"Frame leakage between {first} and {second}"
            )

    class_iou = {}

    for class_id, class_name in CLASS_NAMES.items():
        union = global_unions[class_id]
        intersection = global_intersections[class_id]

        class_iou[class_name] = (
            round(intersection / union, 6)
            if union
            else None
        )

    report = {
        "dataset": str(dataset),
        "splits": split_statistics,
        "leakage": leakage,
        "polygon_reconstruction_iou": class_iou,
        "problems": problems,
    }

    output_directory = PROJECT_ROOT / "runs/dataset_audits"
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = (
        output_directory
        / "marine_debris_segmentation_validation.json"
    )
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("NEZA AI — PREPARED SEGMENTATION DATASET VALIDATION")
    print("=" * 72)

    for split in ("train", "val", "test"):
        values = split_statistics[split]

        print(f"\n{split.upper()}")
        print(f"Images:          {values['images']}")
        print(f"Labels:          {values['labels']}")
        print(f"Positive images: {values['positive_images']}")
        print(f"Negative images: {values['negative_images']}")
        print(
            "Frame range:     "
            f"{values['minimum_frame']}-"
            f"{values['maximum_frame']}"
        )

        print("Instances:")

        for class_name, count in values["instances"].items():
            print(f"  {class_name:20} {count:6d}")

    print("\nSPLIT LEAKAGE")

    for comparison, overlap in leakage.items():
        print(
            f"{comparison}: "
            f"{len(overlap)} overlapping frames"
        )

    print("\nPOLYGON RECONSTRUCTION IoU")

    for class_name, iou in class_iou.items():
        print(f"{class_name:20} {iou}")

    print(f"\nProblems: {len(problems)}")
    print(
        "RESULT: "
        f"{'PASSED' if not problems else 'FAILED'}"
    )
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
