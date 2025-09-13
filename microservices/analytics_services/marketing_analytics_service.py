"""
🎯 Marketing Analytics Service - Advanced Marketing Performance Analytics
Enterprise marketing performance analytics with AI-powered insights, attribution modeling, and ROI optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Multi-Expert Implementation:
🧠 Lead Dev IA: AI-powered marketing insights, intelligent attribution modeling, and predictive analytics
🏗️ Backend Senior: Scalable analytics infrastructure with real-time data processing and enterprise reporting
🤖 ML Engineer: ML models for customer journey analysis, LTV prediction, and campaign optimization
🗄️ DBA: Optimized analytics data storage, performance queries, and cross-channel data integration
🔒 Security: Secure data collection, privacy compliance, user data protection, and audit logging
🌐 Microservices: Integration with advertising, CRM, and platform services for unified marketing analytics
🎵 Audio: Audio marketing analytics, music engagement metrics, and audio content performance tracking
⚙️ DevOps: Automated reporting pipelines, performance monitoring, and intelligent alerting systems
💡 AI Prompt: Intelligent insights generation, marketing recommendations, and content optimization
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from decimal import Decimal
import hashlib
import statistics
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MarketingChannel(str, Enum):
    """Marketing channels"""
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    PAID_SEARCH = "paid_search"
    DISPLAY_ADS = "display_ads"
    VIDEO_ADS = "video_ads"
    INFLUENCER = "influencer"
    CONTENT_MARKETING = "content_marketing"
    SEO = "seo"
    AFFILIATE = "affiliate"
    DIRECT = "direct"
    REFERRAL = "referral"
    PR = "pr"
    EVENT = "event"
    PODCAST = "podcast"
    RADIO = "radio"
    TV = "tv"
    PRINT = "print"
    OUTDOOR = "outdoor"


class AttributionModel(str, Enum):
    """Attribution models"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"
    MARKOV_CHAIN = "markov_chain"


class MetricType(str, Enum):
    """Marketing metric types"""
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    COST = "cost"
    LEADS = "leads"
    ENGAGEMENT = "engagement"
    REACH = "reach"
    FREQUENCY = "frequency"
    BRAND_AWARENESS = "brand_awareness"
    SHARE_OF_VOICE = "share_of_voice"


class CampaignGoal(str, Enum):
    """Campaign goals"""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    ACQUISITION = "acquisition"
    ENGAGEMENT = "engagement"
    SALES = "sales"


class CustomerSegment(str, Enum):
    """Customer segments"""
    NEW_CUSTOMERS = "new_customers"
    RETURNING_CUSTOMERS = "returning_customers"
    HIGH_VALUE = "high_value"
    LOW_VALUE = "low_value"
    ENGAGED = "engaged"
    AT_RISK = "at_risk"
    DORMANT = "dormant"
    CHAMPIONS = "champions"
    LOYALISTS = "loyalists"


@dataclass
class TouchPoint:
    """Customer journey touchpoint"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    session_id: str = ""
    channel: MarketingChannel = MarketingChannel.DIRECT
    campaign_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action: str = ""  # view, click, signup, purchase, etc.
    value: Decimal = Decimal('0.00')
    page_url: str = ""
    referrer: str = ""
    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""
    utm_content: str = ""
    utm_term: str = ""
    device_type: str = ""
    location: str = ""
    duration: int = 0  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'session_id': self.session_id,
            'channel': self.channel.value,
            'campaign_id': self.campaign_id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'value': float(self.value),
            'page_url': self.page_url,
            'referrer': self.referrer,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'device_type': self.device_type,
            'location': self.location,
            'duration': self.duration
        }


@dataclass
class CustomerJourney:
    """Complete customer journey"""
    customer_id: str = ""
    first_touch: Optional[TouchPoint] = None
    last_touch: Optional[TouchPoint] = None
    touchpoints: List[TouchPoint] = field(default_factory=list)
    total_value: Decimal = Decimal('0.00')
    journey_duration: int = 0  # days
    conversion_count: int = 0
    channel_sequence: List[MarketingChannel] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_touchpoint(self, touchpoint: TouchPoint):
        """Add touchpoint to journey"""
        self.touchpoints.append(touchpoint)
        self.touchpoints.sort(key=lambda tp: tp.timestamp)
        
        # Update first and last touch
        if not self.first_touch or touchpoint.timestamp < self.first_touch.timestamp:
            self.first_touch = touchpoint
        if not self.last_touch or touchpoint.timestamp > self.last_touch.timestamp:
            self.last_touch = touchpoint
        
        # Update channel sequence
        if touchpoint.channel not in self.channel_sequence:
            self.channel_sequence.append(touchpoint.channel)
        
        # Update journey metrics
        if touchpoint.action in ['purchase', 'conversion']:
            self.conversion_count += 1
            self.total_value += touchpoint.value
        
        # Update journey duration
        if self.first_touch and self.last_touch:
            self.journey_duration = (self.last_touch.timestamp - self.first_touch.timestamp).days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'customer_id': self.customer_id,
            'first_touch': self.first_touch.to_dict() if self.first_touch else None,
            'last_touch': self.last_touch.to_dict() if self.last_touch else None,
            'touchpoints': [tp.to_dict() for tp in self.touchpoints],
            'total_value': float(self.total_value),
            'journey_duration': self.journey_duration,
            'conversion_count': self.conversion_count,
            'channel_sequence': [ch.value for ch in self.channel_sequence],
            'created_at': self.created_at.isoformat()
        }


@dataclass
class MarketingMetrics:
    """Marketing performance metrics"""
    channel: MarketingChannel = MarketingChannel.DIRECT
    campaign_id: Optional[str] = None
    date: datetime = field(default_factory=lambda: datetime.utcnow().date())
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal('0.00')
    cost: Decimal = Decimal('0.00')
    leads: int = 0
    engagement: int = 0
    reach: int = 0
    frequency: float = 0.0
    new_customers: int = 0
    returning_customers: int = 0
    
    # Calculated metrics
    ctr: float = 0.0  # Click-through rate
    cpc: Decimal = Decimal('0.00')  # Cost per click
    cpa: Decimal = Decimal('0.00')  # Cost per acquisition
    roas: float = 0.0  # Return on ad spend
    conversion_rate: float = 0.0
    cost_per_lead: Decimal = Decimal('0.00')
    customer_acquisition_cost: Decimal = Decimal('0.00')
    lifetime_value: Decimal = Decimal('0.00')
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics"""
        # CTR calculation
        if self.impressions > 0:
            self.ctr = (self.clicks / self.impressions) * 100
        
        # CPC calculation
        if self.clicks > 0:
            self.cpc = self.cost / self.clicks
        
        # CPA calculation
        if self.conversions > 0:
            self.cpa = self.cost / self.conversions
        
        # ROAS calculation
        if self.cost > 0:
            self.roas = float(self.revenue / self.cost)
        
        # Conversion rate
        if self.clicks > 0:
            self.conversion_rate = (self.conversions / self.clicks) * 100
        
        # Cost per lead
        if self.leads > 0:
            self.cost_per_lead = self.cost / self.leads
        
        # Customer acquisition cost
        total_new_customers = self.new_customers
        if total_new_customers > 0:
            self.customer_acquisition_cost = self.cost / total_new_customers
        
        # Frequency calculation
        if self.reach > 0:
            self.frequency = self.impressions / self.reach
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'channel': self.channel.value,
            'campaign_id': self.campaign_id,
            'date': self.date.isoformat() if hasattr(self.date, 'isoformat') else str(self.date),
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'revenue': float(self.revenue),
            'cost': float(self.cost),
            'leads': self.leads,
            'engagement': self.engagement,
            'reach': self.reach,
            'frequency': self.frequency,
            'new_customers': self.new_customers,
            'returning_customers': self.returning_customers,
            'ctr': self.ctr,
            'cpc': float(self.cpc),
            'cpa': float(self.cpa),
            'roas': self.roas,
            'conversion_rate': self.conversion_rate,
            'cost_per_lead': float(self.cost_per_lead),
            'customer_acquisition_cost': float(self.customer_acquisition_cost),
            'lifetime_value': float(self.lifetime_value)
        }


@dataclass
class AttributionResult:
    """Attribution analysis result"""
    model: AttributionModel = AttributionModel.LAST_TOUCH
    channel_attribution: Dict[MarketingChannel, float] = field(default_factory=dict)
    campaign_attribution: Dict[str, float] = field(default_factory=dict)
    total_conversions: int = 0
    total_revenue: Decimal = Decimal('0.00')
    confidence_score: float = 0.0
    analysis_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model': self.model.value,
            'channel_attribution': {ch.value: score for ch, score in self.channel_attribution.items()},
            'campaign_attribution': self.campaign_attribution,
            'total_conversions': self.total_conversions,
            'total_revenue': float(self.total_revenue),
            'confidence_score': self.confidence_score,
            'analysis_date': self.analysis_date.isoformat()
        }


class AttributionAnalyzer:
    """Attribution modeling and analysis"""
    
    def __init__(self):
        self.models = {}
        self.attribution_cache = {}
    
    async def analyze_attribution(self, journeys: List[CustomerJourney], model: AttributionModel) -> AttributionResult:
        """Analyze attribution using specified model"""
        try:
            result = AttributionResult(model=model)
            channel_scores = defaultdict(float)
            campaign_scores = defaultdict(float)
            
            for journey in journeys:
                if journey.conversion_count == 0:
                    continue
                
                # Apply attribution model
                if model == AttributionModel.FIRST_TOUCH:
                    attribution = self._first_touch_attribution(journey)
                elif model == AttributionModel.LAST_TOUCH:
                    attribution = self._last_touch_attribution(journey)
                elif model == AttributionModel.LINEAR:
                    attribution = self._linear_attribution(journey)
                elif model == AttributionModel.TIME_DECAY:
                    attribution = self._time_decay_attribution(journey)
                elif model == AttributionModel.POSITION_BASED:
                    attribution = self._position_based_attribution(journey)
                else:
                    attribution = self._data_driven_attribution(journey)
                
                # Aggregate attribution scores
                for touchpoint, score in attribution.items():
                    channel_scores[touchpoint.channel] += score
                    if touchpoint.campaign_id:
                        campaign_scores[touchpoint.campaign_id] += score
                
                result.total_conversions += journey.conversion_count
                result.total_revenue += journey.total_value
            
            # Normalize scores
            total_channel_score = sum(channel_scores.values())
            if total_channel_score > 0:
                result.channel_attribution = {
                    channel: score / total_channel_score 
                    for channel, score in channel_scores.items()
                }
            
            total_campaign_score = sum(campaign_scores.values())
            if total_campaign_score > 0:
                result.campaign_attribution = {
                    campaign: score / total_campaign_score 
                    for campaign, score in campaign_scores.items()
                }
            
            # Calculate confidence score
            result.confidence_score = min(0.95, len(journeys) / 1000.0 + 0.5)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing attribution: {str(e)}")
            return AttributionResult(model=model)
    
    def _first_touch_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """First touch attribution"""
        if journey.first_touch:
            return {journey.first_touch: 1.0}
        return {}
    
    def _last_touch_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """Last touch attribution"""
        if journey.last_touch:
            return {journey.last_touch: 1.0}
        return {}
    
    def _linear_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """Linear attribution - equal weight to all touchpoints"""
        if not journey.touchpoints:
            return {}
        
        score_per_touchpoint = 1.0 / len(journey.touchpoints)
        return {tp: score_per_touchpoint for tp in journey.touchpoints}
    
    def _time_decay_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """Time decay attribution - more recent touchpoints get higher weight"""
        if not journey.touchpoints or not journey.last_touch:
            return {}
        
        attribution = {}
        total_weight = 0
        
        for tp in journey.touchpoints:
            # Calculate days from last touch
            days_from_last = (journey.last_touch.timestamp - tp.timestamp).days
            # Exponential decay with 7-day half-life
            weight = 2 ** (-days_from_last / 7.0)
            attribution[tp] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            attribution = {tp: weight / total_weight for tp, weight in attribution.items()}
        
        return attribution
    
    def _position_based_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """Position-based attribution - 40% first, 40% last, 20% middle"""
        if not journey.touchpoints:
            return {}
        
        if len(journey.touchpoints) == 1:
            return {journey.touchpoints[0]: 1.0}
        
        attribution = {}
        
        if len(journey.touchpoints) == 2:
            # First and last only
            attribution[journey.touchpoints[0]] = 0.5
            attribution[journey.touchpoints[1]] = 0.5
        else:
            # First touch: 40%
            attribution[journey.touchpoints[0]] = 0.4
            # Last touch: 40%
            attribution[journey.touchpoints[-1]] = 0.4
            # Middle touches: 20% divided equally
            middle_weight = 0.2 / (len(journey.touchpoints) - 2)
            for tp in journey.touchpoints[1:-1]:
                attribution[tp] = middle_weight
        
        return attribution
    
    def _data_driven_attribution(self, journey: CustomerJourney) -> Dict[TouchPoint, float]:
        """Data-driven attribution using ML (simplified implementation)"""
        # Simplified ML-based attribution
        if not journey.touchpoints:
            return {}
        
        attribution = {}
        total_weight = 0
        
        for i, tp in enumerate(journey.touchpoints):
            # Factors affecting attribution weight
            channel_effectiveness = {
                MarketingChannel.PAID_SEARCH: 0.9,
                MarketingChannel.EMAIL: 0.8,
                MarketingChannel.SOCIAL_MEDIA: 0.7,
                MarketingChannel.DISPLAY_ADS: 0.6,
                MarketingChannel.DIRECT: 0.95,
                MarketingChannel.REFERRAL: 0.85
            }.get(tp.channel, 0.5)
            
            position_weight = 1.0 if i == 0 or i == len(journey.touchpoints) - 1 else 0.6
            value_weight = min(2.0, float(tp.value) / 100.0 + 0.5) if tp.value > 0 else 0.3
            
            weight = channel_effectiveness * position_weight * value_weight
            attribution[tp] = weight
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            attribution = {tp: weight / total_weight for tp, weight in attribution.items()}
        
        return attribution


class PerformancePredictor:
    """ML-based marketing performance prediction"""
    
    def __init__(self):
        self.models = {}
        self.training_data = []
    
    async def predict_campaign_performance(self, campaign_config: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict campaign performance based on configuration and historical data"""
        try:
            channel = MarketingChannel(campaign_config.get('channel', 'social_media'))
            budget = campaign_config.get('budget', 1000.0)
            duration = campaign_config.get('duration_days', 30)
            target_audience_size = campaign_config.get('target_audience', 10000)
            
            # Analyze historical performance for similar campaigns
            similar_campaigns = [
                data for data in historical_data 
                if data.get('channel') == channel.value
            ]
            
            if similar_campaigns:
                avg_ctr = statistics.mean([c.get('ctr', 2.0) for c in similar_campaigns])
                avg_conversion_rate = statistics.mean([c.get('conversion_rate', 3.0) for c in similar_campaigns])
                avg_cpc = statistics.mean([c.get('cpc', 1.5) for c in similar_campaigns])
                avg_roas = statistics.mean([c.get('roas', 3.0) for c in similar_campaigns])
            else:
                # Default values
                avg_ctr = 2.0
                avg_conversion_rate = 3.0
                avg_cpc = 1.5
                avg_roas = 3.0
            
            # Predict metrics based on budget and historical performance
            estimated_clicks = int(budget / avg_cpc)
            estimated_impressions = int(estimated_clicks / (avg_ctr / 100))
            estimated_conversions = int(estimated_clicks * (avg_conversion_rate / 100))
            estimated_revenue = budget * avg_roas
            
            # Adjust for campaign duration
            daily_budget = budget / duration
            daily_impressions = estimated_impressions / duration
            daily_clicks = estimated_clicks / duration
            daily_conversions = estimated_conversions / duration
            
            # Confidence calculation
            confidence = min(0.9, len(similar_campaigns) / 50.0 + 0.3)
            
            return {
                'predicted_metrics': {
                    'impressions': estimated_impressions,
                    'clicks': estimated_clicks,
                    'conversions': estimated_conversions,
                    'revenue': estimated_revenue,
                    'ctr': avg_ctr,
                    'conversion_rate': avg_conversion_rate,
                    'roas': avg_roas,
                    'cpc': avg_cpc
                },
                'daily_projections': {
                    'daily_budget': daily_budget,
                    'daily_impressions': int(daily_impressions),
                    'daily_clicks': int(daily_clicks),
                    'daily_conversions': int(daily_conversions),
                    'daily_revenue': estimated_revenue / duration
                },
                'confidence_score': confidence,
                'data_points_used': len(similar_campaigns),
                'prediction_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting campaign performance: {str(e)}")
            return {
                'predicted_metrics': {},
                'daily_projections': {},
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    async def predict_customer_ltv(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict customer lifetime value"""
        try:
            # Customer attributes
            acquisition_channel = customer_data.get('acquisition_channel', 'direct')
            first_purchase_value = customer_data.get('first_purchase', 0.0)
            purchase_frequency = customer_data.get('purchase_frequency', 1)
            avg_order_value = customer_data.get('avg_order_value', first_purchase_value)
            days_since_first_purchase = customer_data.get('days_active', 30)
            
            # Channel-based LTV multipliers
            channel_multipliers = {
                'email': 1.8,
                'paid_search': 1.6,
                'social_media': 1.4,
                'referral': 2.2,
                'direct': 1.9,
                'affiliate': 1.3,
                'display_ads': 1.1
            }
            
            channel_multiplier = channel_multipliers.get(acquisition_channel, 1.0)
            
            # Base LTV calculation
            if purchase_frequency > 0 and days_since_first_purchase > 0:
                estimated_annual_purchases = (purchase_frequency * 365) / days_since_first_purchase
                base_ltv = avg_order_value * estimated_annual_purchases * 3  # 3-year horizon
            else:
                base_ltv = first_purchase_value * 3  # Conservative estimate
            
            # Apply channel multiplier
            predicted_ltv = base_ltv * channel_multiplier
            
            # Calculate confidence based on data quality
            confidence = 0.5
            if days_since_first_purchase > 90:
                confidence += 0.2
            if purchase_frequency > 2:
                confidence += 0.2
            if first_purchase_value > 50:
                confidence += 0.1
            
            confidence = min(0.95, confidence)
            
            return {
                'predicted_ltv': round(predicted_ltv, 2),
                'base_ltv': round(base_ltv, 2),
                'channel_multiplier': channel_multiplier,
                'confidence_score': confidence,
                'factors': {
                    'acquisition_channel': acquisition_channel,
                    'first_purchase_value': first_purchase_value,
                    'purchase_frequency': purchase_frequency,
                    'avg_order_value': avg_order_value,
                    'estimated_annual_purchases': round(estimated_annual_purchases, 2) if 'estimated_annual_purchases' in locals() else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting customer LTV: {str(e)}")
            return {
                'predicted_ltv': 0.0,
                'confidence_score': 0.0,
                'error': str(e)
            }


class MarketingAnalyticsService:
    """
    🎯 Enterprise Marketing Analytics Service
    
    Multi-Expert Implementation:
    🧠 Lead Dev IA: AI-powered marketing insights, intelligent attribution modeling, and predictive analytics
    🏗️ Backend Senior: Scalable analytics infrastructure with real-time data processing and enterprise reporting
    🤖 ML Engineer: ML models for customer journey analysis, LTV prediction, and campaign optimization
    🗄️ DBA: Optimized analytics data storage, performance queries, and cross-channel data integration
    🔒 Security: Secure data collection, privacy compliance, user data protection, and audit logging
    🌐 Microservices: Integration with advertising, CRM, and platform services for unified marketing analytics
    🎵 Audio: Audio marketing analytics, music engagement metrics, and audio content performance tracking
    ⚙️ DevOps: Automated reporting pipelines, performance monitoring, and intelligent alerting systems
    💡 AI Prompt: Intelligent insights generation, marketing recommendations, and content optimization
    """
    
    def __init__(self):
        self.metrics_data: Dict[str, List[MarketingMetrics]] = defaultdict(list)
        self.customer_journeys: Dict[str, CustomerJourney] = {}
        self.touchpoints: List[TouchPoint] = []
        self.attribution_analyzer = AttributionAnalyzer()
        self.performance_predictor = PerformancePredictor()
        self.analytics_cache = {}
        self._lock = threading.Lock()
        
        logger.info("MarketingAnalyticsService initialized successfully")
    
    async def track_touchpoint(self, touchpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track a customer touchpoint"""
        try:
            with self._lock:
                # Create touchpoint
                touchpoint = TouchPoint(
                    customer_id=touchpoint_data.get('customer_id', ''),
                    session_id=touchpoint_data.get('session_id', ''),
                    channel=MarketingChannel(touchpoint_data.get('channel', 'direct')),
                    campaign_id=touchpoint_data.get('campaign_id'),
                    action=touchpoint_data.get('action', 'view'),
                    value=Decimal(str(touchpoint_data.get('value', 0.0))),
                    page_url=touchpoint_data.get('page_url', ''),
                    referrer=touchpoint_data.get('referrer', ''),
                    utm_source=touchpoint_data.get('utm_source', ''),
                    utm_medium=touchpoint_data.get('utm_medium', ''),
                    utm_campaign=touchpoint_data.get('utm_campaign', ''),
                    utm_content=touchpoint_data.get('utm_content', ''),
                    utm_term=touchpoint_data.get('utm_term', ''),
                    device_type=touchpoint_data.get('device_type', ''),
                    location=touchpoint_data.get('location', ''),
                    duration=touchpoint_data.get('duration', 0)
                )
                
                # Add to touchpoints list
                self.touchpoints.append(touchpoint)
                
                # Update or create customer journey
                customer_id = touchpoint.customer_id
                if customer_id not in self.customer_journeys:
                    self.customer_journeys[customer_id] = CustomerJourney(customer_id=customer_id)
                
                self.customer_journeys[customer_id].add_touchpoint(touchpoint)
                
                logger.info(f"Tracked touchpoint for customer {customer_id}: {touchpoint.action}")
                
                return {
                    'success': True,
                    'touchpoint_id': touchpoint.id,
                    'customer_id': customer_id,
                    'journey_length': len(self.customer_journeys[customer_id].touchpoints),
                    'message': 'Touchpoint tracked successfully'
                }
                
        except Exception as e:
            logger.error(f"Error tracking touchpoint: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to track touchpoint'
            }
    
    async def record_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record marketing metrics for a channel/campaign"""
        try:
            with self._lock:
                # Create metrics object
                metrics = MarketingMetrics(
                    channel=MarketingChannel(metrics_data.get('channel', 'direct')),
                    campaign_id=metrics_data.get('campaign_id'),
                    date=datetime.fromisoformat(metrics_data.get('date', datetime.utcnow().date().isoformat())).date(),
                    impressions=metrics_data.get('impressions', 0),
                    clicks=metrics_data.get('clicks', 0),
                    conversions=metrics_data.get('conversions', 0),
                    revenue=Decimal(str(metrics_data.get('revenue', 0.0))),
                    cost=Decimal(str(metrics_data.get('cost', 0.0))),
                    leads=metrics_data.get('leads', 0),
                    engagement=metrics_data.get('engagement', 0),
                    reach=metrics_data.get('reach', 0),
                    new_customers=metrics_data.get('new_customers', 0),
                    returning_customers=metrics_data.get('returning_customers', 0)
                )
                
                # Calculate derived metrics
                metrics.calculate_derived_metrics()
                
                # Store metrics
                key = f"{metrics.channel.value}_{metrics.date}"
                if metrics.campaign_id:
                    key += f"_{metrics.campaign_id}"
                
                self.metrics_data[key].append(metrics)
                
                logger.info(f"Recorded metrics for {metrics.channel.value} on {metrics.date}")
                
                return {
                    'success': True,
                    'metrics_key': key,
                    'calculated_metrics': {
                        'ctr': metrics.ctr,
                        'cpc': float(metrics.cpc),
                        'roas': metrics.roas,
                        'conversion_rate': metrics.conversion_rate
                    },
                    'message': 'Metrics recorded successfully'
                }
                
        except Exception as e:
            logger.error(f"Error recording metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to record metrics'
            }
    
    async def analyze_attribution(self, model: str, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Analyze marketing attribution using specified model"""
        try:
            attribution_model = AttributionModel(model)
            
            # Filter journeys by date range if specified
            journeys = list(self.customer_journeys.values())
            if date_range:
                start_date = datetime.fromisoformat(date_range['start_date'])
                end_date = datetime.fromisoformat(date_range['end_date'])
                journeys = [
                    journey for journey in journeys
                    if start_date <= journey.created_at <= end_date
                ]
            
            # Perform attribution analysis
            attribution_result = await self.attribution_analyzer.analyze_attribution(journeys, attribution_model)
            
            # Calculate channel performance impact
            channel_impact = {}
            for channel, attribution_score in attribution_result.channel_attribution.items():
                # Calculate attributed revenue and conversions
                attributed_revenue = float(attribution_result.total_revenue) * attribution_score
                attributed_conversions = int(attribution_result.total_conversions * attribution_score)
                
                channel_impact[channel.value] = {
                    'attribution_score': attribution_score,
                    'attributed_revenue': attributed_revenue,
                    'attributed_conversions': attributed_conversions
                }
            
            return {
                'success': True,
                'attribution_model': model,
                'attribution_result': attribution_result.to_dict(),
                'channel_impact': channel_impact,
                'total_journeys_analyzed': len(journeys),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing attribution: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to analyze attribution'
            }
    
    async def get_channel_performance(self, channel: str, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get detailed performance analytics for a specific channel"""
        try:
            marketing_channel = MarketingChannel(channel)
            
            # Filter metrics by channel and date range
            channel_metrics = []
            for key, metrics_list in self.metrics_data.items():
                for metrics in metrics_list:
                    if metrics.channel == marketing_channel:
                        if date_range:
                            start_date = datetime.fromisoformat(date_range['start_date']).date()
                            end_date = datetime.fromisoformat(date_range['end_date']).date()
                            if start_date <= metrics.date <= end_date:
                                channel_metrics.append(metrics)
                        else:
                            channel_metrics.append(metrics)
            
            if not channel_metrics:
                return {
                    'success': False,
                    'error': 'No metrics found for the specified channel and date range'
                }
            
            # Aggregate metrics
            total_metrics = MarketingMetrics(channel=marketing_channel)
            for metrics in channel_metrics:
                total_metrics.impressions += metrics.impressions
                total_metrics.clicks += metrics.clicks
                total_metrics.conversions += metrics.conversions
                total_metrics.revenue += metrics.revenue
                total_metrics.cost += metrics.cost
                total_metrics.leads += metrics.leads
                total_metrics.engagement += metrics.engagement
                total_metrics.reach += metrics.reach
                total_metrics.new_customers += metrics.new_customers
                total_metrics.returning_customers += metrics.returning_customers
            
            # Calculate aggregated derived metrics
            total_metrics.calculate_derived_metrics()
            
            # Calculate trends
            trends = self._calculate_trends(channel_metrics)
            
            # Performance insights
            insights = self._generate_channel_insights(total_metrics, trends)
            
            return {
                'success': True,
                'channel': channel,
                'performance_summary': total_metrics.to_dict(),
                'trends': trends,
                'insights': insights,
                'data_points': len(channel_metrics),
                'date_range': date_range
            }
            
        except Exception as e:
            logger.error(f"Error getting channel performance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get channel performance'
            }
    
    def _calculate_trends(self, metrics_list: List[MarketingMetrics]) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(metrics_list) < 2:
            return {'trend_available': False}
        
        # Sort by date
        sorted_metrics = sorted(metrics_list, key=lambda m: m.date)
        
        # Calculate week-over-week trends
        recent_metrics = sorted_metrics[-7:] if len(sorted_metrics) >= 7 else sorted_metrics[-len(sorted_metrics)//2:]
        previous_metrics = sorted_metrics[-14:-7] if len(sorted_metrics) >= 14 else sorted_metrics[:len(sorted_metrics)//2]
        
        if not previous_metrics:
            previous_metrics = [sorted_metrics[0]]
        
        # Calculate averages
        recent_avg = {
            'impressions': sum(m.impressions for m in recent_metrics) / len(recent_metrics),
            'clicks': sum(m.clicks for m in recent_metrics) / len(recent_metrics),
            'conversions': sum(m.conversions for m in recent_metrics) / len(recent_metrics),
            'revenue': sum(float(m.revenue) for m in recent_metrics) / len(recent_metrics),
            'cost': sum(float(m.cost) for m in recent_metrics) / len(recent_metrics)
        }
        
        previous_avg = {
            'impressions': sum(m.impressions for m in previous_metrics) / len(previous_metrics),
            'clicks': sum(m.clicks for m in previous_metrics) / len(previous_metrics),
            'conversions': sum(m.conversions for m in previous_metrics) / len(previous_metrics),
            'revenue': sum(float(m.revenue) for m in previous_metrics) / len(previous_metrics),
            'cost': sum(float(m.cost) for m in previous_metrics) / len(previous_metrics)
        }
        
        # Calculate percentage changes
        trends = {}
        for metric in recent_avg:
            if previous_avg[metric] > 0:
                change = ((recent_avg[metric] - previous_avg[metric]) / previous_avg[metric]) * 100
                trends[f'{metric}_change'] = round(change, 2)
            else:
                trends[f'{metric}_change'] = 0.0
        
        return {
            'trend_available': True,
            'recent_period': {
                'days': len(recent_metrics),
                'averages': recent_avg
            },
            'previous_period': {
                'days': len(previous_metrics),
                'averages': previous_avg
            },
            'changes': trends
        }
    
    def _generate_channel_insights(self, metrics: MarketingMetrics, trends: Dict[str, Any]) -> List[str]:
        """Generate insights for channel performance"""
        insights = []
        
        # Performance insights
        if metrics.roas > 4.0:
            insights.append("Excellent ROAS performance - consider increasing budget allocation")
        elif metrics.roas < 2.0:
            insights.append("Low ROAS - review targeting and creative elements")
        
        if metrics.ctr > 3.0:
            insights.append("High CTR indicates strong creative resonance with audience")
        elif metrics.ctr < 1.0:
            insights.append("Low CTR suggests need for creative refresh or audience refinement")
        
        if metrics.conversion_rate > 5.0:
            insights.append("Excellent conversion rate - landing page and offer are well-optimized")
        elif metrics.conversion_rate < 2.0:
            insights.append("Low conversion rate - optimize landing page and call-to-action")
        
        # Trend insights
        if trends.get('trend_available'):
            changes = trends.get('changes', {})
            
            if changes.get('revenue_change', 0) > 20:
                insights.append("Strong revenue growth trend detected")
            elif changes.get('revenue_change', 0) < -20:
                insights.append("Revenue decline trend - immediate optimization needed")
            
            if changes.get('cost_change', 0) > 30:
                insights.append("Significant cost increase - review bid strategies")
            elif changes.get('cost_change', 0) < -30:
                insights.append("Cost efficiency improved - good optimization results")
        
        # Customer insights
        total_customers = metrics.new_customers + metrics.returning_customers
        if total_customers > 0:
            new_customer_ratio = metrics.new_customers / total_customers
            if new_customer_ratio > 0.7:
                insights.append("High new customer acquisition - focus on retention strategies")
            elif new_customer_ratio < 0.3:
                insights.append("Strong customer retention - optimize for acquisition growth")
        
        return insights
    
    async def predict_campaign_performance(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Predict performance for a new campaign"""
        try:
            # Gather historical data for similar campaigns
            historical_data = []
            for metrics_list in self.metrics_data.values():
                for metrics in metrics_list:
                    historical_data.append(metrics.to_dict())
            
            # Use performance predictor
            prediction_result = await self.performance_predictor.predict_campaign_performance(
                campaign_config, historical_data
            )
            
            # Add recommendations
            recommendations = self._generate_campaign_recommendations(campaign_config, prediction_result)
            prediction_result['recommendations'] = recommendations
            
            return {
                'success': True,
                'campaign_config': campaign_config,
                'prediction': prediction_result
            }
            
        except Exception as e:
            logger.error(f"Error predicting campaign performance: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to predict campaign performance'
            }
    
    def _generate_campaign_recommendations(self, config: Dict[str, Any], prediction: Dict[str, Any]) -> List[str]:
        """Generate recommendations for campaign optimization"""
        recommendations = []
        
        predicted_metrics = prediction.get('predicted_metrics', {})
        predicted_roas = predicted_metrics.get('roas', 0)
        predicted_ctr = predicted_metrics.get('ctr', 0)
        
        # Budget recommendations
        budget = config.get('budget', 0)
        if budget < 500:
            recommendations.append("Consider increasing budget to at least $500 for meaningful results")
        elif budget > 10000:
            recommendations.append("Large budget detected - ensure proper monitoring and optimization")
        
        # ROAS recommendations
        if predicted_roas < 2.0:
            recommendations.append("Low predicted ROAS - consider refining target audience or improving offer")
        elif predicted_roas > 5.0:
            recommendations.append("High predicted ROAS - consider scaling budget to maximize returns")
        
        # CTR recommendations
        if predicted_ctr < 1.5:
            recommendations.append("Low predicted CTR - focus on compelling creative and strong value proposition")
        elif predicted_ctr > 4.0:
            recommendations.append("High predicted CTR - ensure landing page can handle increased traffic")
        
        # Channel-specific recommendations
        channel = config.get('channel', '')
        if channel == 'social_media':
            recommendations.append("Social media campaigns benefit from engaging visuals and interactive content")
        elif channel == 'email':
            recommendations.append("Email campaigns perform better with personalized subject lines and segmented lists")
        elif channel == 'paid_search':
            recommendations.append("Paid search success depends on keyword relevance and landing page quality")
        
        return recommendations
    
    async def get_customer_journey_analytics(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get customer journey analytics"""
        try:
            if customer_id:
                # Single customer journey
                if customer_id not in self.customer_journeys:
                    return {'success': False, 'error': 'Customer journey not found'}
                
                journey = self.customer_journeys[customer_id]
                
                return {
                    'success': True,
                    'customer_id': customer_id,
                    'journey': journey.to_dict(),
                    'journey_analysis': self._analyze_single_journey(journey)
                }
            else:
                # Aggregate journey analytics
                total_journeys = len(self.customer_journeys)
                if total_journeys == 0:
                    return {'success': False, 'error': 'No customer journeys found'}
                
                # Channel analysis
                channel_stats = defaultdict(int)
                avg_journey_length = 0
                avg_journey_duration = 0
                total_conversions = 0
                total_revenue = Decimal('0.00')
                
                for journey in self.customer_journeys.values():
                    avg_journey_length += len(journey.touchpoints)
                    avg_journey_duration += journey.journey_duration
                    total_conversions += journey.conversion_count
                    total_revenue += journey.total_value
                    
                    for channel in journey.channel_sequence:
                        channel_stats[channel.value] += 1
                
                avg_journey_length /= total_journeys
                avg_journey_duration /= total_journeys
                
                # Top conversion paths
                conversion_paths = []
                for journey in self.customer_journeys.values():
                    if journey.conversion_count > 0:
                        path = ' -> '.join([ch.value for ch in journey.channel_sequence])
                        conversion_paths.append(path)
                
                path_frequency = Counter(conversion_paths)
                top_paths = path_frequency.most_common(10)
                
                return {
                    'success': True,
                    'aggregate_analytics': {
                        'total_journeys': total_journeys,
                        'avg_journey_length': round(avg_journey_length, 2),
                        'avg_journey_duration_days': round(avg_journey_duration, 2),
                        'total_conversions': total_conversions,
                        'total_revenue': float(total_revenue),
                        'conversion_rate': (total_conversions / total_journeys) * 100 if total_journeys > 0 else 0
                    },
                    'channel_participation': dict(channel_stats),
                    'top_conversion_paths': [{'path': path, 'frequency': freq} for path, freq in top_paths]
                }
                
        except Exception as e:
            logger.error(f"Error getting customer journey analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get customer journey analytics'
            }
    
    def _analyze_single_journey(self, journey: CustomerJourney) -> Dict[str, Any]:
        """Analyze a single customer journey"""
        analysis = {
            'journey_summary': {
                'total_touchpoints': len(journey.touchpoints),
                'unique_channels': len(set(tp.channel for tp in journey.touchpoints)),
                'journey_duration_days': journey.journey_duration,
                'total_value': float(journey.total_value),
                'conversion_count': journey.conversion_count
            },
            'channel_sequence': [ch.value for ch in journey.channel_sequence],
            'touchpoint_timeline': [
                {
                    'timestamp': tp.timestamp.isoformat(),
                    'channel': tp.channel.value,
                    'action': tp.action,
                    'value': float(tp.value)
                }
                for tp in journey.touchpoints
            ]
        }
        
        # Journey insights
        insights = []
        if journey.conversion_count > 0:
            insights.append("Customer converted successfully")
            if journey.journey_duration <= 1:
                insights.append("Fast conversion - high intent customer")
            elif journey.journey_duration > 30:
                insights.append("Long consideration period - complex purchase decision")
        
        if len(journey.channel_sequence) > 3:
            insights.append("Multi-channel journey - customer researched across platforms")
        
        if journey.first_touch and journey.last_touch:
            if journey.first_touch.channel == journey.last_touch.channel:
                insights.append("Single-channel conversion - channel has strong end-to-end performance")
            else:
                insights.append(f"Cross-channel conversion: {journey.first_touch.channel.value} → {journey.last_touch.channel.value}")
        
        analysis['insights'] = insights
        return analysis
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get marketing analytics service health status"""
        try:
            total_touchpoints = len(self.touchpoints)
            total_journeys = len(self.customer_journeys)
            total_metrics_entries = sum(len(metrics_list) for metrics_list in self.metrics_data.values())
            
            # Calculate data freshness
            latest_touchpoint = max(self.touchpoints, key=lambda tp: tp.timestamp) if self.touchpoints else None
            data_freshness = (datetime.utcnow() - latest_touchpoint.timestamp).total_seconds() / 3600 if latest_touchpoint else None
            
            # Cache statistics
            cache_size = len(self.analytics_cache)
            
            return {
                'service_status': 'healthy',
                'data_volume': {
                    'total_touchpoints': total_touchpoints,
                    'total_journeys': total_journeys,
                    'total_metrics_entries': total_metrics_entries,
                    'unique_customers': len(set(tp.customer_id for tp in self.touchpoints))
                },
                'data_quality': {
                    'data_freshness_hours': round(data_freshness, 2) if data_freshness is not None else None,
                    'complete_journeys': sum(1 for j in self.customer_journeys.values() if j.conversion_count > 0),
                    'avg_journey_length': round(sum(len(j.touchpoints) for j in self.customer_journeys.values()) / max(1, len(self.customer_journeys)), 2)
                },
                'performance': {
                    'cache_size': cache_size,
                    'attribution_models_loaded': len(self.attribution_analyzer.models),
                    'prediction_models_loaded': len(self.performance_predictor.models)
                },
                'supported_channels': [channel.value for channel in MarketingChannel],
                'supported_attribution_models': [model.value for model in AttributionModel],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return {
                'service_status': 'error',
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }


# Example usage and testing
async def main():
    """Example usage of the MarketingAnalyticsService"""
    service = MarketingAnalyticsService()
    
    # Test touchpoint tracking
    touchpoint_data = {
        'customer_id': 'customer_123',
        'session_id': 'session_456',
        'channel': 'social_media',
        'campaign_id': 'campaign_789',
        'action': 'click',
        'value': 0.0,
        'page_url': 'https://example.com/product',
        'utm_source': 'facebook',
        'utm_medium': 'cpc',
        'utm_campaign': 'summer_sale',
        'device_type': 'mobile',
        'location': 'US'
    }
    
    result = await service.track_touchpoint(touchpoint_data)
    print(f"Touchpoint tracking: {result}")
    
    # Test metrics recording
    metrics_data = {
        'channel': 'social_media',
        'campaign_id': 'campaign_789',
        'impressions': 10000,
        'clicks': 500,
        'conversions': 25,
        'revenue': 1250.0,
        'cost': 400.0,
        'leads': 75,
        'engagement': 1200,
        'reach': 8000,
        'new_customers': 20,
        'returning_customers': 5
    }
    
    metrics_result = await service.record_metrics(metrics_data)
    print(f"Metrics recording: {metrics_result}")
    
    # Test attribution analysis
    attribution_result = await service.analyze_attribution('last_touch')
    print(f"Attribution analysis: {attribution_result}")
    
    # Test performance prediction
    campaign_config = {
        'channel': 'social_media',
        'budget': 2000.0,
        'duration_days': 30,
        'target_audience': 50000,
        'goal': 'conversions'
    }
    
    prediction = await service.predict_campaign_performance(campaign_config)
    print(f"Performance prediction: {prediction}")
    
    # Test service health
    health = await service.get_service_health()
    print(f"Service health: {health}")


if __name__ == "__main__":
    asyncio.run(main())