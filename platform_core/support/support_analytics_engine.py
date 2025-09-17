"""🚀 Support Analytics Engine - Business Intelligence Enterprise
================================================================
Module: backend/platform_core/support/support_analytics_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🧠 ANALYTICS ENGINE SUPPORT AVEC ML & BI ENTERPRISE
Système intelligence artificielle pour analytics support
- Analytics satisfaction client avec sentiment ML
- Prédiction churn basée comportement support
- Performance metrics agents temps réel
- Insights amélioration processus support automatisés
- Reporting exécutif avec visualisations avancées
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

logger = logging.getLogger(__name__)


class AnalyticsMetricType(Enum):
    """Types métriques analytics"""
    SATISFACTION_SCORE = "satisfaction_score"
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    CHURN_PROBABILITY = "churn_probability"
    AGENT_PERFORMANCE = "agent_performance"
    TICKET_VOLUME = "ticket_volume"
    ESCALATION_RATE = "escalation_rate"
    FIRST_CONTACT_RESOLUTION = "first_contact_resolution"


class ChurnRiskLevel(Enum):
    """Niveaux risque churn"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerformanceGrade(Enum):
    """Grades performance agent"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 80-89%
    AVERAGE = "average"     # 70-79%
    BELOW_AVERAGE = "below_average"  # 60-69%
    POOR = "poor"           # <60%


@dataclass
class SupportInteraction:
    """Interaction support pour analytics"""
    interaction_id: str
    creator_id: str
    creator_type: str
    creator_tier: str
    agent_id: Optional[str]
    ticket_id: Optional[str]
    interaction_type: str  # chat, ticket, call
    started_at: datetime
    ended_at: Optional[datetime]
    resolution_time: Optional[timedelta]
    satisfaction_score: Optional[float]
    sentiment_score: float
    escalated: bool = False
    resolved_first_contact: bool = False
    tags: List[str] = field(default_factory=list)
    language: str = "en"


@dataclass
class CreatorSupportProfile:
    """Profil support créateur avec historique"""
    creator_id: str
    creator_type: str
    creator_tier: str
    total_interactions: int
    avg_satisfaction: float
    avg_resolution_time: timedelta
    escalation_rate: float
    churn_risk_score: float
    churn_risk_level: ChurnRiskLevel
    last_interaction: datetime
    preferred_language: str
    common_issues: List[str] = field(default_factory=list)
    support_trends: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPerformanceMetrics:
    """Métriques performance agent"""
    agent_id: str
    agent_name: str
    specialty: str
    total_interactions: int
    avg_satisfaction: float
    avg_response_time: timedelta
    avg_resolution_time: timedelta
    first_contact_resolution_rate: float
    escalation_rate: float
    performance_grade: PerformanceGrade
    workload_efficiency: float
    language_proficiency: Dict[str, float]
    creator_type_expertise: Dict[str, float]
    improvement_areas: List[str] = field(default_factory=list)


class SupportAnalyticsEngine:
    """📊 Support Analytics Engine Enterprise
    
    Moteur analytics ML-powered pour support:
    - Analyse satisfaction client avec ML sentiment
    - Prédiction churn comportemental avancée
    - Performance tracking agents temps réel
    - Insights automatisés amélioration processus
    - Reporting BI exécutif avec visualisations
    """
    
    def __init__(self):
        self.interactions_db: List[SupportInteraction] = []
        self.creator_profiles: Dict[str, CreatorSupportProfile] = {}
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        
        # Modèles ML
        self.churn_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.satisfaction_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Analytics temps réel
        self.real_time_metrics = {
            "current_satisfaction": 0.0,
            "active_interactions": 0,
            "avg_response_time": timedelta(),
            "daily_ticket_volume": 0,
            "escalation_rate_today": 0.0
        }
        
        # Configuration seuils
        self.satisfaction_thresholds = {
            "excellent": 4.5,
            "good": 4.0,
            "average": 3.5,
            "poor": 3.0
        }
        
        self.churn_thresholds = {
            ChurnRiskLevel.LOW: 0.2,
            ChurnRiskLevel.MEDIUM: 0.4,
            ChurnRiskLevel.HIGH: 0.6,
            ChurnRiskLevel.CRITICAL: 0.8
        }

    async def initialize_analytics_engine(self, historical_data: List[Dict[str, Any]] = None) -> None:
        """🚀 Initialisation moteur analytics avec données historiques"""
        try:
            if historical_data:
                # Conversion données historiques
                for data in historical_data:
                    interaction = self._convert_to_interaction(data)
                    self.interactions_db.append(interaction)
                    
                # Entraînement modèles ML initiaux
                await self._train_ml_models()
                
                # Génération profils créateurs
                await self._generate_creator_profiles()
                
                # Calcul métriques agents
                await self._calculate_agent_metrics()
                
            logger.info(f"Analytics engine initialisé avec {len(self.interactions_db)} interactions")
            
        except Exception as e:
            logger.error(f"Erreur initialisation analytics: {e}")

    async def analyze_customer_satisfaction(
        self, 
        creator_id: str = None,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """😊 Analyse satisfaction client avec ML sentiment
        
        Args:
            creator_id: ID créateur spécifique (optionnel)
            time_period: Période analyse
            
        Returns:
            Dict: Analytics satisfaction détaillées
        """
        try:
            # Filtrage interactions par période
            cutoff_date = datetime.utcnow() - time_period
            relevant_interactions = [
                i for i in self.interactions_db 
                if i.started_at >= cutoff_date and 
                (not creator_id or i.creator_id == creator_id)
            ]
            
            if not relevant_interactions:
                return {"status": "no_data", "period": str(time_period)}
                
            # Métriques satisfaction de base
            satisfaction_scores = [i.satisfaction_score for i in relevant_interactions if i.satisfaction_score]
            sentiment_scores = [i.sentiment_score for i in relevant_interactions]
            
            avg_satisfaction = np.mean(satisfaction_scores) if satisfaction_scores else 0.0
            avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.0
            
            # Distribution satisfaction
            satisfaction_distribution = self._calculate_satisfaction_distribution(satisfaction_scores)
            
            # Trends temporelles
            satisfaction_trends = await self._analyze_satisfaction_trends(relevant_interactions)
            
            # Facteurs influence satisfaction
            satisfaction_factors = await self._identify_satisfaction_factors(relevant_interactions)
            
            # Prédictions satisfaction future
            satisfaction_predictions = await self._predict_future_satisfaction(relevant_interactions)
            
            # Analyse par segments
            segment_analysis = await self._analyze_satisfaction_by_segments(relevant_interactions)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "period_analyzed": str(time_period),
                "creator_id": creator_id,
                "total_interactions": len(relevant_interactions),
                
                # Métriques principales
                "avg_satisfaction_score": round(avg_satisfaction, 2),
                "avg_sentiment_score": round(avg_sentiment, 2),
                "satisfaction_grade": self._grade_satisfaction(avg_satisfaction),
                
                # Distributions
                "satisfaction_distribution": satisfaction_distribution,
                "trends": satisfaction_trends,
                "influencing_factors": satisfaction_factors,
                "predictions": satisfaction_predictions,
                "segment_analysis": segment_analysis,
                
                # Insights & recommandations
                "insights": await self._generate_satisfaction_insights(
                    avg_satisfaction, satisfaction_trends, satisfaction_factors
                ),
                "improvement_recommendations": await self._generate_satisfaction_recommendations(
                    relevant_interactions, satisfaction_factors
                )
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse satisfaction: {e}")
            return {"error": str(e)}

    async def predict_churn_risk(self, creator_id: str) -> Dict[str, Any]:
        """🚨 Prédiction risque churn ML avec facteurs comportementaux
        
        Args:
            creator_id: ID créateur à analyser
            
        Returns:
            Dict: Prédiction churn avec facteurs risque
        """
        try:
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                return {"error": "Creator profile not found"}
                
            # Features pour prédiction churn
            features = await self._extract_churn_features(creator_id)
            
            if not features:
                return {"error": "Insufficient data for prediction"}
                
            # Prédiction avec modèle ML
            churn_probability = await self._predict_churn_probability(features)
            churn_risk_level = self._classify_churn_risk(churn_probability)
            
            # Facteurs contribuant au risque
            risk_factors = await self._identify_churn_risk_factors(creator_id, features)
            
            # Interventions recommandées
            recommended_interventions = await self._recommend_churn_interventions(
                churn_risk_level, risk_factors, creator_profile
            )
            
            # Timeline prédiction
            churn_timeline = await self._predict_churn_timeline(churn_probability, creator_profile)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "creator_id": creator_id,
                "creator_type": creator_profile.creator_type,
                "creator_tier": creator_profile.creator_tier,
                
                # Prédiction principale
                "churn_probability": round(churn_probability, 3),
                "churn_risk_level": churn_risk_level.value,
                "confidence_score": await self._calculate_prediction_confidence(features),
                
                # Facteurs détaillés
                "risk_factors": risk_factors,
                "protective_factors": await self._identify_protective_factors(creator_id),
                
                # Timeline & interventions
                "predicted_timeline": churn_timeline,
                "recommended_interventions": recommended_interventions,
                "intervention_priority": self._prioritize_interventions(recommended_interventions),
                
                # Contexte historique
                "historical_context": {
                    "total_interactions": creator_profile.total_interactions,
                    "avg_satisfaction": creator_profile.avg_satisfaction,
                    "last_interaction": creator_profile.last_interaction.isoformat(),
                    "escalation_rate": creator_profile.escalation_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction churn: {e}")
            return {"error": str(e)}

    async def measure_agent_performance(
        self, 
        agent_id: str = None,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """👨‍💼 Mesure performance agents avec analytics avancées
        
        Args:
            agent_id: ID agent spécifique (optionnel)
            time_period: Période évaluation
            
        Returns:
            Dict: Métriques performance détaillées
        """
        try:
            # Filtrage interactions par agent/période
            cutoff_date = datetime.utcnow() - time_period
            relevant_interactions = [
                i for i in self.interactions_db 
                if i.started_at >= cutoff_date and 
                i.agent_id and
                (not agent_id or i.agent_id == agent_id)
            ]
            
            if not relevant_interactions:
                return {"status": "no_data", "period": str(time_period)}
                
            # Performance par agent ou global
            if agent_id:
                performance_data = await self._calculate_individual_agent_performance(
                    agent_id, relevant_interactions
                )
            else:
                performance_data = await self._calculate_team_performance(relevant_interactions)
                
            # Benchmarking
            benchmarks = await self._get_performance_benchmarks()
            
            # Tendances performance
            performance_trends = await self._analyze_performance_trends(
                relevant_interactions, agent_id
            )
            
            # Insights amélioration
            improvement_insights = await self._generate_performance_insights(
                performance_data, benchmarks, performance_trends
            )
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "period_analyzed": str(time_period),
                "agent_id": agent_id,
                "total_interactions": len(relevant_interactions),
                
                "performance_data": performance_data,
                "benchmarks": benchmarks,
                "trends": performance_trends,
                "insights": improvement_insights,
                
                # Recommandations spécifiques
                "training_recommendations": await self._recommend_agent_training(
                    performance_data, benchmarks
                ),
                "process_improvements": await self._suggest_process_improvements(
                    performance_data, relevant_interactions
                )
            }
            
        except Exception as e:
            logger.error(f"Erreur mesure performance: {e}")
            return {"error": str(e)}

    async def generate_improvement_insights(
        self, 
        analysis_scope: str = "comprehensive"
    ) -> Dict[str, Any]:
        """💡 Génération insights amélioration processus automatisés
        
        Args:
            analysis_scope: Portée analyse (comprehensive, satisfaction, performance, etc.)
            
        Returns:
            Dict: Insights et recommandations détaillées
        """
        try:
            insights = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_scope": analysis_scope,
                "insights_generated": []
            }
            
            if analysis_scope in ["comprehensive", "satisfaction"]:
                satisfaction_insights = await self._generate_satisfaction_improvement_insights()
                insights["insights_generated"].extend(satisfaction_insights)
                
            if analysis_scope in ["comprehensive", "efficiency"]:
                efficiency_insights = await self._generate_efficiency_insights()
                insights["insights_generated"].extend(efficiency_insights)
                
            if analysis_scope in ["comprehensive", "quality"]:
                quality_insights = await self._generate_quality_insights()
                insights["insights_generated"].extend(quality_insights)
                
            if analysis_scope in ["comprehensive", "resource"]:
                resource_insights = await self._generate_resource_optimization_insights()
                insights["insights_generated"].extend(resource_insights)
                
            # Priorisation insights
            insights["prioritized_insights"] = self._prioritize_insights(
                insights["insights_generated"]
            )
            
            # ROI estimé des améliorations
            insights["roi_estimates"] = await self._estimate_improvement_roi(
                insights["insights_generated"]
            )
            
            # Plan d'action recommandé
            insights["action_plan"] = await self._generate_action_plan(
                insights["prioritized_insights"]
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {e}")
            return {"error": str(e)}

    async def _train_ml_models(self) -> None:
        """🤖 Entraînement modèles ML pour analytics"""
        try:
            if len(self.interactions_db) < 50:  # Minimum pour entraînement
                logger.warning("Données insuffisantes pour entraînement ML")
                return
                
            # Préparation données churn
            churn_features, churn_labels = await self._prepare_churn_training_data()
            
            if len(churn_features) > 10:
                # Entraînement modèle churn
                X_train, X_test, y_train, y_test = train_test_split(
                    churn_features, churn_labels, test_size=0.2, random_state=42
                )
                
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                self.churn_model.fit(X_train_scaled, y_train)
                
                # Validation modèle
                y_pred = self.churn_model.predict(X_test_scaled)
                logger.info(f"Modèle churn entraîné - Accuracy: {np.mean(y_pred == y_test):.2f}")
                
            # Préparation données satisfaction
            satisfaction_features, satisfaction_labels = await self._prepare_satisfaction_training_data()
            
            if len(satisfaction_features) > 10:
                # Entraînement modèle satisfaction
                X_train, X_test, y_train, y_test = train_test_split(
                    satisfaction_features, satisfaction_labels, test_size=0.2, random_state=42
                )
                
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)
                
                self.satisfaction_model.fit(X_train_scaled, y_train)
                
                # Validation modèle
                y_pred = self.satisfaction_model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                logger.info(f"Modèle satisfaction entraîné - MSE: {mse:.3f}")
                
        except Exception as e:
            logger.error(f"Erreur entraînement ML: {e}")

    async def _extract_churn_features(self, creator_id: str) -> Optional[List[float]]:
        """🔍 Extraction features pour prédiction churn"""
        try:
            creator_interactions = [i for i in self.interactions_db if i.creator_id == creator_id]
            
            if not creator_interactions:
                return None
                
            # Features comportementales
            total_interactions = len(creator_interactions)
            avg_satisfaction = np.mean([i.satisfaction_score for i in creator_interactions if i.satisfaction_score])
            avg_sentiment = np.mean([i.sentiment_score for i in creator_interactions])
            escalation_rate = len([i for i in creator_interactions if i.escalated]) / total_interactions
            
            # Features temporelles
            last_interaction = max([i.started_at for i in creator_interactions])
            days_since_last = (datetime.utcnow() - last_interaction).days
            
            # Features résolution
            resolved_interactions = [i for i in creator_interactions if i.resolution_time]
            avg_resolution_time = np.mean([
                i.resolution_time.total_seconds() / 3600 for i in resolved_interactions
            ]) if resolved_interactions else 0
            
            first_contact_rate = len([i for i in creator_interactions if i.resolved_first_contact]) / total_interactions
            
            # Features engagement
            interaction_frequency = total_interactions / max(1, (datetime.utcnow() - creator_interactions[0].started_at).days)
            
            # Création vector features
            features = [
                total_interactions,
                avg_satisfaction if not np.isnan(avg_satisfaction) else 3.0,
                avg_sentiment,
                escalation_rate,
                days_since_last,
                avg_resolution_time,
                first_contact_rate,
                interaction_frequency
            ]
            
            return features
            
        except Exception as e:
            logger.error(f"Erreur extraction features churn: {e}")
            return None

    async def _predict_churn_probability(self, features: List[float]) -> float:
        """🎯 Prédiction probabilité churn avec ML"""
        try:
            # Normalisation features
            features_array = np.array(features).reshape(1, -1)
            features_scaled = self.scaler.transform(features_array)
            
            # Prédiction avec modèle
            if hasattr(self.churn_model, 'predict_proba'):
                churn_prob = self.churn_model.predict_proba(features_scaled)[0][1]
            else:
                # Fallback: calcul heuristique
                churn_prob = self._calculate_heuristic_churn_probability(features)
                
            return float(churn_prob)
            
        except Exception as e:
            logger.error(f"Erreur prédiction churn: {e}")
            return 0.5  # Valeur neutre par défaut

    def _calculate_heuristic_churn_probability(self, features: List[float]) -> float:
        """📊 Calcul heuristique probabilité churn"""
        try:
            # Poids features pour churn
            total_interactions, avg_satisfaction, avg_sentiment, escalation_rate, \
            days_since_last, avg_resolution_time, first_contact_rate, interaction_frequency = features
            
            churn_score = 0.0
            
            # Facteurs négatifs (augmentent churn)
            if avg_satisfaction < 3.0:
                churn_score += 0.3
            elif avg_satisfaction < 3.5:
                churn_score += 0.15
                
            if avg_sentiment < -0.2:
                churn_score += 0.2
                
            if escalation_rate > 0.3:
                churn_score += 0.2
                
            if days_since_last > 60:
                churn_score += 0.3
            elif days_since_last > 30:
                churn_score += 0.15
                
            if first_contact_rate < 0.5:
                churn_score += 0.15
                
            # Facteurs positifs (réduisent churn)
            if avg_satisfaction > 4.0:
                churn_score -= 0.2
                
            if interaction_frequency > 0.5:  # Plus d'une interaction tous les 2 jours
                churn_score -= 0.1
                
            return max(0.0, min(1.0, churn_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul heuristique: {e}")
            return 0.5

    def _classify_churn_risk(self, churn_probability: float) -> ChurnRiskLevel:
        """📊 Classification niveau risque churn"""
        if churn_probability >= 0.8:
            return ChurnRiskLevel.CRITICAL
        elif churn_probability >= 0.6:
            return ChurnRiskLevel.HIGH
        elif churn_probability >= 0.4:
            return ChurnRiskLevel.MEDIUM
        else:
            return ChurnRiskLevel.LOW

    def _convert_to_interaction(self, data: Dict[str, Any]) -> SupportInteraction:
        """🔄 Conversion données vers objet interaction"""
        return SupportInteraction(
            interaction_id=data.get("id", str(uuid.uuid4())),
            creator_id=data["creator_id"],
            creator_type=data.get("creator_type", "general"),
            creator_tier=data.get("creator_tier", "free"),
            agent_id=data.get("agent_id"),
            ticket_id=data.get("ticket_id"),
            interaction_type=data.get("type", "ticket"),
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            satisfaction_score=data.get("satisfaction_score"),
            sentiment_score=data.get("sentiment_score", 0.0),
            escalated=data.get("escalated", False),
            resolved_first_contact=data.get("resolved_first_contact", False),
            language=data.get("language", "en")
        )

    def _calculate_satisfaction_distribution(self, scores: List[float]) -> Dict[str, float]:
        """📊 Distribution scores satisfaction"""
        if not scores:
            return {}
            
        total = len(scores)
        return {
            "excellent": len([s for s in scores if s >= 4.5]) / total * 100,
            "good": len([s for s in scores if 4.0 <= s < 4.5]) / total * 100,
            "average": len([s for s in scores if 3.5 <= s < 4.0]) / total * 100,
            "poor": len([s for s in scores if s < 3.5]) / total * 100
        }

    def _grade_satisfaction(self, avg_satisfaction: float) -> str:
        """⭐ Attribution grade satisfaction"""
        if avg_satisfaction >= self.satisfaction_thresholds["excellent"]:
            return "excellent"
        elif avg_satisfaction >= self.satisfaction_thresholds["good"]:
            return "good"
        elif avg_satisfaction >= self.satisfaction_thresholds["average"]:
            return "average"
        else:
            return "poor"

    async def _analyze_satisfaction_trends(self, interactions: List[SupportInteraction]) -> Dict[str, Any]:
        """📈 Analyse tendances satisfaction temporelles"""
        if len(interactions) < 10:
            return {"status": "insufficient_data"}
            
        # Groupage par semaine
        df = pd.DataFrame([{
            "date": i.started_at.date(),
            "satisfaction": i.satisfaction_score,
            "sentiment": i.sentiment_score
        } for i in interactions if i.satisfaction_score])
        
        if df.empty:
            return {"status": "no_satisfaction_data"}
            
        # Moyenne mobile sur 7 jours
        df_grouped = df.groupby("date").agg({
            "satisfaction": "mean",
            "sentiment": "mean"
        }).reset_index()
        
        df_grouped["satisfaction_ma"] = df_grouped["satisfaction"].rolling(window=7).mean()
        
        # Détection tendance
        recent_avg = df_grouped["satisfaction_ma"].tail(7).mean()
        older_avg = df_grouped["satisfaction_ma"].head(7).mean()
        
        if recent_avg > older_avg + 0.2:
            trend = "improving"
        elif recent_avg < older_avg - 0.2:
            trend = "declining"
        else:
            trend = "stable"
            
        return {
            "trend": trend,
            "recent_average": round(recent_avg, 2),
            "change_magnitude": round(recent_avg - older_avg, 2),
            "data_points": len(df_grouped)
        }

    async def _prepare_churn_training_data(self) -> Tuple[List[List[float]], List[int]]:
        """📚 Préparation données entraînement churn"""
        features = []
        labels = []
        
        # Groupage par créateur
        creators = set(i.creator_id for i in self.interactions_db)
        
        for creator_id in creators:
            creator_features = await self._extract_churn_features(creator_id)
            if creator_features:
                features.append(creator_features)
                
                # Label churn (simulation basée inactivité)
                creator_interactions = [i for i in self.interactions_db if i.creator_id == creator_id]
                last_interaction = max(i.started_at for i in creator_interactions)
                days_inactive = (datetime.utcnow() - last_interaction).days
                
                # Créateur "churned" si inactif > 90 jours et satisfaction < 3.5
                avg_satisfaction = np.mean([i.satisfaction_score for i in creator_interactions if i.satisfaction_score])
                churned = days_inactive > 90 and avg_satisfaction < 3.5
                labels.append(1 if churned else 0)
                
        return features, labels

    async def _prepare_satisfaction_training_data(self) -> Tuple[List[List[float]], List[float]]:
        """📚 Préparation données entraînement satisfaction"""
        features = []
        labels = []
        
        for interaction in self.interactions_db:
            if interaction.satisfaction_score is None:
                continue
                
            # Features interaction
            interaction_features = [
                interaction.sentiment_score,
                1 if interaction.escalated else 0,
                interaction.resolution_time.total_seconds() / 3600 if interaction.resolution_time else 0,
                1 if interaction.resolved_first_contact else 0,
                len(interaction.tags),
                1 if interaction.creator_tier == "enterprise" else 0.5 if interaction.creator_tier == "pro" else 0
            ]
            
            features.append(interaction_features)
            labels.append(interaction.satisfaction_score)
            
        return features, labels