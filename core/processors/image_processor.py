"""Image Processor Module - IA-Influencer-Agent Platform

Industrial-grade image processing engine for content creators and influencers.
Handles image analysis, enhancement, conversion, and AI-powered features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""
import asyncio
import logging
import numpy as np
import tempfile
import hashlib
from typing import Dict, Any, List, Optional, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import json
import time
import io
import base64

# Image processing imports
try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ExifTags
    import cv2
    import numpy as np
    from skimage import exposure, filters, feature, measure
    import imagehash
    IMAGE_LIBS_AVAILABLE = True
except ImportError:
    IMAGE_LIBS_AVAILABLE = False

# AI imports for image analysis
try:
    import torch
    import torchvision.transforms as transforms
    from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
    import face_recognition
    AI_LIBS_AVAILABLE = True
except ImportError:
    AI_LIBS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageFormat(str, Enum):
    """Supported image formats"""    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    SVG = "svg"
    HEIC = "heic"
    RAW = "raw"


class ImageQuality(str, Enum):
    """Image quality levels"""    LOW = "low"          # Compressed, small size
    MEDIUM = "medium"    # Balanced quality/size
    HIGH = "high"        # High quality, larger size
    LOSSLESS = "lossless"  # No compression


class ImageProcessingType(str, Enum):
    """Types of image processing"""    ANALYSIS = "analysis"
    ENHANCEMENT = "enhancement"
    CONVERSION = "conversion"
    COMPRESSION = "compression"
    RESIZE = "resize"
    CROP = "crop"
    FILTER = "filter"
    OBJECT_DETECTION = "object_detection"
    FACE_DETECTION = "face_detection"
    TEXT_EXTRACTION = "text_extraction"
    COLOR_ANALYSIS = "color_analysis"
    ARTISTIC_STYLE = "artistic_style"


@dataclass
class ImageProcessingConfig:
    """Configuration for image processing"""    target_format: ImageFormat = ImageFormat.JPEG
    target_quality: ImageQuality = ImageQuality.HIGH
    max_width: int = 4096
    max_height: int = 4096
    jpeg_quality: int = 90
    png_compression: int = 6
    webp_quality: int = 85
    enable_enhancement: bool = True
    enable_ai_analysis: bool = True
    enable_face_detection: bool = True
    enable_object_detection: bool = True
    enable_text_extraction: bool = True
    enable_color_analysis: bool = True
    enable_metadata_extraction: bool = True
    auto_orient: bool = True
    preserve_exif: bool = True
    thumbnail_size: Tuple[int, int] = (320, 240)
    watermark_enabled: bool = False
    watermark_opacity: float = 0.5


@dataclass
class ImageMetadata:
    """Comprehensive image metadata"""    width: int
    height: int
    format: str
    mode: str
    file_size: int
    has_transparency: bool
    color_depth: int
    dpi: Tuple[int, int]
    orientation: int
    creation_date: Optional[datetime] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[bool] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    software: Optional[str] = None
    artist: Optional[str] = None
    copyright: Optional[str] = None


@dataclass
class ColorAnalysis:
    """Color analysis results"""    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_palette: List[Tuple[int, int, int]] = field(default_factory=list)
    average_color: Optional[Tuple[int, int, int]] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    warmth: Optional[float] = None
    color_harmony: Optional[str] = None
    color_mood: Optional[str] = None


@dataclass
class ImageFeatures:
    """Advanced image features extracted via AI"""    faces_detected: List[Dict[str, Any]] = field(default_factory=list)
    objects_detected: List[Dict[str, Any]] = field(default_factory=list)
    text_regions: List[Dict[str, Any]] = field(default_factory=list)
    extracted_text: Optional[str] = None
    scene_description: Optional[str] = None
    color_analysis: Optional[ColorAnalysis] = None
    artistic_style: Optional[str] = None
    aesthetic_score: Optional[float] = None
    composition_score: Optional[float] = None
    technical_quality: Optional[float] = None
    blur_level: Optional[float] = None
    noise_level: Optional[float] = None
    exposure_level: Optional[float] = None
    landmarks: List[Dict[str, Any]] = field(default_factory=list)
    emotions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ImageAnalysisResult:
    """Result of image analysis"""    success: bool
    metadata: Optional[ImageMetadata] = None
    features: Optional[ImageFeatures] = None
    thumbnail: Optional[str] = None
    fingerprint: Optional[str] = None
    perceptual_hash: Optional[str] = None
    quality_score: Optional[float] = None
    aesthetic_score: Optional[float] = None
    uniqueness_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    error_message: Optional[str] = None


class ImageProcessor:
    """    🖼️ ENTERPRISE IMAGE PROCESSOR
    
    Industrial-grade image processing engine with advanced AI capabilities
    for content creators, photographers, and influencers.
    """    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[ImageProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or ImageProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.ImageProcessor")
        
        # Initialize AI models
        self._object_detector = None
        self._image_captioner = None
        self._aesthetic_scorer = None
        self._initialized = False
        
        if not IMAGE_LIBS_AVAILABLE:
            self.logger.warning("Image processing libraries not available")
        
        if not AI_LIBS_AVAILABLE:
            self.logger.warning("AI libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the image processor"""        try:
            if AI_LIBS_AVAILABLE and self.config.enable_ai_analysis:
                # Initialize object detection model
                if self.config.enable_object_detection:
                    try:
                        self._object_detector = pipeline(
                            "object-detection",
                            model="facebook/detr-resnet-50",
                            return_tensors="pt"
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not load object detector: {e}")
                
                # Initialize image captioning model
                try:
                    self._image_captioner = pipeline(
                        "image-to-text",
                        model="Salesforce/blip-image-captioning-base",
                        return_tensors="pt"
                    )
                except Exception as e:
                    self.logger.warning(f"Could not load image captioner: {e}")
            
            self._initialized = True
            self.logger.info("✅ Image processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize image processor: {e}")
            return False
    
    async def process(
        self,
        content: Union[bytes, str, BinaryIO, Image.Image],
        options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Process image content with comprehensive analysis
        
        Args:
            content: Image content (bytes, file path, file object, or PIL Image)
            options: Processing options
            metadata: Additional metadata
            
        Returns:
            Processing result dictionary
        """        start_time = time.time()
        options = options or {}
        metadata = metadata or {}
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Load image
            image = await self._load_image(content)
            
            if image is None:
                return {
                    "success": False,
                    "error_message": "Failed to load image content",
                    "processing_time": time.time() - start_time
                }
            
            # Extract metadata
            image_metadata = await self._extract_metadata(image, content)
            
            # Validate image
            validation_result = await self._validate_image(image_metadata)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error_message": validation_result["reason"],
                    "processing_time": time.time() - start_time
                }
            
            # Image enhancement
            enhanced_image = image
            if options.get("enhance", True) and self.config.enable_enhancement:
                enhanced_image = await self._enhance_image(image)
            
            # Feature extraction
            features = None
            if self.config.enable_ai_analysis:
                features = await self._extract_features(enhanced_image)
            
            # Generate thumbnail
            thumbnail = None
            if options.get("generate_thumbnail", True):
                thumbnail = await self._generate_thumbnail(enhanced_image)
            
            # Quality assessment
            quality_metrics = await self._assess_quality(enhanced_image)
            
            # Generate fingerprints
            fingerprint = await self._generate_fingerprint(enhanced_image)
            perceptual_hash = await self._generate_perceptual_hash(enhanced_image)
            
            # Generate tags
            tags = await self._generate_tags(
                metadata=image_metadata,
                features=features,
                quality_metrics=quality_metrics
            )
            
            # Format conversion if requested
            processed_content = None
            if options.get("convert_format"):
                target_format = ImageFormat(options.get("target_format", self.config.target_format))
                processed_content = await self._convert_format(enhanced_image, target_format, options)
            
            # Create analysis result
            analysis_result = ImageAnalysisResult(
                success=True,
                metadata=image_metadata,
                features=features,
                thumbnail=thumbnail,
                fingerprint=fingerprint,
                perceptual_hash=perceptual_hash,
                quality_score=quality_metrics.get("quality_score"),
                aesthetic_score=quality_metrics.get("aesthetic_score"),
                uniqueness_score=quality_metrics.get("uniqueness_score"),
                tags=tags,
                processing_time=time.time() - start_time
            )
            
            return {
                "success": True,
                "processed_content": processed_content,
                "analysis_result": analysis_result.__dict__,
                "metadata": image_metadata.__dict__,
                "quality_metrics": quality_metrics,
                "tags": tags,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _load_image(self, content: Union[bytes, str, BinaryIO, Image.Image]) -> Optional[Image.Image]:
        """Load image data from various input types"""        try:
            if not IMAGE_LIBS_AVAILABLE:
                self.logger.error("Image libraries not available")
                return None
            
            if isinstance(content, Image.Image):
                return content
            elif isinstance(content, str):
                # File path
                return Image.open(content)
            elif isinstance(content, bytes):
                # Bytes data
                return Image.open(io.BytesIO(content))
            else:
                # File object
                return Image.open(content)
            
        except Exception as e:
            self.logger.error(f"Failed to load image: {e}")
            return None
    
    async def _extract_metadata(
        self, 
        image: Image.Image, 
        original_content: Union[bytes, str, BinaryIO, Image.Image]
    ) -> ImageMetadata:
        """Extract comprehensive image metadata"""        try:
            # Basic properties
            width, height = image.size
            format_name = image.format or "UNKNOWN"
            mode = image.mode
            
            # File size
            file_size = 0
            if isinstance(original_content, bytes):
                file_size = len(original_content)
            elif isinstance(original_content, str):
                try:
                    file_size = Path(original_content).stat().st_size
                except:
                    pass
            
            # Image properties
            has_transparency = mode in ('RGBA', 'LA') or 'transparency' in image.info
            color_depth = len(mode) * 8 if mode else 24
            dpi = image.info.get('dpi', (72, 72))
            
            # EXIF data extraction
            exif_data = {}
            orientation = 1
            creation_date = None
            camera_make = None
            camera_model = None
            lens_model = None
            focal_length = None
            aperture = None
            shutter_speed = None
            iso = None
            flash = None
            gps_coordinates = None
            software = None
            artist = None
            copyright_info = None
            
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
                
                # Extract specific metadata
                orientation = exif_data.get('Orientation', 1)
                creation_date = exif_data.get('DateTime')
                camera_make = exif_data.get('Make')
                camera_model = exif_data.get('Model')
                lens_model = exif_data.get('LensModel')
                focal_length = exif_data.get('FocalLength')
                aperture = exif_data.get('FNumber')
                shutter_speed = exif_data.get('ExposureTime')
                iso = exif_data.get('ISOSpeedRatings')
                flash = exif_data.get('Flash')
                software = exif_data.get('Software')
                artist = exif_data.get('Artist')
                copyright_info = exif_data.get('Copyright')
                
                # Parse GPS data if available
                gps_info = exif_data.get('GPSInfo')
                if gps_info:
                    gps_coordinates = self._parse_gps_coordinates(gps_info)
                
                # Parse date
                if creation_date:
                    try:
                        creation_date = datetime.strptime(creation_date, '%Y:%m:%d %H:%M:%S')
                    except:
                        creation_date = None
            
            return ImageMetadata(
                width=width,
                height=height,
                format=format_name,
                mode=mode,
                file_size=file_size,
                has_transparency=has_transparency,
                color_depth=color_depth,
                dpi=dpi,
                orientation=orientation,
                creation_date=creation_date,
                camera_make=camera_make,
                camera_model=camera_model,
                lens_model=lens_model,
                focal_length=focal_length,
                aperture=aperture,
                shutter_speed=shutter_speed,
                iso=iso,
                flash=flash,
                gps_coordinates=gps_coordinates,
                software=software,
                artist=artist,
                copyright=copyright_info
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract image metadata: {e}")
            return ImageMetadata(
                width=0,
                height=0,
                format="unknown",
                mode="unknown",
                file_size=0,
                has_transparency=False,
                color_depth=24,
                dpi=(72, 72),
                orientation=1
            )
    
    def _parse_gps_coordinates(self, gps_info: Dict) -> Optional[Tuple[float, float]]:
        """Parse GPS coordinates from EXIF data"""        try:
            def convert_to_degrees(value):
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = gps_info.get(2)  # GPSLatitude
            lat_ref = gps_info.get(1)  # GPSLatitudeRef
            lon = gps_info.get(4)  # GPSLongitude
            lon_ref = gps_info.get(3)  # GPSLongitudeRef
            
            if lat and lon and lat_ref and lon_ref:
                lat_deg = convert_to_degrees(lat)
                lon_deg = convert_to_degrees(lon)
                
                if lat_ref == 'S':
                    lat_deg = -lat_deg
                if lon_ref == 'W':
                    lon_deg = -lon_deg
                
                return (lat_deg, lon_deg)
            
            return None
            
        except Exception as e:
            self.logger.error(f"GPS parsing failed: {e}")
            return None
    
    async def _validate_image(self, metadata: ImageMetadata) -> Dict[str, Any]:
        """Validate image against configuration constraints"""        if metadata.width > self.config.max_width or metadata.height > self.config.max_height:
            return {
                "valid": False,
                "reason": f"Image resolution ({metadata.width}x{metadata.height}) exceeds maximum ({self.config.max_width}x{self.config.max_height})"
            }
        
        if metadata.width == 0 or metadata.height == 0:
            return {
                "valid": False,
                "reason": "Invalid image dimensions"
            }
        
        return {"valid": True}
    
    async def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image quality through various techniques"""        try:
            enhanced = image.copy()
            
            # Auto-orient image based on EXIF
            if self.config.auto_orient:
                enhanced = ImageOps.exif_transpose(enhanced)
            
            # Convert to RGB if necessary for processing
            if enhanced.mode not in ('RGB', 'RGBA'):
                if enhanced.mode == 'RGBA':
                    # Preserve transparency
                    pass
                else:
                    enhanced = enhanced.convert('RGB')
            
            # Auto color balance
            enhanced = ImageOps.autocontrast(enhanced, cutoff=0.1, preserve_tone=True)
            
            # Subtle sharpening
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Slight contrast enhancement
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.05)
            
            # Subtle saturation boost
            if enhanced.mode == 'RGB':
                enhancer = ImageEnhance.Color(enhanced)
                enhanced = enhancer.enhance(1.1)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Image enhancement failed: {e}")
            return image
    
    async def _extract_features(self, image: Image.Image) -> ImageFeatures:
        """Extract advanced image features using computer vision and AI"""        try:
            features = ImageFeatures()
            
            # Convert to numpy array for CV operations
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Face detection
            if self.config.enable_face_detection and AI_LIBS_AVAILABLE:
                faces = await self._detect_faces(image)
                features.faces_detected = faces
            
            # Object detection
            if self.config.enable_object_detection and self._object_detector:
                objects = await self._detect_objects(image)
                features.objects_detected = objects
            
            # Text extraction
            if self.config.enable_text_extraction:
                text_regions, extracted_text = await self._extract_text(image)
                features.text_regions = text_regions
                features.extracted_text = extracted_text
            
            # Scene description
            if self._image_captioner:
                description = await self._generate_description(image)
                features.scene_description = description
            
            # Color analysis
            if self.config.enable_color_analysis:
                color_analysis = await self._analyze_colors(image)
                features.color_analysis = color_analysis
            
            # Technical quality assessment
            features.blur_level = await self._calculate_blur_level(cv_image)
            features.noise_level = await self._calculate_noise_level(cv_image)
            features.exposure_level = await self._calculate_exposure_level(cv_image)
            
            # Aesthetic assessment
            features.aesthetic_score = await self._calculate_aesthetic_score(image)
            features.composition_score = await self._calculate_composition_score(cv_image)
            features.technical_quality = await self._calculate_technical_quality(cv_image)
            
            # Artistic style detection
            features.artistic_style = await self._detect_artistic_style(image)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            return ImageFeatures()
    
    async def _detect_faces(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect faces in the image"""        try:
            # Convert PIL image to numpy array
            img_array = np.array(image)
            
            # Find face locations
            face_locations = face_recognition.face_locations(img_array)
            
            faces = []
            for (top, right, bottom, left) in face_locations:
                # Get face encodings for potential recognition
                face_encoding = face_recognition.face_encodings(img_array, [(top, right, bottom, left)])
                
                face_data = {
                    "bbox": [left, top, right, bottom],
                    "confidence": 1.0,  # face_recognition doesn't provide confidence
                    "landmarks": [],
                    "age": None,  # Would require additional model
                    "gender": None,  # Would require additional model
                    "emotion": None,  # Would require additional model
                    "encoding": face_encoding[0].tolist() if face_encoding else None
                }
                
                # Try to get facial landmarks
                try:
                    landmarks = face_recognition.face_landmarks(img_array, [(top, right, bottom, left)])
                    if landmarks:
                        face_data["landmarks"] = landmarks[0]
                except:
                    pass
                
                faces.append(face_data)
            
            return faces
            
        except Exception as e:
            self.logger.error(f"Face detection failed: {e}")
            return []
    
    async def _detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in the image using AI model"""        try:
            if not self._object_detector:
                return []
            
            # Run object detection
            results = self._object_detector(image)
            
            objects = []
            for result in results:
                objects.append({
                    "label": result["label"],
                    "confidence": result["score"],
                    "bbox": [
                        result["box"]["xmin"],
                        result["box"]["ymin"],
                        result["box"]["xmax"],
                        result["box"]["ymax"]
                    ]
                })
            
            return objects
            
        except Exception as e:
            self.logger.error(f"Object detection failed: {e}")
            return []
    
    async def _extract_text(self, image: Image.Image) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Extract text from the image using OCR"""        try:
            # Use pytesseract for OCR
            import pytesseract
            
            # Get text with bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            extracted_texts = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text:
                    confidence = int(data['conf'][i])
                    if confidence > 30:  # Filter low confidence text
                        text_regions.append({
                            "text": text,
                            "bbox": [
                                data['left'][i],
                                data['top'][i],
                                data['left'][i] + data['width'][i],
                                data['top'][i] + data['height'][i]
                            ],
                            "confidence": confidence / 100.0
                        })
                        extracted_texts.append(text)
            
            full_text = ' '.join(extracted_texts) if extracted_texts else None
            
            return text_regions, full_text
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return [], None
    
    async def _generate_description(self, image: Image.Image) -> Optional[str]:
        """Generate scene description using AI captioning"""        try:
            if not self._image_captioner:
                return None
            
            # Generate caption
            result = self._image_captioner(image)
            
            if result and len(result) > 0:
                return result[0]["generated_text"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Description generation failed: {e}")
            return None
    
    async def _analyze_colors(self, image: Image.Image) -> ColorAnalysis:
        """Analyze color properties of the image"""        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                rgb_image = image.convert('RGB')
            else:
                rgb_image = image
            
            # Convert to numpy array
            img_array = np.array(rgb_image)
            
            # Calculate average color
            average_color = tuple(np.mean(img_array, axis=(0, 1)).astype(int))
            
            # Calculate brightness (perceived luminance)
            brightness = np.mean(0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]) / 255.0
            
            # Calculate contrast (standard deviation of luminance)
            luminance = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
            contrast = np.std(luminance) / 255.0
            
            # Calculate saturation
            hsv_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            saturation = np.mean(hsv_image[:,:,1]) / 255.0
            
            # Calculate warmth (red/blue ratio)
            red_mean = np.mean(img_array[:,:,0])
            blue_mean = np.mean(img_array[:,:,2])
            warmth = red_mean / (blue_mean + 1) if blue_mean > 0 else 1.0
            warmth = min(2.0, warmth) / 2.0  # Normalize to 0-1
            
            # Extract dominant colors using K-means
            dominant_colors = await self._extract_dominant_colors(img_array)
            
            # Determine color mood and harmony
            color_mood = await self._determine_color_mood(brightness, saturation, warmth)
            color_harmony = await self._determine_color_harmony(dominant_colors)
            
            return ColorAnalysis(
                dominant_colors=dominant_colors,
                color_palette=dominant_colors[:5],  # Top 5 colors
                average_color=average_color,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                warmth=warmth,
                color_harmony=color_harmony,
                color_mood=color_mood
            )
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
            return ColorAnalysis()
    
    async def _extract_dominant_colors(self, img_array: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors using K-means clustering"""        try:
            from sklearn.cluster import KMeans
            
            # Reshape image to be a list of pixels
            pixels = img_array.reshape(-1, 3)
            
            # Sample pixels for performance
            if len(pixels) > 10000:
                indices = np.random.choice(len(pixels), 10000, replace=False)
                pixels = pixels[indices]
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the colors
            colors = kmeans.cluster_centers_.astype(int)
            
            # Sort by cluster size
            labels = kmeans.labels_
            color_counts = np.bincount(labels)
            sorted_indices = np.argsort(color_counts)[::-1]
            
            dominant_colors = [tuple(colors[i]) for i in sorted_indices]
            
            return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    async def _determine_color_mood(self, brightness: float, saturation: float, warmth: float) -> str:
        """Determine the color mood of the image"""        try:
            if brightness > 0.7 and saturation > 0.6:
                if warmth > 0.6:
                    return "vibrant_warm"
                else:
                    return "vibrant_cool"
            elif brightness > 0.7:
                return "bright_gentle"
            elif brightness < 0.3:
                if saturation > 0.5:
                    return "dramatic_moody"
                else:
                    return "dark_mysterious"
            elif saturation > 0.7:
                if warmth > 0.6:
                    return "rich_warm"
                else:
                    return "rich_cool"
            elif saturation < 0.3:
                return "muted_neutral"
            else:
                return "balanced"
                
        except:
            return "neutral"
    
    async def _determine_color_harmony(self, dominant_colors: List[Tuple[int, int, int]]) -> str:
        """Determine the color harmony type"""        try:
            if len(dominant_colors) < 2:
                return "monochromatic"
            
            # Convert to HSV for hue analysis
            hsv_colors = []
            for r, g, b in dominant_colors[:3]:
                hsv = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV)[0][0]
                hsv_colors.append(hsv[0])  # Hue value
            
            # Calculate hue differences
            hue_diffs = []
            for i in range(len(hsv_colors) - 1):
                diff = abs(hsv_colors[i] - hsv_colors[i + 1])
                diff = min(diff, 180 - diff)  # Account for circular nature of hue
                hue_diffs.append(diff)
            
            avg_hue_diff = np.mean(hue_diffs)
            
            if avg_hue_diff < 15:
                return "monochromatic"
            elif avg_hue_diff < 45:
                return "analogous"
            elif 45 <= avg_hue_diff <= 75:
                return "triadic"
            elif avg_hue_diff > 150:
                return "complementary"
            else:
                return "split_complementary"
                
        except:
            return "unknown"
    
    async def _calculate_blur_level(self, cv_image: np.ndarray) -> float:
        """Calculate blur level using Laplacian variance"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (higher = less blur)
            normalized_score = min(1.0, blur_score / 1000)
            
            return float(1.0 - normalized_score)  # Return blur level (higher = more blur)
            
        except Exception as e:
            self.logger.error(f"Blur calculation failed: {e}")
            return 0.5
    
    async def _calculate_noise_level(self, cv_image: np.ndarray) -> float:
        """Calculate noise level in the image"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Use standard deviation of Laplacian as noise measure
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            noise_level = np.std(laplacian)
            
            # Normalize to 0-1 scale
            normalized_noise = min(1.0, noise_level / 100)
            
            return float(normalized_noise)
            
        except Exception as e:
            self.logger.error(f"Noise calculation failed: {e}")
            return 0.5
    
    async def _calculate_exposure_level(self, cv_image: np.ndarray) -> float:
        """Calculate exposure level (0 = underexposed, 0.5 = optimal, 1 = overexposed)"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten()
            
            # Calculate exposure metrics
            underexposed_pixels = np.sum(hist[:25])  # Very dark pixels
            overexposed_pixels = np.sum(hist[230:])  # Very bright pixels
            total_pixels = np.sum(hist)
            
            underexposed_ratio = underexposed_pixels / total_pixels
            overexposed_ratio = overexposed_pixels / total_pixels
            
            # Calculate exposure score
            if underexposed_ratio > 0.1:
                exposure_level = 0.2  # Underexposed
            elif overexposed_ratio > 0.1:
                exposure_level = 0.8  # Overexposed
            else:
                # Well exposed - calculate based on mean brightness
                mean_brightness = np.mean(gray) / 255.0
                exposure_level = mean_brightness
            
            return float(exposure_level)
            
        except Exception as e:
            self.logger.error(f"Exposure calculation failed: {e}")
            return 0.5
    
    async def _calculate_aesthetic_score(self, image: Image.Image) -> float:
        """Calculate aesthetic score using rule of thirds and other composition rules"""        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            height, width = gray.shape
            score = 0.0
            
            # Rule of thirds analysis
            third_x = width // 3
            third_y = height // 3
            
            # Check if important features are near rule of thirds lines
            edges = cv2.Canny(gray, 100, 200)
            
            # Count edges near rule of thirds lines
            rule_of_thirds_edges = 0
            
            # Vertical lines
            for x in [third_x, 2 * third_x]:
                rule_of_thirds_edges += np.sum(edges[:, max(0, x-10):min(width, x+10)])
            
            # Horizontal lines
            for y in [third_y, 2 * third_y]:
                rule_of_thirds_edges += np.sum(edges[max(0, y-10):min(height, y+10), :])
            
            total_edges = np.sum(edges)
            if total_edges > 0:
                rule_of_thirds_score = min(1.0, rule_of_thirds_edges / total_edges * 10)
                score += rule_of_thirds_score * 0.3
            
            # Symmetry analysis
            left_half = gray[:, :width//2]
            right_half = cv2.flip(gray[:, width//2:], 1)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            symmetry_score = 1.0 - np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
            score += symmetry_score * 0.2
            
            # Color harmony (simplified)
            color_variance = np.var(cv_image.reshape(-1, 3), axis=0)
            color_harmony_score = 1.0 - np.mean(color_variance) / (255**2)
            score += color_harmony_score * 0.2
            
            # Contrast and brightness balance
            contrast = np.std(gray) / 255.0
            brightness = np.mean(gray) / 255.0
            
            # Optimal contrast and brightness
            contrast_score = min(1.0, contrast * 2)  # Higher contrast is generally better
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal brightness around 0.5
            
            score += contrast_score * 0.15
            score += brightness_score * 0.15
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Aesthetic score calculation failed: {e}")
            return 0.5
    
    async def _calculate_composition_score(self, cv_image: np.ndarray) -> float:
        """Calculate composition score based on visual balance and focal points"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Find focal points using corner detection
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=20, qualityLevel=0.01, minDistance=50)
            
            if corners is None:
                return 0.5
            
            # Calculate distribution of focal points
            corner_coords = corners.reshape(-1, 2)
            
            # Check if focal points follow golden ratio or rule of thirds
            golden_ratio = 0.618
            thirds = [width * 1/3, width * 2/3, height * 1/3, height * 2/3]
            golden_points = [width * golden_ratio, width * (1-golden_ratio), height * golden_ratio, height * (1-golden_ratio)]
            
            composition_score = 0.0
            
            # Score based on proximity to interesting points
            for x, y in corner_coords:
                # Distance to rule of thirds lines
                min_thirds_dist = min([abs(x - thirds[0]), abs(x - thirds[1]), abs(y - thirds[2]), abs(y - thirds[3])])
                thirds_score = max(0, 1.0 - min_thirds_dist / (width * 0.1))
                
                # Distance to golden ratio points
                min_golden_dist = min([abs(x - golden_points[0]), abs(x - golden_points[1]), 
                                     abs(y - golden_points[2]), abs(y - golden_points[3])])
                golden_score = max(0, 1.0 - min_golden_dist / (width * 0.1))
                
                composition_score += max(thirds_score, golden_score)
            
            # Normalize by number of focal points
            if len(corner_coords) > 0:
                composition_score /= len(corner_coords)
            
            return min(1.0, max(0.0, composition_score))
            
        except Exception as e:
            self.logger.error(f"Composition score calculation failed: {e}")
            return 0.5
    
    async def _calculate_technical_quality(self, cv_image: np.ndarray) -> float:
        """Calculate overall technical quality score"""        try:
            # Combine various technical metrics
            blur_level = await self._calculate_blur_level(cv_image)
            noise_level = await self._calculate_noise_level(cv_image)
            exposure_level = await self._calculate_exposure_level(cv_image)
            
            # Sharpness score (inverse of blur)
            sharpness_score = 1.0 - blur_level
            
            # Noise score (inverse of noise)
            noise_score = 1.0 - noise_level
            
            # Exposure score (distance from optimal 0.5)
            exposure_score = 1.0 - abs(exposure_level - 0.5) * 2
            
            # Calculate overall contrast
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            contrast_score = min(1.0, np.std(gray) / 128.0)
            
            # Weighted combination
            technical_quality = (
                sharpness_score * 0.3 +
                noise_score * 0.25 +
                exposure_score * 0.25 +
                contrast_score * 0.2
            )
            
            return min(1.0, max(0.0, technical_quality))
            
        except Exception as e:
            self.logger.error(f"Technical quality calculation failed: {e}")
            return 0.5
    
    async def _detect_artistic_style(self, image: Image.Image) -> str:
        """Detect artistic style of the image (simplified)"""        try:
            # This is a simplified style detection
            # In production, you'd use a trained style classification model
            
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate various image characteristics
            contrast = np.std(gray)
            brightness = np.mean(gray)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Simple style classification based on characteristics
            if edge_density > 0.1 and contrast > 60:
                return "detailed_realistic"
            elif edge_density < 0.05 and contrast < 30:
                return "soft_impressionistic"
            elif brightness < 80 and contrast > 50:
                return "dramatic_chiaroscuro"
            elif brightness > 180:
                return "high_key"
            elif brightness < 60:
                return "low_key"
            elif contrast > 80:
                return "high_contrast"
            else:
                return "natural"
                
        except Exception as e:
            self.logger.error(f"Artistic style detection failed: {e}")
            return "unknown"
    
    async def _generate_thumbnail(self, image: Image.Image) -> str:
        """Generate thumbnail and return as base64 string"""        try:
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(self.config.thumbnail_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            thumbnail.save(buffer, format='JPEG', quality=85)
            img_data = buffer.getvalue()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            return f"data:image/jpeg;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {e}")
            return ""
    
    async def _assess_quality(self, image: Image.Image) -> Dict[str, float]:
        """Assess overall image quality metrics"""        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Calculate individual quality metrics
            aesthetic_score = await self._calculate_aesthetic_score(image)
            technical_quality = await self._calculate_technical_quality(cv_image)
            composition_score = await self._calculate_composition_score(cv_image)
            
            # Calculate uniqueness score (simplified)
            # In production, this would compare against a database of known images
            uniqueness_score = 0.8  # Default assumption
            
            # Overall quality score
            quality_score = (
                aesthetic_score * 0.3 +
                technical_quality * 0.4 +
                composition_score * 0.3
            )
            
            return {
                "quality_score": quality_score,
                "aesthetic_score": aesthetic_score,
                "technical_quality": technical_quality,
                "composition_score": composition_score,
                "uniqueness_score": uniqueness_score
            }
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return {
                "quality_score": 0.5,
                "aesthetic_score": 0.5,
                "technical_quality": 0.5,
                "composition_score": 0.5,
                "uniqueness_score": 0.5
            }
    
    async def _generate_fingerprint(self, image: Image.Image) -> str:
        """Generate image fingerprint for content identification"""        try:
            # Create a standardized representation
            resized = image.resize((64, 64), Image.Resampling.LANCZOS)
            gray = resized.convert('L')
            
            # Convert to bytes and hash
            img_bytes = gray.tobytes()
            fingerprint = hashlib.sha256(img_bytes).hexdigest()[:32]
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation failed: {e}")
            return ""
    
    async def _generate_perceptual_hash(self, image: Image.Image) -> str:
        """Generate perceptual hash for similarity detection"""        try:
            # Use imagehash library for perceptual hashing
            phash = str(imagehash.phash(image))
            return phash
            
        except Exception as e:
            self.logger.error(f"Perceptual hash generation failed: {e}")
            return ""
    
    async def _generate_tags(
        self,
        metadata: ImageMetadata,
        features: Optional[ImageFeatures],
        quality_metrics: Dict[str, float]
    ) -> List[str]:
        """Generate relevant tags for the image content"""        tags = []
        
        try:
            # Format and technical tags
            tags.append(f"format-{metadata.format.lower()}")
            
            # Resolution tags
            if metadata.height >= 2160:
                tags.append("4k")
            elif metadata.height >= 1080:
                tags.append("full-hd")
            elif metadata.height >= 720:
                tags.append("hd")
            
            # Aspect ratio tags
            aspect_ratio = metadata.width / metadata.height if metadata.height > 0 else 1.0
            if abs(aspect_ratio - 1.0) < 0.1:
                tags.append("square")
            elif aspect_ratio > 1.5:
                tags.append("landscape")
            elif aspect_ratio < 0.8:
                tags.append("portrait")
            
            # Quality tags
            quality_score = quality_metrics.get("quality_score", 0.5)
            if quality_score > 0.8:
                tags.append("high-quality")
            elif quality_score < 0.4:
                tags.append("low-quality")
            
            # Feature-based tags
            if features:
                if len(features.faces_detected) > 0:
                    tags.append("people")
                    if len(features.faces_detected) == 1:
                        tags.append("portrait")
                    else:
                        tags.append("group")
                
                if len(features.objects_detected) > 5:
                    tags.append("complex-scene")
                
                if features.extracted_text:
                    tags.append("text")
                
                if features.color_analysis:
                    color_analysis = features.color_analysis
                    if color_analysis.brightness and color_analysis.brightness > 0.7:
                        tags.append("bright")
                    elif color_analysis.brightness and color_analysis.brightness < 0.3:
                        tags.append("dark")
                    
                    if color_analysis.saturation and color_analysis.saturation > 0.7:
                        tags.append("vibrant")
                    elif color_analysis.saturation and color_analysis.saturation < 0.3:
                        tags.append("muted")
                    
                    if color_analysis.color_mood:
                        tags.append(color_analysis.color_mood)
                
                if features.artistic_style:
                    tags.append(features.artistic_style)
            
            # Camera metadata tags
            if metadata.camera_make:
                tags.append(f"camera-{metadata.camera_make.lower().replace(' ', '-')}")
            
            # Transparency tag
            if metadata.has_transparency:
                tags.append("transparent")
            
            return tags
            
        except Exception as e:
            self.logger.error(f"Tag generation failed: {e}")
            return []
    
    async def _convert_format(
        self,
        image: Image.Image,
        target_format: ImageFormat,
        options: Dict[str, Any]
    ) -> bytes:
        """Convert image to target format"""        try:
            # Prepare image for conversion
            converted_image = image.copy()
            
            # Handle format-specific requirements
            if target_format in [ImageFormat.JPEG, ImageFormat.JPG]:
                if converted_image.mode in ('RGBA', 'LA'):
                    # Create white background for JPEG
                    background = Image.new('RGB', converted_image.size, (255, 255, 255))
                    background.paste(converted_image, mask=converted_image.split()[-1] if converted_image.mode == 'RGBA' else None)
                    converted_image = background
                elif converted_image.mode != 'RGB':
                    converted_image = converted_image.convert('RGB')
            
            elif target_format == ImageFormat.PNG:
                # PNG supports transparency
                if converted_image.mode not in ('RGBA', 'RGB', 'L', 'LA'):
                    converted_image = converted_image.convert('RGBA')
            
            # Apply resize if requested
            if "resize" in options:
                width, height = options["resize"]
                converted_image = converted_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            
            save_kwargs = {}
            if target_format in [ImageFormat.JPEG, ImageFormat.JPG]:
                save_kwargs['quality'] = options.get('quality', self.config.jpeg_quality)
                save_kwargs['optimize'] = True
            elif target_format == ImageFormat.PNG:
                save_kwargs['compress_level'] = options.get('compression', self.config.png_compression)
                save_kwargs['optimize'] = True
            elif target_format == ImageFormat.WEBP:
                save_kwargs['quality'] = options.get('quality', self.config.webp_quality)
                save_kwargs['method'] = 6
            
            converted_image.save(buffer, format=target_format.value.upper(), **save_kwargs)
            
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Format conversion failed: {e}")
            return b""
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the image processor"""        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "image_libs_available": IMAGE_LIBS_AVAILABLE,
            "ai_libs_available": AI_LIBS_AVAILABLE,
            "object_detector_loaded": self._object_detector is not None,
            "image_captioner_loaded": self._image_captioner is not None,
            "config": self.config.__dict__
        }


async def create_image_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> ImageProcessor:
    """    Factory function to create and initialize an image processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized ImageProcessor instance
    """    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = ImageProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in ImageProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = ImageProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
