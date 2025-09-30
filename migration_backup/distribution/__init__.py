"""Multi-Platform Distribution Module

Advanced multi-platform content distribution system for the Ainflue platform.
Handles automated publication scheduling, format adaptation, analytics aggregation,
hashtag optimization, and A/B testing across all major social platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel (mlaiel@live.de)
- Distribution Systems Architect: Fahed Mlaiel (mlaiel@live.de)
- Platform Integration Specialist: Fahed Mlaiel (mlaiel@live.de)
- Social Media API Expert: Fahed Mlaiel (mlaiel@live.de)
- Content Optimization Analyst: Fahed Mlaiel (mlaiel@live.de)
"""

# Import core modules with proper error handling
try:
    from .connectors import *
except ImportError:
    pass

try:
    from .scheduling import *
except ImportError:
    pass

try:
    from .core import *
except ImportError:
    pass

try:
    from .analytics import *
except ImportError:
    pass

try:
    from .config import *
except ImportError:
    pass

try:
    from .monitoring import *
except ImportError:
    pass

try:
    from .security import *
except ImportError:
    pass

try:
    from .ai_intelligence import *
except ImportError:
    pass

try:
    from .audience_intelligence import *
except ImportError:
    pass

try:
    from .content_amplification import *
except ImportError:
    pass

try:
    from .creator_collaboration_hub import *
except ImportError:
    pass

try:
    from .crisis_management import *
except ImportError:
    pass

try:
    from .geographic_optimization import *
except ImportError:
    pass

try:
    from .management import *
except ImportError:
    pass

try:
    from .optimization import *
except ImportError:
    pass

try:
    from .platform_optimization import *
except ImportError:
    pass

try:
    from .real_time_optimization import *
except ImportError:
    pass

try:
    from .tests import *
except ImportError:
    pass

try:
    from .viral_optimization import *
except ImportError:
    pass

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Main exports
__all__ = [
    # Core distribution functionality
    "DistributionManager",
    "PlatformConnector", 
    "ContentScheduler",
    "AnalyticsAggregator",
    
    # AI Intelligence (53 Agents)
    "AIOrchestrator",
    "DistributionAICoordinator",
    "ContentIntelligenceEngine",
    "PlatformIntelligenceEngine",
    "AudienceIntelligenceEngine", 
    "ViralIntelligenceEngine",
    "PerformanceIntelligenceEngine",
    "CrisisIntelligenceEngine",
    "GeographicIntelligenceEngine",
    "TemporalIntelligenceEngine",
    "CollaborationIntelligenceEngine",
    "MonetizationIntelligenceEngine",
    "ComplianceIntelligenceEngine",
    "RealTimeIntelligenceEngine",
    
    # AI and optimization
    "AudienceIntelligence",
    "ViralOptimization", 
    "ContentAmplification",
    
    # Management and monitoring
    "ManagementEngine",
    "MonitoringEngine",
    "SecurityEngine",
    
    # Configuration and testing
    "ConfigurationManager",
    "TestingEngine"
]