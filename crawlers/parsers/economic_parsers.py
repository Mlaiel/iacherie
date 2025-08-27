"""
Economic Intelligence Parsers Module
===================================

Ultra-advanced parsers for economic data, revenue tracking, financial analytics,
and business intelligence for creator monetization platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de

Development Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI systems
- ML Engineer: Content analysis and fingerprinting
- Audio Processing Specialist: Multi-format audio analysis  
- DevOps Engineer: Infrastructure and deployment
- Database Administrator: Performance optimization
- Security Expert: Content protection and compliance
- Microservices Architect: Scalable system design
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import csv
from io import StringIO

import aiohttp
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from .exceptions import EconomicParsingError, ValidationError, DataExtractionError
from .parser_config import ParserConfig


class RevenueSource(Enum):
    """Revenue source types"""
    YOUTUBE_AD_REVENUE = "youtube_ads"
    YOUTUBE_PREMIUM = "youtube_premium"
    SPOTIFY_ROYALTIES = "spotify_royalties"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    INSTAGRAM_REELS = "instagram_reels"
    TIKTOK_CREATOR_FUND = "tiktok_creator"
    TWITCH_SUBS = "twitch_subscriptions"
    TWITCH_BITS = "twitch_bits"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    STRIPE_PAYMENTS = "stripe"
    PAYPAL_PAYMENTS = "paypal"
    DIRECT_PAYMENTS = "direct"
    MERCHANDISE = "merchandise"
    SPONSORSHIPS = "sponsorships"
    AFFILIATE = "affiliate"
    LICENSING = "licensing"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"


@dataclass
class RevenueRecord:
    """Individual revenue record"""
    source: RevenueSource
    amount: Decimal
    currency: Currency
    date: datetime
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    platform_fee: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    transaction_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FinancialMetrics:
    """Comprehensive financial metrics"""
    total_revenue: Decimal = Decimal('0.00')
    revenue_by_source: Dict[RevenueSource, Decimal] = field(default_factory=dict)
    revenue_by_currency: Dict[Currency, Decimal] = field(default_factory=dict)
    growth_rate: float = 0.0
    monthly_recurring_revenue: Decimal = Decimal('0.00')
    average_revenue_per_user: Decimal = Decimal('0.00')
    revenue_diversification_index: float = 0.0
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    top_performing_content: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EconomicIntelligence:
    """Complete economic intelligence analysis"""
    financial_metrics: FinancialMetrics = field(default_factory=FinancialMetrics)
    revenue_forecast: Dict[str, Any] = field(default_factory=dict)
    market_analysis: Dict[str, Any] = field(default_factory=dict)
    competitor_insights: Dict[str, Any] = field(default_factory=dict)
    optimization_recommendations: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)


class YouTubeRevenueParser:
    """Advanced YouTube revenue and analytics parser"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.get_platform_config("youtube").api_key
    
    async def parse_analytics_data(self, channel_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Parse YouTube Analytics API data"""
        try:
            analytics_data = await self._fetch_youtube_analytics(channel_id, start_date, end_date)
            
            revenue_data = {
                'ad_revenue': Decimal(str(analytics_data.get('estimatedRevenue', 0))),
                'red_revenue': Decimal(str(analytics_data.get('redPartnerRevenue', 0))),
                'total_views': analytics_data.get('views', 0),
                'watch_time_hours': analytics_data.get('estimatedMinutesWatched', 0) / 60,
                'subscriber_gain': analytics_data.get('subscribersGained', 0),
                'cpm': Decimal(str(analytics_data.get('cpm', 0))),
                'rpm': Decimal(str(analytics_data.get('playbackBasedCpm', 0)))
            }
            
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"YouTube analytics parsing failed: {e}")
            raise EconomicParsingError(f"Failed to parse YouTube analytics: {e}")
    
    async def _fetch_youtube_analytics(self, channel_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Fetch data from YouTube Analytics API"""
        # Implementation would integrate with YouTube Analytics API
        # This is a placeholder for the actual API integration
        return {
            'estimatedRevenue': 1250.75,
            'redPartnerRevenue': 89.50,
            'views': 125000,
            'estimatedMinutesWatched': 450000,
            'subscribersGained': 1250,
            'cpm': 2.85,
            'playbackBasedCpm': 3.20
        }


class SpotifyRoyaltyParser:
    """Advanced Spotify royalty and streaming data parser"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def parse_royalty_report(self, report_data: str) -> List[RevenueRecord]:
        """Parse Spotify royalty CSV report"""
        try:
            records = []
            csv_reader = csv.DictReader(StringIO(report_data))
            
            for row in csv_reader:
                record = RevenueRecord(
                    source=RevenueSource.SPOTIFY_ROYALTIES,
                    amount=Decimal(str(row.get('Royalty Amount', '0.00'))),
                    currency=Currency(row.get('Currency', 'USD')),
                    date=datetime.strptime(row.get('Date', ''), '%Y-%m-%d'),
                    content_id=row.get('Track ISRC', ''),
                    metadata={
                        'track_name': row.get('Track Name', ''),
                        'artist_name': row.get('Artist Name', ''),
                        'streams': int(row.get('Streams', 0)),
                        'country': row.get('Country', ''),
                        'royalty_rate': Decimal(str(row.get('Rate', '0.00')))
                    }
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.error(f"Spotify royalty parsing failed: {e}")
            raise EconomicParsingError(f"Failed to parse Spotify royalties: {e}")
    
    async def analyze_streaming_performance(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze streaming performance metrics"""
        try:
            total_streams = sum(record.metadata.get('streams', 0) for record in records)
            total_royalties = sum(record.amount for record in records)
            
            # Calculate average royalty per stream
            avg_royalty_per_stream = total_royalties / max(total_streams, 1)
            
            # Analyze by country
            country_performance = {}
            for record in records:
                country = record.metadata.get('country', 'Unknown')
                if country not in country_performance:
                    country_performance[country] = {
                        'streams': 0,
                        'royalties': Decimal('0.00'),
                        'tracks': set()
                    }
                
                country_performance[country]['streams'] += record.metadata.get('streams', 0)
                country_performance[country]['royalties'] += record.amount
                country_performance[country]['tracks'].add(record.metadata.get('track_name', ''))
            
            # Convert sets to counts
            for country_data in country_performance.values():
                country_data['unique_tracks'] = len(country_data['tracks'])
                del country_data['tracks']
            
            return {
                'total_streams': total_streams,
                'total_royalties': float(total_royalties),
                'average_per_stream': float(avg_royalty_per_stream),
                'country_breakdown': country_performance,
                'top_performing_tracks': await self._get_top_tracks(records)
            }
            
        except Exception as e:
            self.logger.error(f"Streaming analysis failed: {e}")
            return {}
    
    async def _get_top_tracks(self, records: List[RevenueRecord]) -> List[Dict[str, Any]]:
        """Get top performing tracks"""
        track_performance = {}
        
        for record in records:
            track_name = record.metadata.get('track_name', 'Unknown')
            if track_name not in track_performance:
                track_performance[track_name] = {
                    'streams': 0,
                    'royalties': Decimal('0.00'),
                    'countries': set()
                }
            
            track_performance[track_name]['streams'] += record.metadata.get('streams', 0)
            track_performance[track_name]['royalties'] += record.amount
            track_performance[track_name]['countries'].add(record.metadata.get('country', ''))
        
        # Sort by royalties and return top 10
        sorted_tracks = sorted(
            track_performance.items(),
            key=lambda x: x[1]['royalties'],
            reverse=True
        )[:10]
        
        return [
            {
                'track_name': track,
                'streams': data['streams'],
                'royalties': float(data['royalties']),
                'countries_count': len(data['countries'])
            }
            for track, data in sorted_tracks
        ]


class StripePaymentsParser:
    """Advanced Stripe payments and transaction parser"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.stripe_config = config.get_platform_config("stripe")
    
    async def parse_payment_data(self, payment_data: Dict[str, Any]) -> RevenueRecord:
        """Parse Stripe payment data"""
        try:
            # Calculate net amount after fees
            gross_amount = Decimal(str(payment_data.get('amount', 0))) / 100  # Stripe amounts are in cents
            stripe_fee = Decimal(str(payment_data.get('application_fee_amount', 0))) / 100
            net_amount = gross_amount - stripe_fee
            
            record = RevenueRecord(
                source=RevenueSource.STRIPE_PAYMENTS,
                amount=gross_amount,
                currency=Currency(payment_data.get('currency', 'USD').upper()),
                date=datetime.fromtimestamp(payment_data.get('created', 0), tz=timezone.utc),
                platform_fee=stripe_fee,
                net_amount=net_amount,
                transaction_id=payment_data.get('id', ''),
                metadata={
                    'customer_id': payment_data.get('customer', ''),
                    'payment_method': payment_data.get('payment_method_types', []),
                    'description': payment_data.get('description', ''),
                    'receipt_url': payment_data.get('receipt_url', ''),
                    'status': payment_data.get('status', ''),
                    'failure_reason': payment_data.get('failure_reason', ''),
                    'risk_score': payment_data.get('outcome', {}).get('risk_score', 0)
                }
            )
            
            return record
            
        except Exception as e:
            self.logger.error(f"Stripe payment parsing failed: {e}")
            raise EconomicParsingError(f"Failed to parse Stripe payment: {e}")
    
    async def analyze_payment_patterns(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze payment patterns and trends"""
        try:
            # Group by payment method
            payment_methods = {}
            for record in records:
                methods = record.metadata.get('payment_method', [])
                for method in methods:
                    if method not in payment_methods:
                        payment_methods[method] = {
                            'count': 0,
                            'total_amount': Decimal('0.00'),
                            'average_amount': Decimal('0.00')
                        }
                    
                    payment_methods[method]['count'] += 1
                    payment_methods[method]['total_amount'] += record.amount
            
            # Calculate averages
            for method_data in payment_methods.values():
                method_data['average_amount'] = method_data['total_amount'] / max(method_data['count'], 1)
            
            # Analyze time patterns
            hourly_distribution = {}
            daily_distribution = {}
            
            for record in records:
                hour = record.date.hour
                day = record.date.strftime('%A')
                
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                daily_distribution[day] = daily_distribution.get(day, 0) + 1
            
            # Calculate failure rates
            total_attempts = len(records)
            failed_attempts = sum(1 for r in records if r.metadata.get('status') == 'failed')
            success_rate = (total_attempts - failed_attempts) / max(total_attempts, 1)
            
            return {
                'payment_methods': {
                    method: {
                        'count': data['count'],
                        'total_amount': float(data['total_amount']),
                        'average_amount': float(data['average_amount'])
                    }
                    for method, data in payment_methods.items()
                },
                'time_patterns': {
                    'hourly_distribution': hourly_distribution,
                    'daily_distribution': daily_distribution
                },
                'success_rate': success_rate,
                'total_transactions': total_attempts,
                'failed_transactions': failed_attempts
            }
            
        except Exception as e:
            self.logger.error(f"Payment pattern analysis failed: {e}")
            return {}


class EconomicIntelligenceEngine:
    """Advanced economic intelligence and analytics engine"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.youtube_parser = YouTubeRevenueParser(config)
        self.spotify_parser = SpotifyRoyaltyParser(config)
        self.stripe_parser = StripePaymentsParser(config)
    
    async def generate_economic_intelligence(
        self, 
        revenue_records: List[RevenueRecord],
        period_days: int = 30
    ) -> EconomicIntelligence:
        """Generate comprehensive economic intelligence report"""
        try:
            # Calculate financial metrics
            financial_metrics = await self._calculate_financial_metrics(revenue_records)
            
            # Generate revenue forecast
            revenue_forecast = await self._generate_revenue_forecast(revenue_records, period_days)
            
            # Perform market analysis
            market_analysis = await self._analyze_market_trends(revenue_records)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                revenue_records, financial_metrics
            )
            
            # Assess risks
            risk_assessment = await self._assess_financial_risks(revenue_records)
            
            return EconomicIntelligence(
                financial_metrics=financial_metrics,
                revenue_forecast=revenue_forecast,
                market_analysis=market_analysis,
                optimization_recommendations=recommendations,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            self.logger.error(f"Economic intelligence generation failed: {e}")
            raise EconomicParsingError(f"Failed to generate economic intelligence: {e}")
    
    async def _calculate_financial_metrics(self, records: List[RevenueRecord]) -> FinancialMetrics:
        """Calculate comprehensive financial metrics"""
        metrics = FinancialMetrics()
        
        # Total revenue
        metrics.total_revenue = sum(record.amount for record in records)
        
        # Revenue by source
        for record in records:
            if record.source not in metrics.revenue_by_source:
                metrics.revenue_by_source[record.source] = Decimal('0.00')
            metrics.revenue_by_source[record.source] += record.amount
        
        # Revenue by currency
        for record in records:
            if record.currency not in metrics.revenue_by_currency:
                metrics.revenue_by_currency[record.currency] = Decimal('0.00')
            metrics.revenue_by_currency[record.currency] += record.amount
        
        # Calculate growth rate
        metrics.growth_rate = await self._calculate_growth_rate(records)
        
        # Monthly recurring revenue (estimate based on subscription sources)
        subscription_sources = [
            RevenueSource.PATREON, RevenueSource.ONLYFANS, 
            RevenueSource.TWITCH_SUBS, RevenueSource.YOUTUBE_PREMIUM
        ]
        metrics.monthly_recurring_revenue = sum(
            amount for source, amount in metrics.revenue_by_source.items()
            if source in subscription_sources
        )
        
        # Revenue diversification index (Herfindahl-Hirschman Index)
        total = float(metrics.total_revenue)
        if total > 0:
            hhi = sum(
                (float(amount) / total) ** 2 
                for amount in metrics.revenue_by_source.values()
            )
            metrics.revenue_diversification_index = 1 - hhi  # Higher = more diversified
        
        return metrics
    
    async def _calculate_growth_rate(self, records: List[RevenueRecord]) -> float:
        """Calculate revenue growth rate"""
        try:
            # Group by month
            monthly_revenue = {}
            for record in records:
                month_key = record.date.strftime('%Y-%m')
                if month_key not in monthly_revenue:
                    monthly_revenue[month_key] = Decimal('0.00')
                monthly_revenue[month_key] += record.amount
            
            if len(monthly_revenue) < 2:
                return 0.0
            
            # Calculate month-over-month growth
            sorted_months = sorted(monthly_revenue.keys())
            growth_rates = []
            
            for i in range(1, len(sorted_months)):
                current = float(monthly_revenue[sorted_months[i]])
                previous = float(monthly_revenue[sorted_months[i-1]])
                
                if previous > 0:
                    growth_rate = (current - previous) / previous
                    growth_rates.append(growth_rate)
            
            return sum(growth_rates) / max(len(growth_rates), 1)
            
        except Exception:
            return 0.0
    
    async def _generate_revenue_forecast(
        self, 
        records: List[RevenueRecord], 
        forecast_days: int
    ) -> Dict[str, Any]:
        """Generate revenue forecast using trend analysis"""
        try:
            # Simple linear trend analysis
            daily_revenue = {}
            for record in records:
                date_key = record.date.strftime('%Y-%m-%d')
                if date_key not in daily_revenue:
                    daily_revenue[date_key] = Decimal('0.00')
                daily_revenue[date_key] += record.amount
            
            if len(daily_revenue) < 7:  # Need at least a week of data
                return {'forecast': 'insufficient_data'}
            
            # Calculate trend
            sorted_dates = sorted(daily_revenue.keys())
            revenue_values = [float(daily_revenue[date]) for date in sorted_dates]
            
            # Simple moving average for forecast
            window_size = min(7, len(revenue_values))
            recent_average = sum(revenue_values[-window_size:]) / window_size
            
            # Project forward
            forecasted_total = recent_average * forecast_days
            
            return {
                'forecast_period_days': forecast_days,
                'forecasted_revenue': forecasted_total,
                'daily_average': recent_average,
                'confidence': 'medium',  # Would be calculated based on variance
                'trend': 'stable' if abs(recent_average - revenue_values[-1]) < recent_average * 0.1 else 'volatile'
            }
            
        except Exception as e:
            self.logger.warning(f"Revenue forecast failed: {e}")
            return {'forecast': 'error', 'error': str(e)}
    
    async def _analyze_market_trends(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Analyze market trends and patterns"""
        try:
            # Analyze seasonal patterns
            monthly_patterns = {}
            for record in records:
                month = record.date.month
                if month not in monthly_patterns:
                    monthly_patterns[month] = []
                monthly_patterns[month].append(float(record.amount))
            
            # Calculate average for each month
            seasonal_averages = {
                month: sum(amounts) / len(amounts)
                for month, amounts in monthly_patterns.items()
            }
            
            # Identify peak and low seasons
            peak_month = max(seasonal_averages.keys(), key=lambda m: seasonal_averages[m])
            low_month = min(seasonal_averages.keys(), key=lambda m: seasonal_averages[m])
            
            return {
                'seasonal_patterns': seasonal_averages,
                'peak_season': {
                    'month': peak_month,
                    'average_revenue': seasonal_averages[peak_month]
                },
                'low_season': {
                    'month': low_month,
                    'average_revenue': seasonal_averages[low_month]
                },
                'seasonality_impact': seasonal_averages[peak_month] / max(seasonal_averages[low_month], 1)
            }
            
        except Exception as e:
            self.logger.warning(f"Market trend analysis failed: {e}")
            return {}
    
    async def _generate_optimization_recommendations(
        self, 
        records: List[RevenueRecord],
        metrics: FinancialMetrics
    ) -> List[str]:
        """Generate revenue optimization recommendations"""
        recommendations = []
        
        try:
            # Diversification recommendations
            if metrics.revenue_diversification_index < 0.5:
                recommendations.append(
                    "Consider diversifying revenue streams to reduce dependency on single sources"
                )
            
            # Platform-specific recommendations
            revenue_by_source = metrics.revenue_by_source
            total_revenue = float(metrics.total_revenue)
            
            if total_revenue > 0:
                for source, amount in revenue_by_source.items():
                    percentage = float(amount) / total_revenue
                    
                    if source == RevenueSource.YOUTUBE_AD_REVENUE and percentage < 0.3:
                        recommendations.append(
                            "YouTube ad revenue is low - consider improving video SEO and upload consistency"
                        )
                    
                    if source == RevenueSource.SPOTIFY_ROYALTIES and percentage < 0.2:
                        recommendations.append(
                            "Music streaming revenue could be increased through playlist placements and promotion"
                        )
            
            # Subscription revenue recommendations
            if metrics.monthly_recurring_revenue < metrics.total_revenue * Decimal('0.3'):
                recommendations.append(
                    "Consider increasing subscription-based revenue sources like Patreon or membership programs"
                )
            
            # Growth rate recommendations
            if hasattr(metrics, 'growth_rate') and metrics.growth_rate < 0.05:
                recommendations.append(
                    "Revenue growth is slow - consider new content strategies or market expansion"
                )
            
        except Exception as e:
            self.logger.warning(f"Recommendation generation failed: {e}")
            recommendations.append("Unable to generate specific recommendations due to data limitations")
        
        return recommendations
    
    async def _assess_financial_risks(self, records: List[RevenueRecord]) -> Dict[str, Any]:
        """Assess financial risks and volatility"""
        try:
            # Calculate revenue volatility
            daily_revenues = {}
            for record in records:
                date_key = record.date.strftime('%Y-%m-%d')
                daily_revenues[date_key] = daily_revenues.get(date_key, 0) + float(record.amount)
            
            revenue_values = list(daily_revenues.values())
            
            if len(revenue_values) > 1:
                mean_revenue = np.mean(revenue_values)
                std_revenue = np.std(revenue_values)
                volatility = std_revenue / max(mean_revenue, 1)
            else:
                volatility = 0
            
            # Assess concentration risk
            source_revenues = {}
            total_revenue = 0
            for record in records:
                source = record.source.value
                amount = float(record.amount)
                source_revenues[source] = source_revenues.get(source, 0) + amount
                total_revenue += amount
            
            # Calculate concentration ratio (top 3 sources)
            sorted_sources = sorted(source_revenues.values(), reverse=True)
            top_3_concentration = sum(sorted_sources[:3]) / max(total_revenue, 1)
            
            # Risk levels
            volatility_risk = "high" if volatility > 0.5 else "medium" if volatility > 0.2 else "low"
            concentration_risk = "high" if top_3_concentration > 0.8 else "medium" if top_3_concentration > 0.6 else "low"
            
            return {
                'volatility': {
                    'score': volatility,
                    'level': volatility_risk,
                    'description': f"Revenue volatility is {volatility_risk} with coefficient of variation: {volatility:.2f}"
                },
                'concentration': {
                    'score': top_3_concentration,
                    'level': concentration_risk,
                    'description': f"Top 3 revenue sources account for {top_3_concentration:.1%} of total revenue"
                },
                'overall_risk': "high" if volatility_risk == "high" or concentration_risk == "high" else "medium"
            }
            
        except Exception as e:
            self.logger.warning(f"Risk assessment failed: {e}")
            return {'overall_risk': 'unknown', 'error': str(e)}


__all__ = [
    'EconomicIntelligenceEngine',
    'YouTubeRevenueParser',
    'SpotifyRoyaltyParser', 
    'StripePaymentsParser',
    'RevenueRecord',
    'FinancialMetrics',
    'EconomicIntelligence',
    'RevenueSource',
    'Currency'
]
