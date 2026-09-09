"""
U-Net Semantic Segmentation for NEZA AI
Creates pixel-perfect masks of marine debris
"""
import torch
import numpy as np
import cv2
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    import segmentation_models_pytorch as smp
    HAS_SMP = True
except ImportError:
    HAS_SMP = False
    logger.warning("⚠️ segmentation-models-pytorch not installed. Using dummy U-Net.")

class UNetSegmentor:
    def __init__(self, model_path: str = "models/unet_resnet50_sss.pth"):
        """
        Initialize U-Net segmentor
        
        Args:
            model_path: Path to the trained U-Net model
        """
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_size = (640, 640)
        
        # Initialize model
        self.model = self._create_model()
        
        # Load weights if available
        if Path(model_path).exists() and HAS_SMP:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info(f"✅ U-Net model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load U-Net weights: {e}")
        
        self.model.to(self.device)
        self.model.eval()
    
    def _create_model(self):
        """Create U-Net model"""
        if HAS_SMP:
            return smp.Unet(
                encoder_name="resnet50",
                encoder_weights="imagenet" if Path(self.model_path).exists() else None,
                in_channels=3,
                classes=2  # background + debris
            )
        else:
            # Dummy model for testing
            return None
    
    def segment(self, image: np.ndarray) -> np.ndarray:
        """
        Generate segmentation mask for image
        
        Args:
            image: numpy array (H, W, 3) in BGR format
            
        Returns:
            Binary mask (H, W) where 1 = debris, 0 = background
        """
        if self.model is None:
            # Return dummy mask for testing
            return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        
        # Preprocess image
        img = cv2.resize(image, self.input_size)
        img = img / 255.0  # Normalize
        img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
        
        # Convert to tensor
        tensor = torch.from_numpy(img).float().unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            output = self.model(tensor)
            mask = torch.sigmoid(output)
            mask = (mask > 0.5).float()
        
        # Convert to numpy and resize back
        mask = mask[0, 0].cpu().numpy()
        mask = (mask * 255).astype(np.uint8)
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        
        return mask
    
    def get_mask_overlay(self, image: np.ndarray, mask: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Overlay mask on image for visualization
        
        Args:
            image: Original image
            mask: Binary mask
            alpha: Transparency factor
            
        Returns:
            Image with mask overlay
        """
        overlay = image.copy()
        mask_colored = np.zeros_like(image)
        mask_colored[mask > 0] = [0, 255, 0]  # Green mask
        overlay = cv2.addWeighted(overlay, 1 - alpha, mask_colored, alpha, 0)
        return overlay

# Quick test
if __name__ == "__main__":
    segmentor = UNetSegmentor("models/unet_resnet50_sss.pth")
    dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    mask = segmentor.segment(dummy_image)
    print(f"✅ Mask shape: {mask.shape}")
