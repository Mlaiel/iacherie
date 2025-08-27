"""
Text Agent Module - Industrial Text Processing & NLP System

Advanced AI-powered text processing, analysis, and generation system for content creators.
Handles text fingerprinting, sentiment analysis, language processing, and AI-powered content generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

# Core Components
from .text_agent import (
    TextAgent, 
    TextAgentManager, 
    TextProcessingType, 
    TextQuality,
    TextProcessingConfig,
    TextAnalysisResult
)

from .text_processor import (
    TextProcessor, 
    TextAnalyzer, 
    ProcessingOptions,
    ProcessingLevel,
    TextFormat,
    ProcessingResult
)

from .text_generator import (
    AITextGenerator, 
    ContentSynthesizer,
    GenerationConfig,
    GenerationType,
    WritingStyle,
    ContentFormat,
    GenerationResult
)

from .nlp_engine import (
    NLPEngine, 
    SentimentAnalyzer,
    AnalysisType,
    SentimentPolarity,
    EmotionType,
    SentimentResult,
    EntityResult,
    TopicResult,
    SemanticResult
)

from .language_detector import (
    LanguageDetector, 
    TranslationEngine,
    LanguageConfidence,
    TranslationQuality,
    LanguageDetectionResult,
    TranslationResult
)

# Unified System
from .index import (
    TextAgentSystem,
    analyze_text,
    generate_content,
    translate_text,
    detect_plagiarism,
    get_text_system
)

__version__ = "1.0.0"

__all__ = [
    # Core Agents
    'TextAgent',
    'TextAgentManager',
    
    # Processing Components
    'TextProcessor',
    'TextAnalyzer',
    'AITextGenerator', 
    'ContentSynthesizer',
    'NLPEngine',
    'SentimentAnalyzer',
    'LanguageDetector',
    'TranslationEngine',
    
    # Unified System
    'TextAgentSystem',
    
    # Configuration Classes
    'TextProcessingConfig',
    'ProcessingOptions',
    'GenerationConfig',
    
    # Result Classes
    'TextAnalysisResult',
    'ProcessingResult',
    'GenerationResult',
    'SentimentResult',
    'EntityResult',
    'TopicResult',
    'SemanticResult',
    'LanguageDetectionResult',
    'TranslationResult',
    
    # Enums
    'TextProcessingType',
    'TextQuality',
    'ProcessingLevel',
    'TextFormat',
    'GenerationType',
    'WritingStyle',
    'ContentFormat',
    'AnalysisType',
    'SentimentPolarity',
    'EmotionType',
    'LanguageConfidence',
    'TranslationQuality',
    
    # Convenience Functions
    'analyze_text',
    'generate_content',
    'translate_text',
    'detect_plagiarism',
    'get_text_system'
]

# Module metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel"

# Legal Notice
__legal_notice__ = """
⚠️  CRITICAL LEGAL WARNING:
This module and all its components are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited and illegal.
All violators will face prosecution under German and international copyright law.
For licensing inquiries, contact: mlaiel@live.de
"""
