"""
Attribution Analytics for Ainflue Distribution
Provides advanced attribution modeling and customer journey tracking

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict

import numpy as np
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class AttributionModel(str, Enum):
    """Attribution model types"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    CUSTOM = "custom"


class TouchpointType(str, Enum):
    """Types of customer touchpoints"""
    SOCIAL_POST = "social_post"
    AD_CLICK = "ad_click"
    EMAIL_CLICK = "email_click"
    ORGANIC_SEARCH = "organic_search"
    PAID_SEARCH = "paid_search"
    DIRECT_VISIT = "direct_visit"
    REFERRAL = "referral"
    INFLUENCER_MENTION = "influencer_mention"
    PUSH_NOTIFICATION = "push_notification"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VIDEO_VIEW = "video_view"
    STORY_VIEW = "story_view"
    SHARE = "share"
    COMMENT = "comment"
    LIKE = "like"
    FOLLOW = "follow"


class ConversionType(str, Enum):
    """Types of conversions to track"""
    PURCHASE = "purchase"
    SIGNUP = "signup"
    SUBSCRIPTION = "subscription"
    DOWNLOAD = "download"
    CONTACT = "contact"
    ENGAGEMENT = "engagement"
    SHARE = "share"
    FOLLOW = "follow"
    VIEW = "view"
    CUSTOM = "custom"


@dataclass
class Touchpoint:
    """Customer touchpoint data"""
    touchpoint_id: str
    user_id: str
    session_id: str
    touchpoint_type: TouchpointType
    platform: str
    content_id: Optional[str]
    campaign_id: Optional[str]
    timestamp: datetime
    value: float = 0.0  # Economic value of touchpoint
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Conversion:
    """Conversion event data"""
    conversion_id: str
    user_id: str
    session_id: str
    conversion_type: ConversionType
    value: float
    currency: str = "USD"
    timestamp: datetime = None
    attribution_window_hours: int = 168  # 7 days default
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CustomerJourney(BaseModel):
    """Customer journey model"""
    user_id: str = Field(..., description="User identifier")
    journey_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    touchpoints: List[Touchpoint] = Field(default_factory=list)
    conversions: List[Conversion] = Field(default_factory=list)
    first_touch: Optional[datetime] = Field(None, description="First touchpoint timestamp")
    last_touch: Optional[datetime] = Field(None, description="Last touchpoint timestamp")
    journey_duration_hours: float = Field(default=0.0, description="Journey duration")
    total_touchpoints: int = Field(default=0, description="Total touchpoints")
    unique_platforms: int = Field(default=0, description="Number of unique platforms")
    conversion_probability: float = Field(default=0.0, description="Predicted conversion probability")
    
    @validator('first_touch', 'last_touch')
    def validate_timestamps(cls, v) -> None:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class AttributionResult(BaseModel):
    """Attribution analysis result"""
    conversion_id: str = Field(..., description="Conversion identifier")
    total_value: float = Field(..., description="Total conversion value")
    attributed_touchpoints: List[Dict[str, Any]] = Field(..., description="Attributed touchpoints")
    model_used: AttributionModel = Field(..., description="Attribution model used")
    attribution_window_hours: int = Field(..., description="Attribution window")
    analysis_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = Field(default=1.0, description="Attribution confidence")
    
    @validator('analysis_timestamp')
    def validate_timestamp(cls, v) -> None:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class AttributionAnalytics:
    """
    Advanced attribution analytics engine
    Tracks customer journeys and attributes conversions to touchpoints
    """
    
    def __init__(self) -> None:
        self.touchpoints: Dict[str, Touchpoint] = {}
        self.conversions: Dict[str, Conversion] = {}
        self.journeys: Dict[str, CustomerJourney] = {}
        self.attribution_results: Dict[str, AttributionResult] = {}
        
        # Attribution model configurations
        self.model_configs = {
            AttributionModel.TIME_DECAY: {
                'decay_rate': 0.5,  # Half-life in days
                'decay_function': 'exponential'
            },
            AttributionModel.POSITION_BASED: {
                'first_touch_weight': 0.4,
                'last_touch_weight': 0.4,
                'middle_touches_weight': 0.2
            },
            AttributionModel.DATA_DRIVEN: {
                'min_conversions': 100,  # Minimum conversions for model training
                'lookback_days': 90
            }
        }
        
        # Platform value multipliers
        self.platform_multipliers = {
            'instagram': 1.2,
            'tiktok': 1.1,
            'youtube': 1.3,
            'facebook': 1.0,
            'twitter': 0.9,
            'linkedin': 1.4,
            'email': 1.5,
            'direct': 2.0
        }
        
    async def track_touchpoint(self, touchpoint: Touchpoint) -> bool:
        """
        Track a customer touchpoint
        
        Args:
            touchpoint: Touchpoint data
            
        Returns:
            Success status
        """
        try:
            # Store touchpoint
            self.touchpoints[touchpoint.touchpoint_id] = touchpoint
            
            # Update or create customer journey
            await self._update_customer_journey(touchpoint)
            
            logger.debug(f"Tracked touchpoint: {touchpoint.touchpoint_type.value} for user {touchpoint.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track touchpoint: {e}")
            return False
            
    async def track_conversion(self, conversion: Conversion) -> bool:
        """
        Track a conversion event
        
        Args:
            conversion: Conversion data
            
        Returns:
            Success status
        """
        try:
            # Store conversion
            self.conversions[conversion.conversion_id] = conversion
            
            # Update customer journey
            await self._update_customer_journey_with_conversion(conversion)
            
            # Run attribution analysis
            await self._run_attribution_analysis(conversion)
            
            logger.info(f"Tracked conversion: {conversion.conversion_type.value} - ${conversion.value} for user {conversion.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
            return False
            
    async def _update_customer_journey(self, touchpoint -> None: Touchpoint) -> None:
        """Update customer journey with new touchpoint"""
        user_id = touchpoint.user_id
        
        if user_id not in self.journeys:
            # Create new journey
            self.journeys[user_id] = CustomerJourney(user_id=user_id)
            
        journey = self.journeys[user_id]
        
        # Add touchpoint
        journey.touchpoints.append(touchpoint)
        
        # Update journey metadata
        journey.total_touchpoints = len(journey.touchpoints)
        
        # Update timestamps
        if not journey.first_touch or touchpoint.timestamp < journey.first_touch:
            journey.first_touch = touchpoint.timestamp
            
        if not journey.last_touch or touchpoint.timestamp > journey.last_touch:
            journey.last_touch = touchpoint.timestamp
            
        # Calculate journey duration
        if journey.first_touch and journey.last_touch:
            duration = journey.last_touch - journey.first_touch
            journey.journey_duration_hours = duration.total_seconds() / 3600
            
        # Calculate unique platforms
        platforms = set(tp.platform for tp in journey.touchpoints)
        journey.unique_platforms = len(platforms)
        
        # Update conversion probability (simplified)
        journey.conversion_probability = min(
            0.1 + (journey.total_touchpoints * 0.05) + (journey.unique_platforms * 0.1),
            0.95
        )
        
    async def _update_customer_journey_with_conversion(self, conversion -> None: Conversion) -> None:
        """Update customer journey with conversion"""
        user_id = conversion.user_id
        
        if user_id in self.journeys:
            journey = self.journeys[user_id]
            journey.conversions.append(conversion)
            
    async def _run_attribution_analysis(self, conversion -> None: Conversion) -> None:
        """Run attribution analysis for a conversion"""
        try:
            user_id = conversion.user_id
            
            if user_id not in self.journeys:
                logger.warning(f"No journey found for user {user_id}")
                return
                
            journey = self.journeys[user_id]
            
            # Get touchpoints within attribution window
            cutoff_time = conversion.timestamp - timedelta(hours=conversion.attribution_window_hours)
            relevant_touchpoints = [
                tp for tp in journey.touchpoints
                if tp.timestamp >= cutoff_time and tp.timestamp <= conversion.timestamp
            ]
            
            if not relevant_touchpoints:
                logger.warning(f"No relevant touchpoints found for conversion {conversion.conversion_id}")
                return
                
            # Run different attribution models
            models_to_run = [
                AttributionModel.FIRST_TOUCH,
                AttributionModel.LAST_TOUCH,
                AttributionModel.LINEAR,
                AttributionModel.TIME_DECAY,
                AttributionModel.POSITION_BASED
            ]
            
            for model in models_to_run:
                result = await self._apply_attribution_model(
                    conversion, relevant_touchpoints, model
                )
                
                if result:
                    result_id = f"{conversion.conversion_id}_{model.value}"
                    self.attribution_results[result_id] = result
                    
        except Exception as e:
            logger.error(f"Attribution analysis error: {e}")
            
    async def _apply_attribution_model(self, conversion: Conversion, 
                                     touchpoints: List[Touchpoint], 
                                     model: AttributionModel) -> Optional[AttributionResult]:
        """Apply specific attribution model"""
        try:
            if not touchpoints:
                return None
                
            attributed_touchpoints = []
            
            if model == AttributionModel.FIRST_TOUCH:
                # All credit to first touchpoint
                first_tp = min(touchpoints, key=lambda x: x.timestamp)
                attributed_touchpoints.append({
                    'touchpoint_id': first_tp.touchpoint_id,
                    'platform': first_tp.platform,
                    'touchpoint_type': first_tp.touchpoint_type.value,
                    'attribution_credit': 1.0,
                    'attributed_value': conversion.value,
                    'timestamp': first_tp.timestamp.isoformat()
                })
                
            elif model == AttributionModel.LAST_TOUCH:
                # All credit to last touchpoint
                last_tp = max(touchpoints, key=lambda x: x.timestamp)
                attributed_touchpoints.append({
                    'touchpoint_id': last_tp.touchpoint_id,
                    'platform': last_tp.platform,
                    'touchpoint_type': last_tp.touchpoint_type.value,
                    'attribution_credit': 1.0,
                    'attributed_value': conversion.value,
                    'timestamp': last_tp.timestamp.isoformat()
                })
                
            elif model == AttributionModel.LINEAR:
                # Equal credit to all touchpoints
                credit_per_touchpoint = 1.0 / len(touchpoints)
                value_per_touchpoint = conversion.value / len(touchpoints)
                
                for tp in touchpoints:
                    attributed_touchpoints.append({
                        'touchpoint_id': tp.touchpoint_id,
                        'platform': tp.platform,
                        'touchpoint_type': tp.touchpoint_type.value,
                        'attribution_credit': credit_per_touchpoint,
                        'attributed_value': value_per_touchpoint,
                        'timestamp': tp.timestamp.isoformat()
                    })
                    
            elif model == AttributionModel.TIME_DECAY:
                # Time-decayed attribution
                attributed_touchpoints = await self._apply_time_decay_attribution(
                    conversion, touchpoints
                )
                
            elif model == AttributionModel.POSITION_BASED:
                # Position-based attribution (40% first, 40% last, 20% middle)
                attributed_touchpoints = await self._apply_position_based_attribution(
                    conversion, touchpoints
                )
                
            return AttributionResult(
                conversion_id=conversion.conversion_id,
                total_value=conversion.value,
                attributed_touchpoints=attributed_touchpoints,
                model_used=model,
                attribution_window_hours=conversion.attribution_window_hours,
                confidence_score=self._calculate_confidence_score(touchpoints, model)
            )
            
        except Exception as e:
            logger.error(f"Attribution model application error: {e}")
            return None
            
    async def _apply_time_decay_attribution(self, conversion: Conversion, 
                                          touchpoints: List[Touchpoint]) -> List[Dict[str, Any]]:
        """Apply time decay attribution model"""
        config = self.model_configs[AttributionModel.TIME_DECAY]
        decay_rate = config['decay_rate']
        
        attributed_touchpoints = []
        total_weight = 0.0
        weights = []
        
        # Calculate weights based on time decay
        for tp in touchpoints:
            time_diff_hours = (conversion.timestamp - tp.timestamp).total_seconds() / 3600
            time_diff_days = time_diff_hours / 24
            
            # Exponential decay
            weight = np.exp(-decay_rate * time_diff_days)
            weights.append(weight)
            total_weight += weight
            
        # Normalize weights and attribute value
        for i, (tp, weight) in enumerate(zip(touchpoints, weights)):
            normalized_weight = weight / total_weight if total_weight > 0 else 0
            attributed_value = conversion.value * normalized_weight
            
            attributed_touchpoints.append({
                'touchpoint_id': tp.touchpoint_id,
                'platform': tp.platform,
                'touchpoint_type': tp.touchpoint_type.value,
                'attribution_credit': normalized_weight,
                'attributed_value': attributed_value,
                'timestamp': tp.timestamp.isoformat(),
                'time_decay_weight': weight
            })
            
        return attributed_touchpoints
        
    async def _apply_position_based_attribution(self, conversion: Conversion,
                                              touchpoints: List[Touchpoint]) -> List[Dict[str, Any]]:
        """Apply position-based attribution model"""
        config = self.model_configs[AttributionModel.POSITION_BASED]
        first_weight = config['first_touch_weight']
        last_weight = config['last_touch_weight']
        middle_weight = config['middle_touches_weight']
        
        attributed_touchpoints = []
        
        if len(touchpoints) == 1:
            # Single touchpoint gets all credit
            tp = touchpoints[0]
            attributed_touchpoints.append({
                'touchpoint_id': tp.touchpoint_id,
                'platform': tp.platform,
                'touchpoint_type': tp.touchpoint_type.value,
                'attribution_credit': 1.0,
                'attributed_value': conversion.value,
                'timestamp': tp.timestamp.isoformat()
            })
            
        elif len(touchpoints) == 2:
            # Split between first and last
            for i, tp in enumerate(touchpoints):
                weight = first_weight if i == 0 else last_weight
                attributed_value = conversion.value * weight
                
                attributed_touchpoints.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'platform': tp.platform,
                    'touchpoint_type': tp.touchpoint_type.value,
                    'attribution_credit': weight,
                    'attributed_value': attributed_value,
                    'timestamp': tp.timestamp.isoformat()
                })
                
        else:
            # First, middle, last distribution
            sorted_touchpoints = sorted(touchpoints, key=lambda x: x.timestamp)
            middle_touchpoints = sorted_touchpoints[1:-1]
            middle_weight_per_tp = middle_weight / len(middle_touchpoints) if middle_touchpoints else 0
            
            for i, tp in enumerate(sorted_touchpoints):
                if i == 0:
                    # First touchpoint
                    weight = first_weight
                elif i == len(sorted_touchpoints) - 1:
                    # Last touchpoint
                    weight = last_weight
                else:
                    # Middle touchpoint
                    weight = middle_weight_per_tp
                    
                attributed_value = conversion.value * weight
                
                attributed_touchpoints.append({
                    'touchpoint_id': tp.touchpoint_id,
                    'platform': tp.platform,
                    'touchpoint_type': tp.touchpoint_type.value,
                    'attribution_credit': weight,
                    'attributed_value': attributed_value,
                    'timestamp': tp.timestamp.isoformat(),
                    'position': 'first' if i == 0 else 'last' if i == len(sorted_touchpoints) - 1 else 'middle'
                })
                
        return attributed_touchpoints
        
    def _calculate_confidence_score(self, touchpoints: List[Touchpoint], 
                                  model: AttributionModel) -> float:
        """Calculate confidence score for attribution"""
        base_confidence = 0.8
        
        # Adjust based on number of touchpoints
        touchpoint_factor = min(len(touchpoints) / 5, 1.0)  # Max at 5 touchpoints
        
        # Adjust based on model complexity
        model_factors = {
            AttributionModel.FIRST_TOUCH: 0.6,
            AttributionModel.LAST_TOUCH: 0.6,
            AttributionModel.LINEAR: 0.8,
            AttributionModel.TIME_DECAY: 0.9,
            AttributionModel.POSITION_BASED: 0.9,
            AttributionModel.DATA_DRIVEN: 1.0
        }
        
        model_factor = model_factors.get(model, 0.8)
        
        # Adjust based on time spread
        if len(touchpoints) > 1:
            time_spread_hours = (
                max(tp.timestamp for tp in touchpoints) - 
                min(tp.timestamp for tp in touchpoints)
            ).total_seconds() / 3600
            
            # Better confidence with reasonable time spread (1-168 hours)
            time_factor = 1.0 if 1 <= time_spread_hours <= 168 else 0.8
        else:
            time_factor = 0.7
            
        confidence = base_confidence * touchpoint_factor * model_factor * time_factor
        return min(confidence, 1.0)
        
    async def get_attribution_report(self, 
                                   start_date: datetime, 
                                   end_date: datetime,
                                   model: AttributionModel = AttributionModel.LINEAR) -> Dict[str, Any]:
        """
        Generate attribution report for date range
        
        Args:
            start_date: Report start date
            end_date: Report end date
            model: Attribution model to use
            
        Returns:
            Attribution report
        """
        try:
            # Filter conversions by date range
            conversions_in_period = [
                conv for conv in self.conversions.values()
                if start_date <= conv.timestamp <= end_date
            ]
            
            if not conversions_in_period:
                return {'message': 'No conversions found in date range'}
                
            # Get attribution results for the model
            model_results = [
                result for result in self.attribution_results.values()
                if result.model_used == model and 
                result.conversion_id in [c.conversion_id for c in conversions_in_period]
            ]
            
            # Calculate platform attribution
            platform_attribution = defaultdict(lambda: {
                'attributed_value': 0.0,
                'attribution_count': 0,
                'unique_conversions': set()
            })
            
            touchpoint_type_attribution = defaultdict(lambda: {
                'attributed_value': 0.0,
                'attribution_count': 0,
                'unique_conversions': set()
            })
            
            total_attributed_value = 0.0
            total_conversions = len(conversions_in_period)
            
            for result in model_results:
                total_attributed_value += result.total_value
                
                for attributed_tp in result.attributed_touchpoints:
                    platform = attributed_tp['platform']
                    touchpoint_type = attributed_tp['touchpoint_type']
                    attributed_value = attributed_tp['attributed_value']
                    
                    # Platform attribution
                    platform_attribution[platform]['attributed_value'] += attributed_value
                    platform_attribution[platform]['attribution_count'] += 1
                    platform_attribution[platform]['unique_conversions'].add(result.conversion_id)
                    
                    # Touchpoint type attribution
                    touchpoint_type_attribution[touchpoint_type]['attributed_value'] += attributed_value
                    touchpoint_type_attribution[touchpoint_type]['attribution_count'] += 1
                    touchpoint_type_attribution[touchpoint_type]['unique_conversions'].add(result.conversion_id)
                    
            # Format platform results
            platform_results = []
            for platform, data in platform_attribution.items():
                platform_results.append({
                    'platform': platform,
                    'attributed_value': data['attributed_value'],
                    'attribution_percentage': (data['attributed_value'] / total_attributed_value * 100) if total_attributed_value > 0 else 0,
                    'conversion_count': len(data['unique_conversions']),
                    'average_value_per_conversion': data['attributed_value'] / len(data['unique_conversions']) if data['unique_conversions'] else 0
                })
                
            # Format touchpoint type results
            touchpoint_results = []
            for touchpoint_type, data in touchpoint_type_attribution.items():
                touchpoint_results.append({
                    'touchpoint_type': touchpoint_type,
                    'attributed_value': data['attributed_value'],
                    'attribution_percentage': (data['attributed_value'] / total_attributed_value * 100) if total_attributed_value > 0 else 0,
                    'conversion_count': len(data['unique_conversions']),
                    'average_value_per_conversion': data['attributed_value'] / len(data['unique_conversions']) if data['unique_conversions'] else 0
                })
                
            # Sort by attributed value
            platform_results.sort(key=lambda x: x['attributed_value'], reverse=True)
            touchpoint_results.sort(key=lambda x: x['attributed_value'], reverse=True)
            
            return {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'attribution_model': model.value,
                'summary': {
                    'total_conversions': total_conversions,
                    'total_attributed_value': total_attributed_value,
                    'average_conversion_value': total_attributed_value / total_conversions if total_conversions > 0 else 0,
                    'attributed_conversions': len(model_results)
                },
                'platform_attribution': platform_results,
                'touchpoint_type_attribution': touchpoint_results,
                'top_performing_platform': platform_results[0]['platform'] if platform_results else None,
                'top_performing_touchpoint': touchpoint_results[0]['touchpoint_type'] if touchpoint_results else None
            }
            
        except Exception as e:
            logger.error(f"Attribution report generation error: {e}")
            return {'error': str(e)}
            
    async def get_customer_journey_analysis(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze specific customer journey
        
        Args:
            user_id: Customer identifier
            
        Returns:
            Journey analysis
        """
        try:
            if user_id not in self.journeys:
                return {'error': 'Customer journey not found'}
                
            journey = self.journeys[user_id]
            
            # Analyze touchpoint patterns
            touchpoint_by_platform = defaultdict(int)
            touchpoint_by_type = defaultdict(int)
            touchpoint_timeline = []
            
            for tp in journey.touchpoints:
                touchpoint_by_platform[tp.platform] += 1
                touchpoint_by_type[tp.touchpoint_type.value] += 1
                touchpoint_timeline.append({
                    'timestamp': tp.timestamp.isoformat(),
                    'platform': tp.platform,
                    'type': tp.touchpoint_type.value,
                    'content_id': tp.content_id
                })
                
            # Analyze conversion patterns
            conversion_timeline = []
            total_conversion_value = 0.0
            
            for conv in journey.conversions:
                total_conversion_value += conv.value
                conversion_timeline.append({
                    'timestamp': conv.timestamp.isoformat(),
                    'type': conv.conversion_type.value,
                    'value': conv.value
                })
                
            # Calculate journey insights
            platform_diversity = len(touchpoint_by_platform)
            touchpoint_frequency = len(journey.touchpoints) / max(journey.journey_duration_hours / 24, 1)  # Per day
            
            return {
                'user_id': user_id,
                'journey_summary': {
                    'duration_hours': journey.journey_duration_hours,
                    'total_touchpoints': journey.total_touchpoints,
                    'unique_platforms': journey.unique_platforms,
                    'total_conversions': len(journey.conversions),
                    'total_conversion_value': total_conversion_value,
                    'conversion_probability': journey.conversion_probability
                },
                'touchpoint_analysis': {
                    'by_platform': dict(touchpoint_by_platform),
                    'by_type': dict(touchpoint_by_type),
                    'timeline': touchpoint_timeline,
                    'frequency_per_day': touchpoint_frequency
                },
                'conversion_analysis': {
                    'timeline': conversion_timeline,
                    'average_value': total_conversion_value / len(journey.conversions) if journey.conversions else 0
                },
                'insights': {
                    'platform_diversity_score': min(platform_diversity / 5, 1.0),  # Normalized to 0-1
                    'engagement_intensity': min(touchpoint_frequency / 2, 1.0),  # Normalized to 0-1
                    'journey_complexity': 'high' if journey.total_touchpoints > 10 else 'medium' if journey.total_touchpoints > 5 else 'low'
                }
            }
            
        except Exception as e:
            logger.error(f"Customer journey analysis error: {e}")
            return {'error': str(e)}
            
    def get_attribution_statistics(self) -> Dict[str, Any]:
        """Get overall attribution statistics"""
        try:
            total_touchpoints = len(self.touchpoints)
            total_conversions = len(self.conversions)
            total_journeys = len(self.journeys)
            
            # Calculate average journey metrics
            if self.journeys:
                avg_touchpoints_per_journey = np.mean([j.total_touchpoints for j in self.journeys.values()])
                avg_journey_duration = np.mean([j.journey_duration_hours for j in self.journeys.values()])
                avg_platforms_per_journey = np.mean([j.unique_platforms for j in self.journeys.values()])
            else:
                avg_touchpoints_per_journey = 0
                avg_journey_duration = 0
                avg_platforms_per_journey = 0
                
            # Platform distribution
            platform_counts = defaultdict(int)
            for tp in self.touchpoints.values():
                platform_counts[tp.platform] += 1
                
            # Conversion type distribution
            conversion_type_counts = defaultdict(int)
            total_conversion_value = 0.0
            
            for conv in self.conversions.values():
                conversion_type_counts[conv.conversion_type.value] += 1
                total_conversion_value += conv.value
                
            return {
                'totals': {
                    'touchpoints': total_touchpoints,
                    'conversions': total_conversions,
                    'customer_journeys': total_journeys,
                    'attribution_results': len(self.attribution_results)
                },
                'averages': {
                    'touchpoints_per_journey': round(avg_touchpoints_per_journey, 2),
                    'journey_duration_hours': round(avg_journey_duration, 2),
                    'platforms_per_journey': round(avg_platforms_per_journey, 2),
                    'conversion_value': round(total_conversion_value / total_conversions, 2) if total_conversions > 0 else 0
                },
                'distributions': {
                    'platforms': dict(platform_counts),
                    'conversion_types': dict(conversion_type_counts)
                },
                'conversion_rate': round(total_conversions / total_journeys * 100, 2) if total_journeys > 0 else 0,
                'total_revenue': total_conversion_value
            }
            
        except Exception as e:
            logger.error(f"Attribution statistics error: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'AttributionAnalytics',
    'Touchpoint',
    'Conversion',
    'CustomerJourney',
    'AttributionResult',
    'AttributionModel',
    'TouchpointType',
    'ConversionType'
]