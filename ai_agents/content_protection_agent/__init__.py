"""Content Protection Agent - Multi-Platform Content Protection System

Advanced enterprise-grade content protection across 35+ platforms with AI-powered
fingerprinting, real-time monitoring, and automated violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Features:
- Multi-format fingerprinting (audio, video, image, text)
- 35+ platform monitoring (YouTube, Instagram, TikTok, etc.)
- Real-time violation detection with AI
- DMCA notice generation
- Revenue recovery tracking
"""
from .manager import ContentProtectionManager
from .core.protection_engine import ContentProtectionEngine
from .core.platform_monitor import PlatformMonitor
from .core.fingerprint_generator import FingerprintGenerator
from .models.protection_models import (
    ProtectionRequest,
    ProtectionResult,
    PlatformConfig,
    ViolationReport
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "ContentProtectionManager",
    "ContentProtectionEngine", 
    "PlatformMonitor",
    "FingerprintGenerator",
    "ProtectionRequest",
    "ProtectionResult",
    "PlatformConfig",
    "ViolationReport"
]