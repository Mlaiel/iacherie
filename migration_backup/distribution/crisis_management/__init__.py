"""Crisis Management Engine

Advanced crisis detection, management, and reputation protection system for the Ainflue platform.
Provides real-time crisis monitoring, automated damage control, and reputation recovery
using AI-powered crisis management protocols.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .crisis_detector import CrisisDetector, CrisisAlert
from .damage_control_engine import DamageControlEngine, ControlStrategy
from .reputation_protector import ReputationProtector, ProtectionPlan
from .emergency_communication import EmergencyCommunication, CommunicationPlan
from .sentiment_monitor import SentimentMonitor, SentimentAnalysis
from .recovery_planner import RecoveryPlanner, RecoveryStrategy
from .brand_safety_guardian import BrandSafetyGuardian, SafetyProtocol
from .crisis_analytics import CrisisAnalytics, CrisisMetrics

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "CrisisDetector", "CrisisAlert", "DamageControlEngine", "ControlStrategy",
    "ReputationProtector", "ProtectionPlan", "EmergencyCommunication", "CommunicationPlan",
    "SentimentMonitor", "SentimentAnalysis", "RecoveryPlanner", "RecoveryStrategy",
    "BrandSafetyGuardian", "SafetyProtocol", "CrisisAnalytics", "CrisisMetrics"
]