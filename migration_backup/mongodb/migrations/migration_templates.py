"""Migration Templates and Testing Framework (Aliases)
===================================================

Aliases for migration templates and testing framework components.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

# Import from rollback_manager to avoid duplication
from .rollback_manager import (
    MigrationTemplates as _MigrationTemplates,
    TestingFramework as _TestingFramework,
    get_migration_templates,
    get_testing_framework
)

# Create aliases for backward compatibility
MigrationTemplates = _MigrationTemplates
TestingFramework = _TestingFramework

__all__ = ['MigrationTemplates', 'TestingFramework']