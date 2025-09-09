"""AI Agents Orchestrator - Compatibility Module

This module provides compatibility import for the IA Agents Orchestrator.
Author: Fahed Mlaiel <mlaiel@live.de>
"""

# Import everything from the actual ia_agents_orchestrator module
from .ia_agents_orchestrator import *

# Maintain backward compatibility
__all__ = [
    'IAAgentsOrchestrator',
    'ContentProcessingAgent',
    'ProtectionSecurityAgent',
    'SEOOptimizationAgent',
    'AnalyticsIntelligenceAgent',
    'CollaborationMatchingAgent',
    'MonetizationRevenueAgent',
    'PlatformDistributionAgent',
    'AgentHealthMonitor',
    'WorkloadDistributor',
    'AgentRegistry',
    'OrchestrationConfig'
]