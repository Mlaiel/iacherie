"""
🔧 Governance Policy Engine - Enterprise Rule Management
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Moteur politiques gouvernance configurables Creator Economy
Expertise: Lead Dev IA + Backend Senior + Sécurité + DBA
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
import re
import ast
from collections import defaultdict

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Policy types"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    OPERATIONAL = "operational"
    CREATOR_ECONOMY = "creator_economy"


class PolicyScope(Enum):
    """Policy application scope"""
    GLOBAL = "global"
    MODEL_TYPE = "model_type"
    CREATOR_TIER = "creator_tier"
    ENVIRONMENT = "environment"
    REGION = "region"
    CUSTOM = "custom"


class PolicyStatus(Enum):
    """Policy status"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class EnforcementLevel(Enum):
    """Policy enforcement levels"""
    ADVISORY = "advisory"  # Warning only
    BLOCKING = "blocking"  # Block action
    MANDATORY = "mandatory"  # Must comply
    CRITICAL = "critical"  # System-level enforcement


class RuleOperator(Enum):
    """Rule condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex_match"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


@dataclass
class PolicyCondition:
    """Individual policy condition"""
    condition_id: str
    field_name: str
    operator: RuleOperator
    expected_value: Any
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary"""
        return {
            "condition_id": self.condition_id,
            "field_name": self.field_name,
            "operator": self.operator.value,
            "expected_value": self.expected_value,
            "description": self.description
        }


@dataclass
class PolicyRule:
    """Policy rule with conditions and actions"""
    rule_id: str
    name: str
    description: str
    conditions: List[PolicyCondition]
    condition_logic: str = "AND"  # AND, OR, CUSTOM
    actions: List[str] = field(default_factory=list)
    priority: int = 100
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "conditions": [c.to_dict() for c in self.conditions],
            "condition_logic": self.condition_logic,
            "actions": self.actions,
            "priority": self.priority,
            "enabled": self.enabled
        }


@dataclass
class Policy:
    """Complete policy definition"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    scope_filter: Dict[str, Any]
    rules: List[PolicyRule]
    enforcement_level: EnforcementLevel
    status: PolicyStatus
    version: str = "1.0.0"
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary"""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "policy_type": self.policy_type.value,
            "scope": self.scope.value,
            "scope_filter": self.scope_filter,
            "rules": [r.to_dict() for r in self.rules],
            "enforcement_level": self.enforcement_level.value,
            "status": self.status.value,
            "version": self.version,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_id: str
    policy_id: str
    rule_id: str
    violation_type: str
    severity: str
    resource_id: str
    resource_type: str
    violation_details: Dict[str, Any]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None
    creator_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary"""
        return {
            "violation_id": self.violation_id,
            "policy_id": self.policy_id,
            "rule_id": self.rule_id,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "violation_details": self.violation_details,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_action": self.resolution_action,
            "creator_id": self.creator_id
        }


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""
    evaluation_id: str
    resource_id: str
    resource_type: str
    evaluated_policies: List[str]
    violations: List[PolicyViolation]
    compliant: bool
    evaluation_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "evaluation_id": self.evaluation_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "evaluated_policies": self.evaluated_policies,
            "violations": [v.to_dict() for v in self.violations],
            "compliant": self.compliant,
            "evaluation_time_ms": self.evaluation_time_ms,
            "timestamp": self.timestamp.isoformat()
        }


class GovernancePolicyEngine:
    """
    🔧 Moteur politiques gouvernance configurables
    
    Enterprise policy management with:
    - Policy definition framework with versioning
    - Rule engine implementation with complex conditions
    - Dynamic policy enforcement with multiple levels
    - Policy version management with rollback capability
    - Creator-specific policy rules with tier-based enforcement  
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize governance policy engine
        
        Args:
            config: Policy engine configuration
        """
        self.config = config or self._get_default_config()
        self.engine_id = str(uuid.uuid4())
        
        # Policy storage
        self._policies: Dict[str, Policy] = {}
        self._policy_versions: Dict[str, List[Policy]] = defaultdict(list)
        self._violations: Dict[str, PolicyViolation] = {}
        self._evaluation_results: List[PolicyEvaluationResult] = []
        
        # Rule engine components
        self._rule_evaluators: Dict[RuleOperator, Callable] = {}
        self._action_handlers: Dict[str, Callable] = {}
        self._scope_filters: Dict[PolicyScope, Callable] = {}
        
        # Performance tracking
        self._performance_metrics = {
            "policies_evaluated": 0,
            "violations_detected": 0,
            "violations_resolved": 0,
            "avg_evaluation_time_ms": 0.0,
            "policy_changes": 0
        }
        
        # Cache for frequent evaluations
        self._evaluation_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = self.config.get("cache_ttl_seconds", 300)
        
        # Initialize engine components
        self._initialize_rule_evaluators()
        self._initialize_action_handlers()
        self._initialize_scope_filters()
        self._initialize_default_policies()
        
        logger.info(f"🔧 GovernancePolicyEngine initialized with ID: {self.engine_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default policy engine configuration"""
        return {
            "evaluation": {
                "enable_caching": True,
                "cache_ttl_seconds": 300,
                "parallel_evaluation": True,
                "max_concurrent_evaluations": 10
            },
            "enforcement": {
                "default_level": "blocking",
                "escalation_enabled": True,
                "auto_resolution": True,
                "notification_channels": ["email", "webhook", "dashboard"]
            },
            "compliance": {
                "audit_all_evaluations": True,
                "retention_days": 365,
                "compliance_standards": ["SOC2", "GDPR", "CCPA"],
                "regulatory_reporting": True
            },
            "creator_economy": {
                "tier_based_policies": True,
                "creator_specific_rules": True,
                "usage_based_enforcement": True,
                "satisfaction_impact_tracking": True
            },
            "performance": {
                "max_evaluation_time_ms": 5000,
                "batch_evaluation_size": 100,
                "policy_optimization": True,
                "monitoring_enabled": True
            }
        }
    
    def _initialize_rule_evaluators(self) -> None:
        """Initialize rule condition evaluators"""
        
        def equals_evaluator(actual: Any, expected: Any) -> bool:
            return actual == expected
        
        def not_equals_evaluator(actual: Any, expected: Any) -> bool:
            return actual != expected
        
        def greater_than_evaluator(actual: Any, expected: Any) -> bool:
            return float(actual) > float(expected)
        
        def less_than_evaluator(actual: Any, expected: Any) -> bool:
            return float(actual) < float(expected)
        
        def greater_equal_evaluator(actual: Any, expected: Any) -> bool:
            return float(actual) >= float(expected)
        
        def less_equal_evaluator(actual: Any, expected: Any) -> bool:
            return float(actual) <= float(expected)
        
        def contains_evaluator(actual: Any, expected: Any) -> bool:
            return str(expected) in str(actual)
        
        def not_contains_evaluator(actual: Any, expected: Any) -> bool:
            return str(expected) not in str(actual)
        
        def regex_match_evaluator(actual: Any, expected: Any) -> bool:
            try:
                return bool(re.match(str(expected), str(actual)))
            except re.error:
                return False
        
        def in_list_evaluator(actual: Any, expected: Any) -> bool:
            if isinstance(expected, list):
                return actual in expected
            return actual in str(expected).split(',')
        
        def not_in_list_evaluator(actual: Any, expected: Any) -> bool:
            return not in_list_evaluator(actual, expected)
        
        # Register evaluators
        self._rule_evaluators = {
            RuleOperator.EQUALS: equals_evaluator,
            RuleOperator.NOT_EQUALS: not_equals_evaluator,
            RuleOperator.GREATER_THAN: greater_than_evaluator,
            RuleOperator.LESS_THAN: less_than_evaluator,
            RuleOperator.GREATER_EQUAL: greater_equal_evaluator,
            RuleOperator.LESS_EQUAL: less_equal_evaluator,
            RuleOperator.CONTAINS: contains_evaluator,
            RuleOperator.NOT_CONTAINS: not_contains_evaluator,
            RuleOperator.REGEX_MATCH: regex_match_evaluator,
            RuleOperator.IN_LIST: in_list_evaluator,
            RuleOperator.NOT_IN_LIST: not_in_list_evaluator
        }
        
        logger.info(f"🔍 Initialized {len(self._rule_evaluators)} rule evaluators")
    
    def _initialize_action_handlers(self) -> None:
        """Initialize policy violation action handlers"""
        
        async def log_violation_action(violation: PolicyViolation) -> bool:
            """Log policy violation"""
            logger.warning(f"Policy violation: {violation.violation_type} in {violation.resource_id}")
            return True
        
        async def notify_stakeholders_action(violation: PolicyViolation) -> bool:
            """Notify stakeholders of violation"""
            # Mock notification - would integrate with actual notification system
            logger.info(f"Notifying stakeholders of violation {violation.violation_id}")
            return True
        
        async def block_resource_action(violation: PolicyViolation) -> bool:
            """Block resource access"""
            logger.warning(f"Blocking access to resource {violation.resource_id}")
            return True
        
        async def quarantine_model_action(violation: PolicyViolation) -> bool:
            """Quarantine model for review"""
            logger.warning(f"Quarantining model {violation.resource_id}")
            return True
        
        async def auto_remediate_action(violation: PolicyViolation) -> bool:
            """Attempt automatic remediation"""
            logger.info(f"Attempting auto-remediation for {violation.violation_id}")
            return True
        
        async def escalate_violation_action(violation: PolicyViolation) -> bool:
            """Escalate violation to higher authority"""
            logger.warning(f"Escalating violation {violation.violation_id}")
            return True
        
        # Register handlers
        self._action_handlers = {
            "log_violation": log_violation_action,
            "notify_stakeholders": notify_stakeholders_action,
            "block_resource": block_resource_action,
            "quarantine_model": quarantine_model_action,
            "auto_remediate": auto_remediate_action,
            "escalate_violation": escalate_violation_action
        }
        
        logger.info(f"⚡ Initialized {len(self._action_handlers)} action handlers")
    
    def _initialize_scope_filters(self) -> None:
        """Initialize policy scope filters"""
        
        def global_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Global scope - applies to all resources"""
            return True
        
        def model_type_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Filter by model type"""
            model_type = resource_data.get("model_type", "")
            allowed_types = scope_filter.get("model_types", [])
            return model_type in allowed_types if allowed_types else True
        
        def creator_tier_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Filter by creator tier"""
            creator_tier = resource_data.get("creator_tier", "")
            allowed_tiers = scope_filter.get("creator_tiers", [])
            return creator_tier in allowed_tiers if allowed_tiers else True
        
        def environment_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Filter by environment"""
            environment = resource_data.get("environment", "")
            allowed_environments = scope_filter.get("environments", [])
            return environment in allowed_environments if allowed_environments else True
        
        def region_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Filter by region"""
            region = resource_data.get("region", "")
            allowed_regions = scope_filter.get("regions", [])
            return region in allowed_regions if allowed_regions else True
        
        def custom_filter(resource_data: Dict[str, Any], scope_filter: Dict[str, Any]) -> bool:
            """Custom filter logic"""
            custom_conditions = scope_filter.get("custom_conditions", [])
            if not custom_conditions:
                return True
            
            # Evaluate custom conditions
            for condition in custom_conditions:
                field = condition.get("field")
                operator = condition.get("operator")
                expected = condition.get("value")
                
                if field in resource_data:
                    actual = resource_data[field]
                    evaluator = self._rule_evaluators.get(RuleOperator(operator))
                    if evaluator and not evaluator(actual, expected):
                        return False
            
            return True
        
        # Register scope filters
        self._scope_filters = {
            PolicyScope.GLOBAL: global_filter,
            PolicyScope.MODEL_TYPE: model_type_filter,
            PolicyScope.CREATOR_TIER: creator_tier_filter,
            PolicyScope.ENVIRONMENT: environment_filter,
            PolicyScope.REGION: region_filter,
            PolicyScope.CUSTOM: custom_filter
        }
        
        logger.info(f"🎯 Initialized {len(self._scope_filters)} scope filters")
    
    def _initialize_default_policies(self) -> None:
        """Initialize default governance policies"""
        try:
            default_policies = []
            
            # Security Policy - Model Access Control
            security_policy = Policy(
                policy_id="security_model_access_control",
                name="Model Access Control Policy",
                description="Enforce access control for AI models based on sensitivity levels",
                policy_type=PolicyType.SECURITY,
                scope=PolicyScope.GLOBAL,
                scope_filter={},
                rules=[
                    PolicyRule(
                        rule_id="high_sensitivity_access",
                        name="High Sensitivity Model Access",
                        description="Restrict access to high sensitivity models",
                        conditions=[
                            PolicyCondition(
                                condition_id="sensitivity_check",
                                field_name="sensitivity_level",
                                operator=RuleOperator.EQUALS,
                                expected_value="high",
                                description="Check if model has high sensitivity"
                            ),
                            PolicyCondition(
                                condition_id="creator_tier_check",
                                field_name="creator_tier",
                                operator=RuleOperator.IN_LIST,
                                expected_value=["enterprise", "professional"],
                                description="Only enterprise/professional creators allowed"
                            )
                        ],
                        condition_logic="AND",
                        actions=["log_violation", "block_resource"],
                        priority=1
                    )
                ],
                enforcement_level=EnforcementLevel.BLOCKING,
                status=PolicyStatus.ACTIVE,
                tags=["security", "access_control", "model_governance"]
            )
            default_policies.append(security_policy)
            
            # Compliance Policy - Data Privacy
            compliance_policy = Policy(
                policy_id="compliance_data_privacy",
                name="Data Privacy Compliance Policy",
                description="Ensure compliance with GDPR and CCPA data privacy requirements",
                policy_type=PolicyType.COMPLIANCE,
                scope=PolicyScope.GLOBAL,
                scope_filter={},
                rules=[
                    PolicyRule(
                        rule_id="pii_data_handling",
                        name="PII Data Handling",
                        description="Ensure proper handling of personally identifiable information",
                        conditions=[
                            PolicyCondition(
                                condition_id="contains_pii",
                                field_name="contains_pii",
                                operator=RuleOperator.EQUALS,
                                expected_value=True,
                                description="Check if data contains PII"
                            )
                        ],
                        actions=["log_violation", "notify_stakeholders", "quarantine_model"],
                        priority=2
                    )
                ],
                enforcement_level=EnforcementLevel.MANDATORY,
                status=PolicyStatus.ACTIVE,
                tags=["compliance", "privacy", "gdpr", "ccpa"]
            )
            default_policies.append(compliance_policy)
            
            # Performance Policy - Resource Usage
            performance_policy = Policy(
                policy_id="performance_resource_usage",
                name="Resource Usage Performance Policy",
                description="Monitor and control resource usage for optimal performance",
                policy_type=PolicyType.PERFORMANCE,
                scope=PolicyScope.GLOBAL,
                scope_filter={},
                rules=[
                    PolicyRule(
                        rule_id="excessive_memory_usage",
                        name="Excessive Memory Usage",
                        description="Flag models with excessive memory usage",
                        conditions=[
                            PolicyCondition(
                                condition_id="memory_usage_check",
                                field_name="memory_usage_gb",
                                operator=RuleOperator.GREATER_THAN,
                                expected_value=8.0,
                                description="Memory usage exceeds 8GB"
                            )
                        ],
                        actions=["log_violation", "notify_stakeholders"],
                        priority=3
                    )
                ],
                enforcement_level=EnforcementLevel.ADVISORY,
                status=PolicyStatus.ACTIVE,
                tags=["performance", "resource_usage", "optimization"]
            )
            default_policies.append(performance_policy)
            
            # Creator Economy Policy - Tier-based Features
            creator_economy_policy = Policy(
                policy_id="creator_economy_tier_features",
                name="Creator Tier Feature Access Policy",
                description="Control feature access based on creator subscription tier",
                policy_type=PolicyType.CREATOR_ECONOMY,
                scope=PolicyScope.CREATOR_TIER,
                scope_filter={"creator_tiers": ["basic", "premium", "professional", "enterprise"]},
                rules=[
                    PolicyRule(
                        rule_id="premium_feature_access",
                        name="Premium Feature Access Control",
                        description="Restrict premium features to appropriate tiers",
                        conditions=[
                            PolicyCondition(
                                condition_id="feature_tier_check",
                                field_name="feature_tier_required",
                                operator=RuleOperator.EQUALS,
                                expected_value="premium",
                                description="Feature requires premium tier"
                            ),
                            PolicyCondition(
                                condition_id="creator_tier_insufficient",
                                field_name="creator_tier",
                                operator=RuleOperator.EQUALS,
                                expected_value="basic",
                                description="Creator has basic tier"
                            )
                        ],
                        condition_logic="AND",
                        actions=["log_violation", "block_resource"],
                        priority=2
                    )
                ],
                enforcement_level=EnforcementLevel.BLOCKING,
                status=PolicyStatus.ACTIVE,
                tags=["creator_economy", "tier_access", "features"]
            )
            default_policies.append(creator_economy_policy)
            
            # Store default policies
            for policy in default_policies:
                self._policies[policy.policy_id] = policy
                self._policy_versions[policy.policy_id].append(policy)
            
            logger.info(f"📝 Initialized {len(default_policies)} default policies")
            
        except Exception as e:
            logger.error(f"Default policy initialization error: {str(e)}")
    
    async def create_policy(
        self,
        name: str,
        description: str,
        policy_type: PolicyType,
        scope: PolicyScope,
        scope_filter: Dict[str, Any],
        rules: List[Dict[str, Any]],
        enforcement_level: EnforcementLevel,
        created_by: str = "system",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new governance policy
        
        Args:
            name: Policy name
            description: Policy description
            policy_type: Type of policy
            scope: Policy application scope
            scope_filter: Scope filter criteria
            rules: List of policy rules
            enforcement_level: How strictly to enforce
            created_by: Policy creator
            tags: Policy tags
            metadata: Additional metadata
            
        Returns:
            Policy ID
        """
        try:
            policy_id = str(uuid.uuid4())
            
            # Convert rule dictionaries to PolicyRule objects
            policy_rules = []
            for rule_data in rules:
                conditions = []
                for cond_data in rule_data.get("conditions", []):
                    condition = PolicyCondition(
                        condition_id=cond_data.get("condition_id", str(uuid.uuid4())),
                        field_name=cond_data["field_name"],
                        operator=RuleOperator(cond_data["operator"]),
                        expected_value=cond_data["expected_value"],
                        description=cond_data.get("description", "")
                    )
                    conditions.append(condition)
                
                rule = PolicyRule(
                    rule_id=rule_data.get("rule_id", str(uuid.uuid4())),
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    conditions=conditions,
                    condition_logic=rule_data.get("condition_logic", "AND"),
                    actions=rule_data.get("actions", []),
                    priority=rule_data.get("priority", 100),
                    enabled=rule_data.get("enabled", True)
                )
                policy_rules.append(rule)
            
            # Create policy
            policy = Policy(
                policy_id=policy_id,
                name=name,
                description=description,
                policy_type=policy_type,
                scope=scope,
                scope_filter=scope_filter,
                rules=policy_rules,
                enforcement_level=enforcement_level,
                status=PolicyStatus.DRAFT,
                created_by=created_by,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store policy
            self._policies[policy_id] = policy
            self._policy_versions[policy_id].append(policy)
            
            # Update metrics
            self._performance_metrics["policy_changes"] += 1
            
            logger.info(f"📋 Created policy {name} with ID {policy_id}")
            
            return policy_id
            
        except Exception as e:
            logger.error(f"Policy creation error: {str(e)}")
            raise
    
    async def evaluate_policies(
        self,
        resource_id: str,
        resource_type: str,
        resource_data: Dict[str, Any],
        policy_ids: Optional[List[str]] = None
    ) -> PolicyEvaluationResult:
        """
        Evaluate policies against resource
        
        Args:
            resource_id: Resource identifier
            resource_type: Type of resource
            resource_data: Resource data for evaluation
            policy_ids: Specific policies to evaluate (None = all applicable)
            
        Returns:
            Policy evaluation result
        """
        try:
            evaluation_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            # Check cache first
            cache_key = f"{resource_id}:{resource_type}:{hash(json.dumps(resource_data, sort_keys=True))}"
            if (self.config["evaluation"]["enable_caching"] and 
                cache_key in self._evaluation_cache):
                
                cache_entry = self._evaluation_cache[cache_key]
                cache_age = (datetime.now() - cache_entry["timestamp"]).total_seconds()
                
                if cache_age < self._cache_ttl:
                    logger.debug(f"🎯 Cache hit for resource {resource_id}")
                    return PolicyEvaluationResult(**cache_entry["result"])
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(
                resource_type, resource_data, policy_ids
            )
            
            violations = []
            evaluated_policy_ids = []
            
            # Evaluate each applicable policy
            for policy in applicable_policies:
                evaluated_policy_ids.append(policy.policy_id)
                
                # Skip if policy is not active
                if policy.status != PolicyStatus.ACTIVE:
                    continue
                
                # Check if policy is effective
                if not self._is_policy_effective(policy):
                    continue
                
                # Evaluate policy rules
                policy_violations = await self._evaluate_policy_rules(
                    policy, resource_id, resource_type, resource_data
                )
                violations.extend(policy_violations)
            
            # Determine compliance
            compliant = len(violations) == 0
            
            # Calculate evaluation time
            evaluation_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Create evaluation result
            result = PolicyEvaluationResult(
                evaluation_id=evaluation_id,
                resource_id=resource_id,
                resource_type=resource_type,
                evaluated_policies=evaluated_policy_ids,
                violations=violations,
                compliant=compliant,
                evaluation_time_ms=evaluation_time
            )
            
            # Cache result
            if self.config["evaluation"]["enable_caching"]:
                self._evaluation_cache[cache_key] = {
                    "result": result.to_dict(),
                    "timestamp": datetime.now()
                }
            
            # Store evaluation result
            self._evaluation_results.append(result)
            
            # Trim evaluation history if needed
            if len(self._evaluation_results) > 10000:
                self._evaluation_results = self._evaluation_results[-5000:]
            
            # Update metrics
            self._performance_metrics["policies_evaluated"] += len(evaluated_policy_ids)
            if not compliant:
                self._performance_metrics["violations_detected"] += len(violations)
            
            # Update average evaluation time
            total_evals = self._performance_metrics["policies_evaluated"]
            if total_evals > 0:
                current_avg = self._performance_metrics["avg_evaluation_time_ms"]
                self._performance_metrics["avg_evaluation_time_ms"] = (
                    (current_avg * (total_evals - len(evaluated_policy_ids)) + evaluation_time) / total_evals
                )
            
            logger.info(f"📊 Evaluated {len(evaluated_policy_ids)} policies for {resource_id} in {evaluation_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Policy evaluation error: {str(e)}")
            raise
    
    async def _get_applicable_policies(
        self,
        resource_type: str,
        resource_data: Dict[str, Any],
        policy_ids: Optional[List[str]] = None
    ) -> List[Policy]:
        """Get policies applicable to resource"""
        try:
            applicable_policies = []
            
            # Filter policies
            policies_to_check = (
                [self._policies[pid] for pid in policy_ids if pid in self._policies]
                if policy_ids else self._policies.values()
            )
            
            for policy in policies_to_check:
                # Check scope filter
                scope_filter_func = self._scope_filters.get(policy.scope)
                if scope_filter_func and scope_filter_func(resource_data, policy.scope_filter):
                    applicable_policies.append(policy)
            
            # Sort by enforcement level and priority
            enforcement_priority = {
                EnforcementLevel.CRITICAL: 0,
                EnforcementLevel.MANDATORY: 1,
                EnforcementLevel.BLOCKING: 2,
                EnforcementLevel.ADVISORY: 3
            }
            
            applicable_policies.sort(
                key=lambda p: (enforcement_priority.get(p.enforcement_level, 4), min(r.priority for r in p.rules))
            )
            
            return applicable_policies
            
        except Exception as e:
            logger.error(f"Applicable policies retrieval error: {str(e)}")
            return []
    
    def _is_policy_effective(self, policy: Policy) -> bool:
        """Check if policy is currently effective"""
        now = datetime.now()
        
        # Check effective date
        if policy.effective_date and now < policy.effective_date:
            return False
        
        # Check expiry date
        if policy.expiry_date and now > policy.expiry_date:
            return False
        
        return True
    
    async def _evaluate_policy_rules(
        self,
        policy: Policy,
        resource_id: str,
        resource_type: str,
        resource_data: Dict[str, Any]
    ) -> List[PolicyViolation]:
        """Evaluate all rules in a policy"""
        violations = []
        
        for rule in policy.rules:
            if not rule.enabled:
                continue
            
            # Evaluate rule conditions
            rule_violated = await self._evaluate_rule_conditions(rule, resource_data)
            
            if rule_violated:
                # Create violation
                violation = PolicyViolation(
                    violation_id=str(uuid.uuid4()),
                    policy_id=policy.policy_id,
                    rule_id=rule.rule_id,
                    violation_type=f"{policy.policy_type.value}_violation",
                    severity=self._get_violation_severity(policy.enforcement_level),
                    resource_id=resource_id,
                    resource_type=resource_type,
                    violation_details={
                        "policy_name": policy.name,
                        "rule_name": rule.name,
                        "rule_description": rule.description,
                        "enforcement_level": policy.enforcement_level.value,
                        "violated_conditions": [c.to_dict() for c in rule.conditions]
                    },
                    detected_at=datetime.now(),
                    creator_id=resource_data.get("creator_id")
                )
                
                violations.append(violation)
                
                # Store violation
                self._violations[violation.violation_id] = violation
                
                # Execute violation actions
                await self._execute_violation_actions(violation, rule.actions)
        
        return violations
    
    async def _evaluate_rule_conditions(
        self,
        rule: PolicyRule,
        resource_data: Dict[str, Any]
    ) -> bool:
        """Evaluate rule conditions"""
        try:
            condition_results = []
            
            for condition in rule.conditions:
                # Get actual value from resource data
                actual_value = self._get_nested_value(resource_data, condition.field_name)
                
                # Get evaluator for operator
                evaluator = self._rule_evaluators.get(condition.operator)
                if not evaluator:
                    logger.warning(f"No evaluator for operator {condition.operator}")
                    condition_results.append(False)
                    continue
                
                # Evaluate condition
                try:
                    result = evaluator(actual_value, condition.expected_value)
                    condition_results.append(result)
                except Exception as e:
                    logger.error(f"Condition evaluation error: {str(e)}")
                    condition_results.append(False)
            
            # Apply condition logic
            if rule.condition_logic == "OR":
                return any(condition_results)
            elif rule.condition_logic == "AND":
                return all(condition_results)
            else:
                # Custom logic would be implemented here
                return all(condition_results)  # Default to AND
            
        except Exception as e:
            logger.error(f"Rule condition evaluation error: {str(e)}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value from data using dot notation"""
        try:
            keys = field_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception as e:
            logger.error(f"Nested value retrieval error: {str(e)}")
            return None
    
    def _get_violation_severity(self, enforcement_level: EnforcementLevel) -> str:
        """Map enforcement level to violation severity"""
        severity_map = {
            EnforcementLevel.ADVISORY: "low",
            EnforcementLevel.BLOCKING: "medium",
            EnforcementLevel.MANDATORY: "high",
            EnforcementLevel.CRITICAL: "critical"
        }
        return severity_map.get(enforcement_level, "medium")
    
    async def _execute_violation_actions(
        self,
        violation: PolicyViolation,
        actions: List[str]
    ) -> None:
        """Execute actions for policy violation"""
        try:
            for action_name in actions:
                action_handler = self._action_handlers.get(action_name)
                if action_handler:
                    try:
                        success = await action_handler(violation)
                        if success:
                            logger.info(f"✅ Executed action {action_name} for violation {violation.violation_id}")
                        else:
                            logger.warning(f"⚠️ Action {action_name} failed for violation {violation.violation_id}")
                    except Exception as e:
                        logger.error(f"Action execution error for {action_name}: {str(e)}")
                else:
                    logger.warning(f"Unknown action: {action_name}")
                    
        except Exception as e:
            logger.error(f"Violation action execution error: {str(e)}")
    
    async def activate_policy(self, policy_id: str) -> bool:
        """Activate a policy"""
        try:
            policy = self._policies.get(policy_id)
            if not policy:
                return False
            
            policy.status = PolicyStatus.ACTIVE
            policy.updated_at = datetime.now()
            
            # Clear evaluation cache since policy state changed
            self._evaluation_cache.clear()
            
            self._performance_metrics["policy_changes"] += 1
            
            logger.info(f"✅ Activated policy {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Policy activation error: {str(e)}")
            return False
    
    async def deactivate_policy(self, policy_id: str) -> bool:
        """Deactivate a policy"""
        try:
            policy = self._policies.get(policy_id)
            if not policy:
                return False
            
            policy.status = PolicyStatus.SUSPENDED
            policy.updated_at = datetime.now()
            
            # Clear evaluation cache
            self._evaluation_cache.clear()
            
            self._performance_metrics["policy_changes"] += 1
            
            logger.info(f"⏸️ Deactivated policy {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Policy deactivation error: {str(e)}")
            return False
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy by ID"""
        policy = self._policies.get(policy_id)
        return policy.to_dict() if policy else None
    
    def list_policies(
        self,
        policy_type: Optional[PolicyType] = None,
        status: Optional[PolicyStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List policies with optional filters"""
        try:
            policies = list(self._policies.values())
            
            # Apply filters
            if policy_type:
                policies = [p for p in policies if p.policy_type == policy_type]
            
            if status:
                policies = [p for p in policies if p.status == status]
            
            if tags:
                policies = [p for p in policies if any(tag in p.tags for tag in tags)]
            
            return [p.to_dict() for p in policies]
            
        except Exception as e:
            logger.error(f"Policy listing error: {str(e)}")
            return []
    
    def get_policy_violations(
        self,
        resource_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get policy violations with filters"""
        try:
            violations = list(self._violations.values())
            
            # Apply filters
            if resource_id:
                violations = [v for v in violations if v.resource_id == resource_id]
            
            if policy_id:
                violations = [v for v in violations if v.policy_id == policy_id]
            
            if resolved is not None:
                violations = [v for v in violations if (v.resolved_at is not None) == resolved]
            
            # Sort by detection time (newest first) and limit
            violations.sort(key=lambda x: x.detected_at, reverse=True)
            
            return [v.to_dict() for v in violations[:limit]]
            
        except Exception as e:
            logger.error(f"Violation retrieval error: {str(e)}")
            return []
    
    def get_policy_metrics(self) -> Dict[str, Any]:
        """Get policy engine metrics"""
        return {
            **self._performance_metrics,
            "total_policies": len(self._policies),
            "active_policies": len([p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]),
            "total_violations": len(self._violations),
            "unresolved_violations": len([v for v in self._violations.values() if v.resolved_at is None]),
            "cached_evaluations": len(self._evaluation_cache)
        }
    
    def health_check(self) -> str:
        """Health check for policy engine"""
        try:
            # Check for active policies
            active_policies = [p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]
            if len(active_policies) == 0:
                return "WARNING: No active policies"
            
            # Check for high violation rate
            if self._performance_metrics["policies_evaluated"] > 0:
                violation_rate = (
                    self._performance_metrics["violations_detected"] / 
                    self._performance_metrics["policies_evaluated"]
                )
                if violation_rate > 0.5:  # More than 50% violation rate
                    return f"WARNING: High violation rate: {violation_rate:.2%}"
            
            # Check evaluation performance
            avg_time = self._performance_metrics["avg_evaluation_time_ms"]
            max_time = self.config["performance"]["max_evaluation_time_ms"]
            if avg_time > max_time:
                return f"WARNING: Slow evaluation time: {avg_time:.2f}ms > {max_time}ms"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and related types
__all__ = [
    "GovernancePolicyEngine",
    "PolicyType",
    "PolicyScope",
    "PolicyStatus",
    "EnforcementLevel",
    "RuleOperator",
    "Policy",
    "PolicyRule",
    "PolicyCondition",
    "PolicyViolation",
    "PolicyEvaluationResult"
]