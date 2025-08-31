"""IA Influencer Agent - Content Protection Deployment Module
Enterprise-Grade Content Protection Deployment System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module handles the deployment and orchestration of content protection
systems for multi-format content monitoring and violation detection.
"""
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Content protection deployment components
from .violation_detector import ViolationDetectorDeployment
from .content_monitoring import ContentMonitoringDeployment
from .alert_system import AlertSystemDeployment
from .legal_automation import LegalAutomationDeployment
from .protection_orchestrator import ProtectionOrchestrator
from .compliance_monitor import ComplianceMonitorDeployment

__all__ = [
    "ViolationDetectorDeployment",
    "ContentMonitoringDeployment",
    "AlertSystemDeployment", 
    "LegalAutomationDeployment",
    "ProtectionOrchestrator",
    "ComplianceMonitorDeployment"
]
