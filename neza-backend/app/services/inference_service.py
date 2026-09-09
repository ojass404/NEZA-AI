from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import hashlib
@dataclass
class RawDetection:
    class_name:str; confidence:float; x:float; y:float; width:float; height:float
class InferenceProvider(ABC):
    @abstractmethod
    def predict(self,image_path:Path)->list[RawDetection]: ...
class MockInferenceProvider(InferenceProvider):
    """Deterministic demo provider. These are synthetic detections, not model results."""
    def predict(self,image_path):
        digest=int(hashlib.sha256(image_path.name.encode()).hexdigest()[:8],16)
        shift=digest%30
        return [RawDetection("marine_debris",0.91,400+shift,250,120,80),RawDetection("fishing_net",0.74,700,320,160,90),RawDetection("unknown_anomaly",0.42,180,150,90,60),RawDetection("pipe",0.63,520,500,100,70)]

def get_inference_provider():
    from app.config import settings
    if settings.ai_provider.lower()=="mock": return MockInferenceProvider()
    raise ValueError(f"Unsupported AI_PROVIDER={settings.ai_provider}. Add a real provider implementation in inference_service.py.")
