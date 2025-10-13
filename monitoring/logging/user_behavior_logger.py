"""👥 User Behavior Logger - Advanced UX Analytics & Creator Journey Optimization
==================================================================
Experts: ML Engineer + UX Analytics + Backend Senior + Data Scientist + DevOps
Technologies: Google Analytics 4 + Mixpanel + Segment + ML Patterns + Real-time Streaming
Business Logic: UX optimization Creator Journey → Analytics conversion → Segmentation comportementale
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
from typing import Dict, List, Optional, Any, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
import hashlib
import statistics
from urllib.parse import urlparse, parse_qs

# Configure logging
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================

class UserActionType(Enum):
    """Types d'actions utilisateur"""
    # Navigation
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    HOVER = "hover"
    FORM_INTERACTION = "form_interaction"
    SEARCH = "search"
    FILTER = "filter"
    SORT = "sort"
    
    # Content Interaction
    CONTENT_VIEW = "content_view"
    CONTENT_LIKE = "content_like"
    CONTENT_SHARE = "content_share"
    CONTENT_DOWNLOAD = "content_download"
    CONTENT_COMMENT = "content_comment"
    CONTENT_BOOKMARK = "content_bookmark"
    
    # Creator Journey
    PROFILE_VIEW = "profile_view"
    PROFILE_FOLLOW = "profile_follow"
    PROFILE_MESSAGE = "profile_message"
    SUBSCRIPTION_VIEW = "subscription_view"
    SUBSCRIPTION_PURCHASE = "subscription_purchase"
    TIP_GIVEN = "tip_given"
    
    # Platform Features
    FEATURE_DISCOVERY = "feature_discovery"
    FEATURE_USAGE = "feature_usage"
    FEATURE_ABANDONMENT = "feature_abandonment"
    ONBOARDING_STEP = "onboarding_step"
    TUTORIAL_INTERACTION = "tutorial_interaction"
    
    # Conversion Events
    SIGNUP_STARTED = "signup_started"
    SIGNUP_COMPLETED = "signup_completed"
    PURCHASE_INTENT = "purchase_intent"
    PURCHASE_COMPLETED = "purchase_completed"
    SUBSCRIPTION_INTENT = "subscription_intent"
    
    # Engagement
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TIME_SPENT = "time_spent"
    RETURN_VISIT = "return_visit"
    NOTIFICATION_INTERACTION = "notification_interaction"

class DeviceType(Enum):
    """Types d'appareils"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    WEARABLE = "wearable"
    UNKNOWN = "unknown"

class UserSegment(Enum):
    """Segments d'utilisateurs"""
    NEW_VISITOR = "new_visitor"
    RETURNING_VISITOR = "returning_visitor"
    ENGAGED_USER = "engaged_user"
    CONVERTING_USER = "converting_user"
    LOYAL_USER = "loyal_user"
    CHURNED_USER = "churned_user"
    VIP_USER = "vip_user"

class ConversionFunnel(Enum):
    """Étapes du funnel de conversion"""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"

class BehaviorPattern(Enum):
    """Patterns de comportement"""
    EXPLORER = "explorer"         # Explore beaucoup, engage peu
    CONSUMER = "consumer"         # Consomme du contenu régulièrement
    CREATOR = "creator"           # Crée et partage du contenu
    SOCIAL = "social"             # Interagit beaucoup socialement
    TRANSACTIONAL = "transactional"  # Focalisé sur les achats
    CASUAL = "casual"             # Utilisation sporadique
    POWER_USER = "power_user"     # Utilisation intensive

# ==================== DATA MODELS ====================

@dataclass
class UserBehaviorEvent:
    """Événement de comportement utilisateur complet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # User identification
    user_id: Optional[str] = None
    session_id: str = ""
    anonymous_id: Optional[str] = None
    creator_id: Optional[str] = None  # Si l'utilisateur est un créateur
    
    # Action details
    action_type: UserActionType = UserActionType.PAGE_VIEW
    action_category: str = "navigation"
    action_label: Optional[str] = None
    action_value: Optional[float] = None
    
    # Page/Screen context
    page_url: str = ""
    page_title: str = ""
    page_category: str = ""
    referrer: str = ""
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    
    # Device & Browser
    device_type: DeviceType = DeviceType.UNKNOWN
    browser: str = ""
    operating_system: str = ""
    screen_resolution: str = ""
    viewport_size: str = ""
    user_agent: str = ""
    
    # Geographic
    country: str = ""
    region: str = ""
    city: str = ""
    timezone: str = ""
    ip_address: Optional[str] = None
    
    # Interaction details
    element_clicked: Optional[str] = None
    form_fields: List[str] = field(default_factory=list)
    scroll_depth: float = 0.0  # Percentage
    time_on_page: float = 0.0  # Seconds
    
    # Content context
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    content_category: Optional[str] = None
    creator_profile_viewed: Optional[str] = None
    
    # E-commerce context
    product_id: Optional[str] = None
    product_category: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    transaction_id: Optional[str] = None
    
    # Engagement metrics
    engagement_score: float = 0.0
    interaction_depth: int = 0
    feature_adoption: List[str] = field(default_factory=list)
    
    # User segmentation
    user_segment: Optional[UserSegment] = None
    behavior_pattern: Optional[BehaviorPattern] = None
    conversion_funnel_stage: Optional[ConversionFunnel] = None
    
    # A/B Testing
    experiment_id: Optional[str] = None
    variant: Optional[str] = None
    
    # Custom dimensions
    custom_dimensions: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def calculate_engagement_score(self) -> float:
        """Calcule le score d'engagement"""
        score = 0.0
        
        # Temps passé sur la page
        if self.time_on_page > 30:
            score += 2.0
        elif self.time_on_page > 10:
            score += 1.0
        
        # Profondeur de scroll
        if self.scroll_depth > 75:
            score += 2.0
        elif self.scroll_depth > 50:
            score += 1.0
        elif self.scroll_depth > 25:
            score += 0.5
        
        # Types d'interactions
        high_engagement_actions = [
            UserActionType.CONTENT_LIKE,
            UserActionType.CONTENT_SHARE,
            UserActionType.CONTENT_COMMENT,
            UserActionType.SUBSCRIPTION_PURCHASE,
            UserActionType.TIP_GIVEN
        ]
        
        if self.action_type in high_engagement_actions:
            score += 3.0
        elif self.action_type in [UserActionType.CONTENT_VIEW, UserActionType.PROFILE_FOLLOW]:
            score += 1.0
        
        # Profondeur d'interaction
        score += self.interaction_depth * 0.5
        
        # Adoption de features
        score += len(self.feature_adoption) * 0.3
        
        self.engagement_score = min(score, 10.0)  # Cap à 10
        return self.engagement_score
    
    def determine_user_segment(self, user_history: List['UserBehaviorEvent']) -> UserSegment:
        """Détermine le segment utilisateur basé sur l'historique"""
        if not user_history:
            self.user_segment = UserSegment.NEW_VISITOR
            return self.user_segment
        
        # Calculer les métriques
        total_sessions = len(set(event.session_id for event in user_history))
        total_engagement = sum(event.engagement_score for event in user_history)
        purchases = len([e for e in user_history if e.action_type == UserActionType.PURCHASE_COMPLETED])
        days_active = len(set(event.timestamp.date() for event in user_history))
        
        # Logique de segmentation
        if purchases > 0 and total_engagement > 50:
            self.user_segment = UserSegment.VIP_USER
        elif purchases > 0:
            self.user_segment = UserSegment.CONVERTING_USER
        elif total_engagement > 30 and days_active > 7:
            self.user_segment = UserSegment.LOYAL_USER
        elif total_engagement > 15:
            self.user_segment = UserSegment.ENGAGED_USER
        elif total_sessions > 1:
            self.user_segment = UserSegment.RETURNING_VISITOR
        else:
            self.user_segment = UserSegment.NEW_VISITOR
        
        return self.user_segment
    
    def extract_utm_parameters(self):
        """Extrait les paramètres UTM de l'URL"""
        try:
            parsed_url = urlparse(self.page_url)
            query_params = parse_qs(parsed_url.query)
            
            self.utm_source = query_params.get('utm_source', [None])[0]
            self.utm_medium = query_params.get('utm_medium', [None])[0]
            self.utm_campaign = query_params.get('utm_campaign', [None])[0]
            
        except Exception as e:
            logger.debug(f"Error extracting UTM parameters: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'anonymous_id': self.anonymous_id,
            'creator_id': self.creator_id,
            'action_type': self.action_type.value,
            'action_category': self.action_category,
            'action_label': self.action_label,
            'action_value': self.action_value,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'page_category': self.page_category,
            'referrer': self.referrer,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'device_type': self.device_type.value,
            'browser': self.browser,
            'operating_system': self.operating_system,
            'screen_resolution': self.screen_resolution,
            'viewport_size': self.viewport_size,
            'user_agent': self.user_agent,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'timezone': self.timezone,
            'ip_address': self.ip_address,
            'element_clicked': self.element_clicked,
            'form_fields': self.form_fields,
            'scroll_depth': self.scroll_depth,
            'time_on_page': self.time_on_page,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'content_category': self.content_category,
            'creator_profile_viewed': self.creator_profile_viewed,
            'product_id': self.product_id,
            'product_category': self.product_category,
            'price': self.price,
            'currency': self.currency,
            'transaction_id': self.transaction_id,
            'engagement_score': self.engagement_score,
            'interaction_depth': self.interaction_depth,
            'feature_adoption': self.feature_adoption,
            'user_segment': self.user_segment.value if self.user_segment else None,
            'behavior_pattern': self.behavior_pattern.value if self.behavior_pattern else None,
            'conversion_funnel_stage': self.conversion_funnel_stage.value if self.conversion_funnel_stage else None,
            'experiment_id': self.experiment_id,
            'variant': self.variant,
            'custom_dimensions': self.custom_dimensions,
            'custom_metrics': self.custom_metrics
        }

@dataclass
class UserJourney:
    """Parcours utilisateur complet"""
    user_id: str
    start_time: datetime
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    touchpoints: List[str] = field(default_factory=list)
    conversion_events: List[UserBehaviorEvent] = field(default_factory=list)
    
    # Journey metrics
    total_sessions: int = 0
    total_time_spent: float = 0.0
    pages_visited: int = 0
    unique_pages: Set[str] = field(default_factory=set)
    
    # Conversion metrics
    conversion_rate: float = 0.0
    time_to_conversion: Optional[float] = None
    conversion_value: float = 0.0
    
    # Behavior analysis
    most_engaging_content: Optional[str] = None
    preferred_device: Optional[DeviceType] = None
    peak_activity_times: List[int] = field(default_factory=list)  # Hours
    
    def add_event(self, event: UserBehaviorEvent):
        """Ajoute un événement au parcours"""
        # Update basic metrics
        self.pages_visited += 1
        self.unique_pages.add(event.page_url)
        self.total_time_spent += event.time_on_page
        
        # Track touchpoints
        if event.utm_source:
            touchpoint = f"{event.utm_source}_{event.utm_medium}"
            if touchpoint not in self.touchpoints:
                self.touchpoints.append(touchpoint)
        
        # Track conversion events
        conversion_actions = [
            UserActionType.SIGNUP_COMPLETED,
            UserActionType.PURCHASE_COMPLETED,
            UserActionType.SUBSCRIPTION_PURCHASE
        ]
        
        if event.action_type in conversion_actions:
            self.conversion_events.append(event)
            if event.action_value:
                self.conversion_value += event.action_value
        
        # Update peak activity times
        hour = event.timestamp.hour
        if hour not in self.peak_activity_times:
            self.peak_activity_times.append(hour)

# ==================== ANALYTICS ENGINE ====================

class BehaviorAnalyticsEngine:
    """Moteur d'analytics comportemental avancé"""
    
    def __init__(self):
        self.user_events: Dict[str, List[UserBehaviorEvent]] = defaultdict(list)
        self.user_journeys: Dict[str, UserJourney] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.conversion_funnels: Dict[str, List[UserBehaviorEvent]] = defaultdict(list)
        self.cohort_data: Dict[str, List[str]] = defaultdict(list)  # date -> user_ids
        self.lock = threading.RLock()
        
        # Real-time metrics
        self.realtime_metrics = {
            'active_users_now': 0,
            'page_views_today': 0,
            'conversion_rate_today': 0.0,
            'top_pages': [],
            'bounce_rate': 0.0,
            'average_session_duration': 0.0
        }
        
        # A/B Testing tracking
        self.experiments: Dict[str, Dict[str, Any]] = {}
        
        # Behavior patterns
        self.behavior_clusters: Dict[BehaviorPattern, List[str]] = defaultdict(list)
    
    def analyze_event(self, event: UserBehaviorEvent):
        """Analyse un événement comportemental"""
        with self.lock:
            user_id = event.user_id or event.anonymous_id or "unknown"
            
            # Extract UTM parameters
            event.extract_utm_parameters()
            
            # Calculate engagement score
            event.calculate_engagement_score()
            
            # Add to user history
            self.user_events[user_id].append(event)
            
            # Determine user segment
            event.determine_user_segment(self.user_events[user_id])
            
            # Update or create user journey
            self._update_user_journey(user_id, event)
            
            # Analyze session
            self._analyze_session(event)
            
            # Track conversion funnel
            self._track_conversion_funnel(event)
            
            # Update cohorts
            self._update_cohorts(user_id, event)
            
            # Real-time analytics
            self._update_realtime_metrics(event)
            
            # Behavior pattern analysis
            self._analyze_behavior_patterns(user_id, event)
            
            # A/B Testing analysis
            if event.experiment_id:
                self._track_experiment(event)
    
    def _update_user_journey(self, user_id: str, event: UserBehaviorEvent):
        """Met à jour le parcours utilisateur"""
        if user_id not in self.user_journeys:
            self.user_journeys[user_id] = UserJourney(
                user_id=user_id,
                start_time=event.timestamp
            )
        
        journey = self.user_journeys[user_id]
        journey.add_event(event)
        
        # Update conversion metrics
        if journey.conversion_events:
            journey.conversion_rate = len(journey.conversion_events) / len(self.user_events[user_id])
            
            # Time to conversion (first conversion)
            if journey.time_to_conversion is None:
                first_conversion = min(journey.conversion_events, key=lambda x: x.timestamp)
                journey.time_to_conversion = (first_conversion.timestamp - journey.start_time).total_seconds()
    
    def _analyze_session(self, event: UserBehaviorEvent):
        """Analyse les données de session"""
        session_id = event.session_id
        
        if session_id not in self.session_data:
            self.session_data[session_id] = {
                'start_time': event.timestamp,
                'end_time': event.timestamp,
                'page_views': 0,
                'total_engagement': 0.0,
                'pages': [],
                'device_type': event.device_type,
                'user_id': event.user_id
            }
        
        session = self.session_data[session_id]
        session['end_time'] = event.timestamp
        session['page_views'] += 1
        session['total_engagement'] += event.engagement_score
        
        if event.page_url not in session['pages']:
            session['pages'].append(event.page_url)
    
    def _track_conversion_funnel(self, event: UserBehaviorEvent):
        """Tracking du funnel de conversion"""
        funnel_key = f"{event.utm_campaign or 'direct'}_{event.device_type.value}"
        
        # Determine funnel stage
        stage_mapping = {
            UserActionType.PAGE_VIEW: ConversionFunnel.AWARENESS,
            UserActionType.CONTENT_VIEW: ConversionFunnel.INTEREST,
            UserActionType.SUBSCRIPTION_VIEW: ConversionFunnel.CONSIDERATION,
            UserActionType.PURCHASE_INTENT: ConversionFunnel.INTENT,
            UserActionType.PURCHASE_COMPLETED: ConversionFunnel.PURCHASE,
            UserActionType.RETURN_VISIT: ConversionFunnel.RETENTION
        }
        
        if event.action_type in stage_mapping:
            event.conversion_funnel_stage = stage_mapping[event.action_type]
            self.conversion_funnels[funnel_key].append(event)
    
    def _update_cohorts(self, user_id: str, event: UserBehaviorEvent):
        """Met à jour les données de cohorte"""
        # Cohort basée sur la date de première visite
        user_events = self.user_events[user_id]
        if len(user_events) == 1:  # Premier événement
            cohort_date = event.timestamp.strftime('%Y-%m-%d')
            self.cohort_data[cohort_date].append(user_id)
    
    def _update_realtime_metrics(self, event: UserBehaviorEvent):
        """Met à jour les métriques temps réel"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        # Active users (dernière heure)
        recent_users = set()
        for user_events in self.user_events.values():
            for user_event in user_events:
                if user_event.timestamp >= current_hour:
                    recent_users.add(user_event.user_id or user_event.anonymous_id)
        
        self.realtime_metrics['active_users_now'] = len(recent_users)
        
        # Page views today
        today_events = []
        for user_events in self.user_events.values():
            for user_event in user_events:
                if user_event.timestamp.strftime('%Y-%m-%d') == today:
                    today_events.append(user_event)
        
        self.realtime_metrics['page_views_today'] = len(today_events)
        
        # Top pages
        page_counts = defaultdict(int)
        for user_event in today_events:
            page_counts[user_event.page_url] += 1
        
        self.realtime_metrics['top_pages'] = [
            {'page': page, 'views': count}
            for page, count in sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Conversion rate today
        conversions_today = len([e for e in today_events if e.action_type == UserActionType.PURCHASE_COMPLETED])
        if today_events:
            self.realtime_metrics['conversion_rate_today'] = conversions_today / len(today_events) * 100
        
        # Bounce rate (sessions with only 1 page view)
        today_sessions = {}
        for event in today_events:
            if event.session_id not in today_sessions:
                today_sessions[event.session_id] = 0
            today_sessions[event.session_id] += 1
        
        if today_sessions:
            bounced_sessions = len([s for s in today_sessions.values() if s == 1])
            self.realtime_metrics['bounce_rate'] = bounced_sessions / len(today_sessions) * 100
        
        # Average session duration
        session_durations = []
        for session in self.session_data.values():
            duration = (session['end_time'] - session['start_time']).total_seconds()
            session_durations.append(duration)
        
        if session_durations:
            self.realtime_metrics['average_session_duration'] = statistics.mean(session_durations)
    
    def _analyze_behavior_patterns(self, user_id: str, event: UserBehaviorEvent):
        """Analyse les patterns de comportement"""
        user_events = self.user_events[user_id]
        
        if len(user_events) < 5:  # Pas assez de données
            return
        
        # Analyser les patterns basés sur les actions
        action_counts = defaultdict(int)
        for user_event in user_events:
            action_counts[user_event.action_type] += 1
        
        # Déterminer le pattern comportemental
        total_actions = len(user_events)
        
        # Explorer: beaucoup de page views, peu d'engagement
        if (action_counts[UserActionType.PAGE_VIEW] / total_actions > 0.6 and
            sum(e.engagement_score for e in user_events) / total_actions < 2):
            pattern = BehaviorPattern.EXPLORER
        
        # Creator: actions de création et partage
        elif (action_counts[UserActionType.CONTENT_SHARE] > 0 or
              any(e.creator_id == user_id for e in user_events)):
            pattern = BehaviorPattern.CREATOR
        
        # Social: beaucoup d'interactions sociales
        elif (action_counts[UserActionType.CONTENT_LIKE] +
              action_counts[UserActionType.CONTENT_COMMENT] +
              action_counts[UserActionType.PROFILE_FOLLOW]) / total_actions > 0.3:
            pattern = BehaviorPattern.SOCIAL
        
        # Transactional: focus sur les achats
        elif (action_counts[UserActionType.PURCHASE_COMPLETED] > 0 or
              action_counts[UserActionType.PURCHASE_INTENT] > 0):
            pattern = BehaviorPattern.TRANSACTIONAL
        
        # Power User: utilisation intensive
        elif total_actions > 50 and sum(e.engagement_score for e in user_events) / total_actions > 5:
            pattern = BehaviorPattern.POWER_USER
        
        # Consumer: consommation régulière de contenu
        elif action_counts[UserActionType.CONTENT_VIEW] / total_actions > 0.4:
            pattern = BehaviorPattern.CONSUMER
        
        else:
            pattern = BehaviorPattern.CASUAL
        
        event.behavior_pattern = pattern
        
        # Ajouter à la clustérisation
        if user_id not in self.behavior_clusters[pattern]:
            self.behavior_clusters[pattern].append(user_id)
    
    def _track_experiment(self, event: UserBehaviorEvent):
        """Tracking des expériences A/B"""
        experiment_id = event.experiment_id
        variant = event.variant
        
        if experiment_id not in self.experiments:
            self.experiments[experiment_id] = {
                'variants': defaultdict(lambda: {'users': set(), 'conversions': 0, 'events': 0}),
                'start_date': event.timestamp
            }
        
        experiment = self.experiments[experiment_id]
        variant_data = experiment['variants'][variant]
        
        variant_data['users'].add(event.user_id or event.anonymous_id)
        variant_data['events'] += 1
        
        if event.action_type == UserActionType.PURCHASE_COMPLETED:
            variant_data['conversions'] += 1
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Analytics détaillées pour un utilisateur"""
        if user_id not in self.user_events:
            return {'user_id': user_id, 'status': 'no_data'}
        
        events = self.user_events[user_id]
        journey = self.user_journeys.get(user_id)
        
        # Calculer les métriques
        total_engagement = sum(e.engagement_score for e in events)
        pages_visited = len(set(e.page_url for e in events))
        sessions = len(set(e.session_id for e in events))
        
        # Devices utilisés
        devices = list(set(e.device_type.value for e in events))
        
        # Contenu préféré
        content_views = [e for e in events if e.action_type == UserActionType.CONTENT_VIEW]
        content_categories = defaultdict(int)
        for event in content_views:
            if event.content_category:
                content_categories[event.content_category] += 1
        
        preferred_content = max(content_categories.items(), key=lambda x: x[1])[0] if content_categories else None
        
        return {
            'user_id': user_id,
            'user_segment': events[-1].user_segment.value if events[-1].user_segment else None,
            'behavior_pattern': events[-1].behavior_pattern.value if events[-1].behavior_pattern else None,
            'total_events': len(events),
            'total_engagement': total_engagement,
            'average_engagement': total_engagement / len(events),
            'pages_visited': pages_visited,
            'sessions': sessions,
            'devices_used': devices,
            'preferred_content': preferred_content,
            'conversion_events': len([e for e in events if e.action_type == UserActionType.PURCHASE_COMPLETED]),
            'journey_summary': {
                'start_date': journey.start_time.isoformat() if journey else None,
                'conversion_rate': journey.conversion_rate if journey else 0,
                'conversion_value': journey.conversion_value if journey else 0,
                'time_to_conversion': journey.time_to_conversion if journey else None,
                'touchpoints': journey.touchpoints if journey else []
            } if journey else None,
            'recent_activity': [e.to_dict() for e in events[-5:]]  # 5 dernières activités
        }
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        total_users = len(self.user_events)
        total_events = sum(len(events) for events in self.user_events.values())
        
        # Segmentation des utilisateurs
        segment_distribution = defaultdict(int)
        pattern_distribution = defaultdict(int)
        
        for events in self.user_events.values():
            if events:
                last_event = events[-1]
                if last_event.user_segment:
                    segment_distribution[last_event.user_segment.value] += 1
                if last_event.behavior_pattern:
                    pattern_distribution[last_event.behavior_pattern.value] += 1
        
        # Métriques de conversion
        total_conversions = sum(
            len([e for e in events if e.action_type == UserActionType.PURCHASE_COMPLETED])
            for events in self.user_events.values()
        )
        
        # Top content categories
        content_categories = defaultdict(int)
        for events in self.user_events.values():
            for event in events:
                if event.content_category and event.action_type == UserActionType.CONTENT_VIEW:
                    content_categories[event.content_category] += 1
        
        return {
            'overview': {
                'total_users': total_users,
                'total_events': total_events,
                'total_conversions': total_conversions,
                'conversion_rate': total_conversions / total_users if total_users > 0 else 0,
                'active_experiments': len(self.experiments)
            },
            'realtime_metrics': self.realtime_metrics,
            'user_segmentation': dict(segment_distribution),
            'behavior_patterns': dict(pattern_distribution),
            'top_content_categories': dict(sorted(content_categories.items(), 
                                                key=lambda x: x[1], reverse=True)[:10]),
            'cohort_analysis': {
                'cohorts_tracked': len(self.cohort_data),
                'latest_cohort_size': len(list(self.cohort_data.values())[-1]) if self.cohort_data else 0
            }
        }
    
    def get_conversion_funnel_analysis(self) -> Dict[str, Any]:
        """Analyse des funnels de conversion"""
        funnel_analysis = {}
        
        for funnel_key, events in self.conversion_funnels.items():
            # Compter les événements par étape
            stage_counts = defaultdict(int)
            for event in events:
                if event.conversion_funnel_stage:
                    stage_counts[event.conversion_funnel_stage.value] += 1
            
            # Calculer les taux de conversion entre étapes
            funnel_stages = [
                ConversionFunnel.AWARENESS,
                ConversionFunnel.INTEREST,
                ConversionFunnel.CONSIDERATION,
                ConversionFunnel.INTENT,
                ConversionFunnel.PURCHASE
            ]
            
            conversion_rates = {}
            for i in range(len(funnel_stages) - 1):
                current_stage = funnel_stages[i].value
                next_stage = funnel_stages[i + 1].value
                
                current_count = stage_counts[current_stage]
                next_count = stage_counts[next_stage]
                
                if current_count > 0:
                    conversion_rates[f"{current_stage}_to_{next_stage}"] = next_count / current_count * 100
            
            funnel_analysis[funnel_key] = {
                'stage_counts': dict(stage_counts),
                'conversion_rates': conversion_rates,
                'total_events': len(events)
            }
        
        return funnel_analysis
    
    def get_ab_test_results(self) -> Dict[str, Any]:
        """Résultats des tests A/B"""
        results = {}
        
        for experiment_id, experiment in self.experiments.items():
            variant_results = {}
            
            for variant, data in experiment['variants'].items():
                users_count = len(data['users'])
                conversion_rate = data['conversions'] / users_count if users_count > 0 else 0
                
                variant_results[variant] = {
                    'users': users_count,
                    'events': data['events'],
                    'conversions': data['conversions'],
                    'conversion_rate': conversion_rate * 100
                }
            
            results[experiment_id] = {
                'start_date': experiment['start_date'].isoformat(),
                'variants': variant_results,
                'status': 'running'  # Simplified status
            }
        
        return results

# ==================== MAIN LOGGER CLASS ====================

class UserBehaviorLogger:
    """Logger principal pour comportement utilisateur Creator Economy"""
    
    def __init__(self, buffer_size: int = 10000, auto_flush_interval: int = 30):
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        
        # Storage
        self.event_buffer = deque(maxlen=buffer_size)
        self.analytics_engine = BehaviorAnalyticsEngine()
        
        # Threading
        self.lock = threading.RLock()
        self.is_running = False
        self.flush_thread = None
        
        # Statistics
        self.total_logged = 0
        self.dropped_events = 0
        
        logger.info("👥 User Behavior Logger initialized")
    
    def start(self):
        """Démarre le logger"""
        if self.is_running:
            return
            
        self.is_running = True
        self.flush_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="BehaviorLogger-AutoFlush"
        )
        self.flush_thread.start()
        
        logger.info("🚀 User Behavior Logger started")
    
    def stop(self):
        """Arrête le logger"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
            
        # Flush final
        self._flush_buffer()
        
        logger.info("🛑 User Behavior Logger stopped")
    
    def _auto_flush_loop(self):
        """Boucle de flush automatique"""
        while self.is_running:
            time.sleep(self.auto_flush_interval)
            if self.is_running:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Vide le buffer et traite les événements"""
        with self.lock:
            events_to_process = list(self.event_buffer)
            self.event_buffer.clear()
        
        for event in events_to_process:
            try:
                self.analytics_engine.analyze_event(event)
                logger.debug(f"Processed behavior event: {event.action_type.value}")
            except Exception as e:
                logger.error(f"Error processing behavior event {event.id}: {e}")
    
    def log_event(self, 
                  action_type: UserActionType,
                  user_id: Optional[str] = None,
                  session_id: str = "",
                  page_url: str = "",
                  **kwargs) -> str:
        """Log un événement de comportement"""
        
        event = UserBehaviorEvent(
            action_type=action_type,
            user_id=user_id,
            session_id=session_id,
            page_url=page_url,
            **kwargs
        )
        
        with self.lock:
            if len(self.event_buffer) >= self.buffer_size:
                self.dropped_events += 1
                logger.warning(f"Behavior event buffer full, dropping event {event.id}")
                return ""
            
            self.event_buffer.append(event)
            self.total_logged += 1
        
        logger.debug(f"Logged behavior event: {action_type.value}")
        return event.id
    
    # ==================== SPECIALIZED LOG METHODS ====================
    
    def log_page_view(self, user_id: str, page_url: str, page_title: str = "",
                     session_id: str = "", **kwargs) -> str:
        """Log vue de page"""
        return self.log_event(
            action_type=UserActionType.PAGE_VIEW,
            user_id=user_id,
            session_id=session_id,
            page_url=page_url,
            page_title=page_title,
            action_category="navigation",
            **kwargs
        )
    
    def log_content_interaction(self, user_id: str, content_id: str, 
                               interaction_type: str, creator_id: str = "",
                               **kwargs) -> str:
        """Log interaction avec contenu"""
        action_mapping = {
            "view": UserActionType.CONTENT_VIEW,
            "like": UserActionType.CONTENT_LIKE,
            "share": UserActionType.CONTENT_SHARE,
            "comment": UserActionType.CONTENT_COMMENT,
            "download": UserActionType.CONTENT_DOWNLOAD
        }
        
        action_type = action_mapping.get(interaction_type, UserActionType.CONTENT_VIEW)
        
        return self.log_event(
            action_type=action_type,
            user_id=user_id,
            content_id=content_id,
            creator_profile_viewed=creator_id,
            action_category="content",
            **kwargs
        )
    
    def log_creator_interaction(self, user_id: str, creator_id: str, 
                               interaction_type: str, **kwargs) -> str:
        """Log interaction avec créateur"""
        action_mapping = {
            "follow": UserActionType.PROFILE_FOLLOW,
            "message": UserActionType.PROFILE_MESSAGE,
            "tip": UserActionType.TIP_GIVEN,
            "view_profile": UserActionType.PROFILE_VIEW
        }
        
        action_type = action_mapping.get(interaction_type, UserActionType.PROFILE_VIEW)
        
        return self.log_event(
            action_type=action_type,
            user_id=user_id,
            creator_id=creator_id,
            action_category="creator_interaction",
            **kwargs
        )
    
    def log_purchase_event(self, user_id: str, transaction_id: str, 
                          amount: float, product_id: str = "", **kwargs) -> str:
        """Log événement d'achat"""
        return self.log_event(
            action_type=UserActionType.PURCHASE_COMPLETED,
            user_id=user_id,
            transaction_id=transaction_id,
            action_value=amount,
            product_id=product_id,
            price=amount,
            action_category="conversion",
            **kwargs
        )
    
    def log_search_behavior(self, user_id: str, search_query: str,
                           results_count: int = 0, **kwargs) -> str:
        """Log comportement de recherche"""
        return self.log_event(
            action_type=UserActionType.SEARCH,
            user_id=user_id,
            action_label=search_query,
            action_value=results_count,
            action_category="search",
            custom_dimensions={"search_query": search_query, "results_count": results_count},
            **kwargs
        )
    
    def log_session_data(self, user_id: str, session_id: str, duration: float,
                        pages_viewed: int, device_type: str = "desktop", **kwargs) -> str:
        """Log données de session"""
        device_enum = DeviceType(device_type) if device_type in [d.value for d in DeviceType] else DeviceType.DESKTOP
        
        return self.log_event(
            action_type=UserActionType.SESSION_END,
            user_id=user_id,
            session_id=session_id,
            time_on_page=duration,
            device_type=device_enum,
            custom_metrics={"pages_viewed": pages_viewed},
            action_category="session",
            **kwargs
        )
    
    def log_ab_test_event(self, user_id: str, experiment_id: str, variant: str,
                         action_type: UserActionType, **kwargs) -> str:
        """Log événement de test A/B"""
        return self.log_event(
            action_type=action_type,
            user_id=user_id,
            experiment_id=experiment_id,
            variant=variant,
            action_category="ab_testing",
            **kwargs
        )
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Analytics pour un utilisateur spécifique"""
        return self.analytics_engine.get_user_analytics(user_id)
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        return self.analytics_engine.get_platform_analytics()
    
    def get_conversion_analytics(self) -> Dict[str, Any]:
        """Analytics de conversion"""
        return self.analytics_engine.get_conversion_funnel_analysis()
    
    def get_ab_test_results(self) -> Dict[str, Any]:
        """Résultats des tests A/B"""
        return self.analytics_engine.get_ab_test_results()
    
    def get_realtime_dashboard(self) -> Dict[str, Any]:
        """Dashboard temps réel"""
        return {
            'realtime_metrics': self.analytics_engine.realtime_metrics,
            'logger_stats': self.get_logger_stats(),
            'active_experiments': len(self.analytics_engine.experiments),
            'behavior_clusters': {
                pattern.value: len(users) 
                for pattern, users in self.analytics_engine.behavior_clusters.items()
            }
        }
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Statistiques du logger"""
        with self.lock:
            buffer_size = len(self.event_buffer)
            
        return {
            'total_logged': self.total_logged,
            'dropped_events': self.dropped_events,
            'current_buffer_size': buffer_size,
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': buffer_size / self.buffer_size,
            'is_running': self.is_running,
            'unique_users_tracked': len(self.analytics_engine.user_events),
            'total_sessions': len(self.analytics_engine.session_data)
        }

# ==================== HELPER FUNCTIONS ====================

# Instance globale
_behavior_logger_instance: Optional[UserBehaviorLogger] = None

def get_behavior_logger() -> UserBehaviorLogger:
    """Récupère l'instance singleton du logger"""
    global _behavior_logger_instance
    
    if _behavior_logger_instance is None:
        _behavior_logger_instance = UserBehaviorLogger()
        _behavior_logger_instance.start()
        
    return _behavior_logger_instance

def log_page_view(user_id: str, page_url: str, **kwargs):
    """Helper: Log vue de page"""
    logger_instance = get_behavior_logger()
    return logger_instance.log_page_view(user_id, page_url, **kwargs)

def log_content_view(user_id: str, content_id: str, creator_id: str = "", **kwargs):
    """Helper: Log vue de contenu"""
    logger_instance = get_behavior_logger()
    return logger_instance.log_content_interaction(user_id, content_id, "view", creator_id, **kwargs)

def log_purchase(user_id: str, transaction_id: str, amount: float, **kwargs):
    """Helper: Log achat"""
    logger_instance = get_behavior_logger()
    return logger_instance.log_purchase_event(user_id, transaction_id, amount, **kwargs)

# ==================== DEMO ====================

if __name__ == "__main__":
    # Configuration et démonstration
    behavior_logger = UserBehaviorLogger(buffer_size=1000, auto_flush_interval=10)
    behavior_logger.start()
    
    try:
        # Simulation d'événements utilisateur
        users = ["user_1", "user_2", "user_3"]
        sessions = ["session_1", "session_2", "session_3"]
        
        for i, (user_id, session_id) in enumerate(zip(users, sessions)):
            # Page views
            behavior_logger.log_page_view(
                user_id=user_id,
                session_id=session_id,
                page_url=f"/creator/profile/{i+1}",
                page_title=f"Creator {i+1} Profile",
                device_type=DeviceType.DESKTOP,
                time_on_page=120.0 + i*30
            )
            
            # Content interactions
            behavior_logger.log_content_interaction(
                user_id=user_id,
                content_id=f"content_{i+1}",
                interaction_type="view",
                creator_id=f"creator_{i+1}",
                session_id=session_id
            )
            
            behavior_logger.log_content_interaction(
                user_id=user_id,
                content_id=f"content_{i+1}",
                interaction_type="like",
                creator_id=f"creator_{i+1}",
                session_id=session_id
            )
            
            # Creator interactions
            behavior_logger.log_creator_interaction(
                user_id=user_id,
                creator_id=f"creator_{i+1}",
                interaction_type="follow",
                session_id=session_id
            )
            
            # Purchases (for some users)
            if i > 0:
                behavior_logger.log_purchase_event(
                    user_id=user_id,
                    transaction_id=f"txn_{i+1}",
                    amount=29.99 + i*10,
                    product_id=f"subscription_{i+1}",
                    session_id=session_id
                )
            
            # Search behavior
            behavior_logger.log_search_behavior(
                user_id=user_id,
                search_query=f"creator content {i+1}",
                results_count=15 + i*5,
                session_id=session_id
            )
        
        # Attendre le traitement
        time.sleep(2)
        
        # Afficher les résultats
        print("👥 User Behavior Logger Demo Results:")
        print("\n🔧 Logger Stats:")
        print(json.dumps(behavior_logger.get_logger_stats(), indent=2))
        
        print("\n📊 Platform Analytics:")
        platform_analytics = behavior_logger.get_platform_analytics()
        print(json.dumps(platform_analytics, indent=2, default=str))
        
        print("\n👤 User Analytics (user_1):")
        user_analytics = behavior_logger.get_user_analytics("user_1")
        print(json.dumps(user_analytics, indent=2, default=str))
        
        print("\n🔄 Conversion Analytics:")
        conversion_analytics = behavior_logger.get_conversion_analytics()
        print(json.dumps(conversion_analytics, indent=2, default=str))
        
        print("\n⏱️ Realtime Dashboard:")
        realtime_dashboard = behavior_logger.get_realtime_dashboard()
        print(json.dumps(realtime_dashboard, indent=2, default=str))
        
    finally:
        behavior_logger.stop()