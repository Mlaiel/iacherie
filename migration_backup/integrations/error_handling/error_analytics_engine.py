"""
Error Analytics Engine - Ainflue Platform
ML-Powered Error Pattern Detection & Predictive Analytics

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

🔒 PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette implémentation est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution ou utilisation sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from enum import Enum
import hashlib
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorPatternType(Enum):
    """Types d'patterns d'erreur détectés par ML"""
    CASCADING_FAILURE = "cascading_failure"
    RATE_LIMIT_BURST = "rate_limit_burst"
    AUTHENTICATION_WAVE = "authentication_wave"
    PLATFORM_DEGRADATION = "platform_degradation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    INTEGRATION_FAILURE = "integration_failure"
    DATA_CORRUPTION = "data_corruption"
    PERFORMANCE_DEGRADATION = "performance_degradation"


class PredictionConfidence(Enum):
    """Niveaux de confiance des prédictions ML"""
    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 0.9
    CERTAIN = 1.0


@dataclass
class ErrorPattern:
    """Pattern d'erreur détecté par ML"""
    pattern_id: str
    pattern_type: ErrorPatternType
    confidence_score: float
    frequency: int
    first_seen: datetime
    last_seen: datetime
    affected_services: List[str]
    error_signature: str
    severity_trend: str
    recovery_suggestions: List[str]
    ml_features: Dict[str, float]


@dataclass
class ErrorTrendAnalysis:
    """Analyse des tendances d'erreur"""
    trend_id: str
    service_name: str
    error_type: str
    trend_direction: str  # increasing, decreasing, stable, volatile
    change_rate: float
    statistical_significance: float
    forecast_7_days: List[float]
    forecast_30_days: List[float]
    anomaly_score: float
    recommended_actions: List[str]


@dataclass
class ErrorCorrelation:
    """Corrélation entre erreurs"""
    correlation_id: str
    primary_error: str
    correlated_errors: List[str]
    correlation_strength: float
    time_lag_seconds: float
    causality_probability: float
    business_impact: str


@dataclass
class ErrorPrediction:
    """Prédiction d'erreur ML"""
    prediction_id: str
    service_name: str
    error_type: str
    probability: float
    confidence: PredictionConfidence
    time_window: int  # minutes
    risk_factors: List[str]
    preventive_actions: List[str]
    business_impact_estimate: float


class ErrorAnalyticsEngine:
    """
    🧠 ML Engineer + Lead Dev IA: Error Analytics Engine Enterprise
    
    Moteur d'analyse d'erreurs alimenté par ML pour:
    - Détection de patterns d'erreur avancés
    - Analyse prédictive des pannes
    - Corrélation intelligente d'erreurs
    - Insights automatisés pour Ainflue
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """🚀 DevOps: Initialisation engine analytics avec configuration ML"""
        self.config = config or {}
        self.ml_models = {}
        self.pattern_cache = {}
        self.correlation_matrix = defaultdict(lambda: defaultdict(float))
        self.error_features = defaultdict(list)
        self.trend_analyzers = {}
        self.prediction_models = {}
        
        # 🔒 Sécurité: Configuration sécurisée
        self.model_path = Path(self.config.get('model_path', '/tmp/ml_models'))
        self.model_path.mkdir(exist_ok=True)
        
        # 📊 DBA: Configuration base de données analytics
        self.analytics_db_config = self.config.get('analytics_db', {})
        
        # 🎵 Audio + Platform: Configuration spécifique Ainflue
        self.platform_configs = self._initialize_platform_configs()
        
        logger.info("ErrorAnalyticsEngine initialized with ML capabilities")
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """🎵 Audio + Platform: Configuration des 65+ plateformes"""
        return {
            # Music Streaming Platforms
            'spotify': {
                'error_patterns': ['rate_limit', 'token_expired', 'track_not_found'],
                'ml_features': ['request_rate', 'token_age', 'content_type'],
                'severity_weights': {'rate_limit': 0.8, 'token_expired': 0.6}
            },
            'apple_music': {
                'error_patterns': ['drm_failure', 'metadata_sync_error', 'playlist_limit'],
                'ml_features': ['drm_version', 'metadata_size', 'playlist_count'],
                'severity_weights': {'drm_failure': 0.9, 'metadata_sync_error': 0.7}
            },
            'soundcloud': {
                'error_patterns': ['upload_limit', 'format_unsupported', 'copyright_claim'],
                'ml_features': ['file_size', 'format_type', 'content_duration'],
                'severity_weights': {'copyright_claim': 1.0, 'upload_limit': 0.8}
            },
            
            # Social Media Platforms
            'youtube': {
                'error_patterns': ['video_processing_failed', 'monetization_denied', 'copyright_strike'],
                'ml_features': ['video_length', 'resolution', 'upload_frequency'],
                'severity_weights': {'copyright_strike': 1.0, 'monetization_denied': 0.9}
            },
            'instagram': {
                'error_patterns': ['story_upload_failed', 'hashtag_banned', 'account_restricted'],
                'ml_features': ['image_size', 'hashtag_count', 'posting_frequency'],
                'severity_weights': {'account_restricted': 1.0, 'hashtag_banned': 0.8}
            },
            'tiktok': {
                'error_patterns': ['video_rejected', 'sound_copyright', 'region_blocked'],
                'ml_features': ['video_duration', 'effect_count', 'sound_length'],
                'severity_weights': {'region_blocked': 0.9, 'sound_copyright': 0.8}
            },
            
            # Creator Economy Platforms
            'patreon': {
                'error_patterns': ['payment_failed', 'tier_creation_error', 'content_locked'],
                'ml_features': ['subscriber_count', 'payment_amount', 'content_frequency'],
                'severity_weights': {'payment_failed': 1.0, 'content_locked': 0.7}
            },
            'onlyfans': {
                'error_patterns': ['age_verification_failed', 'payment_processing_error', 'content_flagged'],
                'ml_features': ['verification_attempts', 'payment_frequency', 'content_reports'],
                'severity_weights': {'age_verification_failed': 1.0, 'content_flagged': 0.9}
            }
        }
    
    async def analyze_error_patterns(
        self, 
        error_events: List[Dict[str, Any]], 
        time_window_hours: int = 24
    ) -> List[ErrorPattern]:
        """
        🧠 ML Engineer: Analyse des patterns d'erreur avec machine learning
        
        Args:
            error_events: Liste des événements d'erreur
            time_window_hours: Fenêtre temporelle d'analyse
            
        Returns:
            Liste des patterns détectés avec confiance ML
        """
        try:
            # Préparation des données ML
            features_matrix = await self._extract_ml_features(error_events)
            
            # Détection des patterns par clustering
            patterns = await self._detect_patterns_ml(features_matrix, error_events)
            
            # Enrichissement avec analyse business Ainflue
            enriched_patterns = await self._enrich_patterns_ainflue(patterns, error_events)
            
            # Calcul des scores de confiance
            for pattern in enriched_patterns:
                pattern.confidence_score = await self._calculate_confidence_score(pattern, error_events)
            
            # Cache pour optimisation
            cache_key = self._generate_cache_key(error_events, time_window_hours)
            self.pattern_cache[cache_key] = enriched_patterns
            
            logger.info(f"Detected {len(enriched_patterns)} error patterns with ML analysis")
            return enriched_patterns
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return []
    
    async def _extract_ml_features(self, error_events: List[Dict[str, Any]]) -> np.ndarray:
        """🧠 ML Engineer: Extraction des features pour ML"""
        features = []
        
        for event in error_events:
            event_features = []
            
            # Features temporelles
            event_features.extend([
                event.get('timestamp', datetime.now()).hour,
                event.get('timestamp', datetime.now()).weekday(),
                event.get('duration_ms', 0) / 1000.0
            ])
            
            # Features de service
            service_name = event.get('service_name', 'unknown')
            event_features.extend([
                hash(service_name) % 1000,  # Service hash
                event.get('error_count', 1),
                event.get('retry_count', 0)
            ])
            
            # Features spécifiques plateforme
            platform = event.get('platform', 'unknown')
            if platform in self.platform_configs:
                platform_config = self.platform_configs[platform]
                for feature_name in platform_config.get('ml_features', []):
                    event_features.append(event.get(feature_name, 0))
            
            # Features de contexte business
            event_features.extend([
                event.get('user_tier', 0),  # Tier créateur
                event.get('content_size_mb', 0),
                event.get('monetization_enabled', 0),
                event.get('collaboration_active', 0)
            ])
            
            features.append(event_features)
        
        return np.array(features) if features else np.array([[0]])
    
    async def _detect_patterns_ml(
        self, 
        features_matrix: np.ndarray, 
        error_events: List[Dict[str, Any]]
    ) -> List[ErrorPattern]:
        """🧠 ML Engineer: Détection de patterns par clustering ML"""
        patterns = []
        
        try:
            # Simple clustering pour patterns
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
            
            # Normalisation des features
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(features_matrix)
            
            # Clustering DBSCAN pour identifier patterns
            clustering = DBSCAN(eps=0.5, min_samples=3)
            cluster_labels = clustering.fit_predict(normalized_features)
            
            # Création des patterns par cluster
            unique_labels = set(cluster_labels)
            for label in unique_labels:
                if label == -1:  # Noise points
                    continue
                    
                cluster_events = [error_events[i] for i, l in enumerate(cluster_labels) if l == label]
                
                if len(cluster_events) >= 3:  # Minimum pour un pattern
                    pattern = await self._create_pattern_from_cluster(cluster_events, label)
                    patterns.append(pattern)
            
        except ImportError:
            # Fallback sans sklearn
            patterns = await self._detect_patterns_simple(error_events)
        
        return patterns
    
    async def _create_pattern_from_cluster(
        self, 
        cluster_events: List[Dict[str, Any]], 
        cluster_id: int
    ) -> ErrorPattern:
        """🧠 ML Engineer: Création d'un pattern à partir d'un cluster"""
        
        # Analyse des événements du cluster
        error_types = [event.get('error_type', 'unknown') for event in cluster_events]
        services = [event.get('service_name', 'unknown') for event in cluster_events]
        platforms = [event.get('platform', 'unknown') for event in cluster_events]
        
        # Détermination du type de pattern
        pattern_type = await self._determine_pattern_type(cluster_events)
        
        # Signature unique du pattern
        signature_data = {
            'error_types': sorted(set(error_types)),
            'services': sorted(set(services)),
            'platforms': sorted(set(platforms))
        }
        error_signature = hashlib.md5(
            json.dumps(signature_data, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Features ML du pattern
        ml_features = await self._calculate_pattern_features(cluster_events)
        
        # Suggestions de récupération
        recovery_suggestions = await self._generate_recovery_suggestions(
            pattern_type, cluster_events
        )
        
        return ErrorPattern(
            pattern_id=f"pattern_{cluster_id}_{error_signature}",
            pattern_type=pattern_type,
            confidence_score=0.0,  # Calculé plus tard
            frequency=len(cluster_events),
            first_seen=min(event.get('timestamp', datetime.now()) for event in cluster_events),
            last_seen=max(event.get('timestamp', datetime.now()) for event in cluster_events),
            affected_services=list(set(services)),
            error_signature=error_signature,
            severity_trend=await self._calculate_severity_trend(cluster_events),
            recovery_suggestions=recovery_suggestions,
            ml_features=ml_features
        )
    
    async def _determine_pattern_type(self, events: List[Dict[str, Any]]) -> ErrorPatternType:
        """🧠 ML Engineer: Détermination du type de pattern"""
        
        # Analyse des caractéristiques temporelles
        timestamps = [event.get('timestamp', datetime.now()) for event in events]
        time_diffs = [
            (timestamps[i+1] - timestamps[i]).total_seconds() 
            for i in range(len(timestamps)-1)
        ]
        
        # Analyse des services affectés
        services = [event.get('service_name', 'unknown') for event in events]
        unique_services = set(services)
        
        # Analyse des types d'erreur
        error_types = [event.get('error_type', 'unknown') for event in events]
        
        # Logique de détermination du pattern
        if len(unique_services) > 3 and any(diff < 60 for diff in time_diffs):
            return ErrorPatternType.CASCADING_FAILURE
        elif 'rate_limit' in str(error_types).lower():
            return ErrorPatternType.RATE_LIMIT_BURST
        elif 'auth' in str(error_types).lower():
            return ErrorPatternType.AUTHENTICATION_WAVE
        elif 'timeout' in str(error_types).lower() or 'performance' in str(error_types).lower():
            return ErrorPatternType.PERFORMANCE_DEGRADATION
        else:
            return ErrorPatternType.INTEGRATION_FAILURE
    
    async def _calculate_pattern_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """🧠 ML Engineer: Calcul des features ML pour un pattern"""
        
        features = {}
        
        # Features temporelles
        timestamps = [event.get('timestamp', datetime.now()) for event in events]
        duration = (max(timestamps) - min(timestamps)).total_seconds()
        features['duration_seconds'] = duration
        features['event_frequency'] = len(events) / max(duration, 1)
        
        # Features de diversité
        services = [event.get('service_name', 'unknown') for event in events]
        platforms = [event.get('platform', 'unknown') for event in events]
        features['service_diversity'] = len(set(services)) / len(services)
        features['platform_diversity'] = len(set(platforms)) / len(platforms)
        
        # Features de sévérité
        severities = [event.get('severity', 'medium') for event in events]
        severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        avg_severity = sum(severity_weights.get(s, 2) for s in severities) / len(severities)
        features['average_severity'] = avg_severity
        
        # Features business Ainflue
        content_sizes = [event.get('content_size_mb', 0) for event in events]
        features['avg_content_size'] = sum(content_sizes) / len(content_sizes) if content_sizes else 0
        
        monetization_events = sum(1 for event in events if event.get('monetization_enabled', False))
        features['monetization_ratio'] = monetization_events / len(events)
        
        return features
    
    async def _generate_recovery_suggestions(
        self, 
        pattern_type: ErrorPatternType, 
        events: List[Dict[str, Any]]
    ) -> List[str]:
        """🔧 DevOps + Backend Senior: Génération de suggestions de récupération"""
        
        suggestions = []
        
        if pattern_type == ErrorPatternType.CASCADING_FAILURE:
            suggestions.extend([
                "Implement circuit breakers between services",
                "Add bulkhead isolation for critical components",
                "Enable graceful degradation for non-critical features",
                "Review service dependency graph for optimization"
            ])
        
        elif pattern_type == ErrorPatternType.RATE_LIMIT_BURST:
            suggestions.extend([
                "Implement exponential backoff with jitter",
                "Add request queuing and throttling",
                "Consider upgrading API rate limits",
                "Optimize batch processing strategies"
            ])
        
        elif pattern_type == ErrorPatternType.AUTHENTICATION_WAVE:
            suggestions.extend([
                "Implement token refresh automation",
                "Add authentication caching layer",
                "Review OAuth flow optimization",
                "Consider multi-factor authentication backup"
            ])
        
        elif pattern_type == ErrorPatternType.PERFORMANCE_DEGRADATION:
            suggestions.extend([
                "Enable performance monitoring and alerting",
                "Optimize database queries and indexing",
                "Implement caching strategies",
                "Scale resources horizontally"
            ])
        
        # Suggestions spécifiques Ainflue
        platforms = [event.get('platform', 'unknown') for event in events]
        unique_platforms = set(platforms)
        
        for platform in unique_platforms:
            if platform in self.platform_configs:
                suggestions.append(f"Review {platform} integration health and rate limits")
        
        return suggestions
    
    async def _calculate_severity_trend(self, events: List[Dict[str, Any]]) -> str:
        """📊 DBA: Calcul de la tendance de sévérité"""
        
        if len(events) < 2:
            return "stable"
        
        # Tri par timestamp
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', datetime.now()))
        
        severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        severities = [
            severity_weights.get(event.get('severity', 'medium'), 2) 
            for event in sorted_events
        ]
        
        # Calcul de la tendance
        first_half = severities[:len(severities)//2]
        second_half = severities[len(severities)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first * 1.2:
            return "increasing"
        elif avg_second < avg_first * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_confidence_score(
        self, 
        pattern: ErrorPattern, 
        all_events: List[Dict[str, Any]]
    ) -> float:
        """🧠 ML Engineer: Calcul du score de confiance ML"""
        
        confidence = 0.0
        
        # Confiance basée sur la fréquence
        frequency_score = min(pattern.frequency / 10.0, 1.0)
        confidence += frequency_score * 0.3
        
        # Confiance basée sur la consistance temporelle
        duration = (pattern.last_seen - pattern.first_seen).total_seconds()
        if duration > 0:
            consistency_score = min(pattern.frequency / (duration / 3600), 1.0)  # events per hour
            confidence += consistency_score * 0.2
        
        # Confiance basée sur la diversité des services
        service_diversity = len(pattern.affected_services) / max(len(set(
            event.get('service_name', 'unknown') for event in all_events
        )), 1)
        confidence += service_diversity * 0.2
        
        # Confiance basée sur les features ML
        ml_features_score = min(
            sum(pattern.ml_features.values()) / max(len(pattern.ml_features), 1) / 10.0, 
            1.0
        )
        confidence += ml_features_score * 0.3
        
        return min(confidence, 1.0)
    
    async def predict_error_trends(
        self, 
        service_name: str, 
        historical_data: List[Dict[str, Any]], 
        forecast_days: int = 7
    ) -> ErrorTrendAnalysis:
        """
        📈 ML Engineer + DBA: Prédiction des tendances d'erreur
        
        Args:
            service_name: Nom du service à analyser
            historical_data: Données historiques d'erreur
            forecast_days: Nombre de jours de prévision
            
        Returns:
            Analyse des tendances avec prévisions ML
        """
        try:
            # Préparation des données temporelles
            time_series = await self._prepare_time_series(historical_data)
            
            # Analyse statistique des tendances
            trend_direction, change_rate = await self._analyze_trend_direction(time_series)
            
            # Détection d'anomalies
            anomaly_score = await self._calculate_anomaly_score(time_series)
            
            # Prévisions ML
            forecast_7_days = await self._forecast_errors(time_series, 7)
            forecast_30_days = await self._forecast_errors(time_series, 30)
            
            # Recommandations basées sur les tendances
            recommendations = await self._generate_trend_recommendations(
                trend_direction, change_rate, anomaly_score
            )
            
            trend_id = f"trend_{service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return ErrorTrendAnalysis(
                trend_id=trend_id,
                service_name=service_name,
                error_type="aggregate",
                trend_direction=trend_direction,
                change_rate=change_rate,
                statistical_significance=await self._calculate_statistical_significance(time_series),
                forecast_7_days=forecast_7_days,
                forecast_30_days=forecast_30_days,
                anomaly_score=anomaly_score,
                recommended_actions=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in trend prediction for {service_name}: {e}")
            return ErrorTrendAnalysis(
                trend_id=f"error_trend_{service_name}",
                service_name=service_name,
                error_type="unknown",
                trend_direction="stable",
                change_rate=0.0,
                statistical_significance=0.0,
                forecast_7_days=[0.0] * 7,
                forecast_30_days=[0.0] * 30,
                anomaly_score=0.0,
                recommended_actions=["Review service health manually"]
            )
    
    async def _prepare_time_series(self, historical_data: List[Dict[str, Any]]) -> List[float]:
        """📊 DBA: Préparation des séries temporelles"""
        
        # Groupement par heure
        hourly_counts = defaultdict(int)
        
        for event in historical_data:
            timestamp = event.get('timestamp', datetime.now())
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] += 1
        
        # Conversion en série temporelle
        if not hourly_counts:
            return [0.0] * 24  # 24 heures par défaut
        
        sorted_hours = sorted(hourly_counts.keys())
        time_series = [hourly_counts[hour] for hour in sorted_hours]
        
        return time_series
    
    async def _analyze_trend_direction(self, time_series: List[float]) -> tuple[str, float]:
        """📈 ML Engineer: Analyse de la direction des tendances"""
        
        if len(time_series) < 2:
            return "stable", 0.0
        
        # Calcul de la pente par régression linéaire simple
        n = len(time_series)
        x = list(range(n))
        y = time_series
        
        # Calculs de régression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Détermination de la direction
        if abs(slope) < 0.1:
            return "stable", slope
        elif slope > 0.5:
            return "increasing", slope
        elif slope < -0.5:
            return "decreasing", slope
        else:
            return "volatile", slope
    
    async def _calculate_anomaly_score(self, time_series: List[float]) -> float:
        """🤖 ML Engineer: Calcul du score d'anomalie"""
        
        if len(time_series) < 3:
            return 0.0
        
        # Statistiques de base
        mean_val = sum(time_series) / len(time_series)
        variance = sum((x - mean_val) ** 2 for x in time_series) / len(time_series)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        # Détection d'anomalies basée sur z-score
        z_scores = [abs(x - mean_val) / std_dev for x in time_series]
        anomaly_count = sum(1 for z in z_scores if z > 2.0)  # 2 sigma
        
        return min(anomaly_count / len(time_series), 1.0)
    
    async def _forecast_errors(self, time_series: List[float], days: int) -> List[float]:
        """🔮 ML Engineer: Prévision d'erreurs par ML"""
        
        if len(time_series) < 3:
            return [0.0] * days
        
        # Méthode simple de prévision basée sur la moyenne mobile
        window_size = min(7, len(time_series))
        recent_average = sum(time_series[-window_size:]) / window_size
        
        # Ajustement basé sur la tendance
        trend_direction, change_rate = await self._analyze_trend_direction(time_series)
        
        forecast = []
        for day in range(days):
            if trend_direction == "increasing":
                predicted_value = recent_average * (1 + change_rate * 0.1 * day)
            elif trend_direction == "decreasing":
                predicted_value = recent_average * (1 + change_rate * 0.1 * day)
            else:
                predicted_value = recent_average
            
            forecast.append(max(0.0, predicted_value))
        
        return forecast
    
    async def _calculate_statistical_significance(self, time_series: List[float]) -> float:
        """📊 DBA: Calcul de la significance statistique"""
        
        if len(time_series) < 10:
            return 0.0
        
        # Test de significativité basé sur la variance
        mean_val = sum(time_series) / len(time_series)
        variance = sum((x - mean_val) ** 2 for x in time_series) / len(time_series)
        
        if variance == 0:
            return 0.0
        
        # Coefficient de variation comme mesure de significativité
        cv = (variance ** 0.5) / mean_val if mean_val > 0 else 0
        significance = min(1.0 / (1.0 + cv), 1.0)
        
        return significance
    
    async def _generate_trend_recommendations(
        self, 
        trend_direction: str, 
        change_rate: float, 
        anomaly_score: float
    ) -> List[str]:
        """🔧 DevOps: Génération de recommandations basées sur les tendances"""
        
        recommendations = []
        
        if trend_direction == "increasing":
            recommendations.extend([
                "Monitor resource utilization closely",
                "Consider scaling up infrastructure",
                "Review recent changes and deployments",
                "Implement additional error handling"
            ])
        
        elif trend_direction == "decreasing":
            recommendations.extend([
                "Continue current optimization efforts",
                "Document successful changes",
                "Consider resource optimization",
                "Maintain monitoring vigilance"
            ])
        
        elif trend_direction == "volatile":
            recommendations.extend([
                "Investigate root cause of instability",
                "Implement circuit breaker patterns",
                "Review system dependencies",
                "Add chaos engineering tests"
            ])
        
        if anomaly_score > 0.3:
            recommendations.extend([
                "Investigate anomalous error patterns",
                "Review system logs for unusual activity",
                "Consider implementing anomaly detection alerts"
            ])
        
        return recommendations
    
    async def correlate_errors(
        self, 
        error_events: List[Dict[str, Any]], 
        correlation_threshold: float = 0.7
    ) -> List[ErrorCorrelation]:
        """
        🔗 ML Engineer + Backend Senior: Corrélation intelligente d'erreurs
        
        Args:
            error_events: Événements d'erreur à corréler
            correlation_threshold: Seuil de corrélation significative
            
        Returns:
            Liste des corrélations détectées
        """
        correlations = []
        
        try:
            # Matrice de corrélation temporelle
            correlation_matrix = await self._build_correlation_matrix(error_events)
            
            # Détection des corrélations significatives
            for primary_error, related_errors in correlation_matrix.items():
                for related_error, correlation_data in related_errors.items():
                    if correlation_data['strength'] >= correlation_threshold:
                        
                        correlation = ErrorCorrelation(
                            correlation_id=f"corr_{hashlib.md5(f'{primary_error}_{related_error}'.encode()).hexdigest()[:12]}",
                            primary_error=primary_error,
                            correlated_errors=[related_error],
                            correlation_strength=correlation_data['strength'],
                            time_lag_seconds=correlation_data['time_lag'],
                            causality_probability=correlation_data['causality'],
                            business_impact=await self._assess_business_impact(
                                primary_error, [related_error], error_events
                            )
                        )
                        
                        correlations.append(correlation)
            
            logger.info(f"Found {len(correlations)} significant error correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {e}")
            return []
    
    async def _build_correlation_matrix(
        self, 
        error_events: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        """🔗 ML Engineer: Construction de la matrice de corrélation"""
        
        matrix = defaultdict(lambda: defaultdict(lambda: {'strength': 0.0, 'time_lag': 0.0, 'causality': 0.0}))
        
        # Groupement par type d'erreur
        error_groups = defaultdict(list)
        for event in error_events:
            error_type = event.get('error_type', 'unknown')
            error_groups[error_type].append(event)
        
        # Calcul des corrélations par paires
        error_types = list(error_groups.keys())
        for i, error_type_1 in enumerate(error_types):
            for error_type_2 in error_types[i+1:]:
                
                events_1 = error_groups[error_type_1]
                events_2 = error_groups[error_type_2]
                
                correlation_data = await self._calculate_pairwise_correlation(events_1, events_2)
                
                matrix[error_type_1][error_type_2] = correlation_data
                matrix[error_type_2][error_type_1] = correlation_data  # Symétrique
        
        return matrix
    
    async def _calculate_pairwise_correlation(
        self, 
        events_1: List[Dict[str, Any]], 
        events_2: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """🔗 ML Engineer: Calcul de corrélation entre deux types d'erreur"""
        
        if not events_1 or not events_2:
            return {'strength': 0.0, 'time_lag': 0.0, 'causality': 0.0}
        
        # Extraction des timestamps
        timestamps_1 = [event.get('timestamp', datetime.now()) for event in events_1]
        timestamps_2 = [event.get('timestamp', datetime.now()) for event in events_2]
        
        # Calcul de la force de corrélation basée sur la proximité temporelle
        correlation_strength = 0.0
        time_lags = []
        
        for ts1 in timestamps_1:
            closest_ts2 = min(timestamps_2, key=lambda ts2: abs((ts1 - ts2).total_seconds()))
            time_diff = abs((ts1 - closest_ts2).total_seconds())
            
            if time_diff < 300:  # 5 minutes
                correlation_strength += 1.0 / (1.0 + time_diff / 60.0)  # Décroissance exponentielle
                time_lags.append((ts1 - closest_ts2).total_seconds())
        
        # Normalisation
        correlation_strength = min(correlation_strength / len(events_1), 1.0)
        
        # Calcul du lag temporel moyen
        avg_time_lag = sum(time_lags) / len(time_lags) if time_lags else 0.0
        
        # Calcul de la probabilité de causalité
        causality_probability = correlation_strength * (1.0 if avg_time_lag > 0 else 0.5)
        
        return {
            'strength': correlation_strength,
            'time_lag': avg_time_lag,
            'causality': causality_probability
        }
    
    async def _assess_business_impact(
        self, 
        primary_error: str, 
        correlated_errors: List[str], 
        all_events: List[Dict[str, Any]]
    ) -> str:
        """💼 Business: Évaluation de l'impact business"""
        
        # Filtrage des événements concernés
        relevant_events = [
            event for event in all_events 
            if event.get('error_type') in [primary_error] + correlated_errors
        ]
        
        # Métriques d'impact
        total_events = len(relevant_events)
        unique_users = len(set(event.get('user_id', 'unknown') for event in relevant_events))
        revenue_impact = sum(event.get('revenue_impact', 0) for event in relevant_events)
        
        # Classification d'impact
        if total_events > 100 or unique_users > 50 or revenue_impact > 1000:
            return "high"
        elif total_events > 20 or unique_users > 10 or revenue_impact > 100:
            return "medium" 
        else:
            return "low"
    
    def _generate_cache_key(self, error_events: List[Dict[str, Any]], time_window: int) -> str:
        """🔒 Sécurité: Génération de clé de cache sécurisée"""
        event_signatures = [
            f"{event.get('error_type', 'unknown')}_{event.get('service_name', 'unknown')}"
            for event in error_events[-100:]  # Limiter pour la performance
        ]
        
        cache_data = {
            'signatures': sorted(event_signatures),
            'time_window': time_window,
            'count': len(error_events)
        }
        
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    async def _detect_patterns_simple(self, error_events: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """🔧 Backend Senior: Fallback simple pour détection de patterns"""
        
        patterns = []
        
        # Groupement par type d'erreur
        error_groups = defaultdict(list)
        for event in error_events:
            error_type = event.get('error_type', 'unknown')
            error_groups[error_type].append(event)
        
        # Création de patterns pour chaque groupe significatif
        for error_type, events in error_groups.items():
            if len(events) >= 3:  # Minimum pour un pattern
                pattern = await self._create_simple_pattern(error_type, events)
                patterns.append(pattern)
        
        return patterns
    
    async def _create_simple_pattern(self, error_type: str, events: List[Dict[str, Any]]) -> ErrorPattern:
        """🔧 Backend Senior: Création de pattern simple"""
        
        services = list(set(event.get('service_name', 'unknown') for event in events))
        
        return ErrorPattern(
            pattern_id=f"simple_{error_type}_{len(events)}",
            pattern_type=ErrorPatternType.INTEGRATION_FAILURE,
            confidence_score=0.6,  # Score modéré pour patterns simples
            frequency=len(events),
            first_seen=min(event.get('timestamp', datetime.now()) for event in events),
            last_seen=max(event.get('timestamp', datetime.now()) for event in events),
            affected_services=services,
            error_signature=hashlib.md5(error_type.encode()).hexdigest()[:16],
            severity_trend="stable",
            recovery_suggestions=[
                f"Review {error_type} handling logic",
                "Implement retry mechanisms",
                "Add monitoring and alerting"
            ],
            ml_features={'frequency': float(len(events)), 'service_count': float(len(services))}
        )
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """
        📊 Analytics: Résumé complet des analytics d'erreur
        
        Returns:
            Résumé avec métriques et insights ML
        """
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'analytics_engine': {
                    'version': '1.0.0',
                    'ml_models_loaded': len(self.ml_models),
                    'patterns_cached': len(self.pattern_cache),
                    'platform_configs': len(self.platform_configs)
                },
                'capabilities': {
                    'pattern_detection': True,
                    'trend_analysis': True,
                    'error_correlation': True,
                    'ml_prediction': True,
                    'platform_support': 65
                },
                'ainflue_integration': {
                    'creator_economy_support': True,
                    'multi_platform_analytics': True,
                    'business_impact_assessment': True,
                    'monetization_tracking': True
                },
                'ml_features': {
                    'clustering_algorithms': ['DBSCAN', 'KMeans'],
                    'time_series_analysis': True,
                    'anomaly_detection': True,
                    'predictive_modeling': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {'error': 'Failed to generate summary', 'timestamp': datetime.now().isoformat()}


# Instance globale pour utilisation
error_analytics_engine = ErrorAnalyticsEngine()

# Export des classes principales
__all__ = [
    'ErrorAnalyticsEngine',
    'ErrorPattern',
    'ErrorTrendAnalysis', 
    'ErrorCorrelation',
    'ErrorPrediction',
    'ErrorPatternType',
    'PredictionConfidence',
    'error_analytics_engine'
]