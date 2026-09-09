from dataclasses import dataclass
from app.geospatial.coordinates import destination_from_offset
@dataclass
class GeoTagResult:
    latitude:float|None; longitude:float|None; method:str; accuracy_estimate_m:float|None

def geotag_detection(meta, det, image_width:int, image_height:int):
    if not meta: return GeoTagResult(None,None,"UNAVAILABLE",None)
    if meta.latitude is None or meta.longitude is None: return GeoTagResult(None,None,"UNAVAILABLE",None)
    # Exact GPS is only appropriate when the survey explicitly identifies the detection location as the GPS fix.
    # With only frame GPS, use FRAME_LEVEL. Never fabricate a point from pixels alone.
    if meta.sonar_range_m is None or meta.heading_deg is None or not getattr(meta,"port_or_starboard",None):
        return GeoTagResult(meta.latitude,meta.longitude,"FRAME_LEVEL",None)
    side=getattr(meta,"port_or_starboard",None).lower()
    if side not in {"port","starboard"}: return GeoTagResult(meta.latitude,meta.longitude,"FRAME_LEVEL",None)
    center_x=det.x + det.width/2
    normalized=(center_x/image_width)-0.5
    cross_track=normalized*2*meta.sonar_range_m
    if side=="port": cross_track=-abs(cross_track)
    else: cross_track=abs(cross_track)
    import math
    bearing=math.radians((meta.heading_deg + (90 if cross_track>=0 else -90)) % 360)
    east=abs(cross_track)*math.sin(bearing); north=abs(cross_track)*math.cos(bearing)
    lat,lon=destination_from_offset(meta.latitude,meta.longitude,east,north)
    return GeoTagResult(lat,lon,"OFFSET_ESTIMATE",None)
