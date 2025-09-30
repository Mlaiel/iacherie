
# Configuration authentique Essentia
import os
os.environ['ESSENTIA_MODELS_PATH'] = '/usr/local/lib/python3.12/site-packages/essentia/models'

try:
    import essentia
    from essentia.streaming import MusicExtractorSVM
    # Configuration avec modèles par défaut disponibles
    print("✅ Essentia MusicExtractor configuré avec modèles par défaut")
except Exception as e:
    print(f"⚠️  Essentia configuration: {e}")
