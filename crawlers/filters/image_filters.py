"""
IA Influencer Agent - Image Content Filters
===========================================

Ultra-advanced professional image content filtering for multimedia processing.
Implements enterprise-grade image analysis with AI-powered validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

 STRICT COPYRIGHT PROTECTION 
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat, ImageFilter
    import imagehash
    HAS_IMAGE_LIBS = True
except ImportError:
    HAS_IMAGE_LIBS = False
    logging.warning("Image processing libraries not available. Install opencv-python, pillow, imagehash.")

from .config import ImageFilterConfig
from .filter_engine import FilterResponse, FilterResult, FilterType, ContentItem


class ImageQualityAnalyzer:
    """Image quality analysis and aesthetic scoring."""
    
    def __init__(self):
        """Initialize image quality analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze comprehensive image quality metrics."""



        try:
            quality_metrics = {}
            
            # Convert to appropriate formats
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                gray = image
                pil_image = Image.fromarray(gray)
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'] = float(laplacian_var)
            
            # Brightness analysis
            brightness = np.mean(gray)
            quality_metrics['brightness'] = float(brightness)
            
            # Contrast (standard deviation)
            contrast = np.std(gray)
            quality_metrics['contrast'] = float(contrast)
            
            # Color analysis (if color image)
            if len(image.shape) == 3:
                color_metrics = self._analyze_color_properties(image)
                quality_metrics.update(color_metrics)
            
            # Noise estimation
            noise_level = self._estimate_noise(gray)
            quality_metrics['noise_level'] = float(noise_level)
            
            # Compression artifacts detection
            compression_score = self._detect_compression_artifacts(gray)
            quality_metrics['compression_artifacts'] = float(compression_score)
            
            # Overall quality score calculation
            overall_score = self._calculate_quality_score(quality_metrics)
            quality_metrics['overall_score'] = float(overall_score)
            
            return quality_metrics
            
        except Exception as e:
            self.logger.warning(f"Image quality analysis failed: {str(e)}")
            return {'error': str(e), 'overall_score': 0.5}
    
    def _analyze_color_properties(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze color properties of the image."""



        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Saturation analysis
            saturation_mean = np.mean(hsv[:, :, 1])
            saturation_std = np.std(hsv[:, :, 1])
            
            # Hue distribution
            hue_values = hsv[:, :, 0].flatten()
            hue_histogram = np.histogram(hue_values, bins=360)[0]
            hue_diversity = len(np.where(hue_histogram > 0)[0]) / 360.0
            
            # Color temperature estimation (simplified)
            b, g, r = cv2.split(image)
            color_temperature = (np.mean(r) - np.mean(b)) / (np.mean(r) + np.mean(b) + 1e-6)
            
            return {
                'saturation_mean': float(saturation_mean),
                'saturation_std': float(saturation_std),
                'hue_diversity': float(hue_diversity),
                'color_temperature': float(color_temperature)
            }
            
        except Exception as e:
            self.logger.warning(f"Color analysis failed: {str(e)}")
            return {}
    
    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in the image."""



        try:
            # Use high-pass filter to estimate noise
            kernel = np.array([[-1, -1, -1],
                              [-1,  8, -1],
                              [-1, -1, -1]])
            
            filtered = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
            noise_estimate = np.mean(np.abs(filtered))
            
            return min(100.0, noise_estimate)
            
        except Exception as e:
            self.logger.warning(f"Noise estimation failed: {str(e)}")
            return 10.0  # Default moderate noise
    
    def _detect_compression_artifacts(self, gray_image: np.ndarray) -> float:
        """Detect JPEG compression artifacts."""



        try:
            # Use DCT to detect blocking artifacts
            h, w = gray_image.shape
            
            # Divide image into 8x8 blocks (JPEG standard)
            block_scores = []
            
            for i in range(0, h - 7, 8):
                for j in range(0, w - 7, 8):
                    block = gray_image[i:i+8, j:j+8].astype(np.float32)
                    
                    # Calculate block variance
                    block_var = np.var(block)
                    
                    # Check for artificial boundaries
                    boundary_diff = (
                        np.mean(np.abs(np.diff(block, axis=0))) +
                        np.mean(np.abs(np.diff(block, axis=1)))
                    ) / 2
                    
                    # High variance with low boundary differences suggests artifacts
                    if block_var > 100:
                        artifact_score = 1.0 - (boundary_diff / (block_var + 1e-6))
                        block_scores.append(max(0.0, artifact_score))
            
            return np.mean(block_scores) if block_scores else 0.0
            
        except Exception as e:
            self.logger.warning(f"Compression artifact detection failed: {str(e)}")
            return 0.0
    
    def _calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics."""



        try:
            scores = []
            
            # Sharpness score (normalize laplacian variance)
            sharpness = metrics.get('sharpness', 0)
            sharpness_score = min(1.0, sharpness / 1000.0)
            scores.append(sharpness_score * 0.3)
            
            # Brightness score (optimal range 50-200)
            brightness = metrics.get('brightness', 128)
            brightness_score = 1.0 - abs(128 - brightness) / 128.0
            scores.append(brightness_score * 0.2)
            
            # Contrast score
            contrast = metrics.get('contrast', 0)
            contrast_score = min(1.0, contrast / 100.0)
            scores.append(contrast_score * 0.2)
            
            # Noise penalty
            noise = metrics.get('noise_level', 0)
            noise_penalty = min(0.3, noise / 100.0)
            
            # Compression artifacts penalty
            compression = metrics.get('compression_artifacts', 0)
            compression_penalty = compression * 0.2
            
            # Color diversity bonus (if available)
            hue_diversity = metrics.get('hue_diversity', 0.5)
            color_bonus = hue_diversity * 0.1
            
            # Calculate final score
            base_score = sum(scores)
            final_score = base_score - noise_penalty - compression_penalty + color_bonus
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            self.logger.warning(f"Quality score calculation failed: {str(e)}")
            return 0.5


class ImageAestheticAnalyzer:
    """Image aesthetic quality analysis using computer vision."""
    
    def __init__(self):
        """Initialize aesthetic analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_aesthetic_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze aesthetic properties of the image."""



        try:
            aesthetic_metrics = {}
            
            # Rule of thirds analysis
            aesthetic_metrics.update(self._analyze_composition(image))
            
            # Color harmony analysis
            aesthetic_metrics.update(self._analyze_color_harmony(image))
            
            # Symmetry and balance
            aesthetic_metrics.update(self._analyze_balance(image))
            
            # Depth and perspective
            aesthetic_metrics.update(self._analyze_depth(image))
            
            # Calculate overall aesthetic score
            overall_aesthetic = self._calculate_aesthetic_score(aesthetic_metrics)
            aesthetic_metrics['aesthetic_score'] = float(overall_aesthetic)
            
            return aesthetic_metrics
            
        except Exception as e:
            self.logger.warning(f"Aesthetic analysis failed: {str(e)}")
            return {'error': str(e), 'aesthetic_score': 0.5}
    
    def _analyze_composition(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze compositional elements."""



        try:
            h, w = image.shape[:2]
            
            # Rule of thirds analysis
            third_h, third_w = h // 3, w // 3
            
            # Extract interest points using corner detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            rule_of_thirds_score = 0.0
            if corners is not None:
                # Check alignment with rule of thirds lines
                thirds_lines_x = [third_w, 2 * third_w]
                thirds_lines_y = [third_h, 2 * third_h]
                
                for corner in corners:
                    x, y = corner.ravel()
                    
                    # Check proximity to rule of thirds intersections
                    for tx in thirds_lines_x:
                        for ty in thirds_lines_y:
                            distance = np.sqrt((x - tx)**2 + (y - ty)**2)
                            if distance < min(w, h) * 0.1:  # Within 10% of image size
                                rule_of_thirds_score += 1.0
                
                rule_of_thirds_score = min(1.0, rule_of_thirds_score / 10.0)
            
            # Leading lines detection (simplified)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            leading_lines_score = 0.0
            if lines is not None:
                # Analyze line orientations for compositional strength
                angles = []
                for line in lines[:10]:  # Analyze top 10 lines
                    rho, theta = line[0]
                    angles.append(theta)
                
                # Strong horizontal or vertical lines often improve composition
                angle_variety = len(set(np.round(np.array(angles), 1)))
                leading_lines_score = min(1.0, angle_variety / 5.0)
            
            return {
                'rule_of_thirds_score': float(rule_of_thirds_score),
                'leading_lines_score': float(leading_lines_score),
                'corners_detected': len(corners) if corners is not None else 0
            }
            
        except Exception as e:
            self.logger.warning(f"Composition analysis failed: {str(e)}")
            return {'rule_of_thirds_score': 0.5, 'leading_lines_score': 0.5}
    
    def _analyze_color_harmony(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze color harmony and palette."""



        try:
            if len(image.shape) != 3:
                return {'color_harmony_score': 0.5}
            
            # Convert to HSV for color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Extract dominant colors using k-means
            pixels = image.reshape(-1, 3).astype(np.float32)
            
            # Use k-means to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5  # Find top 5 colors
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Analyze color relationships
            dominant_colors = centers.astype(int)
            
            # Calculate color temperature consistency
            color_temps = []
            for color in dominant_colors:
                b, g, r = color
                temp = (r - b) / (r + b + 1e-6)
                color_temps.append(temp)
            
            temp_consistency = 1.0 - np.std(color_temps)
            
            # Analyze hue distribution
            hue_values = []
            for color in dominant_colors:
                bgr_color = np.uint8([[color]])
                hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)[0][0]
                hue_values.append(hsv_color[0])
            
            # Check for complementary colors
            complementary_score = 0.0
            for i, hue1 in enumerate(hue_values):
                for j, hue2 in enumerate(hue_values[i+1:], i+1):
                    hue_diff = abs(hue1 - hue2)
                    if 150 <= hue_diff <= 210:  # Complementary range
                        complementary_score += 1.0
            
            complementary_score = min(1.0, complementary_score / 5.0)
            
            # Overall color harmony
            harmony_score = (temp_consistency + complementary_score) / 2
            
            return {
                'color_harmony_score': float(max(0.0, min(1.0, harmony_score))),
                'dominant_colors_count': k,
                'temperature_consistency': float(temp_consistency),
                'complementary_score': float(complementary_score)
            }
            
        except Exception as e:
            self.logger.warning(f"Color harmony analysis failed: {str(e)}")
            return {'color_harmony_score': 0.5}
    
    def _analyze_balance(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze visual balance and symmetry."""



        try:
            h, w = image.shape[:2]
            
            # Convert to grayscale for balance analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Horizontal balance
            left_half = gray[:, :w//2]
            right_half = gray[:, w//2:]
            
            left_weight = np.sum(left_half)
            right_weight = np.sum(right_half)
            
            horizontal_balance = 1.0 - abs(left_weight - right_weight) / (left_weight + right_weight + 1e-6)
            
            # Vertical balance
            top_half = gray[:h//2, :]
            bottom_half = gray[h//2:, :]
            
            top_weight = np.sum(top_half)
            bottom_weight = np.sum(bottom_half)
            
            vertical_balance = 1.0 - abs(top_weight - bottom_weight) / (top_weight + bottom_weight + 1e-6)
            
            # Symmetry analysis
            flipped_horizontal = cv2.flip(gray, 1)
            flipped_vertical = cv2.flip(gray, 0)
            
            horizontal_symmetry = cv2.matchTemplate(gray, flipped_horizontal, cv2.TM_CCOEFF_NORMED)[0][0]
            vertical_symmetry = cv2.matchTemplate(gray, flipped_vertical, cv2.TM_CCOEFF_NORMED)[0][0]
            
            return {
                'horizontal_balance': float(horizontal_balance),
                'vertical_balance': float(vertical_balance),
                'horizontal_symmetry': float(max(0.0, horizontal_symmetry)),
                'vertical_symmetry': float(max(0.0, vertical_symmetry)),
                'overall_balance': float((horizontal_balance + vertical_balance) / 2)
            }
            
        except Exception as e:
            self.logger.warning(f"Balance analysis failed: {str(e)}")
            return {'overall_balance': 0.5}
    
    def _analyze_depth(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze depth and perspective cues."""



        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Blur gradient analysis (depth of field)
            blur_map = cv2.GaussianBlur(gray, (15, 15), 0)
            blur_difference = cv2.absdiff(gray, blur_map)
            
            # Areas with high blur difference suggest focus areas
            focus_areas = blur_difference > np.percentile(blur_difference, 80)
            focus_ratio = np.sum(focus_areas) / focus_areas.size
            
            # Perspective lines detection
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            perspective_score = 0.0
            if lines is not None:
                # Look for converging lines (perspective)
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angles.append(theta)
                
                # Check for perspective (converging lines)
                angle_variety = len(set(np.round(np.array(angles), 1)))
                perspective_score = min(1.0, angle_variety / 10.0)
            
            depth_score = (focus_ratio + perspective_score) / 2
            
            return {
                'depth_score': float(depth_score),
                'focus_ratio': float(focus_ratio),
                'perspective_score': float(perspective_score)
            }
            
        except Exception as e:
            self.logger.warning(f"Depth analysis failed: {str(e)}")
            return {'depth_score': 0.5}
    
    def _calculate_aesthetic_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall aesthetic score."""



        try:
            scores = []
            weights = []
            
            # Composition
            comp_score = (
                metrics.get('rule_of_thirds_score', 0.5) +
                metrics.get('leading_lines_score', 0.5)
            ) / 2
            scores.append(comp_score)
            weights.append(0.3)
            
            # Color harmony
            color_score = metrics.get('color_harmony_score', 0.5)
            scores.append(color_score)
            weights.append(0.25)
            
            # Balance
            balance_score = metrics.get('overall_balance', 0.5)
            scores.append(balance_score)
            weights.append(0.25)
            
            # Depth
            depth_score = metrics.get('depth_score', 0.5)
            scores.append(depth_score)
            weights.append(0.2)
            
            # Calculate weighted average
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            
            return weighted_sum / total_weight
            
        except Exception as e:
            self.logger.warning(f"Aesthetic score calculation failed: {str(e)}")
            return 0.5


class ImageDuplicateDetector:
    """Image duplicate detection using perceptual hashing."""
    
    def __init__(self):
        """Initialize duplicate detector."""
        self.logger = logging.getLogger(__name__)
        self.hash_cache = {}
    
    def generate_perceptual_hashes(self, image: np.ndarray) -> Dict[str, str]:
        """Generate multiple perceptual hashes for robust duplicate detection."""



        try:
            # Convert to PIL Image
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image)
            
            hashes = {}
            
            if HAS_IMAGE_LIBS:
                # Different hash algorithms for robust detection
                hashes['average_hash'] = str(imagehash.average_hash(pil_image))
                hashes['perceptual_hash'] = str(imagehash.phash(pil_image))
                hashes['difference_hash'] = str(imagehash.dhash(pil_image))
                hashes['wavelet_hash'] = str(imagehash.whash(pil_image))
            else:
                # Fallback: simple hash based on image statistics
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
                
                # Resize for consistent hashing
                resized = cv2.resize(gray, (32, 32))
                
                # Create hash from pixel intensities
                pixel_hash = hashlib.md5(resized.tobytes()).hexdigest()[:16]
                hashes['fallback_hash'] = pixel_hash
            
            return hashes
            
        except Exception as e:
            self.logger.warning(f"Hash generation failed: {str(e)}")
            return {'error': str(e)}
    
    def calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two perceptual hashes."""



        try:
            if len(hash1) != len(hash2):
                return 0.0
            
            # Hamming distance for perceptual hashes
            differences = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
            similarity = 1.0 - (differences / len(hash1))
            
            return similarity
            
        except Exception as e:
            self.logger.warning(f"Similarity calculation failed: {str(e)}")
            return 0.0


class ImageContentFilter:
    """Enterprise-grade image content filter."""
    
    def __init__(self, config: ImageFilterConfig):
        """Initialize image content filter."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.quality_analyzer = ImageQualityAnalyzer()
        self.aesthetic_analyzer = ImageAestheticAnalyzer()
        self.duplicate_detector = ImageDuplicateDetector()
        
        self.logger.info("Image content filter initialized")
    
    async def filter_async(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Asynchronously filter image content."""



        return await asyncio.get_event_loop().run_in_executor(
            None, self.filter, content, ai_validation, strict_mode
        )
    
    def filter(
        self,
        content: ContentItem,
        ai_validation: bool = True,
        strict_mode: bool = False
    ) -> FilterResponse:
        """Filter image content with comprehensive analysis."""
        start_time = time.time()
        
        try:
            if not HAS_IMAGE_LIBS:
                return FilterResponse(
                    filter_type=FilterType.IMAGE,
                    result=FilterResult.WARNING,
                    score=0.5,
                    confidence=0.0,
                    metadata={'error': 'Image processing libraries not available'},
                    processing_time=time.time() - start_time,
                    warnings=['Image libraries not installed']
                )
            
            # Load and validate image
            image_data, metadata = self._load_image_content(content)
            
            if image_data is None:
                return FilterResponse(
                    filter_type=FilterType.IMAGE,
                    result=FilterResult.FAILED,
                    score=0.0,
                    confidence=1.0,
                    metadata={'error': 'Failed to load image content'},
                    processing_time=time.time() - start_time,
                    errors=['Image loading failed']
                )
            
            # Perform comprehensive image analysis
            analysis_results = self._analyze_image_content(
                image_data, ai_validation, strict_mode
            )
            
            # Calculate overall score and result
            overall_score = self._calculate_overall_score(analysis_results, strict_mode)
            result = self._determine_filter_result(overall_score, analysis_results, strict_mode)
            
            # Prepare response
            response = FilterResponse(
                filter_type=FilterType.IMAGE,
                result=result,
                score=overall_score,
                confidence=analysis_results.get('confidence', 0.85),
                metadata={
                    'image_properties': metadata,
                    'quality_analysis': analysis_results.get('quality', {}),
                    'aesthetic_analysis': analysis_results.get('aesthetic', {}),
                    'duplicate_analysis': analysis_results.get('duplicate', {}),
                    'ai_validation_enabled': ai_validation,
                    'strict_mode': strict_mode
                },
                processing_time=time.time() - start_time,
                warnings=analysis_results.get('warnings', []),
                errors=analysis_results.get('errors', [])
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Image filtering failed: {str(e)}")
            return FilterResponse(
                filter_type=FilterType.IMAGE,
                result=FilterResult.FAILED,
                score=0.0,
                confidence=0.0,
                metadata={'error': str(e)},
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    def _load_image_content(self, content: ContentItem) -> Tuple[Optional[np.ndarray], Dict[str, Any]]:
        """Load and validate image content."""



        try:
            metadata = {}
            
            if content.file_path:
                # Load from file
                image = cv2.imread(content.file_path)
                
                if image is None:
                    self.logger.error(f"Failed to load image file: {content.file_path}")
                    return None, {'error': 'Failed to load image file'}
                
                # Get image properties
                height, width = image.shape[:2]
                channels = image.shape[2] if len(image.shape) == 3 else 1
                
                # Get file metadata
                file_path = Path(content.file_path)
                file_size = file_path.stat().st_size
                
                metadata.update({
                    'filename': file_path.name,
                    'extension': file_path.suffix.lower(),
                    'file_size': file_size,
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'resolution': (width, height)
                })
                
            elif isinstance(content.content_data, bytes):
                # Load from bytes
                nparr = np.frombuffer(content.content_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    self.logger.error("Failed to decode image from bytes")
                    return None, {'error': 'Failed to decode image data'}
                
                height, width = image.shape[:2]
                channels = image.shape[2] if len(image.shape) == 3 else 1
                
                metadata.update({
                    'data_size': len(content.content_data),
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'resolution': (width, height)
                })
                
            else:
                self.logger.error("Unsupported image content format")
                return None, {'error': 'Unsupported image format'}
            
            # Validate against config constraints
            if width < self.config.min_resolution[0] or height < self.config.min_resolution[1]:
                metadata['validation_error'] = f"Resolution {width}x{height} below minimum {self.config.min_resolution}"
                return None, metadata
            
            if width > self.config.max_resolution[0] or height > self.config.max_resolution[1]:
                metadata['validation_warning'] = f"Resolution {width}x{height} exceeds maximum {self.config.max_resolution}"
            
            file_size = metadata.get('file_size') or metadata.get('data_size', 0)
            if file_size < self.config.min_file_size:
                metadata['validation_error'] = f"File size {file_size} below minimum {self.config.min_file_size}"
                return None, metadata
            
            if file_size > self.config.max_file_size:
                metadata['validation_warning'] = f"File size {file_size} exceeds maximum {self.config.max_file_size}"
            
            return image, metadata
            
        except Exception as e:
            self.logger.error(f"Image loading failed: {str(e)}")
            return None, {'error': str(e)}
    
    def _analyze_image_content(
        self,
        image: np.ndarray,
        ai_validation: bool,
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Perform comprehensive image content analysis."""
        analysis_results = {
            'warnings': [],
            'errors': [],
            'confidence': 0.85
        }
        
        try:
            # Quality analysis
            analysis_results['quality'] = self.quality_analyzer.analyze_image_quality(image)
            
            # Aesthetic analysis
            if self.config.enable_aesthetic_scoring and ai_validation:
                analysis_results['aesthetic'] = self.aesthetic_analyzer.analyze_aesthetic_quality(image)
            
            # Duplicate detection
            if self.config.enable_duplicate_detection:
                analysis_results['duplicate'] = self._analyze_duplicates(image)
            
            # Object detection (simplified)
            if self.config.enable_object_detection and ai_validation:
                analysis_results['objects'] = self._detect_objects(image)
            
            # NSFW detection (placeholder)
            if self.config.enable_nsfw_detection and ai_validation:
                analysis_results['nsfw'] = self._detect_nsfw_content(image)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {str(e)}")
            analysis_results['errors'].append(str(e))
            analysis_results['confidence'] = 0.0
            return analysis_results
    
    def _analyze_duplicates(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image for duplicates."""



        try:
            hashes = self.duplicate_detector.generate_perceptual_hashes(image)
            
            # In a real implementation, compare against database of known hashes
            # For now, just return the generated hashes
            return {
                'hashes': hashes,
                'is_duplicate': False,  # Placeholder
                'similarity_scores': {},
                'confidence': 0.8
            }
            
        except Exception as e:
            self.logger.warning(f"Duplicate analysis failed: {str(e)}")
            return {'error': str(e), 'is_duplicate': False}
    
    def _detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect objects in the image."""



        try:
            # Simplified object detection using OpenCV
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Use Haar cascades for basic object detection
            objects_detected = []
            
            # Face detection
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                
                for (x, y, w, h) in faces:
                    objects_detected.append({
                        'type': 'face',
                        'x': int(x), 'y': int(y),
                        'width': int(w), 'height': int(h),
                        'confidence': 0.8
                    })
            except Exception:
                pass
            
            return {
                'objects': objects_detected,
                'object_count': len(objects_detected),
                'detection_confidence': 0.7 if objects_detected else 0.3
            }
            
        except Exception as e:
            self.logger.warning(f"Object detection failed: {str(e)}")
            return {'error': str(e), 'object_count': 0}
    
    def _detect_nsfw_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect NSFW content in the image."""



        try:
            # Placeholder for NSFW detection
            # In real implementation, use specialized models like Yahoo's OpenNSFW
            
            # Simple heuristic based on skin color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 48, 80])
            upper_skin = np.array([20, 255, 255])
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_ratio = np.sum(skin_mask > 0) / skin_mask.size
            
            # Very simple classification
            nsfw_score = min(1.0, skin_ratio * 2.0)  # Normalize
            
            return {
                'nsfw_score': float(nsfw_score),
                'is_nsfw': nsfw_score > self.config.nsfw_threshold,
                'skin_ratio': float(skin_ratio),
                'confidence': 0.5  # Low confidence for this simple method
            }
            
        except Exception as e:
            self.logger.warning(f"NSFW detection failed: {str(e)}")
            return {'error': str(e), 'is_nsfw': False, 'confidence': 0.0}
    
    def _calculate_overall_score(self, analysis_results: Dict[str, Any], strict_mode: bool) -> float:
        """Calculate overall image filter score."""
        scores = []
        weights = []
        
        # Quality score
        quality_score = analysis_results.get('quality', {}).get('overall_score')
        if quality_score is not None:
            scores.append(quality_score)
            weights.append(0.4)
        
        # Aesthetic score
        aesthetic_score = analysis_results.get('aesthetic', {}).get('aesthetic_score')
        if aesthetic_score is not None:
            scores.append(aesthetic_score)
            weights.append(0.3)
        
        # Object detection confidence
        object_confidence = analysis_results.get('objects', {}).get('detection_confidence', 0.0)
        if object_confidence > 0:
            scores.append(object_confidence)
            weights.append(0.2)
        
        # NSFW penalty
        nsfw_data = analysis_results.get('nsfw', {})
        if nsfw_data.get('is_nsfw'):
            nsfw_penalty = nsfw_data.get('nsfw_score', 0.0)
            scores.append(1.0 - nsfw_penalty)  # Invert NSFW score
            weights.append(0.1 if strict_mode else 0.05)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(s * w for s, w in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight
        
        return 0.5  # Default neutral score
    
    def _determine_filter_result(
        self,
        overall_score: float,
        analysis_results: Dict[str, Any],
        strict_mode: bool
    ) -> FilterResult:
        """Determine filter result based on analysis."""
        # Check for blocking conditions
        nsfw_data = analysis_results.get('nsfw', {})
        if nsfw_data.get('is_nsfw') and nsfw_data.get('confidence', 0) > 0.7:
            return FilterResult.BLOCKED
        
        # Quality thresholds
        quality_data = analysis_results.get('quality', {})
        quality_score = quality_data.get('overall_score', 1.0)
        
        if quality_score < 0.3:  # Very poor quality
            return FilterResult.WARNING if not strict_mode else FilterResult.FAILED
        
        # Overall score thresholds
        if strict_mode:
            if overall_score >= 0.8:
                return FilterResult.PASSED
            elif overall_score >= 0.6:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
        else:
            if overall_score >= 0.6:
                return FilterResult.PASSED
            elif overall_score >= 0.4:
                return FilterResult.WARNING
            else:
                return FilterResult.FAILED
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on image filter."""
        health_status = {
            'status': 'healthy',
            'libraries': {
                'opencv': HAS_IMAGE_LIBS,
                'pillow': HAS_IMAGE_LIBS,
                'imagehash': HAS_IMAGE_LIBS,
                'numpy': True
            },
            'config': {
                'aesthetic_scoring': self.config.enable_aesthetic_scoring,
                'object_detection': self.config.enable_object_detection,
                'nsfw_detection': self.config.enable_nsfw_detection,
                'duplicate_detection': self.config.enable_duplicate_detection,
                'supported_formats': len(self.config.supported_formats)
            }
        }
        
        if not HAS_IMAGE_LIBS:
            health_status['status'] = 'warning'
            health_status['message'] = 'Image processing libraries not available'
        
        return health_status
