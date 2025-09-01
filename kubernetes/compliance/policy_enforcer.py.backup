"""IA Influencer Agent - Policy Enforcement Engine
Automated policy enforcement and governance system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from fastapi import HTTPException, Request

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.policy import PolicyRule, PolicyViolation, PolicyExecution
from backend.models.user import User
from backend.core.cache import redis_client
from backend.utils.notifications import send_notification
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel

logger = get_logger(__name__)


class PolicyType(str, Enum):
    """Policy enforcement types"""
    ACCESS_CONTROL = "access_control"
    DATA_RETENTION = "data_retention"
    CONTENT_PROTECTION = "content_protection"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    RATE_LIMITING = "rate_limiting"
    RESOURCE_USAGE = "resource_usage"
    FINANCIAL = "financial"
    PRIVACY = "privacy"


class PolicyAction(str, Enum):
    """Policy enforcement actions"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK_USER = "block_user"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"
    ESCALATE = "escalate"
    QUARANTINE = "quarantine"
    TERMINATE = "terminate"


class PolicySeverity(str, Enum):
    """Policy violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyScope(str, Enum):
    """Policy enforcement scope"""
    USER = "user"
    ORGANIZATION = "organization"
    SYSTEM = "system"
    GLOBAL = "global"


@dataclass
class PolicyCondition:
    """Policy rule condition definition"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, regex
    value: Any
    data_type: str  # string, number, boolean, array, object


@dataclass
class PolicyRule:
    """Complete policy rule definition"""
    rule_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    conditions: List[PolicyCondition]
    action: PolicyAction
    severity: PolicySeverity
    enabled: bool
    priority: int
    metadata: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass
class PolicyEvaluationContext:
    """Context for policy evaluation"""
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    session_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None


@dataclass
class PolicyViolationDetails:
    """Policy violation details"""
    rule_id: str
    rule_name: str
    violation_type: str
    severity: PolicySeverity
    context: PolicyEvaluationContext
    violation_data: Dict[str, Any]
    remediation_suggestions: List[str]


class PolicyEnforcer:
    """Enterprise policy enforcement engine"""
    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.cache_ttl = settings.POLICY_CACHE_TTL
        self.enforcement_enabled = settings.POLICY_ENFORCEMENT_ENABLED
        self.async_enforcement = settings.POLICY_ASYNC_ENFORCEMENT
        
        # Policy evaluation cache
        self._policy_cache: Dict[str, List[PolicyRule]] = {}
        self._evaluation_cache: Dict[str, Dict[str, Any]] = {}
        
        # Built-in policy operators
        self.operators = {
            "eq": lambda a, b: a == b,
            "ne": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "in": lambda a, b: a in b if isinstance(b, (list, set, tuple)) else False,
            "not_in": lambda a, b: a not in b if isinstance(b, (list, set, tuple)) else True,
            "contains": lambda a, b: b in str(a) if isinstance(a, str) else False,
            "startswith": lambda a, b: str(a).startswith(str(b)),
            "endswith": lambda a, b: str(a).endswith(str(b)),
            "regex": lambda a, b: self._regex_match(a, b)
        }
        
        # Pre-defined policy rules for common scenarios
        self.default_policies = self._load_default_policies()
    
    async def evaluate_policies(
        self,
        policy_type: PolicyType,
        context: PolicyEvaluationContext
    ) -> Dict[str, Any]:
        """Evaluate all applicable policies for given context"""
        try:
            if not self.enforcement_enabled:
                return {"action": PolicyAction.ALLOW, "policies_evaluated": 0}
            
            # Get applicable policies
            policies = await self._get_applicable_policies(policy_type, context)
            
            if not policies:
                return {"action": PolicyAction.ALLOW, "policies_evaluated": 0}
            
            # Sort policies by priority (higher number = higher priority)
            policies.sort(key=lambda p: p.priority, reverse=True)
            
            evaluation_results = []
            violations = []
            final_action = PolicyAction.ALLOW
            
            # Evaluate each policy
            for policy in policies:
                try:
                    result = await self._evaluate_single_policy(policy, context)
                    evaluation_results.append(result)
                    
                    # Track violations
                    if result["violated"]:
                        violations.append(PolicyViolationDetails(
                            rule_id=policy.rule_id,
                            rule_name=policy.name,
                            violation_type=policy.policy_type.value,
                            severity=policy.severity,
                            context=context,
                            violation_data=result["details"],
                            remediation_suggestions=result.get("remediation", [])
                        ))
                        
                        # Update final action based on highest severity violation
                        if policy.action in [PolicyAction.DENY, PolicyAction.BLOCK_USER, PolicyAction.TERMINATE]:
                            final_action = policy.action
                            break  # Stop on blocking actions
                        elif policy.action == PolicyAction.THROTTLE and final_action == PolicyAction.ALLOW:
                            final_action = PolicyAction.THROTTLE
                        elif policy.action == PolicyAction.WARN and final_action == PolicyAction.ALLOW:
                            final_action = PolicyAction.WARN
                
                except Exception as e:
                    self.logger.error(f"Error evaluating policy {policy.rule_id}: {str(e)}")
                    continue
            
            # Log policy enforcement
            await self.audit_logger.log_audit_event(
                event_type="policy_enforcement",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO if final_action == PolicyAction.ALLOW else AuditLevel.WARNING,
                message=f"Policy evaluation completed: {final_action.value}",
                details={
                    "policy_type": policy_type.value,
                    "policies_evaluated": len(policies),
                    "violations_found": len(violations),
                    "final_action": final_action.value,
                    "evaluation_results": evaluation_results
                },
                user_id=context.user_id
            )
            
            # Process violations
            if violations:
                await self._process_policy_violations(violations, context)
            
            return {
                "action": final_action,
                "policies_evaluated": len(policies),
                "violations": len(violations),
                "details": evaluation_results,
                "violation_details": [asdict(v) for v in violations]
            }
            
        except Exception as e:
            self.logger.error(f"Error in policy evaluation: {str(e)}")
            # Fail-safe: allow action but log error
            return {"action": PolicyAction.ALLOW, "error": str(e)}
    
    async def enforce_access_control(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        request_data: Dict[str, Any] = None
    ) -> bool:
        """Enforce access control policies"""
        try:
            context = PolicyEvaluationContext(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                request_data=request_data or {},
                timestamp=datetime.utcnow()
            )
            
            result = await self.evaluate_policies(PolicyType.ACCESS_CONTROL, context)
            
            return result["action"] in [PolicyAction.ALLOW, PolicyAction.WARN]
            
        except Exception as e:
            self.logger.error(f"Error in access control enforcement: {str(e)}")
            return False  # Fail-secure
    
    async def enforce_rate_limiting(
        self,
        user_id: int,
        action: str,
        resource_type: str = None
    ) -> Dict[str, Any]:
        """Enforce rate limiting policies"""
        try:
            context = PolicyEvaluationContext(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                timestamp=datetime.utcnow()
            )
            
            result = await self.evaluate_policies(PolicyType.RATE_LIMITING, context)
            
            if result["action"] == PolicyAction.THROTTLE:
                # Implement throttling logic
                throttle_seconds = await self._calculate_throttle_delay(user_id, action)
                return {
                    "allowed": False,
                    "throttled": True,
                    "retry_after": throttle_seconds,
                    "message": "Rate limit exceeded"
                }
            
            return {
                "allowed": result["action"] == PolicyAction.ALLOW,
                "throttled": False,
                "violations": result.get("violations", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting enforcement: {str(e)}")
            return {"allowed": True, "error": str(e)}
    
    async def enforce_content_protection(
        self,
        user_id: int,
        content_type: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce content protection policies"""
        try:
            context = PolicyEvaluationContext(
                user_id=user_id,
                resource_type="content",
                action="upload",
                request_data={
                    "content_type": content_type,
                    **content_data
                },
                timestamp=datetime.utcnow()
            )
            
            result = await self.evaluate_policies(PolicyType.CONTENT_PROTECTION, context)
            
            return {
                "allowed": result["action"] in [PolicyAction.ALLOW, PolicyAction.WARN],
                "action": result["action"].value,
                "violations": result.get("violations", 0),
                "protection_required": result["action"] == PolicyAction.QUARANTINE,
                "details": result.get("violation_details", [])
            }
            
        except Exception as e:
            self.logger.error(f"Error in content protection enforcement: {str(e)}")
            return {"allowed": False, "error": str(e)}
    
    async def create_policy_rule(
        self,
        rule_definition: Dict[str, Any],
        created_by: str
    ) -> PolicyRule:
        """Create new policy rule"""
        try:
            # Validate rule definition
            await self._validate_policy_rule(rule_definition)
            
            # Create policy rule
            policy_rule = PolicyRule(
                rule_id=f"POL-{datetime.utcnow().strftime('%Y%m%d')}-{self._generate_rule_id()}",
                name=rule_definition["name"],
                description=rule_definition["description"],
                policy_type=PolicyType(rule_definition["policy_type"]),
                scope=PolicyScope(rule_definition["scope"]),
                conditions=[
                    PolicyCondition(**cond) for cond in rule_definition["conditions"]
                ],
                action=PolicyAction(rule_definition["action"]),
                severity=PolicySeverity(rule_definition["severity"]),
                enabled=rule_definition.get("enabled", True),
                priority=rule_definition.get("priority", 100),
                metadata=rule_definition.get("metadata", {}),
                created_by=created_by,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database
            async with get_db_session() as session:
                db_policy = PolicyRule(
                    rule_id=policy_rule.rule_id,
                    name=policy_rule.name,
                    description=policy_rule.description,
                    policy_type=policy_rule.policy_type.value,
                    scope=policy_rule.scope.value,
                    conditions=json.dumps([asdict(c) for c in policy_rule.conditions]),
                    action=policy_rule.action.value,
                    severity=policy_rule.severity.value,
                    enabled=policy_rule.enabled,
                    priority=policy_rule.priority,
                    metadata=json.dumps(policy_rule.metadata),
                    created_by=created_by,
                    created_at=policy_rule.created_at,
                    updated_at=policy_rule.updated_at
                )
                
                session.add(db_policy)
                await session.commit()
            
            # Clear policy cache
            await self._clear_policy_cache()
            
            # Log policy creation
            await self.audit_logger.log_audit_event(
                event_type="policy_created",
                category=AuditCategory.ADMIN_ACTION,
                level=AuditLevel.INFO,
                message=f"Policy rule created: {policy_rule.name}",
                details={
                    "rule_id": policy_rule.rule_id,
                    "policy_type": policy_rule.policy_type.value,
                    "action": policy_rule.action.value,
                    "created_by": created_by
                }
            )
            
            return policy_rule
            
        except Exception as e:
            self.logger.error(f"Error creating policy rule: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to create policy rule: {str(e)}")
    
    async def update_policy_rule(
        self,
        rule_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> PolicyRule:
        """Update existing policy rule"""
        try:
            async with get_db_session() as session:
                # Get existing rule
                result = await session.execute(
                    select(PolicyRule).where(PolicyRule.rule_id == rule_id)
                )
                db_policy = result.scalar_one_or_none()
                
                if not db_policy:
                    raise HTTPException(status_code=404, detail="Policy rule not found")
                
                # Update fields
                for field, value in updates.items():
                    if hasattr(db_policy, field):
                        setattr(db_policy, field, value)
                
                db_policy.updated_at = datetime.utcnow()
                await session.commit()
                
                # Clear cache
                await self._clear_policy_cache()
                
                # Log update
                await self.audit_logger.log_audit_event(
                    event_type="policy_updated",
                    category=AuditCategory.ADMIN_ACTION,
                    level=AuditLevel.INFO,
                    message=f"Policy rule updated: {rule_id}",
                    details={
                        "rule_id": rule_id,
                        "updates": updates,
                        "updated_by": updated_by
                    }
                )
                
                return db_policy
                
        except Exception as e:
            self.logger.error(f"Error updating policy rule: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update policy rule")
    
    async def _evaluate_single_policy(
        self,
        policy: PolicyRule,
        context: PolicyEvaluationContext
    ) -> Dict[str, Any]:
        """Evaluate single policy rule against context"""
        try:
            # Check if all conditions are met
            conditions_met = True
            condition_results = []
            
            for condition in policy.conditions:
                result = await self._evaluate_condition(condition, context)
                condition_results.append({
                    "condition": asdict(condition),
                    "result": result,
                    "context_value": self._extract_context_value(condition.field, context)
                })
                
                if not result:
                    conditions_met = False
                    break
            
            return {
                "policy_id": policy.rule_id,
                "policy_name": policy.name,
                "violated": conditions_met,
                "action": policy.action.value if conditions_met else "no_action",
                "severity": policy.severity.value if conditions_met else None,
                "details": {
                    "conditions_evaluated": len(policy.conditions),
                    "conditions_met": conditions_met,
                    "condition_results": condition_results
                },
                "remediation": self._get_remediation_suggestions(policy, context) if conditions_met else []
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating policy {policy.rule_id}: {str(e)}")
            return {
                "policy_id": policy.rule_id,
                "violated": False,
                "error": str(e)
            }
    
    async def _evaluate_condition(
        self,
        condition: PolicyCondition,
        context: PolicyEvaluationContext
    ) -> bool:
        """Evaluate single policy condition"""
        try:
            # Extract value from context
            context_value = self._extract_context_value(condition.field, context)
            
            # Handle null/missing values
            if context_value is None:
                return condition.operator in ["eq", "in"] and condition.value is None
            
            # Type conversion
            context_value = self._convert_value_type(context_value, condition.data_type)
            condition_value = self._convert_value_type(condition.value, condition.data_type)
            
            # Apply operator
            operator_func = self.operators.get(condition.operator)
            if not operator_func:
                self.logger.warning(f"Unknown operator: {condition.operator}")
                return False
            
            return operator_func(context_value, condition_value)
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    def _extract_context_value(self, field: str, context: PolicyEvaluationContext) -> Any:
        """Extract value from evaluation context using dot notation"""
        try:
            # Handle nested field access (e.g., "request_data.content_type")
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
            
        except Exception as e:
            self.logger.error(f"Error extracting context value for field {field}: {str(e)}")
            return None
    
    def _load_default_policies(self) -> List[PolicyRule]:
        """Load pre-defined default policy rules"""
        return [
            # Rate limiting for API calls
            PolicyRule(
                rule_id="POL-DEFAULT-001",
                name="API Rate Limiting",
                description="Limit API calls per user per hour",
                policy_type=PolicyType.RATE_LIMITING,
                scope=PolicyScope.USER,
                conditions=[
                    PolicyCondition("action", "eq", "api_call", "string"),
                    PolicyCondition("request_count_hour", "gt", 1000, "number")
                ],
                action=PolicyAction.THROTTLE,
                severity=PolicySeverity.MEDIUM,
                enabled=True,
                priority=100,
                metadata={"throttle_seconds": 3600},
                created_by="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            
            # Content size limits
            PolicyRule(
                rule_id="POL-DEFAULT-002", 
                name="Content Size Limit",
                description="Limit content upload size",
                policy_type=PolicyType.CONTENT_PROTECTION,
                scope=PolicyScope.GLOBAL,
                conditions=[
                    PolicyCondition("request_data.content_size", "gt", 100*1024*1024, "number")  # 100MB
                ],
                action=PolicyAction.DENY,
                severity=PolicySeverity.HIGH,
                enabled=True,
                priority=200,
                metadata={"max_size_mb": 100},
                created_by="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            
            # Suspicious login attempts
            PolicyRule(
                rule_id="POL-DEFAULT-003",
                name="Suspicious Login Detection",
                description="Detect suspicious login patterns",
                policy_type=PolicyType.SECURITY,
                scope=PolicyScope.USER,
                conditions=[
                    PolicyCondition("action", "eq", "login", "string"),
                    PolicyCondition("failed_attempts_hour", "gte", 5, "number")
                ],
                action=PolicyAction.BLOCK_USER,
                severity=PolicySeverity.CRITICAL,
                enabled=True,
                priority=500,
                metadata={"block_duration_minutes": 60},
                created_by="system",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]


# Export for use in other modules
__all__ = ["PolicyEnforcer", "PolicyType", "PolicyAction", "PolicySeverity", "PolicyScope", "PolicyEvaluationContext"]
