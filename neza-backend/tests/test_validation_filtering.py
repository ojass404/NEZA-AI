import pytest
from app.schemas.metadata import MetadataCreate
from app.services.filtering_service import filter_detections
from app.services.inference_service import RawDetection

def test_latitude_validation():
    with pytest.raises(ValueError): MetadataCreate(latitude=91,longitude=0)

def test_longitude_validation():
    with pytest.raises(ValueError): MetadataCreate(latitude=0,longitude=181)

def test_heading_validation():
    with pytest.raises(ValueError): MetadataCreate(latitude=0,longitude=0,heading_deg=360)

def test_confidence_filtering():
    result=filter_detections([RawDetection("x",.49,0,0,1,1),RawDetection("y",.50,0,0,1,1)])
    assert result[0][1]=="FILTERED"
    assert result[1][1]=="PASSED"
