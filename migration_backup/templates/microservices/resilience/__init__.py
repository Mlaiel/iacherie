#!/usr/bin/env python3
"""
🛡️ Resilience Templates - IA Chéries Microservices Enterprise

Resilience patterns for fault tolerance, graceful degradation,
disaster recovery, and system reliability enhancement.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

from .retry_policy_template import RetryPolicyTemplate
from .timeout_handler_template import TimeoutHandlerTemplate
from .bulkhead_pattern_template import BulkheadPatternTemplate
from .fallback_handler_template import FallbackHandlerTemplate
from .health_circuit_template import HealthCircuitTemplate
from .graceful_shutdown_template import GracefulShutdownTemplate
from .disaster_recovery_template import DisasterRecoveryTemplate
from .failover_template import FailoverTemplate

__all__ = [
    "RetryPolicyTemplate",
    "TimeoutHandlerTemplate",
    "BulkheadPatternTemplate",
    "FallbackHandlerTemplate", 
    "HealthCircuitTemplate",
    "GracefulShutdownTemplate",
    "DisasterRecoveryTemplate",
    "FailoverTemplate"
]