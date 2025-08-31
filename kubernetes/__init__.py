"""IA Influencer Agent - Deployment Module
Enterprise-grade deployment configuration for multi-format creator platform

This module provides production-ready deployment infrastructure for:
- Multi-format content processing (music, video, image, text)
- AI-powered content protection and fingerprinting
- Automated monetization and collaboration matching
- Kubernetes orchestration and cloud deployment
- Security hardening and monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
License: Proprietary - All rights reserved

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""from .docker import container_manager
from .kubernetes import cluster_orchestrator
from .cloud import cloud_provisioner
from .monitoring import deployment_monitor
from .security import security_hardening
from .load_balancer import traffic_manager
from .backup import backup_orchestrator
from .health_checks import health_monitor

__all__ = [
    'container_manager',
    'cluster_orchestrator', 
    'cloud_provisioner',
    'deployment_monitor',
    'security_hardening',
    'traffic_manager',
    'backup_orchestrator',
    'health_monitor'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
