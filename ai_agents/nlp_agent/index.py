"""NLP Agent Index Module
=====================

Central index and routing system for NLP Agent components.
Provides unified access to all NLP processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, List, Any, Optional, Union, Type
import logging
from datetime import datetime

# Core components
from .nlp_orchestrator import NLPOrchestrator
from .text_analyzer import TextAnalyzer
from .sentiment_engine import SentimentEngine
from .language_detector import LanguageDetector
from .content_classifier import ContentClassifier
from .semantic_processor import SemanticProcessor
from .intent_recognizer import IntentRecognizer
from .entity_extractor import EntityExtractor
from .topic_modeler import TopicModeler
from .text_fingerprinter import TextFingerprinter
from .embeddings_engine import EmbeddingsEngine

# Configuration
from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class NLPAgentIndex:
    """
    Central index for NLP Agent components providing unified access
    to all natural language processing capabilities.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize NLP Agent Index with configuration"""
        self.config = config or default_config
        self.components: Dict[str, Any] = {}
        self.initialized_components: Dict[str, bool] = {}
        self._setup_component_registry()
    
    def _setup_component_registry(self):
        """Setup registry of available components"""
        self.component_registry = {
            "orchestrator": {
                "class": NLPOrchestrator,
                "description": "Main orchestration engine for coordinating NLP tasks",
                "category": "core",
                "dependencies": []
            },
            "text_analyzer": {
                "class": TextAnalyzer,
                "description": "Core text analysis and preprocessing engine",
                "category": "analysis",
                "dependencies": []
            },
            "sentiment_engine": {
                "class": SentimentEngine,
                "description": "Advanced sentiment and emotion analysis",
                "category": "sentiment",
                "dependencies": ["text_analyzer"]
            },
            "language_detector": {
                "class": LanguageDetector,
                "description": "Multi-language detection and identification",
                "category": "language",
                "dependencies": ["text_analyzer"]
            },
            "content_classifier": {
                "class": ContentClassifier,
                "description": "Content categorization and classification",
                "category": "classification",
                "dependencies": ["text_analyzer", "embeddings_engine"]
            },
            "semantic_processor": {
                "class": SemanticProcessor,
                "description": "Semantic understanding and meaning extraction",
                "category": "semantics",
                "dependencies": ["embeddings_engine"]
            },
            "intent_recognizer": {
                "class": IntentRecognizer,
                "description": "User intent detection and classification",
                "category": "intent",
                "dependencies": ["text_analyzer", "content_classifier"]
            },
            "entity_extractor": {
                "class": EntityExtractor,
                "description": "Named entity recognition and extraction",
                "category": "entities",
                "dependencies": ["text_analyzer"]
            },
            "topic_modeler": {
                "class": TopicModeler,
                "description": "Topic discovery and modeling",
                "category": "topics",
                "dependencies": ["text_analyzer"]
            },
            "text_fingerprinter": {
                "class": TextFingerprinter,
                "description": "Text fingerprinting and similarity detection",
                "category": "fingerprinting",
                "dependencies": ["embeddings_engine"]
            },
            "embeddings_engine": {
                "class": EmbeddingsEngine,
                "description": "Vector embeddings generation and management",
                "category": "embeddings",
                "dependencies": []
            }
        }
    
    def get_component(self, component_name: str) -> Any:
        """Get or create a component instance"""
        if component_name not in self.component_registry:
            raise ValueError(f"Unknown component: {component_name}")
        
        if component_name not in self.components:
            self._initialize_component(component_name)
        
        return self.components[component_name]
    
    def _initialize_component(self, component_name: str):
        """Initialize a specific component"""
        try:
            component_info = self.component_registry[component_name]
            component_class = component_info["class"]
            
            # Initialize dependencies first
            for dependency in component_info["dependencies"]:
                if dependency not in self.components:
                    self._initialize_component(dependency)
            
            # Initialize the component
            self.components[component_name] = component_class(config=self.config)
            self.initialized_components[component_name] = True
            
            logger.info(f"Initialized component: {component_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize component {component_name}: {e}")
            self.initialized_components[component_name] = False
            raise
    
    def initialize_all_components(self):
        """Initialize all available components"""
        for component_name in self.component_registry:
            if component_name not in self.components:
                try:
                    self._initialize_component(component_name)
                except Exception as e:
                    logger.warning(f"Failed to initialize {component_name}: {e}")
    
    def get_component_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all components"""
        status = {}
        for component_name, component_info in self.component_registry.items():
            status[component_name] = {
                "description": component_info["description"],
                "category": component_info["category"],
                "initialized": self.initialized_components.get(component_name, False),
                "instance_available": component_name in self.components,
                "dependencies": component_info["dependencies"]
            }
        return status
    
    def get_components_by_category(self, category: str) -> List[str]:
        """Get list of components by category"""
        return [
            name for name, info in self.component_registry.items()
            if info["category"] == category
        ]
    
    def get_available_categories(self) -> List[str]:
        """Get list of available component categories"""
        return list(set(
            info["category"] for info in self.component_registry.values()
        ))
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "summary": {
                "total_components": len(self.component_registry),
                "initialized_components": len(self.initialized_components),
                "healthy_components": 0,
                "failed_components": 0
            }
        }
        
        for component_name in self.component_registry:
            try:
                if component_name in self.components:
                    # Try to call a basic method if available
                    component = self.components[component_name]
                    if hasattr(component, 'health_check'):
                        component_health = component.health_check()
                    else:
                        component_health = {"status": "healthy", "details": "Component available"}
                    
                    health_status["components"][component_name] = component_health
                    if component_health.get("status") == "healthy":
                        health_status["summary"]["healthy_components"] += 1
                    else:
                        health_status["summary"]["failed_components"] += 1
                        health_status["overall_status"] = "degraded"
                else:
                    health_status["components"][component_name] = {
                        "status": "not_initialized",
                        "details": "Component not initialized"
                    }
                    health_status["summary"]["failed_components"] += 1
                    
            except Exception as e:
                health_status["components"][component_name] = {
                    "status": "error",
                    "details": str(e)
                }
                health_status["summary"]["failed_components"] += 1
                health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    def shutdown(self):
        """Shutdown all components gracefully"""
        for component_name, component in self.components.items():
            try:
                if hasattr(component, 'shutdown'):
                    component.shutdown()
                logger.info(f"Shutdown component: {component_name}")
            except Exception as e:
                logger.error(f"Error shutting down component {component_name}: {e}")
        
        self.components.clear()
        self.initialized_components.clear()

# Convenience functions for quick access
def create_nlp_orchestrator(config: Optional[NLPAgentConfig] = None) -> NLPOrchestrator:
    """Create and return NLP Orchestrator instance"""
    index = NLPAgentIndex(config)
    return index.get_component("orchestrator")

def create_text_analyzer(config: Optional[NLPAgentConfig] = None) -> TextAnalyzer:
    """Create and return Text Analyzer instance"""
    index = NLPAgentIndex(config)
    return index.get_component("text_analyzer")

def create_sentiment_engine(config: Optional[NLPAgentConfig] = None) -> SentimentEngine:
    """Create and return Sentiment Engine instance"""
    index = NLPAgentIndex(config)
    return index.get_component("sentiment_engine")

def create_language_detector(config: Optional[NLPAgentConfig] = None) -> LanguageDetector:
    """Create and return Language Detector instance"""
    index = NLPAgentIndex(config)
    return index.get_component("language_detector")

def create_content_classifier(config: Optional[NLPAgentConfig] = None) -> ContentClassifier:
    """Create and return Content Classifier instance"""
    index = NLPAgentIndex(config)
    return index.get_component("content_classifier")

def get_nlp_capabilities() -> Dict[str, List[str]]:
    """Get overview of all NLP capabilities by category"""
    index = NLPAgentIndex()
    capabilities = {}
    
    for category in index.get_available_categories():
        capabilities[category] = index.get_components_by_category(category)
    
    return capabilities

# Global index instance for singleton pattern
_global_index: Optional[NLPAgentIndex] = None

def get_global_index(config: Optional[NLPAgentConfig] = None) -> NLPAgentIndex:
    """Get or create global NLP Agent index instance"""
    global _global_index
    if _global_index is None:
        _global_index = NLPAgentIndex(config)
    return _global_index

def reset_global_index():
    """Reset global index (useful for testing)"""
    global _global_index
    if _global_index:
        _global_index.shutdown()
    _global_index = None

# Export main functionality
__all__ = [
    "NLPAgentIndex",
    "create_nlp_orchestrator",
    "create_text_analyzer", 
    "create_sentiment_engine",
    "create_language_detector",
    "create_content_classifier",
    "get_nlp_capabilities",
    "get_global_index",
    "reset_global_index"
]
