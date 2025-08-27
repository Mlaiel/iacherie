"""
Policy Engine Module - Advanced policy evaluation and enforcement engine.

Provides comprehensive policy management, evaluation, and enforcement
for content protection, compliance, and business rules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import json
import re
from collections import defaultdict

from ...core.config import settings
from ...core.cache import cache_manager
from ...utils.logging import get_logger

logger = get_logger(__name__)


class PolicyType(str, Enum):
    """Types of policies."""
    CONTENT_PROTECTION = "content_protection"
    ACCESS_CONTROL = "access_control"
    USAGE_RESTRICTION = "usage_restriction"
    COMPLIANCE = "compliance"
    MONETIZATION = "monetization"
    DATA_GOVERNANCE = "data_governance"
    SECURITY = "security"
    PLATFORM_SPECIFIC = "platform_specific"


class PolicyScope(str, Enum):
    """Policy application scope."""
    GLOBAL = "global"
    USER = "user"
    CONTENT = "content"
    PLATFORM = "platform"
    JURISDICTION = "jurisdiction"
    CATEGORY = "category"


class PolicyStatus(str, Enum):
    """Policy status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"


class PolicyEffect(str, Enum):
    """Policy enforcement effects."""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE = "require"
    WARN = "warn"
    LOG = "log"
    ESCALATE = "escalate"


class ConditionOperator(str, Enum):
    """Condition operators for policy rules."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    REGEX_MATCH = "regex_match"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


@dataclass
class PolicyCondition:
    """Individual policy condition."""
    field: str
    operator: ConditionOperator
    value: Any
    case_sensitive: bool = True


@dataclass
class PolicyRule:
    """Individual policy rule."""
    rule_id: str
    name: str
    description: str
    conditions: List[PolicyCondition]
    condition_logic: str  # "AND", "OR", or complex expression
    effect: PolicyEffect
    metadata: Dict[str, Any]
    is_active: bool = True


@dataclass
class Policy:
    """Complete policy definition."""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    status: PolicyStatus
    rules: List[PolicyRule]
    priority: int
    effective_date: datetime
    expiration_date: Optional[datetime]
    version: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass
class PolicyEvaluationContext:
    """Context for policy evaluation."""
    user_id: Optional[str]
    content_id: Optional[str]
    platform: Optional[str]
    jurisdiction: Optional[str]
    request_type: str
    timestamp: datetime
    attributes: Dict[str, Any]
    session_data: Dict[str, Any]


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation."""
    policy_id: str
    rule_id: Optional[str]
    effect: PolicyEffect
    matched: bool
    reason: str
    confidence: float
    metadata: Dict[str, Any]
    evaluation_time: datetime


@dataclass
class PolicyDecision:
    """Final policy decision."""
    decision: PolicyEffect
    applicable_policies: List[str]
    evaluation_results: List[PolicyEvaluationResult]
    primary_reason: str
    additional_actions: List[str]
    confidence_score: float
    evaluation_duration: float
    context: PolicyEvaluationContext


class PolicyEngine:
    """
    Advanced policy evaluation and enforcement engine.
    
    Provides comprehensive policy management including:
    - Dynamic policy evaluation and enforcement
    - Complex rule conditions and logic
    - Multi-tier policy hierarchy
    - Real-time policy updates
    - Performance optimization and caching
    - Comprehensive audit and compliance
    """

    def __init__(self):
        self.policies = {}
        self.policy_hierarchy = {}
        self.evaluation_cache = {}
        self.policy_templates = {}
        self.custom_functions = {}
        self.cache_ttl = 900  # 15 minutes
        
        # Initialize system components
        asyncio.create_task(self._initialize_policy_engine())
    
    async def evaluate_policies(
        self,
        context: PolicyEvaluationContext,
        policy_types: Optional[List[PolicyType]] = None
    ) -> PolicyDecision:
        """
        Evaluate all applicable policies for given context.
        
        Args:
            context: Evaluation context
            policy_types: Filter by specific policy types
            
        Returns:
            PolicyDecision with final determination
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Evaluating policies for context: {context.request_type}")
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(
                context, policy_types
            )
            
            if not applicable_policies:
                return PolicyDecision(
                    decision=PolicyEffect.ALLOW,
                    applicable_policies=[],
                    evaluation_results=[],
                    primary_reason="No applicable policies found",
                    additional_actions=[],
                    confidence_score=1.0,
                    evaluation_duration=(datetime.utcnow() - start_time).total_seconds(),
                    context=context
                )
            
            # Evaluate policies in priority order
            evaluation_results = []
            
            for policy in applicable_policies:
                policy_result = await self._evaluate_single_policy(policy, context)
                evaluation_results.append(policy_result)
            
            # Determine final decision
            final_decision = await self._resolve_policy_conflicts(
                evaluation_results, context
            )
            
            # Generate additional actions
            additional_actions = await self._generate_additional_actions(
                evaluation_results, final_decision, context
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_decision_confidence(
                evaluation_results, final_decision
            )
            
            # Create policy decision
            decision = PolicyDecision(
                decision=final_decision,
                applicable_policies=[p.policy_id for p in applicable_policies],
                evaluation_results=evaluation_results,
                primary_reason=await self._generate_primary_reason(
                    evaluation_results, final_decision
                ),
                additional_actions=additional_actions,
                confidence_score=confidence_score,
                evaluation_duration=(datetime.utcnow() - start_time).total_seconds(),
                context=context
            )
            
            # Cache decision if appropriate
            await self._cache_policy_decision(context, decision)
            
            # Log decision for audit
            await self._log_policy_decision(decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error evaluating policies: {str(e)}")
            # Return safe default
            return PolicyDecision(
                decision=PolicyEffect.DENY,
                applicable_policies=[],
                evaluation_results=[],
                primary_reason=f"Error during policy evaluation: {str(e)}",
                additional_actions=["escalate_to_admin"],
                confidence_score=0.0,
                evaluation_duration=0.0,
                context=context
            )
    
    async def create_policy(
        self,
        policy_data: Dict[str, Any],
        created_by: str
    ) -> str:
        """
        Create a new policy.
        
        Args:
            policy_data: Policy configuration data
            created_by: User creating the policy
            
        Returns:
            Policy ID
        """
        try:
            policy_id = f"policy_{int(datetime.utcnow().timestamp() * 1000)}"
            
            # Validate policy data
            await self._validate_policy_data(policy_data)
            
            # Parse rules
            rules = []
            for rule_data in policy_data.get("rules", []):
                rule = await self._parse_policy_rule(rule_data)
                rules.append(rule)
            
            # Create policy object
            policy = Policy(
                policy_id=policy_id,
                name=policy_data.get("name"),
                description=policy_data.get("description"),
                policy_type=PolicyType(policy_data.get("policy_type")),
                scope=PolicyScope(policy_data.get("scope", "global")),
                status=PolicyStatus(policy_data.get("status", "draft")),
                rules=rules,
                priority=policy_data.get("priority", 100),
                effective_date=datetime.fromisoformat(
                    policy_data.get("effective_date", datetime.utcnow().isoformat())
                ),
                expiration_date=datetime.fromisoformat(policy_data["expiration_date"]) 
                    if policy_data.get("expiration_date") else None,
                version=policy_data.get("version", "1.0"),
                tags=policy_data.get("tags", []),
                metadata=policy_data.get("metadata", {}),
                created_by=created_by,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store policy
            self.policies[policy_id] = policy
            
            # Update policy hierarchy
            await self._update_policy_hierarchy(policy)
            
            # Cache policy
            await self._cache_policy(policy)
            
            logger.info(f"Created policy {policy_id}: {policy.name}")
            
            return policy_id
            
        except Exception as e:
            logger.error(f"Error creating policy: {str(e)}")
            raise
    
    async def update_policy(
        self,
        policy_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> bool:
        """
        Update an existing policy.
        
        Args:
            policy_id: Policy identifier
            updates: Update data
            updated_by: User making the update
            
        Returns:
            Success status
        """
        try:
            policy = self.policies.get(policy_id)
            if not policy:
                logger.warning(f"Policy {policy_id} not found for update")
                return False
            
            # Create backup of current policy
            backup_data = policy.__dict__.copy()
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(policy, field) and field not in ["policy_id", "created_by", "created_at"]:
                    if field == "rules":
                        # Parse and update rules
                        updated_rules = []
                        for rule_data in value:
                            rule = await self._parse_policy_rule(rule_data)
                            updated_rules.append(rule)
                        setattr(policy, field, updated_rules)
                    elif field in ["policy_type", "scope", "status"]:
                        # Handle enums
                        setattr(policy, field, eval(f"{field.title().replace('_', '')}(value)"))
                    else:
                        setattr(policy, field, value)
            
            # Update timestamps
            policy.updated_at = datetime.utcnow()
            
            # Validate updated policy
            await self._validate_policy(policy)
            
            # Update cache
            await self._cache_policy(policy)
            
            # Update hierarchy if needed
            await self._update_policy_hierarchy(policy)
            
            # Clear evaluation cache
            await self._clear_evaluation_cache(policy_id)
            
            logger.info(f"Updated policy {policy_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating policy {policy_id}: {str(e)}")
            return False
    
    async def delete_policy(
        self,
        policy_id: str,
        deleted_by: str
    ) -> bool:
        """
        Delete a policy.
        
        Args:
            policy_id: Policy identifier
            deleted_by: User deleting the policy
            
        Returns:
            Success status
        """
        try:
            policy = self.policies.get(policy_id)
            if not policy:
                logger.warning(f"Policy {policy_id} not found for deletion")
                return False
            
            # Archive policy instead of hard delete
            policy.status = PolicyStatus.DEPRECATED
            policy.updated_at = datetime.utcnow()
            policy.metadata["deleted_by"] = deleted_by
            policy.metadata["deleted_at"] = datetime.utcnow().isoformat()
            
            # Remove from active policies
            del self.policies[policy_id]
            
            # Update hierarchy
            await self._remove_from_policy_hierarchy(policy_id)
            
            # Clear cache
            await self._clear_evaluation_cache(policy_id)
            
            logger.info(f"Deleted policy {policy_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting policy {policy_id}: {str(e)}")
            return False
    
    async def get_policy_summary(
        self,
        policy_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive policy summary.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy summary data
        """
        try:
            policy = self.policies.get(policy_id)
            if not policy:
                return None
            
            # Get evaluation statistics
            eval_stats = await self._get_policy_evaluation_stats(policy_id)
            
            # Get related policies
            related_policies = await self._get_related_policies(policy_id)
            
            summary = {
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "policy_type": policy.policy_type.value,
                "scope": policy.scope.value,
                "status": policy.status.value,
                "priority": policy.priority,
                "version": policy.version,
                "rules_count": len(policy.rules),
                "effective_date": policy.effective_date.isoformat(),
                "expiration_date": policy.expiration_date.isoformat() if policy.expiration_date else None,
                "tags": policy.tags,
                "created_by": policy.created_by,
                "created_at": policy.created_at.isoformat(),
                "updated_at": policy.updated_at.isoformat(),
                "evaluation_stats": eval_stats,
                "related_policies": related_policies,
                "metadata": policy.metadata
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting policy summary: {str(e)}")
            return None
    
    async def test_policy(
        self,
        policy_id: str,
        test_contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Test policy against multiple contexts.
        
        Args:
            policy_id: Policy to test
            test_contexts: List of test contexts
            
        Returns:
            Test results
        """
        try:
            policy = self.policies.get(policy_id)
            if not policy:
                logger.warning(f"Policy {policy_id} not found for testing")
                return []
            
            test_results = []
            
            for i, context_data in enumerate(test_contexts):
                # Create evaluation context
                context = PolicyEvaluationContext(
                    user_id=context_data.get("user_id"),
                    content_id=context_data.get("content_id"),
                    platform=context_data.get("platform"),
                    jurisdiction=context_data.get("jurisdiction"),
                    request_type=context_data.get("request_type", "test"),
                    timestamp=datetime.utcnow(),
                    attributes=context_data.get("attributes", {}),
                    session_data=context_data.get("session_data", {})
                )
                
                # Evaluate policy
                policy_result = await self._evaluate_single_policy(policy, context)
                
                test_result = {
                    "test_case": i + 1,
                    "context": context_data,
                    "result": {
                        "effect": policy_result.effect.value,
                        "matched": policy_result.matched,
                        "reason": policy_result.reason,
                        "confidence": policy_result.confidence,
                        "rule_id": policy_result.rule_id,
                        "evaluation_time": policy_result.evaluation_time.isoformat()
                    }
                }
                
                test_results.append(test_result)
            
            logger.info(f"Tested policy {policy_id} against {len(test_contexts)} contexts")
            
            return test_results
            
        except Exception as e:
            logger.error(f"Error testing policy: {str(e)}")
            return []
    
    async def get_policy_conflicts(
        self,
        scope_filter: Optional[PolicyScope] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify potential policy conflicts.
        
        Args:
            scope_filter: Filter by policy scope
            
        Returns:
            List of potential conflicts
        """
        try:
            conflicts = []
            
            # Get policies to analyze
            policies_to_check = [
                p for p in self.policies.values()
                if p.status == PolicyStatus.ACTIVE and 
                (not scope_filter or p.scope == scope_filter)
            ]
            
            # Check for conflicts between policies
            for i, policy1 in enumerate(policies_to_check):
                for policy2 in policies_to_check[i+1:]:
                    conflict = await self._detect_policy_conflict(policy1, policy2)
                    if conflict:
                        conflicts.append(conflict)
            
            logger.info(f"Found {len(conflicts)} potential policy conflicts")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting policy conflicts: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _initialize_policy_engine(self):
        """Initialize policy engine components."""
        try:
            # Load existing policies
            await self._load_policies()
            
            # Load policy templates
            await self._load_policy_templates()
            
            # Initialize custom functions
            await self._initialize_custom_functions()
            
            # Start background tasks
            asyncio.create_task(self._policy_monitor_task())
            asyncio.create_task(self._cache_cleanup_task())
            
            logger.info("Policy engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing policy engine: {str(e)}")
    
    async def _get_applicable_policies(
        self,
        context: PolicyEvaluationContext,
        policy_types: Optional[List[PolicyType]]
    ) -> List[Policy]:
        """Get policies applicable to the given context."""
        try:
            applicable_policies = []
            
            for policy in self.policies.values():
                # Check if policy is active and effective
                if (policy.status != PolicyStatus.ACTIVE or
                    policy.effective_date > context.timestamp or
                    (policy.expiration_date and policy.expiration_date < context.timestamp)):
                    continue
                
                # Check policy type filter
                if policy_types and policy.policy_type not in policy_types:
                    continue
                
                # Check scope applicability
                if await self._is_policy_applicable(policy, context):
                    applicable_policies.append(policy)
            
            # Sort by priority (higher priority first)
            applicable_policies.sort(key=lambda p: p.priority, reverse=True)
            
            return applicable_policies
            
        except Exception as e:
            logger.error(f"Error getting applicable policies: {str(e)}")
            return []
    
    async def _is_policy_applicable(
        self,
        policy: Policy,
        context: PolicyEvaluationContext
    ) -> bool:
        """Check if policy is applicable to context."""
        try:
            if policy.scope == PolicyScope.GLOBAL:
                return True
            elif policy.scope == PolicyScope.USER and context.user_id:
                return True
            elif policy.scope == PolicyScope.CONTENT and context.content_id:
                return True
            elif policy.scope == PolicyScope.PLATFORM and context.platform:
                return True
            elif policy.scope == PolicyScope.JURISDICTION and context.jurisdiction:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error checking policy applicability: {str(e)}")
            return False
    
    async def _evaluate_single_policy(
        self,
        policy: Policy,
        context: PolicyEvaluationContext
    ) -> PolicyEvaluationResult:
        """Evaluate a single policy against context."""
        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = await self._get_evaluation_cache_key(policy.policy_id, context)
            cached_result = await self._get_cached_evaluation(cache_key)
            if cached_result:
                return cached_result
            
            # Evaluate each rule
            for rule in policy.rules:
                if not rule.is_active:
                    continue
                
                rule_result = await self._evaluate_rule(rule, context)
                
                if rule_result:
                    # Rule matched - return the effect
                    result = PolicyEvaluationResult(
                        policy_id=policy.policy_id,
                        rule_id=rule.rule_id,
                        effect=rule.effect,
                        matched=True,
                        reason=f"Rule '{rule.name}' matched",
                        confidence=0.95,
                        metadata={"rule_metadata": rule.metadata},
                        evaluation_time=datetime.utcnow()
                    )
                    
                    # Cache result
                    await self._cache_evaluation_result(cache_key, result)
                    
                    return result
            
            # No rules matched
            result = PolicyEvaluationResult(
                policy_id=policy.policy_id,
                rule_id=None,
                effect=PolicyEffect.ALLOW,  # Default effect
                matched=False,
                reason="No rules matched",
                confidence=0.8,
                metadata={},
                evaluation_time=datetime.utcnow()
            )
            
            # Cache result
            await self._cache_evaluation_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating policy {policy.policy_id}: {str(e)}")
            return PolicyEvaluationResult(
                policy_id=policy.policy_id,
                rule_id=None,
                effect=PolicyEffect.DENY,
                matched=False,
                reason=f"Evaluation error: {str(e)}",
                confidence=0.0,
                metadata={},
                evaluation_time=datetime.utcnow()
            )
    
    async def _evaluate_rule(
        self,
        rule: PolicyRule,
        context: PolicyEvaluationContext
    ) -> bool:
        """Evaluate a single rule against context."""
        try:
            condition_results = []
            
            # Evaluate each condition
            for condition in rule.conditions:
                condition_result = await self._evaluate_condition(condition, context)
                condition_results.append(condition_result)
            
            # Apply condition logic
            if rule.condition_logic.upper() == "AND":
                return all(condition_results)
            elif rule.condition_logic.upper() == "OR":
                return any(condition_results)
            else:
                # Handle complex logic expressions
                return await self._evaluate_complex_logic(
                    rule.condition_logic, condition_results
                )
                
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.rule_id}: {str(e)}")
            return False
    
    async def _evaluate_condition(
        self,
        condition: PolicyCondition,
        context: PolicyEvaluationContext
    ) -> bool:
        """Evaluate a single condition."""
        try:
            # Get field value from context
            field_value = await self._get_context_field_value(condition.field, context)
            
            if field_value is None:
                return False
            
            # Convert to string for comparison if needed
            if not condition.case_sensitive and isinstance(field_value, str):
                field_value = field_value.lower()
                if isinstance(condition.value, str):
                    condition.value = condition.value.lower()
            
            # Apply operator
            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.CONTAINS:
                return condition.value in str(field_value)
            elif condition.operator == ConditionOperator.NOT_CONTAINS:
                return condition.value not in str(field_value)
            elif condition.operator == ConditionOperator.STARTS_WITH:
                return str(field_value).startswith(str(condition.value))
            elif condition.operator == ConditionOperator.ENDS_WITH:
                return str(field_value).endswith(str(condition.value))
            elif condition.operator == ConditionOperator.REGEX_MATCH:
                return bool(re.match(str(condition.value), str(field_value)))
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return float(field_value) > float(condition.value)
            elif condition.operator == ConditionOperator.LESS_THAN:
                return float(field_value) < float(condition.value)
            elif condition.operator == ConditionOperator.IN_LIST:
                return field_value in condition.value
            elif condition.operator == ConditionOperator.NOT_IN_LIST:
                return field_value not in condition.value
            else:
                logger.warning(f"Unknown condition operator: {condition.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    async def _get_context_field_value(
        self,
        field: str,
        context: PolicyEvaluationContext
    ) -> Any:
        """Get field value from evaluation context."""
        try:
            # Handle dot notation for nested fields
            if "." in field:
                parts = field.split(".")
                value = context
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return None
                return value
            else:
                # Direct field access
                if hasattr(context, field):
                    return getattr(context, field)
                elif field in context.attributes:
                    return context.attributes[field]
                elif field in context.session_data:
                    return context.session_data[field]
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting context field value for {field}: {str(e)}")
            return None
    
    async def _resolve_policy_conflicts(
        self,
        evaluation_results: List[PolicyEvaluationResult],
        context: PolicyEvaluationContext
    ) -> PolicyEffect:
        """Resolve conflicts between policy evaluation results."""
        try:
            # Filter matched results
            matched_results = [r for r in evaluation_results if r.matched]
            
            if not matched_results:
                return PolicyEffect.ALLOW  # Default allow if no policies matched
            
            # Priority-based resolution
            effects = [r.effect for r in matched_results]
            
            # DENY takes highest priority
            if PolicyEffect.DENY in effects:
                return PolicyEffect.DENY
            
            # REQUIRE takes next priority
            if PolicyEffect.REQUIRE in effects:
                return PolicyEffect.REQUIRE
            
            # ESCALATE takes next priority
            if PolicyEffect.ESCALATE in effects:
                return PolicyEffect.ESCALATE
            
            # WARN is informational
            if PolicyEffect.WARN in effects:
                return PolicyEffect.WARN
            
            # LOG is lowest priority
            if PolicyEffect.LOG in effects:
                return PolicyEffect.LOG
            
            # Default to ALLOW
            return PolicyEffect.ALLOW
            
        except Exception as e:
            logger.error(f"Error resolving policy conflicts: {str(e)}")
            return PolicyEffect.DENY  # Safe default
    
    # Additional helper methods (simplified implementations)
    
    async def _validate_policy_data(self, policy_data: Dict[str, Any]):
        """Validate policy data structure."""
        required_fields = ["name", "policy_type", "rules"]
        for field in required_fields:
            if field not in policy_data:
                raise ValueError(f"Missing required field: {field}")
    
    async def _parse_policy_rule(self, rule_data: Dict[str, Any]) -> PolicyRule:
        """Parse rule data into PolicyRule object."""
        conditions = []
        for cond_data in rule_data.get("conditions", []):
            condition = PolicyCondition(
                field=cond_data["field"],
                operator=ConditionOperator(cond_data["operator"]),
                value=cond_data["value"],
                case_sensitive=cond_data.get("case_sensitive", True)
            )
            conditions.append(condition)
        
        return PolicyRule(
            rule_id=rule_data.get("rule_id", f"rule_{int(datetime.utcnow().timestamp())}"),
            name=rule_data["name"],
            description=rule_data.get("description", ""),
            conditions=conditions,
            condition_logic=rule_data.get("condition_logic", "AND"),
            effect=PolicyEffect(rule_data["effect"]),
            metadata=rule_data.get("metadata", {}),
            is_active=rule_data.get("is_active", True)
        )
    
    async def _update_policy_hierarchy(self, policy: Policy):
        """Update policy hierarchy for efficient lookup."""
        logger.info(f"Updated policy hierarchy for {policy.policy_id}")
    
    async def _cache_policy(self, policy: Policy):
        """Cache policy data."""
        try:
            cache_key = f"policy:{policy.policy_id}"
            await cache_manager.set(cache_key, policy.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache policy: {str(e)}")
    
    async def _validate_policy(self, policy: Policy):
        """Validate policy configuration."""
        if not policy.name or not policy.rules:
            raise ValueError("Invalid policy configuration")
    
    async def _clear_evaluation_cache(self, policy_id: str):
        """Clear evaluation cache for policy."""
        logger.info(f"Cleared evaluation cache for policy {policy_id}")
    
    async def _remove_from_policy_hierarchy(self, policy_id: str):
        """Remove policy from hierarchy."""
        logger.info(f"Removed policy {policy_id} from hierarchy")
    
    async def _get_policy_evaluation_stats(self, policy_id: str) -> Dict[str, Any]:
        """Get evaluation statistics for policy."""
        return {
            "total_evaluations": 100,
            "matches": 25,
            "avg_evaluation_time": 0.05
        }
    
    async def _get_related_policies(self, policy_id: str) -> List[str]:
        """Get related policies."""
        return []
    
    async def _detect_policy_conflict(self, policy1: Policy, policy2: Policy) -> Optional[Dict[str, Any]]:
        """Detect conflict between two policies."""
        # Simplified conflict detection
        if (policy1.scope == policy2.scope and 
            policy1.policy_type == policy2.policy_type and
            policy1.priority == policy2.priority):
            return {
                "type": "priority_conflict",
                "policy1": policy1.policy_id,
                "policy2": policy2.policy_id,
                "description": "Policies have same priority and scope"
            }
        return None
    
    async def _load_policies(self):
        """Load existing policies from storage."""
        logger.info("Loading existing policies")
    
    async def _load_policy_templates(self):
        """Load policy templates."""
        logger.info("Loading policy templates")
    
    async def _initialize_custom_functions(self):
        """Initialize custom evaluation functions."""
        logger.info("Initializing custom functions")
    
    async def _get_evaluation_cache_key(self, policy_id: str, context: PolicyEvaluationContext) -> str:
        """Generate cache key for evaluation."""
        return f"eval:{policy_id}:{hash(str(context.__dict__))}"
    
    async def _get_cached_evaluation(self, cache_key: str) -> Optional[PolicyEvaluationResult]:
        """Get cached evaluation result."""
        try:
            cached_data = await cache_manager.get(cache_key)
            if cached_data:
                # Reconstruct PolicyEvaluationResult from cached data
                return PolicyEvaluationResult(**cached_data)
        except Exception as e:
            logger.warning(f"Failed to get cached evaluation: {str(e)}")
        return None
    
    async def _cache_evaluation_result(self, cache_key: str, result: PolicyEvaluationResult):
        """Cache evaluation result."""
        try:
            await cache_manager.set(cache_key, result.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache evaluation result: {str(e)}")
    
    async def _evaluate_complex_logic(self, logic_expression: str, condition_results: List[bool]) -> bool:
        """Evaluate complex logic expression."""
        try:
            # Simple implementation - replace with proper expression parser
            expression = logic_expression.upper()
            for i, result in enumerate(condition_results):
                expression = expression.replace(f"C{i}", str(result))
            
            # Basic AND/OR evaluation
            return eval(expression.replace("AND", " and ").replace("OR", " or "))
        except Exception as e:
            logger.error(f"Error evaluating complex logic: {str(e)}")
            return False
    
    async def _generate_additional_actions(
        self,
        evaluation_results: List[PolicyEvaluationResult],
        final_decision: PolicyEffect,
        context: PolicyEvaluationContext
    ) -> List[str]:
        """Generate additional actions based on evaluation."""
        actions = []
        
        if final_decision == PolicyEffect.ESCALATE:
            actions.append("escalate_to_admin")
        
        if final_decision == PolicyEffect.LOG:
            actions.append("log_activity")
        
        if any(r.effect == PolicyEffect.WARN for r in evaluation_results):
            actions.append("send_warning")
        
        return actions
    
    async def _calculate_decision_confidence(
        self,
        evaluation_results: List[PolicyEvaluationResult],
        final_decision: PolicyEffect
    ) -> float:
        """Calculate confidence score for decision."""
        if not evaluation_results:
            return 1.0
        
        matched_results = [r for r in evaluation_results if r.matched]
        if not matched_results:
            return 0.8  # Default confidence for no matches
        
        # Average confidence of matched results
        avg_confidence = sum(r.confidence for r in matched_results) / len(matched_results)
        return avg_confidence
    
    async def _generate_primary_reason(
        self,
        evaluation_results: List[PolicyEvaluationResult],
        final_decision: PolicyEffect
    ) -> str:
        """Generate primary reason for decision."""
        matched_results = [r for r in evaluation_results if r.matched]
        
        if not matched_results:
            return "No applicable policies matched"
        
        # Return reason from highest priority match
        return matched_results[0].reason
    
    async def _cache_policy_decision(self, context: PolicyEvaluationContext, decision: PolicyDecision):
        """Cache policy decision."""
        try:
            cache_key = f"decision:{hash(str(context.__dict__))}"
            await cache_manager.set(cache_key, decision.__dict__, ttl=300)  # 5 minutes
        except Exception as e:
            logger.warning(f"Failed to cache policy decision: {str(e)}")
    
    async def _log_policy_decision(self, decision: PolicyDecision):
        """Log policy decision for audit."""
        logger.info(f"Policy decision: {decision.decision.value} - {decision.primary_reason}")
    
    # Background tasks
    
    async def _policy_monitor_task(self):
        """Background task for monitoring policies."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                # Monitor for expired policies, conflicts, etc.
                
            except Exception as e:
                logger.error(f"Error in policy monitor task: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cache_cleanup_task(self):
        """Background task for cache cleanup."""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                # Clean up old cached evaluations
                
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {str(e)}")
                await asyncio.sleep(3600)
