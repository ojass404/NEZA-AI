from app.services.inference_service import RawDetection
from app.config import settings

def filter_detections(detections):
    out=[]
    for d in detections:
        if d.confidence < settings.ai_confidence_threshold:
            out.append((d,"FILTERED","Below confidence threshold"))
        else: out.append((d,"PASSED",None))
    return out

def severity_for(confidence):
    if confidence >= .85: return "HIGH"
    if confidence >= .65: return "MEDIUM"
    return "LOW"
