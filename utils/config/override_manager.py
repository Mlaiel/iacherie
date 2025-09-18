"""
Configuration Override Manager
=============================

Enterprise configuration override management with priority-based merging,
conditional overrides, and dynamic configuration adjustments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
import threading
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class OverridePriority(Enum):
    """Override priority levels."""
    LOWEST = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    HIGHEST = 100
    CRITICAL = 999

class OverrideScope(Enum):
    """Override scope definitions."""
    GLOBAL = "global"
    ENVIRONMENT = "environment"
    USER = "user"
    SESSION = "session"
    FEATURE = "feature"
    TEMPORARY = "temporary"

@dataclass
class ConfigurationOverride:
    """Configuration override definition."""
    name: str
    scope: OverrideScope
    priority: OverridePriority
    config_path: str
    value: Any
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    created_by: Optional[str] = None
    reason: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
            
    def is_expired(self) -> bool:
        """Check if override has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
        
    def should_apply(self, config: Dict[str, Any]) -> bool:
        """Check if override should be applied based on conditions."""
        if self.is_expired():
            return False
            
        if self.condition is None:
            return True
            
        try:
            return self.condition(config)
        except Exception as e:
            logger.warning(f"Override condition evaluation failed for {self.name}: {e}")
            return False

class OverrideManager:
    """
    Enterprise configuration override manager.
    
    Features:
    - Priority-based override application
    - Conditional overrides based on context
    - Scoped overrides (global, environment, user, etc.)
    - Temporary overrides with expiration
    - Override tracking and auditing
    - Thread-safe operations
    - Dynamic override management
    """
    
    def __init__(self):
        self.overrides: List[ConfigurationOverride] = []
        self.lock = threading.RLock()
        self.override_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
    def add_override(self, override: ConfigurationOverride) -> None:
        """
        Add configuration override.
        
        Args:
            override: Configuration override to add
        """
        with self.lock:
            # Remove any existing override with the same name
            self.remove_override(override.name)
            
            self.overrides.append(override)
            
            # Sort by priority (highest first)
            self.overrides.sort(key=lambda x: x.priority.value, reverse=True)
            
            # Add to history
            self._add_to_history("add_override", override.name, override.config_path, override.value)
            
            logger.info(f"Added override {override.name} for {override.config_path} with priority {override.priority.name}")
            
    def remove_override(self, name: str) -> bool:
        """
        Remove configuration override by name.
        
        Args:
            name: Override name to remove
            
        Returns:
            bool: True if override was removed, False if not found
        """
        with self.lock:
            for i, override in enumerate(self.overrides):
                if override.name == name:
                    removed_override = self.overrides.pop(i)
                    self._add_to_history("remove_override", name, removed_override.config_path, None)
                    logger.info(f"Removed override {name}")
                    return True
            return False
            
    def get_override(self, name: str) -> Optional[ConfigurationOverride]:
        """Get override by name."""
        with self.lock:
            for override in self.overrides:
                if override.name == name:
                    return override
            return None
            
    def apply_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all applicable overrides to configuration.
        
        Args:
            config: Base configuration to apply overrides to
            
        Returns:
            Dict with overrides applied
        """
        with self.lock:
            result_config = config.copy()
            applied_overrides = []
            
            # Remove expired overrides
            self._cleanup_expired_overrides()
            
            # Apply overrides in priority order
            for override in self.overrides:
                if override.should_apply(result_config):
                    self._apply_single_override(result_config, override)
                    applied_overrides.append(override.name)
                    
            if applied_overrides:
                logger.debug(f"Applied overrides: {applied_overrides}")
                
            return result_config
            
    def _apply_single_override(self, config: Dict[str, Any], override: ConfigurationOverride) -> None:
        """Apply single override to configuration."""
        keys = override.config_path.split('.')
        current = config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Apply override value
        current[keys[-1]] = override.value
        
    def _cleanup_expired_overrides(self) -> None:
        """Remove expired overrides."""
        expired_names = []
        
        for override in self.overrides[:]:  # Create copy to avoid modification during iteration
            if override.is_expired():
                expired_names.append(override.name)
                self.overrides.remove(override)
                
        if expired_names:
            logger.info(f"Removed expired overrides: {expired_names}")
            
    def add_environment_override(self, environment: str, config_path: str, 
                               value: Any, priority: OverridePriority = OverridePriority.MEDIUM) -> None:
        """Add environment-specific override."""
        condition = lambda config: config.get('environment', {}).get('environment') == environment
        
        override = ConfigurationOverride(
            name=f"env_{environment}_{config_path}",
            scope=OverrideScope.ENVIRONMENT,
            priority=priority,
            config_path=config_path,
            value=value,
            condition=condition,
            reason=f"Environment-specific override for {environment}"
        )
        
        self.add_override(override)
        
    def add_user_override(self, user_id: str, config_path: str, 
                         value: Any, priority: OverridePriority = OverridePriority.HIGH) -> None:
        """Add user-specific override."""
        condition = lambda config: config.get('user', {}).get('id') == user_id
        
        override = ConfigurationOverride(
            name=f"user_{user_id}_{config_path}",
            scope=OverrideScope.USER,
            priority=priority,
            config_path=config_path,
            value=value,
            condition=condition,
            reason=f"User-specific override for {user_id}"
        )
        
        self.add_override(override)
        
    def add_feature_override(self, feature_flag: str, config_path: str, 
                           value: Any, priority: OverridePriority = OverridePriority.HIGH) -> None:
        """Add feature flag-based override."""
        condition = lambda config: config.get('features', {}).get(feature_flag, False)
        
        override = ConfigurationOverride(
            name=f"feature_{feature_flag}_{config_path}",
            scope=OverrideScope.FEATURE,
            priority=priority,
            config_path=config_path,
            value=value,
            condition=condition,
            reason=f"Feature flag override for {feature_flag}"
        )
        
        self.add_override(override)
        
    def add_temporary_override(self, config_path: str, value: Any, 
                             duration_minutes: int, 
                             priority: OverridePriority = OverridePriority.HIGHEST,
                             reason: Optional[str] = None) -> str:
        """
        Add temporary override with automatic expiration.
        
        Args:
            config_path: Configuration path to override
            value: Override value
            duration_minutes: Duration in minutes before expiration
            priority: Override priority
            reason: Reason for override
            
        Returns:
            str: Override name for later reference
        """
        from datetime import timedelta
        
        expires_at = datetime.now() + timedelta(minutes=duration_minutes)
        override_name = f"temp_{config_path}_{int(datetime.now().timestamp())}"
        
        override = ConfigurationOverride(
            name=override_name,
            scope=OverrideScope.TEMPORARY,
            priority=priority,
            config_path=config_path,
            value=value,
            expires_at=expires_at,
            reason=reason or f"Temporary override for {duration_minutes} minutes"
        )
        
        self.add_override(override)
        return override_name
        
    def add_conditional_override(self, name: str, config_path: str, value: Any,
                               condition: Callable[[Dict[str, Any]], bool],
                               priority: OverridePriority = OverridePriority.MEDIUM,
                               scope: OverrideScope = OverrideScope.GLOBAL) -> None:
        """Add conditional override with custom condition function."""
        override = ConfigurationOverride(
            name=name,
            scope=scope,
            priority=priority,
            config_path=config_path,
            value=value,
            condition=condition,
            reason="Conditional override with custom condition"
        )
        
        self.add_override(override)
        
    def list_overrides(self, scope: Optional[OverrideScope] = None) -> List[Dict[str, Any]]:
        """
        List all overrides with optional scope filtering.
        
        Args:
            scope: Optional scope filter
            
        Returns:
            List of override information
        """
        with self.lock:
            result = []
            
            for override in self.overrides:
                if scope is None or override.scope == scope:
                    result.append({
                        'name': override.name,
                        'scope': override.scope.value,
                        'priority': override.priority.name,
                        'config_path': override.config_path,
                        'value': override.value,
                        'created_at': override.created_at.isoformat(),
                        'expires_at': override.expires_at.isoformat() if override.expires_at else None,
                        'is_expired': override.is_expired(),
                        'reason': override.reason
                    })
                    
            return result
            
    def get_override_stats(self) -> Dict[str, Any]:
        """Get override statistics."""
        with self.lock:
            total_overrides = len(self.overrides)
            
            scope_counts = {}
            priority_counts = {}
            expired_count = 0
            
            for override in self.overrides:
                # Count by scope
                scope_counts[override.scope.value] = scope_counts.get(override.scope.value, 0) + 1
                
                # Count by priority
                priority_counts[override.priority.name] = priority_counts.get(override.priority.name, 0) + 1
                
                # Count expired
                if override.is_expired():
                    expired_count += 1
                    
            return {
                'total_overrides': total_overrides,
                'expired_overrides': expired_count,
                'active_overrides': total_overrides - expired_count,
                'scope_distribution': scope_counts,
                'priority_distribution': priority_counts,
                'history_size': len(self.override_history)
            }
            
    def _add_to_history(self, action: str, override_name: str, 
                       config_path: str, value: Any) -> None:
        """Add action to override history."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'override_name': override_name,
            'config_path': config_path,
            'value': value
        }
        
        self.override_history.append(history_entry)
        
        # Trim history if too large
        if len(self.override_history) > self.max_history_size:
            self.override_history = self.override_history[-self.max_history_size:]
            
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get override history."""
        with self.lock:
            if limit:
                return self.override_history[-limit:]
            return self.override_history.copy()
            
    def clear_overrides(self, scope: Optional[OverrideScope] = None) -> int:
        """
        Clear overrides with optional scope filtering.
        
        Args:
            scope: Optional scope filter
            
        Returns:
            int: Number of overrides removed
        """
        with self.lock:
            if scope is None:
                count = len(self.overrides)
                self.overrides.clear()
                self._add_to_history("clear_all", "all", "all", None)
                logger.info(f"Cleared all {count} overrides")
                return count
            else:
                removed_count = 0
                for override in self.overrides[:]:  # Create copy
                    if override.scope == scope:
                        self.overrides.remove(override)
                        removed_count += 1
                        
                self._add_to_history("clear_scope", scope.value, "scope", None)
                logger.info(f"Cleared {removed_count} overrides for scope {scope.value}")
                return removed_count
                
    def export_overrides(self) -> Dict[str, Any]:
        """Export all overrides for backup/restore."""
        with self.lock:
            return {
                'overrides': [
                    {
                        'name': o.name,
                        'scope': o.scope.value,
                        'priority': o.priority.value,
                        'config_path': o.config_path,
                        'value': o.value,
                        'created_at': o.created_at.isoformat(),
                        'expires_at': o.expires_at.isoformat() if o.expires_at else None,
                        'reason': o.reason
                    }
                    for o in self.overrides
                ],
                'export_timestamp': datetime.now().isoformat()
            }
            
    def import_overrides(self, override_data: Dict[str, Any], 
                        replace_existing: bool = False) -> int:
        """
        Import overrides from exported data.
        
        Args:
            override_data: Exported override data
            replace_existing: Whether to replace existing overrides
            
        Returns:
            int: Number of overrides imported
        """
        if replace_existing:
            self.clear_overrides()
            
        imported_count = 0
        
        for override_info in override_data.get('overrides', []):
            try:
                expires_at = None
                if override_info.get('expires_at'):
                    expires_at = datetime.fromisoformat(override_info['expires_at'])
                    
                override = ConfigurationOverride(
                    name=override_info['name'],
                    scope=OverrideScope(override_info['scope']),
                    priority=OverridePriority(override_info['priority']),
                    config_path=override_info['config_path'],
                    value=override_info['value'],
                    expires_at=expires_at,
                    created_at=datetime.fromisoformat(override_info['created_at']),
                    reason=override_info.get('reason')
                )
                
                self.add_override(override)
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Failed to import override {override_info.get('name', 'unknown')}: {e}")
                
        logger.info(f"Imported {imported_count} overrides")
        return imported_count