"""
YOLO Object Detection for NEZA AI
Detects bounding boxes around marine debris in sonar imagery
"""
import torch
import numpy as np
from ultralytics import YOLO
import cv2
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class YOLODetector:
    def __init__(self, model_path: str):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to the trained YOLO model (absolute path)
        """
        self.model_path = model_path
        self.confidence_threshold = 0.25
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Check if model exists
        if not Path(model_path).exists():
            logger.error(f"❌ Model not found at: {model_path}")
            logger.info("📥 Downloading default YOLO model...")
            try:
                # Download default model
                self.model = YOLO('yolov8n.pt')
                # Save it to the specified path
                self.model.save(model_path)
                logger.info(f"✅ Model downloaded and saved to: {model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download model: {e}")
                raise
        else:
            try:
                self.model = YOLO(model_path)
                logger.info(f"✅ YOLO model loaded from {model_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load YOLO model: {e}")
                raise
        
    def detect(self, image: np.ndarray) -> list:
        """
        Run YOLO detection on image
        
        Args:
            image: numpy array (H, W, 3) in BGR format
            
        Returns:
            List of detections with class, confidence, bbox
        """
        if image is None:
            return []
        
        # Run inference
        results = self.model(image, conf=self.confidence_threshold, verbose=False)
        
        # Parse results
        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # Get class name and confidence
                    class_id = int(box.cls)
                    class_name = self.model.names[class_id]
                    confidence = float(box.conf)
                    
                    # Get bounding box (xyxy format)
                    bbox = box.xyxy[0].cpu().numpy().tolist()
                    
                    detections.append({
                        'class': class_name,
                        'class_id': class_id,
                        'confidence': confidence,
                        'bbox': bbox
                    })
        
        return detections
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for YOLO"""
        if image.shape[:2] != (640, 640):
            image = cv2.resize(image, (640, 640))
        return image
    
    def get_class_names(self) -> dict:
        """Get class name mapping"""
        return self.model.names
