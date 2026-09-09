from abc import ABC, abstractmethod
from pathlib import Path
import shutil
from app.config import settings
class StorageService(ABC):
    @abstractmethod
    def save_file(self, source, object_name: str) -> str: ...
    @abstractmethod
    def get_file(self, object_name: str) -> Path: ...
class LocalStorageService(StorageService):
    def __init__(self): self.root=Path(settings.local_storage_path); [ (self.root/x).mkdir(parents=True,exist_ok=True) for x in ("raw","processed","reports","demo") ]
    def save_file(self, source, object_name):
        dest=self.root/object_name; dest.parent.mkdir(parents=True,exist_ok=True); source.seek(0); 
        with dest.open("wb") as f: shutil.copyfileobj(source,f)
        return object_name
    def get_file(self, object_name):
        p=self.root/object_name
        if not p.exists(): raise FileNotFoundError(object_name)
        return p
storage_service = LocalStorageService()
