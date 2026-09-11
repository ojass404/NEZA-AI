# Reserved for future CRS transformations using pyproj.
def ensure_wgs84(crs: str):
    if crs.upper() != "EPSG:4326":
        raise ValueError("Prototype geotagging currently expects EPSG:4326 metadata")
    return "EPSG:4326"
