from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2 import Geography
from app.database.connection import get_db
from app.models.detection import Detection
from app.geospatial.geojson import feature_collection
router=APIRouter(prefix="/map",tags=["Map"])
@router.get("/detections")
def map_detections(min_lat:float|None=None,max_lat:float|None=None,min_lon:float|None=None,max_lon:float|None=None,min_confidence:float=Query(0,ge=0,le=1),class_name:str|None=None,severity:str|None=None,verification_status:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Detection).filter(Detection.confidence>=min_confidence,Detection.latitude.isnot(None),Detection.longitude.isnot(None))
    if min_lat is not None:q=q.filter(Detection.latitude>=min_lat)
    if max_lat is not None:q=q.filter(Detection.latitude<=max_lat)
    if min_lon is not None:q=q.filter(Detection.longitude>=min_lon)
    if max_lon is not None:q=q.filter(Detection.longitude<=max_lon)
    if class_name:q=q.filter(Detection.class_name==class_name)
    if severity:q=q.filter(Detection.severity==severity)
    if verification_status:q=q.filter(Detection.verification_status==verification_status)
    return feature_collection(q.all())
@router.get("/detections/nearby")
def nearby(latitude:float,longitude:float,radius_m:float=Query(1000,gt=0),db:Session=Depends(get_db)):
    point=func.ST_SetSRID(func.ST_MakePoint(longitude,latitude),4326)
    q=db.query(Detection).filter(Detection.location.isnot(None),func.ST_DWithin(Detection.location,point,radius_m))
    return feature_collection(q.all())
