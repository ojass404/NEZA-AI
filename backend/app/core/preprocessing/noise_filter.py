"""
Noise filtering for sonar imagery
Reduces speckle noise and enhances image quality
"""
import cv2
import numpy as np
from skimage.restoration import denoise_wavelet
import logging

logger = logging.getLogger(__name__)

class SonarPreprocessor:
    def __init__(self):
        self.filters = [
            self.speckle_reduction,
            self.bilateral_filter,
            self.clahe_enhancement
        ]
    
    def pipeline(self, image: np.ndarray) -> np.ndarray:
        """
        Apply full preprocessing pipeline
        
        Args:
            image: Input sonar image
            
        Returns:
            Enhanced image
        """
        if image is None:
            return image
        
        result = image.copy()
        
        # Convert to grayscale if needed
        if len(result.shape) == 3 and result.shape[2] == 3:
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        else:
            gray = result
        
        # Apply filters
        for filter_fn in self.filters:
            try:
                gray = filter_fn(gray)
            except Exception as e:
                logger.warning(f"⚠️ Filter {filter_fn.__name__} failed: {e}")
        
        # Convert back to 3-channel if input was color
        if len(result.shape) == 3 and result.shape[2] == 3:
            result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        else:
            result = gray
        
        return result
    
    def speckle_reduction(self, image: np.ndarray) -> np.ndarray:
        """Reduce speckle noise using wavelet denoising"""
        try:
            return denoise_wavelet(image, method='BayesShrink', mode='soft', rescale_sigma=True)
        except:
            # Fallback to median filter
            return cv2.medianBlur(image, 5)
    
    def bilateral_filter(self, image: np.ndarray) -> np.ndarray:
        """Preserve edges while smoothing"""
        return cv2.bilateralFilter(image, 9, 75, 75)
    
    def clahe_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Contrast Limited Adaptive Histogram Equalization"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image.astype(np.uint8))
    
    def shadow_enhance(self, image: np.ndarray, direction='horizontal') -> np.ndarray:
        """Enhance acoustic shadows"""
        # Simple shadow enhancement using directional filtering
        kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        if direction == 'horizontal':
            kernel = kernel.T
        
        shadow_map = cv2.filter2D(image.astype(np.float32), -1, kernel)
        shadow_map = np.clip(shadow_map, 0, 255).astype(np.uint8)
        
        return cv2.addWeighted(image, 0.7, shadow_map, 0.3, 0)
