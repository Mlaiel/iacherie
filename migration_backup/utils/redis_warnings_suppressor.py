"""
🚀💯🔥 REDIS WARNINGS SUPPRESSOR - UTILITIES MODULE! 🔥💯🚀

Module pour supprimer les avertissements Redis et améliorer la sortie de log

Author: Claude - Utility Expert  
Created: 2025-09-29 - FIXING MISSING DEPENDENCIES
Status: 🔧 CRITICAL UTILITY FOR CLEAN LOGGING
"""

import logging
import warnings
import os
from typing import Optional

def suppress_redis_warnings():
    """
    Supprime les avertissements Redis non critiques pour améliorer la lisibilité des logs
    """
    try:
        # Suppression des avertissements Redis
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="redis")
        warnings.filterwarnings("ignore", category=FutureWarning, module="redis")
        warnings.filterwarnings("ignore", category=UserWarning, module="redis")
        
        # Configuration du logging Redis
        redis_logger = logging.getLogger('redis')
        redis_logger.setLevel(logging.ERROR)
        
        # Suppression des avertissements de connexion
        redis_connection_logger = logging.getLogger('redis.connection')
        redis_connection_logger.setLevel(logging.ERROR)
        
        logging.info("✅ Redis warnings suppressed successfully")
        
    except Exception as e:
        logging.warning(f"Could not suppress Redis warnings: {e}")

def configure_redis_logging(level: str = "ERROR"):
    """
    Configure le niveau de logging pour Redis
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        numeric_level = getattr(logging, level.upper(), logging.ERROR)
        
        # Configuration du logger Redis principal
        redis_logger = logging.getLogger('redis')
        redis_logger.setLevel(numeric_level)
        
        # Configuration des loggers Redis spécifiques
        loggers = [
            'redis.connection',
            'redis.client',
            'redis.sentinel',
            'redis.cluster'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(numeric_level)
            
        logging.info(f"✅ Redis logging configured to {level} level")
        
    except Exception as e:
        logging.error(f"❌ Failed to configure Redis logging: {e}")

def suppress_all_redis_noise():
    """
    Supprime complètement tous les messages Redis non critiques
    """
    try:
        # Suppression totale des warnings Redis
        suppress_redis_warnings()
        
        # Configuration du logging au niveau ERROR seulement
        configure_redis_logging("ERROR")
        
        # Suppression des variables d'environnement de debug Redis
        debug_vars = [
            'REDIS_DEBUG',
            'REDIS_VERBOSE',
            'REDIS_LOG_LEVEL'
        ]
        
        for var in debug_vars:
            if var in os.environ:
                del os.environ[var]
        
        logging.info("🔇 All Redis noise suppressed - Clean logging enabled!")
        
    except Exception as e:
        logging.warning(f"Partial Redis noise suppression: {e}")

# Auto-suppression à l'import
suppress_redis_warnings()

# Export des fonctions principales
__all__ = [
    'suppress_redis_warnings',
    'configure_redis_logging', 
    'suppress_all_redis_noise'
]

logging.info("🚀💯🔥 REDIS WARNINGS SUPPRESSOR MODULE LOADED - CLEAN LOGGING READY! 🔥💯🚀")