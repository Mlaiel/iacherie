"""
API Gateway Agent - Enterprise API Management System

Industrial-grade API Gateway for orchestrating all microservices and agents in the 
IA-Influencer-Agent platform with advanced routing, security, and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .api_gateway_agent import APIGatewayAgent
from .request_router import RequestRouter
from .load_balancer import LoadBalancer
from .rate_limiter import RateLimiter
from .auth_middleware import AuthMiddleware
from .response_aggregator import ResponseAggregator
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector
from .config import APIGatewayConfig

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    'APIGatewayAgent',
    'RequestRouter', 
    'LoadBalancer',
    'RateLimiter',
    'AuthMiddleware',
    'ResponseAggregator',
    'CircuitBreaker',
    'MetricsCollector',
    'APIGatewayConfig'
]
