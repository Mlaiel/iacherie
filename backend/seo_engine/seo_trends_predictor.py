"""SEO Trends Predictor - Prédicteur de Tendances SEO IA
======================================================

Système de prédiction des tendances SEO avec machine learning,
analyse prédictive et insights stratégiques pour l'optimisation future.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.

VERSION: 1.0.0 - AI TRENDS PREDICTION
DATE: 2025-09-09
STATUS: ✅ NOUVEAU COMPOSANT PRÉDICTIF CRITIQUE
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import asyncio
import logging
import json
import statistics
import math
from dataclasses import dataclass, field
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)

# === ÉNUMÉRATIONS ===

class TrendType(Enum):
    """Types de tendances SEO"""
    KEYWORD_TREND = "keyword_trend"
    CONTENT_TREND = "content_trend"
    ALGORITHM_TREND = "algorithm_trend"
    TECHNOLOGY_TREND = "technology_trend"
    USER_BEHAVIOR_TREND = "user_behavior_trend"
    COMPETITIVE_TREND = "competitive_trend"
    SEASONAL_TREND = "seasonal_trend"
    EMERGING_TREND = "emerging_trend"

class TrendDirection(Enum):
    """Direction des tendances"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"
    EMERGING = "emerging"
    DECLINING = "declining"

class PredictionConfidence(Enum):
    """Niveau de confiance de prédiction"""
    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"           # 75-90%
    MEDIUM = "medium"       # 60-75%
    LOW = "low"            # 40-60%
    VERY_LOW = "very_low"  # <40%

class TrendTimeframe(Enum):
    """Horizon temporel des tendances"""
    SHORT_TERM = "short_term"      # 1-3 mois
    MEDIUM_TERM = "medium_term"    # 3-12 mois
    LONG_TERM = "long_term"        # 1-3 ans
    STRATEGIC = "strategic"        # 3+ ans

class ImpactLevel(Enum):
    """Niveau d'impact SEO"""
    GAME_CHANGING = "game_changing"
    HIGH_IMPACT = "high_impact"
    MODERATE_IMPACT = "moderate_impact"
    LOW_IMPACT = "low_impact"
    MINIMAL_IMPACT = "minimal_impact"

# === DATACLASSES ===

@dataclass
class TrendData:
    """Données de tendance"""
    name: str
    trend_type: TrendType
    direction: TrendDirection
    momentum: float  # -1.0 to 1.0
    confidence: PredictionConfidence
    timeframe: TrendTimeframe
    impact_level: ImpactLevel
    current_value: float
    predicted_value: float
    historical_data: List[float] = field(default_factory=list)
    related_keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendPrediction:
    """Prédiction de tendance"""
    trend_name: str
    prediction_date: datetime
    forecast_horizon: int  # jours
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    probability_scenarios: Dict[str, float]
    key_drivers: List[str]
    risk_factors: List[str]
    opportunity_score: float

@dataclass
class SeasonalPattern:
    """Pattern saisonnier"""
    pattern_name: str
    season_start: datetime
    season_end: datetime
    peak_intensity: float
    growth_rate: float
    historical_strength: float
    predicted_strength: float

@dataclass
class EmergingTrend:
    """Tendance émergente"""
    trend_id: str
    discovery_date: datetime
    growth_velocity: float
    adoption_rate: float
    market_penetration: float
    disruption_potential: float
    time_to_mainstream: int  # jours
    early_indicators: List[str]

@dataclass
class TrendAnalysisResult:
    """Résultat d'analyse de tendances"""
    analysis_date: datetime
    analyzed_trends: List[TrendData]
    predictions: List[TrendPrediction]
    seasonal_patterns: List[SeasonalPattern]
    emerging_trends: List[EmergingTrend]
    strategic_recommendations: List[str]
    market_insights: Dict[str, Any]
    confidence_score: float

# === TRENDS PREDICTOR PRINCIPAL ===

class SEOTrendsPredictor:
    """
    🔮 Prédicteur de Tendances SEO IA
    
    Système avancé de prédiction des tendances SEO avec ML,
    analyse saisonnière et détection d'opportunités émergentes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize SEO trends predictor"""
        self.config = config or {}
        self.trends_database = defaultdict(list)
        self.prediction_models = {}
        self.historical_patterns = {}
        self.emerging_signals = deque(maxlen=10000)
        
        # Configuration des modèles prédictifs
        self.prediction_config = {
            "short_term_window": 30,     # jours
            "medium_term_window": 180,   # jours
            "long_term_window": 365,     # jours
            "confidence_threshold": 0.75,
            "volatility_threshold": 0.3,
            "emergence_threshold": 2.0   # croissance x2
        }
        
        # Poids des facteurs de prédiction
        self.prediction_weights = {
            "historical_data": 0.4,
            "seasonal_patterns": 0.25,
            "competitive_signals": 0.15,
            "technology_adoption": 0.1,
            "user_behavior": 0.1
        }
        
        # Patterns saisonniers connus
        self.seasonal_templates = {
            "holiday_shopping": {
                "peak_months": [11, 12],
                "growth_start": 10,
                "decline_start": 1
            },
            "back_to_school": {
                "peak_months": [8, 9],
                "growth_start": 7,
                "decline_start": 10
            },
            "summer_trends": {
                "peak_months": [6, 7, 8],
                "growth_start": 5,
                "decline_start": 9
            }
        }
        
        logger.info("🔮 SEO Trends Predictor initialized")
    
    async def analyze_trends(
        self,
        keywords: List[str],
        timeframe: TrendTimeframe = TrendTimeframe.MEDIUM_TERM,
        include_predictions: bool = True
    ) -> TrendAnalysisResult:
        """Analyser les tendances SEO"""
        try:
            analysis_date = datetime.utcnow()
            
            # Analyser les tendances actuelles
            analyzed_trends = await self._analyze_current_trends(keywords, timeframe)
            
            # Générer des prédictions
            predictions = []
            if include_predictions:
                predictions = await self._generate_trend_predictions(
                    analyzed_trends, timeframe
                )
            
            # Détecter les patterns saisonniers
            seasonal_patterns = await self._detect_seasonal_patterns(keywords)
            
            # Identifier les tendances émergentes
            emerging_trends = await self._identify_emerging_trends(keywords)
            
            # Générer des recommandations stratégiques
            strategic_recommendations = await self._generate_strategic_recommendations(
                analyzed_trends, predictions, emerging_trends
            )
            
            # Analyser les insights du marché
            market_insights = await self._analyze_market_insights(
                analyzed_trends, predictions
            )
            
            # Calculer le score de confiance global
            confidence_score = await self._calculate_confidence_score(
                predictions, analyzed_trends
            )
            
            result = TrendAnalysisResult(
                analysis_date=analysis_date,
                analyzed_trends=analyzed_trends,
                predictions=predictions,
                seasonal_patterns=seasonal_patterns,
                emerging_trends=emerging_trends,
                strategic_recommendations=strategic_recommendations,
                market_insights=market_insights,
                confidence_score=confidence_score
            )
            
            # Stocker les résultats pour l'apprentissage
            await self._store_analysis_results(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            raise
    
    async def predict_keyword_performance(
        self,
        keyword: str,
        forecast_days: int = 90,
        include_scenarios: bool = True
    ) -> TrendPrediction:
        """Prédire la performance d'un mot-clé"""
        try:
            # Récupérer les données historiques
            historical_data = await self._get_keyword_historical_data(keyword)
            
            # Détecter les patterns saisonniers
            seasonal_component = await self._extract_seasonal_component(
                keyword, historical_data
            )
            
            # Calculer la tendance de base
            base_trend = await self._calculate_base_trend(historical_data)
            
            # Générer les prédictions
            predicted_values = await self._generate_keyword_forecast(
                historical_data, base_trend, seasonal_component, forecast_days
            )
            
            # Calculer les intervalles de confiance
            confidence_intervals = await self._calculate_confidence_intervals(
                predicted_values, historical_data
            )
            
            # Générer des scénarios
            probability_scenarios = {}
            if include_scenarios:
                probability_scenarios = await self._generate_prediction_scenarios(
                    keyword, predicted_values
                )
            
            # Identifier les facteurs clés
            key_drivers = await self._identify_trend_drivers(keyword, historical_data)
            
            # Analyser les facteurs de risque
            risk_factors = await self._analyze_risk_factors(keyword, predicted_values)
            
            # Calculer le score d'opportunité
            opportunity_score = await self._calculate_opportunity_score(
                keyword, predicted_values, historical_data
            )
            
            prediction = TrendPrediction(
                trend_name=keyword,
                prediction_date=datetime.utcnow(),
                forecast_horizon=forecast_days,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                probability_scenarios=probability_scenarios,
                key_drivers=key_drivers,
                risk_factors=risk_factors,
                opportunity_score=opportunity_score
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict keyword performance: {e}")
            raise
    
    async def detect_emerging_opportunities(
        self,
        industry: str = None,
        min_growth_rate: float = 1.5,
        max_competition: float = 0.7
    ) -> List[EmergingTrend]:
        """Détecter les opportunités émergentes"""
        try:
            emerging_opportunities = []
            
            # Analyser les signaux émergents
            emerging_signals = await self._scan_emerging_signals(industry)
            
            for signal in emerging_signals:
                # Calculer la vélocité de croissance
                growth_velocity = await self._calculate_growth_velocity(signal)
                
                if growth_velocity >= min_growth_rate:
                    # Analyser le taux d'adoption
                    adoption_rate = await self._calculate_adoption_rate(signal)
                    
                    # Évaluer la pénétration du marché
                    market_penetration = await self._calculate_market_penetration(signal)
                    
                    # Évaluer le potentiel de disruption
                    disruption_potential = await self._assess_disruption_potential(signal)
                    
                    # Estimer le temps jusqu'au mainstream
                    time_to_mainstream = await self._estimate_mainstream_timeline(
                        signal, growth_velocity, adoption_rate
                    )
                    
                    # Identifier les indicateurs précoces
                    early_indicators = await self._identify_early_indicators(signal)
                    
                    emerging_trend = EmergingTrend(
                        trend_id=self._generate_trend_id(signal),
                        discovery_date=datetime.utcnow(),
                        growth_velocity=growth_velocity,
                        adoption_rate=adoption_rate,
                        market_penetration=market_penetration,
                        disruption_potential=disruption_potential,
                        time_to_mainstream=time_to_mainstream,
                        early_indicators=early_indicators
                    )
                    
                    emerging_opportunities.append(emerging_trend)
            
            # Trier par potentiel d'opportunité
            emerging_opportunities.sort(
                key=lambda x: x.growth_velocity * x.disruption_potential,
                reverse=True
            )
            
            return emerging_opportunities[:10]  # Top 10 opportunités
            
        except Exception as e:
            logger.error(f"Failed to detect emerging opportunities: {e}")
            raise
    
    async def forecast_seasonal_trends(
        self,
        keywords: List[str],
        forecast_year: int = None
    ) -> List[SeasonalPattern]:
        """Prévoir les tendances saisonnières"""
        try:
            if not forecast_year:
                forecast_year = datetime.utcnow().year + 1
            
            seasonal_forecasts = []
            
            for keyword in keywords:
                # Analyser les patterns historiques
                historical_patterns = await self._analyze_historical_seasonality(keyword)
                
                for pattern_name, pattern_data in historical_patterns.items():
                    # Prédire la force saisonnière
                    predicted_strength = await self._predict_seasonal_strength(
                        keyword, pattern_name, pattern_data, forecast_year
                    )
                    
                    # Déterminer les dates de saison
                    season_dates = await self._calculate_season_dates(
                        pattern_name, forecast_year
                    )
                    
                    seasonal_pattern = SeasonalPattern(
                        pattern_name=f"{keyword}_{pattern_name}",
                        season_start=season_dates["start"],
                        season_end=season_dates["end"],
                        peak_intensity=pattern_data["peak_intensity"],
                        growth_rate=pattern_data["growth_rate"],
                        historical_strength=pattern_data["avg_strength"],
                        predicted_strength=predicted_strength
                    )
                    
                    seasonal_forecasts.append(seasonal_pattern)
            
            return seasonal_forecasts
            
        except Exception as e:
            logger.error(f"Failed to forecast seasonal trends: {e}")
            raise
    
    # === MÉTHODES PRIVÉES ===
    
    async def _analyze_current_trends(
        self, 
        keywords: List[str], 
        timeframe: TrendTimeframe
    ) -> List[TrendData]:
        """Analyser les tendances actuelles"""
        trends = []
        
        for keyword in keywords:
            # Récupérer les données historiques
            historical_data = await self._get_keyword_historical_data(keyword)
            
            if not historical_data:
                continue
            
            # Calculer la direction de la tendance
            direction = await self._calculate_trend_direction(historical_data)
            
            # Calculer le momentum
            momentum = await self._calculate_momentum(historical_data)
            
            # Déterminer le niveau de confiance
            confidence = await self._assess_prediction_confidence(historical_data)
            
            # Évaluer l'impact
            impact_level = await self._assess_impact_level(keyword, momentum)
            
            # Identifier le type de tendance
            trend_type = await self._classify_trend_type(keyword, historical_data)
            
            trend = TrendData(
                name=keyword,
                trend_type=trend_type,
                direction=direction,
                momentum=momentum,
                confidence=confidence,
                timeframe=timeframe,
                impact_level=impact_level,
                current_value=historical_data[-1] if historical_data else 0,
                predicted_value=await self._predict_next_value(historical_data),
                historical_data=historical_data[-30:],  # 30 derniers points
                related_keywords=await self._find_related_keywords(keyword),
                metadata=await self._collect_trend_metadata(keyword)
            )
            
            trends.append(trend)
        
        return trends
    
    async def _generate_trend_predictions(
        self, 
        trends: List[TrendData], 
        timeframe: TrendTimeframe
    ) -> List[TrendPrediction]:
        """Générer des prédictions de tendances"""
        predictions = []
        
        forecast_days = self._get_forecast_days(timeframe)
        
        for trend in trends:
            prediction = await self.predict_keyword_performance(
                trend.name, forecast_days
            )
            predictions.append(prediction)
        
        return predictions
    
    async def _detect_seasonal_patterns(self, keywords: List[str]) -> List[SeasonalPattern]:
        """Détecter les patterns saisonniers"""
        seasonal_patterns = []
        
        for keyword in keywords:
            # Analyser la saisonnalité historique
            patterns = await self._analyze_historical_seasonality(keyword)
            
            for pattern_name, pattern_data in patterns.items():
                if pattern_data["strength"] > 0.3:  # Seuil de significativité
                    pattern = SeasonalPattern(
                        pattern_name=f"{keyword}_{pattern_name}",
                        season_start=pattern_data["start_date"],
                        season_end=pattern_data["end_date"],
                        peak_intensity=pattern_data["peak_intensity"],
                        growth_rate=pattern_data["growth_rate"],
                        historical_strength=pattern_data["strength"],
                        predicted_strength=pattern_data["strength"] * 0.95  # Prédiction conservative
                    )
                    seasonal_patterns.append(pattern)
        
        return seasonal_patterns
    
    async def _identify_emerging_trends(self, keywords: List[str]) -> List[EmergingTrend]:
        """Identifier les tendances émergentes"""
        emerging_trends = []
        
        # Analyser la croissance récente
        for keyword in keywords:
            growth_data = await self._analyze_recent_growth(keyword)
            
            if growth_data["growth_rate"] > self.prediction_config["emergence_threshold"]:
                emerging_trend = EmergingTrend(
                    trend_id=self._generate_trend_id(keyword),
                    discovery_date=datetime.utcnow(),
                    growth_velocity=growth_data["growth_rate"],
                    adoption_rate=growth_data["adoption_rate"],
                    market_penetration=growth_data["market_penetration"],
                    disruption_potential=growth_data["disruption_score"],
                    time_to_mainstream=growth_data["mainstream_timeline"],
                    early_indicators=growth_data["indicators"]
                )
                emerging_trends.append(emerging_trend)
        
        return emerging_trends
    
    async def _get_keyword_historical_data(self, keyword: str) -> List[float]:
        """Récupérer les données historiques d'un mot-clé"""
        # Simulation de données historiques (à remplacer par vraies APIs)
        import random
        
        # Générer des données réalistes avec tendance et saisonnalité
        base_value = random.uniform(1000, 10000)
        trend_factor = random.uniform(0.98, 1.02)
        data = []
        
        for i in range(365):  # 1 an de données
            # Tendance de base
            value = base_value * (trend_factor ** (i / 30))
            
            # Composante saisonnière
            seasonal = 1 + 0.3 * math.sin(2 * math.pi * i / 365)
            value *= seasonal
            
            # Bruit aléatoire
            noise = random.uniform(0.9, 1.1)
            value *= noise
            
            data.append(value)
        
        return data
    
    async def _calculate_trend_direction(self, historical_data: List[float]) -> TrendDirection:
        """Calculer la direction de la tendance"""
        if len(historical_data) < 3:
            return TrendDirection.STABLE
        
        # Calculer la pente de la tendance
        x = list(range(len(historical_data)))
        n = len(historical_data)
        
        slope = ((n * sum(x[i] * historical_data[i] for i in range(n))) - 
                (sum(x) * sum(historical_data))) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        # Calculer la volatilité
        volatility = statistics.stdev(historical_data) / statistics.mean(historical_data)
        
        if volatility > self.prediction_config["volatility_threshold"]:
            return TrendDirection.VOLATILE
        elif slope > 0.1:
            return TrendDirection.RISING
        elif slope < -0.1:
            return TrendDirection.FALLING
        else:
            return TrendDirection.STABLE
    
    async def _calculate_momentum(self, historical_data: List[float]) -> float:
        """Calculer le momentum de la tendance"""
        if len(historical_data) < 10:
            return 0.0
        
        # Comparer les 10 derniers points avec les 10 précédents
        recent_avg = statistics.mean(historical_data[-10:])
        previous_avg = statistics.mean(historical_data[-20:-10])
        
        if previous_avg == 0:
            return 0.0
        
        momentum = (recent_avg - previous_avg) / previous_avg
        return max(-1.0, min(1.0, momentum))  # Normaliser entre -1 et 1
    
    async def _assess_prediction_confidence(self, historical_data: List[float]) -> PredictionConfidence:
        """Évaluer la confiance de prédiction"""
        if len(historical_data) < 30:
            return PredictionConfidence.LOW
        
        # Calculer la régularité des données
        volatility = statistics.stdev(historical_data) / statistics.mean(historical_data)
        
        if volatility < 0.1:
            return PredictionConfidence.VERY_HIGH
        elif volatility < 0.2:
            return PredictionConfidence.HIGH
        elif volatility < 0.3:
            return PredictionConfidence.MEDIUM
        elif volatility < 0.5:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    async def _assess_impact_level(self, keyword: str, momentum: float) -> ImpactLevel:
        """Évaluer le niveau d'impact"""
        abs_momentum = abs(momentum)
        
        if abs_momentum > 0.5:
            return ImpactLevel.GAME_CHANGING
        elif abs_momentum > 0.3:
            return ImpactLevel.HIGH_IMPACT
        elif abs_momentum > 0.1:
            return ImpactLevel.MODERATE_IMPACT
        elif abs_momentum > 0.05:
            return ImpactLevel.LOW_IMPACT
        else:
            return ImpactLevel.MINIMAL_IMPACT
    
    async def _classify_trend_type(self, keyword: str, historical_data: List[float]) -> TrendType:
        """Classifier le type de tendance"""
        # Analyse simple basée sur des patterns (à améliorer avec ML)
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ["new", "emerging", "latest"]):
            return TrendType.EMERGING_TREND
        elif any(word in keyword_lower for word in ["seasonal", "holiday", "christmas", "summer"]):
            return TrendType.SEASONAL_TREND
        elif any(word in keyword_lower for word in ["vs", "comparison", "alternative"]):
            return TrendType.COMPETITIVE_TREND
        elif any(word in keyword_lower for word in ["ai", "tech", "digital", "app"]):
            return TrendType.TECHNOLOGY_TREND
        else:
            return TrendType.KEYWORD_TREND
    
    async def _predict_next_value(self, historical_data: List[float]) -> float:
        """Prédire la prochaine valeur"""
        if not historical_data:
            return 0.0
        
        # Prédiction simple basée sur la moyenne mobile
        if len(historical_data) >= 5:
            return statistics.mean(historical_data[-5:])
        else:
            return historical_data[-1]
    
    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Trouver des mots-clés liés"""
        # Simulation de mots-clés liés
        variations = [
            f"{keyword} tips",
            f"{keyword} guide",
            f"best {keyword}",
            f"{keyword} 2025",
            f"how to {keyword}"
        ]
        return variations[:3]
    
    async def _collect_trend_metadata(self, keyword: str) -> Dict[str, Any]:
        """Collecter les métadonnées de tendance"""
        return {
            "search_volume": 5000,
            "competition": 0.65,
            "cpc": 2.5,
            "region": "global",
            "category": "general"
        }
    
    def _get_forecast_days(self, timeframe: TrendTimeframe) -> int:
        """Obtenir le nombre de jours pour la prévision"""
        mapping = {
            TrendTimeframe.SHORT_TERM: 90,
            TrendTimeframe.MEDIUM_TERM: 180,
            TrendTimeframe.LONG_TERM: 365,
            TrendTimeframe.STRATEGIC: 1095
        }
        return mapping.get(timeframe, 180)
    
    async def _generate_strategic_recommendations(
        self, 
        trends: List[TrendData], 
        predictions: List[TrendPrediction],
        emerging_trends: List[EmergingTrend]
    ) -> List[str]:
        """Générer des recommandations stratégiques"""
        recommendations = []
        
        # Analyser les tendances montantes
        rising_trends = [t for t in trends if t.direction == TrendDirection.RISING]
        if rising_trends:
            top_rising = max(rising_trends, key=lambda x: x.momentum)
            recommendations.append(
                f"Capitalize on rising trend: {top_rising.name} (momentum: {top_rising.momentum:.2f})"
            )
        
        # Analyser les opportunités émergentes
        if emerging_trends:
            top_emerging = max(emerging_trends, key=lambda x: x.growth_velocity)
            recommendations.append(
                f"Early adoption opportunity: {top_emerging.trend_id} (growth: {top_emerging.growth_velocity:.2f}x)"
            )
        
        # Recommandations basées sur les prédictions
        high_confidence_predictions = [
            p for p in predictions 
            if p.opportunity_score > 7.0
        ]
        
        if high_confidence_predictions:
            recommendations.append(
                f"High-opportunity keywords identified: {len(high_confidence_predictions)} candidates"
            )
        
        return recommendations
    
    async def _analyze_market_insights(
        self, 
        trends: List[TrendData], 
        predictions: List[TrendPrediction]
    ) -> Dict[str, Any]:
        """Analyser les insights du marché"""
        total_trends = len(trends)
        rising_trends = len([t for t in trends if t.direction == TrendDirection.RISING])
        high_impact_trends = len([t for t in trends if t.impact_level in [ImpactLevel.HIGH_IMPACT, ImpactLevel.GAME_CHANGING]])
        
        avg_opportunity_score = statistics.mean([p.opportunity_score for p in predictions]) if predictions else 0
        
        return {
            "market_momentum": "positive" if rising_trends > total_trends / 2 else "mixed",
            "total_trends_analyzed": total_trends,
            "rising_trends_percentage": (rising_trends / total_trends * 100) if total_trends > 0 else 0,
            "high_impact_trends": high_impact_trends,
            "average_opportunity_score": avg_opportunity_score,
            "market_volatility": "moderate",
            "strategic_outlook": "Growth opportunities identified"
        }
    
    async def _calculate_confidence_score(
        self, 
        predictions: List[TrendPrediction], 
        trends: List[TrendData]
    ) -> float:
        """Calculer le score de confiance global"""
        if not predictions:
            return 0.0
        
        confidence_values = []
        for trend in trends:
            if trend.confidence == PredictionConfidence.VERY_HIGH:
                confidence_values.append(0.95)
            elif trend.confidence == PredictionConfidence.HIGH:
                confidence_values.append(0.82)
            elif trend.confidence == PredictionConfidence.MEDIUM:
                confidence_values.append(0.67)
            elif trend.confidence == PredictionConfidence.LOW:
                confidence_values.append(0.50)
            else:
                confidence_values.append(0.30)
        
        return statistics.mean(confidence_values) if confidence_values else 0.0
    
    async def _store_analysis_results(self, result: TrendAnalysisResult):
        """Stocker les résultats pour l'apprentissage"""
        # Stocker pour améliorer les prédictions futures
        for trend in result.analyzed_trends:
            self.trends_database[trend.name].append({
                "date": result.analysis_date,
                "value": trend.current_value,
                "direction": trend.direction,
                "momentum": trend.momentum
            })
    
    # Méthodes de prédiction avancées (simplifiées)
    
    async def _extract_seasonal_component(self, keyword: str, data: List[float]) -> List[float]:
        """Extraire la composante saisonnière"""
        # Décomposition simple (à améliorer avec des méthodes avancées)
        seasonal = []
        for i in range(len(data)):
            seasonal_value = 1 + 0.2 * math.sin(2 * math.pi * i / 365)
            seasonal.append(seasonal_value)
        return seasonal
    
    async def _calculate_base_trend(self, data: List[float]) -> float:
        """Calculer la tendance de base"""
        if len(data) < 2:
            return 0.0
        
        # Régression linéaire simple
        x = list(range(len(data)))
        n = len(data)
        
        slope = ((n * sum(x[i] * data[i] for i in range(n))) - 
                (sum(x) * sum(data))) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        return slope
    
    async def _generate_keyword_forecast(
        self, 
        historical: List[float], 
        trend: float, 
        seasonal: List[float], 
        days: int
    ) -> List[float]:
        """Générer une prévision pour un mot-clé"""
        forecast = []
        last_value = historical[-1] if historical else 1000
        
        for i in range(days):
            # Tendance de base
            trend_component = last_value + (trend * i)
            
            # Composante saisonnière
            seasonal_index = (len(historical) + i) % 365
            seasonal_component = seasonal[seasonal_index] if seasonal_index < len(seasonal) else 1.0
            
            # Valeur prédite
            predicted_value = trend_component * seasonal_component
            forecast.append(max(0, predicted_value))
        
        return forecast
    
    async def _calculate_confidence_intervals(
        self, 
        predictions: List[float], 
        historical: List[float]
    ) -> List[Tuple[float, float]]:
        """Calculer les intervalles de confiance"""
        if not historical:
            return [(p * 0.8, p * 1.2) for p in predictions]
        
        # Estimer l'erreur basée sur les données historiques
        volatility = statistics.stdev(historical) / statistics.mean(historical)
        
        intervals = []
        for pred in predictions:
            error_margin = pred * volatility
            lower_bound = max(0, pred - error_margin)
            upper_bound = pred + error_margin
            intervals.append((lower_bound, upper_bound))
        
        return intervals
    
    def _generate_trend_id(self, signal: Any) -> str:
        """Générer un ID unique pour une tendance"""
        signal_str = str(signal)
        return hashlib.md5(signal_str.encode()).hexdigest()[:8]
    
    # Autres méthodes simplifiées...
    async def _generate_prediction_scenarios(self, keyword: str, predictions: List[float]) -> Dict[str, float]:
        return {"optimistic": 0.3, "realistic": 0.5, "pessimistic": 0.2}
    
    async def _identify_trend_drivers(self, keyword: str, data: List[float]) -> List[str]:
        return ["Market demand", "Seasonal patterns", "Competitive landscape"]
    
    async def _analyze_risk_factors(self, keyword: str, predictions: List[float]) -> List[str]:
        return ["Market volatility", "Algorithm changes", "Competitive pressure"]
    
    async def _calculate_opportunity_score(self, keyword: str, predictions: List[float], historical: List[float]) -> float:
        growth_potential = (predictions[-1] / historical[-1]) if historical and historical[-1] > 0 else 1.0
        return min(10.0, max(0.0, growth_potential * 3))
    
    async def _scan_emerging_signals(self, industry: str) -> List[Dict[str, Any]]:
        return [{"name": "emerging_trend_1", "data": [1, 2, 4, 8, 16]}]
    
    async def _calculate_growth_velocity(self, signal: Dict[str, Any]) -> float:
        data = signal.get("data", [1, 1])
        return data[-1] / data[0] if data[0] > 0 else 1.0
    
    async def _calculate_adoption_rate(self, signal: Dict[str, Any]) -> float:
        return 0.25  # 25% adoption simulée
    
    async def _calculate_market_penetration(self, signal: Dict[str, Any]) -> float:
        return 0.15  # 15% penetration simulée
    
    async def _assess_disruption_potential(self, signal: Dict[str, Any]) -> float:
        return 0.7  # 70% potentiel de disruption
    
    async def _estimate_mainstream_timeline(self, signal: Dict[str, Any], velocity: float, adoption: float) -> int:
        return int(365 / velocity)  # Jours jusqu'au mainstream
    
    async def _identify_early_indicators(self, signal: Dict[str, Any]) -> List[str]:
        return ["Increasing search volume", "Social media mentions", "Industry publications"]
    
    async def _analyze_historical_seasonality(self, keyword: str) -> Dict[str, Any]:
        return {
            "holiday_season": {
                "strength": 0.8,
                "peak_intensity": 2.5,
                "growth_rate": 0.15,
                "start_date": datetime(2025, 11, 1),
                "end_date": datetime(2025, 12, 31),
                "avg_strength": 0.75
            }
        }
    
    async def _predict_seasonal_strength(self, keyword: str, pattern: str, data: Dict[str, Any], year: int) -> float:
        return data.get("avg_strength", 0.5) * 0.95  # Prédiction conservative
    
    async def _calculate_season_dates(self, pattern: str, year: int) -> Dict[str, datetime]:
        return {
            "start": datetime(year, 11, 1),
            "end": datetime(year, 12, 31)
        }
    
    async def _analyze_recent_growth(self, keyword: str) -> Dict[str, Any]:
        return {
            "growth_rate": 1.8,
            "adoption_rate": 0.3,
            "market_penetration": 0.2,
            "disruption_score": 0.6,
            "mainstream_timeline": 180,
            "indicators": ["Rising search volume", "New content creation"]
        }


# === TREND ANALYZER ===

class TrendAnalyzer:
    """
    📊 Analyseur de Tendances Avancé
    
    Analyse technique des tendances avec algorithmes
    de détection de patterns et scoring d'opportunités.
    """
    
    def __init__(self):
        self.pattern_detectors = {}
        self.scoring_algorithms = {}
        
        logger.info("📊 Trend Analyzer initialized")
    
    async def analyze_trend_patterns(self, trend_data: List[TrendData]) -> Dict[str, Any]:
        """Analyser les patterns de tendances"""
        patterns = {
            "momentum_clusters": await self._detect_momentum_clusters(trend_data),
            "direction_patterns": await self._analyze_direction_patterns(trend_data),
            "impact_distribution": await self._analyze_impact_distribution(trend_data),
            "confidence_analysis": await self._analyze_confidence_levels(trend_data)
        }
        
        return patterns
    
    async def _detect_momentum_clusters(self, trends: List[TrendData]) -> Dict[str, List[str]]:
        """Détecter les clusters de momentum"""
        high_momentum = [t.name for t in trends if t.momentum > 0.3]
        medium_momentum = [t.name for t in trends if 0.1 <= t.momentum <= 0.3]
        low_momentum = [t.name for t in trends if t.momentum < 0.1]
        
        return {
            "high_momentum": high_momentum,
            "medium_momentum": medium_momentum,
            "low_momentum": low_momentum
        }
    
    async def _analyze_direction_patterns(self, trends: List[TrendData]) -> Dict[str, int]:
        """Analyser les patterns de direction"""
        direction_counts = defaultdict(int)
        for trend in trends:
            direction_counts[trend.direction.value] += 1
        
        return dict(direction_counts)
    
    async def _analyze_impact_distribution(self, trends: List[TrendData]) -> Dict[str, int]:
        """Analyser la distribution des impacts"""
        impact_counts = defaultdict(int)
        for trend in trends:
            impact_counts[trend.impact_level.value] += 1
        
        return dict(impact_counts)
    
    async def _analyze_confidence_levels(self, trends: List[TrendData]) -> Dict[str, float]:
        """Analyser les niveaux de confiance"""
        confidence_mapping = {
            PredictionConfidence.VERY_HIGH: 0.95,
            PredictionConfidence.HIGH: 0.82,
            PredictionConfidence.MEDIUM: 0.67,
            PredictionConfidence.LOW: 0.50,
            PredictionConfidence.VERY_LOW: 0.30
        }
        
        confidence_values = [confidence_mapping[t.confidence] for t in trends]
        
        return {
            "average_confidence": statistics.mean(confidence_values) if confidence_values else 0,
            "confidence_variance": statistics.variance(confidence_values) if len(confidence_values) > 1 else 0,
            "high_confidence_percentage": len([c for c in confidence_values if c >= 0.8]) / len(confidence_values) * 100 if confidence_values else 0
        }


# Export des classes principales
__all__ = [
    "SEOTrendsPredictor", "TrendAnalyzer",
    "TrendData", "TrendPrediction", "SeasonalPattern", "EmergingTrend",
    "TrendAnalysisResult", "TrendType", "TrendDirection", "PredictionConfidence",
    "TrendTimeframe", "ImpactLevel"
]
