"""Prepare Marine Debris FLS masks for YOLO instance segmentation."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SOURCE = (
    PROJECT_ROOT
    / "ml_pipeline/data/raw/marine-debris-fls-datasets/"
    / "md_fls_dataset/data/watertank-segmentation"
)

DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "ml_pipeline/data/processed/marine_debris_fls_yolo_seg"
)

SOURCE_CLASSES = {
    1: "bottle",
    2: "can",
    3: "chain",
    4: "drink_carton",
    5: "hook",
    6: "propeller",
    7: "shampoo_bottle",
    8: "standing_bottle",
    9: "tire",
    10: "valve",
}

YOLO_CLASS_IDS = {
    source_id: target_id
    for target_id, source_id in enumerate(SOURCE_CLASSES)
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--minimum-contour-area",
        type=float,
        default=5.0,
    )
    return parser.parse_args()


def frame_index(path: Path) -> int:
    try:
        return int(path.stem.rsplit("-", 1)[1])
    except (IndexError, ValueError) as error:
        raise ValueError(
            f"Could not extract frame index from {path.name}"
        ) from error


def choose_split(position: int, total: int) -> str:
    train_end = int(total * 0.70)
    validation_end = int(total * 0.85)

    if position < train_end:
        return "train"

    if position < validation_end:
        return "val"

    return "test"


def link_or_copy(source: Path, destination: Path) -> str:
    try:
        os.link(source, destination)
        return "hardlink"
    except OSError:
        shutil.copy2(source, destination)
        return "copy"


def contour_to_yolo_polygon(
    contour: np.ndarray,
    image_width: int,
    image_height: int,
) -> list[float] | None:
    perimeter = cv2.arcLength(contour, closed=True)

    approximated = cv2.approxPolyDP(
        contour,
        epsilon=max(0.5, 0.002 * perimeter),
        closed=True,
    )

    points = approximated.reshape(-1, 2)

    if len(points) < 3:
        return None

    normalized = []

    for x_coordinate, y_coordinate in points:
        normalized.extend(
            [
                min(
                    1.0,
                    max(0.0, float(x_coordinate) / image_width),
                ),
                min(
                    1.0,
                    max(0.0, float(y_coordinate) / image_height),
                ),
            ]
        )

    return normalized


def mask_to_annotations(
    mask: np.ndarray,
    minimum_contour_area: float,
) -> tuple[list[str], Counter[int]]:
    image_height, image_width = mask.shape
    annotations = []
    instance_counts: Counter[int] = Counter()

    for source_class_id in sorted(SOURCE_CLASSES):
        binary_mask = np.where(
            mask == source_class_id,
            255,
            0,
        ).astype(np.uint8)

        contours, _ = cv2.findContours(
            binary_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        target_class_id = YOLO_CLASS_IDS[source_class_id]

        for contour in contours:
            if cv2.contourArea(contour) < minimum_contour_area:
                continue

            polygon = contour_to_yolo_polygon(
                contour,
                image_width,
                image_height,
            )

            if polygon is None:
                continue

            coordinate_text = " ".join(
                f"{value:.6f}"
                for value in polygon
            )

            annotations.append(
                f"{target_class_id} {coordinate_text}"
            )
            instance_counts[source_class_id] += 1

    return annotations, instance_counts


def main() -> None:
    args = parse_arguments()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()

    images_directory = source / "Images"
    masks_directory = source / "Masks"

    if not images_directory.is_dir():
        raise FileNotFoundError(images_directory)

    if not masks_directory.is_dir():
        raise FileNotFoundError(masks_directory)

    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {output}"
        )

    image_paths = sorted(
        images_directory.glob("*.png"),
        key=frame_index,
    )

    if not image_paths:
        raise FileNotFoundError(
            f"No PNG images found in {images_directory}"
        )

    for split in ("train", "val", "test"):
        (output / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )
        (output / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

    split_counts = Counter()
    positive_counts = Counter()
    negative_counts = Counter()
    class_image_counts = {
        split: Counter()
        for split in ("train", "val", "test")
    }
    class_instance_counts = {
        split: Counter()
        for split in ("train", "val", "test")
    }

    manifest_rows = []
    storage_method = None

    for position, image_path in enumerate(image_paths):
        split = choose_split(position, len(image_paths))
        mask_path = masks_directory / image_path.name

        if not mask_path.is_file():
            raise FileNotFoundError(
                f"Matching mask not found: {mask_path}"
            )

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_GRAYSCALE,
        )
        mask = cv2.imread(
            str(mask_path),
            cv2.IMREAD_GRAYSCALE,
        )

        if image is None:
            raise ValueError(f"Unreadable image: {image_path}")

        if mask is None:
            raise ValueError(f"Unreadable mask: {mask_path}")

        if image.shape != mask.shape:
            raise ValueError(
                f"Dimension mismatch for {image_path.name}: "
                f"image={image.shape}, mask={mask.shape}"
            )

        annotation_lines, instance_counts = (
            mask_to_annotations(
                mask,
                args.minimum_contour_area,
            )
        )

        destination_image = (
            output / "images" / split / image_path.name
        )
        destination_label = (
            output
            / "labels"
            / split
            / f"{image_path.stem}.txt"
        )

        method = link_or_copy(
            image_path,
            destination_image,
        )

        if storage_method is None:
            storage_method = method
        elif storage_method != method:
            storage_method = "mixed"

        destination_label.write_text(
            "\n".join(annotation_lines)
            + ("\n" if annotation_lines else ""),
            encoding="utf-8",
        )

        split_counts[split] += 1

        if annotation_lines:
            positive_counts[split] += 1
        else:
            negative_counts[split] += 1

        source_classes = sorted(
            int(value)
            for value in np.unique(mask)
            if int(value) in SOURCE_CLASSES
        )

        for source_class_id in source_classes:
            class_image_counts[split][source_class_id] += 1

        class_instance_counts[split].update(instance_counts)

        manifest_rows.append(
            {
                "filename": image_path.name,
                "frame_index": frame_index(image_path),
                "split": split,
                "contains_target": bool(annotation_lines),
                "source_classes": ",".join(
                    str(value)
                    for value in source_classes
                ),
            }
        )

        if (position + 1) % 250 == 0:
            print(
                f"Prepared {position + 1}/{len(image_paths)}...",
                flush=True,
            )

    manifest_path = output / "manifest.csv"

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "filename",
                "frame_index",
                "split",
                "contains_target",
                "source_classes",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    class_names = {
        YOLO_CLASS_IDS[source_id]: class_name
        for source_id, class_name in SOURCE_CLASSES.items()
    }

    dataset_yaml = {
        "path": str(output),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": class_names,
    }

    dataset_yaml_path = output / "dataset.yaml"
    dataset_yaml_path.write_text(
        yaml.safe_dump(
            dataset_yaml,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    report = {
        "source": str(source),
        "output": str(output),
        "storage_method": storage_method,
        "minimum_contour_area": args.minimum_contour_area,
        "splits": {},
    }

    for split in ("train", "val", "test"):
        report["splits"][split] = {
            "images": split_counts[split],
            "positive_images": positive_counts[split],
            "background_or_wall_only_images": (
                negative_counts[split]
            ),
            "class_image_counts": {
                SOURCE_CLASSES[class_id]: (
                    class_image_counts[split][class_id]
                )
                for class_id in SOURCE_CLASSES
            },
            "class_instance_counts": {
                SOURCE_CLASSES[class_id]: (
                    class_instance_counts[split][class_id]
                )
                for class_id in SOURCE_CLASSES
            },
        }

    report_path = output / "preparation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("MARINE DEBRIS FLS — YOLO SEGMENTATION PREPARATION")
    print("=" * 72)
    print(f"Source:         {source}")
    print(f"Output:         {output}")
    print(f"Storage method: {storage_method}")
    print(f"Dataset YAML:   {dataset_yaml_path}")
    print(f"Manifest:       {manifest_path}")
    print(f"Report:         {report_path}")

    for split in ("train", "val", "test"):
        print(
            f"{split}: "
            f"{split_counts[split]} images | "
            f"{positive_counts[split]} target-positive | "
            f"{negative_counts[split]} wall/background-only"
        )


if __name__ == "__main__":
    main()
