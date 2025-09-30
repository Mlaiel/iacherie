"""Advanced Compression Intelligence Module
High-performance multimedia compression with AI-driven optimization.

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

from .audio_compression import AudioCompressionEngine
from .video_compression import VideoCompressionEngine  
from .image_compression import ImageCompressionEngine
from .adaptive_compression import AdaptiveCompressionEngine
from .lossless_compression import LosslessCompressionEngine
from .compression_profiles import CompressionProfileManager
from .batch_compression import BatchCompressionProcessor
from .streaming_compression import StreamingCompressionEngine
from .quality_preservation import QualityPreservationEngine
from .compression_scheduler import CompressionScheduler
from .optimization_engine import CompressionOptimizationEngine
from .codec_management import CodecManager
from .compression_validation import CompressionValidator

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AudioCompressionEngine",
    "VideoCompressionEngine", 
    "ImageCompressionEngine",
    "AdaptiveCompressionEngine",
    "LosslessCompressionEngine",
    "CompressionProfileManager",
    "BatchCompressionProcessor",
    "StreamingCompressionEngine",
    "QualityPreservationEngine",
    "CompressionScheduler",
    "CompressionOptimizationEngine",
    "CodecManager",
    "CompressionValidator"
]