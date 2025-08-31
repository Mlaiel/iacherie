"""NLP Agent Module - Advanced Natural Language Processing System
=============================================================

Complete NLP agent system for advanced text processing, analysis, and understanding.
Provides comprehensive natural language processing capabilities for content analysis,
sentiment detection, entity recognition, and semantic understanding.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Features:
- Advanced text analysis and preprocessing
- Multi-language sentiment and emotion analysis
- Named entity recognition and extraction
- Language detection (100+ languages supported)
- Content classification and categorization
- Semantic processing and understanding
- Intent recognition and purpose analysis
- Topic modeling and theme discovery
- Text fingerprinting for content protection
- High-quality embeddings generation
- Async processing for high performance
- Configurable fallback methods
- Industrial-grade error handling

Team Specialties:
- Fahed Mlaiel: AI Architecture, NLP Systems, Content Protection
- AI Research Team: Advanced Language Models, Semantic Understanding
- Protection Team: Content Security, Plagiarism Detection
- Engineering Team: Performance Optimization, Scalable Infrastructure
"""
import logging
from typing import Dict, List, Any, Optional, Union

# Import configuration
from .config import NLPAgentConfig, default_config

# Import core components
from .nlp_orchestrator import NLPOrchestrator, ProcessingRequest, ProcessingResult
from .text_analyzer import TextAnalyzer, TextAnalysisResult
from .sentiment_engine import SentimentEngine, SentimentResult
from .language_detector import LanguageDetector, LanguageResult
from .content_classifier import ContentClassifier, ClassificationResult
from .semantic_processor import SemanticProcessor, SemanticResult
from .intent_recognizer import IntentRecognizer, IntentResult
from .entity_extractor import EntityExtractor, ExtractionResult
from .topic_modeler import TopicModeler, TopicModelResult
from .text_fingerprinter import TextFingerprinter, FingerprintingResult
from .embeddings_engine import EmbeddingsEngine, TextEmbedding

# Setup logging
logger = logging.getLogger(__name__)

# Module version and information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced NLP Agent System for Content Processing and Protection"

# Export main classes and functions
__all__ = [
    # Configuration
    'NLPAgentConfig',
    'default_config',
    
    # Core orchestration
    'NLPOrchestrator',
    'ProcessingRequest',
    'ProcessingResult',
    
    # Text analysis
    'TextAnalyzer',
    'TextAnalysisResult',
    
    # Sentiment analysis
    'SentimentEngine',
    'SentimentResult',
    
    # Language detection
    'LanguageDetector',
    'LanguageResult',
    
    # Content classification
    'ContentClassifier',
    'ClassificationResult',
    
    # Semantic processing
    'SemanticProcessor',
    'SemanticResult',
    
    # Intent recognition
    'IntentRecognizer',
    'IntentResult',
    
    # Entity extraction
    'EntityExtractor',
    'ExtractionResult',
    
    # Topic modeling
    'TopicModeler',
    'TopicModelResult',
    
    # Text fingerprinting
    'TextFingerprinter',
    'FingerprintingResult',
    
    # Embeddings
    'EmbeddingsEngine',
    'TextEmbedding',
    
    # Factory functions
    'create_nlp_agent',
    'create_text_analyzer',
    'create_sentiment_engine',
    'create_language_detector',
    'create_content_classifier',
    'create_semantic_processor',
    'create_intent_recognizer',
    'create_entity_extractor',
    'create_topic_modeler',
    'create_text_fingerprinter',
    'create_embeddings_engine',
    
    # Utility functions
    'get_supported_languages',
    'get_available_models',
    'validate_text_input',
]

def create_nlp_agent(config: Optional[NLPAgentConfig] = None) -> NLPOrchestrator:
    """    Create a complete NLP agent with all capabilities
    
    Args:
        config: Optional configuration for the NLP agent
    
    Returns:
        Configured NLPOrchestrator instance
    """    return NLPOrchestrator(config)

def create_text_analyzer(config: Optional[NLPAgentConfig] = None) -> TextAnalyzer:
    """Create a text analyzer instance"""    return TextAnalyzer(config)

def create_sentiment_engine(config: Optional[NLPAgentConfig] = None) -> SentimentEngine:
    """Create a sentiment analysis engine"""    return SentimentEngine(config)

def create_language_detector(config: Optional[NLPAgentConfig] = None) -> LanguageDetector:
    """Create a language detection engine"""    return LanguageDetector(config)

def create_content_classifier(config: Optional[NLPAgentConfig] = None) -> ContentClassifier:
    """Create a content classification engine"""    return ContentClassifier(config)

def create_semantic_processor(config: Optional[NLPAgentConfig] = None) -> SemanticProcessor:
    """Create a semantic processing engine"""    return SemanticProcessor(config)

def create_intent_recognizer(config: Optional[NLPAgentConfig] = None) -> IntentRecognizer:
    """Create an intent recognition engine"""    return IntentRecognizer(config)

def create_entity_extractor(config: Optional[NLPAgentConfig] = None) -> EntityExtractor:
    """Create an entity extraction engine"""    return EntityExtractor(config)

def create_topic_modeler(config: Optional[NLPAgentConfig] = None) -> TopicModeler:
    """Create a topic modeling engine"""    return TopicModeler(config)

def create_text_fingerprinter(config: Optional[NLPAgentConfig] = None) -> TextFingerprinter:
    """Create a text fingerprinting engine"""    return TextFingerprinter(config)

def create_embeddings_engine(config: Optional[NLPAgentConfig] = None) -> EmbeddingsEngine:
    """Create an embeddings engine"""    return EmbeddingsEngine(config)

def get_supported_languages() -> List[str]:
    """Get list of supported languages for analysis"""    # This would typically return languages supported by the models
    return [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
        'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'cs'
    ]

def get_available_models() -> Dict[str, List[str]]:
    """Get available models for different NLP tasks"""    return {
        'sentiment': [
            'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'nlptown/bert-base-multilingual-uncased-sentiment',
            'j-hartmann/emotion-english-distilroberta-base'
        ],
        'language_detection': [
            'papluca/xlm-roberta-base-language-detection',
            'microsoft/DialoGPT-medium'
        ],
        'classification': [
            'facebook/bart-large-mnli',
            'microsoft/DialoGPT-medium'
        ],
        'embeddings': [
            'sentence-transformers/all-MiniLM-L6-v2',
            'sentence-transformers/all-mpnet-base-v2'
        ],
        'entity_extraction': [
            'dbmdz/bert-large-cased-finetuned-conll03-english',
            'Jean-Baptiste/roberta-large-ner-english'
        ],
        'topic_modeling': [
            'sentence-transformers/all-MiniLM-L6-v2',
            'microsoft/DialoGPT-medium'
        ]
    }

def validate_text_input(text: Union[str, List[str]]) -> bool:
    """    Validate text input for processing
    
    Args:
        text: Text or list of texts to validate
    
    Returns:
        True if valid, False otherwise
    """    if isinstance(text, str):
        return len(text.strip()) > 0
    
    elif isinstance(text, list):
        return all(isinstance(t, str) and len(t.strip()) > 0 for t in text)
    
    return False

# Initialize module
logger.info(f"NLP Agent module v{__version__} initialized")
logger.info(f"Author: {__author__} ({__email__})")
logger.info(f"Description: {__description__}")

# Health check function for module
def module_health_check() -> Dict[str, Any]:
    """Perform health check for entire NLP module"""    try:
        orchestrator = create_nlp_agent()
        health_status = orchestrator.health_check()
        
        return {
            "module": "nlp_agent",
            "version": __version__,
            "status": "healthy",
            "orchestrator_status": health_status,
            "supported_languages": len(get_supported_languages()),
            "available_models": sum(len(models) for models in get_available_models().values())
        }
    
    except Exception as e:
        logger.error(f"NLP module health check failed: {e}")
        return {
            "module": "nlp_agent",
            "version": __version__,
            "status": "degraded",
            "error": str(e)
        }

from .nlp_orchestrator import NLPOrchestrator
from .text_analyzer import TextAnalyzer
from .sentiment_engine import SentimentEngine
from .language_detector import LanguageDetector
from .content_classifier import ContentClassifier

__all__ = [
    "NLPOrchestrator",
    "TextAnalyzer",
    "SentimentEngine",
    "LanguageDetector",
    "ContentClassifier"
]

def create_nlp_agent():
    """Factory function to create configured NLP agent"""    return NLPOrchestrator()
