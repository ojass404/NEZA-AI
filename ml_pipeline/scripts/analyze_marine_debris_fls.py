"""Read-only integrity analysis for the Marine Debris FLS dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATASET = (
    PROJECT_ROOT
    / "ml_pipeline/data/raw/marine-debris-fls-datasets/"
    / "md_fls_dataset/data/watertank-segmentation"
)

MASK_CLASSES = {
    0: "background",
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
    11: "wall",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    return parser.parse_args()


def files_by_stem(
    directory: Path,
    suffixes: set[str],
) -> dict[str, Path]:
    return {
        path.stem: path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def parse_annotation(
    annotation_path: Path,
) -> tuple[tuple[int, int], list[dict]]:
    root = ET.parse(annotation_path).getroot()

    width = int(root.findtext("size/width", default="0"))
    height = int(root.findtext("size/height", default="0"))

    objects = []

    for item in root.findall("object"):
        name = item.findtext("name", default="unknown").strip()
        box = item.find("bndbox")

        if box is None:
            objects.append(
                {
                    "name": name,
                    "valid": False,
                    "reason": "missing bndbox",
                }
            )
            continue

        values = {}

        for key in ("x", "y", "w", "h"):
            text = box.findtext(key)

            if text is None:
                values[key] = None
            else:
                values[key] = float(text)

        valid = all(value is not None for value in values.values())

        if valid:
            x = values["x"]
            y = values["y"]
            box_width = values["w"]
            box_height = values["h"]

            valid = (
                x >= 0
                and y >= 0
                and box_width > 0
                and box_height > 0
                and x + box_width <= width
                and y + box_height <= height
            )

        objects.append(
            {
                "name": name,
                "valid": valid,
                **values,
            }
        )

    return (width, height), objects


def main() -> None:
    args = parse_arguments()
    dataset = args.dataset.expanduser().resolve()

    images_directory = dataset / "Images"
    masks_directory = dataset / "Masks"
    annotations_directory = dataset / "BoxAnnotations"

    for directory in (
        images_directory,
        masks_directory,
        annotations_directory,
    ):
        if not directory.is_dir():
            raise FileNotFoundError(
                f"Required directory not found: {directory}"
            )

    images = files_by_stem(
        images_directory,
        {".png", ".jpg", ".jpeg"},
    )
    masks = files_by_stem(masks_directory, {".png"})
    annotations = files_by_stem(
        annotations_directory,
        {".xml"},
    )

    all_stems = set(images) | set(masks) | set(annotations)

    missing_images = sorted(all_stems - set(images))
    missing_masks = sorted(all_stems - set(masks))
    missing_annotations = sorted(all_stems - set(annotations))

    unreadable_images = []
    unreadable_masks = []
    dimension_mismatches = []
    unexpected_mask_values: set[int] = set()
    mask_pixel_counts: Counter[int] = Counter()
    images_per_mask_class: Counter[int] = Counter()
    empty_masks = 0

    annotation_class_counts: Counter[str] = Counter()
    invalid_annotations = []
    annotation_dimension_mismatches = []

    hashes: defaultdict[str, list[str]] = defaultdict(list)

    for index, stem in enumerate(sorted(images), start=1):
        image_path = images[stem]
        image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        if image is None:
            unreadable_images.append(str(image_path))
            continue

        hashes[sha256(image_path)].append(stem)

        mask_path = masks.get(stem)

        if mask_path is not None:
            mask = cv2.imread(
                str(mask_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if mask is None:
                unreadable_masks.append(str(mask_path))
            else:
                if image.shape != mask.shape:
                    dimension_mismatches.append(
                        {
                            "stem": stem,
                            "image_shape": list(image.shape),
                            "mask_shape": list(mask.shape),
                        }
                    )

                values, counts = np.unique(
                    mask,
                    return_counts=True,
                )

                value_set = {
                    int(value)
                    for value in values.tolist()
                }

                unexpected_mask_values.update(
                    value_set - set(MASK_CLASSES)
                )

                for value, count in zip(values, counts):
                    mask_pixel_counts[int(value)] += int(count)

                foreground = value_set - {0}

                if foreground:
                    for value in foreground:
                        images_per_mask_class[value] += 1
                else:
                    empty_masks += 1

        annotation_path = annotations.get(stem)

        if annotation_path is not None:
            try:
                annotation_size, objects = parse_annotation(
                    annotation_path
                )
            except (ET.ParseError, ValueError) as error:
                invalid_annotations.append(
                    {
                        "stem": stem,
                        "reason": str(error),
                    }
                )
                continue

            expected_size = (image.shape[1], image.shape[0])

            if annotation_size != expected_size:
                annotation_dimension_mismatches.append(
                    {
                        "stem": stem,
                        "image_size": list(expected_size),
                        "annotation_size": list(annotation_size),
                    }
                )

            for object_data in objects:
                name = str(object_data["name"]).lower()
                annotation_class_counts[name] += 1

                if not object_data["valid"]:
                    invalid_annotations.append(
                        {
                            "stem": stem,
                            "object": object_data,
                        }
                    )

        if index % 250 == 0:
            print(
                f"Checked {index}/{len(images)} samples...",
                flush=True,
            )

    duplicate_groups = [
        stems
        for stems in hashes.values()
        if len(stems) > 1
    ]

    report = {
        "dataset": str(dataset),
        "counts": {
            "images": len(images),
            "masks": len(masks),
            "annotations": len(annotations),
            "empty_masks": empty_masks,
            "duplicate_image_groups": len(duplicate_groups),
        },
        "pairing": {
            "missing_images": missing_images,
            "missing_masks": missing_masks,
            "missing_annotations": missing_annotations,
        },
        "integrity": {
            "unreadable_images": unreadable_images,
            "unreadable_masks": unreadable_masks,
            "dimension_mismatches": dimension_mismatches,
            "annotation_dimension_mismatches": (
                annotation_dimension_mismatches
            ),
            "invalid_annotations": invalid_annotations,
            "unexpected_mask_values": sorted(
                unexpected_mask_values
            ),
        },
        "mask_classes": {
            MASK_CLASSES.get(value, f"unknown_{value}"): {
                "class_id": value,
                "pixel_count": mask_pixel_counts[value],
                "images_containing_class": (
                    images_per_mask_class[value]
                ),
            }
            for value in sorted(mask_pixel_counts)
        },
        "annotation_classes": dict(
            sorted(annotation_class_counts.items())
        ),
        "duplicate_image_groups": duplicate_groups[:100],
    }

    output_directory = PROJECT_ROOT / "runs/dataset_audits"
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = (
        output_directory / "marine_debris_fls_audit.json"
    )
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    problems = sum(
        (
            len(missing_images),
            len(missing_masks),
            len(missing_annotations),
            len(unreadable_images),
            len(unreadable_masks),
            len(dimension_mismatches),
            len(annotation_dimension_mismatches),
            len(invalid_annotations),
            len(unexpected_mask_values),
        )
    )

    print("\n" + "=" * 68)
    print("NEZA AI — MARINE DEBRIS FLS DATASET AUDIT")
    print("=" * 68)
    print(f"Images:                    {len(images)}")
    print(f"Masks:                     {len(masks)}")
    print(f"Box annotations:           {len(annotations)}")
    print(f"Missing images:            {len(missing_images)}")
    print(f"Missing masks:             {len(missing_masks)}")
    print(f"Missing annotations:       {len(missing_annotations)}")
    print(f"Unreadable images:         {len(unreadable_images)}")
    print(f"Unreadable masks:          {len(unreadable_masks)}")
    print(f"Dimension mismatches:      {len(dimension_mismatches)}")
    print(
        "Annotation size mismatch: "
        f"{len(annotation_dimension_mismatches)}"
    )
    print(f"Invalid annotations:       {len(invalid_annotations)}")
    print(f"Empty masks:               {empty_masks}")
    print(f"Duplicate image groups:    {len(duplicate_groups)}")
    print(
        "Unexpected mask values:   "
        f"{sorted(unexpected_mask_values)}"
    )

    print("\nMASK CLASS DISTRIBUTION")

    for value in sorted(mask_pixel_counts):
        class_name = MASK_CLASSES.get(
            value,
            f"unknown_{value}",
        )
        print(
            f"{value:2d} {class_name:20} "
            f"images={images_per_mask_class[value]:4d} "
            f"pixels={mask_pixel_counts[value]:12d}"
        )

    print("\nXML ANNOTATION DISTRIBUTION")

    for name, count in sorted(annotation_class_counts.items()):
        print(f"{name:25} {count:6d}")

    print(f"\nProblems detected: {problems}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
