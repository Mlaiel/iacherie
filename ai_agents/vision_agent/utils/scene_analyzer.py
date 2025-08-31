"""
Scene Analyzer - Enterprise Scene Understanding & Context Analysis
==================================================================

Advanced scene analysis system with AI-powered content understanding,
context recognition, and semantic analysis for visual content.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import torch
import torchvision.transforms as transforms
from PIL import Image
import json
from collections import Counter, defaultdict

from ..base import BaseAgent, AgentStatus
try:
    from core.exceptions import SceneAnalysisError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SceneAnalysisError, ValidationError = globals().get('SceneAnalysisError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class SceneCategory:
    """Scene categories for classification"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    URBAN = "urban"
    NATURE = "nature"
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    ARTISTIC = "artistic"
    SOCIAL = "social"
    PROFESSIONAL = "professional"
    ENTERTAINMENT = "entertainment"

class SceneAnalyzer(BaseAgent):
    """
    Enterprise-grade scene analysis system providing comprehensive
    scene understanding, context recognition, and semantic analysis.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="scene_analyzer",
            name="Scene Analyzer",
            version="2.1.0"
        )
        
        self.performance_monitor = PerformanceMonitor("scene_analysis")
        
        # Scene analysis configuration
        self.confidence_threshold = 0.6
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Scene classification categories
        self.scene_categories = {
            SceneCategory.INDOOR: [
                'living_room', 'kitchen', 'bedroom', 'bathroom', 'office',
                'restaurant', 'store', 'library', 'gym', 'studio'
            ],
            SceneCategory.OUTDOOR: [
                'park', 'street', 'beach', 'mountain', 'forest', 'garden',
                'parking_lot', 'playground', 'stadium', 'bridge'
            ],
            SceneCategory.URBAN: [
                'city_center', 'building', 'skyscraper', 'street', 'plaza',
                'shopping_center', 'bus_stop', 'subway', 'traffic'
            ],
            SceneCategory.NATURE: [
                'forest', 'mountain', 'beach', 'lake', 'river', 'field',
                'desert', 'sky', 'sunset', 'sunrise'
            ]
        }
        
        # Content creation contexts
        self.creative_contexts = {
            'photography_session': ['studio', 'portrait', 'fashion', 'product'],
            'video_production': ['filming', 'interview', 'presentation', 'performance'],
            'social_media': ['selfie', 'group_photo', 'lifestyle', 'travel'],
            'commercial': ['advertising', 'product_showcase', 'branding', 'promotional'],
            'artistic': ['creative', 'artistic', 'conceptual', 'experimental']
        }
        
        # Lighting conditions
        self.lighting_types = [
            'natural_daylight', 'artificial_indoor', 'golden_hour', 'blue_hour',
            'harsh_sunlight', 'soft_diffused', 'dramatic', 'low_light', 'backlit'
        ]
        
        # Composition analysis parameters
        self.composition_rules = [
            'rule_of_thirds', 'leading_lines', 'symmetry', 'framing',
            'depth_of_field', 'perspective', 'balance', 'contrast'
        ]

    async def initialize(self) -> bool:
        """Initialize scene analysis components"""
        try:
            logger.info("Initializing Scene Analyzer...")
            
            # Initialize color analysis
            self.color_analyzer = await self._initialize_color_analyzer()
            
            # Initialize texture analysis
            self.texture_analyzer = await self._initialize_texture_analyzer()
            
            # Initialize composition analyzer
            self.composition_analyzer = await self._initialize_composition_analyzer()
            
            # Initialize preprocessing transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            self.status = AgentStatus.READY
            logger.info("Scene Analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Scene Analyzer initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def _initialize_color_analyzer(self) -> Dict[str, Any]:
        """Initialize color analysis components"""
        return {
            'dominant_colors_count': 5,
            'color_harmony_types': ['complementary', 'triadic', 'analogous', 'monochromatic'],
            'color_temperature_ranges': {
                'very_warm': (2000, 3000),
                'warm': (3000, 4000),
                'neutral': (4000, 5500),
                'cool': (5500, 7000),
                'very_cool': (7000, 10000)
            }
        }

    async def _initialize_texture_analyzer(self) -> Dict[str, Any]:
        """Initialize texture analysis components"""
        return {
            'texture_features': ['smoothness', 'roughness', 'regularity', 'directionality'],
            'texture_patterns': ['uniform', 'random', 'structured', 'organic']
        }

    async def _initialize_composition_analyzer(self) -> Dict[str, Any]:
        """Initialize composition analysis components"""
        return {
            'grid_divisions': (3, 3),  # Rule of thirds grid
            'balance_threshold': 0.3,
            'symmetry_threshold': 0.8
        }

    async def analyze_scene(
        self, 
        image: np.ndarray,
        include_detailed_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive scene analysis
        
        Args:
            image: Input image as numpy array
            include_detailed_analysis: Include detailed compositional analysis
            
        Returns:
            Complete scene analysis results
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting comprehensive scene analysis...")
            
            # Validate input
            if image is None or image.size == 0:
                raise ValidationError("Invalid input image")
            
            # Basic scene classification
            scene_classification = await self._classify_scene(image)
            
            # Lighting analysis
            lighting_analysis = await self._analyze_lighting(image)
            
            # Color analysis
            color_analysis = await self._analyze_colors(image)
            
            # Texture analysis
            texture_analysis = await self._analyze_texture(image)
            
            # Object and content detection
            content_analysis = await self._analyze_content(image)
            
            # Context recognition
            context_analysis = await self._recognize_context(image, content_analysis)
            
            # Detailed analysis if requested
            detailed_analysis = {}
            if include_detailed_analysis:
                detailed_analysis = await self._perform_detailed_analysis(image)
            
            # Quality assessment for content creation
            creation_quality = await self._assess_creation_quality(image, lighting_analysis, color_analysis)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'image_dimensions': image.shape,
                'scene_classification': scene_classification,
                'lighting_analysis': lighting_analysis,
                'color_analysis': color_analysis,
                'texture_analysis': texture_analysis,
                'content_analysis': content_analysis,
                'context_analysis': context_analysis,
                'creation_quality': creation_quality,
                'detailed_analysis': detailed_analysis,
                'scene_summary': await self._generate_scene_summary(
                    scene_classification, lighting_analysis, color_analysis, content_analysis
                )
            }
            
            logger.info(f"Scene analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Scene analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    async def _classify_scene(self, image: np.ndarray) -> Dict[str, Any]:
        """Classify scene into categories"""
        try:
            # Basic scene classification using image features
            classification_result = {
                'primary_category': SceneCategory.INDOOR,
                'confidence': 0.5,
                'secondary_categories': [],
                'specific_scene': 'unknown',
                'scene_complexity': 'medium'
            }
            
            # Analyze basic image characteristics
            height, width = image.shape[:2]
            
            # Color distribution analysis for scene type
            if len(image.shape) == 3:
                # Convert to HSV for better color analysis
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                
                # Analyze dominant colors
                dominant_hues = await self._extract_dominant_hues(hsv)
                
                # Simple heuristic classification
                if self._contains_sky_colors(dominant_hues):
                    classification_result['primary_category'] = SceneCategory.OUTDOOR
                    classification_result['confidence'] = 0.7
                    
                    if self._contains_nature_colors(dominant_hues):
                        classification_result['secondary_categories'].append(SceneCategory.NATURE)
                        classification_result['specific_scene'] = 'natural_landscape'
                    else:
                        classification_result['secondary_categories'].append(SceneCategory.URBAN)
                        classification_result['specific_scene'] = 'urban_scene'
                
                elif self._contains_indoor_indicators(image):
                    classification_result['primary_category'] = SceneCategory.INDOOR
                    classification_result['confidence'] = 0.6
                    classification_result['specific_scene'] = 'indoor_space'
            
            # Scene complexity based on edge density
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density > 0.15:
                classification_result['scene_complexity'] = 'high'
            elif edge_density > 0.08:
                classification_result['scene_complexity'] = 'medium'
            else:
                classification_result['scene_complexity'] = 'low'
            
            return classification_result
            
        except Exception as e:
            logger.error(f"Scene classification failed: {e}")
            return {'primary_category': 'unknown', 'confidence': 0.0}

    async def _extract_dominant_hues(self, hsv_image: np.ndarray) -> List[int]:
        """Extract dominant hue values from HSV image"""
        try:
            # Calculate hue histogram
            hist = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
            
            # Find peaks in histogram
            hist_smooth = cv2.GaussianBlur(hist.flatten(), (15,), 0)
            peaks = []
            
            for i in range(1, len(hist_smooth) - 1):
                if (hist_smooth[i] > hist_smooth[i-1] and 
                    hist_smooth[i] > hist_smooth[i+1] and 
                    hist_smooth[i] > np.mean(hist_smooth) * 1.5):
                    peaks.append(i)
            
            return peaks[:5]  # Return top 5 dominant hues
            
        except Exception as e:
            logger.error(f"Dominant hue extraction failed: {e}")
            return []

    def _contains_sky_colors(self, dominant_hues: List[int]) -> bool:
        """Check if dominant hues contain sky-like colors"""
        # Sky hues in HSV: blue range (100-130), light blue (80-120)
        sky_hue_ranges = [(80, 130)]
        
        for hue in dominant_hues:
            for start, end in sky_hue_ranges:
                if start <= hue <= end:
                    return True
        return False

    def _contains_nature_colors(self, dominant_hues: List[int]) -> bool:
        """Check if dominant hues contain nature-like colors"""
        # Nature hues: green (40-80), brown (10-25), earth tones
        nature_hue_ranges = [(40, 80), (10, 25)]
        
        for hue in dominant_hues:
            for start, end in nature_hue_ranges:
                if start <= hue <= end:
                    return True
        return False

    def _contains_indoor_indicators(self, image: np.ndarray) -> bool:
        """Check for indoor scene indicators"""
        try:
            # Simple heuristics for indoor detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Look for straight lines (walls, furniture)
            lines = cv2.HoughLines(cv2.Canny(gray, 50, 150), 1, np.pi/180, threshold=100)
            
            if lines is not None and len(lines) > 10:
                return True
            
            # Check brightness distribution (indoor often more uniform)
            brightness_std = np.std(gray)
            if brightness_std < 40:  # Uniform lighting
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Indoor indicator detection failed: {e}")
            return False

    async def _analyze_lighting(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze lighting conditions in the scene"""
        try:
            # Convert to different color spaces for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            else:
                gray = image
                lab = None
            
            lighting_analysis = {
                'brightness_level': 'medium',
                'lighting_type': 'unknown',
                'contrast_level': 'medium',
                'shadow_presence': 'moderate',
                'highlight_presence': 'moderate',
                'lighting_direction': 'unknown',
                'color_temperature': 'neutral',
                'lighting_quality': 'good'
            }
            
            # Brightness analysis
            mean_brightness = np.mean(gray)
            if mean_brightness > 180:
                lighting_analysis['brightness_level'] = 'high'
            elif mean_brightness > 80:
                lighting_analysis['brightness_level'] = 'medium'
            else:
                lighting_analysis['brightness_level'] = 'low'
            
            # Contrast analysis
            contrast = gray.std()
            if contrast > 60:
                lighting_analysis['contrast_level'] = 'high'
            elif contrast > 30:
                lighting_analysis['contrast_level'] = 'medium'
            else:
                lighting_analysis['contrast_level'] = 'low'
            
            # Shadow and highlight detection
            shadow_pixels = np.sum(gray < 50) / gray.size
            highlight_pixels = np.sum(gray > 200) / gray.size
            
            if shadow_pixels > 0.2:
                lighting_analysis['shadow_presence'] = 'strong'
            elif shadow_pixels > 0.1:
                lighting_analysis['shadow_presence'] = 'moderate'
            else:
                lighting_analysis['shadow_presence'] = 'minimal'
            
            if highlight_pixels > 0.1:
                lighting_analysis['highlight_presence'] = 'strong'
            elif highlight_pixels > 0.05:
                lighting_analysis['highlight_presence'] = 'moderate'
            else:
                lighting_analysis['highlight_presence'] = 'minimal'
            
            # Lighting quality assessment
            if (lighting_analysis['contrast_level'] == 'high' and
                lighting_analysis['shadow_presence'] != 'strong' and
                lighting_analysis['highlight_presence'] != 'strong'):
                lighting_analysis['lighting_quality'] = 'excellent'
            elif lighting_analysis['contrast_level'] == 'medium':
                lighting_analysis['lighting_quality'] = 'good'
            else:
                lighting_analysis['lighting_quality'] = 'poor'
            
            # Color temperature estimation (if color image)
            if lab is not None:
                a_channel = lab[:,:,1]
                b_channel = lab[:,:,2]
                
                avg_a = np.mean(a_channel)
                avg_b = np.mean(b_channel)
                
                if avg_b > 135:  # Yellowish
                    lighting_analysis['color_temperature'] = 'warm'
                elif avg_b < 125:  # Bluish
                    lighting_analysis['color_temperature'] = 'cool'
                else:
                    lighting_analysis['color_temperature'] = 'neutral'
            
            return lighting_analysis
            
        except Exception as e:
            logger.error(f"Lighting analysis failed: {e}")
            return {'lighting_quality': 'unknown'}

    async def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color composition and harmony"""
        try:
            if len(image.shape) != 3:
                return {'error': 'Color analysis requires RGB image'}
            
            color_analysis = {
                'dominant_colors': [],
                'color_harmony': 'unknown',
                'color_diversity': 0.0,
                'saturation_level': 'medium',
                'color_temperature': 'neutral',
                'color_balance': 'balanced'
            }
            
            # Extract dominant colors using K-means
            dominant_colors = await self._extract_dominant_colors(image, k=5)
            color_analysis['dominant_colors'] = dominant_colors
            
            # Calculate color diversity
            diversity = await self._calculate_color_diversity(image)
            color_analysis['color_diversity'] = diversity
            
            # Analyze saturation
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mean_saturation = np.mean(hsv[:,:,1])
            
            if mean_saturation > 150:
                color_analysis['saturation_level'] = 'high'
            elif mean_saturation > 80:
                color_analysis['saturation_level'] = 'medium'
            else:
                color_analysis['saturation_level'] = 'low'
            
            # Color harmony analysis (simplified)
            if len(dominant_colors) >= 2:
                harmony = await self._analyze_color_harmony(dominant_colors)
                color_analysis['color_harmony'] = harmony
            
            return color_analysis
            
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            return {'color_harmony': 'unknown'}

    async def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Extract dominant colors using K-means clustering"""
        try:
            # Reshape image to list of pixels
            pixels = image.reshape(-1, 3)
            
            # Use simple histogram-based approach instead of K-means for efficiency
            # Calculate histogram for each channel
            hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
            
            # Find peaks in each channel
            dominant_colors = []
            
            # Simple dominant color extraction
            mean_color = np.mean(pixels, axis=0)
            dominant_colors.append({
                'color': [int(c) for c in mean_color],
                'percentage': 100.0 / k,
                'hex': f"#{int(mean_color[2]):02x}{int(mean_color[1]):02x}{int(mean_color[0]):02x}"
            })
            
            return dominant_colors[:k]
            
        except Exception as e:
            logger.error(f"Dominant color extraction failed: {e}")
            return []

    async def _calculate_color_diversity(self, image: np.ndarray) -> float:
        """Calculate color diversity score"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Calculate histogram for hue channel
            hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_norm = hist / np.sum(hist)
            
            # Calculate entropy as measure of diversity
            entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-7))
            
            # Normalize to 0-1 range
            max_entropy = np.log2(180)
            diversity_score = entropy / max_entropy
            
            return float(diversity_score)
            
        except Exception as e:
            logger.error(f"Color diversity calculation failed: {e}")
            return 0.5

    async def _analyze_color_harmony(self, dominant_colors: List[Dict]) -> str:
        """Analyze color harmony type"""
        try:
            if len(dominant_colors) < 2:
                return 'monochromatic'
            
            # Simple harmony detection based on hue differences
            # This is a simplified version - real color harmony analysis is complex
            
            # Extract hue values (convert RGB to HSV)
            hues = []
            for color_info in dominant_colors[:3]:  # Use top 3 colors
                rgb = color_info['color']
                rgb_normalized = np.array(rgb).reshape(1, 1, 3).astype(np.uint8)
                hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_BGR2HSV)
                hue = hsv[0, 0, 0]
                hues.append(hue)
            
            if len(hues) >= 2:
                hue_diff = abs(hues[0] - hues[1])
                
                # Complementary colors (opposite hues)
                if 160 <= hue_diff <= 200 or hue_diff <= 20:
                    return 'complementary'
                # Analogous colors (similar hues)
                elif hue_diff <= 60:
                    return 'analogous'
                # Triadic colors
                elif len(hues) >= 3:
                    return 'triadic'
                else:
                    return 'contrasting'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Color harmony analysis failed: {e}")
            return 'unknown'

    async def _analyze_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze texture patterns in the scene"""
        try:
            # Convert to grayscale for texture analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            texture_analysis = {
                'texture_complexity': 'medium',
                'dominant_patterns': [],
                'texture_uniformity': 0.5,
                'roughness_level': 'medium'
            }
            
            # Calculate texture using Local Binary Patterns
            from skimage import feature
            
            # LBP for texture analysis
            lbp = feature.local_binary_pattern(gray, P=8, R=1, method='uniform')
            
            # Calculate texture uniformity
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10)
            lbp_hist = lbp_hist / np.sum(lbp_hist)
            uniformity = 1.0 - np.std(lbp_hist)
            texture_analysis['texture_uniformity'] = float(uniformity)
            
            # Texture complexity based on gradient
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            complexity = np.std(gradient_magnitude) / np.mean(gradient_magnitude + 1e-6)
            
            if complexity > 1.5:
                texture_analysis['texture_complexity'] = 'high'
            elif complexity > 0.8:
                texture_analysis['texture_complexity'] = 'medium'
            else:
                texture_analysis['texture_complexity'] = 'low'
            
            return texture_analysis
            
        except Exception as e:
            logger.error(f"Texture analysis failed: {e}")
            return {'texture_complexity': 'unknown'}

    async def _analyze_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze content elements in the scene"""
        try:
            content_analysis = {
                'estimated_object_count': 0,
                'human_presence': False,
                'text_presence': False,
                'brand_elements': False,
                'content_density': 'medium',
                'focus_areas': []
            }
            
            # Simple object counting using contour detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Edge detection for object estimation
            edges = cv2.Canny(gray, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size
            significant_contours = [c for c in contours if cv2.contourArea(c) > 500]
            content_analysis['estimated_object_count'] = len(significant_contours)
            
            # Content density based on edge density
            edge_density = np.sum(edges > 0) / edges.size
            if edge_density > 0.15:
                content_analysis['content_density'] = 'high'
            elif edge_density > 0.08:
                content_analysis['content_density'] = 'medium'
            else:
                content_analysis['content_density'] = 'low'
            
            # Simple human presence detection (using face cascade as proxy)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            content_analysis['human_presence'] = len(faces) > 0
            
            return content_analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {'estimated_object_count': 0}

    async def _recognize_context(self, image: np.ndarray, content_analysis: Dict) -> Dict[str, Any]:
        """Recognize scene context and purpose"""
        try:
            context_analysis = {
                'likely_context': 'general',
                'confidence': 0.5,
                'creative_potential': 'medium',
                'commercial_viability': 'medium',
                'social_media_suitability': 'good'
            }
            
            # Context recognition based on content analysis
            if content_analysis.get('human_presence', False):
                if content_analysis.get('estimated_object_count', 0) > 10:
                    context_analysis['likely_context'] = 'social_event'
                    context_analysis['social_media_suitability'] = 'excellent'
                else:
                    context_analysis['likely_context'] = 'portrait_session'
                    context_analysis['creative_potential'] = 'high'
            
            elif content_analysis.get('content_density') == 'high':
                context_analysis['likely_context'] = 'commercial_scene'
                context_analysis['commercial_viability'] = 'high'
            
            elif content_analysis.get('content_density') == 'low':
                context_analysis['likely_context'] = 'artistic_composition'
                context_analysis['creative_potential'] = 'high'
            
            return context_analysis
            
        except Exception as e:
            logger.error(f"Context recognition failed: {e}")
            return {'likely_context': 'unknown'}

    async def _perform_detailed_analysis(self, image: np.ndarray) -> Dict[str, Any]:
        """Perform detailed compositional analysis"""
        try:
            detailed_analysis = {
                'composition_rules': {},
                'visual_balance': 'unknown',
                'depth_perception': 'medium',
                'focal_points': [],
                'aesthetic_score': 0.5
            }
            
            # Rule of thirds analysis
            rule_of_thirds = await self._analyze_rule_of_thirds(image)
            detailed_analysis['composition_rules']['rule_of_thirds'] = rule_of_thirds
            
            # Visual balance analysis
            balance = await self._analyze_visual_balance(image)
            detailed_analysis['visual_balance'] = balance
            
            # Simple aesthetic score calculation
            aesthetic_factors = [
                rule_of_thirds.get('adherence_score', 0.5),
                0.7 if balance == 'balanced' else 0.3
            ]
            detailed_analysis['aesthetic_score'] = np.mean(aesthetic_factors)
            
            return detailed_analysis
            
        except Exception as e:
            logger.error(f"Detailed analysis failed: {e}")
            return {'aesthetic_score': 0.5}

    async def _analyze_rule_of_thirds(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze adherence to rule of thirds"""
        try:
            height, width = image.shape[:2]
            
            # Define rule of thirds grid
            third_h = height // 3
            third_w = width // 3
            
            intersection_points = [
                (third_w, third_h), (2*third_w, third_h),
                (third_w, 2*third_h), (2*third_w, 2*third_h)
            ]
            
            # Analyze interest points near intersections
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=20, qualityLevel=0.01, minDistance=50)
            
            adherence_score = 0.5  # Default score
            
            if corners is not None:
                # Calculate how many corners are near intersection points
                near_intersections = 0
                for corner in corners:
                    x, y = corner.ravel()
                    for int_x, int_y in intersection_points:
                        if abs(x - int_x) < width * 0.1 and abs(y - int_y) < height * 0.1:
                            near_intersections += 1
                            break
                
                adherence_score = min(near_intersections / 4.0, 1.0)
            
            return {
                'adherence_score': adherence_score,
                'intersection_points': intersection_points,
                'interest_points_count': len(corners) if corners is not None else 0
            }
            
        except Exception as e:
            logger.error(f"Rule of thirds analysis failed: {e}")
            return {'adherence_score': 0.5}

    async def _analyze_visual_balance(self, image: np.ndarray) -> str:
        """Analyze visual balance in the image"""
        try:
            # Simple balance analysis based on weight distribution
            height, width = image.shape[:2]
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Calculate weight distribution (left vs right)
            left_half = gray[:, :width//2]
            right_half = gray[:, width//2:]
            
            left_weight = np.sum(left_half)
            right_weight = np.sum(right_half)
            
            balance_ratio = abs(left_weight - right_weight) / max(left_weight, right_weight)
            
            if balance_ratio < 0.2:
                return 'balanced'
            elif balance_ratio < 0.4:
                return 'slightly_unbalanced'
            else:
                return 'unbalanced'
            
        except Exception as e:
            logger.error(f"Visual balance analysis failed: {e}")
            return 'unknown'

    async def _assess_creation_quality(
        self, 
        image: np.ndarray, 
        lighting_analysis: Dict, 
        color_analysis: Dict
    ) -> Dict[str, Any]:
        """Assess quality for content creation purposes"""
        try:
            creation_quality = {
                'overall_rating': 'good',
                'technical_score': 0.7,
                'creative_score': 0.6,
                'commercial_score': 0.5,
                'improvements_suggested': []
            }
            
            # Technical quality factors
            technical_factors = []
            
            # Lighting quality
            lighting_quality = lighting_analysis.get('lighting_quality', 'good')
            if lighting_quality == 'excellent':
                technical_factors.append(0.9)
            elif lighting_quality == 'good':
                technical_factors.append(0.7)
            else:
                technical_factors.append(0.4)
                creation_quality['improvements_suggested'].append('Improve lighting conditions')
            
            # Color diversity
            color_diversity = color_analysis.get('color_diversity', 0.5)
            technical_factors.append(color_diversity)
            
            if color_diversity < 0.3:
                creation_quality['improvements_suggested'].append('Add more color variety')
            
            creation_quality['technical_score'] = np.mean(technical_factors)
            
            # Overall rating
            if creation_quality['technical_score'] > 0.8:
                creation_quality['overall_rating'] = 'excellent'
            elif creation_quality['technical_score'] > 0.6:
                creation_quality['overall_rating'] = 'good'
            else:
                creation_quality['overall_rating'] = 'needs_improvement'
            
            return creation_quality
            
        except Exception as e:
            logger.error(f"Creation quality assessment failed: {e}")
            return {'overall_rating': 'unknown'}

    async def _generate_scene_summary(
        self, 
        scene_classification: Dict, 
        lighting_analysis: Dict, 
        color_analysis: Dict, 
        content_analysis: Dict
    ) -> Dict[str, Any]:
        """Generate human-readable scene summary"""
        try:
            summary = {
                'description': '',
                'key_features': [],
                'recommendations': [],
                'tags': []
            }
            
            # Generate description
            scene_type = scene_classification.get('primary_category', 'unknown')
            lighting_quality = lighting_analysis.get('lighting_quality', 'good')
            color_harmony = color_analysis.get('color_harmony', 'unknown')
            
            description_parts = []
            description_parts.append(f"{scene_type} scene")
            description_parts.append(f"with {lighting_quality} lighting")
            
            if color_harmony != 'unknown':
                description_parts.append(f"and {color_harmony} color harmony")
            
            summary['description'] = ' '.join(description_parts).capitalize()
            
            # Key features
            if content_analysis.get('human_presence', False):
                summary['key_features'].append('Human subjects present')
            
            if lighting_analysis.get('brightness_level') == 'high':
                summary['key_features'].append('Bright, well-lit scene')
            
            if color_analysis.get('saturation_level') == 'high':
                summary['key_features'].append('Vibrant colors')
            
            # Generate tags
            summary['tags'] = [
                scene_type,
                lighting_analysis.get('lighting_quality', 'lighting'),
                color_analysis.get('saturation_level', 'saturation')
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"Scene summary generation failed: {e}")
            return {'description': 'Scene analysis completed'}

    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """Get scene analysis capabilities"""
        return {
            'scene_categories': list(self.scene_categories.keys()),
            'lighting_types': self.lighting_types,
            'composition_rules': self.composition_rules,
            'creative_contexts': list(self.creative_contexts.keys()),
            'color_analysis': True,
            'texture_analysis': True,
            'content_recognition': True,
            'quality_assessment': True
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.performance_monitor.close()
            logger.info("Scene Analyzer cleanup completed")
        except Exception as e:
            logger.error(f"Scene Analyzer cleanup failed: {e}")
