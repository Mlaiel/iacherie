"""Testing Framework (Alias)
=========================

Alias for testing framework component.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

# Import from rollback_manager to avoid duplication
from .rollback_manager import (
    TestingFramework as _TestingFramework,
    get_testing_framework
)

# Create alias for backward compatibility
TestingFramework = _TestingFramework

__all__ = ['TestingFramework']