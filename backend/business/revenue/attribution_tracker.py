"""Revenue Attribution Tracker - IA Influencer Agent Platform
=========================================================

Advanced multi-platform revenue attribution and tracking system for
accurate revenue source identification and performance measurement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class AttributionModel(Enum):
    """Revenue attribution models."""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


class RevenueSource(Enum):
    """Revenue source types."""
    DIRECT_SALES = "direct_sales"
    AFFILIATE_MARKETING = "affiliate_marketing"
    SPONSORED_CONTENT = "sponsored_content"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    PLATFORM_REVENUE = "platform_revenue"


@dataclass
class AttributionTouchpoint:
    """Revenue attribution touchpoint."""
    touchpoint_id: str
    timestamp: datetime
    platform: str
    content_id: str
    interaction_type: str
    user_id: str
    revenue_value: Decimal
    attribution_weight: float
    conversion_probability: float


@dataclass
class RevenueAttribution:
    """Revenue attribution result."""
    revenue_id: str
    total_revenue: Decimal
    attribution_model: AttributionModel
    touchpoints: List[AttributionTouchpoint]
    attribution_breakdown: Dict[str, Decimal]
    confidence_score: float
    time_to_conversion: timedelta


class RevenueAttributionTracker:
    """Advanced revenue attribution tracking system."""
    
    def __init__(self, creator_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize revenue attribution tracker."""
        self.creator_id = creator_id
        self.config = config or {}
        self.touchpoint_history: List[AttributionTouchpoint] = []
        self.attribution_models: Dict[AttributionModel, Any] = {}
        self.conversion_tracking: Dict[str, Any] = {}
        
    async def track_touchpoint(
        self,
        platform: str,
        content_id: str,
        interaction_type: str,
        user_id: str,
        interaction_data: Dict[str, Any]
    ) -> str:
        """Track a revenue attribution touchpoint."""
        try:
            touchpoint_id = str(uuid.uuid4())
            
            # Calculate revenue value for this touchpoint
            revenue_value = await self._calculate_touchpoint_revenue_value(
                platform, interaction_type, interaction_data
            )
            
            # Calculate conversion probability
            conversion_probability = await self._calculate_conversion_probability(
                platform, interaction_type, user_id, interaction_data
            )
            
            # Create touchpoint
            touchpoint = AttributionTouchpoint(
                touchpoint_id=touchpoint_id,
                timestamp=datetime.utcnow(),
                platform=platform,
                content_id=content_id,
                interaction_type=interaction_type,
                user_id=user_id,
                revenue_value=revenue_value,
                attribution_weight=0.0,  # Will be calculated during attribution
                conversion_probability=conversion_probability
            )
            
            # Store touchpoint
            self.touchpoint_history.append(touchpoint)
            
            # Update user journey tracking
            await self._update_user_journey_tracking(user_id, touchpoint)
            
            logger.info(f"Tracked touchpoint {touchpoint_id} for user {user_id}")
            return touchpoint_id
            
        except Exception as e:
            logger.error(f"Failed to track touchpoint: {e}")
            raise
    
    async def attribute_revenue(
        self,
        revenue_event: Dict[str, Any],
        attribution_model: AttributionModel = AttributionModel.DATA_DRIVEN,
        lookback_days: int = 30
    ) -> RevenueAttribution:
        """Attribute revenue to touchpoints using specified model."""
        try:
            user_id = revenue_event['user_id']
            revenue_amount = Decimal(str(revenue_event['amount']))
            conversion_time = datetime.fromisoformat(revenue_event['timestamp'])
            
            # Get relevant touchpoints for this conversion
            relevant_touchpoints = await self._get_relevant_touchpoints(
                user_id, conversion_time, lookback_days
            )
            
            if not relevant_touchpoints:
                logger.warning(f"No touchpoints found for revenue attribution: {user_id}")
                return self._create_empty_attribution(revenue_event)
            
            # Apply attribution model
            attributed_touchpoints = await self._apply_attribution_model(
                relevant_touchpoints, attribution_model, revenue_amount
            )
            
            # Calculate attribution breakdown
            attribution_breakdown = await self._calculate_attribution_breakdown(
                attributed_touchpoints
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_attribution_confidence(
                attributed_touchpoints, attribution_model
            )
            
            # Calculate time to conversion
            first_touchpoint = min(attributed_touchpoints, key=lambda tp: tp.timestamp)
            time_to_conversion = conversion_time - first_touchpoint.timestamp
            
            # Create attribution result
            attribution = RevenueAttribution(
                revenue_id=revenue_event.get('revenue_id', str(uuid.uuid4())),
                total_revenue=revenue_amount,
                attribution_model=attribution_model,
                touchpoints=attributed_touchpoints,
                attribution_breakdown=attribution_breakdown,
                confidence_score=confidence_score,
                time_to_conversion=time_to_conversion
            )
            
            # Store attribution result
            await self._store_attribution_result(attribution)
            
            return attribution
            
        except Exception as e:
            logger.error(f"Revenue attribution failed: {e}")
            raise
    
    async def analyze_attribution_performance(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = "platform"
    ) -> Dict[str, Any]:
        """Analyze attribution performance across different dimensions."""
        try:
            # Get attribution data for the period
            attribution_data = await self._get_attribution_data(start_date, end_date)
            
            # Group and analyze data
            if group_by == "platform":
                analysis = await self._analyze_by_platform(attribution_data)
            elif group_by == "content":
                analysis = await self._analyze_by_content(attribution_data)
            elif group_by == "time":
                analysis = await self._analyze_by_time(attribution_data)
            else:
                analysis = await self._analyze_overall(attribution_data)
            
            # Calculate key metrics
            key_metrics = await self._calculate_attribution_metrics(attribution_data)
            
            return {
                "analysis": analysis,
                "key_metrics": key_metrics,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_revenue_attributed": sum(
                    float(attr.total_revenue) for attr in attribution_data
                )
            }
            
        except Exception as e:
            logger.error(f"Attribution performance analysis failed: {e}")
            raise
    
    async def compare_attribution_models(
        self,
        revenue_events: List[Dict[str, Any]],
        models: List[AttributionModel] = None
    ) -> Dict[str, Any]:
        """Compare different attribution models for the same revenue events."""
        try:
            if models is None:
                models = [
                    AttributionModel.FIRST_TOUCH,
                    AttributionModel.LAST_TOUCH,
                    AttributionModel.LINEAR,
                    AttributionModel.DATA_DRIVEN
                ]
            
            model_comparisons = {}
            
            for model in models:
                model_results = []
                
                for revenue_event in revenue_events:
                    attribution = await self.attribute_revenue(revenue_event, model)
                    model_results.append(attribution)
                
                # Calculate model performance metrics
                model_performance = await self._calculate_model_performance(model_results)
                
                model_comparisons[model.value] = {
                    "attributions": len(model_results),
                    "performance": model_performance,
                    "avg_confidence": sum(
                        attr.confidence_score for attr in model_results
                    ) / len(model_results) if model_results else 0,
                    "total_attributed_revenue": sum(
                        float(attr.total_revenue) for attr in model_results
                    )
                }
            
            # Recommend best model
            best_model = await self._recommend_best_attribution_model(model_comparisons)
            
            return {
                "model_comparisons": model_comparisons,
                "recommended_model": best_model,
                "comparison_summary": await self._generate_comparison_summary(
                    model_comparisons
                )
            }
            
        except Exception as e:
            logger.error(f"Attribution model comparison failed: {e}")
            raise
    
    async def generate_attribution_insights(
        self,
        analysis_period_days: int = 90
    ) -> Dict[str, Any]:
        """Generate actionable insights from attribution data."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Get comprehensive attribution analysis
            attribution_analysis = await self.analyze_attribution_performance(
                start_date, end_date
            )
            
            # Identify high-performing touchpoints
            high_performing_touchpoints = await self._identify_high_performing_touchpoints(
                start_date, end_date
            )
            
            # Analyze conversion patterns
            conversion_patterns = await self._analyze_conversion_patterns(
                start_date, end_date
            )
            
            # Calculate opportunity scores
            opportunity_scores = await self._calculate_opportunity_scores(
                attribution_analysis, conversion_patterns
            )
            
            # Generate recommendations
            recommendations = await self._generate_attribution_recommendations(
                high_performing_touchpoints, conversion_patterns, opportunity_scores
            )
            
            return {
                "insights": {
                    "high_performing_touchpoints": high_performing_touchpoints,
                    "conversion_patterns": conversion_patterns,
                    "opportunity_scores": opportunity_scores
                },
                "recommendations": recommendations,
                "attribution_analysis": attribution_analysis,
                "analysis_period_days": analysis_period_days
            }
            
        except Exception as e:
            logger.error(f"Attribution insights generation failed: {e}")
            raise
    
    async def _calculate_touchpoint_revenue_value(
        self,
        platform: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ) -> Decimal:
        """Calculate potential revenue value for a touchpoint."""
        # Base value calculation based on interaction type
        base_values = {
            "view": Decimal("0.50"),
            "like": Decimal("1.00"),
            "comment": Decimal("2.50"),
            "share": Decimal("5.00"),
            "click": Decimal("3.00"),
            "purchase": Decimal("50.00"),
            "subscription": Decimal("25.00")
        }
        
        base_value = base_values.get(interaction_type, Decimal("1.00"))
        
        # Platform multiplier
        platform_multipliers = {
            "youtube": Decimal("1.2"),
            "instagram": Decimal("1.1"),
            "tiktok": Decimal("1.0"),
            "twitter": Decimal("0.9"),
            "facebook": Decimal("1.1")
        }
        
        platform_multiplier = platform_multipliers.get(platform.lower(), Decimal("1.0"))
        
        # Engagement quality multiplier
        engagement_quality = interaction_data.get("engagement_quality", 1.0)
        quality_multiplier = Decimal(str(max(0.5, min(2.0, engagement_quality))))
        
        revenue_value = base_value * platform_multiplier * quality_multiplier
        
        return revenue_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    async def _calculate_conversion_probability(
        self,
        platform: str,
        interaction_type: str,
        user_id: str,
        interaction_data: Dict[str, Any]
    ) -> float:
        """Calculate conversion probability for a touchpoint."""
        # Base conversion probabilities by interaction type
        base_probabilities = {
            "view": 0.01,
            "like": 0.02,
            "comment": 0.05,
            "share": 0.08,
            "click": 0.12,
            "purchase": 0.90,
            "subscription": 0.85
        }
        
        base_prob = base_probabilities.get(interaction_type, 0.01)
        
        # User engagement history factor
        user_engagement_score = interaction_data.get("user_engagement_score", 0.5)
        
        # Platform conversion factor
        platform_factors = {
            "youtube": 1.1,
            "instagram": 1.0,
            "tiktok": 0.9,
            "twitter": 0.8,
            "facebook": 1.0
        }
        
        platform_factor = platform_factors.get(platform.lower(), 1.0)
        
        # Calculate final probability
        probability = base_prob * user_engagement_score * platform_factor
        
        return max(0.001, min(0.999, probability))
    
    async def _update_user_journey_tracking(
        self,
        user_id: str,
        touchpoint: AttributionTouchpoint
    ) -> None:
        """Update user journey tracking with new touchpoint."""
        if user_id not in self.conversion_tracking:
            self.conversion_tracking[user_id] = {
                "touchpoints": [],
                "first_interaction": touchpoint.timestamp,
                "last_interaction": touchpoint.timestamp,
                "total_interactions": 0,
                "conversion_score": 0.0
            }
        
        journey = self.conversion_tracking[user_id]
        journey["touchpoints"].append(touchpoint.touchpoint_id)
        journey["last_interaction"] = touchpoint.timestamp
        journey["total_interactions"] += 1
        
        # Update conversion score
        journey["conversion_score"] += touchpoint.conversion_probability * 0.1
        journey["conversion_score"] = min(1.0, journey["conversion_score"])
    
    async def _get_relevant_touchpoints(
        self,
        user_id: str,
        conversion_time: datetime,
        lookback_days: int
    ) -> List[AttributionTouchpoint]:
        """Get relevant touchpoints for revenue attribution."""
        cutoff_time = conversion_time - timedelta(days=lookback_days)
        
        relevant_touchpoints = [
            tp for tp in self.touchpoint_history
            if (tp.user_id == user_id and 
                cutoff_time <= tp.timestamp <= conversion_time)
        ]
        
        # Sort by timestamp
        relevant_touchpoints.sort(key=lambda tp: tp.timestamp)
        
        return relevant_touchpoints
    
    async def _apply_attribution_model(
        self,
        touchpoints: List[AttributionTouchpoint],
        model: AttributionModel,
        total_revenue: Decimal
    ) -> List[AttributionTouchpoint]:
        """Apply attribution model to assign weights to touchpoints."""
        if not touchpoints:
            return []
        
        # Calculate weights based on model
        if model == AttributionModel.FIRST_TOUCH:
            weights = await self._calculate_first_touch_weights(touchpoints)
        elif model == AttributionModel.LAST_TOUCH:
            weights = await self._calculate_last_touch_weights(touchpoints)
        elif model == AttributionModel.LINEAR:
            weights = await self._calculate_linear_weights(touchpoints)
        elif model == AttributionModel.TIME_DECAY:
            weights = await self._calculate_time_decay_weights(touchpoints)
        elif model == AttributionModel.POSITION_BASED:
            weights = await self._calculate_position_based_weights(touchpoints)
        else:  # DATA_DRIVEN
            weights = await self._calculate_data_driven_weights(touchpoints)
        
        # Apply weights to touchpoints
        attributed_touchpoints = []
        for i, touchpoint in enumerate(touchpoints):
            attributed_touchpoint = AttributionTouchpoint(
                touchpoint_id=touchpoint.touchpoint_id,
                timestamp=touchpoint.timestamp,
                platform=touchpoint.platform,
                content_id=touchpoint.content_id,
                interaction_type=touchpoint.interaction_type,
                user_id=touchpoint.user_id,
                revenue_value=total_revenue * Decimal(str(weights[i])),
                attribution_weight=weights[i],
                conversion_probability=touchpoint.conversion_probability
            )
            attributed_touchpoints.append(attributed_touchpoint)
        
        return attributed_touchpoints
    
    async def _calculate_first_touch_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate first touch attribution weights."""
        weights = [0.0] * len(touchpoints)
        if touchpoints:
            weights[0] = 1.0
        return weights
    
    async def _calculate_last_touch_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate last touch attribution weights."""
        weights = [0.0] * len(touchpoints)
        if touchpoints:
            weights[-1] = 1.0
        return weights
    
    async def _calculate_linear_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate linear attribution weights."""
        if not touchpoints:
            return []
        
        weight = 1.0 / len(touchpoints)
        return [weight] * len(touchpoints)
    
    async def _calculate_time_decay_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate time decay attribution weights."""
        if not touchpoints:
            return []
        
        # More recent touchpoints get higher weights
        decay_factor = 0.5
        weights = []
        
        conversion_time = touchpoints[-1].timestamp
        
        for touchpoint in touchpoints:
            time_diff = (conversion_time - touchpoint.timestamp).total_seconds()
            days_diff = time_diff / (24 * 3600)
            
            # Calculate decay weight
            weight = decay_factor ** days_diff
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        return weights
    
    async def _calculate_position_based_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate position-based attribution weights (40% first, 20% last, 40% middle)."""
        if not touchpoints:
            return []
        
        if len(touchpoints) == 1:
            return [1.0]
        
        weights = [0.0] * len(touchpoints)
        
        # First touch gets 40%
        weights[0] = 0.4
        
        # Last touch gets 20%
        weights[-1] = 0.2
        
        # Middle touches share remaining 40%
        if len(touchpoints) > 2:
            middle_weight = 0.4 / (len(touchpoints) - 2)
            for i in range(1, len(touchpoints) - 1):
                weights[i] = middle_weight
        
        return weights
    
    async def _calculate_data_driven_weights(
        self,
        touchpoints: List[AttributionTouchpoint]
    ) -> List[float]:
        """Calculate data-driven attribution weights based on conversion probabilities."""
        if not touchpoints:
            return []
        
        # Use conversion probabilities as basis for weights
        conversion_probs = [tp.conversion_probability for tp in touchpoints]
        
        # Apply additional factors
        weights = []
        for i, prob in enumerate(conversion_probs):
            # Factor in position (slight bias toward middle of journey)
            position_factor = 1.0
            if len(touchpoints) > 1:
                position = i / (len(touchpoints) - 1)  # 0 to 1
                # Slight U-curve: higher weight for first, last, and middle
                position_factor = 0.8 + 0.4 * (1 - abs(position - 0.5) * 2)
            
            weight = prob * position_factor
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            # Fallback to linear if no conversion probabilities
            weight = 1.0 / len(touchpoints)
            weights = [weight] * len(touchpoints)
        
        return weights
    
    async def _calculate_attribution_breakdown(
        self,
        attributed_touchpoints: List[AttributionTouchpoint]
    ) -> Dict[str, Decimal]:
        """Calculate attribution breakdown by platform/channel."""
        breakdown = {}
        
        for touchpoint in attributed_touchpoints:
            platform = touchpoint.platform
            if platform not in breakdown:
                breakdown[platform] = Decimal('0')
            breakdown[platform] += touchpoint.revenue_value
        
        # Round values
        for platform in breakdown:
            breakdown[platform] = breakdown[platform].quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        return breakdown
    
    async def _calculate_attribution_confidence(
        self,
        attributed_touchpoints: List[AttributionTouchpoint],
        attribution_model: AttributionModel
    ) -> float:
        """Calculate confidence score for attribution."""
        if not attributed_touchpoints:
            return 0.0
        
        # Base confidence by model
        model_confidences = {
            AttributionModel.FIRST_TOUCH: 0.6,
            AttributionModel.LAST_TOUCH: 0.7,
            AttributionModel.LINEAR: 0.75,
            AttributionModel.TIME_DECAY: 0.8,
            AttributionModel.POSITION_BASED: 0.85,
            AttributionModel.DATA_DRIVEN: 0.9
        }
        
        base_confidence = model_confidences.get(attribution_model, 0.7)
        
        # Adjust based on touchpoint quality
        avg_conversion_prob = sum(
            tp.conversion_probability for tp in attributed_touchpoints
        ) / len(attributed_touchpoints)
        
        # Adjust based on journey length (more touchpoints = higher confidence)
        journey_factor = min(1.0, len(attributed_touchpoints) / 5.0)
        
        final_confidence = base_confidence * avg_conversion_prob * journey_factor
        
        return max(0.1, min(0.95, final_confidence))
    
    def _create_empty_attribution(self, revenue_event: Dict[str, Any]) -> RevenueAttribution:
        """Create empty attribution for revenues with no touchpoints."""
        return RevenueAttribution(
            revenue_id=revenue_event.get('revenue_id', str(uuid.uuid4())),
            total_revenue=Decimal(str(revenue_event['amount'])),
            attribution_model=AttributionModel.LAST_TOUCH,
            touchpoints=[],
            attribution_breakdown={'direct': Decimal(str(revenue_event['amount']))},
            confidence_score=0.3,
            time_to_conversion=timedelta(0)
        )
    
    async def _store_attribution_result(self, attribution: RevenueAttribution) -> None:
        """Store attribution result for future analysis."""
        # In a real implementation, this would store to a database
        logger.info(f"Stored attribution result for revenue {attribution.revenue_id}")
    
    async def _get_attribution_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[RevenueAttribution]:
        """Get attribution data for the specified period."""
        # In a real implementation, this would query the database
        # For now, return mock data based on touchpoint history
        
        # Filter touchpoints by date range
        relevant_touchpoints = [
            tp for tp in self.touchpoint_history
            if start_date <= tp.timestamp <= end_date
        ]
        
        # Create mock attribution data
        mock_attributions = []
        for i, touchpoint in enumerate(relevant_touchpoints[:10]):  # Limit for example
            attribution = RevenueAttribution(
                revenue_id=str(uuid.uuid4()),
                total_revenue=touchpoint.revenue_value * Decimal('10'),
                attribution_model=AttributionModel.DATA_DRIVEN,
                touchpoints=[touchpoint],
                attribution_breakdown={touchpoint.platform: touchpoint.revenue_value * Decimal('10')},
                confidence_score=0.8,
                time_to_conversion=timedelta(days=1)
            )
            mock_attributions.append(attribution)
        
        return mock_attributions
    
    async def _analyze_by_platform(
        self,
        attribution_data: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Analyze attribution data by platform."""
        platform_analysis = {}
        
        for attribution in attribution_data:
            for platform, revenue in attribution.attribution_breakdown.items():
                if platform not in platform_analysis:
                    platform_analysis[platform] = {
                        'total_revenue': Decimal('0'),
                        'attribution_count': 0,
                        'avg_confidence': 0.0,
                        'confidence_scores': []
                    }
                
                platform_analysis[platform]['total_revenue'] += revenue
                platform_analysis[platform]['attribution_count'] += 1
                platform_analysis[platform]['confidence_scores'].append(attribution.confidence_score)
        
        # Calculate averages
        for platform, data in platform_analysis.items():
            if data['confidence_scores']:
                data['avg_confidence'] = sum(data['confidence_scores']) / len(data['confidence_scores'])
            data['avg_revenue_per_attribution'] = float(
                data['total_revenue'] / data['attribution_count']
            ) if data['attribution_count'] > 0 else 0
            del data['confidence_scores']  # Remove intermediate data
        
        return platform_analysis
    
    async def _analyze_by_content(
        self,
        attribution_data: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Analyze attribution data by content."""
        content_analysis = {}
        
        for attribution in attribution_data:
            for touchpoint in attribution.touchpoints:
                content_id = touchpoint.content_id
                if content_id not in content_analysis:
                    content_analysis[content_id] = {
                        'total_attributed_revenue': Decimal('0'),
                        'touchpoint_count': 0,
                        'platforms': set(),
                        'interaction_types': set()
                    }
                
                content_analysis[content_id]['total_attributed_revenue'] += touchpoint.revenue_value
                content_analysis[content_id]['touchpoint_count'] += 1
                content_analysis[content_id]['platforms'].add(touchpoint.platform)
                content_analysis[content_id]['interaction_types'].add(touchpoint.interaction_type)
        
        # Convert sets to lists for JSON serialization
        for content_id, data in content_analysis.items():
            data['platforms'] = list(data['platforms'])
            data['interaction_types'] = list(data['interaction_types'])
            data['total_attributed_revenue'] = float(data['total_attributed_revenue'])
        
        return content_analysis
    
    async def _analyze_by_time(
        self,
        attribution_data: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Analyze attribution data by time periods."""
        time_analysis = {}
        
        for attribution in attribution_data:
            # Group by conversion time to conversion
            days_to_conversion = attribution.time_to_conversion.days
            
            # Group into buckets
            if days_to_conversion <= 1:
                bucket = "0-1 days"
            elif days_to_conversion <= 7:
                bucket = "2-7 days"
            elif days_to_conversion <= 30:
                bucket = "8-30 days"
            else:
                bucket = "30+ days"
            
            if bucket not in time_analysis:
                time_analysis[bucket] = {
                    'total_revenue': Decimal('0'),
                    'attribution_count': 0,
                    'avg_confidence': 0.0,
                    'confidence_scores': []
                }
            
            time_analysis[bucket]['total_revenue'] += attribution.total_revenue
            time_analysis[bucket]['attribution_count'] += 1
            time_analysis[bucket]['confidence_scores'].append(attribution.confidence_score)
        
        # Calculate averages
        for bucket, data in time_analysis.items():
            if data['confidence_scores']:
                data['avg_confidence'] = sum(data['confidence_scores']) / len(data['confidence_scores'])
            data['total_revenue'] = float(data['total_revenue'])
            del data['confidence_scores']
        
        return time_analysis
    
    async def _analyze_overall(
        self,
        attribution_data: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Analyze overall attribution performance."""
        if not attribution_data:
            return {}
        
        total_revenue = sum(float(attr.total_revenue) for attr in attribution_data)
        avg_confidence = sum(attr.confidence_score for attr in attribution_data) / len(attribution_data)
        avg_time_to_conversion = sum(
            attr.time_to_conversion.total_seconds() for attr in attribution_data
        ) / len(attribution_data) / (24 * 3600)  # Convert to days
        
        # Count unique touchpoint types
        all_touchpoints = []
        for attr in attribution_data:
            all_touchpoints.extend(attr.touchpoints)
        
        unique_platforms = set(tp.platform for tp in all_touchpoints)
        unique_interaction_types = set(tp.interaction_type for tp in all_touchpoints)
        
        return {
            'total_revenue': total_revenue,
            'attribution_count': len(attribution_data),
            'avg_confidence': avg_confidence,
            'avg_time_to_conversion_days': avg_time_to_conversion,
            'unique_platforms': len(unique_platforms),
            'unique_interaction_types': len(unique_interaction_types),
            'total_touchpoints': len(all_touchpoints)
        }
    
    async def _calculate_attribution_metrics(
        self,
        attribution_data: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Calculate key attribution metrics."""
        if not attribution_data:
            return {}
        
        # Attribution model distribution
        model_distribution = {}
        for attr in attribution_data:
            model = attr.attribution_model.value
            model_distribution[model] = model_distribution.get(model, 0) + 1
        
        # Revenue distribution by confidence
        high_confidence_revenue = sum(
            float(attr.total_revenue) for attr in attribution_data
            if attr.confidence_score >= 0.8
        )
        
        medium_confidence_revenue = sum(
            float(attr.total_revenue) for attr in attribution_data
            if 0.5 <= attr.confidence_score < 0.8
        )
        
        low_confidence_revenue = sum(
            float(attr.total_revenue) for attr in attribution_data
            if attr.confidence_score < 0.5
        )
        
        return {
            'model_distribution': model_distribution,
            'revenue_by_confidence': {
                'high_confidence': high_confidence_revenue,
                'medium_confidence': medium_confidence_revenue,
                'low_confidence': low_confidence_revenue
            },
            'attribution_accuracy_score': sum(
                attr.confidence_score for attr in attribution_data
            ) / len(attribution_data)
        }
    
    async def _calculate_model_performance(
        self,
        model_results: List[RevenueAttribution]
    ) -> Dict[str, Any]:
        """Calculate performance metrics for an attribution model."""
        if not model_results:
            return {}
        
        avg_confidence = sum(attr.confidence_score for attr in model_results) / len(model_results)
        total_revenue = sum(float(attr.total_revenue) for attr in model_results)
        
        # Calculate touchpoint utilization
        total_touchpoints = sum(len(attr.touchpoints) for attr in model_results)
        avg_touchpoints_per_attribution = total_touchpoints / len(model_results)
        
        return {
            'avg_confidence': avg_confidence,
            'total_revenue': total_revenue,
            'avg_touchpoints_per_attribution': avg_touchpoints_per_attribution,
            'attribution_count': len(model_results)
        }
    
    async def _recommend_best_attribution_model(
        self,
        model_comparisons: Dict[str, Any]
    ) -> str:
        """Recommend the best attribution model based on performance metrics."""
        best_model = None
        best_score = 0
        
        for model, performance in model_comparisons.items():
            # Calculate composite score
            confidence_score = performance['avg_confidence']
            revenue_completeness = min(1.0, performance['total_attributed_revenue'] / 10000)  # Normalize
            
            composite_score = (confidence_score * 0.7) + (revenue_completeness * 0.3)
            
            if composite_score > best_score:
                best_score = composite_score
                best_model = model
        
        return best_model or "data_driven"
    
    async def _generate_comparison_summary(
        self,
        model_comparisons: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate a summary of model comparison results."""
        summary = {}
        
        # Find model with highest confidence
        highest_confidence_model = max(
            model_comparisons.keys(),
            key=lambda m: model_comparisons[m]['avg_confidence']
        )
        
        # Find model with most revenue attributed
        highest_revenue_model = max(
            model_comparisons.keys(),
            key=lambda m: model_comparisons[m]['total_attributed_revenue']
        )
        
        summary['highest_confidence'] = f"{highest_confidence_model} with {model_comparisons[highest_confidence_model]['avg_confidence']:.2%} confidence"
        summary['highest_revenue'] = f"{highest_revenue_model} attributed ${model_comparisons[highest_revenue_model]['total_attributed_revenue']:,.2f}"
        
        return summary
    
    async def _identify_high_performing_touchpoints(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Identify high-performing touchpoints."""
        # Filter touchpoints by date range
        relevant_touchpoints = [
            tp for tp in self.touchpoint_history
            if start_date <= tp.timestamp <= end_date
        ]
        
        # Sort by revenue value and conversion probability
        high_performers = sorted(
            relevant_touchpoints,
            key=lambda tp: float(tp.revenue_value) * tp.conversion_probability,
            reverse=True
        )[:10]  # Top 10
        
        return [
            {
                'platform': tp.platform,
                'interaction_type': tp.interaction_type,
                'revenue_value': float(tp.revenue_value),
                'conversion_probability': tp.conversion_probability,
                'performance_score': float(tp.revenue_value) * tp.conversion_probability
            }
            for tp in high_performers
        ]
    
    async def _analyze_conversion_patterns(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze conversion patterns in user journeys."""
        patterns = {
            'common_sequences': [],
            'optimal_journey_length': 0,
            'platform_switching': 0,
            'time_patterns': {}
        }
        
        # Analyze user journeys
        for user_id, journey in self.conversion_tracking.items():
            if journey['total_interactions'] >= 2:
                # Analyze platform switching
                user_touchpoints = [
                    tp for tp in self.touchpoint_history
                    if tp.user_id == user_id and start_date <= tp.timestamp <= end_date
                ]
                
                if len(user_touchpoints) > 1:
                    platforms = [tp.platform for tp in user_touchpoints]
                    unique_platforms = set(platforms)
                    
                    if len(unique_platforms) > 1:
                        patterns['platform_switching'] += 1
        
        # Calculate optimal journey length (simplified)
        if self.conversion_tracking:
            avg_interactions = sum(
                journey['total_interactions'] for journey in self.conversion_tracking.values()
            ) / len(self.conversion_tracking)
            patterns['optimal_journey_length'] = round(avg_interactions)
        
        return patterns
    
    async def _calculate_opportunity_scores(
        self,
        attribution_analysis: Dict[str, Any],
        conversion_patterns: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate opportunity scores for optimization."""
        opportunities = {}
        
        # Platform expansion opportunity
        platform_analysis = attribution_analysis.get('analysis', {})
        if len(platform_analysis) < 3:
            opportunities['platform_expansion'] = 0.8
        else:
            opportunities['platform_expansion'] = 0.3
        
        # Journey optimization opportunity
        optimal_length = conversion_patterns.get('optimal_journey_length', 3)
        if optimal_length < 2:
            opportunities['journey_optimization'] = 0.7
        else:
            opportunities['journey_optimization'] = 0.4
        
        # Cross-platform strategy opportunity
        platform_switching = conversion_patterns.get('platform_switching', 0)
        total_users = len(self.conversion_tracking)
        
        if total_users > 0:
            switching_rate = platform_switching / total_users
            if switching_rate < 0.3:
                opportunities['cross_platform_strategy'] = 0.9
            else:
                opportunities['cross_platform_strategy'] = 0.2
        else:
            opportunities['cross_platform_strategy'] = 0.5
        
        return opportunities
    
    async def _generate_attribution_recommendations(
        self,
        high_performing_touchpoints: List[Dict[str, Any]],
        conversion_patterns: Dict[str, Any],
        opportunity_scores: Dict[str, float]
    ) -> List[str]:
        """Generate actionable attribution recommendations."""
        recommendations = []
        
        # Platform recommendations
        if opportunity_scores.get('platform_expansion', 0) > 0.6:
            recommendations.append(
                "Expand to additional platforms to diversify revenue attribution sources"
            )
        
        # High-performing touchpoint recommendations
        if high_performing_touchpoints:
            top_platform = high_performing_touchpoints[0]['platform']
            top_interaction = high_performing_touchpoints[0]['interaction_type']
            recommendations.append(
                f"Focus on {top_interaction} interactions on {top_platform} for highest revenue impact"
            )
        
        # Journey optimization recommendations
        if opportunity_scores.get('journey_optimization', 0) > 0.5:
            recommendations.append(
                "Optimize user journey length to improve conversion attribution accuracy"
            )
        
        # Cross-platform strategy recommendations
        if opportunity_scores.get('cross_platform_strategy', 0) > 0.7:
            recommendations.append(
                "Implement cross-platform campaigns to increase multi-touchpoint conversions"
            )
        
        # Attribution model recommendations
        recommendations.append(
            "Consider using data-driven attribution for the most accurate revenue attribution"
        )
        
        return recommendations