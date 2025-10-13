#!/usr/bin/env python3
"""
Gestionnaire TensorFlow Singleton - Solution Solide
===================================================
Auteur: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. Tous droits réservés.

Gestionnaire singleton pour éviter les conflits d'initialisation TensorFlow
sans désactiver les fonctionnalités IA.
"""

import threading
import os
import logging

logger = logging.getLogger(__name__)

class TensorFlowManager:
    """
Gestionnaire singleton pour TensorFlow avec initialisation sécurisée."""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _tf = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TensorFlowManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_tensorflow()
    
    def _initialize_tensorflow(self):
        """
Initialisation sécurisée de TensorFlow une seule fois."""
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            try:
                # Vérifier si TensorFlow est déjà chargé
                import sys
                if 'tensorflow' in sys.modules:
                    logger.info("TensorFlow déjà chargé dans sys.modules, utilisation de l'instance existante")
                    self._tf = sys.modules['tensorflow']
                    self._initialized = True
                    return
                
                # Configuration environnement AVANT import
                os.environ.update({
                    'TF_CPP_MIN_LOG_LEVEL': '2',
                    'TF_ENABLE_ONEDNN_OPTS': '0',
                    'TF_FORCE_GPU_ALLOW_GROWTH': 'true'
                })
                
                # Import TensorFlow de manière sécurisée
                import tensorflow as tf
                
                # Configuration GPU si disponible
                gpus = tf.config.experimental.list_physical_devices('GPU')
                if gpus:
                    try:
                        for gpu in gpus:
                            tf.config.experimental.set_memory_growth(gpu, True)
                    except RuntimeError as e:
                        logger.warning(f"GPU configuration: {e}")
                
                self._tf = tf
                self._initialized = True
                logger.info("✅ TensorFlow initialisé correctement avec singleton")
                
            except Exception as e:
                logger.error(f"❌ Erreur initialisation TensorFlow: {e}")
                # Fallback gracieux sans crash
                self._tf = None
                self._initialized = True
    
    @property
    def tf(self):
        """
Accès sécurisé à TensorFlow."""
        if not self._initialized:
            self._initialize_tensorflow()
        return self._tf
    
    @property
    def is_available(self):
        """
Vérifie si TensorFlow est disponible."""
        return self._tf is not None

# Instance globale du gestionnaire
_tf_manager = TensorFlowManager()

def get_tensorflow():
    """
Obtient l'instance TensorFlow de manière sécurisée."""
    return _tf_manager.tf

def is_tensorflow_available():
    """
Vérifie si TensorFlow est disponible."""
    return _tf_manager.is_available

# Export des fonctions principales
__all__ = ['get_tensorflow', 'is_tensorflow_available', 'TensorFlowManager']