#!/usr/bin/env python3
"""
🎵 AUDIO PROCESSING DATASETS - ENTERPRISE AI TRAINING ARCHITECTURE
=================================================================

**Module:** datasets/audio_processing/__init__.py
**Author:** Fahed Mlaiel (mlaiel@live.de)
**Copyright:** © 2025 Fahed Mlaiel - Tous Droits Réservés
**Date:** September 2025
**Version:** 1.0.0 - Production Ready

MISSION ENTERPRISE:
Datasets spécialisés audio pour agents IA de la plateforme IA Chéries.
Support 13+ agents audio avec datasets haute qualité pour speech, music,
fingerprinting, enhancement, et generation.
"""

from typing import Dict, List, Optional, Any

# Core audio datasets
from .index import AudioProcessingDatasets

# Export public API
__all__ = [
    'AudioProcessingDatasets'
]

# Audio Constants
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
SAMPLE_RATES = [16000, 22050, 44100, 48000]
DEFAULT_SAMPLE_RATE = 22050
MAX_AUDIO_LENGTH = 600  # seconds
QUALITY_THRESHOLD = 0.95

def get_audio_processing_info() -> Dict[str, Any]:
    """Informations module audio processing"""
    return {
        "module_name": "Audio Processing Datasets",
        "supported_formats": SUPPORTED_AUDIO_FORMATS,
        "sample_rates": SAMPLE_RATES,
        "quality_threshold": QUALITY_THRESHOLD,
        "specialized_datasets": 18,
        "enterprise_ready": True,
        "ai_agents_supported": 13
    }