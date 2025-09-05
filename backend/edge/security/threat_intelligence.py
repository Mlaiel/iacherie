"""Threat Intelligence Module - simplified version already included in intrusion_detection.py"""

from .intrusion_detection import ThreatIntelligence, ThreatIndicator, ThreatSource, create_threat_intelligence

__all__ = [
    "ThreatIntelligence",
    "ThreatIndicator", 
    "ThreatSource",
    "create_threat_intelligence"
]