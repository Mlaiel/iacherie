"""NLP Module Tests Package for IA Influencer Agent Platform

Comprehensive test suite for Natural Language Processing components
covering all modules with industrial-grade testing standards.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de

Team Expertise:
✅ Lead Dev + Architecte Développeur IA - Fahed Mlaiel
✅ Développeur Backend Senior (Python/FastAPI/Django) - Fahed Mlaiel  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face) - Fahed Mlaiel
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB) - Fahed Mlaiel
✅ Spécialiste Sécurité Backend - Fahed Mlaiel
✅ Architecte Microservices - Fahed Mlaiel
✅ Développeur Audio - Fahed Mlaiel
✅ DevOps Engineer - Fahed Mlaiel
✅ IA Prompt Engineer - Fahed Mlaiel
"""__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Test configuration
TEST_CONFIG = {
    'async_timeout': 30.0,
    'batch_size': 10,
    'max_test_iterations': 1000,
    'memory_limit_mb': 1024,
    'performance_threshold_ms': 100,
    'accuracy_threshold': 0.85,
    'coverage_threshold': 95.0
}

# Test data directory
TEST_DATA_DIR = "/workspaces/Ainflue/tests_backend/ai/nlp/test_data"

# Shared test utilities
from .conftest import *

# Import test classes
from .test_analysis import TextAnalysisTests, AdvancedTextAnalysisTests

# Create additional test classes
class SentimentAnalysisTests(TextAnalysisTests):
    """Specialized tests for sentiment analysis"""
    pass

class ContentGenerationTests(TextAnalysisTests):
    """Specialized tests for content generation"""
    pass

class LanguageDetectionTests(TextAnalysisTests):
    """Specialized tests for language detection"""
    pass

class TranslationTests(TextAnalysisTests):
    """Specialized tests for translation"""
    pass

# Export test classes
__all__ = [
    'TextAnalysisTests',
    'AdvancedTextAnalysisTests',
    'SentimentAnalysisTests',
    'ContentGenerationTests',
    'LanguageDetectionTests',
    'TranslationTests',
    'TEST_CONFIG',
    'TEST_DATA_DIR'
]
