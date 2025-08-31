"""
Vision Agent Index - Main Entry Point
====================================

Point d'entrée principal pour le système de vision IA-Influencer-Agent.
Fournit une interface unifiée et simplifiée pour tous les composants vision.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  AVERTISSEMENT LÉGAL CRITIQUE:
Ce code et cette conception architecturale sont la propriété intellectuelle exclusive de Fahed Mlaiel.
L'utilisation, la copie, la distribution ou la commercialisation non autorisées sont strictement interdites.
Contact: mlaiel@live.de pour les demandes de licence.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# Imports des composants principaux
from .vision_orchestrator import VisionOrchestrator
from .config import VisionAgentConfig, vision_config
from .image_processor import ImageProcessor
from .video_analyzer import VideoAnalyzer
from .object_detector import ObjectDetector
from .visual_similarity import VisualSimilarityMatcher
from .face_recognition import FaceRecognitionSystem
from .optical_character_reader import OpticalCharacterReader
from .scene_analyzer import SceneAnalyzer
from .metadata_extractor import MetadataExtractor

# Configuration du logging
logger = logging.getLogger(__name__)

# Classes de requête et réponse simplifiées
class VisionRequest:
    """Requête simplifiée pour le traitement vision"""
    
    def __init__(
        self,
        content_id: str,
        file_path: Optional[str] = None,
        file_data: Optional[bytes] = None,
        content_type: str = "image",
        tasks: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        self.content_id = content_id
        self.file_path = file_path
        self.file_data = file_data
        self.content_type = content_type
        self.tasks = tasks or ['detection', 'quality', 'metadata']
        self.options = options or {}
        self.created_at = datetime.now()


class VisionResponse:
    """Réponse simplifiée du traitement vision"""
    
    def __init__(
        self,
        content_id: str,
        success: bool = False,
        results: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        processing_time: float = 0.0,
        confidence: float = 0.0
    ):
        self.content_id = content_id
        self.success = success
        self.results = results or {}
        self.errors = errors or []
        self.processing_time = processing_time
        self.confidence = confidence
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir la réponse en dictionnaire"""



        return {
            'content_id': self.content_id,
            'success': self.success,
            'results': self.results,
            'errors': self.errors,
            'processing_time': self.processing_time,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }


class VisionAgentIndex:
    """
    Point d'entrée principal et interface unifiée pour le système Vision Agent
    
    Cette classe fournit une API simplifiée pour accéder à toutes les fonctionnalités
    du système de vision IA-Influencer-Agent.
    """
    
    def __init__(self, config: Optional[VisionAgentConfig] = None):
        """
        Initialiser l'index Vision Agent
        
        Args:
            config: Configuration optionnelle, utilise la configuration par défaut si non fournie
        """
        self.config = config or vision_config
        self.orchestrator: Optional[VisionOrchestrator] = None
        self.is_initialized = False
        
        # Statistiques d'utilisation
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'last_request_time': None
        }
        
        logger.info("Vision Agent Index créé avec succès")
    
    async def initialize(self) -> bool:
        """
        Initialiser tous les composants du système vision
        
        Returns:
            True si l'initialisation est réussie, False sinon
        """



        try:
            logger.info("Initialisation du système Vision Agent...")
            
            # Créer et initialiser l'orchestrateur principal
            self.orchestrator = VisionOrchestrator()
            success = await self.orchestrator.initialize()
            
            if success:
                self.is_initialized = True
                logger.info(" Système Vision Agent initialisé avec succès")
                return True
            else:
                logger.error(" Échec de l'initialisation du système Vision Agent")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système Vision Agent: {e}")
            return False
    
    async def process(
        self,
        content_id: str,
        file_path: Optional[str] = None,
        file_data: Optional[bytes] = None,
        content_type: str = "image",
        tasks: Optional[List[str]] = None,
        **options
    ) -> VisionResponse:
        """
        Traiter du contenu visuel avec l'interface simplifiée
        
        Args:
            content_id: Identifiant unique du contenu
            file_path: Chemin vers le fichier (optionnel)
            file_data: Données binaires du fichier (optionnel)
            content_type: Type de contenu ('image', 'video')
            tasks: Liste des tâches à effectuer
            **options: Options supplémentaires
            
        Returns:
            VisionResponse avec les résultats du traitement
        """
        start_time = datetime.now()
        
        # Vérifier l'initialisation
        if not self.is_initialized:
            await self.initialize()
        
        if not self.is_initialized:
            return VisionResponse(
                content_id=content_id,
                success=False,
                errors=["Système non initialisé"]
            )
        
        try:
            # Mettre à jour les statistiques
            self.stats['total_requests'] += 1
            self.stats['last_request_time'] = start_time
            
            # Créer la requête Vision
            request = VisionRequest(
                content_id=content_id,
                file_path=file_path,
                file_data=file_data,
                content_type=content_type,
                tasks=tasks,
                options=options
            )
            
            # Convertir vers le format orchestrateur
            orchestrator_request = await self._convert_to_orchestrator_request(request)
            
            # Traiter via l'orchestrateur
            result = await self.orchestrator.process_content(orchestrator_request)
            
            # Calculer le temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Convertir le résultat vers le format simplifié
            response = await self._convert_from_orchestrator_result(
                result, content_id, processing_time
            )
            
            # Mettre à jour les statistiques
            if response.success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            
            self.stats['total_processing_time'] += processing_time
            self.stats['average_processing_time'] = (
                self.stats['total_processing_time'] / self.stats['total_requests']
            )
            
            logger.info(
                f"Traitement terminé pour {content_id} "
                f"en {processing_time:.2f}s (confiance: {response.confidence:.3f})"
            )
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats['failed_requests'] += 1
            
            logger.error(f"Erreur lors du traitement de {content_id}: {e}")
            
            return VisionResponse(
                content_id=content_id,
                success=False,
                errors=[str(e)],
                processing_time=processing_time
            )
    
    async def _convert_to_orchestrator_request(self, request: VisionRequest) -> Any:
        """Convertir VisionRequest vers le format de l'orchestrateur"""
        # Import dynamique pour éviter les imports circulaires
        from ..core.types import VisionProcessingRequest
        
        return VisionProcessingRequest(
            content_id=request.content_id,
            file_path=request.file_path,
            file_data=request.file_data,
            content_type=request.content_type,
            processing_tasks=request.tasks,
            fingerprint_generation=True,
            similarity_threshold=0.8,
            processing_priority="normal",
            metadata_extraction=True,
            **request.options
        )
    
    async def _convert_from_orchestrator_result(
        self, 
        result: Any, 
        content_id: str,
        processing_time: float
    ) -> VisionResponse:
        """Convertir le résultat de l'orchestrateur vers VisionResponse"""
        
        success = result.processing_status in ["completed", "completed_with_errors"]
        
        # Agréger tous les résultats
        aggregated_results = {}
        
        if hasattr(result, 'detection_results') and result.detection_results:
            aggregated_results['objects'] = result.detection_results
        
        if hasattr(result, 'face_results') and result.face_results:
            aggregated_results['faces'] = result.face_results
        
        if hasattr(result, 'ocr_results') and result.ocr_results:
            aggregated_results['text'] = result.ocr_results
        
        if hasattr(result, 'scene_analysis') and result.scene_analysis:
            aggregated_results['scene'] = result.scene_analysis
        
        if hasattr(result, 'quality_metrics') and result.quality_metrics:
            aggregated_results['quality'] = result.quality_metrics
        
        if hasattr(result, 'similarity_data') and result.similarity_data:
            aggregated_results['similarity'] = result.similarity_data
        
        if hasattr(result, 'metadata') and result.metadata:
            aggregated_results['metadata'] = result.metadata
        
        return VisionResponse(
            content_id=content_id,
            success=success,
            results=aggregated_results,
            errors=getattr(result, 'errors', []),
            processing_time=processing_time,
            confidence=getattr(result, 'confidence_score', 0.0)
        )
    
    async def batch_process(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[VisionResponse]:
        """
        Traiter plusieurs contenus en lot
        
        Args:
            requests: Liste des paramètres de requête
            max_concurrent: Nombre maximum de traitements simultanés
            
        Returns:
            Liste des réponses de traitement
        """
        tasks = []
        
        for req_params in requests:
            task = self.process(**req_params)
            tasks.append(task)
        
        # Limiter la concurrence
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(task):
            async with semaphore:
                return await task
        
        limited_tasks = [process_with_limit(task) for task in tasks]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        # Convertir les exceptions en réponses d'erreur
        responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                responses.append(VisionResponse(
                    content_id=f"batch_item_{i}",
                    success=False,
                    errors=[str(result)]
                ))
            else:
                responses.append(result)
        
        return responses
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Obtenir les capacités du système"""



        return {
            'supported_formats': {
                'image': ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp', 'gif'],
                'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
            },
            'available_tasks': [
                'detection',      # Détection d'objets
                'faces',          # Reconnaissance faciale
                'ocr',           # Reconnaissance de texte
                'scene',         # Analyse de scène
                'quality',       # Évaluation de qualité
                'similarity',    # Comparaison visuelle
                'metadata'       # Extraction de métadonnées
            ],
            'processing_modes': ['single', 'batch', 'stream'],
            'max_file_size': '100MB',
            'max_batch_size': 50,
            'gpu_acceleration': True
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'utilisation"""



        return self.stats.copy()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtenir l'état de santé du système"""
        if not self.is_initialized:
            return {
                'status': 'not_initialized',
                'healthy': False,
                'message': 'Système non initialisé'
            }
        
        return {
            'status': 'operational',
            'healthy': True,
            'initialized': self.is_initialized,
            'components_status': 'all_operational',
            'last_request': self.stats['last_request_time'],
            'success_rate': (
                self.stats['successful_requests'] / max(1, self.stats['total_requests']) * 100
            )
        }
    
    async def cleanup(self) -> None:
        """Nettoyer les ressources"""



        try:
            if self.orchestrator:
                await self.orchestrator.cleanup()
            
            self.is_initialized = False
            logger.info("Vision Agent Index nettoyé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")


# Instance globale pour faciliter l'utilisation
_global_vision_agent: Optional[VisionAgentIndex] = None


async def get_vision_agent() -> VisionAgentIndex:
    """Obtenir l'instance globale de Vision Agent (singleton pattern)"""
    global _global_vision_agent
    
    if _global_vision_agent is None:
        _global_vision_agent = VisionAgentIndex()
        await _global_vision_agent.initialize()
    
    return _global_vision_agent


# Fonctions utilitaires d'accès rapide
async def quick_process(
    content_id: str,
    file_path: Optional[str] = None,
    file_data: Optional[bytes] = None,
    content_type: str = "image",
    tasks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Interface rapide pour traiter du contenu
    
    Returns:
        Dictionnaire avec les résultats du traitement
    """
    agent = await get_vision_agent()
    response = await agent.process(
        content_id=content_id,
        file_path=file_path,
        file_data=file_data,
        content_type=content_type,
        tasks=tasks
    )
    return response.to_dict()


async def quick_analyze_image(file_path: str) -> Dict[str, Any]:
    """Analyser rapidement une image"""
    content_id = f"quick_image_{datetime.now().timestamp()}"
    return await quick_process(
        content_id=content_id,
        file_path=file_path,
        content_type="image",
        tasks=['detection', 'quality', 'scene', 'metadata']
    )


async def quick_analyze_video(file_path: str) -> Dict[str, Any]:
    """Analyser rapidement une vidéo"""
    content_id = f"quick_video_{datetime.now().timestamp()}"
    return await quick_process(
        content_id=content_id,
        file_path=file_path,
        content_type="video",
        tasks=['scene', 'quality', 'metadata']
    )


# Fonctions de convenance pour l'API
def create_vision_index(config: Optional[VisionAgentConfig] = None) -> VisionAgentIndex:
    """Créer une nouvelle instance de Vision Agent Index"""



    return VisionAgentIndex(config)


# Métadonnées du module
__version__ = "2.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Exports principaux
__all__ = [
    'VisionAgentIndex',
    'VisionRequest',
    'VisionResponse',
    'get_vision_agent',
    'quick_process',
    'quick_analyze_image',
    'quick_analyze_video',
    'create_vision_index'
]

# Logging d'initialisation
logger.info(f"Vision Agent Index v{__version__} chargé")
logger.info(" Point d'entrée principal prêt")
logger.info("  Code propriétaire - Fahed Mlaiel - Tous droits réservés")
