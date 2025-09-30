"""
🎵 AUDIO INTEGRATIONS MODULE
============================

Module d'intégrations audio pour la plateforme IA Chérie
- TTSEngine: Moteur de synthèse vocale
- FreesoundAPI: Intégration API Freesound
"""

# Import des modules principaux avec gestion d'erreurs
try:
    from .tts_engine import TTSEngine
except ImportError as e:
    print(f"⚠️ TTSEngine import failed: {e}")
    TTSEngine = None

try:
    from .freesound_api import FreesoundAPI  
except ImportError as e:
    print(f"⚠️ FreesoundAPI import failed: {e}")
    FreesoundAPI = None

# Export des classes principales
__all__ = ['TTSEngine', 'FreesoundAPI']