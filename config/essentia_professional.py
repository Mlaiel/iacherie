#!/usr/bin/env python3
"""
🎵 Essentia Configuration Professional
=====================================

Configuration professionnelle pour Essentia MusicExtractor.
Installation et configuration des modèles manquants.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
import sys
import logging
from pathlib import Path

def setup_essentia_models():
    """Configuration professionnelle des modèles Essentia"""
    
    try:
        import essentia
        from essentia.standard import MusicExtractor
        
        # Configuration des chemins de modèles
        models_path = Path.home() / '.essentia' / 'models'
        models_path.mkdir(parents=True, exist_ok=True)
        
        # Configuration des variables d'environnement
        os.environ['ESSENTIA_MODELS_PATH'] = str(models_path)
        
        # Configuration du logger pour éviter les messages indésirables
        essentia_logger = logging.getLogger('essentia')
        essentia_logger.setLevel(logging.WARNING)
        
        # Test de création d'un extracteur avec configuration silencieuse
        try:
            extractor = MusicExtractor()
            return True, "Essentia configuré avec succès"
        except Exception as e:
            return False, f"Erreur configuration MusicExtractor: {e}"
            
    except ImportError:
        return install_essentia()

def install_essentia():
    """Installation professionnelle d'Essentia"""
    try:
        import subprocess
        
        # Installation via pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "essentia-tensorflow", "--upgrade"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return setup_essentia_models()
        else:
            return False, f"Installation Essentia échouée: {result.stderr}"
            
    except Exception as e:
        return False, f"Erreur installation Essentia: {e}"

def create_fallback_music_extractor():
    """Créer un extracteur de musique de fallback"""
    
    class FallbackMusicExtractor:
        """Extracteur de musique de fallback pour développement"""
        
        def __init__(self, *args, **kwargs):
            self.configured = True
            
        def __call__(self, audio_file):
            """Retourne des métadonnées de base"""
            return {
                'metadata': {
                    'audio_properties': {
                        'length': 0.0,
                        'sample_rate': 44100,
                        'bit_rate': 128000
                    }
                },
                'lowlevel': {},
                'rhythm': {},
                'tonal': {}
            }
    
    return FallbackMusicExtractor

# Auto-configuration
success, message = setup_essentia_models()
if not success:
    logging.info(f"Essentia fallback activé: {message}")
    MusicExtractorFallback = create_fallback_music_extractor()

__all__ = ['setup_essentia_models', 'install_essentia', 'create_fallback_music_extractor']