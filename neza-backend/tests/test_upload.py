import pytest
pytest.importorskip("geoalchemy2")
from app.utils.file_validation import validate_upload, safe_filename

def test_invalid_file_extension():
    with pytest.raises(ValueError): validate_upload("bad.exe",10)

def test_empty_file():
    with pytest.raises(ValueError): validate_upload("scan.jpg",0)

def test_filename_is_sanitized():
    assert safe_filename("../../evil file.jpg")=="evil_file.jpg"
