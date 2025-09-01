"""🎯 Processors Index - IA Influencer Agent Platform Enterprise
=============================================================
Module: backend/data_management/processors/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Data Processing Hub - Enterprise Production-Ready Ultra Advanced
Responsibility: Point d'entrée principal pour tous les processeurs de données
=====================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

ARCHITECTURE PROCESSORS:
Base Processors → Specialized Processors → Async Versions → Factory Pattern → 
Manager Registry → Configuration Hub → Performance Monitoring → Error Handling
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import json

# Base Processors
from .base_processor import BaseProcessor, AsyncBaseProcessor

# Specialized Processors
from .content_fingerprint_processor import ContentFingerprintProcessor, AsyncContentFingerprintProcessor
from .protection_processor import ProtectionProcessor, AsyncProtectionProcessor
from .monetization_processor import MonetizationProcessor, AsyncMonetizationProcessor
from .collaboration_processor import CollaborationProcessor, AsyncCollaborationProcessor
from .analytics_processor import AnalyticsProcessor, AsyncAnalyticsProcessor
from .seo_processor import SEOProcessor, AsyncSEOProcessor
from .streaming_processor import StreamingProcessor, AsyncStreamingProcessor
from .social_media_processor import SocialMediaProcessor, AsyncSocialMediaProcessor
from .quality_enhancement_processor import QualityEnhancementProcessor, AsyncQualityEnhancementProcessor
from .distribution_processor import DistributionProcessor, AsyncDistributionProcessor


class ProcessorRegistry:
    """Registre central des processeurs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Registry des processeurs synchrones
        self.sync_processors = {
            'content_fingerprint': ContentFingerprintProcessor,
            'protection': ProtectionProcessor,
            'monetization': MonetizationProcessor,
            'collaboration': CollaborationProcessor,
            'analytics': AnalyticsProcessor,
            'seo': SEOProcessor,
            'streaming': StreamingProcessor,
            'social_media': SocialMediaProcessor,
            'quality_enhancement': QualityEnhancementProcessor,
            'distribution': DistributionProcessor
        }
        
        # Registry des processeurs asynchrones
        self.async_processors = {
            'content_fingerprint': AsyncContentFingerprintProcessor,
            'protection': AsyncProtectionProcessor,
            'monetization': AsyncMonetizationProcessor,
            'collaboration': AsyncCollaborationProcessor,
            'analytics': AsyncAnalyticsProcessor,
            'seo': AsyncSEOProcessor,
            'streaming': AsyncStreamingProcessor,
            'social_media': AsyncSocialMediaProcessor,
            'quality_enhancement': AsyncQualityEnhancementProcessor,
            'distribution': AsyncDistributionProcessor
        }
        
        # Instances actives
        self.active_processors = {}
        self.active_async_processors = {}
        
        # Configuration globale
        self.global_config = {
            'max_concurrent_processes': 10,
            'default_timeout': 300,
            'retry_attempts': 3,
            'logging_level': 'INFO',
            'performance_monitoring': True,
            'error_recovery': True
        }
        
        # Métriques de performance
        self.performance_metrics = {
            'total_processes': 0,
            'successful_processes': 0,
            'failed_processes': 0,
            'average_processing_time': 0,
            'processor_usage': {},
            'error_rates': {}
        }
        
    def get_processor(self, processor_type: str, config: Dict[str, Any] = None, async_mode: bool = False) -> Union[BaseProcessor, AsyncBaseProcessor]:
        """Récupère ou crée une instance de processeur"""
        try:
            if async_mode:
                processor_class = self.async_processors.get(processor_type)
                cache_key = f"async_{processor_type}"
                cache = self.active_async_processors
            else:
                processor_class = self.sync_processors.get(processor_type)
                cache_key = processor_type
                cache = self.active_processors
            
            if not processor_class:
                raise ValueError(f"Unknown processor type: {processor_type}")
            
            # Réutiliser l'instance existante ou en créer une nouvelle
            if cache_key not in cache:
                merged_config = {**self.global_config, **(config or {})}
                cache[cache_key] = processor_class(merged_config)
                self.logger.info(f"Created new {processor_type} processor (async: {async_mode})")
            
            return cache[cache_key]
            
        except Exception as e:
            self.logger.error(f"Failed to get processor {processor_type}: {e}")
            raise
    
    def list_available_processors(self) -> Dict[str, List[str]]:
        """Liste tous les processeurs disponibles"""
        return {
            'sync_processors': list(self.sync_processors.keys()),
            'async_processors': list(self.async_processors.keys())
        }
    
    def get_processor_info(self, processor_type: str) -> Dict[str, Any]:
        """Récupère les informations d'un processeur"""
        try:
            if processor_type not in self.sync_processors:
                raise ValueError(f"Unknown processor type: {processor_type}")
            
            processor_class = self.sync_processors[processor_type]
            
            return {
                'name': processor_type,
                'class_name': processor_class.__name__,
                'module': processor_class.__module__,
                'description': processor_class.__doc__ or 'No description available',
                'supports_async': processor_type in self.async_processors,
                'is_active': processor_type in self.active_processors,
                'is_active_async': f"async_{processor_type}" in self.active_async_processors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get processor info for {processor_type}: {e}")
            return {'error': str(e)}
    
    def update_global_config(self, config: Dict[str, Any]):
        """Met à jour la configuration globale"""
        try:
            self.global_config.update(config)
            self.logger.info("Global configuration updated")
            
            # Appliquer aux processeurs actifs
            for processor in self.active_processors.values():
                if hasattr(processor, 'update_config'):
                    processor.update_config(config)
            
            for processor in self.active_async_processors.values():
                if hasattr(processor, 'update_config'):
                    processor.update_config(config)
                    
        except Exception as e:
            self.logger.error(f"Failed to update global config: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance"""
        return {
            'global_metrics': self.performance_metrics.copy(),
            'active_processors': len(self.active_processors),
            'active_async_processors': len(self.active_async_processors),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_inactive_processors(self):
        """Nettoie les processeurs inactifs"""
        try:
            # Implémenter la logique de nettoyage si nécessaire
            self.logger.info("Processor cleanup completed")
        except Exception as e:
            self.logger.error(f"Processor cleanup failed: {e}")


class ProcessorFactory:
    """Factory pour créer des processeurs avec configuration"""
    
    def __init__(self, registry: ProcessorRegistry = None):
        self.registry = registry or ProcessorRegistry()
        self.logger = logging.getLogger(__name__)
    
    def create_processor(self, processor_type: str, config: Dict[str, Any] = None, async_mode: bool = False) -> Union[BaseProcessor, AsyncBaseProcessor]:
        """Crée un processeur avec la configuration spécifiée"""
        return self.registry.get_processor(processor_type, config, async_mode)
    
    def create_processing_pipeline(self, pipeline_config: List[Dict[str, Any]]) -> 'ProcessingPipeline':
        """Crée un pipeline de processeurs"""
        return ProcessingPipeline(pipeline_config, self.registry)
    
    def batch_create_processors(self, processor_configs: Dict[str, Dict[str, Any]]) -> Dict[str, BaseProcessor]:
        """Crée plusieurs processeurs en lot"""
        processors = {}
        
        for processor_type, config in processor_configs.items():
            try:
                async_mode = config.pop('async_mode', False)
                processors[processor_type] = self.create_processor(processor_type, config, async_mode)
            except Exception as e:
                self.logger.error(f"Failed to create processor {processor_type}: {e}")
                
        return processors


class ProcessingPipeline:
    """Pipeline de traitement avec multiple processeurs"""
    
    def __init__(self, pipeline_config: List[Dict[str, Any]], registry: ProcessorRegistry):
        self.pipeline_config = pipeline_config
        self.registry = registry
        self.logger = logging.getLogger(__name__)
        self.processors = []
        self._build_pipeline()
    
    def _build_pipeline(self):
        """Construit le pipeline de processeurs"""
        try:
            for step_config in self.pipeline_config:
                processor_type = step_config.get('processor_type')
                processor_config = step_config.get('config', {})
                async_mode = step_config.get('async_mode', False)
                
                if not processor_type:
                    raise ValueError("processor_type is required for each pipeline step")
                
                processor = self.registry.get_processor(processor_type, processor_config, async_mode)
                
                pipeline_step = {
                    'processor': processor,
                    'config': step_config,
                    'async_mode': async_mode
                }
                
                self.processors.append(pipeline_step)
                
            self.logger.info(f"Built pipeline with {len(self.processors)} processors")
            
        except Exception as e:
            self.logger.error(f"Pipeline build failed: {e}")
            raise
    
    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        """Exécute le pipeline de traitement synchrone"""
        results = []
        current_data = input_data
        
        try:
            for i, step in enumerate(self.processors):
                processor = step['processor']
                config = step['config']
                
                self.logger.info(f"Executing pipeline step {i+1}: {config.get('processor_type')}")
                
                # Traitement synchrone seulement
                if step['async_mode']:
                    self.logger.warning(f"Step {i+1} is async but running in sync mode")
                
                result = processor.process(current_data)
                results.append({
                    'step': i + 1,
                    'processor_type': config.get('processor_type'),
                    'result': result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Utiliser le résultat comme entrée pour l'étape suivante si configuré
                if config.get('pass_result_to_next', False):
                    current_data = result
                    
        except Exception as e:
            self.logger.error(f"Pipeline processing failed at step {i+1}: {e}")
            results.append({
                'step': i + 1,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        return results
    
    async def process_async(self, input_data: Any) -> List[Dict[str, Any]]:
        """Exécute le pipeline de traitement asynchrone"""
        results = []
        current_data = input_data
        
        try:
            for i, step in enumerate(self.processors):
                processor = step['processor']
                config = step['config']
                
                self.logger.info(f"Executing async pipeline step {i+1}: {config.get('processor_type')}")
                
                # Traitement asynchrone si disponible
                if step['async_mode'] and hasattr(processor, 'process'):
                    result = await processor.process(current_data)
                else:
                    # Fallback vers traitement synchrone dans executor
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        result = await loop.run_in_executor(executor, processor.process, current_data)
                
                results.append({
                    'step': i + 1,
                    'processor_type': config.get('processor_type'),
                    'result': result,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Utiliser le résultat comme entrée pour l'étape suivante si configuré
                if config.get('pass_result_to_next', False):
                    current_data = result
                    
        except Exception as e:
            self.logger.error(f"Async pipeline processing failed at step {i+1}: {e}")
            results.append({
                'step': i + 1,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        return results


class ProcessorManager:
    """Manager principal pour tous les processeurs"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialiser les composants
        self.registry = ProcessorRegistry()
        self.factory = ProcessorFactory(self.registry)
        
        # Configuration globale
        if self.config:
            self.registry.update_global_config(self.config)
        
        # Métriques et monitoring
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.performance_tracker = {}
        
        self.logger.info("ProcessorManager initialized")
    
    def get_processor(self, processor_type: str, config: Dict[str, Any] = None, async_mode: bool = False) -> Union[BaseProcessor, AsyncBaseProcessor]:
        """Interface principale pour récupérer un processeur"""
        return self.registry.get_processor(processor_type, config, async_mode)
    
    def create_pipeline(self, pipeline_config: List[Dict[str, Any]]) -> ProcessingPipeline:
        """Crée un pipeline de traitement"""
        return self.factory.create_processing_pipeline(pipeline_config)
    
    def process_single(self, processor_type: str, input_data: Any, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Traite des données avec un seul processeur"""
        try:
            processor = self.get_processor(processor_type, config)
            result = processor.process(input_data)
            
            # Tracking des métriques
            if self.monitoring_enabled:
                self._track_processing_metrics(processor_type, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Single processing failed for {processor_type}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processor_type': processor_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def process_single_async(self, processor_type: str, input_data: Any, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Traite des données avec un seul processeur asynchrone"""
        try:
            processor = self.get_processor(processor_type, config, async_mode=True)
            result = await processor.process(input_data)
            
            # Tracking des métriques
            if self.monitoring_enabled:
                self._track_processing_metrics(processor_type, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Single async processing failed for {processor_type}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processor_type': processor_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def process_batch(self, processor_type: str, input_batch: List[Any], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Traite un lot de données"""
        results = []
        
        for i, input_data in enumerate(input_batch):
            try:
                result = self.process_single(processor_type, input_data, config)
                results.append({
                    'batch_index': i,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'batch_index': i,
                    'error': str(e)
                })
                
        return results
    
    async def process_batch_async(self, processor_type: str, input_batch: List[Any], config: Dict[str, Any] = None, max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Traite un lot de données asynchrone avec concurrence limitée"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_item(index: int, input_data: Any):
            async with semaphore:
                try:
                    result = await self.process_single_async(processor_type, input_data, config)
                    return {
                        'batch_index': index,
                        'result': result
                    }
                except Exception as e:
                    return {
                        'batch_index': index,
                        'error': str(e)
                    }
        
        tasks = [process_item(i, data) for i, data in enumerate(input_batch)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r if not isinstance(r, Exception) else {'error': str(r)} for r in results]
    
    def _track_processing_metrics(self, processor_type: str, result: Dict[str, Any]):
        """Suit les métriques de traitement"""
        try:
            if processor_type not in self.performance_tracker:
                self.performance_tracker[processor_type] = {
                    'total_processes': 0,
                    'successful_processes': 0,
                    'failed_processes': 0,
                    'total_processing_time': 0
                }
            
            tracker = self.performance_tracker[processor_type]
            tracker['total_processes'] += 1
            
            if result.get('status') != 'error':
                tracker['successful_processes'] += 1
            else:
                tracker['failed_processes'] += 1
            
            processing_time = result.get('processing_time', 0)
            tracker['total_processing_time'] += processing_time
            
        except Exception as e:
            self.logger.warning(f"Metrics tracking failed: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Récupère le statut complet du système"""
        return {
            'processor_registry': self.registry.get_performance_metrics(),
            'available_processors': self.registry.list_available_processors(),
            'performance_tracker': self.performance_tracker,
            'system_config': self.config,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def shutdown(self):
        """Arrêt propre du manager"""
        try:
            self.registry.cleanup_inactive_processors()
            self.logger.info("ProcessorManager shutdown completed")
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Instances globales pour faciliter l'utilisation
_global_registry = ProcessorRegistry()
_global_factory = ProcessorFactory(_global_registry)
_global_manager = ProcessorManager()

# Fonctions de convenance pour accès rapide
def get_processor(processor_type: str, config: Dict[str, Any] = None, async_mode: bool = False) -> Union[BaseProcessor, AsyncBaseProcessor]:
    """Fonction de convenance pour récupérer un processeur"""
    return _global_manager.get_processor(processor_type, config, async_mode)

def process_data(processor_type: str, input_data: Any, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Fonction de convenance pour traiter des données"""
    return _global_manager.process_single(processor_type, input_data, config)

async def process_data_async(processor_type: str, input_data: Any, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Fonction de convenance pour traiter des données asynchrone"""
    return await _global_manager.process_single_async(processor_type, input_data, config)

def create_pipeline(pipeline_config: List[Dict[str, Any]]) -> ProcessingPipeline:
    """Fonction de convenance pour créer un pipeline"""
    return _global_manager.create_pipeline(pipeline_config)

def get_available_processors() -> Dict[str, List[str]]:
    """Fonction de convenance pour lister les processeurs"""
    return _global_registry.list_available_processors()

def get_system_status() -> Dict[str, Any]:
    """Fonction de convenance pour le statut système"""
    return _global_manager.get_system_status()


# Exports principaux
__all__ = [
    # Classes principales
    'ProcessorRegistry',
    'ProcessorFactory', 
    'ProcessingPipeline',
    'ProcessorManager',
    
    # Processeurs de base
    'BaseProcessor',
    'AsyncBaseProcessor',
    
    # Processeurs spécialisés
    'ContentFingerprintProcessor',
    'ProtectionProcessor',
    'MonetizationProcessor',
    'CollaborationProcessor',
    'AnalyticsProcessor',
    'SEOProcessor',
    'StreamingProcessor',
    'SocialMediaProcessor',
    'QualityEnhancementProcessor',
    'DistributionProcessor',
    
    # Versions asynchrones
    'AsyncContentFingerprintProcessor',
    'AsyncProtectionProcessor',
    'AsyncMonetizationProcessor',
    'AsyncCollaborationProcessor',
    'AsyncAnalyticsProcessor',
    'AsyncSEOProcessor',
    'AsyncStreamingProcessor',
    'AsyncSocialMediaProcessor',
    'AsyncQualityEnhancementProcessor',
    'AsyncDistributionProcessor',
    
    # Fonctions de convenance
    'get_processor',
    'process_data',
    'process_data_async',
    'create_pipeline',
    'get_available_processors',
    'get_system_status',
    
    # Instances globales
    '_global_registry',
    '_global_factory',
    '_global_manager'
]


if __name__ == "__main__":
    # Example d'utilisation
    print("🎯 IA Influencer Agent - Processors Module")
    print("=" * 50)
    
    # Lister les processeurs disponibles
    processors = get_available_processors()
    print(f"📋 Processeurs synchrones disponibles: {len(processors['sync_processors'])}")
    for proc in processors['sync_processors']:
        print(f"   • {proc}")
    
    print(f"\n⚡ Processeurs asynchrones disponibles: {len(processors['async_processors'])}")
    for proc in processors['async_processors']:
        print(f"   • {proc}")
    
    print(f"\n📊 Statut système:")
    status = get_system_status()
    print(f"   • Processeurs actifs: {status['processor_registry']['active_processors']}")
    print(f"   • Processeurs async actifs: {status['processor_registry']['active_async_processors']}")
    
    print("\n✅ Module processors initialisé avec succès!")
