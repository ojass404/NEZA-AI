"""Read-only integrity and class analysis for the UATD dataset."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = PROJECT_ROOT / "ml_pipeline/data/raw/uatd"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    return parser.parse_args()


def section_name(path: Path, dataset: Path) -> str:
    relative_parts = path.relative_to(dataset).parts

    if not relative_parts:
        return "unknown"

    first_part = relative_parts[0].lower()

    if "training" in first_part:
        return "training"
    if "test_1" in first_part or "test1" in first_part:
        return "test_1"
    if "test_2" in first_part or "test2" in first_part:
        return "test_2"

    return first_part


def parse_box(
    box: ET.Element,
) -> tuple[float, float, float, float] | None:
    xmin = box.findtext("xmin")
    ymin = box.findtext("ymin")
    xmax = box.findtext("xmax")
    ymax = box.findtext("ymax")

    if all(
        value is not None
        for value in (xmin, ymin, xmax, ymax)
    ):
        return (
            float(xmin),
            float(ymin),
            float(xmax),
            float(ymax),
        )

    x_value = box.findtext("x")
    y_value = box.findtext("y")
    width_value = box.findtext("w")
    height_value = box.findtext("h")

    if all(
        value is not None
        for value in (
            x_value,
            y_value,
            width_value,
            height_value,
        )
    ):
        x = float(x_value)
        y = float(y_value)
        width = float(width_value)
        height = float(height_value)

        return (
            x,
            y,
            x + width,
            y + height,
        )

    return None


def main() -> None:
    args = parse_arguments()
    dataset = args.dataset.expanduser().resolve()

    if not dataset.is_dir():
        raise FileNotFoundError(
            f"UATD directory not found: {dataset}"
        )

    image_paths = sorted(
        path
        for path in dataset.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".bmp"
    )

    annotation_paths = sorted(
        path
        for path in dataset.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".xml"
    )

    images_by_section: defaultdict[str, dict[str, Path]] = (
        defaultdict(dict)
    )
    annotations_by_section: defaultdict[str, dict[str, Path]] = (
        defaultdict(dict)
    )

    duplicate_image_stems = []
    duplicate_annotation_stems = []

    for path in image_paths:
        section = section_name(path, dataset)

        if path.stem in images_by_section[section]:
            duplicate_image_stems.append(
                f"{section}/{path.stem}"
            )

        images_by_section[section][path.stem] = path

    for path in annotation_paths:
        section = section_name(path, dataset)

        if path.stem in annotations_by_section[section]:
            duplicate_annotation_stems.append(
                f"{section}/{path.stem}"
            )

        annotations_by_section[section][path.stem] = path

    sections = sorted(
        set(images_by_section)
        | set(annotations_by_section)
    )

    unreadable_images = []
    malformed_xml = []
    dimension_mismatches = []
    invalid_boxes = []
    missing_images = []
    missing_annotations = []

    object_counts = Counter()
    class_image_counts = Counter()
    section_statistics = {}

    processed = 0

    for section in sections:
        images = images_by_section[section]
        annotations = annotations_by_section[section]

        image_stems = set(images)
        annotation_stems = set(annotations)

        section_missing_annotations = sorted(
            image_stems - annotation_stems
        )
        section_missing_images = sorted(
            annotation_stems - image_stems
        )

        missing_annotations.extend(
            f"{section}/{stem}"
            for stem in section_missing_annotations
        )
        missing_images.extend(
            f"{section}/{stem}"
            for stem in section_missing_images
        )

        section_objects = Counter()
        section_class_images = Counter()
        section_valid_boxes = 0

        for stem in sorted(image_stems & annotation_stems):
            image_path = images[stem]
            annotation_path = annotations[stem]

            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE,
            )

            if image is None:
                unreadable_images.append(str(image_path))
                continue

            image_height, image_width = image.shape

            try:
                root = ET.parse(annotation_path).getroot()
            except ET.ParseError as error:
                malformed_xml.append(
                    {
                        "path": str(annotation_path),
                        "error": str(error),
                    }
                )
                continue

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
                dimension_mismatches.append(
                    {
                        "stem": stem,
                        "section": section,
                        "image_size": [
                            image_width,
                            image_height,
                        ],
                        "xml_size": [
                            xml_width,
                            xml_height,
                        ],
                    }
                )

            classes_in_image = set()

            for object_element in root.findall("object"):
                class_name = object_element.findtext(
                    "name",
                    default="unknown",
                ).strip().lower()

                box_element = object_element.find("bndbox")

                if box_element is None:
                    invalid_boxes.append(
                        {
                            "section": section,
                            "stem": stem,
                            "class": class_name,
                            "reason": "missing bndbox",
                        }
                    )
                    continue

                try:
                    coordinates = parse_box(box_element)
                except ValueError:
                    coordinates = None

                if coordinates is None:
                    invalid_boxes.append(
                        {
                            "section": section,
                            "stem": stem,
                            "class": class_name,
                            "reason": "invalid coordinates",
                        }
                    )
                    continue

                xmin, ymin, xmax, ymax = coordinates

                valid = (
                    xmin >= 0
                    and ymin >= 0
                    and xmax > xmin
                    and ymax > ymin
                    and xmax <= image_width
                    and ymax <= image_height
                )

                if not valid:
                    invalid_boxes.append(
                        {
                            "section": section,
                            "stem": stem,
                            "class": class_name,
                            "box": list(coordinates),
                            "image_size": [
                                image_width,
                                image_height,
                            ],
                        }
                    )
                    continue

                object_counts[class_name] += 1
                section_objects[class_name] += 1
                classes_in_image.add(class_name)
                section_valid_boxes += 1

            for class_name in classes_in_image:
                class_image_counts[class_name] += 1
                section_class_images[class_name] += 1

            processed += 1

            if processed % 500 == 0:
                print(
                    f"Checked {processed} image/XML pairs...",
                    flush=True,
                )

        section_statistics[section] = {
            "images": len(images),
            "annotations": len(annotations),
            "paired_files": len(
                image_stems & annotation_stems
            ),
            "missing_images": len(
                section_missing_images
            ),
            "missing_annotations": len(
                section_missing_annotations
            ),
            "valid_boxes": section_valid_boxes,
            "object_counts": dict(
                sorted(section_objects.items())
            ),
            "class_image_counts": dict(
                sorted(section_class_images.items())
            ),
        }

    problems = sum(
        (
            len(duplicate_image_stems),
            len(duplicate_annotation_stems),
            len(unreadable_images),
            len(malformed_xml),
            len(dimension_mismatches),
            len(invalid_boxes),
            len(missing_images),
            len(missing_annotations),
        )
    )

    report = {
        "dataset": str(dataset),
        "sections": section_statistics,
        "total_images": len(image_paths),
        "total_annotations": len(annotation_paths),
        "object_counts": dict(sorted(object_counts.items())),
        "class_image_counts": dict(
            sorted(class_image_counts.items())
        ),
        "problems": {
            "duplicate_image_stems": duplicate_image_stems,
            "duplicate_annotation_stems": (
                duplicate_annotation_stems
            ),
            "unreadable_images": unreadable_images,
            "malformed_xml": malformed_xml,
            "dimension_mismatches": dimension_mismatches,
            "invalid_boxes": invalid_boxes,
            "missing_images": missing_images,
            "missing_annotations": missing_annotations,
        },
    }

    output_directory = PROJECT_ROOT / "runs/dataset_audits"
    output_directory.mkdir(parents=True, exist_ok=True)
    report_path = output_directory / "uatd_audit.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("NEZA AI — UATD DATASET AUDIT")
    print("=" * 72)
    print(f"Images:                {len(image_paths)}")
    print(f"Annotations:           {len(annotation_paths)}")
    print(f"Missing images:        {len(missing_images)}")
    print(f"Missing annotations:   {len(missing_annotations)}")
    print(f"Unreadable images:     {len(unreadable_images)}")
    print(f"Malformed XML files:   {len(malformed_xml)}")
    print(
        "Dimension mismatches: "
        f"{len(dimension_mismatches)}"
    )
    print(f"Invalid boxes:         {len(invalid_boxes)}")
    print(
        "Duplicate image stems: "
        f"{len(duplicate_image_stems)}"
    )

    print("\nSECTION COUNTS")

    for section, values in section_statistics.items():
        print(
            f"{section:15} "
            f"images={values['images']:5d} "
            f"xml={values['annotations']:5d} "
            f"boxes={values['valid_boxes']:6d}"
        )

    print("\nCLASS DISTRIBUTION")

    for class_name in sorted(object_counts):
        print(
            f"{class_name:25} "
            f"images={class_image_counts[class_name]:5d} "
            f"objects={object_counts[class_name]:6d}"
        )

    print(f"\nProblems detected: {problems}")
    print(
        "RESULT: "
        f"{'PASSED' if problems == 0 else 'REVIEW REQUIRED'}"
    )
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
