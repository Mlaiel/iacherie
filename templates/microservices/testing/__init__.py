#!/usr/bin/env python3
"""
🧪 Testing Templates - IA Chérie Microservices Enterprise

Comprehensive testing templates for unit tests, integration tests,
load testing, security testing, and end-to-end testing automation.

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de

⚠️ PROPRIETARY SOFTWARE - Unauthorized use prohibited
"""

from .unit_test_template import UnitTestTemplate
from .integration_test_template import IntegrationTestTemplate
from .contract_test_template import ContractTestTemplate
from .load_test_template import LoadTestTemplate
from .chaos_test_template import ChaosTestTemplate
from .security_test_template import SecurityTestTemplate
from .performance_test_template import PerformanceTestTemplate
from .e2e_test_template import E2ETestTemplate

__all__ = [
    "UnitTestTemplate",
    "IntegrationTestTemplate", 
    "ContractTestTemplate",
    "LoadTestTemplate",
    "ChaosTestTemplate",
    "SecurityTestTemplate",
    "PerformanceTestTemplate",
    "E2ETestTemplate"
]