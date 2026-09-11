from pathlib import Path
import mimetypes, re
from app.config import settings
ALLOWED_EXTENSIONS={".jpg",".jpeg",".png",".tif",".tiff"}
def safe_filename(name):
    base=Path(name or "upload").name
    return re.sub(r"[^A-Za-z0-9._-]", "_", base)[:255]
def validate_upload(filename,size):
    ext=Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS: raise ValueError(f"Unsupported file type: {ext}")
    if size<=0: raise ValueError("Uploaded file is empty")
    if size>settings.max_upload_bytes: raise ValueError(f"File exceeds {settings.max_upload_size_mb} MB limit")
