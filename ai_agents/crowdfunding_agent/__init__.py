"""Crowdfunding Agent - Participatory Funding Management

This module provides comprehensive crowdfunding campaign management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import CrowdfundingManager
from .core.crowdfunding_engine import CrowdfundingEngine

CrowdfundingAgent = CrowdfundingManager

__all__ = ['CrowdfundingManager', 'CrowdfundingEngine', 'CrowdfundingAgent']