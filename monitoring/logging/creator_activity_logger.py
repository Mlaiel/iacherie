"""🎨 Creator Activity Logger - Advanced Creator Journey Tracking
==================================================================
Experts: Lead Dev IA + ML Engineer + DBA + Analytics Engineer
Technologies: ClickHouse + TimeSeries DB + WebSockets + Real-time Analytics
Business Logic: Tracking complet parcours créateur multi-format
==================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================

class ActivityType(Enum):
    """Types d'activité créateur"""
    # Content Creation
    CONTENT_CREATED = "content_created"
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_EDITED = "content_edited"
    CONTENT_DELETED = "content_deleted"
    
    # Content Interaction
    CONTENT_VIEWED = "content_viewed"
    CONTENT_LIKED = "content_liked"
    CONTENT_SHARED = "content_shared"
    CONTENT_COMMENTED = "content_commented"
    
    # Creator Journey
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    TIER_UPGRADED = "tier_upgraded"
    VERIFICATION_REQUESTED = "verification_requested"
    VERIFICATION_COMPLETED = "verification_completed"
    
    # Monetization
    MONETIZATION_ENABLED = "monetization_enabled"
    PAYMENT_RECEIVED = "payment_received"
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    
    # Collaboration
    COLLABORATION_REQUESTED = "collaboration_requested"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_COMPLETED = "collaboration_completed"
    
    # Analytics & Insights
    ANALYTICS_VIEWED = "analytics_viewed"
    REPORT_GENERATED = "report_generated"
    INSIGHTS_ACCESSED = "insights_accessed"
    
    # Platform Interaction
    LOGIN = "login"
    LOGOUT = "logout"
    SETTINGS_CHANGED = "settings_changed"
    NOTIFICATION_READ = "notification_read"

class ContentFormat(Enum):
    """Formats de contenu supportés"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"
    SHORT_VIDEO = "short_video"
    STORY = "story"
    MIXED_MEDIA = "mixed_media"
    INTERACTIVE = "interactive"

class EngagementLevel(Enum):
    """Niveaux d'engagement utilisateur"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VIRAL = "viral"

class CreatorStatus(Enum):
    """Statuts du créateur"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"

# ==================== DATA MODELS ====================

@dataclass
class CreatorActivity:
    """Modèle d'activité créateur complet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Creator context
    creator_id: str = ""
    creator_tier: Optional[str] = None
    creator_status: Optional[CreatorStatus] = None
    
    # Activity details
    activity_type: ActivityType = ActivityType.CONTENT_CREATED
    activity_category: str = "content"  # content, profile, monetization, collaboration
    
    # Content context
    content_id: Optional[str] = None
    content_format: Optional[ContentFormat] = None
    content_title: Optional[str] = None
    content_duration: Optional[int] = None  # seconds
    content_size: Optional[int] = None  # bytes
    
    # Engagement metrics
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    engagement_rate: float = 0.0
    engagement_level: Optional[EngagementLevel] = None
    
    # Business metrics
    revenue_generated: float = 0.0
    conversion_rate: float = 0.0
    roi: float = 0.0
    
    # Technical context
    platform: str = "iacherie"
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Session context
    session_id: Optional[str] = None
    session_duration: Optional[int] = None
    page_views: int = 0
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics
    previous_activity_id: Optional[str] = None
    activity_sequence: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'creator_id': self.creator_id,
            'creator_tier': self.creator_tier,
            'creator_status': self.creator_status.value if self.creator_status else None,
            'activity_type': self.activity_type.value,
            'activity_category': self.activity_category,
            'content_id': self.content_id,
            'content_format': self.content_format.value if self.content_format else None,
            'content_title': self.content_title,
            'content_duration': self.content_duration,
            'content_size': self.content_size,
            'views': self.views,
            'likes': self.likes,
            'shares': self.shares,
            'comments': self.comments,
            'engagement_rate': self.engagement_rate,
            'engagement_level': self.engagement_level.value if self.engagement_level else None,
            'revenue_generated': self.revenue_generated,
            'conversion_rate': self.conversion_rate,
            'roi': self.roi,
            'platform': self.platform,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'session_duration': self.session_duration,
            'page_views': self.page_views,
            'tags': self.tags,
            'metadata': self.metadata,
            'previous_activity_id': self.previous_activity_id,
            'activity_sequence': self.activity_sequence
        }

@dataclass
class CreatorJourney:
    """Parcours complet d'un créateur"""
    creator_id: str
    start_date: datetime
    activities: List[CreatorActivity] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Journey metrics
    total_activities: int = 0
    unique_content_formats: Set[ContentFormat] = field(default_factory=set)
    total_engagement: int = 0
    total_revenue: float = 0.0
    
    # Journey analysis
    most_active_day: Optional[str] = None
    preferred_content_format: Optional[ContentFormat] = None
    average_session_duration: float = 0.0
    retention_score: float = 0.0
    
    def add_activity(self, activity: CreatorActivity):
        """Ajoute une activité au parcours"""
        self.activities.append(activity)
        self.total_activities += 1
        
        if activity.content_format:
            self.unique_content_formats.add(activity.content_format)
            
        self.total_engagement += activity.views + activity.likes + activity.shares
        self.total_revenue += activity.revenue_generated
        
        # Update metrics
        self._update_journey_metrics()
    
    def _update_journey_metrics(self):
        """Met à jour les métriques du parcours"""
        if not self.activities:
            return
            
        # Format préféré
        format_counts = defaultdict(int)
        session_durations = []
        daily_activities = defaultdict(int)
        
        for activity in self.activities:
            if activity.content_format:
                format_counts[activity.content_format] += 1
                
            if activity.session_duration:
                session_durations.append(activity.session_duration)
                
            day = activity.timestamp.strftime('%Y-%m-%d')
            daily_activities[day] += 1
        
        # Format le plus utilisé
        if format_counts:
            self.preferred_content_format = max(format_counts.items(), key=lambda x: x[1])[0]
        
        # Durée moyenne de session
        if session_durations:
            self.average_session_duration = sum(session_durations) / len(session_durations)
        
        # Jour le plus actif
        if daily_activities:
            self.most_active_day = max(daily_activities.items(), key=lambda x: x[1])[0]
        
        # Score de rétention basé sur la fréquence d'activité
        days_active = len(daily_activities)
        total_days = (datetime.utcnow() - self.start_date).days + 1
        self.retention_score = days_active / total_days if total_days > 0 else 0.0

# ==================== ANALYTICS ENGINE ====================

class CreatorAnalyticsEngine:
    """Moteur d'analytics avancé pour activités créateur"""
    
    def __init__(self):
        self.journeys: Dict[str, CreatorJourney] = {}
        self.activity_patterns = defaultdict(list)
        self.engagement_trends = defaultdict(list)
        self.format_performance = defaultdict(list)
        self.lock = threading.RLock()
        
        # Real-time metrics
        self.realtime_metrics = {
            'active_creators': 0,
            'total_activities_today': 0,
            'trending_formats': [],
            'top_performers': [],
            'engagement_rate_avg': 0.0
        }
    
    def analyze_activity(self, activity: CreatorActivity):
        """Analyse une activité en temps réel"""
        with self.lock:
            creator_id = activity.creator_id
            
            # Initialiser le parcours si nécessaire
            if creator_id not in self.journeys:
                self.journeys[creator_id] = CreatorJourney(
                    creator_id=creator_id,
                    start_date=activity.timestamp
                )
            
            # Ajouter l'activité au parcours
            self.journeys[creator_id].add_activity(activity)
            
            # Analytics patterns
            self._analyze_activity_patterns(activity)
            self._analyze_engagement_trends(activity)
            self._analyze_format_performance(activity)
            self._update_realtime_metrics()
    
    def _analyze_activity_patterns(self, activity: CreatorActivity):
        """Analyse les patterns d'activité"""
        hour = activity.timestamp.hour
        day_of_week = activity.timestamp.weekday()
        
        pattern_key = f"{activity.activity_type.value}_{hour}_{day_of_week}"
        self.activity_patterns[pattern_key].append({
            'timestamp': activity.timestamp,
            'creator_id': activity.creator_id,
            'engagement': activity.views + activity.likes + activity.shares
        })
    
    def _analyze_engagement_trends(self, activity: CreatorActivity):
        """Analyse les tendances d'engagement"""
        if activity.engagement_rate > 0:
            date_key = activity.timestamp.strftime('%Y-%m-%d')
            self.engagement_trends[date_key].append({
                'creator_id': activity.creator_id,
                'engagement_rate': activity.engagement_rate,
                'content_format': activity.content_format.value if activity.content_format else None,
                'activity_type': activity.activity_type.value
            })
    
    def _analyze_format_performance(self, activity: CreatorActivity):
        """Analyse la performance par format"""
        if activity.content_format:
            format_key = activity.content_format.value
            self.format_performance[format_key].append({
                'timestamp': activity.timestamp,
                'creator_id': activity.creator_id,
                'views': activity.views,
                'engagement_rate': activity.engagement_rate,
                'revenue': activity.revenue_generated
            })
    
    def _update_realtime_metrics(self):
        """Met à jour les métriques temps réel"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Créateurs actifs aujourd'hui
        active_today = set()
        activities_today = 0
        engagement_rates = []
        
        for journey in self.journeys.values():
            for activity in journey.activities:
                if activity.timestamp.strftime('%Y-%m-%d') == today:
                    active_today.add(activity.creator_id)
                    activities_today += 1
                    if activity.engagement_rate > 0:
                        engagement_rates.append(activity.engagement_rate)
        
        self.realtime_metrics['active_creators'] = len(active_today)
        self.realtime_metrics['total_activities_today'] = activities_today
        self.realtime_metrics['engagement_rate_avg'] = (
            sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
        )
        
        # Top formats
        format_counts = defaultdict(int)
        for activities in self.format_performance.values():
            format_counts[activities[0]['creator_id']] = len(activities)
        
        self.realtime_metrics['trending_formats'] = [
            format_name for format_name, _ in 
            sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def get_creator_insights(self, creator_id: str) -> Dict[str, Any]:
        """Insights détaillés pour un créateur"""
        if creator_id not in self.journeys:
            return {}
        
        journey = self.journeys[creator_id]
        
        # Performance metrics
        recent_activities = [
            a for a in journey.activities 
            if a.timestamp >= datetime.utcnow() - timedelta(days=30)
        ]
        
        recent_engagement = sum(
            a.views + a.likes + a.shares for a in recent_activities
        )
        
        recent_revenue = sum(a.revenue_generated for a in recent_activities)
        
        # Content analysis
        format_distribution = defaultdict(int)
        for activity in journey.activities:
            if activity.content_format:
                format_distribution[activity.content_format.value] += 1
        
        return {
            'creator_id': creator_id,
            'journey_start': journey.start_date.isoformat(),
            'total_activities': journey.total_activities,
            'unique_formats': len(journey.unique_content_formats),
            'total_engagement': journey.total_engagement,
            'total_revenue': journey.total_revenue,
            'preferred_format': journey.preferred_content_format.value if journey.preferred_content_format else None,
            'most_active_day': journey.most_active_day,
            'avg_session_duration': journey.average_session_duration,
            'retention_score': journey.retention_score,
            'recent_30d': {
                'activities': len(recent_activities),
                'engagement': recent_engagement,
                'revenue': recent_revenue
            },
            'format_distribution': dict(format_distribution),
            'milestones': journey.milestones
        }
    
    def get_platform_insights(self) -> Dict[str, Any]:
        """Insights globaux de la plateforme"""
        total_creators = len(self.journeys)
        total_activities = sum(j.total_activities for j in self.journeys.values())
        total_engagement = sum(j.total_engagement for j in self.journeys.values())
        total_revenue = sum(j.total_revenue for j in self.journeys.values())
        
        # Top créateurs
        top_creators = sorted(
            [(cid, j.total_engagement) for cid, j in self.journeys.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Formats populaires
        all_formats = defaultdict(int)
        for journey in self.journeys.values():
            for fmt in journey.unique_content_formats:
                all_formats[fmt.value] += 1
        
        return {
            'platform_overview': {
                'total_creators': total_creators,
                'total_activities': total_activities,
                'total_engagement': total_engagement,
                'total_revenue': total_revenue,
                'avg_engagement_per_creator': total_engagement / total_creators if total_creators > 0 else 0,
                'avg_revenue_per_creator': total_revenue / total_creators if total_creators > 0 else 0
            },
            'realtime_metrics': self.realtime_metrics,
            'top_creators': [
                {'creator_id': cid, 'engagement': eng} 
                for cid, eng in top_creators
            ],
            'popular_formats': dict(sorted(all_formats.items(), key=lambda x: x[1], reverse=True)),
            'activity_patterns': self._get_activity_pattern_summary(),
            'engagement_trends': self._get_engagement_trend_summary()
        }
    
    def _get_activity_pattern_summary(self) -> Dict[str, Any]:
        """Résumé des patterns d'activité"""
        patterns_by_hour = defaultdict(int)
        patterns_by_day = defaultdict(int)
        
        for pattern_key, activities in self.activity_patterns.items():
            parts = pattern_key.split('_')
            if len(parts) >= 3:
                hour = int(parts[1])
                day = int(parts[2])
                patterns_by_hour[hour] += len(activities)
                patterns_by_day[day] += len(activities)
        
        return {
            'peak_hours': dict(sorted(patterns_by_hour.items(), key=lambda x: x[1], reverse=True)[:5]),
            'active_days': dict(sorted(patterns_by_day.items(), key=lambda x: x[1], reverse=True))
        }
    
    def _get_engagement_trend_summary(self) -> Dict[str, Any]:
        """Résumé des tendances d'engagement"""
        daily_avg = {}
        for date, engagements in self.engagement_trends.items():
            avg_rate = sum(e['engagement_rate'] for e in engagements) / len(engagements)
            daily_avg[date] = avg_rate
        
        return {
            'daily_averages': dict(sorted(daily_avg.items())[-7:]),  # Last 7 days
            'trend_direction': self._calculate_trend_direction(daily_avg)
        }
    
    def _calculate_trend_direction(self, daily_data: Dict[str, float]) -> str:
        """Calcule la direction de tendance"""
        if len(daily_data) < 2:
            return "insufficient_data"
        
        values = list(daily_data.values())
        recent_avg = sum(values[-3:]) / 3 if len(values) >= 3 else values[-1]
        older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

# ==================== MAIN LOGGER CLASS ====================

class CreatorActivityLogger:
    """Logger principal pour activités créateur"""
    
    def __init__(self, buffer_size: int = 5000, auto_flush_interval: int = 30):
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        
        # Storage
        self.activity_buffer = deque(maxlen=buffer_size)
        self.analytics_engine = CreatorAnalyticsEngine()
        
        # Threading
        self.lock = threading.RLock()
        self.is_running = False
        self.flush_thread = None
        
        # Metrics
        self.total_logged = 0
        self.dropped_activities = 0
        
        logger.info("🎨 Creator Activity Logger initialized")
    
    def start(self):
        """Démarre le logger"""
        if self.is_running:
            return
            
        self.is_running = True
        self.flush_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="CreatorActivityLogger-AutoFlush"
        )
        self.flush_thread.start()
        
        logger.info("🚀 Creator Activity Logger started")
    
    def stop(self):
        """Arrête le logger"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
            
        # Flush final
        self._flush_buffer()
        
        logger.info("🛑 Creator Activity Logger stopped")
    
    def _auto_flush_loop(self):
        """Boucle de flush automatique"""
        while self.is_running:
            time.sleep(self.auto_flush_interval)
            if self.is_running:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Vide le buffer et traite les activités"""
        with self.lock:
            activities_to_process = list(self.activity_buffer)
            self.activity_buffer.clear()
        
        for activity in activities_to_process:
            try:
                self.analytics_engine.analyze_activity(activity)
            except Exception as e:
                logger.error(f"Error processing activity {activity.id}: {e}")
    
    def log_activity(self, 
                    creator_id: str,
                    activity_type: ActivityType,
                    **kwargs) -> str:
        """Log une activité créateur"""
        
        activity = CreatorActivity(
            creator_id=creator_id,
            activity_type=activity_type,
            **kwargs
        )
        
        with self.lock:
            if len(self.activity_buffer) >= self.buffer_size:
                self.dropped_activities += 1
                logger.warning(f"Activity buffer full, dropping activity for creator {creator_id}")
                return ""
            
            self.activity_buffer.append(activity)
            self.total_logged += 1
        
        logger.debug(f"Logged activity {activity_type.value} for creator {creator_id}")
        return activity.id
    
    # ==================== SPECIALIZED LOG METHODS ====================
    
    def log_content_creation(self, creator_id: str, content_format: ContentFormat,
                           title: str = "", duration: int = 0, size: int = 0,
                           **kwargs) -> str:
        """Log création de contenu"""
        return self.log_activity(
            creator_id=creator_id,
            activity_type=ActivityType.CONTENT_CREATED,
            content_format=content_format,
            content_title=title,
            content_duration=duration,
            content_size=size,
            activity_category="content",
            **kwargs
        )
    
    def log_content_engagement(self, creator_id: str, content_id: str,
                             views: int = 0, likes: int = 0, shares: int = 0,
                             comments: int = 0, **kwargs) -> str:
        """Log engagement sur contenu"""
        engagement_rate = 0.0
        if views > 0:
            engagement_rate = (likes + shares + comments) / views
        
        engagement_level = EngagementLevel.LOW
        if engagement_rate > 0.1:
            engagement_level = EngagementLevel.HIGH
        elif engagement_rate > 0.05:
            engagement_level = EngagementLevel.MEDIUM
        elif engagement_rate > 0.15:
            engagement_level = EngagementLevel.VIRAL
        
        return self.log_activity(
            creator_id=creator_id,
            activity_type=ActivityType.CONTENT_VIEWED,
            content_id=content_id,
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            engagement_rate=engagement_rate,
            engagement_level=engagement_level,
            activity_category="content",
            **kwargs
        )
    
    def log_monetization_event(self, creator_id: str, revenue: float,
                             conversion_rate: float = 0.0, **kwargs) -> str:
        """Log événement monétisation"""
        return self.log_activity(
            creator_id=creator_id,
            activity_type=ActivityType.PAYMENT_RECEIVED,
            revenue_generated=revenue,
            conversion_rate=conversion_rate,
            activity_category="monetization",
            **kwargs
        )
    
    def log_collaboration_event(self, creator_id: str, collaboration_type: str,
                              partner_id: str = "", **kwargs) -> str:
        """Log événement collaboration"""
        activity_type = ActivityType.COLLABORATION_REQUESTED
        if collaboration_type == "accepted":
            activity_type = ActivityType.COLLABORATION_ACCEPTED
        elif collaboration_type == "completed":
            activity_type = ActivityType.COLLABORATION_COMPLETED
        
        return self.log_activity(
            creator_id=creator_id,
            activity_type=activity_type,
            activity_category="collaboration",
            metadata={"partner_id": partner_id, "collaboration_type": collaboration_type},
            **kwargs
        )
    
    def log_session_activity(self, creator_id: str, session_id: str,
                           duration: int, page_views: int = 1, **kwargs) -> str:
        """Log activité de session"""
        return self.log_activity(
            creator_id=creator_id,
            activity_type=ActivityType.LOGIN,
            session_id=session_id,
            session_duration=duration,
            page_views=page_views,
            activity_category="session",
            **kwargs
        )
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_creator_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Analytics détaillées pour un créateur"""
        return self.analytics_engine.get_creator_insights(creator_id)
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        return self.analytics_engine.get_platform_insights()
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Statistiques du logger"""
        with self.lock:
            buffer_size = len(self.activity_buffer)
            
        return {
            'total_logged': self.total_logged,
            'dropped_activities': self.dropped_activities,
            'current_buffer_size': buffer_size,
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': buffer_size / self.buffer_size,
            'is_running': self.is_running,
            'total_creators': len(self.analytics_engine.journeys),
            'realtime_metrics': self.analytics_engine.realtime_metrics
        }
    
    def get_activity_patterns(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Patterns d'activité (global ou par créateur)"""
        if creator_id:
            insights = self.analytics_engine.get_creator_insights(creator_id)
            return {
                'creator_id': creator_id,
                'patterns': insights
            }
        else:
            return self.analytics_engine.get_platform_insights()

# ==================== HELPER FUNCTIONS ====================

# Instance globale
_activity_logger_instance: Optional[CreatorActivityLogger] = None

def get_activity_logger() -> CreatorActivityLogger:
    """Récupère l'instance singleton du logger"""
    global _activity_logger_instance
    
    if _activity_logger_instance is None:
        _activity_logger_instance = CreatorActivityLogger()
        _activity_logger_instance.start()
        
    return _activity_logger_instance

def log_creator_content(creator_id: str, content_format: str, **kwargs):
    """Helper: Log création de contenu"""
    logger_instance = get_activity_logger()
    fmt = ContentFormat(content_format) if content_format in [f.value for f in ContentFormat] else ContentFormat.TEXT
    return logger_instance.log_content_creation(creator_id, fmt, **kwargs)

def log_creator_engagement(creator_id: str, content_id: str, **kwargs):
    """Helper: Log engagement"""
    logger_instance = get_activity_logger()
    return logger_instance.log_content_engagement(creator_id, content_id, **kwargs)

def log_creator_revenue(creator_id: str, amount: float, **kwargs):
    """Helper: Log revenus"""
    logger_instance = get_activity_logger()
    return logger_instance.log_monetization_event(creator_id, amount, **kwargs)

# ==================== DEMO ====================

if __name__ == "__main__":
    # Configuration et démonstration
    logger = CreatorActivityLogger(buffer_size=1000, auto_flush_interval=10)
    logger.start()
    
    try:
        # Simulation d'activités créateur
        creators = ["creator_1", "creator_2", "creator_3"]
        
        for i, creator_id in enumerate(creators):
            # Création de contenu
            logger.log_content_creation(
                creator_id=creator_id,
                content_format=ContentFormat.VIDEO,
                content_title=f"Video Tutorial {i+1}",
                content_duration=180,
                content_size=50000000
            )
            
            # Engagement
            logger.log_content_engagement(
                creator_id=creator_id,
                content_id=f"content_{i+1}",
                views=1000 + i*500,
                likes=50 + i*25,
                shares=10 + i*5,
                comments=20 + i*10
            )
            
            # Monétisation
            logger.log_monetization_event(
                creator_id=creator_id,
                revenue=100.0 + i*50,
                conversion_rate=0.05 + i*0.01
            )
        
        # Attendre le traitement
        time.sleep(2)
        
        # Afficher les analytics
        print("📊 Creator Activity Logger Demo Results:")
        print("\n🔧 Logger Stats:")
        print(json.dumps(logger.get_logger_stats(), indent=2))
        
        print("\n🎯 Platform Analytics:")
        platform_analytics = logger.get_platform_analytics()
        print(json.dumps(platform_analytics, indent=2, default=str))
        
        print("\n👤 Creator Analytics (creator_1):")
        creator_analytics = logger.get_creator_analytics("creator_1")
        print(json.dumps(creator_analytics, indent=2, default=str))
        
    finally:
        logger.stop()