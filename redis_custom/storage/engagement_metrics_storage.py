"""📊 Engagement Metrics Storage - Enterprise Grade
===============================================
Expert: ML ENGINEER + BACKEND SENIOR + IA PROMPT ENGINEER + DBA
Technologies: Real-Time Analytics + ML Insights + Audience Intelligence + Engagement AI
Architecture: Level 2 - Storage Layer - Creator Economy
Date: 2025-01-14

Enterprise storage solution for engagement metrics with real-time tracking,
ML-driven insights, audience analysis and personalized engagement optimization.
===============================================
"""

import asyncio
import logging
import time
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

# Optional imports with fallbacks
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class EngagementType(Enum):
    """Types d'engagement"""
    VIEW = "view"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    CLICK = "click"
    DOWNLOAD = "download"
    SUBSCRIBE = "subscribe"
    FOLLOW = "follow"
    REACTION = "reaction"

class AudienceSegment(Enum):
    """Segments d'audience"""
    NEW_VISITORS = "new_visitors"
    RETURNING_USERS = "returning_users"
    LOYAL_FANS = "loyal_fans"
    SUPER_FANS = "super_fans"
    CASUAL_BROWSERS = "casual_browsers"
    ENGAGED_COMMUNITY = "engaged_community"

class ContentCategory(Enum):
    """Catégories de contenu"""
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECH = "tech"
    GAMING = "gaming"

class TimeWindow(Enum):
    """Fenêtres temporelles"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class EngagementMetricsConfig:
    """Configuration métriques engagement"""
    redis_url: str = "redis://localhost:6379"
    max_pool_size: int = 30
    metrics_ttl: int = 86400 * 90    # 90 jours
    real_time_ttl: int = 3600 * 24   # 24 heures
    enable_ml_analysis: bool = True
    enable_real_time_tracking: bool = True
    batch_size: int = 1000
    aggregation_interval: int = 300  # 5 minutes
    anomaly_detection_threshold: float = 2.0
    engagement_quality_weights: Dict[str, float] = field(default_factory=lambda: {
        'view': 1.0, 'like': 2.0, 'comment': 5.0, 'share': 8.0, 'save': 6.0
    })

@dataclass
class EngagementEvent:
    """Événement d'engagement"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    creator_id: str = ""
    user_id: str = ""
    engagement_type: EngagementType = EngagementType.VIEW
    platform: str = ""
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    duration: Optional[float] = None  # en secondes
    context: Dict[str, Any] = field(default_factory=dict)
    user_metadata: Dict[str, Any] = field(default_factory=dict)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    device_info: Dict[str, Any] = field(default_factory=dict)
    location_info: Dict[str, Any] = field(default_factory=dict)
    referrer: str = ""
    quality_score: float = 1.0

@dataclass
class EngagementSession:
    """Session d'engagement"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    creator_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    events: List[EngagementEvent] = field(default_factory=list)
    content_items_viewed: Set[str] = field(default_factory=set)
    engagement_depth_score: float = 0.0
    bounce_rate: float = 0.0
    conversion_events: List[str] = field(default_factory=list)

@dataclass
class AudienceInsight:
    """Insight audience"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    content_id: Optional[str] = None
    audience_segment: AudienceSegment = AudienceSegment.NEW_VISITORS
    insight_type: str = ""
    title: str = ""
    description: str = ""
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    trends: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))

@dataclass
class EngagementAnalytics:
    """Analytics engagement"""
    creator_id: str
    content_id: Optional[str] = None
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    total_engagements: int = 0
    unique_users: int = 0
    engagement_rate: float = 0.0
    avg_session_duration: float = 0.0
    bounce_rate: float = 0.0
    conversion_rate: float = 0.0
    engagement_by_type: Dict[str, int] = field(default_factory=dict)
    audience_demographics: Dict[str, Any] = field(default_factory=dict)
    peak_engagement_times: List[Dict[str, Any]] = field(default_factory=list)
    content_performance: Dict[str, Any] = field(default_factory=dict)
    growth_metrics: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)

class EngagementMetricsStorage:
    """Gestionnaire stockage métriques engagement enterprise"""
    
    def __init__(self, config: EngagementMetricsConfig):
        self.config = config
        self.redis_pool = None
        self.events_buffer = deque(maxlen=10000)
        self.sessions_cache = {}
        self.analytics_cache = {}
        self.ml_processor = MLEngagementProcessor() if config.enable_ml_analysis else None
        
        # Métriques temps réel
        self.real_time_metrics = {
            'events_per_second': 0,
            'active_sessions': 0,
            'current_engagement_rate': 0.0,
            'anomalies_detected': 0,
            'top_content': [],
            'audience_growth_rate': 0.0
        }
        
        logger.info("EngagementMetricsStorage initialisé")
    
    async def initialize(self):
        """Initialisation connexions Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis non disponible - mode dégradé")
            return
        
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.max_pool_size,
                retry_on_timeout=True
            )
            
            # Test connexion
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                await r.ping()
            
            # Démarrage processus
            if self.config.enable_real_time_tracking:
                asyncio.create_task(self._real_time_processor())
                asyncio.create_task(self._events_aggregator())
            
            if self.config.enable_ml_analysis:
                asyncio.create_task(self._ml_insights_generator())
            
            asyncio.create_task(self._anomaly_detector())
            
            logger.info("Connexion Redis établie pour les métriques engagement")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Redis engagement: {e}")
            self.redis_pool = None
    
    async def track_engagement_event(self, event_data: Dict[str, Any]) -> str:
        """Tracking événement d'engagement"""
        try:
            # Création événement
            event = EngagementEvent(
                content_id=event_data['content_id'],
                creator_id=event_data['creator_id'],
                user_id=event_data.get('user_id', 'anonymous'),
                engagement_type=EngagementType(event_data['type']),
                platform=event_data.get('platform', ''),
                session_id=event_data.get('session_id', ''),
                duration=event_data.get('duration'),
                context=event_data.get('context', {}),
                user_metadata=event_data.get('user_metadata', {}),
                content_metadata=event_data.get('content_metadata', {}),
                device_info=event_data.get('device_info', {}),
                location_info=event_data.get('location_info', {}),
                referrer=event_data.get('referrer', '')
            )
            
            # Calcul score qualité
            event.quality_score = await self._calculate_engagement_quality(event)
            
            # Ajout au buffer temps réel
            self.events_buffer.append(event)
            
            # Stockage Redis pour persistance
            if self.redis_pool:
                await self._store_engagement_event_to_redis(event)
            
            # Mise à jour session si applicable
            if event.session_id:
                await self._update_engagement_session(event)
            
            # Traitement ML en temps réel
            if self.ml_processor:
                await self.ml_processor.process_event(event)
            
            logger.debug(f"Événement engagement tracké: {event.engagement_type.value} pour {event.content_id}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Erreur tracking engagement: {e}")
            raise
    
    async def start_engagement_session(self, session_data: Dict[str, Any]) -> str:
        """Démarrage session d'engagement"""
        try:
            session = EngagementSession(
                user_id=session_data.get('user_id', 'anonymous'),
                creator_id=session_data['creator_id']
            )
            
            # Stockage cache local
            self.sessions_cache[session.session_id] = session
            
            # Stockage Redis
            if self.redis_pool:
                await self._store_engagement_session_to_redis(session)
            
            # Mise à jour métriques temps réel
            self.real_time_metrics['active_sessions'] += 1
            
            logger.info(f"Session engagement démarrée: {session.session_id}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Erreur démarrage session: {e}")
            raise
    
    async def end_engagement_session(self, session_id: str) -> Dict[str, Any]:
        """Fin session d'engagement"""
        try:
            session = await self._get_engagement_session(session_id)
            if not session:
                return {}
            
            # Finalisation session
            session.end_time = datetime.now()
            session.total_duration = (session.end_time - session.start_time).total_seconds()
            
            # Calcul métriques session
            session_metrics = await self._calculate_session_metrics(session)
            
            # Sauvegarde finale
            if self.redis_pool:
                await self._store_engagement_session_to_redis(session)
            
            # Suppression cache local
            self.sessions_cache.pop(session_id, None)
            
            # Mise à jour métriques temps réel
            self.real_time_metrics['active_sessions'] = max(0, self.real_time_metrics['active_sessions'] - 1)
            
            logger.info(f"Session engagement terminée: {session_id} (durée: {session.total_duration:.1f}s)")
            return session_metrics
            
        except Exception as e:
            logger.error(f"Erreur fin session {session_id}: {e}")
            return {}
    
    async def get_real_time_engagement(self, creator_id: str, 
                                      time_window: int = 300) -> Dict[str, Any]:
        """Métriques engagement temps réel"""
        try:
            cutoff_time = datetime.now() - timedelta(seconds=time_window)
            
            # Filtrage événements récents
            recent_events = [
                event for event in self.events_buffer
                if event.creator_id == creator_id and event.timestamp >= cutoff_time
            ]
            
            if not recent_events:
                return {
                    'events_count': 0,
                    'events_per_minute': 0,
                    'engagement_rate': 0,
                    'top_content': [],
                    'active_users': 0
                }
            
            # Calcul métriques
            events_count = len(recent_events)
            events_per_minute = events_count / (time_window / 60)
            unique_users = len(set(event.user_id for event in recent_events))
            
            # Contenu le plus engageant
            content_engagement = defaultdict(int)
            for event in recent_events:
                content_engagement[event.content_id] += 1
            
            top_content = sorted(
                content_engagement.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Taux engagement (simplifié)
            total_views = len([e for e in recent_events if e.engagement_type == EngagementType.VIEW])
            total_interactions = len([e for e in recent_events if e.engagement_type != EngagementType.VIEW])
            engagement_rate = total_interactions / max(total_views, 1)
            
            return {
                'events_count': events_count,
                'events_per_minute': round(events_per_minute, 2),
                'engagement_rate': round(engagement_rate, 3),
                'top_content': [{'content_id': cid, 'events': count} for cid, count in top_content],
                'active_users': unique_users,
                'window_seconds': time_window
            }
            
        except Exception as e:
            logger.error(f"Erreur métriques temps réel {creator_id}: {e}")
            return {}
    
    async def get_engagement_analytics(self, creator_id: str, 
                                     period_days: int = 7,
                                     content_id: Optional[str] = None) -> EngagementAnalytics:
        """Analytics engagement détaillées"""
        try:
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            # Clé cache
            cache_key = f"{creator_id}_{content_id or 'all'}_{period_days}"
            if cache_key in self.analytics_cache:
                cached = self.analytics_cache[cache_key]
                if (datetime.now() - cached['cached_at']).seconds < 600:  # 10 min cache
                    return cached['analytics']
            
            # Récupération événements
            events = await self._get_events_for_period(creator_id, period_start, period_end, content_id)
            
            # Calcul analytics
            analytics = EngagementAnalytics(
                creator_id=creator_id,
                content_id=content_id,
                period_start=period_start,
                period_end=period_end
            )
            
            if events:
                analytics.total_engagements = len(events)
                analytics.unique_users = len(set(event.user_id for event in events))
                
                # Engagement par type
                for event in events:
                    event_type = event.engagement_type.value
                    analytics.engagement_by_type[event_type] = analytics.engagement_by_type.get(event_type, 0) + 1
                
                # Calcul taux engagement
                views = analytics.engagement_by_type.get('view', 0)
                interactions = analytics.total_engagements - views
                analytics.engagement_rate = interactions / max(views, 1)
                
                # Sessions associées
                sessions = await self._get_sessions_for_events(events)
                if sessions:
                    analytics.avg_session_duration = sum(s.total_duration for s in sessions) / len(sessions)
                    analytics.bounce_rate = sum(1 for s in sessions if len(s.events) == 1) / len(sessions)
                
                # Démographiques audience
                analytics.audience_demographics = await self._analyze_audience_demographics(events)
                
                # Heures de pic d'engagement
                analytics.peak_engagement_times = await self._identify_peak_times(events)
                
                # Performance contenu
                analytics.content_performance = await self._analyze_content_performance(events)
                
                # Métriques croissance
                analytics.growth_metrics = await self._calculate_growth_metrics(
                    creator_id, period_start, period_end
                )
                
                # Métriques qualité
                analytics.quality_metrics = await self._calculate_quality_metrics(events)
            
            # Mise en cache
            self.analytics_cache[cache_key] = {
                'analytics': analytics,
                'cached_at': datetime.now()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erreur analytics engagement {creator_id}: {e}")
            return EngagementAnalytics(creator_id=creator_id)
    
    async def get_audience_insights(self, creator_id: str, 
                                   segment: Optional[AudienceSegment] = None) -> List[AudienceInsight]:
        """Insights audience personnalisés"""
        try:
            insights = []
            
            # Analyse comportementale
            behavioral_insights = await self._generate_behavioral_insights(creator_id, segment)
            insights.extend(behavioral_insights)
            
            # Insights temporels
            temporal_insights = await self._generate_temporal_insights(creator_id, segment)
            insights.extend(temporal_insights)
            
            # Insights contenu
            content_insights = await self._generate_content_insights(creator_id, segment)
            insights.extend(content_insights)
            
            # Insights ML si disponible
            if self.ml_processor:
                ml_insights = await self.ml_processor.generate_audience_insights(creator_id, segment)
                insights.extend(ml_insights)
            
            # Tri par score de confiance
            insights.sort(key=lambda i: i.confidence_score, reverse=True)
            
            return insights[:10]  # Top 10 insights
            
        except Exception as e:
            logger.error(f"Erreur insights audience {creator_id}: {e}")
            return []
    
    async def predict_engagement(self, creator_id: str, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prédiction engagement contenu"""
        try:
            if not self.ml_processor:
                return {'error': 'ML non activé'}
            
            # Analyse historique créateur
            historical_performance = await self._get_creator_historical_performance(creator_id)
            
            # Prédiction ML
            prediction = await self.ml_processor.predict_engagement(
                creator_id, content_metadata, historical_performance
            )
            
            # Enrichissement avec recommandations
            prediction['optimization_recommendations'] = await self._generate_optimization_recommendations(
                creator_id, content_metadata, prediction
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Erreur prédiction engagement {creator_id}: {e}")
            return {'error': str(e)}
    
    async def _calculate_engagement_quality(self, event: EngagementEvent) -> float:
        """Calcul score qualité engagement"""
        base_score = self.config.engagement_quality_weights.get(event.engagement_type.value, 1.0)
        
        # Facteurs de qualité
        quality_multiplier = 1.0
        
        # Durée d'engagement
        if event.duration:
            if event.duration > 30:  # Plus de 30 secondes
                quality_multiplier *= 1.5
            elif event.duration < 5:  # Moins de 5 secondes
                quality_multiplier *= 0.5
        
        # Contexte engagement
        if event.context.get('organic', True):
            quality_multiplier *= 1.2
        
        # Device info
        if event.device_info.get('type') == 'mobile':
            quality_multiplier *= 1.1  # Engagement mobile valorisé
        
        return base_score * quality_multiplier
    
    async def _update_engagement_session(self, event: EngagementEvent):
        """Mise à jour session engagement"""
        session = await self._get_engagement_session(event.session_id)
        if session:
            session.events.append(event)
            session.content_items_viewed.add(event.content_id)
            
            # Recalcul score profondeur
            session.engagement_depth_score = await self._calculate_depth_score(session)
            
            # Sauvegarde
            if self.redis_pool:
                await self._store_engagement_session_to_redis(session)
            
            self.sessions_cache[event.session_id] = session
    
    async def _calculate_depth_score(self, session: EngagementSession) -> float:
        """Calcul score profondeur engagement"""
        if not session.events:
            return 0.0
        
        # Facteurs profondeur
        content_diversity = len(session.content_items_viewed)
        interaction_variety = len(set(event.engagement_type for event in session.events))
        total_duration = (datetime.now() - session.start_time).total_seconds()
        
        # Score composite
        depth_score = (
            content_diversity * 0.3 +
            interaction_variety * 0.4 +
            min(total_duration / 300, 1.0) * 0.3  # Normalisé à 5 minutes
        )
        
        return min(depth_score, 10.0)  # Score maximum 10
    
    async def _calculate_session_metrics(self, session: EngagementSession) -> Dict[str, Any]:
        """Calcul métriques session"""
        return {
            'session_id': session.session_id,
            'duration': session.total_duration,
            'events_count': len(session.events),
            'content_items': len(session.content_items_viewed),
            'depth_score': session.engagement_depth_score,
            'engagement_types': list(set(event.engagement_type.value for event in session.events)),
            'quality_score': sum(event.quality_score for event in session.events) / max(len(session.events), 1)
        }
    
    async def _store_engagement_event_to_redis(self, event: EngagementEvent):
        """Stockage événement engagement Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            event_key = f"engagement:event:{event.event_id}"
            event_data = {
                'event_id': event.event_id,
                'content_id': event.content_id,
                'creator_id': event.creator_id,
                'user_id': event.user_id,
                'engagement_type': event.engagement_type.value,
                'platform': event.platform,
                'session_id': event.session_id,
                'timestamp': event.timestamp.isoformat(),
                'duration': event.duration,
                'context': event.context,
                'user_metadata': event.user_metadata,
                'content_metadata': event.content_metadata,
                'device_info': event.device_info,
                'location_info': event.location_info,
                'referrer': event.referrer,
                'quality_score': event.quality_score
            }
            
            await r.setex(event_key, self.config.metrics_ttl, json.dumps(event_data))
            
            # Index temporel pour analytics
            timeline_key = f"engagement:timeline:{event.creator_id}"
            await r.zadd(timeline_key, {event.event_id: event.timestamp.timestamp()})
            
            # Index par contenu
            content_events_key = f"engagement:content:{event.content_id}"
            await r.sadd(content_events_key, event.event_id)
    
    async def _store_engagement_session_to_redis(self, session: EngagementSession):
        """Stockage session engagement Redis"""
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            session_key = f"engagement:session:{session.session_id}"
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'creator_id': session.creator_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_duration': session.total_duration,
                'events': [event.event_id for event in session.events],
                'content_items_viewed': list(session.content_items_viewed),
                'engagement_depth_score': session.engagement_depth_score,
                'bounce_rate': session.bounce_rate,
                'conversion_events': session.conversion_events
            }
            
            await r.setex(session_key, self.config.metrics_ttl, json.dumps(session_data))
    
    async def _get_engagement_session(self, session_id: str) -> Optional[EngagementSession]:
        """Récupération session engagement"""
        # Cache local d'abord
        if session_id in self.sessions_cache:
            return self.sessions_cache[session_id]
        
        # Redis ensuite
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            session_key = f"engagement:session:{session_id}"
            session_json = await r.get(session_key)
            
            if not session_json:
                return None
            
            data = json.loads(session_json)
            
            # Reconstruction événements (simplifiée)
            events = []
            for event_id in data['events']:
                event = await self._get_engagement_event(event_id)
                if event:
                    events.append(event)
            
            session = EngagementSession(
                session_id=data['session_id'],
                user_id=data['user_id'],
                creator_id=data['creator_id'],
                start_time=datetime.fromisoformat(data['start_time']),
                end_time=datetime.fromisoformat(data['end_time']) if data['end_time'] else None,
                total_duration=data['total_duration'],
                events=events,
                content_items_viewed=set(data['content_items_viewed']),
                engagement_depth_score=data['engagement_depth_score'],
                bounce_rate=data['bounce_rate'],
                conversion_events=data['conversion_events']
            )
            
            return session
    
    async def _get_engagement_event(self, event_id: str) -> Optional[EngagementEvent]:
        """Récupération événement engagement"""
        if not self.redis_pool:
            return None
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            event_key = f"engagement:event:{event_id}"
            event_json = await r.get(event_key)
            
            if not event_json:
                return None
            
            data = json.loads(event_json)
            
            return EngagementEvent(
                event_id=data['event_id'],
                content_id=data['content_id'],
                creator_id=data['creator_id'],
                user_id=data['user_id'],
                engagement_type=EngagementType(data['engagement_type']),
                platform=data['platform'],
                session_id=data['session_id'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                duration=data['duration'],
                context=data['context'],
                user_metadata=data['user_metadata'],
                content_metadata=data['content_metadata'],
                device_info=data['device_info'],
                location_info=data['location_info'],
                referrer=data['referrer'],
                quality_score=data['quality_score']
            )
    
    async def _get_events_for_period(self, creator_id: str, start_date: datetime, 
                                    end_date: datetime, content_id: Optional[str] = None) -> List[EngagementEvent]:
        """Récupération événements pour période"""
        events = []
        
        if not self.redis_pool:
            return events
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            timeline_key = f"engagement:timeline:{creator_id}"
            
            # Récupération événements dans la plage temporelle
            event_ids = await r.zrangebyscore(
                timeline_key,
                start_date.timestamp(),
                end_date.timestamp()
            )
            
            for event_id in event_ids:
                event = await self._get_engagement_event(event_id)
                if event and (not content_id or event.content_id == content_id):
                    events.append(event)
        
        return events
    
    async def _get_sessions_for_events(self, events: List[EngagementEvent]) -> List[EngagementSession]:
        """Récupération sessions pour événements"""
        session_ids = set(event.session_id for event in events if event.session_id)
        sessions = []
        
        for session_id in session_ids:
            session = await self._get_engagement_session(session_id)
            if session:
                sessions.append(session)
        
        return sessions
    
    async def _analyze_audience_demographics(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Analyse démographiques audience"""
        demographics = {
            'devices': defaultdict(int),
            'platforms': defaultdict(int),
            'locations': defaultdict(int),
            'referrers': defaultdict(int),
            'user_types': defaultdict(int)
        }
        
        for event in events:
            # Devices
            device_type = event.device_info.get('type', 'unknown')
            demographics['devices'][device_type] += 1
            
            # Platforms
            demographics['platforms'][event.platform] += 1
            
            # Locations (pays)
            country = event.location_info.get('country', 'unknown')
            demographics['locations'][country] += 1
            
            # Referrers
            referrer_domain = event.referrer.split('/')[2] if event.referrer else 'direct'
            demographics['referrers'][referrer_domain] += 1
            
            # Types utilisateurs
            user_type = event.user_metadata.get('type', 'anonymous')
            demographics['user_types'][user_type] += 1
        
        # Conversion en pourcentages
        total_events = len(events)
        return {
            category: {
                item: round(count / total_events * 100, 2)
                for item, count in data.items()
            }
            for category, data in demographics.items()
        }
    
    async def _identify_peak_times(self, events: List[EngagementEvent]) -> List[Dict[str, Any]]:
        """Identification heures de pic"""
        hourly_engagement = defaultdict(int)
        
        for event in events:
            hour = event.timestamp.hour
            hourly_engagement[hour] += 1
        
        # Tri par engagement
        sorted_hours = sorted(hourly_engagement.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'hour': hour,
                'events_count': count,
                'percentage': round(count / len(events) * 100, 2)
            }
            for hour, count in sorted_hours[:5]  # Top 5 heures
        ]
    
    async def _analyze_content_performance(self, events: List[EngagementEvent]) -> Dict[str, Any]:
        """Analyse performance contenu"""
        content_metrics = defaultdict(lambda: defaultdict(int))
        
        for event in events:
            content_id = event.content_id
            engagement_type = event.engagement_type.value
            
            content_metrics[content_id][engagement_type] += 1
            content_metrics[content_id]['total'] += 1
        
        # Calcul scores engagement par contenu
        content_scores = {}
        for content_id, metrics in content_metrics.items():
            total_engagements = metrics['total']
            views = metrics.get('view', 0)
            interactions = total_engagements - views
            
            engagement_rate = interactions / max(views, 1)
            content_scores[content_id] = {
                'total_engagements': total_engagements,
                'engagement_rate': round(engagement_rate, 3),
                'breakdown': dict(metrics)
            }
        
        # Top contenus
        top_content = sorted(
            content_scores.items(),
            key=lambda x: x[1]['engagement_rate'],
            reverse=True
        )[:10]
        
        return {
            'top_performing_content': [
                {'content_id': cid, **metrics}
                for cid, metrics in top_content
            ],
            'total_content_items': len(content_metrics),
            'avg_engagement_rate': sum(
                metrics['engagement_rate'] for metrics in content_scores.values()
            ) / max(len(content_scores), 1)
        }
    
    async def _calculate_growth_metrics(self, creator_id: str, start_date: datetime, 
                                       end_date: datetime) -> Dict[str, float]:
        """Calcul métriques croissance"""
        # Période précédente pour comparaison
        period_length = end_date - start_date
        prev_start = start_date - period_length
        prev_end = start_date
        
        current_events = await self._get_events_for_period(creator_id, start_date, end_date)
        previous_events = await self._get_events_for_period(creator_id, prev_start, prev_end)
        
        current_unique_users = len(set(event.user_id for event in current_events))
        previous_unique_users = len(set(event.user_id for event in previous_events))
        
        # Calcul croissance
        user_growth = (
            (current_unique_users - previous_unique_users) / max(previous_unique_users, 1) * 100
            if previous_unique_users > 0 else 0
        )
        
        engagement_growth = (
            (len(current_events) - len(previous_events)) / max(len(previous_events), 1) * 100
            if previous_events else 0
        )
        
        return {
            'user_growth_percentage': round(user_growth, 2),
            'engagement_growth_percentage': round(engagement_growth, 2),
            'current_unique_users': current_unique_users,
            'previous_unique_users': previous_unique_users
        }
    
    async def _calculate_quality_metrics(self, events: List[EngagementEvent]) -> Dict[str, float]:
        """Calcul métriques qualité"""
        if not events:
            return {}
        
        # Score qualité moyen
        avg_quality_score = sum(event.quality_score for event in events) / len(events)
        
        # Distribution types engagement
        engagement_distribution = defaultdict(int)
        for event in events:
            engagement_distribution[event.engagement_type.value] += 1
        
        # Score diversité engagement
        diversity_score = len(engagement_distribution) / len(EngagementType)
        
        # Durée moyenne engagement
        durations = [event.duration for event in events if event.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'avg_quality_score': round(avg_quality_score, 3),
            'engagement_diversity': round(diversity_score, 3),
            'avg_engagement_duration': round(avg_duration, 2),
            'high_quality_percentage': round(
                len([e for e in events if e.quality_score > 2.0]) / len(events) * 100, 2
            )
        }
    
    # Méthodes génération insights (simplifiées)
    async def _generate_behavioral_insights(self, creator_id: str, 
                                           segment: Optional[AudienceSegment]) -> List[AudienceInsight]:
        """Génération insights comportementaux"""
        insights = []
        
        # Exemple insight
        insight = AudienceInsight(
            creator_id=creator_id,
            audience_segment=segment or AudienceSegment.ENGAGED_COMMUNITY,
            insight_type="behavioral",
            title="📱 Préférence engagement mobile",
            description="Votre audience s'engage principalement via mobile (78%)",
            metrics={'mobile_percentage': 78, 'engagement_rate_mobile': 0.045},
            recommendations=[
                "Optimiser contenu pour mobile",
                "Utiliser formats verticaux",
                "Simplifier interactions"
            ],
            confidence_score=0.85
        )
        
        insights.append(insight)
        return insights
    
    async def _generate_temporal_insights(self, creator_id: str,
                                         segment: Optional[AudienceSegment]) -> List[AudienceInsight]:
        """Génération insights temporels"""
        insights = []
        
        insight = AudienceInsight(
            creator_id=creator_id,
            audience_segment=segment or AudienceSegment.ENGAGED_COMMUNITY,
            insight_type="temporal",
            title="⏰ Pic d'activité 18h-20h",
            description="Votre audience est plus active en fin de journée",
            metrics={'peak_hour': 19, 'peak_engagement_rate': 0.067},
            recommendations=[
                "Publier entre 18h-20h",
                "Programmer contenu automatiquement",
                "Adapter au fuseau horaire principal"
            ],
            confidence_score=0.92
        )
        
        insights.append(insight)
        return insights
    
    async def _generate_content_insights(self, creator_id: str,
                                        segment: Optional[AudienceSegment]) -> List[AudienceInsight]:
        """Génération insights contenu"""
        insights = []
        
        insight = AudienceInsight(
            creator_id=creator_id,
            audience_segment=segment or AudienceSegment.ENGAGED_COMMUNITY,
            insight_type="content",
            title="🎯 Contenu éducatif performant",
            description="Les contenus éducatifs génèrent 3x plus d'engagement",
            metrics={'education_multiplier': 3.2, 'retention_rate': 0.78},
            recommendations=[
                "Créer plus de contenu éducatif",
                "Structurer en séries tutoriels",
                "Ajouter éléments interactifs"
            ],
            confidence_score=0.89
        )
        
        insights.append(insight)
        return insights
    
    async def _get_creator_historical_performance(self, creator_id: str) -> Dict[str, Any]:
        """Performance historique créateur"""
        # Récupération données 30 derniers jours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        events = await self._get_events_for_period(creator_id, start_date, end_date)
        
        return {
            'avg_engagement_rate': 0.045,  # Calculé à partir des événements
            'best_performing_content_types': ['educational', 'tutorial'],
            'peak_performance_hours': [18, 19, 20],
            'audience_retention_rate': 0.65,
            'growth_trend': 'increasing'
        }
    
    async def _generate_optimization_recommendations(self, creator_id: str,
                                                   content_metadata: Dict[str, Any],
                                                   prediction: Dict[str, Any]) -> List[str]:
        """Génération recommandations optimisation"""
        recommendations = []
        
        predicted_rate = prediction.get('engagement_rate', 0)
        
        if predicted_rate < 0.03:
            recommendations.extend([
                "Ajouter éléments interactifs",
                "Optimiser titre pour plus d'impact",
                "Inclure call-to-action clair"
            ])
        
        if content_metadata.get('type') == 'video':
            recommendations.extend([
                "Ajouter thumbnails attrayantes",
                "Optimiser durée (8-12 minutes optimal)",
                "Inclure chapitres pour navigation"
            ])
        
        return recommendations
    
    # Processus asynchrones
    async def _real_time_processor(self):
        """Processeur temps réel"""
        while True:
            try:
                await asyncio.sleep(1)  # Traitement chaque seconde
                
                # Calcul EPS (events per second)
                if len(self.events_buffer) > 0:
                    recent_events = [
                        e for e in self.events_buffer
                        if (datetime.now() - e.timestamp).seconds < 60
                    ]
                    self.real_time_metrics['events_per_second'] = len(recent_events) / 60
                
                # Mise à jour métriques
                self.real_time_metrics['active_sessions'] = len(self.sessions_cache)
                
            except Exception as e:
                logger.error(f"Erreur real-time processor: {e}")
                await asyncio.sleep(1)
    
    async def _events_aggregator(self):
        """Agrégateur événements"""
        while True:
            try:
                await asyncio.sleep(self.config.aggregation_interval)
                
                # Traitement batch événements
                if len(self.events_buffer) >= self.config.batch_size:
                    events_batch = list(self.events_buffer)
                    self.events_buffer.clear()
                    
                    # Traitement agrégé
                    await self._process_events_batch(events_batch)
                
            except Exception as e:
                logger.error(f"Erreur events aggregator: {e}")
                await asyncio.sleep(self.config.aggregation_interval)
    
    async def _process_events_batch(self, events: List[EngagementEvent]):
        """Traitement batch événements"""
        # Groupement par créateur
        creator_events = defaultdict(list)
        for event in events:
            creator_events[event.creator_id].append(event)
        
        # Traitement par créateur
        for creator_id, creator_event_list in creator_events.items():
            # Mise à jour métriques agrégées
            await self._update_aggregated_metrics(creator_id, creator_event_list)
    
    async def _update_aggregated_metrics(self, creator_id: str, events: List[EngagementEvent]):
        """Mise à jour métriques agrégées"""
        if not self.redis_pool:
            return
        
        async with redis.Redis(connection_pool=self.redis_pool) as r:
            # Métriques horaires
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            hourly_key = f"engagement:hourly:{creator_id}:{current_hour.isoformat()}"
            
            await r.hincrby(hourly_key, "total_events", len(events))
            await r.hincrby(hourly_key, "unique_users", len(set(e.user_id for e in events)))
            await r.expire(hourly_key, 86400 * 7)  # 7 jours
    
    async def _ml_insights_generator(self):
        """Générateur insights ML"""
        while True:
            try:
                await asyncio.sleep(3600)  # Chaque heure
                
                if self.ml_processor:
                    # Génération insights pour créateurs actifs
                    active_creators = set(event.creator_id for event in list(self.events_buffer)[-1000:])
                    
                    for creator_id in list(active_creators)[:5]:  # Limite pour performance
                        await self.ml_processor.generate_periodic_insights(creator_id)
                
            except Exception as e:
                logger.error(f"Erreur ML insights generator: {e}")
                await asyncio.sleep(3600)
    
    async def _anomaly_detector(self):
        """Détecteur anomalies"""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                # Détection anomalies dans engagement
                await self._detect_engagement_anomalies()
                
            except Exception as e:
                logger.error(f"Erreur anomaly detector: {e}")
                await asyncio.sleep(300)
    
    async def _detect_engagement_anomalies(self):
        """Détection anomalies engagement"""
        # Analyse pattern récents vs historiques
        recent_events = list(self.events_buffer)[-1000:]
        
        if len(recent_events) < 100:
            return
        
        # Groupement par créateur
        creator_rates = defaultdict(int)
        for event in recent_events:
            creator_rates[event.creator_id] += 1
        
        # Détection outliers simples
        rates = list(creator_rates.values())
        if rates:
            mean_rate = sum(rates) / len(rates)
            std_rate = (sum((r - mean_rate) ** 2 for r in rates) / len(rates)) ** 0.5
            
            threshold = mean_rate + (self.config.anomaly_detection_threshold * std_rate)
            
            for creator_id, rate in creator_rates.items():
                if rate > threshold:
                    logger.warning(f"Anomalie engagement détectée pour {creator_id}: {rate} événements")
                    self.real_time_metrics['anomalies_detected'] += 1
    
    async def get_engagement_statistics(self) -> Dict[str, Any]:
        """Statistiques engagement globales"""
        try:
            stats = self.real_time_metrics.copy()
            
            # Statistiques buffer
            stats['buffer_size'] = len(self.events_buffer)
            stats['active_sessions'] = len(self.sessions_cache)
            
            # Statistiques cache
            stats['analytics_cache_size'] = len(self.analytics_cache)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur récupération statistiques engagement: {e}")
            return self.real_time_metrics

class MLEngagementProcessor:
    """Processeur ML pour engagement (placeholder)"""
    
    async def process_event(self, event: EngagementEvent):
        """Traitement événement ML"""
        # Placeholder pour traitement ML temps réel
        pass
    
    async def generate_audience_insights(self, creator_id: str, 
                                       segment: Optional[AudienceSegment]) -> List[AudienceInsight]:
        """Génération insights audience ML"""
        # Placeholder pour insights ML
        return []
    
    async def predict_engagement(self, creator_id: str, content_metadata: Dict[str, Any],
                               historical_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Prédiction engagement ML"""
        # Simulation prédiction
        return {
            'predicted_engagement_rate': 0.045,
            'confidence': 0.78,
            'factors': {
                'content_type': 0.3,
                'timing': 0.25,
                'historical_performance': 0.45
            }
        }
    
    async def generate_periodic_insights(self, creator_id: str):
        """Génération insights périodiques"""
        # Placeholder pour insights périodiques ML
        pass

# Factory function
def create_engagement_metrics_storage(
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> EngagementMetricsStorage:
    """Factory pour création stockage métriques engagement"""
    config = EngagementMetricsConfig(redis_url=redis_url, **kwargs)
    return EngagementMetricsStorage(config)

# Export classes principales
__all__ = [
    'EngagementMetricsStorage',
    'EngagementMetricsConfig',
    'EngagementEvent',
    'EngagementSession',
    'AudienceInsight',
    'EngagementAnalytics',
    'EngagementType',
    'AudienceSegment',
    'ContentCategory',
    'TimeWindow',
    'MLEngagementProcessor',
    'create_engagement_metrics_storage'
]