"""Data Streams Management Module for IA Influencer Agent Platform
==============================================================

Professional real-time data streaming layer for multi-format content processing,
protection monitoring, and revenue tracking workflows.

Features:
- Real-time content streaming and processing
- Live protection monitoring and alerts
- Revenue stream tracking and analytics
- Event-driven architecture for scalability
- Multi-platform data synchronization

Business Logic Flow:
User Upload → Stream Processing → AI Analysis → Protection → Monetization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  LEGAL WARNING 
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""
# Import all core components
from .manager import DataStreamManager, StreamType, StreamStatus, StreamEvent, StreamMetrics
from .processor import RealTimeProcessor, ProcessingJob, ProcessingPriority, ProcessingStage, ProcessingMetrics, ProcessingResult, ContentFormat
from .events import EventStreamer
from .monitoring import StreamMonitor
from .revenue import RevenueStreamer
from .platform import PlatformStreamer
from .analytics import StreamAnalytics
from .buffer import StreamBuffer, BufferConfig, BufferType, CompressionType, EvictionPolicy
from .scheduler import StreamScheduler
from .connector import StreamConnector
from .queue import StreamQueue

# Import index module for registry and utilities
from .index import (
    streams_registry,
    StreamsRegistry,
    StreamsModuleConfig,
    get_default_manager,
    get_default_processor,
    create_stream_components,
    get_module_info
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"

# Team Specialties
__team_specialties__ = [
    "Lead Developer IA",
    "Senior Backend Engineer", 
    "ML Engineer",
    "Database Administrator",
    "Security Specialist",
    "Microservices Architect",
    "Audio Processing Expert",
    "DevOps Engineer",
    "IA Prompt Engineer"
]

__all__ = [
    # Core Components
    "DataStreamManager",
    "RealTimeProcessor", 
    "EventStreamer",
    
    # Monitoring & Analytics
    "StreamMonitor",
    "StreamAnalytics",
    
    # Revenue & Platform Integration
    "RevenueStreamer",
    "PlatformStreamer",
    
    # Infrastructure
    "StreamBuffer",
    "StreamScheduler",
    "StreamConnector",
    "StreamQueue",
    
    # Enums and Types
    "StreamType",
    "StreamStatus",
    "ProcessingPriority",
    "ProcessingStage",
    "ContentFormat",
    "BufferType",
    "CompressionType",
    "EvictionPolicy",
    
    # Data Classes
    "StreamEvent",
    "StreamMetrics",
    "ProcessingJob",
    "ProcessingMetrics",
    "ProcessingResult",
    "BufferConfig",
    
    # Registry & Utilities
    "streams_registry",
    "StreamsRegistry",
    "StreamsModuleConfig",
    "get_default_manager",
    "get_default_processor",
    "create_stream_components",
    "get_module_info",
]
