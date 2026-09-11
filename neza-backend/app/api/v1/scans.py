import logging
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.scan import Scan
from app.models.scan_metadata import ScanMetadata
from app.schemas.scan import UploadResponse, ScanResponse, ProcessResponse
from app.schemas.metadata import MetadataCreate
from app.services.storage_service import storage_service
from app.services.preprocessing_service import preprocess
from app.services.inference_service import get_inference_provider
from app.services.filtering_service import filter_detections
from app.services.detection_service import create_detections
from app.services.report_service import write_reports
from app.utils.file_validation import safe_filename, validate_upload
from app.config import settings
from app.core.exceptions import AppError
router=APIRouter(prefix="/scans",tags=["Scans","Metadata"]); log=logging.getLogger(__name__)

def get_scan(db,id):
    scan=db.get(Scan,id)
    if not scan: raise AppError("SCAN_NOT_FOUND","The requested scan does not exist.",404)
    return scan

@router.post("/upload",response_model=UploadResponse)
def upload(file:UploadFile=File(...),survey_name:str|None=Form(None),description:str|None=Form(None),db:Session=Depends(get_db)):
    content=bytearray()
    while True:
        chunk=file.file.read(1024*1024)
        if not chunk: break
        content.extend(chunk)
        if len(content)>settings.max_upload_bytes: raise AppError("FILE_TOO_LARGE",f"File exceeds {settings.max_upload_size_mb} MB limit.",413)
    try: validate_upload(file.filename or "",len(content))
    except ValueError as e: raise AppError("INVALID_FILE",str(e),400)
    scan=Scan(filename=safe_filename(file.filename),storage_path="",file_type=Path(file.filename).suffix.lower().lstrip("."),file_size=len(content),survey_name=survey_name,description=description)
    db.add(scan); db.flush(); object_name=f"raw/{scan.id}_{scan.filename}"
    import io
    storage_service.save_file(io.BytesIO(content),object_name); scan.storage_path=object_name; db.commit()
    log.info("Scan uploaded scan_id=%s",scan.id)
    return UploadResponse(scan_id=scan.id,filename=scan.filename,status=scan.status,message="Sonar scan uploaded successfully")

@router.post("/{scan_id}/metadata")
def add_metadata(scan_id:UUID,payload:MetadataCreate,db:Session=Depends(get_db)):
    scan=get_scan(db,scan_id)
    if scan.metadata_record: raise AppError("METADATA_EXISTS","Metadata already exists for this scan.",409)
    m=ScanMetadata(scan_id=scan.id,**payload.model_dump()); db.add(m); db.commit(); return {"scan_id":scan.id,"message":"Scan metadata stored successfully"}

@router.post("/{scan_id}/process",response_model=ProcessResponse)
def process(scan_id:UUID,db:Session=Depends(get_db)):
    scan=get_scan(db,scan_id)
    if scan.status=="PROCESSING": return ProcessResponse(scan_id=scan.id,status="PROCESSING",message="Scan is already processing")
    try:
        scan.status="PROCESSING"; scan.error_message=None; db.commit()
        raw_path=storage_service.get_file(scan.storage_path); processed=Path(settings.local_storage_path)/"processed"/f"{scan.id}.png"
        preprocess(raw_path,processed)
        provider=get_inference_provider(); raw_dets=provider.predict(processed); log.info("AI inference completed scan_id=%s detections=%s",scan.id,len(raw_dets))
        filtered=filter_detections(raw_dets)
        # The demo provider uses a 1000x700 coordinate space; a real provider should return actual image dimensions.
        create_detections(db,scan,scan.metadata_record,filtered,image_width=1000,image_height=700)
        write_reports(db,scan,list(scan.detections)); scan.status="COMPLETED"; db.commit()
        log.info("Scan completed scan_id=%s",scan.id)
        return ProcessResponse(scan_id=scan.id,status=scan.status,message="Scan processing completed")
    except Exception as e:
        db.rollback(); scan=db.get(Scan,scan_id); scan.status="FAILED"; scan.error_message=str(e); db.commit(); log.exception("Scan failed scan_id=%s",scan_id); raise AppError("PROCESSING_FAILED",str(e),500)

@router.get("/{scan_id}",response_model=ScanResponse)
def get_scan_status(scan_id:UUID,db:Session=Depends(get_db)):
    scan=get_scan(db,scan_id); dets=list(scan.detections); return ScanResponse(scan_id=scan.id,filename=scan.filename,status=scan.status,detection_count=len(dets),geotagged_detection_count=sum(d.latitude is not None for d in dets),created_at=scan.created_at,updated_at=scan.updated_at)
