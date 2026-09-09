"""
Priority assignment for NEZA AI
Assigns HIGH/MEDIUM/LOW priority based on confidence and class
"""
import logging

logger = logging.getLogger(__name__)

class PriorityAssigner:
    def __init__(self):
        # Classes that get priority boost
        self.high_priority_classes = ['ghost_net', 'shipwreck']
        self.medium_priority_classes = ['pipe', 'cylinder', 'container']
        
        self.high_confidence_threshold = 80
        self.medium_confidence_threshold = 50
    
    def assign(self, confidence: float, class_name: str) -> str:
        """
        Assign priority based on confidence and class
        
        Args:
            confidence: Confidence percentage (0-100)
            class_name: Name of the detected class
            
        Returns:
            'HIGH', 'MEDIUM', or 'LOW'
        """
        # Check if high priority class
        if class_name in self.high_priority_classes:
            if confidence >= 60:  # Lower threshold for high-priority classes
                return 'HIGH'
            elif confidence >= 40:
                return 'MEDIUM'
        
        # Check if medium priority class
        if class_name in self.medium_priority_classes:
            if confidence >= 70:
                return 'HIGH'
            elif confidence >= 40:
                return 'MEDIUM'
        
        # Default based on confidence only
        if confidence >= self.high_confidence_threshold:
            return 'HIGH'
        elif confidence >= self.medium_confidence_threshold:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def assign_batch(self, detections: list) -> list:
        """
        Assign priority to multiple detections
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List with updated priority values
        """
        for det in detections:
            det['priority'] = self.assign(
                det.get('confidence', 0),
                det.get('class', 'unknown')
            )
        return detections
