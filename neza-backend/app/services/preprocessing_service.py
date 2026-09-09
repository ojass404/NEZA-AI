from dataclasses import dataclass
from pathlib import Path
import cv2
@dataclass
class PreprocessingConfig:
    resize_width:int|None=None; resize_height:int|None=None; denoise_enabled:bool=False; contrast_enabled:bool=False; normalization_enabled:bool=False

def preprocess(image_path: Path, output_path: Path, config: PreprocessingConfig|None=None):
    config=config or PreprocessingConfig()
    image=cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if image is None: raise ValueError("Unable to read image")
    if len(image.shape)==3: image=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if config.resize_width and config.resize_height: image=cv2.resize(image,(config.resize_width,config.resize_height))
    if config.denoise_enabled: image=cv2.GaussianBlur(image,(3,3),0)
    if config.contrast_enabled: image=cv2.equalizeHist(image)
    if config.normalization_enabled: image=cv2.normalize(image,None,0,255,cv2.NORM_MINMAX)
    output_path.parent.mkdir(parents=True,exist_ok=True); cv2.imwrite(str(output_path),image); return output_path
