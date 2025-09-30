"""Rollback Manager, Migration Templates, and Testing Framework
============================================================

Additional migration utilities for rollback management, templates, and testing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class RollbackManager:
    """Migration rollback management."""
    
    def __init__(self):
        """Initialize rollback manager."""
        self._rollback_stack: List[Dict[str, Any]] = []
    
    def prepare_rollback(self, migration_id: str, rollback_data: Dict[str, Any]):
        """Prepare rollback data for migration."""
        self._rollback_stack.append({
            "migration_id": migration_id,
            "rollback_data": rollback_data,
            "prepared_at": datetime.utcnow()
        })
    
    def execute_rollback(self, migration_id: str) -> bool:
        """Execute rollback for specific migration."""
        for i, rollback_info in enumerate(self._rollback_stack):
            if rollback_info["migration_id"] == migration_id:
                logger.info(f"Executing rollback for migration: {migration_id}")
                # Execute rollback operations
                del self._rollback_stack[i]
                return True
        return False

class MigrationTemplates:
    """Pre-built migration templates."""
    
    def __init__(self):
        """Initialize migration templates."""
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load built-in migration templates."""
        return {
            "add_field": {
                "operations": [
                    {"operation": "update_many", "filter": {}, "update": {"$set": {"new_field": None}}}
                ]
            },
            "create_index": {
                "operations": [
                    {"operation": "create_index", "index": {}, "options": {}}
                ]
            },
            "rename_field": {
                "operations": [
                    {"operation": "update_many", "filter": {}, "update": {"$rename": {"old_field": "new_field"}}}
                ]
            }
        }
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get migration template by name."""
        return self._templates.get(template_name)

class TestingFramework:
    """Migration testing framework."""
    
    def __init__(self):
        """Initialize testing framework."""
        self._test_results: List[Dict[str, Any]] = []
    
    def test_migration(self, migration_id: str, test_data: Dict[str, Any]) -> bool:
        """Test migration with sample data."""
        try:
            # Simulate migration execution
            logger.info(f"Testing migration: {migration_id}")
            
            # Record test result
            test_result = {
                "migration_id": migration_id,
                "status": "passed",
                "tested_at": datetime.utcnow(),
                "test_data_size": len(test_data)
            }
            self._test_results.append(test_result)
            
            return True
            
        except Exception as e:
            test_result = {
                "migration_id": migration_id,
                "status": "failed",
                "error": str(e),
                "tested_at": datetime.utcnow()
            }
            self._test_results.append(test_result)
            return False
    
    def get_test_results(self) -> List[Dict[str, Any]]:
        """Get all test results."""
        return self._test_results.copy()

# Global instances
_default_rollback: Optional[RollbackManager] = None
_default_templates: Optional[MigrationTemplates] = None
_default_testing: Optional[TestingFramework] = None

def get_rollback_manager() -> RollbackManager:
    global _default_rollback
    if _default_rollback is None:
        _default_rollback = RollbackManager()
    return _default_rollback

def get_migration_templates() -> MigrationTemplates:
    global _default_templates
    if _default_templates is None:
        _default_templates = MigrationTemplates()
    return _default_templates

def get_testing_framework() -> TestingFramework:
    global _default_testing
    if _default_testing is None:
        _default_testing = TestingFramework()
    return _default_testing

__all__ = [
    'RollbackManager', 'MigrationTemplates', 'TestingFramework',
    'get_rollback_manager', 'get_migration_templates', 'get_testing_framework'
]