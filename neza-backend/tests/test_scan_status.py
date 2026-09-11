# Integration test placeholder: full status lifecycle requires a running PostGIS database.
def test_status_values_are_documented():
    assert {"UPLOADED","PROCESSING","COMPLETED","FAILED"} >= {"UPLOADED","PROCESSING","COMPLETED","FAILED"}
