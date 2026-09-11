#!/usr/bin/env python3
"""Prepare SubPipe Mini HF/LF SSS data for quick YOLO training."""

import csv
import json
import os
import shutil
from collections import Counter
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_ROOT = Path(
    "/Users/ojasmahajan/Public/Projects/NEZA-AI/ml_pipeline/data/raw/subpipe_mini/DATA"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "ml_pipeline"
    / "data"
    / "processed"
    / "subpipe_mini_yolo"
)

FREQUENCIES = {
    "hf": SOURCE_ROOT / "SSS_HF_images",
    "lf": SOURCE_ROOT / "SSS_LF_images",
}

IMAGE_EXTENSIONS = {
    ".pbm",
    ".png",
    ".jpg",
    ".jpeg",
}

SPLIT_RATIOS = {
    "train": 0.70,
    "val": 0.15,
    "test": 0.15,
}


def locate_directory(
    root: Path,
    required_name: str,
) -> Path:
    matches = [
        path
        for path in root.rglob("*")
        if path.is_dir()
        and path.name.lower() == required_name.lower()
    ]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected one {required_name!r} directory "
            f"inside {root}; found {matches}"
        )

    return matches[0]


def collect_images(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def split_records(
    records: list[Path],
) -> dict[str, list[Path]]:
    total = len(records)
    train_end = int(total * SPLIT_RATIOS["train"])
    val_end = train_end + int(
        total * SPLIT_RATIOS["val"]
    )

    return {
        "train": records[:train_end],
        "val": records[train_end:val_end],
        "test": records[val_end:],
    }


def validate_label(path: Path) -> tuple[int, set[int]]:
    if not path.is_file():
        return 0, set()

    instance_count = 0
    class_ids: set[int] = set()

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = line.strip()

        if not line:
            continue

        values = line.split()

        if len(values) != 5:
            raise ValueError(
                f"{path}:{line_number}: expected five "
                f"YOLO values, received {len(values)}"
            )

        class_id = int(values[0])
        coordinates = [float(value) for value in values[1:]]

        if class_id != 0:
            raise ValueError(
                f"{path}:{line_number}: unexpected "
                f"class ID {class_id}"
            )

        if not all(0.0 <= value <= 1.0 for value in coordinates):
            raise ValueError(
                f"{path}:{line_number}: coordinates "
                "must be normalized between 0 and 1"
            )

        if coordinates[2] <= 0 or coordinates[3] <= 0:
            raise ValueError(
                f"{path}:{line_number}: invalid box size"
            )

        class_ids.add(class_id)
        instance_count += 1

    return instance_count, class_ids


def create_symlink(
    source: Path,
    destination: Path,
) -> None:
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.symlink_to(source.resolve())


def main() -> None:
    if not SOURCE_ROOT.is_dir():
        raise FileNotFoundError(
            f"SubPipe DATA directory not found: {SOURCE_ROOT}"
        )

    if OUTPUT_ROOT.exists():
        if any(OUTPUT_ROOT.iterdir()):
            raise FileExistsError(
                f"Output directory is not empty: {OUTPUT_ROOT}"
            )
    else:
        OUTPUT_ROOT.mkdir(parents=True)

    for split in ("train", "val", "test"):
        (OUTPUT_ROOT / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )
        (OUTPUT_ROOT / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

    manifest_rows = []
    split_counts = Counter()
    positive_counts = Counter()
    negative_counts = Counter()
    instance_counts = Counter()

    for frequency, frequency_root in FREQUENCIES.items():
        if not frequency_root.is_dir():
            raise FileNotFoundError(frequency_root)

        image_directory = locate_directory(
            frequency_root,
            "Image",
        )
        label_directory = locate_directory(
            frequency_root,
            "YOLO_Annotation",
        )

        images = collect_images(image_directory)

        if not images:
            raise ValueError(
                f"No images found in {image_directory}"
            )

        frequency_splits = split_records(images)

        for split, split_images in frequency_splits.items():
            for image_path in split_images:
                label_path = (
                    label_directory
                    / f"{image_path.stem}.txt"
                )

                instances, class_ids = validate_label(
                    label_path
                )

                prepared_stem = (
                    f"{frequency}_{image_path.stem}"
                )

                destination_image = (
                    OUTPUT_ROOT
                    / "images"
                    / split
                    / f"{prepared_stem}.png"
                )

                destination_label = (
                    OUTPUT_ROOT
                    / "labels"
                    / split
                    / f"{prepared_stem}.txt"
                )

                image = cv2.imread(
                    str(image_path),
                    cv2.IMREAD_GRAYSCALE,
                )

                if image is None:
                    raise ValueError(
                        f"OpenCV could not read: {image_path}"
                    )

                if not cv2.imwrite(
                    str(destination_image),
                    image,
                ):
                    raise RuntimeError(
                        f"Could not write: {destination_image}"
                    )

                if label_path.is_file():
                    create_symlink(
                        label_path,
                        destination_label,
                    )
                    positive_counts[split] += 1
                else:
                    destination_label.write_text(
                        "",
                        encoding="utf-8",
                    )
                    negative_counts[split] += 1

                split_counts[split] += 1
                instance_counts[split] += instances

                manifest_rows.append(
                    {
                        "prepared_image": (
                            destination_image.name
                        ),
                        "split": split,
                        "frequency": frequency.upper(),
                        "source_image": str(
                            image_path.resolve()
                        ),
                        "source_label": (
                            str(label_path.resolve())
                            if label_path.is_file()
                            else ""
                        ),
                        "instances": instances,
                        "class_ids": ",".join(
                            str(value)
                            for value in sorted(class_ids)
                        ),
                    }
                )

    dataset_yaml = OUTPUT_ROOT / "dataset.yaml"
    dataset_yaml.write_text(
        f"path: {OUTPUT_ROOT.resolve()}\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "\n"
        "names:\n"
        "  0: submarine_pipeline\n"
        "\n"
        "nc: 1\n",
        encoding="utf-8",
    )

    manifest_path = OUTPUT_ROOT / "manifest.csv"

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
                "frequency",
                "source_image",
                "source_label",
                "instances",
                "class_ids",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    report = {
        "dataset": "SubPipeMini2",
        "task": "SSS submarine pipeline detection",
        "source": str(SOURCE_ROOT),
        "output": str(OUTPUT_ROOT),
        "storage_method": "PNG conversion with label symlinks",
        "classes": {
            "0": "submarine_pipeline",
        },
        "splits": {
            split: {
                "images": split_counts[split],
                "positive_images": positive_counts[split],
                "negative_images": negative_counts[split],
                "instances": instance_counts[split],
            }
            for split in ("train", "val", "test")
        },
    }

    report_path = OUTPUT_ROOT / "preparation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("=" * 72)
    print("NEZA AI — SUBPIPE MINI PREPARATION COMPLETED")
    print("=" * 72)
    print(f"Source:       {SOURCE_ROOT}")
    print(f"Output:       {OUTPUT_ROOT}")
    print(f"Dataset YAML: {dataset_yaml}")
    print(f"Manifest:     {manifest_path}")

    for split in ("train", "val", "test"):
        print(
            f"{split}: {split_counts[split]} images | "
            f"{positive_counts[split]} positive | "
            f"{negative_counts[split]} negative | "
            f"{instance_counts[split]} instances"
        )


if __name__ == "__main__":
    main()
