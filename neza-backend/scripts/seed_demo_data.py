from datetime import datetime, timezone
from pathlib import Path
from app.database.init_db import init_db
from app.database.connection import SessionLocal
from app.models.scan import Scan
from app.models.scan_metadata import ScanMetadata
from app.models.detection import Detection
from app.config import settings
from app.geospatial.coordinates import geojson_point
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
init_db(); db=SessionLocal()
try:
    scan=Scan(filename="DEMO_sonar_sample.jpg",storage_path="demo/DEMO_sonar_sample.jpg",file_type="jpg",file_size=0,status="COMPLETED",survey_name="DEMO DATA - NEZA AI",description="Synthetic demo records for SIH prototype demonstration."); db.add(scan); db.flush()
    m=ScanMetadata(scan_id=scan.id,timestamp=datetime.now(timezone.utc),latitude=19.0760,longitude=72.8777,depth_m=25.4,heading_deg=120.5,altitude_m=10.2,vehicle_type="AUV",vehicle_id="AUV-DEMO",sonar_range_m=50,ping_id="PING-DEMO-0001",source="synthetic demo",crs="EPSG:4326"); db.add(m); db.flush()
    vals=[("fishing_net",.91,19.0760,72.8777,"HIGH"),("pipe",.72,19.0762,72.8779,"MEDIUM"),("marine_debris",.58,19.0758,72.8775,"LOW"),("unknown_anomaly",.47,None,None,"LOW")]
    for i,(c,conf,lat,lon,sev) in enumerate(vals):
        d=Detection(scan_id=scan.id,class_name=c,confidence=conf,confidence_percent=round(conf*100),bbox_x=100+i*120,bbox_y=150,bbox_width=100,bbox_height=70,latitude=lat,longitude=lon,severity=sev,verification_status="PENDING",filter_status="PASSED" if conf>=.5 else "FILTERED",filter_reason=None if conf>=.5 else "Below confidence threshold",model_name="DEMO_DATA",model_version="synthetic-1.0",geotagging_method="FRAME_LEVEL" if lat else "UNAVAILABLE")
        if lat is not None:d.location=from_shape(Point(lon,lat),srid=4326)
        db.add(d)
    db.commit(); print(f"Created DEMO scan: {scan.id}")
finally: db.close()
