"""Advanced Image Analytics Engine
Professional image analysis, composition assessment, and quality evaluation.

This module provides comprehensive image analytics including color analysis,
composition evaluation, aesthetic scoring, and technical quality assessment.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import asyncio
from datetime import datetime
from skimage import measure, feature, filters
from scipy import ndimage
import colorsys

logger = logging.getLogger(__name__)

@dataclass
class ImageMetrics:
    """Comprehensive image metrics data structure"""
    file_path: str
    resolution: Tuple[int, int]
    channels: int
    bit_depth: Optional[int] = None
    file_size: Optional[int] = None
    
    # Quality metrics
    quality_score: float = 0.0
    sharpness_score: float = 0.0
    noise_level: float = 0.0
    compression_artifacts: float = 0.0
    
    # Color analysis
    color_distribution: Dict[str, float] = field(default_factory=dict)
    color_harmony: float = 0.0
    color_temperature: float = 0.0
    saturation_levels: Dict[str, float] = field(default_factory=dict)
    
    # Composition analysis
    composition_score: float = 0.0
    rule_of_thirds_score: float = 0.0
    symmetry_score: float = 0.0
    balance_score: float = 0.0
    leading_lines_score: float = 0.0
    
    # Technical analysis
    contrast_ratio: float = 0.0
    brightness_distribution: Dict[str, float] = field(default_factory=dict)
    histogram_analysis: Dict[str, Any] = field(default_factory=dict)
    exposure_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Aesthetic features
    aesthetic_score: float = 0.0
    visual_complexity: float = 0.0
    texture_analysis: Dict[str, float] = field(default_factory=dict)
    edge_density: float = 0.0
    
    # Object detection
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    face_detection: List[Dict[str, Any]] = field(default_factory=list)
    
    # Processing metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0


class ColorAnalyzer:
    """Advanced color analysis and harmony assessment"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
    async def analyze_color_distribution(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution and characteristics"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Color distribution in RGB
            color_means = {
                'red_mean': float(np.mean(image[:, :, 2])),
                'green_mean': float(np.mean(image[:, :, 1])),
                'blue_mean': float(np.mean(image[:, :, 0])),
                'red_std': float(np.std(image[:, :, 2])),
                'green_std': float(np.std(image[:, :, 1])),
                'blue_std': float(np.std(image[:, :, 0]))
            }
            
            # HSV analysis
            hsv_analysis = {
                'hue_mean': float(np.mean(hsv[:, :, 0])),
                'saturation_mean': float(np.mean(hsv[:, :, 1])),
                'value_mean': float(np.mean(hsv[:, :, 2])),
                'hue_std': float(np.std(hsv[:, :, 0])),
                'saturation_std': float(np.std(hsv[:, :, 1])),
                'value_std': float(np.std(hsv[:, :, 2]))
            }
            
            # Dominant colors
            dominant_colors = await self._extract_dominant_colors(image)
            
            # Color temperature estimation
            color_temperature = await self._estimate_color_temperature(image)
            
            return {
                'color_means': color_means,
                'hsv_analysis': hsv_analysis,
                'dominant_colors': dominant_colors,
                'color_temperature': color_temperature
            }
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
            return {}
    
    async def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Extract dominant colors using K-means clustering"""
        try:
            # Reshape image to list of pixels
            pixels = image.reshape(-1, 3).astype(np.float32)
            
            # Apply K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Calculate color percentages
            unique_labels, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels) * 100
            
            dominant_colors = []
            for i, (center, percentage) in enumerate(zip(centers, percentages)):
                # Convert BGR to RGB
                rgb_color = center[::-1].astype(int)
                
                # Convert to HSV for additional info
                hsv_color = colorsys.rgb_to_hsv(rgb_color[0]/255, rgb_color[1]/255, rgb_color[2]/255)
                
                dominant_colors.append({
                    'color_index': int(i),
                    'rgb': rgb_color.tolist(),
                    'bgr': center.astype(int).tolist(),
                    'hsv': [float(hsv_color[0]*360), float(hsv_color[1]*100), float(hsv_color[2]*100)],
                    'percentage': float(percentage)
                })
            
            # Sort by percentage
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    async def _estimate_color_temperature(self, image: np.ndarray) -> float:
        """Estimate color temperature of the image"""
        try:
            # Convert to RGB
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Calculate average RGB values
            r_avg = np.mean(rgb[:, :, 0])
            g_avg = np.mean(rgb[:, :, 1])
            b_avg = np.mean(rgb[:, :, 2])
            
            # Simple color temperature estimation
            # Based on the ratio of blue to red
            if r_avg > 0:
                blue_red_ratio = b_avg / r_avg
                
                # Approximate color temperature mapping
                if blue_red_ratio > 1.2:
                    color_temp = 6500 + (blue_red_ratio - 1.2) * 2000  # Cool
                elif blue_red_ratio < 0.8:
                    color_temp = 3000 - (0.8 - blue_red_ratio) * 1000  # Warm
                else:
                    color_temp = 5500  # Neutral
                
                return float(max(2000, min(10000, color_temp)))
            
            return 5500.0  # Default neutral temperature
            
        except Exception as e:
            self.logger.error(f"Color temperature estimation failed: {e}")
            return 5500.0
    
    async def calculate_color_harmony(self, dominant_colors: List[Dict[str, Any]]) -> float:
        """Calculate color harmony score based on color theory"""
        try:
            if len(dominant_colors) < 2:
                return 1.0
            
            # Extract hue values
            hues = [color['hsv'][0] for color in dominant_colors[:5]]  # Top 5 colors
            
            # Calculate hue differences
            harmony_scores = []
            
            for i in range(len(hues)):
                for j in range(i + 1, len(hues)):
                    hue_diff = abs(hues[i] - hues[j])
                    hue_diff = min(hue_diff, 360 - hue_diff)  # Circular distance
                    
                    # Score based on color harmony rules
                    if 0 <= hue_diff <= 30:  # Analogous
                        score = 1.0
                    elif 150 <= hue_diff <= 210:  # Complementary
                        score = 0.9
                    elif 110 <= hue_diff <= 130:  # Triadic
                        score = 0.8
                    elif 50 <= hue_diff <= 70:  # Split complementary
                        score = 0.7
                    else:
                        score = 0.5
                    
                    harmony_scores.append(score)
            
            return float(np.mean(harmony_scores)) if harmony_scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Color harmony calculation failed: {e}")
            return 0.5


class CompositionAnalyzer:
    """Advanced composition analysis and aesthetic evaluation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
    async def analyze_composition(self, image: np.ndarray) -> Dict[str, float]:
        """Comprehensive composition analysis"""
        try:
            # Rule of thirds
            rule_of_thirds = await self._analyze_rule_of_thirds(image)
            
            # Symmetry analysis
            symmetry_score = await self._analyze_symmetry(image)
            
            # Balance analysis
            balance_score = await self._analyze_balance(image)
            
            # Leading lines
            leading_lines = await self._analyze_leading_lines(image)
            
            # Overall composition score
            composition_factors = [
                rule_of_thirds,
                symmetry_score,
                balance_score,
                leading_lines
            ]
            
            composition_score = np.mean(composition_factors)
            
            return {
                'rule_of_thirds_score': float(rule_of_thirds),
                'symmetry_score': float(symmetry_score),
                'balance_score': float(balance_score),
                'leading_lines_score': float(leading_lines),
                'overall_composition_score': float(composition_score)
            }
            
        except Exception as e:
            self.logger.error(f"Composition analysis failed: {e}")
            return {}
    
    async def _analyze_rule_of_thirds(self, image: np.ndarray) -> float:
        """Analyze adherence to rule of thirds"""
        try:
            h, w = image.shape[:2]
            
            # Define rule of thirds lines
            third_h = h // 3
            third_w = w // 3
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Find significant points (high gradient areas)
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate interest points near rule of thirds intersections
            intersections = [
                (third_w, third_h),
                (2 * third_w, third_h),
                (third_w, 2 * third_h),
                (2 * third_w, 2 * third_h)
            ]
            
            scores = []
            for x, y in intersections:
                # Check area around intersection
                area_size = min(w // 10, h // 10)
                x1, y1 = max(0, x - area_size), max(0, y - area_size)
                x2, y2 = min(w, x + area_size), min(h, y + area_size)
                
                area_edges = edges[y1:y2, x1:x2]
                edge_density = np.sum(area_edges) / (area_edges.size * 255)
                scores.append(edge_density)
            
            return float(np.mean(scores))
            
        except Exception as e:
            self.logger.error(f"Rule of thirds analysis failed: {e}")
            return 0.5
    
    async def _analyze_symmetry(self, image: np.ndarray) -> float:
        """Analyze image symmetry"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Vertical symmetry
            left_half = gray[:, :w//2]
            right_half = np.fliplr(gray[:, w//2:])
            
            # Ensure same size
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            vertical_symmetry = 1.0 - np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
            
            # Horizontal symmetry
            top_half = gray[:h//2, :]
            bottom_half = np.flipud(gray[h//2:, :])
            
            min_height = min(top_half.shape[0], bottom_half.shape[0])
            top_half = top_half[:min_height, :]
            bottom_half = bottom_half[:min_height, :]
            
            horizontal_symmetry = 1.0 - np.mean(np.abs(top_half.astype(float) - bottom_half.astype(float))) / 255.0
            
            # Return best symmetry score
            return float(max(vertical_symmetry, horizontal_symmetry))
            
        except Exception as e:
            self.logger.error(f"Symmetry analysis failed: {e}")
            return 0.5
    
    async def _analyze_balance(self, image: np.ndarray) -> float:
        """Analyze visual balance of the image"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Calculate center of mass
            total_mass = np.sum(gray)
            if total_mass == 0:
                return 0.5
            
            # Create coordinate grids
            y_coords, x_coords = np.mgrid[0:h, 0:w]
            
            # Calculate weighted center of mass
            center_x = np.sum(x_coords * gray) / total_mass
            center_y = np.sum(y_coords * gray) / total_mass
            
            # Calculate distance from image center
            image_center_x, image_center_y = w / 2, h / 2
            distance_from_center = np.sqrt((center_x - image_center_x)**2 + (center_y - image_center_y)**2)
            
            # Normalize distance
            max_distance = np.sqrt((w/2)**2 + (h/2)**2)
            balance_score = 1.0 - (distance_from_center / max_distance)
            
            return float(max(0.0, balance_score))
            
        except Exception as e:
            self.logger.error(f"Balance analysis failed: {e}")
            return 0.5
    
    async def _analyze_leading_lines(self, image: np.ndarray) -> float:
        """Analyze leading lines in the image"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough line detection
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is None:
                return 0.3
            
            # Analyze line directions
            angles = []
            for line in lines:
                rho, theta = line[0]
                angles.append(theta)
            
            # Score based on line variety and strength
            if len(angles) > 0:
                # Prefer diagonal lines (leading lines)
                diagonal_count = sum(1 for angle in angles if 0.2 < angle < 2.9)
                line_score = min(1.0, diagonal_count / len(angles) + len(angles) / 50.0)
                return float(line_score)
            
            return 0.3
            
        except Exception as e:
            self.logger.error(f"Leading lines analysis failed: {e}")
            return 0.3


class ImageAnalyzer:
    """Comprehensive image analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Initialize sub-analyzers
        self.color_analyzer = ColorAnalyzer(config)
        self.composition_analyzer = CompositionAnalyzer(config)
        
        # Analysis parameters
        self.quality_threshold = self.config.get('quality_threshold', 0.7)
        
    async def analyze_file(self, file_path: str) -> ImageMetrics:
        """Comprehensive image file analysis"""
        start_time = datetime.now()
        
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Cannot load image: {file_path}")
            
            # Get image properties
            h, w, c = image.shape
            file_size = Path(file_path).stat().st_size
            
            # Initialize metrics
            metrics = ImageMetrics(
                file_path=file_path,
                resolution=(w, h),
                channels=c,
                file_size=file_size
            )
            
            # Quality analysis
            await self._analyze_quality(image, metrics)
            
            # Color analysis
            await self._analyze_colors(image, metrics)
            
            # Composition analysis
            await self._analyze_composition(image, metrics)
            
            # Technical analysis
            await self._analyze_technical_aspects(image, metrics)
            
            # Aesthetic analysis
            await self._analyze_aesthetics(image, metrics)
            
            # Calculate processing time
            metrics.processing_time = (datetime.now() - start_time).total_seconds()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Image analysis failed for {file_path}: {e}")
            raise
    
    async def _analyze_quality(self, image: np.ndarray, metrics: ImageMetrics) -> None:
        """Analyze image quality metrics"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            metrics.sharpness_score = float(laplacian.var())
            
            # Noise estimation
            noise_score = filters.rank.median(gray, np.ones((3, 3)))
            noise_level = np.mean(np.abs(gray.astype(float) - noise_score.astype(float)))
            metrics.noise_level = float(noise_level)
            
            # Compression artifacts detection (simplified)
            # Look for blocking artifacts
            block_size = 8
            artifacts = 0
            for y in range(0, gray.shape[0] - block_size, block_size):
                for x in range(0, gray.shape[1] - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size]
                    if np.std(block) < 5:  # Very uniform block might indicate compression
                        artifacts += 1
            
            total_blocks = (gray.shape[0] // block_size) * (gray.shape[1] // block_size)
            metrics.compression_artifacts = float(artifacts / total_blocks) if total_blocks > 0 else 0.0
            
            # Overall quality score
            sharpness_norm = min(metrics.sharpness_score / 1000.0, 1.0)
            noise_norm = max(0.0, 1.0 - metrics.noise_level / 50.0)
            artifacts_norm = max(0.0, 1.0 - metrics.compression_artifacts)
            
            metrics.quality_score = float(np.mean([sharpness_norm, noise_norm, artifacts_norm]))
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
    
    async def _analyze_colors(self, image: np.ndarray, metrics: ImageMetrics) -> None:
        """Analyze color characteristics"""
        try:
            color_analysis = await self.color_analyzer.analyze_color_distribution(image)
            
            if color_analysis:
                metrics.color_distribution = color_analysis.get('color_means', {})
                metrics.color_temperature = color_analysis.get('color_temperature', 5500.0)
                
                # Calculate color harmony
                dominant_colors = color_analysis.get('dominant_colors', [])
                metrics.color_harmony = await self.color_analyzer.calculate_color_harmony(dominant_colors)
                
                # Saturation analysis
                hsv_analysis = color_analysis.get('hsv_analysis', {})
                metrics.saturation_levels = {
                    'average_saturation': hsv_analysis.get('saturation_mean', 0.0),
                    'saturation_variance': hsv_analysis.get('saturation_std', 0.0)
                }
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
    
    async def _analyze_composition(self, image: np.ndarray, metrics: ImageMetrics) -> None:
        """Analyze composition aspects"""
        try:
            composition_analysis = await self.composition_analyzer.analyze_composition(image)
            
            if composition_analysis:
                metrics.rule_of_thirds_score = composition_analysis.get('rule_of_thirds_score', 0.5)
                metrics.symmetry_score = composition_analysis.get('symmetry_score', 0.5)
                metrics.balance_score = composition_analysis.get('balance_score', 0.5)
                metrics.leading_lines_score = composition_analysis.get('leading_lines_score', 0.5)
                metrics.composition_score = composition_analysis.get('overall_composition_score', 0.5)
            
        except Exception as e:
            self.logger.error(f"Composition analysis failed: {e}")
    
    async def _analyze_technical_aspects(self, image: np.ndarray, metrics: ImageMetrics) -> None:
        """Analyze technical image aspects"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Contrast analysis
            min_val, max_val = np.min(gray), np.max(gray)
            metrics.contrast_ratio = float((max_val - min_val) / 255.0) if max_val > min_val else 0.0
            
            # Brightness distribution
            brightness_mean = np.mean(gray)
            brightness_std = np.std(gray)
            
            metrics.brightness_distribution = {
                'mean_brightness': float(brightness_mean),
                'brightness_std': float(brightness_std),
                'min_brightness': float(min_val),
                'max_brightness': float(max_val)
            }
            
            # Histogram analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_normalized = hist.flatten() / np.sum(hist)
            
            metrics.histogram_analysis = {
                'entropy': float(-np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))),
                'peak_count': int(len(np.where(hist > np.max(hist) * 0.1)[0])),
                'histogram_spread': float(np.std(hist_normalized))
            }
            
            # Exposure analysis
            underexposed = np.sum(gray < 25) / gray.size
            overexposed = np.sum(gray > 230) / gray.size
            well_exposed = 1.0 - underexposed - overexposed
            
            metrics.exposure_analysis = {
                'underexposed_percentage': float(underexposed * 100),
                'overexposed_percentage': float(overexposed * 100),
                'well_exposed_percentage': float(well_exposed * 100)
            }
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed: {e}")
    
    async def _analyze_aesthetics(self, image: np.ndarray, metrics: ImageMetrics) -> None:
        """Analyze aesthetic qualities"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Visual complexity
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            metrics.edge_density = float(edge_density)
            
            # Texture analysis
            glcm = feature.graycomatrix(gray, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256, symmetric=True, normed=True)
            
            contrast = feature.graycoprops(glcm, 'contrast')[0, 0]
            homogeneity = feature.graycoprops(glcm, 'homogeneity')[0, 0]
            energy = feature.graycoprops(glcm, 'energy')[0, 0]
            
            metrics.texture_analysis = {
                'contrast': float(contrast),
                'homogeneity': float(homogeneity),
                'energy': float(energy)
            }
            
            # Visual complexity score
            complexity_factors = [
                edge_density * 2,  # Edge density contributes more
                1.0 - homogeneity,  # Less homogeneity = more complex
                contrast / 1000.0  # Normalize contrast
            ]
            metrics.visual_complexity = float(np.mean(complexity_factors))
            
            # Aesthetic score (simplified model)
            aesthetic_factors = [
                metrics.composition_score,
                metrics.color_harmony,
                min(1.0, metrics.sharpness_score / 500.0),  # Normalize sharpness
                metrics.contrast_ratio,
                1.0 - min(1.0, metrics.visual_complexity)  # Prefer moderate complexity
            ]
            
            metrics.aesthetic_score = float(np.mean(aesthetic_factors))
            
        except Exception as e:
            self.logger.error(f"Aesthetic analysis failed: {e}")
    
    async def batch_analyze(self, file_paths: List[str]) -> List[ImageMetrics]:
        """Analyze multiple image files"""
        try:
            tasks = [self.analyze_file(path) for path in file_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to analyze {file_paths[i]}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch image analysis failed: {e}")
            return []