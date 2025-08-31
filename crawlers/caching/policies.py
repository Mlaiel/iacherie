#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Policies - Advanced Cache Policy Management System
========================================================

Comprehensive policy management for cache behavior control,
lifecycle management, and intelligent decision making.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import threading
from abc import ABC, abstractmethod

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class PolicyType(Enum):
    """Cache policy types."""    EVICTION = "eviction"
    RETENTION = "retention"
    ACCESS = "access"
    STORAGE = "storage"
    SECURITY = "security"
    PERFORMANCE = "performance"

class PolicyScope(Enum):
    """Policy scope levels."""    GLOBAL = "global"
    NAMESPACE = "namespace"
    KEY_PATTERN = "key_pattern"
    USER = "user"
    SESSION = "session"

class PolicyAction(Enum):
    """Policy actions."""    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    REDIRECT = "redirect"
    LOG = "log"
    ALERT = "alert"

class ConditionOperator(Enum):
    """Condition operators."""    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    REGEX_MATCH = "regex_match"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"

@dataclass
class PolicyCondition:
    """Policy condition definition."""    field: str
    operator: ConditionOperator
    value: Any
    case_sensitive: bool = True

@dataclass
class PolicyRule:
    """Policy rule definition."""    rule_id: str
    name: str
    description: str
    conditions: List[PolicyCondition]
    action: PolicyAction
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class CachePolicy:
    """Cache policy definition."""    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    scope_pattern: str
    rules: List[PolicyRule]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyEvaluation:
    """Policy evaluation result."""    policy_id: str
    rule_id: Optional[str]
    action: PolicyAction
    allowed: bool
    reason: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    evaluation_time: datetime = field(default_factory=datetime.now)

class PolicyEngine:
    """    Advanced cache policy management engine.
    
    Features:
    - Multi-level policy hierarchy
    - Rule-based decision making
    - Pattern matching
    - Dynamic policy updates
    - Audit logging
    """    
    def __init__(self):
        """Initialize policy engine."""        self.logger = logging.getLogger(f"{__name__}.PolicyEngine")
        
        # Policy storage
        self.policies: Dict[str, CachePolicy] = {}
        self.policies_by_type: Dict[PolicyType, List[CachePolicy]] = {
            policy_type: [] for policy_type in PolicyType
        }
        
        # Rule evaluators
        self.condition_evaluators: Dict[ConditionOperator, Callable] = {
            ConditionOperator.EQUALS: self._evaluate_equals,
            ConditionOperator.NOT_EQUALS: self._evaluate_not_equals,
            ConditionOperator.GREATER_THAN: self._evaluate_greater_than,
            ConditionOperator.LESS_THAN: self._evaluate_less_than,
            ConditionOperator.CONTAINS: self._evaluate_contains,
            ConditionOperator.REGEX_MATCH: self._evaluate_regex_match,
            ConditionOperator.IN_LIST: self._evaluate_in_list,
            ConditionOperator.NOT_IN_LIST: self._evaluate_not_in_list
        }
        
        # Evaluation cache
        self.evaluation_cache: Dict[str, PolicyEvaluation] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Statistics
        self.stats = {
            'total_evaluations': 0,
            'policy_hits': 0,
            'cache_hits': 0,
            'evaluation_time_total': 0.0
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        self.logger.info("Policy engine initialized")
    
    async def add_policy(self, policy: CachePolicy) -> bool:
        """Add cache policy."""        try:
            with self.lock:
                self.policies[policy.policy_id] = policy
                self.policies_by_type[policy.policy_type].append(policy)
                
                # Sort by priority (higher priority first)
                self.policies_by_type[policy.policy_type].sort(
                    key=lambda p: max(rule.priority for rule in p.rules) if p.rules else 0,
                    reverse=True
                )
            
            self.logger.info(f"Added policy {policy.name} ({policy.policy_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding policy: {e}")
            return False
    
    async def remove_policy(self, policy_id: str) -> bool:
        """Remove cache policy."""        try:
            with self.lock:
                if policy_id not in self.policies:
                    return False
                
                policy = self.policies[policy_id]
                del self.policies[policy_id]
                
                # Remove from type index
                self.policies_by_type[policy.policy_type] = [
                    p for p in self.policies_by_type[policy.policy_type]
                    if p.policy_id != policy_id
                ]
            
            self.logger.info(f"Removed policy {policy_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing policy: {e}")
            return False
    
    async def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Update cache policy."""        try:
            with self.lock:
                if policy_id not in self.policies:
                    return False
                
                policy = self.policies[policy_id]
                
                # Update fields
                for field, value in updates.items():
                    if hasattr(policy, field):
                        setattr(policy, field, value)
                
                policy.updated_at = datetime.now()
                
                # Refresh type index
                self.policies_by_type[policy.policy_type] = [
                    p for p in self.policies_by_type[policy.policy_type]
                    if p.policy_id != policy_id
                ]
                self.policies_by_type[policy.policy_type].append(policy)
                
                # Re-sort by priority
                self.policies_by_type[policy.policy_type].sort(
                    key=lambda p: max(rule.priority for rule in p.rules) if p.rules else 0,
                    reverse=True
                )
            
            # Clear evaluation cache
            self.evaluation_cache.clear()
            
            self.logger.info(f"Updated policy {policy_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating policy: {e}")
            return False
    
    async def evaluate_policies(self, policy_type: PolicyType,
                              context: Dict[str, Any]) -> List[PolicyEvaluation]:
        """        Evaluate policies for given context.
        
        Args:
            policy_type: Type of policies to evaluate
            context: Evaluation context
            
        Returns:
            List of policy evaluations
        """        try:
            start_time = datetime.now()
            evaluations = []
            
            # Check evaluation cache
            cache_key = self._generate_cache_key(policy_type, context)
            if cache_key in self.evaluation_cache:
                cached_eval = self.evaluation_cache[cache_key]
                if (start_time - cached_eval.evaluation_time).total_seconds() < self.cache_ttl:
                    self.stats['cache_hits'] += 1
                    return [cached_eval]
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(policy_type, context)
            
            # Evaluate each policy
            for policy in applicable_policies:
                if not policy.enabled:
                    continue
                
                evaluation = await self._evaluate_policy(policy, context)
                if evaluation:
                    evaluations.append(evaluation)
                    
                    # Cache the evaluation
                    self.evaluation_cache[cache_key] = evaluation
                    
                    # If action is definitive, stop evaluation
                    if evaluation.action in [PolicyAction.ALLOW, PolicyAction.DENY]:
                        break
            
            # Update statistics
            self.stats['total_evaluations'] += 1
            if evaluations:
                self.stats['policy_hits'] += 1
            
            evaluation_time = (datetime.now() - start_time).total_seconds()
            self.stats['evaluation_time_total'] += evaluation_time
            
            return evaluations
            
        except Exception as e:
            self.logger.error(f"Error evaluating policies: {e}")
            return []
    
    async def _get_applicable_policies(self, policy_type: PolicyType,
                                     context: Dict[str, Any]) -> List[CachePolicy]:
        """Get policies applicable to the context."""        try:
            applicable = []
            
            with self.lock:
                policies = self.policies_by_type[policy_type]
            
            for policy in policies:
                if await self._is_policy_applicable(policy, context):
                    applicable.append(policy)
            
            return applicable
            
        except Exception as e:
            self.logger.error(f"Error getting applicable policies: {e}")
            return []
    
    async def _is_policy_applicable(self, policy: CachePolicy,
                                  context: Dict[str, Any]) -> bool:
        """Check if policy is applicable to context."""        try:
            # Check scope
            if policy.scope == PolicyScope.GLOBAL:
                return True
            
            elif policy.scope == PolicyScope.NAMESPACE:
                namespace = context.get('namespace', '')
                return namespace == policy.scope_pattern
            
            elif policy.scope == PolicyScope.KEY_PATTERN:
                key = context.get('key', '')
                return self._match_pattern(key, policy.scope_pattern)
            
            elif policy.scope == PolicyScope.USER:
                user_id = context.get('user_id', '')
                return user_id == policy.scope_pattern
            
            elif policy.scope == PolicyScope.SESSION:
                session_id = context.get('session_id', '')
                return session_id == policy.scope_pattern
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking policy applicability: {e}")
            return False
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """Match text against pattern."""        try:
            # Support wildcards and regex
            if '*' in pattern or '?' in pattern:
                # Convert wildcard to regex
                regex_pattern = pattern.replace('*', '.*').replace('?', '.')
                return bool(re.match(regex_pattern, text))
            elif pattern.startswith('regex:'):
                regex_pattern = pattern[6:]  # Remove 'regex:' prefix
                return bool(re.match(regex_pattern, text))
            else:
                return text == pattern
                
        except Exception:
            return False
    
    async def _evaluate_policy(self, policy: CachePolicy,
                             context: Dict[str, Any]) -> Optional[PolicyEvaluation]:
        """Evaluate single policy against context."""        try:
            # Evaluate rules in priority order
            for rule in sorted(policy.rules, key=lambda r: r.priority, reverse=True):
                if not rule.enabled:
                    continue
                
                if await self._evaluate_rule(rule, context):
                    return PolicyEvaluation(
                        policy_id=policy.policy_id,
                        rule_id=rule.rule_id,
                        action=rule.action,
                        allowed=rule.action == PolicyAction.ALLOW,
                        reason=f"Rule '{rule.name}' matched",
                        parameters=rule.action_parameters
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error evaluating policy: {e}")
            return None
    
    async def _evaluate_rule(self, rule: PolicyRule,
                           context: Dict[str, Any]) -> bool:
        """Evaluate rule conditions."""        try:
            # All conditions must be true (AND logic)
            for condition in rule.conditions:
                if not await self._evaluate_condition(condition, context):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule: {e}")
            return False
    
    async def _evaluate_condition(self, condition: PolicyCondition,
                                context: Dict[str, Any]) -> bool:
        """Evaluate single condition."""        try:
            # Get field value from context
            field_value = context.get(condition.field)
            
            if field_value is None:
                return False
            
            # Get evaluator function
            evaluator = self.condition_evaluators.get(condition.operator)
            if not evaluator:
                self.logger.warning(f"Unknown condition operator: {condition.operator}")
                return False
            
            return evaluator(field_value, condition.value, condition.case_sensitive)
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _evaluate_equals(self, field_value: Any, condition_value: Any,
                        case_sensitive: bool) -> bool:
        """Evaluate equals condition."""        if isinstance(field_value, str) and isinstance(condition_value, str):
            if not case_sensitive:
                return field_value.lower() == condition_value.lower()
        return field_value == condition_value
    
    def _evaluate_not_equals(self, field_value: Any, condition_value: Any,
                           case_sensitive: bool) -> bool:
        """Evaluate not equals condition."""        return not self._evaluate_equals(field_value, condition_value, case_sensitive)
    
    def _evaluate_greater_than(self, field_value: Any, condition_value: Any,
                             case_sensitive: bool) -> bool:
        """Evaluate greater than condition."""        try:
            return float(field_value) > float(condition_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_than(self, field_value: Any, condition_value: Any,
                          case_sensitive: bool) -> bool:
        """Evaluate less than condition."""        try:
            return float(field_value) < float(condition_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_contains(self, field_value: Any, condition_value: Any,
                         case_sensitive: bool) -> bool:
        """Evaluate contains condition."""        try:
            field_str = str(field_value)
            condition_str = str(condition_value)
            
            if not case_sensitive:
                field_str = field_str.lower()
                condition_str = condition_str.lower()
            
            return condition_str in field_str
        except Exception:
            return False
    
    def _evaluate_regex_match(self, field_value: Any, condition_value: Any,
                            case_sensitive: bool) -> bool:
        """Evaluate regex match condition."""        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            return bool(re.search(str(condition_value), str(field_value), flags))
        except Exception:
            return False
    
    def _evaluate_in_list(self, field_value: Any, condition_value: Any,
                        case_sensitive: bool) -> bool:
        """Evaluate in list condition."""        try:
            if not isinstance(condition_value, list):
                return False
            
            if isinstance(field_value, str) and not case_sensitive:
                field_value = field_value.lower()
                condition_value = [str(v).lower() for v in condition_value]
            
            return field_value in condition_value
        except Exception:
            return False
    
    def _evaluate_not_in_list(self, field_value: Any, condition_value: Any,
                            case_sensitive: bool) -> bool:
        """Evaluate not in list condition."""        return not self._evaluate_in_list(field_value, condition_value, case_sensitive)
    
    def _generate_cache_key(self, policy_type: PolicyType,
                          context: Dict[str, Any]) -> str:
        """Generate cache key for evaluation."""        try:
            # Create deterministic key from policy type and context
            key_parts = [policy_type.value]
            
            # Sort context items for consistent key generation
            for k, v in sorted(context.items()):
                key_parts.append(f"{k}:{v}")
            
            return "|".join(key_parts)
            
        except Exception:
            return f"{policy_type.value}:unknown"
    
    async def get_policy_stats(self) -> Dict[str, Any]:
        """Get policy engine statistics."""        try:
            with self.lock:
                policy_counts = {}
                for policy_type in PolicyType:
                    policy_counts[policy_type.value] = len(self.policies_by_type[policy_type])
                
                total_policies = len(self.policies)
                total_rules = sum(len(p.rules) for p in self.policies.values())
                
                avg_evaluation_time = (
                    self.stats['evaluation_time_total'] / self.stats['total_evaluations']
                    if self.stats['total_evaluations'] > 0 else 0
                )
                
                cache_hit_rate = (
                    self.stats['cache_hits'] / self.stats['total_evaluations']
                    if self.stats['total_evaluations'] > 0 else 0
                )
                
                return {
                    'total_policies': total_policies,
                    'total_rules': total_rules,
                    'policies_by_type': policy_counts,
                    'evaluation_stats': {
                        'total_evaluations': self.stats['total_evaluations'],
                        'policy_hits': self.stats['policy_hits'],
                        'cache_hits': self.stats['cache_hits'],
                        'cache_hit_rate': cache_hit_rate,
                        'average_evaluation_time_ms': avg_evaluation_time * 1000
                    },
                    'cache_size': len(self.evaluation_cache)
                }
            
        except Exception as e:
            self.logger.error(f"Error getting policy stats: {e}")
            return {}
    
    async def export_policies(self) -> Dict[str, Any]:
        """Export all policies to dictionary."""        try:
            with self.lock:
                policies_data = {}
                
                for policy_id, policy in self.policies.items():
                    policies_data[policy_id] = {
                        'policy_id': policy.policy_id,
                        'name': policy.name,
                        'description': policy.description,
                        'policy_type': policy.policy_type.value,
                        'scope': policy.scope.value,
                        'scope_pattern': policy.scope_pattern,
                        'enabled': policy.enabled,
                        'created_at': policy.created_at.isoformat(),
                        'updated_at': policy.updated_at.isoformat(),
                        'metadata': policy.metadata,
                        'rules': [
                            {
                                'rule_id': rule.rule_id,
                                'name': rule.name,
                                'description': rule.description,
                                'action': rule.action.value,
                                'action_parameters': rule.action_parameters,
                                'priority': rule.priority,
                                'enabled': rule.enabled,
                                'conditions': [
                                    {
                                        'field': cond.field,
                                        'operator': cond.operator.value,
                                        'value': cond.value,
                                        'case_sensitive': cond.case_sensitive
                                    }
                                    for cond in rule.conditions
                                ]
                            }
                            for rule in policy.rules
                        ]
                    }
                
                return {
                    'policies': policies_data,
                    'export_timestamp': datetime.now().isoformat(),
                    'total_policies': len(policies_data)
                }
            
        except Exception as e:
            self.logger.error(f"Error exporting policies: {e}")
            return {}
    
    async def import_policies(self, policies_data: Dict[str, Any],
                            overwrite_existing: bool = False) -> Tuple[int, int]:
        """        Import policies from dictionary.
        
        Returns:
            Tuple of (imported_count, error_count)
        """        try:
            imported_count = 0
            error_count = 0
            
            policies_dict = policies_data.get('policies', {})
            
            for policy_id, policy_data in policies_dict.items():
                try:
                    # Check if policy exists
                    if policy_id in self.policies and not overwrite_existing:
                        continue
                    
                    # Create policy rules
                    rules = []
                    for rule_data in policy_data.get('rules', []):
                        conditions = []
                        for cond_data in rule_data.get('conditions', []):
                            condition = PolicyCondition(
                                field=cond_data['field'],
                                operator=ConditionOperator(cond_data['operator']),
                                value=cond_data['value'],
                                case_sensitive=cond_data.get('case_sensitive', True)
                            )
                            conditions.append(condition)
                        
                        rule = PolicyRule(
                            rule_id=rule_data['rule_id'],
                            name=rule_data['name'],
                            description=rule_data['description'],
                            conditions=conditions,
                            action=PolicyAction(rule_data['action']),
                            action_parameters=rule_data.get('action_parameters', {}),
                            priority=rule_data.get('priority', 100),
                            enabled=rule_data.get('enabled', True)
                        )
                        rules.append(rule)
                    
                    # Create policy
                    policy = CachePolicy(
                        policy_id=policy_data['policy_id'],
                        name=policy_data['name'],
                        description=policy_data['description'],
                        policy_type=PolicyType(policy_data['policy_type']),
                        scope=PolicyScope(policy_data['scope']),
                        scope_pattern=policy_data['scope_pattern'],
                        rules=rules,
                        enabled=policy_data.get('enabled', True),
                        metadata=policy_data.get('metadata', {})
                    )
                    
                    # Add policy
                    success = await self.add_policy(policy)
                    if success:
                        imported_count += 1
                    else:
                        error_count += 1
                
                except Exception as e:
                    self.logger.error(f"Error importing policy {policy_id}: {e}")
                    error_count += 1
            
            self.logger.info(f"Imported {imported_count} policies, {error_count} errors")
            return imported_count, error_count
            
        except Exception as e:
            self.logger.error(f"Error importing policies: {e}")
            return 0, 1

class PolicyTemplates:
    """Pre-defined policy templates for common use cases."""    
    @staticmethod
    def create_size_limit_policy(max_size_mb: int, namespace: str = "*") -> CachePolicy:
        """Create policy to limit cache entry size."""        rule = PolicyRule(
            rule_id=generate_uuid(),
            name="Size Limit Rule",
            description=f"Deny cache entries larger than {max_size_mb}MB",
            conditions=[
                PolicyCondition(
                    field="size_bytes",
                    operator=ConditionOperator.GREATER_THAN,
                    value=max_size_mb * 1024 * 1024
                )
            ],
            action=PolicyAction.DENY,
            priority=100
        )
        
        return CachePolicy(
            policy_id=generate_uuid(),
            name=f"Size Limit Policy ({max_size_mb}MB)",
            description=f"Limit cache entry size to {max_size_mb}MB",
            policy_type=PolicyType.STORAGE,
            scope=PolicyScope.KEY_PATTERN,
            scope_pattern=namespace,
            rules=[rule]
        )
    
    @staticmethod
    def create_ttl_policy(ttl_seconds: int, key_pattern: str) -> CachePolicy:
        """Create TTL-based retention policy."""        rule = PolicyRule(
            rule_id=generate_uuid(),
            name="TTL Rule",
            description=f"Set TTL to {ttl_seconds} seconds",
            conditions=[],  # No conditions - always apply
            action=PolicyAction.MODIFY,
            action_parameters={'ttl_seconds': ttl_seconds},
            priority=100
        )
        
        return CachePolicy(
            policy_id=generate_uuid(),
            name=f"TTL Policy ({ttl_seconds}s)",
            description=f"Set TTL to {ttl_seconds} seconds for matching keys",
            policy_type=PolicyType.RETENTION,
            scope=PolicyScope.KEY_PATTERN,
            scope_pattern=key_pattern,
            rules=[rule]
        )
    
    @staticmethod
    def create_access_control_policy(allowed_users: List[str],
                                   key_pattern: str) -> CachePolicy:
        """Create user access control policy."""        rule = PolicyRule(
            rule_id=generate_uuid(),
            name="Access Control Rule",
            description="Allow access only to specified users",
            conditions=[
                PolicyCondition(
                    field="user_id",
                    operator=ConditionOperator.IN_LIST,
                    value=allowed_users
                )
            ],
            action=PolicyAction.ALLOW,
            priority=100
        )
        
        deny_rule = PolicyRule(
            rule_id=generate_uuid(),
            name="Access Deny Rule",
            description="Deny access to unauthorized users",
            conditions=[],  # No conditions - catch-all
            action=PolicyAction.DENY,
            priority=50
        )
        
        return CachePolicy(
            policy_id=generate_uuid(),
            name="Access Control Policy",
            description=f"Control access to keys matching {key_pattern}",
            policy_type=PolicyType.ACCESS,
            scope=PolicyScope.KEY_PATTERN,
            scope_pattern=key_pattern,
            rules=[rule, deny_rule]
        )
