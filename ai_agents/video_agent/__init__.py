"""
Video Agent Module - Industrial Video Processing & Analysis System

Advanced AI-powered video processing, analysis, and generation system for video content creators.
Handles video fingerprinting, quality analysis, format conversion, and AI-powered video enhancement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Video Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

from .video_agent import VideoAgent, VideoAgentManager
from .video_processor import VideoProcessor, VideoAnalyzer
from .video_generator import AIVideoGenerator, VideoSynthesizer
from .video_enhancer import VideoEnhancer, FrameStabilizer
from .format_converter import VideoFormatConverter, CompressionOptimizer
from .index import VideoAgentIndex

__all__ = [
    'VideoAgent',
    'VideoAgentManager', 
    'VideoProcessor',
    'VideoAnalyzer',
    'AIVideoGenerator',
    'VideoSynthesizer',
    'VideoEnhancer',
    'FrameStabilizer',
    'VideoFormatConverter',
    'CompressionOptimizer',
    'VideoAgentIndex'
]
