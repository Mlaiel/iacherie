"""
Storage Agent - Index Principal & Point d'Entrée Central
========================================================

Point d'entrée principal pour le système de stockage multi-backend intelligent.
Fournit une interface unifiée pour toutes les opérations de stockage, traitement,
optimisation et sauvegarde de contenu.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  AVIS JURIDIQUE CRITIQUE:
Cette technologie d'agent de stockage est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, distribution, ingénierie inverse ou commercialisation est strictement interdite.
Contact: mlaiel@live.de pour demandes de licence UNIQUEMENT.

Spécialités de l'Équipe:
- Développeur IA Principal & Ingénieur Backend Senior: Fahed Mlaiel
- Ingénieur Machine Learning & Spécialiste Traitement Audio: Fahed Mlaiel  
- Administrateur Base Données & Expert Sécurité: Fahed Mlaiel
- Architecte Microservices & Ingénieur DevOps: Fahed Mlaiel
- Ingénieur Prompt IA & Spécialiste Protection Contenu: Fahed Mlaiel
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from .storage_orchestrator import StorageOrchestrator, StorageStrategy, StorageRequest
from .backend_manager import BackendManager, StorageBackend
from .file_processor import FileProcessor, ProcessingType
from .content_optimizer import ContentOptimizer, OptimizationType
from .backup_manager import BackupManager, BackupType

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageAgentIndex:
    """
    Index principal et coordinateur central pour le Storage Agent.
    Fournit une interface unifiée pour toutes les opérations de stockage.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise l'index principal du Storage Agent
        
        Args:
            config: Configuration optionnelle pour tous les composants
        """
        self.config = config or {}
        self._initialize_components()
        self._setup_logging()
        
    def _initialize_components(self):
        """Initialise tous les composants du Storage Agent"""
        logger.info(" Initialisation des composants Storage Agent...")
        
        # Orchestrateur principal
        self.orchestrator = StorageOrchestrator(self.config.get('orchestrator', {}))
        
        # Gestionnaire de backends
        self.backend_manager = BackendManager(self.config.get('backends', {}))
        
        # Processeur de fichiers
        self.file_processor = FileProcessor(self.config.get('processing', {}))
        
        # Optimiseur de contenu
        self.content_optimizer = ContentOptimizer(self.config.get('optimization', {}))
        
        # Gestionnaire de sauvegardes
        self.backup_manager = BackupManager(self.config.get('backup', {}))
        
        logger.info(" Tous les composants Storage Agent initialisés avec succès")
        
    def _setup_logging(self):
        """Configure le logging pour tous les composants"""
        log_level = self.config.get('log_level', 'INFO')
        logging.getLogger('storage_agent').setLevel(getattr(logging, log_level))
        
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé de tous les composants du Storage Agent
        
        Returns:
            Dict contenant l'état de santé de tous les composants
        """
        logger.info(" Vérification santé Storage Agent...")
        
        health_status = {
            'overall_status': 'healthy',
            'timestamp': asyncio.get_event_loop().time(),
            'components': {}
        }
        
        try:
            # Vérification orchestrateur
            health_status['components']['orchestrator'] = {
                'status': 'healthy',
                'active_strategies': len(self.orchestrator.strategies),
                'processed_files': getattr(self.orchestrator, 'processed_count', 0)
            }
            
            # Vérification backend manager
            backend_health = await self.backend_manager.check_all_backends_health()
            health_status['components']['backend_manager'] = {
                'status': 'healthy' if backend_health['healthy_backends'] > 0 else 'unhealthy',
                'healthy_backends': backend_health['healthy_backends'],
                'total_backends': backend_health['total_backends']
            }
            
            # Vérification processeur de fichiers
            health_status['components']['file_processor'] = {
                'status': 'healthy',
                'supported_formats': len(self.file_processor.supported_formats),
                'active_workers': getattr(self.file_processor, 'active_workers', 0)
            }
            
            # Vérification optimiseur de contenu
            health_status['components']['content_optimizer'] = {
                'status': 'healthy',
                'optimization_types': len(self.content_optimizer.optimization_types),
                'ai_models_loaded': getattr(self.content_optimizer, 'models_loaded', False)
            }
            
            # Vérification gestionnaire de sauvegardes
            health_status['components']['backup_manager'] = {
                'status': 'healthy',
                'active_backups': len(getattr(self.backup_manager, 'active_backups', [])),
                'scheduled_backups': len(getattr(self.backup_manager, 'scheduled_backups', []))
            }
            
        except Exception as e:
            logger.error(f" Erreur lors de la vérification santé: {e}")
            health_status['overall_status'] = 'unhealthy'
            health_status['error'] = str(e)
            
        logger.info(f" Vérification santé terminée: {health_status['overall_status']}")
        return health_status
        
    async def store_content(
        self,
        file_path: Union[str, Path],
        filename: Optional[str] = None,
        strategy: StorageStrategy = StorageStrategy.HYBRID,
        optimize: bool = True,
        backup: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Interface principale pour stocker du contenu avec traitement complet
        
        Args:
            file_path: Chemin vers le fichier à stocker
            filename: Nom personnalisé pour le fichier (optionnel)
            strategy: Stratégie de stockage à utiliser
            optimize: Activer l'optimisation du contenu
            backup: Créer une sauvegarde automatique
            metadata: Métadonnées additionnelles
            
        Returns:
            Dict contenant les résultats de l'opération de stockage
        """
        logger.info(f" Stockage contenu: {file_path} avec stratégie {strategy.value}")
        
        try:
            # Créer la requête de stockage
            request = StorageRequest(
                file_path=str(file_path),
                filename=filename or Path(file_path).name,
                strategy=strategy,
                optimize=optimize,
                backup=backup,
                metadata=metadata or {}
            )
            
            # Exécuter le stockage via l'orchestrateur
            result = await self.orchestrator.store_file(request)
            
            logger.info(f" Contenu stocké avec succès: {result.file_id}")
            return {
                'success': True,
                'file_id': result.file_id,
                'storage_info': result.storage_info,
                'optimization_results': result.optimization_results,
                'backup_info': result.backup_info,
                'cdn_urls': result.cdn_urls
            }
            
        except Exception as e:
            logger.error(f" Erreur stockage contenu: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
            
    async def retrieve_content(
        self,
        file_id: str,
        prefer_cdn: bool = True,
        quality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Récupère du contenu stocké
        
        Args:
            file_id: Identifiant du fichier à récupérer
            prefer_cdn: Préférer les URLs CDN si disponibles
            quality: Qualité spécifique à récupérer
            
        Returns:
            Dict contenant les informations et URLs du fichier
        """
        logger.info(f" Récupération contenu: {file_id}")
        
        try:
            file_info = await self.orchestrator.retrieve_file(
                file_id=file_id,
                prefer_cdn=prefer_cdn,
                quality=quality
            )
            
            logger.info(f" Contenu récupéré avec succès: {file_id}")
            return {
                'success': True,
                'file_info': file_info
            }
            
        except Exception as e:
            logger.error(f" Erreur récupération contenu: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_id': file_id
            }
            
    async def optimize_content(
        self,
        file_path: Union[str, Path],
        optimization_type: OptimizationType = OptimizationType.COMPREHENSIVE,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimise du contenu existant
        
        Args:
            file_path: Chemin vers le fichier à optimiser
            optimization_type: Type d'optimisation à appliquer
            options: Options d'optimisation personnalisées
            
        Returns:
            Dict contenant les résultats de l'optimisation
        """
        logger.info(f" Optimisation contenu: {file_path}")
        
        try:
            result = await self.content_optimizer.optimize_content(
                file_path=str(file_path),
                optimization_type=optimization_type,
                options=options or {}
            )
            
            logger.info(f" Contenu optimisé avec succès")
            return {
                'success': True,
                'optimization_result': result
            }
            
        except Exception as e:
            logger.error(f" Erreur optimisation contenu: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }
            
    async def create_backup(
        self,
        file_ids: List[str],
        backup_type: BackupType = BackupType.INCREMENTAL,
        destination_backends: Optional[List[StorageBackend]] = None
    ) -> Dict[str, Any]:
        """
        Crée une sauvegarde de fichiers spécifiés
        
        Args:
            file_ids: Liste des identifiants de fichiers à sauvegarder
            backup_type: Type de sauvegarde à créer
            destination_backends: Backends de destination spécifiques
            
        Returns:
            Dict contenant les informations de sauvegarde
        """
        logger.info(f" Création sauvegarde pour {len(file_ids)} fichiers")
        
        try:
            backup_result = await self.backup_manager.create_backup(
                file_ids=file_ids,
                backup_type=backup_type,
                destination_backends=destination_backends
            )
            
            logger.info(f" Sauvegarde créée avec succès: {backup_result.backup_id}")
            return {
                'success': True,
                'backup_result': backup_result
            }
            
        except Exception as e:
            logger.error(f" Erreur création sauvegarde: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_ids': file_ids
            }
            
    async def get_analytics(self) -> Dict[str, Any]:
        """
        Récupère les analytics et métriques du Storage Agent
        
        Returns:
            Dict contenant toutes les métriques système
        """
        logger.info(" Récupération analytics Storage Agent")
        
        try:
            analytics = {
                'storage_stats': await self._get_storage_stats(),
                'processing_stats': await self._get_processing_stats(),
                'optimization_stats': await self._get_optimization_stats(),
                'backup_stats': await self._get_backup_stats(),
                'performance_metrics': await self._get_performance_metrics()
            }
            
            logger.info(" Analytics récupérées avec succès")
            return analytics
            
        except Exception as e:
            logger.error(f" Erreur récupération analytics: {e}")
            return {'error': str(e)}
            
    async def _get_storage_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de stockage"""



        return {
            'total_files': getattr(self.orchestrator, 'total_files', 0),
            'total_size': getattr(self.orchestrator, 'total_size', 0),
            'backend_usage': await self.backend_manager.get_usage_stats(),
            'strategy_distribution': getattr(self.orchestrator, 'strategy_stats', {})
        }
        
    async def _get_processing_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de traitement"""



        return {
            'files_processed': getattr(self.file_processor, 'files_processed', 0),
            'processing_time_avg': getattr(self.file_processor, 'avg_processing_time', 0),
            'format_distribution': getattr(self.file_processor, 'format_stats', {}),
            'error_rate': getattr(self.file_processor, 'error_rate', 0)
        }
        
    async def _get_optimization_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'optimisation"""



        return {
            'optimizations_performed': getattr(self.content_optimizer, 'optimizations_count', 0),
            'avg_size_reduction': getattr(self.content_optimizer, 'avg_size_reduction', 0),
            'seo_improvements': getattr(self.content_optimizer, 'seo_improvements', 0),
            'quality_scores': getattr(self.content_optimizer, 'quality_scores', {})
        }
        
    async def _get_backup_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de sauvegarde"""



        return {
            'total_backups': getattr(self.backup_manager, 'total_backups', 0),
            'backup_size': getattr(self.backup_manager, 'total_backup_size', 0),
            'success_rate': getattr(self.backup_manager, 'backup_success_rate', 0),
            'retention_compliance': getattr(self.backup_manager, 'retention_compliance', 0)
        }
        
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance système"""



        return {
            'response_time': getattr(self, 'avg_response_time', 0),
            'throughput': getattr(self, 'throughput', 0),
            'cpu_usage': getattr(self, 'cpu_usage', 0),
            'memory_usage': getattr(self, 'memory_usage', 0),
            'uptime': getattr(self, 'uptime', 0)
        }

# Fonction factory principale pour créer l'index
def create_storage_agent_index(config: Optional[Dict[str, Any]] = None) -> StorageAgentIndex:
    """
    Factory function pour créer l'index principal du Storage Agent
    
    Args:
        config: Configuration optionnelle pour tous les composants
        
    Returns:
        StorageAgentIndex: Instance configurée de l'index principal
    """



    return StorageAgentIndex(config)

# Configuration par défaut recommandée
DEFAULT_CONFIG = {
    'orchestrator': {
        'default_strategy': StorageStrategy.HYBRID.value,
        'auto_optimization': True,
        'auto_backup': True
    },
    'backends': {
        'local': {'enabled': True, 'priority': 1},
        's3': {'enabled': True, 'priority': 2},
        'minio': {'enabled': True, 'priority': 3}
    },
    'processing': {
        'max_workers': 8,
        'timeout': 300,
        'auto_format_detection': True
    },
    'optimization': {
        'default_quality': 85,
        'enable_seo': True,
        'enable_compression': True
    },
    'backup': {
        'retention_days': 30,
        'compression': True,
        'encryption': True,
        'schedule': '0 2 * * *'
    },
    'log_level': 'INFO'
}

# Point d'entrée principal
if __name__ == "__main__":
    # Exemple d'utilisation de l'index
    async def main():
        # Créer l'index avec configuration par défaut
        storage_index = create_storage_agent_index(DEFAULT_CONFIG)
        
        # Vérifier la santé du système
        health = await storage_index.health_check()
        print(f"État santé Storage Agent: {health['overall_status']}")
        
        # Exemple de stockage de contenu
        result = await storage_index.store_content(
            file_path="example.jpg",
            strategy=StorageStrategy.PERFORMANCE,
            optimize=True,
            backup=True
        )
        
        if result['success']:
            print(f"Fichier stocké avec succès: {result['file_id']}")
        else:
            print(f"Erreur stockage: {result['error']}")
            
        # Récupérer les analytics
        analytics = await storage_index.get_analytics()
        print(f"Analytics système: {analytics}")
        
    # Exécuter l'exemple
    asyncio.run(main())
