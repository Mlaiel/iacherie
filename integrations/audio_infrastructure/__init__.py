"""🎵 Audio Infrastructure Module - Enterprise Implementation
========================================================

Module d'infrastructure audio enterprise avec traitement temps réel,
streaming optimization et codecs professionnels pour Ainflue.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_audio_infrastructure import (
    EnterpriseAudioInfrastructure,
    AudioConfiguration,
    AudioStream,
    AudioProcessingJob,
    AudioMetrics,
    AudioFormat,
    AudioQuality,
    ProcessingType,
    StreamingProtocol,
    initialize_audio_infrastructure
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseAudioInfrastructure",
    "AudioConfiguration",
    "AudioStream",
    "AudioProcessingJob",
    "AudioMetrics",
    "AudioFormat",
    "AudioQuality",
    "ProcessingType",
    "StreamingProtocol",
    "initialize_audio_infrastructure"
]