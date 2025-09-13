"""
Observability Module - Ainflue Infrastructure Enterprise
========================================================
Point d'entrée principal pour tous les services d'observabilité

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

# Imports principaux
from . import *

# Exports publics principaux
__all__ = [
    'MonitoringManager',
    'PrometheusManager',
    'GrafanaManager',
    'JaegerManager',
    'ELKStackManager',
    'AlertManager',
    'MetricsCollector',
    'LogAggregator',
    'PerformanceMonitor',
    'HealthChecker'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise observability infrastructure for Ainflue platform"

# Configuration observabilité métier Ainflue
AINFLUE_OBSERVABILITY_WORKFLOW = {
    'upload': 'Monitor content upload performance and errors',
    'ai_processing': 'Track AI model performance and resource usage', 
    'protection': 'Monitor IP protection and copyright enforcement',
    'monetization': 'Track revenue metrics and payment processing',
    'collaboration': 'Monitor creator interactions and matching',
    'seo': 'Track SEO performance and optimization metrics',
    'distribution': 'Monitor 65+ platform distribution performance'
}

# Métriques business pour créateurs
CREATOR_METRICS = {
    'engagement': 'User engagement and interaction metrics',
    'performance': 'Content performance across platforms',
    'revenue': 'Revenue tracking and optimization',
    'quality': 'Content quality and AI enhancement metrics',
    'security': 'Security and protection effectiveness'
}