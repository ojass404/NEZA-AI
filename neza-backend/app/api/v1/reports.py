import json
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.scan import Scan
from app.models.detection import Detection
from app.services.report_service import build_json
from app.core.exceptions import AppError
from app.config import settings
from app.geospatial.geojson import feature_collection
router=APIRouter(prefix="/scans",tags=["Reports"])
def scan(db,id):
 s=db.get(Scan,id)
 if not s: raise AppError("SCAN_NOT_FOUND","The requested scan does not exist.",404)
 return s
@router.get("/{scan_id}/geojson")
def geojson(scan_id:UUID,db:Session=Depends(get_db)):
 s=scan(db,scan_id); return feature_collection(list(s.detections))
@router.get("/{scan_id}/report/json")
def report_json(scan_id:UUID,db:Session=Depends(get_db)):
 s=scan(db,scan_id); return JSONResponse(build_json(s,list(s.detections)))
@router.get("/{scan_id}/report/geojson")
def report_geojson(scan_id:UUID,db:Session=Depends(get_db)):
 s=scan(db,scan_id); return feature_collection(list(s.detections))
@router.get("/{scan_id}/report/csv")
def report_csv(scan_id:UUID,db:Session=Depends(get_db)):
 s=scan(db,scan_id); p=__import__('pathlib').Path(settings.local_storage_path)/"reports"/str(scan_id)/"report.csv"
 if not p.exists(): raise AppError("REPORT_NOT_FOUND","CSV report has not been generated yet.",404)
 return FileResponse(p,media_type="text/csv",filename=f"neza_{scan_id}.csv")
