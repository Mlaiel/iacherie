"""
ApiGateway Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade api_gateway capabilities with
intelligent optimization and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

# Master Manager
from .manager import (
    ApiGatewayManager,
    ApiGatewaySystemStatus
)

# Core System
from .core.api_gateway_engine import (
    ApiGatewayEngine,
    ApiGatewayJob,
    ApiGatewayResult
)

# Legacy compatibility (for smooth migration)
from .manager import ApiGatewayManager as ApiGatewayAgent

__all__ = [
    # Master Manager
    'ApiGatewayManager',
    'ApiGatewaySystemStatus',
    
    # Core System
    'ApiGatewayEngine',
    'ApiGatewayJob',
    'ApiGatewayResult',
    
    # Legacy compatibility
    'ApiGatewayAgent'
]
