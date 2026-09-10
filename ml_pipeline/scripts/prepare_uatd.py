"""Prepare the official UATD splits for YOLO object detection."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = PROJECT_ROOT / "ml_pipeline/data/raw/uatd"
DEFAULT_OUTPUT = PROJECT_ROOT / "ml_pipeline/data/processed/uatd_yolo"

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

CLASS_IDS = {
    class_name: class_id
    for class_id, class_name in CLASS_NAMES.items()
}

SOURCE_SPLITS = {
    "training": "train",
    "test_1": "val",
    "test_2": "test",
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
    return parser.parse_args()


def normalized_class_name(value: str) -> str:
    return "_".join(value.strip().lower().split())


def files_by_stem(
    root: Path,
    suffix: str,
) -> dict[str, Path]:
    files = {}

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() != suffix:
            continue

        if path.stem in files:
            raise ValueError(
                f"Duplicate filename stem in {root}: {path.stem}"
            )

        files[path.stem] = path

    return files


def parse_xml(
    xml_path: Path,
    image_width: int,
    image_height: int,
) -> tuple[list[dict], list[str]]:
    root = ET.parse(xml_path).getroot()
    objects = []
    problems = []

    xml_width = int(
        float(
            root.findtext(
                "size/width",
                default=str(image_width),
            )
        )
    )
    xml_height = int(
        float(
            root.findtext(
                "size/height",
                default=str(image_height),
            )
        )
    )

    if (
        xml_width != image_width
        or xml_height != image_height
    ):
        problems.append(
            "annotation dimensions do not match the image"
        )

    for object_element in root.findall("object"):
        source_name = object_element.findtext(
            "name",
            default="",
        )
        class_name = normalized_class_name(source_name)

        if class_name not in CLASS_IDS:
            problems.append(
                f"unsupported class: {source_name}"
            )
            continue

        box = object_element.find("bndbox")

        if box is None:
            problems.append(
                f"{class_name}: missing bounding box"
            )
            continue

        try:
            xmin = float(box.findtext("xmin", default="nan"))
            ymin = float(box.findtext("ymin", default="nan"))
            xmax = float(box.findtext("xmax", default="nan"))
            ymax = float(box.findtext("ymax", default="nan"))
        except ValueError:
            problems.append(
                f"{class_name}: non-numeric bounding box"
            )
            continue

        valid = (
            xmin >= 0
            and ymin >= 0
            and xmax > xmin
            and ymax > ymin
            and xmax <= image_width
            and ymax <= image_height
        )

        if not valid:
            problems.append(
                f"{class_name}: invalid box "
                f"{xmin},{ymin},{xmax},{ymax}"
            )
            continue

        objects.append(
            {
                "class_name": class_name,
                "class_id": CLASS_IDS[class_name],
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
        )

    return objects, problems


def object_to_yolo(
    object_data: dict,
    image_width: int,
    image_height: int,
) -> str:
    xmin = object_data["xmin"]
    ymin = object_data["ymin"]
    xmax = object_data["xmax"]
    ymax = object_data["ymax"]

    box_width = xmax - xmin
    box_height = ymax - ymin
    center_x = xmin + box_width / 2
    center_y = ymin + box_height / 2

    normalized = (
        center_x / image_width,
        center_y / image_height,
        box_width / image_width,
        box_height / image_height,
    )

    return (
        f"{object_data['class_id']} "
        + " ".join(
            f"{value:.6f}"
            for value in normalized
        )
    )


def link_or_copy(
    source: Path,
    destination: Path,
) -> str:
    try:
        os.link(source, destination)
        return "hardlink"
    except OSError:
        shutil.copy2(source, destination)
        return "copy"


def main() -> None:
    args = parse_arguments()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()

    if not source.is_dir():
        raise FileNotFoundError(source)

    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {output}"
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
    split_object_counts = {
        split: Counter()
        for split in ("train", "val", "test")
    }
    excluded_records = []
    manifest_rows = []
    storage_method = None

    # Exact duplicate images detected across official UATD splits.
    # Keep the training copy and, for the val/test duplicate, keep val.
    cross_split_duplicate_exclusions = {
        ("test_1", "00141"),
        ("test_2", "00071"),
        ("test_2", "00277"),
    }

    for source_section, output_split in SOURCE_SPLITS.items():
        matching_directories = [
            path
            for path in source.iterdir()
            if path.is_dir()
            and source_section in path.name.lower()
        ]

        if len(matching_directories) != 1:
            raise FileNotFoundError(
                f"Expected one directory matching "
                f"{source_section!r} inside {source}; "
                f"found: {matching_directories}"
            )

        section_directory = matching_directories[0]

        images = files_by_stem(section_directory, ".bmp")
        annotations = files_by_stem(
            section_directory,
            ".xml",
        )

        missing_annotations = set(images) - set(annotations)
        missing_images = set(annotations) - set(images)

        if missing_annotations:
            raise ValueError(
                f"{source_section} has images without XML: "
                f"{sorted(missing_annotations)[:10]}"
            )

        if missing_images:
            raise ValueError(
                f"{source_section} has XML without images: "
                f"{sorted(missing_images)[:10]}"
            )

        for position, stem in enumerate(
            sorted(images),
            start=1,
        ):
            image_path = images[stem]
            xml_path = annotations[stem]

            if (
                source_section,
                stem,
            ) in cross_split_duplicate_exclusions:
                excluded_records.append(
                    {
                        "source_section": source_section,
                        "stem": stem,
                        "reason": (
                            "exact duplicate image across "
                            "official dataset splits"
                        ),
                    }
                )
                continue

            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if image is None:
                excluded_records.append(
                    {
                        "source_section": source_section,
                        "stem": stem,
                        "reason": "unreadable image",
                    }
                )
                continue

            image_height, image_width = image.shape

            try:
                objects, problems = parse_xml(
                    xml_path,
                    image_width,
                    image_height,
                )
            except ET.ParseError as error:
                objects = []
                problems = [f"malformed XML: {error}"]

            if problems:
                excluded_records.append(
                    {
                        "source_section": source_section,
                        "stem": stem,
                        "reason": "; ".join(problems),
                    }
                )
                continue

            destination_image = (
                output
                / "images"
                / output_split
                / image_path.name
            )
            destination_label = (
                output
                / "labels"
                / output_split
                / f"{stem}.txt"
            )

            method = link_or_copy(
                image_path,
                destination_image,
            )

            if storage_method is None:
                storage_method = method
            elif storage_method != method:
                storage_method = "mixed"

            label_lines = [
                object_to_yolo(
                    object_data,
                    image_width,
                    image_height,
                )
                for object_data in objects
            ]

            destination_label.write_text(
                "\n".join(label_lines)
                + ("\n" if label_lines else ""),
                encoding="utf-8",
            )

            split_counts[output_split] += 1

            for object_data in objects:
                split_object_counts[output_split][
                    object_data["class_name"]
                ] += 1

            manifest_rows.append(
                {
                    "prepared_image": image_path.name,
                    "split": output_split,
                    "source_section": source_section,
                    "source_image": str(image_path),
                    "source_annotation": str(xml_path),
                    "width": image_width,
                    "height": image_height,
                    "object_count": len(objects),
                    "classes": ",".join(
                        sorted(
                            {
                                object_data["class_name"]
                                for object_data in objects
                            }
                        )
                    ),
                }
            )

            if position % 500 == 0:
                print(
                    f"{source_section}: processed "
                    f"{position}/{len(images)}...",
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
                "prepared_image",
                "split",
                "source_section",
                "source_image",
                "source_annotation",
                "width",
                "height",
                "object_count",
                "classes",
            ],
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    dataset_yaml = {
        "path": str(output),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": CLASS_NAMES,
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
        "splits": {
            split: {
                "images": split_counts[split],
                "objects": dict(
                    sorted(
                        split_object_counts[split].items()
                    )
                ),
            }
            for split in ("train", "val", "test")
        },
        "excluded_images": excluded_records,
    }

    report_path = output / "preparation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("NEZA AI — UATD YOLO PREPARATION")
    print("=" * 72)
    print(f"Source:          {source}")
    print(f"Output:          {output}")
    print(f"Storage method:  {storage_method}")
    print(f"Dataset YAML:    {dataset_yaml_path}")
    print(f"Manifest:        {manifest_path}")
    print(f"Report:          {report_path}")
    print(f"Excluded images: {len(excluded_records)}")

    for split in ("train", "val", "test"):
        print(
            f"{split}: "
            f"{split_counts[split]} images | "
            f"{sum(split_object_counts[split].values())} objects"
        )


if __name__ == "__main__":
    main()
