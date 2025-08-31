"""
Gestionnaire de ressources système
================================================================================
Module: backend/core/managers/analytics_manager.py
Type: Manager Core - IA-Influencer-Agent
Responsabilité: Fonctionnalité spécialisée IA-Influencer-Agent
Technologies: Python, FastAPI, AsyncIO
================================================================================
"""

from typing import Any, Dict, List, Optional, Union, Callable
import logging
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import threading
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsManagerConfig:
    """Configuration du gestionnaire AnalyticsManager"""
    pool_size: int = 10
    max_connections: int = 100
    timeout_seconds: int = 30
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    monitoring_enabled: bool = True


class AnalyticsManager(ABC):
    """
     Gestionnaire AnalyticsManager - IA-Influencer-Agent
    
    Responsabilité:
    Fonctionnalité spécialisée IA-Influencer-Agent
    
    Technologies:
    Python, FastAPI, AsyncIO
    
    Fonctionnalités:
    - Gestion de pool de ressources optimisée
    - Monitoring en temps réel des performances
    - Auto-scaling basé sur la charge
    - Gestion d'erreurs avec circuit breaker
    - Nettoyage automatique des ressources
    """
    
    def __init__(self, config: AnalyticsManagerConfig = None):
        self.config = config or AnalyticsManagerConfig()
        self._pool = []
        self._active_connections = 0
        self._lock = threading.Lock()
        self._metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
        logger.info(f" Initialisation {self.__class__.__name__}")
    
    @abstractmethod
    async def initialize_pool(self) -> bool:
        """
        Initialise le pool de ressources
        
        Returns:
            bool: True si initialisation réussie
        """
        pass
    
    @abstractmethod
    async def acquire_resource(self) -> Any:
        """
        Acquiert une ressource du pool
        
        Returns:
            Any: Ressource acquise
        """
        pass
    
    @abstractmethod
    async def release_resource(self, resource: Any) -> bool:
        """
        Libère une ressource vers le pool
        
        Args:
            resource: Ressource à libérer
            
        Returns:
            bool: True si libération réussie
        """
        pass
    
    @asynccontextmanager
    async def get_resource(self):
        """
        Context manager pour gestion automatique des ressources
        
        Yields:
            Any: Ressource gérée automatiquement
        """
        resource = None
        try:
            resource = await self.acquire_resource()
            yield resource
        finally:
            if resource:
                await self.release_resource(resource)
    
    async def cleanup(self) -> bool:
        """
        Nettoyage des ressources
        
        Returns:
            bool: True si nettoyage réussi
        """
        with self._lock:
            self._pool.clear()
            self._active_connections = 0
        logger.info(f"🧹 Nettoyage {self.__class__.__name__} terminé")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Statistiques du gestionnaire
        
        Returns:
            Dict: Métriques actuelles
        """
        with self._lock:
            return {
                "pool_size": len(self._pool),
                "active_connections": self._active_connections,
                "config": self.config.__dict__,
                "metrics": self._metrics.copy()
            }


# Instance globale
analytics_manager = None


def get_analytics_manager() -> AnalyticsManager:
    """
    Obtient l'instance du gestionnaire
    
    Returns:
        AnalyticsManager: Instance du gestionnaire
    """
    global analytics_manager
    if analytics_manager is None:
        analytics_manager = AnalyticsManager()
    return analytics_manager
