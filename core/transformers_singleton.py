"""
Gestionnaire singleton pour les imports transformers
Évite les conflits TensorFlow avec la librairie transformers
"""

import threading
import logging
import warnings
import sys
from typing import Optional, Any

logger = logging.getLogger(__name__)

class TransformersManager:
    """
Gestionnaire singleton thread-safe pour transformers"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _transformers_modules = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def _initialize_transformers(self):
        """
Initialise transformers de manière sécurisée"""
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
                    logger.info("TensorFlow singleton OK avant # import transformers")
                
                # Configurer les variables d'environnement pour transformers
                import os
                os.environ.setdefault('TRANSFORMERS_OFFLINE', '0')
                os.environ.setdefault('TRANSFORMERS_NO_ADVISORY_WARNINGS', '1')
                
                # Supprimer les warnings transformers/tensorflow
                warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
                warnings.filterwarnings('ignore', message='.*tensorflow.*')
                
                # Import protégé des modules transformers principaux
                try:
                    import transformers
                    self._transformers_modules['transformers'] = transformers
                    
                    # Import des classes principales
                    from transformers import (
                        AutoTokenizer, AutoModel, pipeline,
                        AutoModelForSequenceClassification,
                        AutoModelForTokenClassification,
                        AutoConfig, AutoProcessor
                    )
                    
                    self._transformers_modules.update({
                        'AutoTokenizer': AutoTokenizer,
                        'AutoModel': AutoModel,
                        'pipeline': pipeline,
                        'AutoModelForSequenceClassification': AutoModelForSequenceClassification,
                        'AutoModelForTokenClassification': AutoModelForTokenClassification,
                        'AutoConfig': AutoConfig,
                        'AutoProcessor': AutoProcessor
                    })
                    
                    logger.info("✅ Transformers initialisé avec succès via singleton")
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'# import transformers: {e}")
                    # Créer des mocks pour éviter les erreurs
                    self._transformers_modules = {
                        'transformers': None,
                        'AutoTokenizer': None,
                        'AutoModel': None,
                        'pipeline': None,
                        'AutoModelForSequenceClassification': None,
                        'AutoModelForTokenClassification': None,
                        'AutoConfig': None,
                        'AutoProcessor': None
                    }
                    
                self._initialized = True
                
            except Exception as e:
                logger.error(f"Erreur fatale lors de l'initialisation transformers: {e}")
                self._initialized = True  # Éviter les boucles infinies
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """
Récupère un module transformers spécifique"""
        if not self._initialized:
            self._initialize_transformers()
        return self._transformers_modules.get(module_name)
    
    def get_transformers(self):
        """
Récupère le module transformers principal"""
        return self.get_module('transformers')
    
    def get_pipeline(self):
        """
Récupère la fonction pipeline"""
        return self.get_module('pipeline')
    
    def get_auto_tokenizer(self):
        """
Récupère AutoTokenizer"""
        return self.get_module('AutoTokenizer')
    
    def get_auto_model(self):
        """
Récupère AutoModel"""
        return self.get_module('AutoModel')
    
    def get_auto_model_for_sequence_classification(self):
        """
Récupère AutoModelForSequenceClassification"""
        return self.get_module('AutoModelForSequenceClassification')
    
    def get_auto_config(self):
        """
Récupère AutoConfig"""
        return self.get_module('AutoConfig')

# Instance globale du gestionnaire
_manager = TransformersManager()

def get_transformers():
    """
Fonction de convenance pour obtenir transformers"""
    return _manager.get_transformers()

def get_pipeline():
    """
Fonction de convenance pour obtenir pipeline"""
    return _manager.get_pipeline()

def get_auto_tokenizer():
    """
Fonction de convenance pour obtenir AutoTokenizer"""
    return _manager.get_auto_tokenizer()

def get_auto_model():
    """
Fonction de convenance pour obtenir AutoModel"""
    return _manager.get_auto_model()

def get_auto_model_for_sequence_classification():
    """
Fonction de convenance pour obtenir AutoModelForSequenceClassification"""
    return _manager.get_auto_model_for_sequence_classification()

def get_auto_config():
    """
Fonction de convenance pour obtenir AutoConfig"""
    return _manager.get_auto_config()

def is_transformers_available() -> bool:
    """
Vérifie si transformers est disponible"""
    transformers_module = get_transformers()
    return transformers_module is not None

# Initialisation lors de l'import du module
if not _manager._initialized:
    _manager._initialize_transformers()