"""
Data Pipelines Module for IA Influencer Agent Platform
======================================================

Professional data pipeline orchestration for multi-format content processing,
AI protection, and monetization workflows for digital creators.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI architecture
- ML Engineer: Deep learning models and AI processing pipelines
- DBA: High-performance database optimization
- Security Engineer: Enterprise-grade security protocols
- Microservices Architect: Scalable distributed systems
- Audio Engineer: Professional audio processing and analysis
- DevOps Engineer: Production deployment and monitoring
- AI Prompt Engineer: Intelligent content generation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, theft, copying, or reproduction without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will
result in immediate legal action under German and international copyright laws.
"""

from .content_ingestion import ContentIngestionPipeline, MultiFormatProcessor
from .protection_pipeline import ProtectionPipeline, FingerprintingEngine
from .monetization_pipeline import MonetizationPipeline, RevenueCalculatorEngine
from .analytics_pipeline import AnalyticsPipeline, MetricsAggregator
from .collaboration_pipeline import CollaborationPipeline, MatchingEngine
from .distribution_pipeline import DistributionPipeline, PlatformManager
from .orchestrator import PipelineOrchestrator, WorkflowManager
from .monitoring import PipelineMonitor, HealthChecker

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - All Rights Reserved"

__all__ = [
    # Core Pipelines
    "ContentIngestionPipeline",
    "ProtectionPipeline", 
    "MonetizationPipeline",
    "AnalyticsPipeline",
    "CollaborationPipeline",
    "DistributionPipeline",
    
    # Processing Engines
    "MultiFormatProcessor",
    "FingerprintingEngine",
    "RevenueCalculatorEngine",
    "MetricsAggregator",
    "MatchingEngine",
    "PlatformManager",
    
    # Orchestration
    "PipelineOrchestrator",
    "WorkflowManager",
    "PipelineMonitor",
    "HealthChecker",
]
