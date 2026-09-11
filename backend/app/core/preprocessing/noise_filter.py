"""Optional deterministic preprocessing for side-scan sonar imagery."""

import cv2
import numpy as np


class SonarPreprocessor:
    """Reduce speckle noise and improve local contrast."""

    def __init__(
        self,
        median_kernel: int = 3,
        bilateral_diameter: int = 5,
        bilateral_sigma_color: float = 35.0,
        bilateral_sigma_space: float = 35.0,
        clahe_clip_limit: float = 2.0,
    ) -> None:
        if median_kernel < 3 or median_kernel % 2 == 0:
            raise ValueError(
                "median_kernel must be an odd integer of at least 3."
            )

        self.median_kernel = median_kernel
        self.bilateral_diameter = bilateral_diameter
        self.bilateral_sigma_color = bilateral_sigma_color
        self.bilateral_sigma_space = bilateral_sigma_space
        self.clahe = cv2.createCLAHE(
            clipLimit=clahe_clip_limit,
            tileGridSize=(8, 8),
        )

    @staticmethod
    def _to_uint8(image: np.ndarray) -> np.ndarray:
        if image is None:
            raise ValueError("Input image cannot be None.")

        if not isinstance(image, np.ndarray):
            raise TypeError("Input image must be a NumPy array.")

        if image.size == 0:
            raise ValueError("Input image cannot be empty.")

        if image.dtype == np.uint8:
            return image.copy()

        values = image.astype(np.float32)
        minimum = float(values.min())
        maximum = float(values.max())

        if maximum <= minimum:
            return np.zeros(values.shape, dtype=np.uint8)

        normalized = cv2.normalize(
            values,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        )
        return normalized.astype(np.uint8)

    def pipeline(self, image: np.ndarray) -> np.ndarray:
        """Return an enhanced image with the same channel layout."""
        source = self._to_uint8(image)
        original_was_color = source.ndim == 3

        if original_was_color:
            grayscale = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        elif source.ndim == 2:
            grayscale = source
        else:
            raise ValueError(
                "Expected a grayscale or three-channel BGR image."
            )

        filtered = cv2.medianBlur(
            grayscale,
            self.median_kernel,
        )

        filtered = cv2.bilateralFilter(
            filtered,
            self.bilateral_diameter,
            self.bilateral_sigma_color,
            self.bilateral_sigma_space,
        )

        enhanced = self.clahe.apply(filtered)

        if original_was_color:
            return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        return enhanced

    def shadow_map(self, image: np.ndarray) -> np.ndarray:
        """Create a diagnostic gradient map; not a confidence score."""
        source = self._to_uint8(image)

        if source.ndim == 3:
            source = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)

        gradient_x = cv2.Sobel(
            source,
            cv2.CV_32F,
            1,
            0,
            ksize=3,
        )

        return cv2.convertScaleAbs(gradient_x)
