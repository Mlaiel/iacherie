"""
Cohort Analyzer
Advanced cohort analysis for ML experiments

This module provides:
- User cohort creation and analysis
- Cohort-based A/B testing
- Retention and conversion analysis
- Behavioral segmentation
- Temporal cohort analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CohortType(Enum):
    ACQUISITION = "acquisition"
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"

@dataclass
class CohortDefinition:
    """Definition of a user cohort"""
    name: str
    type: CohortType
    criteria: Dict[str, Any]
    date_range: Tuple[datetime, datetime]
    size_estimate: Optional[int] = None

@dataclass
class CohortAnalysisResult:
    """Results from cohort analysis"""
    cohort_name: str
    control_metrics: Dict[str, float]
    treatment_metrics: Dict[str, float]
    statistical_significance: Dict[str, Any]
    business_impact: Dict[str, Any]
    recommendations: List[str]

class CohortAnalyzer:
    """
    Advanced cohort analysis for experimentation
    Enables granular analysis of user segments
    """
    
    def __init__(self):
        self.defined_cohorts: Dict[str, CohortDefinition] = {}
        self.analysis_cache: Dict[str, Any] = {}
        
    async def define_cohort(
        self,
        name: str,
        cohort_type: CohortType,
        criteria: Dict[str, Any],
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> CohortDefinition:
        """
        Define a new user cohort for analysis
        
        Args:
            name: Cohort identifier
            cohort_type: Type of cohort
            criteria: Criteria for cohort membership
            date_range: Date range for cohort selection
            
        Returns:
            cohort_definition: Defined cohort
        """
        try:
            if date_range is None:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            # Estimate cohort size
            size_estimate = await self._estimate_cohort_size(criteria, date_range)
            
            cohort_definition = CohortDefinition(
                name=name,
                type=cohort_type,
                criteria=criteria,
                date_range=date_range,
                size_estimate=size_estimate
            )
            
            self.defined_cohorts[name] = cohort_definition
            
            logger.info(f"Defined cohort '{name}' with estimated size {size_estimate}")
            return cohort_definition
            
        except Exception as e:
            logger.error(f"Failed to define cohort: {e}")
            raise
    
    async def create_acquisition_cohort(
        self,
        name: str,
        signup_date_range: Tuple[datetime, datetime],
        channel: Optional[str] = None,
        additional_criteria: Optional[Dict[str, Any]] = None
    ) -> CohortDefinition:
        """
        Create acquisition-based cohort
        
        Args:
            name: Cohort name
            signup_date_range: Date range for user signups
            channel: Acquisition channel filter
            additional_criteria: Additional filtering criteria
            
        Returns:
            cohort_definition: Acquisition cohort
        """
        try:
            criteria = {
                "signup_date": {
                    "start": signup_date_range[0],
                    "end": signup_date_range[1]
                }
            }
            
            if channel:
                criteria["acquisition_channel"] = channel
                
            if additional_criteria:
                criteria.update(additional_criteria)
            
            return await self.define_cohort(
                name=name,
                cohort_type=CohortType.ACQUISITION,
                criteria=criteria,
                date_range=signup_date_range
            )
            
        except Exception as e:
            logger.error(f"Failed to create acquisition cohort: {e}")
            raise
    
    async def create_behavioral_cohort(
        self,
        name: str,
        behaviors: List[str],
        frequency_threshold: int,
        time_window_days: int = 30
    ) -> CohortDefinition:
        """
        Create behavior-based cohort
        
        Args:
            name: Cohort name
            behaviors: List of behaviors to track
            frequency_threshold: Minimum frequency of behaviors
            time_window_days: Time window for behavior analysis
            
        Returns:
            cohort_definition: Behavioral cohort
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_window_days)
            
            criteria = {
                "behaviors": behaviors,
                "frequency_threshold": frequency_threshold,
                "time_window": {
                    "start": start_date,
                    "end": end_date,
                    "days": time_window_days
                }
            }
            
            return await self.define_cohort(
                name=name,
                cohort_type=CohortType.BEHAVIORAL,
                criteria=criteria,
                date_range=(start_date, end_date)
            )
            
        except Exception as e:
            logger.error(f"Failed to create behavioral cohort: {e}")
            raise
    
    async def create_engagement_cohort(
        self,
        name: str,
        engagement_metrics: Dict[str, Any],
        percentile_threshold: float = 0.8
    ) -> CohortDefinition:
        """
        Create engagement-based cohort (high/low engagement users)
        
        Args:
            name: Cohort name
            engagement_metrics: Metrics to measure engagement
            percentile_threshold: Percentile threshold for high engagement
            
        Returns:
            cohort_definition: Engagement cohort
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            criteria = {
                "engagement_metrics": engagement_metrics,
                "percentile_threshold": percentile_threshold,
                "measurement_period": {
                    "start": start_date,
                    "end": end_date
                }
            }
            
            return await self.define_cohort(
                name=name,
                cohort_type=CohortType.ENGAGEMENT,
                criteria=criteria,
                date_range=(start_date, end_date)
            )
            
        except Exception as e:
            logger.error(f"Failed to create engagement cohort: {e}")
            raise
    
    async def analyze_cohort_experiment(
        self,
        cohort_name: str,
        experiment_id: str,
        metrics_to_analyze: List[str]
    ) -> CohortAnalysisResult:
        """
        Analyze experiment results for specific cohort
        
        Args:
            cohort_name: Cohort to analyze
            experiment_id: Experiment identifier
            metrics_to_analyze: Metrics to compare
            
        Returns:
            analysis_result: Cohort-specific analysis results
        """
        try:
            if cohort_name not in self.defined_cohorts:
                raise ValueError(f"Cohort '{cohort_name}' not found")
            
            cohort = self.defined_cohorts[cohort_name]
            
            # Get cohort members
            cohort_users = await self._get_cohort_members(cohort)
            
            # Get experiment data for cohort
            control_data = await self._get_cohort_experiment_data(
                cohort_users, experiment_id, "control"
            )
            treatment_data = await self._get_cohort_experiment_data(
                cohort_users, experiment_id, "treatment"
            )
            
            # Calculate metrics
            control_metrics = await self._calculate_cohort_metrics(
                control_data, metrics_to_analyze
            )
            treatment_metrics = await self._calculate_cohort_metrics(
                treatment_data, metrics_to_analyze
            )
            
            # Statistical significance testing
            statistical_significance = await self._test_cohort_significance(
                control_metrics, treatment_metrics
            )
            
            # Business impact analysis
            business_impact = await self._analyze_cohort_business_impact(
                cohort, control_metrics, treatment_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_cohort_recommendations(
                cohort, statistical_significance, business_impact
            )
            
            analysis_result = CohortAnalysisResult(
                cohort_name=cohort_name,
                control_metrics=control_metrics,
                treatment_metrics=treatment_metrics,
                statistical_significance=statistical_significance,
                business_impact=business_impact,
                recommendations=recommendations
            )
            
            logger.info(f"Completed cohort analysis for '{cohort_name}' in experiment {experiment_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze cohort experiment: {e}")
            raise
    
    async def compare_cohorts(
        self,
        cohort_names: List[str],
        experiment_id: str,
        primary_metric: str
    ) -> Dict[str, Any]:
        """
        Compare multiple cohorts within the same experiment
        
        Args:
            cohort_names: List of cohorts to compare
            experiment_id: Experiment identifier
            primary_metric: Primary metric for comparison
            
        Returns:
            comparison_results: Multi-cohort comparison analysis
        """
        try:
            cohort_results = {}
            
            # Analyze each cohort
            for cohort_name in cohort_names:
                if cohort_name not in self.defined_cohorts:
                    logger.warning(f"Cohort '{cohort_name}' not found, skipping")
                    continue
                
                result = await self.analyze_cohort_experiment(
                    cohort_name, experiment_id, [primary_metric]
                )
                cohort_results[cohort_name] = result
            
            # Cross-cohort analysis
            comparison_analysis = await self._perform_cross_cohort_analysis(
                cohort_results, primary_metric
            )
            
            # Identify winning cohorts
            winning_cohorts = await self._identify_winning_cohorts(
                cohort_results, primary_metric
            )
            
            # Generate insights
            insights = await self._generate_cross_cohort_insights(
                cohort_results, comparison_analysis, winning_cohorts
            )
            
            return {
                "experiment_id": experiment_id,
                "cohort_results": cohort_results,
                "comparison_analysis": comparison_analysis,
                "winning_cohorts": winning_cohorts,
                "insights": insights,
                "primary_metric": primary_metric
            }
            
        except Exception as e:
            logger.error(f"Failed to compare cohorts: {e}")
            raise
    
    async def temporal_cohort_analysis(
        self,
        base_cohort_name: str,
        time_periods: List[Tuple[datetime, datetime]],
        experiment_id: str,
        metric: str
    ) -> Dict[str, Any]:
        """
        Analyze cohort performance across different time periods
        
        Args:
            base_cohort_name: Base cohort definition
            time_periods: List of time periods to analyze
            experiment_id: Experiment identifier
            metric: Metric to track over time
            
        Returns:
            temporal_analysis: Time-based cohort analysis
        """
        try:
            if base_cohort_name not in self.defined_cohorts:
                raise ValueError(f"Base cohort '{base_cohort_name}' not found")
            
            base_cohort = self.defined_cohorts[base_cohort_name]
            temporal_results = {}
            
            # Analyze each time period
            for i, (start_date, end_date) in enumerate(time_periods):
                period_name = f"{base_cohort_name}_period_{i+1}"
                
                # Create temporal cohort
                temporal_criteria = base_cohort.criteria.copy()
                temporal_criteria["temporal_filter"] = {
                    "start": start_date,
                    "end": end_date
                }
                
                temporal_cohort = CohortDefinition(
                    name=period_name,
                    type=base_cohort.type,
                    criteria=temporal_criteria,
                    date_range=(start_date, end_date)
                )
                
                # Analyze temporal cohort
                period_result = await self.analyze_cohort_experiment(
                    period_name, experiment_id, [metric]
                )
                
                temporal_results[period_name] = {
                    "period": (start_date, end_date),
                    "result": period_result
                }
            
            # Trend analysis
            trend_analysis = await self._analyze_temporal_trends(
                temporal_results, metric
            )
            
            return {
                "base_cohort": base_cohort_name,
                "time_periods": time_periods,
                "temporal_results": temporal_results,
                "trend_analysis": trend_analysis,
                "metric": metric
            }
            
        except Exception as e:
            logger.error(f"Failed to perform temporal cohort analysis: {e}")
            raise
    
    async def _estimate_cohort_size(
        self,
        criteria: Dict[str, Any],
        date_range: Tuple[datetime, datetime]
    ) -> int:
        """Estimate the size of a cohort based on criteria"""
        # Placeholder implementation
        # In practice, this would query the actual data source
        base_size = 10000  # Default estimate
        
        # Apply filters to estimate size reduction
        if "acquisition_channel" in criteria:
            base_size = int(base_size * 0.3)  # Channel-specific reduction
            
        if "behaviors" in criteria:
            base_size = int(base_size * 0.2)  # Behavioral filter reduction
            
        if "engagement_metrics" in criteria:
            threshold = criteria.get("percentile_threshold", 0.8)
            base_size = int(base_size * (1 - threshold))
        
        return max(100, base_size)  # Minimum cohort size
    
    async def _get_cohort_members(self, cohort: CohortDefinition) -> List[str]:
        """Get list of user IDs in the cohort"""
        # Placeholder implementation
        # In practice, this would query the user database
        estimated_size = cohort.size_estimate or 1000
        return [f"user_{i}" for i in range(estimated_size)]
    
    async def _get_cohort_experiment_data(
        self,
        cohort_users: List[str],
        experiment_id: str,
        variant: str
    ) -> Dict[str, Any]:
        """Get experiment data for cohort users in specific variant"""
        # Placeholder implementation
        # In practice, this would query the experiment tracking system
        return {
            "users": cohort_users,
            "variant": variant,
            "experiment_id": experiment_id,
            "metrics": {}  # Would contain actual metric data
        }
    
    async def _calculate_cohort_metrics(
        self,
        cohort_data: Dict[str, Any],
        metrics: List[str]
    ) -> Dict[str, float]:
        """Calculate metrics for cohort"""
        # Placeholder implementation
        calculated_metrics = {}
        
        for metric in metrics:
            # Simulate metric calculation
            if metric == "conversion_rate":
                calculated_metrics[metric] = np.random.beta(2, 8)  # ~0.2 average
            elif metric == "revenue_per_user":
                calculated_metrics[metric] = np.random.gamma(2, 10)  # ~$20 average
            elif metric == "retention_rate":
                calculated_metrics[metric] = np.random.beta(3, 2)  # ~0.6 average
            else:
                calculated_metrics[metric] = np.random.normal(0.5, 0.1)
        
        return calculated_metrics
    
    async def _test_cohort_significance(
        self,
        control_metrics: Dict[str, float],
        treatment_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Test statistical significance for cohort comparison"""
        # Simplified significance testing
        results = {}
        
        for metric in control_metrics:
            if metric in treatment_metrics:
                control_val = control_metrics[metric]
                treatment_val = treatment_metrics[metric]
                
                # Simulate significance test
                diff = treatment_val - control_val
                p_value = np.random.uniform(0.01, 0.1)  # Simulate p-value
                
                results[metric] = {
                    "difference": diff,
                    "relative_change": diff / control_val if control_val != 0 else 0,
                    "p_value": p_value,
                    "is_significant": p_value < 0.05
                }
        
        return results
    
    async def _analyze_cohort_business_impact(
        self,
        cohort: CohortDefinition,
        control_metrics: Dict[str, float],
        treatment_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze business impact for cohort"""
        impact_analysis = {
            "cohort_type": cohort.type.value,
            "estimated_size": cohort.size_estimate,
            "revenue_impact": 0,
            "engagement_impact": 0
        }
        
        # Calculate revenue impact
        if "revenue_per_user" in control_metrics and "revenue_per_user" in treatment_metrics:
            revenue_diff = treatment_metrics["revenue_per_user"] - control_metrics["revenue_per_user"]
            impact_analysis["revenue_impact"] = revenue_diff * (cohort.size_estimate or 1000)
        
        # Calculate engagement impact
        if "engagement_score" in control_metrics and "engagement_score" in treatment_metrics:
            engagement_diff = treatment_metrics["engagement_score"] - control_metrics["engagement_score"]
            impact_analysis["engagement_impact"] = engagement_diff
        
        return impact_analysis
    
    async def _generate_cohort_recommendations(
        self,
        cohort: CohortDefinition,
        significance: Dict[str, Any],
        business_impact: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations for cohort"""
        recommendations = []
        
        # Check for significant positive results
        significant_improvements = [
            metric for metric, result in significance.items()
            if result.get("is_significant", False) and result.get("difference", 0) > 0
        ]
        
        if significant_improvements:
            recommendations.append(
                f"Deploy treatment to {cohort.name} cohort - significant improvements in {', '.join(significant_improvements)}"
            )
        
        # Check business impact
        if business_impact.get("revenue_impact", 0) > 1000:  # $1000+ impact
            recommendations.append(
                f"High revenue impact potential: ${business_impact['revenue_impact']:.2f} for cohort"
            )
        
        # Cohort-specific recommendations
        if cohort.type == CohortType.ACQUISITION:
            recommendations.append("Consider expanding to similar acquisition channels")
        elif cohort.type == CohortType.BEHAVIORAL:
            recommendations.append("Investigate behavioral patterns for broader application")
        
        if not recommendations:
            recommendations.append("Continue monitoring - no clear advantage detected")
        
        return recommendations
    
    async def _perform_cross_cohort_analysis(
        self,
        cohort_results: Dict[str, CohortAnalysisResult],
        primary_metric: str
    ) -> Dict[str, Any]:
        """Perform analysis across multiple cohorts"""
        analysis = {
            "metric_comparison": {},
            "variance_analysis": {},
            "effect_size_comparison": {}
        }
        
        # Compare primary metric across cohorts
        cohort_values = {}
        for cohort_name, result in cohort_results.items():
            control_val = result.control_metrics.get(primary_metric, 0)
            treatment_val = result.treatment_metrics.get(primary_metric, 0)
            improvement = treatment_val - control_val
            
            cohort_values[cohort_name] = {
                "control": control_val,
                "treatment": treatment_val,
                "improvement": improvement,
                "relative_improvement": improvement / control_val if control_val != 0 else 0
            }
        
        analysis["metric_comparison"] = cohort_values
        
        # Analyze variance across cohorts
        improvements = [data["improvement"] for data in cohort_values.values()]
        analysis["variance_analysis"] = {
            "mean_improvement": np.mean(improvements),
            "std_improvement": np.std(improvements),
            "min_improvement": np.min(improvements),
            "max_improvement": np.max(improvements)
        }
        
        return analysis
    
    async def _identify_winning_cohorts(
        self,
        cohort_results: Dict[str, CohortAnalysisResult],
        primary_metric: str
    ) -> List[str]:
        """Identify cohorts with best performance"""
        cohort_performance = []
        
        for cohort_name, result in cohort_results.items():
            control_val = result.control_metrics.get(primary_metric, 0)
            treatment_val = result.treatment_metrics.get(primary_metric, 0)
            
            # Check if significant and positive
            significance = result.statistical_significance.get(primary_metric, {})
            is_significant = significance.get("is_significant", False)
            improvement = treatment_val - control_val
            
            if is_significant and improvement > 0:
                cohort_performance.append((cohort_name, improvement))
        
        # Sort by improvement and return top performers
        cohort_performance.sort(key=lambda x: x[1], reverse=True)
        return [cohort for cohort, _ in cohort_performance[:3]]  # Top 3
    
    async def _generate_cross_cohort_insights(
        self,
        cohort_results: Dict[str, CohortAnalysisResult],
        comparison_analysis: Dict[str, Any],
        winning_cohorts: List[str]
    ) -> List[str]:
        """Generate insights from cross-cohort analysis"""
        insights = []
        
        if winning_cohorts:
            insights.append(f"Top performing cohorts: {', '.join(winning_cohorts)}")
        
        variance = comparison_analysis["variance_analysis"]
        if variance["std_improvement"] > variance["mean_improvement"] * 0.5:
            insights.append("High variance in cohort performance - consider targeted strategies")
        
        if variance["mean_improvement"] > 0:
            insights.append(f"Average improvement across cohorts: {variance['mean_improvement']:.3f}")
        
        return insights
    
    async def _analyze_temporal_trends(
        self,
        temporal_results: Dict[str, Any],
        metric: str
    ) -> Dict[str, Any]:
        """Analyze trends across time periods"""
        improvements = []
        periods = []
        
        for period_name, data in temporal_results.items():
            result = data["result"]
            control_val = result.control_metrics.get(metric, 0)
            treatment_val = result.treatment_metrics.get(metric, 0)
            improvement = treatment_val - control_val
            
            improvements.append(improvement)
            periods.append(data["period"])
        
        # Calculate trend
        x = np.arange(len(improvements))
        if len(improvements) > 1:
            slope = np.polyfit(x, improvements, 1)[0]
            trend = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        else:
            slope = 0
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "slope": slope,
            "improvements": improvements,
            "periods": periods,
            "average_improvement": np.mean(improvements),
            "improvement_variance": np.var(improvements)
        }