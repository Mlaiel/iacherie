"""
Simple Agents Module - Main Import Interface
This module provides the main interface for importing the simple agents system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import sys
import importlib

def _import_agents():
    """Lazy import the simple agents to avoid dependency issues"""
    try:
        from scripts.setup.simple_agents import (
            AgentStatus,
            AgentRequest,
            AgentResponse,
            BaseAgent,
            ProtectionAgent,
            SEOAgent,
            CollaborationAgent,
            DistributionAgent,
            MonetizationAgent,
            RightsManager,
            WorkflowMetrics,
            NotificationService
        )
        return {
            'AgentStatus': AgentStatus,
            'AgentRequest': AgentRequest,
            'AgentResponse': AgentResponse,
            'BaseAgent': BaseAgent,
            'ProtectionAgent': ProtectionAgent,
            'SEOAgent': SEOAgent,
            'CollaborationAgent': CollaborationAgent,
            'DistributionAgent': DistributionAgent,
            'MonetizationAgent': MonetizationAgent,
            'RightsManager': RightsManager,
            'WorkflowMetrics': WorkflowMetrics,
            'NotificationService': NotificationService
        }
    except ImportError as e:
        # Provide fallback implementations or raise a more helpful error
        print(f"Warning: Could not import simple agents: {e}")
        return None

# Create a module-level proxy to expose the functionality
_agent_components = None

def __getattr__(name):
    """Proxy attribute access to load agent components on demand"""
    global _agent_components
    if _agent_components is None:
        _agent_components = _import_agents()
    
    if _agent_components and name in _agent_components:
        return _agent_components[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'AgentStatus',
    'AgentRequest', 
    'AgentResponse',
    'BaseAgent',
    'ProtectionAgent',
    'SEOAgent',
    'CollaborationAgent',
    'DistributionAgent',
    'MonetizationAgent',
    'RightsManager',
    'WorkflowMetrics',
    'NotificationService'
]