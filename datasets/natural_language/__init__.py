#!/usr/bin/env python3
"""
🗣️ NATURAL LANGUAGE DATASETS - ENTERPRISE AI TRAINING ARCHITECTURE
==================================================================

**Module:** datasets/natural_language/__init__.py
**Author:** Fahed Mlaiel (mlaiel@live.de)
**Copyright:** © 2025 Fahed Mlaiel - Tous Droits Réservés
**Date:** September 2025
**Version:** 1.0.0 - Production Ready

MISSION ENTERPRISE:
Datasets spécialisés NLP pour agents IA de la plateforme Ainflue.
Support 15+ agents language avec datasets multilingues haute qualité.
"""

from typing import Dict, List, Optional, Any

# Core NLP datasets
from .index import NaturalLanguageDatasets

# Export public API
__all__ = [
    'NaturalLanguageDatasets'
]

# NLP Constants
SUPPORTED_LANGUAGES = ['en', 'fr', 'de', 'es', 'it', 'pt', 'ar', 'zh', 'ja', 'ko', 'ru']
MAX_SEQUENCE_LENGTH = 512
DEFAULT_VOCABULARY_SIZE = 50000
QUALITY_THRESHOLD = 0.95

def get_natural_language_info() -> Dict[str, Any]:
    """Informations module natural language"""
    return {
        "module_name": "Natural Language Datasets",
        "supported_languages": SUPPORTED_LANGUAGES,
        "quality_threshold": QUALITY_THRESHOLD,
        "max_sequence_length": MAX_SEQUENCE_LENGTH,
        "specialized_datasets": 16,
        "enterprise_ready": True,
        "ai_agents_supported": 15
    }