from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg2://neza:neza@localhost:5432/neza"
    storage_mode: str = "local"
    local_storage_path: str = "./storage"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "neza-sonar"
    minio_enabled: bool = False
    ai_provider: str = "mock"
    ai_confidence_threshold: float = Field(default=0.50, ge=0, le=1)
    default_crs: str = "EPSG:4326"
    max_upload_size_mb: int = Field(default=200, gt=0)
    cors_origins_raw: str = "http://localhost:5173,http://127.0.0.1:5173"
    @property
    def cors_origins(self): return [x.strip() for x in self.cors_origins_raw.split(",") if x.strip()]
    @property
    def max_upload_bytes(self): return self.max_upload_size_mb * 1024 * 1024

@lru_cache
def get_settings(): return Settings()
settings = get_settings()
