"""
Fingerprinting - IA Chéries Integrations
====================================
Point d'entrée principal pour protection des droits numériques.
Orchestration fingerprinting, watermarking et DMCA automation.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Integrations  
Version: 1.0 Production
"""

# Phase 1: Multi-Modal Fingerprinting - COMPLETED
from .audio_fingerprinting import AudioFingerprinting
from .video_fingerprinting import VideoFingerprinting
from .image_fingerprinting import ImageFingerprinting
from .text_fingerprinting import TextFingerprinting
from .blockchain_fingerprinting import BlockchainFingerprinting

# Phase 2: Advanced Protection Systems - TO BE IMPLEMENTED
# from .watermarking_engine import WatermarkingEngine
# from .plagiarism_detection import PlagiarismDetection
# from .dmca_automation import DMCAAutomation
# from .rights_management import RightsManagement

# Configuration logique métier IA Chéries
FINGERPRINTING_CONFIG = {
    'supported_formats': {
        'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
        'video': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        'image': ['jpg', 'png', 'tiff', 'bmp', 'webp'],
        'text': ['txt', 'md', 'doc', 'pdf', 'html']
    },
    'fingerprint_algorithms': ['chromaprint', 'perceptual_hash', 'dhash', 'ahash'],
    'watermark_types': ['visible', 'invisible', 'blockchain', 'steganographic'],
    'detection_sensitivity': ['low', 'medium', 'high', 'ultra'],
    'blockchain_networks': ['ethereum', 'polygon', 'bsc', 'solana'],
    'legal_jurisdictions': ['us', 'eu', 'uk', 'ca', 'au', 'global'],
    'dmca_providers': ['google', 'youtube', 'instagram', 'tiktok', 'spotify']
}

def get_rights_protection_manager():
    """Factory pour créer le gestionnaire principal de protection."""
    return {
        # Phase 1: Multi-Modal Fingerprinting - COMPLETED
        'audio': AudioFingerprinting(),
        'video': VideoFingerprinting(),
        'image': ImageFingerprinting(),
        'text': TextFingerprinting(),
        'blockchain': BlockchainFingerprinting(),
        
        # Phase 2: Advanced Protection Systems - TO BE IMPLEMENTED
        # 'watermarking': WatermarkingEngine(),
        # 'plagiarism': PlagiarismDetection(),
        # 'dmca': DMCAAutomation(),
        # 'rights': RightsManagement()
    }