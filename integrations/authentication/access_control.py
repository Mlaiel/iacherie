# -*- coding: utf-8 -*-
"""
IA Chérie Platform - Enterprise Access Control System
Advanced access control with policy-based authorization
Author: IA Chérie Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import time
from typing import Dict, List, Set, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading
import re
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class AccessDecision(Enum):
    """Access control decisions"""
    ALLOW = "allow"
    DENY = "deny"
    ABSTAIN = "abstain"

class PolicyType(Enum):
    """Policy types"""
    ROLE_BASED = "role_based"
    ATTRIBUTE_BASED = "attribute_based"
    RULE_BASED = "rule_based"
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"
    RESOURCE_BASED = "resource_based"

@dataclass
class AccessRequest:
    """Access request context"""
    user_id: str
    resource: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: Optional[str] = None
    
@dataclass
class AccessPolicy:
    """Access control policy"""
    id: str
    name: str
    policy_type: PolicyType
    rules: Dict[str, Any]
    priority: int = 100
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    description: str = ""

@dataclass
class AccessLog:
    """Access control log entry"""
    request_id: str
    user_id: str
    resource: str
    action: str
    decision: AccessDecision
    policies_evaluated: List[str]
    evaluation_time_ms: float
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""

class AccessControlSystem:
    """Enterprise Access Control System"""
    
    def __init__(self):
        """Initialize access control system"""
        self.policies: Dict[str, AccessPolicy] = {}
        self.access_logs: List[AccessLog] = []
        self.policy_cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=10)
        self._lock = threading.RLock()
        self._request_counter = 0
        
        # Policy evaluators
        self.policy_evaluators = {
            PolicyType.ROLE_BASED: self._evaluate_role_based_policy,
            PolicyType.ATTRIBUTE_BASED: self._evaluate_attribute_based_policy,
            PolicyType.RULE_BASED: self._evaluate_rule_based_policy,
            PolicyType.TIME_BASED: self._evaluate_time_based_policy,
            PolicyType.LOCATION_BASED: self._evaluate_location_based_policy,
            PolicyType.RESOURCE_BASED: self._evaluate_resource_based_policy
        }
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("🔐 Access Control System initialized successfully")
    
    def _initialize_default_policies(self):
        """Initialize default access control policies"""
        default_policies = [
            # Admin access policy
            AccessPolicy(
                id="admin_full_access",
                name="Administrator Full Access",
                policy_type=PolicyType.ROLE_BASED,
                rules={
                    "required_roles": ["admin", "super_admin"],
                    "resources": ["*"],
                    "actions": ["*"]
                },
                priority=10,
                description="Full access for administrators"
            ),
            
            # User self-access policy
            AccessPolicy(
                id="user_self_access",
                name="User Self Access",
                policy_type=PolicyType.ATTRIBUTE_BASED,
                rules={
                    "conditions": [
                        {
                            "attribute": "resource.owner_id",
                            "operator": "equals",
                            "value": "${user_id}"
                        }
                    ],
                    "actions": ["read", "update"]
                },
                priority=50,
                description="Users can access their own resources"
            ),
            
            # Business hours policy
            AccessPolicy(
                id="business_hours_only",
                name="Business Hours Access",
                policy_type=PolicyType.TIME_BASED,
                rules={
                    "time_ranges": [
                        {
                            "start_hour": 9,
                            "end_hour": 17,
                            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                        }
                    ],
                    "resources": ["admin/*", "system/*"],
                    "exceptions": ["emergency_access"]
                },
                priority=30,
                description="Restrict admin access to business hours"
            ),
            
            # Read-only for viewers
            AccessPolicy(
                id="viewer_read_only",
                name="Viewer Read Only Access",
                policy_type=PolicyType.ROLE_BASED,
                rules={
                    "required_roles": ["viewer"],
                    "actions": ["read", "list"],
                    "resources": ["content/*", "user/profile"]
                },
                priority=60,
                description="Read-only access for viewers"
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.id] = policy
        
        logger.info(f"🛡️ Initialized {len(default_policies)} default access policies")
    
    def create_policy(self, policy: AccessPolicy) -> bool:
        """Create new access policy"""
        try:
            with self._lock:
                if policy.id in self.policies:
                    logger.warning(f"⚠️ Policy {policy.id} already exists")
                    return False
                
                # Validate policy structure
                if not self._validate_policy(policy):
                    logger.error(f"❌ Invalid policy structure: {policy.id}")
                    return False
                
                self.policies[policy.id] = policy
                self._clear_policy_cache()
                
                logger.info(f"✅ Created access policy: {policy.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creating policy {policy.id}: {str(e)}")
            return False
    
    def _validate_policy(self, policy: AccessPolicy) -> bool:
        """Validate policy structure"""
        try:
            # Check required fields
            if not policy.id or not policy.name or not policy.rules:
                return False
            
            # Validate based on policy type
            if policy.policy_type == PolicyType.ROLE_BASED:
                return "required_roles" in policy.rules
            elif policy.policy_type == PolicyType.ATTRIBUTE_BASED:
                return "conditions" in policy.rules
            elif policy.policy_type == PolicyType.TIME_BASED:
                return "time_ranges" in policy.rules
            
            return True
            
        except Exception:
            return False
    
    def evaluate_access(self, request: AccessRequest) -> AccessDecision:
        """Evaluate access request against policies"""
        start_time = time.time()
        
        try:
            with self._lock:
                # Generate request ID if not provided
                if not request.request_id:
                    self._request_counter += 1
                    request.request_id = f"req_{self._request_counter}_{int(time.time())}"
                
                # Get applicable policies
                applicable_policies = self._get_applicable_policies(request)
                
                # Evaluate policies in priority order
                policies_evaluated = []
                final_decision = AccessDecision.DENY  # Default deny
                
                for policy in sorted(applicable_policies, key=lambda p: p.priority):
                    decision = self._evaluate_policy(policy, request)
                    policies_evaluated.append(policy.id)
                    
                    if decision == AccessDecision.ALLOW:
                        final_decision = AccessDecision.ALLOW
                        break
                    elif decision == AccessDecision.DENY:
                        final_decision = AccessDecision.DENY
                        break
                
                # Calculate evaluation time
                evaluation_time = (time.time() - start_time) * 1000
                
                # Log the access attempt
                self._log_access_attempt(request, final_decision, policies_evaluated, evaluation_time)
                
                logger.info(f"🔍 Access evaluation: {request.user_id} -> {request.resource}:{request.action} = {final_decision.value}")
                return final_decision
                
        except Exception as e:
            logger.error(f"❌ Error evaluating access: {str(e)}")
            return AccessDecision.DENY
    
    def _get_applicable_policies(self, request: AccessRequest) -> List[AccessPolicy]:
        """Get policies applicable to the request"""
        applicable = []
        
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            
            # Check if policy applies to this resource/action
            if self._policy_applies_to_request(policy, request):
                applicable.append(policy)
        
        return applicable
    
    def _policy_applies_to_request(self, policy: AccessPolicy, request: AccessRequest) -> bool:
        """Check if policy applies to request"""
        try:
            # Check resource patterns
            if "resources" in policy.rules:
                resource_patterns = policy.rules["resources"]
                if not self._matches_patterns(request.resource, resource_patterns):
                    return False
            
            # Check action patterns
            if "actions" in policy.rules:
                action_patterns = policy.rules["actions"]
                if not self._matches_patterns(request.action, action_patterns):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _matches_patterns(self, value: str, patterns: List[str]) -> bool:
        """Check if value matches any pattern"""
        for pattern in patterns:
            if pattern == "*" or value == pattern:
                return True
            
            # Wildcard matching
            if "*" in pattern:
                regex_pattern = pattern.replace("*", ".*")
                if re.match(f"^{regex_pattern}$", value):
                    return True
        
        return False
    
    def _evaluate_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate single policy against request"""
        try:
            evaluator = self.policy_evaluators.get(policy.policy_type)
            if evaluator:
                return evaluator(policy, request)
            else:
                logger.warning(f"⚠️ No evaluator for policy type: {policy.policy_type}")
                return AccessDecision.ABSTAIN
                
        except Exception as e:
            logger.error(f"❌ Error evaluating policy {policy.id}: {str(e)}")
            return AccessDecision.DENY
    
    def _evaluate_role_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate role-based policy"""
        try:
            required_roles = policy.rules.get("required_roles", [])
            user_roles = request.context.get("user_roles", [])
            
            # Check if user has any required role
            if any(role in user_roles for role in required_roles):
                return AccessDecision.ALLOW
            
            return AccessDecision.ABSTAIN
            
        except Exception:
            return AccessDecision.DENY
    
    def _evaluate_attribute_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate attribute-based policy"""
        try:
            conditions = policy.rules.get("conditions", [])
            
            for condition in conditions:
                if not self._evaluate_condition(condition, request):
                    return AccessDecision.ABSTAIN
            
            return AccessDecision.ALLOW
            
        except Exception:
            return AccessDecision.DENY
    
    def _evaluate_condition(self, condition: Dict[str, Any], request: AccessRequest) -> bool:
        """Evaluate single condition"""
        try:
            attribute = condition.get("attribute")
            operator = condition.get("operator")
            expected_value = condition.get("value")
            
            # Get actual value from request context
            actual_value = self._get_attribute_value(attribute, request)
            
            # Replace variables in expected value
            if isinstance(expected_value, str) and "${" in expected_value:
                expected_value = expected_value.replace("${user_id}", request.user_id)
            
            # Evaluate based on operator
            if operator == "equals":
                return actual_value == expected_value
            elif operator == "not_equals":
                return actual_value != expected_value
            elif operator == "contains":
                return expected_value in str(actual_value)
            elif operator == "in":
                return actual_value in expected_value
            
            return False
            
        except Exception:
            return False
    
    def _get_attribute_value(self, attribute: str, request: AccessRequest) -> Any:
        """Get attribute value from request context"""
        try:
            # Handle nested attributes like "resource.owner_id"
            parts = attribute.split(".")
            value = request.context
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _evaluate_rule_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate rule-based policy"""
        # Placeholder for custom rule evaluation
        return AccessDecision.ABSTAIN
    
    def _evaluate_time_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate time-based policy"""
        try:
            time_ranges = policy.rules.get("time_ranges", [])
            current_time = datetime.now()
            
            for time_range in time_ranges:
                if self._is_within_time_range(current_time, time_range):
                    return AccessDecision.ALLOW
            
            return AccessDecision.ABSTAIN
            
        except Exception:
            return AccessDecision.DENY
    
    def _is_within_time_range(self, current_time: datetime, time_range: Dict[str, Any]) -> bool:
        """Check if current time is within allowed range"""
        try:
            # Check day of week
            allowed_days = time_range.get("days", [])
            current_day = current_time.strftime("%A").lower()
            
            if allowed_days and current_day not in allowed_days:
                return False
            
            # Check hour range
            start_hour = time_range.get("start_hour", 0)
            end_hour = time_range.get("end_hour", 23)
            current_hour = current_time.hour
            
            return start_hour <= current_hour <= end_hour
            
        except Exception:
            return False
    
    def _evaluate_location_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate location-based policy"""
        # Placeholder for location-based evaluation
        return AccessDecision.ABSTAIN
    
    def _evaluate_resource_based_policy(self, policy: AccessPolicy, request: AccessRequest) -> AccessDecision:
        """Evaluate resource-based policy"""
        # Placeholder for resource-based evaluation
        return AccessDecision.ABSTAIN
    
    def _log_access_attempt(self, request: AccessRequest, decision: AccessDecision, 
                           policies_evaluated: List[str], evaluation_time: float):
        """Log access attempt"""
        try:
            log_entry = AccessLog(
                request_id=request.request_id,
                user_id=request.user_id,
                resource=request.resource,
                action=request.action,
                decision=decision,
                policies_evaluated=policies_evaluated,
                evaluation_time_ms=evaluation_time,
                context=request.context.copy()
            )
            
            self.access_logs.append(log_entry)
            
            # Keep only recent logs (last 1000)
            if len(self.access_logs) > 1000:
                self.access_logs = self.access_logs[-1000:]
                
        except Exception as e:
            logger.error(f"❌ Error logging access attempt: {str(e)}")
    
    def _clear_policy_cache(self):
        """Clear policy cache"""
        with self._lock:
            self.policy_cache.clear()
    
    def get_policy(self, policy_id: str) -> Optional[AccessPolicy]:
        """Get policy by ID"""
        return self.policies.get(policy_id)
    
    def update_policy(self, policy: AccessPolicy) -> bool:
        """Update existing policy"""
        try:
            with self._lock:
                if policy.id not in self.policies:
                    logger.error(f"❌ Policy {policy.id} does not exist")
                    return False
                
                if not self._validate_policy(policy):
                    logger.error(f"❌ Invalid policy structure: {policy.id}")
                    return False
                
                policy.updated_at = datetime.now()
                self.policies[policy.id] = policy
                self._clear_policy_cache()
                
                logger.info(f"✅ Updated policy: {policy.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating policy {policy.id}: {str(e)}")
            return False
    
    def delete_policy(self, policy_id: str) -> bool:
        """Delete policy"""
        try:
            with self._lock:
                if policy_id not in self.policies:
                    logger.error(f"❌ Policy {policy_id} does not exist")
                    return False
                
                del self.policies[policy_id]
                self._clear_policy_cache()
                
                logger.info(f"✅ Deleted policy: {policy_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error deleting policy {policy_id}: {str(e)}")
            return False
    
    def get_access_logs(self, user_id: Optional[str] = None, 
                       resource: Optional[str] = None, 
                       limit: int = 100) -> List[AccessLog]:
        """Get access logs with optional filtering"""
        try:
            logs = self.access_logs.copy()
            
            # Filter by user_id
            if user_id:
                logs = [log for log in logs if log.user_id == user_id]
            
            # Filter by resource
            if resource:
                logs = [log for log in logs if log.resource == resource]
            
            # Sort by timestamp (newest first) and limit
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting access logs: {str(e)}")
            return []
    
    def get_all_policies(self) -> Dict[str, AccessPolicy]:
        """Get all policies"""
        return self.policies.copy()

def require_permission(resource: str, action: str = "read"):
    """Decorator for permission-based access control"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would integrate with your authentication system
            # For now, it's a placeholder
            user_id = kwargs.get('user_id') or getattr(args[0] if args else None, 'user_id', None)
            
            if not user_id:
                raise PermissionError("User ID required for access control")
            
            # Create access request
            request = AccessRequest(
                user_id=user_id,
                resource=resource,
                action=action,
                context=kwargs.get('context', {})
            )
            
            # Evaluate access
            decision = access_control_system.evaluate_access(request)
            
            if decision != AccessDecision.ALLOW:
                raise PermissionError(f"Access denied to {resource}:{action}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Create global instance
access_control_system = AccessControlSystem()

# Export main classes and instance
__all__ = [
    'AccessControlSystem',
    'AccessRequest',
    'AccessPolicy',
    'AccessLog',
    'AccessDecision',
    'PolicyType',
    'require_permission',
    'access_control_system'
]