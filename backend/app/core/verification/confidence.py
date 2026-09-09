"""
Confidence scoring for NEZA AI
Calculates final confidence score combining multiple factors
"""
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    def __init__(self):
        self.yolo_weight = 0.6
        self.mask_weight = 0.3
        self.shadow_weight = 0.1
    
    def calculate(self, yolo_confidence: float, mask_coverage: float = None, shadow_score: float = 0.5) -> float:
        """
        Calculate final confidence score (0-100%)
        
        Args:
            yolo_confidence: Raw confidence from YOLO (0-1)
            mask_coverage: Coverage from U-Net mask (0-1)
            shadow_score: Shadow verification score (0-1)
            
        Returns:
            Confidence percentage (0-100)
        """
        # Start with YOLO confidence
        confidence = yolo_confidence
        
        # Adjust with mask coverage if available
        if mask_coverage is not None:
            mask_factor = min(1.0, mask_coverage * 1.5)  # Boost good masks
            confidence = confidence * (1 - self.mask_weight) + mask_factor * self.mask_weight
        
        # Adjust with shadow score
        confidence = confidence * (1 - self.shadow_weight) + shadow_score * self.shadow_weight
        
        # Clamp and convert to percentage
        confidence = max(0, min(1, confidence))
        return round(confidence * 100, 1)
    
    def calculate_batch(self, detections: list) -> list:
        """
        Calculate confidence for multiple detections
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List with updated confidence scores
        """
        for det in detections:
            mask_coverage = det.get('mask_coverage', None)
            shadow_score = det.get('shadow_score', 0.5)
            det['confidence'] = self.calculate(
                det.get('yolo_confidence', 0.5),
                mask_coverage,
                shadow_score
            )
        return detections
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Get confidence level string
        
        Args:
            confidence: Confidence percentage (0-100)
            
        Returns:
            'HIGH', 'MEDIUM', or 'LOW'
        """
        if confidence >= 80:
            return 'HIGH'
        elif confidence >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
