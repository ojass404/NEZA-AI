# NEZA AI - Neptune Environmental Zone Analytics AI

[![CI](https://github.com/yourusername/neza-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/neza-ai/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Overview

NEZA AI is an AI-powered automated underwater marine debris and anomaly detection system using Side-Scan Sonar (SSS) imagery. It detects ghost nets, shipwrecks, pipelines, and other man-made objects on the seafloor.

### Key Features
-  **Object Detection & Segmentation**: YOLO + U-Net models
-  **Acoustic Noise Filtering**: Speckle reduction and shadow analysis
-  **Geotagging Engine**: Automatic GPS coordinate extraction
-  **Report Generation**: JSON/CSV reports with confidence scores
-  **Offline-First**: Works on AUVs, ROVs, and edge devices
-  **Flutter Dashboard**: Cross-platform UI (iOS, Android, Web)

##  Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Flutter, Riverpod |
| Backend | FastAPI, PostgreSQL, Redis |
| ML/AI | PyTorch, YOLO, U-Net, ONNX |
| Geospatial | Geopy, PyProj, Folium |
| Deployment | Docker, Kubernetes |

##  Architecture

![Architecture Diagram](docs/images/architecture.png)

##  Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Flutter 3.0+

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/neza-ai.git
cd neza-ai

# Setup environment
cp .env.example .env

# Start with Docker
docker-compose up -d

# Or manual setup
./scripts/setup.sh
