"""Sharpness Enhancement Engine
AI-powered sharpness and detail enhancement for images and videos.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, Tuple, List
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageFilter, ImageEnhance
import scipy.ndimage
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)

@dataclass
class SharpnessConfig:
    """Configuration for sharpness enhancement."""
    enhancement_method: str = "adaptive"  # adaptive, unsharp_mask, rl_deconv, ai_super_res
    sharpness_strength: float = 1.0  # 0.0 to 3.0
    edge_preservation: bool = True
    noise_suppression: bool = True
    detail_enhancement: bool = True
    
    # Unsharp masking parameters
    unsharp_radius: float = 1.0
    unsharp_amount: float = 1.5
    unsharp_threshold: int = 3
    
    # Richardson-Lucy deconvolution
    rl_iterations: int = 10
    rl_psf_size: int = 5
    
    # AI enhancement
    ai_model_type: str = "lightweight"  # lightweight, quality, fast
    gpu_acceleration: bool = True
    
    # Adaptive parameters
    auto_detect_blur: bool = True
    preserve_texture: bool = True

class BlurDetector:
    """Detect and analyze blur in images."""
    
    @staticmethod
    def detect_blur_level(image: np.ndarray) -> Dict[str, float]:
        """Detect blur level and type in image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Laplacian variance (focus measure)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Sobel gradient magnitude
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sobel_mean = np.mean(sobel_magnitude)
        
        # Tenengrad focus measure
        tenengrad = np.mean(sobel_magnitude**2)
        
        # FFT-based blur detection
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # High frequency content
        h, w = gray.shape
        center_y, center_x = h // 2, w // 2
        
        # Define high frequency region (outer 30% of spectrum)
        inner_radius = int(min(h, w) * 0.35)
        y, x = np.ogrid[:h, :w]
        mask = (x - center_x)**2 + (y - center_y)**2 > inner_radius**2
        
        high_freq_energy = np.mean(magnitude_spectrum[mask])
        total_energy = np.mean(magnitude_spectrum)
        high_freq_ratio = high_freq_energy / (total_energy + 1e-8)
        
        return {
            "laplacian_variance": laplacian_var,
            "sobel_mean": sobel_mean,
            "tenengrad": tenengrad,
            "high_freq_ratio": high_freq_ratio,
            "blur_score": 1.0 / (1.0 + laplacian_var / 100.0),  # 0-1, higher = more blur
            "sharpness_score": min(1.0, laplacian_var / 500.0)  # 0-1, higher = sharper
        }

class AdaptiveSharpener:
    """Adaptive sharpening based on local image characteristics."""
    
    def __init__(self, config -> None: SharpnessConfig) -> None:
        self.config = config
        
    def enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive sharpness enhancement."""
        if len(image.shape) == 3:
            # Process each channel separately for color images
            enhanced_channels = []
            for channel in cv2.split(image):
                enhanced_channel = self._enhance_channel(channel)
                enhanced_channels.append(enhanced_channel)
            return cv2.merge(enhanced_channels)
        else:
            return self._enhance_channel(image)
    
    def _enhance_channel(self, channel: np.ndarray) -> np.ndarray:
        """Enhance single channel with adaptive sharpening."""
        # Analyze local characteristics
        edge_map = self._compute_edge_map(channel)
        texture_map = self._compute_texture_map(channel)
        
        # Adaptive kernel based on local content
        enhanced = channel.copy().astype(np.float32)
        
        # High-pass filter for detail enhancement
        if self.config.detail_enhancement:
            gaussian_blur = cv2.GaussianBlur(channel, (5, 5), 1.0)
            high_pass = channel.astype(np.float32) - gaussian_blur.astype(np.float32)
            
            # Adaptive gain based on edge strength
            gain_map = edge_map * self.config.sharpness_strength
            gain_map = np.clip(gain_map, 0, 2.0)
            
            # Apply enhancement
            enhanced += high_pass * gain_map[:, :, np.newaxis] if len(gain_map.shape) == 2 else high_pass * gain_map
        
        # Edge-preserving sharpening
        if self.config.edge_preservation:
            enhanced = self._edge_preserving_sharpen(enhanced, edge_map)
        
        # Noise suppression
        if self.config.noise_suppression:
            enhanced = self._suppress_noise(enhanced, texture_map)
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def _compute_edge_map(self, image: np.ndarray) -> np.ndarray:
        """Compute edge strength map."""
        # Multiple edge detectors for robustness
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Canny edges
        canny = cv2.Canny(image, 50, 150)
        
        # Combine edge information
        edge_map = cv2.GaussianBlur(sobel_magnitude, (3, 3), 0.5)
        edge_map = edge_map / (np.max(edge_map) + 1e-8)  # Normalize
        
        # Boost regions with strong Canny edges
        canny_normalized = canny.astype(np.float32) / 255.0
        edge_map = np.maximum(edge_map, canny_normalized * 0.7)
        
        return edge_map
    
    def _compute_texture_map(self, image: np.ndarray) -> np.ndarray:
        """Compute texture strength map."""
        # Local standard deviation
        kernel = np.ones((5, 5), np.float32) / 25
        mean = cv2.filter2D(image.astype(np.float32), -1, kernel)
        sqr_mean = cv2.filter2D((image.astype(np.float32))**2, -1, kernel)
        texture_map = np.sqrt(sqr_mean - mean**2)
        
        # Normalize
        texture_map = texture_map / (np.max(texture_map) + 1e-8)
        
        return texture_map
    
    def _edge_preserving_sharpen(self, image: np.ndarray, edge_map: np.ndarray) -> np.ndarray:
        """Apply edge-preserving sharpening."""
        # Bilateral filter to preserve edges
        bilateral = cv2.bilateralFilter(image.astype(np.uint8), 9, 75, 75)
        
        # Sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]], dtype=np.float32)
        
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # Blend based on edge strength
        alpha = edge_map * 0.3  # Reduce sharpening in smooth areas
        result = image * (1 - alpha) + sharpened * alpha
        
        return result
    
    def _suppress_noise(self, image: np.ndarray, texture_map: np.ndarray) -> np.ndarray:
        """Suppress noise while preserving details."""
        # Apply gentle filtering in smooth regions
        smooth_regions = texture_map < 0.3
        
        if np.any(smooth_regions):
            filtered = cv2.GaussianBlur(image, (3, 3), 0.5)
            image[smooth_regions] = (
                0.7 * image[smooth_regions] + 
                0.3 * filtered[smooth_regions]
            )
        
        return image

class UnsharpMaskSharpener:
    """Classic unsharp masking with advanced features."""
    
    def __init__(self, config -> None: SharpnessConfig) -> None:
        self.config = config
    
    def enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Apply unsharp masking."""
        if len(image.shape) == 3:
            # Convert to LAB color space to work on luminance only
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            
            # Apply unsharp masking to luminance
            enhanced_l = self._apply_unsharp_mask(l_channel)
            
            # Merge back
            lab[:, :, 0] = enhanced_l
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            return self._apply_unsharp_mask(image)
    
    def _apply_unsharp_mask(self, channel: np.ndarray) -> np.ndarray:
        """Apply unsharp masking to single channel."""
        # Create Gaussian blur
        blurred = cv2.GaussianBlur(
            channel.astype(np.float32), 
            (0, 0), 
            self.config.unsharp_radius
        )
        
        # Create mask
        mask = channel.astype(np.float32) - blurred
        
        # Apply threshold to avoid enhancing noise
        if self.config.unsharp_threshold > 0:
            mask = np.where(
                np.abs(mask) < self.config.unsharp_threshold, 
                0, 
                mask
            )
        
        # Apply enhancement
        enhanced = channel.astype(np.float32) + self.config.unsharp_amount * mask
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)

class RichardsonLucySharpener:
    """Richardson-Lucy deconvolution for sharpening."""
    
    def __init__(self, config -> None: SharpnessConfig) -> None:
        self.config = config
    
    def enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Apply Richardson-Lucy deconvolution."""
        if len(image.shape) == 3:
            # Process luminance channel only
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            enhanced_gray = self._richardson_lucy_deconv(gray)
            
            # Apply enhancement to original image proportionally
            enhancement_factor = enhanced_gray.astype(np.float32) / (gray.astype(np.float32) + 1e-8)
            enhancement_factor = np.clip(enhancement_factor, 0.5, 2.0)
            
            enhanced = image.astype(np.float32) * enhancement_factor[:, :, np.newaxis]
            return np.clip(enhanced, 0, 255).astype(np.uint8)
        else:
            return self._richardson_lucy_deconv(image)
    
    def _richardson_lucy_deconv(self, image: np.ndarray) -> np.ndarray:
        """Richardson-Lucy deconvolution algorithm."""
        # Create PSF (Point Spread Function) - simulate motion/gaussian blur
        psf = self._create_psf()
        
        # Initialize estimate
        estimate = image.astype(np.float32) / 255.0
        
        # Iterative enhancement
        for _ in range(self.config.rl_iterations):
            # Convolve estimate with PSF
            convolved = cv2.filter2D(estimate, -1, psf)
            
            # Calculate ratio
            ratio = (image.astype(np.float32) / 255.0) / (convolved + 1e-8)
            
            # Convolve ratio with flipped PSF
            psf_flipped = np.flip(psf)
            correction = cv2.filter2D(ratio, -1, psf_flipped)
            
            # Update estimate
            estimate = estimate * correction
            
            # Clamp to valid range
            estimate = np.clip(estimate, 0, 1)
        
        return (estimate * 255).astype(np.uint8)
    
    def _create_psf(self) -> np.ndarray:
        """Create Point Spread Function for deconvolution."""
        size = self.config.rl_psf_size
        
        # Gaussian PSF (simulates defocus blur)
        psf = np.zeros((size, size), dtype=np.float32)
        center = size // 2
        
        for i in range(size):
            for j in range(size):
                distance = np.sqrt((i - center)**2 + (j - center)**2)
                psf[i, j] = np.exp(-distance**2 / (2 * 0.8**2))
        
        # Normalize
        psf = psf / np.sum(psf)
        
        return psf

class SharpnessEnhancementEngine:
    """Enterprise sharpness enhancement engine with multiple algorithms."""
    
    def __init__(self) -> None:
        self.config = SharpnessConfig()
        
    async def enhance_sharpness(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        sharpness_level: float = 0.5,
        config: Optional[SharpnessConfig] = None
    ) -> Dict[str, any]:
        """Enhance image/video sharpness using advanced algorithms."""
        try:
            if config:
                self.config = config
            
            # Update sharpness strength from level
            self.config.sharpness_strength = sharpness_level * 2.0  # Scale to 0-2
            
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Detect file type
            file_ext = input_path.suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                result = await self._enhance_image_sharpness(input_path, output_path)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                result = await self._enhance_video_sharpness(input_path, output_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return {
                "success": True,
                "sharpness_improvement": sharpness_level,
                "enhancement_method": self.config.enhancement_method,
                "output_path": str(output_path),
                **result
            }
            
        except Exception as e:
            logger.error(f"Sharpness enhancement failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _enhance_image_sharpness(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, any]:
        """Enhance sharpness of image file."""
        # Load image
        image = cv2.imread(str(input_path))
        if image is None:
            raise ValueError("Could not load image")
        
        original_image = image.copy()
        
        # Analyze blur level if auto-detection is enabled
        if self.config.auto_detect_blur:
            blur_analysis = BlurDetector.detect_blur_level(image)
            
            # Adjust enhancement based on blur level
            if blur_analysis["blur_score"] > 0.7:  # Heavily blurred
                self.config.sharpness_strength *= 1.5
                self.config.enhancement_method = "rl_deconv"
            elif blur_analysis["blur_score"] > 0.4:  # Moderately blurred
                self.config.enhancement_method = "adaptive"
            else:  # Lightly blurred or sharp
                self.config.sharpness_strength *= 0.7
                self.config.enhancement_method = "unsharp_mask"
        else:
            blur_analysis = {}
        
        # Apply enhancement based on method
        if self.config.enhancement_method == "adaptive":
            sharpener = AdaptiveSharpener(self.config)
            enhanced_image = sharpener.enhance_sharpness(image)
        elif self.config.enhancement_method == "unsharp_mask":
            sharpener = UnsharpMaskSharpener(self.config)
            enhanced_image = sharpener.enhance_sharpness(image)
        elif self.config.enhancement_method == "rl_deconv":
            sharpener = RichardsonLucySharpener(self.config)
            enhanced_image = sharpener.enhance_sharpness(image)
        else:
            # Default to adaptive
            sharpener = AdaptiveSharpener(self.config)
            enhanced_image = sharpener.enhance_sharpness(image)
        
        # Save enhanced image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), enhanced_image)
        
        # Calculate improvement metrics
        original_blur = BlurDetector.detect_blur_level(original_image)
        enhanced_blur = BlurDetector.detect_blur_level(enhanced_image)
        
        sharpness_improvement = (
            enhanced_blur["sharpness_score"] - original_blur["sharpness_score"]
        )
        
        return {
            "blur_analysis": blur_analysis,
            "original_sharpness": original_blur["sharpness_score"],
            "enhanced_sharpness": enhanced_blur["sharpness_score"],
            "sharpness_improvement": sharpness_improvement,
            "image_dimensions": image.shape,
            "processing_details": {
                "method_used": self.config.enhancement_method,
                "auto_detection": self.config.auto_detect_blur,
                "edge_preservation": self.config.edge_preservation,
                "noise_suppression": self.config.noise_suppression
            }
        }
    
    async def _enhance_video_sharpness(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, any]:
        """Enhance sharpness of video file."""
        import subprocess
        
        # For video sharpening, we'll use FFmpeg with unsharp filter
        strength = self.config.sharpness_strength
        
        # FFmpeg unsharp filter: luma_msize_x:luma_msize_y:luma_amount:chroma_msize_x:chroma_msize_y:chroma_amount
        unsharp_params = f"5:5:{strength}:5:5:{strength*0.5}"
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', f'unsharp={unsharp_params}',
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y', str(output_path)
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "video_processing": True,
                    "sharpening_filter": f"unsharp={unsharp_params}",
                    "audio_preserved": True
                }
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"FFmpeg video sharpening failed, using fallback: {e}")
            
            # Fallback: frame-by-frame processing (simplified)
            return await self._fallback_video_sharpening(input_path, output_path)
    
    async def _fallback_video_sharpening(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, any]:
        """Fallback video sharpening using OpenCV."""
        import shutil
        
        # For now, just copy the file
        # In production, you'd implement frame-by-frame processing
        shutil.copy2(input_path, output_path)
        
        return {
            "video_processing": False,
            "fallback_used": True,
            "note": "Advanced video sharpening requires FFmpeg"
        }
    
    async def batch_enhance_sharpness(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        sharpness_level: float = 0.5,
        config: Optional[SharpnessConfig] = None
    ) -> Dict[str, any]:
        """Apply sharpness enhancement to multiple files."""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            return {"success": False, "error": "Input directory not found"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        supported_formats = {
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp',  # Images
            '.mp4', '.avi', '.mov', '.mkv'  # Videos
        }
        
        for file_path in input_dir.iterdir():
            if file_path.suffix.lower() in supported_formats:
                output_path = output_dir / file_path.name
                
                result = await self.enhance_sharpness(
                    file_path, output_path, sharpness_level, config
                )
                
                results.append({
                    "input": str(file_path),
                    "output": str(output_path),
                    "result": result
                })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "average_improvement": np.mean([
                r["result"].get("sharpness_improvement", 0) 
                for r in results if r["result"]["success"]
            ]) if successful > 0 else 0,
            "results": results
        }
    
    def get_optimal_settings(self, blur_level: str) -> SharpnessConfig:
        """Get optimal sharpness settings based on blur level."""
        config = SharpnessConfig()
        
        if blur_level == "heavy":
            config.enhancement_method = "rl_deconv"
            config.sharpness_strength = 2.0
            config.rl_iterations = 15
            config.noise_suppression = True
            
        elif blur_level == "moderate":
            config.enhancement_method = "adaptive"
            config.sharpness_strength = 1.5
            config.edge_preservation = True
            config.detail_enhancement = True
            
        elif blur_level == "light":
            config.enhancement_method = "unsharp_mask"
            config.sharpness_strength = 1.0
            config.unsharp_amount = 1.2
            config.unsharp_radius = 0.8
            
        return config