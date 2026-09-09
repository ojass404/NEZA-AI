from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from app.core.logging import configure_logging
from app.core.exceptions import AppError, app_error_handler

configure_logging()
app = FastAPI(title="NEZA AI Backend", version=settings.app_version, description="Prototype backend for AI-powered marine debris and underwater anomaly intelligence.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(AppError, app_error_handler)
app.include_router(api_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def root():
    return {"service": "NEZA AI Backend", "docs": "/docs"}
