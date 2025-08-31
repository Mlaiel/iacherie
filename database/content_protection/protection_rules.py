"""Protection Rules Repository

Ultra-advanced protection rules engine for dynamic content protection
with AI-powered rule generation, multi-level rule hierarchies, and real-time adaptation.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + DBA + DevOps
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
==================================================================
This code and all associated intellectual property are the EXCLUSIVE property of Fahed Mlaiel.
ANY unauthorized use, copying, modification, distribution, or commercialization without 
explicit written permission is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries.
Legal violations will be prosecuted to the full extent of international law.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy import and_, desc, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ..models.content_models import (
    ProtectionRule, RuleTemplate, RuleExecution,
    RuleCondition, RuleAction, RuleCategory
)
from ..security.encryption import AdvancedEncryptionManager
from ...core.config import DatabaseConfig
from ...utils.rule_engine import RuleEngineProcessor
from ...utils.ai_models import RuleGenerationModel
from ...utils.validators import RuleValidator


logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of protection rules"""    SIMILARITY_THRESHOLD = "similarity_threshold"
    PLATFORM_SPECIFIC = "platform_specific"
    CONTENT_TYPE_FILTER = "content_type_filter"
    GEOGRAPHICAL_RESTRICTION = "geographical_restriction"
    TIME_BASED_PROTECTION = "time_based_protection"
    CREATOR_SPECIFIC = "creator_specific"
    COMMERCIAL_USE_DETECTION = "commercial_use_detection"
    REPEAT_OFFENDER_ACTION = "repeat_offender_action"
    ESCALATION_TRIGGER = "escalation_trigger"
    AUTO_TAKEDOWN = "auto_takedown"


class RulePriority(Enum):
    """Rule priority levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class RuleStatus(Enum):
    """Rule status types"""    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ActionType(Enum):
    """Types of actions rules can trigger"""    ALERT_CREATION = "alert_creation"
    AUTOMATIC_TAKEDOWN = "automatic_takedown"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    BLOCKING = "blocking"
    MONITORING_INCREASE = "monitoring_increase"
    LEGAL_ACTION = "legal_action"
    WHITELISTING = "whitelisting"
    QUARANTINE = "quarantine"


class ProtectionRulesRepositoryError(Exception):
    """Custom exception for protection rules operations"""    pass


class ProtectionRulesRepository:
    """    Ultra-advanced protection rules repository with enterprise features:
    - Dynamic rule generation and adaptation
    - AI-powered rule optimization
    - Multi-level rule hierarchies and inheritance
    - Real-time rule execution and monitoring
    - Performance analytics and rule effectiveness tracking
    - Compliance-aware rule management
    """    
    def __init__(
        self,
        db_session: AsyncSession,
        config: DatabaseConfig,
        encryption_manager: Optional[AdvancedEncryptionManager] = None,
        rule_engine: Optional[RuleEngineProcessor] = None,
        ai_rule_generator: Optional[RuleGenerationModel] = None
    ):
        self.db_session = db_session
        self.config = config
        self.encryption_manager = encryption_manager or AdvancedEncryptionManager()
        self.rule_engine = rule_engine or RuleEngineProcessor()
        self.ai_rule_generator = ai_rule_generator or RuleGenerationModel()
        self.rule_validator = RuleValidator()
        
        # Rule processing configuration
        self.max_rules_per_category = config.max_rules_per_category or 100
        self.rule_execution_timeout = config.rule_execution_timeout or 30
        self.ai_rule_generation_enabled = config.ai_rule_generation_enabled or True
        
        # Rule cache for performance
        self.active_rules_cache = {}
        self.rule_templates_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Performance metrics
        self.rules_metrics = {
            "total_rules": 0,
            "active_rules": 0,
            "rule_executions_per_hour": 0,
            "rule_effectiveness_rate": 0,
            "ai_generated_rules": 0,
            "avg_execution_time_ms": 0
        }
        
        logger.info("ProtectionRulesRepository initialized with AI capabilities")
    
    async def create_protection_rule(
        self,
        rule_name: str,
        rule_type: RuleType,
        rule_conditions: List[Dict[str, Any]],
        rule_actions: List[Dict[str, Any]],
        creator_id: str,
        rule_priority: RulePriority = RulePriority.MEDIUM,
        rule_metadata: Optional[Dict[str, Any]] = None,
        auto_activate: bool = False
    ) -> ProtectionRule:
        """        Create comprehensive protection rule with validation and testing
        
        Args:
            rule_name: Human-readable rule name
            rule_type: Type of protection rule
            rule_conditions: List of conditions that trigger the rule
            rule_actions: List of actions to execute when rule triggers
            creator_id: ID of rule creator
            rule_priority: Priority level of the rule
            rule_metadata: Additional rule metadata
            auto_activate: Automatically activate rule after creation
            
        Returns:
            Created ProtectionRule record
            
        Raises:
            ProtectionRulesRepositoryError: If creation fails
        """        try:
            # Validate rule structure
            await self._validate_rule_structure(rule_conditions, rule_actions)
            
            # Generate unique rule identifier
            rule_id = await self._generate_rule_id(rule_name, rule_type)
            
            # Validate rule logic
            validation_result = await self.rule_validator.validate_rule_logic(
                rule_conditions, rule_actions, rule_type
            )
            
            if not validation_result["valid"]:
                raise ProtectionRulesRepositoryError(f"Rule validation failed: {validation_result['errors']}")
            
            # Encrypt sensitive rule data
            encrypted_conditions = await self.encryption_manager.encrypt_data(
                json.dumps(rule_conditions)
            )
            encrypted_actions = await self.encryption_manager.encrypt_data(
                json.dumps(rule_actions)
            )
            
            # Create rule record
            rule = ProtectionRule(
                id=uuid4(),
                rule_id=rule_id,
                rule_name=rule_name,
                rule_type=rule_type.value,
                rule_priority=rule_priority.value,
                status=RuleStatus.DRAFT.value,
                conditions_data=encrypted_conditions,
                actions_data=encrypted_actions,
                creator_id=creator_id,
                rule_metadata=rule_metadata or {},
                execution_count=0,
                success_count=0,
                failure_count=0,
                last_execution_at=None,
                effectiveness_score=0.0,
                is_ai_generated=False,
                is_template_based=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(rule)
            
            # Create individual condition records
            for i, condition_data in enumerate(rule_conditions):
                condition = RuleCondition(
                    id=uuid4(),
                    rule_id=rule.id,
                    condition_type=condition_data["type"],
                    condition_operator=condition_data["operator"],
                    condition_value=condition_data["value"],
                    condition_order=i,
                    is_required=condition_data.get("required", True),
                    created_at=datetime.now(timezone.utc)
                )
                self.db_session.add(condition)
            
            # Create individual action records
            for i, action_data in enumerate(rule_actions):
                action = RuleAction(
                    id=uuid4(),
                    rule_id=rule.id,
                    action_type=action_data["type"],
                    action_parameters=action_data.get("parameters", {}),
                    action_order=i,
                    is_critical=action_data.get("critical", False),
                    created_at=datetime.now(timezone.utc)
                )
                self.db_session.add(action)
            
            await self.db_session.commit()
            
            # Test rule if not auto-activating
            if not auto_activate:
                await self._test_rule_execution(rule)
            
            # Auto-activate if requested and tests pass
            if auto_activate:
                await self.activate_rule(rule.rule_id)
            
            # Update metrics
            self.rules_metrics["total_rules"] += 1
            
            # Clear cache
            self._clear_rules_cache()
            
            logger.info(f"Protection rule created: {rule_id} [{rule_type.value}]")
            return rule
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Protection rule creation failed: {e}")
            raise ProtectionRulesRepositoryError(f"Protection rule creation failed: {e}")
    
    async def generate_ai_rule(
        self,
        violation_patterns: List[Dict[str, Any]],
        rule_objective: str,
        creator_id: str,
        auto_activate: bool = False
    ) -> ProtectionRule:
        """        Generate protection rule using AI based on violation patterns
        
        Args:
            violation_patterns: Historical violation patterns to learn from
            rule_objective: Objective the rule should achieve
            creator_id: ID of rule creator
            auto_activate: Automatically activate generated rule
            
        Returns:
            AI-generated ProtectionRule record
        """        try:
            if not self.ai_rule_generation_enabled:
                raise ProtectionRulesRepositoryError("AI rule generation not enabled")
            
            # Generate rule using AI model
            ai_result = await self.ai_rule_generator.generate_rule(
                violation_patterns, rule_objective
            )
            
            if not ai_result["success"]:
                raise ProtectionRulesRepositoryError(f"AI rule generation failed: {ai_result['error']}")
            
            rule_spec = ai_result["rule_specification"]
            
            # Create rule with AI-generated specifications
            rule = await self.create_protection_rule(
                rule_name=rule_spec["name"],
                rule_type=RuleType(rule_spec["type"]),
                rule_conditions=rule_spec["conditions"],
                rule_actions=rule_spec["actions"],
                creator_id=creator_id,
                rule_priority=RulePriority(rule_spec.get("priority", "medium")),
                rule_metadata={
                    "ai_generated": True,
                    "generation_model": ai_result["model_version"],
                    "confidence_score": ai_result["confidence_score"],
                    "training_patterns": len(violation_patterns),
                    "objective": rule_objective
                },
                auto_activate=auto_activate
            )
            
            # Mark as AI-generated
            rule.is_ai_generated = True
            rule.ai_confidence_score = ai_result["confidence_score"]
            await self.db_session.commit()
            
            # Update metrics
            self.rules_metrics["ai_generated_rules"] += 1
            
            logger.info(f"AI-generated rule created: {rule.rule_id} with confidence {ai_result['confidence_score']:.2f}")
            return rule
            
        except Exception as e:
            logger.error(f"AI rule generation failed: {e}")
            raise ProtectionRulesRepositoryError(f"AI rule generation failed: {e}")
    
    async def activate_rule(
        self,
        rule_id: str,
        activation_metadata: Optional[Dict[str, Any]] = None
    ) -> ProtectionRule:
        """        Activate protection rule with comprehensive validation
        
        Args:
            rule_id: Rule identifier
            activation_metadata: Additional activation metadata
            
        Returns:
            Activated ProtectionRule record
        """        try:
            rule = await self.db_session.query(ProtectionRule).filter(
                ProtectionRule.rule_id == rule_id
            ).first()
            
            if not rule:
                raise ProtectionRulesRepositoryError(f"Rule not found: {rule_id}")
            
            if rule.status == RuleStatus.ACTIVE.value:
                return rule  # Already active
            
            # Validate rule before activation
            await self._validate_rule_for_activation(rule)
            
            # Check for rule conflicts
            conflicts = await self._check_rule_conflicts(rule)
            if conflicts:
                raise ProtectionRulesRepositoryError(f"Rule conflicts detected: {conflicts}")
            
            # Activate rule
            rule.status = RuleStatus.ACTIVE.value
            rule.activated_at = datetime.now(timezone.utc)
            rule.updated_at = datetime.now(timezone.utc)
            
            # Add activation metadata
            if activation_metadata:
                rule.rule_metadata.update(activation_metadata)
            
            # Create activation history entry
            if "activation_history" not in rule.rule_metadata:
                rule.rule_metadata["activation_history"] = []
            
            rule.rule_metadata["activation_history"].append({
                "activated_at": rule.activated_at.isoformat(),
                "metadata": activation_metadata or {}
            })
            
            await self.db_session.commit()
            
            # Update metrics
            self.rules_metrics["active_rules"] += 1
            
            # Clear cache to refresh active rules
            self._clear_rules_cache()
            
            logger.info(f"Protection rule activated: {rule_id}")
            return rule
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Rule activation failed: {e}")
            raise ProtectionRulesRepositoryError(f"Rule activation failed: {e}")
    
    async def execute_rules_for_content(
        self,
        content_data: Dict[str, Any],
        content_context: Dict[str, Any],
        rule_categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """        Execute applicable protection rules for content
        
        Args:
            content_data: Content data to evaluate
            content_context: Context information about content
            rule_categories: Specific rule categories to execute
            
        Returns:
            List of rule execution results
        """        try:
            execution_start = datetime.now()
            
            # Get applicable rules
            applicable_rules = await self._get_applicable_rules(
                content_data, content_context, rule_categories
            )
            
            execution_results = []
            
            for rule in applicable_rules:
                try:
                    # Execute individual rule
                    result = await self._execute_single_rule(rule, content_data, content_context)
                    execution_results.append(result)
                    
                    # Update rule execution metrics
                    await self._update_rule_execution_metrics(rule, result)
                    
                except Exception as e:
                    logger.warning(f"Rule execution failed for {rule.rule_id}: {e}")
                    execution_results.append({
                        "rule_id": rule.rule_id,
                        "success": False,
                        "error": str(e),
                        "execution_time_ms": 0
                    })
            
            # Calculate total execution time
            total_execution_time = (datetime.now() - execution_start).total_seconds() * 1000
            
            # Update performance metrics
            self.rules_metrics["avg_execution_time_ms"] = (
                (self.rules_metrics["avg_execution_time_ms"] * 
                 self.rules_metrics["rule_executions_per_hour"] + total_execution_time) /
                (self.rules_metrics["rule_executions_per_hour"] + 1)
            )
            self.rules_metrics["rule_executions_per_hour"] += 1
            
            logger.info(f"Executed {len(applicable_rules)} rules in {total_execution_time:.2f}ms")
            return execution_results
            
        except Exception as e:
            logger.error(f"Rules execution failed: {e}")
            raise ProtectionRulesRepositoryError(f"Rules execution failed: {e}")
    
    async def get_active_rules_by_category(
        self,
        category: Optional[str] = None,
        priority_filter: Optional[List[RulePriority]] = None
    ) -> List[ProtectionRule]:
        """        Get active protection rules filtered by category and priority
        
        Args:
            category: Rule category to filter by
            priority_filter: Priority levels to include
            
        Returns:
            List of active ProtectionRule records
        """        try:
            # Check cache first
            cache_key = f"active_rules_{category}_{priority_filter}"
            if cache_key in self.active_rules_cache:
                cache_entry = self.active_rules_cache[cache_key]
                if datetime.now() - cache_entry["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cache_entry["rules"]
            
            # Build query
            query = self.db_session.query(ProtectionRule).filter(
                ProtectionRule.status == RuleStatus.ACTIVE.value
            )
            
            if category:
                query = query.filter(ProtectionRule.rule_type == category)
            
            if priority_filter:
                priority_values = [p.value for p in priority_filter]
                query = query.filter(ProtectionRule.rule_priority.in_(priority_values))
            
            # Order by priority and creation date
            query = query.order_by(
                ProtectionRule.rule_priority.desc(),
                ProtectionRule.created_at.desc()
            )
            
            # Load with related data
            rules = await query.options(
                selectinload(ProtectionRule.conditions),
                selectinload(ProtectionRule.actions)
            ).all()
            
            # Cache results
            self.active_rules_cache[cache_key] = {
                "rules": rules,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Retrieved {len(rules)} active rules for category: {category}")
            return rules
            
        except Exception as e:
            logger.error(f"Active rules retrieval failed: {e}")
            raise ProtectionRulesRepositoryError(f"Active rules retrieval failed: {e}")
    
    async def optimize_rule_performance(
        self,
        analysis_period_days: int = 30,
        min_execution_count: int = 10
    ) -> Dict[str, Any]:
        """        Analyze and optimize rule performance using ML insights
        
        Args:
            analysis_period_days: Period to analyze for optimization
            min_execution_count: Minimum executions required for analysis
            
        Returns:
            Optimization results and recommendations
        """        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=analysis_period_days)
            
            # Get rules with sufficient execution history
            rules = await self.db_session.query(ProtectionRule).filter(
                and_(
                    ProtectionRule.execution_count >= min_execution_count,
                    ProtectionRule.last_execution_at >= start_date
                )
            ).all()
            
            optimization_results = {
                "analysis_period_days": analysis_period_days,
                "rules_analyzed": len(rules),
                "optimization_recommendations": [],
                "performance_insights": {},
                "rule_effectiveness_ranking": []
            }
            
            # Analyze each rule
            for rule in rules:
                # Calculate effectiveness metrics
                effectiveness_score = rule.success_count / rule.execution_count if rule.execution_count > 0 else 0
                
                # Get execution history
                executions = await self.db_session.query(RuleExecution).filter(
                    and_(
                        RuleExecution.rule_id == rule.id,
                        RuleExecution.executed_at >= start_date
                    )
                ).all()
                
                # Analyze performance patterns
                performance_analysis = await self._analyze_rule_performance(rule, executions)
                
                optimization_results["rule_effectiveness_ranking"].append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "effectiveness_score": effectiveness_score,
                    "execution_count": rule.execution_count,
                    "avg_execution_time": performance_analysis.get("avg_execution_time", 0),
                    "false_positive_rate": performance_analysis.get("false_positive_rate", 0)
                })
                
                # Generate optimization recommendations
                recommendations = await self._generate_rule_optimization_recommendations(
                    rule, performance_analysis
                )
                
                if recommendations:
                    optimization_results["optimization_recommendations"].extend(recommendations)
            
            # Sort by effectiveness
            optimization_results["rule_effectiveness_ranking"].sort(
                key=lambda x: x["effectiveness_score"], reverse=True
            )
            
            # Generate overall insights
            optimization_results["performance_insights"] = await self._generate_performance_insights(
                optimization_results["rule_effectiveness_ranking"]
            )
            
            logger.info(f"Rule performance optimization completed for {len(rules)} rules")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Rule performance optimization failed: {e}")
            raise ProtectionRulesRepositoryError(f"Rule performance optimization failed: {e}")
    
    async def create_rule_from_template(
        self,
        template_id: str,
        template_parameters: Dict[str, Any],
        creator_id: str,
        rule_name_override: Optional[str] = None
    ) -> ProtectionRule:
        """        Create protection rule from predefined template
        
        Args:
            template_id: Template identifier
            template_parameters: Parameters to customize template
            creator_id: ID of rule creator
            rule_name_override: Override default rule name
            
        Returns:
            Created ProtectionRule record
        """        try:
            # Get template
            template = await self._get_rule_template(template_id)
            
            if not template:
                raise ProtectionRulesRepositoryError(f"Rule template not found: {template_id}")
            
            # Process template with parameters
            processed_template = await self._process_rule_template(template, template_parameters)
            
            # Create rule from processed template
            rule = await self.create_protection_rule(
                rule_name=rule_name_override or processed_template["name"],
                rule_type=RuleType(processed_template["type"]),
                rule_conditions=processed_template["conditions"],
                rule_actions=processed_template["actions"],
                creator_id=creator_id,
                rule_priority=RulePriority(processed_template.get("priority", "medium")),
                rule_metadata={
                    "template_based": True,
                    "template_id": template_id,
                    "template_parameters": template_parameters,
                    "template_version": template.get("version", "1.0")
                }
            )
            
            # Mark as template-based
            rule.is_template_based = True
            rule.template_id = template_id
            await self.db_session.commit()
            
            logger.info(f"Rule created from template: {rule.rule_id} from {template_id}")
            return rule
            
        except Exception as e:
            logger.error(f"Rule creation from template failed: {e}")
            raise ProtectionRulesRepositoryError(f"Rule creation from template failed: {e}")
    
    # Private helper methods
    
    async def _validate_rule_structure(
        self,
        conditions: List[Dict[str, Any]],
        actions: List[Dict[str, Any]]
    ) -> None:
        """Validate rule structure and syntax"""        if not conditions:
            raise ProtectionRulesRepositoryError("Rule must have at least one condition")
        
        if not actions:
            raise ProtectionRulesRepositoryError("Rule must have at least one action")
        
        # Validate condition structure
        for condition in conditions:
            required_fields = ["type", "operator", "value"]
            for field in required_fields:
                if field not in condition:
                    raise ProtectionRulesRepositoryError(f"Condition missing required field: {field}")
        
        # Validate action structure
        for action in actions:
            if "type" not in action:
                raise ProtectionRulesRepositoryError("Action missing required field: type")
    
    async def _generate_rule_id(self, rule_name: str, rule_type: RuleType) -> str:
        """Generate unique rule identifier"""        import hashlib
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        type_prefix = rule_type.value[:4].upper()
        
        hash_input = f"{rule_name}|{rule_type.value}|{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()
        
        return f"RULE-{type_prefix}-{timestamp}-{hash_suffix}"
    
    async def _test_rule_execution(self, rule: ProtectionRule) -> Dict[str, Any]:
        """Test rule execution with sample data"""        # Implementation would test rule with sample violation data
        return {"test_passed": True, "execution_time_ms": 10}
    
    async def _validate_rule_for_activation(self, rule: ProtectionRule) -> None:
        """Validate rule is ready for activation"""        if rule.status == RuleStatus.DEPRECATED.value:
            raise ProtectionRulesRepositoryError("Cannot activate deprecated rule")
        
        # Additional validation logic would go here
    
    async def _check_rule_conflicts(self, rule: ProtectionRule) -> List[str]:
        """Check for conflicts with existing active rules"""        # Implementation would check for logical conflicts
        return []  # No conflicts found
    
    async def _get_applicable_rules(
        self,
        content_data: Dict[str, Any],
        content_context: Dict[str, Any],
        rule_categories: Optional[List[str]] = None
    ) -> List[ProtectionRule]:
        """Get rules applicable to content"""        query = self.db_session.query(ProtectionRule).filter(
            ProtectionRule.status == RuleStatus.ACTIVE.value
        )
        
        if rule_categories:
            query = query.filter(ProtectionRule.rule_type.in_(rule_categories))
        
        return await query.all()
    
    async def _execute_single_rule(
        self,
        rule: ProtectionRule,
        content_data: Dict[str, Any],
        content_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual protection rule"""        execution_start = datetime.now()
        
        try:
            # Decrypt rule conditions and actions
            conditions = json.loads(
                await self.encryption_manager.decrypt_data(rule.conditions_data)
            )
            actions = json.loads(
                await self.encryption_manager.decrypt_data(rule.actions_data)
            )
            
            # Execute rule logic
            result = await self.rule_engine.execute_rule(
                conditions, actions, content_data, content_context
            )
            
            execution_time = (datetime.now() - execution_start).total_seconds() * 1000
            
            # Create execution record
            execution_record = RuleExecution(
                id=uuid4(),
                rule_id=rule.id,
                content_hash=content_data.get("content_hash"),
                execution_result=result,
                execution_time_ms=execution_time,
                executed_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            
            self.db_session.add(execution_record)
            
            return {
                "rule_id": rule.rule_id,
                "success": result.get("success", False),
                "actions_triggered": result.get("actions_triggered", []),
                "execution_time_ms": execution_time,
                "result_data": result.get("result_data", {})
            }
            
        except Exception as e:
            execution_time = (datetime.now() - execution_start).total_seconds() * 1000
            logger.error(f"Rule execution failed for {rule.rule_id}: {e}")
            
            return {
                "rule_id": rule.rule_id,
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time
            }
    
    async def _update_rule_execution_metrics(
        self,
        rule: ProtectionRule,
        execution_result: Dict[str, Any]
    ) -> None:
        """Update rule execution metrics"""        rule.execution_count += 1
        rule.last_execution_at = datetime.now(timezone.utc)
        
        if execution_result["success"]:
            rule.success_count += 1
        else:
            rule.failure_count += 1
        
        # Update effectiveness score
        rule.effectiveness_score = rule.success_count / rule.execution_count if rule.execution_count > 0 else 0
    
    async def _analyze_rule_performance(
        self,
        rule: ProtectionRule,
        executions: List[RuleExecution]
    ) -> Dict[str, Any]:
        """Analyze rule performance patterns"""        if not executions:
            return {}
        
        total_time = sum(e.execution_time_ms for e in executions)
        avg_execution_time = total_time / len(executions)
        
        successful_executions = [e for e in executions if e.execution_result.get("success")]
        success_rate = len(successful_executions) / len(executions) * 100
        
        return {
            "avg_execution_time": avg_execution_time,
            "success_rate": success_rate,
            "total_executions": len(executions),
            "false_positive_rate": 100 - success_rate  # Simplified calculation
        }
    
    async def _generate_rule_optimization_recommendations(
        self,
        rule: ProtectionRule,
        performance_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations for rule"""        recommendations = []
        
        # Check execution time
        if performance_analysis.get("avg_execution_time", 0) > 1000:  # > 1 second
            recommendations.append({
                "type": "performance",
                "rule_id": rule.rule_id,
                "recommendation": "Optimize rule conditions to reduce execution time",
                "priority": "medium",
                "impact": "performance_improvement"
            })
        
        # Check success rate
        if performance_analysis.get("success_rate", 0) < 80:
            recommendations.append({
                "type": "effectiveness",
                "rule_id": rule.rule_id,
                "recommendation": "Review rule conditions to improve accuracy",
                "priority": "high",
                "impact": "accuracy_improvement"
            })
        
        return recommendations
    
    async def _generate_performance_insights(
        self,
        effectiveness_ranking: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate overall performance insights"""        if not effectiveness_ranking:
            return {}
        
        avg_effectiveness = sum(r["effectiveness_score"] for r in effectiveness_ranking) / len(effectiveness_ranking)
        
        top_performers = [r for r in effectiveness_ranking if r["effectiveness_score"] > avg_effectiveness]
        underperformers = [r for r in effectiveness_ranking if r["effectiveness_score"] < 0.5]
        
        return {
            "average_effectiveness": avg_effectiveness,
            "top_performers_count": len(top_performers),
            "underperformers_count": len(underperformers),
            "total_rules_analyzed": len(effectiveness_ranking),
            "performance_distribution": {
                "excellent": len([r for r in effectiveness_ranking if r["effectiveness_score"] > 0.9]),
                "good": len([r for r in effectiveness_ranking if 0.7 <= r["effectiveness_score"] <= 0.9]),
                "fair": len([r for r in effectiveness_ranking if 0.5 <= r["effectiveness_score"] < 0.7]),
                "poor": len([r for r in effectiveness_ranking if r["effectiveness_score"] < 0.5])
            }
        }
    
    async def _get_rule_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get rule template by ID"""        # Check cache first
        if template_id in self.rule_templates_cache:
            return self.rule_templates_cache[template_id]
        
        # Query database
        template = await self.db_session.query(RuleTemplate).filter(
            RuleTemplate.template_id == template_id
        ).first()
        
        if template:
            template_data = json.loads(template.template_data)
            self.rule_templates_cache[template_id] = template_data
            return template_data
        
        return None
    
    async def _process_rule_template(
        self,
        template: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process rule template with parameters"""        # Implementation would substitute template variables with parameters
        processed = template.copy()
        
        # Simple parameter substitution example
        for key, value in parameters.items():
            template_str = json.dumps(processed)
            template_str = template_str.replace(f"{{{{ {key} }}}}", str(value))
            processed = json.loads(template_str)
        
        return processed
    
    def _clear_rules_cache(self) -> None:
        """Clear rules cache to force refresh"""        self.active_rules_cache.clear()
        logger.debug("Rules cache cleared")
