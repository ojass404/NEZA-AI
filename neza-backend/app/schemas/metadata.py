from datetime import datetime
from pydantic import BaseModel, Field, field_validator
class MetadataCreate(BaseModel):
    timestamp: datetime | None = None
    latitude: float
    longitude: float
    depth_m: float | None = Field(default=None, ge=0)
    heading_deg: float | None = None
    altitude_m: float | None = Field(default=None, ge=0)
    vehicle_type: str | None = None
    vehicle_id: str | None = None
    sonar_range_m: float | None = Field(default=None, gt=0)
    port_or_starboard: str | None = None
    ping_id: str | None = None
    source: str | None = None
    crs: str = "EPSG:4326"
    metadata_json: dict = Field(default_factory=dict)
    @field_validator("latitude")
    @classmethod
    def lat(cls,v):
        if not -90 <= v <= 90: raise ValueError("latitude must be between -90 and 90")
        return v
    @field_validator("longitude")
    @classmethod
    def lon(cls,v):
        if not -180 <= v <= 180: raise ValueError("longitude must be between -180 and 180")
        return v
    @field_validator("port_or_starboard")
    @classmethod
    def side(cls,v):
        if v is not None and v.lower() not in {"port","starboard"}: raise ValueError("port_or_starboard must be port or starboard")
        return v.lower() if v else v
    @field_validator("heading_deg")
    @classmethod
    def heading(cls,v):
        if v is not None and not 0 <= v < 360: raise ValueError("heading_deg must be in [0, 360)")
        return v

