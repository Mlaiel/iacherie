"""Security Access Controller - IA-Influencer-Agent Platform

Security-focused access controller with advanced security policies
and enforcement mechanisms for blockchain operations.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security clearance levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    security_level: SecurityLevel
    allowed_operations: List[str]
    time_restrictions: Dict[str, Any]
    location_restrictions: List[str]
    device_restrictions: List[str]
    multi_factor_required: bool
    audit_required: bool


class SecurityAccessController:
    """Security Access Control System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.access_history: List[Dict[str, Any]] = []
        
        self._init_default_policies()
    
    def _init_default_policies(self):
        """Initialize default security policies"""
        import uuid
        
        policies = [
            SecurityPolicy(
                policy_id=str(uuid.uuid4()),
                name="Public Access",
                security_level=SecurityLevel.PUBLIC,
                allowed_operations=["read", "view"],
                time_restrictions={},
                location_restrictions=[],
                device_restrictions=[],
                multi_factor_required=False,
                audit_required=False
            ),
            SecurityPolicy(
                policy_id=str(uuid.uuid4()),
                name="High Security Operations",
                security_level=SecurityLevel.SECRET,
                allowed_operations=["admin", "modify", "delete"],
                time_restrictions={"business_hours_only": True},
                location_restrictions=["trusted_networks"],
                device_restrictions=["managed_devices"],
                multi_factor_required=True,
                audit_required=True
            )
        ]
        
        for policy in policies:
            self.security_policies[policy.policy_id] = policy
    
    async def enforce_security_policy(
        self,
        user_id: str,
        operation: str,
        resource: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce security policy for operation"""
        try:
            # Determine required security level
            required_level = self._determine_security_level(operation, resource)
            
            # Check user clearance
            user_clearance = context.get("security_clearance", SecurityLevel.PUBLIC)
            
            if not self._has_sufficient_clearance(user_clearance, required_level):
                return {
                    "access_granted": False,
                    "reason": "Insufficient security clearance",
                    "required_level": required_level.value,
                    "user_level": user_clearance.value
                }
            
            # Find applicable policy
            applicable_policy = self._find_applicable_policy(required_level, operation)
            
            if not applicable_policy:
                return {
                    "access_granted": False,
                    "reason": "No applicable security policy found"
                }
            
            # Enforce policy constraints
            policy_check = await self._check_policy_constraints(
                applicable_policy, context
            )
            
            if not policy_check["passed"]:
                return {
                    "access_granted": False,
                    "reason": "Policy constraint violation",
                    "violations": policy_check["violations"]
                }
            
            # Log access
            await self._log_security_access(user_id, operation, resource, True)
            
            return {
                "access_granted": True,
                "policy_id": applicable_policy.policy_id,
                "security_level": required_level.value,
                "audit_required": applicable_policy.audit_required
            }
            
        except Exception as e:
            self.logger.error(f"Security policy enforcement failed: {e}")
            raise
    
    def _determine_security_level(self, operation: str, resource: str) -> SecurityLevel:
        """Determine required security level for operation"""
        high_security_operations = ["admin", "delete", "modify_security", "transfer_funds"]
        confidential_resources = ["private_keys", "user_data", "financial_data"]
        
        if operation in high_security_operations:
            return SecurityLevel.SECRET
        elif resource in confidential_resources:
            return SecurityLevel.CONFIDENTIAL
        else:
            return SecurityLevel.INTERNAL
    
    def _has_sufficient_clearance(
        self,
        user_clearance: SecurityLevel,
        required_level: SecurityLevel
    ) -> bool:
        """Check if user has sufficient security clearance"""
        clearance_hierarchy = {
            SecurityLevel.PUBLIC: 0,
            SecurityLevel.INTERNAL: 1,
            SecurityLevel.CONFIDENTIAL: 2,
            SecurityLevel.SECRET: 3,
            SecurityLevel.TOP_SECRET: 4
        }
        
        user_level = clearance_hierarchy.get(user_clearance, 0)
        required = clearance_hierarchy.get(required_level, 0)
        
        return user_level >= required
    
    def _find_applicable_policy(
        self,
        security_level: SecurityLevel,
        operation: str
    ) -> Optional[SecurityPolicy]:
        """Find applicable security policy"""
        for policy in self.security_policies.values():
            if (policy.security_level == security_level and
                operation in policy.allowed_operations):
                return policy
        
        return None
    
    async def _check_policy_constraints(
        self,
        policy: SecurityPolicy,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if context meets policy constraints"""
        violations = []
        
        # Check time restrictions
        if policy.time_restrictions.get("business_hours_only"):
            current_hour = datetime.utcnow().hour
            if not (9 <= current_hour <= 17):  # 9 AM to 5 PM
                violations.append("Outside business hours")
        
        # Check location restrictions
        if policy.location_restrictions:
            user_location = context.get("location", "unknown")
            if user_location not in policy.location_restrictions:
                violations.append(f"Untrusted location: {user_location}")
        
        # Check device restrictions
        if policy.device_restrictions:
            device_type = context.get("device_type", "unknown")
            if device_type not in policy.device_restrictions:
                violations.append(f"Unmanaged device: {device_type}")
        
        # Check multi-factor authentication
        if policy.multi_factor_required:
            mfa_verified = context.get("mfa_verified", False)
            if not mfa_verified:
                violations.append("Multi-factor authentication required")
        
        return {
            "passed": len(violations) == 0,
            "violations": violations
        }
    
    async def _log_security_access(
        self,
        user_id: str,
        operation: str,
        resource: str,
        granted: bool
    ):
        """Log security access attempt"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "resource": resource,
            "access_granted": granted
        }
        
        self.access_history.append(log_entry)
        
        # Keep only recent history
        if len(self.access_history) > 10000:
            self.access_history = self.access_history[-10000:]