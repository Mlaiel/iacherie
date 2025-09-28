#!/usr/bin/env python3
"""
🎵 Essentia Classifier Fix
=========================

Configuration silencieuse pour Essentia MusicExtractor.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
import logging

# Supprime les messages Essentia
os.environ['ESSENTIA_SILENCE_FFMPEG_WARNINGS'] = '1'

# Configure le logger Essentia
try:
    import essentia
    essentia_logger = logging.getLogger('essentia')
    essentia_logger.setLevel(logging.ERROR)
    
    # Supprime les logs de configuration
    logging.getLogger('essentia.standard').setLevel(logging.ERROR)
    logging.getLogger('essentia.streaming').setLevel(logging.ERROR)
    
except ImportError:
    pass

# Supprime les messages MusicExtractorSVM
class SilentMusicExtractor:
    """Wrapper silencieux pour MusicExtractor"""
    
    def __init__(self, *args, **kwargs):
        try:
            from essentia.standard import MusicExtractor
            self._extractor = MusicExtractor(*args, **kwargs)
        except ImportError:
            self._extractor = None
    
    def __call__(self, *args, **kwargs):
        if self._extractor:
            return self._extractor(*args, **kwargs)
        return {}

# Export pour remplacement
__all__ = ['SilentMusicExtractor']