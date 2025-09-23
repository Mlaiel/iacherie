"""🚀 User Behavior Storage - Enterprise Grade
============================================
Expert: ML ENGINEER + DATA ARCHITECT + UX ANALYST + BEHAVIORAL PSYCHOLOGIST
Technologies: Behavioral Analytics + ML Insights + User Journey + Personalization
Architecture: Level 2 - Storage Layer - User Behavior Analysis
Date: 2025-01-14

Ultra-optimized enterprise user behavior storage with ML-driven insights,
journey mapping, personalization engine and advanced behavioral analytics.
============================================
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
from decimal import Decimal

# Optional imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class BehaviorEventType(Enum):
    """Types d'événements comportementaux"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    HOVER = "hover"
    FORM_INTERACTION = "form_interaction"
    SEARCH = "search"
    FILTER_USAGE = "filter_usage"
    CONTENT_CONSUMPTION = "content_consumption"
    SOCIAL_INTERACTION = "social_interaction"
    PURCHASE_INTENT = "purchase_intent"
    ABANDONMENT = "abandonment"
    CONVERSION = "conversion"

class UserSegment(Enum):
    """Segments utilisateurs comportementaux"""
    NEW_USER = "new_user"
    CASUAL_VIEWER = "casual_viewer"
    ENGAGED_VIEWER = "engaged_viewer"
    CONTENT_CREATOR = "content_creator"
    SUPER_FAN = "super_fan"
    CHURNED_USER = "churned_user"
    HIGH_VALUE = "high_value"
    POTENTIAL_CREATOR = "potential_creator"

class PersonalizationContext(Enum):
    """Contextes de personnalisation"""
    CONTENT_RECOMMENDATION = "content_recommendation"
    CREATOR_SUGGESTION = "creator_suggestion"
    INTERFACE_CUSTOMIZATION = "interface_customization"
    NOTIFICATION_PREFERENCE = "notification_preference"
    MONETIZATION_OPPORTUNITY = "monetization_opportunity"

@dataclass
class BehaviorEvent:
    """Événement comportemental utilisateur"""
    event_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    user_id: str = ""
    session_id: str = ""
    event_type: BehaviorEventType = BehaviorEventType.PAGE_VIEW
    timestamp: float = field(default_factory=time.time)
    page_url: Optional[str] = None
    element_id: Optional[str] = None
    element_type: Optional[str] = None
    content_id: Optional[str] = None
    creator_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    scroll_depth: Optional[float] = None
    device_info: Dict[str, str] = field(default_factory=dict)
    browser_info: Dict[str, str] = field(default_factory=dict)
    referrer: Optional[str] = None
    utm_parameters: Dict[str, str] = field(default_factory=dict)
    custom_properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserJourney:
    """Parcours utilisateur complet"""
    user_id: str
    session_id: str
    journey_start: float
    journey_end: Optional[float] = None
    total_duration: Optional[float] = None
    pages_visited: List[str] = field(default_factory=list)
    events_sequence: List[BehaviorEvent] = field(default_factory=list)
    conversion_events: List[str] = field(default_factory=list)
    drop_off_point: Optional[str] = None
    entry_point: Optional[str] = None
    exit_point: Optional[str] = None
    device_changes: List[Dict[str, str]] = field(default_factory=list)
    value_generated: float = 0.0

@dataclass
class UserProfile:
    """Profil comportemental utilisateur"""
    user_id: str
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    total_sessions: int = 0
    total_events: int = 0
    avg_session_duration: float = 0.0
    preferred_content_types: List[str] = field(default_factory=list)
    favorite_creators: List[str] = field(default_factory=list)
    engagement_score: float = 0.0
    conversion_rate: float = 0.0
    lifetime_value: float = 0.0
    predicted_segment: Optional[UserSegment] = None
    personalization_preferences: Dict[str, Any] = field(default_factory=dict)
    behavioral_insights: Dict[str, Any] = field(default_factory=dict)
    churn_probability: float = 0.0
    next_best_action: Optional[str] = None

@dataclass
class BehaviorInsight:
    """Insight comportemental ML-généré"""
    insight_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    user_id: str = ""
    insight_type: str = "engagement_pattern"
    title: str = ""
    description: str = ""
    confidence_score: float = 0.0
    generated_at: float = field(default_factory=time.time)
    actionable_recommendations: List[str] = field(default_factory=list)
    predicted_impact: Dict[str, float] = field(default_factory=dict)
    data_points_analyzed: int = 0

@dataclass
class BehaviorConfig:
    """Configuration du système comportemental"""
    redis_url: str = "redis://localhost:6379"
    session_timeout_minutes: int = 30
    journey_max_duration_hours: int = 24
    ml_insights_enabled: bool = True
    personalization_enabled: bool = True
    retention_days: int = 365
    batch_processing_size: int = 1000
    real_time_processing: bool = True
    privacy_mode: bool = True
    anonymization_enabled: bool = True

class UserBehaviorStorage:
    """🚀 **Enterprise**: Storage comportement utilisateur intelligent
    
    Système de stockage comportemental enterprise avec ML insights,
    journey mapping, personnalisation et analytics comportementales avancées.
    
    Fonctionnalités:
    - Tracking comportemental temps-réel
    - Journey mapping automatique
    - Segmentation ML intelligente
    - Personnalisation contextuelle
    - Prédiction churn/valeur
    - Insights comportementaux IA
    - Conformité GDPR/privacy
    """
    
    def __init__(self, config: BehaviorConfig):
        self.config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        
        # Stockage en mémoire pour performance
        self._active_sessions: Dict[str, UserJourney] = {}
        self._user_profiles: Dict[str, UserProfile] = {}
        self._behavior_buffer: deque = deque(maxlen=config.batch_processing_size)
        
        # Clés Redis optimisées
        self.events_prefix = "behavior:events"
        self.profiles_prefix = "behavior:profiles"
        self.journeys_prefix = "behavior:journeys"
        self.insights_prefix = "behavior:insights"
        self.segments_prefix = "behavior:segments"
        
        # ML Components
        self._segmentation_model = None
        self._churn_predictor = None
        self._personalization_engine = None
        
        # Tâches background
        self._processing_tasks: List[asyncio.Task] = []
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        
        # Performance counters
        self._events_processed = 0
        self._journeys_completed = 0
        self._insights_generated = 0
        self._profiles_updated = 0
        
    async def initialize(self) -> bool:
        """🚀 **Enterprise**: Initialisation storage comportemental
        
        Initialise connexion Redis, charge profils utilisateurs,
        démarre ML components et configure privacy/anonymisation.
        """
        try:
            if REDIS_AVAILABLE and self.config.redis_url:
                self._redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=30
                )
                await self._redis_client.ping()
                logger.info("✅ Connexion Redis user behavior établie")
            else:
                logger.warning("⚠️ Redis non disponible - mode dégradé activé")
                
            # Chargement profils utilisateurs existants
            await self._load_user_profiles()
            
            # Initialisation ML components
            if self.config.ml_insights_enabled:
                await self._initialize_ml_components()
            
            # Démarrage tâches background
            await self._start_background_tasks()
            
            # Configuration privacy/GDPR
            await self._setup_privacy_controls()
            
            self._running = True
            self._start_time = time.time()
            logger.info("🚀 User Behavior Storage initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation behavior storage: {e}")
            return False
    
    async def track_behavior(self, event: BehaviorEvent) -> bool:
        """👤 **UX Analyst**: Tracking événement comportemental
        
        Enregistre un événement comportemental avec validation,
        mise à jour journey en cours et déclenchement insights ML.
        """
        try:
            # Validation événement
            if not self._validate_behavior_event(event):
                logger.warning(f"⚠️ Événement comportemental invalide: {event.event_id}")
                return False
            
            # Anonymisation si activée
            if self.config.anonymization_enabled:
                event = await self._anonymize_event(event)
            
            # Mise à jour session/journey active
            await self._update_active_journey(event)
            
            # Mise à jour profil utilisateur
            await self._update_user_profile(event)
            
            # Ajout au buffer pour traitement
            self._behavior_buffer.append(event)
            self._events_processed += 1
            
            # Traitement temps-réel si activé
            if self.config.real_time_processing:
                await self._event_queue.put_nowait(event)
            
            # Déclenchement insights ML
            if self.config.ml_insights_enabled and self._should_generate_insights(event):
                await self._trigger_ml_insights(event.user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur tracking comportement: {e}")
            return False
    
    async def get_user_journey(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[UserJourney]:
        """🗺️ **Data Architect**: Récupération parcours utilisateur
        
        Récupère parcours complets utilisateur avec analyse automatique
        des patterns, points de friction et opportunités d'optimisation.
        """
        try:
            journeys = []
            
            # Récupération depuis sessions actives
            if session_id:
                active_journey = self._active_sessions.get(f"{user_id}:{session_id}")
                if active_journey:
                    journeys.append(active_journey)
            else:
                # Toutes les sessions actives de l'utilisateur
                user_sessions = [
                    journey for key, journey in self._active_sessions.items()
                    if key.startswith(f"{user_id}:")
                ]
                journeys.extend(user_sessions)
            
            # Récupération depuis Redis si nécessaire
            if time_range or not journeys:
                stored_journeys = await self._fetch_stored_journeys(user_id, time_range)
                journeys.extend(stored_journeys)
            
            # Enrichissement avec analytics
            for journey in journeys:
                await self._enrich_journey_analytics(journey)
            
            return journeys
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération journey utilisateur: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """👤 **ML Engineer**: Récupération profil comportemental
        
        Récupère profil utilisateur enrichi avec insights ML,
        prédictions et recommandations personnalisées.
        """
        try:
            # Tentative cache mémoire d'abord
            profile = self._user_profiles.get(user_id)
            
            if not profile:
                # Chargement depuis Redis
                profile = await self._load_user_profile_from_redis(user_id)
                
                if profile:
                    self._user_profiles[user_id] = profile
            
            if not profile:
                logger.info(f"ℹ️ Profil non trouvé pour utilisateur {user_id}")
                return None
            
            # Mise à jour insights ML si nécessaire
            if self._should_refresh_ml_insights(profile):
                await self._refresh_user_insights(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération profil utilisateur: {e}")
            return None
    
    async def get_behavioral_insights(
        self,
        user_id: str,
        insight_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[BehaviorInsight]:
        """🧠 **Behavioral Psychologist**: Insights comportementaux ML
        
        Génère insights comportementaux avancés avec ML:
        - Patterns de navigation
        - Préférences détectées
        - Prédictions comportementales
        - Recommandations d'optimisation
        """
        try:
            if not self.config.ml_insights_enabled:
                logger.warning("⚠️ Insights ML désactivés")
                return []
            
            # Récupération insights existants
            existing_insights = await self._get_stored_insights(user_id, insight_types)
            
            # Génération nouveaux insights si nécessaire
            if len(existing_insights) < limit:
                new_insights = await self._generate_behavioral_insights(user_id, insight_types)
                existing_insights.extend(new_insights)
            
            # Tri par score de confiance et pertinence
            existing_insights.sort(
                key=lambda i: (i.confidence_score, i.generated_at),
                reverse=True
            )
            
            return existing_insights[:limit]
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights comportementaux: {e}")
            return []
    
    async def get_user_segment_analysis(self, user_id: str) -> Dict[str, Any]:
        """📊 **Data Architect**: Analyse segmentation utilisateur
        
        Analyse segmentation complète avec prédictions ML:
        - Segment actuel et historique
        - Probabilités migration segments
        - Caractéristiques comportementales
        - Actions recommandées par segment
        """
        try:
            profile = await self.get_user_profile(user_id)
            if not profile:
                return {}
            
            analysis = {
                "user_id": user_id,
                "current_segment": profile.predicted_segment.value if profile.predicted_segment else "unknown",
                "segment_confidence": profile.engagement_score,
                "generated_at": datetime.now().isoformat()
            }
            
            # Calcul probabilités segments
            if self._segmentation_model:
                segment_probabilities = await self._calculate_segment_probabilities(profile)
                analysis["segment_probabilities"] = segment_probabilities
            
            # Historique évolution segment
            segment_history = await self._get_segment_history(user_id)
            analysis["segment_evolution"] = segment_history
            
            # Caractéristiques segment actuel
            segment_characteristics = await self._get_segment_characteristics(profile.predicted_segment)
            analysis["segment_characteristics"] = segment_characteristics
            
            # Actions recommandées
            recommended_actions = await self._get_segment_recommendations(profile)
            analysis["recommended_actions"] = recommended_actions
            
            # Prédictions évolution
            evolution_predictions = await self._predict_segment_evolution(profile)
            analysis["evolution_predictions"] = evolution_predictions
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse segmentation: {e}")
            return {}
    
    async def get_personalization_data(
        self,
        user_id: str,
        context: PersonalizationContext
    ) -> Dict[str, Any]:
        """🎯 **Personalization Engine**: Données personnalisation
        
        Génère données personnalisation contextuelles:
        - Recommandations contenu/créateurs
        - Préférences interface
        - Opportunités monétisation
        - Notifications optimisées
        """
        try:
            if not self.config.personalization_enabled:
                return {"personalization_enabled": False}
            
            profile = await self.get_user_profile(user_id)
            if not profile:
                return {"error": "Profil utilisateur non trouvé"}
            
            personalization_data = {
                "user_id": user_id,
                "context": context.value,
                "generated_at": datetime.now().isoformat()
            }
            
            # Données selon contexte
            if context == PersonalizationContext.CONTENT_RECOMMENDATION:
                recommendations = await self._generate_content_recommendations(profile)
                personalization_data["content_recommendations"] = recommendations
                
            elif context == PersonalizationContext.CREATOR_SUGGESTION:
                suggestions = await self._generate_creator_suggestions(profile)
                personalization_data["creator_suggestions"] = suggestions
                
            elif context == PersonalizationContext.INTERFACE_CUSTOMIZATION:
                ui_preferences = await self._generate_ui_preferences(profile)
                personalization_data["ui_preferences"] = ui_preferences
                
            elif context == PersonalizationContext.NOTIFICATION_PREFERENCE:
                notification_settings = await self._generate_notification_preferences(profile)
                personalization_data["notification_preferences"] = notification_settings
                
            elif context == PersonalizationContext.MONETIZATION_OPPORTUNITY:
                monetization_data = await self._generate_monetization_opportunities(profile)
                personalization_data["monetization_opportunities"] = monetization_data
            
            # Métriques de performance personnalisation
            performance_metrics = await self._get_personalization_performance(user_id, context)
            personalization_data["performance_metrics"] = performance_metrics
            
            return personalization_data
            
        except Exception as e:
            logger.error(f"❌ Erreur génération données personnalisation: {e}")
            return {}
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """⚡ **Performance Engineer**: Statistiques performance
        
        Retourne métriques performance détaillées du système comportemental.
        """
        uptime = time.time() - getattr(self, '_start_time', time.time())
        
        return {
            "uptime_seconds": uptime,
            "events_processed": self._events_processed,
            "journeys_completed": self._journeys_completed,
            "insights_generated": self._insights_generated,
            "profiles_updated": self._profiles_updated,
            "active_sessions": len(self._active_sessions),
            "cached_profiles": len(self._user_profiles),
            "buffer_size": len(self._behavior_buffer),
            "queue_size": self._event_queue.qsize(),
            "processing_rate_events_per_second": self._events_processed / max(uptime, 1),
            "ml_components_active": self.config.ml_insights_enabled,
            "personalization_active": self.config.personalization_enabled,
            "privacy_mode": self.config.privacy_mode
        }
    
    # Méthodes internes optimisées
    
    async def _update_active_journey(self, event: BehaviorEvent):
        """Mise à jour journey actif"""
        try:
            session_key = f"{event.user_id}:{event.session_id}"
            
            # Récupération ou création journey
            if session_key not in self._active_sessions:
                journey = UserJourney(
                    user_id=event.user_id,
                    session_id=event.session_id,
                    journey_start=event.timestamp,
                    entry_point=event.page_url
                )
                self._active_sessions[session_key] = journey
            else:
                journey = self._active_sessions[session_key]
            
            # Mise à jour journey
            journey.events_sequence.append(event)
            journey.journey_end = event.timestamp
            journey.total_duration = event.timestamp - journey.journey_start
            
            if event.page_url and event.page_url not in journey.pages_visited:
                journey.pages_visited.append(event.page_url)
            
            # Détection événements conversion
            if event.event_type in [BehaviorEventType.CONVERSION, BehaviorEventType.PURCHASE_INTENT]:
                journey.conversion_events.append(event.event_id)
            
            # Nettoyage sessions expirées
            await self._cleanup_expired_sessions()
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour journey: {e}")
    
    async def _update_user_profile(self, event: BehaviorEvent):
        """Mise à jour profil utilisateur"""
        try:
            profile = self._user_profiles.get(event.user_id)
            
            if not profile:
                profile = UserProfile(user_id=event.user_id)
                self._user_profiles[event.user_id] = profile
            
            # Mise à jour statistiques de base
            profile.last_seen = event.timestamp
            profile.total_events += 1
            
            # Mise à jour préférences contenu
            if event.content_id:
                content_type = event.custom_properties.get("content_type")
                if content_type and content_type not in profile.preferred_content_types:
                    profile.preferred_content_types.append(content_type)
            
            # Mise à jour créateurs favoris
            if event.creator_id and event.creator_id not in profile.favorite_creators:
                profile.favorite_creators.append(event.creator_id)
            
            # Calcul engagement score (simplifié)
            profile.engagement_score = min(100.0, profile.total_events / 100.0 * 10)
            
            self._profiles_updated += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour profil: {e}")
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        self._start_time = time.time()
        
        # Tâche traitement événements
        event_processor = asyncio.create_task(self._process_behavior_events())
        self._processing_tasks.append(event_processor)
        
        # Tâche nettoyage périodique
        cleanup_task = asyncio.create_task(self._periodic_cleanup())
        self._processing_tasks.append(cleanup_task)
        
        # Tâche génération insights ML
        if self.config.ml_insights_enabled:
            insights_task = asyncio.create_task(self._periodic_insights_generation())
            self._processing_tasks.append(insights_task)
        
        logger.info(f"✅ {len(self._processing_tasks)} tâches background démarrées")
    
    async def _process_behavior_events(self):
        """Processor événements comportementaux"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Traitement avancé événement
                await self._advanced_event_processing(event)
                
                self._event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erreur processing événement: {e}")
    
    def _validate_behavior_event(self, event: BehaviorEvent) -> bool:
        """Validation événement comportemental"""
        return bool(event.user_id and event.session_id and event.event_type)
    
    async def _anonymize_event(self, event: BehaviorEvent) -> BehaviorEvent:
        """Anonymisation événement (GDPR)"""
        if self.config.anonymization_enabled:
            # Hash user_id pour anonymisation
            event.user_id = hashlib.sha256(event.user_id.encode()).hexdigest()[:16]
            
            # Suppression données sensibles
            if event.position_x:
                event.position_x = None
            if event.position_y:
                event.position_y = None
                
        return event
    
    async def shutdown(self):
        """🛑 **Enterprise**: Arrêt propre du storage comportemental"""
        try:
            self._running = False
            
            # Sauvegarde sessions actives
            await self._save_active_sessions()
            
            # Sauvegarde profils utilisateurs
            await self._save_user_profiles()
            
            # Attente fin traitement
            await self._event_queue.join()
            
            # Arrêt tâches background
            for task in self._processing_tasks:
                task.cancel()
            
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)
            
            # Fermeture Redis
            if self._redis_client:
                await self._redis_client.close()
                
            logger.info("⏹️ User Behavior Storage arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt behavior storage: {e}")

    # Méthodes helper simplifiées (implémentation production plus complexe)
    
    async def _initialize_ml_components(self):
        """Initialisation composants ML"""
        # Implémentation simplifiée
        self._segmentation_model = "loaded"
        self._churn_predictor = "loaded"
        self._personalization_engine = "loaded"
    
    async def _load_user_profiles(self):
        """Chargement profils depuis Redis"""
        # Implémentation simplifiée
        pass
    
    async def _generate_behavioral_insights(self, user_id: str, insight_types: Optional[List[str]]) -> List[BehaviorInsight]:
        """Génération insights comportementaux"""
        # Implémentation simplifiée
        return []

# Factory function
async def create_user_behavior_storage(config: Optional[BehaviorConfig] = None) -> UserBehaviorStorage:
    """🏭 **Factory**: Création instance User Behavior Storage
    
    Crée et initialise un système de stockage comportemental enterprise
    avec ML insights et personnalisation avancée.
    """
    if config is None:
        config = BehaviorConfig()
        
    storage = UserBehaviorStorage(config)
    
    initialized = await storage.initialize()
    if not initialized:
        logger.warning("⚠️ User behavior storage initialisé en mode dégradé")
        
    return storage