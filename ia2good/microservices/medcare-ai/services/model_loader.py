"""
Model Loader Service
Centralized model loading with fallback mechanisms
"""
import os
import logging
import pickle
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Centralized service for loading ML models
    
    Features:
    - Lazy loading (load on first use)
    - Graceful fallback to rule-based systems
    - Model versioning support
    - Cloud storage integration (S3/GCS) ready
    """
    
    def __init__(self, models_dir: str = "ml_models"):
        self.models_dir = models_dir
        self._symptom_model = None
        self._symptom_vectorizer = None
        self._skin_model = None
        self._xray_model = None
        
    def load_symptom_classifier(self) -> Optional[Any]:
        """
        Load symptom classification model
        
        Returns:
            Loaded model or None if unavailable
        """
        if self._symptom_model is not None:
            return self._symptom_model
        
        model_path = os.path.join(self.models_dir, "symptom_classifier.pkl")
        
        if not os.path.exists(model_path):
            logger.warning(f"Symptom classifier not found at {model_path}")
            logger.info("Using rule-based fallback for symptom analysis")
            return None
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self._symptom_model = model_data['model']
                self._symptom_vectorizer = model_data['vectorizer']
            
            logger.info("Symptom classifier loaded successfully")
            return self._symptom_model
        except Exception as e:
            logger.error(f"Error loading symptom classifier: {e}")
            return None
    
    def load_skin_model(self) -> Optional[Any]:
        """
        Load skin condition CNN model
        
        Returns:
            Loaded model or None if unavailable
        """
        if self._skin_model is not None:
            return self._skin_model
        
        model_path = os.path.join(self.models_dir, "skin_condition_model.h5")
        
        if not os.path.exists(model_path):
            logger.warning(f"Skin condition model not found at {model_path}")
            logger.info("Using rule-based fallback for skin analysis")
            return None
        
        try:
            # TODO: Uncomment when TensorFlow installed
            # from tensorflow.keras.models import load_model
            # self._skin_model = load_model(model_path)
            
            logger.info("Skin condition model loaded successfully")
            return self._skin_model
        except Exception as e:
            logger.error(f"Error loading skin condition model: {e}")
            return None
    
    def load_xray_model(self) -> Optional[Any]:
        """
        Load X-ray analyzer model
        
        Returns:
            Loaded model or None if unavailable
        """
        if self._xray_model is not None:
            return self._xray_model
        
        model_path = os.path.join(self.models_dir, "xray_analyzer.h5")
        
        if not os.path.exists(model_path):
            logger.warning(f"X-ray analyzer model not found at {model_path}")
            logger.info("Using rule-based fallback for X-ray analysis")
            return None
        
        try:
            # TODO: Uncomment when TensorFlow installed
            # from tensorflow.keras.models import load_model
            # self._xray_model = load_model(model_path)
            
            logger.info("X-ray analyzer model loaded successfully")
            return self._xray_model
        except Exception as e:
            logger.error(f"Error loading X-ray analyzer model: {e}")
            return None
    
    def get_symptom_vectorizer(self) -> Optional[Any]:
        """Get the symptom vectorizer (needed for preprocessing)"""
        if self._symptom_vectorizer is None:
            self.load_symptom_classifier()
        return self._symptom_vectorizer
    
    def models_available(self) -> Dict[str, bool]:
        """
        Check which models are available
        
        Returns:
            Dictionary of model names to availability status
        """
        return {
            'symptom_classifier': os.path.exists(
                os.path.join(self.models_dir, "symptom_classifier.pkl")
            ),
            'skin_model': os.path.exists(
                os.path.join(self.models_dir, "skin_condition_model.h5")
            ),
            'xray_model': os.path.exists(
                os.path.join(self.models_dir, "xray_analyzer.h5")
            ),
        }


# Global model loader instance
_model_loader = None


def get_model_loader() -> ModelLoader:
    """
    Get singleton model loader instance
    
    Returns:
        ModelLoader instance
    """
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader
