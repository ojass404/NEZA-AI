import csv, json
from pathlib import Path
from datetime import datetime, timezone
from app.config import settings
from app.models.report import Report
from app.geospatial.geojson import feature_collection

def detection_dict(d): return {"detection_id":str(d.id),"scan_id":str(d.scan_id),"class_name":d.class_name,"confidence":d.confidence,"confidence_percent":d.confidence_percent,"bbox_x":d.bbox_x,"bbox_y":d.bbox_y,"bbox_width":d.bbox_width,"bbox_height":d.bbox_height,"latitude":d.latitude,"longitude":d.longitude,"estimated_length_m":d.estimated_length_m,"estimated_width_m":d.estimated_width_m,"estimated_area_m2":d.estimated_area_m2,"severity":d.severity,"verification_status":d.verification_status,"geotagging_method":d.geotagging_method,"location_accuracy_m":d.location_accuracy_m,"model_name":d.model_name,"model_version":d.model_version,"created_at":d.created_at.isoformat() if d.created_at else None}

def summary(dets): return {"total_detections":len(dets),"confirmed":sum(d.verification_status=="CONFIRMED" for d in dets),"pending":sum(d.verification_status=="PENDING" for d in dets),"rejected":sum(d.verification_status=="REJECTED" for d in dets),"geotagged":sum(d.latitude is not None and d.longitude is not None for d in dets),"high_priority":sum(d.severity in {"HIGH","CRITICAL"} for d in dets)}

def build_json(scan,dets,report_id=None):
    rid=str(report_id) if report_id else None
    return {"report_id":rid,"scan_id":str(scan.id),"generated_at":datetime.now(timezone.utc).isoformat(),"summary":summary(dets),"detections":[detection_dict(d) for d in dets]}

def write_reports(db,scan,dets):
    root=Path(settings.local_storage_path)/"reports"/str(scan.id); root.mkdir(parents=True,exist_ok=True)
    rjson=Report(scan_id=scan.id,report_type="JSON",file_path=str(root/"report.json")); db.add(rjson); db.flush()
    (root/"report.json").write_text(json.dumps(build_json(scan,dets,rjson.id),indent=2),encoding="utf-8")
    rg=Report(scan_id=scan.id,report_type="GEOJSON",file_path=str(root/"report.geojson")); db.add(rg); db.flush(); (root/"report.geojson").write_text(json.dumps(feature_collection(dets),indent=2),encoding="utf-8")
    rc=Report(scan_id=scan.id,report_type="CSV",file_path=str(root/"report.csv")); db.add(rc); db.flush()
    rows=[detection_dict(d) for d in dets]
    with (root/"report.csv").open("w",newline="",encoding="utf-8") as f:
        fields=list(rows[0].keys()) if rows else ["detection_id","scan_id","class_name"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return {"json":rjson,"geojson":rg,"csv":rc}
