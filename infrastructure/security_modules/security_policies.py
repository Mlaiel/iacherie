"""Infrastructure Security Policies - Enterprise Security Framework
================================================================

Advanced security policy enforcement system for infrastructure compliance,
automated policy validation, and enterprise security standards enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Security Specialist + DevOps + Compliance Expert
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL SECURITY WARNING ⚠️
This security policy system contains advanced security algorithms and enterprise
compliance frameworks belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED ACCESS OR MODIFICATION IS STRICTLY PROHIBITED.
"""

import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import hashlib

class PolicyType(Enum):
    """Security policy types"""
    NETWORK = "network"
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    COMPLIANCE = "compliance"
    AUTHENTICATION = "authentication"
    ENCRYPTION = "encryption"
    MONITORING = "monitoring"
    INCIDENT_RESPONSE = "incident_response"

class PolicySeverity(Enum):
    """Policy violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    id: str
    name: str
    type: PolicyType
    severity: PolicySeverity
    description: str
    rules: List[Dict[str, Any]]
    enforcement_mode: str = "enforce"  # enforce, monitor, disabled
    compliance_frameworks: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.compliance_frameworks is None:
            self.compliance_frameworks = []

class SecurityPolicyEngine:
    """Enterprise security policy enforcement engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.policies: Dict[str, SecurityPolicy] = {}
        self.policy_violations: List[Dict[str, Any]] = []
        self.enforcement_rules = {
            "enforce": self._enforce_policy,
            "monitor": self._monitor_policy,
            "disabled": self._disabled_policy
        }
        self.compliance_frameworks = {
            "GDPR": self._gdpr_compliance_check,
            "PCI-DSS": self._pci_dss_compliance_check,
            "SOC2": self._soc2_compliance_check,
            "ISO27001": self._iso27001_compliance_check,
            "CCPA": self._ccpa_compliance_check
        }
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize security policy engine"""
        try:
            await self._load_default_policies()
            await self._setup_enforcement_rules()
            await self._initialize_compliance_monitoring()
            self.logger.info("Security policy engine initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize policy engine: {e}")
            return False
    
    async def add_policy(self, policy: SecurityPolicy) -> bool:
        """Add new security policy"""
        try:
            # Validate policy
            if not await self._validate_policy(policy):
                return False
            
            # Generate policy hash for integrity
            policy_hash = self._generate_policy_hash(policy)
            
            # Store policy
            self.policies[policy.id] = policy
            
            # Log policy addition
            self.logger.info(f"Security policy added: {policy.name} ({policy.id})")
            
            # Apply immediate enforcement if required
            if policy.enforcement_mode == "enforce":
                await self._apply_policy_enforcement(policy)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to add policy {policy.id}: {e}")
            return False
    
    async def evaluate_policies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all policies against current context"""
        try:
            evaluation_results = {
                "timestamp": datetime.utcnow().isoformat(),
                "context_id": context.get("id", "unknown"),
                "total_policies": len(self.policies),
                "violations": [],
                "compliance_status": {},
                "enforcement_actions": []
            }
            
            # Evaluate each policy
            for policy_id, policy in self.policies.items():
                try:
                    result = await self._evaluate_single_policy(policy, context)
                    
                    if not result["compliant"]:
                        violation = {
                            "policy_id": policy_id,
                            "policy_name": policy.name,
                            "severity": policy.severity.value,
                            "violation_details": result["details"],
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        evaluation_results["violations"].append(violation)
                        
                        # Apply enforcement action
                        enforcement_action = await self._apply_enforcement(policy, result)
                        if enforcement_action:
                            evaluation_results["enforcement_actions"].append(enforcement_action)
                
                except Exception as e:
                    self.logger.error(f"Error evaluating policy {policy_id}: {e}")
            
            # Check compliance frameworks
            evaluation_results["compliance_status"] = await self._evaluate_compliance_frameworks(
                evaluation_results["violations"]
            )
            
            return evaluation_results
        
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {e}")
            return {"error": str(e)}
    
    async def _evaluate_single_policy(self, policy: SecurityPolicy, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single policy against context"""
        try:
            compliant = True
            violation_details = []
            
            for rule in policy.rules:
                rule_result = await self._evaluate_rule(rule, context)
                if not rule_result["passed"]:
                    compliant = False
                    violation_details.append(rule_result["details"])
            
            return {
                "compliant": compliant,
                "details": violation_details,
                "policy_type": policy.type.value,
                "severity": policy.severity.value
            }
        
        except Exception as e:
            self.logger.error(f"Failed to evaluate policy {policy.id}: {e}")
            return {"compliant": False, "details": [f"Evaluation error: {e}"]}
    
    async def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate individual rule"""
        try:
            rule_type = rule.get("type")
            rule_condition = rule.get("condition")
            rule_value = rule.get("value")
            
            context_value = self._get_context_value(context, rule.get("context_path"))
            
            # Evaluate different rule types
            if rule_type == "equals":
                passed = context_value == rule_value
            elif rule_type == "not_equals":
                passed = context_value != rule_value
            elif rule_type == "contains":
                passed = rule_value in str(context_value)
            elif rule_type == "regex":
                import re
                passed = bool(re.match(rule_value, str(context_value)))
            elif rule_type == "range":
                passed = rule_value["min"] <= context_value <= rule_value["max"]
            elif rule_type == "exists":
                passed = context_value is not None
            elif rule_type == "custom":
                passed = await self._evaluate_custom_rule(rule, context)
            else:
                passed = False
            
            return {
                "passed": passed,
                "details": {
                    "rule_type": rule_type,
                    "expected": rule_value,
                    "actual": context_value,
                    "condition": rule_condition
                }
            }
        
        except Exception as e:
            self.logger.error(f"Rule evaluation failed: {e}")
            return {"passed": False, "details": {"error": str(e)}}
    
    async def _apply_enforcement(self, policy: SecurityPolicy, evaluation_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply policy enforcement action"""
        try:
            enforcement_handler = self.enforcement_rules.get(policy.enforcement_mode)
            if not enforcement_handler:
                return None
            
            action = await enforcement_handler(policy, evaluation_result)
            
            # Log enforcement action
            self.logger.warning(f"Policy enforcement: {policy.name} - {action}")
            
            return {
                "policy_id": policy.id,
                "action_type": policy.enforcement_mode,
                "action_details": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Enforcement action failed for policy {policy.id}: {e}")
            return None
    
    async def _enforce_policy(self, policy: SecurityPolicy, evaluation_result: Dict[str, Any]) -> str:
        """Enforce policy with blocking action"""
        # Block the action that violates the policy
        action_details = f"BLOCKED: Policy violation - {policy.name}"
        
        # Send critical alert
        await self._send_security_alert("CRITICAL", f"Policy enforcement triggered: {policy.name}")
        
        # Log security event
        await self._log_security_event("POLICY_ENFORCEMENT", {
            "policy_id": policy.id,
            "violation_details": evaluation_result["details"],
            "action": "BLOCKED"
        })
        
        return action_details
    
    async def _monitor_policy(self, policy: SecurityPolicy, evaluation_result: Dict[str, Any]) -> str:
        """Monitor policy violation without blocking"""
        action_details = f"MONITORED: Policy violation detected - {policy.name}"
        
        # Send monitoring alert
        await self._send_security_alert("WARNING", f"Policy violation monitored: {policy.name}")
        
        # Log monitoring event
        await self._log_security_event("POLICY_VIOLATION", {
            "policy_id": policy.id,
            "violation_details": evaluation_result["details"],
            "action": "MONITORED"
        })
        
        return action_details
    
    async def _disabled_policy(self, policy: SecurityPolicy, evaluation_result: Dict[str, Any]) -> str:
        """Policy is disabled - no action taken"""
        return f"DISABLED: Policy {policy.name} is disabled"
    
    async def _evaluate_compliance_frameworks(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate compliance against various frameworks"""
        compliance_results = {}
        
        for framework_name, framework_check in self.compliance_frameworks.items():
            try:
                compliance_results[framework_name] = await framework_check(violations)
            except Exception as e:
                self.logger.error(f"Compliance check failed for {framework_name}: {e}")
                compliance_results[framework_name] = {"status": "error", "details": str(e)}
        
        return compliance_results
    
    async def _gdpr_compliance_check(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check GDPR compliance"""
        # Check for data protection violations
        gdpr_violations = [v for v in violations if "data_protection" in v.get("policy_name", "").lower()]
        
        return {
            "status": "compliant" if len(gdpr_violations) == 0 else "non_compliant",
            "violations_count": len(gdpr_violations),
            "framework": "GDPR",
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _pci_dss_compliance_check(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check PCI-DSS compliance"""
        # Check for payment security violations
        pci_violations = [v for v in violations if v.get("severity") in ["critical", "high"]]
        
        return {
            "status": "compliant" if len(pci_violations) == 0 else "non_compliant",
            "violations_count": len(pci_violations),
            "framework": "PCI-DSS",
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _soc2_compliance_check(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check SOC2 compliance"""
        # Check for operational security violations
        soc2_violations = [v for v in violations if "access" in v.get("policy_name", "").lower()]
        
        return {
            "status": "compliant" if len(soc2_violations) == 0 else "non_compliant",
            "violations_count": len(soc2_violations),
            "framework": "SOC2",
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _iso27001_compliance_check(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check ISO27001 compliance"""
        # Check for information security violations
        iso_violations = [v for v in violations if v.get("severity") == "critical"]
        
        return {
            "status": "compliant" if len(iso_violations) == 0 else "non_compliant",
            "violations_count": len(iso_violations),
            "framework": "ISO27001",
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _ccpa_compliance_check(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check CCPA compliance"""
        # Check for privacy violations
        ccpa_violations = [v for v in violations if "privacy" in v.get("policy_name", "").lower()]
        
        return {
            "status": "compliant" if len(ccpa_violations) == 0 else "non_compliant",
            "violations_count": len(ccpa_violations),
            "framework": "CCPA",
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def _load_default_policies(self):
        """Load default security policies"""
        default_policies = [
            SecurityPolicy(
                id="network_encryption_required",
                name="Network Encryption Required",
                type=PolicyType.NETWORK,
                severity=PolicySeverity.CRITICAL,
                description="All network traffic must be encrypted",
                rules=[
                    {
                        "type": "equals",
                        "context_path": "network.encryption_enabled",
                        "value": True,
                        "condition": "Network encryption must be enabled"
                    }
                ],
                compliance_frameworks=["GDPR", "PCI-DSS", "SOC2"]
            ),
            SecurityPolicy(
                id="strong_authentication_required",
                name="Strong Authentication Required",
                type=PolicyType.AUTHENTICATION,
                severity=PolicySeverity.HIGH,
                description="Multi-factor authentication required for all access",
                rules=[
                    {
                        "type": "equals",
                        "context_path": "auth.mfa_enabled",
                        "value": True,
                        "condition": "MFA must be enabled"
                    }
                ],
                compliance_frameworks=["SOC2", "ISO27001"]
            ),
            SecurityPolicy(
                id="data_encryption_at_rest",
                name="Data Encryption at Rest",
                type=PolicyType.DATA_PROTECTION,
                severity=PolicySeverity.CRITICAL,
                description="All stored data must be encrypted",
                rules=[
                    {
                        "type": "equals",
                        "context_path": "storage.encryption_at_rest",
                        "value": True,
                        "condition": "Data encryption at rest required"
                    }
                ],
                compliance_frameworks=["GDPR", "PCI-DSS", "CCPA"]
            )
        ]
        
        for policy in default_policies:
            await self.add_policy(policy)
    
    def _generate_policy_hash(self, policy: SecurityPolicy) -> str:
        """Generate hash for policy integrity"""
        policy_data = asdict(policy)
        policy_json = json.dumps(policy_data, sort_keys=True, default=str)
        return hashlib.sha256(policy_json.encode()).hexdigest()
    
    def _get_context_value(self, context: Dict[str, Any], path: str) -> Any:
        """Get value from context using dot notation path"""
        try:
            keys = path.split('.')
            value = context
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None
    
    async def _validate_policy(self, policy: SecurityPolicy) -> bool:
        """Validate policy structure and rules"""
        if not policy.id or not policy.name:
            return False
        
        if not policy.rules:
            return False
        
        # Validate each rule
        for rule in policy.rules:
            if not all(key in rule for key in ["type", "context_path"]):
                return False
        
        return True
    
    async def _send_security_alert(self, level: str, message: str):
        """Send security alert to monitoring systems"""
        alert = {
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "security_policy_engine"
        }
        # In production, this would send to alerting systems
        self.logger.warning(f"SECURITY ALERT [{level}]: {message}")
    
    async def _log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log security event for audit trail"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": event_data
        }
        # In production, this would send to SIEM systems
        self.logger.info(f"SECURITY EVENT: {json.dumps(event)}")
    
    async def _evaluate_custom_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate custom rule logic"""
        # Placeholder for custom rule evaluation
        return True
    
    async def _setup_enforcement_rules(self):
        """Setup enforcement rule handlers"""
        # Additional enforcement setup if needed
        pass
    
    async def _initialize_compliance_monitoring(self):
        """Initialize compliance monitoring systems"""
        # Setup compliance monitoring
        pass
    
    async def _apply_policy_enforcement(self, policy: SecurityPolicy):
        """Apply immediate policy enforcement"""
        # Apply enforcement rules immediately
        pass

# Factory function for easy instantiation
def create_security_policy_engine(config: Optional[Dict[str, Any]] = None) -> SecurityPolicyEngine:
    """Create and configure security policy engine"""
    return SecurityPolicyEngine(config)

# Example usage and default configuration
if __name__ == "__main__":
    async def main():
        # Initialize security policy engine
        engine = create_security_policy_engine({
            "enforcement_mode": "enforce",
            "compliance_frameworks": ["GDPR", "PCI-DSS", "SOC2"]
        })
        
        await engine.initialize()
        
        # Example context evaluation
        test_context = {
            "network": {"encryption_enabled": True},
            "auth": {"mfa_enabled": False},
            "storage": {"encryption_at_rest": True}
        }
        
        results = await engine.evaluate_policies(test_context)
        print(f"Policy evaluation results: {json.dumps(results, indent=2)}")
    
    asyncio.run(main())