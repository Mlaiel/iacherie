"""Backend Tests Configuration Module
=====================================

Configuration module for backend testing infrastructure including
industrial testing configurations, test environments, and test parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Import configuration modules
try:
    from .industrial_testing_config import (
        TestingLevel,
        TestingScope,
        IndustrialTestConfig,
        TestEnvironment,
        TestingMetrics,
        get_testing_config,
        validate_test_environment
    )
    INDUSTRIAL_CONFIG_AVAILABLE = True
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Industrial testing config not available: {e}")
    INDUSTRIAL_CONFIG_AVAILABLE = False

# Module exports
__all__ = []

if INDUSTRIAL_CONFIG_AVAILABLE:
    __all__.extend([
        "TestingLevel",
        "TestingScope", 
        "IndustrialTestConfig",
        "TestEnvironment",
        "TestingMetrics",
        "get_testing_config",
        "validate_test_environment"
    ])

# Module initialization
import logging
logger = logging.getLogger(__name__)
logger.info(f"🧪 Backend Tests Config v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")