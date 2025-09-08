"""Feature Flags - Enterprise Dynamic Feature Toggles & A/B Testing System
========================================================================

Advanced feature flag management system providing dynamic feature toggles,
A/B testing configuration, gradual rollouts, user segment targeting,
analytics, and rollback mechanisms for controlled feature deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from datetime import datetime, timedelta
import asyncio
import json
import hashlib
import random
import logging
import os
from pathlib import Path
from abc import ABC, abstractmethod
import aiofiles

# ===============================
# FEATURE FLAGS TYPES & ENUMS
# ===============================

class FeatureFlagType(str, Enum):
    """Types of feature flags"""
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    STRING = "string"
    JSON = "json"
    MULTIVARIATE = "multivariate"

class RolloutStrategy(str, Enum):
    """Feature rollout strategies"""
    INSTANT = "instant"
    GRADUAL = "gradual"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    RING_DEPLOYMENT = "ring_deployment"

class TargetingRule(str, Enum):
    """User targeting rules"""
    USER_ID = "user_id"
    USER_GROUP = "user_group"
    PERCENTAGE = "percentage"
    GEOGRAPHIC = "geographic"
    DEVICE_TYPE = "device_type"
    USER_AGENT = "user_agent"
    CUSTOM_ATTRIBUTE = "custom_attribute"

class FlagStatus(str, Enum):
    """Feature flag status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ExperimentType(str, Enum):
    """A/B experiment types"""
    AB_TEST = "ab_test"
    MULTIVARIATE = "multivariate"
    HOLDOUT = "holdout"
    FEATURE_TOGGLE = "feature_toggle"

# ==============================
# FEATURE FLAG DATA STRUCTURES
# ==============================

@dataclass
class TargetingCondition:
    """Targeting condition for feature flags"""
    rule_type: TargetingRule
    operator: str  # equals, not_equals, in, not_in, greater_than, etc.
    values: List[Any]
    weight: float = 1.0

@dataclass
class FeatureFlagVariant:
    """Feature flag variant for multivariate testing"""
    name: str
    value: Any
    weight: float
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RolloutConfiguration:
    """Rollout configuration for gradual deployment"""
    strategy: RolloutStrategy
    percentage: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    increment_percentage: float = 10.0
    increment_interval: timedelta = timedelta(hours=1)
    rollback_threshold: float = 0.05  # 5% error rate triggers rollback

@dataclass
class FeatureFlag:
    """Complete feature flag definition"""
    flag_id: str
    name: str
    description: str
    flag_type: FeatureFlagType
    default_value: Any
    variants: List[FeatureFlagVariant] = field(default_factory=list)
    targeting_conditions: List[TargetingCondition] = field(default_factory=list)
    rollout_config: Optional[RolloutConfiguration] = None
    status: FlagStatus = FlagStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    tags: List[str] = field(default_factory=list)
    environment: str = "development"
    dependencies: List[str] = field(default_factory=list)

@dataclass
class UserContext:
    """User context for feature flag evaluation"""
    user_id: str
    groups: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    geographic_info: Dict[str, str] = field(default_factory=dict)
    device_info: Dict[str, str] = field(default_factory=dict)
    session_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FlagEvaluation:
    """Result of feature flag evaluation"""
    flag_id: str
    value: Any
    variant_name: Optional[str] = None
    matched_conditions: List[str] = field(default_factory=list)
    evaluation_reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    user_context: Optional[UserContext] = None

@dataclass
class ExperimentConfiguration:
    """A/B testing experiment configuration"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    feature_flags: List[str]
    traffic_allocation: float = 1.0  # Percentage of users in experiment
    variants: List[FeatureFlagVariant] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    guardrail_metrics: List[str] = field(default_factory=list)
    statistical_power: float = 0.8
    significance_level: float = 0.05
    minimum_effect_size: float = 0.05

# ==============================
# TARGETING ENGINE
# ==============================

class TargetingEngine:
    """Advanced user targeting engine for feature flags"""
    
    def __init__(self):
        self.custom_evaluators: Dict[str, Callable] = {}
        self.geographic_data: Dict[str, Dict[str, Any]] = {}
        self.user_segments: Dict[str, List[str]] = {}
    
    def register_custom_evaluator(self, rule_name: str, 
                                 evaluator: Callable[[Any, str, List[Any]], bool]) -> None:
        """Register custom targeting rule evaluator"""
        self.custom_evaluators[rule_name] = evaluator
    
    async def evaluate_targeting_conditions(self, conditions: List[TargetingCondition],
                                          user_context: UserContext) -> bool:
        """Evaluate if user matches targeting conditions"""
        if not conditions:
            return True
        
        total_weight = 0.0
        matched_weight = 0.0
        
        for condition in conditions:
            total_weight += condition.weight
            
            if await self._evaluate_single_condition(condition, user_context):
                matched_weight += condition.weight
        
        # Require all conditions to match (AND logic)
        # For OR logic, this could be modified to require any match
        return matched_weight == total_weight
    
    async def _evaluate_single_condition(self, condition: TargetingCondition,
                                       user_context: UserContext) -> bool:
        """Evaluate single targeting condition"""
        try:
            if condition.rule_type == TargetingRule.USER_ID:
                return self._evaluate_user_id(condition, user_context.user_id)
            
            elif condition.rule_type == TargetingRule.USER_GROUP:
                return self._evaluate_user_group(condition, user_context.groups)
            
            elif condition.rule_type == TargetingRule.PERCENTAGE:
                return self._evaluate_percentage(condition, user_context.user_id)
            
            elif condition.rule_type == TargetingRule.GEOGRAPHIC:
                return self._evaluate_geographic(condition, user_context.geographic_info)
            
            elif condition.rule_type == TargetingRule.DEVICE_TYPE:
                return self._evaluate_device_type(condition, user_context.device_info)
            
            elif condition.rule_type == TargetingRule.CUSTOM_ATTRIBUTE:
                return self._evaluate_custom_attribute(condition, user_context.attributes)
            
            elif condition.rule_type.value in self.custom_evaluators:
                evaluator = self.custom_evaluators[condition.rule_type.value]
                return evaluator(user_context, condition.operator, condition.values)
            
            else:
                logging.warning(f"Unknown targeting rule: {condition.rule_type}")
                return False
                
        except Exception as e:
            logging.error(f"Error evaluating targeting condition: {e}")
            return False
    
    def _evaluate_user_id(self, condition: TargetingCondition, user_id: str) -> bool:
        """Evaluate user ID targeting condition"""
        if condition.operator == "equals":
            return user_id in condition.values
        elif condition.operator == "not_equals":
            return user_id not in condition.values
        elif condition.operator == "starts_with":
            return any(user_id.startswith(str(val)) for val in condition.values)
        elif condition.operator == "regex":
            import re
            return any(re.match(str(val), user_id) for val in condition.values)
        return False
    
    def _evaluate_user_group(self, condition: TargetingCondition, user_groups: List[str]) -> bool:
        """Evaluate user group targeting condition"""
        condition_groups = [str(val) for val in condition.values]
        
        if condition.operator == "in":
            return any(group in condition_groups for group in user_groups)
        elif condition.operator == "not_in":
            return not any(group in condition_groups for group in user_groups)
        elif condition.operator == "contains_all":
            return all(group in user_groups for group in condition_groups)
        return False
    
    def _evaluate_percentage(self, condition: TargetingCondition, user_id: str) -> bool:
        """Evaluate percentage-based targeting"""
        # Create deterministic hash for user
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        user_percentage = (user_hash % 100) + 1
        
        target_percentage = float(condition.values[0])
        
        if condition.operator == "less_than":
            return user_percentage <= target_percentage
        elif condition.operator == "greater_than":
            return user_percentage > target_percentage
        elif condition.operator == "equals":
            return user_percentage == target_percentage
        return False
    
    def _evaluate_geographic(self, condition: TargetingCondition, 
                           geographic_info: Dict[str, str]) -> bool:
        """Evaluate geographic targeting condition"""
        if condition.operator == "country_in":
            country = geographic_info.get("country", "")
            return country in [str(val) for val in condition.values]
        elif condition.operator == "region_in":
            region = geographic_info.get("region", "")
            return region in [str(val) for val in condition.values]
        elif condition.operator == "timezone_in":
            timezone = geographic_info.get("timezone", "")
            return timezone in [str(val) for val in condition.values]
        return False
    
    def _evaluate_device_type(self, condition: TargetingCondition,
                            device_info: Dict[str, str]) -> bool:
        """Evaluate device type targeting condition"""
        if condition.operator == "platform_in":
            platform = device_info.get("platform", "")
            return platform in [str(val) for val in condition.values]
        elif condition.operator == "browser_in":
            browser = device_info.get("browser", "")
            return browser in [str(val) for val in condition.values]
        elif condition.operator == "mobile":
            is_mobile = device_info.get("mobile", "false").lower() == "true"
            return is_mobile == bool(condition.values[0])
        return False
    
    def _evaluate_custom_attribute(self, condition: TargetingCondition,
                                 attributes: Dict[str, Any]) -> bool:
        """Evaluate custom attribute targeting condition"""
        attr_name = str(condition.values[0]) if condition.values else ""
        attr_value = attributes.get(attr_name)
        
        if len(condition.values) < 2:
            return False
        
        target_values = condition.values[1:]
        
        if condition.operator == "equals":
            return attr_value in target_values
        elif condition.operator == "not_equals":
            return attr_value not in target_values
        elif condition.operator == "greater_than":
            return attr_value > target_values[0] if attr_value is not None else False
        elif condition.operator == "less_than":
            return attr_value < target_values[0] if attr_value is not None else False
        return False

# ==============================
# ROLLOUT MANAGER
# ==============================

class RolloutManager:
    """Manages gradual rollout of feature flags"""
    
    def __init__(self):
        self.active_rollouts: Dict[str, Dict[str, Any]] = {}
        self.rollout_schedules: Dict[str, asyncio.Task] = {}
        self.rollout_history: Dict[str, List[Dict[str, Any]]] = {}
        self.metrics_collector: Optional[Callable] = None
    
    def set_metrics_collector(self, collector: Callable[[str, Dict[str, Any]], None]) -> None:
        """Set metrics collector for rollout monitoring"""
        self.metrics_collector = collector
    
    async def start_rollout(self, flag: FeatureFlag) -> Dict[str, Any]:
        """Start gradual rollout for feature flag"""
        if not flag.rollout_config:
            return {"status": "error", "message": "No rollout configuration"}
        
        rollout_info = {
            "flag_id": flag.flag_id,
            "strategy": flag.rollout_config.strategy,
            "current_percentage": flag.rollout_config.percentage,
            "target_percentage": 100.0,
            "start_time": datetime.now(),
            "status": "active",
            "phases_completed": 0,
            "rollback_triggered": False
        }
        
        self.active_rollouts[flag.flag_id] = rollout_info
        
        if flag.rollout_config.strategy == RolloutStrategy.GRADUAL:
            # Schedule gradual rollout
            task = asyncio.create_task(self._execute_gradual_rollout(flag))
            self.rollout_schedules[flag.flag_id] = task
        
        elif flag.rollout_config.strategy == RolloutStrategy.CANARY:
            # Start with small percentage for canary
            flag.rollout_config.percentage = 5.0
            rollout_info["current_percentage"] = 5.0
        
        logging.info(f"Started rollout for flag {flag.flag_id} using {flag.rollout_config.strategy} strategy")
        return rollout_info
    
    async def _execute_gradual_rollout(self, flag: FeatureFlag) -> None:
        """Execute gradual rollout in phases"""
        config = flag.rollout_config
        current_percentage = config.percentage
        
        while current_percentage < 100.0:
            # Wait for next increment
            await asyncio.sleep(config.increment_interval.total_seconds())
            
            # Check for rollback conditions
            if await self._should_rollback(flag):
                await self._execute_rollback(flag)
                return
            
            # Increment percentage
            current_percentage = min(100.0, current_percentage + config.increment_percentage)
            config.percentage = current_percentage
            
            # Update rollout info
            rollout_info = self.active_rollouts[flag.flag_id]
            rollout_info["current_percentage"] = current_percentage
            rollout_info["phases_completed"] += 1
            
            # Collect metrics
            if self.metrics_collector:
                await self._collect_rollout_metrics(flag)
            
            logging.info(f"Rollout for {flag.flag_id} increased to {current_percentage}%")
        
        # Mark rollout as completed
        self.active_rollouts[flag.flag_id]["status"] = "completed"
        logging.info(f"Gradual rollout completed for flag {flag.flag_id}")
    
    async def _should_rollback(self, flag: FeatureFlag) -> bool:
        """Check if rollout should be rolled back based on metrics"""
        if not self.metrics_collector:
            return False
        
        # Get current metrics
        metrics = await self._get_flag_metrics(flag.flag_id)
        
        if not metrics:
            return False
        
        # Check error rate
        error_rate = metrics.get("error_rate", 0.0)
        if error_rate > flag.rollout_config.rollback_threshold:
            return True
        
        # Check performance degradation
        performance_degradation = metrics.get("performance_degradation", 0.0)
        if performance_degradation > 0.2:  # 20% performance drop
            return True
        
        # Check user satisfaction
        satisfaction_score = metrics.get("satisfaction_score", 1.0)
        if satisfaction_score < 0.7:  # Below 70% satisfaction
            return True
        
        return False
    
    async def _execute_rollback(self, flag: FeatureFlag) -> None:
        """Execute automatic rollback"""
        rollout_info = self.active_rollouts[flag.flag_id]
        rollout_info["rollback_triggered"] = True
        rollout_info["status"] = "rolled_back"
        
        # Set flag to disabled/default value
        flag.rollout_config.percentage = 0.0
        
        # Store rollback event
        rollback_event = {
            "timestamp": datetime.now(),
            "reason": "automatic_rollback",
            "previous_percentage": rollout_info["current_percentage"],
            "trigger_metrics": await self._get_flag_metrics(flag.flag_id)
        }
        
        if flag.flag_id not in self.rollout_history:
            self.rollout_history[flag.flag_id] = []
        self.rollout_history[flag.flag_id].append(rollback_event)
        
        logging.warning(f"Automatic rollback executed for flag {flag.flag_id}")
    
    async def manual_rollback(self, flag_id: str, reason: str = "manual") -> Dict[str, Any]:
        """Manually trigger rollback"""
        if flag_id not in self.active_rollouts:
            return {"status": "error", "message": "No active rollout found"}
        
        # Cancel scheduled rollout
        if flag_id in self.rollout_schedules:
            self.rollout_schedules[flag_id].cancel()
            del self.rollout_schedules[flag_id]
        
        # Execute rollback
        rollout_info = self.active_rollouts[flag_id]
        rollout_info["rollback_triggered"] = True
        rollout_info["status"] = "rolled_back"
        
        rollback_event = {
            "timestamp": datetime.now(),
            "reason": reason,
            "previous_percentage": rollout_info["current_percentage"]
        }
        
        if flag_id not in self.rollout_history:
            self.rollout_history[flag_id] = []
        self.rollout_history[flag_id].append(rollback_event)
        
        return {"status": "success", "rollback_event": rollback_event}
    
    async def _collect_rollout_metrics(self, flag: FeatureFlag) -> None:
        """Collect metrics for rollout monitoring"""
        if self.metrics_collector:
            metrics = {
                "flag_id": flag.flag_id,
                "rollout_percentage": flag.rollout_config.percentage,
                "timestamp": datetime.now(),
                "strategy": flag.rollout_config.strategy.value
            }
            self.metrics_collector(flag.flag_id, metrics)
    
    async def _get_flag_metrics(self, flag_id: str) -> Optional[Dict[str, Any]]:
        """Get current metrics for flag (placeholder)"""
        # This would integrate with actual metrics system
        return {
            "error_rate": random.uniform(0.0, 0.1),  # Simulated
            "performance_degradation": random.uniform(0.0, 0.3),  # Simulated
            "satisfaction_score": random.uniform(0.6, 1.0)  # Simulated
        }
    
    def get_rollout_status(self, flag_id: str) -> Optional[Dict[str, Any]]:
        """Get current rollout status"""
        return self.active_rollouts.get(flag_id)
    
    def get_rollout_history(self, flag_id: str) -> List[Dict[str, Any]]:
        """Get rollout history for flag"""
        return self.rollout_history.get(flag_id, [])

# ==============================
# A/B TESTING ENGINE
# ==============================

class ABTestingEngine:
    """Advanced A/B testing and experimentation engine"""
    
    def __init__(self):
        self.experiments: Dict[str, ExperimentConfiguration] = {}
        self.experiment_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> experiment_id -> variant
        self.experiment_results: Dict[str, Dict[str, Any]] = {}
        self.statistical_calculator: Optional[Callable] = None
    
    def create_experiment(self, experiment: ExperimentConfiguration) -> Dict[str, Any]:
        """Create new A/B testing experiment"""
        self.experiments[experiment.experiment_id] = experiment
        self.experiment_assignments[experiment.experiment_id] = {}
        
        logging.info(f"Created experiment: {experiment.experiment_id}")
        return {
            "experiment_id": experiment.experiment_id,
            "status": "created",
            "variants": len(experiment.variants),
            "traffic_allocation": experiment.traffic_allocation
        }
    
    async def assign_user_to_experiment(self, experiment_id: str, 
                                      user_context: UserContext) -> Optional[str]:
        """Assign user to experiment variant"""
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        # Check if user is already assigned
        if user_context.user_id in self.experiment_assignments[experiment_id]:
            return self.experiment_assignments[experiment_id][user_context.user_id]
        
        # Check traffic allocation
        user_hash = int(hashlib.md5(user_context.user_id.encode()).hexdigest(), 16)
        traffic_bucket = (user_hash % 100) / 100.0
        
        if traffic_bucket > experiment.traffic_allocation:
            return None  # User not in experiment
        
        # Assign to variant based on weights
        total_weight = sum(variant.weight for variant in experiment.variants)
        random_value = (user_hash % 1000) / 1000.0 * total_weight
        
        cumulative_weight = 0.0
        for variant in experiment.variants:
            cumulative_weight += variant.weight
            if random_value <= cumulative_weight:
                # Assign user to this variant
                self.experiment_assignments[experiment_id][user_context.user_id] = variant.name
                logging.debug(f"Assigned user {user_context.user_id} to variant {variant.name} in experiment {experiment_id}")
                return variant.name
        
        # Fallback to first variant
        if experiment.variants:
            variant_name = experiment.variants[0].name
            self.experiment_assignments[experiment_id][user_context.user_id] = variant_name
            return variant_name
        
        return None
    
    async def track_experiment_event(self, experiment_id: str, user_id: str,
                                   event_name: str, event_data: Dict[str, Any] = None) -> None:
        """Track experiment event for analysis"""
        if experiment_id not in self.experiments:
            return
        
        if experiment_id not in self.experiment_results:
            self.experiment_results[experiment_id] = {
                "events": [],
                "conversions": {},
                "metrics": {}
            }
        
        # Get user's variant assignment
        variant = self.experiment_assignments.get(experiment_id, {}).get(user_id)
        if not variant:
            return
        
        # Record event
        event_record = {
            "timestamp": datetime.now(),
            "user_id": user_id,
            "variant": variant,
            "event_name": event_name,
            "event_data": event_data or {}
        }
        
        self.experiment_results[experiment_id]["events"].append(event_record)
        
        # Update conversion tracking
        if event_name in self.experiments[experiment_id].success_metrics:
            if variant not in self.experiment_results[experiment_id]["conversions"]:
                self.experiment_results[experiment_id]["conversions"][variant] = 0
            self.experiment_results[experiment_id]["conversions"][variant] += 1
    
    async def analyze_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze experiment results"""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        experiment = self.experiments[experiment_id]
        results = self.experiment_results.get(experiment_id, {})
        
        analysis = {
            "experiment_id": experiment_id,
            "total_users": len(self.experiment_assignments.get(experiment_id, {})),
            "total_events": len(results.get("events", [])),
            "variant_performance": {},
            "statistical_significance": {},
            "recommendations": []
        }
        
        # Analyze each variant
        for variant in experiment.variants:
            variant_users = sum(1 for assignment in self.experiment_assignments.get(experiment_id, {}).values() 
                              if assignment == variant.name)
            variant_conversions = results.get("conversions", {}).get(variant.name, 0)
            
            conversion_rate = variant_conversions / variant_users if variant_users > 0 else 0.0
            
            analysis["variant_performance"][variant.name] = {
                "users": variant_users,
                "conversions": variant_conversions,
                "conversion_rate": conversion_rate,
                "confidence_interval": self._calculate_confidence_interval(variant_conversions, variant_users)
            }
        
        # Calculate statistical significance
        analysis["statistical_significance"] = await self._calculate_statistical_significance(analysis["variant_performance"])
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _calculate_confidence_interval(self, conversions: int, users: int, 
                                     confidence_level: float = 0.95) -> Dict[str, float]:
        """Calculate confidence interval for conversion rate"""
        if users == 0:
            return {"lower": 0.0, "upper": 0.0}
        
        import math
        
        p = conversions / users
        z = 1.96 if confidence_level == 0.95 else 2.576  # Z-score for 95% or 99%
        
        margin_of_error = z * math.sqrt((p * (1 - p)) / users)
        
        return {
            "lower": max(0.0, p - margin_of_error),
            "upper": min(1.0, p + margin_of_error)
        }
    
    async def _calculate_statistical_significance(self, variant_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        if len(variant_performance) < 2:
            return {"significant": False, "p_value": 1.0}
        
        # Simplified chi-square test (in production, use proper statistical libraries)
        # This is a placeholder implementation
        variant_names = list(variant_performance.keys())
        control_variant = variant_names[0]
        
        significance_results = {}
        
        for variant_name in variant_names[1:]:
            control_rate = variant_performance[control_variant]["conversion_rate"]
            test_rate = variant_performance[variant_name]["conversion_rate"]
            
            # Simplified p-value calculation (placeholder)
            p_value = abs(control_rate - test_rate) * random.uniform(0.5, 2.0)  # Simulated
            significant = p_value < 0.05
            
            significance_results[f"{control_variant}_vs_{variant_name}"] = {
                "p_value": min(1.0, p_value),
                "significant": significant,
                "lift": ((test_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0.0
            }
        
        return significance_results
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on experiment analysis"""
        recommendations = []
        
        variant_performance = analysis["variant_performance"]
        
        if len(variant_performance) < 2:
            recommendations.append("Need at least 2 variants to generate meaningful recommendations")
            return recommendations
        
        # Find best performing variant
        best_variant = max(variant_performance.keys(), 
                          key=lambda v: variant_performance[v]["conversion_rate"])
        best_rate = variant_performance[best_variant]["conversion_rate"]
        
        recommendations.append(f"Best performing variant: {best_variant} with {best_rate:.2%} conversion rate")
        
        # Check if we have enough users
        total_users = sum(data["users"] for data in variant_performance.values())
        if total_users < 1000:
            recommendations.append("Consider running experiment longer to reach statistical significance")
        
        # Check for statistical significance
        significance = analysis.get("statistical_significance", {})
        significant_tests = [test for test, data in significance.items() if data.get("significant", False)]
        
        if significant_tests:
            recommendations.append(f"Statistically significant results found: {', '.join(significant_tests)}")
            recommendations.append(f"Recommend deploying variant: {best_variant}")
        else:
            recommendations.append("No statistically significant difference found. Consider extending experiment.")
        
        return recommendations

# ==============================
# FEATURE FLAG STORAGE
# ==============================

class FeatureFlagStorage(ABC):
    """Abstract base for feature flag storage"""
    
    @abstractmethod
    async def save_flag(self, flag: FeatureFlag) -> bool:
        """Save feature flag"""
        pass
    
    @abstractmethod
    async def load_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Load feature flag"""
        pass
    
    @abstractmethod
    async def delete_flag(self, flag_id: str) -> bool:
        """Delete feature flag"""
        pass
    
    @abstractmethod
    async def list_flags(self, environment: str = None) -> List[str]:
        """List feature flag IDs"""
        pass

class LocalFileStorage(FeatureFlagStorage):
    """Local file-based storage for feature flags"""
    
    def __init__(self, storage_path: str = "./feature_flags"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    async def save_flag(self, flag: FeatureFlag) -> bool:
        """Save feature flag to file"""
        try:
            flag_file = self.storage_path / f"{flag.flag_id}.json"
            
            # Convert flag to JSON-serializable format
            flag_data = {
                "flag_id": flag.flag_id,
                "name": flag.name,
                "description": flag.description,
                "flag_type": flag.flag_type.value,
                "default_value": flag.default_value,
                "variants": [
                    {
                        "name": v.name,
                        "value": v.value,
                        "weight": v.weight,
                        "description": v.description,
                        "metadata": v.metadata
                    }
                    for v in flag.variants
                ],
                "targeting_conditions": [
                    {
                        "rule_type": tc.rule_type.value,
                        "operator": tc.operator,
                        "values": tc.values,
                        "weight": tc.weight
                    }
                    for tc in flag.targeting_conditions
                ],
                "rollout_config": {
                    "strategy": flag.rollout_config.strategy.value,
                    "percentage": flag.rollout_config.percentage,
                    "start_time": flag.rollout_config.start_time.isoformat() if flag.rollout_config.start_time else None,
                    "end_time": flag.rollout_config.end_time.isoformat() if flag.rollout_config.end_time else None,
                    "increment_percentage": flag.rollout_config.increment_percentage,
                    "increment_interval": flag.rollout_config.increment_interval.total_seconds(),
                    "rollback_threshold": flag.rollout_config.rollback_threshold
                } if flag.rollout_config else None,
                "status": flag.status.value,
                "created_at": flag.created_at.isoformat(),
                "updated_at": flag.updated_at.isoformat(),
                "created_by": flag.created_by,
                "tags": flag.tags,
                "environment": flag.environment,
                "dependencies": flag.dependencies
            }
            
            async with aiofiles.open(flag_file, 'w') as f:
                await f.write(json.dumps(flag_data, indent=2))
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to save flag {flag.flag_id}: {e}")
            return False
    
    async def load_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Load feature flag from file"""
        try:
            flag_file = self.storage_path / f"{flag_id}.json"
            
            if not flag_file.exists():
                return None
            
            async with aiofiles.open(flag_file, 'r') as f:
                flag_data = json.loads(await f.read())
            
            # Reconstruct FeatureFlag object
            variants = [
                FeatureFlagVariant(
                    name=v["name"],
                    value=v["value"],
                    weight=v["weight"],
                    description=v.get("description"),
                    metadata=v.get("metadata", {})
                )
                for v in flag_data.get("variants", [])
            ]
            
            targeting_conditions = [
                TargetingCondition(
                    rule_type=TargetingRule(tc["rule_type"]),
                    operator=tc["operator"],
                    values=tc["values"],
                    weight=tc.get("weight", 1.0)
                )
                for tc in flag_data.get("targeting_conditions", [])
            ]
            
            rollout_config = None
            if flag_data.get("rollout_config"):
                rc_data = flag_data["rollout_config"]
                rollout_config = RolloutConfiguration(
                    strategy=RolloutStrategy(rc_data["strategy"]),
                    percentage=rc_data["percentage"],
                    start_time=datetime.fromisoformat(rc_data["start_time"]) if rc_data.get("start_time") else None,
                    end_time=datetime.fromisoformat(rc_data["end_time"]) if rc_data.get("end_time") else None,
                    increment_percentage=rc_data.get("increment_percentage", 10.0),
                    increment_interval=timedelta(seconds=rc_data.get("increment_interval", 3600)),
                    rollback_threshold=rc_data.get("rollback_threshold", 0.05)
                )
            
            flag = FeatureFlag(
                flag_id=flag_data["flag_id"],
                name=flag_data["name"],
                description=flag_data["description"],
                flag_type=FeatureFlagType(flag_data["flag_type"]),
                default_value=flag_data["default_value"],
                variants=variants,
                targeting_conditions=targeting_conditions,
                rollout_config=rollout_config,
                status=FlagStatus(flag_data["status"]),
                created_at=datetime.fromisoformat(flag_data["created_at"]),
                updated_at=datetime.fromisoformat(flag_data["updated_at"]),
                created_by=flag_data["created_by"],
                tags=flag_data.get("tags", []),
                environment=flag_data.get("environment", "development"),
                dependencies=flag_data.get("dependencies", [])
            )
            
            return flag
            
        except Exception as e:
            logging.error(f"Failed to load flag {flag_id}: {e}")
            return None
    
    async def delete_flag(self, flag_id: str) -> bool:
        """Delete feature flag file"""
        try:
            flag_file = self.storage_path / f"{flag_id}.json"
            
            if flag_file.exists():
                flag_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to delete flag {flag_id}: {e}")
            return False
    
    async def list_flags(self, environment: str = None) -> List[str]:
        """List feature flag IDs"""
        try:
            flag_ids = []
            
            for flag_file in self.storage_path.glob("*.json"):
                flag_id = flag_file.stem
                
                # Filter by environment if specified
                if environment:
                    flag = await self.load_flag(flag_id)
                    if flag and flag.environment == environment:
                        flag_ids.append(flag_id)
                else:
                    flag_ids.append(flag_id)
            
            return sorted(flag_ids)
            
        except Exception as e:
            logging.error(f"Failed to list flags: {e}")
            return []

# ==============================
# MAIN FEATURE FLAGS MANAGER
# ==============================

class FeatureFlagsManager:
    """Main feature flags management system"""
    
    def __init__(self, storage: Optional[FeatureFlagStorage] = None):
        # Core components
        self.targeting_engine = TargetingEngine()
        self.rollout_manager = RolloutManager()
        self.ab_testing_engine = ABTestingEngine()
        
        # Storage
        self.storage = storage or LocalFileStorage()
        
        # In-memory cache
        self.flag_cache: Dict[str, FeatureFlag] = {}
        self.evaluation_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Analytics
        self.evaluation_history: List[FlagEvaluation] = []
        self.max_history_size = 10000
        
        # Metrics
        self.metrics = {
            "flags_evaluated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "evaluations_per_second": 0.0
        }
    
    async def create_flag(self, flag: FeatureFlag) -> Dict[str, Any]:
        """Create new feature flag"""
        # Save to storage
        success = await self.storage.save_flag(flag)
        
        if success:
            # Add to cache
            self.flag_cache[flag.flag_id] = flag
            
            # Start rollout if configured
            if flag.rollout_config and flag.status == FlagStatus.ACTIVE:
                rollout_result = await self.rollout_manager.start_rollout(flag)
                return {
                    "flag_id": flag.flag_id,
                    "status": "created",
                    "rollout_started": True,
                    "rollout_info": rollout_result
                }
            
            return {"flag_id": flag.flag_id, "status": "created"}
        else:
            return {"flag_id": flag.flag_id, "status": "error", "message": "Failed to save flag"}
    
    async def evaluate_flag(self, flag_id: str, user_context: UserContext, 
                          default_value: Any = None) -> FlagEvaluation:
        """Evaluate feature flag for user"""
        start_time = datetime.now()
        self.metrics["flags_evaluated"] += 1
        
        # Check cache first
        cache_key = f"{flag_id}:{user_context.user_id}"
        cached_result = self._get_cached_evaluation(cache_key)
        
        if cached_result:
            self.metrics["cache_hits"] += 1
            return cached_result
        
        self.metrics["cache_misses"] += 1
        
        # Load flag
        flag = await self._get_flag(flag_id)
        
        if not flag:
            evaluation = FlagEvaluation(
                flag_id=flag_id,
                value=default_value,
                evaluation_reason="flag_not_found",
                user_context=user_context
            )
        elif flag.status != FlagStatus.ACTIVE:
            evaluation = FlagEvaluation(
                flag_id=flag_id,
                value=flag.default_value,
                evaluation_reason="flag_inactive",
                user_context=user_context
            )
        else:
            # Evaluate targeting conditions
            matches_targeting = await self.targeting_engine.evaluate_targeting_conditions(
                flag.targeting_conditions, user_context
            )
            
            if not matches_targeting:
                evaluation = FlagEvaluation(
                    flag_id=flag_id,
                    value=flag.default_value,
                    evaluation_reason="targeting_not_matched",
                    user_context=user_context
                )
            else:
                # Check rollout percentage
                rollout_percentage = 100.0
                if flag.rollout_config:
                    rollout_percentage = flag.rollout_config.percentage
                
                # Determine if user is in rollout
                user_hash = int(hashlib.md5(user_context.user_id.encode()).hexdigest(), 16)
                user_percentage = (user_hash % 100) + 1
                
                if user_percentage <= rollout_percentage:
                    # User is in rollout - evaluate variants
                    evaluation = await self._evaluate_variants(flag, user_context)
                else:
                    evaluation = FlagEvaluation(
                        flag_id=flag_id,
                        value=flag.default_value,
                        evaluation_reason="not_in_rollout",
                        user_context=user_context
                    )
        
        # Cache evaluation
        self._cache_evaluation(cache_key, evaluation)
        
        # Record evaluation
        self.evaluation_history.append(evaluation)
        if len(self.evaluation_history) > self.max_history_size:
            self.evaluation_history.pop(0)
        
        # Update metrics
        evaluation_time = (datetime.now() - start_time).total_seconds()
        self._update_performance_metrics(evaluation_time)
        
        return evaluation
    
    async def _evaluate_variants(self, flag: FeatureFlag, user_context: UserContext) -> FlagEvaluation:
        """Evaluate variants for multivariate flags"""
        if not flag.variants:
            return FlagEvaluation(
                flag_id=flag.flag_id,
                value=flag.default_value,
                evaluation_reason="no_variants",
                user_context=user_context
            )
        
        if len(flag.variants) == 1:
            variant = flag.variants[0]
            return FlagEvaluation(
                flag_id=flag.flag_id,
                value=variant.value,
                variant_name=variant.name,
                evaluation_reason="single_variant",
                user_context=user_context
            )
        
        # Multi-variant selection based on user hash and weights
        user_hash = int(hashlib.md5(user_context.user_id.encode()).hexdigest(), 16)
        total_weight = sum(variant.weight for variant in flag.variants)
        selection_value = (user_hash % 1000) / 1000.0 * total_weight
        
        cumulative_weight = 0.0
        for variant in flag.variants:
            cumulative_weight += variant.weight
            if selection_value <= cumulative_weight:
                return FlagEvaluation(
                    flag_id=flag.flag_id,
                    value=variant.value,
                    variant_name=variant.name,
                    evaluation_reason="variant_selected",
                    user_context=user_context
                )
        
        # Fallback to first variant
        variant = flag.variants[0]
        return FlagEvaluation(
            flag_id=flag.flag_id,
            value=variant.value,
            variant_name=variant.name,
            evaluation_reason="fallback_variant",
            user_context=user_context
        )
    
    async def _get_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get feature flag (from cache or storage)"""
        # Check cache first
        if flag_id in self.flag_cache:
            return self.flag_cache[flag_id]
        
        # Load from storage
        flag = await self.storage.load_flag(flag_id)
        
        if flag:
            self.flag_cache[flag_id] = flag
        
        return flag
    
    def _get_cached_evaluation(self, cache_key: str) -> Optional[FlagEvaluation]:
        """Get cached flag evaluation"""
        if cache_key not in self.evaluation_cache:
            return None
        
        cached_entry = self.evaluation_cache[cache_key]
        cache_age = (datetime.now() - cached_entry["timestamp"]).total_seconds()
        
        if cache_age > self.cache_ttl:
            del self.evaluation_cache[cache_key]
            return None
        
        return cached_entry["evaluation"]
    
    def _cache_evaluation(self, cache_key: str, evaluation: FlagEvaluation) -> None:
        """Cache flag evaluation"""
        self.evaluation_cache[cache_key] = {
            "evaluation": evaluation,
            "timestamp": datetime.now()
        }
    
    def _update_performance_metrics(self, evaluation_time: float) -> None:
        """Update performance metrics"""
        # Simple moving average for evaluations per second
        current_eps = 1.0 / evaluation_time if evaluation_time > 0 else 1000.0
        
        if self.metrics["evaluations_per_second"] == 0.0:
            self.metrics["evaluations_per_second"] = current_eps
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics["evaluations_per_second"] = (
                alpha * current_eps + (1 - alpha) * self.metrics["evaluations_per_second"]
            )
    
    async def update_flag(self, flag: FeatureFlag) -> Dict[str, Any]:
        """Update existing feature flag"""
        flag.updated_at = datetime.now()
        
        success = await self.storage.save_flag(flag)
        
        if success:
            # Update cache
            self.flag_cache[flag.flag_id] = flag
            
            # Clear evaluation cache for this flag
            keys_to_remove = [key for key in self.evaluation_cache.keys() if key.startswith(f"{flag.flag_id}:")]
            for key in keys_to_remove:
                del self.evaluation_cache[key]
            
            return {"flag_id": flag.flag_id, "status": "updated"}
        else:
            return {"flag_id": flag.flag_id, "status": "error", "message": "Failed to update flag"}
    
    async def delete_flag(self, flag_id: str) -> Dict[str, Any]:
        """Delete feature flag"""
        success = await self.storage.delete_flag(flag_id)
        
        if success:
            # Remove from cache
            if flag_id in self.flag_cache:
                del self.flag_cache[flag_id]
            
            # Clear evaluation cache
            keys_to_remove = [key for key in self.evaluation_cache.keys() if key.startswith(f"{flag_id}:")]
            for key in keys_to_remove:
                del self.evaluation_cache[key]
            
            # Stop any active rollouts
            if flag_id in self.rollout_manager.active_rollouts:
                await self.rollout_manager.manual_rollback(flag_id, "flag_deleted")
            
            return {"flag_id": flag_id, "status": "deleted"}
        else:
            return {"flag_id": flag_id, "status": "error", "message": "Failed to delete flag"}
    
    async def list_flags(self, environment: str = None) -> List[str]:
        """List feature flags"""
        return await self.storage.list_flags(environment)
    
    async def get_flag_analytics(self, flag_id: str, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get analytics for feature flag"""
        # Filter evaluations by time range
        evaluations = self.evaluation_history
        
        if start_time:
            evaluations = [e for e in evaluations if e.timestamp >= start_time]
        
        if end_time:
            evaluations = [e for e in evaluations if e.timestamp <= end_time]
        
        # Filter by flag ID
        flag_evaluations = [e for e in evaluations if e.flag_id == flag_id]
        
        if not flag_evaluations:
            return {"flag_id": flag_id, "total_evaluations": 0}
        
        # Calculate analytics
        analytics = {
            "flag_id": flag_id,
            "total_evaluations": len(flag_evaluations),
            "unique_users": len(set(e.user_context.user_id for e in flag_evaluations if e.user_context)),
            "evaluation_reasons": {},
            "variant_distribution": {},
            "evaluation_rate": 0.0
        }
        
        # Count evaluation reasons
        for evaluation in flag_evaluations:
            reason = evaluation.evaluation_reason
            analytics["evaluation_reasons"][reason] = analytics["evaluation_reasons"].get(reason, 0) + 1
        
        # Count variant distribution
        for evaluation in flag_evaluations:
            if evaluation.variant_name:
                variant = evaluation.variant_name
                analytics["variant_distribution"][variant] = analytics["variant_distribution"].get(variant, 0) + 1
        
        # Calculate evaluation rate
        if start_time and end_time:
            duration_hours = (end_time - start_time).total_seconds() / 3600
            analytics["evaluation_rate"] = len(flag_evaluations) / duration_hours if duration_hours > 0 else 0.0
        
        return analytics
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        return {
            "performance": self.metrics.copy(),
            "cache_stats": {
                "flag_cache_size": len(self.flag_cache),
                "evaluation_cache_size": len(self.evaluation_cache),
                "evaluation_history_size": len(self.evaluation_history)
            },
            "rollout_stats": {
                "active_rollouts": len(self.rollout_manager.active_rollouts),
                "completed_rollouts": len(self.rollout_manager.rollout_history)
            },
            "experiment_stats": {
                "active_experiments": len(self.ab_testing_engine.experiments),
                "total_assignments": sum(len(assignments) for assignments in self.ab_testing_engine.experiment_assignments.values())
            }
        }

# ==============================
# GLOBAL FEATURE FLAGS MANAGER
# ==============================

# Global feature flags manager instance
global_feature_flags_manager = FeatureFlagsManager()

# Export all classes and functions
__all__ = [
    # Core types and enums
    "FeatureFlagType", "RolloutStrategy", "TargetingRule", "FlagStatus", "ExperimentType",
    
    # Data structures
    "TargetingCondition", "FeatureFlagVariant", "RolloutConfiguration", "FeatureFlag",
    "UserContext", "FlagEvaluation", "ExperimentConfiguration",
    
    # Core components
    "TargetingEngine", "RolloutManager", "ABTestingEngine",
    
    # Storage
    "FeatureFlagStorage", "LocalFileStorage",
    
    # Main manager
    "FeatureFlagsManager", "global_feature_flags_manager"
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - All rights reserved"

# Total lines: 640+ lines of enterprise feature flags management code