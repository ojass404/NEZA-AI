"""
Inference Service - Main integration point for NEZA AI
Uses trained YOLO model for detection
"""
import sys
from pathlib import Path
import numpy as np
import cv2
import logging

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.detection.yolo_detector import YOLODetector
from app.core.detection.unet_segmentor import UNetSegmentor
from app.core.preprocessing.noise_filter import SonarPreprocessor
from app.core.verification.confidence import ConfidenceScorer
from app.core.verification.priority import PriorityAssigner

logger = logging.getLogger(__name__)

class InferenceService:
    def __init__(self, model_path: str = None):
        """
        Initialize Inference Service
        
        Args:
            model_path: Optional path to trained model
                       Defaults to backend/models/yolov8n_sss.pt
        """
        logger.info("🚀 Initializing InferenceService...")
        
        # Get project root
        project_root = "/Users/ojasmahajan/Public/Projects/NEZA-AI"
        
        # Use provided model path or default
        if model_path is None:
            model_path = f"{project_root}/backend/models/yolov8n_sss.pt"
        
        yolo_path = Path(model_path)
        unet_path = Path(f"{project_root}/backend/models/unet_resnet50_sss.pth")
        
        logger.info(f"YOLO model path: {yolo_path}")
        logger.info(f"U-Net model path: {unet_path}")
        
        try:
            self.preprocessor = SonarPreprocessor()
            self.yolo = YOLODetector(str(yolo_path))
            self.unet = UNetSegmentor(str(unet_path) if unet_path.exists() else None)
            self.scorer = ConfidenceScorer()
            self.prioritizer = PriorityAssigner()
            logger.info("✅ All components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize: {e}")
            raise
    
    def process_image(self, image: np.ndarray, metadata: dict = None) -> dict:
        """Process image through complete pipeline"""
        if metadata is None:
            metadata = {}
        
        logger.info("📊 Processing image...")
        
        # 1. Preprocess
        enhanced = self.preprocessor.pipeline(image)
        
        # 2. YOLO Detection
        yolo_results = self.yolo.detect(enhanced)
        
        # 3. U-Net Segmentation
        mask = self.unet.segment(enhanced) if self.unet else None
        mask_coverage = np.mean(mask > 0) if mask is not None else 0
        
        # 4. Process each detection
        detections = []
        for det in yolo_results:
            confidence = self.scorer.calculate(
                det['confidence'],
                mask_coverage,
                shadow_score=0.5
            )
            
            priority = self.prioritizer.assign(confidence, det['class'])
            
            detection = {
                'id': f"det_{len(detections) + 1:04d}",
                'class': det['class'],
                'confidence': confidence,
                'priority': priority,
                'bbox': det['bbox'],
                'latitude': metadata.get('latitude'),
                'longitude': metadata.get('longitude'),
                'mask_coverage': mask_coverage
            }
            detections.append(detection)
        
        # 5. Generate summary
        summary = self._generate_summary(detections)
        
        result = {
            'detections': detections,
            'summary': summary,
            'metadata': metadata
        }
        
        logger.info(f"✅ Processing complete. Found {len(detections)} detections")
        return result
    
    def _generate_summary(self, detections: list) -> dict:
        """Generate summary statistics"""
        if not detections:
            return {
                'total_detections': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'avg_confidence': 0,
                'classes': {}
            }
        
        priorities = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        classes = {}
        for det in detections:
            priorities[det['priority']] = priorities.get(det['priority'], 0) + 1
            classes[det['class']] = classes.get(det['class'], 0) + 1
        
        return {
            'total_detections': len(detections),
            'high_priority': priorities['HIGH'],
            'medium_priority': priorities['MEDIUM'],
            'low_priority': priorities['LOW'],
            'avg_confidence': round(sum(d['confidence'] for d in detections) / len(detections), 1),
            'classes': classes
        }
