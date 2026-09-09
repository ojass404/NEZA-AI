"""
Test script to verify models are working
"""
import sys
import cv2
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.core.detection.yolo_detector import YOLODetector
from app.core.detection.unet_segmentor import UNetSegmentor
from app.core.preprocessing.noise_filter import SonarPreprocessor

def test_models():
    print("🧪 Testing NEZA AI ML Models...")
    
    # 1. Test Preprocessor
    print("📌 Testing Preprocessor...")
    preprocessor = SonarPreprocessor()
    
    # 2. Test YOLO
    print("📌 Testing YOLO Detector...")
    try:
        yolo = YOLODetector("../backend/models/yolov8n_sss.pt")
        print("✅ YOLO loaded successfully")
    except Exception as e:
        print(f"❌ YOLO failed: {e}")
    
    # 3. Test U-Net
    print("📌 Testing U-Net Segmentor...")
    try:
        unet = UNetSegmentor("../backend/models/unet_resnet50_sss.pth")
        print("✅ U-Net loaded successfully")
    except Exception as e:
        print(f"❌ U-Net failed: {e}")
    
    # 4. Create a dummy image and test detection
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    print("📌 Testing inference on dummy image...")
    try:
        # Preprocess
        preprocessed = preprocessor.pipeline(dummy_image)
        
        # Detect
        results = yolo.detect(preprocessed)
        print(f"✅ Detection successful! Found {len(results)} objects")
        
        # Segment
        mask = unet.segment(preprocessed)
        print(f"✅ Segmentation successful! Mask shape: {mask.shape}")
        
    except Exception as e:
        print(f"❌ Inference failed: {e}")
    
    print("🎉 Model testing complete!")

if __name__ == "__main__":
    test_models()
