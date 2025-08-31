"""Market Intelligence Engine - Advanced Market Analysis System
Provides comprehensive market intelligence and competitive analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from core.exceptions import AnalysisError, DataError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    AnalysisError, DataError = globals().get('AnalysisError, DataError', Exception)
from ...utils.data_validator import DataValidator
from ...ml.prediction_engine import PredictionEngine


@dataclass
class MarketTrend:
    """Market trend data structure."""    trend_id: str
    name: str
    category: str
    growth_rate: float
    momentum: str
    confidence: float
    time_horizon: str
    impact_level: str
    related_keywords: List[str]
    market_segments: List[str]
    identified_at: datetime


@dataclass
class CompetitiveLandscape:
    """Competitive landscape analysis."""    landscape_id: str
    market_segment: str
    total_competitors: int
    market_concentration: float
    competition_intensity: str
    barriers_to_entry: List[str]
    key_success_factors: List[str]
    competitive_clusters: Dict[str, List[str]]
    market_leaders: List[Dict[str, Any]]
    emerging_threats: List[Dict[str, Any]]
    analysis_date: datetime


@dataclass
class OpportunityMatrix:
    """Market opportunity analysis matrix."""    matrix_id: str
    segment: str
    opportunities: List[Dict[str, Any]]
    threats: List[Dict[str, Any]]
    market_gaps: List[Dict[str, Any]]
    innovation_areas: List[str]
    investment_priorities: List[str]
    risk_factors: List[str]
    time_to_market: Dict[str, int]
    resource_requirements: Dict[str, Any]
    success_probability: float


class MarketIntelligenceEngine:
    """    Advanced market intelligence and analysis engine.
    
    Provides comprehensive market analysis, trend identification,
    competitive landscape mapping, and opportunity assessment.
    """    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the market intelligence engine."""        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.data_validator = DataValidator()
        self.prediction_engine = PredictionEngine()
        
        # Analysis parameters
        self.trend_threshold = config.get("trend_threshold", 0.15)
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.lookback_period = config.get("lookback_period", 90)
        
        # Market data cache
        self.market_cache: Dict[str, Any] = {}
        self.trend_cache: Dict[str, MarketTrend] = {}
        self.landscape_cache: Dict[str, CompetitiveLandscape] = {}
        
        self.logger.info("MarketIntelligenceEngine initialized")
    
    async def analyze_market_trends(self, segment: str, data: Dict[str, Any]) -> List[MarketTrend]:
        """Analyze and identify market trends for a specific segment."""        try:
            self.logger.info(f"Analyzing market trends for segment: {segment}")
            
            # Validate input data
            validated_data = await self._validate_market_data(data)
            
            # Extract time series data
            time_series = await self._extract_time_series(validated_data)
            
            # Identify trends using statistical analysis
            trends = await self._identify_statistical_trends(time_series, segment)
            
            # Apply machine learning for pattern recognition
            ml_trends = await self._identify_ml_patterns(time_series, segment)
            
            # Combine and validate trends
            combined_trends = await self._combine_and_validate_trends(trends, ml_trends)
            
            # Calculate trend confidence and momentum
            for trend in combined_trends:
                trend.confidence = await self._calculate_trend_confidence(trend, time_series)
                trend.momentum = await self._calculate_trend_momentum(trend, time_series)
            
            # Cache results
            for trend in combined_trends:
                self.trend_cache[trend.trend_id] = trend
            
            self.logger.info(f"Identified {len(combined_trends)} trends for segment {segment}")
            return combined_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing market trends: {str(e)}")
            raise AnalysisError(f"Failed to analyze market trends: {str(e)}")
    
    async def analyze_competitive_landscape(self, segment: str, competitors: List[Dict[str, Any]]) -> CompetitiveLandscape:
        """Analyze the competitive landscape for a market segment."""        try:
            self.logger.info(f"Analyzing competitive landscape for segment: {segment}")
            
            if not competitors:
                raise DataError("No competitor data provided")
            
            # Prepare competitor data for analysis
            competitor_features = await self._extract_competitor_features(competitors)
            
            # Calculate market concentration
            market_concentration = await self._calculate_market_concentration(competitors)
            
            # Determine competition intensity
            competition_intensity = await self._assess_competition_intensity(competitors)
            
            # Identify competitive clusters
            competitive_clusters = await self._identify_competitive_clusters(competitor_features)
            
            # Analyze market leaders
            market_leaders = await self._identify_market_leaders(competitors)
            
            # Identify emerging threats
            emerging_threats = await self._identify_emerging_threats(competitors)
            
            # Analyze barriers to entry
            barriers_to_entry = await self._analyze_barriers_to_entry(competitors, segment)
            
            # Identify key success factors
            key_success_factors = await self._identify_success_factors(competitors)
            
            # Create competitive landscape
            landscape = CompetitiveLandscape(
                landscape_id=f"landscape_{segment}_{datetime.utcnow().strftime('%Y%m%d')}",
                market_segment=segment,
                total_competitors=len(competitors),
                market_concentration=market_concentration,
                competition_intensity=competition_intensity,
                barriers_to_entry=barriers_to_entry,
                key_success_factors=key_success_factors,
                competitive_clusters=competitive_clusters,
                market_leaders=market_leaders,
                emerging_threats=emerging_threats,
                analysis_date=datetime.utcnow()
            )
            
            # Cache results
            self.landscape_cache[segment] = landscape
            
            self.logger.info(f"Competitive landscape analysis completed for {segment}")
            return landscape
            
        except Exception as e:
            self.logger.error(f"Error analyzing competitive landscape: {str(e)}")
            raise AnalysisError(f"Failed to analyze competitive landscape: {str(e)}")
    
    async def create_opportunity_matrix(self, segment: str, market_data: Dict[str, Any]) -> OpportunityMatrix:
        """Create comprehensive opportunity matrix for market segment."""        try:
            self.logger.info(f"Creating opportunity matrix for segment: {segment}")
            
            # Identify market opportunities
            opportunities = await self._identify_market_opportunities(segment, market_data)
            
            # Assess market threats
            threats = await self._assess_market_threats(segment, market_data)
            
            # Identify market gaps
            market_gaps = await self._identify_market_gaps(segment, market_data)
            
            # Analyze innovation areas
            innovation_areas = await self._analyze_innovation_areas(segment, market_data)
            
            # Prioritize investments
            investment_priorities = await self._prioritize_investments(opportunities, market_gaps)
            
            # Assess risk factors
            risk_factors = await self._assess_risk_factors(segment, threats)
            
            # Estimate time to market
            time_to_market = await self._estimate_time_to_market(opportunities)
            
            # Calculate resource requirements
            resource_requirements = await self._calculate_resource_requirements(opportunities)
            
            # Calculate overall success probability
            success_probability = await self._calculate_success_probability(opportunities, threats)
            
            # Create opportunity matrix
            matrix = OpportunityMatrix(
                matrix_id=f"matrix_{segment}_{datetime.utcnow().strftime('%Y%m%d')}",
                segment=segment,
                opportunities=opportunities,
                threats=threats,
                market_gaps=market_gaps,
                innovation_areas=innovation_areas,
                investment_priorities=investment_priorities,
                risk_factors=risk_factors,
                time_to_market=time_to_market,
                resource_requirements=resource_requirements,
                success_probability=success_probability
            )
            
            self.logger.info(f"Opportunity matrix created for {segment}")
            return matrix
            
        except Exception as e:
            self.logger.error(f"Error creating opportunity matrix: {str(e)}")
            raise AnalysisError(f"Failed to create opportunity matrix: {str(e)}")
    
    async def predict_market_evolution(self, segment: str, horizon: int = 12) -> Dict[str, Any]:
        """Predict market evolution over specified time horizon (months)."""        try:
            self.logger.info(f"Predicting market evolution for {segment} over {horizon} months")
            
            # Get historical market data
            historical_data = await self._get_historical_market_data(segment)
            
            # Prepare data for prediction
            features = await self._prepare_prediction_features(historical_data)
            
            # Generate market size predictions
            size_predictions = await self.prediction_engine.predict_time_series(
                features["market_size"], horizon
            )
            
            # Generate growth rate predictions
            growth_predictions = await self.prediction_engine.predict_time_series(
                features["growth_rate"], horizon
            )
            
            # Generate competitor count predictions
            competitor_predictions = await self.prediction_engine.predict_time_series(
                features["competitor_count"], horizon
            )
            
            # Generate trend evolution predictions
            trend_evolution = await self._predict_trend_evolution(segment, horizon)
            
            # Generate disruption probability
            disruption_probability = await self._calculate_disruption_probability(segment)
            
            predictions = {
                "segment": segment,
                "horizon_months": horizon,
                "market_size_forecast": size_predictions,
                "growth_rate_forecast": growth_predictions,
                "competitor_count_forecast": competitor_predictions,
                "trend_evolution": trend_evolution,
                "disruption_probability": disruption_probability,
                "confidence_intervals": await self._calculate_confidence_intervals(
                    size_predictions, growth_predictions
                ),
                "scenario_analysis": await self._generate_scenario_analysis(segment, horizon),
                "prediction_date": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Market evolution prediction completed for {segment}")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting market evolution: {str(e)}")
            raise AnalysisError(f"Failed to predict market evolution: {str(e)}")
    
    async def _identify_statistical_trends(self, time_series: Dict[str, List], segment: str) -> List[MarketTrend]:
        """Identify trends using statistical analysis methods."""        trends = []
        
        for metric, data in time_series.items():
            if len(data) < 3:
                continue
                
            # Calculate trend using linear regression
            x = np.arange(len(data))
            y = np.array(data)
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Check if trend is significant
            if abs(slope) > self.trend_threshold and p_value < 0.05:
                trend_type = "growth" if slope > 0 else "decline"
                
                trend = MarketTrend(
                    trend_id=f"trend_{segment}_{metric}_{datetime.utcnow().strftime('%Y%m%d')}",
                    name=f"{metric.replace('_', ' ').title()} {trend_type.title()}",
                    category=metric,
                    growth_rate=float(slope),
                    momentum="",  # To be calculated later
                    confidence=float(r_value ** 2),
                    time_horizon="short_term",
                    impact_level=self._calculate_impact_level(abs(slope)),
                    related_keywords=[metric, trend_type, segment],
                    market_segments=[segment],
                    identified_at=datetime.utcnow()
                )
                
                trends.append(trend)
        
        return trends
    
    async def _identify_competitive_clusters(self, competitor_features: pd.DataFrame) -> Dict[str, List[str]]:
        """Identify competitive clusters using machine learning."""        try:
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(competitor_features.drop('name', axis=1))
            
            # Determine optimal number of clusters
            optimal_clusters = await self._find_optimal_clusters(features_scaled)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            # Group competitors by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                cluster_name = f"cluster_{label}"
                if cluster_name not in clusters:
                    clusters[cluster_name] = []
                clusters[cluster_name].append(competitor_features.iloc[i]['name'])
            
            return clusters
            
        except Exception as e:
            self.logger.error(f"Error identifying competitive clusters: {str(e)}")
            return {}
    
    async def _calculate_market_concentration(self, competitors: List[Dict[str, Any]]) -> float:
        """Calculate market concentration using Herfindahl-Hirschman Index."""        try:
            total_market_share = sum(comp.get('market_share', 0) for comp in competitors)
            if total_market_share == 0:
                return 0.0
            
            # Calculate HHI
            hhi = sum((comp.get('market_share', 0) / total_market_share) ** 2 for comp in competitors)
            return float(hhi)
            
        except Exception as e:
            self.logger.error(f"Error calculating market concentration: {str(e)}")
            return 0.0
    
    async def _assess_competition_intensity(self, competitors: List[Dict[str, Any]]) -> str:
        """Assess the intensity of competition in the market."""        try:
            # Factors to consider
            num_competitors = len(competitors)
            avg_growth = np.mean([comp.get('growth_rate', 0) for comp in competitors])
            price_competition = len([comp for comp in competitors if comp.get('pricing_strategy', {}).get('competitive', False)])
            
            # Calculate intensity score
            intensity_score = 0
            
            if num_competitors > 20:
                intensity_score += 3
            elif num_competitors > 10:
                intensity_score += 2
            elif num_competitors > 5:
                intensity_score += 1
            
            if avg_growth > 0.15:
                intensity_score += 2
            elif avg_growth > 0.05:
                intensity_score += 1
            
            if price_competition / num_competitors > 0.5:
                intensity_score += 2
            
            # Determine intensity level
            if intensity_score >= 6:
                return "very_high"
            elif intensity_score >= 4:
                return "high"
            elif intensity_score >= 2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.error(f"Error assessing competition intensity: {str(e)}")
            return "unknown"
