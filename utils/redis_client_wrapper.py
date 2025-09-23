"""
🔄 Redis Client Wrapper - Solution au conflit d'import circulaire
================================================================

Wrapper pour le client Redis qui évite les conflits avec le module local 'redis'.
Cette abstraction permet d'utiliser le package Redis Python sans interférence.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import sys
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Clear any existing redis imports to avoid circular dependency
redis_modules_to_clear = [k for k in sys.modules.keys() if k.startswith('redis') and not k.startswith('redis_client_wrapper')]
for module_name in redis_modules_to_clear:
    if 'redis.' in module_name or module_name == 'redis':
        try:
            del sys.modules[module_name]
        except KeyError:
            pass

# Import Redis package using absolute import
try:
    import redis as external_redis
    REDIS_AVAILABLE = True
    logger.info("External Redis package imported successfully")
except ImportError as e:
    external_redis = None
    REDIS_AVAILABLE = False
    logger.warning(f"Redis package not available: {e}")


class RedisClientWrapper:
    """
    Wrapper pour le client Redis qui évite les conflits d'import
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.kwargs = kwargs
        self.client = None
        
        if REDIS_AVAILABLE:
            try:
                self.client = external_redis.Redis(host=host, port=port, db=db, **kwargs)
                logger.info(f"Redis client connected to {host}:{port}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.client = None
        else:
            logger.warning("Redis not available, using mock client")
    
    def get_client(self) -> Optional[Any]:
        """Retourne le client Redis ou None si non disponible"""
        return self.client
    
    def is_available(self) -> bool:
        """Vérifie si Redis est disponible"""
        return self.client is not None
    
    def ping(self) -> bool:
        """Test de connexion Redis"""
        if self.client:
            try:
                return self.client.ping()
            except Exception as e:
                logger.error(f"Redis ping failed: {e}")
                return False
        return False


# Instance globale pour réutilisation
_redis_wrapper = None

def get_redis_client(host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs) -> RedisClientWrapper:
    """
    Récupère une instance du wrapper Redis
    """
    global _redis_wrapper
    if _redis_wrapper is None:
        _redis_wrapper = RedisClientWrapper(host=host, port=port, db=db, **kwargs)
    return _redis_wrapper


def create_redis_client(host: str = 'localhost', port: int = 6379, db: int = 0, **kwargs) -> Optional[Any]:
    """
    Crée un nouveau client Redis direct (si disponible)
    """
    if REDIS_AVAILABLE:
        try:
            return external_redis.Redis(host=host, port=port, db=db, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None
    return None


# Export des fonctions et classes principales
__all__ = [
    'RedisClientWrapper',
    'get_redis_client', 
    'create_redis_client',
    'REDIS_AVAILABLE',
    'external_redis'
]