"""Validate the prepared UATD YOLO detection dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = (
    PROJECT_ROOT / "ml_pipeline/data/processed/uatd_yolo"
)

CLASS_NAMES = {
    0: "ball",
    1: "circle_cage",
    2: "cube",
    3: "cylinder",
    4: "human_body",
    5: "metal_bucket",
    6: "plane",
    7: "rov",
    8: "square_cage",
    9: "tyre",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    return parser.parse_args()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_manifest(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def validate_label(
    label_path: Path,
) -> tuple[Counter[int], list[str]]:
    counts = Counter()
    problems = []

    for line_number, line in enumerate(
        label_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        content = line.strip()

        if not content:
            continue

        values = content.split()

        if len(values) != 5:
            problems.append(
                f"{label_path}:{line_number}: "
                f"expected 5 values, found {len(values)}"
            )
            continue

        try:
            class_id = int(values[0])
            x_center, y_center, width, height = (
                float(value)
                for value in values[1:]
            )
        except ValueError:
            problems.append(
                f"{label_path}:{line_number}: "
                "contains non-numeric values"
            )
            continue

        if class_id not in CLASS_NAMES:
            problems.append(
                f"{label_path}:{line_number}: "
                f"invalid class ID {class_id}"
            )
            continue

        if not all(
            0 <= value <= 1
            for value in (
                x_center,
                y_center,
                width,
                height,
            )
        ):
            problems.append(
                f"{label_path}:{line_number}: "
                "value outside the 0–1 range"
            )
            continue

        if width <= 0 or height <= 0:
            problems.append(
                f"{label_path}:{line_number}: "
                "box has zero area"
            )
            continue

        xmin = x_center - width / 2
        ymin = y_center - height / 2
        xmax = x_center + width / 2
        ymax = y_center + height / 2

        tolerance = 0.00001

        if (
            xmin < -tolerance
            or ymin < -tolerance
            or xmax > 1 + tolerance
            or ymax > 1 + tolerance
        ):
            problems.append(
                f"{label_path}:{line_number}: "
                "box extends outside the image"
            )
            continue

        counts[class_id] += 1

    return counts, problems


def main() -> None:
    args = parse_arguments()
    dataset = args.dataset.expanduser().resolve()

    manifest_path = dataset / "manifest.csv"
    yaml_path = dataset / "dataset.yaml"
    preparation_report_path = (
        dataset / "preparation_report.json"
    )

    for path in (
        manifest_path,
        yaml_path,
        preparation_report_path,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    manifest_rows = load_manifest(manifest_path)
    manifest_by_split = Counter(
        row["split"]
        for row in manifest_rows
    )

    dataset_config = yaml.safe_load(
        yaml_path.read_text(encoding="utf-8")
    )

    problems = []
    split_statistics = {}
    hashes: defaultdict[str, list[dict]] = defaultdict(list)

    for split in ("train", "val", "test"):
        images_directory = dataset / "images" / split
        labels_directory = dataset / "labels" / split

        image_paths = sorted(
            path
            for path in images_directory.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".bmp"
        )
        label_paths = sorted(
            path
            for path in labels_directory.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".txt"
        )

        image_stems = {
            path.stem
            for path in image_paths
        }
        label_stems = {
            path.stem
            for path in label_paths
        }

        missing_labels = sorted(
            image_stems - label_stems
        )
        missing_images = sorted(
            label_stems - image_stems
        )

        for stem in missing_labels:
            problems.append(
                f"{split}: missing label for {stem}"
            )

        for stem in missing_images:
            problems.append(
                f"{split}: missing image for {stem}"
            )

        if manifest_by_split[split] != len(image_paths):
            problems.append(
                f"{split}: manifest contains "
                f"{manifest_by_split[split]} rows but "
                f"{len(image_paths)} images exist"
            )

        class_counts = Counter()
        positive_images = 0
        negative_images = 0
        unreadable_images = 0

        for index, image_path in enumerate(
            image_paths,
            start=1,
        ):
            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if image is None:
                unreadable_images += 1
                problems.append(
                    f"Unreadable image: {image_path}"
                )
                continue

            digest = file_hash(image_path)
            hashes[digest].append(
                {
                    "split": split,
                    "filename": image_path.name,
                }
            )

            label_path = (
                labels_directory
                / f"{image_path.stem}.txt"
            )

            if not label_path.is_file():
                continue

            counts, label_problems = validate_label(
                label_path
            )
            class_counts.update(counts)
            problems.extend(label_problems)

            if sum(counts.values()) > 0:
                positive_images += 1
            else:
                negative_images += 1

            if index % 500 == 0:
                print(
                    f"{split}: validated "
                    f"{index}/{len(image_paths)}...",
                    flush=True,
                )

        split_statistics[split] = {
            "images": len(image_paths),
            "labels": len(label_paths),
            "positive_images": positive_images,
            "negative_images": negative_images,
            "unreadable_images": unreadable_images,
            "instances": {
                CLASS_NAMES[class_id]: class_counts[class_id]
                for class_id in CLASS_NAMES
            },
        }

    cross_split_duplicates = []

    for digest, records in hashes.items():
        record_splits = {
            record["split"]
            for record in records
        }

        if len(record_splits) > 1:
            cross_split_duplicates.append(
                {
                    "sha256": digest,
                    "records": records,
                }
            )

    if cross_split_duplicates:
        problems.append(
            f"Found {len(cross_split_duplicates)} exact "
            "image duplicates across splits"
        )

    expected_names = {
        class_id: class_name
        for class_id, class_name in CLASS_NAMES.items()
    }

    configured_names = {
        int(class_id): class_name
        for class_id, class_name
        in dataset_config["names"].items()
    }

    if configured_names != expected_names:
        problems.append(
            "dataset.yaml class mapping is incorrect"
        )

    report = {
        "dataset": str(dataset),
        "splits": split_statistics,
        "manifest_rows": len(manifest_rows),
        "cross_split_duplicate_groups": (
            cross_split_duplicates
        ),
        "problems": problems,
    }

    output_directory = PROJECT_ROOT / "runs/dataset_audits"
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = output_directory / "uatd_validation.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("NEZA AI — PREPARED UATD VALIDATION")
    print("=" * 72)

    for split in ("train", "val", "test"):
        values = split_statistics[split]

        print(f"\n{split.upper()}")
        print(f"Images:          {values['images']}")
        print(f"Labels:          {values['labels']}")
        print(f"Positive images: {values['positive_images']}")
        print(f"Negative images: {values['negative_images']}")
        print(f"Unreadable:      {values['unreadable_images']}")
        print("Instances:")

        for class_name, count in values["instances"].items():
            print(f"  {class_name:20} {count:6d}")

    print(
        "\nCross-split duplicate groups: "
        f"{len(cross_split_duplicates)}"
    )
    print(f"Problems: {len(problems)}")
    print(
        "RESULT: "
        f"{'PASSED' if not problems else 'FAILED'}"
    )
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
