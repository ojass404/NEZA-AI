from types import SimpleNamespace
from app.services.geotagging_service import geotag_detection

def test_frame_level_geotagging():
    meta=SimpleNamespace(latitude=19.076, longitude=72.8777, heading_deg=None, sonar_range_m=None, port_or_starboard=None)
    det=SimpleNamespace(x=100,y=100,width=50,height=50)
    result=geotag_detection(meta,det,1000,700)
    assert result.method=="FRAME_LEVEL"
    assert result.latitude==19.076
    assert result.longitude==72.8777

def test_unavailable_without_metadata():
    det=SimpleNamespace(x=1,y=1,width=1,height=1)
    result=geotag_detection(None,det,1000,700)
    assert result.method=="UNAVAILABLE"
    assert result.latitude is None
