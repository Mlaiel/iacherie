"""Image Effects Engine
Creative image effects and artistic filters for professional content creation.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from scipy import ndimage
from scipy.ndimage import gaussian_filter
from typing import Dict, Optional, Union, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import skimage
from skimage import filters, segmentation, measure

logger = logging.getLogger(__name__)

@dataclass
class ImageEffectsConfig:
    """Configuration for image effects."""
    output_quality: int = 95  # JPEG quality 1-100
    preserve_exif: bool = True
    output_format: str = "JPEG"  # JPEG, PNG, WEBP
    resize_enabled: bool = False
    target_size: Tuple[int, int] = (1920, 1080)
    maintain_aspect_ratio: bool = True
    gpu_acceleration: bool = True
    batch_processing: bool = False

class ArtisticFilters:
    """Collection of artistic filter effects."""
    
    def __init__(self, config -> None: ImageEffectsConfig) -> None:
        self.config = config
    
    def oil_painting_effect(self, image: np.ndarray, radius: int = 7, intensity: int = 20) -> np.ndarray:
        """Create oil painting effect."""
        # Convert to RGB if BGR
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Apply oil painting effect using OpenCV
        oil_painted = cv2.xphoto.oilPainting(rgb_image, radius, intensity)
        
        # Convert back to BGR if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            return cv2.cvtColor(oil_painted, cv2.COLOR_RGB2BGR)
        return oil_painted
    
    def watercolor_effect(self, image: np.ndarray, sigma_s: float = 50, sigma_r: float = 0.2) -> np.ndarray:
        """Create watercolor effect using bilateral filtering."""
        # Apply bilateral filter multiple times for watercolor effect
        result = image.copy()
        
        for _ in range(3):
            result = cv2.bilateralFilter(result, 9, sigma_r * 255, sigma_s)
        
        # Add edge enhancement
        edges = cv2.Canny(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY), 50, 150)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Blend with original
        result = cv2.addWeighted(result, 0.8, edges_colored, 0.2, 0)
        
        return result
    
    def pencil_sketch_effect(self, image: np.ndarray, blur_value: int = 21) -> np.ndarray:
        """Create pencil sketch effect."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Create inverse image
        inverted = 255 - gray
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (blur_value, blur_value), 0)
        
        # Create pencil sketch
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        
        # Convert back to BGR
        sketch_colored = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        return sketch_colored
    
    def cartoon_effect(self, image: np.ndarray, num_down: int = 2, num_bilateral: int = 7) -> np.ndarray:
        """Create cartoon effect."""
        # Downsample image
        img = image.copy()
        for _ in range(num_down):
            img = cv2.pyrDown(img)
        
        # Apply bilateral filter
        for _ in range(num_bilateral):
            img = cv2.bilateralFilter(img, 9, 200, 200)
        
        # Upsample image
        for _ in range(num_down):
            img = cv2.pyrUp(img)
        
        # Resize to original dimensions
        if img.shape != image.shape:
            img = cv2.resize(img, (image.shape[1], image.shape[0]))
        
        # Create edge mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine cartoon and edges
        cartoon = cv2.bitwise_and(img, edges)
        
        return cartoon
    
    def vintage_effect(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """Create vintage photo effect."""
        result = image.copy().astype(np.float32)
        
        # Add warm color cast
        result[:, :, 0] *= 0.9  # Reduce blue
        result[:, :, 1] *= 1.1  # Enhance green
        result[:, :, 2] *= 1.2  # Enhance red
        
        # Add vignette effect
        h, w = result.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Create vignette mask
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        vignette = 1 - (dist_from_center / max_dist) * intensity
        vignette = np.clip(vignette, 0.2, 1.0)
        
        # Apply vignette
        for i in range(3):
            result[:, :, i] *= vignette
        
        # Add noise for grain effect
        noise = np.random.normal(0, 5, result.shape)
        result += noise * intensity
        
        return np.clip(result, 0, 255).astype(np.uint8)

class CreativeFilters:
    """Advanced creative filters and effects."""
    
    def __init__(self, config -> None: ImageEffectsConfig) -> None:
        self.config = config
    
    def pop_art_effect(self, image: np.ndarray, levels: int = 4) -> np.ndarray:
        """Create pop art effect with posterization."""
        # Quantize colors
        factor = 256 // levels
        quantized = (image // factor) * factor
        
        # Enhance saturation
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.5)  # Increase saturation
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Add edge lines
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        result = cv2.addWeighted(result, 0.9, edges_colored, 0.1, 0)
        
        return result
    
    def cyberpunk_effect(self, image: np.ndarray, intensity: float = 0.8) -> np.ndarray:
        """Create cyberpunk/neon effect."""
        result = image.copy().astype(np.float32)
        
        # Enhance blues and purples
        result[:, :, 0] *= (1 + intensity * 0.3)  # Blue
        result[:, :, 1] *= (1 - intensity * 0.2)  # Green (reduce)
        result[:, :, 2] *= (1 + intensity * 0.1)  # Red
        
        # Add neon glow effect
        blurred = cv2.GaussianBlur(result, (15, 15), 0)
        glow = cv2.addWeighted(result, 0.7, blurred, 0.3 * intensity, 0)
        
        # Increase contrast
        glow = cv2.convertScaleAbs(glow, alpha=1.2, beta=10)
        
        return np.clip(glow, 0, 255).astype(np.uint8)
    
    def dream_effect(self, image: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Create dreamy, ethereal effect."""
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(image, (21, 21), 0)
        
        # Create soft light blend
        dream = cv2.addWeighted(image, 1 - strength, blurred, strength, 0)
        
        # Add soft glow
        glow_blur = cv2.GaussianBlur(dream, (51, 51), 0)
        dream = cv2.addWeighted(dream, 0.8, glow_blur, 0.2 * strength, 0)
        
        # Lighten overall
        dream = cv2.convertScaleAbs(dream, alpha=1.0, beta=int(20 * strength))
        
        return dream
    
    def film_noir_effect(self, image: np.ndarray, contrast: float = 1.5) -> np.ndarray:
        """Create film noir effect."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast
        enhanced = cv2.convertScaleAbs(gray, alpha=contrast, beta=0)
        
        # Add dramatic shadows
        # Create shadow mask
        shadow_mask = enhanced < 100
        enhanced[shadow_mask] = enhanced[shadow_mask] * 0.5
        
        # Add highlights
        highlight_mask = enhanced > 180
        enhanced[highlight_mask] = np.minimum(enhanced[highlight_mask] * 1.2, 255)
        
        # Convert back to BGR for consistency
        noir = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return noir

class GeometricEffects:
    """Geometric transformation effects."""
    
    def __init__(self, config -> None: ImageEffectsConfig) -> None:
        self.config = config
    
    def fisheye_effect(self, image: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Create fisheye distortion effect."""
        h, w = image.shape[:2]
        
        # Create coordinate matrices
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Center coordinates
        cx, cy = w / 2, h / 2
        
        # Convert to polar coordinates
        x_centered = x - cx
        y_centered = y - cy
        r = np.sqrt(x_centered**2 + y_centered**2)
        theta = np.arctan2(y_centered, x_centered)
        
        # Apply fisheye distortion
        max_r = min(cx, cy)
        r_normalized = r / max_r
        r_distorted = r_normalized * (1 + strength * r_normalized**2)
        
        # Convert back to cartesian
        x_new = r_distorted * max_r * np.cos(theta) + cx
        y_new = r_distorted * max_r * np.sin(theta) + cy
        
        # Remap the image
        map_x = x_new.astype(np.float32)
        map_y = y_new.astype(np.float32)
        
        distorted = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)
        
        return distorted
    
    def swirl_effect(self, image: np.ndarray, strength: float = 1.0, radius: float = 0.5) -> np.ndarray:
        """Create swirl/spiral effect."""
        h, w = image.shape[:2]
        
        # Create coordinate matrices
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Center coordinates
        cx, cy = w / 2, h / 2
        
        # Convert to polar coordinates
        x_centered = x - cx
        y_centered = y - cy
        r = np.sqrt(x_centered**2 + y_centered**2)
        theta = np.arctan2(y_centered, x_centered)
        
        # Apply swirl effect
        max_r = min(cx, cy) * radius
        swirl_factor = np.where(r < max_r, strength * (1 - r / max_r), 0)
        theta_new = theta + swirl_factor
        
        # Convert back to cartesian
        x_new = r * np.cos(theta_new) + cx
        y_new = r * np.sin(theta_new) + cy
        
        # Remap the image
        map_x = x_new.astype(np.float32)
        map_y = y_new.astype(np.float32)
        
        swirled = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)
        
        return swirled

class ImageEffectsEngine:
    """Enterprise image effects processing engine with professional creative tools."""
    
    def __init__(self) -> None:
        self.config = ImageEffectsConfig()
        self.artistic_filters = ArtisticFilters(self.config)
        self.creative_filters = CreativeFilters(self.config)
        self.geometric_effects = GeometricEffects(self.config)
        
    async def apply_artistic_filter(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        filter_type: str = "oil_painting",
        intensity: float = 0.5,
        config: Optional[ImageEffectsConfig] = None
    ) -> Dict[str, any]:
        """Apply artistic filter to image."""
        try:
            if config:
                self.config = config
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {filter_type} filter: {input_path}")
            
            # Load image
            image = cv2.imread(str(input_path))
            if image is None:
                raise ValueError(f"Cannot load image: {input_path}")
            
            original_shape = image.shape
            
            # Apply artistic filter
            if filter_type == "oil_painting":
                result = self.artistic_filters.oil_painting_effect(
                    image, radius=int(7 * intensity), intensity=int(20 * intensity)
                )
            elif filter_type == "watercolor":
                result = self.artistic_filters.watercolor_effect(
                    image, sigma_s=50 * intensity, sigma_r=0.2 * intensity
                )
            elif filter_type == "pencil_sketch":
                result = self.artistic_filters.pencil_sketch_effect(
                    image, blur_value=int(21 * intensity)
                )
            elif filter_type == "cartoon":
                result = self.artistic_filters.cartoon_effect(
                    image, num_down=max(1, int(2 * intensity)), num_bilateral=int(7 * intensity)
                )
            elif filter_type == "vintage":
                result = self.artistic_filters.vintage_effect(image, intensity)
            elif filter_type == "pop_art":
                result = self.creative_filters.pop_art_effect(
                    image, levels=max(2, int(8 * intensity))
                )
            elif filter_type == "cyberpunk":
                result = self.creative_filters.cyberpunk_effect(image, intensity)
            elif filter_type == "dream":
                result = self.creative_filters.dream_effect(image, intensity)
            elif filter_type == "film_noir":
                result = self.creative_filters.film_noir_effect(
                    image, contrast=1.0 + intensity
                )
            elif filter_type == "fisheye":
                result = self.geometric_effects.fisheye_effect(image, intensity)
            elif filter_type == "swirl":
                result = self.geometric_effects.swirl_effect(image, intensity * 2)
            else:
                logger.warning(f"Unknown filter type: {filter_type}")
                result = image
            
            # Resize if configured
            if self.config.resize_enabled:
                if self.config.maintain_aspect_ratio:
                    h, w = result.shape[:2]
                    target_w, target_h = self.config.target_size
                    aspect_ratio = w / h
                    
                    if aspect_ratio > (target_w / target_h):
                        # Fit to width
                        new_w = target_w
                        new_h = int(target_w / aspect_ratio)
                    else:
                        # Fit to height
                        new_h = target_h
                        new_w = int(target_h * aspect_ratio)
                    
                    result = cv2.resize(result, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
                else:
                    result = cv2.resize(result, self.config.target_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Save result
            if self.config.output_format.upper() == "PNG":
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            elif self.config.output_format.upper() == "WEBP":
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_WEBP_QUALITY, self.config.output_quality])
            else:  # JPEG
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, self.config.output_quality])
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(image, result)
            
            logger.info("Artistic filter applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "filter_type": filter_type,
                "intensity": intensity,
                "original_shape": original_shape,
                "output_shape": result.shape,
                "quality_metrics": quality_metrics,
                "output_format": self.config.output_format
            }
            
        except Exception as e:
            logger.error(f"Artistic filter failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "filter_type": filter_type
            }
    
    async def apply_creative_effect(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        effect_type: str = "glow",
        parameters: Dict = None,
        config: Optional[ImageEffectsConfig] = None
    ) -> Dict[str, any]:
        """Apply creative effects with custom parameters."""
        try:
            if config:
                self.config = config
                
            if parameters is None:
                parameters = {"intensity": 0.5}
                
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            logger.info(f"Applying {effect_type} creative effect: {input_path}")
            
            # Load image
            image = cv2.imread(str(input_path))
            if image is None:
                raise ValueError(f"Cannot load image: {input_path}")
            
            intensity = parameters.get("intensity", 0.5)
            
            # Apply creative effect
            if effect_type == "glow":
                # Soft glow effect
                blurred = cv2.GaussianBlur(image, (51, 51), 0)
                result = cv2.addWeighted(image, 0.8, blurred, 0.2 * intensity, 0)
                
            elif effect_type == "sharpen":
                # Unsharp mask
                gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
                result = cv2.addWeighted(image, 1.0 + intensity, gaussian, -intensity, 0)
                
            elif effect_type == "emboss":
                # Emboss effect
                kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
                embossed = cv2.filter2D(image, -1, kernel)
                result = cv2.addWeighted(image, 1 - intensity, embossed, intensity, 128)
                
            elif effect_type == "sepia":
                # Sepia tone
                sepia_filter = np.array([[0.272, 0.534, 0.131],
                                       [0.349, 0.686, 0.168],
                                       [0.393, 0.769, 0.189]])
                sepia_image = cv2.transform(image, sepia_filter)
                result = cv2.addWeighted(image, 1 - intensity, sepia_image, intensity, 0)
                
            elif effect_type == "cross_process":
                # Cross processing effect
                result = image.copy().astype(np.float32)
                result[:, :, 0] = np.clip(result[:, :, 0] * 1.2 - 20, 0, 255)  # Blue
                result[:, :, 1] = np.clip(result[:, :, 1] * 0.8 + 30, 0, 255)   # Green
                result[:, :, 2] = np.clip(result[:, :, 2] * 1.1 + 10, 0, 255)   # Red
                result = result.astype(np.uint8)
                result = cv2.addWeighted(image, 1 - intensity, result, intensity, 0)
                
            else:
                logger.warning(f"Unknown effect type: {effect_type}")
                result = image
            
            # Save result
            if self.config.output_format.upper() == "PNG":
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                cv2.imwrite(str(output_path), result, [cv2.IMWRITE_JPEG_QUALITY, self.config.output_quality])
            
            logger.info("Creative effect applied successfully")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "effect_type": effect_type,
                "parameters": parameters,
                "output_format": self.config.output_format
            }
            
        except Exception as e:
            logger.error(f"Creative effect failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "input_path": str(input_path),
                "effect_type": effect_type
            }
    
    def _calculate_quality_metrics(self, original: np.ndarray, processed: np.ndarray) -> Dict[str, float]:
        """Calculate image quality metrics."""
        # Ensure same size for comparison
        if original.shape != processed.shape:
            processed = cv2.resize(processed, (original.shape[1], original.shape[0]))
        
        # Convert to grayscale for SSIM calculation
        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM (Structural Similarity Index)
        ssim = skimage.metrics.structural_similarity(original_gray, processed_gray)
        
        # Calculate PSNR (Peak Signal-to-Noise Ratio)
        mse = np.mean((original.astype(float) - processed.astype(float)) ** 2)
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
        
        return {
            "ssim": float(ssim),
            "psnr": float(psnr),
            "quality_score": float((ssim + min(psnr / 40, 1.0)) / 2)
        }
    
    async def batch_process(
        self,
        input_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        filter_type: str = "oil_painting",
        intensity: float = 0.5,
        config: Optional[ImageEffectsConfig] = None
    ) -> Dict[str, any]:
        """Batch process multiple images with the same filter."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for input_path in input_paths:
            input_path = Path(input_path)
            output_path = output_dir / f"{input_path.stem}_{filter_type}{input_path.suffix}"
            
            result = await self.apply_artistic_filter(input_path, output_path, filter_type, intensity, config)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "success": True,
            "processed_images": len(input_paths),
            "successful_processing": successful,
            "failed_processing": len(input_paths) - successful,
            "results": results
        }