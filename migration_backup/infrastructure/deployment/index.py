"""
Deployment Module - Ainflue Infrastructure Enterprise
====================================================
Point d'entrée principal pour tous les services de déploiement

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

# Imports principaux
from . import *

# Exports publics
__all__ = [
    'DeploymentManager',
    'CICDManager', 
    'PipelineManager',
    'BlueGreenDeployer',
    'CanaryDeployer',
    'RollingUpdater',
    'ReleaseManager'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de" 
__description__ = "Enterprise deployment infrastructure for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_DEPLOYMENT_WORKFLOW = {
    'upload': 'Multi-format content upload processing',
    'ai_processing': 'AI enhancement and analysis pipeline', 
    'protection': 'Rights protection and watermarking',
    'monetization': 'Revenue optimization across platforms',
    'collaboration': 'AI matching and gamification deployment',
    'seo': 'Professional SEO optimization deployment',
    'distribution': 'Massive distribution to 65+ platforms'
}

# Deployment strategies pour créateurs Ainflue
CREATOR_DEPLOYMENT_STRATEGIES = {
    'musician': 'Blue-green deployment for audio platforms',
    'blogger': 'Canary deployment for content platforms', 
    'photographer': 'Rolling update for visual platforms',
    'influencer': 'Multi-platform simultaneous deployment',
    'comedian': 'Performance-optimized deployment'
}