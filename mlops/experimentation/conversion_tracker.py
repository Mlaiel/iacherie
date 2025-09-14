"""
Conversion Tracker
Advanced conversion tracking and funnel analysis for ML experiments

This module provides:
- Multi-step conversion funnel tracking
- Attribution modeling for conversions
- Real-time conversion monitoring
- A/B test impact on conversion rates
- Conversion optimization recommendations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class ConversionType(Enum):
    SIGNUP = "signup"
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    CONTENT_CREATION = "content_creation"
    SOCIAL_SHARE = "social_share"
    PREMIUM_UPGRADE = "premium_upgrade"
    REFERRAL = "referral"

class AttributionModel(Enum):
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"

@dataclass
class ConversionEvent:
    """Individual conversion event"""
    user_id: str
    event_type: ConversionType
    timestamp: datetime
    value: Optional[float] = None
    experiment_variant: Optional[str] = None
    attribution_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionFunnel:
    """Multi-step conversion funnel definition"""
    name: str
    steps: List[ConversionType]
    time_window_hours: int = 24
    required_sequence: bool = True

@dataclass
class ConversionAnalysis:
    """Results from conversion analysis"""
    funnel_name: str
    control_rates: Dict[str, float]
    treatment_rates: Dict[str, float]
    statistical_significance: Dict[str, Any]
    attribution_analysis: Dict[str, Any]
    optimization_recommendations: List[str]

class ConversionTracker:
    """
    Advanced conversion tracking and analysis system
    Provides comprehensive funnel and attribution analysis
    """
    
    def __init__(self):
        self.conversion_events: List[ConversionEvent] = []
        self.defined_funnels: Dict[str, ConversionFunnel] = {}
        self.tracking_active = False
        
    async def start_tracking(self) -> None:
        """Start conversion event tracking"""
        try:
            self.tracking_active = True
            logger.info("Conversion tracking started")
            
            # Start background tracking task
            asyncio.create_task(self._background_tracking())
            
        except Exception as e:
            logger.error(f"Failed to start tracking: {e}")
            raise
    
    async def stop_tracking(self) -> None:
        """Stop conversion event tracking"""
        try:
            self.tracking_active = False
            logger.info("Conversion tracking stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop tracking: {e}")
            raise
    
    async def track_conversion(
        self,
        user_id: str,
        event_type: ConversionType,
        value: Optional[float] = None,
        experiment_variant: Optional[str] = None,
        attribution_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track a conversion event
        
        Args:
            user_id: User identifier
            event_type: Type of conversion
            value: Monetary value of conversion
            experiment_variant: A/B test variant
            attribution_data: Attribution information
            metadata: Additional event metadata
        """
        try:
            conversion_event = ConversionEvent(
                user_id=user_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                value=value,
                experiment_variant=experiment_variant,
                attribution_data=attribution_data or {},
                metadata=metadata or {}
            )
            
            self.conversion_events.append(conversion_event)
            
            # Real-time processing
            await self._process_conversion_event(conversion_event)
            
            logger.debug(f"Tracked conversion: {event_type.value} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
            raise
    
    async def define_funnel(
        self,
        name: str,
        steps: List[ConversionType],
        time_window_hours: int = 24,
        required_sequence: bool = True
    ) -> ConversionFunnel:
        """
        Define a conversion funnel for tracking
        
        Args:
            name: Funnel identifier
            steps: Ordered list of conversion steps
            time_window_hours: Time window for funnel completion
            required_sequence: Whether steps must occur in order
            
        Returns:
            conversion_funnel: Defined funnel
        """
        try:
            funnel = ConversionFunnel(
                name=name,
                steps=steps,
                time_window_hours=time_window_hours,
                required_sequence=required_sequence
            )
            
            self.defined_funnels[name] = funnel
            
            logger.info(f"Defined conversion funnel '{name}' with {len(steps)} steps")
            return funnel
            
        except Exception as e:
            logger.error(f"Failed to define funnel: {e}")
            raise
    
    async def analyze_funnel_experiment(
        self,
        funnel_name: str,
        experiment_id: str,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> ConversionAnalysis:
        """
        Analyze funnel performance in A/B experiment
        
        Args:
            funnel_name: Funnel to analyze
            experiment_id: Experiment identifier
            date_range: Date range for analysis
            
        Returns:
            conversion_analysis: Funnel analysis results
        """
        try:
            if funnel_name not in self.defined_funnels:
                raise ValueError(f"Funnel '{funnel_name}' not found")
            
            funnel = self.defined_funnels[funnel_name]
            
            # Filter events for analysis
            filtered_events = await self._filter_events_for_analysis(
                experiment_id, date_range
            )
            
            # Separate control and treatment events
            control_events = [e for e in filtered_events if e.experiment_variant == "control"]
            treatment_events = [e for e in filtered_events if e.experiment_variant == "treatment"]
            
            # Calculate funnel rates
            control_rates = await self._calculate_funnel_rates(control_events, funnel)
            treatment_rates = await self._calculate_funnel_rates(treatment_events, funnel)
            
            # Statistical significance testing
            statistical_significance = await self._test_funnel_significance(
                control_rates, treatment_rates, control_events, treatment_events
            )
            
            # Attribution analysis
            attribution_analysis = await self._analyze_attribution(
                control_events + treatment_events, funnel
            )
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_funnel_recommendations(
                funnel, control_rates, treatment_rates, statistical_significance
            )
            
            analysis = ConversionAnalysis(
                funnel_name=funnel_name,
                control_rates=control_rates,
                treatment_rates=treatment_rates,
                statistical_significance=statistical_significance,
                attribution_analysis=attribution_analysis,
                optimization_recommendations=optimization_recommendations
            )
            
            logger.info(f"Completed funnel analysis for '{funnel_name}' in experiment {experiment_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze funnel experiment: {e}")
            raise
    
    async def calculate_conversion_attribution(
        self,
        user_id: str,
        conversion_event: ConversionEvent,
        attribution_model: AttributionModel = AttributionModel.LAST_TOUCH,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate attribution for a conversion event
        
        Args:
            user_id: User identifier
            conversion_event: Conversion to attribute
            attribution_model: Attribution model to use
            lookback_days: Lookback window for attribution
            
        Returns:
            attribution_result: Attribution analysis
        """
        try:
            # Get user's touchpoint history
            lookback_start = conversion_event.timestamp - timedelta(days=lookback_days)
            user_touchpoints = await self._get_user_touchpoints(
                user_id, lookback_start, conversion_event.timestamp
            )
            
            if not user_touchpoints:
                return {
                    "attributed_touchpoints": [],
                    "attribution_weights": {},
                    "model_used": attribution_model.value
                }
            
            # Apply attribution model
            attribution_weights = await self._apply_attribution_model(
                user_touchpoints, attribution_model
            )
            
            # Calculate attributed value
            attributed_value = {}
            conversion_value = conversion_event.value or 0
            
            for touchpoint, weight in attribution_weights.items():
                attributed_value[touchpoint] = conversion_value * weight
            
            return {
                "attributed_touchpoints": list(attribution_weights.keys()),
                "attribution_weights": attribution_weights,
                "attributed_values": attributed_value,
                "total_value": conversion_value,
                "model_used": attribution_model.value,
                "touchpoint_count": len(user_touchpoints)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate attribution: {e}")
            raise
    
    async def get_real_time_conversion_metrics(
        self,
        experiment_id: str,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get real-time conversion metrics for experiment
        
        Args:
            experiment_id: Experiment identifier
            time_window_minutes: Time window for metrics
            
        Returns:
            real_time_metrics: Current conversion performance
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            # Filter recent events
            recent_events = [
                e for e in self.conversion_events
                if e.timestamp >= cutoff_time and 
                   e.metadata.get("experiment_id") == experiment_id
            ]
            
            # Group by variant
            control_events = [e for e in recent_events if e.experiment_variant == "control"]
            treatment_events = [e for e in recent_events if e.experiment_variant == "treatment"]
            
            # Calculate metrics
            metrics = {
                "time_window_minutes": time_window_minutes,
                "total_conversions": len(recent_events),
                "control_conversions": len(control_events),
                "treatment_conversions": len(treatment_events),
                "control_conversion_rate": await self._calculate_instant_rate(control_events),
                "treatment_conversion_rate": await self._calculate_instant_rate(treatment_events),
                "conversion_types": await self._get_conversion_type_breakdown(recent_events),
                "total_value": sum(e.value or 0 for e in recent_events),
                "average_conversion_value": np.mean([e.value for e in recent_events if e.value]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Calculate lift
            if metrics["control_conversion_rate"] > 0:
                metrics["conversion_lift"] = (
                    (metrics["treatment_conversion_rate"] - metrics["control_conversion_rate"]) /
                    metrics["control_conversion_rate"]
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get real-time metrics: {e}")
            raise
    
    async def optimize_conversion_funnel(
        self,
        funnel_name: str,
        analysis_results: ConversionAnalysis
    ) -> Dict[str, Any]:
        """
        Generate optimization recommendations for conversion funnel
        
        Args:
            funnel_name: Funnel to optimize
            analysis_results: Previous analysis results
            
        Returns:
            optimization_plan: Detailed optimization recommendations
        """
        try:
            funnel = self.defined_funnels[funnel_name]
            optimization_plan = {
                "funnel_name": funnel_name,
                "current_performance": analysis_results.control_rates,
                "target_performance": analysis_results.treatment_rates,
                "optimization_opportunities": [],
                "recommended_actions": [],
                "estimated_impact": {}
            }
            
            # Identify bottleneck steps
            bottlenecks = await self._identify_funnel_bottlenecks(
                funnel, analysis_results.control_rates
            )
            
            # Generate step-specific recommendations
            for step_idx, step in enumerate(funnel.steps):
                step_name = step.value
                control_rate = analysis_results.control_rates.get(step_name, 0)
                treatment_rate = analysis_results.treatment_rates.get(step_name, 0)
                
                if treatment_rate > control_rate:
                    improvement = treatment_rate - control_rate
                    optimization_plan["optimization_opportunities"].append({
                        "step": step_name,
                        "current_rate": control_rate,
                        "potential_rate": treatment_rate,
                        "improvement": improvement,
                        "is_bottleneck": step_name in bottlenecks
                    })
            
            # Generate actionable recommendations
            recommendations = await self._generate_actionable_recommendations(
                funnel, analysis_results, bottlenecks
            )
            optimization_plan["recommended_actions"] = recommendations
            
            # Estimate overall impact
            estimated_impact = await self._estimate_optimization_impact(
                funnel, analysis_results, optimization_plan["optimization_opportunities"]
            )
            optimization_plan["estimated_impact"] = estimated_impact
            
            return optimization_plan
            
        except Exception as e:
            logger.error(f"Failed to optimize funnel: {e}")
            raise
    
    async def _background_tracking(self) -> None:
        """Background task for real-time tracking processing"""
        while self.tracking_active:
            try:
                # Process any pending events
                await self._process_pending_events()
                
                # Clean up old events
                await self._cleanup_old_events()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                logger.error(f"Error in background tracking: {e}")
                await asyncio.sleep(60)
    
    async def _process_conversion_event(self, event: ConversionEvent) -> None:
        """Process individual conversion event"""
        try:
            # Update real-time metrics
            await self._update_real_time_metrics(event)
            
            # Check for funnel completions
            await self._check_funnel_completions(event)
            
            # Trigger alerts if needed
            await self._check_conversion_alerts(event)
            
        except Exception as e:
            logger.error(f"Failed to process conversion event: {e}")
    
    async def _filter_events_for_analysis(
        self,
        experiment_id: str,
        date_range: Optional[Tuple[datetime, datetime]]
    ) -> List[ConversionEvent]:
        """Filter conversion events for analysis"""
        filtered_events = []
        
        for event in self.conversion_events:
            # Check experiment
            if event.metadata.get("experiment_id") != experiment_id:
                continue
            
            # Check date range
            if date_range:
                start_date, end_date = date_range
                if not (start_date <= event.timestamp <= end_date):
                    continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    async def _calculate_funnel_rates(
        self,
        events: List[ConversionEvent],
        funnel: ConversionFunnel
    ) -> Dict[str, float]:
        """Calculate conversion rates for each funnel step"""
        rates = {}
        
        # Group events by user
        user_events = {}
        for event in events:
            if event.user_id not in user_events:
                user_events[event.user_id] = []
            user_events[event.user_id].append(event)
        
        # Calculate rates for each step
        total_users = len(user_events)
        if total_users == 0:
            return {step.value: 0.0 for step in funnel.steps}
        
        for step_idx, step in enumerate(funnel.steps):
            users_completed_step = 0
            
            for user_id, user_event_list in user_events.items():
                if await self._user_completed_step(user_event_list, step, funnel):
                    users_completed_step += 1
            
            rates[step.value] = users_completed_step / total_users
        
        return rates
    
    async def _user_completed_step(
        self,
        user_events: List[ConversionEvent],
        step: ConversionType,
        funnel: ConversionFunnel
    ) -> bool:
        """Check if user completed specific funnel step"""
        step_events = [e for e in user_events if e.event_type == step]
        return len(step_events) > 0
    
    async def _test_funnel_significance(
        self,
        control_rates: Dict[str, float],
        treatment_rates: Dict[str, float],
        control_events: List[ConversionEvent],
        treatment_events: List[ConversionEvent]
    ) -> Dict[str, Any]:
        """Test statistical significance of funnel improvements"""
        significance_results = {}
        
        control_users = len(set(e.user_id for e in control_events))
        treatment_users = len(set(e.user_id for e in treatment_events))
        
        for step in control_rates:
            if step in treatment_rates:
                control_rate = control_rates[step]
                treatment_rate = treatment_rates[step]
                
                # Simplified significance test
                control_successes = int(control_rate * control_users)
                treatment_successes = int(treatment_rate * treatment_users)
                
                # Z-test for proportions
                if control_users > 0 and treatment_users > 0:
                    pooled_rate = (control_successes + treatment_successes) / (control_users + treatment_users)
                    se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_users + 1/treatment_users))
                    
                    if se > 0:
                        z_score = (treatment_rate - control_rate) / se
                        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
                    else:
                        z_score = 0
                        p_value = 1.0
                else:
                    z_score = 0
                    p_value = 1.0
                
                significance_results[step] = {
                    "control_rate": control_rate,
                    "treatment_rate": treatment_rate,
                    "difference": treatment_rate - control_rate,
                    "relative_change": (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0,
                    "z_score": z_score,
                    "p_value": p_value,
                    "is_significant": p_value < 0.05,
                    "control_sample_size": control_users,
                    "treatment_sample_size": treatment_users
                }
        
        return significance_results
    
    async def _analyze_attribution(
        self,
        events: List[ConversionEvent],
        funnel: ConversionFunnel
    ) -> Dict[str, Any]:
        """Analyze attribution patterns in funnel"""
        attribution_analysis = {
            "touchpoint_analysis": {},
            "common_paths": [],
            "drop_off_points": {}
        }
        
        # Analyze touchpoint effectiveness
        for step in funnel.steps:
            step_events = [e for e in events if e.event_type == step]
            if step_events:
                attribution_analysis["touchpoint_analysis"][step.value] = {
                    "event_count": len(step_events),
                    "unique_users": len(set(e.user_id for e in step_events)),
                    "total_value": sum(e.value or 0 for e in step_events),
                    "average_time_to_conversion": await self._calculate_average_time_to_conversion(step_events)
                }
        
        return attribution_analysis
    
    async def _generate_funnel_recommendations(
        self,
        funnel: ConversionFunnel,
        control_rates: Dict[str, float],
        treatment_rates: Dict[str, float],
        significance: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable funnel optimization recommendations"""
        recommendations = []
        
        # Identify significant improvements
        significant_improvements = [
            step for step, results in significance.items()
            if results.get("is_significant", False) and results.get("difference", 0) > 0
        ]
        
        if significant_improvements:
            recommendations.append(
                f"Deploy treatment variant - significant improvements in: {', '.join(significant_improvements)}"
            )
        
        # Identify bottlenecks
        lowest_rate_step = min(control_rates, key=control_rates.get)
        if control_rates[lowest_rate_step] < 0.3:  # 30% threshold
            recommendations.append(
                f"Focus optimization efforts on '{lowest_rate_step}' step - lowest conversion rate ({control_rates[lowest_rate_step]:.2%})"
            )
        
        # Check for large improvements
        large_improvements = [
            step for step, results in significance.items()
            if results.get("relative_change", 0) > 0.2  # 20% improvement
        ]
        
        if large_improvements:
            recommendations.append(
                f"Prioritize rollout for steps with large improvements: {', '.join(large_improvements)}"
            )
        
        return recommendations
    
    async def _calculate_instant_rate(self, events: List[ConversionEvent]) -> float:
        """Calculate instantaneous conversion rate"""
        if not events:
            return 0.0
        
        # For real-time metrics, we calculate based on unique users who converted
        unique_users = len(set(e.user_id for e in events))
        
        # This is a simplified calculation - in practice you'd need total users exposed
        return unique_users / max(100, unique_users)  # Placeholder denominator
    
    async def _get_conversion_type_breakdown(
        self, events: List[ConversionEvent]
    ) -> Dict[str, int]:
        """Get breakdown of conversion types"""
        breakdown = {}
        for event in events:
            event_type = event.event_type.value
            breakdown[event_type] = breakdown.get(event_type, 0) + 1
        return breakdown
    
    async def _identify_funnel_bottlenecks(
        self,
        funnel: ConversionFunnel,
        rates: Dict[str, float]
    ) -> List[str]:
        """Identify bottleneck steps in funnel"""
        if not rates:
            return []
        
        # Find steps with conversion rates significantly below average
        average_rate = np.mean(list(rates.values()))
        threshold = average_rate * 0.7  # 30% below average
        
        bottlenecks = [
            step for step, rate in rates.items()
            if rate < threshold
        ]
        
        return bottlenecks
    
    async def _generate_actionable_recommendations(
        self,
        funnel: ConversionFunnel,
        analysis: ConversionAnalysis,
        bottlenecks: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate specific actionable recommendations"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            recommendations.append({
                "step": bottleneck,
                "issue": "Low conversion rate",
                "recommended_action": f"Optimize user experience for {bottleneck} step",
                "priority": "high",
                "estimated_effort": "medium"
            })
        
        return recommendations
    
    async def _estimate_optimization_impact(
        self,
        funnel: ConversionFunnel,
        analysis: ConversionAnalysis,
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate impact of optimization efforts"""
        total_improvement = 0
        for opportunity in opportunities:
            total_improvement += opportunity.get("improvement", 0)
        
        return {
            "estimated_conversion_lift": total_improvement,
            "confidence_level": "medium",
            "implementation_timeline": "2-4 weeks"
        }
    
    # Additional helper methods would be implemented here...
    async def _get_user_touchpoints(self, user_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get user touchpoints for attribution"""
        return []  # Placeholder
    
    async def _apply_attribution_model(self, touchpoints: List[Dict[str, Any]], model: AttributionModel) -> Dict[str, float]:
        """Apply attribution model to touchpoints"""
        return {}  # Placeholder
    
    async def _update_real_time_metrics(self, event: ConversionEvent) -> None:
        """Update real-time metrics"""
        pass  # Placeholder
    
    async def _check_funnel_completions(self, event: ConversionEvent) -> None:
        """Check for funnel completions"""
        pass  # Placeholder
    
    async def _check_conversion_alerts(self, event: ConversionEvent) -> None:
        """Check if alerts should be triggered"""
        pass  # Placeholder
    
    async def _process_pending_events(self) -> None:
        """Process any pending events"""
        pass  # Placeholder
    
    async def _cleanup_old_events(self) -> None:
        """Clean up old events to manage memory"""
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        self.conversion_events = [
            e for e in self.conversion_events
            if e.timestamp >= cutoff_time
        ]
    
    async def _calculate_average_time_to_conversion(self, events: List[ConversionEvent]) -> float:
        """Calculate average time to conversion"""
        if not events:
            return 0.0
        return 24.0  # Placeholder - 24 hours average