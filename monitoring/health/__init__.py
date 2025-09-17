"""🏥 Health Monitoring Module | Ainflue Creator Economy Enterprise
==============================================================================
© 2025 Fahed Mlaiel <mlaiel@live.de> - TOUS DROITS RÉSERVÉS

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande: mlaiel@live.de
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Experts: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
         Microservices + Audio + DevOps + IA Prompt Engineer
Architecture: Creator Economy Enterprise Health Monitoring System
==============================================================================
"""

# =============== CORE HEALTH MONITORING IMPORTS ===============

try:
    # Main orchestrator and configuration
    from .index import (
        HealthMonitoringOrchestrator,
        CreatorEconomyHealthConfig,
        CreatorTier,
        CreatorFormat,
        create_health_monitoring_orchestrator,
        health_monitoring_context
    )
except ImportError as e:
    print(f"⚠️ Main orchestrator not available: {e}")
    HealthMonitoringOrchestrator = None

try:
    # Creator Economy specialized components
    from .creator_economy_health_orchestrator import (
        CreatorEconomyHealthOrchestrator,
        CreatorHealthMetrics,
        CreatorEconomyOverallHealth,
        CreatorHealthStatus,
        MonetizationHealthLevel,
        ContentPipelineStatus
    )
except ImportError as e:
    print(f"⚠️ Creator Economy orchestrator not available: {e}")
    CreatorEconomyHealthOrchestrator = None

try:
    from .creator_performance_health_monitor import (
        CreatorPerformanceHealthMonitor,
        CreatorPerformanceProfile,
        PerformanceMetric,
        PerformanceAnalyticsSnapshot,
        PerformanceHealthLevel,
        PerformanceMetricType,
        PerformanceTrendDirection
    )
except ImportError as e:
    print(f"⚠️ Performance monitor not available: {e}")
    CreatorPerformanceHealthMonitor = None

try:
    from .ai_ml_health_intelligence_engine import (
        AIMLHealthIntelligenceEngine,
        AIModelHealthMetrics,
        AIEcosystemHealthSnapshot,
        AIIntelligenceInsight,
        AIModelHealthStatus,
        AIProcessingType,
        ModelPerformanceLevel,
        AIResourceType
    )
except ImportError as e:
    print(f"⚠️ AI/ML intelligence engine not available: {e}")
    AIMLHealthIntelligenceEngine = None

# Existing core health checks
from .health_checks import (
    HealthChecksManager,
    SystemMetrics,
    HealthChecker,
    MonitoringConfig,
    track_performance
)

# =============== MODULE VERSION AND METADATA ===============

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Creator Economy Enterprise Health Monitoring System"

# =============== CREATOR ECONOMY HEALTH MONITORING EXPORTS ===============

__all__ = [
    # Core health checks (always available)
    "HealthChecksManager",
    "SystemMetrics",
    "HealthChecker",
    "MonitoringConfig",
    "track_performance",
    
    # Module metadata
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]

# Add optional components to exports if available
if HealthMonitoringOrchestrator:
    __all__.extend([
        "HealthMonitoringOrchestrator",
        "CreatorEconomyHealthConfig",
        "CreatorTier", 
        "CreatorFormat",
        "create_health_monitoring_orchestrator",
        "health_monitoring_context"
    ])

if CreatorEconomyHealthOrchestrator:
    __all__.extend([
        "CreatorEconomyHealthOrchestrator",
        "CreatorHealthMetrics",
        "CreatorEconomyOverallHealth", 
        "CreatorHealthStatus",
        "MonetizationHealthLevel",
        "ContentPipelineStatus"
    ])

if CreatorPerformanceHealthMonitor:
    __all__.extend([
        "CreatorPerformanceHealthMonitor",
        "CreatorPerformanceProfile",
        "PerformanceMetric",
        "PerformanceAnalyticsSnapshot",
        "PerformanceHealthLevel",
        "PerformanceMetricType", 
        "PerformanceTrendDirection"
    ])

if AIMLHealthIntelligenceEngine:
    __all__.extend([
        "AIMLHealthIntelligenceEngine",
        "AIModelHealthMetrics",
        "AIEcosystemHealthSnapshot",
        "AIIntelligenceInsight",
        "AIModelHealthStatus",
        "AIProcessingType",
        "ModelPerformanceLevel",
        "AIResourceType"
    ])

# =============== HEALTH MONITORING UTILITY FUNCTIONS ===============

def get_health_monitoring_info() -> dict:
    """📋 Obtenir les informations du module de monitoring
    
    Returns:
        dict: Informations du module
    """
    available_components = {}
    
    if HealthMonitoringOrchestrator:
        available_components["orchestrator"] = "HealthMonitoringOrchestrator"
    if CreatorEconomyHealthOrchestrator:
        available_components["creator_economy"] = "CreatorEconomyHealthOrchestrator"
    if CreatorPerformanceHealthMonitor:
        available_components["performance"] = "CreatorPerformanceHealthMonitor"
    if AIMLHealthIntelligenceEngine:
        available_components["ai_ml"] = "AIMLHealthIntelligenceEngine"
    
    available_components["core_checks"] = "HealthChecksManager"
    
    return {
        "module_name": "health",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "available_components": available_components,
        "total_components": len(available_components),
        "features": [
            "Real-time health monitoring",
            "Creator Economy specialized analytics",
            "AI/ML performance intelligence", 
            "Predictive health analytics",
            "Automated optimization",
            "Multi-tier creator support",
            "Cross-format collaboration tracking",
            "Revenue health monitoring",
            "Content pipeline validation",
            "Enterprise compliance monitoring"
        ]
    }

# =============== HEALTH MONITORING CONSTANTS ===============

# Creator Economy health thresholds
CREATOR_HEALTH_THRESHOLDS = {
    "excellent": 90.0,
    "good": 75.0,
    "average": 60.0,
    "poor": 40.0,
    "critical": 20.0
}

# Performance monitoring intervals
MONITORING_INTERVALS = {
    "real_time": 10,      # seconds
    "frequent": 60,       # seconds  
    "standard": 300,      # seconds (5 minutes)
    "periodic": 1800,     # seconds (30 minutes)
    "daily": 86400        # seconds (24 hours)
}

# AI/ML model health benchmarks
AI_MODEL_BENCHMARKS = {
    "content_analysis": {"accuracy": 85.0, "latency_ms": 100.0},
    "audio_processing": {"accuracy": 90.0, "latency_ms": 500.0},
    "image_processing": {"accuracy": 88.0, "latency_ms": 200.0},
    "video_processing": {"accuracy": 85.0, "latency_ms": 1000.0},
    "text_processing": {"accuracy": 92.0, "latency_ms": 50.0}
}

# Export constants
__all__.extend([
    "get_health_monitoring_info", 
    "CREATOR_HEALTH_THRESHOLDS",
    "MONITORING_INTERVALS",
    "AI_MODEL_BENCHMARKS"
])