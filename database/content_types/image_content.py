"""Image Content Management Module - Professional Image Content Processing System

Module spécialisé pour la gestion, l'analyse et la protection du contenu image
dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Computer Vision Expert, Image Processing Specialist, Content Protection Expert  
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import hashlib
import json
import asyncio
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
import imagehash
from skimage import feature, filters, measure

logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Supported image formats with technical specifications"""    JPEG = {"ext": ".jpg", "compression": "lossy", "quality": "good", "transparency": False}
    PNG = {"ext": ".png", "compression": "lossless", "quality": "excellent", "transparency": True}
    TIFF = {"ext": ".tiff", "compression": "lossless", "quality": "excellent", "transparency": True}
    WEBP = {"ext": ".webp", "compression": "both", "quality": "very_good", "transparency": True}
    HEIF = {"ext": ".heif", "compression": "lossy", "quality": "excellent", "transparency": False}
    BMP = {"ext": ".bmp", "compression": "none", "quality": "excellent", "transparency": False}
    GIF = {"ext": ".gif", "compression": "lossless", "quality": "fair", "transparency": True}
    SVG = {"ext": ".svg", "compression": "none", "quality": "vector", "transparency": True}

class ImageContentType(Enum):
    """Image content classification types"""    PHOTOGRAPH = "photograph"
    ARTWORK = "artwork"
    DIAGRAM = "diagram"
    SCREENSHOT = "screenshot"
    DOCUMENT = "document"
    LOGO = "logo"
    ICON = "icon"
    MEME = "meme"
    INFOGRAPHIC = "infographic"
    CHART = "chart"
    MAP = "map"
    PATTERN = "pattern"
    TEXTURE = "texture"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class ImageQuality(Enum):
    """Image quality classifications"""    LOW = {"max_pixels": 307200, "description": "480p and below"}  # 640x480
    MEDIUM = {"max_pixels": 921600, "description": "720p"}  # 1280x720
    HIGH = {"max_pixels": 2073600, "description": "1080p"}  # 1920x1080
    VERY_HIGH = {"max_pixels": 8294400, "description": "4K"}  # 3840x2160
    ULTRA = {"max_pixels": float('inf'), "description": "Above 4K"}

@dataclass
class ImageMetadata:
    """Comprehensive image metadata structure"""    # Technical metadata
    width: int
    height: int
    channels: int
    bit_depth: Optional[int] = None
    color_space: Optional[str] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    dpi: Optional[Tuple[int, int]] = None
    aspect_ratio: Optional[str] = None
    
    # EXIF metadata
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[str] = None
    exposure_mode: Optional[str] = None
    white_balance: Optional[str] = None
    
    # Geographic metadata
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None
    location_name: Optional[str] = None
    
    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    copyright: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    
    # Rights and licensing
    license: Optional[str] = None
    usage_rights: Optional[str] = None
    model_release: bool = False
    property_release: bool = False
    
    # Image analysis metadata
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_palette: List[str] = field(default_factory=list)
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    sharpness: Optional[float] = None
    noise_level: Optional[float] = None
    
    # Content analysis
    content_type: Optional[ImageContentType] = None
    quality_level: Optional[ImageQuality] = None
    faces_detected: int = 0
    objects_detected: List[str] = field(default_factory=list)
    text_detected: bool = False
    scene_type: Optional[str] = None
    
    # Quality metrics
    quality_score: Optional[float] = None
    technical_quality: Optional[float] = None
    aesthetic_quality: Optional[float] = None
    composition_score: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    date_taken: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImageFingerprint:
    """Image fingerprint for content identification and protection"""    content_id: str
    primary_hash: str
    perceptual_hash: str
    difference_hash: str
    wavelet_hash: str
    color_hash: str
    structural_hash: str
    histogram_features: Optional[np.ndarray] = None
    texture_features: Optional[np.ndarray] = None
    edge_features: Optional[np.ndarray] = None
    sift_keypoints: Optional[List[cv2.KeyPoint]] = None
    sift_descriptors: Optional[np.ndarray] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.0
    quality_indicators: Dict[str, float] = field(default_factory=dict)

class ImageContentManager:
    """    Professional image content management system with advanced processing capabilities
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """        Initialize the Image Content Manager
        
        Args:
            config: Configuration dictionary for image processing
        """        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.ImageContentManager")
        self.supported_formats = [fmt.value["ext"] for fmt in ImageFormat]
        
        # Initialize processing components
        self._init_components()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for image processing"""        return {
            "max_file_size_mb": 50,
            "max_dimension": 8192,
            "quality_threshold": 0.7,
            "enable_fingerprinting": True,
            "enable_exif_extraction": True,
            "enable_quality_analysis": True,
            "enable_face_detection": True,
            "enable_object_detection": False,  # Requires additional models
            "enable_text_detection": True,
            "enable_color_analysis": True,
            "thumbnail_size": (300, 300),
            "hash_sizes": {"phash": 8, "dhash": 8, "whash": 8},
            "sift_features": True,
            "histogram_analysis": True
        }
    
    def _init_components(self):
        """Initialize image processing components"""        self.logger.info("Initializing Image Content Manager components...")
        
        # OpenCV configuration
        self.face_cascade = None
        try:
            # Load face detection classifier
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            self.logger.warning(f"Face detection not available: {e}")
        
        # SIFT detector for feature extraction
        try:
            self.sift = cv2.SIFT_create()
        except Exception as e:
            self.logger.warning(f"SIFT detector not available: {e}")
            self.sift = None
        
        # Image analysis parameters
        self.analysis_config = {
            "histogram_bins": 256,
            "color_clusters": 5,
            "edge_threshold": (50, 150),
            "noise_estimation_kernel": 3
        }
        
        self.logger.info("Image Content Manager initialized successfully")
    
    async def process_image_file(
        self,
        file_path: Union[str, Path],
        extract_metadata: bool = True,
        generate_fingerprint: bool = True,
        quality_analysis: bool = True,
        content_analysis: bool = True
    ) -> Dict[str, Any]:
        """        Process image file with comprehensive analysis
        
        Args:
            file_path: Path to image file
            extract_metadata: Whether to extract metadata
            generate_fingerprint: Whether to generate fingerprint
            quality_analysis: Whether to perform quality analysis
            content_analysis: Whether to perform content analysis
            
        Returns:
            Dict containing processed image information
        """        try:
            file_path = Path(file_path)
            self.logger.info(f"Processing image file: {file_path}")
            
            # Validate file
            if not await self._validate_image_file(file_path):
                raise ValueError(f"Invalid image file: {file_path}")
            
            # Load image
            pil_image = Image.open(file_path)
            cv_image = cv2.imread(str(file_path))
            
            if cv_image is None:
                raise ValueError(f"Cannot load image: {file_path}")
            
            # Convert BGR to RGB for consistency
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            results = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "processing_timestamp": datetime.now(timezone.utc),
                "image_dimensions": (pil_image.width, pil_image.height),
                "color_mode": pil_image.mode,
                "format": pil_image.format
            }
            
            # Extract metadata
            if extract_metadata:
                metadata = await self._extract_image_metadata(file_path, pil_image, cv_image_rgb)
                results["metadata"] = metadata
            
            # Generate fingerprint
            if generate_fingerprint:
                fingerprint = await self._generate_image_fingerprint(cv_image_rgb, pil_image, str(file_path))
                results["fingerprint"] = fingerprint
            
            # Quality analysis
            if quality_analysis:
                quality_metrics = await self._analyze_image_quality(cv_image_rgb)
                results["quality_metrics"] = quality_metrics
            
            # Content analysis
            if content_analysis:
                content_analysis_results = await self._analyze_image_content(cv_image_rgb)
                results["content_analysis"] = content_analysis_results
            
            # Content classification
            content_type = await self._classify_image_content(cv_image_rgb, metadata if extract_metadata else None)
            results["content_classification"] = content_type
            
            self.logger.info(f"Image processing completed for: {file_path}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process image file {file_path}: {e}")
            raise
    
    async def _validate_image_file(self, file_path: Path) -> bool:
        """Validate image file format and accessibility"""        try:
            # Check file existence and size
            if not file_path.exists():
                return False
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                self.logger.warning(f"File size {file_size_mb:.2f}MB exceeds limit")
                return False
            
            # Check format support
            if file_path.suffix.lower() not in self.supported_formats:
                return False
            
            # Try to open image
            try:
                with Image.open(file_path) as img:
                    # Check dimensions
                    if max(img.width, img.height) > self.config["max_dimension"]:
                        self.logger.warning(f"Image dimensions {img.width}x{img.height} exceed limit")
                        return False
                    return True
            except Exception:
                return False
                
        except Exception as e:
            self.logger.error(f"Image file validation failed: {e}")
            return False
    
    async def _extract_image_metadata(
        self, 
        file_path: Path, 
        pil_image: Image.Image,
        cv_image: np.ndarray
    ) -> ImageMetadata:
        """Extract comprehensive image metadata"""        try:
            # Basic technical metadata
            width, height = pil_image.size
            channels = len(cv_image.shape) if len(cv_image.shape) == 3 else cv_image.shape[2]
            
            # Calculate aspect ratio
            aspect_ratio = f"{width}:{height}"
            gcd = np.gcd(width, height)
            if gcd > 1:
                aspect_ratio = f"{width//gcd}:{height//gcd}"
            
            metadata = ImageMetadata(
                width=width,
                height=height,
                channels=channels,
                file_size=file_path.stat().st_size,
                format=pil_image.format,
                color_space=pil_image.mode,
                aspect_ratio=aspect_ratio
            )
            
            # DPI information
            if hasattr(pil_image, 'info') and 'dpi' in pil_image.info:
                metadata.dpi = pil_image.info['dpi']
            
            # Determine quality level
            total_pixels = width * height
            for quality in ImageQuality:
                if total_pixels <= quality.value["max_pixels"]:
                    metadata.quality_level = quality
                    break
            else:
                metadata.quality_level = ImageQuality.ULTRA
            
            # Extract EXIF data
            if self.config.get("enable_exif_extraction", True):
                await self._extract_exif_metadata(pil_image, metadata)
            
            # Color analysis
            if self.config.get("enable_color_analysis", True):
                color_stats = await self._analyze_color_properties(cv_image)
                metadata.dominant_colors = color_stats["dominant_colors"]
                metadata.brightness = color_stats["brightness"]
                metadata.contrast = color_stats["contrast"]
                metadata.saturation = color_stats["saturation"]
            
            # Face detection
            if self.config.get("enable_face_detection", True) and self.face_cascade is not None:
                faces_count = await self._detect_faces(cv_image)
                metadata.faces_detected = faces_count
            
            # Text detection
            if self.config.get("enable_text_detection", True):
                text_detected = await self._detect_text(cv_image)
                metadata.text_detected = text_detected
            
            # Quality assessment
            if self.config.get("enable_quality_analysis", True):
                quality_scores = await self._assess_image_quality(cv_image)
                metadata.sharpness = quality_scores["sharpness"]
                metadata.noise_level = quality_scores["noise_level"]
                metadata.technical_quality = quality_scores["technical_quality"]
            
            metadata.analyzed_at = datetime.now(timezone.utc)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Image metadata extraction failed: {e}")
            raise
    
    async def _extract_exif_metadata(self, pil_image: Image.Image, metadata: ImageMetadata):
        """Extract EXIF metadata from image"""        try:
            exif_data = pil_image._getexif()
            if exif_data is not None:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Camera information
                    if tag == "Make":
                        metadata.camera_make = str(value)
                    elif tag == "Model":
                        metadata.camera_model = str(value)
                    elif tag == "LensModel":
                        metadata.lens_model = str(value)
                    elif tag == "FocalLength":
                        if isinstance(value, tuple) and len(value) == 2:
                            metadata.focal_length = float(value[0] / value[1])
                        else:
                            metadata.focal_length = float(value)
                    
                    # Camera settings
                    elif tag == "FNumber":
                        if isinstance(value, tuple) and len(value) == 2:
                            metadata.aperture = f"f/{value[0]/value[1]:.1f}"
                        else:
                            metadata.aperture = f"f/{float(value):.1f}"
                    elif tag == "ExposureTime":
                        if isinstance(value, tuple) and len(value) == 2:
                            metadata.shutter_speed = f"1/{int(value[1]/value[0])}"
                        else:
                            metadata.shutter_speed = str(value)
                    elif tag == "ISOSpeedRatings":
                        metadata.iso = int(value)
                    elif tag == "Flash":
                        metadata.flash = "Yes" if value & 1 else "No"
                    elif tag == "ExposureMode":
                        metadata.exposure_mode = str(value)
                    elif tag == "WhiteBalance":
                        metadata.white_balance = str(value)
                    
                    # Date and time
                    elif tag == "DateTime":
                        try:
                            metadata.date_taken = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                        except ValueError:
                            pass
                    
                    # GPS information
                    elif tag == "GPSInfo":
                        gps_info = value
                        if isinstance(gps_info, dict):
                            lat, lon = self._extract_gps_coordinates(gps_info)
                            if lat is not None and lon is not None:
                                metadata.gps_latitude = lat
                                metadata.gps_longitude = lon
                    
                    # Copyright and description
                    elif tag == "Copyright":
                        metadata.copyright = str(value)
                    elif tag == "ImageDescription":
                        metadata.description = str(value)
                    elif tag == "Artist":
                        metadata.creator = str(value)
                        
        except Exception as e:
            self.logger.warning(f"EXIF extraction failed: {e}")
    
    def _extract_gps_coordinates(self, gps_info: Dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract GPS coordinates from EXIF GPS info"""        try:
            def convert_to_degrees(value):
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = None
            lon = None
            
            if 2 in gps_info and 1 in gps_info:  # Latitude
                lat = convert_to_degrees(gps_info[2])
                if gps_info[1] == 'S':
                    lat = -lat
            
            if 4 in gps_info and 3 in gps_info:  # Longitude
                lon = convert_to_degrees(gps_info[4])
                if gps_info[3] == 'W':
                    lon = -lon
            
            return lat, lon
            
        except Exception as e:
            self.logger.warning(f"GPS coordinate extraction failed: {e}")
            return None, None
    
    async def _analyze_color_properties(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color properties of the image"""        try:
            # Convert to different color spaces for analysis
            lab_image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Brightness (L channel in LAB)
            brightness = float(np.mean(lab_image[:, :, 0]))
            
            # Contrast (standard deviation of L channel)
            contrast = float(np.std(lab_image[:, :, 0]))
            
            # Saturation (S channel in HSV)
            saturation = float(np.mean(hsv_image[:, :, 1]))
            
            # Extract dominant colors using K-means
            dominant_colors = await self._extract_dominant_colors(image)
            
            return {
                "brightness": brightness,
                "contrast": contrast,
                "saturation": saturation,
                "dominant_colors": dominant_colors
            }
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
            return {
                "brightness": 0.0,
                "contrast": 0.0,
                "saturation": 0.0,
                "dominant_colors": []
            }
    
    async def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using K-means clustering"""        try:
            # Reshape image to list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to int and sort by frequency
            centers = np.uint8(centers)
            dominant_colors = []
            
            for center in centers:
                dominant_colors.append((int(center[0]), int(center[1]), int(center[2])))
            
            return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    async def _detect_faces(self, image: np.ndarray) -> int:
        """Detect faces in the image"""        try:
            if self.face_cascade is None:
                return 0
            
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            return len(faces)
            
        except Exception as e:
            self.logger.error(f"Face detection failed: {e}")
            return 0
    
    async def _detect_text(self, image: np.ndarray) -> bool:
        """Detect text presence in the image using edge analysis"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for horizontal line patterns (typical of text)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Count line pixels
            line_pixels = np.sum(horizontal_lines > 0)
            
            # Threshold for text detection
            text_threshold = image.shape[0] * image.shape[1] * 0.01  # 1% of image pixels
            
            return line_pixels > text_threshold
            
        except Exception as e:
            self.logger.error(f"Text detection failed: {e}")
            return False
    
    async def _assess_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Assess technical quality of the image"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Sharpness using Laplacian variance
            sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            
            # Noise estimation using high-frequency content
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            noise_response = cv2.filter2D(gray, cv2.CV_64F, kernel)
            noise_level = float(np.std(noise_response))
            
            # Overall technical quality score
            sharpness_score = min(sharpness / 1000, 1.0)  # Normalize sharpness
            noise_score = max(0, 1.0 - (noise_level / 100))  # Lower noise is better
            
            technical_quality = (sharpness_score * 0.6 + noise_score * 0.4)
            
            return {
                "sharpness": sharpness,
                "noise_level": noise_level,
                "technical_quality": technical_quality
            }
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return {
                "sharpness": 0.0,
                "noise_level": 0.0,
                "technical_quality": 0.5
            }
    
    async def _generate_image_fingerprint(
        self, 
        cv_image: np.ndarray,
        pil_image: Image.Image,
        content_id: str
    ) -> ImageFingerprint:
        """Generate comprehensive image fingerprint for content protection"""        try:
            # Primary hash (raw image data)
            primary_hash = hashlib.sha256(cv_image.tobytes()).hexdigest()
            
            # Perceptual hashes using imagehash library
            perceptual_hash = str(imagehash.phash(pil_image, hash_size=self.config["hash_sizes"]["phash"]))
            difference_hash = str(imagehash.dhash(pil_image, hash_size=self.config["hash_sizes"]["dhash"]))
            wavelet_hash = str(imagehash.whash(pil_image, hash_size=self.config["hash_sizes"]["whash"]))
            
            # Color hash
            color_hash = await self._generate_color_hash(cv_image)
            
            # Structural hash based on edges
            structural_hash = await self._generate_structural_hash(cv_image)
            
            # Advanced features
            histogram_features = await self._extract_histogram_features(cv_image)
            texture_features = await self._extract_texture_features(cv_image)
            edge_features = await self._extract_edge_features(cv_image)
            
            # SIFT features for robust matching
            sift_keypoints, sift_descriptors = await self._extract_sift_features(cv_image)
            
            # Quality indicators
            quality_indicators = {
                "spatial_resolution": float(cv_image.shape[0] * cv_image.shape[1]),
                "color_depth": float(cv_image.max() - cv_image.min()),
                "edge_density": float(np.sum(cv2.Canny(cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY), 50, 150) > 0)),
                "texture_complexity": float(np.std(filters.sobel(cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY))))
            }
            
            # Confidence score based on image quality
            confidence_score = min(1.0, (
                min(quality_indicators["spatial_resolution"] / 1000000, 1.0) * 0.25 +
                min(quality_indicators["color_depth"] / 255, 1.0) * 0.25 +
                min(quality_indicators["edge_density"] / 10000, 1.0) * 0.25 +
                min(quality_indicators["texture_complexity"] / 100, 1.0) * 0.25
            ))
            
            fingerprint = ImageFingerprint(
                content_id=hashlib.md5(content_id.encode()).hexdigest(),
                primary_hash=primary_hash,
                perceptual_hash=perceptual_hash,
                difference_hash=difference_hash,
                wavelet_hash=wavelet_hash,
                color_hash=color_hash,
                structural_hash=structural_hash,
                histogram_features=histogram_features,
                texture_features=texture_features,
                edge_features=edge_features,
                sift_keypoints=sift_keypoints,
                sift_descriptors=sift_descriptors,
                confidence_score=confidence_score,
                quality_indicators=quality_indicators
            )
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Image fingerprint generation failed: {e}")
            raise
    
    async def _generate_color_hash(self, image: np.ndarray) -> str:
        """Generate color-based hash"""        try:
            # Calculate color histogram
            hist_r = cv2.calcHist([image], [0], None, [32], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [32], [0, 256])
            hist_b = cv2.calcHist([image], [2], None, [32], [0, 256])
            
            # Combine histograms
            combined_hist = np.concatenate([hist_r.flatten(), hist_g.flatten(), hist_b.flatten()])
            
            # Normalize
            combined_hist = combined_hist / np.sum(combined_hist)
            
            return hashlib.sha256(combined_hist.tobytes()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Color hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_structural_hash(self, image: np.ndarray) -> str:
        """Generate structural hash based on edges and shapes"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Extract structural features
            structural_features = []
            for contour in contours[:50]:  # Limit to first 50 contours
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    structural_features.extend([area, perimeter, circularity])
            
            # Pad or truncate to fixed size
            structural_features = structural_features[:150]  # Fixed size
            while len(structural_features) < 150:
                structural_features.append(0.0)
            
            structural_str = json.dumps(structural_features, sort_keys=True)
            return hashlib.sha256(structural_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Structural hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _extract_histogram_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract histogram-based features"""        try:
            # Color histograms
            hist_r = cv2.calcHist([image], [0], None, [64], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [64], [0, 256])
            hist_b = cv2.calcHist([image], [2], None, [64], [0, 256])
            
            # Grayscale histogram
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            hist_gray = cv2.calcHist([gray], [0], None, [64], [0, 256])
            
            # Combine all histograms
            histogram_features = np.concatenate([
                hist_r.flatten(),
                hist_g.flatten(),
                hist_b.flatten(),
                hist_gray.flatten()
            ])
            
            # Normalize
            histogram_features = histogram_features / np.sum(histogram_features)
            
            return histogram_features
            
        except Exception as e:
            self.logger.error(f"Histogram feature extraction failed: {e}")
            return None
    
    async def _extract_texture_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract texture-based features using LBP and GLCM"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Local Binary Pattern
            radius = 3
            n_points = 8 * radius
            lbp = feature.local_binary_pattern(gray, n_points, radius, method='uniform')
            
            # LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
            lbp_hist = lbp_hist.astype(float)
            lbp_hist /= (lbp_hist.sum() + 1e-10)
            
            # Gray Level Co-occurrence Matrix features (simplified)
            # Calculate GLCM properties
            glcm_props = []
            try:
                # Resize image for GLCM calculation if too large
                if gray.shape[0] > 256 or gray.shape[1] > 256:
                    gray_resized = cv2.resize(gray, (256, 256))
                else:
                    gray_resized = gray
                
                # Simple texture measures
                glcm_props.extend([
                    float(np.std(gray_resized)),  # Standard deviation
                    float(filters.sobel(gray_resized).var()),  # Edge variance
                    float(np.mean(np.abs(np.diff(gray_resized, axis=0)))),  # Vertical differences
                    float(np.mean(np.abs(np.diff(gray_resized, axis=1))))   # Horizontal differences
                ])
            except Exception:
                glcm_props = [0.0, 0.0, 0.0, 0.0]
            
            # Combine features
            texture_features = np.concatenate([lbp_hist, glcm_props])
            
            return texture_features
            
        except Exception as e:
            self.logger.error(f"Texture feature extraction failed: {e}")
            return None
    
    async def _extract_edge_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract edge-based features"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Different edge detection methods
            edges_canny = cv2.Canny(gray, 50, 150)
            edges_sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            edges_sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges_laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Edge statistics
            edge_features = [
                float(np.sum(edges_canny > 0)),  # Canny edge count
                float(np.mean(np.abs(edges_sobel_x))),  # Sobel X mean
                float(np.mean(np.abs(edges_sobel_y))),  # Sobel Y mean
                float(np.std(edges_sobel_x)),  # Sobel X std
                float(np.std(edges_sobel_y)),  # Sobel Y std
                float(np.mean(np.abs(edges_laplacian))),  # Laplacian mean
                float(np.std(edges_laplacian)),  # Laplacian std
            ]
            
            # Edge direction histogram
            edge_magnitude = np.sqrt(edges_sobel_x**2 + edges_sobel_y**2)
            edge_direction = np.arctan2(edges_sobel_y, edges_sobel_x)
            
            # Direction histogram (8 bins)
            dir_hist, _ = np.histogram(edge_direction.ravel(), bins=8, range=(-np.pi, np.pi))
            dir_hist = dir_hist.astype(float)
            dir_hist /= (dir_hist.sum() + 1e-10)
            
            edge_features.extend(dir_hist.tolist())
            
            return np.array(edge_features)
            
        except Exception as e:
            self.logger.error(f"Edge feature extraction failed: {e}")
            return None
    
    async def _extract_sift_features(self, image: np.ndarray) -> Tuple[Optional[List], Optional[np.ndarray]]:
        """Extract SIFT keypoints and descriptors"""        try:
            if self.sift is None:
                return None, None
            
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = self.sift.detectAndCompute(gray, None)
            
            # Convert keypoints to serializable format
            kp_data = []
            if keypoints:
                for kp in keypoints[:100]:  # Limit to 100 keypoints
                    kp_data.append({
                        'x': float(kp.pt[0]),
                        'y': float(kp.pt[1]),
                        'size': float(kp.size),
                        'angle': float(kp.angle),
                        'response': float(kp.response)
                    })
            
            return kp_data, descriptors
            
        except Exception as e:
            self.logger.error(f"SIFT feature extraction failed: {e}")
            return None, None
    
    async def _analyze_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """Analyze comprehensive image quality metrics"""        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            quality_metrics = {}
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics["sharpness"] = float(sharpness)
            
            # Noise estimation
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            noise_response = cv2.filter2D(gray, cv2.CV_64F, kernel)
            noise_level = np.std(noise_response)
            quality_metrics["noise_level"] = float(noise_level)
            
            # Contrast
            contrast = np.std(gray)
            quality_metrics["contrast"] = float(contrast)
            
            # Brightness distribution
            brightness = np.mean(gray)
            quality_metrics["brightness"] = float(brightness)
            
            # Dynamic range
            dynamic_range = float(np.max(gray) - np.min(gray))
            quality_metrics["dynamic_range"] = dynamic_range
            
            # Exposure quality (based on histogram distribution)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            # Check for clipping
            underexposed = np.sum(hist[:10]) / np.sum(hist)
            overexposed = np.sum(hist[-10:]) / np.sum(hist)
            exposure_quality = 1.0 - (underexposed + overexposed)
            quality_metrics["exposure_quality"] = float(exposure_quality)
            
            # Overall quality score
            sharpness_score = min(sharpness / 1000, 1.0)
            noise_score = max(0, 1.0 - (noise_level / 100))
            contrast_score = min(contrast / 64, 1.0)
            exposure_score = exposure_quality
            
            overall_quality = (
                sharpness_score * 0.3 +
                noise_score * 0.25 +
                contrast_score * 0.25 +
                exposure_score * 0.2
            )
            
            quality_metrics["overall_quality"] = max(0.0, min(1.0, overall_quality))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Image quality analysis failed: {e}")
            return {"overall_quality": 0.5, "error": str(e)}
    
    async def _analyze_image_content(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze image content for objects, scenes, etc."""        try:
            content_analysis = {
                "objects_detected": [],
                "scene_type": None,
                "composition_analysis": {},
                "aesthetic_scores": {}
            }
            
            # Basic composition analysis
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Rule of thirds analysis
            h, w = gray.shape
            third_h, third_w = h // 3, w // 3
            
            # Calculate interest points near rule of thirds lines
            roi_points = [
                gray[third_h:2*third_h, third_w:2*third_w],  # Center
                gray[:third_h, :third_w],  # Top-left
                gray[:third_h, 2*third_w:],  # Top-right
                gray[2*third_h:, :third_w],  # Bottom-left
                gray[2*third_h:, 2*third_w:]  # Bottom-right
            ]
            
            composition_scores = []
            for roi in roi_points:
                if roi.size > 0:
                    variance = np.var(roi)
                    composition_scores.append(variance)
            
            content_analysis["composition_analysis"] = {
                "rule_of_thirds_score": float(np.mean(composition_scores)) if composition_scores else 0.0,
                "center_weight": float(np.var(roi_points[0])) if roi_points[0].size > 0 else 0.0
            }
            
            # Color harmony analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hue_var = np.var(hsv[:, :, 0])
            saturation_mean = np.mean(hsv[:, :, 1])
            
            content_analysis["aesthetic_scores"] = {
                "color_harmony": float(1.0 / (1.0 + hue_var / 1000)),
                "color_vibrancy": float(saturation_mean / 255)
            }
            
            # Simple scene classification based on color and texture
            if saturation_mean > 150:
                content_analysis["scene_type"] = "vibrant"
            elif np.mean(gray) < 80:
                content_analysis["scene_type"] = "dark"
            elif np.mean(gray) > 180:
                content_analysis["scene_type"] = "bright"
            else:
                content_analysis["scene_type"] = "neutral"
            
            return content_analysis
            
        except Exception as e:
            self.logger.error(f"Image content analysis failed: {e}")
            return {
                "objects_detected": [],
                "scene_type": "unknown",
                "composition_analysis": {},
                "aesthetic_scores": {}
            }
    
    async def _classify_image_content(
        self, 
        image: np.ndarray, 
        metadata: Optional[ImageMetadata] = None
    ) -> ImageContentType:
        """Classify image content type using visual and metadata features"""        try:
            # Simple heuristic classification (in production, use ML model)
            
            # Check for faces (portraits)
            if metadata and metadata.faces_detected > 0:
                return ImageContentType.PORTRAIT
            
            # Check for text (documents, screenshots)
            if metadata and metadata.text_detected:
                # Check aspect ratio for document detection
                if metadata.aspect_ratio and ":" in metadata.aspect_ratio:
                    ratio_parts = metadata.aspect_ratio.split(":")
                    if len(ratio_parts) == 2:
                        w_ratio, h_ratio = int(ratio_parts[0]), int(ratio_parts[1])
                        if h_ratio > w_ratio * 1.2:  # Tall aspect ratio
                            return ImageContentType.DOCUMENT
                return ImageContentType.SCREENSHOT
            
            # Analyze image properties
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Edge density for diagram/artwork detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (image.shape[0] * image.shape[1])
            
            # Color variance for artwork/logo detection
            color_variance = np.var(image.reshape(-1, 3), axis=0).mean()
            
            # Size-based classification
            if metadata:
                total_pixels = metadata.width * metadata.height
                
                # Small images might be icons or logos
                if total_pixels < 10000:  # 100x100
                    if edge_density > 0.1:
                        return ImageContentType.ICON
                    else:
                        return ImageContentType.LOGO
            
            # High edge density suggests diagrams or artwork
            if edge_density > 0.05:
                if color_variance < 1000:
                    return ImageContentType.DIAGRAM
                else:
                    return ImageContentType.ARTWORK
            
            # Low edge density, natural colors suggest photograph
            if edge_density < 0.02 and color_variance > 2000:
                # Check if landscape (wide aspect ratio)
                if metadata and metadata.aspect_ratio:
                    ratio_parts = metadata.aspect_ratio.split(":")
                    if len(ratio_parts) == 2:
                        w_ratio, h_ratio = int(ratio_parts[0]), int(ratio_parts[1])
                        if w_ratio > h_ratio * 1.3:  # Wide aspect ratio
                            return ImageContentType.LANDSCAPE
                
                return ImageContentType.PHOTOGRAPH
            
            # Default to photograph
            return ImageContentType.PHOTOGRAPH
            
        except Exception as e:
            self.logger.error(f"Image content classification failed: {e}")
            return ImageContentType.PHOTOGRAPH  # Default fallback
    
    async def store_content(self, image_content: Dict[str, Any]) -> str:
        """Store processed image content in database"""        try:
            # Generate unique content ID
            content_id = hashlib.sha256(
                f"{image_content['file_path']}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Here you would implement database storage
            # For now, return the generated ID
            
            self.logger.info(f"Image content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to store image content: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""        return [fmt.value["ext"] for fmt in ImageFormat]
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific image format"""        for fmt in ImageFormat:
            if fmt.value["ext"] == f".{format_name.lower()}" or fmt.name.lower() == format_name.lower():
                return fmt.value
        return None
