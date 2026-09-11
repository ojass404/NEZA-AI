#!/usr/bin/env python3
"""Export the trained NEZA AI YOLO model to ONNX."""

from __future__ import annotations

import argparse
from pathlib import Path

import onnx
import onnxruntime as ort
from ultralytics import YOLO


def main() -> None:
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]

    default_model = (
        project_root
        / "backend"
        / "models"
        / "yolov8n_sss.pt"
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        type=Path,
        default=default_model,
    )

    parser.add_argument(
        "--image-size",
        type=int,
        default=640,
    )

    parser.add_argument(
        "--opset",
        type=int,
        default=17,
    )

    args = parser.parse_args()

    model_path = args.model.resolve()

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    print("=" * 60)
    print("NEZA AI — ONNX EXPORT")
    print("=" * 60)
    print(f"Source model: {model_path}")
    print(f"Image size:   {args.image_size}")
    print(f"ONNX opset:   {args.opset}")
    print("=" * 60)

    model = YOLO(str(model_path))

    exported_path = model.export(
        format="onnx",
        imgsz=args.image_size,
        opset=args.opset,
        batch=1,
        dynamic=False,
        simplify=False,
        device="cpu",
    )

    onnx_path = Path(exported_path).resolve()

    if not onnx_path.exists():
        raise FileNotFoundError(
            f"Exported ONNX model not found: {onnx_path}"
        )

    onnx_model = onnx.load(str(onnx_path))
    onnx.checker.check_model(onnx_model)

    session = ort.InferenceSession(
        str(onnx_path),
        providers=["CPUExecutionProvider"],
    )

    print("\nONNX validation passed.")
    print(f"Exported model: {onnx_path}")
    print(
        f"File size: "
        f"{onnx_path.stat().st_size / (1024 ** 2):.2f} MB"
    )

    print("\nModel inputs:")

    for model_input in session.get_inputs():
        print(
            f"  {model_input.name}: "
            f"{model_input.shape} "
            f"{model_input.type}"
        )

    print("\nModel outputs:")

    for model_output in session.get_outputs():
        print(
            f"  {model_output.name}: "
            f"{model_output.shape} "
            f"{model_output.type}"
        )


if __name__ == "__main__":
    main()