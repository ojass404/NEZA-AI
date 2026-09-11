import pytest
pytest.importorskip("geoalchemy2")
from app.schemas.detection import VerificationUpdate

def test_verification_schema_accepts_status():
    p=VerificationUpdate(verification_status="CONFIRMED",notes="ok")
    assert p.verification_status=="CONFIRMED"
