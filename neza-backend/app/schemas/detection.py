from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
class BBox(BaseModel): x: float; y: float; width: float; height: float
class Location(BaseModel): latitude: float; longitude: float
class DetectionResponse(BaseModel):
    id: UUID; scan_id: UUID; class_name: str; confidence: float; confidence_percent: int; bbox: BBox; location: Location | None; severity: str | None; verification_status: str; filter_status: str; geotagging_method: str; location_accuracy_m: float | None; estimated_length_m: float | None; estimated_width_m: float | None; estimated_area_m2: float | None; model_name: str | None; model_version: str | None; created_at: datetime
class DetectionsResponse(BaseModel): scan_id: UUID; count: int; detections: list[DetectionResponse]
class VerificationUpdate(BaseModel):
    verification_status: str
    notes: str | None = None
    verified_by: str | None = None
