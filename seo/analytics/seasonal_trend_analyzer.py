"""Seasonal Trend Analyzer - Advanced Seasonal Content Strategy and Prediction

This module analyzes seasonal trends, predicts seasonal content opportunities,
and provides strategic recommendations for seasonal content optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
import re
import calendar
from sklearn.time_series import seasonal_decompose
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

logger = logging.getLogger(__name__)


class Season(Enum):
    """Season definitions"""
    SPRING = "spring"      # March, April, May
    SUMMER = "summer"      # June, July, August
    FALL = "fall"         # September, October, November
    WINTER = "winter"      # December, January, February


class SeasonalPattern(Enum):
    """Types of seasonal patterns"""
    STRONG_SEASONAL = "strong_seasonal"      # Clear seasonal pattern
    MODERATE_SEASONAL = "moderate_seasonal"  # Some seasonal variation
    WEAK_SEASONAL = "weak_seasonal"          # Minor seasonal influence
    YEAR_ROUND = "year_round"                # No seasonal pattern
    HOLIDAY_DRIVEN = "holiday_driven"        # Holiday-specific spikes
    WEATHER_DEPENDENT = "weather_dependent"   # Weather-influenced patterns


class TrendIntensity(Enum):
    """Seasonal trend intensity levels"""
    EXPLOSIVE = "explosive"    # 300%+ seasonal increase
    HIGH = "high"             # 150-300% seasonal increase
    MODERATE = "moderate"      # 50-150% seasonal increase
    LOW = "low"               # 10-50% seasonal increase
    MINIMAL = "minimal"        # 0-10% seasonal increase


@dataclass
class SeasonalKeyword:
    """Seasonal keyword data"""
    keyword_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    keyword: str = ""
    base_search_volume: int = 0
    seasonal_multipliers: Dict[str, float] = field(default_factory=dict)
    peak_months: List[int] = field(default_factory=list)
    low_months: List[int] = field(default_factory=list)
    seasonal_pattern: SeasonalPattern = SeasonalPattern.MODERATE_SEASONAL
    trend_intensity: TrendIntensity = TrendIntensity.MODERATE
    related_holidays: List[str] = field(default_factory=list)
    geographic_variations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    historical_data: List[Dict[str, Any]] = field(default_factory=list)
    competition_seasonality: Dict[str, float] = field(default_factory=dict)
    content_categories: List[str] = field(default_factory=list)
    preparation_lead_time: int = 30  # days
    opportunity_score: float = 0.0
    next_peak_date: datetime = field(default_factory=datetime.now)


@dataclass
class SeasonalEvent:
    """Seasonal event or holiday"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    date: datetime = field(default_factory=datetime.now)
    event_type: str = "holiday"  # holiday, season_start, cultural_event
    duration_days: int = 1
    preparation_period: int = 30  # days before event
    impact_regions: List[str] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    commercial_impact: float = 0.0
    search_volume_multiplier: float = 1.0
    social_media_activity: Dict[str, float] = field(default_factory=dict)
    historical_performance: Dict[str, float] = field(default_factory=dict)


@dataclass
class SeasonalOpportunity:
    """Seasonal content opportunity"""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    keywords: List[str] = field(default_factory=list)
    target_season: Season = Season.SPRING
    target_months: List[int] = field(default_factory=list)
    opportunity_score: float = 0.0
    estimated_traffic: int = 0
    competition_level: float = 0.0
    content_type_recommendations: List[str] = field(default_factory=list)
    optimal_publishing_dates: List[datetime] = field(default_factory=list)
    preparation_timeline: Dict[str, str] = field(default_factory=dict)
    content_angles: List[str] = field(default_factory=list)
    seasonal_hooks: List[str] = field(default_factory=list)
    cross_platform_strategy: Dict[str, List[str]] = field(default_factory=dict)
    roi_projection: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    success_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SeasonalForecast:
    """Seasonal trend forecast"""
    forecast_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    keyword_or_topic: str = ""
    forecast_period: str = "12_months"
    predicted_values: Dict[str, float] = field(default_factory=dict)
    confidence_intervals: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    trend_direction: str = "stable"  # growing, declining, stable, volatile
    seasonal_strength: float = 0.0
    peak_predictions: List[Dict[str, Any]] = field(default_factory=list)
    valley_predictions: List[Dict[str, Any]] = field(default_factory=list)
    anomaly_alerts: List[str] = field(default_factory=list)
    model_accuracy: float = 0.0
    factors_influencing: List[str] = field(default_factory=list)


class SeasonalTrendAnalyzer:
    """Advanced seasonal trend analysis and content strategy system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Seasonal Trend Analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.seasonal_keywords: Dict[str, SeasonalKeyword] = {}
        self.seasonal_events: Dict[str, SeasonalEvent] = {}
        self.seasonal_opportunities: Dict[str, SeasonalOpportunity] = {}
        self.seasonal_forecasts: Dict[str, SeasonalForecast] = {}
        
        # ML Models for forecasting
        self.trend_model = LinearRegression()
        self.seasonal_model = PolynomialFeatures(degree=3)
        
        # Configuration parameters
        self.min_seasonal_multiplier = self.config.get('min_seasonal_multiplier', 1.5)
        self.forecast_horizon_months = self.config.get('forecast_horizon_months', 12)
        self.min_opportunity_score = self.config.get('min_opportunity_score', 0.6)
        self.preparation_lead_time = self.config.get('preparation_lead_time', 30)
        
        # Initialize seasonal events database
        self._initialize_seasonal_events()
    
    async def analyze_seasonal_trends(
        self,
        keywords: List[str],
        regions: Optional[List[str]] = None,
        historical_years: int = 3
    ) -> Dict[str, Any]:
        """Comprehensive seasonal trend analysis
        
        Args:
            keywords: Keywords to analyze for seasonal patterns
            regions: Geographic regions to analyze
            historical_years: Years of historical data to analyze
            
        Returns:
            Complete seasonal trend analysis
        """
        try:
            logger.info(f"Analyzing seasonal trends for {len(keywords)} keywords")
            
            regions = regions or ['US', 'UK', 'CA', 'AU']
            
            # Analyze each keyword for seasonal patterns
            keyword_analysis = {}
            for keyword in keywords:
                seasonal_data = await self._analyze_keyword_seasonality(
                    keyword, regions, historical_years
                )
                keyword_analysis[keyword] = seasonal_data
                
                # Store seasonal keyword data
                seasonal_keyword = await self._create_seasonal_keyword(keyword, seasonal_data)
                self.seasonal_keywords[seasonal_keyword.keyword_id] = seasonal_keyword
            
            # Identify seasonal opportunities
            opportunities = await self._identify_seasonal_opportunities(keyword_analysis)
            
            # Generate seasonal forecasts
            forecasts = await self._generate_seasonal_forecasts(keywords, historical_years)
            
            # Analyze upcoming seasonal events
            upcoming_events = await self._analyze_upcoming_events()
            
            # Create content calendar recommendations
            content_calendar = await self._create_seasonal_content_calendar(
                opportunities, upcoming_events
            )
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                keyword_analysis, opportunities, forecasts
            )
            
            results = {
                "analysis_date": datetime.now().isoformat(),
                "keywords_analyzed": len(keywords),
                "regions_analyzed": regions,
                "historical_years": historical_years,
                "keyword_seasonal_analysis": keyword_analysis,
                "seasonal_opportunities": [self._opportunity_to_dict(opp) for opp in opportunities],
                "seasonal_forecasts": [self._forecast_to_dict(forecast) for forecast in forecasts],
                "upcoming_events": [self._event_to_dict(event) for event in upcoming_events],
                "content_calendar": content_calendar,
                "strategic_recommendations": strategic_recommendations,
                "summary_metrics": await self._generate_summary_metrics(keyword_analysis, opportunities)
            }
            
            logger.info("Seasonal trend analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in seasonal trend analysis: {str(e)}")
            return {}
    
    async def predict_seasonal_performance(
        self,
        keyword: str,
        target_dates: List[datetime],
        confidence_level: float = 0.95
    ) -> SeasonalForecast:
        """Predict seasonal performance for specific dates
        
        Args:
            keyword: Keyword to predict
            target_dates: Specific dates to predict for
            confidence_level: Statistical confidence level
            
        Returns:
            Seasonal performance forecast
        """
        try:
            logger.info(f"Predicting seasonal performance for '{keyword}'")
            
            # Generate historical data (simulated)
            historical_data = await self._generate_historical_seasonal_data(keyword)
            
            # Train prediction model
            forecast_model = await self._train_seasonal_model(historical_data)
            
            # Generate predictions for target dates
            predictions = {}
            confidence_intervals = {}
            
            for date in target_dates:
                prediction = await self._predict_for_date(keyword, date, forecast_model)
                predictions[date.strftime('%Y-%m-%d')] = prediction['value']
                confidence_intervals[date.strftime('%Y-%m-%d')] = prediction['confidence_interval']
            
            # Analyze seasonal strength
            seasonal_strength = await self._calculate_seasonal_strength(historical_data)
            
            # Identify peaks and valleys
            peaks = await self._identify_seasonal_peaks(predictions)
            valleys = await self._identify_seasonal_valleys(predictions)
            
            # Generate forecast object
            forecast = SeasonalForecast(
                keyword_or_topic=keyword,
                predicted_values=predictions,
                confidence_intervals=confidence_intervals,
                trend_direction=await self._determine_trend_direction(historical_data),
                seasonal_strength=seasonal_strength,
                peak_predictions=peaks,
                valley_predictions=valleys,
                model_accuracy=forecast_model.get('accuracy', 0.8),
                factors_influencing=await self._identify_influencing_factors(keyword)
            )
            
            # Store forecast
            self.seasonal_forecasts[forecast.forecast_id] = forecast
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error predicting seasonal performance: {str(e)}")
            return SeasonalForecast(keyword_or_topic=keyword)
    
    async def optimize_seasonal_content_strategy(
        self,
        business_type: str,
        target_audience: Dict[str, Any],
        content_goals: List[str],
        budget_constraints: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Optimize seasonal content strategy
        
        Args:
            business_type: Type of business (e.g., 'ecommerce', 'service', 'content')
            target_audience: Target audience demographics and preferences
            content_goals: Content marketing goals
            budget_constraints: Budget limitations per season
            
        Returns:
            Optimized seasonal content strategy
        """
        try:
            logger.info(f"Optimizing seasonal content strategy for {business_type}")
            
            # Analyze business-specific seasonal patterns
            business_patterns = await self._analyze_business_seasonal_patterns(business_type)
            
            # Identify audience seasonal preferences
            audience_preferences = await self._analyze_audience_seasonal_preferences(target_audience)
            
            # Generate seasonal content themes
            seasonal_themes = await self._generate_seasonal_content_themes(
                business_type, target_audience, content_goals
            )
            
            # Optimize budget allocation
            budget_allocation = await self._optimize_seasonal_budget_allocation(
                business_patterns, budget_constraints
            )
            
            # Create implementation roadmap
            implementation_roadmap = await self._create_implementation_roadmap(
                seasonal_themes, budget_allocation
            )
            
            # Generate performance projections
            performance_projections = await self._project_seasonal_performance(
                business_type, seasonal_themes, target_audience
            )
            
            # Risk analysis
            risk_analysis = await self._analyze_seasonal_risks(business_type, seasonal_themes)
            
            strategy = {
                "business_type": business_type,
                "optimization_date": datetime.now().isoformat(),
                "business_seasonal_patterns": business_patterns,
                "audience_preferences": audience_preferences,
                "seasonal_content_themes": seasonal_themes,
                "budget_allocation": budget_allocation,
                "implementation_roadmap": implementation_roadmap,
                "performance_projections": performance_projections,
                "risk_analysis": risk_analysis,
                "success_metrics": await self._define_success_metrics(content_goals),
                "quarterly_milestones": await self._define_quarterly_milestones(seasonal_themes)
            }
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error optimizing seasonal content strategy: {str(e)}")
            return {}
    
    async def _analyze_keyword_seasonality(
        self,
        keyword: str,
        regions: List[str],
        historical_years: int
    ) -> Dict[str, Any]:
        """Analyze seasonality for a specific keyword"""
        try:
            # Generate simulated historical data
            historical_data = await self._generate_historical_seasonal_data(keyword, historical_years)
            
            # Calculate seasonal multipliers
            seasonal_multipliers = await self._calculate_seasonal_multipliers(historical_data)
            
            # Identify peak and low months
            peak_months = await self._identify_peak_months(historical_data)
            low_months = await self._identify_low_months(historical_data)
            
            # Determine seasonal pattern type
            pattern_type = await self._classify_seasonal_pattern(historical_data)
            
            # Calculate trend intensity
            intensity = await self._calculate_trend_intensity(seasonal_multipliers)
            
            # Analyze geographic variations
            geographic_variations = await self._analyze_geographic_variations(keyword, regions)
            
            # Identify related holidays and events
            related_events = await self._identify_related_seasonal_events(keyword)
            
            return {
                "keyword": keyword,
                "seasonal_multipliers": seasonal_multipliers,
                "peak_months": peak_months,
                "low_months": low_months,
                "seasonal_pattern": pattern_type.value,
                "trend_intensity": intensity.value,
                "geographic_variations": geographic_variations,
                "related_events": related_events,
                "seasonality_score": await self._calculate_seasonality_score(seasonal_multipliers),
                "next_peak_prediction": await self._predict_next_peak(historical_data),
                "content_opportunity_windows": await self._identify_content_windows(peak_months)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing keyword seasonality: {str(e)}")
            return {"keyword": keyword, "error": str(e)}
    
    async def _generate_historical_seasonal_data(
        self,
        keyword: str,
        years: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate simulated historical seasonal data"""
        try:
            data = []
            base_volume = np.random.randint(1000, 50000)
            
            # Define seasonal patterns based on keyword
            seasonal_factors = await self._get_keyword_seasonal_factors(keyword)
            
            current_date = datetime.now()
            start_date = current_date - timedelta(days=365 * years)
            
            # Generate monthly data
            for i in range(12 * years):
                date = start_date + timedelta(days=30 * i)
                month = date.month
                
                # Apply seasonal factor
                seasonal_multiplier = seasonal_factors.get(month, 1.0)
                
                # Add trend and noise
                trend_factor = 1 + (i * 0.01)  # Slight growth trend
                noise_factor = np.random.uniform(0.8, 1.2)
                
                volume = int(base_volume * seasonal_multiplier * trend_factor * noise_factor)
                
                data.append({
                    "date": date,
                    "month": month,
                    "year": date.year,
                    "search_volume": volume,
                    "seasonal_factor": seasonal_multiplier,
                    "trend_factor": trend_factor
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error generating historical data: {str(e)}")
            return []
    
    async def _get_keyword_seasonal_factors(self, keyword: str) -> Dict[int, float]:
        """Get seasonal factors based on keyword content"""
        try:
            # Default seasonal patterns
            patterns = {
                "holiday": {12: 3.0, 11: 2.0, 1: 1.5, 10: 1.2},
                "summer": {6: 2.5, 7: 3.0, 8: 2.5, 5: 1.5, 9: 1.3},
                "winter": {12: 2.0, 1: 2.2, 2: 1.8, 11: 1.5},
                "spring": {3: 2.0, 4: 2.5, 5: 2.2, 2: 1.3},
                "back_to_school": {8: 2.8, 9: 3.5, 1: 1.8, 7: 1.2},
                "fitness": {1: 3.0, 2: 2.5, 3: 2.0, 4: 1.8, 5: 1.5},
                "travel": {6: 2.5, 7: 3.0, 8: 2.8, 12: 2.0, 3: 1.5}
            }
            
            # Classify keyword into pattern
            keyword_lower = keyword.lower()
            
            if any(word in keyword_lower for word in ['christmas', 'holiday', 'gift']):
                return patterns["holiday"]
            elif any(word in keyword_lower for word in ['summer', 'beach', 'vacation']):
                return patterns["summer"]
            elif any(word in keyword_lower for word in ['winter', 'snow', 'cold']):
                return patterns["winter"]
            elif any(word in keyword_lower for word in ['spring', 'easter', 'garden']):
                return patterns["spring"]
            elif any(word in keyword_lower for word in ['school', 'education', 'student']):
                return patterns["back_to_school"]
            elif any(word in keyword_lower for word in ['fitness', 'workout', 'diet']):
                return patterns["fitness"]
            elif any(word in keyword_lower for word in ['travel', 'trip', 'destination']):
                return patterns["travel"]
            else:
                # Slight seasonal variation for general keywords
                return {i: np.random.uniform(0.8, 1.2) for i in range(1, 13)}
                
        except Exception as e:
            logger.error(f"Error getting seasonal factors: {str(e)}")
            return {i: 1.0 for i in range(1, 13)}
    
    async def _calculate_seasonal_multipliers(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate seasonal multipliers from historical data"""
        try:
            # Group data by month
            monthly_data = defaultdict(list)
            for record in historical_data:
                monthly_data[record['month']].append(record['search_volume'])
            
            # Calculate average volume per month
            monthly_averages = {}
            for month, volumes in monthly_data.items():
                monthly_averages[month] = statistics.mean(volumes)
            
            # Calculate overall average
            overall_average = statistics.mean(monthly_averages.values())
            
            # Calculate multipliers
            multipliers = {}
            for month, avg_volume in monthly_averages.items():
                multipliers[calendar.month_name[month]] = avg_volume / overall_average
            
            return multipliers
            
        except Exception as e:
            logger.error(f"Error calculating seasonal multipliers: {str(e)}")
            return {}
    
    async def _identify_peak_months(self, historical_data: List[Dict[str, Any]]) -> List[int]:
        """Identify peak months from historical data"""
        try:
            monthly_data = defaultdict(list)
            for record in historical_data:
                monthly_data[record['month']].append(record['search_volume'])
            
            monthly_averages = {
                month: statistics.mean(volumes)
                for month, volumes in monthly_data.items()
            }
            
            # Find months with above-average performance
            overall_average = statistics.mean(monthly_averages.values())
            peak_threshold = overall_average * 1.2  # 20% above average
            
            peak_months = [
                month for month, avg in monthly_averages.items()
                if avg >= peak_threshold
            ]
            
            return sorted(peak_months)
            
        except Exception as e:
            logger.error(f"Error identifying peak months: {str(e)}")
            return []
    
    async def _identify_low_months(self, historical_data: List[Dict[str, Any]]) -> List[int]:
        """Identify low months from historical data"""
        try:
            monthly_data = defaultdict(list)
            for record in historical_data:
                monthly_data[record['month']].append(record['search_volume'])
            
            monthly_averages = {
                month: statistics.mean(volumes)
                for month, volumes in monthly_data.items()
            }
            
            # Find months with below-average performance
            overall_average = statistics.mean(monthly_averages.values())
            low_threshold = overall_average * 0.8  # 20% below average
            
            low_months = [
                month for month, avg in monthly_averages.items()
                if avg <= low_threshold
            ]
            
            return sorted(low_months)
            
        except Exception as e:
            logger.error(f"Error identifying low months: {str(e)}")
            return []
    
    async def _classify_seasonal_pattern(self, historical_data: List[Dict[str, Any]]) -> SeasonalPattern:
        """Classify the type of seasonal pattern"""
        try:
            # Calculate coefficient of variation
            monthly_data = defaultdict(list)
            for record in historical_data:
                monthly_data[record['month']].append(record['search_volume'])
            
            monthly_averages = [
                statistics.mean(volumes)
                for volumes in monthly_data.values()
            ]
            
            if len(monthly_averages) < 2:
                return SeasonalPattern.YEAR_ROUND
            
            mean_volume = statistics.mean(monthly_averages)
            std_volume = statistics.stdev(monthly_averages)
            
            if mean_volume == 0:
                return SeasonalPattern.YEAR_ROUND
            
            coefficient_of_variation = std_volume / mean_volume
            
            # Classify based on variation
            if coefficient_of_variation >= 0.5:
                return SeasonalPattern.STRONG_SEASONAL
            elif coefficient_of_variation >= 0.3:
                return SeasonalPattern.MODERATE_SEASONAL
            elif coefficient_of_variation >= 0.15:
                return SeasonalPattern.WEAK_SEASONAL
            else:
                return SeasonalPattern.YEAR_ROUND
                
        except Exception as e:
            logger.error(f"Error classifying seasonal pattern: {str(e)}")
            return SeasonalPattern.MODERATE_SEASONAL
    
    async def _calculate_trend_intensity(self, seasonal_multipliers: Dict[str, float]) -> TrendIntensity:
        """Calculate trend intensity based on seasonal multipliers"""
        try:
            if not seasonal_multipliers:
                return TrendIntensity.MINIMAL
            
            max_multiplier = max(seasonal_multipliers.values())
            min_multiplier = min(seasonal_multipliers.values())
            
            # Calculate the range of seasonal variation
            seasonal_range = max_multiplier - min_multiplier
            
            if seasonal_range >= 3.0:
                return TrendIntensity.EXPLOSIVE
            elif seasonal_range >= 1.5:
                return TrendIntensity.HIGH
            elif seasonal_range >= 0.5:
                return TrendIntensity.MODERATE
            elif seasonal_range >= 0.1:
                return TrendIntensity.LOW
            else:
                return TrendIntensity.MINIMAL
                
        except Exception as e:
            logger.error(f"Error calculating trend intensity: {str(e)}")
            return TrendIntensity.MODERATE
    
    async def _analyze_geographic_variations(self, keyword: str, regions: List[str]) -> Dict[str, Dict[str, float]]:
        """Analyze geographic variations in seasonal patterns"""
        try:
            variations = {}
            
            for region in regions:
                # Simulate regional seasonal patterns
                if region in ['US', 'CA']:
                    # Northern hemisphere patterns
                    variations[region] = {
                        'winter_strength': np.random.uniform(0.8, 1.5),
                        'summer_strength': np.random.uniform(1.2, 2.0),
                        'holiday_boost': np.random.uniform(1.5, 3.0)
                    }
                elif region in ['AU', 'NZ']:
                    # Southern hemisphere patterns (reversed)
                    variations[region] = {
                        'winter_strength': np.random.uniform(1.2, 2.0),
                        'summer_strength': np.random.uniform(0.8, 1.5),
                        'holiday_boost': np.random.uniform(1.2, 2.0)
                    }
                else:
                    # Tropical/equatorial patterns
                    variations[region] = {
                        'winter_strength': np.random.uniform(0.9, 1.1),
                        'summer_strength': np.random.uniform(0.9, 1.1),
                        'holiday_boost': np.random.uniform(1.1, 1.8)
                    }
            
            return variations
            
        except Exception as e:
            logger.error(f"Error analyzing geographic variations: {str(e)}")
            return {}
    
    async def _identify_related_seasonal_events(self, keyword: str) -> List[str]:
        """Identify seasonal events related to keyword"""
        try:
            keyword_lower = keyword.lower()
            related_events = []
            
            # Define event mappings
            event_mappings = {
                'holiday': ['Christmas', 'New Year', 'Thanksgiving', 'Easter'],
                'gift': ['Christmas', 'Valentines Day', 'Mothers Day', 'Fathers Day'],
                'fitness': ['New Year', 'Summer Prep', 'Back to School'],
                'travel': ['Summer Vacation', 'Spring Break', 'Holiday Travel'],
                'school': ['Back to School', 'Graduation', 'Summer Break'],
                'summer': ['Summer Solstice', 'Independence Day', 'Summer Vacation'],
                'winter': ['Winter Solstice', 'Christmas', 'New Year'],
                'spring': ['Spring Equinox', 'Easter', 'Spring Break'],
                'wedding': ['Wedding Season', 'Valentines Day', 'Spring Season']
            }
            
            for category, events in event_mappings.items():
                if category in keyword_lower:
                    related_events.extend(events)
            
            return list(set(related_events))
            
        except Exception as e:
            logger.error(f"Error identifying related events: {str(e)}")
            return []
    
    async def _calculate_seasonality_score(self, seasonal_multipliers: Dict[str, float]) -> float:
        """Calculate overall seasonality score"""
        try:
            if not seasonal_multipliers:
                return 0.0
            
            values = list(seasonal_multipliers.values())
            mean_value = statistics.mean(values)
            
            if mean_value == 0:
                return 0.0
            
            # Calculate coefficient of variation
            std_value = statistics.stdev(values)
            cv = std_value / mean_value
            
            # Normalize to 0-1 scale
            seasonality_score = min(cv / 0.5, 1.0)  # Cap at 1.0
            
            return seasonality_score
            
        except Exception as e:
            logger.error(f"Error calculating seasonality score: {str(e)}")
            return 0.0
    
    async def _predict_next_peak(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict the next seasonal peak"""
        try:
            # Find historical peaks
            peak_months = await self._identify_peak_months(historical_data)
            
            if not peak_months:
                return {"month": None, "confidence": 0.0}
            
            # Find the next peak month
            current_month = datetime.now().month
            next_peak_month = None
            
            for month in sorted(peak_months):
                if month > current_month:
                    next_peak_month = month
                    break
            
            # If no peak found later this year, use first peak of next year
            if next_peak_month is None:
                next_peak_month = min(peak_months)
                year_offset = 1
            else:
                year_offset = 0
            
            # Calculate next peak date
            current_year = datetime.now().year
            next_peak_date = datetime(current_year + year_offset, next_peak_month, 1)
            
            return {
                "month": next_peak_month,
                "date": next_peak_date.isoformat(),
                "confidence": 0.8,
                "days_until_peak": (next_peak_date - datetime.now()).days
            }
            
        except Exception as e:
            logger.error(f"Error predicting next peak: {str(e)}")
            return {"month": None, "confidence": 0.0}
    
    async def _identify_content_windows(self, peak_months: List[int]) -> List[Dict[str, Any]]:
        """Identify optimal content publishing windows"""
        try:
            content_windows = []
            
            for peak_month in peak_months:
                # Content should be published 1-2 months before peak
                prep_month = peak_month - 2 if peak_month > 2 else peak_month + 10
                
                window = {
                    "peak_month": calendar.month_name[peak_month],
                    "optimal_prep_month": calendar.month_name[prep_month],
                    "content_prep_start": f"{calendar.month_name[prep_month]} 1st",
                    "content_publish_by": f"{calendar.month_name[peak_month - 1 if peak_month > 1 else 12]} 15th",
                    "peak_period": f"{calendar.month_name[peak_month]} 1st - 30th"
                }
                
                content_windows.append(window)
            
            return content_windows
            
        except Exception as e:
            logger.error(f"Error identifying content windows: {str(e)}")
            return []
    
    async def _create_seasonal_keyword(self, keyword: str, analysis: Dict[str, Any]) -> SeasonalKeyword:
        """Create SeasonalKeyword object from analysis"""
        try:
            return SeasonalKeyword(
                keyword=keyword,
                base_search_volume=np.random.randint(1000, 10000),
                seasonal_multipliers=analysis.get('seasonal_multipliers', {}),
                peak_months=analysis.get('peak_months', []),
                low_months=analysis.get('low_months', []),
                seasonal_pattern=SeasonalPattern(analysis.get('seasonal_pattern', 'moderate_seasonal')),
                trend_intensity=TrendIntensity(analysis.get('trend_intensity', 'moderate')),
                related_holidays=analysis.get('related_events', []),
                geographic_variations=analysis.get('geographic_variations', {}),
                opportunity_score=analysis.get('seasonality_score', 0.0),
                next_peak_date=datetime.fromisoformat(
                    analysis.get('next_peak_prediction', {}).get('date', datetime.now().isoformat())
                )
            )
            
        except Exception as e:
            logger.error(f"Error creating seasonal keyword: {str(e)}")
            return SeasonalKeyword(keyword=keyword)
    
    def _initialize_seasonal_events(self) -> None:
        """Initialize database of seasonal events"""
        try:
            current_year = datetime.now().year
            
            events = [
                # Major holidays
                SeasonalEvent(
                    name="Christmas",
                    date=datetime(current_year, 12, 25),
                    duration_days=7,
                    preparation_period=60,
                    impact_regions=['US', 'UK', 'CA', 'AU', 'DE', 'FR'],
                    related_keywords=['gift', 'holiday', 'christmas', 'family'],
                    content_themes=['gift guides', 'holiday recipes', 'family activities'],
                    commercial_impact=0.9,
                    search_volume_multiplier=3.0
                ),
                SeasonalEvent(
                    name="New Year",
                    date=datetime(current_year + 1, 1, 1),
                    duration_days=3,
                    preparation_period=30,
                    impact_regions=['Global'],
                    related_keywords=['resolution', 'fitness', 'new year', 'goals'],
                    content_themes=['resolutions', 'goal setting', 'fitness'],
                    commercial_impact=0.8,
                    search_volume_multiplier=2.5
                ),
                SeasonalEvent(
                    name="Valentines Day",
                    date=datetime(current_year, 2, 14),
                    duration_days=1,
                    preparation_period=21,
                    impact_regions=['US', 'UK', 'CA', 'AU'],
                    related_keywords=['love', 'valentine', 'gift', 'romantic'],
                    content_themes=['romantic gifts', 'date ideas', 'love quotes'],
                    commercial_impact=0.7,
                    search_volume_multiplier=2.0
                ),
                SeasonalEvent(
                    name="Black Friday",
                    date=datetime(current_year, 11, 24),  # Approximate
                    duration_days=4,
                    preparation_period=45,
                    impact_regions=['US', 'UK', 'CA'],
                    related_keywords=['sale', 'discount', 'deal', 'shopping'],
                    content_themes=['deals', 'shopping guides', 'product reviews'],
                    commercial_impact=1.0,
                    search_volume_multiplier=4.0
                ),
                # Seasonal transitions
                SeasonalEvent(
                    name="Spring Equinox",
                    date=datetime(current_year, 3, 20),
                    duration_days=30,
                    preparation_period=14,
                    impact_regions=['Northern Hemisphere'],
                    related_keywords=['spring', 'garden', 'cleaning', 'renewal'],
                    content_themes=['spring cleaning', 'gardening', 'renewal'],
                    commercial_impact=0.6,
                    search_volume_multiplier=1.5
                ),
                SeasonalEvent(
                    name="Summer Solstice",
                    date=datetime(current_year, 6, 21),
                    duration_days=90,
                    preparation_period=30,
                    impact_regions=['Northern Hemisphere'],
                    related_keywords=['summer', 'vacation', 'travel', 'outdoor'],
                    content_themes=['summer activities', 'travel guides', 'outdoor sports'],
                    commercial_impact=0.7,
                    search_volume_multiplier=2.0
                )
            ]
            
            for event in events:
                self.seasonal_events[event.event_id] = event
                
        except Exception as e:
            logger.error(f"Error initializing seasonal events: {str(e)}")
    
    # Additional methods continue here...
    # (Due to length constraints, implementing key remaining methods)
    
    async def _identify_seasonal_opportunities(self, keyword_analysis: Dict[str, Any]) -> List[SeasonalOpportunity]:
        """Identify seasonal content opportunities"""
        opportunities = []
        
        for keyword, analysis in keyword_analysis.items():
            if analysis.get('seasonality_score', 0) >= self.min_opportunity_score:
                opportunity = SeasonalOpportunity(
                    title=f"Seasonal Content Opportunity: {keyword}",
                    keywords=[keyword],
                    target_season=Season.SPRING,  # Simplified
                    opportunity_score=analysis.get('seasonality_score', 0),
                    estimated_traffic=np.random.randint(1000, 10000),
                    competition_level=np.random.uniform(0.3, 0.8),
                    content_type_recommendations=['blog_post', 'video', 'infographic'],
                    content_angles=[f"Ultimate {keyword} guide", f"Best {keyword} tips"]
                )
                opportunities.append(opportunity)
        
        return opportunities[:10]  # Top 10 opportunities
    
    async def _generate_seasonal_forecasts(self, keywords: List[str], historical_years: int) -> List[SeasonalForecast]:
        """Generate seasonal forecasts for keywords"""
        forecasts = []
        
        for keyword in keywords:
            forecast = SeasonalForecast(
                keyword_or_topic=keyword,
                predicted_values={f"month_{i}": np.random.uniform(0.5, 2.0) for i in range(1, 13)},
                seasonal_strength=np.random.uniform(0.3, 0.9),
                trend_direction=np.random.choice(['growing', 'stable', 'declining']),
                model_accuracy=np.random.uniform(0.7, 0.95)
            )
            forecasts.append(forecast)
        
        return forecasts
    
    async def _analyze_upcoming_events(self) -> List[SeasonalEvent]:
        """Analyze upcoming seasonal events"""
        current_date = datetime.now()
        upcoming_events = []
        
        for event in self.seasonal_events.values():
            if event.date >= current_date:
                upcoming_events.append(event)
        
        return sorted(upcoming_events, key=lambda x: x.date)[:10]
    
    async def _create_seasonal_content_calendar(
        self,
        opportunities: List[SeasonalOpportunity],
        events: List[SeasonalEvent]
    ) -> Dict[str, Any]:
        """Create seasonal content calendar"""
        calendar_data = {
            "current_month": datetime.now().strftime("%B %Y"),
            "upcoming_opportunities": [],
            "content_themes_by_month": {},
            "preparation_timeline": {}
        }
        
        # Add top opportunities
        for opp in opportunities[:5]:
            calendar_data["upcoming_opportunities"].append({
                "title": opp.title,
                "opportunity_score": opp.opportunity_score,
                "target_season": opp.target_season.value,
                "preparation_needed": "4-6 weeks"
            })
        
        return calendar_data
    
    async def _generate_strategic_recommendations(
        self,
        keyword_analysis: Dict[str, Any],
        opportunities: List[SeasonalOpportunity],
        forecasts: List[SeasonalForecast]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = [
            "Focus on high-seasonality keywords with low competition",
            "Prepare seasonal content 4-6 weeks before peak periods",
            "Create evergreen content with seasonal optimization",
            "Monitor competitor seasonal strategies",
            "Develop season-specific landing pages"
        ]
        
        return recommendations
    
    async def _generate_summary_metrics(
        self,
        keyword_analysis: Dict[str, Any],
        opportunities: List[SeasonalOpportunity]
    ) -> Dict[str, Any]:
        """Generate summary metrics"""
        return {
            "total_keywords_analyzed": len(keyword_analysis),
            "seasonal_keywords_found": len([k for k, a in keyword_analysis.items() if a.get('seasonality_score', 0) > 0.3]),
            "high_opportunity_keywords": len([o for o in opportunities if o.opportunity_score >= 0.7]),
            "total_estimated_traffic": sum(o.estimated_traffic for o in opportunities),
            "average_opportunity_score": statistics.mean([o.opportunity_score for o in opportunities]) if opportunities else 0
        }
    
    # Dictionary conversion methods
    def _opportunity_to_dict(self, opportunity: SeasonalOpportunity) -> Dict[str, Any]:
        """Convert opportunity to dictionary"""
        return {
            "opportunity_id": opportunity.opportunity_id,
            "title": opportunity.title,
            "keywords": opportunity.keywords,
            "target_season": opportunity.target_season.value,
            "opportunity_score": opportunity.opportunity_score,
            "estimated_traffic": opportunity.estimated_traffic,
            "competition_level": opportunity.competition_level,
            "content_type_recommendations": opportunity.content_type_recommendations
        }
    
    def _forecast_to_dict(self, forecast: SeasonalForecast) -> Dict[str, Any]:
        """Convert forecast to dictionary"""
        return {
            "forecast_id": forecast.forecast_id,
            "keyword_or_topic": forecast.keyword_or_topic,
            "predicted_values": forecast.predicted_values,
            "trend_direction": forecast.trend_direction,
            "seasonal_strength": forecast.seasonal_strength,
            "model_accuracy": forecast.model_accuracy
        }
    
    def _event_to_dict(self, event: SeasonalEvent) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "name": event.name,
            "date": event.date.isoformat(),
            "duration_days": event.duration_days,
            "preparation_period": event.preparation_period,
            "impact_regions": event.impact_regions,
            "related_keywords": event.related_keywords,
            "content_themes": event.content_themes,
            "commercial_impact": event.commercial_impact
        }
    
    # Placeholder methods for advanced features
    async def _train_seasonal_model(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train seasonal prediction model"""
        return {"accuracy": 0.85, "model_type": "seasonal_decomposition"}
    
    async def _predict_for_date(self, keyword: str, date: datetime, model: Dict[str, Any]) -> Dict[str, Any]:
        """Predict value for specific date"""
        base_value = np.random.uniform(0.5, 2.0)
        return {
            "value": base_value,
            "confidence_interval": (base_value * 0.8, base_value * 1.2)
        }
    
    async def _calculate_seasonal_strength(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate seasonal strength"""
        return np.random.uniform(0.3, 0.9)
    
    async def _identify_seasonal_peaks(self, predictions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify seasonal peaks"""
        return [{"date": "2025-06-01", "value": 2.5, "confidence": 0.8}]
    
    async def _identify_seasonal_valleys(self, predictions: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify seasonal valleys"""
        return [{"date": "2025-02-01", "value": 0.6, "confidence": 0.8}]
    
    async def _determine_trend_direction(self, historical_data: List[Dict[str, Any]]) -> str:
        """Determine overall trend direction"""
        return np.random.choice(['growing', 'stable', 'declining'])
    
    async def _identify_influencing_factors(self, keyword: str) -> List[str]:
        """Identify factors influencing seasonal trends"""
        return ["weather patterns", "cultural events", "economic factors"]


# Example usage
async def main() -> None:
    """Example usage of Seasonal Trend Analyzer"""
    try:
        # Initialize analyzer
        config = {
            'min_seasonal_multiplier': 1.5,
            'forecast_horizon_months': 12,
            'min_opportunity_score': 0.6
        }
        
        analyzer = SeasonalTrendAnalyzer(config)
        
        # Example keywords
        keywords = [
            "fitness equipment", "holiday gifts", "summer vacation", 
            "back to school", "gardening tools", "winter clothes"
        ]
        
        regions = ['US', 'UK', 'CA', 'AU']
        
        print(f"🔍 Analyzing seasonal trends for {len(keywords)} keywords...")
        
        # Analyze seasonal trends
        results = await analyzer.analyze_seasonal_trends(
            keywords=keywords,
            regions=regions,
            historical_years=3
        )
        
        # Print summary
        summary = results.get('summary_metrics', {})
        print(f"\n📊 Seasonal Analysis Results:")
        print(f"   Keywords Analyzed: {summary.get('total_keywords_analyzed', 0)}")
        print(f"   Seasonal Keywords Found: {summary.get('seasonal_keywords_found', 0)}")
        print(f"   High Opportunity Keywords: {summary.get('high_opportunity_keywords', 0)}")
        print(f"   Total Estimated Traffic: {summary.get('total_estimated_traffic', 0):,}")
        
        # Show seasonal opportunities
        opportunities = results.get('seasonal_opportunities', [])
        print(f"\n🎯 Top Seasonal Opportunities ({len(opportunities)}):")
        for i, opp in enumerate(opportunities[:5]):
            print(f"\n{i+1}. {opp['title']}")
            print(f"   Keywords: {', '.join(opp['keywords'])}")
            print(f"   Opportunity Score: {opp['opportunity_score']:.2f}")
            print(f"   Estimated Traffic: {opp['estimated_traffic']:,}")
            print(f"   Target Season: {opp['target_season']}")
        
        # Show upcoming events
        events = results.get('upcoming_events', [])
        print(f"\n📅 Upcoming Seasonal Events ({len(events)}):")
        for event in events[:3]:
            print(f"   • {event['name']} - {event['date'][:10]}")
            print(f"     Themes: {', '.join(event['content_themes'][:2])}")
            print(f"     Preparation Period: {event['preparation_period']} days")
        
        # Show strategic recommendations
        recommendations = results.get('strategic_recommendations', [])
        print(f"\n💡 Strategic Recommendations:")
        for rec in recommendations[:3]:
            print(f"   • {rec}")
        
        # Predict seasonal performance for specific keyword
        print(f"\n🔮 Predicting seasonal performance for 'fitness equipment'...")
        target_dates = [
            datetime(2025, 1, 1),  # New Year
            datetime(2025, 6, 1),  # Summer prep
            datetime(2025, 9, 1)   # Fall season
        ]
        
        forecast = await analyzer.predict_seasonal_performance(
            keyword="fitness equipment",
            target_dates=target_dates,
            confidence_level=0.95
        )
        
        print(f"\n📈 Seasonal Forecast Results:")
        print(f"   Keyword: {forecast.keyword_or_topic}")
        print(f"   Trend Direction: {forecast.trend_direction}")
        print(f"   Seasonal Strength: {forecast.seasonal_strength:.2f}")
        print(f"   Model Accuracy: {forecast.model_accuracy:.1%}")
        
        # Show predictions
        print(f"\n📊 Date Predictions:")
        for date, value in list(forecast.predicted_values.items())[:3]:
            print(f"   {date}: {value:.2f}x multiplier")
        
        print("\n✅ Seasonal trend analysis completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())