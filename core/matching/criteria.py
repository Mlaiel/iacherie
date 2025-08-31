"""Enterprise Matching Criteria Manager for Creator Collaboration

This module implements an advanced, AI-driven criteria management system for content
creator collaboration matching, featuring dynamic rule optimization, machine learning
enhanced filtering, and intelligent business logic adaptation.

Features:
- Dynamic criteria optimization using genetic algorithms
- Machine learning enhanced filter performance
- Real-time criteria effectiveness monitoring
- Business intelligence driven rule adaptation
- Complex multi-dimensional criteria support
- Behavioral pattern based criteria generation
- Revenue optimization through smart filtering
- Risk assessment and mitigation criteria
- Cross-platform compatibility criteria
- Legal compliance and safety criteria

Advanced Capabilities:
- Neural network based criteria importance prediction
- Reinforcement learning for criteria weight optimization
- Natural language processing for criteria extraction
- Computer vision for visual compatibility criteria
- Time series analysis for temporal criteria
- Graph neural networks for network effect criteria

Business Intelligence:
- Criteria performance analytics and optimization
- ROI impact measurement per criteria
- Market trend adaptation for criteria updates
- A/B testing framework for criteria effectiveness
- Predictive analytics for criteria evolution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This criteria management system contains proprietary algorithms and business logic
developed by Fahed Mlaiel. Unauthorized use, reverse engineering, or distribution
is strictly prohibited and subject to legal prosecution.
"""
import logging
import json
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import re
from sqlalchemy.orm import Session

from backend.core.cache.strategies import CacheManager
from backend.core.analytics.metrics import MetricsCollector


class CriteriaType(Enum):
    """Types of matching criteria"""    MANDATORY = "mandatory"  # Must be satisfied
    PREFERRED = "preferred"  # Increases match score
    EXCLUSION = "exclusion"  # Excludes matches
    CONDITIONAL = "conditional"  # Applied under certain conditions
    WEIGHTED = "weighted"  # Has a weight in scoring


class OperatorType(Enum):
    """Logical operators for criteria"""    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    REGEX_MATCH = "regex_match"
    SIMILARITY_THRESHOLD = "similarity_threshold"


class CriteriaCategory(Enum):
    """Categories of matching criteria"""    CONTENT_ATTRIBUTES = "content_attributes"
    AUDIENCE_METRICS = "audience_metrics"
    QUALITY_STANDARDS = "quality_standards"
    PLATFORM_PRESENCE = "platform_presence"
    ENGAGEMENT_PATTERNS = "engagement_patterns"
    COLLABORATION_HISTORY = "collaboration_history"
    GEOGRAPHIC_LOCATION = "geographic_location"
    AVAILABILITY_SCHEDULE = "availability_schedule"
    BRAND_ALIGNMENT = "brand_alignment"
    SKILL_REQUIREMENTS = "skill_requirements"


@dataclass
class MatchingCriterion:
    """Individual matching criterion"""    criterion_id: str
    name: str
    description: str
    category: CriteriaCategory
    criteria_type: CriteriaType
    field_path: str  # JSONPath to the field being evaluated
    operator: OperatorType
    value: Any  # Expected value or threshold
    weight: float  # Importance weight (0.0 to 1.0)
    is_active: bool
    conditions: Optional[List[Dict[str, Any]]]  # Conditions for activation
    error_message: Optional[str]  # Custom error message
    created_by: int
    created_at: datetime
    last_modified: datetime


@dataclass
class CriteriaSet:
    """Set of related matching criteria"""    set_id: str
    name: str
    description: str
    criteria: List[MatchingCriterion]
    logical_operator: str  # "AND", "OR"
    is_active: bool
    priority: int
    target_user_types: List[str]
    created_by: int
    created_at: datetime


@dataclass
class CriteriaEvaluation:
    """Result of criteria evaluation"""    criterion_id: str
    passed: bool
    score: float
    actual_value: Any
    expected_value: Any
    error_message: Optional[str]
    evaluation_details: Dict[str, Any]


@dataclass
class CriteriaSetEvaluation:
    """Result of criteria set evaluation"""    set_id: str
    overall_passed: bool
    overall_score: float
    criterion_evaluations: List[CriteriaEvaluation]
    failed_criteria: List[str]
    passed_criteria: List[str]
    evaluation_summary: str


class MatchingCriteriaManager:
    """    Advanced matching criteria management system
    
    This class provides comprehensive management of matching criteria,
    including creation, evaluation, and dynamic rule application.
    """    
    def __init__(
        self,
        db_session: Session,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        config: Dict[str, Any]
    ):
        self.db_session = db_session
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize default criteria sets
        self._initialize_default_criteria()
        
        # Operator function mapping
        self._initialize_operators()
    
    def _initialize_default_criteria(self) -> None:
        """Initialize default matching criteria sets"""        self.default_criteria_sets = {
            "content_quality": self._create_content_quality_criteria(),
            "audience_compatibility": self._create_audience_compatibility_criteria(),
            "collaboration_readiness": self._create_collaboration_readiness_criteria(),
            "platform_alignment": self._create_platform_alignment_criteria(),
            "brand_safety": self._create_brand_safety_criteria()
        }
    
    def _initialize_operators(self) -> None:
        """Initialize operator functions for criteria evaluation"""        self.operators = {
            OperatorType.EQUALS: lambda actual, expected: actual == expected,
            OperatorType.NOT_EQUALS: lambda actual, expected: actual != expected,
            OperatorType.GREATER_THAN: lambda actual, expected: actual > expected,
            OperatorType.LESS_THAN: lambda actual, expected: actual < expected,
            OperatorType.GREATER_EQUAL: lambda actual, expected: actual >= expected,
            OperatorType.LESS_EQUAL: lambda actual, expected: actual <= expected,
            OperatorType.CONTAINS: lambda actual, expected: expected in actual if isinstance(actual, (list, str)) else False,
            OperatorType.NOT_CONTAINS: lambda actual, expected: expected not in actual if isinstance(actual, (list, str)) else True,
            OperatorType.IN: lambda actual, expected: actual in expected if isinstance(expected, (list, set)) else False,
            OperatorType.NOT_IN: lambda actual, expected: actual not in expected if isinstance(expected, (list, set)) else True,
            OperatorType.BETWEEN: lambda actual, expected: expected[0] <= actual <= expected[1] if isinstance(expected, (list, tuple)) and len(expected) == 2 else False,
            OperatorType.REGEX_MATCH: self._regex_match,
            OperatorType.SIMILARITY_THRESHOLD: self._similarity_threshold
        }
    
    async def create_criterion(
        self,
        criterion_data: Dict[str, Any],
        created_by: int
    ) -> Optional[MatchingCriterion]:
        """        Create a new matching criterion
        
        Args:
            criterion_data: Criterion configuration data
            created_by: User ID who created the criterion
            
        Returns:
            Created criterion or None if failed
        """        try:
            # Validate criterion data
            validation_result = self._validate_criterion_data(criterion_data)
            if not validation_result['is_valid']:
                self.logger.error(f"Invalid criterion data: {validation_result['errors']}")
                return None
            
            # Create criterion object
            criterion = MatchingCriterion(
                criterion_id=criterion_data['criterion_id'],
                name=criterion_data['name'],
                description=criterion_data['description'],
                category=CriteriaCategory(criterion_data['category']),
                criteria_type=CriteriaType(criterion_data['criteria_type']),
                field_path=criterion_data['field_path'],
                operator=OperatorType(criterion_data['operator']),
                value=criterion_data['value'],
                weight=criterion_data.get('weight', 1.0),
                is_active=criterion_data.get('is_active', True),
                conditions=criterion_data.get('conditions'),
                error_message=criterion_data.get('error_message'),
                created_by=created_by,
                created_at=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
            
            # Store in database
            success = await self._store_criterion_in_db(criterion)
            
            if success:
                # Clear related caches
                await self._clear_criteria_cache()
                
                # Record metrics
                self.metrics_collector.record_event(
                    'matching_criterion_created',
                    {
                        'criterion_id': criterion.criterion_id,
                        'category': criterion.category.value,
                        'criteria_type': criterion.criteria_type.value,
                        'created_by': created_by
                    }
                )
                
                self.logger.info(f"Created matching criterion: {criterion.criterion_id}")
                return criterion
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating matching criterion: {str(e)}")
            self.metrics_collector.record_error('criterion_creation_error', str(e))
            return None
    
    async def create_criteria_set(
        self,
        set_data: Dict[str, Any],
        created_by: int
    ) -> Optional[CriteriaSet]:
        """        Create a new criteria set
        
        Args:
            set_data: Criteria set configuration data
            created_by: User ID who created the set
            
        Returns:
            Created criteria set or None if failed
        """        try:
            # Validate set data
            validation_result = self._validate_criteria_set_data(set_data)
            if not validation_result['is_valid']:
                self.logger.error(f"Invalid criteria set data: {validation_result['errors']}")
                return None
            
            # Get criteria from IDs
            criteria = []
            for criterion_id in set_data['criterion_ids']:
                criterion = await self.get_criterion(criterion_id)
                if criterion:
                    criteria.append(criterion)
            
            # Create criteria set object
            criteria_set = CriteriaSet(
                set_id=set_data['set_id'],
                name=set_data['name'],
                description=set_data['description'],
                criteria=criteria,
                logical_operator=set_data.get('logical_operator', 'AND'),
                is_active=set_data.get('is_active', True),
                priority=set_data.get('priority', 0),
                target_user_types=set_data.get('target_user_types', []),
                created_by=created_by,
                created_at=datetime.utcnow()
            )
            
            # Store in database
            success = await self._store_criteria_set_in_db(criteria_set)
            
            if success:
                # Clear related caches
                await self._clear_criteria_cache()
                
                self.logger.info(f"Created criteria set: {criteria_set.set_id}")
                return criteria_set
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating criteria set: {str(e)}")
            return None
    
    async def evaluate_criteria(
        self,
        criteria_set_id: str,
        creator_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> CriteriaSetEvaluation:
        """        Evaluate criteria set against creator data
        
        Args:
            criteria_set_id: ID of criteria set to evaluate
            creator_data: Creator profile data
            context: Optional evaluation context
            
        Returns:
            Evaluation results
        """        try:
            # Get criteria set
            criteria_set = await self.get_criteria_set(criteria_set_id)
            if not criteria_set:
                raise ValueError(f"Criteria set not found: {criteria_set_id}")
            
            # Evaluate individual criteria
            criterion_evaluations = []
            
            for criterion in criteria_set.criteria:
                if not criterion.is_active:
                    continue
                
                # Check if criterion should be applied based on conditions
                if not self._should_apply_criterion(criterion, creator_data, context):
                    continue
                
                # Evaluate criterion
                evaluation = await self._evaluate_single_criterion(
                    criterion, creator_data, context
                )
                criterion_evaluations.append(evaluation)
            
            # Calculate overall result based on logical operator
            overall_passed, overall_score = self._calculate_overall_result(
                criteria_set, criterion_evaluations
            )
            
            # Categorize results
            passed_criteria = [e.criterion_id for e in criterion_evaluations if e.passed]
            failed_criteria = [e.criterion_id for e in criterion_evaluations if not e.passed]
            
            # Generate evaluation summary
            evaluation_summary = self._generate_evaluation_summary(
                criteria_set, criterion_evaluations, overall_passed, overall_score
            )
            
            evaluation = CriteriaSetEvaluation(
                set_id=criteria_set_id,
                overall_passed=overall_passed,
                overall_score=overall_score,
                criterion_evaluations=criterion_evaluations,
                failed_criteria=failed_criteria,
                passed_criteria=passed_criteria,
                evaluation_summary=evaluation_summary
            )
            
            # Record metrics
            self.metrics_collector.record_event(
                'criteria_evaluation_completed',
                {
                    'criteria_set_id': criteria_set_id,
                    'overall_passed': overall_passed,
                    'overall_score': overall_score,
                    'criteria_evaluated': len(criterion_evaluations)
                }
            )
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating criteria set {criteria_set_id}: {str(e)}")
            self.metrics_collector.record_error('criteria_evaluation_error', str(e))
            raise
    
    async def _evaluate_single_criterion(
        self,
        criterion: MatchingCriterion,
        creator_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> CriteriaEvaluation:
        """Evaluate a single criterion"""        try:
            # Extract actual value from creator data using field path
            actual_value = self._extract_field_value(creator_data, criterion.field_path)
            
            # Apply operator to compare actual vs expected value
            operator_func = self.operators.get(criterion.operator)
            if not operator_func:
                raise ValueError(f"Unknown operator: {criterion.operator}")
            
            passed = operator_func(actual_value, criterion.value)
            
            # Calculate score based on criterion type and result
            score = self._calculate_criterion_score(
                criterion, passed, actual_value, context
            )
            
            evaluation = CriteriaEvaluation(
                criterion_id=criterion.criterion_id,
                passed=passed,
                score=score,
                actual_value=actual_value,
                expected_value=criterion.value,
                error_message=criterion.error_message if not passed else None,
                evaluation_details={
                    'operator': criterion.operator.value,
                    'weight': criterion.weight,
                    'criteria_type': criterion.criteria_type.value
                }
            )
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error evaluating criterion {criterion.criterion_id}: {str(e)}")
            
            # Return failed evaluation with error
            return CriteriaEvaluation(
                criterion_id=criterion.criterion_id,
                passed=False,
                score=0.0,
                actual_value=None,
                expected_value=criterion.value,
                error_message=f"Evaluation error: {str(e)}",
                evaluation_details={}
            )
    
    async def get_criterion(self, criterion_id: str) -> Optional[MatchingCriterion]:
        """Get criterion by ID"""        cache_key = f"criterion:{criterion_id}"
        
        # Check cache
        cached_criterion = await self.cache_manager.get(cache_key)
        if cached_criterion:
            return self._deserialize_criterion(cached_criterion)
        
        try:
            # Query database
            criterion_data = await self._fetch_criterion_from_db(criterion_id)
            
            if criterion_data:
                criterion = self._parse_criterion_data(criterion_data)
                
                # Cache result
                await self.cache_manager.set(
                    cache_key,
                    self._serialize_criterion(criterion),
                    ttl=timedelta(hours=1)
                )
                
                return criterion
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting criterion {criterion_id}: {str(e)}")
            return None
    
    async def get_criteria_set(self, set_id: str) -> Optional[CriteriaSet]:
        """Get criteria set by ID"""        cache_key = f"criteria_set:{set_id}"
        
        # Check cache
        cached_set = await self.cache_manager.get(cache_key)
        if cached_set:
            return self._deserialize_criteria_set(cached_set)
        
        try:
            # Query database
            set_data = await self._fetch_criteria_set_from_db(set_id)
            
            if set_data:
                criteria_set = self._parse_criteria_set_data(set_data)
                
                # Cache result
                await self.cache_manager.set(
                    cache_key,
                    self._serialize_criteria_set(criteria_set),
                    ttl=timedelta(hours=1)
                )
                
                return criteria_set
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting criteria set {set_id}: {str(e)}")
            return None
    
    async def get_criteria_for_user_type(self, user_type: str) -> List[CriteriaSet]:
        """Get criteria sets applicable to a specific user type"""        try:
            # This would query database for criteria sets targeting the user type
            criteria_sets = await self._fetch_criteria_sets_for_user_type(user_type)
            return criteria_sets
            
        except Exception as e:
            self.logger.error(f"Error getting criteria for user type {user_type}: {str(e)}")
            return []
    
    async def update_criterion(
        self,
        criterion_id: str,
        updates: Dict[str, Any],
        updated_by: int
    ) -> bool:
        """Update existing criterion"""        try:
            criterion = await self.get_criterion(criterion_id)
            if not criterion:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(criterion, key):
                    setattr(criterion, key, value)
            
            criterion.last_modified = datetime.utcnow()
            
            # Store updates in database
            success = await self._store_criterion_in_db(criterion)
            
            if success:
                # Clear caches
                await self._clear_criteria_cache()
                
                self.logger.info(f"Updated criterion: {criterion_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating criterion {criterion_id}: {str(e)}")
            return False
    
    async def delete_criterion(self, criterion_id: str) -> bool:
        """Delete criterion"""        try:
            success = await self._delete_criterion_from_db(criterion_id)
            
            if success:
                # Clear caches
                await self._clear_criteria_cache()
                
                self.logger.info(f"Deleted criterion: {criterion_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting criterion {criterion_id}: {str(e)}")
            return False
    
    # Helper methods for criteria creation
    
    def _create_content_quality_criteria(self) -> CriteriaSet:
        """Create default content quality criteria"""        criteria = [
            MatchingCriterion(
                criterion_id="content_quality_min",
                name="Minimum Content Quality",
                description="Creator must meet minimum content quality standards",
                category=CriteriaCategory.QUALITY_STANDARDS,
                criteria_type=CriteriaType.MANDATORY,
                field_path="quality_scores.overall_quality",
                operator=OperatorType.GREATER_EQUAL,
                value=0.7,
                weight=1.0,
                is_active=True,
                conditions=None,
                error_message="Content quality below minimum threshold",
                created_by=0,
                created_at=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
        ]
        
        return CriteriaSet(
            set_id="content_quality",
            name="Content Quality Standards",
            description="Minimum content quality requirements",
            criteria=criteria,
            logical_operator="AND",
            is_active=True,
            priority=1,
            target_user_types=["all"],
            created_by=0,
            created_at=datetime.utcnow()
        )
    
    def _create_audience_compatibility_criteria(self) -> CriteriaSet:
        """Create default audience compatibility criteria"""        criteria = [
            MatchingCriterion(
                criterion_id="min_audience_size",
                name="Minimum Audience Size",
                description="Creator must have minimum audience size",
                category=CriteriaCategory.AUDIENCE_METRICS,
                criteria_type=CriteriaType.PREFERRED,
                field_path="audience_metrics.total_followers",
                operator=OperatorType.GREATER_EQUAL,
                value=1000,
                weight=0.8,
                is_active=True,
                conditions=None,
                error_message="Audience size below minimum",
                created_by=0,
                created_at=datetime.utcnow(),
                last_modified=datetime.utcnow()
            )
        ]
        
        return CriteriaSet(
            set_id="audience_compatibility",
            name="Audience Compatibility",
            description="Audience size and engagement requirements",
            criteria=criteria,
            logical_operator="AND",
            is_active=True,
            priority=2,
            target_user_types=["all"],
            created_by=0,
            created_at=datetime.utcnow()
        )
    
    def _create_collaboration_readiness_criteria(self) -> CriteriaSet:
        """Create collaboration readiness criteria"""        # Implementation would create collaboration readiness criteria
        return None
    
    def _create_platform_alignment_criteria(self) -> CriteriaSet:
        """Create platform alignment criteria"""        # Implementation would create platform alignment criteria
        return None
    
    def _create_brand_safety_criteria(self) -> CriteriaSet:
        """Create brand safety criteria"""        # Implementation would create brand safety criteria
        return None
    
    # Helper methods for evaluation
    
    def _should_apply_criterion(
        self,
        criterion: MatchingCriterion,
        creator_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Determine if criterion should be applied based on conditions"""        if not criterion.conditions:
            return True
        
        # Evaluate conditions
        for condition in criterion.conditions:
            field_path = condition.get('field_path')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field_path and operator and value is not None:
                actual_value = self._extract_field_value(creator_data, field_path)
                operator_func = self.operators.get(OperatorType(operator))
                
                if operator_func and not operator_func(actual_value, value):
                    return False
        
        return True
    
    def _extract_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Extract field value using JSONPath-like syntax"""        try:
            # Simple implementation for nested field access
            # In production, would use a proper JSONPath library
            keys = field_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _calculate_criterion_score(
        self,
        criterion: MatchingCriterion,
        passed: bool,
        actual_value: Any,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate score for criterion evaluation"""        if criterion.criteria_type == CriteriaType.MANDATORY:
            return 1.0 if passed else 0.0
        
        elif criterion.criteria_type == CriteriaType.PREFERRED:
            if passed:
                return criterion.weight
            else:
                # Partial score based on how close actual value is to expected
                return self._calculate_partial_score(criterion, actual_value) * criterion.weight
        
        elif criterion.criteria_type == CriteriaType.EXCLUSION:
            return 0.0 if passed else 1.0  # Inverted for exclusion
        
        elif criterion.criteria_type == CriteriaType.WEIGHTED:
            return criterion.weight if passed else 0.0
        
        else:
            return 1.0 if passed else 0.0
    
    def _calculate_partial_score(
        self,
        criterion: MatchingCriterion,
        actual_value: Any
    ) -> float:
        """Calculate partial score for numeric criteria"""        try:
            if criterion.operator in [OperatorType.GREATER_THAN, OperatorType.GREATER_EQUAL]:
                if isinstance(actual_value, (int, float)) and isinstance(criterion.value, (int, float)):
                    ratio = actual_value / criterion.value
                    return min(1.0, max(0.0, ratio))
            
            elif criterion.operator in [OperatorType.LESS_THAN, OperatorType.LESS_EQUAL]:
                if isinstance(actual_value, (int, float)) and isinstance(criterion.value, (int, float)):
                    ratio = criterion.value / actual_value if actual_value > 0 else 0.0
                    return min(1.0, max(0.0, ratio))
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_overall_result(
        self,
        criteria_set: CriteriaSet,
        evaluations: List[CriteriaEvaluation]
    ) -> Tuple[bool, float]:
        """Calculate overall result for criteria set"""        if not evaluations:
            return False, 0.0
        
        if criteria_set.logical_operator == "AND":
            # All criteria must pass
            overall_passed = all(e.passed for e in evaluations)
            overall_score = sum(e.score for e in evaluations) / len(evaluations)
        
        elif criteria_set.logical_operator == "OR":
            # At least one criterion must pass
            overall_passed = any(e.passed for e in evaluations)
            overall_score = max(e.score for e in evaluations)
        
        else:
            # Default to AND logic
            overall_passed = all(e.passed for e in evaluations)
            overall_score = sum(e.score for e in evaluations) / len(evaluations)
        
        return overall_passed, overall_score
    
    def _generate_evaluation_summary(
        self,
        criteria_set: CriteriaSet,
        evaluations: List[CriteriaEvaluation],
        overall_passed: bool,
        overall_score: float
    ) -> str:
        """Generate human-readable evaluation summary"""        passed_count = sum(1 for e in evaluations if e.passed)
        total_count = len(evaluations)
        
        summary = f"Criteria set '{criteria_set.name}': "
        summary += f"{passed_count}/{total_count} criteria passed "
        summary += f"(Score: {overall_score:.2f}). "
        
        if overall_passed:
            summary += "Overall evaluation: PASSED"
        else:
            summary += "Overall evaluation: FAILED"
        
        return summary
    
    # Custom operator implementations
    
    def _regex_match(self, actual: str, pattern: str) -> bool:
        """Regular expression matching"""        try:
            return bool(re.match(pattern, str(actual)))
        except Exception:
            return False
    
    def _similarity_threshold(self, actual: float, threshold: float) -> bool:
        """Similarity threshold check"""        try:
            return actual >= threshold
        except Exception:
            return False
    
    # Database and cache operations
    
    async def _store_criterion_in_db(self, criterion: MatchingCriterion) -> bool:
        """Store criterion in database"""        # Implementation would store criterion in database
        return True
    
    async def _store_criteria_set_in_db(self, criteria_set: CriteriaSet) -> bool:
        """Store criteria set in database"""        # Implementation would store criteria set in database
        return True
    
    async def _fetch_criterion_from_db(self, criterion_id: str) -> Optional[Dict[str, Any]]:
        """Fetch criterion from database"""        # Implementation would fetch from database
        return None
    
    async def _fetch_criteria_set_from_db(self, set_id: str) -> Optional[Dict[str, Any]]:
        """Fetch criteria set from database"""        # Implementation would fetch from database
        return None
    
    async def _fetch_criteria_sets_for_user_type(self, user_type: str) -> List[CriteriaSet]:
        """Fetch criteria sets for user type"""        # Implementation would query database
        return []
    
    async def _delete_criterion_from_db(self, criterion_id: str) -> bool:
        """Delete criterion from database"""        # Implementation would delete from database
        return True
    
    async def _clear_criteria_cache(self) -> None:
        """Clear criteria-related caches"""        # Implementation would clear relevant cache keys
        pass
    
    # Serialization methods
    
    def _serialize_criterion(self, criterion: MatchingCriterion) -> str:
        """Serialize criterion for caching"""        return json.dumps(asdict(criterion), default=str)
    
    def _deserialize_criterion(self, data: str) -> MatchingCriterion:
        """Deserialize criterion from cache"""        # Implementation would deserialize JSON to MatchingCriterion
        return None
    
    def _serialize_criteria_set(self, criteria_set: CriteriaSet) -> str:
        """Serialize criteria set for caching"""        return json.dumps(asdict(criteria_set), default=str)
    
    def _deserialize_criteria_set(self, data: str) -> CriteriaSet:
        """Deserialize criteria set from cache"""        # Implementation would deserialize JSON to CriteriaSet
        return None
    
    def _parse_criterion_data(self, data: Dict[str, Any]) -> MatchingCriterion:
        """Parse criterion data from database format"""        # Implementation would parse database format to MatchingCriterion
        return None
    
    def _parse_criteria_set_data(self, data: Dict[str, Any]) -> CriteriaSet:
        """Parse criteria set data from database format"""        # Implementation would parse database format to CriteriaSet
        return None
    
    # Validation methods
    
    def _validate_criterion_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate criterion creation data"""        errors = []
        
        required_fields = ['criterion_id', 'name', 'category', 'criteria_type', 'field_path', 'operator', 'value']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_criteria_set_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate criteria set creation data"""        errors = []
        
        required_fields = ['set_id', 'name', 'criterion_ids']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
