import logging
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from app.models.detection import Detection
from app.services.filtering_service import severity_for
from app.services.geotagging_service import geotag_detection
log=logging.getLogger(__name__)

def create_detections(db, scan, metadata, filtered, image_width=1000, image_height=700, model_name="mock-demo", model_version="1.0"):
    saved=[]
    for raw, status, reason in filtered:
        if status != "PASSED": continue
        geo=geotag_detection(metadata,raw,image_width,image_height)
        d=Detection(scan_id=scan.id,class_name=raw.class_name,confidence=raw.confidence,confidence_percent=round(raw.confidence*100),bbox_x=raw.x,bbox_y=raw.y,bbox_width=raw.width,bbox_height=raw.height,
            latitude=geo.latitude,longitude=geo.longitude,severity=severity_for(raw.confidence),verification_status="PENDING",filter_status=status,filter_reason=reason,model_name=model_name,model_version=model_version,geotagging_method=geo.method,location_accuracy_m=geo.accuracy_estimate_m)
        if geo.latitude is not None: d.location=from_shape(Point(geo.longitude,geo.latitude), srid=4326)
        # Only estimate a cross-track width when sonar range provides a usable image scale.
        if metadata and metadata.sonar_range_m: d.estimated_width_m=(raw.width/image_width)*2*metadata.sonar_range_m
        db.add(d); saved.append(d)
    db.flush(); log.info("%s detections passed confidence filter",len(saved)); return saved
