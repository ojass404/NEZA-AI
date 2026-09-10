#!/usr/bin/env python3
"""
Prepare AI4Shipwrecks for YOLO using object-centred crops.

Positive samples:
- Locate the complete shipwreck using its segmentation mask.
- Create a square crop around the complete object.
- Add surrounding seabed context.
- Resize the crop to 640 x 640.
- Convert the mask boundary into a YOLO bounding box.

Negative samples:
- Extract one background crop from every empty-mask image.

The original dataset is never modified.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
from pathlib import Path

import cv2
import numpy as np


VALIDATION_GROUPS = {
    "DM_Wilson",
    "DR_Hanna",
}

VALIDATION_TERRAIN_GROUPS = {
    "Mischelley_Reef",
}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
}


def group_name(filename_stem: str) -> str:
    """Convert DM_Wilson_01 to DM_Wilson."""
    return re.sub(r"_\d+$", "", filename_stem)


def development_split(group: str) -> str:
    if group in VALIDATION_GROUPS:
        return "val"

    return "train"


def terrain_split(group: str) -> str:
    if group in VALIDATION_TERRAIN_GROUPS:
        return "val"

    return "train"


def square_crop(
    image: np.ndarray,
    centre_x: float,
    centre_y: float,
    side: int,
) -> tuple[np.ndarray, int, int]:
    """
    Extract a square crop.

    Areas extending outside the source image are padded with black pixels.
    Returns the crop and its original x/y starting position.
    """
    height, width = image.shape

    start_x = int(round(centre_x - side / 2))
    start_y = int(round(centre_y - side / 2))

    end_x = start_x + side
    end_y = start_y + side

    source_x1 = max(0, start_x)
    source_y1 = max(0, start_y)
    source_x2 = min(width, end_x)
    source_y2 = min(height, end_y)

    crop = np.zeros(
        (side, side),
        dtype=image.dtype,
    )

    destination_x1 = source_x1 - start_x
    destination_y1 = source_y1 - start_y

    destination_x2 = (
        destination_x1
        + source_x2
        - source_x1
    )
    destination_y2 = (
        destination_y1
        + source_y2
        - source_y1
    )

    crop[
        destination_y1:destination_y2,
        destination_x1:destination_x2,
    ] = image[
        source_y1:source_y2,
        source_x1:source_x2,
    ]

    return crop, start_x, start_y


def positive_crop(
    image: np.ndarray,
    mask: np.ndarray,
    output_size: int,
    context_scale: float,
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Create an object-centred crop and its YOLO box."""
    ys, xs = np.where(mask > 0)

    object_x1 = int(xs.min())
    object_y1 = int(ys.min())
    object_x2 = int(xs.max()) + 1
    object_y2 = int(ys.max()) + 1

    object_width = object_x2 - object_x1
    object_height = object_y2 - object_y1

    centre_x = (object_x1 + object_x2) / 2
    centre_y = (object_y1 + object_y2) / 2

    crop_side = max(
        output_size,
        math.ceil(
            max(object_width, object_height)
            * context_scale
        ),
    )

    crop, crop_start_x, crop_start_y = square_crop(
        image=image,
        centre_x=centre_x,
        centre_y=centre_y,
        side=crop_side,
    )

    relative_x1 = object_x1 - crop_start_x
    relative_y1 = object_y1 - crop_start_y
    relative_x2 = object_x2 - crop_start_x
    relative_y2 = object_y2 - crop_start_y

    relative_x1 = max(0, min(crop_side, relative_x1))
    relative_y1 = max(0, min(crop_side, relative_y1))
    relative_x2 = max(0, min(crop_side, relative_x2))
    relative_y2 = max(0, min(crop_side, relative_y2))

    box_width = relative_x2 - relative_x1
    box_height = relative_y2 - relative_y1

    yolo_centre_x = (
        relative_x1 + box_width / 2
    ) / crop_side

    yolo_centre_y = (
        relative_y1 + box_height / 2
    ) / crop_side

    yolo_width = box_width / crop_side
    yolo_height = box_height / crop_side

    resized = cv2.resize(
        crop,
        (output_size, output_size),
        interpolation=cv2.INTER_AREA,
    )

    return resized, (
        yolo_centre_x,
        yolo_centre_y,
        yolo_width,
        yolo_height,
    )


def negative_crop(
    image: np.ndarray,
    output_size: int,
    rng: random.Random,
) -> np.ndarray:
    """Extract one deterministic background crop."""
    height, width = image.shape

    if width > output_size:
        start_x = rng.randint(
            0,
            width - output_size,
        )
    else:
        start_x = 0

    if height > output_size:
        start_y = rng.randint(
            0,
            height - output_size,
        )
    else:
        start_y = 0

    centre_x = start_x + output_size / 2
    centre_y = start_y + output_size / 2

    crop, _, _ = square_crop(
        image=image,
        centre_x=centre_x,
        centre_y=centre_y,
        side=output_size,
    )

    return crop


def process_directory(
    image_dir: Path,
    mask_dir: Path,
    output_root: Path,
    split_function,
    source_category: str,
    output_size: int,
    context_scale: float,
    jpeg_quality: int,
    rng: random.Random,
    manifest_rows: list[dict],
    counters: dict,
) -> None:
    """Convert every matching image-mask pair."""
    image_paths = sorted(
        path
        for path in image_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    for image_path in image_paths:
        mask_path = mask_dir / f"{image_path.stem}.png"

        if not mask_path.exists():
            print(f"WARNING: Missing mask: {mask_path}")
            continue

        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_GRAYSCALE,
        )

        mask = cv2.imread(
            str(mask_path),
            cv2.IMREAD_GRAYSCALE,
        )

        if image is None or mask is None:
            print(f"WARNING: Unreadable pair: {image_path.name}")
            continue

        if image.shape != mask.shape:
            print(f"WARNING: Size mismatch: {image_path.name}")
            continue

        group = group_name(image_path.stem)
        split = split_function(group)
        positive = bool(np.any(mask > 0))

        if positive:
            prepared_image, yolo_box = positive_crop(
                image=image,
                mask=mask,
                output_size=output_size,
                context_scale=context_scale,
            )

            centre_x, centre_y, width, height = yolo_box

            label_text = (
                f"0 "
                f"{centre_x:.6f} "
                f"{centre_y:.6f} "
                f"{width:.6f} "
                f"{height:.6f}\n"
            )
        else:
            prepared_image = negative_crop(
                image=image,
                output_size=output_size,
                rng=rng,
            )

            label_text = ""

        output_stem = (
            f"{source_category}_"
            f"{image_path.stem}"
        )

        output_image = (
            output_root
            / "images"
            / split
            / f"{output_stem}.jpg"
        )

        output_label = (
            output_root
            / "labels"
            / split
            / f"{output_stem}.txt"
        )

        cv2.imwrite(
            str(output_image),
            prepared_image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                jpeg_quality,
            ],
        )

        output_label.write_text(
            label_text,
            encoding="utf-8",
        )

        counters[split]["total"] += 1

        if positive:
            counters[split]["positive"] += 1
        else:
            counters[split]["negative"] += 1

        manifest_rows.append(
            {
                "prepared_image": output_image.name,
                "split": split,
                "source_image": image_path.name,
                "source_group": group,
                "source_category": source_category,
                "contains_shipwreck": positive,
            }
        )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        type=Path,
        default=Path(
            "data/raw/ai4shipwrecks/"
            "_data/AI4Shipwrecks"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/processed/ai4shipwrecks_yolo_v2"
        ),
    )

    parser.add_argument(
        "--output-size",
        type=int,
        default=640,
    )

    parser.add_argument(
        "--context-scale",
        type=float,
        default=1.35,
    )

    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=90,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = parser.parse_args()

    if not args.source.exists():
        raise FileNotFoundError(
            f"Dataset not found: {args.source.resolve()}"
        )

    if args.output.exists():
        existing_files = list(args.output.rglob("*"))

        if existing_files:
            raise FileExistsError(
                f"Output is not empty: {args.output}\n"
                "Use a new output directory."
            )

    for split in ("train", "val", "test"):
        (args.output / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

        (args.output / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

    rng = random.Random(args.seed)
    manifest_rows = []

    counters = {
        split: {
            "total": 0,
            "positive": 0,
            "negative": 0,
        }
        for split in ("train", "val", "test")
    }

    process_directory(
        image_dir=args.source / "train/images",
        mask_dir=args.source / "train/labels",
        output_root=args.output,
        split_function=development_split,
        source_category="wreck",
        output_size=args.output_size,
        context_scale=args.context_scale,
        jpeg_quality=args.jpeg_quality,
        rng=rng,
        manifest_rows=manifest_rows,
        counters=counters,
    )

    process_directory(
        image_dir=args.source / "test/images",
        mask_dir=args.source / "test/labels",
        output_root=args.output,
        split_function=lambda _: "test",
        source_category="wreck",
        output_size=args.output_size,
        context_scale=args.context_scale,
        jpeg_quality=args.jpeg_quality,
        rng=rng,
        manifest_rows=manifest_rows,
        counters=counters,
    )

    process_directory(
        image_dir=args.source / "extras/terrain/images",
        mask_dir=args.source / "extras/terrain/labels",
        output_root=args.output,
        split_function=terrain_split,
        source_category="terrain",
        output_size=args.output_size,
        context_scale=args.context_scale,
        jpeg_quality=args.jpeg_quality,
        rng=rng,
        manifest_rows=manifest_rows,
        counters=counters,
    )

    manifest_path = args.output / "manifest.csv"

    with manifest_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "prepared_image",
                "split",
                "source_image",
                "source_group",
                "source_category",
                "contains_shipwreck",
            ],
        )

        writer.writeheader()
        writer.writerows(manifest_rows)

    dataset_yaml = args.output / "dataset.yaml"

    dataset_yaml.write_text(
        f"path: {args.output.resolve()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "\n"
        "names:\n"
        "  0: shipwreck\n"
        "\n"
        "nc: 1\n",
        encoding="utf-8",
    )

    print("\nDataset preparation completed.")
    print(f"Output: {args.output.resolve()}")
    print(f"Dataset configuration: {dataset_yaml.resolve()}")

    for split in ("train", "val", "test"):
        values = counters[split]

        print(
            f"{split}: "
            f"{values['total']} total | "
            f"{values['positive']} positive | "
            f"{values['negative']} negative"
        )


if __name__ == "__main__":
    main()