from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
class UploadResponse(BaseModel): scan_id: UUID; filename: str; status: str; message: str
class ScanResponse(BaseModel):
    scan_id: UUID; filename: str; status: str; detection_count: int; geotagged_detection_count: int; created_at: datetime; updated_at: datetime
class ProcessResponse(BaseModel): scan_id: UUID; status: str; message: str
