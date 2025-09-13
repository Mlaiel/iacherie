"""
Fingerprinting Module - Ainflue Integrations
===========================================
Module de protection des droits numériques enterprise avec
fingerprinting multi-format, watermarking et automation DMCA.

Support pour:
- Fingerprinting audio, vidéo, image, texte
- Watermarking intelligent et blockchain
- Détection plagiat et infringement
- Automation DMCA et legal compliance
- Protection droits globale multi-juridictions

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

from .audio_fingerprinting import AudioFingerprinting
from .video_fingerprinting import VideoFingerprinting
from .image_fingerprinting import ImageFingerprinting
from .text_fingerprinting import TextFingerprinting
from .blockchain_fingerprinting import BlockchainFingerprinting
from .watermarking_engine import WatermarkingEngine
from .plagiarism_detection import PlagiarismDetection
from .dmca_automation import DMCAAutomation
from .rights_management import RightsManagement

__all__ = [
    'AudioFingerprinting',
    'VideoFingerprinting', 
    'ImageFingerprinting',
    'TextFingerprinting',
    'BlockchainFingerprinting',
    'WatermarkingEngine',
    'PlagiarismDetection',
    'DMCAAutomation',
    'RightsManagement'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Digital Rights Protection enterprise - Fingerprinting et DMCA automation"