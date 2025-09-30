"""SEO Conversion Tracking - Advanced Conversion Attribution for SEO
Tracks and analyzes conversions from organic search traffic with advanced attribution models.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import aiohttp
from decimal import Decimal

logger = logging.getLogger(__name__)


class ConversionType(Enum):
    """Conversion types for SEO tracking"""
    PURCHASE = "purchase"
    SIGNUP = "signup"
    SUBSCRIPTION = "subscription"
    DOWNLOAD = "download"
    CONTACT = "contact"
    VIDEO_VIEW = "video_view"
    CONTENT_ENGAGEMENT = "content_engagement"
    CREATOR_FOLLOW = "creator_follow"


class AttributionModel(Enum):
    """Attribution models for conversion tracking"""
    FIRST_CLICK = "first_click"
    LAST_CLICK = "last_click"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


@dataclass
class ConversionEvent:
    """Individual conversion event"""
    event_id: str
    user_id: str
    session_id: str
    conversion_type: ConversionType
    value: Decimal
    timestamp: datetime
    source_url: str
    landing_page: str
    search_query: Optional[str] = None
    organic_keywords: List[str] = field(default_factory=list)
    referrer: Optional[str] = None
    user_agent: str = ""
    ip_address: str = ""
    campaign_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionPath:
    """User conversion path tracking"""
    user_id: str
    path_id: str
    touchpoints: List[Dict[str, Any]] = field(default_factory=list)
    total_value: Decimal = Decimal('0')
    conversion_events: List[ConversionEvent] = field(default_factory=list)
    attribution_model: AttributionModel = AttributionModel.LAST_CLICK
    path_length: int = 0
    time_to_conversion: timedelta = timedelta()


@dataclass
class SEOConversionMetrics:
    """SEO conversion metrics"""
    total_conversions: int
    total_value: Decimal
    conversion_rate: float
    avg_order_value: Decimal
    revenue_per_visitor: Decimal
    organic_conversion_share: float
    top_converting_keywords: List[Tuple[str, int, Decimal]]
    top_converting_pages: List[Tuple[str, int, Decimal]]
    conversion_by_type: Dict[ConversionType, int]
    attribution_breakdown: Dict[AttributionModel, Decimal]


class SEOConversionTracker:
    """Advanced SEO conversion tracking and attribution system"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SEO conversion tracker
        
        Args:
            config: Configuration including database, analytics settings
        """
        self.config = config
        self.conversion_events: List[ConversionEvent] = []
        self.conversion_paths: Dict[str, ConversionPath] = {}
        self.attribution_weights = self._initialize_attribution_weights()
        
    def _initialize_attribution_weights(self) -> Dict[AttributionModel, Dict[str, float]]:
        """Initialize attribution model weights"""
        return {
            AttributionModel.FIRST_CLICK: {"first": 1.0},
            AttributionModel.LAST_CLICK: {"last": 1.0},
            AttributionModel.LINEAR: {"equal": 1.0},
            AttributionModel.TIME_DECAY: {"decay_factor": 0.7},
            AttributionModel.POSITION_BASED: {"first": 0.4, "last": 0.4, "middle": 0.2},
            AttributionModel.DATA_DRIVEN: {"ml_weights": True}
        }
    
    async def track_conversion(self, conversion_data: Dict[str, Any]) -> str:
        """Track a conversion event
        
        Args:
            conversion_data: Conversion event data
            
        Returns:
            Conversion event ID
        """
        try:
            conversion_event = ConversionEvent(
                event_id=conversion_data.get('event_id', self._generate_event_id()),
                user_id=conversion_data['user_id'],
                session_id=conversion_data['session_id'],
                conversion_type=ConversionType(conversion_data['conversion_type']),
                value=Decimal(str(conversion_data.get('value', 0))),
                timestamp=datetime.fromisoformat(conversion_data.get('timestamp', datetime.now().isoformat())),
                source_url=conversion_data.get('source_url', ''),
                landing_page=conversion_data.get('landing_page', ''),
                search_query=conversion_data.get('search_query'),
                organic_keywords=conversion_data.get('organic_keywords', []),
                referrer=conversion_data.get('referrer'),
                user_agent=conversion_data.get('user_agent', ''),
                ip_address=conversion_data.get('ip_address', ''),
                campaign_data=conversion_data.get('campaign_data', {})
            )
            
            self.conversion_events.append(conversion_event)
            await self._update_conversion_path(conversion_event)
            await self._store_conversion_event(conversion_event)
            
            logger.info(f"Tracked conversion: {conversion_event.event_id}")
            return conversion_event.event_id
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
            raise
    
    async def _update_conversion_path(self, conversion_event: ConversionEvent):
        """Update user conversion path"""
        try:
            user_id = conversion_event.user_id
            
            if user_id not in self.conversion_paths:
                self.conversion_paths[user_id] = ConversionPath(
                    user_id=user_id,
                    path_id=f"path_{user_id}_{datetime.now().timestamp()}"
                )
            
            path = self.conversion_paths[user_id]
            
            # Add touchpoint
            touchpoint = {
                'timestamp': conversion_event.timestamp,
                'source_url': conversion_event.source_url,
                'landing_page': conversion_event.landing_page,
                'search_query': conversion_event.search_query,
                'organic_keywords': conversion_event.organic_keywords,
                'conversion_type': conversion_event.conversion_type.value,
                'value': conversion_event.value
            }
            
            path.touchpoints.append(touchpoint)
            path.conversion_events.append(conversion_event)
            path.total_value += conversion_event.value
            path.path_length = len(path.touchpoints)
            
            if path.touchpoints:
                first_touch = path.touchpoints[0]['timestamp']
                last_touch = path.touchpoints[-1]['timestamp']
                path.time_to_conversion = last_touch - first_touch
                
        except Exception as e:
            logger.error(f"Error updating conversion path: {str(e)}")
    
    async def calculate_attribution(self, 
                                 user_id: str, 
                                 model: AttributionModel) -> Dict[str, Decimal]:
        """Calculate attribution for conversion path
        
        Args:
            user_id: User identifier
            model: Attribution model to use
            
        Returns:
            Attribution weights by touchpoint
        """
        try:
            if user_id not in self.conversion_paths:
                return {}
                
            path = self.conversion_paths[user_id]
            touchpoints = path.touchpoints
            
            if not touchpoints:
                return {}
            
            attribution = {}
            total_value = path.total_value
            
            if model == AttributionModel.FIRST_CLICK:
                if touchpoints:
                    attribution[touchpoints[0]['source_url']] = total_value
                    
            elif model == AttributionModel.LAST_CLICK:
                if touchpoints:
                    attribution[touchpoints[-1]['source_url']] = total_value
                    
            elif model == AttributionModel.LINEAR:
                weight_per_touch = total_value / len(touchpoints)
                for touchpoint in touchpoints:
                    url = touchpoint['source_url']
                    attribution[url] = attribution.get(url, Decimal('0')) + weight_per_touch
                    
            elif model == AttributionModel.TIME_DECAY:
                decay_factor = self.attribution_weights[model]['decay_factor']
                total_weight = sum(decay_factor ** i for i in range(len(touchpoints)))
                
                for i, touchpoint in enumerate(reversed(touchpoints)):
                    weight = (decay_factor ** i) / total_weight
                    url = touchpoint['source_url']
                    attribution[url] = attribution.get(url, Decimal('0')) + (total_value * Decimal(str(weight)))
                    
            elif model == AttributionModel.POSITION_BASED:
                if len(touchpoints) == 1:
                    attribution[touchpoints[0]['source_url']] = total_value
                elif len(touchpoints) == 2:
                    attribution[touchpoints[0]['source_url']] = total_value * Decimal('0.5')
                    attribution[touchpoints[1]['source_url']] = total_value * Decimal('0.5')
                else:
                    first_weight = Decimal('0.4')
                    last_weight = Decimal('0.4')
                    middle_weight = Decimal('0.2') / (len(touchpoints) - 2)
                    
                    attribution[touchpoints[0]['source_url']] = total_value * first_weight
                    attribution[touchpoints[-1]['source_url']] = total_value * last_weight
                    
                    for touchpoint in touchpoints[1:-1]:
                        url = touchpoint['source_url']
                        attribution[url] = attribution.get(url, Decimal('0')) + (total_value * middle_weight)
            
            return attribution
            
        except Exception as e:
            logger.error(f"Error calculating attribution: {str(e)}")
            return {}
    
    async def get_seo_conversion_metrics(self, 
                                       start_date: datetime,
                                       end_date: datetime) -> SEOConversionMetrics:
        """Get comprehensive SEO conversion metrics
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            SEO conversion metrics
        """
        try:
            # Filter events by date range
            filtered_events = [
                event for event in self.conversion_events
                if start_date <= event.timestamp <= end_date
            ]
            
            # Calculate basic metrics
            total_conversions = len(filtered_events)
            total_value = sum(event.value for event in filtered_events)
            
            # Get organic traffic data for conversion rate calculation
            organic_visitors = await self._get_organic_visitors(start_date, end_date)
            conversion_rate = (total_conversions / organic_visitors) * 100 if organic_visitors > 0 else 0
            
            # Calculate advanced metrics
            avg_order_value = total_value / total_conversions if total_conversions > 0 else Decimal('0')
            revenue_per_visitor = total_value / organic_visitors if organic_visitors > 0 else Decimal('0')
            
            # Get organic conversion share
            total_site_conversions = await self._get_total_site_conversions(start_date, end_date)
            organic_conversion_share = (total_conversions / total_site_conversions) * 100 if total_site_conversions > 0 else 0
            
            # Top converting keywords
            keyword_conversions = {}
            keyword_values = {}
            
            for event in filtered_events:
                for keyword in event.organic_keywords:
                    keyword_conversions[keyword] = keyword_conversions.get(keyword, 0) + 1
                    keyword_values[keyword] = keyword_values.get(keyword, Decimal('0')) + event.value
            
            top_converting_keywords = sorted(
                [(k, v, keyword_values[k]) for k, v in keyword_conversions.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Top converting pages
            page_conversions = {}
            page_values = {}
            
            for event in filtered_events:
                page = event.landing_page
                page_conversions[page] = page_conversions.get(page, 0) + 1
                page_values[page] = page_values.get(page, Decimal('0')) + event.value
            
            top_converting_pages = sorted(
                [(k, v, page_values[k]) for k, v in page_conversions.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Conversion by type
            conversion_by_type = {}
            for event in filtered_events:
                conv_type = event.conversion_type
                conversion_by_type[conv_type] = conversion_by_type.get(conv_type, 0) + 1
            
            # Attribution breakdown
            attribution_breakdown = {}
            for model in AttributionModel:
                model_value = Decimal('0')
                for user_id in self.conversion_paths:
                    attribution = await self.calculate_attribution(user_id, model)
                    model_value += sum(attribution.values())
                attribution_breakdown[model] = model_value
            
            return SEOConversionMetrics(
                total_conversions=total_conversions,
                total_value=total_value,
                conversion_rate=conversion_rate,
                avg_order_value=avg_order_value,
                revenue_per_visitor=revenue_per_visitor,
                organic_conversion_share=organic_conversion_share,
                top_converting_keywords=top_converting_keywords,
                top_converting_pages=top_converting_pages,
                conversion_by_type=conversion_by_type,
                attribution_breakdown=attribution_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error getting SEO conversion metrics: {str(e)}")
            raise
    
    async def _get_organic_visitors(self, start_date: datetime, end_date: datetime) -> int:
        """Get organic visitor count for period"""
        # This would integrate with analytics system
        # Placeholder implementation
        return 1000
    
    async def _get_total_site_conversions(self, start_date: datetime, end_date: datetime) -> int:
        """Get total site conversions for period"""
        # This would integrate with analytics system
        # Placeholder implementation
        return 150
    
    async def _store_conversion_event(self, event: ConversionEvent):
        """Store conversion event to database"""
        # This would integrate with database system
        # Placeholder implementation
        logger.debug(f"Storing conversion event: {event.event_id}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())
    
    async def analyze_conversion_funnel(self, funnel_steps: List[str]) -> Dict[str, Any]:
        """Analyze conversion funnel for SEO traffic
        
        Args:
            funnel_steps: List of funnel step URLs/events
            
        Returns:
            Funnel analysis results
        """
        try:
            funnel_data = {}
            
            for step in funnel_steps:
                funnel_data[step] = {
                    'visitors': 0,
                    'conversions': 0,
                    'conversion_rate': 0.0,
                    'drop_off_rate': 0.0
                }
            
            # Analyze user paths through funnel
            for path in self.conversion_paths.values():
                current_step_index = 0
                
                for touchpoint in path.touchpoints:
                    page = touchpoint['landing_page']
                    
                    # Check if this page matches current funnel step
                    if current_step_index < len(funnel_steps) and page == funnel_steps[current_step_index]:
                        funnel_data[page]['visitors'] += 1
                        
                        # Check if user converted at this step
                        if any(event.landing_page == page for event in path.conversion_events):
                            funnel_data[page]['conversions'] += 1
                        
                        current_step_index += 1
            
            # Calculate rates
            total_visitors = sum(data['visitors'] for data in funnel_data.values())
            
            for step, data in funnel_data.items():
                if data['visitors'] > 0:
                    data['conversion_rate'] = (data['conversions'] / data['visitors']) * 100
                
                if total_visitors > 0:
                    data['drop_off_rate'] = ((total_visitors - data['visitors']) / total_visitors) * 100
            
            return {
                'funnel_steps': funnel_data,
                'total_funnel_conversion_rate': (sum(data['conversions'] for data in funnel_data.values()) / total_visitors * 100) if total_visitors > 0 else 0,
                'biggest_drop_off': max(funnel_data.items(), key=lambda x: x[1]['drop_off_rate']) if funnel_data else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversion funnel: {str(e)}")
            return {}
    
    async def get_keyword_conversion_value(self, keyword: str) -> Dict[str, Any]:
        """Get conversion value analysis for specific keyword
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Keyword conversion value data
        """
        try:
            keyword_events = [
                event for event in self.conversion_events
                if keyword.lower() in [kw.lower() for kw in event.organic_keywords]
            ]
            
            if not keyword_events:
                return {'keyword': keyword, 'conversions': 0, 'total_value': Decimal('0')}
            
            total_conversions = len(keyword_events)
            total_value = sum(event.value for event in keyword_events)
            avg_conversion_value = total_value / total_conversions if total_conversions > 0 else Decimal('0')
            
            # Conversion types breakdown
            conversion_types = {}
            for event in keyword_events:
                conv_type = event.conversion_type.value
                conversion_types[conv_type] = conversion_types.get(conv_type, 0) + 1
            
            # Landing pages breakdown
            landing_pages = {}
            for event in keyword_events:
                page = event.landing_page
                landing_pages[page] = landing_pages.get(page, 0) + 1
            
            return {
                'keyword': keyword,
                'conversions': total_conversions,
                'total_value': total_value,
                'avg_conversion_value': avg_conversion_value,
                'conversion_types': conversion_types,
                'top_landing_pages': sorted(landing_pages.items(), key=lambda x: x[1], reverse=True)[:5],
                'conversion_trend': await self._get_keyword_conversion_trend(keyword)
            }
            
        except Exception as e:
            logger.error(f"Error getting keyword conversion value: {str(e)}")
            return {}
    
    async def _get_keyword_conversion_trend(self, keyword: str) -> List[Dict[str, Any]]:
        """Get conversion trend for keyword over time"""
        # This would analyze conversion trends over time periods
        # Placeholder implementation
        return []


class ConversionReportGenerator:
    """Generate detailed conversion reports for SEO"""
    
    def __init__(self, tracker: SEOConversionTracker):
        self.tracker = tracker
    
    async def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Generate monthly conversion report"""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            metrics = await self.tracker.get_seo_conversion_metrics(start_date, end_date)
            
            return {
                'period': f"{year}-{month:02d}",
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'metrics': metrics,
                'insights': await self._generate_insights(metrics),
                'recommendations': await self._generate_recommendations(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}")
            return {}
    
    async def _generate_insights(self, metrics: SEOConversionMetrics) -> List[str]:
        """Generate insights from conversion metrics"""
        insights = []
        
        if metrics.conversion_rate > 3.0:
            insights.append("Excellent organic conversion rate - above industry average")
        elif metrics.conversion_rate < 1.0:
            insights.append("Low organic conversion rate - optimization needed")
        
        if metrics.organic_conversion_share > 50:
            insights.append("SEO is a major conversion driver for the platform")
        
        return insights
    
    async def _generate_recommendations(self, metrics: SEOConversionMetrics) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if metrics.conversion_rate < 2.0:
            recommendations.append("Focus on optimizing landing page content and user experience")
        
        if len(metrics.top_converting_keywords) > 0:
            top_keyword = metrics.top_converting_keywords[0][0]
            recommendations.append(f"Expand content around high-converting keyword: {top_keyword}")
        
        return recommendations