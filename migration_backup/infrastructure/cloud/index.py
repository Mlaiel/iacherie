"""
Cloud Module - Ainflue Infrastructure Enterprise
===============================================
Point d'entrée principal pour tous les services cloud

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

# Imports principaux
from . import *

# Exports publics principaux
__all__ = [
    'CostManager',
    'MultiCloudManager',
    'AWSProvider',
    'GCPProvider',
    'AzureProvider',
    'MultiCloudOrchestrator',
    'HybridCloudManager',
    'CloudCostOptimizer',
    'CloudSecurityManager',
    'CloudMigrationTool',
    'ResourceProvisioner'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise multi-cloud infrastructure for Ainflue platform"

# Configuration cloud métier Ainflue
AINFLUE_CLOUD_WORKFLOW = {
    'upload': 'Multi-cloud content storage with global distribution',
    'ai_processing': 'GPU-optimized cloud instances for AI workloads', 
    'protection': 'Secure cloud storage for IP rights and blockchain integration',
    'monetization': 'Reliable cloud infrastructure for payment processing',
    'collaboration': 'Global cloud presence for creator collaboration',
    'seo': 'Edge computing for SEO optimization and fast delivery',
    'distribution': 'Multi-cloud CDN for 65+ platform distribution'
}

# Stratégies cloud pour créateurs
CREATOR_CLOUD_STRATEGIES = {
    'musician': 'High-bandwidth cloud storage for audio files with global CDN',
    'blogger': 'Content-optimized cloud infrastructure with caching',
    'photographer': 'High-capacity cloud storage with image optimization',
    'influencer': 'Multi-region cloud presence for global audience',
    'comedian': 'Video-optimized cloud infrastructure with streaming support'
}