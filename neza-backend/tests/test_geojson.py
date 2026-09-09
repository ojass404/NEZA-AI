from app.geospatial.geojson import feature_collection

def test_geojson_coordinate_order():
    class D: pass
    d=D(); d.id="d1"; d.scan_id="s1"; d.latitude=19.0760; d.longitude=72.8777; d.class_name="fishing_net"; d.confidence=.91; d.confidence_percent=91; d.severity="HIGH"; d.verification_status="PENDING"; d.estimated_length_m=None; d.estimated_width_m=None; d.estimated_area_m2=None; d.geotagging_method="FRAME_LEVEL"; d.location_accuracy_m=None
    geo=feature_collection([d])
    coords=geo["features"][0]["geometry"]["coordinates"]
    assert coords[0]==d.longitude
    assert coords[1]==d.latitude
