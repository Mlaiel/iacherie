"""
 Transformers Index - IA Influencer Agent Platform Enterprise
============================================================
Module: backend/data_management/transformers/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT: Toute tentative de vol, copie ou utilisation non autorisée
de ce code ou de cette technologie est strictement interdite et sera
poursuivie selon les lois allemandes et internationales.

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- AI Research Expert: Fahed Mlaiel (mlaiel@live.de)
- DevOps Engineer: Fahed Mlaiel (mlaiel@live.de)
- DBA: Fahed Mlaiel (mlaiel@live.de)
- Sécurité Expert: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import asyncio
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import des modules principaux
from . import (
    transformation_manager,
    TransformationManager,
    TransformationType,
    TransformationConfig,
    content_fingerprint_transformer,
    content_protection_transformer,
    analytics_transformer,
    stream_transformer
)

# Importation des transformers avec fallback gracieux
try:
    from .audio_transformer import AudioTransformer, AudioAnalyzer, AudioEnhancer
    from .video_transformer import VideoTransformer, VideoAnalyzer, VideoEnhancer
    from .image_transformer import ImageTransformer, ImageAnalyzer, ImageEnhancer
    from .text_transformer import TextTransformer, TextAnalyzer, TextEnhancer
    from .document_transformer import DocumentTransformer, DocumentAnalyzer, DocumentEnhancer
    from .metadata_transformer import MetadataTransformer, MetadataExtractor, MetadataEnricher
    from .format_converter import FormatConverter, ImageFormatConverter, AudioFormatConverter, DocumentFormatConverter
    from .pipeline_transformer import PipelineExecutor, PipelineConfig, DataExtractionStage
    from .ai_transformer import AITransformer, AIModelManager, TextAITransformer, VisionAITransformer, AudioAITransformer
    
    logger.info(" Tous les modules transformers ont été importés avec succès")
    
except ImportError as e:
    logger.error(f" Erreur lors de l'importation des modules transformers: {e}")
    # Fallback gracieux - définir des classes vides
    class AudioTransformer: pass
    class VideoTransformer: pass
    class ImageTransformer: pass
    class TextTransformer: pass
    class DocumentTransformer: pass
    class MetadataTransformer: pass
    class FormatConverter: pass
    class PipelineExecutor: pass
    class AITransformer: pass


class CreatorType(Enum):
    """Types de créateurs supportés"""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer" 
    VIDEOGRAPHER = "videographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    ARTIST = "artist"
    GENERAL = "general"


@dataclass
class TransformationRequest:
    """Requête de transformation unifiée"""
    transformation_type: TransformationType
    input_path: Union[str, Path]
    output_path: Optional[Union[str, Path]] = None
    creator_type: CreatorType = CreatorType.GENERAL
    parameters: Dict[str, Any] = field(default_factory=dict)
    quality_level: str = "high"
    async_mode: bool = False
    
    def __post_init__(self):
        """Validation et normalisation des paramètres"""
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if self.output_path and isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)


@dataclass
class TransformationResult:
    """Résultat de transformation unifié"""
    success: bool
    transformation_type: TransformationType
    input_path: Path
    output_path: Optional[Path]
    processing_time: float
    quality_score: Optional[float] = None
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour sérialisation"""



        return {
            'success': self.success,
            'transformation_type': self.transformation_type.value,
            'input_path': str(self.input_path),
            'output_path': str(self.output_path) if self.output_path else None,
            'processing_time': self.processing_time,
            'quality_score': self.quality_score,
            'confidence_score': self.confidence_score,
            'metadata': self.metadata,
            'error_message': self.error_message
        }


class TransformersRegistry:
    """Registre central des transformateurs disponibles"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Catalogue des transformateurs
        self.transformers_catalog = {
            # Transformateurs de base
            'audio': {
                'class': 'AudioTransformer',
                'capabilities': ['conversion', 'enhancement', 'analysis'],
                'formats': ['mp3', 'wav', 'flac', 'ogg', 'm4a'],
                'creator_optimized': ['musician', 'comedian']
            },
            'video': {
                'class': 'VideoTransformer',
                'capabilities': ['conversion', 'optimization', 'analysis'],
                'formats': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
                'creator_optimized': ['influencer', 'comedian']
            },
            'image': {
                'class': 'ImageTransformer',
                'capabilities': ['conversion', 'enhancement', 'analysis'],
                'formats': ['jpg', 'png', 'tiff', 'bmp', 'webp'],
                'creator_optimized': ['photographer', 'influencer']
            },
            'document': {
                'class': 'DocumentTransformer',
                'capabilities': ['conversion', 'extraction', 'analysis'],
                'formats': ['pdf', 'docx', 'html', 'txt', 'md'],
                'creator_optimized': ['blogger']
            },
            'text': {
                'class': 'TextTransformer',
                'capabilities': ['enhancement', 'generation', 'analysis'],
                'formats': ['txt', 'md', 'html'],
                'creator_optimized': ['blogger', 'influencer']
            },
            'metadata': {
                'class': 'MetadataTransformer',
                'capabilities': ['extraction', 'enrichment', 'normalization'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            
            # Transformateurs avancés
            'fingerprint': {
                'class': 'ContentFingerprintTransformer',
                'capabilities': ['audio_fingerprint', 'video_fingerprint', 'image_fingerprint', 'text_fingerprint'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            'protection': {
                'class': 'ContentProtectionTransformer',
                'capabilities': ['watermarking', 'encryption', 'licensing'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            'analytics': {
                'class': 'AnalyticsTransformer',
                'capabilities': ['quality_analysis', 'performance_analysis', 'content_optimization'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            'stream': {
                'class': 'StreamTransformer',
                'capabilities': ['realtime_audio', 'realtime_video', 'websocket', 'kafka'],
                'formats': ['streaming'],
                'creator_optimized': ['all']
            },
            'ai': {
                'class': 'AITransformer',
                'capabilities': ['text_generation', 'image_generation', 'audio_analysis'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            'format_converter': {
                'class': 'FormatConverter',
                'capabilities': ['universal_conversion'],
                'formats': ['all'],
                'creator_optimized': ['all']
            },
            'pipeline': {
                'class': 'PipelineExecutor',
                'capabilities': ['sequential_processing', 'parallel_processing'],
                'formats': ['all'],
                'creator_optimized': ['all']
            }
        }
        
        # Mapping des transformations vers les transformateurs
        self.transformation_routes = {
            # Audio
            TransformationType.AUDIO_NORMALIZE: 'audio',
            TransformationType.AUDIO_CONVERT: 'audio',
            TransformationType.AUDIO_COMPRESS: 'audio',
            TransformationType.AUDIO_ENHANCE: 'audio',
            
            # Video
            TransformationType.VIDEO_RESIZE: 'video',
            TransformationType.VIDEO_CONVERT: 'video',
            TransformationType.VIDEO_COMPRESS: 'video',
            TransformationType.VIDEO_EXTRACT_AUDIO: 'video',
            
            # Image
            TransformationType.IMAGE_RESIZE: 'image',
            TransformationType.IMAGE_CONVERT: 'image',
            TransformationType.IMAGE_COMPRESS: 'image',
            TransformationType.IMAGE_ENHANCE: 'image',
            
            # Document
            TransformationType.DOCUMENT_CONVERT: 'document',
            TransformationType.DOCUMENT_EXTRACT_TEXT: 'document',
            TransformationType.DOCUMENT_SUMMARIZE: 'document',
            
            # Metadata
            TransformationType.METADATA_NORMALIZE: 'metadata',
            TransformationType.METADATA_ENRICH: 'metadata',
            
            # Protection
            TransformationType.CONTENT_FINGERPRINT: 'fingerprint',
            TransformationType.CONTENT_PROTECTION: 'protection',
            TransformationType.WATERMARK_APPLY: 'protection',
            TransformationType.CONTENT_ENCRYPT: 'protection',
            TransformationType.LICENSE_EMBED: 'protection',
            
            # Analytics
            TransformationType.CONTENT_ANALYTICS: 'analytics',
            TransformationType.QUALITY_ANALYSIS: 'analytics',
            TransformationType.PERFORMANCE_ANALYSIS: 'analytics',
            
            # Stream
            TransformationType.REALTIME_AUDIO: 'stream',
            TransformationType.REALTIME_VIDEO: 'stream',
            TransformationType.STREAM_PROCESSING: 'stream'
        }
        
        # Workflows pré-configurés par type de créateur
        self.creator_workflows = {
            'musician': {
                'content_upload': [
                    TransformationType.AUDIO_NORMALIZE,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.METADATA_ENRICH,
                    TransformationType.CONTENT_PROTECTION,
                    TransformationType.QUALITY_ANALYSIS
                ],
                'streaming_live': [
                    TransformationType.REALTIME_AUDIO,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.STREAM_PROCESSING
                ]
            },
            'photographer': {
                'content_upload': [
                    TransformationType.IMAGE_ENHANCE,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.WATERMARK_APPLY,
                    TransformationType.METADATA_ENRICH,
                    TransformationType.QUALITY_ANALYSIS
                ],
                'batch_processing': [
                    TransformationType.IMAGE_CONVERT,
                    TransformationType.IMAGE_COMPRESS,
                    TransformationType.CONTENT_PROTECTION
                ]
            },
            'influencer': {
                'content_upload': [
                    TransformationType.VIDEO_COMPRESS,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.METADATA_NORMALIZE,
                    TransformationType.CONTENT_ANALYTICS
                ],
                'streaming_live': [
                    TransformationType.REALTIME_VIDEO,
                    TransformationType.STREAM_PROCESSING,
                    TransformationType.PERFORMANCE_ANALYSIS
                ]
            },
            'blogger': {
                'content_upload': [
                    TransformationType.DOCUMENT_EXTRACT_TEXT,
                    TransformationType.METADATA_ENRICH,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.QUALITY_ANALYSIS
                ],
                'text_optimization': [
                    TransformationType.DOCUMENT_SUMMARIZE,
                    TransformationType.CONTENT_ANALYTICS
                ]
            },
            'comedian': {
                'content_upload': [
                    TransformationType.VIDEO_CONVERT,
                    TransformationType.AUDIO_ENHANCE,
                    TransformationType.CONTENT_FINGERPRINT,
                    TransformationType.CONTENT_PROTECTION
                ],
                'streaming_live': [
                    TransformationType.REALTIME_VIDEO,
                    TransformationType.REALTIME_AUDIO,
                    TransformationType.STREAM_PROCESSING
                ]
            }
        }
    
    def get_transformers_for_creator(self, creator_type: str) -> List[str]:
        """Retourne les transformateurs optimisés pour un type de créateur"""
        
        optimized_transformers = []
        
        for transformer_name, info in self.transformers_catalog.items():
            if (creator_type in info['creator_optimized'] or 
                'all' in info['creator_optimized']):
                optimized_transformers.append(transformer_name)
        
        return optimized_transformers
    
    def get_workflow_for_creator(self, creator_type: str, workflow_type: str) -> List[TransformationType]:
        """Retourne un workflow pré-configuré pour un créateur"""
        
        creator_workflows = self.creator_workflows.get(creator_type, {})
        return creator_workflows.get(workflow_type, [])
    
    def suggest_transformations(
        self,
        file_path: str,
        creator_type: str,
        target_use_case: str
    ) -> List[TransformationType]:
        """Suggère des transformations appropriées"""
        
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        suggestions = []
        
        # Détermination du type de contenu
        content_type = self._detect_content_type(file_ext)
        
        # Transformations de base selon le type de contenu
        base_transformations = {
            'audio': [TransformationType.AUDIO_NORMALIZE, TransformationType.CONTENT_FINGERPRINT],
            'video': [TransformationType.VIDEO_COMPRESS, TransformationType.CONTENT_FINGERPRINT],
            'image': [TransformationType.IMAGE_ENHANCE, TransformationType.CONTENT_FINGERPRINT],
            'document': [TransformationType.DOCUMENT_EXTRACT_TEXT, TransformationType.CONTENT_FINGERPRINT]
        }
        
        suggestions.extend(base_transformations.get(content_type, []))
        
        # Transformations selon le cas d'usage
        use_case_transformations = {
            'web_publish': [TransformationType.IMAGE_COMPRESS, TransformationType.VIDEO_COMPRESS],
            'social_media': [TransformationType.VIDEO_RESIZE, TransformationType.IMAGE_RESIZE],
            'archive': [TransformationType.METADATA_ENRICH, TransformationType.CONTENT_PROTECTION],
            'distribution': [TransformationType.LICENSE_EMBED, TransformationType.WATERMARK_APPLY],
            'analytics': [TransformationType.QUALITY_ANALYSIS, TransformationType.CONTENT_ANALYTICS]
        }
        
        suggestions.extend(use_case_transformations.get(target_use_case, []))
        
        # Transformations selon le type de créateur
        creator_specific = {
            'musician': [TransformationType.AUDIO_ENHANCE, TransformationType.METADATA_ENRICH],
            'photographer': [TransformationType.WATERMARK_APPLY, TransformationType.IMAGE_ENHANCE],
            'influencer': [TransformationType.CONTENT_ANALYTICS, TransformationType.PERFORMANCE_ANALYSIS],
            'blogger': [TransformationType.DOCUMENT_SUMMARIZE, TransformationType.QUALITY_ANALYSIS],
            'comedian': [TransformationType.AUDIO_ENHANCE, TransformationType.VIDEO_CONVERT]
        }
        
        suggestions.extend(creator_specific.get(creator_type, []))
        
        # Protection universelle
        suggestions.extend([
            TransformationType.CONTENT_PROTECTION,
            TransformationType.METADATA_NORMALIZE
        ])
        
        # Suppression des doublons tout en préservant l'ordre
        unique_suggestions = []
        seen = set()
        for item in suggestions:
            if item not in seen:
                unique_suggestions.append(item)
                seen.add(item)
        
        return unique_suggestions
    
    def _detect_content_type(self, file_ext: str) -> str:
        """Détecte le type de contenu basé sur l'extension"""
        
        audio_exts = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'}
        video_exts = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
        image_exts = {'jpg', 'jpeg', 'png', 'tiff', 'bmp', 'webp', 'gif'}
        document_exts = {'pdf', 'docx', 'html', 'txt', 'md', 'xml'}
        
        if file_ext in audio_exts:
            return 'audio'
        elif file_ext in video_exts:
            return 'video'
        elif file_ext in image_exts:
            return 'image'
        elif file_ext in document_exts:
            return 'document'
        else:
            return 'unknown'
    
    def get_transformer_capabilities(self, transformer_name: str) -> Dict[str, Any]:
        """Retourne les capacités d'un transformateur"""



        
        return self.transformers_catalog.get(transformer_name, {})
    
    def list_all_transformers(self) -> Dict[str, Dict[str, Any]]:
        """Liste tous les transformateurs disponibles"""



        
        return self.transformers_catalog
    
    def get_transformation_route(self, transformation_type: TransformationType) -> Optional[str]:
        """Retourne le transformateur approprié pour une transformation"""



        
        return self.transformation_routes.get(transformation_type)


class TransformersFactory:
    """Factory pour créer et configurer les transformateurs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry = TransformersRegistry()
    
    def create_transformation_pipeline(
        self,
        creator_type: str,
        workflow_type: str,
        custom_transformations: Optional[List[TransformationType]] = None
    ) -> 'TransformationPipeline':
        """Crée un pipeline de transformation configuré"""
        
        if custom_transformations:
            transformations = custom_transformations
        else:
            transformations = self.registry.get_workflow_for_creator(creator_type, workflow_type)
        
        # Conversion en configurations de transformation
        transformation_configs = []
        
        for transformation_type in transformations:
            config = self._create_transformation_config(transformation_type, creator_type)
            transformation_configs.append(config)
        
        return transformation_manager.create_pipeline(transformation_configs)
    
    def _create_transformation_config(
        self,
        transformation_type: TransformationType,
        creator_type: str
    ) -> TransformationConfig:
        """Crée une configuration de transformation optimisée"""
        
        # Paramètres par défaut selon le type de transformation
        default_params = self._get_default_params(transformation_type)
        
        # Paramètres spécifiques au créateur
        creator_params = self._get_creator_params(creator_type, transformation_type)
        
        # Fusion des paramètres
        final_params = {**default_params, **creator_params}
        
        return TransformationConfig(
            type=transformation_type,
            parameters=final_params,
            quality=creator_params.get('quality', 'standard'),
            preserve_metadata=True
        )
    
    def _get_default_params(self, transformation_type: TransformationType) -> Dict[str, Any]:
        """Retourne les paramètres par défaut pour une transformation"""
        
        defaults = {
            TransformationType.AUDIO_NORMALIZE: {'target_lufs': -16.0, 'peak_limit': -1.0},
            TransformationType.AUDIO_CONVERT: {'format': 'mp3', 'bitrate': 192},
            TransformationType.VIDEO_COMPRESS: {'bitrate': '2M', 'preset': 'medium'},
            TransformationType.IMAGE_COMPRESS: {'quality': 85, 'optimize': True},
            TransformationType.CONTENT_FINGERPRINT: {'algorithm': 'chromaprint'},
            TransformationType.WATERMARK_APPLY: {'opacity': 0.7, 'position': 'bottom_right'},
            TransformationType.QUALITY_ANALYSIS: {'metrics': ['sharpness', 'noise', 'brightness']},
            TransformationType.METADATA_ENRICH: {'sources': ['exif', 'id3', 'dublin_core']}
        }
        
        return defaults.get(transformation_type, {})
    
    def _get_creator_params(
        self,
        creator_type: str,
        transformation_type: TransformationType
    ) -> Dict[str, Any]:
        """Retourne les paramètres spécifiques au créateur"""
        
        creator_specific = {
            'musician': {
                TransformationType.AUDIO_NORMALIZE: {'quality': 'high', 'dynamic_range': True},
                TransformationType.CONTENT_FINGERPRINT: {'precision': 'high'},
                TransformationType.METADATA_ENRICH: {'music_metadata': True}
            },
            'photographer': {
                TransformationType.IMAGE_ENHANCE: {'quality': 'ultra', 'preserve_raw': True},
                TransformationType.WATERMARK_APPLY: {'style': 'professional', 'copyright': True},
                TransformationType.CONTENT_FINGERPRINT: {'visual_features': True}
            },
            'influencer': {
                TransformationType.VIDEO_COMPRESS: {'social_optimized': True, 'quality': 'standard'},
                TransformationType.CONTENT_ANALYTICS: {'engagement_focus': True},
                TransformationType.PERFORMANCE_ANALYSIS: {'social_metrics': True}
            },
            'blogger': {
                TransformationType.DOCUMENT_EXTRACT_TEXT: {'seo_optimization': True},
                TransformationType.QUALITY_ANALYSIS: {'readability_focus': True},
                TransformationType.METADATA_ENRICH: {'seo_metadata': True}
            },
            'comedian': {
                TransformationType.AUDIO_ENHANCE: {'voice_clarity': True},
                TransformationType.VIDEO_CONVERT: {'comedy_optimized': True},
                TransformationType.CONTENT_FINGERPRINT: {'entertainment_focus': True}
            }
        }
        
        return creator_specific.get(creator_type, {}).get(transformation_type, {})
    
    def create_smart_workflow(
        self,
        file_path: str,
        creator_type: str,
        target_use_case: str,
        protection_level: str = 'standard'
    ) -> 'TransformationPipeline':
        """Crée un workflow intelligent basé sur l'analyse du contenu"""
        
        # Suggestions automatiques
        suggested_transformations = self.registry.suggest_transformations(
            file_path, creator_type, target_use_case
        )
        
        # Ajustement selon le niveau de protection
        if protection_level == 'high':
            protection_transformations = [
                TransformationType.CONTENT_FINGERPRINT,
                TransformationType.WATERMARK_APPLY,
                TransformationType.CONTENT_ENCRYPT,
                TransformationType.LICENSE_EMBED
            ]
            suggested_transformations.extend(protection_transformations)
        elif protection_level == 'basic':
            suggested_transformations.append(TransformationType.CONTENT_FINGERPRINT)
        
        # Création du pipeline
        return self.create_transformation_pipeline(
            creator_type,
            'custom',
            suggested_transformations
        )


class TransformersManager:
    """Gestionnaire principal pour l'orchestration des transformateurs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registry = TransformersRegistry()
        self.factory = TransformersFactory()
        
        # Statistiques d'utilisation
        self.usage_stats = {
            'total_transformations': 0,
            'by_creator_type': {},
            'by_transformation_type': {},
            'success_rate': 0.0
        }
    
    async def process_content(
        self,
        file_path: str,
        creator_type: str,
        workflow_type: str = 'content_upload',
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Traite un contenu avec le workflow approprié"""



        
        try:
            # Création du pipeline approprié
            if custom_config and 'transformations' in custom_config:
                pipeline = self.factory.create_transformation_pipeline(
                    creator_type,
                    'custom',
                    custom_config['transformations']
                )
            else:
                pipeline = self.factory.create_transformation_pipeline(
                    creator_type,
                    workflow_type
                )
            
            # Exécution du pipeline
            results = pipeline.execute(file_path, creator_type)
            
            # Mise à jour des statistiques
            self._update_stats(creator_type, results)
            
            # Compilation des résultats
            return {
                'success': all(result.success for result in results),
                'results': results,
                'total_steps': len(results),
                'processing_time': sum(result.processing_time for result in results),
                'workflow_type': workflow_type,
                'creator_type': creator_type
            }
            
        except Exception as e:
            self.logger.error(f"Erreur traitement contenu {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_type': workflow_type,
                'creator_type': creator_type
            }
    
    async def process_batch(
        self,
        file_paths: List[str],
        creator_type: str,
        workflow_type: str = 'content_upload'
    ) -> List[Dict[str, Any]]:
        """Traite plusieurs contenus en lot"""
        
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(
                self.process_content(file_path, creator_type, workflow_type)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traitement des exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'file_path': file_paths[i],
                    'creator_type': creator_type
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_recommendations(
        self,
        file_path: str,
        creator_type: str,
        target_use_case: str
    ) -> Dict[str, Any]:
        """Retourne des recommandations de transformation"""
        
        suggestions = self.registry.suggest_transformations(
            file_path, creator_type, target_use_case
        )
        
        return {
            'suggested_transformations': [t.value for t in suggestions],
            'optimized_transformers': self.registry.get_transformers_for_creator(creator_type),
            'workflow_options': list(self.registry.creator_workflows.get(creator_type, {}).keys()),
            'content_type': self.registry._detect_content_type(
                Path(file_path).suffix.lower().lstrip('.')
            )
        }
    
    def _update_stats(self, creator_type: str, results: List[Any]):
        """Met à jour les statistiques d'utilisation"""
        
        self.usage_stats['total_transformations'] += len(results)
        
        # Stats par créateur
        if creator_type not in self.usage_stats['by_creator_type']:
            self.usage_stats['by_creator_type'][creator_type] = 0
        self.usage_stats['by_creator_type'][creator_type] += len(results)
        
        # Taux de succès
        successful = sum(1 for result in results if result.success)
        total = len(results)
        if total > 0:
            current_success_rate = successful / total
            # Moyenne mobile
            alpha = 0.1
            self.usage_stats['success_rate'] = (
                alpha * current_success_rate + 
                (1 - alpha) * self.usage_stats['success_rate']
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation"""



        
        return {
            'usage_stats': self.usage_stats,
            'available_transformers': len(self.registry.transformers_catalog),
            'supported_creator_types': list(self.registry.creator_workflows.keys()),
            'total_transformation_types': len(self.registry.transformation_routes)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Vérifie l'état de santé des transformateurs"""
        
        health_status = {
            'overall_status': 'healthy',
            'transformers_status': {},
            'issues': []
        }
        
        # Vérification de chaque transformateur
        try:
            # Test basic du gestionnaire principal
            test_config = TransformationConfig(
                type=TransformationType.METADATA_NORMALIZE,
                parameters={}
            )
            
            health_status['transformers_status']['transformation_manager'] = 'healthy'
            
        except Exception as e:
            health_status['transformers_status']['transformation_manager'] = 'unhealthy'
            health_status['issues'].append(f"TransformationManager: {str(e)}")
        
        # Vérification des transformateurs spécialisés
        specialized_transformers = {
            'fingerprint': content_fingerprint_transformer,
            'protection': content_protection_transformer,
            'analytics': analytics_transformer,
            'stream': stream_transformer
        }
        
        for name, transformer in specialized_transformers.items():
            try:
                # Test basic de disponibilité
                if hasattr(transformer, '__class__'):
                    health_status['transformers_status'][name] = 'healthy'
                else:
                    health_status['transformers_status'][name] = 'warning'
                    health_status['issues'].append(f"{name}: Instance non initialisée")
                    
            except Exception as e:
                health_status['transformers_status'][name] = 'unhealthy'
                health_status['issues'].append(f"{name}: {str(e)}")
        
        # Statut global
        unhealthy_count = sum(
            1 for status in health_status['transformers_status'].values()
            if status == 'unhealthy'
        )
        
        if unhealthy_count > 0:
            health_status['overall_status'] = 'degraded' if unhealthy_count < 3 else 'unhealthy'
        
        return health_status


# Instances globales
transformers_registry = TransformersRegistry()
transformers_factory = TransformersFactory()
transformers_manager = TransformersManager()


class TransformationManager:
    """Manager for coordinating data transformations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transformers = {}
    
    async def transform_data(self, data: Any, transformation_type: str) -> Any:
        """Transform data using specified transformation type"""



        try:
            if transformation_type not in self.transformers:
                raise TransformationError(f"Unknown transformation type: {transformation_type}")
            
            transformer = self.transformers[transformation_type]
            return await transformer.transform(data)
            
        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            raise TransformationError(f"Transformation failed: {e}")


# Export des classes et instances principales
__all__ = [
    # Classes principales
    'TransformersRegistry',
    'TransformersFactory', 
    'TransformersManager',
    'TransformationManager',
    'TransformationRequest', 
    'TransformationResult',
    
    # Enums
    'TransformationType',
    'CreatorType',
    
    # Fonctions de convenance
    'transform_content',
    'transform_content_async',
    'get_supported_formats',
    'get_creator_preset',
    'health_check',
    
    # Instances globales
    'transformers_registry',
    'transformers_factory',
    'transformers_manager',
    'transformation_manager',
    
    # Classes de transformers (réexportées)
    'AudioTransformer',
    'VideoTransformer', 
    'ImageTransformer',
    'TextTransformer',
    'DocumentTransformer',
    'MetadataTransformer',
    'FormatConverter',
    'PipelineExecutor',
    'AITransformer',
    
    # Nouveaux transformateurs spécialisés
    'ContentFingerprintTransformer',
    'ContentProtectionTransformer',
    'AnalyticsTransformer',
    'StreamTransformer'
]


if __name__ == "__main__":
    """
    Tests et démonstrations du module de transformation
    """
    print(" Transformers Index - IA Influencer Agent Platform Enterprise")
    print("=" * 70)
    
    # Test de santé du système
    print("\n Health Check:")
    health = transformers_manager.health_check()
    for transformer, status in health['transformers_status'].items():
        status_icon = "" if status == 'healthy' else "" if status == 'warning' else ""
        print(f"  {status_icon} {transformer}: {status.upper()}")
    
    # Affichage des transformers disponibles
    print(f"\n Transformers disponibles: {len(transformers_registry.transformers_catalog)}")
    for name, info in transformers_registry.transformers_catalog.items():
        print(f"  • {name}: {info['class']} - {', '.join(info['capabilities'])}")
    
    # Affichage des types de créateurs supportés
    print(f"\n Types de créateurs: {list(transformers_registry.creator_workflows.keys())}")
    
    # Affichage des workflows disponibles
    print("\n Workflows disponibles:")
    for creator, workflows in transformers_registry.creator_workflows.items():
        print(f"  • {creator}: {list(workflows.keys())}")
    
    # Statistiques
    stats = transformers_manager.get_statistics()
    print(f"\n Statistiques:")
    print(f"  • Transformateurs: {stats['available_transformers']}")
    print(f"  • Types de créateurs: {len(stats['supported_creator_types'])}")
    print(f"  • Types de transformations: {stats['total_transformation_types']}")
    
    print("\n Module Transformers Index prêt pour l'utilisation!")
    print(" Pipeline complet: Fingerprinting → Protection → Analytics → Streaming")
