#!/usr/bin/env python3
"""
🧪 Enterprise Notification A/B Testing Engine - Ainflue Platform Core
Advanced template and timing optimization with statistical analysis

© 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import numpy as np
from scipy import stats
import hashlib
import random

class TestType(Enum):
    """Types of A/B tests"""
    CONTENT = "content"
    SUBJECT_LINE = "subject_line"
    TIMING = "timing"
    CHANNEL = "channel"
    TEMPLATE = "template"
    PERSONALIZATION = "personalization"
    FREQUENCY = "frequency"

class TestStatus(Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StatisticalSignificance(Enum):
    """Statistical significance levels"""
    NOT_SIGNIFICANT = "not_significant"
    SIGNIFICANT = "significant"
    HIGHLY_SIGNIFICANT = "highly_significant"

class AllocationMethod(Enum):
    """Traffic allocation methods"""
    RANDOM = "random"
    WEIGHTED = "weighted"
    SEGMENT_BASED = "segment_based"
    GEOGRAPHIC = "geographic"

@dataclass
class TestVariant:
    """A/B test variant definition"""
    id: str
    name: str
    content: str
    metadata: Dict[str, Any]
    allocation_percentage: float
    is_control: bool = False

@dataclass
class TestMetrics:
    """A/B test performance metrics"""
    variant_id: str
    impressions: int
    clicks: int
    conversions: int
    engagement_rate: float
    conversion_rate: float
    click_through_rate: float
    unsubscribe_rate: float
    bounce_rate: float
    revenue: float = 0.0

@dataclass
class StatisticalResult:
    """Statistical analysis result"""
    variant_a_id: str
    variant_b_id: str
    metric: str
    p_value: float
    confidence_level: float
    effect_size: float
    significance: StatisticalSignificance
    winner: Optional[str]
    lift_percentage: float

@dataclass
class ABTest:
    """A/B test configuration"""
    id: str
    name: str
    description: str
    test_type: TestType
    variants: List[TestVariant]
    target_audience: Dict[str, Any]
    allocation_method: AllocationMethod
    minimum_sample_size: int
    confidence_level: float
    test_duration_days: int
    status: TestStatus
    primary_metric: str
    secondary_metrics: List[str]
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_by: str

@dataclass
class TestResult:
    """Complete A/B test result"""
    test_id: str
    metrics: Dict[str, TestMetrics]  # variant_id -> metrics
    statistical_results: List[StatisticalResult]
    winner: Optional[str]
    confidence: float
    recommendation: str
    insights: List[str]
    duration_days: int
    total_participants: int
    analyzed_at: datetime

class NotificationABTestingEngine:
    """Enterprise A/B testing engine for notification optimization"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.logger = logging.getLogger(__name__)
        
        # Active tests
        self.active_tests: Dict[str, ABTest] = {}
        self.test_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> test_id -> variant_id
        
        # Statistical configuration
        self.default_confidence_level = 0.95
        self.minimum_effect_size = 0.05  # 5% minimum detectable effect
        self.minimum_sample_size = 100
        
        # Test templates
        self.test_templates = {
            TestType.CONTENT: {
                'name': 'Content Optimization Test',
                'duration_days': 7,
                'primary_metric': 'engagement_rate',
                'secondary_metrics': ['click_through_rate', 'conversion_rate']
            },
            TestType.SUBJECT_LINE: {
                'name': 'Subject Line Test',
                'duration_days': 3,
                'primary_metric': 'open_rate',
                'secondary_metrics': ['click_through_rate']
            },
            TestType.TIMING: {
                'name': 'Send Time Optimization',
                'duration_days': 14,
                'primary_metric': 'engagement_rate',
                'secondary_metrics': ['open_rate', 'click_through_rate']
            }
        }
        
        # Performance metrics
        self.metrics = {
            'tests_created': 0,
            'tests_running': 0,
            'tests_completed': 0,
            'variant_assignments': 0,
            'statistical_analyses': 0,
            'significant_results': 0,
            'total_participants': 0,
            'average_lift': 0.0
        }

    async def initialize(self):
        """Initialize A/B testing engine"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.logger.info("✅ A/B testing engine initialized with Redis connection")
            
            # Load active tests
            await self._load_active_tests()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize A/B testing engine: {e}")
            raise

    async def create_ab_test(
        self,
        name: str,
        test_type: TestType,
        variants: List[Dict[str, Any]],
        target_audience: Optional[Dict[str, Any]] = None,
        allocation_method: AllocationMethod = AllocationMethod.RANDOM,
        minimum_sample_size: Optional[int] = None,
        confidence_level: Optional[float] = None,
        test_duration_days: Optional[int] = None,
        primary_metric: Optional[str] = None,
        secondary_metrics: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> ABTest:
        """
        Create new A/B test
        
        Args:
            name: Test name
            test_type: Type of test to run
            variants: List of test variants
            target_audience: Audience targeting criteria
            allocation_method: How to allocate traffic
            minimum_sample_size: Minimum sample size for significance
            confidence_level: Statistical confidence level (0.9, 0.95, 0.99)
            test_duration_days: Maximum test duration
            primary_metric: Primary metric to optimize
            secondary_metrics: Additional metrics to track
            created_by: Who created the test
            
        Returns:
            ABTest configuration object
        """
        
        test_id = str(uuid.uuid4())
        
        # Apply defaults from template
        template = self.test_templates.get(test_type, {})
        if not primary_metric:
            primary_metric = template.get('primary_metric', 'engagement_rate')
        if not secondary_metrics:
            secondary_metrics = template.get('secondary_metrics', [])
        if not test_duration_days:
            test_duration_days = template.get('duration_days', 7)
        if not confidence_level:
            confidence_level = self.default_confidence_level
        if not minimum_sample_size:
            minimum_sample_size = self.minimum_sample_size
        
        # Create test variants
        test_variants = []
        total_allocation = 0.0
        
        for i, variant_data in enumerate(variants):
            variant_id = str(uuid.uuid4())
            
            allocation = variant_data.get('allocation_percentage', 100.0 / len(variants))
            total_allocation += allocation
            
            variant = TestVariant(
                id=variant_id,
                name=variant_data.get('name', f'Variant {chr(65 + i)}'),  # A, B, C...
                content=variant_data.get('content', ''),
                metadata=variant_data.get('metadata', {}),
                allocation_percentage=allocation,
                is_control=(i == 0)  # First variant is control
            )
            test_variants.append(variant)
        
        # Normalize allocations to 100%
        if total_allocation != 100.0:
            for variant in test_variants:
                variant.allocation_percentage = (variant.allocation_percentage / total_allocation) * 100.0
        
        # Create A/B test
        ab_test = ABTest(
            id=test_id,
            name=name,
            description=f"{test_type.value.replace('_', ' ').title()} test comparing {len(test_variants)} variants",
            test_type=test_type,
            variants=test_variants,
            target_audience=target_audience or {},
            allocation_method=allocation_method,
            minimum_sample_size=minimum_sample_size,
            confidence_level=confidence_level,
            test_duration_days=test_duration_days,
            status=TestStatus.DRAFT,
            primary_metric=primary_metric,
            secondary_metrics=secondary_metrics,
            created_at=datetime.utcnow(),
            started_at=None,
            ended_at=None,
            created_by=created_by
        )
        
        # Store test
        self.active_tests[test_id] = ab_test
        await self._save_ab_test(ab_test)
        
        self.metrics['tests_created'] += 1
        
        self.logger.info(f"✅ A/B test created: {name} ({test_id})")
        
        return ab_test

    async def start_ab_test(self, test_id: str) -> bool:
        """Start running an A/B test"""
        
        try:
            if test_id not in self.active_tests:
                self.logger.error(f"❌ Test not found: {test_id}")
                return False
            
            test = self.active_tests[test_id]
            
            if test.status != TestStatus.DRAFT:
                self.logger.error(f"❌ Test cannot be started in status: {test.status.value}")
                return False
            
            # Validate test configuration
            if len(test.variants) < 2:
                self.logger.error(f"❌ Test must have at least 2 variants")
                return False
            
            # Start the test
            test.status = TestStatus.RUNNING
            test.started_at = datetime.utcnow()
            
            # Initialize metrics for each variant
            for variant in test.variants:
                await self._initialize_variant_metrics(test_id, variant.id)
            
            # Save updated test
            await self._save_ab_test(test)
            
            self.metrics['tests_running'] += 1
            
            self.logger.info(f"✅ A/B test started: {test.name} ({test_id})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start A/B test: {e}")
            return False

    async def assign_user_to_variant(
        self,
        user_id: str,
        test_id: str,
        user_attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Assign user to test variant
        
        Args:
            user_id: User identifier
            test_id: Test identifier
            user_attributes: User attributes for targeting
            
        Returns:
            Variant ID if assigned, None if not eligible
        """
        
        try:
            if test_id not in self.active_tests:
                return None
            
            test = self.active_tests[test_id]
            
            if test.status != TestStatus.RUNNING:
                return None
            
            # Check if user already assigned
            if user_id in self.test_assignments and test_id in self.test_assignments[user_id]:
                return self.test_assignments[user_id][test_id]
            
            # Check if user matches target audience
            if not await self._user_matches_audience(user_id, test.target_audience, user_attributes):
                return None
            
            # Assign to variant based on allocation method
            variant_id = await self._allocate_user_to_variant(user_id, test)
            
            if variant_id:
                # Store assignment
                if user_id not in self.test_assignments:
                    self.test_assignments[user_id] = {}
                self.test_assignments[user_id][test_id] = variant_id
                
                # Save to Redis
                await self.redis_client.hset(
                    f"test_assignments:{user_id}",
                    test_id,
                    variant_id
                )
                
                self.metrics['variant_assignments'] += 1
                
                self.logger.debug(f"User {user_id} assigned to variant {variant_id} in test {test_id}")
            
            return variant_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to assign user to variant: {e}")
            return None

    async def _allocate_user_to_variant(self, user_id: str, test: ABTest) -> Optional[str]:
        """Allocate user to variant based on allocation method"""
        
        if test.allocation_method == AllocationMethod.RANDOM:
            return self._random_allocation(user_id, test.variants)
            
        elif test.allocation_method == AllocationMethod.WEIGHTED:
            return self._weighted_allocation(user_id, test.variants)
            
        elif test.allocation_method == AllocationMethod.SEGMENT_BASED:
            return self._segment_based_allocation(user_id, test.variants)
        
        # Default to random
        return self._random_allocation(user_id, test.variants)

    def _random_allocation(self, user_id: str, variants: List[TestVariant]) -> str:
        """Random allocation with consistent assignment"""
        
        # Use hash of user_id for deterministic randomness
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        random_value = (user_hash % 10000) / 100.0  # 0-100
        
        cumulative_allocation = 0.0
        for variant in variants:
            cumulative_allocation += variant.allocation_percentage
            if random_value <= cumulative_allocation:
                return variant.id
        
        # Fallback to first variant
        return variants[0].id

    def _weighted_allocation(self, user_id: str, variants: List[TestVariant]) -> str:
        """Weighted allocation based on performance"""
        
        # For now, same as random - would implement dynamic weighting based on performance
        return self._random_allocation(user_id, variants)

    def _segment_based_allocation(self, user_id: str, variants: List[TestVariant]) -> str:
        """Segment-based allocation"""
        
        # For now, same as random - would implement based on user segments
        return self._random_allocation(user_id, variants)

    async def _user_matches_audience(
        self,
        user_id: str,
        target_audience: Dict[str, Any],
        user_attributes: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if user matches target audience criteria"""
        
        if not target_audience:
            return True  # No targeting criteria
        
        if not user_attributes:
            return True  # Can't verify, allow by default
        
        # Check each targeting criterion
        for criterion, expected_value in target_audience.items():
            user_value = user_attributes.get(criterion)
            
            if criterion == 'age':
                if isinstance(expected_value, dict):
                    min_age = expected_value.get('min', 0)
                    max_age = expected_value.get('max', 999)
                    if not (min_age <= user_value <= max_age):
                        return False
                
            elif criterion == 'location':
                if isinstance(expected_value, list):
                    if user_value not in expected_value:
                        return False
                
            elif criterion == 'segment':
                if isinstance(expected_value, list):
                    if user_value not in expected_value:
                        return False
                elif user_value != expected_value:
                    return False
        
        return True

    async def track_notification_event(
        self,
        user_id: str,
        notification_id: str,
        event_type: str,  # 'sent', 'delivered', 'opened', 'clicked', 'converted', 'unsubscribed'
        test_id: Optional[str] = None,
        variant_id: Optional[str] = None,
        value: float = 0.0
    ):
        """Track notification event for A/B testing"""
        
        try:
            # Find test assignment if not provided
            if not test_id or not variant_id:
                if user_id in self.test_assignments:
                    for tid, vid in self.test_assignments[user_id].items():
                        if tid in self.active_tests:
                            test_id = tid
                            variant_id = vid
                            break
            
            if not test_id or not variant_id:
                return  # User not in any test
            
            # Update metrics
            metrics_key = f"test_metrics:{test_id}:{variant_id}"
            
            if event_type == 'sent':
                await self.redis_client.hincrby(metrics_key, 'impressions', 1)
                
            elif event_type == 'opened':
                await self.redis_client.hincrby(metrics_key, 'opens', 1)
                
            elif event_type == 'clicked':
                await self.redis_client.hincrby(metrics_key, 'clicks', 1)
                
            elif event_type == 'converted':
                await self.redis_client.hincrby(metrics_key, 'conversions', 1)
                if value > 0:
                    await self.redis_client.hincrbyfloat(metrics_key, 'revenue', value)
                
            elif event_type == 'unsubscribed':
                await self.redis_client.hincrby(metrics_key, 'unsubscribes', 1)
                
            elif event_type == 'bounced':
                await self.redis_client.hincrby(metrics_key, 'bounces', 1)
            
            # Set expiration
            await self.redis_client.expire(metrics_key, 86400 * 30)  # 30 days
            
            # Track event details
            event_data = {
                'user_id': user_id,
                'notification_id': notification_id,
                'test_id': test_id,
                'variant_id': variant_id,
                'event_type': event_type,
                'value': value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await self.redis_client.lpush(
                f"test_events:{test_id}",
                json.dumps(event_data)
            )
            await self.redis_client.ltrim(f"test_events:{test_id}", 0, 9999)  # Keep last 10k events
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track notification event: {e}")

    async def analyze_test_results(self, test_id: str) -> Optional[TestResult]:
        """Analyze A/B test results with statistical significance"""
        
        try:
            if test_id not in self.active_tests:
                self.logger.error(f"❌ Test not found: {test_id}")
                return None
            
            test = self.active_tests[test_id]
            
            # Get metrics for each variant
            variant_metrics = {}
            total_participants = 0
            
            for variant in test.variants:
                metrics = await self._calculate_variant_metrics(test_id, variant.id)
                variant_metrics[variant.id] = metrics
                total_participants += metrics.impressions
            
            # Check if test has sufficient data
            if total_participants < test.minimum_sample_size:
                self.logger.warning(f"⚠️ Insufficient sample size for test {test_id}")
                return None
            
            # Perform statistical analysis
            statistical_results = []
            control_variant = next((v for v in test.variants if v.is_control), test.variants[0])
            control_metrics = variant_metrics[control_variant.id]
            
            winner = None
            max_lift = 0.0
            
            for variant in test.variants:
                if variant.id == control_variant.id:
                    continue  # Skip control vs control
                
                test_metrics = variant_metrics[variant.id]
                
                # Analyze primary metric
                stat_result = await self._perform_statistical_test(
                    control_metrics,
                    test_metrics,
                    test.primary_metric,
                    test.confidence_level
                )
                
                statistical_results.append(stat_result)
                
                # Determine winner
                if (stat_result.significance != StatisticalSignificance.NOT_SIGNIFICANT and
                    stat_result.lift_percentage > max_lift):
                    max_lift = stat_result.lift_percentage
                    winner = variant.id
            
            # Generate insights
            insights = self._generate_test_insights(test, variant_metrics, statistical_results)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(test, statistical_results, winner)
            
            # Calculate test duration
            duration_days = 0
            if test.started_at:
                duration = datetime.utcnow() - test.started_at
                duration_days = duration.days
            
            # Create test result
            test_result = TestResult(
                test_id=test_id,
                metrics=variant_metrics,
                statistical_results=statistical_results,
                winner=winner,
                confidence=test.confidence_level,
                recommendation=recommendation,
                insights=insights,
                duration_days=duration_days,
                total_participants=total_participants,
                analyzed_at=datetime.utcnow()
            )
            
            self.metrics['statistical_analyses'] += 1
            if any(r.significance != StatisticalSignificance.NOT_SIGNIFICANT for r in statistical_results):
                self.metrics['significant_results'] += 1
            
            # Update average lift
            if max_lift > 0:
                current_avg = self.metrics.get('average_lift', 0.0)
                self.metrics['average_lift'] = (current_avg * 0.9) + (max_lift * 0.1)
            
            return test_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze test results: {e}")
            return None

    async def _calculate_variant_metrics(self, test_id: str, variant_id: str) -> TestMetrics:
        """Calculate metrics for a test variant"""
        
        metrics_key = f"test_metrics:{test_id}:{variant_id}"
        
        # Get raw metrics from Redis
        raw_metrics = await self.redis_client.hgetall(metrics_key)
        
        impressions = int(raw_metrics.get('impressions', 0))
        opens = int(raw_metrics.get('opens', 0))
        clicks = int(raw_metrics.get('clicks', 0))
        conversions = int(raw_metrics.get('conversions', 0))
        unsubscribes = int(raw_metrics.get('unsubscribes', 0))
        bounces = int(raw_metrics.get('bounces', 0))
        revenue = float(raw_metrics.get('revenue', 0.0))
        
        # Calculate rates
        engagement_rate = opens / impressions if impressions > 0 else 0.0
        click_through_rate = clicks / impressions if impressions > 0 else 0.0
        conversion_rate = conversions / impressions if impressions > 0 else 0.0
        unsubscribe_rate = unsubscribes / impressions if impressions > 0 else 0.0
        bounce_rate = bounces / impressions if impressions > 0 else 0.0
        
        return TestMetrics(
            variant_id=variant_id,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            engagement_rate=engagement_rate,
            conversion_rate=conversion_rate,
            click_through_rate=click_through_rate,
            unsubscribe_rate=unsubscribe_rate,
            bounce_rate=bounce_rate,
            revenue=revenue
        )

    async def _perform_statistical_test(
        self,
        control_metrics: TestMetrics,
        test_metrics: TestMetrics,
        metric_name: str,
        confidence_level: float
    ) -> StatisticalResult:
        """Perform statistical significance test"""
        
        # Get metric values
        control_value = getattr(control_metrics, metric_name, 0.0)
        test_value = getattr(test_metrics, metric_name, 0.0)
        
        control_n = control_metrics.impressions
        test_n = test_metrics.impressions
        
        # Calculate lift
        lift_percentage = ((test_value - control_value) / control_value * 100) if control_value > 0 else 0.0
        
        # Perform appropriate statistical test
        if metric_name in ['engagement_rate', 'conversion_rate', 'click_through_rate']:
            # Proportion test (z-test)
            p_value, effect_size = self._proportion_test(
                control_value, test_value, control_n, test_n
            )
        else:
            # Mean comparison (t-test) - simplified
            p_value = 0.5  # Placeholder
            effect_size = abs(test_value - control_value)
        
        # Determine significance
        alpha = 1 - confidence_level
        
        if p_value < alpha / 2:  # Two-tailed test
            if p_value < 0.001:
                significance = StatisticalSignificance.HIGHLY_SIGNIFICANT
            else:
                significance = StatisticalSignificance.SIGNIFICANT
        else:
            significance = StatisticalSignificance.NOT_SIGNIFICANT
        
        # Determine winner
        winner = None
        if significance != StatisticalSignificance.NOT_SIGNIFICANT:
            winner = test_metrics.variant_id if test_value > control_value else control_metrics.variant_id
        
        return StatisticalResult(
            variant_a_id=control_metrics.variant_id,
            variant_b_id=test_metrics.variant_id,
            metric=metric_name,
            p_value=p_value,
            confidence_level=confidence_level,
            effect_size=effect_size,
            significance=significance,
            winner=winner,
            lift_percentage=lift_percentage
        )

    def _proportion_test(self, p1: float, p2: float, n1: int, n2: int) -> Tuple[float, float]:
        """Perform two-proportion z-test"""
        
        if n1 == 0 or n2 == 0:
            return 1.0, 0.0
        
        # Convert rates to counts
        x1 = int(p1 * n1)
        x2 = int(p2 * n2)
        
        # Pooled proportion
        p_pool = (x1 + x2) / (n1 + n2)
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return 1.0, 0.0
        
        # Z-statistic
        z = (p2 - p1) / se
        
        # P-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        
        # Effect size (Cohen's h for proportions)
        effect_size = 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))
        
        return p_value, abs(effect_size)

    def _generate_test_insights(
        self,
        test: ABTest,
        variant_metrics: Dict[str, TestMetrics],
        statistical_results: List[StatisticalResult]
    ) -> List[str]:
        """Generate insights from test results"""
        
        insights = []
        
        # Best performing variant
        best_variant_id = None
        best_metric_value = 0.0
        
        for variant_id, metrics in variant_metrics.items():
            metric_value = getattr(metrics, test.primary_metric, 0.0)
            if metric_value > best_metric_value:
                best_metric_value = metric_value
                best_variant_id = variant_id
        
        if best_variant_id:
            best_variant = next(v for v in test.variants if v.id == best_variant_id)
            insights.append(f"Highest {test.primary_metric}: {best_variant.name} ({best_metric_value:.2%})")
        
        # Statistical significance insights
        significant_results = [r for r in statistical_results if r.significance != StatisticalSignificance.NOT_SIGNIFICANT]
        
        if significant_results:
            max_lift = max(r.lift_percentage for r in significant_results)
            insights.append(f"Maximum lift achieved: {max_lift:.1f}%")
        else:
            insights.append("No statistically significant differences detected")
        
        # Sample size insights
        total_participants = sum(m.impressions for m in variant_metrics.values())
        if total_participants < test.minimum_sample_size * 2:
            insights.append("Consider running test longer for more reliable results")
        
        # Performance patterns
        control_variant = next(v for v in test.variants if v.is_control)
        control_metrics = variant_metrics[control_variant.id]
        
        for variant in test.variants:
            if variant.is_control:
                continue
            
            variant_metrics_obj = variant_metrics[variant.id]
            
            # Compare engagement patterns
            if variant_metrics_obj.engagement_rate > control_metrics.engagement_rate * 1.1:
                insights.append(f"{variant.name} shows strong engagement improvement")
            
            if variant_metrics_obj.unsubscribe_rate > control_metrics.unsubscribe_rate * 1.5:
                insights.append(f"{variant.name} has elevated unsubscribe rate - investigate content")
        
        return insights

    def _generate_recommendation(
        self,
        test: ABTest,
        statistical_results: List[StatisticalResult],
        winner: Optional[str]
    ) -> str:
        """Generate recommendation based on test results"""
        
        if not winner:
            return "Continue testing or implement control variant. No significant improvement detected."
        
        winner_variant = next(v for v in test.variants if v.id == winner)
        
        # Find the winning result
        winning_result = next(
            (r for r in statistical_results if r.winner == winner),
            None
        )
        
        if not winning_result:
            return f"Implement {winner_variant.name} variant based on performance metrics."
        
        if winning_result.significance == StatisticalSignificance.HIGHLY_SIGNIFICANT:
            confidence_text = "high confidence"
        else:
            confidence_text = "moderate confidence"
        
        return (
            f"Implement {winner_variant.name} variant with {confidence_text}. "
            f"Expected {winning_result.metric} improvement: {winning_result.lift_percentage:.1f}%"
        )

    async def stop_ab_test(self, test_id: str, reason: str = "completed") -> bool:
        """Stop running A/B test"""
        
        try:
            if test_id not in self.active_tests:
                return False
            
            test = self.active_tests[test_id]
            
            if test.status != TestStatus.RUNNING:
                return False
            
            # Update test status
            test.status = TestStatus.COMPLETED if reason == "completed" else TestStatus.CANCELLED
            test.ended_at = datetime.utcnow()
            
            # Save updated test
            await self._save_ab_test(test)
            
            if reason == "completed":
                self.metrics['tests_completed'] += 1
            
            self.metrics['tests_running'] -= 1
            
            self.logger.info(f"✅ A/B test stopped: {test.name} ({test_id}) - {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop A/B test: {e}")
            return False

    async def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of A/B test"""
        
        if test_id not in self.active_tests:
            return None
        
        test = self.active_tests[test_id]
        
        # Get current metrics
        variant_metrics = {}
        total_participants = 0
        
        for variant in test.variants:
            metrics = await self._calculate_variant_metrics(test_id, variant.id)
            variant_metrics[variant.id] = asdict(metrics)
            total_participants += metrics.impressions
        
        # Calculate progress
        progress_percentage = min(100, (total_participants / test.minimum_sample_size) * 100)
        
        # Calculate remaining time
        remaining_days = 0
        if test.started_at and test.status == TestStatus.RUNNING:
            elapsed = datetime.utcnow() - test.started_at
            remaining = timedelta(days=test.test_duration_days) - elapsed
            remaining_days = max(0, remaining.days)
        
        return {
            'test_id': test_id,
            'name': test.name,
            'status': test.status.value,
            'progress_percentage': progress_percentage,
            'total_participants': total_participants,
            'minimum_sample_size': test.minimum_sample_size,
            'remaining_days': remaining_days,
            'variant_metrics': variant_metrics,
            'created_at': test.created_at.isoformat(),
            'started_at': test.started_at.isoformat() if test.started_at else None,
            'ended_at': test.ended_at.isoformat() if test.ended_at else None
        }

    async def _save_ab_test(self, test: ABTest):
        """Save A/B test to Redis"""
        try:
            test_dict = asdict(test)
            # Convert datetime objects
            test_dict['created_at'] = test.created_at.isoformat()
            test_dict['started_at'] = test.started_at.isoformat() if test.started_at else None
            test_dict['ended_at'] = test.ended_at.isoformat() if test.ended_at else None
            
            # Convert enums
            test_dict['test_type'] = test.test_type.value
            test_dict['status'] = test.status.value
            test_dict['allocation_method'] = test.allocation_method.value
            
            await self.redis_client.setex(
                f"ab_test:{test.id}",
                86400 * 90,  # 90 days
                json.dumps(test_dict)
            )
        except Exception as e:
            self.logger.error(f"❌ Failed to save A/B test: {e}")

    async def _load_active_tests(self):
        """Load active tests from Redis"""
        try:
            # This would typically scan for active test keys
            # For now, we'll start with empty active tests
            pass
        except Exception as e:
            self.logger.error(f"❌ Failed to load active tests: {e}")

    async def _initialize_variant_metrics(self, test_id: str, variant_id: str):
        """Initialize metrics for a test variant"""
        metrics_key = f"test_metrics:{test_id}:{variant_id}"
        
        initial_metrics = {
            'impressions': 0,
            'opens': 0,
            'clicks': 0,
            'conversions': 0,
            'unsubscribes': 0,
            'bounces': 0,
            'revenue': 0.0
        }
        
        await self.redis_client.hmset(metrics_key, initial_metrics)
        await self.redis_client.expire(metrics_key, 86400 * 30)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get A/B testing engine metrics"""
        
        return {
            **self.metrics,
            'active_tests': len(self.active_tests),
            'user_assignments': len(self.test_assignments),
            'supported_test_types': len(TestType),
            'default_confidence_level': self.default_confidence_level,
            'minimum_effect_size': self.minimum_effect_size
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("✅ A/B testing engine cleanup completed")

# Example usage and testing
if __name__ == "__main__":
    async def test_ab_testing_engine():
        """Test A/B testing engine functionality"""
        
        # Initialize engine
        engine = NotificationABTestingEngine()
        await engine.initialize()
        
        # Create A/B test
        variants = [
            {
                'name': 'Control',
                'content': 'You have a new message!',
                'allocation_percentage': 50
            },
            {
                'name': 'Variant A',
                'content': 'Hey! You\'ve got a new message 🎉',
                'allocation_percentage': 50
            }
        ]
        
        test = await engine.create_ab_test(
            name="Message Notification Test",
            test_type=TestType.CONTENT,
            variants=variants,
            minimum_sample_size=200,
            test_duration_days=7,
            primary_metric='engagement_rate'
        )
        
        print(f"A/B test created: {test.name} ({test.id})")
        
        # Start test
        started = await engine.start_ab_test(test.id)
        print(f"Test started: {started}")
        
        # Assign users to variants
        for i in range(100):
            user_id = f"user_{i}"
            variant_id = await engine.assign_user_to_variant(user_id, test.id)
            print(f"User {user_id} assigned to variant {variant_id}")
            
            # Simulate events
            await engine.track_notification_event(user_id, f"notif_{i}", 'sent', test.id, variant_id)
            
            if i % 2 == 0:  # 50% open rate
                await engine.track_notification_event(user_id, f"notif_{i}", 'opened', test.id, variant_id)
                
            if i % 4 == 0:  # 25% click rate
                await engine.track_notification_event(user_id, f"notif_{i}", 'clicked', test.id, variant_id)
        
        # Analyze results
        results = await engine.analyze_test_results(test.id)
        if results:
            print(f"\nTest Results:")
            print(f"Winner: {results.winner}")
            print(f"Recommendation: {results.recommendation}")
            print(f"Insights: {results.insights}")
            
            for variant_id, metrics in results.metrics.items():
                variant_name = next(v.name for v in test.variants if v.id == variant_id)
                print(f"\n{variant_name}:")
                print(f"  Impressions: {metrics.impressions}")
                print(f"  Engagement Rate: {metrics.engagement_rate:.2%}")
        
        # Get test status
        status = await engine.get_test_status(test.id)
        print(f"\nTest Status: {json.dumps(status, indent=2)}")
        
        # Get metrics
        metrics = await engine.get_metrics()
        print(f"\nEngine Metrics: {json.dumps(metrics, indent=2)}")
        
        await engine.cleanup()
    
    # Run test
    asyncio.run(test_ab_testing_engine())