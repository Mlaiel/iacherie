# Core Computer Vision Processing Engine
# Advanced Industrial-Grade Visual Intelligence System
#
# Created by: Fahed Mlaiel (mlaiel@live.de)
# 
# ⚠️  STRICT COPYRIGHT WARNING ⚠️ 
# This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
# ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
# without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
# STRICTLY PROHIBITED and will result in immediate legal action.
# All rights reserved. Patent pending.

import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import hashlib
import base64
import io
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualMetadata:
    """Comprehensive visual content metadata structure"""
    file_path: str
    file_size: int
    dimensions: Tuple[int, int]
    format: str
    color_space: str
    bit_depth: int
    compression: Optional[str]
    creation_date: datetime
    modification_date: datetime
    camera_info: Optional[Dict[str, Any]] = None
    gps_data: Optional[Dict[str, float]] = None
    creator_info: Optional[Dict[str, str]] = None
    processing_history: List[str] = field(default_factory=list)
    content_hash: Optional[str] = None
    quality_score: Optional[float] = None

@dataclass
class VisualFeatures:
    """Advanced visual features extracted from content"""
    histogram: np.ndarray
    color_moments: Dict[str, float]
    texture_features: Dict[str, float]
    edge_density: float
    brightness_stats: Dict[str, float]
    contrast_ratio: float
    saturation_levels: Dict[str, float]
    dominant_colors: List[Tuple[int, int, int]]
    complexity_score: float
    aesthetic_score: float
    technical_quality: Dict[str, float]
    content_tags: List[str] = field(default_factory=list)

@dataclass
class ProcessingResult:
    """Result structure for vision processing operations"""
    success: bool
    message: str
    processed_content: Optional[np.ndarray] = None
    metadata: Optional[VisualMetadata] = None
    features: Optional[VisualFeatures] = None
    processing_time: Optional[float] = None
    quality_improvement: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class AnalysisMetrics:
    """Comprehensive analysis metrics for performance tracking"""
    processing_time: float
    memory_usage: float
    cpu_usage: float
    accuracy_scores: Dict[str, float]
    confidence_levels: Dict[str, float]
    error_rates: Dict[str, float]
    throughput: float
    latency: float

class VisionProcessor:
    """
    Advanced computer vision processing engine for the IA Influencer Agent platform.
    
    Provides enterprise-grade visual content analysis, processing, and enhancement
    capabilities for content creators across multiple formats and platforms.
    """
    
    def __init__(self, 
                 gpu_enabled: bool = True,
                 batch_size: int = 32,
                 cache_size: int = 1000,
                 quality_threshold: float = 0.8):
        """
        Initialize the VisionProcessor with advanced configuration.
        
        Args:
            gpu_enabled: Enable GPU acceleration for processing
            batch_size: Batch size for ML model inference
            cache_size: Size of the processing cache
            quality_threshold: Minimum quality threshold for content
        """
        self.gpu_enabled = gpu_enabled and torch.cuda.is_available()
        self.device = torch.device("cuda" if self.gpu_enabled else "cpu")
        self.batch_size = batch_size
        self.cache_size = cache_size
        self.quality_threshold = quality_threshold
        
        # Initialize processing cache
        self._cache = {}
        self._cache_order = []
        
        # Initialize transformation pipelines
        self._init_transforms()
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"VisionProcessor initialized - Device: {self.device}, GPU: {self.gpu_enabled}")
    
    def _init_transforms(self):
        """Initialize image transformation pipelines"""
        self.standard_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.high_res_transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], 
                               std=[0.5, 0.5, 0.5])
        ])
    
    def process_image(self, 
                     image_input: Union[str, np.ndarray, Image.Image],
                     enhancement_level: str = "standard",
                     extract_features: bool = True,
                     generate_metadata: bool = True) -> ProcessingResult:
        """
        Process a single image with comprehensive analysis and enhancement.
        
        Args:
            image_input: Image file path, numpy array, or PIL Image
            enhancement_level: Level of enhancement ("basic", "standard", "professional")
            extract_features: Whether to extract visual features
            generate_metadata: Whether to generate comprehensive metadata
            
        Returns:
            ProcessingResult: Comprehensive processing results
        """
        start_time = datetime.now()
        
        try:
            # Load and validate image
            image = self._load_image(image_input)
            if image is None:
                return ProcessingResult(
                    success=False,
                    message="Failed to load image",
                    errors=["Invalid image input or file not found"]
                )
            
            # Generate content hash for caching
            content_hash = self._generate_content_hash(image)
            
            # Check cache first
            if content_hash in self._cache:
                cached_result = self._cache[content_hash]
                cached_result.message = "Retrieved from cache"
                return cached_result
            
            # Process image
            processed_image = self._enhance_image(image, enhancement_level)
            
            # Extract features if requested
            features = None
            if extract_features:
                features = self._extract_visual_features(processed_image)
            
            # Generate metadata if requested
            metadata = None
            if generate_metadata:
                metadata = self._generate_metadata(image_input, processed_image, content_hash)
            
            # Calculate processing metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            quality_improvement = self._calculate_quality_improvement(image, processed_image)
            
            # Create result
            result = ProcessingResult(
                success=True,
                message="Image processed successfully",
                processed_content=processed_image,
                metadata=metadata,
                features=features,
                processing_time=processing_time,
                quality_improvement=quality_improvement
            )
            
            # Cache result
            self._update_cache(content_hash, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return ProcessingResult(
                success=False,
                message=f"Processing failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def process_batch(self, 
                           image_inputs: List[Union[str, np.ndarray, Image.Image]],
                           enhancement_level: str = "standard",
                           extract_features: bool = True,
                           generate_metadata: bool = True) -> List[ProcessingResult]:
        """
        Process multiple images asynchronously in batches.
        
        Args:
            image_inputs: List of image inputs
            enhancement_level: Level of enhancement
            extract_features: Whether to extract visual features
            generate_metadata: Whether to generate metadata
            
        Returns:
            List[ProcessingResult]: Results for each processed image
        """
        results = []
        
        # Process in batches
        for i in range(0, len(image_inputs), self.batch_size):
            batch = image_inputs[i:i + self.batch_size]
            
            # Create async tasks for batch processing
            tasks = []
            for image_input in batch:
                task = asyncio.create_task(
                    self._process_image_async(image_input, enhancement_level, 
                                            extract_features, generate_metadata)
                )
                tasks.append(task)
            
            # Wait for batch completion
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        
        return results
    
    async def _process_image_async(self, 
                                  image_input: Union[str, np.ndarray, Image.Image],
                                  enhancement_level: str,
                                  extract_features: bool,
                                  generate_metadata: bool) -> ProcessingResult:
        """Async wrapper for image processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.process_image,
            image_input,
            enhancement_level,
            extract_features,
            generate_metadata
        )
    
    def _load_image(self, image_input: Union[str, np.ndarray, Image.Image]) -> Optional[np.ndarray]:
        """Load image from various input formats"""
        try:
            if isinstance(image_input, str):
                # Load from file path
                if Path(image_input).exists():
                    image = cv2.imread(image_input)
                    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    # Try base64 decode
                    try:
                        image_data = base64.b64decode(image_input)
                        image = Image.open(io.BytesIO(image_data))
                        return np.array(image)
                    except:
                        return None
            
            elif isinstance(image_input, np.ndarray):
                return image_input
            
            elif isinstance(image_input, Image.Image):
                return np.array(image_input)
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    def _enhance_image(self, image: np.ndarray, enhancement_level: str) -> np.ndarray:
        """Apply image enhancement based on specified level"""
        enhanced = image.copy()
        
        if enhancement_level == "basic":
            # Basic enhancement: brightness and contrast
            enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=20)
        
        elif enhancement_level == "standard":
            # Standard enhancement: comprehensive processing
            # Noise reduction
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # Contrast enhancement
            lab = cv2.cvtColor(enhanced, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            # Sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        elif enhancement_level == "professional":
            # Professional enhancement: advanced processing
            # Advanced noise reduction
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
            
            # Multi-scale contrast enhancement
            enhanced = self._apply_multiscale_retinex(enhanced)
            
            # Color balance
            enhanced = self._apply_color_balance(enhanced)
            
            # Detail enhancement
            enhanced = self._apply_unsharp_mask(enhanced)
        
        return np.clip(enhanced, 0, 255).astype(np.uint8)
    
    def _apply_multiscale_retinex(self, image: np.ndarray) -> np.ndarray:
        """Apply multi-scale retinex for dynamic range compression"""
        image_float = image.astype(np.float64) + 1.0
        
        retinex = np.zeros_like(image_float)
        scales = [15, 80, 250]
        
        for scale in scales:
            gaussian = cv2.GaussianBlur(image_float, (0, 0), scale)
            retinex += np.log10(image_float) - np.log10(gaussian)
        
        retinex = retinex / len(scales)
        retinex = np.expm1(retinex)
        
        # Normalize to 0-255
        retinex = cv2.normalize(retinex, None, 0, 255, cv2.NORM_MINMAX)
        
        return retinex.astype(np.uint8)
    
    def _apply_color_balance(self, image: np.ndarray) -> np.ndarray:
        """Apply automatic color balance"""
        result = image.copy()
        
        for i in range(3):  # RGB channels
            hist = cv2.calcHist([result], [i], None, [256], [0, 256])
            
            # Find the 1st and 99th percentiles
            total_pixels = hist.sum()
            current_sum = 0
            low_val = high_val = 0
            
            for j in range(256):
                current_sum += hist[j]
                if current_sum > total_pixels * 0.01 and low_val == 0:
                    low_val = j
                if current_sum > total_pixels * 0.99 and high_val == 0:
                    high_val = j
                    break
            
            # Apply linear stretch
            if high_val > low_val:
                result[:, :, i] = cv2.normalize(result[:, :, i], None, 0, 255, cv2.NORM_MINMAX)
        
        return result
    
    def _apply_unsharp_mask(self, image: np.ndarray, radius: float = 2.0, 
                           amount: float = 1.5) -> np.ndarray:
        """Apply unsharp mask for detail enhancement"""
        blurred = cv2.GaussianBlur(image, (0, 0), radius)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return sharpened
    
    def _extract_visual_features(self, image: np.ndarray) -> VisualFeatures:
        """Extract comprehensive visual features from image"""
        
        # Color histogram
        hist_r = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([image], [2], None, [256], [0, 256])
        histogram = np.concatenate([hist_r.flatten(), hist_g.flatten(), hist_b.flatten()])
        
        # Color moments
        color_moments = {}
        for i, channel in enumerate(['r', 'g', 'b']):
            channel_data = image[:, :, i].flatten()
            color_moments[f'{channel}_mean'] = np.mean(channel_data)
            color_moments[f'{channel}_std'] = np.std(channel_data)
            color_moments[f'{channel}_skew'] = self._calculate_skewness(channel_data)
        
        # Texture features using Gray-Level Co-occurrence Matrix
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        texture_features = self._calculate_glcm_features(gray)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Brightness statistics
        brightness_stats = {
            'mean': np.mean(gray),
            'std': np.std(gray),
            'min': np.min(gray),
            'max': np.max(gray)
        }
        
        # Contrast ratio
        contrast_ratio = np.std(gray) / (np.mean(gray) + 1e-8)
        
        # Saturation levels
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation_levels = {
            'mean': np.mean(hsv[:, :, 1]),
            'std': np.std(hsv[:, :, 1]),
            'high_sat_ratio': np.sum(hsv[:, :, 1] > 200) / hsv[:, :, 1].size
        }
        
        # Dominant colors using K-means
        dominant_colors = self._extract_dominant_colors(image, k=5)
        
        # Complexity score based on edge density and color diversity
        color_diversity = len(np.unique(image.reshape(-1, 3), axis=0))
        complexity_score = edge_density * 0.6 + (color_diversity / (image.shape[0] * image.shape[1])) * 0.4
        
        # Aesthetic score using rule of thirds and symmetry
        aesthetic_score = self._calculate_aesthetic_score(image)
        
        # Technical quality metrics
        technical_quality = {
            'sharpness': self._calculate_sharpness(gray),
            'noise_level': self._estimate_noise_level(gray),
            'exposure_quality': self._assess_exposure_quality(gray),
            'color_accuracy': self._assess_color_accuracy(image)
        }
        
        return VisualFeatures(
            histogram=histogram,
            color_moments=color_moments,
            texture_features=texture_features,
            edge_density=edge_density,
            brightness_stats=brightness_stats,
            contrast_ratio=contrast_ratio,
            saturation_levels=saturation_levels,
            dominant_colors=dominant_colors,
            complexity_score=complexity_score,
            aesthetic_score=aesthetic_score,
            technical_quality=technical_quality
        )
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data distribution"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        skewness = np.mean(((data - mean) / std) ** 3)
        return float(skewness)
    
    def _calculate_glcm_features(self, gray: np.ndarray) -> Dict[str, float]:
        """Calculate Gray-Level Co-occurrence Matrix features"""
        # Simplified GLCM features calculation
        # In production, use skimage.feature.greycomatrix
        
        # Calculate basic texture measures
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        texture_features = {
            'contrast': np.var(sobel_x) + np.var(sobel_y),
            'homogeneity': 1.0 / (1.0 + np.var(gray)),
            'energy': np.sum(gray ** 2) / (gray.shape[0] * gray.shape[1]),
            'correlation': np.corrcoef(sobel_x.flatten(), sobel_y.flatten())[0, 1]
        }
        
        # Replace NaN with 0
        for key, value in texture_features.items():
            if np.isnan(value):
                texture_features[key] = 0.0
        
        return texture_features
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using K-means clustering"""
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers to int tuples
        dominant_colors = [tuple(map(int, center)) for center in centers]
        
        return dominant_colors
    
    def _calculate_aesthetic_score(self, image: np.ndarray) -> float:
        """Calculate aesthetic score based on photographic principles"""
        
        # Rule of thirds score
        height, width = image.shape[:2]
        thirds_h = [height // 3, 2 * height // 3]
        thirds_w = [width // 3, 2 * width // 3]
        
        # Calculate edge density at rule of thirds lines
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        thirds_score = 0
        for h in thirds_h:
            thirds_score += np.sum(edges[h-2:h+2, :])
        for w in thirds_w:
            thirds_score += np.sum(edges[:, w-2:w+2])
        
        thirds_score = thirds_score / (edges.shape[0] * edges.shape[1])
        
        # Symmetry score
        left_half = image[:, :width//2]
        right_half = np.flip(image[:, width//2:], axis=1)
        min_width = min(left_half.shape[1], right_half.shape[1])
        
        symmetry_score = 1.0 - np.mean(np.abs(
            left_half[:, :min_width].astype(float) - 
            right_half[:, :min_width].astype(float)
        )) / 255.0
        
        # Color harmony score
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hue_std = np.std(hsv[:, :, 0])
        color_harmony = 1.0 / (1.0 + hue_std / 180.0)
        
        # Combined aesthetic score
        aesthetic_score = (thirds_score * 0.4 + symmetry_score * 0.3 + color_harmony * 0.3)
        
        return min(1.0, aesthetic_score)
    
    def _calculate_sharpness(self, gray: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return float(laplacian_var)
    
    def _estimate_noise_level(self, gray: np.ndarray) -> float:
        """Estimate noise level in image"""
        # Use median filter to estimate noise
        median_filtered = cv2.medianBlur(gray, 5)
        noise = np.abs(gray.astype(float) - median_filtered.astype(float))
        noise_level = np.mean(noise)
        return float(noise_level)
    
    def _assess_exposure_quality(self, gray: np.ndarray) -> float:
        """Assess exposure quality based on histogram distribution"""
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        
        # Check for under/over exposure
        under_exposed = np.sum(hist[:25])  # Very dark pixels
        over_exposed = np.sum(hist[230:])  # Very bright pixels
        
        # Ideal exposure has minimal clipping
        exposure_quality = 1.0 - (under_exposed + over_exposed)
        
        return max(0.0, exposure_quality)
    
    def _assess_color_accuracy(self, image: np.ndarray) -> float:
        """Assess color accuracy based on color distribution"""
        # Simple color accuracy measure based on color balance
        r_mean = np.mean(image[:, :, 0])
        g_mean = np.mean(image[:, :, 1])
        b_mean = np.mean(image[:, :, 2])
        
        # Good color accuracy has balanced channels
        color_balance = 1.0 - (np.std([r_mean, g_mean, b_mean]) / 255.0)
        
        return max(0.0, color_balance)
    
    def _generate_metadata(self, 
                          image_input: Union[str, np.ndarray, Image.Image],
                          processed_image: np.ndarray,
                          content_hash: str) -> VisualMetadata:
        """Generate comprehensive metadata for processed image"""
        
        file_path = str(image_input) if isinstance(image_input, str) else "memory"
        file_size = processed_image.nbytes
        dimensions = (processed_image.shape[1], processed_image.shape[0])
        
        # Calculate quality score
        quality_score = self._calculate_overall_quality(processed_image)
        
        metadata = VisualMetadata(
            file_path=file_path,
            file_size=file_size,
            dimensions=dimensions,
            format="RGB",
            color_space="sRGB",
            bit_depth=8,
            compression=None,
            creation_date=datetime.now(),
            modification_date=datetime.now(),
            content_hash=content_hash,
            quality_score=quality_score,
            processing_history=["AI Enhancement Applied"]
        )
        
        return metadata
    
    def _calculate_overall_quality(self, image: np.ndarray) -> float:
        """Calculate overall quality score for image"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Multiple quality metrics
        sharpness = self._calculate_sharpness(gray)
        noise_level = self._estimate_noise_level(gray)
        exposure_quality = self._assess_exposure_quality(gray)
        color_accuracy = self._assess_color_accuracy(image)
        
        # Normalize sharpness (higher is better)
        sharpness_norm = min(1.0, sharpness / 1000.0)
        
        # Normalize noise (lower is better)
        noise_norm = max(0.0, 1.0 - noise_level / 50.0)
        
        # Weighted combination
        quality_score = (
            sharpness_norm * 0.3 +
            noise_norm * 0.2 +
            exposure_quality * 0.3 +
            color_accuracy * 0.2
        )
        
        return quality_score
    
    def _calculate_quality_improvement(self, 
                                     original: np.ndarray, 
                                     enhanced: np.ndarray) -> float:
        """Calculate quality improvement percentage"""
        original_quality = self._calculate_overall_quality(original)
        enhanced_quality = self._calculate_overall_quality(enhanced)
        
        if original_quality == 0:
            return 0.0
        
        improvement = ((enhanced_quality - original_quality) / original_quality) * 100
        return max(0.0, improvement)
    
    def _generate_content_hash(self, image: np.ndarray) -> str:
        """Generate unique hash for image content"""
        # Create hash based on image content
        image_bytes = image.tobytes()
        hash_object = hashlib.sha256(image_bytes)
        return hash_object.hexdigest()
    
    def _update_cache(self, content_hash: str, result: ProcessingResult):
        """Update processing cache with result"""
        if len(self._cache) >= self.cache_size:
            # Remove oldest entry
            oldest_hash = self._cache_order.pop(0)
            del self._cache[oldest_hash]
        
        self._cache[content_hash] = result
        self._cache_order.append(content_hash)
    
    def clear_cache(self):
        """Clear processing cache"""
        self._cache.clear()
        self._cache_order.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "cache_capacity": self.cache_size,
            "cache_hit_ratio": getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1)
        }

class ImageAnalyzer:
    """
    Specialized image analysis engine for content recognition and classification.
    
    Provides advanced analysis capabilities for the IA Influencer Agent platform,
    supporting content creators with automated image understanding and tagging.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize ImageAnalyzer with pre-trained models"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self._init_models()
    
    def _init_models(self):
        """Initialize analysis models"""
        # In production, load actual pre-trained models
        # For now, use placeholder architectures
        
        self.scene_classifier = self._create_scene_classifier()
        self.content_classifier = self._create_content_classifier()
        
        logger.info("ImageAnalyzer models initialized")
    
    def _create_scene_classifier(self) -> nn.Module:
        """Create scene classification model"""
        model = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((7, 7)),
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 512),
            nn.ReLU(),
            nn.Linear(512, 100)  # 100 scene categories
        )
        return model.to(self.device)
    
    def _create_content_classifier(self) -> nn.Module:
        """Create content classification model"""
        model = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((8, 8)),
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 256),
            nn.ReLU(),
            nn.Linear(256, 50)  # 50 content categories
        )
        return model.to(self.device)
    
    def analyze_scene(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze scene content and return confidence scores"""
        # Convert to tensor and normalize
        if image.max() > 1:
            image = image.astype(np.float32) / 255.0
        
        image_tensor = torch.from_numpy(image.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.scene_classifier(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
        
        # Mock scene categories for demonstration
        scene_categories = [
            "outdoor", "indoor", "urban", "nature", "portrait", "landscape",
            "architecture", "vehicle", "food", "animal", "sports", "event",
            "art", "technology", "fashion", "travel", "music", "business"
        ]
        
        # Return top predictions
        top_probs, top_indices = torch.topk(probabilities, min(len(scene_categories), 5))
        
        results = {}
        for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
            if i < len(scene_categories):
                results[scene_categories[i]] = float(prob.cpu())
        
        return results
    
    def analyze_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Comprehensive content analysis"""
        scene_analysis = self.analyze_scene(image)
        
        # Additional content analysis
        content_analysis = {
            "scene_classification": scene_analysis,
            "dominant_objects": self._detect_objects_simple(image),
            "color_palette": self._analyze_color_palette(image),
            "composition_analysis": self._analyze_composition(image),
            "style_analysis": self._analyze_style(image)
        }
        
        return content_analysis
    
    def _detect_objects_simple(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Simple object detection using traditional CV methods"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Use Haar cascades for basic object detection
        # In production, use YOLO or other advanced models
        
        objects = []
        
        # Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            objects.append({
                "type": "face",
                "confidence": 0.8,
                "bbox": [int(x), int(y), int(w), int(h)]
            })
        
        return objects
    
    def _analyze_color_palette(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color palette of image"""
        # Extract dominant colors
        data = image.reshape((-1, 3))
        data = np.float32(data)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 5, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Calculate color percentages
        unique, counts = np.unique(labels, return_counts=True)
        percentages = counts / counts.sum()
        
        color_palette = []
        for center, percentage in zip(centers, percentages):
            color_palette.append({
                "color": tuple(map(int, center)),
                "percentage": float(percentage),
                "hex": "#{:02x}{:02x}{:02x}".format(int(center[0]), int(center[1]), int(center[2]))
            })
        
        # Sort by percentage
        color_palette.sort(key=lambda x: x["percentage"], reverse=True)
        
        return {
            "dominant_colors": color_palette,
            "color_temperature": self._calculate_color_temperature(image),
            "saturation_level": np.mean(cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:, :, 1])
        }
    
    def _calculate_color_temperature(self, image: np.ndarray) -> str:
        """Calculate approximate color temperature"""
        r_mean = np.mean(image[:, :, 0])
        g_mean = np.mean(image[:, :, 1])
        b_mean = np.mean(image[:, :, 2])
        
        if b_mean > r_mean:
            return "cool"
        elif r_mean > b_mean:
            return "warm"
        else:
            return "neutral"
    
    def _analyze_composition(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image composition"""
        height, width = image.shape[:2]
        
        # Rule of thirds analysis
        thirds_h = [height // 3, 2 * height // 3]
        thirds_w = [width // 3, 2 * width // 3]
        
        # Edge detection for composition analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate edge density at thirds intersections
        intersection_scores = []
        for h in thirds_h:
            for w in thirds_w:
                region = edges[max(0, h-10):min(height, h+10), 
                              max(0, w-10):min(width, w+10)]
                score = np.sum(region) / (region.shape[0] * region.shape[1])
                intersection_scores.append(score)
        
        composition_score = np.mean(intersection_scores)
        
        return {
            "rule_of_thirds_score": float(composition_score),
            "symmetry_score": self._calculate_symmetry(image),
            "leading_lines": self._detect_leading_lines(edges),
            "balance_score": self._calculate_balance(image)
        }
    
    def _calculate_symmetry(self, image: np.ndarray) -> float:
        """Calculate symmetry score"""
        height, width = image.shape[:2]
        
        # Vertical symmetry
        left_half = image[:, :width//2]
        right_half = np.flip(image[:, width//2:], axis=1)
        min_width = min(left_half.shape[1], right_half.shape[1])
        
        vertical_symmetry = 1.0 - np.mean(np.abs(
            left_half[:, :min_width].astype(float) - 
            right_half[:, :min_width].astype(float)
        )) / 255.0
        
        return max(0.0, vertical_symmetry)
    
    def _detect_leading_lines(self, edges: np.ndarray) -> int:
        """Detect leading lines in image"""
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        return len(lines) if lines is not None else 0
    
    def _calculate_balance(self, image: np.ndarray) -> float:
        """Calculate visual balance of image"""
        height, width = image.shape[:2]
        
        # Convert to grayscale for weight calculation
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate center of mass
        y_indices, x_indices = np.indices(gray.shape)
        total_weight = np.sum(gray)
        
        if total_weight == 0:
            return 0.5
        
        center_x = np.sum(x_indices * gray) / total_weight
        center_y = np.sum(y_indices * gray) / total_weight
        
        # Calculate distance from image center
        image_center_x = width / 2
        image_center_y = height / 2
        
        distance = np.sqrt((center_x - image_center_x)**2 + (center_y - image_center_y)**2)
        max_distance = np.sqrt((width/2)**2 + (height/2)**2)
        
        balance_score = 1.0 - (distance / max_distance)
        
        return max(0.0, balance_score)
    
    def _analyze_style(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze artistic style of image"""
        
        # Simple style analysis based on statistical features
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Texture analysis
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        texture_strength = np.mean(np.sqrt(sobel_x**2 + sobel_y**2))
        
        # Color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        saturation_mean = np.mean(hsv[:, :, 1])
        
        # Determine style characteristics
        style_analysis = {
            "texture_strength": float(texture_strength),
            "color_vibrancy": float(saturation_mean),
            "contrast_level": float(np.std(gray)),
            "estimated_style": self._classify_style(texture_strength, saturation_mean, np.std(gray))
        }
        
        return style_analysis
    
    def _classify_style(self, texture: float, saturation: float, contrast: float) -> str:
        """Classify artistic style based on features"""
        
        if texture > 100 and contrast > 50:
            return "high_detail"
        elif saturation > 150:
            return "vibrant"
        elif contrast < 30:
            return "soft"
        elif texture < 50:
            return "minimal"
        else:
            return "balanced"

class VideoAnalyzer:
    """
    Advanced video analysis engine for temporal visual content processing.
    
    Specialized for analyzing video content for the IA Influencer Agent platform,
    supporting content creators with automated video understanding and optimization.
    """
    
    def __init__(self, frame_sampling_rate: float = 1.0):
        """
        Initialize VideoAnalyzer.
        
        Args:
            frame_sampling_rate: Rate of frame sampling (frames per second)
        """
        self.frame_sampling_rate = frame_sampling_rate
        self.image_analyzer = ImageAnalyzer()
        
        logger.info("VideoAnalyzer initialized")
    
    def analyze_video(self, video_path: str, 
                     max_frames: int = 100) -> Dict[str, Any]:
        """
        Comprehensive video analysis.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to analyze
            
        Returns:
            Dict: Comprehensive video analysis results
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate frame sampling interval
            sample_interval = max(1, frame_count // min(max_frames, frame_count))
            
            frame_analyses = []
            frame_number = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % sample_interval == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Analyze frame
                    frame_analysis = self.image_analyzer.analyze_content(frame_rgb)
                    frame_analysis["timestamp"] = frame_number / fps
                    frame_analysis["frame_number"] = frame_number
                    
                    frame_analyses.append(frame_analysis)
                
                frame_number += 1
            
            cap.release()
            
            # Aggregate video-level analysis
            video_analysis = self._aggregate_video_analysis(frame_analyses)
            
            # Add video metadata
            video_analysis["metadata"] = {
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "resolution": (width, height),
                "analyzed_frames": len(frame_analyses)
            }
            
            return video_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            raise
    
    def _aggregate_video_analysis(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate frame-level analyses into video-level insights"""
        
        if not frame_analyses:
            return {}
        
        # Aggregate scene classifications
        scene_votes = {}
        for frame in frame_analyses:
            scene_classification = frame.get("scene_classification", {})
            for scene, confidence in scene_classification.items():
                if scene not in scene_votes:
                    scene_votes[scene] = []
                scene_votes[scene].append(confidence)
        
        # Calculate average confidence for each scene
        average_scenes = {}
        for scene, confidences in scene_votes.items():
            average_scenes[scene] = np.mean(confidences)
        
        # Sort by confidence
        sorted_scenes = sorted(average_scenes.items(), key=lambda x: x[1], reverse=True)
        
        # Analyze color consistency
        color_consistency = self._analyze_color_consistency(frame_analyses)
        
        # Analyze motion patterns
        motion_analysis = self._analyze_motion_patterns(frame_analyses)
        
        # Quality consistency
        quality_consistency = self._analyze_quality_consistency(frame_analyses)
        
        return {
            "primary_scenes": sorted_scenes[:3],
            "scene_transitions": self._detect_scene_transitions(frame_analyses),
            "color_consistency": color_consistency,
            "motion_analysis": motion_analysis,
            "quality_consistency": quality_consistency,
            "temporal_features": self._extract_temporal_features(frame_analyses)
        }
    
    def _analyze_color_consistency(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze color consistency across video"""
        
        color_temperatures = []
        saturation_levels = []
        
        for frame in frame_analyses:
            color_palette = frame.get("color_palette", {})
            if "color_temperature" in color_palette:
                # Convert temperature to numeric value
                temp_map = {"cool": 0, "neutral": 0.5, "warm": 1}
                color_temperatures.append(temp_map.get(color_palette["color_temperature"], 0.5))
            
            if "saturation_level" in color_palette:
                saturation_levels.append(color_palette["saturation_level"])
        
        consistency = {}
        
        if color_temperatures:
            consistency["temperature_variance"] = float(np.var(color_temperatures))
        
        if saturation_levels:
            consistency["saturation_variance"] = float(np.var(saturation_levels))
        
        return consistency
    
    def _analyze_motion_patterns(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze motion patterns in video"""
        
        # Simple motion analysis based on composition changes
        composition_scores = []
        
        for frame in frame_analyses:
            composition = frame.get("composition_analysis", {})
            if "rule_of_thirds_score" in composition:
                composition_scores.append(composition["rule_of_thirds_score"])
        
        motion_analysis = {
            "composition_stability": float(1.0 - np.var(composition_scores)) if composition_scores else 0.0,
            "estimated_motion_level": "low" if np.var(composition_scores) < 0.1 else "medium" if np.var(composition_scores) < 0.3 else "high"
        }
        
        return motion_analysis
    
    def _analyze_quality_consistency(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze quality consistency across video"""
        
        # Extract quality metrics from composition and style analyses
        sharpness_indicators = []
        balance_scores = []
        
        for frame in frame_analyses:
            composition = frame.get("composition_analysis", {})
            style = frame.get("style_analysis", {})
            
            if "balance_score" in composition:
                balance_scores.append(composition["balance_score"])
            
            if "contrast_level" in style:
                sharpness_indicators.append(style["contrast_level"])
        
        consistency = {}
        
        if balance_scores:
            consistency["balance_consistency"] = float(1.0 - np.var(balance_scores))
        
        if sharpness_indicators:
            consistency["sharpness_consistency"] = float(1.0 - np.var(sharpness_indicators))
        
        return consistency
    
    def _detect_scene_transitions(self, frame_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect scene transitions in video"""
        
        transitions = []
        
        for i in range(1, len(frame_analyses)):
            current_frame = frame_analyses[i]
            previous_frame = frame_analyses[i-1]
            
            # Compare scene classifications
            current_scenes = current_frame.get("scene_classification", {})
            previous_scenes = previous_frame.get("scene_classification", {})
            
            # Calculate scene similarity
            similarity = self._calculate_scene_similarity(current_scenes, previous_scenes)
            
            # If similarity is low, it might be a scene transition
            if similarity < 0.7:
                transitions.append({
                    "timestamp": current_frame.get("timestamp", 0),
                    "frame_number": current_frame.get("frame_number", 0),
                    "similarity_score": similarity,
                    "transition_type": "scene_change"
                })
        
        return transitions
    
    def _calculate_scene_similarity(self, scenes1: Dict[str, float], 
                                   scenes2: Dict[str, float]) -> float:
        """Calculate similarity between two scene classifications"""
        
        if not scenes1 or not scenes2:
            return 0.0
        
        # Get common scenes
        common_scenes = set(scenes1.keys()) & set(scenes2.keys())
        
        if not common_scenes:
            return 0.0
        
        # Calculate weighted similarity
        total_similarity = 0.0
        total_weight = 0.0
        
        for scene in common_scenes:
            weight = (scenes1[scene] + scenes2[scene]) / 2
            similarity = 1.0 - abs(scenes1[scene] - scenes2[scene])
            total_similarity += similarity * weight
            total_weight += weight
        
        return total_similarity / total_weight if total_weight > 0 else 0.0
    
    def _extract_temporal_features(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract temporal features from video analysis"""
        
        if not frame_analyses:
            return {}
        
        # Extract various temporal patterns
        timestamps = [frame.get("timestamp", 0) for frame in frame_analyses]
        
        # Color evolution
        color_evolution = []
        for frame in frame_analyses:
            color_palette = frame.get("color_palette", {})
            dominant_colors = color_palette.get("dominant_colors", [])
            if dominant_colors:
                color_evolution.append(dominant_colors[0]["color"])
        
        # Style evolution
        style_evolution = []
        for frame in frame_analyses:
            style = frame.get("style_analysis", {})
            if "estimated_style" in style:
                style_evolution.append(style["estimated_style"])
        
        return {
            "duration_analyzed": max(timestamps) - min(timestamps) if timestamps else 0,
            "color_evolution": color_evolution,
            "style_evolution": style_evolution,
            "dominant_style": max(set(style_evolution), key=style_evolution.count) if style_evolution else "unknown"
        }
