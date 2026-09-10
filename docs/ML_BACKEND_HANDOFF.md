# NEZA AI — ML Backend Handoff

## Available Models

Place the trained model files at:

- `backend/models/yolov8n_sss.pt`
- `backend/models/yolov8n_sss.onnx`

The model files are excluded from Git because they are generated binary artifacts.

## Available Scripts

| Purpose | Script |
|---|---|
| Prepare dataset | `ml_pipeline/scripts/prepare_ai4shipwrecks.py` |
| Validate dataset | `ml_pipeline/scripts/validate_prepared_dataset.py` |
| Train YOLO | `ml_pipeline/scripts/train_yolo.py` |
| Evaluate model | `ml_pipeline/scripts/evaluate_yolo.py` |
| Single-image inference | `ml_pipeline/scripts/predict_yolo.py` |
| Full-strip inference | `ml_pipeline/scripts/predict_sonar_strip.py` |
| Export ONNX | `ml_pipeline/scripts/export_yolo.py` |
| Benchmark formats | `ml_pipeline/scripts/benchmark_yolo_formats.py` |

## Single-Image Inference

```bash
cd ml_pipeline

python scripts/predict_yolo.py \
  --model ../backend/models/yolov8n_sss.onnx \
  --image PATH_TO_IMAGE \
  --confidence 0.20 \
  --latitude LATITUDE \
  --longitude LONGITUDE

## Preprocessing decision

The optional sonar enhancement module must remain disabled in backend
inference. Validation showed that it reduced F1 from 0.6667 to 0.4091 and
increased false positives from 7 to 18.

Use raw sonar images for the current trained model.

## Segmentation status

Semantic segmentation is intentionally disabled because no verified U-Net
model has been trained and evaluated. The existing prototype must provide
YOLO bounding-box detection only.

## Automated validation

Run the integration tests from the repository root:

```bash
PYTHONPATH="$PWD/backend" python -m unittest \
  backend/tests/test_ml_integration.py \
  -v
