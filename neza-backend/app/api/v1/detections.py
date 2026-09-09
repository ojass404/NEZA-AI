from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.detection import Detection
from app.models.scan import Scan
from app.schemas.detection import DetectionsResponse,DetectionResponse,VerificationUpdate
from app.core.exceptions import AppError
from datetime import datetime, timezone
router=APIRouter(prefix="/detections",tags=["Detections"])

def to_response(d): return DetectionResponse(id=d.id,scan_id=d.scan_id,class_name=d.class_name,confidence=d.confidence,confidence_percent=d.confidence_percent,bbox={"x":d.bbox_x,"y":d.bbox_y,"width":d.bbox_width,"height":d.bbox_height},location={"latitude":d.latitude,"longitude":d.longitude} if d.latitude is not None else None,severity=d.severity,verification_status=d.verification_status,filter_status=d.filter_status,geotagging_method=d.geotagging_method,location_accuracy_m=d.location_accuracy_m,estimated_length_m=d.estimated_length_m,estimated_width_m=d.estimated_width_m,estimated_area_m2=d.estimated_area_m2,model_name=d.model_name,model_version=d.model_version,created_at=d.created_at)
@router.get("/scans/{scan_id}/detections",response_model=DetectionsResponse)
def list_detections(scan_id:UUID,db:Session=Depends(get_db)):
    if not db.get(Scan,scan_id): raise AppError("SCAN_NOT_FOUND","The requested scan does not exist.",404)
    ds=db.query(Detection).filter(Detection.scan_id==scan_id).order_by(Detection.created_at).all(); return DetectionsResponse(scan_id=scan_id,count=len(ds),detections=[to_response(d) for d in ds])
@router.patch("/{detection_id}/verification",response_model=DetectionResponse)
def verify(detection_id:UUID,payload:VerificationUpdate,db:Session=Depends(get_db)):
    if payload.verification_status not in {"PENDING","CONFIRMED","REJECTED"}: raise AppError("INVALID_VERIFICATION_STATUS","Use PENDING, CONFIRMED, or REJECTED.",400)
    d=db.get(Detection,detection_id)
    if not d: raise AppError("DETECTION_NOT_FOUND","The requested detection does not exist.",404)
    d.verification_status=payload.verification_status; d.verification_notes=payload.notes; d.verified_by=payload.verified_by; d.verified_at=datetime.now(timezone.utc) if payload.verification_status!="PENDING" else None; db.commit(); return to_response(d)
