def feature(d):
    if d.latitude is None or d.longitude is None: return None
    return {"type":"Feature","id":str(d.id),"geometry":{"type":"Point","coordinates":[d.longitude,d.latitude]},"properties":{
        "detection_id":str(d.id),"scan_id":str(d.scan_id),"class_name":d.class_name,"confidence":d.confidence,"confidence_percent":d.confidence_percent,
        "severity":d.severity,"verification_status":d.verification_status,"estimated_length_m":d.estimated_length_m,"estimated_width_m":d.estimated_width_m,
        "estimated_area_m2":d.estimated_area_m2,"geotagging_method":d.geotagging_method,"location_accuracy_m":d.location_accuracy_m}}

def feature_collection(detections): return {"type":"FeatureCollection","features":[x for d in detections if (x:=feature(d)) is not None]}
