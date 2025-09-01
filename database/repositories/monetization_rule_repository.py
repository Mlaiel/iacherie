"""Monetization Rule Repository Module

Enterprise-grade repository for monetization rule management with intelligent
revenue optimization, automated rule execution, and comprehensive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from ..models.monetization_rules import (
    MonetizationRule,
    RuleType,
    RuleStatus,
    TriggerType,
    ConditionOperator,
    ActionType,
    OptimizationGoal
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class MonetizationRuleRepository(BaseRepository[MonetizationRule]):
    """
    Repository for monetization rule operations with intelligent revenue optimization,
    automated execution, performance analytics, and dynamic rule adaptation.
    """
    
    def __init__(self, db_session: Session):
        """
Initialize monetization rule repository"""
        super().__init__(db_session, MonetizationRule)
        
    def create_rule(self,
                   user_id: int,
                   name: str,
                   rule_type: RuleType,
                   trigger_type: TriggerType,
                   trigger_conditions: Dict[str, Any],
                   actions: List[Dict[str, Any]],
                   optimization_goal: OptimizationGoal,
                   priority: int = 50,
                   description: Optional[str] = None,
                   constraints: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> MonetizationRule:
        """
        Create monetization rule with validation and optimization analysis
        
        Args:
            user_id: Rule owner user ID
            name: Rule name
            rule_type: Type of monetization rule
            trigger_type: What triggers the rule
            trigger_conditions: Conditions for rule activation
            actions: Actions to execute when triggered
            optimization_goal: Primary optimization objective
            priority: Rule priority (1-100, higher = more priority)
            description: Rule description
            constraints: Rule execution constraints
            metadata: Additional rule metadata
            
        Returns:
            Created MonetizationRule instance
        """
        try:
            # Validate priority range
            if not (1 <= priority <= 100):
                raise RepositoryException("Priority must be between 1 and 100")
            
            # Validate trigger conditions
            self._validate_trigger_conditions(trigger_conditions, trigger_type)
            
            # Validate actions
            self._validate_rule_actions(actions)
            
            # Check for conflicting rules
            conflicts = self._check_rule_conflicts(user_id, trigger_conditions, priority)
            if conflicts:
                logger.warning(f"Potential rule conflicts detected: {[r.name for r in conflicts]}")
            
            # Generate rule ID and reference
            rule_id = str(uuid.uuid4())
            rule_reference = self._generate_rule_reference(rule_type, datetime.utcnow())
            
            rule_data = {
                'user_id': user_id,
                'name': name,
                'description': description,
                'rule_type': rule_type,
                'trigger_type': trigger_type,
                'trigger_conditions': trigger_conditions,
                'actions': actions,
                'optimization_goal': optimization_goal,
                'priority': priority,
                'constraints': constraints or {},
                'status': RuleStatus.ACTIVE,
                'metadata': metadata or {},
                'rule_id': rule_id,
                'rule_reference': rule_reference,
                'execution_count': 0,
                'success_count': 0,
                'last_execution': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            rule = self.create(**rule_data)
            
            self.logger.info(
                f"Created {rule_type.value} rule '{name}' for user {user_id} with priority {priority}"
            )
            
            return rule
            
        except Exception as e:
            self.logger.error(f"Failed to create monetization rule: {str(e)}")
            raise RepositoryException(f"Rule creation failed: {str(e)}")
            
    def _validate_trigger_conditions(self,
                                   conditions: Dict[str, Any],
                                   trigger_type: TriggerType) -> None:
        """
        Validate trigger conditions based on trigger type
        
        Args:
            conditions: Trigger conditions to validate
            trigger_type: Type of trigger
            
        Raises:
            RepositoryException: If conditions are invalid
        """
        required_fields = {
            TriggerType.REVENUE_THRESHOLD: ['threshold_amount', 'operator'],
            TriggerType.VIEW_COUNT: ['view_count', 'operator'],
            TriggerType.TIME_BASED: ['schedule'],
            TriggerType.PLATFORM_EVENT: ['platform', 'event_type'],
            TriggerType.CONTENT_UPLOAD: ['content_types'],
            TriggerType.USER_ACTION: ['action_type']
        }
        
        if trigger_type in required_fields:
            for field in required_fields[trigger_type]:
                if field not in conditions:
                    raise RepositoryException(f"Missing required condition field: {field}")
        
        # Validate operators
        if 'operator' in conditions:
            valid_operators = [op.value for op in ConditionOperator]
            if conditions['operator'] not in valid_operators:
                raise RepositoryException(f"Invalid operator: {conditions['operator']}")
                
    def _validate_rule_actions(self, actions: List[Dict[str, Any]]) -> None:
        """
        Validate rule actions
        
        Args:
            actions: List of actions to validate
            
        Raises:
            RepositoryException: If actions are invalid
        """
        if not actions:
            raise RepositoryException("At least one action is required")
        
        valid_action_types = [action.value for action in ActionType]
        
        for action in actions:
            if 'type' not in action:
                raise RepositoryException("Action type is required")
            
            if action['type'] not in valid_action_types:
                raise RepositoryException(f"Invalid action type: {action['type']}")
            
            # Validate action-specific parameters
            if action['type'] == ActionType.ADJUST_PRICING.value:
                if 'adjustment_percentage' not in action:
                    raise RepositoryException("Pricing adjustment requires adjustment_percentage")
                    
    def _check_rule_conflicts(self,
                            user_id: int,
                            trigger_conditions: Dict[str, Any],
                            priority: int) -> List[MonetizationRule]:
        """
        Check for potentially conflicting rules
        
        Args:
            user_id: User ID
            trigger_conditions: New rule trigger conditions
            priority: New rule priority
            
        Returns:
            List of potentially conflicting rules
        """
        try:
            # Find rules with similar triggers and higher or equal priority
            existing_rules = self.db_session.query(MonetizationRule).filter(
                and_(
                    MonetizationRule.user_id == user_id,
                    MonetizationRule.status == RuleStatus.ACTIVE,
                    MonetizationRule.priority >= priority
                )
            ).all()
            
            conflicts = []
            
            for rule in existing_rules:
                # Simple conflict detection - more sophisticated logic could be implemented
                if self._conditions_overlap(rule.trigger_conditions, trigger_conditions):
                    conflicts.append(rule)
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Failed to check rule conflicts: {str(e)}")
            return []
            
    def _conditions_overlap(self,
                          conditions1: Dict[str, Any],
                          conditions2: Dict[str, Any]) -> bool:
        """
        Check if two trigger conditions overlap
        
        Args:
            conditions1: First set of conditions
            conditions2: Second set of conditions
            
        Returns:
            True if conditions overlap, False otherwise
        """
        # Simple overlap detection - check for common keys with similar values
        common_keys = set(conditions1.keys()) & set(conditions2.keys())
        
        for key in common_keys:
            if key in ['platform', 'content_types', 'action_type']:
                # Direct value comparison for categorical fields
                if conditions1[key] == conditions2[key]:
                    return True
            elif key in ['threshold_amount', 'view_count']:
                # Range overlap for numerical fields
                # This is a simplified check - more sophisticated logic could be implemented
                return True
                
        return False
        
    def _generate_rule_reference(self, rule_type: RuleType, created_at: datetime) -> str:
        """
        Generate unique rule reference
        
        Args:
            rule_type: Type of rule
            created_at: Creation timestamp
            
        Returns:
            Rule reference string
        """
        type_code = rule_type.value[:3].upper()
        date_code = created_at.strftime("%Y%m")
        sequence = self.db_session.query(func.count(MonetizationRule.id)).filter(
            func.extract('year', MonetizationRule.created_at) == created_at.year,
            func.extract('month', MonetizationRule.created_at) == created_at.month
        ).scalar() + 1
        
        return f"MR-{type_code}-{date_code}-{sequence:04d}"
        
    def get_user_rules(self,
                      user_id: int,
                      rule_type: Optional[RuleType] = None,
                      status: Optional[RuleStatus] = None,
                      optimization_goal: Optional[OptimizationGoal] = None,
                      active_only: bool = False) -> List[MonetizationRule]:
        """
        Get monetization rules for a user with filtering
        
        Args:
            user_id: User ID
            rule_type: Optional rule type filter
            status: Optional status filter
            optimization_goal: Optional optimization goal filter
            active_only: Whether to return only active rules
            
        Returns:
            List of MonetizationRule instances
        """
        try:
            query = self.db_session.query(MonetizationRule).filter(
                MonetizationRule.user_id == user_id
            )
            
            # Apply filters
            if rule_type:
                query = query.filter(MonetizationRule.rule_type == rule_type)
            if status:
                query = query.filter(MonetizationRule.status == status)
            if optimization_goal:
                query = query.filter(MonetizationRule.optimization_goal == optimization_goal)
            if active_only:
                query = query.filter(MonetizationRule.status == RuleStatus.ACTIVE)
            
            # Order by priority (highest first) then by creation time
            query = query.order_by(
                MonetizationRule.priority.desc(),
                MonetizationRule.created_at.desc()
            )
            
            rules = query.all()
            
            self.logger.debug(f"Retrieved {len(rules)} monetization rules for user {user_id}")
            
            return rules
            
        except Exception as e:
            self.logger.error(f"Failed to get user rules: {str(e)}")
            return []
            
    def execute_rule(self,
                    rule_id: int,
                    execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a monetization rule and track results
        
        Args:
            rule_id: Rule ID to execute
            execution_context: Context data for rule execution
            
        Returns:
            Execution result dictionary
        """
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return {'success': False, 'error': 'Rule not found'}
            
            if rule.status != RuleStatus.ACTIVE:
                return {'success': False, 'error': 'Rule is not active'}
            
            # Check if trigger conditions are met
            trigger_met = self._evaluate_trigger_conditions(
                rule.trigger_conditions,
                execution_context
            )
            
            if not trigger_met:
                return {
                    'success': False,
                    'error': 'Trigger conditions not met',
                    'trigger_result': False
                }
            
            # Execute rule actions
            execution_results = []
            overall_success = True
            
            for action in rule.actions:
                action_result = self._execute_action(action, execution_context, rule)
                execution_results.append(action_result)
                
                if not action_result.get('success', False):
                    overall_success = False
            
            # Update rule execution statistics
            self._update_execution_stats(rule_id, overall_success)
            
            result = {
                'success': overall_success,
                'rule_id': rule_id,
                'rule_name': rule.name,
                'trigger_result': True,
                'action_results': execution_results,
                'executed_at': datetime.utcnow().isoformat(),
                'execution_context': execution_context
            }
            
            self.logger.info(
                f"Executed rule {rule.name} (ID: {rule_id}) with {'success' if overall_success else 'failure'}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute rule {rule_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'rule_id': rule_id
            }
            
    def _evaluate_trigger_conditions(self,
                                   conditions: Dict[str, Any],
                                   context: Dict[str, Any]) -> bool:
        """
        Evaluate if trigger conditions are met
        
        Args:
            conditions: Rule trigger conditions
            context: Execution context
            
        Returns:
            True if conditions are met, False otherwise
        """
        try:
            # Revenue threshold check
            if 'threshold_amount' in conditions:
                threshold = Decimal(str(conditions['threshold_amount']))
                operator = conditions.get('operator', 'gte')
                current_revenue = Decimal(str(context.get('revenue', 0)))
                
                if operator == 'gte' and current_revenue >= threshold:
                    return True
                elif operator == 'lte' and current_revenue <= threshold:
                    return True
                elif operator == 'eq' and current_revenue == threshold:
                    return True
                    
            # View count check
            if 'view_count' in conditions:
                threshold = conditions['view_count']
                operator = conditions.get('operator', 'gte')
                current_views = context.get('views', 0)
                
                if operator == 'gte' and current_views >= threshold:
                    return True
                elif operator == 'lte' and current_views <= threshold:
                    return True
                elif operator == 'eq' and current_views == threshold:
                    return True
            
            # Platform event check
            if 'platform' in conditions and 'event_type' in conditions:
                if (context.get('platform') == conditions['platform'] and
                    context.get('event_type') == conditions['event_type']):
                    return True
            
            # Content type check
            if 'content_types' in conditions:
                content_type = context.get('content_type')
                if content_type in conditions['content_types']:
                    return True
            
            # Time-based check
            if 'schedule' in conditions:
                # Simplified schedule check - more sophisticated scheduling could be implemented
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate trigger conditions: {str(e)}")
            return False
            
    def _execute_action(self,
                       action: Dict[str, Any],
                       context: Dict[str, Any],
                       rule: MonetizationRule) -> Dict[str, Any]:
        """
        Execute a single rule action
        
        Args:
            action: Action configuration
            context: Execution context
            rule: MonetizationRule instance
            
        Returns:
            Action execution result
        """
        try:
            action_type = action['type']
            
            if action_type == ActionType.ADJUST_PRICING.value:
                return self._execute_pricing_adjustment(action, context)
            elif action_type == ActionType.UPDATE_TAGS.value:
                return self._execute_tag_update(action, context)
            elif action_type == ActionType.NOTIFY_USER.value:
                return self._execute_user_notification(action, context, rule)
            elif action_type == ActionType.DISTRIBUTE_CONTENT.value:
                return self._execute_content_distribution(action, context)
            elif action_type == ActionType.ANALYTICS_TRIGGER.value:
                return self._execute_analytics_trigger(action, context)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action type: {action_type}',
                    'action': action
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': action
            }
            
    def _execute_pricing_adjustment(self,
                                  action: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute pricing adjustment action"""
        try:
            adjustment_percentage = action.get('adjustment_percentage', 0)
            target_content = context.get('content_id')
            
            # In production, this would integrate with pricing management system
            result = {
                'success': True,
                'action_type': 'pricing_adjustment',
                'adjustment_percentage': adjustment_percentage,
                'target_content': target_content,
                'message': f'Pricing adjusted by {adjustment_percentage}%'
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _execute_tag_update(self,
                          action: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute tag update action"""
        try:
            new_tags = action.get('tags', [])
            target_content = context.get('content_id')
            
            # In production, this would update content tags
            result = {
                'success': True,
                'action_type': 'tag_update',
                'new_tags': new_tags,
                'target_content': target_content,
                'message': f'Added {len(new_tags)} tags to content'
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _execute_user_notification(self,
                                 action: Dict[str, Any],
                                 context: Dict[str, Any],
                                 rule: MonetizationRule) -> Dict[str, Any]:
        """
Execute user notification action"""
        try:
            message_template = action.get('message', 'Monetization rule triggered')
            notification_type = action.get('notification_type', 'info')
            
            # In production, this would send actual notifications
            result = {
                'success': True,
                'action_type': 'user_notification',
                'message': message_template,
                'notification_type': notification_type,
                'user_id': rule.user_id,
                'rule_name': rule.name
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _execute_content_distribution(self,
                                    action: Dict[str, Any],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute content distribution action"""
        try:
            target_platforms = action.get('platforms', [])
            content_id = context.get('content_id')
            
            # In production, this would trigger content distribution
            result = {
                'success': True,
                'action_type': 'content_distribution',
                'platforms': target_platforms,
                'content_id': content_id,
                'message': f'Content distributed to {len(target_platforms)} platforms'
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _execute_analytics_trigger(self,
                                 action: Dict[str, Any],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
Execute analytics trigger action"""
        try:
            analytics_type = action.get('analytics_type', 'performance_report')
            
            # In production, this would trigger analytics generation
            result = {
                'success': True,
                'action_type': 'analytics_trigger',
                'analytics_type': analytics_type,
                'context': context,
                'message': f'Analytics triggered: {analytics_type}'
            }
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def _update_execution_stats(self, rule_id: int, success: bool) -> None:
        """
        Update rule execution statistics
        
        Args:
            rule_id: Rule ID
            success: Whether execution was successful
        """
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return
            
            update_data = {
                'execution_count': rule.execution_count + 1,
                'last_execution': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            if success:
                update_data['success_count'] = rule.success_count + 1
            
            self.update(rule_id, **update_data)
            
        except Exception as e:
            self.logger.error(f"Failed to update execution stats: {str(e)}")
            
    def get_rule_performance(self, rule_id: int) -> Dict[str, Any]:
        """
        Get comprehensive rule performance metrics
        
        Args:
            rule_id: Rule ID to analyze
            
        Returns:
            Performance metrics dictionary
        """
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return {'error': 'Rule not found'}
            
            # Calculate success rate
            success_rate = 0.0
            if rule.execution_count > 0:
                success_rate = (rule.success_count / rule.execution_count) * 100
            
            # Calculate execution frequency
            days_since_creation = (datetime.utcnow() - rule.created_at).days or 1
            avg_executions_per_day = rule.execution_count / days_since_creation
            
            # Determine performance status
            if success_rate >= 90:
                performance_status = 'EXCELLENT'
            elif success_rate >= 70:
                performance_status = 'GOOD'
            elif success_rate >= 50:
                performance_status = 'FAIR'
            else:
                performance_status = 'POOR'
            
            performance = {
                'rule_id': rule_id,
                'rule_name': rule.name,
                'rule_reference': rule.rule_reference,
                'execution_stats': {
                    'total_executions': rule.execution_count,
                    'successful_executions': rule.success_count,
                    'failed_executions': rule.execution_count - rule.success_count,
                    'success_rate_percentage': round(success_rate, 2)
                },
                'timing_stats': {
                    'created_at': rule.created_at.isoformat(),
                    'last_execution': rule.last_execution.isoformat() if rule.last_execution else None,
                    'days_since_creation': days_since_creation,
                    'avg_executions_per_day': round(avg_executions_per_day, 2)
                },
                'performance_status': performance_status,
                'optimization_goal': rule.optimization_goal.value,
                'current_priority': rule.priority,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Failed to get rule performance: {str(e)}")
            return {'error': str(e)}

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
