"""
Gestionnaire singleton pour sentence-transformers
Évite les conflits TensorFlow avec la librairie sentence-transformers
"""

import threading
import logging
import warnings
from typing import Optional, Any

logger = logging.getLogger(__name__)

class SentenceTransformersManager:
    """
Gestionnaire singleton thread-safe pour sentence-transformers"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _sentence_transformers_module = None
    _sentence_transformer_class = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_sentence_transformers(self):
        """
Initialise sentence-transformers de manière sécurisée"""
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            try:
                # S'assurer que TensorFlow est initialisé en premier via notre singleton
                from .tensorflow_singleton import get_tensorflow
                tf = get_tensorflow()
                if tf:
                    logger.info("TensorFlow singleton OK avant import sentence-transformers")
                
                # S'assurer que transformers est initialisé en premier via notre singleton
                from .transformers_singleton import get_transformers
                transformers = get_transformers()
                if transformers:
                    logger.info("Transformers singleton OK avant import sentence-transformers")
                
                # Configurer les variables d'environnement pour sentence-transformers
                import os
                os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', '/tmp/.sentence_transformers')
                
                # Supprimer les warnings sentence-transformers
                warnings.filterwarnings('ignore', category=UserWarning, module='sentence_transformers')
                warnings.filterwarnings('ignore', message='.*sentence.*transformers.*')
                
                # Import protégé de sentence-transformers
                try:
                    import sentence_transformers
                    from sentence_transformers import SentenceTransformer
                    
                    self._sentence_transformers_module = sentence_transformers
                    self._sentence_transformer_class = SentenceTransformer
                    
                    logger.info("✅ Sentence-transformers initialisé avec succès via singleton")
                    
                except Exception as e:
                    logger.debug(f"Sentence-transformers non disponible: {e}")
                    # Module non disponible - ne pas créer de mocks
                    self._sentence_transformers_module = None
                    self._sentence_transformer_class = None
                    
                self._initialized = True
                
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation sentence-transformers: {e}")
                self._initialized = True  # Éviter les boucles infinies
    
    def get_sentence_transformers(self):
        """
Récupère le module sentence_transformers principal"""
        if not self._initialized:
            self._initialize_sentence_transformers()
        return self._sentence_transformers_module
    
    def get_sentence_transformer(self):
        """
Récupère la classe SentenceTransformer"""
        if not self._initialized:
            self._initialize_sentence_transformers()
        return self._sentence_transformer_class

# Instance globale du gestionnaire
_manager = SentenceTransformersManager()

def get_sentence_transformers():
    """
Fonction de convenance pour obtenir sentence_transformers"""
    return _manager.get_sentence_transformers()

def get_sentence_transformer():
    """
Fonction de convenance pour obtenir SentenceTransformer"""
    return _manager.get_sentence_transformer()

def is_sentence_transformers_available() -> bool:
    """
Vérifie si sentence-transformers est disponible"""
    sentence_transformers_module = get_sentence_transformers()
    return sentence_transformers_module is not None

# Initialisation lors de l'import du module
if not _manager._initialized:
    _manager._initialize_sentence_transformers()