#!/usr/bin/env python3
"""
🔧 LangDetect Error Fix
======================

Correction du problème d'import LangDetectError.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

# Correction de l'import LangDetectError
try:
    from langdetect import detect, LangDetectException as LangDetectError
    from langdetect.lang_detect_exception import LangDetectException
    
    # Export pour compatibilité
    __all__ = ['detect', 'LangDetectError', 'LangDetectException']
    
except ImportError:
    # Fallback si langdetect non disponible
    def detect(text):
        return 'en'  # Défaut anglais
    
    class LangDetectError(Exception):
        pass
    
    LangDetectException = LangDetectError
    
    __all__ = ['detect', 'LangDetectError', 'LangDetectException']