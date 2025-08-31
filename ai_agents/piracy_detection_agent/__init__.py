"""Piracy Detection Agent - Deep Web Monitoring & Content Piracy Detection

Advanced AI-powered piracy detection system with deep web monitoring capabilities,
dark web scanning, and comprehensive intellectual property protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Features:
- Deep web and dark web monitoring
- Torrent and P2P network scanning
- Streaming site detection
- File sharing platform monitoring
- AI-powered content matching
"""from .manager import PiracyDetectionManager
from .core.deep_web_scanner import DeepWebScanner
from .core.torrent_monitor import TorrentMonitor
from .core.streaming_detector import StreamingDetector
from .models.piracy_models import (
    PiracyDetectionRequest,
    PiracyDetectionResult,
    PiracySource,
    ThreatLevel
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    "PiracyDetectionManager",
    "DeepWebScanner",
    "TorrentMonitor", 
    "StreamingDetector",
    "PiracyDetectionRequest",
    "PiracyDetectionResult",
    "PiracySource",
    "ThreatLevel"
]