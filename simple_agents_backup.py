#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Top-level simple_agents module import alias
==========================================

This module provides a top-level import alias for the simple agents
to maintain backward compatibility with existing test imports.

Author: Auto-generated for import compatibility  
"""
# Import all public components from the scripts.setup module
from scripts.setup.simple_agents import *

# Ensure main classes are available at module level
from scripts.setup.simple_agents import (
    BaseAgent,
    AgentStatus,
    CollaborationAgent,
    SEOAgent,
    DistributionAgent,
    MonetizationAgent,
    ProtectionAgent,
    AgentRequest,
    AgentResponse,
    WorkflowMetrics
)

__all__ = [
    'BaseAgent',
    'AgentStatus',
    'CollaborationAgent',
    'SEOAgent',
    'DistributionAgent',
    'MonetizationAgent',
    'ProtectionAgent',
    'AgentRequest',
    'AgentResponse',
    'WorkflowMetrics'
]