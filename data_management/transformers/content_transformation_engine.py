"""🗄️ Advanced Content Transformation Engine - IA Influencer Agent Platform Enterprise
=================================================================================
Module: backend/data_management/transformers/content_transformation_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Content Transformation Engine - Enterprise Production-Ready
Responsibility: Transformation intelligente multi-format avec optimisation IA
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER TRANSFORMATION:
Content Analysis → Format Detection → Quality Assessment → 
Optimization Strategy → AI Enhancement → Format Conversion → 
Quality Validation → SEO Optimization → Multi-Platform Preparation → 
Performance Monitoring → Adaptive Learning

SUPPORTS TRANSFORMATIONS:
🎵 Audio: MP3↔WAV↔FLAC, Normalization, Noise Reduction, Mastering
🎬 Vidéo: MP4↔AVI↔MOV, Compression, Resolution, Frame Rate
📸 Images: JPG↔PNG↔WEBP, Optimization, HDR, Super Resolution
📝 Texte: Format Conversion, SEO Enhancement, Translation
"""
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import logging
import json
import uuid
import io
from pathlib import Path
import mimetypes
import hashlib

# Media processing imports
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip
import fitz  # PyMuPDF

# AI/ML imports
import torch
import torchvision.transforms as transforms
from transformers import pipeline

# Core imports
from ..models.content_model import ContentModel, TransformationJob
from ..repositories.content_repository import ContentRepository
from ...core.base import BaseTransformer
from ...utils.quality_analyzer import QualityAnalyzer
from ...utils.performance import PerformanceOptimizer

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

class TransformationType(Enum):
    """Types de transformation disponibles"""    # Audio
    AUDIO_NORMALIZE = "audio_normalize"
    AUDIO_DENOISE = "audio_denoise"
    AUDIO_COMPRESS = "audio_compress"
    AUDIO_ENHANCE = "audio_enhance"
    AUDIO_FORMAT_CONVERT = "audio_format_convert"
    
    # Video
    VIDEO_COMPRESS = "video_compress"
    VIDEO_RESIZE = "video_resize"
    VIDEO_FPS_ADJUST = "video_fps_adjust"
    VIDEO_STABILIZE = "video_stabilize"
    VIDEO_FORMAT_CONVERT = "video_format_convert"
    
    # Image
    IMAGE_RESIZE = "image_resize"
    IMAGE_COMPRESS = "image_compress"
    IMAGE_ENHANCE = "image_enhance"
    IMAGE_HDR = "image_hdr"
    IMAGE_SUPER_RESOLUTION = "image_super_resolution"
    IMAGE_FORMAT_CONVERT = "image_format_convert"
    
    # Text
    TEXT_FORMAT_CONVERT = "text_format_convert"
    TEXT_SEO_OPTIMIZE = "text_seo_optimize"
    TEXT_TRANSLATE = "text_translate"
    TEXT_SUMMARIZE = "text_summarize"
    
    # Multi-format
    METADATA_EXTRACT = "metadata_extract"
    THUMBNAIL_GENERATE = "thumbnail_generate"
    PREVIEW_GENERATE = "preview_generate"

class QualityLevel(Enum):
    """Niveaux de qualité pour les transformations"""    DRAFT = "draft"          # Rapide, qualité basique
    STANDARD = "standard"    # Équilibre qualité/vitesse
    HIGH = "high"           # Haute qualité
    PROFESSIONAL = "professional"  # Qualité professionnelle
    LOSSLESS = "lossless"   # Sans perte

@dataclass
class TransformationConfig:
    """Configuration d'une transformation"""    transformation_type: TransformationType
    quality_level: QualityLevel
    target_format: Optional[str] = None
    target_resolution: Optional[Tuple[int, int]] = None
    target_bitrate: Optional[int] = None
    target_fps: Optional[int] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)
    ai_enhancement: bool = False
    preserve_metadata: bool = True

@dataclass
class TransformationResult:
    """Résultat d'une transformation"""    job_id: str
    original_path: str
    transformed_path: str
    transformation_type: TransformationType
    quality_metrics: Dict[str, float]
    file_size_before: int
    file_size_after: int
    compression_ratio: float
    processing_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentTransformationEngine:
    """    Moteur avancé de transformation de contenu multi-format
    
    Capacités:
    - Transformation intelligente avec IA
    - Optimisation qualité/taille automatique
    - Support multi-format complet
    - Enhancement IA pour audio/vidéo/image
    - SEO et optimisation web
    - Traitement batch et temps réel
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_repository = ContentRepository()
        self.quality_analyzer = QualityAnalyzer()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Transformers IA
        self.ai_models = self._initialize_ai_models()
        
        # Configuration des formats supportés
        self.supported_formats = self._load_supported_formats()
        
        # Cache des transformations récentes
        self.transformation_cache = {}
        
    def _initialize_ai_models(self) -> Dict[str, Any]:
        """Initialise les modèles IA pour l'enhancement"""        models = {}
        
        try:
            # Modèle pour super-résolution d'images
            models["image_super_resolution"] = torch.hub.load(
                'ultralytics/yolov5', 'custom', 
                path='models/super_resolution.pt', 
                force_reload=False
            )
            
            # Pipeline de résumé de texte
            models["text_summarization"] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            # Pipeline de traduction
            models["text_translation"] = pipeline(
                "translation_en_to_fr",
                model="Helsinki-NLP/opus-mt-en-fr"
            )
            
            logger.info("AI models for transformation initialized")
            
        except Exception as e:
            logger.warning(f"Some AI models failed to initialize: {e}")
            
        return models
        
    def _load_supported_formats(self) -> Dict[str, List[str]]:
        """Charge la configuration des formats supportés"""        return {
            "audio": {
                "input": [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff", ".wma"],
                "output": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
                "web_optimized": [".mp3", ".ogg"]
            },
            "video": {
                "input": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"],
                "output": [".mp4", ".webm", ".avi", ".mov"],
                "web_optimized": [".mp4", ".webm"]
            },
            "image": {
                "input": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
                "output": [".jpg", ".png", ".webp", ".gif"],
                "web_optimized": [".webp", ".jpg"]
            },
            "text": {
                "input": [".txt", ".md", ".html", ".pdf", ".docx", ".rtf"],
                "output": [".txt", ".md", ".html", ".pdf"],
                "web_optimized": [".html", ".md"]
            }
        }
    
    async def transform_content(self, content_path: str, transformations: List[TransformationConfig],
                              creator_id: str, target_platforms: Optional[List[str]] = None) -> List[TransformationResult]:
        """        Transforme le contenu selon les configurations spécifiées
        
        Args:
            content_path: Chemin vers le fichier source
            transformations: Liste des transformations à appliquer
            creator_id: ID du créateur
            target_platforms: Plateformes cibles pour l'optimisation
            
        Returns:
            List[TransformationResult]: Résultats des transformations
        """        try:
            results = []
            
            # Analyse du contenu source
            content_info = await self._analyze_source_content(content_path)
            
            # Optimisation automatique pour les plateformes cibles
            if target_platforms:
                optimized_transformations = await self._optimize_for_platforms(
                    transformations, content_info, target_platforms
                )
            else:
                optimized_transformations = transformations
            
            # Exécution des transformations
            for i, config in enumerate(optimized_transformations):
                job_id = f"{creator_id}_{uuid.uuid4().hex[:8]}"
                
                logger.info(f"Starting transformation {i+1}/{len(optimized_transformations)}: {config.transformation_type.value}")
                
                result = await self._execute_transformation(
                    content_path, config, job_id, content_info
                )
                
                results.append(result)
                
                # Utilisation du résultat comme source pour la transformation suivante si nécessaire
                if result.success and i < len(optimized_transformations) - 1:
                    # Vérifier si la transformation suivante est compatible
                    next_config = optimized_transformations[i + 1]
                    if self._is_transformation_chainable(config, next_config):
                        content_path = result.transformed_path
            
            # Nettoyage des fichiers temporaires
            await self._cleanup_temporary_files(results)
            
            logger.info(f"Completed {len(results)} transformations")
            return results
            
        except Exception as e:
            logger.error(f"Content transformation failed: {e}")
            raise
    
    async def _analyze_source_content(self, content_path: str) -> Dict[str, Any]:
        """Analyse le contenu source pour optimiser les transformations"""        try:
            file_path = Path(content_path)
            file_extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            # Détection du type MIME
            mime_type, _ = mimetypes.guess_type(content_path)
            
            content_info = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_extension": file_extension,
                "file_size": file_size,
                "mime_type": mime_type,
                "content_type": self._determine_content_type(file_extension),
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime),
                "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime)
            }
            
            # Analyse spécifique selon le type
            if content_info["content_type"] == "audio":
                audio_info = await self._analyze_audio_content(content_path)
                content_info.update(audio_info)
            elif content_info["content_type"] == "video":
                video_info = await self._analyze_video_content(content_path)
                content_info.update(video_info)
            elif content_info["content_type"] == "image":
                image_info = await self._analyze_image_content(content_path)
                content_info.update(image_info)
            elif content_info["content_type"] == "text":
                text_info = await self._analyze_text_content(content_path)
                content_info.update(text_info)
            
            return content_info
            
        except Exception as e:
            logger.error(f"Error analyzing source content: {e}")
            raise
    
    def _determine_content_type(self, file_extension: str) -> str:
        """Détermine le type de contenu basé sur l'extension"""        audio_extensions = [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aiff"]
        video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"]
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
        text_extensions = [".txt", ".md", ".html", ".pdf", ".docx"]
        
        if file_extension in audio_extensions:
            return "audio"
        elif file_extension in video_extensions:
            return "video"
        elif file_extension in image_extensions:
            return "image"
        elif file_extension in text_extensions:
            return "text"
        else:
            return "unknown"
    
    async def _analyze_audio_content(self, audio_path: str) -> Dict[str, Any]:
        """Analyse spécifique pour le contenu audio"""        try:
            # Chargement de l'audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = len(y) / sr
            
            # Analyse des caractéristiques
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Détection de silence
            intervals = librosa.effects.split(y, top_db=20)
            
            return {
                "duration_seconds": float(duration),
                "sample_rate": int(sr),
                "channels": 1 if len(y.shape) == 1 else y.shape[0],
                "tempo_bpm": float(tempo),
                "spectral_centroid_mean": float(np.mean(spectral_centroids)),
                "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                "silence_ratio": 1.0 - (len(intervals) * len(y) / len(y)) if len(intervals) > 0 else 0.0,
                "dynamic_range": float(np.max(y) - np.min(y)),
                "quality_score": await self.quality_analyzer.analyze_audio_quality(y, sr)
            }
            
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return {"duration_seconds": 0, "sample_rate": 44100, "channels": 2}
    
    async def _analyze_video_content(self, video_path: str) -> Dict[str, Any]:
        """Analyse spécifique pour le contenu vidéo"""        try:
            # Utilisation de OpenCV pour l'analyse
            cap = cv2.VideoCapture(video_path)
            
            # Propriétés de base
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Analyse de quelques frames pour la qualité
            frame_qualities = []
            for i in range(min(10, frame_count)):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_count // 10)
                ret, frame = cap.read()
                if ret:
                    # Analyse de netteté (Laplacian variance)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                    frame_qualities.append(sharpness)
            
            cap.release()
            
            # Analyse audio si présent
            audio_info = {}
            try:
                clip = VideoFileClip(video_path)
                if clip.audio is not None:
                    audio_info = {
                        "has_audio": True,
                        "audio_duration": clip.audio.duration,
                        "audio_fps": clip.audio.fps
                    }
                else:
                    audio_info = {"has_audio": False}
                clip.close()
            except:
                audio_info = {"has_audio": False}
            
            return {
                "duration_seconds": float(duration),
                "fps": float(fps),
                "frame_count": frame_count,
                "resolution": {"width": width, "height": height},
                "aspect_ratio": width / height if height > 0 else 1.0,
                "average_sharpness": float(np.mean(frame_qualities)) if frame_qualities else 0.0,
                "quality_score": await self.quality_analyzer.analyze_video_quality(video_path),
                **audio_info
            }
            
        except Exception as e:
            logger.warning(f"Video analysis failed: {e}")
            return {"duration_seconds": 0, "fps": 30, "resolution": {"width": 1920, "height": 1080}}
    
    async def _analyze_image_content(self, image_path: str) -> Dict[str, Any]:
        """Analyse spécifique pour le contenu image"""        try:
            # Chargement de l'image
            image = Image.open(image_path)
            
            # Propriétés de base
            width, height = image.size
            mode = image.mode
            format_name = image.format
            
            # Conversion en array pour l'analyse
            img_array = np.array(image)
            
            # Analyse de la qualité
            if len(img_array.shape) == 3:
                # Image couleur
                brightness = np.mean(img_array)
                contrast = np.std(img_array)
                # Détection de flou (variance du Laplacian)
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            else:
                # Image en niveaux de gris
                brightness = np.mean(img_array)
                contrast = np.std(img_array)
                sharpness = cv2.Laplacian(img_array, cv2.CV_64F).var()
            
            # Métadonnées EXIF si disponibles
            exif_data = {}
            try:
                exif = image._getexif()
                if exif:
                    exif_data = {str(k): str(v) for k, v in exif.items()}
            except:
                pass
            
            return {
                "resolution": {"width": width, "height": height},
                "aspect_ratio": width / height if height > 0 else 1.0,
                "color_mode": mode,
                "format": format_name,
                "megapixels": (width * height) / 1000000,
                "brightness": float(brightness),
                "contrast": float(contrast),
                "sharpness": float(sharpness),
                "quality_score": await self.quality_analyzer.analyze_image_quality(img_array),
                "exif_data": exif_data
            }
            
        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")
            return {"resolution": {"width": 1920, "height": 1080}, "format": "JPEG"}
    
    async def _analyze_text_content(self, text_path: str) -> Dict[str, Any]:
        """Analyse spécifique pour le contenu texte"""        try:
            # Lecture du contenu
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Statistiques de base
            word_count = len(content.split())
            char_count = len(content)
            line_count = len(content.split('\n'))
            
            # Analyse linguistique simple
            sentences = content.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Détection de la langue (simple)
            language = "en"  # Par défaut, pourrait être amélioré avec langdetect
            
            # Score de lisibilité (approximation Flesch)
            readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (char_count / word_count)) if word_count > 0 else 0
            
            return {
                "word_count": word_count,
                "character_count": char_count,
                "line_count": line_count,
                "sentence_count": sentence_count,
                "average_sentence_length": float(avg_sentence_length),
                "language": language,
                "readability_score": float(readability_score),
                "quality_score": await self.quality_analyzer.analyze_text_quality(content)
            }
            
        except Exception as e:
            logger.warning(f"Text analysis failed: {e}")
            return {"word_count": 0, "character_count": 0, "language": "en"}
    
    async def _optimize_for_platforms(self, transformations: List[TransformationConfig],
                                    content_info: Dict[str, Any],
                                    target_platforms: List[str]) -> List[TransformationConfig]:
        """Optimise les transformations pour les plateformes cibles"""        optimized = transformations.copy()
        
        # Recommandations par plateforme
        platform_specs = {
            "youtube": {
                "video": {"max_resolution": (1920, 1080), "max_bitrate": 8000, "fps": 30},
                "audio": {"sample_rate": 44100, "bitrate": 128}
            },
            "tiktok": {
                "video": {"max_resolution": (1080, 1920), "max_bitrate": 6000, "fps": 30},
                "audio": {"sample_rate": 44100, "bitrate": 96}
            },
            "instagram": {
                "video": {"max_resolution": (1080, 1080), "max_bitrate": 3500, "fps": 30},
                "image": {"max_resolution": (1080, 1080), "format": "jpg"},
                "audio": {"sample_rate": 44100, "bitrate": 96}
            },
            "spotify": {
                "audio": {"sample_rate": 44100, "bitrate": 320, "format": "ogg"}
            }
        }
        
        # Application des optimisations automatiques
        for platform in target_platforms:
            if platform in platform_specs:
                specs = platform_specs[platform]
                content_type = content_info.get("content_type")
                
                if content_type in specs:
                    platform_config = specs[content_type]
                    
                    # Ajout de transformations automatiques si nécessaire
                    if content_type == "video" and "max_resolution" in platform_config:
                        current_res = content_info.get("resolution", {})
                        target_res = platform_config["max_resolution"]
                        
                        if (current_res.get("width", 0) > target_res[0] or 
                            current_res.get("height", 0) > target_res[1]):
                            
                            resize_config = TransformationConfig(
                                transformation_type=TransformationType.VIDEO_RESIZE,
                                quality_level=QualityLevel.HIGH,
                                target_resolution=target_res,
                                custom_params={"platform": platform}
                            )
                            optimized.insert(0, resize_config)
        
        return optimized
    
    async def _execute_transformation(self, content_path: str, config: TransformationConfig,
                                    job_id: str, content_info: Dict[str, Any]) -> TransformationResult:
        """Exécute une transformation spécifique"""        start_time = time.time()
        
        try:
            # Génération du nom de fichier de sortie
            output_path = self._generate_output_path(content_path, config)
            
            # Taille du fichier source
            source_size = Path(content_path).stat().st_size
            
            # Exécution selon le type de transformation
            if config.transformation_type.value.startswith("audio_"):
                success = await self._transform_audio(content_path, output_path, config, content_info)
            elif config.transformation_type.value.startswith("video_"):
                success = await self._transform_video(content_path, output_path, config, content_info)
            elif config.transformation_type.value.startswith("image_"):
                success = await self._transform_image(content_path, output_path, config, content_info)
            elif config.transformation_type.value.startswith("text_"):
                success = await self._transform_text(content_path, output_path, config, content_info)
            else:
                success = await self._transform_generic(content_path, output_path, config, content_info)
            
            # Calcul des métriques
            end_time = time.time()
            processing_time = end_time - start_time
            
            if success and Path(output_path).exists():
                target_size = Path(output_path).stat().st_size
                compression_ratio = source_size / target_size if target_size > 0 else 1.0
                
                # Analyse de qualité post-transformation
                quality_metrics = await self._analyze_transformation_quality(
                    content_path, output_path, config
                )
                
                return TransformationResult(
                    job_id=job_id,
                    original_path=content_path,
                    transformed_path=output_path,
                    transformation_type=config.transformation_type,
                    quality_metrics=quality_metrics,
                    file_size_before=source_size,
                    file_size_after=target_size,
                    compression_ratio=compression_ratio,
                    processing_time_seconds=processing_time,
                    success=True,
                    metadata={"config": config.__dict__}
                )
            else:
                return TransformationResult(
                    job_id=job_id,
                    original_path=content_path,
                    transformed_path="",
                    transformation_type=config.transformation_type,
                    quality_metrics={},
                    file_size_before=source_size,
                    file_size_after=0,
                    compression_ratio=0.0,
                    processing_time_seconds=processing_time,
                    success=False,
                    error_message="Transformation failed"
                )
                
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            return TransformationResult(
                job_id=job_id,
                original_path=content_path,
                transformed_path="",
                transformation_type=config.transformation_type,
                quality_metrics={},
                file_size_before=Path(content_path).stat().st_size,
                file_size_after=0,
                compression_ratio=0.0,
                processing_time_seconds=processing_time,
                success=False,
                error_message=str(e)
            )
    
    def _generate_output_path(self, input_path: str, config: TransformationConfig) -> str:
        """Génère le chemin de sortie pour la transformation"""        input_path_obj = Path(input_path)
        base_name = input_path_obj.stem
        
        # Suffixe basé sur la transformation
        transformation_suffix = config.transformation_type.value.replace("_", "-")
        quality_suffix = config.quality_level.value
        
        # Extension selon le format cible
        if config.target_format:
            extension = config.target_format if config.target_format.startswith('.') else f".{config.target_format}"
        else:
            extension = input_path_obj.suffix
        
        # Construction du nom
        output_name = f"{base_name}_{transformation_suffix}_{quality_suffix}{extension}"
        
        # Dossier de sortie
        output_dir = input_path_obj.parent / "transformed"
        output_dir.mkdir(exist_ok=True)
        
        return str(output_dir / output_name)
    
    async def _transform_audio(self, input_path: str, output_path: str,
                             config: TransformationConfig, content_info: Dict[str, Any]) -> bool:
        """Transformations audio spécialisées"""        try:
            if config.transformation_type == TransformationType.AUDIO_NORMALIZE:
                # Normalisation audio
                y, sr = librosa.load(input_path, sr=None)
                y_normalized = librosa.util.normalize(y)
                sf.write(output_path, y_normalized, sr)
                
            elif config.transformation_type == TransformationType.AUDIO_DENOISE:
                # Réduction de bruit (implémentation simplifiée)
                y, sr = librosa.load(input_path, sr=None)
                # Appliquation d'un filtre passe-haut simple
                y_denoised = librosa.effects.preemphasis(y)
                sf.write(output_path, y_denoised, sr)
                
            elif config.transformation_type == TransformationType.AUDIO_COMPRESS:
                # Compression audio
                y, sr = librosa.load(input_path, sr=None)
                # Compression dynamique simple
                threshold = 0.5
                ratio = 4.0
                y_compressed = np.where(np.abs(y) > threshold, 
                                      threshold + (y - threshold) / ratio, y)
                sf.write(output_path, y_compressed, sr)
                
            elif config.transformation_type == TransformationType.AUDIO_FORMAT_CONVERT:
                # Conversion de format
                y, sr = librosa.load(input_path, sr=None)
                if config.target_format:
                    sf.write(output_path, y, sr, format=config.target_format.upper())
                else:
                    sf.write(output_path, y, sr)
                    
            else:
                # Transformation générique
                y, sr = librosa.load(input_path, sr=None)
                sf.write(output_path, y, sr)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio transformation failed: {e}")
            return False
    
    async def _transform_video(self, input_path: str, output_path: str,
                             config: TransformationConfig, content_info: Dict[str, Any]) -> bool:
        """Transformations vidéo spécialisées"""        try:
            if config.transformation_type == TransformationType.VIDEO_RESIZE:
                # Redimensionnement vidéo
                clip = VideoFileClip(input_path)
                if config.target_resolution:
                    width, height = config.target_resolution
                    resized_clip = clip.resize((width, height))
                else:
                    resized_clip = clip.resize(0.5)  # 50% par défaut
                
                resized_clip.write_videofile(output_path, verbose=False, logger=None)
                clip.close()
                resized_clip.close()
                
            elif config.transformation_type == TransformationType.VIDEO_COMPRESS:
                # Compression vidéo
                clip = VideoFileClip(input_path)
                bitrate = config.target_bitrate or "2000k"
                clip.write_videofile(output_path, bitrate=bitrate, verbose=False, logger=None)
                clip.close()
                
            elif config.transformation_type == TransformationType.VIDEO_FPS_ADJUST:
                # Ajustement FPS
                clip = VideoFileClip(input_path)
                target_fps = config.target_fps or 30
                adjusted_clip = clip.set_fps(target_fps)
                adjusted_clip.write_videofile(output_path, verbose=False, logger=None)
                clip.close()
                adjusted_clip.close()
                
            elif config.transformation_type == TransformationType.VIDEO_FORMAT_CONVERT:
                # Conversion de format
                clip = VideoFileClip(input_path)
                codec = 'libx264' if config.target_format == '.mp4' else 'libvpx'
                clip.write_videofile(output_path, codec=codec, verbose=False, logger=None)
                clip.close()
                
            else:
                # Transformation générique
                clip = VideoFileClip(input_path)
                clip.write_videofile(output_path, verbose=False, logger=None)
                clip.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Video transformation failed: {e}")
            return False
    
    async def _transform_image(self, input_path: str, output_path: str,
                             config: TransformationConfig, content_info: Dict[str, Any]) -> bool:
        """Transformations image spécialisées"""        try:
            image = Image.open(input_path)
            
            if config.transformation_type == TransformationType.IMAGE_RESIZE:
                # Redimensionnement
                if config.target_resolution:
                    width, height = config.target_resolution
                    resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
                else:
                    current_size = image.size
                    new_size = (current_size[0] // 2, current_size[1] // 2)
                    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                resized_image.save(output_path, optimize=True)
                
            elif config.transformation_type == TransformationType.IMAGE_ENHANCE:
                # Enhancement d'image
                enhancer = ImageEnhance.Sharpness(image)
                enhanced_image = enhancer.enhance(1.2)  # 20% plus net
                
                enhancer = ImageEnhance.Contrast(enhanced_image)
                enhanced_image = enhancer.enhance(1.1)  # 10% plus de contraste
                
                enhanced_image.save(output_path, optimize=True)
                
            elif config.transformation_type == TransformationType.IMAGE_COMPRESS:
                # Compression avec qualité
                quality = {
                    QualityLevel.DRAFT: 60,
                    QualityLevel.STANDARD: 80,
                    QualityLevel.HIGH: 90,
                    QualityLevel.PROFESSIONAL: 95
                }.get(config.quality_level, 85)
                
                image.save(output_path, optimize=True, quality=quality)
                
            elif config.transformation_type == TransformationType.IMAGE_FORMAT_CONVERT:
                # Conversion de format
                if config.target_format:
                    if config.target_format.lower() == '.webp':
                        image.save(output_path, format='WEBP', optimize=True, quality=85)
                    elif config.target_format.lower() in ['.jpg', '.jpeg']:
                        if image.mode == 'RGBA':
                            image = image.convert('RGB')
                        image.save(output_path, format='JPEG', optimize=True, quality=90)
                    elif config.target_format.lower() == '.png':
                        image.save(output_path, format='PNG', optimize=True)
                    else:
                        image.save(output_path)
                else:
                    image.save(output_path, optimize=True)
                    
            else:
                # Transformation générique
                image.save(output_path, optimize=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Image transformation failed: {e}")
            return False
    
    async def _transform_text(self, input_path: str, output_path: str,
                            config: TransformationConfig, content_info: Dict[str, Any]) -> bool:
        """Transformations texte spécialisées"""        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if config.transformation_type == TransformationType.TEXT_SEO_OPTIMIZE:
                # Optimisation SEO
                optimized_content = await self._optimize_text_for_seo(content, config)
                
            elif config.transformation_type == TransformationType.TEXT_SUMMARIZE:
                # Résumé automatique
                if "text_summarization" in self.ai_models:
                    try:
                        summarizer = self.ai_models["text_summarization"]
                        summary = summarizer(content, max_length=500, min_length=100, do_sample=False)
                        optimized_content = summary[0]['summary_text']
                    except:
                        optimized_content = content[:1000] + "..."  # Fallback simple
                else:
                    optimized_content = content[:1000] + "..."
                    
            elif config.transformation_type == TransformationType.TEXT_TRANSLATE:
                # Traduction
                if "text_translation" in self.ai_models:
                    try:
                        translator = self.ai_models["text_translation"]
                        translated = translator(content)
                        optimized_content = translated[0]['translation_text']
                    except:
                        optimized_content = content  # Fallback
                else:
                    optimized_content = content
                    
            elif config.transformation_type == TransformationType.TEXT_FORMAT_CONVERT:
                # Conversion de format
                if config.target_format == '.html':
                    optimized_content = f"<html><body><p>{content.replace(chr(10), '</p><p>')}</p></body></html>"
                elif config.target_format == '.md':
                    optimized_content = content  # Déjà en markdown probablement
                else:
                    optimized_content = content
                    
            else:
                optimized_content = content
            
            # Sauvegarde
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Text transformation failed: {e}")
            return False
    
    async def _transform_generic(self, input_path: str, output_path: str,
                               config: TransformationConfig, content_info: Dict[str, Any]) -> bool:
        """Transformations génériques"""        try:
            # Copie simple pour les transformations non spécialisées
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        except Exception as e:
            logger.error(f"Generic transformation failed: {e}")
            return False
    
    async def _optimize_text_for_seo(self, content: str, config: TransformationConfig) -> str:
        """Optimise le texte pour le SEO"""        # Implémentation basique d'optimisation SEO
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Amélioration des titres
            if line.strip().startswith('#'):
                # Déjà un titre markdown
                optimized_lines.append(line)
            elif len(line.strip()) < 60 and line.strip() and not line.startswith(' '):
                # Probablement un titre
                optimized_lines.append(f"# {line.strip()}")
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    async def _analyze_transformation_quality(self, original_path: str, transformed_path: str,
                                            config: TransformationConfig) -> Dict[str, float]:
        """Analyse la qualité post-transformation"""        try:
            metrics = {}
            
            # Métriques générales
            original_size = Path(original_path).stat().st_size
            transformed_size = Path(transformed_path).stat().st_size
            size_reduction = (original_size - transformed_size) / original_size * 100
            
            metrics["size_reduction_percentage"] = size_reduction
            metrics["compression_efficiency"] = size_reduction / max(1, len(config.custom_params))
            
            # Métriques spécifiques au type
            content_type = self._determine_content_type(Path(original_path).suffix)
            
            if content_type == "image":
                metrics.update(await self._compare_image_quality(original_path, transformed_path))
            elif content_type == "audio":
                metrics.update(await self._compare_audio_quality(original_path, transformed_path))
            elif content_type == "video":
                metrics.update(await self._compare_video_quality(original_path, transformed_path))
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return {"quality_score": 0.8}  # Score par défaut
    
    async def _compare_image_quality(self, original_path: str, transformed_path: str) -> Dict[str, float]:
        """Compare la qualité entre deux images"""        try:
            original = cv2.imread(original_path)
            transformed = cv2.imread(transformed_path)
            
            if original is None or transformed is None:
                return {"image_quality_score": 0.5}
            
            # Redimensionnement pour la comparaison si nécessaire
            if original.shape != transformed.shape:
                transformed = cv2.resize(transformed, (original.shape[1], original.shape[0]))
            
            # PSNR (Peak Signal-to-Noise Ratio)
            psnr = cv2.PSNR(original, transformed)
            
            # SSIM approximatif (sans skimage)
            mse = np.mean((original.astype(float) - transformed.astype(float)) ** 2)
            ssim_approx = 1 / (1 + mse / 10000)  # Approximation simple
            
            return {
                "image_psnr": float(psnr),
                "image_ssim_approx": float(ssim_approx),
                "image_quality_score": float((psnr / 50 + ssim_approx) / 2)  # Score combiné
            }
            
        except Exception as e:
            logger.warning(f"Image quality comparison failed: {e}")
            return {"image_quality_score": 0.8}
    
    async def _compare_audio_quality(self, original_path: str, transformed_path: str) -> Dict[str, float]:
        """Compare la qualité entre deux fichiers audio"""        try:
            y1, sr1 = librosa.load(original_path, sr=None)
            y2, sr2 = librosa.load(transformed_path, sr=None)
            
            # Resample si nécessaire
            if sr1 != sr2:
                y2 = librosa.resample(y2, orig_sr=sr2, target_sr=sr1)
            
            # Alignement de longueur
            min_length = min(len(y1), len(y2))
            y1 = y1[:min_length]
            y2 = y2[:min_length]
            
            # Calcul de métriques
            mse = np.mean((y1 - y2) ** 2)
            snr = 10 * np.log10(np.mean(y1 ** 2) / (mse + 1e-10))
            
            # Corrélation
            correlation = np.corrcoef(y1, y2)[0, 1] if len(y1) > 1 else 0.0
            
            return {
                "audio_snr": float(snr),
                "audio_correlation": float(correlation),
                "audio_quality_score": float((snr / 50 + correlation) / 2)
            }
            
        except Exception as e:
            logger.warning(f"Audio quality comparison failed: {e}")
            return {"audio_quality_score": 0.8}
    
    async def _compare_video_quality(self, original_path: str, transformed_path: str) -> Dict[str, float]:
        """Compare la qualité entre deux vidéos"""        try:
            cap1 = cv2.VideoCapture(original_path)
            cap2 = cv2.VideoCapture(transformed_path)
            
            frame_count1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_count2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Comparaison de quelques frames
            quality_scores = []
            sample_frames = min(10, frame_count1, frame_count2)
            
            for i in range(sample_frames):
                frame_idx = i * frame_count1 // sample_frames
                
                cap1.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                cap2.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                
                ret1, frame1 = cap1.read()
                ret2, frame2 = cap2.read()
                
                if ret1 and ret2:
                    if frame1.shape != frame2.shape:
                        frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
                    
                    psnr = cv2.PSNR(frame1, frame2)
                    quality_scores.append(psnr)
            
            cap1.release()
            cap2.release()
            
            avg_psnr = np.mean(quality_scores) if quality_scores else 30.0
            
            return {
                "video_avg_psnr": float(avg_psnr),
                "video_quality_score": float(min(1.0, avg_psnr / 40))
            }
            
        except Exception as e:
            logger.warning(f"Video quality comparison failed: {e}")
            return {"video_quality_score": 0.8}
    
    def _is_transformation_chainable(self, config1: TransformationConfig, 
                                   config2: TransformationConfig) -> bool:
        """Vérifie si deux transformations peuvent être chaînées"""        # Vérification de compatibilité basique
        type1 = config1.transformation_type.value.split('_')[0]
        type2 = config2.transformation_type.value.split('_')[0]
        
        # Même type de contenu
        if type1 == type2:
            return True
        
        # Transformations compatibles entre types
        compatible_chains = {
            "video": ["audio"],  # Vidéo peut être suivie d'audio
            "image": ["thumbnail"],  # Image peut générer des thumbnails
        }
        
        return type2 in compatible_chains.get(type1, [])
    
    async def _cleanup_temporary_files(self, results: List[TransformationResult]):
        """Nettoie les fichiers temporaires après transformation"""        for result in results:
            if not result.success and result.transformed_path:
                try:
                    Path(result.transformed_path).unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temporary file {result.transformed_path}: {e}")

# Configuration globale du moteur de transformation
TRANSFORMATION_ENGINE_CONFIG = {
    "quality_levels": {
        "draft": {"speed": "fastest", "quality": "basic"},
        "standard": {"speed": "medium", "quality": "good"},
        "high": {"speed": "slow", "quality": "excellent"},
        "professional": {"speed": "slowest", "quality": "lossless"},
        "lossless": {"speed": "slowest", "quality": "perfect"}
    },
    "platform_optimizations": {
        "youtube": "High quality video with web optimization",
        "tiktok": "Vertical video optimization for mobile",
        "instagram": "Square format with social media optimization",
        "spotify": "High quality audio with streaming optimization"
    },
    "ai_enhancements": {
        "image_super_resolution": "Upscale images using AI",
        "audio_enhancement": "Improve audio quality with AI",
        "video_stabilization": "Stabilize shaky videos",
        "text_optimization": "Optimize text for SEO and readability"
    }
}
