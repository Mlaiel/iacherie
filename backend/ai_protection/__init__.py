"""AI Protection Rights Module

This module provides comprehensive AI-powered content protection and rights management
functionality including watermarking, blockchain registry, copyright detection,
NFT generation, and digital rights management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from .watermark_engine import WatermarkEngine
from .blockchain_registry import BlockchainRightsRegistry
from .copyright_detector import CopyrightDetector
from .nft_generator import NFTGenerator
from .rights_manager import DigitalRightsManager

__all__ = [
    'WatermarkEngine',
    'BlockchainRightsRegistry', 
    'CopyrightDetector',
    'NFTGenerator',
    'DigitalRightsManager'
]

__version__ = "1.0.0"