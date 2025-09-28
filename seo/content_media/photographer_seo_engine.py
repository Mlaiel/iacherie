"""Photographer SEO Engine
Advanced SEO optimization specialized for photographers and visual content creators.

Features:
- Image metadata optimization
- Alt-text generation with AI
- Photo gallery SEO
- Portfolio optimization
- Stock photo SEO
- Photography blog integration
- Client gallery SEO
- Photo contest optimization

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Expertise: Lead Dev IA + Photography Expert + SEO Specialist + Visual Content Strategist
"""

import asyncio
import logging
import os
import base64
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re
import hashlib
from pathlib import Path

try:
    from PIL import Image, ImageStat, ExifTags
    from PIL.ExifTags import TAGS
    import cv2
    import numpy as np
    # from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
    from colorthief import ColorThief
    import requests
    from io import BytesIO
    import torch
    from sklearn.cluster import KMeans
    import webcolors
    import exifread
except ImportError as e:
    logging.warning(f"Optional photographer SEO dependencies not available: {e}")

logger = logging.getLogger(__name__)


class PhotographyGenre(Enum):
    """Photography genres for specialized SEO optimization."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    WEDDING = "wedding"
    STREET = "street"
    WILDLIFE = "wildlife"
    MACRO = "macro"
    FASHION = "fashion"
    COMMERCIAL = "commercial"
    REAL_ESTATE = "real_estate"
    PRODUCT = "product"
    FOOD = "food"
    TRAVEL = "travel"
    SPORTS = "sports"
    EVENT = "event"
    ARCHITECTURAL = "architectural"
    DOCUMENTARY = "documentary"
    FINE_ART = "fine_art"
    STOCK = "stock"
    NEWBORN = "newborn"
    FAMILY = "family"


class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    TIFF = "tiff"
    RAW = "raw"
    WEBP = "webp"
    HEIC = "heic"
    BMP = "bmp"
    GIF = "gif"


class ColorPalette(Enum):
    """Color palette types for image analysis."""
    WARM = "warm"
    COOL = "cool"
    MONOCHROME = "monochrome"
    VIBRANT = "vibrant"
    MUTED = "muted"
    PASTEL = "pastel"
    EARTH_TONES = "earth_tones"
    COMPLEMENTARY = "complementary"
    ANALOGOUS = "analogous"
    TRIADIC = "triadic"


class LightingCondition(Enum):
    """Lighting conditions for photography."""
    NATURAL_LIGHT = "natural_light"
    STUDIO_LIGHTING = "studio_lighting"
    GOLDEN_HOUR = "golden_hour"
    BLUE_HOUR = "blue_hour"
    OVERCAST = "overcast"
    BACKLIT = "backlit"
    SIDE_LIT = "side_lit"
    FRONT_LIT = "front_lit"
    LOW_LIGHT = "low_light"
    HIGH_KEY = "high_key"
    LOW_KEY = "low_key"


@dataclass
class ImageMetadata:
    """Comprehensive image metadata structure."""
    filename: str
    file_path: str
    file_size: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    format: Optional[ImageFormat] = None
    color_mode: Optional[str] = None
    has_transparency: bool = False
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[bool] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    location: Optional[str] = None
    photographer: Optional[str] = None
    copyright: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    genre: Optional[PhotographyGenre] = None


@dataclass
class ImageAnalysis:
    """AI-powered image analysis results."""
    dominant_colors: List[str] = field(default_factory=list)
    color_palette: Optional[ColorPalette] = None
    brightness_level: Optional[float] = None
    contrast_level: Optional[float] = None
    saturation_level: Optional[float] = None
    sharpness_score: Optional[float] = None
    composition_score: Optional[float] = None
    lighting_condition: Optional[LightingCondition] = None
    mood: Optional[str] = None
    subjects_detected: List[str] = field(default_factory=list)
    objects_detected: List[str] = field(default_factory=list)
    faces_count: int = 0
    people_count: int = 0
    emotion_detected: List[str] = field(default_factory=list)
    scene_type: Optional[str] = None
    quality_score: Optional[float] = None
    technical_issues: List[str] = field(default_factory=list)


@dataclass
class SEOOptimizedImage:
    """SEO-optimized image data."""
    original_metadata: ImageMetadata
    image_analysis: ImageAnalysis
    optimized_filename: str
    optimized_alt_text: str
    optimized_title: str
    optimized_description: str
    suggested_keywords: List[str]
    caption: str
    structured_data: Dict[str, Any]
    social_media_variants: Dict[str, Dict[str, Any]]
    seo_score: float
    improvement_suggestions: List[str]
    licensing_recommendations: List[str]
    platform_optimization: Dict[str, Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhotographyPortfolio:
    """Photography portfolio data structure."""
    photographer_name: str
    portfolio_title: str
    description: str
    website_url: Optional[str] = None
    contact_info: Dict[str, str] = field(default_factory=dict)
    specialties: List[PhotographyGenre] = field(default_factory=list)
    experience_years: Optional[int] = None
    awards: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    equipment: List[str] = field(default_factory=list)
    services_offered: List[str] = field(default_factory=list)
    pricing_packages: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    social_media: Dict[str, str] = field(default_factory=dict)
    client_testimonials: List[Dict[str, str]] = field(default_factory=list)
    featured_images: List[str] = field(default_factory=list)
    galleries: Dict[str, List[str]] = field(default_factory=dict)


class PhotographerSEOEngine:
    """Advanced SEO engine specialized for photographers and visual content creators.
    
    Provides comprehensive image SEO optimization, portfolio enhancement, and 
    photography business growth strategies.
    """
    
    def __init__(self, 
                 enable_ai_analysis: bool = True,
                 api_keys: Dict[str, str] = None):
        """Initialize Photographer SEO Engine.
        
        Args:
            enable_ai_analysis: Enable AI-powered image analysis
            api_keys: Dictionary containing API keys for various services
        """
        self.enable_ai_analysis = enable_ai_analysis
        self.api_keys = api_keys or {}
        
        # Initialize AI models if available
        self.image_captioner = None
        self.object_detector = None
        self.face_detector = None
        self.emotion_analyzer = None
        
        if enable_ai_analysis:
            try:
                # Image captioning model
                self.image_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.image_captioner = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                
                # Object detection
                self.object_detector = pipeline("object-detection", 
                                               model="facebook/detr-resnet-50")
                
                # Additional models would be initialized here
                logger.info("AI models loaded successfully")
                
            except Exception as e:
                logger.warning(f"AI models not available: {e}")
        
        # Photography-specific SEO keywords
        self.photography_keywords = {
            "technical": ["iso", "aperture", "shutter speed", "focal length", "depth of field", "bokeh"],
            "lighting": ["natural light", "studio lighting", "golden hour", "blue hour", "backlit"],
            "composition": ["rule of thirds", "leading lines", "symmetry", "framing", "perspective"],
            "genres": [genre.value for genre in PhotographyGenre],
            "equipment": ["camera", "lens", "tripod", "flash", "filter", "drone"],
            "editing": ["lightroom", "photoshop", "raw", "hdr", "color grading", "retouching"],
            "business": ["portfolio", "client", "booking", "pricing", "package", "wedding photography"],
            "platforms": ["instagram", "flickr", "500px", "behance", "shutterstock", "getty images"]
        }
        
        # Image optimization settings
        self.optimization_settings = {
            "max_file_size": 2 * 1024 * 1024,  # 2MB
            "web_dimensions": {
                "thumbnail": (300, 300),
                "medium": (800, 600),
                "large": (1920, 1080),
                "social_square": (1080, 1080),
                "social_story": (1080, 1920)
            },
            "quality_settings": {
                "web": 85,
                "print": 95,
                "social": 80
            }
        }
        
        logger.info("Photographer SEO Engine initialized successfully")
    
    async def optimize_image_seo(self, 
                               image_path: str,
                               target_keywords: List[str] = None,
                               genre: PhotographyGenre = None) -> SEOOptimizedImage:
        """Optimize a single image for SEO.
        
        Args:
            image_path: Path to the image file
            target_keywords: Target keywords for SEO
            genre: Photography genre
            
        Returns:
            SEOOptimizedImage with complete optimization data
        """
        try:
            # Extract image metadata
            metadata = await self._extract_image_metadata(image_path)
            if genre:
                metadata.genre = genre
            
            # Perform AI image analysis
            image_analysis = await self._analyze_image_content(image_path)
            
            # Generate SEO optimizations
            optimized_filename = self._optimize_filename(metadata, target_keywords)
            optimized_alt_text = await self._generate_alt_text(metadata, image_analysis, target_keywords)
            optimized_title = await self._generate_image_title(metadata, image_analysis, target_keywords)
            optimized_description = await self._generate_image_description(metadata, image_analysis)
            suggested_keywords = await self._generate_image_keywords(metadata, image_analysis)
            caption = await self._generate_social_caption(metadata, image_analysis)
            
            # Create structured data
            structured_data = self._create_image_structured_data(metadata, image_analysis)
            
            # Generate social media variants
            social_media_variants = await self._create_social_media_variants(
                image_path, metadata, image_analysis
            )
            
            # Calculate SEO score
            seo_score = self._calculate_image_seo_score(
                metadata, optimized_alt_text, optimized_title, suggested_keywords
            )
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_image_improvement_suggestions(
                metadata, image_analysis, seo_score
            )
            
            # Generate licensing recommendations
            licensing_recommendations = self._generate_licensing_recommendations(metadata, image_analysis)
            
            # Platform-specific optimization
            platform_optimization = await self._optimize_for_platforms(
                metadata, image_analysis, suggested_keywords
            )
            
            return SEOOptimizedImage(
                original_metadata=metadata,
                image_analysis=image_analysis,
                optimized_filename=optimized_filename,
                optimized_alt_text=optimized_alt_text,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                suggested_keywords=suggested_keywords,
                caption=caption,
                structured_data=structured_data,
                social_media_variants=social_media_variants,
                seo_score=seo_score,
                improvement_suggestions=improvement_suggestions,
                licensing_recommendations=licensing_recommendations,
                platform_optimization=platform_optimization
            )
            
        except Exception as e:
            logger.error(f"Error optimizing image SEO for {image_path}: {e}")
            raise
    
    async def optimize_portfolio_seo(self, 
                                   portfolio: PhotographyPortfolio,
                                   target_markets: List[str] = None) -> Dict[str, Any]:
        """Optimize photography portfolio for SEO.
        
        Args:
            portfolio: Photography portfolio data
            target_markets: Target geographical markets
            
        Returns:
            Dictionary with portfolio optimization recommendations
        """
        try:
            optimization_results = {
                "seo_optimized_title": "",
                "meta_description": "",
                "structured_data": {},
                "keyword_strategy": {},
                "content_recommendations": [],
                "local_seo_strategy": {},
                "social_media_optimization": {},
                "gallery_optimization": {},
                "client_acquisition_strategy": {},
                "performance_tracking": {}
            }
            
            # Optimize portfolio title and description
            optimization_results["seo_optimized_title"] = await self._optimize_portfolio_title(portfolio)
            optimization_results["meta_description"] = await self._optimize_portfolio_meta_description(portfolio)
            
            # Create structured data for portfolio
            optimization_results["structured_data"] = self._create_portfolio_structured_data(portfolio)
            
            # Develop keyword strategy
            optimization_results["keyword_strategy"] = await self._develop_portfolio_keyword_strategy(
                portfolio, target_markets
            )
            
            # Generate content recommendations
            optimization_results["content_recommendations"] = await self._generate_portfolio_content_recommendations(
                portfolio
            )
            
            # Local SEO strategy
            if target_markets:
                optimization_results["local_seo_strategy"] = await self._create_local_seo_strategy(
                    portfolio, target_markets
                )
            
            # Social media optimization
            optimization_results["social_media_optimization"] = await self._optimize_portfolio_social_media(
                portfolio
            )
            
            # Gallery optimization
            optimization_results["gallery_optimization"] = await self._optimize_portfolio_galleries(
                portfolio
            )
            
            # Client acquisition strategy
            optimization_results["client_acquisition_strategy"] = self._create_client_acquisition_strategy(
                portfolio
            )
            
            # Performance tracking setup
            optimization_results["performance_tracking"] = self._setup_portfolio_performance_tracking(
                portfolio
            )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio SEO: {e}")
            return {}
    
    async def optimize_stock_photography_seo(self, 
                                           image_paths: List[str],
                                           stock_platform: str = "shutterstock") -> Dict[str, Any]:
        """Optimize images for stock photography platforms.
        
        Args:
            image_paths: List of image file paths
            stock_platform: Target stock platform
            
        Returns:
            Dictionary with stock photography optimization results
        """
        try:
            stock_optimization = {
                "platform_requirements": {},
                "optimized_images": [],
                "keyword_strategies": {},
                "submission_recommendations": [],
                "market_analysis": {},
                "pricing_strategies": {},
                "portfolio_categorization": {}
            }
            
            # Get platform-specific requirements
            stock_optimization["platform_requirements"] = self._get_stock_platform_requirements(stock_platform)
            
            # Process each image
            for image_path in image_paths:
                try:
                    # Optimize for stock photography
                    stock_optimized_image = await self._optimize_for_stock_photography(
                        image_path, stock_platform
                    )
                    stock_optimization["optimized_images"].append(stock_optimized_image)
                    
                except Exception as e:
                    logger.warning(f"Failed to optimize {image_path} for stock: {e}")
            
            # Develop keyword strategies
            stock_optimization["keyword_strategies"] = await self._develop_stock_keyword_strategies(
                stock_optimization["optimized_images"]
            )
            
            # Generate submission recommendations
            stock_optimization["submission_recommendations"] = self._generate_stock_submission_recommendations(
                stock_optimization["optimized_images"], stock_platform
            )
            
            # Market analysis
            stock_optimization["market_analysis"] = await self._perform_stock_market_analysis(
                stock_optimization["optimized_images"]
            )
            
            # Pricing strategies
            stock_optimization["pricing_strategies"] = self._generate_stock_pricing_strategies(
                stock_optimization["optimized_images"], stock_platform
            )
            
            # Portfolio categorization
            stock_optimization["portfolio_categorization"] = self._categorize_stock_portfolio(
                stock_optimization["optimized_images"]
            )
            
            return stock_optimization
            
        except Exception as e:
            logger.error(f"Error optimizing stock photography SEO: {e}")
            return {}
    
    # Private helper methods
    
    async def _extract_image_metadata(self, image_path: str) -> ImageMetadata:
        """Extract comprehensive metadata from image file."""
        try:
            # Get file information
            file_path = Path(image_path)
            file_stats = file_path.stat()
            
            metadata = ImageMetadata(
                filename=file_path.name,
                file_path=str(file_path),
                file_size=file_stats.st_size,
                creation_date=datetime.fromtimestamp(file_stats.st_ctime),
                modification_date=datetime.fromtimestamp(file_stats.st_mtime)
            )
            
            # Open image with PIL
            with Image.open(image_path) as img:
                metadata.dimensions = img.size
                metadata.format = ImageFormat(img.format.lower()) if img.format else None
                metadata.color_mode = img.mode
                metadata.has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'Make':
                            metadata.camera_make = str(value)
                        elif tag == 'Model':
                            metadata.camera_model = str(value)
                        elif tag == 'LensModel':
                            metadata.lens_model = str(value)
                        elif tag == 'FocalLength':
                            metadata.focal_length = float(value) if isinstance(value, (int, float)) else None
                        elif tag == 'FNumber':
                            metadata.aperture = float(value) if isinstance(value, (int, float)) else None
                        elif tag == 'ExposureTime':
                            metadata.shutter_speed = str(value)
                        elif tag == 'ISOSpeedRatings':
                            metadata.iso = int(value) if isinstance(value, (int, float)) else None
                        elif tag == 'Flash':
                            metadata.flash = bool(value & 1) if isinstance(value, int) else None
                        elif tag == 'GPSInfo':
                            gps_coords = self._extract_gps_coordinates(value)
                            if gps_coords:
                                metadata.gps_coordinates = gps_coords
                        elif tag == 'Artist':
                            metadata.photographer = str(value)
                        elif tag == 'Copyright':
                            metadata.copyright = str(value)
                        elif tag == 'ImageDescription':
                            metadata.description = str(value)
                        elif tag == 'Keywords':
                            if isinstance(value, str):
                                metadata.keywords = [kw.strip() for kw in value.split(',')]
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {image_path}: {e}")
            return ImageMetadata(filename=Path(image_path).name, file_path=image_path)
    
    async def _analyze_image_content(self, image_path: str) -> ImageAnalysis:
        """Perform AI-powered image content analysis."""
        try:
            analysis = ImageAnalysis()
            
            # Load image
            image = Image.open(image_path)
            cv_image = cv2.imread(image_path)
            
            # Color analysis
            analysis.dominant_colors = self._extract_dominant_colors(image)
            analysis.color_palette = self._determine_color_palette(analysis.dominant_colors)
            
            # Technical analysis
            analysis.brightness_level = self._calculate_brightness(cv_image)
            analysis.contrast_level = self._calculate_contrast(cv_image)
            analysis.saturation_level = self._calculate_saturation(cv_image)
            analysis.sharpness_score = self._calculate_sharpness(cv_image)
            
            # AI-powered analysis
            if self.enable_ai_analysis and self.image_captioner:
                # Generate image caption
                inputs = self.image_processor(image, return_tensors="pt")
                out = self.image_captioner.generate(**inputs, max_length=50)
                caption = self.image_processor.decode(out[0], skip_special_tokens=True)
                
                # Extract subjects and objects from caption
                analysis.subjects_detected = self._extract_subjects_from_caption(caption)
                
                # Object detection
                if self.object_detector:
                    try:
                        objects = self.object_detector(image)
                        analysis.objects_detected = [obj['label'] for obj in objects]
                    except Exception as e:
                        logger.warning(f"Object detection failed: {e}")
                
                # Face detection
                analysis.faces_count = self._count_faces(cv_image)
                
                # Determine scene type and mood
                analysis.scene_type = self._classify_scene_type(caption)
                analysis.mood = self._determine_image_mood(analysis)
            
            # Composition analysis
            analysis.composition_score = self._analyze_composition(cv_image)
            
            # Lighting condition detection
            analysis.lighting_condition = self._detect_lighting_condition(cv_image)
            
            # Quality assessment
            analysis.quality_score = self._assess_image_quality(cv_image)
            analysis.technical_issues = self._detect_technical_issues(cv_image, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing image content: {e}")
            return ImageAnalysis()
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from image."""
        try:
            # Resize image for faster processing
            image_small = image.resize((150, 150))
            
            # Convert to RGB if necessary
            if image_small.mode != 'RGB':
                image_small = image_small.convert('RGB')
            
            # Convert to numpy array
            data = np.array(image_small)
            data = data.reshape((-1, 3))
            
            # Use KMeans clustering to find dominant colors
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(data)
            
            # Get color centers and convert to hex
            colors = []
            for center in kmeans.cluster_centers_:
                rgb = tuple(map(int, center))
                try:
                    hex_color = webcolors.rgb_to_hex(rgb)
                    colors.append(hex_color)
                except ValueError:
                    # If exact color name not found, use hex representation
                    hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
                    colors.append(hex_color)
            
            return colors
            
        except Exception as e:
            logger.warning(f"Error extracting dominant colors: {e}")
            return ['#000000']  # Default to black
    
    def _determine_color_palette(self, colors: List[str]) -> ColorPalette:
        """Determine the color palette type."""
        try:
            if not colors:
                return ColorPalette.MONOCHROME
            
            # Convert hex colors to RGB for analysis
            rgb_colors = []
            for color in colors[:3]:  # Analyze top 3 colors
                try:
                    rgb = webcolors.hex_to_rgb(color)
                    rgb_colors.append(rgb)
                except ValueError:
                    continue
            
            if not rgb_colors:
                return ColorPalette.MONOCHROME
            
            # Calculate color properties
            saturations = []
            brightnesses = []
            
            for rgb in rgb_colors:
                r, g, b = [x/255.0 for x in rgb]
                max_val = max(r, g, b)
                min_val = min(r, g, b)
                
                # Saturation
                saturation = (max_val - min_val) / max_val if max_val > 0 else 0
                saturations.append(saturation)
                
                # Brightness
                brightness = (r + g + b) / 3
                brightnesses.append(brightness)
            
            avg_saturation = sum(saturations) / len(saturations)
            avg_brightness = sum(brightnesses) / len(brightnesses)
            
            # Classify palette
            if avg_saturation < 0.1:
                return ColorPalette.MONOCHROME
            elif avg_saturation > 0.7:
                return ColorPalette.VIBRANT
            elif avg_brightness > 0.8:
                return ColorPalette.PASTEL
            elif avg_saturation < 0.3:
                return ColorPalette.MUTED
            else:
                # Check for warm/cool tones
                warm_count = 0
                for rgb in rgb_colors:
                    r, g, b = rgb
                    if r > b:  # More red than blue indicates warm
                        warm_count += 1
                
                if warm_count > len(rgb_colors) / 2:
                    return ColorPalette.WARM
                else:
                    return ColorPalette.COOL
                    
        except Exception as e:
            logger.warning(f"Error determining color palette: {e}")
            return ColorPalette.MONOCHROME
    
    def _calculate_brightness(self, image: np.ndarray) -> float:
        """Calculate image brightness level."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return float(np.mean(gray) / 255.0)
        except Exception:
            return 0.5
    
    def _calculate_contrast(self, image: np.ndarray) -> float:
        """Calculate image contrast level."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return float(np.std(gray) / 255.0)
        except Exception:
            return 0.5
    
    def _calculate_saturation(self, image: np.ndarray) -> float:
        """Calculate image saturation level."""
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            return float(np.mean(hsv[:, :, 1]) / 255.0)
        except Exception:
            return 0.5
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """Calculate image sharpness score."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            return float(np.var(laplacian))
        except Exception:
            return 0.0
    
    def _count_faces(self, image: np.ndarray) -> int:
        """Count faces in the image."""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces)
        except Exception:
            return 0
    
    def _analyze_composition(self, image: np.ndarray) -> float:
        """Analyze image composition quality."""
        try:
            # Simple composition analysis based on rule of thirds
            height, width = image.shape[:2]
            
            # Divide image into 9 sections (rule of thirds)
            third_h = height // 3
            third_w = width // 3
            
            # Calculate variance in each section to assess balance
            sections = []
            for i in range(3):
                for j in range(3):
                    section = image[i*third_h:(i+1)*third_h, j*third_w:(j+1)*third_w]
                    gray_section = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
                    sections.append(np.var(gray_section))
            
            # Good composition has balanced variance across sections
            composition_score = 1.0 - (np.std(sections) / np.mean(sections)) if np.mean(sections) > 0 else 0.5
            return max(0.0, min(1.0, composition_score))
            
        except Exception:
            return 0.5
    
    def _detect_lighting_condition(self, image: np.ndarray) -> LightingCondition:
        """Detect lighting conditions in the image."""
        try:
            # Convert to LAB color space for better lighting analysis
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]
            
            # Calculate lighting metrics
            brightness = np.mean(l_channel)
            contrast = np.std(l_channel)
            
            # Simple heuristic classification
            if brightness > 200:
                return LightingCondition.HIGH_KEY
            elif brightness < 50:
                return LightingCondition.LOW_KEY
            elif contrast > 50:
                return LightingCondition.STUDIO_LIGHTING
            else:
                return LightingCondition.NATURAL_LIGHT
                
        except Exception:
            return LightingCondition.NATURAL_LIGHT
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """Assess overall image quality."""
        try:
            # Multiple quality metrics
            scores = []
            
            # Sharpness
            sharpness = self._calculate_sharpness(image)
            scores.append(min(1.0, sharpness / 1000))  # Normalize
            
            # Noise level (inverse correlation with quality)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            noise = np.std(gray)
            noise_score = max(0.0, 1.0 - (noise / 100))
            scores.append(noise_score)
            
            # Exposure (balanced brightness)
            brightness = self._calculate_brightness(image)
            exposure_score = 1.0 - abs(0.5 - brightness) * 2
            scores.append(exposure_score)
            
            # Overall quality
            return sum(scores) / len(scores)
            
        except Exception:
            return 0.5
    
    def _detect_technical_issues(self, image: np.ndarray, analysis: ImageAnalysis) -> List[str]:
        """Detect technical issues in the image."""
        issues = []
        
        try:
            # Check for overexposure
            if analysis.brightness_level and analysis.brightness_level > 0.9:
                issues.append("Possible overexposure")
            
            # Check for underexposure
            if analysis.brightness_level and analysis.brightness_level < 0.1:
                issues.append("Possible underexposure")
            
            # Check for low contrast
            if analysis.contrast_level and analysis.contrast_level < 0.1:
                issues.append("Low contrast")
            
            # Check for blur
            if analysis.sharpness_score and analysis.sharpness_score < 100:
                issues.append("Possible blur or soft focus")
            
            # Check image resolution
            height, width = image.shape[:2]
            if width < 1920 or height < 1080:
                issues.append("Low resolution for modern web standards")
            
        except Exception as e:
            logger.warning(f"Error detecting technical issues: {e}")
        
        return issues
    
    # Additional helper methods (simplified for brevity)
    
    def _extract_subjects_from_caption(self, caption: str) -> List[str]:
        """Extract subjects from AI-generated caption."""
        subjects = []
        common_subjects = [
            "person", "people", "man", "woman", "child", "baby",
            "dog", "cat", "bird", "animal", "flower", "tree",
            "building", "car", "food", "landscape", "portrait"
        ]
        
        caption_lower = caption.lower()
        for subject in common_subjects:
            if subject in caption_lower:
                subjects.append(subject)
        
        return subjects
    
    def _classify_scene_type(self, caption: str) -> str:
        """Classify scene type from caption."""
        scene_keywords = {
            "indoor": ["room", "house", "inside", "interior"],
            "outdoor": ["outside", "landscape", "sky", "mountain", "beach"],
            "portrait": ["person", "man", "woman", "face", "people"],
            "nature": ["tree", "flower", "animal", "forest", "garden"],
            "urban": ["city", "street", "building", "road", "car"]
        }
        
        caption_lower = caption.lower()
        for scene_type, keywords in scene_keywords.items():
            if any(keyword in caption_lower for keyword in keywords):
                return scene_type
        
        return "general"
    
    def _determine_image_mood(self, analysis: ImageAnalysis) -> str:
        """Determine image mood based on analysis."""
        if analysis.brightness_level and analysis.brightness_level > 0.7:
            if analysis.saturation_level and analysis.saturation_level > 0.6:
                return "vibrant"
            else:
                return "bright"
        elif analysis.brightness_level and analysis.brightness_level < 0.3:
            return "dramatic"
        elif analysis.color_palette == ColorPalette.WARM:
            return "warm"
        elif analysis.color_palette == ColorPalette.COOL:
            return "cool"
        else:
            return "neutral"
    
    def _optimize_filename(self, metadata: ImageMetadata, keywords: List[str] = None) -> str:
        """Optimize filename for SEO."""
        try:
            # Start with basic info
            parts = []
            
            # Add photographer name if available
            if metadata.photographer:
                photographer_clean = re.sub(r'[^a-zA-Z0-9]', '', metadata.photographer.lower())
                parts.append(photographer_clean)
            
            # Add primary keyword
            if keywords:
                primary_keyword = re.sub(r'[^a-zA-Z0-9]', '-', keywords[0].lower())
                parts.append(primary_keyword)
            
            # Add genre if available
            if metadata.genre:
                parts.append(metadata.genre.value)
            
            # Add date
            if metadata.creation_date:
                date_str = metadata.creation_date.strftime("%Y-%m")
                parts.append(date_str)
            
            # Combine parts
            filename_base = "-".join(parts) if parts else "optimized-image"
            
            # Add file extension
            original_ext = Path(metadata.filename).suffix
            return f"{filename_base}{original_ext}"
            
        except Exception as e:
            logger.warning(f"Error optimizing filename: {e}")
            return metadata.filename
    
    async def _generate_alt_text(self, 
                               metadata: ImageMetadata,
                               analysis: ImageAnalysis,
                               keywords: List[str] = None) -> str:
        """Generate SEO-optimized alt text."""
        try:
            alt_parts = []
            
            # Add primary subject/scene
            if analysis.subjects_detected:
                alt_parts.append(analysis.subjects_detected[0])
            elif analysis.scene_type:
                alt_parts.append(analysis.scene_type)
            
            # Add descriptive elements
            if analysis.lighting_condition:
                lighting_desc = analysis.lighting_condition.value.replace("_", " ")
                alt_parts.append(f"with {lighting_desc}")
            
            # Add color information
            if analysis.color_palette and analysis.color_palette != ColorPalette.MONOCHROME:
                color_desc = analysis.color_palette.value.replace("_", " ")
                alt_parts.append(f"featuring {color_desc} tones")
            
            # Add photographer credit if available
            if metadata.photographer:
                alt_parts.append(f"by {metadata.photographer}")
            
            # Include primary keyword if provided
            if keywords and keywords[0] not in " ".join(alt_parts).lower():
                alt_parts.insert(0, keywords[0])
            
            alt_text = " ".join(alt_parts)
            
            # Ensure proper length (125 characters max recommended)
            if len(alt_text) > 125:
                alt_text = alt_text[:122] + "..."
            
            return alt_text.capitalize()
            
        except Exception as e:
            logger.warning(f"Error generating alt text: {e}")
            return "Professional photography image"
    
    async def _generate_image_title(self,
                                  metadata: ImageMetadata,
                                  analysis: ImageAnalysis,
                                  keywords: List[str] = None) -> str:
        """Generate SEO-optimized image title."""
        try:
            title_parts = []
            
            # Add primary keyword or subject
            if keywords:
                title_parts.append(keywords[0].title())
            elif analysis.subjects_detected:
                title_parts.append(analysis.subjects_detected[0].title())
            
            # Add genre or style
            if metadata.genre:
                genre_desc = metadata.genre.value.replace("_", " ").title()
                title_parts.append(f"{genre_desc} Photography")
            
            # Add photographer name
            if metadata.photographer:
                title_parts.append(f"by {metadata.photographer}")
            
            title = " - ".join(title_parts) if title_parts else "Professional Photography"
            
            return title
            
        except Exception as e:
            logger.warning(f"Error generating image title: {e}")
            return "Professional Photography"
    
    async def _generate_image_description(self,
                                        metadata: ImageMetadata,
                                        analysis: ImageAnalysis) -> str:
        """Generate detailed image description."""
        try:
            description_parts = []
            
            # Technical details
            tech_details = []
            if metadata.camera_make and metadata.camera_model:
                tech_details.append(f"Shot with {metadata.camera_make} {metadata.camera_model}")
            
            if metadata.lens_model:
                tech_details.append(f"using {metadata.lens_model}")
            
            if metadata.focal_length:
                tech_details.append(f"at {metadata.focal_length}mm")
            
            if metadata.aperture:
                tech_details.append(f"f/{metadata.aperture}")
            
            if tech_details:
                description_parts.append(". ".join(tech_details))
            
            # Image characteristics
            char_details = []
            if analysis.lighting_condition:
                lighting = analysis.lighting_condition.value.replace("_", " ")
                char_details.append(f"Features {lighting}")
            
            if analysis.color_palette and analysis.color_palette != ColorPalette.MONOCHROME:
                colors = analysis.color_palette.value.replace("_", " ")
                char_details.append(f"with beautiful {colors}")
            
            if char_details:
                description_parts.append(". ".join(char_details))
            
            # Copyright and attribution
            if metadata.photographer:
                description_parts.append(f"Photographed by {metadata.photographer}")
            
            if metadata.copyright:
                description_parts.append(f"© {metadata.copyright}")
            
            return ". ".join(description_parts) + "." if description_parts else "Professional photography."
            
        except Exception as e:
            logger.warning(f"Error generating image description: {e}")
            return "Professional photography."
    
    async def _generate_image_keywords(self,
                                     metadata: ImageMetadata,
                                     analysis: ImageAnalysis) -> List[str]:
        """Generate comprehensive keyword list for the image."""
        keywords = set()
        
        try:
            # From metadata
            if metadata.keywords:
                keywords.update(metadata.keywords)
            
            if metadata.genre:
                keywords.add(metadata.genre.value)
                keywords.add(f"{metadata.genre.value} photography")
            
            # From analysis
            if analysis.subjects_detected:
                keywords.update(analysis.subjects_detected)
            
            if analysis.objects_detected:
                keywords.update(analysis.objects_detected)
            
            if analysis.scene_type:
                keywords.add(analysis.scene_type)
            
            if analysis.lighting_condition:
                lighting_kw = analysis.lighting_condition.value.replace("_", " ")
                keywords.add(lighting_kw)
            
            if analysis.color_palette and analysis.color_palette != ColorPalette.MONOCHROME:
                color_kw = analysis.color_palette.value.replace("_", " ")
                keywords.add(color_kw)
                keywords.add(f"{color_kw} photography")
            
            # Technical keywords
            if metadata.camera_make:
                keywords.add(metadata.camera_make.lower())
            
            # General photography keywords
            keywords.update([
                "photography", "professional", "high quality",
                "digital photography", "creative", "artistic"
            ])
            
            # Location-based keywords if GPS available
            if metadata.gps_coordinates and metadata.location:
                keywords.add(metadata.location)
            
            return list(keywords)[:20]  # Limit to 20 most relevant keywords
            
        except Exception as e:
            logger.warning(f"Error generating keywords: {e}")
            return ["photography", "professional", "image"]
    
    # Additional methods for completeness (simplified implementations)
    
    def _extract_gps_coordinates(self, gps_info: dict) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from EXIF data."""
        try:
            # Simplified GPS extraction - would need more robust implementation
            if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                lat = float(gps_info['GPSLatitude'][0])
                lon = float(gps_info['GPSLongitude'][0])
                return (lat, lon)
        except Exception:
            pass
        return None
    
    async def _generate_social_caption(self,
                                     metadata: ImageMetadata,
                                     analysis: ImageAnalysis) -> str:
        """Generate social media caption."""
        caption_parts = []
        
        if analysis.subjects_detected:
            caption_parts.append(f"Capturing the beauty of {analysis.subjects_detected[0]}")
        
        if metadata.genre:
            genre_desc = metadata.genre.value.replace("_", " ")
            caption_parts.append(f"#{genre_desc}photography")
        
        caption_parts.extend(["#photography", "#professional", "#artistic"])
        
        return " ".join(caption_parts)
    
    def _create_image_structured_data(self,
                                    metadata: ImageMetadata,
                                    analysis: ImageAnalysis) -> Dict[str, Any]:
        """Create structured data for the image."""
        structured_data = {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "name": metadata.filename,
            "description": metadata.description or "Professional photography",
            "creator": {
                "@type": "Person",
                "name": metadata.photographer
            } if metadata.photographer else None,
            "dateCreated": metadata.creation_date.isoformat() if metadata.creation_date else None,
            "width": str(metadata.dimensions[0]) if metadata.dimensions else None,
            "height": str(metadata.dimensions[1]) if metadata.dimensions else None,
            "encodingFormat": metadata.format.value if metadata.format else None
        }
        
        # Remove None values
        return {k: v for k, v in structured_data.items() if v is not None}
    
    def _calculate_image_seo_score(self,
                                 metadata: ImageMetadata,
                                 alt_text: str,
                                 title: str,
                                 keywords: List[str]) -> float:
        """Calculate overall SEO score for the image."""
        score = 0.0
        max_score = 100.0
        
        # Filename optimization (20 points)
        if re.search(r'[a-z]+-[a-z]+', metadata.filename):
            score += 20
        
        # Alt text quality (25 points)
        if alt_text and len(alt_text) > 10:
            score += 25
        
        # Title optimization (20 points)
        if title and len(title) > 5:
            score += 20
        
        # Keywords quantity (15 points)
        if len(keywords) >= 5:
            score += 15
        elif len(keywords) >= 3:
            score += 10
        
        # Metadata completeness (20 points)
        metadata_score = 0
        if metadata.photographer:
            metadata_score += 5
        if metadata.description:
            metadata_score += 5
        if metadata.keywords:
            metadata_score += 5
        if metadata.genre:
            metadata_score += 5
        score += metadata_score
        
        return min(max_score, score)
    
    def _generate_image_improvement_suggestions(self,
                                              metadata: ImageMetadata,
                                              analysis: ImageAnalysis,
                                              seo_score: float) -> List[str]:
        """Generate improvement suggestions for the image."""
        suggestions = []
        
        if seo_score < 60:
            suggestions.append("Optimize filename with descriptive keywords")
        
        if not metadata.photographer:
            suggestions.append("Add photographer attribution in metadata")
        
        if not metadata.description:
            suggestions.append("Add detailed description in image metadata")
        
        if len(metadata.keywords) < 5:
            suggestions.append("Add more relevant keywords to image metadata")
        
        if analysis.quality_score and analysis.quality_score < 0.7:
            suggestions.append("Consider improving image technical quality")
        
        if analysis.technical_issues:
            suggestions.extend([f"Address: {issue}" for issue in analysis.technical_issues])
        
        return suggestions[:5]
    
    def _generate_licensing_recommendations(self,
                                          metadata: ImageMetadata,
                                          analysis: ImageAnalysis) -> List[str]:
        """Generate licensing recommendations."""
        recommendations = []
        
        if analysis.quality_score and analysis.quality_score > 0.8:
            recommendations.append("High quality - suitable for premium stock licensing")
        
        if metadata.genre == PhotographyGenre.COMMERCIAL:
            recommendations.append("Ensure model releases for commercial use")
        
        if analysis.faces_count > 0:
            recommendations.append("Obtain model releases for identifiable people")
        
        if metadata.gps_coordinates:
            recommendations.append("Consider location releases for recognizable properties")
        
        recommendations.append("Register copyright for IP protection")
        
        return recommendations[:5]