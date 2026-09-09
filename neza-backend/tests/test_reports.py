import pytest
pytest.importorskip("geoalchemy2")
from app.services.report_service import summary

def test_report_summary():
    class D: pass
    ds=[]
    for status,sev,loc in [("CONFIRMED","HIGH",True),("PENDING","MEDIUM",True),("REJECTED","LOW",False)]:
        d=D(); d.verification_status=status; d.severity=sev; d.latitude=1 if loc else None; d.longitude=2 if loc else None; ds.append(d)
    s=summary(ds)
    assert s=={"total_detections":3,"confirmed":1,"pending":1,"rejected":1,"geotagged":2,"high_priority":1}
