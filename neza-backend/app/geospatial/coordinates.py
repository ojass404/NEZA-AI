from math import cos, radians

def validate_lat_lon(latitude: float, longitude: float):
    if not -90 <= latitude <= 90: raise ValueError("latitude out of range")
    if not -180 <= longitude <= 180: raise ValueError("longitude out of range")

def destination_from_offset(lat: float, lon: float, east_m: float, north_m: float):
    """Small-distance WGS84 approximation; suitable for prototype offsets."""
    lat2 = lat + north_m / 111_320.0
    lon2 = lon + east_m / (111_320.0 * max(cos(radians(lat)), 1e-9))
    validate_lat_lon(lat2, lon2)
    return lat2, lon2

def geojson_point(lon: float, lat: float): return {"type":"Point","coordinates":[lon,lat]}
