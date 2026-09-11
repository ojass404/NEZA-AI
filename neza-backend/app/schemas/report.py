from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
class ReportSummary(BaseModel): total_detections:int; confirmed:int; pending:int; rejected:int; geotagged:int; high_priority:int
class ReportResponse(BaseModel): report_id:UUID; scan_id:UUID; generated_at:datetime; summary:ReportSummary; detections:list[dict]
