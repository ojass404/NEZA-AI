# NEZA AI Backend — SIH26057 Prototype

A simple local-first FastAPI backend for the NEZA AI marine debris / underwater anomaly workflow. It is intentionally a prototype: the mock inference provider produces deterministic **synthetic demo detections** so the complete API → filtering → geotagging → PostGIS → GeoJSON/CSV → human verification loop can be demonstrated before the real AI model is ready.

## Architecture

```text
React / MapLibre
      |
      | REST / JSON / GeoJSON
      v
FastAPI /api/v1
      |
      +--> Local Storage
      +--> PostgreSQL + PostGIS
      +--> Processing Service
              |
              +--> OpenCV preprocessing
              +--> InferenceProvider (mock now, real model later)
              +--> confidence filter
              +--> geotagging engine
              +--> PostGIS point
              +--> JSON / GeoJSON / CSV reports
```

## Folder structure

`app/api` HTTP routes, `app/schemas` validation, `app/services` business logic, `app/models` database models, `app/geospatial` coordinate/GeoJSON helpers, `storage` local files, `tests` automated tests.

## Windows setup

Install Python 3.11+ and Docker Desktop. In PowerShell:

```powershell
git clone <your-repo>
cd neza-backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d
python scripts\init_db.py
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs**.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` for the current shell.

## Environment

`.env` is local-only. The important defaults are `AI_PROVIDER=mock`, `AI_CONFIDENCE_THRESHOLD=0.50`, local filesystem storage, and PostgreSQL at localhost:5432.

## End-to-end demo

### 1. Upload

```bash
curl -X POST "http://localhost:8000/api/v1/scans/upload" -F "file=@sample_sonar.jpg" -F "survey_name=SIH Demo Survey" -F "description=Prototype sonar image"
```

Save the returned `scan_id`.

### 2. Add metadata

```bash
curl -X POST "http://localhost:8000/api/v1/scans/<SCAN_ID>/metadata" -H "Content-Type: application/json" -d "{"timestamp":"2026-09-09T10:30:00Z","latitude":19.0760,"longitude":72.8777,"depth_m":25.4,"heading_deg":120.5,"altitude_m":10.2,"vehicle_type":"AUV","vehicle_id":"AUV-01","sonar_range_m":50,"ping_id":"PING-0001","crs":"EPSG:4326"}"
```

### 3. Process

```bash
curl -X POST "http://localhost:8000/api/v1/scans/<SCAN_ID>/process"
```

Processing is synchronous in this prototype. The endpoint returns `COMPLETED` when finished, or `FAILED` if the pipeline errors.

### 4. Status

```bash
curl "http://localhost:8000/api/v1/scans/<SCAN_ID>"
```

### 5. Detections

```bash
curl "http://localhost:8000/api/v1/scans/<SCAN_ID>/detections"
```

### 6. GeoJSON

```bash
curl "http://localhost:8000/api/v1/scans/<SCAN_ID>/geojson"
```

The result is a standards-compliant `FeatureCollection` directly consumable by MapLibre. GeoJSON coordinates are always `[longitude, latitude]`.

### 7. JSON report

```bash
curl "http://localhost:8000/api/v1/scans/<SCAN_ID>/report/json"
```

### 8. CSV report

```bash
curl -OJ "http://localhost:8000/api/v1/scans/<SCAN_ID>/report/csv"
```

### 9. Human verification

```bash
curl -X PATCH "http://localhost:8000/api/v1/detections/<DETECTION_ID>/verification" -H "Content-Type: application/json" -d "{"verification_status":"CONFIRMED","notes":"Verified by marine survey expert","verified_by":"demo-expert"}"
```

## Demo seed data

After database initialization:

```bash
python scripts/seed_demo_data.py
```

This creates one clearly labeled **DEMO DATA** scan, metadata and four synthetic detections. It does not claim they came from real sonar or a trained model.

## Geotagging

The engine intentionally separates image coordinates from geographic coordinates.

1. **FRAME_LEVEL** — if GPS latitude/longitude exists but no sufficient sonar geometry exists, the detection inherits the frame GPS position. This is an approximation, not a pixel-accurate location.
2. **OFFSET_ESTIMATE** — if latitude, longitude, heading, sonar range and port/starboard side are available, the engine estimates a cross-track offset and rotates it using heading. This is a prototype approximation and should be replaced with ping-level sonar geometry when real navigation/sonar data is available.
3. **PING_LEVEL** — reserved for future precise ping navigation.
4. **UNAVAILABLE** — no valid coordinates are fabricated.

The small-distance conversion uses a WGS84 approximation. Coordinate order is checked in tests: database/GeoJSON uses longitude first for GeoJSON and a PostGIS `Point(lon, lat)`.

## Dimensions

Pixel dimensions are not converted into meters unless a sonar range is supplied. In the current prototype only a simple cross-track width estimate is made when range is available; otherwise physical dimensions remain `null`.

## Severity

Prototype heuristic only: `HIGH >= 0.85`, `MEDIUM >= 0.65`, otherwise `LOW`. This is not a scientifically validated risk score.

## Real AI integration

Implement a new `InferenceProvider` in `app/services/inference_service.py`, for example `YOLOInferenceProvider`, and return the same `RawDetection` contract. Then change `AI_PROVIDER` selection. The frontend API does not change. Do not put model code inside FastAPI routes.

The backend does **not** implement a fake YOLO/UNet. The mock provider is only a deterministic integration harness.

## PostGIS

`detections.location` is `geography(POINT, 4326)` with a spatial index. Nearby queries use PostGIS `ST_DWithin`, not manual Python distance calculations. PostGIS is enabled automatically by `scripts/init_db.py`.

## MapLibre frontend contract

```js
const res = await fetch(`${API_BASE}/api/v1/map/detections?min_confidence=0.7`);
const geojson = await res.json();
map.addSource("detections", { type: "geojson", data: geojson });
```

The frontend only talks to FastAPI; it never connects to PostgreSQL or the AI provider directly.

## API list

| Tag | Endpoint | Purpose |
|---|---|---|
| Health | `GET /api/v1/health` | Service health |
| Health | `GET /api/v1/health/dependencies` | DB/storage/AI checks |
| Scans | `POST /api/v1/scans/upload` | Upload sonar image |
| Metadata | `POST /api/v1/scans/{id}/metadata` | Attach navigation metadata |
| Scans | `POST /api/v1/scans/{id}/process` | Run processing pipeline |
| Scans | `GET /api/v1/scans/{id}` | Scan status |
| Detections | `GET /api/v1/scans/{id}/detections` | Detection list |
| Detections | `PATCH /api/v1/detections/{id}/verification` | Confirm/reject |
| Reports | `GET /api/v1/scans/{id}/geojson` | Map GeoJSON |
| Reports | `GET /api/v1/scans/{id}/report/json` | JSON report |
| Reports | `GET /api/v1/scans/{id}/report/geojson` | GeoJSON report |
| Reports | `GET /api/v1/scans/{id}/report/csv` | CSV download |
| Map | `GET /api/v1/map/detections` | Filtered map data |
| Map | `GET /api/v1/map/detections/nearby` | PostGIS radius query |

Swagger: **http://localhost:8000/docs**; OpenAPI: **http://localhost:8000/openapi.json**.

## MinIO

The application is structured around a storage abstraction. The first working implementation is local storage. MinIO is intentionally not required for the prototype. To add it, implement `MinioStorageService` behind the same `StorageService` methods and select it from configuration. This keeps file/object-storage changes out of the API and processing layers.

## Future background processing

The current process endpoint is synchronous because that is easiest to demo and debug. Later, the body of the processing route can be moved to a task function and invoked by Celery/RabbitMQ (or FastAPI background tasks for a lighter step) without changing the frontend contract: upload → process → status/detections.

## Testing

Run:

```bash
pytest -q
```

The tests cover validation, filtering, frame-level geotagging, GeoJSON coordinate order, reports and API behavior where database infrastructure is available.

## Prototype limitations

- Mock inference is synthetic and not an accuracy claim.
- No authentication is included.
- No ping-level inertial/sonar georeferencing is implemented.
- No scientifically validated debris severity/risk model is implemented.
- No acoustic-shadow validation is claimed.
- Synchronous processing is used.
- The initial storage backend is local filesystem.
- Real sonar formats and metadata parsers must be added when sample survey data is available.
