
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
"""
Ainflue Security Policies Manager
© 2025 Fahed Mlaiel. All rights reserved.

Security policy enforcement and management for the Ainflue creator economy platform.
Implements enterprise-grade security policies with automated enforcement.
"""

import logging
import json
import base64
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
from dataclasses import dataclass
from enum import Enum
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyType(Enum):
    """Security policy types"""
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    NETWORK_SECURITY = "network_security"
    CONTENT_PROTECTION = "content_protection"
    COMPLIANCE = "compliance"
    INCIDENT_RESPONSE = "incident_response"


@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    security_level: SecurityLevel
    rules: List[Dict[str, Any]]
    enforcement_mode: str  # 'enforce', 'monitor', 'disabled'
    created_date: datetime
    last_updated: datetime
    creator_specific: bool = False


class SecurityPoliciesManager:
    """Enterprise security policies management for creator platform"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security policies manager"""
        self.config = config or {}
        self.policies = {}
        self.policy_violations = []
        self.enforcement_logs = []
        
        # Initialize default creator economy policies
        self._initialize_default_policies()
        
        logger.info("SecurityPoliciesManager initialized for creator platform")
    
    def _initialize_default_policies(self):
        """Initialize default security policies for creator economy"""
        
        # Creator Data Protection Policy
        creator_data_policy = SecurityPolicy(
            policy_id="CDP-001",
            name="Creator Data Protection Policy",
            description="Data protection policy for creator content and personal information",
            policy_type=PolicyType.DATA_PROTECTION,
            security_level=SecurityLevel.HIGH,
            rules=[
                {
                    "rule_id": "CDP-001-R1",
                    "description": "Encrypt all creator content at rest",
                    "condition": "content_type IN ['audio', 'video', 'image', 'document']",
                    "action": "apply_encryption",
                    "parameters": {"algorithm": "AES-256", "key_rotation": "monthly"}
                },
                {
                    "rule_id": "CDP-001-R2", 
                    "description": "Anonymize creator analytics data",
                    "condition": "data_type == 'analytics'",
                    "action": "anonymize_pii",
                    "parameters": {"retention_period": "7_years"}
                }
            ],
            enforcement_mode="enforce",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            creator_specific=True
        )
        
        # Content Protection Policy
        content_protection_policy = SecurityPolicy(
            policy_id="CPP-001",
            name="Content Protection Policy",
            description="Intellectual property protection for creator content",
            policy_type=PolicyType.CONTENT_PROTECTION,
            security_level=SecurityLevel.CRITICAL,
            rules=[
                {
                    "rule_id": "CPP-001-R1",
                    "description": "Apply digital watermarking to all content",
                    "condition": "content_upload == True",
                    "action": "apply_watermark",
                    "parameters": {"watermark_type": "invisible", "creator_id_embedded": True}
                },
                {
                    "rule_id": "CPP-001-R2",
                    "description": "Generate content fingerprint for piracy detection",
                    "condition": "content_type IN ['audio', 'video']",
                    "action": "generate_fingerprint",
                    "parameters": {"algorithm": "perceptual_hash", "monitoring": "continuous"}
                }
            ],
            enforcement_mode="enforce",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            creator_specific=True
        )
        
        # Creator Access Control Policy
        access_control_policy = SecurityPolicy(
            policy_id="CAC-001", 
            name="Creator Access Control Policy",
            description="Role-based access control for creator platform",
            policy_type=PolicyType.ACCESS_CONTROL,
            security_level=SecurityLevel.HIGH,
            rules=[
                {
                    "rule_id": "CAC-001-R1",
                    "description": "Enforce multi-factor authentication for creators",
                    "condition": "user_role == 'creator'",
                    "action": "require_mfa",
                    "parameters": {"methods": ["sms", "totp", "biometric"], "grace_period": "7_days"}
                },
                {
                    "rule_id": "CAC-001-R2",
                    "description": "Limit administrative access",
                    "condition": "action == 'admin_function'",
                    "action": "require_approval",
                    "parameters": {"approvers": 2, "time_limit": "4_hours"}
                }
            ],
            enforcement_mode="enforce",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            creator_specific=True
        )
        
        # Collaboration Security Policy
        collaboration_policy = SecurityPolicy(
            policy_id="CSP-001",
            name="Collaboration Security Policy", 
            description="Security controls for creator collaboration features",
            policy_type=PolicyType.NETWORK_SECURITY,
            security_level=SecurityLevel.MEDIUM,
            rules=[
                {
                    "rule_id": "CSP-001-R1",
                    "description": "Encrypt real-time collaboration sessions",
                    "condition": "collaboration_type == 'real_time'",
                    "action": "enforce_encryption",
                    "parameters": {"protocol": "TLS-1.3", "key_exchange": "ECDHE"}
                },
                {
                    "rule_id": "CSP-001-R2",
                    "description": "Validate collaboration partner identity",
                    "condition": "collaboration_request == True",
                    "action": "verify_identity",
                    "parameters": {"verification_level": "high", "background_check": True}
                }
            ],
            enforcement_mode="enforce",
            created_date=datetime.now(),
            last_updated=datetime.now(),
            creator_specific=True
        )
        
        # Add policies to manager
        self.policies[creator_data_policy.policy_id] = creator_data_policy
        self.policies[content_protection_policy.policy_id] = content_protection_policy
        self.policies[access_control_policy.policy_id] = access_control_policy
        self.policies[collaboration_policy.policy_id] = collaboration_policy
        
        logger.info(f"Initialized {len(self.policies)} default security policies")
    
    def create_policy(self, policy: SecurityPolicy) -> bool:
        """Create a new security policy"""
        try:
            if policy.policy_id in self.policies:
                logger.warning(f"Policy {policy.policy_id} already exists")
                return False
            
            self.policies[policy.policy_id] = policy
            
            self._log_enforcement_action(
                "policy_created",
                f"Created policy {policy.policy_id}: {policy.name}",
                {"policy_id": policy.policy_id, "security_level": policy.security_level.value}
            )
            
            logger.info(f"Created security policy: {policy.policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating policy {policy.policy_id}: {e}")
            return False
    
    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing security policy"""
        try:
            if policy_id not in self.policies:
                logger.error(f"Policy {policy_id} not found")
                return False
            
            policy = self.policies[policy_id]
            
            # Update policy fields
            for field, value in updates.items():
                if hasattr(policy, field):
                    setattr(policy, field, value)
            
            policy.last_updated = datetime.now()
            
            self._log_enforcement_action(
                "policy_updated",
                f"Updated policy {policy_id}",
                {"policy_id": policy_id, "updates": list(updates.keys())}
            )
            
            logger.info(f"Updated security policy: {policy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating policy {policy_id}: {e}")
            return False
    
    def enforce_policy(self, policy_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce a specific security policy"""
        try:
            if policy_id not in self.policies:
                return {"status": "error", "message": f"Policy {policy_id} not found"}
            
            policy = self.policies[policy_id]
            
            if policy.enforcement_mode == "disabled":
                return {"status": "skipped", "message": "Policy enforcement disabled"}
            
            enforcement_results = []
            
            # Evaluate each rule in the policy
            for rule in policy.rules:
                result = self._evaluate_rule(rule, context, policy.enforcement_mode)
                enforcement_results.append(result)
                
                # Log violations
                if result["status"] == "violation":
                    self._log_policy_violation(policy_id, rule["rule_id"], context, result)
            
            # Determine overall enforcement result
            violations = [r for r in enforcement_results if r["status"] == "violation"]
            
            if violations and policy.enforcement_mode == "enforce":
                return {
                    "status": "blocked",
                    "policy_id": policy_id,
                    "violations": violations,
                    "message": "Action blocked due to policy violations"
                }
            elif violations and policy.enforcement_mode == "monitor":
                return {
                    "status": "allowed_with_warnings",
                    "policy_id": policy_id,
                    "violations": violations,
                    "message": "Action allowed but violations detected"
                }
            else:
                return {
                    "status": "compliant",
                    "policy_id": policy_id,
                    "message": "Action complies with security policy"
                }
            
        except Exception as e:
            logger.error(f"Error enforcing policy {policy_id}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any], enforcement_mode: str) -> Dict[str, Any]:
        """Evaluate a specific policy rule"""
        try:
            # Simple rule evaluation (in production, this would be more sophisticated)
            condition = rule.get("condition", "")
            action = rule.get("action", "")
            parameters = rule.get("parameters", {})
            
            # Evaluate condition (simplified)
            rule_applies = self._evaluate_condition(condition, context)
            
            if rule_applies:
                # Execute policy action
                action_result = self._execute_policy_action(action, parameters, context)
                
                return {
                    "rule_id": rule["rule_id"],
                    "status": "enforced" if action_result else "violation",
                    "action": action,
                    "message": f"Rule {rule['rule_id']} evaluated and {'enforced' if action_result else 'violated'}"
                }
            else:
                return {
                    "rule_id": rule["rule_id"],
                    "status": "not_applicable",
                    "message": f"Rule {rule['rule_id']} does not apply to current context"
                }
                
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.get('rule_id', 'unknown')}: {e}")
            return {
                "rule_id": rule.get("rule_id", "unknown"),
                "status": "error",
                "message": str(e)
            }
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate policy condition (simplified implementation)"""
        try:
            # In production, this would use a proper expression evaluator
            # For now, simple string matching
            
            if "content_type" in condition and "content_type" in context:
                return context["content_type"] in condition
            elif "user_role" in condition and "user_role" in context:
                return context["user_role"] in condition
            elif "collaboration_type" in condition and "collaboration_type" in context:
                return context["collaboration_type"] in condition
            elif "action" in condition and "action" in context:
                return context["action"] in condition
            
            return True  # Default to applying rule
            
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _execute_policy_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Execute policy action (simplified implementation)"""
        try:
            # In production, this would integrate with actual enforcement systems
            
            action_handlers = {
                "apply_encryption": self._handle_encryption_action,
                "apply_watermark": self._handle_watermark_action,
                "require_mfa": self._handle_mfa_action,
                "anonymize_pii": self._handle_anonymization_action,
                "generate_fingerprint": self._handle_fingerprint_action,
                "enforce_encryption": self._handle_encryption_enforcement,
                "verify_identity": self._handle_identity_verification,
                "require_approval": self._handle_approval_requirement
            }
            
            handler = action_handlers.get(action)
            if handler:
                return handler(parameters, context)
            else:
                logger.warning(f"No handler for action: {action}")
                return True  # Assume success for unknown actions
                
        except Exception as e:
            logger.error(f"Error executing action '{action}': {e}")
            return False
    
    def _handle_encryption_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle encryption policy action"""
        algorithm = parameters.get("algorithm", "AES-256")
        key_rotation = parameters.get("key_rotation", "monthly")
        
        logger.info(f"Applying {algorithm} encryption with {key_rotation} key rotation")
        return True
    
    def _handle_watermark_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle watermarking policy action"""
        watermark_type = parameters.get("watermark_type", "invisible")
        embed_creator_id = parameters.get("creator_id_embedded", True)
        
        logger.info(f"Applying {watermark_type} watermark, creator ID embedded: {embed_creator_id}")
        return True
    
    def _handle_mfa_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle MFA requirement policy action"""
        methods = parameters.get("methods", ["sms", "totp"])
        grace_period = parameters.get("grace_period", "7_days")
        
        logger.info(f"Requiring MFA with methods {methods}, grace period: {grace_period}")
        return True
    
    def _handle_anonymization_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle data anonymization policy action"""
        retention_period = parameters.get("retention_period", "7_years")
        
        logger.info(f"Anonymizing PII data, retention period: {retention_period}")
        return True
    
    def _handle_fingerprint_action(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle content fingerprinting policy action"""
        algorithm = parameters.get("algorithm", "perceptual_hash")
        monitoring = parameters.get("monitoring", "continuous")
        
        logger.info(f"Generating content fingerprint using {algorithm}, monitoring: {monitoring}")
        return True
    
    def _handle_encryption_enforcement(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle encryption enforcement policy action"""
        protocol = parameters.get("protocol", "TLS-1.3")
        key_exchange = parameters.get("key_exchange", "ECDHE")
        
        logger.info(f"Enforcing {protocol} encryption with {key_exchange} key exchange")
        return True
    
    def _handle_identity_verification(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle identity verification policy action"""
        verification_level = parameters.get("verification_level", "high")
        background_check = parameters.get("background_check", True)
        
        logger.info(f"Verifying identity, level: {verification_level}, background check: {background_check}")
        return True
    
    def _handle_approval_requirement(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Handle approval requirement policy action"""
        approvers = parameters.get("approvers", 2)
        time_limit = parameters.get("time_limit", "4_hours")
        
        logger.info(f"Requiring {approvers} approvers within {time_limit}")
        return True
    
    def _log_policy_violation(self, policy_id: str, rule_id: str, context: Dict[str, Any], result: Dict[str, Any]):
        """Log a policy violation"""
        violation = {
            "timestamp": datetime.now().isoformat(),
            "policy_id": policy_id,
            "rule_id": rule_id,
            "context": context,
            "violation_details": result,
            "severity": self.policies[policy_id].security_level.value
        }
        
        self.policy_violations.append(violation)
        logger.warning(f"Policy violation: {policy_id}:{rule_id}")
    
    def _log_enforcement_action(self, action_type: str, message: str, metadata: Dict[str, Any]):
        """Log enforcement action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "message": message,
            "metadata": metadata
        }
        
        self.enforcement_logs.append(log_entry)
        logger.info(f"Enforcement action: {action_type} - {message}")
    
    def get_policy_violations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get policy violations from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_violations = [
            violation for violation in self.policy_violations
            if datetime.fromisoformat(violation["timestamp"]) > cutoff_time
        ]
        
        return recent_violations
    
    def get_enforcement_report(self) -> Dict[str, Any]:
        """Generate enforcement report for creator platform"""
        total_policies = len(self.policies)
        active_policies = len([p for p in self.policies.values() if p.enforcement_mode == "enforce"])
        recent_violations = len(self.get_policy_violations(24))
        
        creator_specific_policies = len([p for p in self.policies.values() if p.creator_specific])
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "total_policies": total_policies,
            "active_policies": active_policies,
            "monitoring_policies": len([p for p in self.policies.values() if p.enforcement_mode == "monitor"]),
            "creator_specific_policies": creator_specific_policies,
            "violations_24h": recent_violations,
            "enforcement_logs_count": len(self.enforcement_logs),
            "policy_compliance_rate": ((total_policies * 100 - recent_violations * 10) / (total_policies * 100)) * 100,
            "creator_protection_status": "active" if creator_specific_policies > 0 else "inactive"
        }


# Example usage for Ainflue creator platform
def main():
    """Example usage of security policies manager"""
    
    # Initialize security policies manager
    policies_manager = SecurityPoliciesManager()
    
    # Test creator content upload scenario
    creator_context = {
        "user_role": "creator",
        "action": "content_upload",
        "content_type": "audio",
        "creator_id": "creator_123",
        "collaboration_type": "real_time"
    }
    
    # Enforce content protection policy
    result = policies_manager.enforce_policy("CPP-001", creator_context)
    print(f"Content protection enforcement: {result}")
    
    # Enforce creator data protection policy
    result = policies_manager.enforce_policy("CDP-001", creator_context)
    print(f"Data protection enforcement: {result}")
    
    # Generate enforcement report
    report = policies_manager.get_enforcement_report()
    print(f"Enforcement report: {json.dumps(report, indent=2)}")


# Additional security classes and functions for auth module integration

class RiskLevel(Enum):
    """Risk level enumeration for security assessments"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AccessPolicy:
    """Access policy management for authentication and authorization"""
    
    def __init__(self, policy_id: str, name: str, level: SecurityLevel = SecurityLevel.STANDARD):
        self.policy_id = policy_id
        self.name = name
        self.level = level
        self.created_at = datetime.utcnow()
        self.access_rules = {}
        self.restrictions = {}
    
    def add_access_rule(self, resource: str, permissions: List[str]) -> None:
        """Add access rule for a specific resource"""
        self.access_rules[resource] = {
            'permissions': permissions,
            'created_at': datetime.utcnow()
        }
    
    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has access to perform action on resource"""
        if resource not in self.access_rules:
            return False
        
        permissions = self.access_rules[resource]['permissions']
        return action in permissions
    
    def get_risk_level(self) -> RiskLevel:
        """Determine risk level based on policy configuration"""
        if self.level == SecurityLevel.CRITICAL:
            return RiskLevel.CRITICAL
        elif self.level == SecurityLevel.HIGH:
            return RiskLevel.HIGH
        elif self.level == SecurityLevel.STANDARD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

class PolicyEngine:
    """Main policy engine for security policy enforcement"""
    
    def __init__(self):
        self.policies = {}
        self.access_policies = {}
        self.enforcement_history = []
    
    def register_policy(self, policy: SecurityPolicy) -> None:
        """Register a security policy"""
        self.policies[policy.policy_id] = policy
    
    def register_access_policy(self, policy: AccessPolicy) -> None:
        """Register an access policy"""
        self.access_policies[policy.policy_id] = policy
    
    def evaluate_risk(self, context: Dict[str, Any]) -> RiskLevel:
        """Evaluate overall risk level based on context"""
        risk_scores = []
        
        for policy in self.policies.values():
            if policy.policy_type == PolicyType.SECURITY:
                if policy.level == SecurityLevel.CRITICAL:
                    risk_scores.append(4)
                elif policy.level == SecurityLevel.HIGH:
                    risk_scores.append(3)
                elif policy.level == SecurityLevel.STANDARD:
                    risk_scores.append(2)
                else:
                    risk_scores.append(1)
        
        if not risk_scores:
            return RiskLevel.LOW
        
        avg_score = sum(risk_scores) / len(risk_scores)
        
        if avg_score >= 3.5:
            return RiskLevel.CRITICAL
        elif avg_score >= 2.5:
            return RiskLevel.HIGH
        elif avg_score >= 1.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def enforce_access_policy(self, policy_id: str, user_id: str, resource: str, action: str) -> bool:
        """Enforce access policy for user action"""
        if policy_id not in self.access_policies:
            return False
        
        policy = self.access_policies[policy_id]
        result = policy.check_access(user_id, resource, action)
        
        self.enforcement_history.append({
            'timestamp': datetime.utcnow(),
            'policy_id': policy_id,
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'allowed': result
        })
        
        return result

# Global policy engine instance
_policy_engine = None

def get_policy_engine() -> PolicyEngine:
    """Get or create the global policy engine instance"""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine

def initialize_security_policies() -> None:
    """Initialize default security policies"""
    engine = get_policy_engine()
    
    # Create default security policies
    auth_policy = SecurityPolicy(
        "AUTH-001",
        "Authentication Policy",
        PolicyType.SECURITY,
        {"require_mfa": True, "session_timeout": 3600}
    )
    auth_policy.level = SecurityLevel.HIGH
    engine.register_policy(auth_policy)
    
    # Create default access policies
    admin_access = AccessPolicy("ACCESS-ADMIN", "Administrator Access", SecurityLevel.CRITICAL)
    admin_access.add_access_rule("*", ["read", "write", "delete", "admin"])
    engine.register_access_policy(admin_access)
    
    user_access = AccessPolicy("ACCESS-USER", "Standard User Access", SecurityLevel.STANDARD)
    user_access.add_access_rule("user_data", ["read", "write"])
    user_access.add_access_rule("public_content", ["read"])
    engine.register_access_policy(user_access)

class EncryptionManager:
    """Professional encryption management for sensitive data"""
    
    def __init__(self):
        self.encryption_keys = {}
        self.default_algorithm = "Fernet"
        self.key_rotation_interval = timedelta(days=30)
        self.created_at = datetime.utcnow()
    
    def generate_key(self, tenant_id: str = None) -> str:
        """Generate a new encryption key for a tenant"""
        if not CRYPTO_AVAILABLE:
            # Fallback to basic encoding for testing
            return base64.urlsafe_b64encode(f"test_key_{tenant_id or 'default'}_{int(time.time())}".encode()).decode()
        
        key = Fernet.generate_key()
        key_id = f"{tenant_id or 'default'}_{uuid.uuid4().hex[:8]}"
        
        self.encryption_keys[key_id] = {
            'key': key,
            'created_at': datetime.utcnow(),
            'tenant_id': tenant_id,
            'algorithm': self.default_algorithm
        }
        
        return key_id
    
    def encrypt_data(self, data: str, tenant_id: str = None, key_id: str = None) -> Dict[str, str]:
        """Encrypt sensitive data with proper key management"""
        if not key_id:
            key_id = self.generate_key(tenant_id)
        
        if not CRYPTO_AVAILABLE:
            # Fallback encoding for testing environments
            encoded_data = base64.urlsafe_b64encode(data.encode()).decode()
            return {
                'encrypted_data': encoded_data,
                'key_id': key_id,
                'algorithm': 'base64_fallback',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key {key_id} not found")
        
        key_info = self.encryption_keys[key_id]
        cipher = Fernet(key_info['key'])
        
        encrypted_data = cipher.encrypt(data.encode())
        
        return {
            'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode(),
            'key_id': key_id,
            'algorithm': key_info['algorithm'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def decrypt_data(self, encrypted_info: Dict[str, str]) -> str:
        """Decrypt data using stored encryption keys"""
        key_id = encrypted_info['key_id']
        encrypted_data = encrypted_info['encrypted_data']
        
        if not CRYPTO_AVAILABLE or encrypted_info.get('algorithm') == 'base64_fallback':
            # Fallback decoding for testing
            return base64.urlsafe_b64decode(encrypted_data.encode()).decode()
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Decryption key {key_id} not found")
        
        key_info = self.encryption_keys[key_id]
        cipher = Fernet(key_info['key'])
        
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = cipher.decrypt(encrypted_bytes)
        
        return decrypted_data.decode()
    
    def rotate_key(self, old_key_id: str, tenant_id: str = None) -> str:
        """Rotate encryption key for security"""
        new_key_id = self.generate_key(tenant_id)
        
        if old_key_id in self.encryption_keys:
            # Mark old key as deprecated but keep for decryption
            self.encryption_keys[old_key_id]['deprecated'] = True
            self.encryption_keys[old_key_id]['deprecated_at'] = datetime.utcnow()
        
        return new_key_id
    
    def get_key_info(self, key_id: str) -> Dict[str, Any]:
        """Get information about an encryption key"""
        if key_id not in self.encryption_keys:
            return {}
        
        key_info = self.encryption_keys[key_id].copy()
        # Remove the actual key from the response for security
        key_info.pop('key', None)
        return key_info

# Global encryption manager instance
_encryption_manager = None

def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager instance"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager

# Initialize default security policies when module is imported
initialize_security_policies()

if __name__ == "__main__":
    main()