"""A/B Testing Engine

Advanced automated A/B testing system for optimizing content performance
across multiple platforms with statistical significance testing and
intelligent variant generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
try:
    import numpy as np
    from scipy import stats
except ImportError:
    np = stats = None
from collections import defaultdict
import random

from .platform_connectors import SocialPlatform, ContentPayload, PublicationResult


def safe_mean(values) -> None:
    """Calculate mean safely without numpy"""
    if not values:
        return 0.0
    return sum(values) / len(values)

def safe_random_uniform(low, high) -> None:
    """Generate random uniform value without numpy"""
    import random
    return random.uniform(low, high)

def safe_sqrt(value) -> None:
    """Calculate square root safely"""
    import math
    return math.sqrt(max(0, value))

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Types of A/B tests supported"""
    TITLE_OPTIMIZATION = "title_optimization"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    POSTING_TIME = "posting_time"
    CONTENT_FORMAT = "content_format"
    THUMBNAIL_TESTING = "thumbnail_testing"
    DESCRIPTION_TESTING = "description_testing"
    CTA_OPTIMIZATION = "cta_optimization"
    AUDIENCE_TARGETING = "audience_targeting"
    PLATFORM_COMPARISON = "platform_comparison"


class TestStatus(Enum):
    """A/B test status states"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class StatisticalSignificance(Enum):
    """Statistical significance levels"""
    NOT_SIGNIFICANT = "not_significant"
    TRENDING = "trending"
    SIGNIFICANT = "significant"
    HIGHLY_SIGNIFICANT = "highly_significant"


@dataclass
class TestVariant:
    """A/B test variant configuration"""
    id: str
    name: str
    description: str
    
    # Content modifications
    content_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Targeting changes
    audience_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Timing changes
    timing_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Platform-specific changes
    platform_changes: Dict[SocialPlatform, Dict[str, Any]] = field(default_factory=dict)
    
    # Traffic allocation
    traffic_percentage: float = 50.0
    
    # Expected performance
    expected_lift: Optional[float] = None
    hypothesis: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for test analysis"""
    # Core metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    
    # Engagement metrics
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saves: int = 0
    
    # Calculated metrics
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    cost_per_click: float = 0.0
    cost_per_conversion: float = 0.0
    return_on_ad_spend: float = 0.0
    engagement_rate: float = 0.0
    
    # Statistical data
    sample_size: int = 0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    p_value: float = 1.0
    
    # Time-based metrics
    measurement_start: datetime = field(default_factory=datetime.now)
    measurement_end: Optional[datetime] = None


@dataclass
class TestResult:
    """A/B test result with statistical analysis"""
    test_id: str
    test_type: TestType
    
    # Variant performance
    variant_results: Dict[str, PerformanceMetrics] = field(default_factory=dict)
    
    # Statistical analysis
    winner: Optional[str] = None
    statistical_significance: StatisticalSignificance = StatisticalSignificance.NOT_SIGNIFICANT
    confidence_level: float = 0.0
    
    # Performance comparison
    performance_lift: Dict[str, float] = field(default_factory=dict)  # % improvement over control
    
    # Insights and recommendations
    key_insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Test metadata
    test_duration_hours: float = 0.0
    total_traffic: int = 0
    cost_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Completion info
    completed_at: Optional[datetime] = None
    early_stopped: bool = False
    early_stop_reason: Optional[str] = None


class ABTestingEngine:
    """Advanced automated A/B testing system"""
    
    # Test configuration defaults
    DEFAULT_TEST_CONFIG = {
        "minimum_sample_size": 1000,
        "maximum_test_duration_days": 14,
        "confidence_level": 0.95,
        "minimum_detectable_effect": 0.05,  # 5% minimum improvement
        "early_stopping_enabled": True,
        "statistical_power": 0.8
    }
    
    # Platform-specific test configurations
    PLATFORM_TEST_CONFIGS = {
        SocialPlatform.INSTAGRAM: {
            "optimal_test_duration_hours": 72,
            "minimum_sample_size": 500,
            "primary_metrics": ["engagement_rate", "reach", "clicks"]
        },
        SocialPlatform.TIKTOK: {
            "optimal_test_duration_hours": 48,
            "minimum_sample_size": 1000,
            "primary_metrics": ["views", "shares", "completion_rate"]
        },
        SocialPlatform.YOUTUBE: {
            "optimal_test_duration_hours": 168,  # 1 week
            "minimum_sample_size": 2000,
            "primary_metrics": ["views", "watch_time", "subscribers"]
        },
        SocialPlatform.TWITTER: {
            "optimal_test_duration_hours": 24,
            "minimum_sample_size": 300,
            "primary_metrics": ["impressions", "engagements", "clicks"]
        },
        SocialPlatform.FACEBOOK: {
            "optimal_test_duration_hours": 96,
            "minimum_sample_size": 800,
            "primary_metrics": ["reach", "engagement", "clicks"]
        },
        SocialPlatform.LINKEDIN: {
            "optimal_test_duration_hours": 120,  # 5 days
            "minimum_sample_size": 400,
            "primary_metrics": ["impressions", "clicks", "leads"]
        }
    }
    
    def __init__(self) -> None:
        self.active_tests: Dict[str, Dict[str, Any]] = {}
        self.completed_tests: Dict[str, TestResult] = {}
        self.test_performance_data: Dict[str, Dict[str, List[PerformanceMetrics]]] = defaultdict(lambda: defaultdict(list))
        self.variant_generators: Dict[TestType, callable] = {}
        
        # Initialize variant generators
        self._initialize_variant_generators()
    
    def _initialize_variant_generators(self) -> None:
        """Initialize variant generation functions"""
        self.variant_generators = {
            TestType.TITLE_OPTIMIZATION: self._generate_title_variants,
            TestType.HASHTAG_OPTIMIZATION: self._generate_hashtag_variants,
            TestType.POSTING_TIME: self._generate_timing_variants,
            TestType.CONTENT_FORMAT: self._generate_format_variants,
            TestType.THUMBNAIL_TESTING: self._generate_thumbnail_variants,
            TestType.DESCRIPTION_TESTING: self._generate_description_variants,
            TestType.CTA_OPTIMIZATION: self._generate_cta_variants,
            TestType.AUDIENCE_TARGETING: self._generate_audience_variants
        }
    
    async def create_ab_test(
        self,
        test_name: str,
        test_type: TestType,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform],
        primary_metric: str = "engagement_rate",
        custom_variants: Optional[List[TestVariant]] = None,
        test_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create and configure a new A/B test"""
        try:
            test_id = str(uuid.uuid4())
            
            # Merge test configuration
            config = {**self.DEFAULT_TEST_CONFIG, **(test_config or {})}
            
            # Generate test variants
            if custom_variants:
                variants = custom_variants
            else:
                variants = await self._generate_test_variants(
                    test_type, base_content, target_platforms
                )
            
            # Calculate traffic allocation
            total_allocation = sum(v.traffic_percentage for v in variants)
            if total_allocation != 100.0:
                # Normalize allocations
                for variant in variants:
                    variant.traffic_percentage = (variant.traffic_percentage / total_allocation) * 100.0
            
            # Calculate required sample size
            required_sample_size = self._calculate_sample_size(
                primary_metric=primary_metric,
                minimum_detectable_effect=config["minimum_detectable_effect"],
                statistical_power=config["statistical_power"],
                confidence_level=config["confidence_level"]
            )
            
            # Create test configuration
            test_data = {
                "test_id": test_id,
                "test_name": test_name,
                "test_type": test_type,
                "status": TestStatus.DRAFT,
                "base_content": asdict(base_content),
                "variants": [asdict(v) for v in variants],
                "target_platforms": [p.value for p in target_platforms],
                "primary_metric": primary_metric,
                "config": config,
                "required_sample_size": required_sample_size,
                "created_at": datetime.now(),
                "started_at": None,
                "scheduled_end": None,
                "actual_metrics": {}
            }
            
            self.active_tests[test_id] = test_data
            
            logger.info(f"Created A/B test '{test_name}' with {len(variants)} variants")
            return test_id
        
        except Exception as e:
            logger.error(f"A/B test creation failed: {str(e)}")
            raise
    
    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        try:
            if test_id not in self.active_tests:
                logger.error(f"Test {test_id} not found")
                return False
            
            test_data = self.active_tests[test_id]
            
            if test_data["status"] != TestStatus.DRAFT:
                logger.error(f"Test {test_id} is not in draft status")
                return False
            
            # Update test status
            test_data["status"] = TestStatus.RUNNING
            test_data["started_at"] = datetime.now()
            
            # Calculate scheduled end time
            max_duration_days = test_data["config"]["maximum_test_duration_days"]
            test_data["scheduled_end"] = datetime.now() + timedelta(days=max_duration_days)
            
            # Initialize performance tracking
            for variant in test_data["variants"]:
                variant_id = variant["id"]
                self.test_performance_data[test_id][variant_id] = []
            
            logger.info(f"Started A/B test {test_id}")
            return True
        
        except Exception as e:
            logger.error(f"Test start failed: {str(e)}")
            return False
    
    async def record_performance(
        self,
        test_id -> None: str,
        variant_id -> None: str,
        platform -> None: SocialPlatform,
        metrics -> None: Dict[str, Any]
    ) -> None:
        """Record performance metrics for a test variant"""
        try:
            if test_id not in self.active_tests:
                logger.warning(f"Performance recorded for unknown test {test_id}")
                return
            
            test_data = self.active_tests[test_id]
            
            if test_data["status"] != TestStatus.RUNNING:
                logger.warning(f"Performance recorded for non-running test {test_id}")
                return
            
            # Create performance metrics object
            performance = PerformanceMetrics(
                impressions=metrics.get("impressions", 0),
                clicks=metrics.get("clicks", 0),
                conversions=metrics.get("conversions", 0),
                revenue=metrics.get("revenue", 0.0),
                likes=metrics.get("likes", 0),
                shares=metrics.get("shares", 0),
                comments=metrics.get("comments", 0),
                saves=metrics.get("saves", 0),
                sample_size=metrics.get("sample_size", 0),
                measurement_start=datetime.now()
            )
            
            # Calculate derived metrics
            if performance.impressions > 0:
                performance.click_through_rate = performance.clicks / performance.impressions
                performance.engagement_rate = (
                    (performance.likes + performance.shares + performance.comments + performance.saves) /
                    performance.impressions
                )
            
            if performance.clicks > 0:
                performance.conversion_rate = performance.conversions / performance.clicks
            
            # Store performance data
            self.test_performance_data[test_id][variant_id].append(performance)
            
            # Check for early stopping conditions
            if test_data["config"]["early_stopping_enabled"]:
                await self._check_early_stopping(test_id)
        
        except Exception as e:
            logger.error(f"Performance recording failed: {str(e)}")
    
    async def _check_early_stopping(self, test_id -> None: str) -> None:
        """Check if test meets early stopping criteria"""
        try:
            test_data = self.active_tests[test_id]
            
            # Get latest performance data
            variant_performance = {}
            
            for variant in test_data["variants"]:
                variant_id = variant["id"]
                performance_history = self.test_performance_data[test_id][variant_id]
                
                if performance_history:
                    # Get most recent performance
                    variant_performance[variant_id] = performance_history[-1]
            
            if len(variant_performance) < 2:
                return  # Need at least 2 variants to compare
            
            # Check sample size requirements
            min_sample_size = test_data["required_sample_size"]
            total_sample_size = sum(p.sample_size for p in variant_performance.values())
            
            if total_sample_size < min_sample_size:
                return  # Not enough data yet
            
            # Perform statistical significance test
            primary_metric = test_data["primary_metric"]
            significance_result = await self._test_statistical_significance(
                variant_performance, primary_metric
            )
            
            # Check for early stopping conditions
            if significance_result["significance"] == StatisticalSignificance.HIGHLY_SIGNIFICANT:
                # High confidence - can stop early
                await self._complete_test(test_id, early_stop=True, reason="High statistical significance reached")
            elif significance_result["significance"] == StatisticalSignificance.SIGNIFICANT:
                # Check if test has run for minimum duration
                test_start = test_data["started_at"]
                min_duration = timedelta(hours=24)  # Minimum 24 hours
                
                if datetime.now() - test_start > min_duration:
                    await self._complete_test(test_id, early_stop=True, reason="Statistical significance reached")
        
        except Exception as e:
            logger.error(f"Early stopping check failed: {str(e)}")
    
    async def _test_statistical_significance(
        self,
        variant_performance: Dict[str, PerformanceMetrics],
        metric: str
    ) -> Dict[str, Any]:
        """Test statistical significance between variants"""
        try:
            # Get metric values for each variant
            variant_data = {}
            
            for variant_id, performance in variant_performance.items():
                if hasattr(performance, metric):
                    metric_value = getattr(performance, metric)
                    sample_size = performance.sample_size
                    
                    # Create synthetic data for statistical testing
                    # In real implementation, this would use actual individual data points
                    if metric in ["click_through_rate", "conversion_rate", "engagement_rate"]:
                        # For rate metrics, create binary outcome data
                        successes = int(metric_value * sample_size)
                        variant_data[variant_id] = {
                            "successes": successes,
                            "sample_size": sample_size,
                            "rate": metric_value
                        }
                    else:
                        # For count metrics, use Poisson distribution
                        variant_data[variant_id] = {
                            "value": metric_value,
                            "sample_size": sample_size
                        }
            
            if len(variant_data) < 2:
                return {
                    "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                    "p_value": 1.0,
                    "confidence": 0.0
                }
            
            # Perform two-sample test
            variant_ids = list(variant_data.keys())
            control_id = variant_ids[0]  # First variant as control
            treatment_id = variant_ids[1]  # Second variant as treatment
            
            control_data = variant_data[control_id]
            treatment_data = variant_data[treatment_id]
            
            if metric in ["click_through_rate", "conversion_rate", "engagement_rate"]:
                # Two-proportion z-test
                p_value, confidence = self._two_proportion_test(
                    control_data["successes"], control_data["sample_size"],
                    treatment_data["successes"], treatment_data["sample_size"]
                )
            else:
                # Two-sample t-test (simplified)
                # In practice, you'd need the actual distribution of values
                control_mean = control_data["value"]
                treatment_mean = treatment_data["value"]
                
                # Estimate standard errors (simplified)
                control_se = math.sqrt(control_mean) / math.sqrt(control_data["sample_size"])
                treatment_se = math.sqrt(treatment_mean) / math.sqrt(treatment_data["sample_size"])
                
                # Pooled standard error
                pooled_se = math.sqrt(control_se**2 + treatment_se**2)
                
                if pooled_se > 0:
                    z_score = (treatment_mean - control_mean) / pooled_se
                    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
                    confidence = 1 - p_value
                else:
                    p_value = 1.0
                    confidence = 0.0
            
            # Determine significance level
            if p_value < 0.001:
                significance = StatisticalSignificance.HIGHLY_SIGNIFICANT
            elif p_value < 0.05:
                significance = StatisticalSignificance.SIGNIFICANT
            elif p_value < 0.1:
                significance = StatisticalSignificance.TRENDING
            else:
                significance = StatisticalSignificance.NOT_SIGNIFICANT
            
            return {
                "significance": significance,
                "p_value": p_value,
                "confidence": confidence,
                "control_metric": control_data.get("rate", control_data.get("value", 0)),
                "treatment_metric": treatment_data.get("rate", treatment_data.get("value", 0))
            }
        
        except Exception as e:
            logger.error(f"Statistical significance test failed: {str(e)}")
            return {
                "significance": StatisticalSignificance.NOT_SIGNIFICANT,
                "p_value": 1.0,
                "confidence": 0.0
            }
    
    def _two_proportion_test(self, x1: int, n1: int, x2: int, n2: int) -> Tuple[float, float]:
        """Perform two-proportion z-test"""
        try:
            p1 = x1 / n1 if n1 > 0 else 0
            p2 = x2 / n2 if n2 > 0 else 0
            
            # Pooled proportion
            p_pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) > 0 else 0
            
            # Standard error
            se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)) if p_pooled > 0 and p_pooled < 1 else 0
            
            if se > 0:
                # Z-score
                z = (p2 - p1) / se
                
                # Two-tailed p-value
                p_value = 2 * (1 - stats.norm.cdf(abs(z)))
                confidence = 1 - p_value
            else:
                p_value = 1.0
                confidence = 0.0
            
            return p_value, confidence
        
        except Exception as e:
            logger.error(f"Two-proportion test failed: {str(e)}")
            return 1.0, 0.0
    
    async def _complete_test(self, test_id -> None: str, early_stop -> None: bool = False, reason -> None: Optional[str] = None) -> None:
        """Complete an A/B test and generate results"""
        try:
            test_data = self.active_tests[test_id]
            test_data["status"] = TestStatus.COMPLETED
            
            # Generate test results
            result = await self._analyze_test_results(test_id)
            
            if early_stop:
                result.early_stopped = True
                result.early_stop_reason = reason
            
            result.completed_at = datetime.now()
            
            # Calculate test duration
            start_time = test_data["started_at"]
            result.test_duration_hours = (datetime.now() - start_time).total_seconds() / 3600
            
            # Store completed test
            self.completed_tests[test_id] = result
            
            # Remove from active tests
            del self.active_tests[test_id]
            
            logger.info(f"Completed A/B test {test_id} - Winner: {result.winner}")
        
        except Exception as e:
            logger.error(f"Test completion failed: {str(e)}")
    
    async def _analyze_test_results(self, test_id: str) -> TestResult:
        """Analyze test results and determine winner"""
        try:
            test_data = self.active_tests[test_id]
            
            # Collect final performance metrics
            variant_results = {}
            
            for variant in test_data["variants"]:
                variant_id = variant["id"]
                performance_history = self.test_performance_data[test_id][variant_id]
                
                if performance_history:
                    # Aggregate performance metrics
                    final_performance = self._aggregate_performance_metrics(performance_history)
                    variant_results[variant_id] = final_performance
            
            # Perform statistical analysis
            primary_metric = test_data["primary_metric"]
            significance_result = await self._test_statistical_significance(
                variant_results, primary_metric
            )
            
            # Determine winner
            winner = None
            if significance_result["significance"] in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]:
                # Find variant with best performance
                best_performance = 0
                for variant_id, performance in variant_results.items():
                    metric_value = getattr(performance, primary_metric, 0)
                    if metric_value > best_performance:
                        best_performance = metric_value
                        winner = variant_id
            
            # Calculate performance lift
            performance_lift = {}
            if len(variant_results) >= 2:
                control_id = list(variant_results.keys())[0]  # First variant as control
                control_performance = getattr(variant_results[control_id], primary_metric, 0)
                
                for variant_id, performance in variant_results.items():
                    if variant_id != control_id:
                        variant_performance = getattr(performance, primary_metric, 0)
                        if control_performance > 0:
                            lift = ((variant_performance - control_performance) / control_performance) * 100
                        else:
                            lift = 0
                        performance_lift[variant_id] = lift
            
            # Generate insights and recommendations
            insights = self._generate_test_insights(test_data, variant_results, significance_result)
            recommendations = self._generate_test_recommendations(test_data, variant_results, winner)
            
            # Calculate total traffic
            total_traffic = sum(p.sample_size for p in variant_results.values())
            
            # Create test result
            result = TestResult(
                test_id=test_id,
                test_type=TestType(test_data["test_type"]),
                variant_results=variant_results,
                winner=winner,
                statistical_significance=significance_result["significance"],
                confidence_level=significance_result["confidence"],
                performance_lift=performance_lift,
                key_insights=insights,
                recommendations=recommendations,
                total_traffic=total_traffic
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Test result analysis failed: {str(e)}")
            return TestResult(test_id=test_id, test_type=TestType.TITLE_OPTIMIZATION)
    
    def _aggregate_performance_metrics(self, performance_history: List[PerformanceMetrics]) -> PerformanceMetrics:
        """Aggregate performance metrics from history"""
        if not performance_history:
            return PerformanceMetrics()
        
        # Sum cumulative metrics
        total_impressions = sum(p.impressions for p in performance_history)
        total_clicks = sum(p.clicks for p in performance_history)
        total_conversions = sum(p.conversions for p in performance_history)
        total_revenue = sum(p.revenue for p in performance_history)
        total_likes = sum(p.likes for p in performance_history)
        total_shares = sum(p.shares for p in performance_history)
        total_comments = sum(p.comments for p in performance_history)
        total_saves = sum(p.saves for p in performance_history)
        total_sample_size = sum(p.sample_size for p in performance_history)
        
        # Calculate rates
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        cvr = total_conversions / total_clicks if total_clicks > 0 else 0
        engagement_rate = (total_likes + total_shares + total_comments + total_saves) / total_impressions if total_impressions > 0 else 0
        
        return PerformanceMetrics(
            impressions=total_impressions,
            clicks=total_clicks,
            conversions=total_conversions,
            revenue=total_revenue,
            likes=total_likes,
            shares=total_shares,
            comments=total_comments,
            saves=total_saves,
            click_through_rate=ctr,
            conversion_rate=cvr,
            engagement_rate=engagement_rate,
            sample_size=total_sample_size,
            measurement_start=performance_history[0].measurement_start,
            measurement_end=performance_history[-1].measurement_start
        )
    
    def _generate_test_insights(
        self,
        test_data: Dict[str, Any],
        variant_results: Dict[str, PerformanceMetrics],
        significance_result: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from test results"""
        insights = []
        
        test_type = TestType(test_data["test_type"])
        primary_metric = test_data["primary_metric"]
        
        # Statistical significance insight
        significance = significance_result["significance"]
        if significance == StatisticalSignificance.HIGHLY_SIGNIFICANT:
            insights.append(f"Results show high statistical significance (p < 0.001)")
        elif significance == StatisticalSignificance.SIGNIFICANT:
            insights.append(f"Results show statistical significance (p < 0.05)")
        elif significance == StatisticalSignificance.TRENDING:
            insights.append(f"Results show trending significance (p < 0.10)")
        else:
            insights.append(f"Results do not show statistical significance")
        
        # Performance insights
        if len(variant_results) >= 2:
            performances = [getattr(p, primary_metric, 0) for p in variant_results.values()]
            best_performance = max(performances)
            worst_performance = min(performances)
            
            if best_performance > 0 and worst_performance > 0:
                improvement = ((best_performance - worst_performance) / worst_performance) * 100
                insights.append(f"Best variant performed {improvement:.1f}% better than worst")
        
        # Test-type specific insights
        if test_type == TestType.TITLE_OPTIMIZATION:
            insights.append("Title variations can significantly impact click-through rates")
        elif test_type == TestType.HASHTAG_OPTIMIZATION:
            insights.append("Hashtag selection affects content discoverability and engagement")
        elif test_type == TestType.POSTING_TIME:
            insights.append("Timing optimization can improve audience reach and engagement")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _generate_test_recommendations(
        self,
        test_data: Dict[str, Any],
        variant_results: Dict[str, PerformanceMetrics],
        winner: Optional[str]
    ) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if winner:
            winner_variant = None
            for variant in test_data["variants"]:
                if variant["id"] == winner:
                    winner_variant = variant
                    break
            
            if winner_variant:
                recommendations.append(f"Implement winning variant: {winner_variant['name']}")
                
                # Specific recommendations based on changes
                if "content_changes" in winner_variant and winner_variant["content_changes"]:
                    changes = winner_variant["content_changes"]
                    if "title" in changes:
                        recommendations.append(f"Use optimized title format for future content")
                    if "hashtags" in changes:
                        recommendations.append(f"Apply winning hashtag strategy to similar content")
        else:
            recommendations.append("No statistically significant winner found")
            recommendations.append("Consider running test longer or with larger sample size")
            recommendations.append("Test more distinct variations to find meaningful differences")
        
        # General recommendations
        recommendations.append("Monitor performance post-implementation to confirm results")
        recommendations.append("Consider testing additional elements to further optimize performance")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _generate_test_variants(
        self,
        test_type: TestType,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform]
    ) -> List[TestVariant]:
        """Generate test variants based on test type"""
        try:
            generator = self.variant_generators.get(test_type)
            if not generator:
                # Create default control variant
                return [TestVariant(
                    id="control",
                    name="Control",
                    description="Original content without modifications",
                    traffic_percentage=100.0
                )]
            
            return await generator(base_content, target_platforms)
        
        except Exception as e:
            logger.error(f"Variant generation failed: {str(e)}")
            return []
    
    async def _generate_title_variants(
        self,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform]
    ) -> List[TestVariant]:
        """Generate title optimization variants"""
        original_title = base_content.title or "Original Title"
        
        variants = [
            TestVariant(
                id="control",
                name="Control",
                description="Original title",
                content_changes={"title": original_title},
                traffic_percentage=50.0,
                hypothesis="Original title serves as control baseline"
            )
        ]
        
        # Generate title variations
        title_strategies = [
            {
                "id": "emotional",
                "name": "Emotional Appeal",
                "description": "Title with emotional trigger words",
                "changes": {"title": f"🔥 {original_title} - You Won't Believe This!"},
                "hypothesis": "Emotional appeal increases click-through rate"
            },
            {
                "id": "urgency",
                "name": "Urgency",
                "description": "Title with urgency indicators",
                "changes": {"title": f"URGENT: {original_title} (Limited Time)"},
                "hypothesis": "Urgency creates FOMO and drives engagement"
            },
            {
                "id": "question",
                "name": "Question Format",
                "description": "Title as a question",
                "changes": {"title": f"Want to Know About {original_title}?"},
                "hypothesis": "Questions engage curiosity and increase clicks"
            }
        ]
        
        for strategy in title_strategies[:1]:  # Use one variant for simplicity
            variant = TestVariant(
                id=strategy["id"],
                name=strategy["name"],
                description=strategy["description"],
                content_changes=strategy["changes"],
                traffic_percentage=50.0,
                hypothesis=strategy["hypothesis"]
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_hashtag_variants(
        self,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform]
    ) -> List[TestVariant]:
        """Generate hashtag optimization variants"""
        original_tags = base_content.tags or []
        
        return [
            TestVariant(
                id="control",
                name="Control Hashtags",
                description="Original hashtag set",
                content_changes={"hashtags": original_tags},
                traffic_percentage=50.0
            ),
            TestVariant(
                id="trending",
                name="Trending Hashtags",
                description="Focus on trending hashtags",
                content_changes={"hashtags": original_tags + ["#viral", "#trending", "#fyp"]},
                traffic_percentage=50.0,
                hypothesis="Trending hashtags increase discoverability"
            )
        ]
    
    async def _generate_timing_variants(
        self,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform]
    ) -> List[TestVariant]:
        """Generate posting time variants"""
        return [
            TestVariant(
                id="morning",
                name="Morning Post",
                description="Post in morning hours (8-10 AM)",
                timing_changes={"hour": 9},
                traffic_percentage=50.0,
                hypothesis="Morning posts capture commute audience"
            ),
            TestVariant(
                id="evening",
                name="Evening Post",
                description="Post in evening hours (6-8 PM)",
                timing_changes={"hour": 19},
                traffic_percentage=50.0,
                hypothesis="Evening posts capture leisure audience"
            )
        ]
    
    async def _generate_format_variants(
        self,
        base_content: ContentPayload,
        target_platforms: List[SocialPlatform]
    ) -> List[TestVariant]:
        """Generate content format variants"""
        return [
            TestVariant(
                id="video",
                name="Video Format",
                description="Video content format",
                content_changes={"format": "video"},
                traffic_percentage=50.0
            ),
            TestVariant(
                id="carousel",
                name="Carousel Format",
                description="Carousel/slideshow format",
                content_changes={"format": "carousel"},
                traffic_percentage=50.0
            )
        ]
    
    # Placeholder methods for other variant types
    async def _generate_thumbnail_variants(self, base_content: ContentPayload, target_platforms: List[SocialPlatform]) -> List[TestVariant]:
        """Generate thumbnail variants"""
        return [TestVariant(id="control", name="Control", description="Original thumbnail", traffic_percentage=100.0)]
    
    async def _generate_description_variants(self, base_content: ContentPayload, target_platforms: List[SocialPlatform]) -> List[TestVariant]:
        """Generate description variants"""
        return [TestVariant(id="control", name="Control", description="Original description", traffic_percentage=100.0)]
    
    async def _generate_cta_variants(self, base_content: ContentPayload, target_platforms: List[SocialPlatform]) -> List[TestVariant]:
        """Generate call-to-action variants"""
        return [TestVariant(id="control", name="Control", description="Original CTA", traffic_percentage=100.0)]
    
    async def _generate_audience_variants(self, base_content: ContentPayload, target_platforms: List[SocialPlatform]) -> List[TestVariant]:
        """Generate audience targeting variants"""
        return [TestVariant(id="control", name="Control", description="Original audience", traffic_percentage=100.0)]
    
    def _calculate_sample_size(
        self,
        primary_metric: str,
        minimum_detectable_effect: float,
        statistical_power: float,
        confidence_level: float
    ) -> int:
        """Calculate required sample size for test"""
        try:
            # Simplified sample size calculation
            # In practice, this would use more sophisticated statistical formulas
            
            alpha = 1 - confidence_level
            beta = 1 - statistical_power
            
            # Z-scores for alpha and beta
            z_alpha = stats.norm.ppf(1 - alpha/2)
            z_beta = stats.norm.ppf(statistical_power)
            
            # Estimate baseline conversion rate based on metric type
            baseline_rates = {
                "click_through_rate": 0.02,
                "conversion_rate": 0.05,
                "engagement_rate": 0.04,
                "revenue": 100.0
            }
            
            baseline = baseline_rates.get(primary_metric, 0.05)
            
            if primary_metric in ["click_through_rate", "conversion_rate", "engagement_rate"]:
                # For proportion metrics
                p1 = baseline
                p2 = baseline * (1 + minimum_detectable_effect)
                
                pooled_p = (p1 + p2) / 2
                
                sample_size = (
                    (z_alpha + z_beta) ** 2 * 2 * pooled_p * (1 - pooled_p)
                ) / ((p2 - p1) ** 2)
            else:
                # For continuous metrics (simplified)
                # Assume coefficient of variation of 1.0
                cv = 1.0
                effect_size = minimum_detectable_effect
                
                sample_size = (
                    2 * (z_alpha + z_beta) ** 2 * (cv ** 2)
                ) / (effect_size ** 2)
            
            # Return per-variant sample size (multiply by 2 for two variants)
            return max(int(sample_size), 100)  # Minimum 100 per variant
        
        except Exception as e:
            logger.error(f"Sample size calculation failed: {str(e)}")
            return 1000  # Default sample size
    
    async def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an A/B test"""
        try:
            if test_id in self.active_tests:
                test_data = self.active_tests[test_id]
                
                # Add current performance summary
                current_performance = {}
                for variant in test_data["variants"]:
                    variant_id = variant["id"]
                    performance_history = self.test_performance_data[test_id][variant_id]
                    
                    if performance_history:
                        latest = performance_history[-1]
                        current_performance[variant_id] = {
                            "impressions": latest.impressions,
                            "clicks": latest.clicks,
                            "engagement_rate": latest.engagement_rate,
                            "sample_size": latest.sample_size
                        }
                
                test_data["current_performance"] = current_performance
                return test_data
            
            elif test_id in self.completed_tests:
                result = self.completed_tests[test_id]
                return asdict(result)
            
            return None
        
        except Exception as e:
            logger.error(f"Test status retrieval failed: {str(e)}")
            return None
    
    async def list_active_tests(self) -> List[Dict[str, Any]]:
        """List all active A/B tests"""
        try:
            active_list = []
            
            for test_id, test_data in self.active_tests.items():
                summary = {
                    "test_id": test_id,
                    "test_name": test_data["test_name"],
                    "test_type": test_data["test_type"].value if isinstance(test_data["test_type"], TestType) else test_data["test_type"],
                    "status": test_data["status"].value if isinstance(test_data["status"], TestStatus) else test_data["status"],
                    "created_at": test_data["created_at"],
                    "started_at": test_data.get("started_at"),
                    "variant_count": len(test_data["variants"]),
                    "platform_count": len(test_data["target_platforms"])
                }
                active_list.append(summary)
            
            return active_list
        
        except Exception as e:
            logger.error(f"Active tests listing failed: {str(e)}")
            return []
    
    async def get_testing_statistics(self) -> Dict[str, Any]:
        """Get A/B testing engine statistics"""
        try:
            total_active = len(self.active_tests)
            total_completed = len(self.completed_tests)
            
            # Test type distribution
            test_type_distribution = defaultdict(int)
            for test_data in self.active_tests.values():
                test_type = test_data["test_type"]
                test_type_distribution[test_type.value if isinstance(test_type, TestType) else test_type] += 1
            
            for result in self.completed_tests.values():
                test_type_distribution[result.test_type.value] += 1
            
            # Success rate (tests with significant results)
            significant_tests = sum(
                1 for result in self.completed_tests.values()
                if result.statistical_significance in [StatisticalSignificance.SIGNIFICANT, StatisticalSignificance.HIGHLY_SIGNIFICANT]
            )
            
            success_rate = (significant_tests / total_completed) if total_completed > 0 else 0
            
            # Average test duration for completed tests
            completed_durations = [
                result.test_duration_hours for result in self.completed_tests.values()
                if result.test_duration_hours > 0
            ]
            avg_duration = safe_mean(completed_durations) if completed_durations else 0
            
            return {
                "total_active_tests": total_active,
                "total_completed_tests": total_completed,
                "success_rate": success_rate,
                "average_test_duration_hours": avg_duration,
                "test_type_distribution": dict(test_type_distribution),
                "significant_tests": significant_tests,
                "total_performance_records": sum(
                    len(variant_data) 
                    for test_data in self.test_performance_data.values() 
                    for variant_data in test_data.values()
                )
            }
        
        except Exception as e:
            logger.error(f"Statistics generation failed: {str(e)}")
            return {}
    
    def clear_test_data(self, test_id -> None: str) -> None:
        """Clear test data and performance history"""
        try:
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            
            if test_id in self.completed_tests:
                del self.completed_tests[test_id]
            
            if test_id in self.test_performance_data:
                del self.test_performance_data[test_id]
            
            logger.info(f"Cleared test data for {test_id}")
        
        except Exception as e:
            logger.error(f"Test data clearing failed: {str(e)}")