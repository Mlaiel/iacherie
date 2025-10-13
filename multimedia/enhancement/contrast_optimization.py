"""Contrast Optimization Engine
Intelligent contrast and brightness optimization using advanced algorithms.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Optional, Union, Tuple, List
from pathlib import Path
from dataclasses import dataclass
import logging
from PIL import Image, ImageEnhance
import scipy.optimize
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

@dataclass
class ContrastConfig:
    """Configuration for contrast optimization."""
    optimization_method: str = "adaptive"  # adaptive, histogram_eq, clahe, gamma_correction
    target_contrast: float = None  # Auto-determine if None
    preserve_highlights: bool = True
    preserve_shadows: bool = True
    local_adaptation: bool = True
    
    # CLAHE parameters
    clahe_clip_limit: float = 2.0
    clahe_tile_size: Tuple[int, int] = (8, 8)
    
    # Gamma correction
    gamma_auto: bool = True
    gamma_value: float = 1.0
    
    # Advanced settings
    histogram_analysis: bool = True
    edge_preservation: bool = True
    color_preservation: bool = True
    multi_scale_processing: bool = True

class HistogramAnalyzer:
    """Analyze image histograms for contrast optimization."""
    
    @staticmethod
    def analyze_histogram(image: np.ndarray) -> Dict[str, float]:
        """Analyze image histogram characteristics."""
        if len(image.shape) == 3:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / np.sum(hist)  # Normalize
        
        # Calculate statistics
        mean_luminance = np.mean(gray)
        std_luminance = np.std(gray)
        
        # Contrast metrics
        rms_contrast = std_luminance / (mean_luminance + 1e-8)
        
        # Dynamic range
        min_val, max_val = np.min(gray), np.max(gray)
        dynamic_range = max_val - min_val
        
        # Distribution analysis
        shadow_ratio = np.sum(hist[:85]) / np.sum(hist)  # Percentage in shadows
        highlight_ratio = np.sum(hist[170:]) / np.sum(hist)  # Percentage in highlights
        midtone_ratio = np.sum(hist[85:170]) / np.sum(hist)  # Percentage in midtones
        
        # Entropy (measure of information content)
        entropy = -np.sum(hist * np.log2(hist + 1e-8))
        
        # Peak analysis
        peak_indices = np.where(hist > np.mean(hist) + 2 * np.std(hist))[0]
        num_peaks = len(peak_indices)
        
        return {
            "mean_luminance": float(mean_luminance),
            "std_luminance": float(std_luminance),
            "rms_contrast": float(rms_contrast),
            "dynamic_range": float(dynamic_range),
            "shadow_ratio": float(shadow_ratio),
            "highlight_ratio": float(highlight_ratio),
            "midtone_ratio": float(midtone_ratio),
            "entropy": float(entropy),
            "num_peaks": int(num_peaks),
            "under_exposed": shadow_ratio > 0.6,
            "over_exposed": highlight_ratio > 0.3,
            "low_contrast": rms_contrast < 0.3,
            "high_contrast": rms_contrast > 0.8
        }
    
    @staticmethod
    def estimate_optimal_gamma(image: np.ndarray) -> float:
        """Estimate optimal gamma correction value."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate mean luminance
        mean_lum = np.mean(gray) / 255.0
        
        # Estimate gamma to bring mean luminance closer to 0.5
        target_mean = 0.5
        
        if mean_lum > 0.01:  # Avoid division by zero
            estimated_gamma = np.log(target_mean) / np.log(mean_lum)
        else:
            estimated_gamma = 1.0
        
        # Clamp gamma to reasonable range
        estimated_gamma = np.clip(estimated_gamma, 0.3, 3.0)
        
        return estimated_gamma

class AdaptiveContrastEnhancer:
    """Adaptive contrast enhancement based on local and global characteristics."""
    
    def __init__(self, config: ContrastConfig):
        self.config = config
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive contrast enhancement."""
        if len(image.shape) == 3:
            # Process in LAB color space to preserve color
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            
            # Enhance luminance channel
            enhanced_l = self._enhance_luminance_channel(l_channel)
            
            # Merge back
            lab[:, :, 0] = enhanced_l
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            return self._enhance_luminance_channel(image)
    
    def _enhance_luminance_channel(self, channel: np.ndarray) -> np.ndarray:
        """Enhance single luminance channel."""
        # Analyze local and global characteristics
        global_stats = HistogramAnalyzer.analyze_histogram(channel)
        
        # Multi-scale processing if enabled
        if self.config.multi_scale_processing:
            enhanced = self._multi_scale_enhancement(channel, global_stats)
        else:
            enhanced = self._single_scale_enhancement(channel, global_stats)
        
        # Local adaptation if enabled
        if self.config.local_adaptation:
            enhanced = self._apply_local_adaptation(enhanced, channel)
        
        return enhanced
    
    def _multi_scale_enhancement(self, channel: np.ndarray, stats: Dict) -> np.ndarray:
        """Multi-scale contrast enhancement."""
        enhanced = channel.copy().astype(np.float32)
        
        # Different scales for detail enhancement
        scales = [1, 2, 4]
        weights = [0.6, 0.3, 0.1]
        
        for scale, weight in zip(scales, weights):
            # Downsample
            if scale > 1:
                small = cv2.resize(channel, None, fx=1/scale, fy=1/scale, interpolation=cv2.INTER_AREA)
            else:
                small = channel
            
            # Enhance at this scale
            enhanced_small = self._single_scale_enhancement(small, stats)
            
            # Upsample back
            if scale > 1:
                enhanced_scale = cv2.resize(enhanced_small, (channel.shape[1], channel.shape[0]), 
                                          interpolation=cv2.INTER_CUBIC)
            else:
                enhanced_scale = enhanced_small
            
            # Blend with accumulated result
            enhanced = enhanced * (1 - weight) + enhanced_scale.astype(np.float32) * weight
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def _single_scale_enhancement(self, channel: np.ndarray, stats: Dict) -> np.ndarray:
        """Single scale contrast enhancement."""
        enhanced = channel.copy()
        
        # Choose enhancement strategy based on analysis
        if stats["low_contrast"]:
            enhanced = self._enhance_low_contrast(enhanced, stats)
        elif stats["high_contrast"]:
            enhanced = self._reduce_excessive_contrast(enhanced, stats)
        else:
            enhanced = self._balanced_enhancement(enhanced, stats)
        
        # Address exposure issues
        if stats["under_exposed"]:
            enhanced = self._correct_underexposure(enhanced)
        elif stats["over_exposed"]:
            enhanced = self._correct_overexposure(enhanced)
        
        return enhanced
    
    def _enhance_low_contrast(self, channel: np.ndarray, stats: Dict) -> np.ndarray:
        """Enhance low contrast images."""
        # Histogram stretching
        min_val, max_val = np.percentile(channel, [2, 98])  # Robust min/max
        
        if max_val > min_val:
            # Stretch histogram
            stretched = ((channel.astype(np.float32) - min_val) / (max_val - min_val) * 255)
            stretched = np.clip(stretched, 0, 255)
        else:
            stretched = channel.astype(np.float32)
        
        # Apply S-curve for additional contrast
        stretched = self._apply_s_curve(stretched, strength=0.3)
        
        return stretched.astype(np.uint8)
    
    def _reduce_excessive_contrast(self, channel: np.ndarray, stats: Dict) -> np.ndarray:
        """Reduce excessive contrast while preserving details."""
        # Gentle compression of dynamic range
        compressed = np.power(channel.astype(np.float32) / 255.0, 1.2) * 255
        
        # Blend with original to preserve some contrast
        result = channel.astype(np.float32) * 0.7 + compressed * 0.3
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _balanced_enhancement(self, channel: np.ndarray, stats: Dict) -> np.ndarray:
        """Balanced enhancement for normal contrast images."""
        # Gentle S-curve enhancement
        enhanced = self._apply_s_curve(channel.astype(np.float32), strength=0.15)
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def _correct_underexposure(self, channel: np.ndarray) -> np.ndarray:
        """Correct underexposed images."""
        # Gamma correction to lift shadows
        gamma = 0.7  # Lift shadows
        corrected = np.power(channel.astype(np.float32) / 255.0, gamma) * 255
        
        return np.clip(corrected, 0, 255).astype(np.uint8)
    
    def _correct_overexposure(self, channel: np.ndarray) -> np.ndarray:
        """Correct overexposed images."""
        # Gamma correction to compress highlights
        gamma = 1.3  # Compress highlights
        corrected = np.power(channel.astype(np.float32) / 255.0, gamma) * 255
        
        return np.clip(corrected, 0, 255).astype(np.uint8)
    
    def _apply_s_curve(self, image: np.ndarray, strength: float = 0.2) -> np.ndarray:
        """Apply S-curve for contrast enhancement."""
        # Normalize to 0-1
        normalized = image / 255.0
        
        # S-curve function
        s_curve = 0.5 * (1 + np.tanh(strength * (normalized - 0.5) / (1 - np.abs(normalized - 0.5) + 1e-8)))
        
        # Blend with original
        result = normalized * (1 - strength) + s_curve * strength
        
        return result * 255
    
    def _apply_local_adaptation(self, enhanced: np.ndarray, original: np.ndarray) -> np.ndarray:
        """Apply local adaptation to preserve local characteristics."""
        # Calculate local mean and std
        kernel_size = 15
        kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size ** 2)
        
        local_mean = cv2.filter2D(original.astype(np.float32), -1, kernel)
        local_std = cv2.filter2D((original.astype(np.float32) - local_mean) ** 2, -1, kernel)
        local_std = np.sqrt(local_std)
        
        # Adaptation weight based on local contrast
        adaptation_weight = local_std / (local_std + 20)  # Areas with low local contrast get more enhancement
        
        # Apply local adaptation
        result = enhanced.astype(np.float32) * adaptation_weight + original.astype(np.float32) * (1 - adaptation_weight)
        
        return np.clip(result, 0, 255).astype(np.uint8)

class ContrastOptimizationEngine:
    """Enterprise contrast optimization engine with multiple algorithms."""
    
    def __init__(self):
        self.config = ContrastConfig()
        
    async def optimize_contrast(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        contrast_level: float = 0.5,
        config: Optional[ContrastConfig] = None
    ) -> Dict[str, any]:
        """Optimize image/video contrast using advanced algorithms."""
        try:
            if config:
                self.config = config
            
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Detect file type
            file_ext = input_path.suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                result = await self._optimize_image_contrast(input_path, output_path, contrast_level)
            elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                result = await self._optimize_video_contrast(input_path, output_path, contrast_level)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return {
                "success": True,
                "contrast_improvement": contrast_level,
                "optimization_method": self.config.optimization_method,
                "output_path": str(output_path),
                **result
            }
            
        except Exception as e:
            logger.error(f"Contrast optimization failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _optimize_image_contrast(
        self, 
        input_path: Path, 
        output_path: Path, 
        contrast_level: float
    ) -> Dict[str, any]:
        """Optimize contrast of image file."""
        # Load image
        image = cv2.imread(str(input_path))
        if image is None:
            raise ValueError("Could not load image")
        
        original_image = image.copy()
        
        # Analyze original image
        original_analysis = HistogramAnalyzer.analyze_histogram(image)
        
        # Apply contrast optimization based on method
        optimized_image = await self._apply_contrast_optimization(image, contrast_level, original_analysis)
        
        # Save optimized image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), optimized_image)
        
        # Analyze optimized image
        optimized_analysis = HistogramAnalyzer.analyze_histogram(optimized_image)
        
        # Calculate improvement metrics
        improvement_metrics = await self._calculate_improvement_metrics(
            original_analysis, optimized_analysis, original_image, optimized_image
        )
        
        return {
            "image_processing": True,
            "image_dimensions": image.shape,
            "original_analysis": original_analysis,
            "optimized_analysis": optimized_analysis,
            "improvement_metrics": improvement_metrics,
            "processing_details": {
                "method_used": self.config.optimization_method,
                "local_adaptation": self.config.local_adaptation,
                "multi_scale": self.config.multi_scale_processing,
                "edge_preservation": self.config.edge_preservation
            }
        }
    
    async def _apply_contrast_optimization(
        self, 
        image: np.ndarray, 
        contrast_level: float, 
        analysis: Dict
    ) -> np.ndarray:
        """Apply contrast optimization based on selected method."""
        
        if self.config.optimization_method == "adaptive":
            enhancer = AdaptiveContrastEnhancer(self.config)
            optimized = enhancer.enhance_contrast(image)
            
        elif self.config.optimization_method == "histogram_eq":
            optimized = await self._apply_histogram_equalization(image)
            
        elif self.config.optimization_method == "clahe":
            optimized = await self._apply_clahe(image)
            
        elif self.config.optimization_method == "gamma_correction":
            optimized = await self._apply_gamma_correction(image, analysis)
            
        else:
            # Default to adaptive
            enhancer = AdaptiveContrastEnhancer(self.config)
            optimized = enhancer.enhance_contrast(image)
        
        # Blend with original based on contrast_level
        if contrast_level < 1.0:
            optimized = (
                image.astype(np.float32) * (1 - contrast_level) + 
                optimized.astype(np.float32) * contrast_level
            ).astype(np.uint8)
        
        return optimized
    
    async def _apply_histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """Apply histogram equalization."""
        if len(image.shape) == 3:
            # Apply to luminance channel in YUV color space
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            return cv2.equalizeHist(image)
    
    async def _apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """Apply Contrast Limited Adaptive Histogram Equalization."""
        clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit,
            tileGridSize=self.config.clahe_tile_size
        )
        
        if len(image.shape) == 3:
            # Apply to luminance channel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            return clahe.apply(image)
    
    async def _apply_gamma_correction(self, image: np.ndarray, analysis: Dict) -> np.ndarray:
        """Apply gamma correction."""
        if self.config.gamma_auto:
            # Auto-estimate gamma
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            gamma = HistogramAnalyzer.estimate_optimal_gamma(gray)
        else:
            gamma = self.config.gamma_value
        
        # Build lookup table
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        
        # Apply lookup table
        return cv2.LUT(image, table)
    
    async def _optimize_video_contrast(
        self, 
        input_path: Path, 
        output_path: Path, 
        contrast_level: float
    ) -> Dict[str, any]:
        """Optimize contrast of video file."""
        import subprocess
        
        # Create FFmpeg filter based on optimization method
        filter_string = await self._create_ffmpeg_contrast_filter(contrast_level)
        
        ffmpeg_cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', filter_string,
            '-c:a', 'copy',  # Copy audio
            '-y', str(output_path)
        ]
        
        try:
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "video_processing": True,
                    "contrast_filter": filter_string,
                    "audio_preserved": True
                }
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"FFmpeg video contrast optimization failed, using fallback: {e}")
            
            # Fallback: copy file
            import shutil
            shutil.copy2(input_path, output_path)
            
            return {
                "video_processing": False,
                "fallback_used": True,
                "note": "Advanced video contrast optimization requires FFmpeg"
            }
    
    async def _create_ffmpeg_contrast_filter(self, contrast_level: float) -> str:
        """Create FFmpeg contrast filter string."""
        filters = []
        
        if self.config.optimization_method == "histogram_eq":
            filters.append("histeq=strength=0.8")
        elif self.config.optimization_method == "clahe":
            filters.append(f"histeq=strength={contrast_level}")
        elif self.config.optimization_method == "gamma_correction":
            filters.append(f"eq=gamma={1.0 + contrast_level * 0.5}")
        else:  # adaptive or default
            # Use combination of filters for adaptive enhancement
            contrast_value = 1.0 + contrast_level * 0.3
            filters.append(f"eq=contrast={contrast_value}")
            filters.append("histeq=strength=0.2")
        
        return ",".join(filters)
    
    async def _calculate_improvement_metrics(
        self,
        original_analysis: Dict,
        optimized_analysis: Dict,
        original_image: np.ndarray,
        optimized_image: np.ndarray
    ) -> Dict[str, float]:
        """Calculate contrast improvement metrics."""
        # Contrast improvement
        contrast_improvement = (
            optimized_analysis["rms_contrast"] - original_analysis["rms_contrast"]
        )
        
        # Dynamic range improvement
        dr_improvement = (
            optimized_analysis["dynamic_range"] - original_analysis["dynamic_range"]
        )
        
        # Entropy improvement (information content)
        entropy_improvement = (
            optimized_analysis["entropy"] - original_analysis["entropy"]
        )
        
        # Calculate PSNR and SSIM for quality assessment
        psnr = cv2.PSNR(original_image, optimized_image)
        ssim = self._calculate_ssim(original_image, optimized_image)
        
        return {
            "contrast_improvement": float(contrast_improvement),
            "dynamic_range_improvement": float(dr_improvement),
            "entropy_improvement": float(entropy_improvement),
            "psnr": float(psnr),
            "ssim": float(ssim),
            "overall_improvement": float((contrast_improvement + dr_improvement + entropy_improvement) / 3)
        }
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index."""
        # Convert to grayscale if needed
        if len(img1.shape) == 3:
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        else:
            gray1, gray2 = img1, img2
        
        # SSIM calculation (simplified)
        mu1 = cv2.GaussianBlur(gray1.astype(float), (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(gray2.astype(float), (11, 11), 1.5)
        
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.GaussianBlur(gray1.astype(float) * gray1.astype(float), (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(gray2.astype(float) * gray2.astype(float), (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(gray1.astype(float) * gray2.astype(float), (11, 11), 1.5) - mu1_mu2
        
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        
        ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / ((mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2))
        
        return float(np.mean(ssim_map))
    
    async def batch_optimize_contrast(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        contrast_level: float = 0.5,
        config: Optional[ContrastConfig] = None
    ) -> Dict[str, any]:
        """Apply contrast optimization to multiple files."""
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
                
                result = await self.optimize_contrast(
                    file_path, output_path, contrast_level, config
                )
                
                results.append({
                    "input": str(file_path),
                    "output": str(output_path),
                    "result": result
                })
        
        successful = sum(1 for r in results if r["result"]["success"])
        
        if successful > 0:
            avg_improvement = np.mean([
                r["result"].get("improvement_metrics", {}).get("overall_improvement", 0)
                for r in results if r["result"]["success"]
            ])
        else:
            avg_improvement = 0
        
        return {
            "success": True,
            "total_processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "average_improvement": float(avg_improvement),
            "results": results
        }
    
    def get_optimal_settings(self, image_characteristics: str) -> ContrastConfig:
        """Get optimal contrast settings based on image characteristics."""
        config = ContrastConfig()
        
        if image_characteristics == "low_contrast":
            config.optimization_method = "adaptive"
            config.multi_scale_processing = True
            config.local_adaptation = True
            
        elif image_characteristics == "high_contrast":
            config.optimization_method = "clahe"
            config.clahe_clip_limit = 1.5
            config.preserve_highlights = True
            config.preserve_shadows = True
            
        elif image_characteristics == "underexposed":
            config.optimization_method = "gamma_correction"
            config.gamma_auto = True
            config.preserve_highlights = False
            
        elif image_characteristics == "overexposed":
            config.optimization_method = "adaptive"
            config.preserve_shadows = False
            config.local_adaptation = True
            
        return config