"""Advanced Multimedia Analytics Module
Analytics multimedia orchestrator for enterprise-grade insights and performance monitoring.

This module provides comprehensive analytics capabilities for multimedia content processing,
including audio analysis, video analytics, performance metrics, and engagement tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

from .audio_analytics import AudioAnalyzer, AudioMetrics, SpectrogramAnalyzer
from .video_analytics import VideoAnalyzer, MotionDetector, SceneAnalyzer
from .image_analytics import ImageAnalyzer, ColorAnalyzer, CompositionAnalyzer
from .performance_metrics import PerformanceTracker, ProcessingMetrics, ResourceMonitor
from .quality_metrics import QualityAssessment, QualityScorer, MultimediaQuality
from .engagement_analytics import EngagementTracker, UserBehaviorAnalyzer, InteractionMetrics
from .conversion_analytics import ConversionTracker, FormatAnalyzer, CompressionAnalytics
from .streaming_analytics import StreamingMonitor, BandwidthAnalyzer, QoSMetrics
from .distribution_metrics import DistributionTracker, PlatformAnalytics, ReachMetrics
from .ai_processing_insights import AIInsightEngine, ModelPerformanceTracker, PredictionAnalytics
from .creator_behavior_analysis import CreatorAnalyzer, ContentPatternAnalyzer, TrendDetector
from .content_trend_analysis import TrendAnalyzer, ViralityPredictor, ContentTrendEngine
from .multimedia_dashboard import MultimediaDashboard, AnalyticsDashboard, RealtimeMonitor

# Version information
__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Export all analytics components
__all__ = [
    # Audio Analytics
    "AudioAnalyzer", "AudioMetrics", "SpectrogramAnalyzer",
    
    # Video Analytics
    "VideoAnalyzer", "MotionDetector", "SceneAnalyzer",
    
    # Image Analytics
    "ImageAnalyzer", "ColorAnalyzer", "CompositionAnalyzer",
    
    # Performance Metrics
    "PerformanceTracker", "ProcessingMetrics", "ResourceMonitor",
    
    # Quality Metrics
    "QualityAssessment", "QualityScorer", "MultimediaQuality",
    
    # Engagement Analytics
    "EngagementTracker", "UserBehaviorAnalyzer", "InteractionMetrics",
    
    # Conversion Analytics
    "ConversionTracker", "FormatAnalyzer", "CompressionAnalytics",
    
    # Streaming Analytics
    "StreamingMonitor", "BandwidthAnalyzer", "QoSMetrics",
    
    # Distribution Metrics
    "DistributionTracker", "PlatformAnalytics", "ReachMetrics",
    
    # AI Processing Insights
    "AIInsightEngine", "ModelPerformanceTracker", "PredictionAnalytics",
    
    # Creator Behavior Analysis
    "CreatorAnalyzer", "ContentPatternAnalyzer", "TrendDetector",
    
    # Content Trend Analysis
    "TrendAnalyzer", "ViralityPredictor", "ContentTrendEngine",
    
    # Multimedia Dashboard
    "MultimediaDashboard", "AnalyticsDashboard", "RealtimeMonitor"
]