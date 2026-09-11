from fastapi import APIRouter
from app.api.v1 import health, scans, detections, reports, map as map_api
from app.core.exceptions import AppError, app_error_handler
api_router=APIRouter()
api_router.include_router(health.router); api_router.include_router(scans.router); api_router.include_router(detections.router); api_router.include_router(reports.router); api_router.include_router(map_api.router)
