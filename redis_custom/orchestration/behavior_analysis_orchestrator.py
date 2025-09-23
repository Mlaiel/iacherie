#!/usr/bin/env python3
"""🧠 Behavior Analysis Orchestrator - AI-Powered Behavior Intelligence
======================================================================
Expert: ML ENGINEER + LEAD DEV IA + BACKEND SENIOR + DATA SCIENTIST
Technologies: Behavioral Analytics + Pattern Recognition + User Intelligence + Predictive Modeling
Architecture: Level 3 - Behavioral Intelligence Layer
Date: 2025-01-14

Ultra-advanced behavioral analysis system for creator economy with ML-driven
user behavior prediction, engagement optimization and intelligent insights.
======================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
======================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Import Redis with absolute path to avoid circular import
try:
    import redis as redis_client
except ImportError:
    redis_client = None
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import statistics

logger = logging.getLogger(__name__)

class BehaviorType(Enum):
    """Types de comportements analysés"""
    CREATOR_WORKFLOW = "creator_workflow"
    CONTENT_CONSUMPTION = "content_consumption"
    COLLABORATION_PATTERN = "collaboration_pattern"
    MONETIZATION_BEHAVIOR = "monetization_behavior"
    ENGAGEMENT_PATTERN = "engagement_pattern"
    PLATFORM_NAVIGATION = "platform_navigation"
    SOCIAL_INTERACTION = "social_interaction"
    CREATIVE_PROCESS = "creative_process"

class BehaviorState(Enum):
    """États des comportements"""
    NORMAL = "normal"
    ANOMALOUS = "anomalous"
    TRENDING = "trending"
    DECLINING = "declining"
    EMERGING = "emerging"
    CRITICAL = "critical"
    OPTIMAL = "optimal"
    SUBOPTIMAL = "suboptimal"

class AnalysisScope(Enum):
    """Portée de l'analyse comportementale"""
    INDIVIDUAL = "individual"
    GROUP = "group"
    COMMUNITY = "community"
    PLATFORM_WIDE = "platform_wide"
    SEGMENT = "segment"
    COHORT = "cohort"

class BehaviorInsightType(Enum):
    """Types d'insights comportementaux"""
    PATTERN_DISCOVERY = "pattern_discovery"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_IDENTIFICATION = "trend_identification"
    SEGMENTATION = "segmentation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    OPTIMIZATION = "optimization"
    INTERVENTION = "intervention"

@dataclass
class BehaviorEvent:
    """Événement comportemental"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    behavior_type: BehaviorType = BehaviorType.CREATOR_WORKFLOW
    action: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    platform: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    value: float = 0.0
    sequence_position: int = 0

@dataclass
class BehaviorPattern:
    """Pattern comportemental identifié"""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""
    behavior_type: BehaviorType = BehaviorType.CREATOR_WORKFLOW
    frequency: float = 0.0
    confidence: float = 0.0
    support: float = 0.0
    sequence: List[str] = field(default_factory=list)
    characteristics: Dict[str, Any] = field(default_factory=dict)
    users_affected: List[str] = field(default_factory=list)
    temporal_properties: Dict[str, Any] = field(default_factory=dict)
    business_impact: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BehaviorSegment:
    """Segment comportemental"""
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    segment_name: str = ""
    description: str = ""
    users: List[str] = field(default_factory=list)
    characteristics: Dict[str, Any] = field(default_factory=dict)
    behavior_patterns: List[str] = field(default_factory=list)
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    value_metrics: Dict[str, float] = field(default_factory=dict)
    size: int = 0
    cohesion: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BehaviorInsight:
    """Insight comportemental"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: BehaviorInsightType = BehaviorInsightType.PATTERN_DISCOVERY
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    impact_score: float = 0.0
    actionability: float = 0.0
    affected_users: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    business_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class BehaviorPrediction:
    """Prédiction comportementale"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    predicted_behavior: str = ""
    behavior_type: BehaviorType = BehaviorType.CREATOR_WORKFLOW
    probability: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    time_horizon: timedelta = timedelta(hours=24)
    factors: Dict[str, float] = field(default_factory=dict)
    business_value: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BehaviorAnalysisConfig:
    """Configuration de l'analyse comportementale"""
    analysis_window: timedelta = timedelta(days=30)
    min_events_per_user: int = 10
    min_pattern_support: float = 0.01
    min_pattern_confidence: float = 0.5
    clustering_algorithm: str = "kmeans"
    max_clusters: int = 20
    anomaly_threshold: float = 0.1
    insight_refresh_interval: timedelta = timedelta(hours=6)
    prediction_horizon: timedelta = timedelta(days=7)
    enable_real_time: bool = True
    enable_segmentation: bool = True
    enable_predictions: bool = True

class RedisBehaviorAnalysisOrchestrator:
    """Orchestrateur d'analyse comportementale Redis enterprise"""
    
    def __init__(self, config: BehaviorAnalysisConfig, redis_client_instance: Optional[Any] = None):
        self.config = config
        self.redis_client = redis_client_instance or (redis_client.Redis() if redis_client else None)
        self.is_running = False
        self.analysis_tasks = {}
        self.behavior_models = {}
        self.pattern_cache = {}
        self.segment_cache = {}
        self.insight_cache = {}
        self.prediction_cache = {}
        
        # ML Components
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=config.anomaly_threshold)
        self.cluster_model = None
        self.pattern_classifier = RandomForestClassifier(n_estimators=100)
        
        # Performance metrics
        self.metrics = {
            'events_processed': 0,
            'patterns_identified': 0,
            'insights_generated': 0,
            'predictions_made': 0,
            'analysis_latency': [],
            'accuracy_scores': [],
            'last_analysis': None
        }
        
    async def initialize(self) -> bool:
        """Initialise l'orchestrateur d'analyse comportementale"""
        try:
            logger.info("🧠 Initializing Behavior Analysis Orchestrator...")
            
            # Initialiser les modèles ML
            await self._initialize_ml_models()
            
            # Charger les données historiques
            await self._load_historical_data()
            
            # Configurer les tâches d'analyse
            await self._setup_analysis_tasks()
            
            self.is_running = True
            logger.info("✅ Behavior Analysis Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Behavior Analysis Orchestrator: {e}")
            return False
    
    async def _initialize_ml_models(self):
        """Initialise les modèles ML"""
        try:
            # Charger ou entraîner les modèles
            historical_data = await self._load_training_data()
            
            if len(historical_data) > 100:
                # Entraîner l'anomaly detector
                features = self._extract_features(historical_data)
                self.anomaly_detector.fit(features)
                
                # Initialiser le clustering
                if self.config.clustering_algorithm == "kmeans":
                    self.cluster_model = KMeans(n_clusters=min(10, len(features)//10))
                elif self.config.clustering_algorithm == "dbscan":
                    self.cluster_model = DBSCAN(eps=0.5, min_samples=5)
                
                if hasattr(self.cluster_model, 'fit'):
                    self.cluster_model.fit(features)
                
                logger.info("✅ ML models initialized and trained")
            else:
                logger.warning("⚠️ Insufficient data for ML model training")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {e}")
    
    async def _load_training_data(self) -> List[BehaviorEvent]:
        """Charge les données d'entraînement"""
        try:
            # Simuler des données d'entraînement (en production, charger depuis Redis)
            training_data = []
            
            # Charger depuis Redis si disponible
            keys = await self._get_redis_keys("behavior:events:*")
            for key in keys[:1000]:  # Limiter pour l'entraînement
                data = await self._get_redis_data(key)
                if data:
                    event = BehaviorEvent(**data)
                    training_data.append(event)
            
            return training_data
            
        except Exception as e:
            logger.error(f"❌ Failed to load training data: {e}")
            return []
    
    async def _get_redis_keys(self, pattern: str) -> List[str]:
        """Récupère les clés Redis correspondant au pattern"""
        try:
            return [key.decode() for key in self.redis_client.keys(pattern)]
        except:
            return []
    
    async def _get_redis_data(self, key: str) -> Optional[Dict]:
        """Récupère les données depuis Redis"""
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except:
            return None
    
    def _extract_features(self, events: List[BehaviorEvent]) -> np.ndarray:
        """Extrait les features pour l'analyse ML"""
        features = []
        
        for event in events:
            feature_vector = [
                event.duration,
                event.value,
                event.sequence_position,
                hash(event.action) % 1000,  # Hash de l'action
                event.timestamp.hour,  # Heure du jour
                event.timestamp.weekday(),  # Jour de la semaine
                len(event.context),  # Richesse du contexte
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    async def _load_historical_data(self):
        """Charge les données historiques"""
        try:
            # Charger les patterns existants
            pattern_keys = await self._get_redis_keys("behavior:patterns:*")
            for key in pattern_keys:
                data = await self._get_redis_data(key)
                if data:
                    pattern = BehaviorPattern(**data)
                    self.pattern_cache[pattern.pattern_id] = pattern
            
            # Charger les segments existants
            segment_keys = await self._get_redis_keys("behavior:segments:*")
            for key in segment_keys:
                data = await self._get_redis_data(key)
                if data:
                    segment = BehaviorSegment(**data)
                    self.segment_cache[segment.segment_id] = segment
            
            logger.info(f"✅ Loaded {len(self.pattern_cache)} patterns and {len(self.segment_cache)} segments")
            
        except Exception as e:
            logger.error(f"❌ Failed to load historical data: {e}")
    
    async def _setup_analysis_tasks(self):
        """Configure les tâches d'analyse"""
        if self.config.enable_real_time:
            self.analysis_tasks['real_time'] = asyncio.create_task(
                self._real_time_analysis_loop()
            )
        
        self.analysis_tasks['batch'] = asyncio.create_task(
            self._batch_analysis_loop()
        )
        
        if self.config.enable_segmentation:
            self.analysis_tasks['segmentation'] = asyncio.create_task(
                self._segmentation_loop()
            )
        
        if self.config.enable_predictions:
            self.analysis_tasks['predictions'] = asyncio.create_task(
                self._prediction_loop()
            )
    
    async def process_behavior_event(self, event: BehaviorEvent) -> Dict[str, Any]:
        """Traite un événement comportemental"""
        try:
            start_time = time.time()
            
            # Stocker l'événement
            await self._store_event(event)
            
            # Analyse en temps réel si activée
            real_time_insights = []
            if self.config.enable_real_time:
                real_time_insights = await self._analyze_event_real_time(event)
            
            # Mise à jour des métriques
            self.metrics['events_processed'] += 1
            processing_time = time.time() - start_time
            self.metrics['analysis_latency'].append(processing_time)
            
            # Garder seulement les 1000 dernières latences
            if len(self.metrics['analysis_latency']) > 1000:
                self.metrics['analysis_latency'] = self.metrics['analysis_latency'][-1000:]
            
            return {
                'event_id': event.event_id,
                'processing_time': processing_time,
                'real_time_insights': real_time_insights,
                'status': 'processed'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process behavior event: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    async def _store_event(self, event: BehaviorEvent):
        """Stocke un événement dans Redis"""
        try:
            key = f"behavior:events:{event.user_id}:{event.event_id}"
            data = {
                'event_id': event.event_id,
                'user_id': event.user_id,
                'behavior_type': event.behavior_type.value,
                'action': event.action,
                'context': event.context,
                'timestamp': event.timestamp.isoformat(),
                'session_id': event.session_id,
                'platform': event.platform,
                'metadata': event.metadata,
                'duration': event.duration,
                'value': event.value,
                'sequence_position': event.sequence_position
            }
            
            self.redis_client.setex(
                key,
                int(self.config.analysis_window.total_seconds()),
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to store event: {e}")
    
    async def _analyze_event_real_time(self, event: BehaviorEvent) -> List[BehaviorInsight]:
        """Analyse un événement en temps réel"""
        insights = []
        
        try:
            # Détection d'anomalies
            if self.anomaly_detector:
                features = self._extract_features([event])
                if len(features) > 0:
                    anomaly_score = self.anomaly_detector.decision_function(features)[0]
                    
                    if anomaly_score < -0.5:  # Seuil d'anomalie
                        insight = BehaviorInsight(
                            insight_type=BehaviorInsightType.ANOMALY_DETECTION,
                            title="Anomalous Behavior Detected",
                            description=f"Unusual {event.behavior_type.value} behavior detected for user {event.user_id}",
                            confidence=min(1.0, abs(anomaly_score)),
                            impact_score=0.7,
                            actionability=0.8,
                            affected_users=[event.user_id],
                            recommendations=["Investigate user activity", "Check for potential issues"],
                            data_points={'anomaly_score': anomaly_score, 'event_id': event.event_id}
                        )
                        insights.append(insight)
            
            # Détection de patterns émergents
            emerging_patterns = await self._detect_emerging_patterns(event)
            insights.extend(emerging_patterns)
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze event in real-time: {e}")
        
        return insights
    
    async def _detect_emerging_patterns(self, event: BehaviorEvent) -> List[BehaviorInsight]:
        """Détecte les patterns émergents"""
        insights = []
        
        try:
            # Récupérer les événements récents du même utilisateur
            recent_events = await self._get_user_recent_events(event.user_id, hours=24)
            
            if len(recent_events) >= 5:
                # Analyser les séquences d'actions
                actions = [e.action for e in recent_events]
                action_sequence = ' -> '.join(actions[-5:])  # Dernières 5 actions
                
                # Vérifier si c'est un nouveau pattern
                if action_sequence not in self.pattern_cache:
                    pattern = BehaviorPattern(
                        pattern_type="emerging_sequence",
                        behavior_type=event.behavior_type,
                        sequence=actions[-5:],
                        frequency=1,
                        confidence=0.6,
                        users_affected=[event.user_id],
                        business_impact=0.5
                    )
                    
                    self.pattern_cache[pattern.pattern_id] = pattern
                    
                    insight = BehaviorInsight(
                        insight_type=BehaviorInsightType.PATTERN_DISCOVERY,
                        title="New Behavior Pattern Emerging",
                        description=f"New sequence pattern detected: {action_sequence}",
                        confidence=0.6,
                        impact_score=0.5,
                        actionability=0.7,
                        affected_users=[event.user_id],
                        recommendations=["Monitor pattern development", "Consider UX optimization"],
                        data_points={'pattern_id': pattern.pattern_id, 'sequence': action_sequence}
                    )
                    insights.append(insight)
            
        except Exception as e:
            logger.error(f"❌ Failed to detect emerging patterns: {e}")
        
        return insights
    
    async def _get_user_recent_events(self, user_id: str, hours: int = 24) -> List[BehaviorEvent]:
        """Récupère les événements récents d'un utilisateur"""
        try:
            events = []
            pattern = f"behavior:events:{user_id}:*"
            keys = await self._get_redis_keys(pattern)
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for key in keys[-100:]:  # Limiter à 100 événements récents
                data = await self._get_redis_data(key)
                if data:
                    event_time = datetime.fromisoformat(data['timestamp'])
                    if event_time > cutoff_time:
                        event = BehaviorEvent(**data)
                        events.append(event)
            
            # Trier par timestamp
            events.sort(key=lambda x: x.timestamp)
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to get user recent events: {e}")
            return []
    
    async def _real_time_analysis_loop(self):
        """Boucle d'analyse en temps réel"""
        while self.is_running:
            try:
                # Cette boucle traite les événements en continu
                # En production, elle écouterait un stream Redis ou une queue
                await asyncio.sleep(1)  # Simuler le traitement en temps réel
                
            except Exception as e:
                logger.error(f"❌ Error in real-time analysis loop: {e}")
                await asyncio.sleep(5)
    
    async def _batch_analysis_loop(self):
        """Boucle d'analyse par batch"""
        while self.is_running:
            try:
                logger.info("🔄 Starting batch behavior analysis...")
                
                # Analyser les patterns
                await self._analyze_behavior_patterns()
                
                # Générer des insights
                await self._generate_behavioral_insights()
                
                # Mettre à jour les métriques
                self.metrics['last_analysis'] = datetime.now()
                
                logger.info("✅ Batch behavior analysis completed")
                
                # Attendre avant la prochaine analyse
                await asyncio.sleep(self.config.insight_refresh_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in batch analysis loop: {e}")
                await asyncio.sleep(300)  # Attendre 5 minutes en cas d'erreur
    
    async def _analyze_behavior_patterns(self):
        """Analyse les patterns comportementaux"""
        try:
            # Récupérer tous les événements de la fenêtre d'analyse
            cutoff_time = datetime.now() - self.config.analysis_window
            all_events = await self._get_events_since(cutoff_time)
            
            if len(all_events) < self.config.min_events_per_user:
                logger.warning("⚠️ Insufficient events for pattern analysis")
                return
            
            # Grouper par utilisateur
            user_events = {}
            for event in all_events:
                if event.user_id not in user_events:
                    user_events[event.user_id] = []
                user_events[event.user_id].append(event)
            
            # Analyser les patterns pour chaque utilisateur
            for user_id, events in user_events.items():
                if len(events) >= self.config.min_events_per_user:
                    patterns = await self._extract_user_patterns(user_id, events)
                    for pattern in patterns:
                        self.pattern_cache[pattern.pattern_id] = pattern
                        self.metrics['patterns_identified'] += 1
            
            logger.info(f"✅ Analyzed patterns for {len(user_events)} users")
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze behavior patterns: {e}")
    
    async def _get_events_since(self, cutoff_time: datetime) -> List[BehaviorEvent]:
        """Récupère tous les événements depuis une date donnée"""
        try:
            events = []
            pattern = "behavior:events:*"
            keys = await self._get_redis_keys(pattern)
            
            for key in keys:
                data = await self._get_redis_data(key)
                if data:
                    event_time = datetime.fromisoformat(data['timestamp'])
                    if event_time > cutoff_time:
                        event = BehaviorEvent(**data)
                        events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to get events since {cutoff_time}: {e}")
            return []
    
    async def _extract_user_patterns(self, user_id: str, events: List[BehaviorEvent]) -> List[BehaviorPattern]:
        """Extrait les patterns d'un utilisateur"""
        patterns = []
        
        try:
            # Analyser les séquences d'actions
            actions = [event.action for event in events]
            
            # Trouver les séquences fréquentes (algorithme simple)
            sequence_counts = {}
            for i in range(len(actions) - 2):
                sequence = tuple(actions[i:i+3])  # Séquences de 3 actions
                sequence_counts[sequence] = sequence_counts.get(sequence, 0) + 1
            
            # Créer des patterns pour les séquences fréquentes
            total_sequences = len(actions) - 2
            for sequence, count in sequence_counts.items():
                support = count / total_sequences if total_sequences > 0 else 0
                
                if support >= self.config.min_pattern_support:
                    pattern = BehaviorPattern(
                        pattern_type="action_sequence",
                        behavior_type=events[0].behavior_type,
                        sequence=list(sequence),
                        frequency=count,
                        confidence=min(1.0, support * 2),  # Confidence heuristique
                        support=support,
                        users_affected=[user_id],
                        business_impact=self._calculate_business_impact(sequence, events)
                    )
                    patterns.append(pattern)
            
            # Analyser les patterns temporels
            temporal_patterns = await self._extract_temporal_patterns(user_id, events)
            patterns.extend(temporal_patterns)
            
        except Exception as e:
            logger.error(f"❌ Failed to extract user patterns for {user_id}: {e}")
        
        return patterns
    
    def _calculate_business_impact(self, sequence: tuple, events: List[BehaviorEvent]) -> float:
        """Calcule l'impact business d'un pattern"""
        try:
            # Calculer l'impact basé sur la valeur des événements
            sequence_events = [e for e in events if e.action in sequence]
            if not sequence_events:
                return 0.0
            
            avg_value = statistics.mean([e.value for e in sequence_events if e.value > 0])
            avg_duration = statistics.mean([e.duration for e in sequence_events if e.duration > 0])
            
            # Impact heuristique basé sur valeur et engagement
            impact = min(1.0, (avg_value / 100) + (avg_duration / 3600))  # Normaliser
            return impact
            
        except:
            return 0.5  # Impact par défaut
    
    async def _extract_temporal_patterns(self, user_id: str, events: List[BehaviorEvent]) -> List[BehaviorPattern]:
        """Extrait les patterns temporels"""
        patterns = []
        
        try:
            # Analyser les patterns par heure du jour
            hourly_activity = {}
            for event in events:
                hour = event.timestamp.hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            # Identifier les pics d'activité
            max_activity = max(hourly_activity.values()) if hourly_activity else 0
            peak_hours = [hour for hour, count in hourly_activity.items() 
                         if count >= max_activity * 0.8]
            
            if peak_hours:
                pattern = BehaviorPattern(
                    pattern_type="temporal_peak",
                    behavior_type=events[0].behavior_type,
                    characteristics={'peak_hours': peak_hours, 'max_activity': max_activity},
                    frequency=max_activity,
                    confidence=0.8,
                    users_affected=[user_id],
                    business_impact=0.6
                )
                patterns.append(pattern)
            
        except Exception as e:
            logger.error(f"❌ Failed to extract temporal patterns: {e}")
        
        return patterns
    
    async def _generate_behavioral_insights(self):
        """Génère des insights comportementaux"""
        try:
            insights = []
            
            # Analyser les patterns pour générer des insights
            for pattern in self.pattern_cache.values():
                insight = await self._pattern_to_insight(pattern)
                if insight:
                    insights.append(insight)
            
            # Analyser les tendances globales
            trend_insights = await self._analyze_global_trends()
            insights.extend(trend_insights)
            
            # Stocker les insights
            for insight in insights:
                self.insight_cache[insight.insight_id] = insight
                await self._store_insight(insight)
                self.metrics['insights_generated'] += 1
            
            logger.info(f"✅ Generated {len(insights)} behavioral insights")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate behavioral insights: {e}")
    
    async def _pattern_to_insight(self, pattern: BehaviorPattern) -> Optional[BehaviorInsight]:
        """Convertit un pattern en insight"""
        try:
            if pattern.confidence < self.config.min_pattern_confidence:
                return None
            
            insight_type = BehaviorInsightType.PATTERN_DISCOVERY
            title = f"Pattern Detected: {pattern.pattern_type}"
            description = f"Identified {pattern.pattern_type} pattern with {pattern.confidence:.2f} confidence"
            
            recommendations = []
            if pattern.business_impact > 0.7:
                recommendations.append("High business impact - prioritize optimization")
            if pattern.confidence > 0.8:
                recommendations.append("High confidence pattern - consider automation")
            
            insight = BehaviorInsight(
                insight_type=insight_type,
                title=title,
                description=description,
                confidence=pattern.confidence,
                impact_score=pattern.business_impact,
                actionability=0.8,
                affected_users=pattern.users_affected,
                recommendations=recommendations,
                data_points={
                    'pattern_id': pattern.pattern_id,
                    'frequency': pattern.frequency,
                    'support': pattern.support
                }
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to convert pattern to insight: {e}")
            return None
    
    async def _analyze_global_trends(self) -> List[BehaviorInsight]:
        """Analyse les tendances globales"""
        insights = []
        
        try:
            # Analyser l'évolution du nombre d'événements
            current_events = await self._count_recent_events(hours=24)
            previous_events = await self._count_recent_events(hours=48, offset_hours=24)
            
            if previous_events > 0:
                trend = (current_events - previous_events) / previous_events
                
                if abs(trend) > 0.2:  # Changement significatif de 20%
                    direction = "increasing" if trend > 0 else "decreasing"
                    insight = BehaviorInsight(
                        insight_type=BehaviorInsightType.TREND_IDENTIFICATION,
                        title=f"Activity Trend: {direction.title()}",
                        description=f"User activity is {direction} by {abs(trend)*100:.1f}%",
                        confidence=0.8,
                        impact_score=min(1.0, abs(trend)),
                        actionability=0.9,
                        data_points={
                            'trend_percentage': trend * 100,
                            'current_events': current_events,
                            'previous_events': previous_events
                        },
                        recommendations=[
                            "Monitor trend continuation",
                            "Investigate underlying causes",
                            "Adjust resource allocation if needed"
                        ]
                    )
                    insights.append(insight)
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze global trends: {e}")
        
        return insights
    
    async def _count_recent_events(self, hours: int, offset_hours: int = 0) -> int:
        """Compte les événements récents"""
        try:
            end_time = datetime.now() - timedelta(hours=offset_hours)
            start_time = end_time - timedelta(hours=hours)
            
            events = await self._get_events_between(start_time, end_time)
            return len(events)
            
        except Exception as e:
            logger.error(f"❌ Failed to count recent events: {e}")
            return 0
    
    async def _get_events_between(self, start_time: datetime, end_time: datetime) -> List[BehaviorEvent]:
        """Récupère les événements entre deux dates"""
        try:
            events = []
            pattern = "behavior:events:*"
            keys = await self._get_redis_keys(pattern)
            
            for key in keys:
                data = await self._get_redis_data(key)
                if data:
                    event_time = datetime.fromisoformat(data['timestamp'])
                    if start_time <= event_time <= end_time:
                        event = BehaviorEvent(**data)
                        events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to get events between {start_time} and {end_time}: {e}")
            return []
    
    async def _store_insight(self, insight: BehaviorInsight):
        """Stocke un insight dans Redis"""
        try:
            key = f"behavior:insights:{insight.insight_id}"
            data = {
                'insight_id': insight.insight_id,
                'insight_type': insight.insight_type.value,
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence,
                'impact_score': insight.impact_score,
                'actionability': insight.actionability,
                'affected_users': insight.affected_users,
                'recommendations': insight.recommendations,
                'data_points': insight.data_points,
                'business_metrics': insight.business_metrics,
                'created_at': insight.created_at.isoformat()
            }
            
            # TTL basé sur la date d'expiration ou 7 jours par défaut
            ttl = 7 * 24 * 3600  # 7 jours
            if insight.expires_at:
                ttl = int((insight.expires_at - datetime.now()).total_seconds())
            
            self.redis_client.setex(key, ttl, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store insight: {e}")
    
    async def _segmentation_loop(self):
        """Boucle de segmentation comportementale"""
        while self.is_running:
            try:
                logger.info("🔄 Starting behavior segmentation...")
                
                await self._perform_user_segmentation()
                
                logger.info("✅ Behavior segmentation completed")
                
                # Attendre avant la prochaine segmentation
                await asyncio.sleep(24 * 3600)  # 1 fois par jour
                
            except Exception as e:
                logger.error(f"❌ Error in segmentation loop: {e}")
                await asyncio.sleep(3600)  # Attendre 1 heure en cas d'erreur
    
    async def _perform_user_segmentation(self):
        """Effectue la segmentation des utilisateurs"""
        try:
            # Récupérer tous les utilisateurs avec leurs événements
            all_events = await self._get_events_since(
                datetime.now() - self.config.analysis_window
            )
            
            if len(all_events) < 100:
                logger.warning("⚠️ Insufficient events for segmentation")
                return
            
            # Grouper par utilisateur et créer des features
            user_features = {}
            for event in all_events:
                if event.user_id not in user_features:
                    user_features[event.user_id] = {
                        'event_count': 0,
                        'total_duration': 0,
                        'total_value': 0,
                        'unique_actions': set(),
                        'behavior_types': set(),
                        'avg_session_duration': 0,
                        'peak_hour': 0
                    }
                
                features = user_features[event.user_id]
                features['event_count'] += 1
                features['total_duration'] += event.duration
                features['total_value'] += event.value
                features['unique_actions'].add(event.action)
                features['behavior_types'].add(event.behavior_type.value)
                features['peak_hour'] = event.timestamp.hour  # Simplifié
            
            # Convertir en format numérique pour clustering
            user_ids = list(user_features.keys())
            feature_matrix = []
            
            for user_id in user_ids:
                features = user_features[user_id]
                feature_vector = [
                    features['event_count'],
                    features['total_duration'],
                    features['total_value'],
                    len(features['unique_actions']),
                    len(features['behavior_types']),
                    features['peak_hour']
                ]
                feature_matrix.append(feature_vector)
            
            feature_matrix = np.array(feature_matrix)
            
            # Normaliser les features
            if len(feature_matrix) > 0:
                feature_matrix = self.scaler.fit_transform(feature_matrix)
                
                # Effectuer le clustering
                if self.cluster_model:
                    cluster_labels = self.cluster_model.fit_predict(feature_matrix)
                    
                    # Créer les segments
                    segments = {}
                    for i, label in enumerate(cluster_labels):
                        if label not in segments:
                            segments[label] = []
                        segments[label].append(user_ids[i])
                    
                    # Créer les objets BehaviorSegment
                    for label, users in segments.items():
                        if len(users) >= 5:  # Minimum 5 utilisateurs par segment
                            segment = await self._create_behavior_segment(label, users, user_features)
                            self.segment_cache[segment.segment_id] = segment
                            await self._store_segment(segment)
                    
                    logger.info(f"✅ Created {len(segments)} user segments")
            
        except Exception as e:
            logger.error(f"❌ Failed to perform user segmentation: {e}")
    
    async def _create_behavior_segment(self, label: int, users: List[str], 
                                     user_features: Dict[str, Dict]) -> BehaviorSegment:
        """Crée un segment comportemental"""
        try:
            # Calculer les caractéristiques du segment
            characteristics = {
                'avg_event_count': 0,
                'avg_duration': 0,
                'avg_value': 0,
                'common_actions': [],
                'common_behavior_types': []
            }
            
            total_events = 0
            total_duration = 0
            total_value = 0
            all_actions = []
            all_behavior_types = []
            
            for user_id in users:
                features = user_features[user_id]
                total_events += features['event_count']
                total_duration += features['total_duration']
                total_value += features['total_value']
                all_actions.extend(list(features['unique_actions']))
                all_behavior_types.extend(list(features['behavior_types']))
            
            if len(users) > 0:
                characteristics['avg_event_count'] = total_events / len(users)
                characteristics['avg_duration'] = total_duration / len(users)
                characteristics['avg_value'] = total_value / len(users)
            
            # Actions et behavior types les plus communs
            from collections import Counter
            action_counts = Counter(all_actions)
            behavior_counts = Counter(all_behavior_types)
            
            characteristics['common_actions'] = [action for action, count in action_counts.most_common(5)]
            characteristics['common_behavior_types'] = [bt for bt, count in behavior_counts.most_common(3)]
            
            # Nommer le segment
            segment_name = f"Segment_{label}"
            if characteristics['avg_value'] > 50:
                segment_name = f"High_Value_Users_{label}"
            elif characteristics['avg_event_count'] > 100:
                segment_name = f"Highly_Active_Users_{label}"
            elif characteristics['avg_duration'] > 3600:
                segment_name = f"Engaged_Users_{label}"
            
            segment = BehaviorSegment(
                segment_name=segment_name,
                description=f"Behavioral segment with {len(users)} users",
                users=users,
                characteristics=characteristics,
                size=len(users),
                cohesion=0.8  # Simplifié
            )
            
            return segment
            
        except Exception as e:
            logger.error(f"❌ Failed to create behavior segment: {e}")
            return BehaviorSegment()
    
    async def _store_segment(self, segment: BehaviorSegment):
        """Stocke un segment dans Redis"""
        try:
            key = f"behavior:segments:{segment.segment_id}"
            data = {
                'segment_id': segment.segment_id,
                'segment_name': segment.segment_name,
                'description': segment.description,
                'users': segment.users,
                'characteristics': segment.characteristics,
                'behavior_patterns': segment.behavior_patterns,
                'engagement_metrics': segment.engagement_metrics,
                'value_metrics': segment.value_metrics,
                'size': segment.size,
                'cohesion': segment.cohesion,
                'created_at': segment.created_at.isoformat()
            }
            
            self.redis_client.setex(
                key,
                30 * 24 * 3600,  # 30 jours
                json.dumps(data)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to store segment: {e}")
    
    async def _prediction_loop(self):
        """Boucle de prédiction comportementale"""
        while self.is_running:
            try:
                logger.info("🔄 Starting behavior predictions...")
                
                await self._generate_behavior_predictions()
                
                logger.info("✅ Behavior predictions completed")
                
                # Attendre avant les prochaines prédictions
                await asyncio.sleep(6 * 3600)  # Toutes les 6 heures
                
            except Exception as e:
                logger.error(f"❌ Error in prediction loop: {e}")
                await asyncio.sleep(3600)  # Attendre 1 heure en cas d'erreur
    
    async def _generate_behavior_predictions(self):
        """Génère des prédictions comportementales"""
        try:
            # Récupérer les utilisateurs actifs
            recent_events = await self._get_events_since(
                datetime.now() - timedelta(days=7)
            )
            
            active_users = set(event.user_id for event in recent_events)
            
            for user_id in list(active_users)[:100]:  # Limiter à 100 utilisateurs
                prediction = await self._predict_user_behavior(user_id)
                if prediction:
                    self.prediction_cache[prediction.prediction_id] = prediction
                    await self._store_prediction(prediction)
                    self.metrics['predictions_made'] += 1
            
            logger.info(f"✅ Generated predictions for {len(active_users)} users")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate behavior predictions: {e}")
    
    async def _predict_user_behavior(self, user_id: str) -> Optional[BehaviorPrediction]:
        """Prédit le comportement d'un utilisateur"""
        try:
            # Récupérer l'historique de l'utilisateur
            user_events = await self._get_user_recent_events(user_id, hours=7*24)
            
            if len(user_events) < 5:
                return None
            
            # Analyser les patterns temporels
            hourly_activity = {}
            daily_activity = {}
            
            for event in user_events:
                hour = event.timestamp.hour
                day = event.timestamp.weekday()
                
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
                daily_activity[day] = daily_activity.get(day, 0) + 1
            
            # Prédire l'heure de prochaine activité
            if hourly_activity:
                predicted_hour = max(hourly_activity.items(), key=lambda x: x[1])[0]
                predicted_day = max(daily_activity.items(), key=lambda x: x[1])[0]
                
                # Prédire l'action la plus probable
                recent_actions = [event.action for event in user_events[-10:]]
                from collections import Counter
                action_counts = Counter(recent_actions)
                predicted_action = action_counts.most_common(1)[0][0] if action_counts else "unknown"
                
                # Calculer la probabilité (heuristique simple)
                probability = min(0.95, max(hourly_activity.values()) / len(user_events))
                
                prediction = BehaviorPrediction(
                    user_id=user_id,
                    predicted_behavior=predicted_action,
                    behavior_type=user_events[-1].behavior_type,
                    probability=probability,
                    confidence_interval=(probability - 0.1, probability + 0.1),
                    time_horizon=timedelta(hours=24),
                    factors={
                        'historical_frequency': probability,
                        'time_consistency': 0.8,
                        'pattern_strength': len(recent_actions) / 10
                    },
                    business_value=0.6,
                    recommendation=f"Expect {predicted_action} activity around {predicted_hour}:00"
                )
                
                return prediction
            
        except Exception as e:
            logger.error(f"❌ Failed to predict user behavior for {user_id}: {e}")
        
        return None
    
    async def _store_prediction(self, prediction: BehaviorPrediction):
        """Stocke une prédiction dans Redis"""
        try:
            key = f"behavior:predictions:{prediction.user_id}:{prediction.prediction_id}"
            data = {
                'prediction_id': prediction.prediction_id,
                'user_id': prediction.user_id,
                'predicted_behavior': prediction.predicted_behavior,
                'behavior_type': prediction.behavior_type.value,
                'probability': prediction.probability,
                'confidence_interval': prediction.confidence_interval,
                'time_horizon': prediction.time_horizon.total_seconds(),
                'factors': prediction.factors,
                'business_value': prediction.business_value,
                'recommendation': prediction.recommendation,
                'created_at': prediction.created_at.isoformat()
            }
            
            ttl = int(prediction.time_horizon.total_seconds()) + 3600  # +1h buffer
            self.redis_client.setex(key, ttl, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store prediction: {e}")
    
    async def get_user_insights(self, user_id: str) -> List[BehaviorInsight]:
        """Récupère les insights d'un utilisateur"""
        try:
            insights = []
            
            for insight in self.insight_cache.values():
                if user_id in insight.affected_users:
                    insights.append(insight)
            
            # Trier par impact et confiance
            insights.sort(key=lambda x: (x.impact_score, x.confidence), reverse=True)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get user insights: {e}")
            return []
    
    async def get_user_predictions(self, user_id: str) -> List[BehaviorPrediction]:
        """Récupère les prédictions d'un utilisateur"""
        try:
            predictions = []
            
            for prediction in self.prediction_cache.values():
                if prediction.user_id == user_id:
                    predictions.append(prediction)
            
            # Trier par probabilité
            predictions.sort(key=lambda x: x.probability, reverse=True)
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Failed to get user predictions: {e}")
            return []
    
    async def get_behavior_segments(self) -> List[BehaviorSegment]:
        """Récupère tous les segments comportementaux"""
        try:
            segments = list(self.segment_cache.values())
            segments.sort(key=lambda x: x.size, reverse=True)
            return segments
            
        except Exception as e:
            logger.error(f"❌ Failed to get behavior segments: {e}")
            return []
    
    async def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de l'orchestrateur"""
        try:
            avg_latency = statistics.mean(self.metrics['analysis_latency']) if self.metrics['analysis_latency'] else 0
            
            return {
                'events_processed': self.metrics['events_processed'],
                'patterns_identified': self.metrics['patterns_identified'],
                'insights_generated': self.metrics['insights_generated'],
                'predictions_made': self.metrics['predictions_made'],
                'avg_analysis_latency_ms': avg_latency * 1000,
                'cached_patterns': len(self.pattern_cache),
                'cached_segments': len(self.segment_cache),
                'cached_insights': len(self.insight_cache),
                'cached_predictions': len(self.prediction_cache),
                'last_analysis': self.metrics['last_analysis'].isoformat() if self.metrics['last_analysis'] else None,
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get orchestrator metrics: {e}")
            return {}
    
    async def shutdown(self):
        """Arrête l'orchestrateur"""
        try:
            logger.info("🛑 Shutting down Behavior Analysis Orchestrator...")
            
            self.is_running = False
            
            # Arrêter les tâches d'analyse
            for task_name, task in self.analysis_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                    logger.info(f"✅ {task_name} task stopped")
            
            logger.info("✅ Behavior Analysis Orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Factory function pour créer l'orchestrateur
async def create_behavior_analysis_orchestrator(
    config: Optional[BehaviorAnalysisConfig] = None,
    redis_client_instance: Optional[Any] = None
) -> RedisBehaviorAnalysisOrchestrator:
    """Crée et initialise un orchestrateur d'analyse comportementale"""
    
    if config is None:
        config = BehaviorAnalysisConfig()
    
    orchestrator = RedisBehaviorAnalysisOrchestrator(config, redis_client_instance)
    
    if await orchestrator.initialize():
        return orchestrator
    else:
        raise RuntimeError("Failed to initialize Behavior Analysis Orchestrator")

__all__ = [
    'RedisBehaviorAnalysisOrchestrator',
    'BehaviorAnalysisConfig',
    'BehaviorEvent',
    'BehaviorPattern',
    'BehaviorSegment',
    'BehaviorInsight',
    'BehaviorPrediction',
    'BehaviorType',
    'BehaviorState',
    'AnalysisScope',
    'BehaviorInsightType',
    'create_behavior_analysis_orchestrator'
]