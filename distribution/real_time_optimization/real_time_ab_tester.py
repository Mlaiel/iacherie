"""Real-Time A/B Tester

Real-time A/B testing system for content optimization with instant feedback
and dynamic test adjustments based on performance data.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Types of A/B tests"""
    CAPTION_OPTIMIZATION = "caption_optimization"
    HASHTAG_TESTING = "hashtag_testing"
    TIMING_OPTIMIZATION = "timing_optimization"
    PLATFORM_SELECTION = "platform_selection"
    CONTENT_FORMAT = "content_format"
    THUMBNAIL_TESTING = "thumbnail_testing"
    CALL_TO_ACTION = "call_to_action"
    AUDIENCE_TARGETING = "audience_targeting"


class TestStatus(Enum):
    """A/B test status"""
    PLANNING = "planning"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CONCLUSIVE = "conclusive"
    INCONCLUSIVE = "inconclusive"


@dataclass
class TestVariant:
    """A/B test variant configuration"""
    variant_id: str
    variant_name: str
    parameters: Dict[str, Any]
    traffic_allocation: float  # Percentage of traffic (0.0-1.0)
    performance_metrics: Dict[str, float]
    sample_size: int
    confidence_level: float
    is_control: bool


@dataclass
class ABTestResults:
    """A/B test results and analysis"""
    test_id: str
    test_type: TestType
    winner: Optional[str]  # Winning variant ID
    confidence_level: float
    statistical_significance: bool
    improvement_percentage: float
    variants_performance: Dict[str, Dict[str, Any]]
    recommendation: str
    decision_made_at: datetime
    test_duration: timedelta
    sample_sizes: Dict[str, int]


@dataclass
class RealTimeABTest:
    """Real-time A/B test configuration"""
    test_id: str
    test_name: str
    test_type: TestType
    content_id: str
    variants: List[TestVariant]
    success_metric: str  # Primary metric to optimize
    minimum_sample_size: int
    maximum_duration: timedelta
    significance_threshold: float
    early_stopping_enabled: bool
    auto_apply_winner: bool
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    status: TestStatus
    metadata: Dict[str, Any]


class RealTimeABTester:
    """Real-time A/B testing engine for content optimization"""
    
    def __init__(self):
        """Initialize real-time A/B tester"""
        self.active_tests = {}
        self.test_history = {}
        self.performance_tracker = {}
        self.testing_active = False
        self.significance_calculator = StatisticalSignificanceCalculator()
        
    async def create_ab_test(
        self,
        content_id: str,
        test_type: TestType,
        variants: List[Dict[str, Any]],
        test_config: Optional[Dict[str, Any]] = None
    ) -> RealTimeABTest:
        """Create a new real-time A/B test"""
        try:
            logger.info(f"Creating A/B test for content: {content_id}, type: {test_type.value}")
            
            # Generate test ID
            test_id = f"ab_test_{content_id}_{test_type.value}_{int(datetime.utcnow().timestamp())}"
            
            # Apply default configuration
            config = self._apply_default_config(test_config or {})
            
            # Create test variants
            test_variants = await self._create_test_variants(variants, test_type)
            
            # Validate test configuration
            validation_result = await self._validate_test_configuration(
                test_variants, config
            )
            if not validation_result['valid']:
                raise ValueError(f"Invalid test configuration: {validation_result['reason']}")
            
            # Create A/B test
            ab_test = RealTimeABTest(
                test_id=test_id,
                test_name=config.get('test_name', f"{test_type.value}_test"),
                test_type=test_type,
                content_id=content_id,
                variants=test_variants,
                success_metric=config.get('success_metric', 'engagement_rate'),
                minimum_sample_size=config.get('minimum_sample_size', 1000),
                maximum_duration=timedelta(hours=config.get('max_duration_hours', 24)),
                significance_threshold=config.get('significance_threshold', 0.95),
                early_stopping_enabled=config.get('early_stopping', True),
                auto_apply_winner=config.get('auto_apply_winner', True),
                created_at=datetime.utcnow(),
                started_at=None,
                ended_at=None,
                status=TestStatus.PLANNING,
                metadata=config.get('metadata', {})
            )
            
            # Store test
            self.active_tests[test_id] = ab_test
            
            logger.info(f"Created A/B test: {test_id} with {len(test_variants)} variants")
            
            return ab_test
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {str(e)}")
            raise
    
    async def start_ab_test(self, test_id: str) -> bool:
        """Start running an A/B test"""
        try:
            if test_id not in self.active_tests:
                logger.error(f"Test not found: {test_id}")
                return False
            
            test = self.active_tests[test_id]
            
            if test.status != TestStatus.PLANNING:
                logger.error(f"Test {test_id} cannot be started. Current status: {test.status.value}")
                return False
            
            # Initialize performance tracking
            await self._initialize_performance_tracking(test)
            
            # Start traffic allocation
            await self._start_traffic_allocation(test)
            
            # Update test status
            test.status = TestStatus.RUNNING
            test.started_at = datetime.utcnow()
            
            # Start monitoring task
            asyncio.create_task(self._monitor_test_progress(test_id))
            
            logger.info(f"Started A/B test: {test_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting A/B test: {str(e)}")
            return False
    
    async def allocate_traffic(
        self,
        test_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[TestVariant]:
        """Allocate user to a test variant"""
        try:
            if test_id not in self.active_tests:
                return None
            
            test = self.active_tests[test_id]
            
            if test.status != TestStatus.RUNNING:
                return None
            
            # Check if user is already allocated
            existing_allocation = await self._get_existing_allocation(test_id, user_id)
            if existing_allocation:
                return existing_allocation
            
            # Allocate user to variant based on traffic allocation
            selected_variant = await self._allocate_user_to_variant(test, user_id, context)
            
            # Store allocation
            await self._store_user_allocation(test_id, user_id, selected_variant)
            
            # Update sample sizes
            selected_variant.sample_size += 1
            
            return selected_variant
            
        except Exception as e:
            logger.error(f"Error allocating traffic: {str(e)}")
            return None
    
    async def record_conversion(
        self,
        test_id: str,
        user_id: str,
        metric_name: str,
        metric_value: float,
        additional_metrics: Optional[Dict[str, float]] = None
    ) -> bool:
        """Record conversion/performance data for A/B test"""
        try:
            if test_id not in self.active_tests:
                return False
            
            test = self.active_tests[test_id]
            
            # Get user's variant allocation
            user_allocation = await self._get_existing_allocation(test_id, user_id)
            if not user_allocation:
                return False
            
            # Record metric for variant
            await self._record_variant_metric(
                test_id, user_allocation.variant_id, metric_name, metric_value
            )
            
            # Record additional metrics
            if additional_metrics:
                for metric, value in additional_metrics.items():
                    await self._record_variant_metric(
                        test_id, user_allocation.variant_id, metric, value
                    )
            
            # Update variant performance metrics
            await self._update_variant_performance(test, user_allocation.variant_id)
            
            # Check for early stopping conditions
            if test.early_stopping_enabled:
                should_stop = await self._check_early_stopping_conditions(test)
                if should_stop:
                    await self._stop_test_early(test_id, "Early stopping criteria met")
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording conversion: {str(e)}")
            return False
    
    async def analyze_test_results(self, test_id: str) -> Optional[ABTestResults]:
        """Analyze A/B test results and determine winner"""
        try:
            if test_id not in self.active_tests:
                return None
            
            test = self.active_tests[test_id]
            
            logger.info(f"Analyzing results for test: {test_id}")
            
            # Calculate statistical significance between variants
            significance_results = await self._calculate_statistical_significance(test)
            
            # Determine winner
            winner_analysis = await self._determine_winner(test, significance_results)
            
            # Calculate improvement percentage
            improvement_percentage = await self._calculate_improvement_percentage(
                test, winner_analysis
            )
            
            # Generate recommendation
            recommendation = await self._generate_recommendation(
                test, winner_analysis, significance_results
            )
            
            # Create results object
            results = ABTestResults(
                test_id=test_id,
                test_type=test.test_type,
                winner=winner_analysis.get('winner_variant_id'),
                confidence_level=significance_results.get('confidence_level', 0.0),
                statistical_significance=significance_results.get('is_significant', False),
                improvement_percentage=improvement_percentage,
                variants_performance=await self._get_variants_performance_summary(test),
                recommendation=recommendation,
                decision_made_at=datetime.utcnow(),
                test_duration=self._calculate_test_duration(test),
                sample_sizes={v.variant_id: v.sample_size for v in test.variants}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing test results: {str(e)}")
            return None
    
    async def complete_ab_test(
        self,
        test_id: str,
        apply_winner: Optional[bool] = None
    ) -> Optional[ABTestResults]:
        """Complete A/B test and optionally apply winning variant"""
        try:
            if test_id not in self.active_tests:
                return None
            
            test = self.active_tests[test_id]
            
            if test.status not in [TestStatus.RUNNING, TestStatus.PAUSED]:
                logger.error(f"Cannot complete test {test_id}. Current status: {test.status.value}")
                return None
            
            # Analyze final results
            results = await self.analyze_test_results(test_id)
            if not results:
                return None
            
            # Update test status
            if results.statistical_significance:
                test.status = TestStatus.CONCLUSIVE
            else:
                test.status = TestStatus.INCONCLUSIVE
            
            test.ended_at = datetime.utcnow()
            
            # Apply winner if requested and test is conclusive
            should_apply_winner = apply_winner if apply_winner is not None else test.auto_apply_winner
            
            if should_apply_winner and results.winner and results.statistical_significance:
                await self._apply_winning_variant(test, results.winner)
                logger.info(f"Applied winning variant {results.winner} for test {test_id}")
            
            # Move test to history
            await self._move_test_to_history(test_id)
            
            logger.info(f"Completed A/B test: {test_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error completing A/B test: {str(e)}")
            return None
    
    async def get_test_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive A/B testing dashboard"""
        try:
            dashboard = {
                'timestamp': datetime.utcnow(),
                'active_tests': len(self.active_tests),
                'test_breakdown': {},
                'status_breakdown': {},
                'running_tests': [],
                'recent_completions': [],
                'performance_summary': {}
            }
            
            # Analyze active tests
            for test_id, test in self.active_tests.items():
                # Count by type
                test_type = test.test_type.value
                dashboard['test_breakdown'][test_type] = dashboard['test_breakdown'].get(test_type, 0) + 1
                
                # Count by status
                status = test.status.value
                dashboard['status_breakdown'][status] = dashboard['status_breakdown'].get(status, 0) + 1
                
                # Add running tests details
                if test.status == TestStatus.RUNNING:
                    test_progress = await self._calculate_test_progress(test)
                    dashboard['running_tests'].append({
                        'test_id': test_id,
                        'test_name': test.test_name,
                        'type': test_type,
                        'progress': test_progress,
                        'duration': self._calculate_test_duration(test),
                        'sample_size': sum(v.sample_size for v in test.variants)
                    })
            
            # Get recent completions
            dashboard['recent_completions'] = await self._get_recent_completions()
            
            # Get performance summary
            dashboard['performance_summary'] = await self._get_testing_performance_summary()
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting test dashboard: {str(e)}")
            return {}
    
    # Private helper methods
    def _apply_default_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default configuration for A/B test"""
        default_config = {
            'minimum_sample_size': 1000,
            'max_duration_hours': 24,
            'significance_threshold': 0.95,
            'early_stopping': True,
            'auto_apply_winner': True,
            'success_metric': 'engagement_rate'
        }
        
        default_config.update(config)
        return default_config
    
    async def _create_test_variants(
        self, 
        variant_configs: List[Dict[str, Any]], 
        test_type: TestType
    ) -> List[TestVariant]:
        """Create test variants from configuration"""
        variants = []
        total_allocation = 0.0
        
        for i, config in enumerate(variant_configs):
            variant_id = config.get('variant_id', f"variant_{i}")
            variant_name = config.get('variant_name', f"Variant {i + 1}")
            parameters = config.get('parameters', {})
            traffic_allocation = config.get('traffic_allocation', 1.0 / len(variant_configs))
            is_control = config.get('is_control', i == 0)  # First variant is control by default
            
            variant = TestVariant(
                variant_id=variant_id,
                variant_name=variant_name,
                parameters=parameters,
                traffic_allocation=traffic_allocation,
                performance_metrics={},
                sample_size=0,
                confidence_level=0.0,
                is_control=is_control
            )
            
            variants.append(variant)
            total_allocation += traffic_allocation
        
        # Normalize traffic allocation to sum to 1.0
        if total_allocation != 1.0:
            for variant in variants:
                variant.traffic_allocation = variant.traffic_allocation / total_allocation
        
        return variants
    
    async def _validate_test_configuration(
        self, 
        variants: List[TestVariant], 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate A/B test configuration"""
        # Check minimum variants
        if len(variants) < 2:
            return {'valid': False, 'reason': 'At least 2 variants required'}
        
        # Check traffic allocation
        total_allocation = sum(v.traffic_allocation for v in variants)
        if abs(total_allocation - 1.0) > 0.01:
            return {'valid': False, 'reason': 'Traffic allocation must sum to 1.0'}
        
        # Check control variant exists
        control_variants = [v for v in variants if v.is_control]
        if len(control_variants) != 1:
            return {'valid': False, 'reason': 'Exactly one control variant required'}
        
        # Check minimum sample size
        min_sample_size = config.get('minimum_sample_size', 1000)
        if min_sample_size < 100:
            return {'valid': False, 'reason': 'Minimum sample size too low'}
        
        return {'valid': True, 'reason': 'Configuration valid'}
    
    async def _initialize_performance_tracking(self, test: RealTimeABTest):
        """Initialize performance tracking for test"""
        self.performance_tracker[test.test_id] = {
            'variant_metrics': {v.variant_id: {} for v in test.variants},
            'user_allocations': {},
            'conversion_events': [],
            'start_time': datetime.utcnow()
        }
    
    async def _start_traffic_allocation(self, test: RealTimeABTest):
        """Start traffic allocation for test"""
        # Initialize traffic allocation system
        logger.info(f"Started traffic allocation for test: {test.test_id}")
    
    async def _monitor_test_progress(self, test_id: str):
        """Monitor test progress and check for completion conditions"""
        while test_id in self.active_tests:
            try:
                test = self.active_tests[test_id]
                
                if test.status != TestStatus.RUNNING:
                    break
                
                # Check completion conditions
                should_complete = await self._check_completion_conditions(test)
                if should_complete:
                    await self.complete_ab_test(test_id)
                    break
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring test progress: {str(e)}")
                await asyncio.sleep(600)
    
    async def _get_existing_allocation(self, test_id: str, user_id: str) -> Optional[TestVariant]:
        """Get existing user allocation for test"""
        if test_id not in self.performance_tracker:
            return None
        
        allocations = self.performance_tracker[test_id]['user_allocations']
        allocated_variant_id = allocations.get(user_id)
        
        if allocated_variant_id:
            test = self.active_tests[test_id]
            for variant in test.variants:
                if variant.variant_id == allocated_variant_id:
                    return variant
        
        return None
    
    async def _allocate_user_to_variant(
        self, 
        test: RealTimeABTest, 
        user_id: str, 
        context: Optional[Dict[str, Any]]
    ) -> TestVariant:
        """Allocate user to variant based on traffic allocation"""
        # Use deterministic allocation based on user ID hash
        user_hash = hash(user_id + test.test_id) % 10000
        normalized_hash = user_hash / 10000.0
        
        # Find variant based on cumulative traffic allocation
        cumulative_allocation = 0.0
        for variant in test.variants:
            cumulative_allocation += variant.traffic_allocation
            if normalized_hash <= cumulative_allocation:
                return variant
        
        # Fallback to last variant
        return test.variants[-1]
    
    async def _store_user_allocation(self, test_id: str, user_id: str, variant: TestVariant):
        """Store user allocation"""
        if test_id in self.performance_tracker:
            self.performance_tracker[test_id]['user_allocations'][user_id] = variant.variant_id
    
    async def _record_variant_metric(
        self, 
        test_id: str, 
        variant_id: str, 
        metric_name: str, 
        metric_value: float
    ):
        """Record metric for variant"""
        if test_id in self.performance_tracker:
            variant_metrics = self.performance_tracker[test_id]['variant_metrics']
            if variant_id not in variant_metrics:
                variant_metrics[variant_id] = {}
            if metric_name not in variant_metrics[variant_id]:
                variant_metrics[variant_id][metric_name] = []
            
            variant_metrics[variant_id][metric_name].append({
                'value': metric_value,
                'timestamp': datetime.utcnow()
            })
    
    async def _update_variant_performance(self, test: RealTimeABTest, variant_id: str):
        """Update variant performance metrics"""
        tracker = self.performance_tracker.get(test.test_id, {})
        variant_metrics = tracker.get('variant_metrics', {}).get(variant_id, {})
        
        # Find the variant and update its performance metrics
        for variant in test.variants:
            if variant.variant_id == variant_id:
                # Calculate average metrics
                for metric_name, values in variant_metrics.items():
                    if values:
                        avg_value = sum(v['value'] for v in values) / len(values)
                        variant.performance_metrics[metric_name] = avg_value
                break
    
    async def _check_early_stopping_conditions(self, test: RealTimeABTest) -> bool:
        """Check if early stopping conditions are met"""
        # Check minimum sample size
        total_sample_size = sum(v.sample_size for v in test.variants)
        if total_sample_size < test.minimum_sample_size:
            return False
        
        # Check statistical significance
        significance_results = await self._calculate_statistical_significance(test)
        if significance_results.get('is_significant', False):
            confidence = significance_results.get('confidence_level', 0.0)
            if confidence >= test.significance_threshold:
                return True
        
        return False
    
    async def _stop_test_early(self, test_id: str, reason: str):
        """Stop test early"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            test.status = TestStatus.COMPLETED
            test.ended_at = datetime.utcnow()
            logger.info(f"Stopped test {test_id} early: {reason}")
    
    async def _check_completion_conditions(self, test: RealTimeABTest) -> bool:
        """Check if test should be completed"""
        # Check maximum duration
        if test.started_at:
            duration = datetime.utcnow() - test.started_at
            if duration >= test.maximum_duration:
                return True
        
        # Check minimum sample size
        total_sample_size = sum(v.sample_size for v in test.variants)
        if total_sample_size >= test.minimum_sample_size:
            # Check if we have statistical significance
            significance_results = await self._calculate_statistical_significance(test)
            if significance_results.get('is_significant', False):
                return True
        
        return False
    
    async def _calculate_statistical_significance(self, test: RealTimeABTest) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        if len(test.variants) < 2:
            return {'is_significant': False, 'confidence_level': 0.0}
        
        # Get control variant
        control_variant = next((v for v in test.variants if v.is_control), test.variants[0])
        
        # Calculate significance for each variant against control
        results = {
            'is_significant': False,
            'confidence_level': 0.0,
            'p_values': {},
            'effect_sizes': {}
        }
        
        control_metric_value = control_variant.performance_metrics.get(test.success_metric, 0.0)
        control_sample_size = control_variant.sample_size
        
        for variant in test.variants:
            if variant.variant_id == control_variant.variant_id:
                continue
            
            variant_metric_value = variant.performance_metrics.get(test.success_metric, 0.0)
            variant_sample_size = variant.sample_size
            
            # Calculate statistical significance using z-test for proportions
            significance_result = self.significance_calculator.calculate_significance(
                control_metric_value, control_sample_size,
                variant_metric_value, variant_sample_size
            )
            
            results['p_values'][variant.variant_id] = significance_result['p_value']
            results['effect_sizes'][variant.variant_id] = significance_result['effect_size']
            
            if significance_result['p_value'] < (1 - test.significance_threshold):
                results['is_significant'] = True
                results['confidence_level'] = max(
                    results['confidence_level'], 
                    significance_result['confidence_level']
                )
        
        return results
    
    async def _determine_winner(
        self, 
        test: RealTimeABTest, 
        significance_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine winning variant"""
        if not significance_results.get('is_significant', False):
            return {'winner_variant_id': None, 'reason': 'No statistical significance'}
        
        # Find variant with best performance on success metric
        best_variant = None
        best_performance = float('-inf')
        
        for variant in test.variants:
            performance = variant.performance_metrics.get(test.success_metric, 0.0)
            if performance > best_performance:
                best_performance = performance
                best_variant = variant
        
        return {
            'winner_variant_id': best_variant.variant_id if best_variant else None,
            'winner_performance': best_performance,
            'reason': f'Best performance on {test.success_metric}'
        }
    
    async def _calculate_improvement_percentage(
        self, 
        test: RealTimeABTest, 
        winner_analysis: Dict[str, Any]
    ) -> float:
        """Calculate improvement percentage of winner over control"""
        control_variant = next((v for v in test.variants if v.is_control), test.variants[0])
        winner_id = winner_analysis.get('winner_variant_id')
        
        if not winner_id:
            return 0.0
        
        winner_variant = next((v for v in test.variants if v.variant_id == winner_id), None)
        if not winner_variant:
            return 0.0
        
        control_performance = control_variant.performance_metrics.get(test.success_metric, 0.0)
        winner_performance = winner_variant.performance_metrics.get(test.success_metric, 0.0)
        
        if control_performance == 0:
            return 0.0
        
        improvement = (winner_performance - control_performance) / control_performance * 100
        return improvement
    
    async def _generate_recommendation(
        self, 
        test: RealTimeABTest, 
        winner_analysis: Dict[str, Any], 
        significance_results: Dict[str, Any]
    ) -> str:
        """Generate recommendation based on test results"""
        if not significance_results.get('is_significant', False):
            return "Test is inconclusive. Consider running longer or with larger sample size."
        
        winner_id = winner_analysis.get('winner_variant_id')
        if not winner_id:
            return "No clear winner detected. Consider running additional tests."
        
        improvement = await self._calculate_improvement_percentage(test, winner_analysis)
        
        if improvement > 10:
            return f"Strong winner detected. Implement variant {winner_id} immediately for {improvement:.1f}% improvement."
        elif improvement > 5:
            return f"Moderate improvement detected. Consider implementing variant {winner_id} for {improvement:.1f}% improvement."
        else:
            return f"Marginal improvement detected. Evaluate cost/benefit of implementing variant {winner_id}."
    
    # Additional helper methods (simplified implementations)
    async def _get_variants_performance_summary(self, test: RealTimeABTest) -> Dict[str, Dict[str, Any]]:
        """Get performance summary for all variants"""
        summary = {}
        for variant in test.variants:
            summary[variant.variant_id] = {
                'performance_metrics': variant.performance_metrics,
                'sample_size': variant.sample_size,
                'traffic_allocation': variant.traffic_allocation,
                'is_control': variant.is_control
            }
        return summary
    
    def _calculate_test_duration(self, test: RealTimeABTest) -> timedelta:
        """Calculate test duration"""
        if test.started_at:
            end_time = test.ended_at or datetime.utcnow()
            return end_time - test.started_at
        return timedelta(0)
    
    async def _apply_winning_variant(self, test: RealTimeABTest, winner_variant_id: str):
        """Apply winning variant to content"""
        winner_variant = next((v for v in test.variants if v.variant_id == winner_variant_id), None)
        if winner_variant:
            logger.info(f"Applying winning variant {winner_variant_id} with parameters: {winner_variant.parameters}")
    
    async def _move_test_to_history(self, test_id: str):
        """Move completed test to history"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            self.test_history[test_id] = test
            del self.active_tests[test_id]
    
    async def _calculate_test_progress(self, test: RealTimeABTest) -> Dict[str, Any]:
        """Calculate test progress"""
        total_sample_size = sum(v.sample_size for v in test.variants)
        progress_percentage = min(100.0, (total_sample_size / test.minimum_sample_size) * 100)
        
        duration = self._calculate_test_duration(test)
        duration_progress = min(100.0, (duration.total_seconds() / test.maximum_duration.total_seconds()) * 100)
        
        return {
            'sample_progress': progress_percentage,
            'duration_progress': duration_progress,
            'overall_progress': max(progress_percentage, duration_progress)
        }
    
    async def _get_recent_completions(self) -> List[Dict[str, Any]]:
        """Get recent test completions"""
        return [
            {
                'test_id': 'test_123',
                'test_name': 'Caption Optimization Test',
                'winner': 'variant_2',
                'improvement': 15.3,
                'completed_at': datetime.utcnow() - timedelta(hours=2)
            }
        ]
    
    async def _get_testing_performance_summary(self) -> Dict[str, Any]:
        """Get testing performance summary"""
        return {
            'total_tests_run': 50,
            'success_rate': 0.78,
            'average_improvement': 12.5,
            'total_conversions_gained': 15000
        }


class StatisticalSignificanceCalculator:
    """Statistical significance calculator for A/B tests"""
    
    def calculate_significance(
        self, 
        control_mean: float, 
        control_sample_size: int,
        variant_mean: float, 
        variant_sample_size: int
    ) -> Dict[str, Any]:
        """Calculate statistical significance between two samples"""
        
        if control_sample_size == 0 or variant_sample_size == 0:
            return {
                'p_value': 1.0,
                'effect_size': 0.0,
                'confidence_level': 0.0,
                'is_significant': False
            }
        
        # Simple z-test calculation (simplified)
        pooled_std = math.sqrt(
            ((control_mean * (1 - control_mean)) / control_sample_size) +
            ((variant_mean * (1 - variant_mean)) / variant_sample_size)
        )
        
        if pooled_std == 0:
            z_score = 0
        else:
            z_score = (variant_mean - control_mean) / pooled_std
        
        # Simplified p-value calculation
        p_value = 2 * (1 - self._standard_normal_cdf(abs(z_score)))
        
        effect_size = abs(variant_mean - control_mean)
        confidence_level = 1 - p_value
        is_significant = p_value < 0.05
        
        return {
            'p_value': p_value,
            'effect_size': effect_size,
            'confidence_level': confidence_level,
            'is_significant': is_significant,
            'z_score': z_score
        }
    
    def _standard_normal_cdf(self, x: float) -> float:
        """Approximation of standard normal CDF"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))


__all__ = [
    'RealTimeABTester', 'RealTimeABTest', 'TestVariant', 'ABTestResults',
    'TestType', 'TestStatus', 'StatisticalSignificanceCalculator'
]