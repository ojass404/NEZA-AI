#!/usr/bin/env python3
"""Validate the prepared AI4Shipwrecks YOLO dataset."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import cv2


def validate_split(
    dataset_root: Path,
    split: str,
    image_size: int,
) -> tuple[bool, dict]:
    image_dir = dataset_root / "images" / split
    label_dir = dataset_root / "labels" / split

    images = {
        path.stem: path
        for path in image_dir.glob("*.jpg")
    }

    labels = {
        path.stem: path
        for path in label_dir.glob("*.txt")
    }

    problems = []
    positive = 0
    negative = 0

    missing_labels = sorted(set(images) - set(labels))
    missing_images = sorted(set(labels) - set(images))

    for stem in missing_labels:
        problems.append(f"Missing label: {stem}")

    for stem in missing_images:
        problems.append(f"Missing image: {stem}")

    for stem in sorted(set(images) & set(labels)):
        image = cv2.imread(str(images[stem]))

        if image is None:
            problems.append(f"Unreadable image: {images[stem].name}")
            continue

        if image.shape[:2] != (image_size, image_size):
            problems.append(
                f"Incorrect dimensions: {images[stem].name} "
                f"{image.shape[:2]}"
            )

        content = labels[stem].read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            negative += 1
            continue

        positive += 1

        for line_number, line in enumerate(
            content.splitlines(),
            start=1,
        ):
            parts = line.split()

            if len(parts) != 5:
                problems.append(
                    f"Malformed label: {labels[stem].name}:"
                    f"{line_number}"
                )
                continue

            try:
                class_id = int(parts[0])
                centre_x, centre_y, width, height = [
                    float(value)
                    for value in parts[1:]
                ]
            except ValueError:
                problems.append(
                    f"Non-numeric label: {labels[stem].name}:"
                    f"{line_number}"
                )
                continue

            if class_id != 0:
                problems.append(
                    f"Unexpected class {class_id}: "
                    f"{labels[stem].name}"
                )

            values = (centre_x, centre_y, width, height)

            if not all(0.0 <= value <= 1.0 for value in values):
                problems.append(
                    f"Value outside YOLO range: "
                    f"{labels[stem].name}"
                )

            if width <= 0 or height <= 0:
                problems.append(
                    f"Zero-sized box: {labels[stem].name}"
                )

            x1 = centre_x - width / 2
            y1 = centre_y - height / 2
            x2 = centre_x + width / 2
            y2 = centre_y + height / 2

            tolerance = 1e-5

            if (
                x1 < -tolerance
                or y1 < -tolerance
                or x2 > 1 + tolerance
                or y2 > 1 + tolerance
            ):
                problems.append(
                    f"Box outside image: {labels[stem].name}"
                )

    statistics = {
        "images": len(images),
        "labels": len(labels),
        "positive": positive,
        "negative": negative,
        "problems": problems,
    }

    return not problems, statistics


def validate_group_leakage(
    manifest_path: Path,
) -> tuple[bool, list[str]]:
    groups = defaultdict(set)
    problems = []

    if not manifest_path.exists():
        return False, ["manifest.csv is missing"]

    with manifest_path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        for row in csv.DictReader(file):
            groups[row["split"]].add(
                row["source_group"]
            )

    comparisons = (
        ("train", "val"),
        ("train", "test"),
        ("val", "test"),
    )

    for first, second in comparisons:
        overlap = groups[first] & groups[second]

        if overlap:
            problems.append(
                f"Group leakage between {first} and {second}: "
                f"{sorted(overlap)}"
            )
        else:
            print(f"{first} vs {second}: no overlap")

    return not problems, problems


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "data/processed/ai4shipwrecks_yolo_v2"
        ),
    )

    parser.add_argument(
        "--image-size",
        type=int,
        default=640,
    )

    args = parser.parse_args()

    if not args.dataset.exists():
        raise FileNotFoundError(
            f"Dataset not found: {args.dataset.resolve()}"
        )

    dataset_valid = True

    print("=" * 60)
    print("NEZA AI — DATASET VALIDATION")
    print("=" * 60)

    for split in ("train", "val", "test"):
        split_valid, statistics = validate_split(
            dataset_root=args.dataset,
            split=split,
            image_size=args.image_size,
        )

        print(f"\n{split.upper()}")
        print(f"Images:     {statistics['images']}")
        print(f"Labels:     {statistics['labels']}")
        print(f"Positive:   {statistics['positive']}")
        print(f"Negative:   {statistics['negative']}")
        print(f"Problems:   {len(statistics['problems'])}")

        for problem in statistics["problems"][:10]:
            print(f"  - {problem}")

        dataset_valid = dataset_valid and split_valid

    print("\nGROUP LEAKAGE")

    leakage_valid, leakage_problems = validate_group_leakage(
        args.dataset / "manifest.csv"
    )

    for problem in leakage_problems:
        print(f"  - {problem}")

    dataset_valid = dataset_valid and leakage_valid

    size_bytes = sum(
        path.stat().st_size
        for path in args.dataset.rglob("*")
        if path.is_file()
    )

    print(
        f"\nDataset size: "
        f"{size_bytes / (1024 ** 2):.2f} MB"
    )

    print("\n" + "=" * 60)

    if dataset_valid:
        print("RESULT: PASSED")
    else:
        print("RESULT: FAILED")
        raise SystemExit(1)


if __name__ == "__main__":
    main()