"""
PagerDuty Integration Module for Ainflue Platform
Intelligent alerting and incident management for Creator Economy

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

from .pagerduty_client import PagerDutyClient, IncidentSeverity, IncidentStatus
from .escalation_manager import EscalationManager
from .intelligent_alert_router import IntelligentAlertRouter
from .creator_incident_classifier import (
    CreatorIncidentClassifier, 
    CreatorWorkflowStage, 
    IncidentCategory, 
    BusinessImpactLevel, 
    TeamAssignment
)
from .revenue_impact_calculator import (
    RevenueImpactCalculator,
    RevenueStreamType,
    ImpactSeverity,
    CreatorMetrics,
    IncidentImpactResult
)
from .collaboration_incident_manager import (
    CollaborationIncidentManager,
    CollaborationType,
    StakeholderRole,
    CollaborationIncident
)

__all__ = [
    # Core PagerDuty Integration
    'PagerDutyClient',
    'IncidentSeverity',
    'IncidentStatus',
    'EscalationManager',
    'IntelligentAlertRouter',
    
    # Creator-Specific Classification
    'CreatorIncidentClassifier',
    'CreatorWorkflowStage',
    'IncidentCategory',
    'BusinessImpactLevel',
    'TeamAssignment',
    
    # Revenue Impact Assessment
    'RevenueImpactCalculator',
    'RevenueStreamType',
    'ImpactSeverity',
    'CreatorMetrics',
    'IncidentImpactResult',
    
    # Collaboration Management
    'CollaborationIncidentManager',
    'CollaborationType',
    'StakeholderRole',
    'CollaborationIncident'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise PagerDuty Integration for Creator Economy Platform"