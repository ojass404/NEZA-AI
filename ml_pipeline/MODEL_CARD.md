# NEZA AI — Shipwreck Detection Model Card

## Model

- Architecture: YOLOv8n object detector
- Task: Shipwreck/anomaly candidate detection in side-scan sonar imagery
- Classes: `shipwreck`
- Input size: 640 × 640 pixels
- PyTorch model: `backend/models/yolov8n_sss.pt`
- ONNX model: `backend/models/yolov8n_sss.onnx`
- Human verification: Required

## Intended Use

The model detects possible shipwrecks or artificial-anomaly candidates in side-scan sonar imagery.

It can support:

- Sonar survey review
- Candidate anomaly localization
- Bounding-box generation
- Confidence scoring
- JSON and CSV report generation
- Full-resolution sonar-strip inference using tiled processing

## Dataset

AI4Shipwrecks was converted from segmentation masks into YOLO bounding-box annotations.

| Split | Images | Positive | Background |
|---|---:|---:|---:|
| Train | 131 | 70 | 61 |
| Validation | 35 | 17 | 18 |
| Test | 120 | 74 | 46 |

Dataset validation confirmed:

- Matching images and labels
- Valid normalized YOLO annotations
- No missing files
- No source-group leakage between splits
- Prepared dataset size: approximately 37.74 MB

## Baseline Performance

### Validation set

| Metric | Result |
|---|---:|
| Precision | 0.6978 |
| Recall | 0.7647 |
| F1-score | 0.7297 |
| mAP@50 | 0.7286 |
| mAP@50–95 | 0.3450 |

Validation operational confidence threshold: `0.10`.

### Untouched test set

| Metric | Result |
|---|---:|
| Precision | 0.3903 |
| Recall | 0.5190 |
| mAP@50 | 0.3471 |
| mAP@50–95 | 0.1214 |

The untouched test results show limited generalization and must not be hidden when presenting the model.

## Recommended Thresholds

- Object-centred 640 × 640 images: `0.20`
- Full sonar-strip candidate screening: `0.05`
- Full-strip minimum bounding-box area: `5000` pixels
- Human verification is required for every detection

The full-strip area filter is an initial heuristic tested on a limited sample and requires validation on more sonar strips.

## Deployment Benchmark

Benchmark image produced one detection in both formats.

| Format | Device | Mean inference time |
|---|---|---:|
| PyTorch | Apple MPS | 7.23 ms |
| ONNX | CPU | 21.14 ms |

Parity results:

- Same detection count: Yes
- Confidence difference: `5.96e-08`
- Maximum bounding-box difference: `6.10e-05` pixels

The benchmark measures model inference on one 640 × 640 image. It does not include full sonar-strip tiling, file loading, drawing, or report generation.

## Outputs

The inference pipeline produces:

- Annotated sonar image
- Detection confidence percentage
- Pixel bounding-box coordinates
- Bounding-box width and height
- JSON anomaly report
- CSV anomaly report
- Optional source latitude and longitude
- Human-verification status

## Limitations

- The model was trained only on AI4Shipwrecks imagery.
- The only trained class is `shipwreck`.
- It does not reliably classify ghost nets, pipes, cylinders, plastic, metal debris, or fishing traps.
- It may confuse acoustic shadows, rocks, terrain patterns, and sonar noise with artificial objects.
- Low confidence thresholds increase recall but also increase false positives.
- Latitude and longitude cannot be inferred from image pixels without matching sonar metadata.
- Test-set performance indicates that additional labelled sonar data is required.
- This model must not be used as an autonomous navigation or cleanup decision system.

## Accurate Prototype Description

> Detection and localization of possible shipwrecks or artificial-anomaly candidates in side-scan sonar imagery, with confidence scores and human verification.

## Reproduction

```bash
cd ml_pipeline

python scripts/prepare_ai4shipwrecks.py
python scripts/validate_prepared_dataset.py
python scripts/train_yolo.py

python scripts/evaluate_yolo.py \
  --split val \
  --confidence 0.10

python scripts/export_yolo.py

## Preprocessing Validation

The optional median, bilateral, and CLAHE preprocessing pipeline was
evaluated on the complete validation split at confidence 0.10 and IoU 0.50.

| Input | Precision | Recall | F1 |
|---|---:|---:|---:|
| Raw sonar images | 0.6316 | 0.7059 | 0.6667 |
| Preprocessed images | 0.3333 | 0.5294 | 0.4091 |

Preprocessing increased false positives from 7 to 18 and reduced true
positives from 12 to 9. Therefore, preprocessing is available only as an
experimental module and is disabled during operational inference.

The model must continue receiving raw sonar imagery until a preprocessing
configuration is validated through retraining and untouched-test evaluation.

## Backend Safety Decisions

- Missing model files raise an explicit error.
- Generic YOLO weights are never substituted automatically.
- PyTorch inference supports CUDA, Apple MPS, and CPU.
- ONNX inference uses CPU.
- Model confidence is reported without artificial modification.
- Unverified U-Net segmentation is disabled.
- Unsupported debris classes are not generated.
- Every candidate requires human verification.
