"""🔄 Transformation System - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/data_management/transformers/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json

from .audio_transformer import AudioTransformer, AsyncAudioTransformer
from .video_transformer import VideoTransformer, AsyncVideoTransformer
from .image_transformer import ImageTransformer, AsyncImageTransformer
from .document_transformer import DocumentTransformer, AsyncDocumentTransformer
from .metadata_transformer import MetadataTransformer, AsyncMetadataTransformer
from .text_transformer import TextTransformer, AsyncTextTransformer
from .format_converter import FormatConverter, AsyncFormatConverter
from .pipeline_transformer import PipelineExecutor, PipelineConfig
from .ai_transformer import AITransformer, AITransformationConfig
from .content_fingerprint_transformer import (
    ContentFingerprintTransformer, FingerprintConfig, ContentFingerprintResult,
    FingerprintType, FingerprintAlgorithm, content_fingerprint_transformer
)
from .protection_transformer import (
    ContentProtectionTransformer, ProtectionConfig, WatermarkConfiguration,
    EncryptionConfiguration, LicenseConfiguration, ContentProtectionResult,
    ProtectionLevel, WatermarkType, EncryptionType, LicenseType,
    content_protection_transformer
)
from .analytics_transformer import (
    AnalyticsTransformer, AnalyticsConfig, AnalyticsResult,
    AnalyticsType, MetricType, ContentCategory, analytics_transformer
)
from .stream_transformer import (
    StreamTransformer, StreamConfig, StreamProcessingResult,
    StreamType, ProcessingMode, StreamFormat, stream_transformer
)

class TransformationType(Enum):
    """Types de transformations supportées"""    # Transformations audio
    AUDIO_NORMALIZE = "audio_normalize"
    AUDIO_CONVERT = "audio_convert"
    AUDIO_COMPRESS = "audio_compress"
    AUDIO_ENHANCE = "audio_enhance"
    
    # Transformations vidéo
    VIDEO_RESIZE = "video_resize"
    VIDEO_CONVERT = "video_convert"
    VIDEO_COMPRESS = "video_compress"
    VIDEO_EXTRACT_AUDIO = "video_extract_audio"
    
    # Transformations image
    IMAGE_RESIZE = "image_resize"
    IMAGE_CONVERT = "image_convert"
    IMAGE_COMPRESS = "image_compress"
    IMAGE_ENHANCE = "image_enhance"
    
    # Transformations document
    DOCUMENT_CONVERT = "document_convert"
    DOCUMENT_EXTRACT_TEXT = "document_extract_text"
    DOCUMENT_SUMMARIZE = "document_summarize"
    
    # Transformations métadonnées
    METADATA_NORMALIZE = "metadata_normalize"
    METADATA_ENRICH = "metadata_enrich"
    
    # Transformations protection
    CONTENT_FINGERPRINT = "content_fingerprint"
    CONTENT_PROTECTION = "content_protection"
    WATERMARK_APPLY = "watermark_apply"
    CONTENT_ENCRYPT = "content_encrypt"
    LICENSE_EMBED = "license_embed"
    
    # Transformations analytics
    CONTENT_ANALYTICS = "content_analytics"
    QUALITY_ANALYSIS = "quality_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    
    # Transformations streaming
    REALTIME_AUDIO = "realtime_audio"
    REALTIME_VIDEO = "realtime_video"
    STREAM_PROCESSING = "stream_processing"

@dataclass
class TransformationConfig:
    """Configuration d'une transformation"""    type: TransformationType
    parameters: Dict[str, Any]
    output_format: Optional[str] = None
    quality: str = "standard"  # low, standard, high, ultra
    preserve_metadata: bool = True

@dataclass
class TransformationResult:
    """Résultat d'une transformation"""    success: bool
    input_path: str
    output_path: Optional[str]
    transformation_type: TransformationType
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    processing_time: float

class TransformationManager:
    """Gestionnaire principal des transformations"""    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des transformateurs spécialisés
        self.transformers = {
            'audio': AudioTransformer(),
            'video': VideoTransformer(),
            'image': ImageTransformer(),
            'document': DocumentTransformer(),
            'metadata': MetadataTransformer(),
            'fingerprint': content_fingerprint_transformer,
            'protection': content_protection_transformer,
            'analytics': analytics_transformer,
            'stream': stream_transformer
        }
        
        # Mapping des types de transformation vers les transformateurs
        self.transformation_mapping = {
            TransformationType.AUDIO_NORMALIZE: 'audio',
            TransformationType.AUDIO_CONVERT: 'audio',
            TransformationType.AUDIO_COMPRESS: 'audio',
            TransformationType.AUDIO_ENHANCE: 'audio',
            
            TransformationType.VIDEO_RESIZE: 'video',
            TransformationType.VIDEO_CONVERT: 'video',
            TransformationType.VIDEO_COMPRESS: 'video',
            TransformationType.VIDEO_EXTRACT_AUDIO: 'video',
            
            TransformationType.IMAGE_RESIZE: 'image',
            TransformationType.IMAGE_CONVERT: 'image',
            TransformationType.IMAGE_COMPRESS: 'image',
            TransformationType.IMAGE_ENHANCE: 'image',
            
            TransformationType.DOCUMENT_CONVERT: 'document',
            TransformationType.DOCUMENT_EXTRACT_TEXT: 'document',
            TransformationType.DOCUMENT_SUMMARIZE: 'document',
            
            TransformationType.METADATA_NORMALIZE: 'metadata',
            TransformationType.METADATA_ENRICH: 'metadata',
            
            # Protection transformations
            TransformationType.CONTENT_FINGERPRINT: 'fingerprint',
            TransformationType.CONTENT_PROTECTION: 'protection',
            TransformationType.WATERMARK_APPLY: 'protection',
            TransformationType.CONTENT_ENCRYPT: 'protection',
            TransformationType.LICENSE_EMBED: 'protection',
            
            # Analytics transformations
            TransformationType.CONTENT_ANALYTICS: 'analytics',
            TransformationType.QUALITY_ANALYSIS: 'analytics',
            TransformationType.PERFORMANCE_ANALYSIS: 'analytics',
            
            # Stream transformations
            TransformationType.REALTIME_AUDIO: 'stream',
            TransformationType.REALTIME_VIDEO: 'stream',
            TransformationType.STREAM_PROCESSING: 'stream'
        }
        
        # Configurations par défaut par type de créateur
        self.creator_defaults = {
            'musician': {
                'audio_quality': 'high',
                'preferred_formats': ['flac', 'wav', 'mp3'],
                'normalization': True,
                'metadata_enrichment': True,
                'fingerprint_enabled': True,
                'protection_level': 'advanced',
                'analytics_enabled': True,
                'streaming_quality': 'high'
            },
            'influencer': {
                'video_quality': 'standard',
                'preferred_formats': ['mp4', 'webm'],
                'compression': True,
                'social_optimization': True,
                'fingerprint_enabled': True,
                'protection_level': 'standard',
                'analytics_enabled': True,
                'streaming_quality': 'standard'
            },
            'photographer': {
                'image_quality': 'ultra',
                'preferred_formats': ['jpg', 'png', 'tiff'],
                'watermarking': True,
                'metadata_preservation': True,
                'fingerprint_enabled': True,
                'protection_level': 'advanced',
                'analytics_enabled': True,
                'streaming_quality': 'ultra'
            },
            'blogger': {
                'document_formats': ['html', 'md', 'pdf'],
                'text_optimization': True,
                'seo_enhancement': True,
                'fingerprint_enabled': True,
                'protection_level': 'basic',
                'analytics_enabled': True,
                'streaming_quality': 'standard'
            },
            'comedian': {
                'video_quality': 'high',
                'audio_enhancement': True,
                'subtitle_generation': True,
                'fingerprint_enabled': True,
                'protection_level': 'standard',
                'analytics_enabled': True,
                'streaming_quality': 'high'
            }
        }
    
    def transform(
        self,
        input_path: str,
        config: TransformationConfig,
        output_path: Optional[str] = None,
        creator_type: Optional[str] = None
    ) -> TransformationResult:
        """Effectue une transformation selon la configuration"""        
        try:
            # Déterminer le transformateur approprié
            transformer_type = self.transformation_mapping.get(config.type)
            if not transformer_type:
                return TransformationResult(
                    success=False,
                    input_path=input_path,
                    output_path=None,
                    transformation_type=config.type,
                    metadata={},
                    errors=[f"Type de transformation non supporté: {config.type}"],
                    warnings=[],
                    processing_time=0.0
                )
            
            transformer = self.transformers[transformer_type]
            
            # Appliquer les defaults du créateur si spécifié
            if creator_type and creator_type in self.creator_defaults:
                defaults = self.creator_defaults[creator_type]
                config = self._apply_creator_defaults(config, defaults)
            
            # Effectuer la transformation
            return transformer.transform(input_path, config, output_path)
            
        except Exception as e:
            self.logger.error(f"Erreur transformation {input_path}: {e}")
            return TransformationResult(
                success=False,
                input_path=input_path,
                output_path=None,
                transformation_type=config.type,
                metadata={},
                errors=[f"Erreur système: {str(e)}"],
                warnings=[],
                processing_time=0.0
            )
    
    def transform_batch(
        self,
        inputs: List[Tuple[str, TransformationConfig]],
        creator_type: Optional[str] = None
    ) -> List[TransformationResult]:
        """Effectue des transformations en lot"""        results = []
        
        for input_path, config in inputs:
            result = self.transform(input_path, config, creator_type=creator_type)
            results.append(result)
        
        return results
    
    def create_pipeline(
        self,
        transformations: List[TransformationConfig]
    ) -> 'TransformationPipeline':
        """Crée un pipeline de transformations séquentielles"""        return TransformationPipeline(transformations, self)
    
    def get_optimal_config(
        self,
        input_path: str,
        target_use_case: str,
        creator_type: str
    ) -> List[TransformationConfig]:
        """Suggère une configuration optimale selon l'usage cible"""        
        file_ext = Path(input_path).suffix.lower().lstrip('.')
        configs = []
        
        # Déterminer le type de contenu
        if file_ext in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
            content_type = 'audio'
        elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            content_type = 'video'
        elif file_ext in ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'webp']:
            content_type = 'image'
        else:
            content_type = 'document'
        
        # Configurations selon l'usage cible
        if target_use_case == 'web_publish':
            configs.extend(self._get_web_publish_configs(content_type, creator_type))
        elif target_use_case == 'social_media':
            configs.extend(self._get_social_media_configs(content_type, creator_type))
        elif target_use_case == 'archive':
            configs.extend(self._get_archive_configs(content_type, creator_type))
        elif target_use_case == 'distribution':
            configs.extend(self._get_distribution_configs(content_type, creator_type))
        
        return configs
    
    def _apply_creator_defaults(
        self,
        config: TransformationConfig,
        defaults: Dict[str, Any]
    ) -> TransformationConfig:
        """Applique les paramètres par défaut du type de créateur"""        
        # Copier la config existante
        new_params = config.parameters.copy()
        
        # Appliquer les defaults si pas déjà spécifiés
        for key, value in defaults.items():
            if key not in new_params:
                new_params[key] = value
        
        return TransformationConfig(
            type=config.type,
            parameters=new_params,
            output_format=config.output_format,
            quality=defaults.get('quality', config.quality),
            preserve_metadata=config.preserve_metadata
        )
    
    def _get_web_publish_configs(self, content_type: str, creator_type: str) -> List[TransformationConfig]:
        """Configurations optimales pour publication web"""        configs = []
        
        if content_type == 'audio':
            configs.append(TransformationConfig(
                type=TransformationType.AUDIO_CONVERT,
                parameters={'format': 'mp3', 'bitrate': 192},
                quality='standard'
            ))
        elif content_type == 'video':
            configs.append(TransformationConfig(
                type=TransformationType.VIDEO_COMPRESS,
                parameters={'format': 'mp4', 'bitrate': '2M'},
                quality='standard'
            ))
        elif content_type == 'image':
            configs.append(TransformationConfig(
                type=TransformationType.IMAGE_COMPRESS,
                parameters={'format': 'jpg', 'quality': 85},
                quality='standard'
            ))
        
        return configs
    
    def _get_social_media_configs(self, content_type: str, creator_type: str) -> List[TransformationConfig]:
        """Configurations optimales pour réseaux sociaux"""        configs = []
        
        if content_type == 'video':
            configs.append(TransformationConfig(
                type=TransformationType.VIDEO_RESIZE,
                parameters={'resolution': [1080, 1920], 'aspect_ratio': '9:16'},
                quality='high'
            ))
        elif content_type == 'image':
            configs.append(TransformationConfig(
                type=TransformationType.IMAGE_RESIZE,
                parameters={'resolution': [1080, 1080]},
                quality='high'
            ))
        
        return configs
    
    def _get_archive_configs(self, content_type: str, creator_type: str) -> List[TransformationConfig]:
        """Configurations pour archivage long terme"""        configs = []
        
        if content_type == 'audio':
            configs.append(TransformationConfig(
                type=TransformationType.AUDIO_CONVERT,
                parameters={'format': 'flac'},
                quality='ultra',
                preserve_metadata=True
            ))
        
        return configs
    
    def _get_distribution_configs(self, content_type: str, creator_type: str) -> List[TransformationConfig]:
        """Configurations pour distribution commerciale"""        configs = []
        
        # Normalisation des métadonnées pour tous types
        configs.append(TransformationConfig(
            type=TransformationType.METADATA_NORMALIZE,
            parameters={'standards': ['dublin_core', 'id3v2']},
            preserve_metadata=True
        ))
        
        return configs

class TransformationPipeline:
    """Pipeline de transformations séquentielles"""    
    def __init__(self, transformations: List[TransformationConfig], manager: TransformationManager):
        self.transformations = transformations
        self.manager = manager
        self.logger = logging.getLogger(__name__)
    
    def execute(self, input_path: str, creator_type: Optional[str] = None) -> List[TransformationResult]:
        """Exécute le pipeline sur un fichier"""        results = []
        current_path = input_path
        
        for i, config in enumerate(self.transformations):
            self.logger.info(f"Étape {i+1}/{len(self.transformations)}: {config.type.value}")
            
            result = self.manager.transform(current_path, config, creator_type=creator_type)
            results.append(result)
            
            if not result.success:
                self.logger.error(f"Échec étape {i+1}: {result.errors}")
                break
            
            # Utiliser la sortie comme entrée de la prochaine étape
            if result.output_path:
                current_path = result.output_path
        
        return results

# Instance globale
transformation_manager = TransformationManager()

# Export des classes principales
__all__ = [
    'TransformationManager',
    'TransformationConfig',
    'TransformationResult',
    'TransformationType',
    'TransformationPipeline',
    'AudioTransformer',
    'AsyncAudioTransformer',
    'VideoTransformer', 
    'AsyncVideoTransformer',
    'ImageTransformer',
    'AsyncImageTransformer',
    'DocumentTransformer',
    'AsyncDocumentTransformer',
    'MetadataTransformer',
    'AsyncMetadataTransformer',
    'TextTransformer',
    'AsyncTextTransformer',
    'FormatConverter',
    'AsyncFormatConverter',
    'PipelineExecutor',
    'PipelineConfig',
    'AITransformer',
    'AITransformationConfig',
    # Protection et Fingerprinting
    'ContentFingerprintTransformer',
    'ContentProtectionTransformer',
    'FingerprintConfig',
    'ProtectionConfig',
    'WatermarkConfiguration',
    'EncryptionConfiguration',
    'LicenseConfiguration',
    'ContentFingerprintResult',
    'ContentProtectionResult',
    'FingerprintType',
    'FingerprintAlgorithm',
    'ProtectionLevel',
    'WatermarkType',
    'EncryptionType',
    'LicenseType',
    # Analytics
    'AnalyticsTransformer',
    'AnalyticsConfig',
    'AnalyticsResult',
    'AnalyticsType',
    'MetricType',
    'ContentCategory',
    # Streaming
    'StreamTransformer',
    'StreamConfig',
    'StreamProcessingResult',
    'StreamType',
    'ProcessingMode',
    'StreamFormat',
    # Instances globales
    'transformation_manager',
    'content_fingerprint_transformer',
    'content_protection_transformer',
    'analytics_transformer',
    'stream_transformer'
]
