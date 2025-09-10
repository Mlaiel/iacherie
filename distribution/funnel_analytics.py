"""
Funnel Analytics Engine
=====================

Advanced conversion funnel analysis system for Ainflue Distribution Platform.
Tracks user journey through conversion funnels with detailed step analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class FunnelStepType(Enum):
    """Types of funnel steps"""
    AWARENESS = "awareness"  # User becomes aware of content/brand
    INTEREST = "interest"  # User shows interest (click, view)
    CONSIDERATION = "consideration"  # User considers action (profile visit)
    INTENT = "intent"  # User shows purchase intent (add to cart)
    EVALUATION = "evaluation"  # User evaluates options (comparison)
    PURCHASE = "purchase"  # User makes purchase
    LOYALTY = "loyalty"  # User becomes repeat customer
    ADVOCACY = "advocacy"  # User becomes brand advocate

class AttributionModel(Enum):
    """Attribution models for funnel analysis"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"

class ConversionType(Enum):
    """Types of conversions to track"""
    SUBSCRIPTION = "subscription"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    ENGAGEMENT = "engagement"
    CONTENT_CONSUMPTION = "content_consumption"
    SOCIAL_FOLLOW = "social_follow"
    EMAIL_SIGNUP = "email_signup"
    PREMIUM_UPGRADE = "premium_upgrade"

@dataclass
class FunnelStep:
    """Definition of a funnel step"""
    step_id: str
    step_name: str
    step_type: FunnelStepType
    event_criteria: Dict[str, Any]
    required_previous_steps: List[str] = field(default_factory=list)
    max_time_since_previous: Optional[timedelta] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FunnelDefinition:
    """Complete funnel definition"""
    funnel_id: str
    funnel_name: str
    description: str
    steps: List[FunnelStep]
    conversion_goal: ConversionType
    attribution_model: AttributionModel = AttributionModel.LAST_TOUCH
    analysis_window_days: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserJourney:
    """Individual user journey through funnel"""
    user_id: str
    funnel_id: str
    journey_start: datetime
    journey_end: Optional[datetime] = None
    steps_completed: List[str] = field(default_factory=list)
    step_timestamps: Dict[str, datetime] = field(default_factory=dict)
    converted: bool = False
    conversion_value: float = 0.0
    attribution_data: Dict[str, Any] = field(default_factory=dict)
    dropout_step: Optional[str] = None
    total_time_to_convert: Optional[timedelta] = None

@dataclass
class FunnelStepMetrics:
    """Metrics for a specific funnel step"""
    step_id: str
    step_name: str
    step_position: int
    total_users_entered: int
    users_completed: int
    users_dropped_off: int
    completion_rate: float
    dropout_rate: float
    avg_time_to_complete: Optional[timedelta] = None
    conversion_rate_from_top: float = 0.0
    revenue_generated: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FunnelAnalysisResult:
    """Complete funnel analysis results"""
    funnel_definition: FunnelDefinition
    analysis_period: Tuple[datetime, datetime]
    total_users_entered: int
    total_conversions: int
    overall_conversion_rate: float
    total_revenue: float
    avg_time_to_convert: Optional[timedelta] = None
    step_metrics: List[FunnelStepMetrics] = field(default_factory=list)
    user_journeys: List[UserJourney] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    attribution_analysis: Dict[str, Any] = field(default_factory=dict)

class FunnelAnalytics:
    """
    Advanced funnel analytics engine
    
    Features:
    - Multi-step funnel analysis
    - Attribution modeling
    - User journey tracking
    - Conversion optimization insights
    - A/B testing support
    - Cohort funnel analysis
    - Real-time funnel monitoring
    """
    
    def __init__(self):
        self.user_events: List[Dict[str, Any]] = []
        self.funnels: Dict[str, FunnelDefinition] = {}
        self.user_journeys: Dict[str, List[UserJourney]] = defaultdict(list)
        self.analysis_cache: Dict[str, FunnelAnalysisResult] = {}
        
    async def add_user_events(self, events: List[Dict[str, Any]]):
        """Add user events for funnel analysis"""
        for event in events:
            # Ensure required fields
            event.setdefault('user_id', '')
            event.setdefault('event_type', '')
            event.setdefault('timestamp', datetime.now(timezone.utc))
            event.setdefault('platform', '')
            event.setdefault('metadata', {})
            
            self.user_events.append(event)
            
        logger.info(f"Added {len(events)} user events for funnel analysis")
        
    async def define_funnel(self, definition: FunnelDefinition):
        """Define a new conversion funnel"""
        # Validate funnel definition
        if not definition.steps:
            raise ValueError("Funnel must have at least one step")
            
        # Sort steps to ensure proper order
        for i, step in enumerate(definition.steps):
            step.metadata["step_position"] = i
            
        self.funnels[definition.funnel_id] = definition
        logger.info(f"Defined funnel {definition.funnel_id} with {len(definition.steps)} steps")
        
    async def analyze_funnel(
        self, 
        funnel_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        refresh_cache: bool = False
    ) -> FunnelAnalysisResult:
        """
        Perform comprehensive funnel analysis
        
        Args:
            funnel_id: ID of the funnel to analyze
            start_date: Analysis start date (default: 30 days ago)
            end_date: Analysis end date (default: now)
            refresh_cache: Whether to refresh cached results
            
        Returns:
            FunnelAnalysisResult with complete analysis
        """
        if funnel_id not in self.funnels:
            raise ValueError(f"Funnel {funnel_id} not found")
            
        # Set default date range
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        cache_key = f"{funnel_id}_{start_date.isoformat()}_{end_date.isoformat()}"
        
        # Check cache
        if not refresh_cache and cache_key in self.analysis_cache:
            logger.info(f"Returning cached funnel analysis for {funnel_id}")
            return self.analysis_cache[cache_key]
            
        definition = self.funnels[funnel_id]
        logger.info(f"Analyzing funnel {funnel_id} from {start_date} to {end_date}")
        
        # Build user journeys
        user_journeys = await self._build_user_journeys(definition, start_date, end_date)
        
        # Calculate step metrics
        step_metrics = await self._calculate_step_metrics(definition, user_journeys)
        
        # Calculate overall metrics
        total_users_entered = len(user_journeys)
        converted_journeys = [j for j in user_journeys if j.converted]
        total_conversions = len(converted_journeys)
        overall_conversion_rate = total_conversions / total_users_entered if total_users_entered > 0 else 0.0
        total_revenue = sum(j.conversion_value for j in converted_journeys)
        
        # Calculate average time to convert
        conversion_times = [j.total_time_to_convert for j in converted_journeys if j.total_time_to_convert]
        avg_time_to_convert = None
        if conversion_times:
            avg_time_to_convert = sum(conversion_times, timedelta()) / len(conversion_times)
            
        # Perform attribution analysis
        attribution_analysis = await self._perform_attribution_analysis(definition, user_journeys)
        
        # Generate insights and recommendations
        insights = await self._generate_funnel_insights(definition, step_metrics, user_journeys)
        recommendations = await self._generate_funnel_recommendations(definition, step_metrics, user_journeys)
        
        result = FunnelAnalysisResult(
            funnel_definition=definition,
            analysis_period=(start_date, end_date),
            total_users_entered=total_users_entered,
            total_conversions=total_conversions,
            overall_conversion_rate=overall_conversion_rate,
            total_revenue=total_revenue,
            avg_time_to_convert=avg_time_to_convert,
            step_metrics=step_metrics,
            user_journeys=user_journeys,
            insights=insights,
            recommendations=recommendations,
            attribution_analysis=attribution_analysis
        )
        
        # Cache the result
        self.analysis_cache[cache_key] = result
        
        logger.info(f"Completed funnel analysis: {total_users_entered} users, {total_conversions} conversions ({overall_conversion_rate:.2%})")
        return result
        
    async def _build_user_journeys(
        self, 
        definition: FunnelDefinition, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[UserJourney]:
        """Build user journeys through the funnel"""
        # Filter events to analysis period
        period_events = [
            event for event in self.user_events
            if start_date <= event['timestamp'] <= end_date
        ]
        
        # Group events by user
        user_events = defaultdict(list)
        for event in period_events:
            user_events[event['user_id']].append(event)
            
        # Sort events by timestamp for each user
        for user_id in user_events:
            user_events[user_id].sort(key=lambda e: e['timestamp'])
            
        journeys = []
        
        for user_id, events in user_events.items():
            journey = await self._build_single_user_journey(user_id, events, definition)
            if journey:
                journeys.append(journey)
                
        return journeys
        
    async def _build_single_user_journey(
        self, 
        user_id: str, 
        events: List[Dict[str, Any]], 
        definition: FunnelDefinition
    ) -> Optional[UserJourney]:
        """Build journey for a single user"""
        journey = UserJourney(
            user_id=user_id,
            funnel_id=definition.funnel_id,
            journey_start=events[0]['timestamp']
        )
        
        current_step_index = 0
        
        for event in events:
            # Check if event matches current step
            if current_step_index < len(definition.steps):
                current_step = definition.steps[current_step_index]
                
                if await self._event_matches_step(event, current_step):
                    # Check time constraint
                    if current_step.max_time_since_previous:
                        if journey.steps_completed:
                            last_step_time = journey.step_timestamps[journey.steps_completed[-1]]
                            time_since_last = event['timestamp'] - last_step_time
                            if time_since_last > current_step.max_time_since_previous:
                                # Time constraint violated, journey ends
                                journey.dropout_step = current_step.step_id
                                break
                                
                    # Step completed
                    journey.steps_completed.append(current_step.step_id)
                    journey.step_timestamps[current_step.step_id] = event['timestamp']
                    current_step_index += 1
                    
                    # Check if this is the final conversion step
                    if current_step_index == len(definition.steps):
                        journey.converted = True
                        journey.journey_end = event['timestamp']
                        journey.total_time_to_convert = journey.journey_end - journey.journey_start
                        journey.conversion_value = event.get('revenue', 0.0)
                        break
                        
        # Set dropout step if not converted
        if not journey.converted and current_step_index < len(definition.steps):
            journey.dropout_step = definition.steps[current_step_index].step_id
            
        # Only return journey if user entered the funnel (completed at least first step)
        return journey if journey.steps_completed else None
        
    async def _event_matches_step(self, event: Dict[str, Any], step: FunnelStep) -> bool:
        """Check if an event matches a funnel step criteria"""
        criteria = step.event_criteria
        
        # Check event type
        if 'event_type' in criteria:
            if event['event_type'] != criteria['event_type']:
                return False
                
        # Check platform
        if 'platform' in criteria:
            if event['platform'] != criteria['platform']:
                return False
                
        # Check custom criteria in metadata
        for key, expected_value in criteria.items():
            if key in ['event_type', 'platform']:
                continue
                
            if key in event.get('metadata', {}):
                if event['metadata'][key] != expected_value:
                    return False
            elif key in event:
                if event[key] != expected_value:
                    return False
                    
        return True
        
    async def _calculate_step_metrics(
        self, 
        definition: FunnelDefinition, 
        user_journeys: List[UserJourney]
    ) -> List[FunnelStepMetrics]:
        """Calculate metrics for each funnel step"""
        step_metrics = []
        
        for i, step in enumerate(definition.steps):
            # Count users who reached this step
            users_entered = len([
                j for j in user_journeys 
                if len(j.steps_completed) > i
            ])
            
            # Count users who completed this step
            users_completed = len([
                j for j in user_journeys 
                if step.step_id in j.steps_completed
            ])
            
            # Count users who dropped off at this step
            users_dropped_off = len([
                j for j in user_journeys 
                if j.dropout_step == step.step_id
            ])
            
            # Calculate rates
            completion_rate = users_completed / users_entered if users_entered > 0 else 0.0
            dropout_rate = users_dropped_off / users_entered if users_entered > 0 else 0.0
            
            # Calculate conversion rate from top of funnel
            total_funnel_entries = len(user_journeys)
            conversion_rate_from_top = users_completed / total_funnel_entries if total_funnel_entries > 0 else 0.0
            
            # Calculate average time to complete step
            step_completion_times = []
            for journey in user_journeys:
                if step.step_id in journey.step_timestamps:
                    if i == 0:
                        # First step - time from journey start
                        time_to_complete = journey.step_timestamps[step.step_id] - journey.journey_start
                    else:
                        # Subsequent steps - time from previous step
                        prev_step = definition.steps[i-1]
                        if prev_step.step_id in journey.step_timestamps:
                            time_to_complete = (journey.step_timestamps[step.step_id] - 
                                              journey.step_timestamps[prev_step.step_id])
                        else:
                            continue
                    step_completion_times.append(time_to_complete)
                    
            avg_time_to_complete = None
            if step_completion_times:
                avg_time_to_complete = sum(step_completion_times, timedelta()) / len(step_completion_times)
                
            # Calculate revenue generated at this step
            revenue_generated = 0.0
            if step.step_type in [FunnelStepType.PURCHASE, FunnelStepType.INTENT]:
                revenue_generated = sum(
                    j.conversion_value for j in user_journeys 
                    if step.step_id in j.steps_completed and j.converted
                )
                
            metrics = FunnelStepMetrics(
                step_id=step.step_id,
                step_name=step.step_name,
                step_position=i,
                total_users_entered=users_entered,
                users_completed=users_completed,
                users_dropped_off=users_dropped_off,
                completion_rate=completion_rate,
                dropout_rate=dropout_rate,
                avg_time_to_complete=avg_time_to_complete,
                conversion_rate_from_top=conversion_rate_from_top,
                revenue_generated=revenue_generated,
                metadata={
                    "step_type": step.step_type.value,
                    "average_time_seconds": avg_time_to_complete.total_seconds() if avg_time_to_complete else 0
                }
            )
            
            step_metrics.append(metrics)
            
        return step_metrics
        
    async def _perform_attribution_analysis(
        self, 
        definition: FunnelDefinition, 
        user_journeys: List[UserJourney]
    ) -> Dict[str, Any]:
        """Perform attribution analysis based on model"""
        attribution_data = {
            "model": definition.attribution_model.value,
            "channel_attribution": defaultdict(float),
            "step_attribution": defaultdict(float),
            "time_based_attribution": {}
        }
        
        converted_journeys = [j for j in user_journeys if j.converted]
        
        for journey in converted_journeys:
            # Get touchpoints (events that led to conversion)
            touchpoints = []
            for step_id in journey.steps_completed:
                touchpoints.append({
                    "step_id": step_id,
                    "timestamp": journey.step_timestamps[step_id],
                    "value": journey.conversion_value
                })
                
            if not touchpoints:
                continue
                
            # Apply attribution model
            if definition.attribution_model == AttributionModel.FIRST_TOUCH:
                attribution_data["step_attribution"][touchpoints[0]["step_id"]] += journey.conversion_value
                
            elif definition.attribution_model == AttributionModel.LAST_TOUCH:
                attribution_data["step_attribution"][touchpoints[-1]["step_id"]] += journey.conversion_value
                
            elif definition.attribution_model == AttributionModel.LINEAR:
                value_per_touchpoint = journey.conversion_value / len(touchpoints)
                for touchpoint in touchpoints:
                    attribution_data["step_attribution"][touchpoint["step_id"]] += value_per_touchpoint
                    
            elif definition.attribution_model == AttributionModel.TIME_DECAY:
                # Give more credit to recent touchpoints
                total_weight = sum(2**i for i in range(len(touchpoints)))
                for i, touchpoint in enumerate(touchpoints):
                    weight = 2**i / total_weight
                    attributed_value = journey.conversion_value * weight
                    attribution_data["step_attribution"][touchpoint["step_id"]] += attributed_value
                    
            elif definition.attribution_model == AttributionModel.POSITION_BASED:
                # 40% to first, 40% to last, 20% split among middle
                if len(touchpoints) == 1:
                    attribution_data["step_attribution"][touchpoints[0]["step_id"]] += journey.conversion_value
                elif len(touchpoints) == 2:
                    attribution_data["step_attribution"][touchpoints[0]["step_id"]] += journey.conversion_value * 0.5
                    attribution_data["step_attribution"][touchpoints[1]["step_id"]] += journey.conversion_value * 0.5
                else:
                    attribution_data["step_attribution"][touchpoints[0]["step_id"]] += journey.conversion_value * 0.4
                    attribution_data["step_attribution"][touchpoints[-1]["step_id"]] += journey.conversion_value * 0.4
                    
                    middle_value = journey.conversion_value * 0.2 / (len(touchpoints) - 2)
                    for touchpoint in touchpoints[1:-1]:
                        attribution_data["step_attribution"][touchpoint["step_id"]] += middle_value
                        
        return dict(attribution_data)
        
    async def _generate_funnel_insights(
        self, 
        definition: FunnelDefinition, 
        step_metrics: List[FunnelStepMetrics],
        user_journeys: List[UserJourney]
    ) -> List[str]:
        """Generate insights from funnel analysis"""
        insights = []
        
        if not step_metrics:
            return ["No funnel data available for analysis"]
            
        # Overall funnel performance
        total_conversion_rate = step_metrics[-1].conversion_rate_from_top if step_metrics else 0.0
        if total_conversion_rate > 0.1:  # 10%
            insights.append(f"Strong overall conversion rate of {total_conversion_rate:.1%}")
        elif total_conversion_rate > 0.05:  # 5%
            insights.append(f"Moderate conversion rate of {total_conversion_rate:.1%} with room for improvement")
        else:
            insights.append(f"Low conversion rate of {total_conversion_rate:.1%} indicates significant optimization opportunities")
            
        # Identify biggest drop-off points
        dropout_rates = [(metrics.step_name, metrics.dropout_rate) for metrics in step_metrics]
        dropout_rates.sort(key=lambda x: x[1], reverse=True)
        
        if dropout_rates and dropout_rates[0][1] > 0.3:
            insights.append(f"Highest dropout occurs at '{dropout_rates[0][0]}' step ({dropout_rates[0][1]:.1%})")
            
        # Conversion time insights
        converted_journeys = [j for j in user_journeys if j.converted]
        if converted_journeys:
            conversion_times = [j.total_time_to_convert.total_seconds() / 3600 for j in converted_journeys if j.total_time_to_convert]
            if conversion_times:
                avg_hours = sum(conversion_times) / len(conversion_times)
                if avg_hours < 1:
                    insights.append(f"Quick conversion funnel - users convert within {avg_hours:.1f} hours on average")
                elif avg_hours < 24:
                    insights.append(f"Same-day conversions - average time to convert is {avg_hours:.1f} hours")
                else:
                    insights.append(f"Extended consideration period - average {avg_hours/24:.1f} days to convert")
                    
        # Step completion insights
        step_completion_rates = [metrics.completion_rate for metrics in step_metrics]
        if len(step_completion_rates) > 1:
            rate_variance = np.std(step_completion_rates)
            if rate_variance < 0.1:
                insights.append("Consistent step completion rates indicate smooth user flow")
            else:
                insights.append("Variable step completion rates suggest user experience inconsistencies")
                
        return insights
        
    async def _generate_funnel_recommendations(
        self, 
        definition: FunnelDefinition, 
        step_metrics: List[FunnelStepMetrics],
        user_journeys: List[UserJourney]
    ) -> List[str]:
        """Generate recommendations for funnel optimization"""
        recommendations = []
        
        if not step_metrics:
            return ["Collect more user interaction data to enable funnel optimization"]
            
        # Identify steps with high dropout for optimization
        high_dropout_steps = [metrics for metrics in step_metrics if metrics.dropout_rate > 0.3]
        for step in high_dropout_steps:
            recommendations.append(
                f"Optimize '{step.step_name}' step - {step.dropout_rate:.1%} dropout rate indicates friction"
            )
            
        # Time-based recommendations
        slow_steps = [metrics for metrics in step_metrics 
                     if metrics.avg_time_to_complete and metrics.avg_time_to_complete.total_seconds() > 3600]
        for step in slow_steps:
            hours = step.avg_time_to_complete.total_seconds() / 3600
            recommendations.append(
                f"Reduce friction in '{step.step_name}' step - users take {hours:.1f} hours on average"
            )
            
        # Conversion rate recommendations
        total_conversion_rate = step_metrics[-1].conversion_rate_from_top if step_metrics else 0.0
        if total_conversion_rate < 0.05:
            recommendations.append("Consider A/B testing different funnel flows to improve overall conversion")
            recommendations.append("Implement progressive profiling to reduce form abandonment")
            
        # Attribution-based recommendations
        first_step_conversion = step_metrics[0].conversion_rate_from_top if step_metrics else 0.0
        last_step_conversion = step_metrics[-1].conversion_rate_from_top if step_metrics else 0.0
        
        if first_step_conversion > 0.8 and last_step_conversion < 0.1:
            recommendations.append("Strong initial interest but poor conversion - focus on later funnel steps")
        elif first_step_conversion < 0.3:
            recommendations.append("Low initial engagement - improve top-of-funnel content and targeting")
            
        return recommendations
        
    async def compare_funnels(
        self, 
        funnel_ids: List[str], 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Compare multiple funnels and identify best performers"""
        if len(funnel_ids) < 2:
            raise ValueError("At least 2 funnels required for comparison")
            
        # Analyze all funnels
        funnel_results = {}
        for funnel_id in funnel_ids:
            funnel_results[funnel_id] = await self.analyze_funnel(funnel_id, start_date, end_date)
            
        # Generate comparison
        comparison = {
            "funnels_compared": len(funnel_ids),
            "performance_comparison": {},
            "best_performers": {},
            "insights": []
        }
        
        # Compare conversion rates
        conversion_rates = {
            fid: result.overall_conversion_rate 
            for fid, result in funnel_results.items()
        }
        
        best_conversion_funnel = max(conversion_rates, key=conversion_rates.get)
        comparison["best_performers"]["conversion_rate"] = best_conversion_funnel
        
        # Compare average conversion times
        avg_conversion_times = {}
        for fid, result in funnel_results.items():
            if result.avg_time_to_convert:
                avg_conversion_times[fid] = result.avg_time_to_convert.total_seconds()
                
        if avg_conversion_times:
            fastest_funnel = min(avg_conversion_times, key=avg_conversion_times.get)
            comparison["best_performers"]["speed"] = fastest_funnel
            
        # Generate comparison insights
        best_rate = conversion_rates[best_conversion_funnel]
        worst_rate = min(conversion_rates.values())
        
        if best_rate > worst_rate * 2:
            comparison["insights"].append(
                f"Funnel '{best_conversion_funnel}' converts {best_rate/worst_rate:.1f}x better than worst performer"
            )
            
        return comparison

# Usage example
async def example_usage():
    """Example usage of FunnelAnalytics"""
    analytics = FunnelAnalytics()
    
    # Generate sample user events
    sample_events = []
    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    
    for user_id in range(1, 1001):  # 1000 users
        user_base_time = base_time + timedelta(hours=user_id)
        
        # Awareness event (everyone)
        sample_events.append({
            "user_id": f"user_{user_id}",
            "event_type": "content_view",
            "timestamp": user_base_time,
            "platform": "instagram",
            "metadata": {"content_type": "video"}
        })
        
        # Interest event (80% continue)
        if user_id % 5 != 0:
            sample_events.append({
                "user_id": f"user_{user_id}",
                "event_type": "profile_visit",
                "timestamp": user_base_time + timedelta(minutes=5),
                "platform": "instagram"
            })
            
            # Consideration event (50% continue)
            if user_id % 2 == 0:
                sample_events.append({
                    "user_id": f"user_{user_id}",
                    "event_type": "link_click",
                    "timestamp": user_base_time + timedelta(minutes=15),
                    "platform": "instagram",
                    "metadata": {"link_type": "bio_link"}
                })
                
                # Purchase event (10% convert)
                if user_id % 10 == 0:
                    sample_events.append({
                        "user_id": f"user_{user_id}",
                        "event_type": "purchase",
                        "timestamp": user_base_time + timedelta(hours=2),
                        "platform": "website",
                        "revenue": 29.99
                    })
                    
    await analytics.add_user_events(sample_events)
    
    # Define conversion funnel
    funnel_def = FunnelDefinition(
        funnel_id="instagram_to_purchase",
        funnel_name="Instagram to Purchase Funnel",
        description="User journey from Instagram content view to purchase",
        steps=[
            FunnelStep(
                step_id="awareness",
                step_name="Content View",
                step_type=FunnelStepType.AWARENESS,
                event_criteria={"event_type": "content_view"}
            ),
            FunnelStep(
                step_id="interest", 
                step_name="Profile Visit",
                step_type=FunnelStepType.INTEREST,
                event_criteria={"event_type": "profile_visit"},
                max_time_since_previous=timedelta(hours=1)
            ),
            FunnelStep(
                step_id="consideration",
                step_name="Link Click", 
                step_type=FunnelStepType.CONSIDERATION,
                event_criteria={"event_type": "link_click"},
                max_time_since_previous=timedelta(hours=2)
            ),
            FunnelStep(
                step_id="purchase",
                step_name="Purchase",
                step_type=FunnelStepType.PURCHASE, 
                event_criteria={"event_type": "purchase"},
                max_time_since_previous=timedelta(days=1)
            )
        ],
        conversion_goal=ConversionType.PURCHASE,
        attribution_model=AttributionModel.LINEAR
    )
    
    await analytics.define_funnel(funnel_def)
    
    # Analyze funnel
    result = await analytics.analyze_funnel("instagram_to_purchase")
    
    print(f"Funnel Analysis Results:")
    print(f"Total Users Entered: {result.total_users_entered}")
    print(f"Total Conversions: {result.total_conversions}")
    print(f"Conversion Rate: {result.overall_conversion_rate:.2%}")
    print(f"Total Revenue: ${result.total_revenue:.2f}")
    
    print(f"\nStep Metrics:")
    for step in result.step_metrics:
        print(f"  {step.step_name}: {step.completion_rate:.1%} completion, {step.dropout_rate:.1%} dropout")
        
    print(f"\nInsights:")
    for insight in result.insights:
        print(f"  - {insight}")
        
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")

if __name__ == "__main__":
    asyncio.run(example_usage())