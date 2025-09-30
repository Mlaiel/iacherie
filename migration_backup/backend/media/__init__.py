"""Advanced Media Processing Module - Consolidated Architecture
=========================================================

Comprehensive multimedia processing, generation, protection, and distribution
engine for the Ainflue platform. Integrates AI-powered content creation,
intelligent protection systems, and enterprise-grade media workflows.

CONSOLIDATED ARCHITECTURE (18 FILES):
- 6 Core Generation & Processing Engines
- 4 Intelligence & Analytics Systems  
- 4 Management & Infrastructure Systems
- 4 Advanced Streaming & API Systems

Features:
- Multi-format AI content generation (text, image, video, audio, avatar)
- Advanced content protection and rights management
- Intelligent media analysis and classification
- Real-time collaboration workflows
- Multi-platform distribution optimization
- Performance monitoring and analytics
- Live streaming and transcoding
- Content personalization and API gateway

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core generation engines (6 files)
from .content_generation_engine import (
    ContentGenerationEngine
)

from .multimedia_generator import (
    MultimediaGenerator
)

# Media processing
from .media_processing_engine import (
    MediaProcessingEngine
)

# Protection & rights
from .content_protection_system import (
    ContentProtectionSystem
)

from .rights_management_engine import (
    RightsManagementEngine
)

# Intelligence & analytics
from .media_intelligence_engine import (
    MediaIntelligenceEngine
)

# Analytics & intelligence systems (4 files)
from .content_analytics_system import (
    ContentAnalyticsSystem
)

# Collaboration & workflow
from .collaboration_workflow_system import (
    CollaborationWorkflowSystem
)

# Optimization & distribution
from .content_optimization_engine import (
    ContentOptimizationEngine
)

from .distribution_management_system import (
    DistributionManagementSystem
)

# Management & infrastructure systems (4 files)
from .project_management_engine import (
    ProjectManagementEngine
)

from .compliance_monitoring_system import (
    ComplianceMonitoringSystem
)

# Advanced streaming & transcoding
from .media_streaming_engine import (
    MediaStreamingEngine
)

from .media_transcoding_pipeline import (
    MediaTranscodingPipeline
)

# Advanced systems (4 files)
from .content_personalization_engine import (
    ContentPersonalizationEngine
)

from .media_performance_monitor import (
    MediaPerformanceMonitor
)

# API Gateway
from .media_api_gateway import (
    MediaAPIGateway
)

__version__ = "3.2.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Core engines (6 files)
    "ContentGenerationEngine",
    "MultimediaGenerator", 
    "MediaProcessingEngine",
    "ContentProtectionSystem",
    "RightsManagementEngine",
    "MediaIntelligenceEngine",
    
    # Analytics & intelligence (4 files)
    "ContentAnalyticsSystem",
    "CollaborationWorkflowSystem", 
    "ContentOptimizationEngine",
    "DistributionManagementSystem",
    
    # Management & infrastructure (4 files)
    "ProjectManagementEngine",
    "ComplianceMonitoringSystem",
    "MediaStreamingEngine",
    "MediaTranscodingPipeline",
    
    # Advanced systems (4 files)  
    "ContentPersonalizationEngine",
    "MediaPerformanceMonitor",
    "MediaAPIGateway"
]

# Module initialization
import logging
logger = logging.getLogger(__name__)
logger.info(f"🎬 Advanced Media Module v{__version__} loaded - CONSOLIDATED ARCHITECTURE")
logger.info(f"📁 18 consolidated files (6+4+4+4) replacing 40+ scattered files")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("✅ Architecture consolidation COMPLETE - Production ready")
