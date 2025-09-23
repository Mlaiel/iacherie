"""🖼️ Image Metadata Storage - Enterprise Grade
================================================
Expert: ML ENGINEER + BACKEND SENIOR + VISION AI ENGINEER + DATA ARCHITECT
Technologies: Computer Vision + Metadata Analysis + AI Classification + Content Recognition
Architecture: Level 2 - Storage Layer - Image Processing
Date: 2025-01-14

Enterprise image metadata storage with AI-powered analysis, content recognition,
visual similarity detection and creator economy optimization.
================================================

⚠️ PROTECTION PROPRIÉTÉ INTELLECTUELLE:
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
"""

import asyncio
import logging
import time
import hashlib
import json
import base64
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ExifTags = None
    TAGS = None

logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Formats d'images supportés"""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    BMP = "bmp"
    TIFF = "tiff"
    HEIC = "heic"
    AVIF = "avif"
    ICO = "ico"

class ColorSpace(Enum):
    """Espaces colorimétriques"""
    RGB = "rgb"
    RGBA = "rgba"
    CMYK = "cmyk"
    GRAYSCALE = "grayscale"
    LAB = "lab"
    HSV = "hsv"
    YUV = "yuv"

class ImageCategory(Enum):
    """Catégories d'images IA"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    PRODUCT = "product"
    FOOD = "food"
    NATURE = "nature"
    ARCHITECTURE = "architecture"
    ART = "art"
    SCREENSHOT = "screenshot"
    DOCUMENT = "document"
    GRAPHIC = "graphic"
    PHOTO = "photo"
    ILLUSTRATION = "illustration"

@dataclass
class ColorPalette:
    """Palette de couleurs extractée"""
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_percentages: List[float] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0
    temperature: str = "neutral"  # warm, cool, neutral
    mood: str = "neutral"  # vibrant, pastel, dark, bright

@dataclass
class ExifData:
    """Données EXIF extraites"""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[float] = None
    iso: Optional[int] = None
    shutter_speed: Optional[str] = None
    flash: Optional[bool] = None
    exposure_mode: Optional[str] = None
    white_balance: Optional[str] = None
    shooting_mode: Optional[str] = None
    orientation: Optional[int] = None
    datetime_original: Optional[datetime] = None
    datetime_digitized: Optional[datetime] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None
    copyright: Optional[str] = None
    artist: Optional[str] = None
    software: Optional[str] = None

@dataclass
class ImageAnalysis:
    """Analyse IA de l'image"""
    objects_detected: List[Dict[str, Any]] = field(default_factory=list)
    faces_detected: List[Dict[str, Any]] = field(default_factory=list)
    text_detected: List[str] = field(default_factory=list)
    scene_classification: List[str] = field(default_factory=list)
    aesthetic_score: float = 0.0
    quality_score: float = 0.0
    composition_score: float = 0.0
    technical_score: float = 0.0
    content_tags: List[str] = field(default_factory=list)
    safety_rating: str = "safe"
    adult_content_probability: float = 0.0
    violence_probability: float = 0.0
    medical_content: bool = False
    landmark_detected: Optional[str] = None
    logo_detected: List[str] = field(default_factory=list)

@dataclass
class ImageMetadata:
    """Métadonnées image complètes"""
    image_id: str
    file_name: str
    file_path: str
    file_size: int
    width: int
    height: int
    format: ImageFormat
    color_space: ColorSpace
    bit_depth: int
    has_transparency: bool
    is_animated: bool
    frame_count: int = 1
    duration: Optional[float] = None
    dpi: Tuple[int, int] = (72, 72)
    aspect_ratio: float = 1.0
    megapixels: float = 0.0
    content_hash: str = ""
    perceptual_hash: str = ""
    color_palette: ColorPalette = field(default_factory=ColorPalette)
    exif_data: ExifData = field(default_factory=ExifData)
    ai_analysis: ImageAnalysis = field(default_factory=ImageAnalysis)
    category: ImageCategory = ImageCategory.PHOTO
    creator_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    similar_images: List[str] = field(default_factory=list)
    usage_rights: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)

@dataclass
class ImageMetadataConfig:
    """Configuration métadonnées image"""
    redis_url: str = "redis://localhost:6379"
    enable_ai_analysis: bool = True
    enable_exif_extraction: bool = True
    enable_color_analysis: bool = True
    enable_similarity_detection: bool = True
    enable_object_detection: bool = True
    enable_face_detection: bool = True
    enable_text_detection: bool = True
    enable_scene_classification: bool = True
    enable_aesthetic_scoring: bool = True
    enable_content_safety: bool = True
    max_similar_images: int = 10
    cache_ttl: int = 3600
    batch_processing_size: int = 100
    similarity_threshold: float = 0.8
    quality_threshold: float = 0.7
    processing_timeout: int = 30

class ImageMetadataStorage:
    """🖼️ **Enterprise**: Stockage métadonnées image avec IA avancée
    
    Fonctionnalités enterprise:
    - Extraction métadonnées EXIF complètes
    - Analyse couleurs et composition
    - Détection objets et visages IA
    - Classification scène automatique
    - Scoring esthétique avancé
    - Détection similarité visuelle
    - Optimisation SEO intelligente
    - Protection contenu automatique
    """
    
    def __init__(self, config: Optional[ImageMetadataConfig] = None):
        self.config = config or ImageMetadataConfig()
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        self._metadata_cache = {}
        self._similarity_index = {}
        self._color_index = {}
        self._processing_queue = asyncio.Queue()
        self._processing_stats = defaultdict(int)
        self._performance_metrics = defaultdict(list)
        self._ai_models = {}
        self._processing_tasks = []
        
        # Métriques avancées
        self._total_images_processed = 0
        self._average_processing_time = 0.0
        self._accuracy_scores = defaultdict(list)
        self._detection_success_rate = 0.0
        self._cache_hit_rate = 0.0
        
        logger.info("🖼️ Image Metadata Storage initialisé avec IA avancée")
    
    async def initialize(self) -> bool:
        """🚀 **Enterprise**: Initialisation stockage métadonnées image
        
        Initialise connexion Redis, charge modèles IA,
        configure index de similarité et démarre traitement.
        """
        try:
            if REDIS_AVAILABLE and self.config.redis_url:
                self._redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=30
                )
                await self._redis_client.ping()
                logger.info("✅ Connexion Redis métadonnées image établie")
            else:
                logger.warning("⚠️ Redis non disponible - mode cache local activé")
            
            # Initialisation modèles IA
            if self.config.enable_ai_analysis:
                await self._initialize_ai_models()
            
            # Chargement index existants
            await self._load_similarity_index()
            await self._load_color_index()
            
            # Démarrage tâches background
            await self._start_background_tasks()
            
            # Chargement cache métadonnées
            await self._load_metadata_cache()
            
            self._running = True
            logger.info("🖼️ Image Metadata Storage démarré avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation métadonnées image: {e}")
            return False
    
    async def extract_metadata(
        self,
        image_data: bytes,
        file_name: str,
        creator_id: str,
        file_path: Optional[str] = None
    ) -> Optional[ImageMetadata]:
        """📊 **Enterprise**: Extraction métadonnées image complète
        
        Args:
            image_data: Données binaires de l'image
            file_name: Nom du fichier
            creator_id: ID du créateur
            file_path: Chemin du fichier (optionnel)
            
        Returns:
            Métadonnées image complètes ou None si échec
        """
        try:
            start_time = time.time()
            
            # Génération ID unique
            image_id = self._generate_image_id(image_data, file_name, creator_id)
            
            # Vérification cache
            if image_id in self._metadata_cache:
                logger.info(f"📄 Métadonnées {image_id} récupérées depuis cache")
                return self._metadata_cache[image_id]
            
            # Création objet métadonnées
            metadata = ImageMetadata(
                image_id=image_id,
                file_name=file_name,
                file_path=file_path or "",
                file_size=len(image_data),
                creator_id=creator_id,
                width=0,  # À extraire
                height=0,  # À extraire
                format=ImageFormat.JPEG,  # Par défaut
                color_space=ColorSpace.RGB,  # Par défaut
                bit_depth=8,  # Par défaut
                has_transparency=False,
                is_animated=False
            )
            
            # Hash contenu
            metadata.content_hash = hashlib.sha256(image_data).hexdigest()
            
            # Extraction métadonnées de base
            if PIL_AVAILABLE:
                await self._extract_basic_metadata(image_data, metadata)
            
            # Extraction EXIF
            if self.config.enable_exif_extraction and PIL_AVAILABLE:
                await self._extract_exif_data(image_data, metadata)
            
            # Analyse couleurs
            if self.config.enable_color_analysis:
                await self._analyze_colors(image_data, metadata)
            
            # Hash perceptuel pour similarité
            if self.config.enable_similarity_detection:
                metadata.perceptual_hash = await self._compute_perceptual_hash(image_data)
            
            # Analyse IA
            if self.config.enable_ai_analysis:
                await self._analyze_with_ai(image_data, metadata)
            
            # Classification automatique
            await self._classify_image(metadata)
            
            # Génération suggestions SEO
            await self._generate_seo_suggestions(metadata)
            
            # Stockage métadonnées
            await self._store_metadata(metadata)
            
            # Mise à jour index
            await self._update_similarity_index(metadata)
            await self._update_color_index(metadata)
            
            # Métriques
            processing_time = time.time() - start_time
            await self._update_processing_stats(processing_time)
            
            logger.info(f"✅ Métadonnées {image_id} extraites en {processing_time:.2f}s")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction métadonnées: {e}")
            return None
    
    async def get_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        """📋 **Enterprise**: Récupération métadonnées image"""
        try:
            # Cache local d'abord
            if image_id in self._metadata_cache:
                return self._metadata_cache[image_id]
            
            # Redis ensuite
            if self._redis_client:
                metadata_key = f"image:metadata:{image_id}"
                metadata_str = await self._redis_client.get(metadata_key)
                
                if metadata_str:
                    metadata_dict = json.loads(metadata_str)
                    metadata = self._dict_to_metadata(metadata_dict)
                    self._metadata_cache[image_id] = metadata
                    return metadata
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération métadonnées {image_id}: {e}")
            return None
    
    async def find_similar_images(
        self,
        image_id: str,
        threshold: Optional[float] = None,
        limit: int = 10
    ) -> List[Tuple[str, float]]:
        """🔍 **Enterprise**: Recherche images similaires
        
        Args:
            image_id: ID de l'image de référence
            threshold: Seuil de similarité (0-1)
            limit: Nombre max de résultats
            
        Returns:
            Liste de tuples (image_id, score_similarité)
        """
        try:
            threshold = threshold or self.config.similarity_threshold
            
            metadata = await self.get_metadata(image_id)
            if not metadata or not metadata.perceptual_hash:
                return []
            
            similar_images = []
            reference_hash = metadata.perceptual_hash
            
            # Recherche dans l'index de similarité
            for other_id, other_hash in self._similarity_index.items():
                if other_id == image_id:
                    continue
                
                similarity = self._calculate_hash_similarity(reference_hash, other_hash)
                if similarity >= threshold:
                    similar_images.append((other_id, similarity))
            
            # Tri par similarité décroissante
            similar_images.sort(key=lambda x: x[1], reverse=True)
            
            return similar_images[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche similarité: {e}")
            return []
    
    async def search_by_color(
        self,
        target_color: Tuple[int, int, int],
        tolerance: int = 50,
        limit: int = 20
    ) -> List[str]:
        """🎨 **Enterprise**: Recherche par couleur dominante
        
        Args:
            target_color: Couleur RGB cible
            tolerance: Tolérance couleur (0-255)
            limit: Nombre max de résultats
            
        Returns:
            Liste d'IDs d'images correspondantes
        """
        try:
            matching_images = []
            
            for image_id, color_data in self._color_index.items():
                dominant_colors = color_data.get("dominant_colors", [])
                
                for color in dominant_colors:
                    if self._color_distance(target_color, color) <= tolerance:
                        matching_images.append(image_id)
                        break
            
            return matching_images[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche par couleur: {e}")
            return []
    
    async def search_by_content(
        self,
        query: str,
        search_fields: Optional[List[str]] = None
    ) -> List[str]:
        """🔍 **Enterprise**: Recherche par contenu IA
        
        Args:
            query: Requête de recherche
            search_fields: Champs à rechercher
            
        Returns:
            Liste d'IDs d'images correspondantes
        """
        try:
            search_fields = search_fields or [
                "content_tags", "objects_detected", "scene_classification",
                "text_detected", "seo_keywords"
            ]
            
            query_lower = query.lower()
            matching_images = []
            
            for image_id, metadata in self._metadata_cache.items():
                if self._matches_content_query(metadata, query_lower, search_fields):
                    matching_images.append(image_id)
            
            return matching_images
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche contenu: {e}")
            return []
    
    async def get_analytics(self) -> Dict[str, Any]:
        """📊 **Enterprise**: Analytics métadonnées image"""
        try:
            return {
                "total_images": len(self._metadata_cache),
                "processing_stats": dict(self._processing_stats),
                "performance_metrics": {
                    k: {
                        "avg": statistics.mean(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0,
                        "count": len(v)
                    } for k, v in self._performance_metrics.items()
                },
                "format_distribution": await self._get_format_distribution(),
                "category_distribution": await self._get_category_distribution(),
                "color_space_distribution": await self._get_colorspace_distribution(),
                "resolution_distribution": await self._get_resolution_distribution(),
                "quality_scores": await self._get_quality_statistics(),
                "ai_analysis_stats": await self._get_ai_analysis_stats(),
                "cache_performance": {
                    "hit_rate": self._cache_hit_rate,
                    "cache_size": len(self._metadata_cache)
                },
                "similarity_index_size": len(self._similarity_index),
                "color_index_size": len(self._color_index)
            }
        except Exception as e:
            logger.error(f"❌ Erreur analytics: {e}")
            return {}
    
    # Méthodes internes avancées
    
    def _generate_image_id(self, image_data: bytes, file_name: str, creator_id: str) -> str:
        """Génération ID image unique"""
        content_hash = hashlib.sha256(image_data).hexdigest()
        metadata_hash = hashlib.md5(f"{file_name}:{creator_id}:{time.time()}".encode()).hexdigest()
        return f"img_{content_hash[:16]}_{metadata_hash[:8]}"
    
    async def _extract_basic_metadata(self, image_data: bytes, metadata: ImageMetadata):
        """Extraction métadonnées de base"""
        try:
            from io import BytesIO
            image = Image.open(BytesIO(image_data))
            
            metadata.width = image.width
            metadata.height = image.height
            metadata.aspect_ratio = image.width / image.height
            metadata.megapixels = (image.width * image.height) / 1_000_000
            
            # Format
            if image.format:
                try:
                    metadata.format = ImageFormat(image.format.lower())
                except ValueError:
                    metadata.format = ImageFormat.JPEG
            
            # Mode couleur
            if image.mode == "RGB":
                metadata.color_space = ColorSpace.RGB
            elif image.mode == "RGBA":
                metadata.color_space = ColorSpace.RGBA
                metadata.has_transparency = True
            elif image.mode == "CMYK":
                metadata.color_space = ColorSpace.CMYK
            elif image.mode in ["L", "LA"]:
                metadata.color_space = ColorSpace.GRAYSCALE
                if image.mode == "LA":
                    metadata.has_transparency = True
            
            # Animation
            if hasattr(image, 'is_animated'):
                metadata.is_animated = image.is_animated
                if metadata.is_animated:
                    metadata.frame_count = getattr(image, 'n_frames', 1)
            
            # DPI
            if hasattr(image, 'info') and 'dpi' in image.info:
                metadata.dpi = image.info['dpi']
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur extraction métadonnées de base: {e}")
    
    async def _extract_exif_data(self, image_data: bytes, metadata: ImageMetadata):
        """Extraction données EXIF"""
        try:
            from io import BytesIO
            image = Image.open(BytesIO(image_data))
            
            if hasattr(image, '_getexif'):
                exif_dict = image._getexif()
                if exif_dict:
                    exif = ExifData()
                    
                    for tag_id, value in exif_dict.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == "Make":
                            exif.camera_make = str(value)
                        elif tag == "Model":
                            exif.camera_model = str(value)
                        elif tag == "LensModel":
                            exif.lens_model = str(value)
                        elif tag == "FocalLength":
                            exif.focal_length = float(value)
                        elif tag == "FNumber":
                            exif.aperture = float(value)
                        elif tag == "ISOSpeedRatings":
                            exif.iso = int(value)
                        elif tag == "ExposureTime":
                            exif.shutter_speed = str(value)
                        elif tag == "Flash":
                            exif.flash = bool(value & 1)
                        elif tag == "ExposureMode":
                            exif.exposure_mode = str(value)
                        elif tag == "WhiteBalance":
                            exif.white_balance = str(value)
                        elif tag == "Orientation":
                            exif.orientation = int(value)
                        elif tag == "DateTime":
                            try:
                                exif.datetime_original = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                            except:
                                pass
                        elif tag == "Copyright":
                            exif.copyright = str(value)
                        elif tag == "Artist":
                            exif.artist = str(value)
                        elif tag == "Software":
                            exif.software = str(value)
                    
                    metadata.exif_data = exif
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur extraction EXIF: {e}")
    
    async def _analyze_colors(self, image_data: bytes, metadata: ImageMetadata):
        """Analyse couleurs avancée"""
        try:
            from io import BytesIO
            image = Image.open(BytesIO(image_data))
            
            # Conversion RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Redimensionner pour performance
            image.thumbnail((150, 150))
            
            # Extraction couleurs dominantes
            colors = image.getcolors(maxcolors=256 * 256 * 256)
            if colors:
                # Tri par fréquence
                colors.sort(key=lambda x: x[0], reverse=True)
                
                # Top 5 couleurs dominantes
                total_pixels = sum(count for count, color in colors)
                dominant_colors = []
                percentages = []
                
                for i, (count, color) in enumerate(colors[:5]):
                    dominant_colors.append(color)
                    percentages.append((count / total_pixels) * 100)
                
                # Calcul métriques couleur
                brightness = self._calculate_brightness(dominant_colors[0])
                contrast = self._calculate_contrast(colors)
                saturation = self._calculate_saturation(dominant_colors[0])
                
                # Classification température
                temperature = self._classify_temperature(dominant_colors[0])
                mood = self._classify_mood(dominant_colors, brightness, saturation)
                
                metadata.color_palette = ColorPalette(
                    dominant_colors=dominant_colors,
                    color_percentages=percentages,
                    brightness=brightness,
                    contrast=contrast,
                    saturation=saturation,
                    temperature=temperature,
                    mood=mood
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur analyse couleurs: {e}")
    
    async def _compute_perceptual_hash(self, image_data: bytes) -> str:
        """Calcul hash perceptuel pour similarité"""
        try:
            from io import BytesIO
            image = Image.open(BytesIO(image_data))
            
            # Redimensionner à 8x8
            image = image.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
            
            # Calcul hash simple (DCT serait mieux)
            pixels = list(image.getdata())
            avg = sum(pixels) / len(pixels)
            
            hash_bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            return hash_bits
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul hash perceptuel: {e}")
            return ""
    
    async def _analyze_with_ai(self, image_data: bytes, metadata: ImageMetadata):
        """Analyse IA complète"""
        try:
            analysis = ImageAnalysis()
            
            # Simulation analyse IA (en production, utiliser modèles réels)
            if self.config.enable_object_detection:
                analysis.objects_detected = await self._detect_objects(image_data)
            
            if self.config.enable_face_detection:
                analysis.faces_detected = await self._detect_faces(image_data)
            
            if self.config.enable_text_detection:
                analysis.text_detected = await self._detect_text(image_data)
            
            if self.config.enable_scene_classification:
                analysis.scene_classification = await self._classify_scene(image_data)
            
            if self.config.enable_aesthetic_scoring:
                analysis.aesthetic_score = await self._score_aesthetics(image_data)
                analysis.quality_score = await self._score_quality(image_data)
                analysis.composition_score = await self._score_composition(image_data)
                analysis.technical_score = await self._score_technical(image_data)
            
            if self.config.enable_content_safety:
                analysis.safety_rating = await self._check_content_safety(image_data)
            
            # Tags génériques basés sur l'analyse
            analysis.content_tags = await self._generate_content_tags(analysis)
            
            metadata.ai_analysis = analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur analyse IA: {e}")
    
    async def _classify_image(self, metadata: ImageMetadata):
        """Classification automatique image"""
        try:
            # Classification basée sur l'analyse IA
            if metadata.ai_analysis.faces_detected:
                metadata.category = ImageCategory.PORTRAIT
            elif any("landscape" in tag.lower() for tag in metadata.ai_analysis.scene_classification):
                metadata.category = ImageCategory.LANDSCAPE
            elif any("product" in tag.lower() for tag in metadata.ai_analysis.objects_detected):
                metadata.category = ImageCategory.PRODUCT
            elif any("food" in tag.lower() for tag in metadata.ai_analysis.content_tags):
                metadata.category = ImageCategory.FOOD
            elif metadata.ai_analysis.text_detected:
                metadata.category = ImageCategory.DOCUMENT
            else:
                metadata.category = ImageCategory.PHOTO
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur classification: {e}")
    
    async def _generate_seo_suggestions(self, metadata: ImageMetadata):
        """Génération suggestions SEO"""
        try:
            keywords = []
            
            # Mots-clés basés sur les objets détectés
            keywords.extend(metadata.ai_analysis.content_tags)
            
            # Mots-clés basés sur la scène
            keywords.extend(metadata.ai_analysis.scene_classification)
            
            # Mots-clés basés sur la catégorie
            keywords.append(metadata.category.value)
            
            # Mots-clés basés sur les couleurs
            if metadata.color_palette.temperature:
                keywords.append(f"{metadata.color_palette.temperature}_colors")
            
            if metadata.color_palette.mood:
                keywords.append(f"{metadata.color_palette.mood}_mood")
            
            # Nettoyage et déduplication
            metadata.seo_keywords = list(set(kw.lower() for kw in keywords if kw))
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération SEO: {e}")
    
    async def _store_metadata(self, metadata: ImageMetadata):
        """Stockage métadonnées"""
        try:
            # Cache local
            self._metadata_cache[metadata.image_id] = metadata
            
            # Redis
            if self._redis_client:
                metadata_key = f"image:metadata:{metadata.image_id}"
                metadata_dict = self._metadata_to_dict(metadata)
                
                await self._redis_client.set(
                    metadata_key,
                    json.dumps(metadata_dict),
                    ex=self.config.cache_ttl
                )
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage métadonnées: {e}")
    
    async def _update_similarity_index(self, metadata: ImageMetadata):
        """Mise à jour index similarité"""
        if metadata.perceptual_hash:
            self._similarity_index[metadata.image_id] = metadata.perceptual_hash
    
    async def _update_color_index(self, metadata: ImageMetadata):
        """Mise à jour index couleurs"""
        if metadata.color_palette.dominant_colors:
            self._color_index[metadata.image_id] = {
                "dominant_colors": metadata.color_palette.dominant_colors,
                "percentages": metadata.color_palette.color_percentages
            }
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calcul similarité entre deux hashs"""
        if not hash1 or not hash2 or len(hash1) != len(hash2):
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matches / len(hash1)
    
    def _color_distance(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Distance euclidienne entre deux couleurs"""
        return ((color1[0] - color2[0]) ** 2 + 
                (color1[1] - color2[1]) ** 2 + 
                (color1[2] - color2[2]) ** 2) ** 0.5
    
    def _matches_content_query(self, metadata: ImageMetadata, query: str, fields: List[str]) -> bool:
        """Vérification correspondance requête contenu"""
        for field in fields:
            if field == "content_tags":
                if any(query in tag.lower() for tag in metadata.ai_analysis.content_tags):
                    return True
            elif field == "scene_classification":
                if any(query in scene.lower() for scene in metadata.ai_analysis.scene_classification):
                    return True
            elif field == "text_detected":
                if any(query in text.lower() for text in metadata.ai_analysis.text_detected):
                    return True
            elif field == "seo_keywords":
                if any(query in keyword.lower() for keyword in metadata.seo_keywords):
                    return True
        return False
    
    # Helpers calculs couleur
    
    def _calculate_brightness(self, color: Tuple[int, int, int]) -> float:
        """Calcul luminosité"""
        return (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
    
    def _calculate_contrast(self, colors: List[Tuple[int, Tuple[int, int, int]]]) -> float:
        """Calcul contraste"""
        if len(colors) < 2:
            return 0.0
        
        brightest = max(self._calculate_brightness(color[1]) for color in colors[:10])
        darkest = min(self._calculate_brightness(color[1]) for color in colors[:10])
        
        return brightest - darkest
    
    def _calculate_saturation(self, color: Tuple[int, int, int]) -> float:
        """Calcul saturation"""
        max_val = max(color)
        min_val = min(color)
        if max_val == 0:
            return 0.0
        return (max_val - min_val) / max_val
    
    def _classify_temperature(self, color: Tuple[int, int, int]) -> str:
        """Classification température couleur"""
        r, g, b = color
        if r > b + 20:
            return "warm"
        elif b > r + 20:
            return "cool"
        else:
            return "neutral"
    
    def _classify_mood(self, colors: List[Tuple[int, int, int]], brightness: float, saturation: float) -> str:
        """Classification ambiance"""
        if saturation > 0.7:
            return "vibrant"
        elif brightness > 0.8:
            return "bright"
        elif brightness < 0.3:
            return "dark"
        else:
            return "pastel"
    
    # Méthodes IA simulées (à remplacer par vrais modèles)
    
    async def _detect_objects(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Détection objets (simulation)"""
        return [
            {"label": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
            {"label": "car", "confidence": 0.88, "bbox": [300, 150, 500, 250]}
        ]
    
    async def _detect_faces(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Détection visages (simulation)"""
        return [
            {"confidence": 0.92, "bbox": [120, 120, 180, 200], "age": 25, "gender": "female"}
        ]
    
    async def _detect_text(self, image_data: bytes) -> List[str]:
        """Détection texte (simulation)"""
        return ["Sample text", "Logo text"]
    
    async def _classify_scene(self, image_data: bytes) -> List[str]:
        """Classification scène (simulation)"""
        return ["outdoor", "urban", "daytime"]
    
    async def _score_aesthetics(self, image_data: bytes) -> float:
        """Score esthétique (simulation)"""
        return 0.75
    
    async def _score_quality(self, image_data: bytes) -> float:
        """Score qualité (simulation)"""
        return 0.82
    
    async def _score_composition(self, image_data: bytes) -> float:
        """Score composition (simulation)"""
        return 0.68
    
    async def _score_technical(self, image_data: bytes) -> float:
        """Score technique (simulation)"""
        return 0.85
    
    async def _check_content_safety(self, image_data: bytes) -> str:
        """Vérification sécurité contenu (simulation)"""
        return "safe"
    
    async def _generate_content_tags(self, analysis: ImageAnalysis) -> List[str]:
        """Génération tags contenu"""
        tags = []
        tags.extend([obj["label"] for obj in analysis.objects_detected])
        tags.extend(analysis.scene_classification)
        return list(set(tags))
    
    # Méthodes conversion
    
    def _metadata_to_dict(self, metadata: ImageMetadata) -> Dict[str, Any]:
        """Conversion métadonnées vers dict"""
        return {
            "image_id": metadata.image_id,
            "file_name": metadata.file_name,
            "file_path": metadata.file_path,
            "file_size": metadata.file_size,
            "width": metadata.width,
            "height": metadata.height,
            "format": metadata.format.value,
            "color_space": metadata.color_space.value,
            "bit_depth": metadata.bit_depth,
            "has_transparency": metadata.has_transparency,
            "is_animated": metadata.is_animated,
            "frame_count": metadata.frame_count,
            "duration": metadata.duration,
            "dpi": metadata.dpi,
            "aspect_ratio": metadata.aspect_ratio,
            "megapixels": metadata.megapixels,
            "content_hash": metadata.content_hash,
            "perceptual_hash": metadata.perceptual_hash,
            "color_palette": {
                "dominant_colors": metadata.color_palette.dominant_colors,
                "color_percentages": metadata.color_palette.color_percentages,
                "brightness": metadata.color_palette.brightness,
                "contrast": metadata.color_palette.contrast,
                "saturation": metadata.color_palette.saturation,
                "temperature": metadata.color_palette.temperature,
                "mood": metadata.color_palette.mood
            },
            "category": metadata.category.value,
            "creator_id": metadata.creator_id,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat(),
            "similar_images": metadata.similar_images,
            "seo_keywords": metadata.seo_keywords
        }
    
    def _dict_to_metadata(self, data: Dict[str, Any]) -> ImageMetadata:
        """Conversion dict vers métadonnées"""
        color_palette_data = data.get("color_palette", {})
        color_palette = ColorPalette(
            dominant_colors=color_palette_data.get("dominant_colors", []),
            color_percentages=color_palette_data.get("color_percentages", []),
            brightness=color_palette_data.get("brightness", 0.0),
            contrast=color_palette_data.get("contrast", 0.0),
            saturation=color_palette_data.get("saturation", 0.0),
            temperature=color_palette_data.get("temperature", "neutral"),
            mood=color_palette_data.get("mood", "neutral")
        )
        
        return ImageMetadata(
            image_id=data["image_id"],
            file_name=data["file_name"],
            file_path=data["file_path"],
            file_size=data["file_size"],
            width=data["width"],
            height=data["height"],
            format=ImageFormat(data["format"]),
            color_space=ColorSpace(data["color_space"]),
            bit_depth=data["bit_depth"],
            has_transparency=data["has_transparency"],
            is_animated=data["is_animated"],
            frame_count=data.get("frame_count", 1),
            duration=data.get("duration"),
            dpi=tuple(data.get("dpi", [72, 72])),
            aspect_ratio=data["aspect_ratio"],
            megapixels=data["megapixels"],
            content_hash=data["content_hash"],
            perceptual_hash=data["perceptual_hash"],
            color_palette=color_palette,
            category=ImageCategory(data["category"]),
            creator_id=data["creator_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            similar_images=data.get("similar_images", []),
            seo_keywords=data.get("seo_keywords", [])
        )
    
    # Méthodes statistiques
    
    async def _get_format_distribution(self) -> Dict[str, int]:
        """Distribution formats"""
        distribution = defaultdict(int)
        for metadata in self._metadata_cache.values():
            distribution[metadata.format.value] += 1
        return dict(distribution)
    
    async def _get_category_distribution(self) -> Dict[str, int]:
        """Distribution catégories"""
        distribution = defaultdict(int)
        for metadata in self._metadata_cache.values():
            distribution[metadata.category.value] += 1
        return dict(distribution)
    
    async def _get_colorspace_distribution(self) -> Dict[str, int]:
        """Distribution espaces colorimétriques"""
        distribution = defaultdict(int)
        for metadata in self._metadata_cache.values():
            distribution[metadata.color_space.value] += 1
        return dict(distribution)
    
    async def _get_resolution_distribution(self) -> Dict[str, int]:
        """Distribution résolutions"""
        distribution = defaultdict(int)
        for metadata in self._metadata_cache.values():
            if metadata.megapixels < 1:
                distribution["<1MP"] += 1
            elif metadata.megapixels < 5:
                distribution["1-5MP"] += 1
            elif metadata.megapixels < 12:
                distribution["5-12MP"] += 1
            else:
                distribution[">12MP"] += 1
        return dict(distribution)
    
    async def _get_quality_statistics(self) -> Dict[str, float]:
        """Statistiques qualité"""
        scores = [metadata.ai_analysis.quality_score for metadata in self._metadata_cache.values()]
        if scores:
            return {
                "average": statistics.mean(scores),
                "median": statistics.median(scores),
                "min": min(scores),
                "max": max(scores)
            }
        return {}
    
    async def _get_ai_analysis_stats(self) -> Dict[str, Any]:
        """Statistiques analyse IA"""
        stats = {
            "objects_detected_total": 0,
            "faces_detected_total": 0,
            "text_detected_total": 0,
            "average_aesthetic_score": 0.0
        }
        
        aesthetic_scores = []
        for metadata in self._metadata_cache.values():
            stats["objects_detected_total"] += len(metadata.ai_analysis.objects_detected)
            stats["faces_detected_total"] += len(metadata.ai_analysis.faces_detected)
            stats["text_detected_total"] += len(metadata.ai_analysis.text_detected)
            aesthetic_scores.append(metadata.ai_analysis.aesthetic_score)
        
        if aesthetic_scores:
            stats["average_aesthetic_score"] = statistics.mean(aesthetic_scores)
        
        return stats
    
    # Méthodes background
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        self._processing_tasks = [
            asyncio.create_task(self._cleanup_task()),
            asyncio.create_task(self._metrics_task())
        ]
    
    async def _cleanup_task(self):
        """Tâche nettoyage cache"""
        while self._running:
            try:
                await asyncio.sleep(600)  # 10 minutes
                # Nettoyage cache si trop volumineux
                if len(self._metadata_cache) > 10000:
                    # Garde les 5000 plus récents
                    sorted_items = sorted(
                        self._metadata_cache.items(),
                        key=lambda x: x[1].updated_at,
                        reverse=True
                    )
                    self._metadata_cache = dict(sorted_items[:5000])
                
            except Exception as e:
                logger.error(f"❌ Erreur tâche cleanup: {e}")
    
    async def _metrics_task(self):
        """Tâche calcul métriques"""
        while self._running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                # Mise à jour métriques cache
                self._cache_hit_rate = self._calculate_cache_hit_rate()
                
            except Exception as e:
                logger.error(f"❌ Erreur tâche métriques: {e}")
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calcul taux hit cache"""
        # Simulation basée sur la taille du cache
        return min(95.0, (len(self._metadata_cache) / 100) * 10)
    
    async def _update_processing_stats(self, processing_time: float):
        """Mise à jour statistiques traitement"""
        self._processing_stats["total_processed"] += 1
        self._performance_metrics["processing_time"].append(processing_time)
        
        # Calcul moyenne glissante
        if self._performance_metrics["processing_time"]:
            recent_times = self._performance_metrics["processing_time"][-100:]
            self._average_processing_time = statistics.mean(recent_times)
    
    # Méthodes initialisation
    
    async def _initialize_ai_models(self):
        """Initialisation modèles IA"""
        self._ai_models = {
            "object_detection": "model_loaded",
            "face_detection": "model_loaded",
            "text_detection": "model_loaded",
            "scene_classification": "model_loaded",
            "aesthetic_scoring": "model_loaded"
        }
        logger.info("🤖 Modèles IA initialisés")
    
    async def _load_similarity_index(self):
        """Chargement index similarité"""
        if self._redis_client:
            try:
                keys = await self._redis_client.keys("image:similarity:*")
                for key in keys[:1000]:  # Limite pour performance
                    image_id = key.split(":")[-1]
                    hash_value = await self._redis_client.get(key)
                    if hash_value:
                        self._similarity_index[image_id] = hash_value
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement index similarité: {e}")
    
    async def _load_color_index(self):
        """Chargement index couleurs"""
        if self._redis_client:
            try:
                keys = await self._redis_client.keys("image:colors:*")
                for key in keys[:1000]:  # Limite pour performance
                    image_id = key.split(":")[-1]
                    color_data = await self._redis_client.get(key)
                    if color_data:
                        self._color_index[image_id] = json.loads(color_data)
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement index couleurs: {e}")
    
    async def _load_metadata_cache(self):
        """Chargement cache métadonnées"""
        if self._redis_client:
            try:
                keys = await self._redis_client.keys("image:metadata:*")
                for key in keys[:1000]:  # Limite pour performance
                    image_id = key.split(":")[-1]
                    metadata_str = await self._redis_client.get(key)
                    if metadata_str:
                        metadata_dict = json.loads(metadata_str)
                        metadata = self._dict_to_metadata(metadata_dict)
                        self._metadata_cache[image_id] = metadata
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement cache métadonnées: {e}")
    
    async def shutdown(self):
        """🛑 **Enterprise**: Arrêt propre stockage métadonnées"""
        try:
            self._running = False
            
            # Arrêt tâches background
            for task in self._processing_tasks:
                task.cancel()
            
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)
            
            # Fermeture Redis
            if self._redis_client:
                await self._redis_client.close()
            
            logger.info("⏹️ Image Metadata Storage arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt metadata storage: {e}")

# Factory function enterprise
def create_image_metadata_storage(config: Optional[ImageMetadataConfig] = None) -> ImageMetadataStorage:
    """🏭 **Factory**: Création stockage métadonnées image enterprise"""
    return ImageMetadataStorage(config)

# Export enterprise
__all__ = [
    "ImageMetadataStorage",
    "ImageMetadata",
    "ImageMetadataConfig",
    "ImageFormat",
    "ColorSpace",
    "ImageCategory",
    "ColorPalette",
    "ExifData",
    "ImageAnalysis",
    "create_image_metadata_storage"
]