"""Business Rules Engine - IA Influencer Agent Platform
=====================================================

Consolidated business rules engine providing comprehensive rule evaluation,
validation, and enforcement for content creation, monetization, and collaboration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of business rules."""
    CONTENT_VALIDATION = "content_validation"
    MONETIZATION_RULES = "monetization_rules"
    COLLABORATION_RULES = "collaboration_rules"
    PROTECTION_RULES = "protection_rules"
    COMPLIANCE_RULES = "compliance_rules"
    AUDIENCE_RULES = "audience_rules"
    PLATFORM_RULES = "platform_rules"


class RulePriority(Enum):
    """Rule priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BusinessRule:
    """Business rule definition."""
    rule_id: str
    name: str
    rule_type: RuleType
    priority: RulePriority
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleEvaluationContext:
    """Context for rule evaluation."""
    user_id: str
    content_id: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    creator_type: Optional[str] = None
    audience_size: int = 0
    revenue_data: Dict[str, Any] = field(default_factory=dict)
    collaboration_data: Dict[str, Any] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation."""
    rule_id: str
    passed: bool
    message: str
    actions_required: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_time: datetime = field(default_factory=datetime.utcnow)


class BusinessRulesEngine:
    """
    Consolidated business rules engine for the IA Influencer platform.
    
    Manages and evaluates business rules across all domains including content,
    monetization, collaboration, protection, and compliance.
    """
    
    def __init__(self) -> None:
        """Initialize the business rules engine."""
        self.rules: Dict[str, BusinessRule] = {}
        self.rule_sets: Dict[RuleType, List[str]] = {rule_type: [] for rule_type in RuleType}
        self.logger = logging.getLogger(__name__)
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default business rules."""
        default_rules = [
            # Content validation rules
            BusinessRule(
                rule_id="content_protection_required",
                name="Content Protection Required",
                rule_type=RuleType.CONTENT_VALIDATION,
                priority=RulePriority.CRITICAL,
                conditions={"content_type": ["audio", "video", "image"], "protection_enabled": True},
                actions=[{"type": "enable_protection", "fingerprint": True}]
            ),
            BusinessRule(
                rule_id="minimum_content_threshold",
                name="Minimum Content Threshold",
                rule_type=RuleType.CONTENT_VALIDATION,
                priority=RulePriority.HIGH,
                conditions={"content_count": {"min": 1}},
                actions=[{"type": "validate_content_count"}]
            ),
            # Monetization rules
            BusinessRule(
                rule_id="minimum_audience_size",
                name="Minimum Audience Size for Monetization",
                rule_type=RuleType.MONETIZATION_RULES,
                priority=RulePriority.HIGH,
                conditions={"audience_size": {"min": 1000}},
                actions=[{"type": "enable_monetization"}]
            ),
            # Collaboration rules
            BusinessRule(
                rule_id="minimum_match_score",
                name="Minimum Collaboration Match Score",
                rule_type=RuleType.COLLABORATION_RULES,
                priority=RulePriority.MEDIUM,
                conditions={"match_score": {"min": 0.7}},
                actions=[{"type": "allow_collaboration"}]
            ),
            # Protection rules
            BusinessRule(
                rule_id="auto_protection_enabled",
                name="Auto Protection Enabled",
                rule_type=RuleType.PROTECTION_RULES,
                priority=RulePriority.CRITICAL,
                conditions={"auto_protection": True},
                actions=[{"type": "enable_auto_protection"}]
            ),
            # Compliance rules
            BusinessRule(
                rule_id="always_personalize",
                name="Always Allow Personalization",
                rule_type=RuleType.COMPLIANCE_RULES,
                priority=RulePriority.LOW,
                conditions={"personalization": True},
                actions=[{"type": "allow_personalization"}]
            )
        ]
        
        for rule in default_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: BusinessRule) -> str:
        """Add a business rule to the engine."""
        try:
            self.rules[rule.rule_id] = rule
            self.rule_sets[rule.rule_type].append(rule.rule_id)
            self.logger.info(f"Added business rule: {rule.name} ({rule.rule_id})")
            return rule.rule_id
        except Exception as e:
            self.logger.error(f"Failed to add rule {rule.rule_id}: {str(e)}")
            raise
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a business rule from the engine."""
        try:
            if rule_id in self.rules:
                rule = self.rules[rule_id]
                del self.rules[rule_id]
                if rule_id in self.rule_sets[rule.rule_type]:
                    self.rule_sets[rule.rule_type].remove(rule_id)
                self.logger.info(f"Removed business rule: {rule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove rule {rule_id}: {str(e)}")
            return False
    
    async def evaluate_rule(self, rule_id: str, context: RuleEvaluationContext) -> RuleEvaluationResult:
        """Evaluate a specific business rule."""
        try:
            if rule_id not in self.rules:
                return RuleEvaluationResult(
                    rule_id=rule_id,
                    passed=False,
                    message=f"Rule {rule_id} not found"
                )
            
            rule = self.rules[rule_id]
            if not rule.is_active:
                return RuleEvaluationResult(
                    rule_id=rule_id,
                    passed=True,
                    message=f"Rule {rule_id} is inactive"
                )
            
            # Evaluate rule conditions
            passed = await self._evaluate_conditions(rule.conditions, context)
            
            result = RuleEvaluationResult(
                rule_id=rule_id,
                passed=passed,
                message=f"Rule {rule.name} {'passed' if passed else 'failed'}",
                actions_required=rule.actions if passed else [],
                metadata={"rule_type": rule.rule_type.value, "priority": rule.priority.value}
            )
            
            self.logger.debug(f"Rule evaluation: {rule_id} = {passed}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule_id}: {str(e)}")
            return RuleEvaluationResult(
                rule_id=rule_id,
                passed=False,
                message=f"Error evaluating rule: {str(e)}"
            )
    
    async def evaluate_rules_by_type(self, rule_type: RuleType, context: RuleEvaluationContext) -> List[RuleEvaluationResult]:
        """Evaluate all rules of a specific type."""
        try:
            results = []
            rule_ids = self.rule_sets.get(rule_type, [])
            
            for rule_id in rule_ids:
                result = await self.evaluate_rule(rule_id, context)
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating rules by type {rule_type}: {str(e)}")
            return []
    
    async def evaluate_all_rules(self, context: RuleEvaluationContext) -> Dict[str, RuleEvaluationResult]:
        """Evaluate all active business rules."""
        try:
            results = {}
            
            for rule_id in self.rules:
                result = await self.evaluate_rule(rule_id, context)
                results[rule_id] = result
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating all rules: {str(e)}")
            return {}
    
    async def _evaluate_conditions(self, conditions: Dict[str, Any], context: RuleEvaluationContext) -> bool:
        """Evaluate rule conditions against context."""
        try:
            for condition_key, condition_value in conditions.items():
                # Handle different condition types
                if condition_key == "content_type":
                    if context.content_type not in condition_value:
                        return False
                
                elif condition_key == "protection_enabled":
                    # Check if protection is enabled in custom data
                    protection_enabled = context.custom_data.get("protection_enabled", True)
                    if protection_enabled != condition_value:
                        return False
                
                elif condition_key == "content_count":
                    content_count = context.custom_data.get("content_count", 0)
                    if isinstance(condition_value, dict):
                        if "min" in condition_value and content_count < condition_value["min"]:
                            return False
                        if "max" in condition_value and content_count > condition_value["max"]:
                            return False
                    elif content_count != condition_value:
                        return False
                
                elif condition_key == "audience_size":
                    if isinstance(condition_value, dict):
                        if "min" in condition_value and context.audience_size < condition_value["min"]:
                            return False
                        if "max" in condition_value and context.audience_size > condition_value["max"]:
                            return False
                    elif context.audience_size != condition_value:
                        return False
                
                elif condition_key == "match_score":
                    match_score = context.collaboration_data.get("match_score", 0)
                    if isinstance(condition_value, dict):
                        if "min" in condition_value and match_score < condition_value["min"]:
                            return False
                    elif match_score != condition_value:
                        return False
                
                elif condition_key == "auto_protection":
                    auto_protection = context.custom_data.get("auto_protection", True)
                    if auto_protection != condition_value:
                        return False
                
                elif condition_key == "personalization":
                    # Always allow personalization for now
                    continue
                
                else:
                    # Check in custom data
                    custom_value = context.custom_data.get(condition_key)
                    if custom_value != condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {str(e)}")
            return False
    
    def get_rule_summary(self) -> Dict[str, Any]:
        """Get summary of all rules."""
        try:
            summary = {
                "total_rules": len(self.rules),
                "active_rules": len([r for r in self.rules.values() if r.is_active]),
                "rules_by_type": {},
                "rules_by_priority": {}
            }
            
            for rule_type in RuleType:
                summary["rules_by_type"][rule_type.value] = len(self.rule_sets[rule_type])
            
            for priority in RulePriority:
                summary["rules_by_priority"][priority.value] = len([
                    r for r in self.rules.values() if r.priority == priority
                ])
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting rule summary: {str(e)}")
            return {}
    
    async def validate_business_rules(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Validate business rules for a specific context."""
        try:
            context = RuleEvaluationContext(
                user_id=user_id,
                content_id=kwargs.get("content_id"),
                platform=kwargs.get("platform"),
                content_type=kwargs.get("content_type"),
                creator_type=kwargs.get("creator_type"),
                audience_size=kwargs.get("audience_size", 0),
                revenue_data=kwargs.get("revenue_data", {}),
                collaboration_data=kwargs.get("collaboration_data", {}),
                custom_data=kwargs.get("custom_data", {})
            )
            
            results = await self.evaluate_all_rules(context)
            
            passed_rules = [r for r in results.values() if r.passed]
            failed_rules = [r for r in results.values() if not r.passed]
            
            return {
                "validation_passed": len(failed_rules) == 0,
                "total_rules_evaluated": len(results),
                "passed_rules": len(passed_rules),
                "failed_rules": len(failed_rules),
                "critical_failures": len([r for r in failed_rules if results[r.rule_id].metadata.get("priority") == "critical"]),
                "results": {r.rule_id: {"passed": r.passed, "message": r.message} for r in results.values()},
                "actions_required": [action for r in passed_rules for action in r.actions_required]
            }
            
        except Exception as e:
            self.logger.error(f"Error validating business rules: {str(e)}")
            return {
                "validation_passed": False,
                "error": str(e)
            }