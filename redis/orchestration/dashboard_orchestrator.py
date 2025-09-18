#!/usr/bin/env python3
"""📈 Redis Dashboard Orchestrator - Advanced Dashboard Management & Visualization Engine
========================================================================================
Expert: FRONTEND ARCHITECT + DATA SCIENTIST + BACKEND SENIOR + UX EXPERT
Technologies: Dashboard Intelligence + Data Visualization + Real-Time Updates + Creator Economy Dashboards
Architecture: Level 3 - Dashboard Intelligence Layer
Date: 2025-01-14

Ultra-advanced dashboard orchestration system with AI-powered visualizations,
real-time updates, creator economy dashboards and intelligent layout optimization.
========================================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
========================================================================================
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
import json
import math
import statistics
from collections import deque, defaultdict
import redis
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types de dashboards"""
    CREATOR_OVERVIEW = "creator_overview"
    CREATOR_ANALYTICS = "creator_analytics"
    CREATOR_MONETIZATION = "creator_monetization"
    SYSTEM_OVERVIEW = "system_overview"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    REAL_TIME_MONITORING = "real_time_monitoring"
    COLLABORATION_ANALYTICS = "collaboration_analytics"
    CONTENT_PERFORMANCE = "content_performance"
    SECURITY_DASHBOARD = "security_dashboard"

class WidgetType(Enum):
    """Types de widgets dashboard"""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    TABLE = "table"
    PROGRESS_BAR = "progress_bar"
    GAUGE = "gauge"
    MAP = "map"
    TIMELINE = "timeline"
    NOTIFICATION_FEED = "notification_feed"
    QUICK_ACTIONS = "quick_actions"

class UpdateFrequency(Enum):
    """Fréquences de mise à jour"""
    REAL_TIME = "real_time"      # 1-5 secondes
    HIGH = "high"                # 30 secondes
    MEDIUM = "medium"            # 2 minutes
    LOW = "low"                  # 15 minutes
    ON_DEMAND = "on_demand"      # Sur demande

class LayoutType(Enum):
    """Types de layout"""
    GRID = "grid"
    MASONRY = "masonry"
    FLEXIBLE = "flexible"
    SIDEBAR = "sidebar"
    TABS = "tabs"
    SINGLE_PAGE = "single_page"

class DataSourceType(Enum):
    """Types de sources de données"""
    REAL_TIME_METRICS = "real_time_metrics"
    AGGREGATED_DATA = "aggregated_data"
    EXTERNAL_API = "external_api"
    STATIC_DATA = "static_data"
    USER_INPUT = "user_input"
    CALCULATED_FIELD = "calculated_field"

@dataclass
class DashboardWidget:
    """Widget de dashboard"""
    widget_id: str = ""
    title: str = ""
    widget_type: WidgetType = WidgetType.METRIC_CARD
    
    # Position et taille
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: Dict[str, int] = field(default_factory=lambda: {"width": 4, "height": 3})
    
    # Configuration données
    data_source: DataSourceType = DataSourceType.REAL_TIME_METRICS
    data_query: Dict[str, Any] = field(default_factory=dict)
    data_transformation: Optional[str] = None
    
    # Configuration visuelle
    visualization_config: Dict[str, Any] = field(default_factory=dict)
    style_config: Dict[str, Any] = field(default_factory=dict)
    
    # Mise à jour
    update_frequency: UpdateFrequency = UpdateFrequency.MEDIUM
    auto_refresh: bool = True
    last_updated: Optional[datetime] = None
    
    # Interactivité
    interactive: bool = True
    drill_down_config: Optional[Dict[str, Any]] = None
    click_actions: List[str] = field(default_factory=list)
    
    # Données cache
    cached_data: Optional[Dict[str, Any]] = None
    cache_expires: Optional[datetime] = None
    
    # Personnalisation
    customizable: bool = True
    user_preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Configuration dashboard"""
    dashboard_id: str = ""
    name: str = ""
    description: str = ""
    dashboard_type: DashboardType = DashboardType.CREATOR_OVERVIEW
    
    # Layout
    layout_type: LayoutType = LayoutType.GRID
    layout_config: Dict[str, Any] = field(default_factory=dict)
    
    # Widgets
    widgets: List[DashboardWidget] = field(default_factory=list)
    
    # Permissions
    owner_id: str = ""
    visibility: str = "private"  # private, shared, public
    allowed_users: List[str] = field(default_factory=list)
    
    # Configuration
    auto_refresh_enabled: bool = True
    refresh_interval: int = 60  # secondes
    theme: str = "default"
    responsive: bool = True
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    
    # Analytics dashboard
    view_count: int = 0
    unique_viewers: int = 0
    avg_time_spent: float = 0.0
    
    # Performance
    load_time_avg: float = 0.0
    render_performance: Dict[str, float] = field(default_factory=dict)

@dataclass
class DashboardTemplate:
    """Template de dashboard"""
    template_id: str = ""
    name: str = ""
    description: str = ""
    dashboard_type: DashboardType = DashboardType.CREATOR_OVERVIEW
    
    # Configuration template
    widget_templates: List[Dict[str, Any]] = field(default_factory=list)
    layout_template: Dict[str, Any] = field(default_factory=dict)
    
    # Personnalisation
    customization_options: Dict[str, Any] = field(default_factory=dict)
    required_data_sources: List[str] = field(default_factory=list)
    
    # Métadonnées
    category: str = ""
    tags: List[str] = field(default_factory=list)
    popularity_score: float = 0.0
    
    # Versions
    version: str = "1.0"
    changelog: List[str] = field(default_factory=list)

@dataclass
class DashboardSubscription:
    """Abonnement dashboard"""
    subscription_id: str = ""
    user_id: str = ""
    dashboard_id: str = ""
    
    # Configuration notifications
    email_notifications: bool = False
    alert_thresholds: Dict[str, Any] = field(default_factory=dict)
    notification_frequency: str = "daily"
    
    # Préférences
    preferred_delivery_time: str = "09:00"
    include_insights: bool = True
    include_recommendations: bool = True
    
    # État
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class RedisDashboardOrchestrator:
    """📈 Orchestrateur de dashboards Redis ultra-intelligent"""
    
    def __init__(self):
        """Initialisation orchestrateur dashboards"""
        self.redis_client = None
        self.is_running = False
        
        # Storage dashboards
        self.dashboards = {}
        self.dashboard_templates = {}
        self.active_subscriptions = {}
        self.dashboard_cache = {}
        
        # Système de rendu
        self.render_queue = deque()
        self.render_workers = {}
        self.real_time_connections = defaultdict(set)
        
        # Analytics dashboards
        self.dashboard_analytics = defaultdict(dict)
        self.user_interactions = defaultdict(list)
        self.performance_metrics = defaultdict(dict)
        
        # Configuration optimisations
        self.cache_config = {
            "default_ttl": 300,  # 5 minutes
            "high_frequency_ttl": 60,  # 1 minute
            "low_frequency_ttl": 900   # 15 minutes
        }
        
        # Système de recommandations
        self.recommendation_engine = None
        self.layout_optimizer = None
        
        # Métriques système
        self.orchestrator_metrics = {
            "dashboards_created": 0,
            "widgets_rendered": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "real_time_updates": 0,
            "average_render_time": 0.0
        }
        
        # Initialiser templates par défaut
        self._initialize_default_templates()
        
        logger.info("📈 Orchestrateur dashboards Redis initialisé")

    async def start(self, redis_connection=None):
        """Démarrer l'orchestrateur dashboards"""
        try:
            self.redis_client = redis_connection or redis.Redis(decode_responses=True)
            self.is_running = True
            
            # Démarrer services dashboard
            dashboard_tasks = [
                self._run_real_time_updates(),
                self._run_cache_maintenance(),
                self._run_render_queue_processor(),
                self._run_analytics_collector(),
                self._run_subscription_manager(),
                self._run_recommendation_engine(),
                self._run_performance_monitor()
            ]
            
            await asyncio.gather(*dashboard_tasks, return_exceptions=True)
            
            logger.info("📈 Orchestrateur dashboards démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage orchestrateur dashboards: {e}")
            raise

    async def stop(self):
        """Arrêter l'orchestrateur"""
        self.is_running = False
        logger.info("📈 Orchestrateur dashboards arrêté")

    async def create_dashboard(self, dashboard_config: Dict[str, Any], user_id: str) -> str:
        """Créer un nouveau dashboard"""
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Créer dashboard depuis config
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=dashboard_config.get("name", "Nouveau Dashboard"),
                description=dashboard_config.get("description", ""),
                dashboard_type=DashboardType(dashboard_config.get("type", "creator_overview")),
                owner_id=user_id,
                layout_type=LayoutType(dashboard_config.get("layout", "grid"))
            )
            
            # Ajouter widgets depuis template si spécifié
            template_id = dashboard_config.get("template_id")
            if template_id and template_id in self.dashboard_templates:
                await self._apply_template_to_dashboard(dashboard, template_id)
            
            # Ajouter widgets personnalisés
            if "widgets" in dashboard_config:
                for widget_config in dashboard_config["widgets"]:
                    widget = await self._create_widget_from_config(widget_config)
                    dashboard.widgets.append(widget)
            
            # Valider et optimiser layout
            await self._optimize_dashboard_layout(dashboard)
            
            # Sauvegarder
            self.dashboards[dashboard_id] = dashboard
            await self._persist_dashboard(dashboard)
            
            # Initialiser cache widgets
            await self._initialize_dashboard_cache(dashboard)
            
            self.orchestrator_metrics["dashboards_created"] += 1
            
            logger.info(f"📈 Dashboard créé: {dashboard.name} ({dashboard_id})")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création dashboard: {e}")
            raise

    async def render_dashboard(self, dashboard_id: str, user_id: str, 
                              viewport: Dict[str, int] = None) -> Dict[str, Any]:
        """Rendre un dashboard complet"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                dashboard = await self._load_dashboard(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard non trouvé: {dashboard_id}")
            
            # Vérifier permissions
            if not await self._check_dashboard_permissions(dashboard, user_id):
                raise PermissionError("Accès dashboard non autorisé")
            
            # Configuration rendu
            render_config = {
                "viewport": viewport or {"width": 1920, "height": 1080},
                "user_id": user_id,
                "timestamp": datetime.now(),
                "real_time_enabled": dashboard.auto_refresh_enabled
            }
            
            # Rendre widgets
            rendered_widgets = []
            for widget in dashboard.widgets:
                rendered_widget = await self._render_widget(widget, render_config)
                rendered_widgets.append(rendered_widget)
            
            # Optimiser layout pour viewport
            optimized_layout = await self._optimize_layout_for_viewport(
                dashboard.layout_config, 
                rendered_widgets,
                render_config["viewport"]
            )
            
            # Générer configuration dashboard
            dashboard_render = {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "type": dashboard.dashboard_type.value,
                "layout": {
                    "type": dashboard.layout_type.value,
                    "config": optimized_layout
                },
                "widgets": rendered_widgets,
                "theme": dashboard.theme,
                "responsive": dashboard.responsive,
                "auto_refresh": {
                    "enabled": dashboard.auto_refresh_enabled,
                    "interval": dashboard.refresh_interval
                },
                "metadata": {
                    "rendered_at": render_config["timestamp"].isoformat(),
                    "viewport": render_config["viewport"],
                    "user_id": user_id
                },
                "real_time_config": await self._get_real_time_config(dashboard),
                "performance": await self._get_dashboard_performance_info(dashboard_id)
            }
            
            # Enregistrer analytics
            await self._record_dashboard_view(dashboard_id, user_id)
            
            # Ajouter à connexions temps réel si nécessaire
            if dashboard.auto_refresh_enabled:
                self.real_time_connections[dashboard_id].add(user_id)
            
            logger.info(f"📈 Dashboard rendu: {dashboard_id} pour {user_id}")
            return dashboard_render
            
        except Exception as e:
            logger.error(f"❌ Erreur rendu dashboard {dashboard_id}: {e}")
            raise

    async def create_creator_dashboard(self, creator_id: str, dashboard_type: str = "overview") -> str:
        """Créer dashboard spécialisé créateur"""
        try:
            # Configuration selon type
            if dashboard_type == "overview":
                template_id = "creator_overview_template"
                widgets_config = [
                    {
                        "type": "metric_card",
                        "title": "Followers",
                        "data_query": {"metric": "followers_count", "creator_id": creator_id},
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 3, "height": 2}
                    },
                    {
                        "type": "metric_card", 
                        "title": "Engagement Rate",
                        "data_query": {"metric": "engagement_rate", "creator_id": creator_id},
                        "position": {"x": 3, "y": 0},
                        "size": {"width": 3, "height": 2}
                    },
                    {
                        "type": "line_chart",
                        "title": "Revenue Trend",
                        "data_query": {"metric": "revenue", "creator_id": creator_id, "time_range": "30d"},
                        "position": {"x": 0, "y": 2},
                        "size": {"width": 6, "height": 4}
                    },
                    {
                        "type": "bar_chart",
                        "title": "Content Performance",
                        "data_query": {"metric": "content_performance", "creator_id": creator_id},
                        "position": {"x": 6, "y": 0},
                        "size": {"width": 6, "height": 6}
                    }
                ]
            
            elif dashboard_type == "analytics":
                template_id = "creator_analytics_template"
                widgets_config = [
                    {
                        "type": "heatmap",
                        "title": "Activity Heatmap",
                        "data_query": {"metric": "activity_heatmap", "creator_id": creator_id},
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 8, "height": 4}
                    },
                    {
                        "type": "pie_chart",
                        "title": "Revenue Sources",
                        "data_query": {"metric": "revenue_breakdown", "creator_id": creator_id},
                        "position": {"x": 8, "y": 0},
                        "size": {"width": 4, "height": 4}
                    },
                    {
                        "type": "table",
                        "title": "Top Content",
                        "data_query": {"metric": "top_content", "creator_id": creator_id},
                        "position": {"x": 0, "y": 4},
                        "size": {"width": 12, "height": 4}
                    }
                ]
            
            elif dashboard_type == "monetization":
                template_id = "creator_monetization_template"
                widgets_config = [
                    {
                        "type": "gauge",
                        "title": "Monthly Revenue Goal",
                        "data_query": {"metric": "revenue_goal_progress", "creator_id": creator_id},
                        "position": {"x": 0, "y": 0},
                        "size": {"width": 4, "height": 3}
                    },
                    {
                        "type": "line_chart",
                        "title": "Revenue vs Engagement",
                        "data_query": {"metric": "revenue_engagement_correlation", "creator_id": creator_id},
                        "position": {"x": 4, "y": 0},
                        "size": {"width": 8, "height": 3}
                    }
                ]
            
            else:
                raise ValueError(f"Type dashboard créateur non supporté: {dashboard_type}")
            
            # Créer dashboard
            dashboard_config = {
                "name": f"Creator {dashboard_type.title()} - {creator_id}",
                "description": f"Dashboard {dashboard_type} pour créateur {creator_id}",
                "type": f"creator_{dashboard_type}",
                "template_id": template_id,
                "widgets": widgets_config,
                "layout": "grid"
            }
            
            dashboard_id = await self.create_dashboard(dashboard_config, creator_id)
            
            # Configurer abonnements automatiques
            await self._setup_creator_dashboard_subscriptions(dashboard_id, creator_id)
            
            logger.info(f"📈 Dashboard créateur créé: {dashboard_type} pour {creator_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création dashboard créateur: {e}")
            raise

    async def update_widget_data(self, dashboard_id: str, widget_id: str, 
                               force_refresh: bool = False) -> Dict[str, Any]:
        """Mettre à jour données d'un widget"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                dashboard = await self._load_dashboard(dashboard_id)
            
            # Trouver widget
            widget = None
            for w in dashboard.widgets:
                if w.widget_id == widget_id:
                    widget = w
                    break
            
            if not widget:
                raise ValueError(f"Widget non trouvé: {widget_id}")
            
            # Vérifier cache si pas de force refresh
            if not force_refresh and widget.cached_data and widget.cache_expires:
                if datetime.now() < widget.cache_expires:
                    self.orchestrator_metrics["cache_hits"] += 1
                    return widget.cached_data
            
            self.orchestrator_metrics["cache_misses"] += 1
            
            # Récupérer nouvelles données
            widget_data = await self._fetch_widget_data(widget)
            
            # Appliquer transformations
            if widget.data_transformation:
                widget_data = await self._apply_data_transformation(
                    widget_data, widget.data_transformation
                )
            
            # Mise en cache
            widget.cached_data = widget_data
            widget.cache_expires = datetime.now() + timedelta(
                seconds=self._get_cache_ttl(widget.update_frequency)
            )
            widget.last_updated = datetime.now()
            
            # Diffuser mise à jour temps réel
            if dashboard.auto_refresh_enabled:
                await self._broadcast_widget_update(dashboard_id, widget_id, widget_data)
            
            self.orchestrator_metrics["widgets_rendered"] += 1
            
            logger.debug(f"📈 Widget mis à jour: {widget_id}")
            return widget_data
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour widget {widget_id}: {e}")
            return {"error": str(e)}

    async def get_dashboard_analytics(self, dashboard_id: str) -> Dict[str, Any]:
        """Récupérer analytics d'un dashboard"""
        try:
            dashboard = self.dashboards.get(dashboard_id)
            if not dashboard:
                return {"error": "Dashboard non trouvé"}
            
            analytics = {
                "dashboard_id": dashboard_id,
                "basic_metrics": {
                    "view_count": dashboard.view_count,
                    "unique_viewers": dashboard.unique_viewers,
                    "avg_time_spent": dashboard.avg_time_spent,
                    "last_accessed": dashboard.last_accessed.isoformat() if dashboard.last_accessed else None
                },
                
                "performance_metrics": {
                    "load_time_avg": dashboard.load_time_avg,
                    "render_performance": dashboard.render_performance,
                    "cache_efficiency": await self._calculate_cache_efficiency(dashboard_id)
                },
                
                "usage_patterns": await self._analyze_dashboard_usage_patterns(dashboard_id),
                "widget_analytics": await self._get_widgets_analytics(dashboard_id),
                "user_interactions": await self._analyze_user_interactions(dashboard_id),
                
                "optimization_suggestions": await self._generate_optimization_suggestions(dashboard_id),
                "performance_score": await self._calculate_performance_score(dashboard_id),
                
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Erreur analytics dashboard {dashboard_id}: {e}")
            return {"error": str(e)}

    async def create_dashboard_template(self, template_config: Dict[str, Any]) -> str:
        """Créer un template de dashboard"""
        try:
            template_id = str(uuid.uuid4())
            
            template = DashboardTemplate(
                template_id=template_id,
                name=template_config.get("name", "Nouveau Template"),
                description=template_config.get("description", ""),
                dashboard_type=DashboardType(template_config.get("type", "creator_overview")),
                widget_templates=template_config.get("widgets", []),
                layout_template=template_config.get("layout", {}),
                customization_options=template_config.get("customization", {}),
                category=template_config.get("category", "custom"),
                tags=template_config.get("tags", [])
            )
            
            # Valider template
            if not await self._validate_template(template):
                raise ValueError("Template invalide")
            
            # Sauvegarder
            self.dashboard_templates[template_id] = template
            await self._persist_template(template)
            
            logger.info(f"📈 Template dashboard créé: {template.name}")
            return template_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création template: {e}")
            raise

    async def subscribe_to_dashboard(self, user_id: str, dashboard_id: str, 
                                   subscription_config: Dict[str, Any]) -> str:
        """S'abonner aux notifications d'un dashboard"""
        try:
            subscription_id = str(uuid.uuid4())
            
            subscription = DashboardSubscription(
                subscription_id=subscription_id,
                user_id=user_id,
                dashboard_id=dashboard_id,
                email_notifications=subscription_config.get("email_notifications", False),
                alert_thresholds=subscription_config.get("alert_thresholds", {}),
                notification_frequency=subscription_config.get("frequency", "daily"),
                preferred_delivery_time=subscription_config.get("delivery_time", "09:00"),
                include_insights=subscription_config.get("include_insights", True),
                include_recommendations=subscription_config.get("include_recommendations", True)
            )
            
            self.active_subscriptions[subscription_id] = subscription
            await self._persist_subscription(subscription)
            
            logger.info(f"📈 Abonnement dashboard créé: {user_id} -> {dashboard_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création abonnement: {e}")
            raise

    # ================== MÉTHODES PRIVÉES ==================

    def _initialize_default_templates(self):
        """Initialiser templates par défaut"""
        # Template créateur overview
        creator_overview_template = DashboardTemplate(
            template_id="creator_overview_template",
            name="Creator Overview",
            description="Vue d'ensemble pour créateurs",
            dashboard_type=DashboardType.CREATOR_OVERVIEW,
            widget_templates=[
                {"type": "metric_card", "title": "Followers", "position": {"x": 0, "y": 0}},
                {"type": "metric_card", "title": "Engagement", "position": {"x": 3, "y": 0}},
                {"type": "line_chart", "title": "Growth", "position": {"x": 0, "y": 2}}
            ],
            category="creator",
            tags=["creator", "overview", "analytics"]
        )
        self.dashboard_templates["creator_overview_template"] = creator_overview_template
        
        # Template système monitoring
        system_monitoring_template = DashboardTemplate(
            template_id="system_monitoring_template", 
            name="System Monitoring",
            description="Monitoring système temps réel",
            dashboard_type=DashboardType.REAL_TIME_MONITORING,
            widget_templates=[
                {"type": "gauge", "title": "CPU Usage", "position": {"x": 0, "y": 0}},
                {"type": "gauge", "title": "Memory Usage", "position": {"x": 3, "y": 0}},
                {"type": "line_chart", "title": "Performance", "position": {"x": 0, "y": 2}}
            ],
            category="system",
            tags=["system", "monitoring", "performance"]
        )
        self.dashboard_templates["system_monitoring_template"] = system_monitoring_template

    async def _run_real_time_updates(self):
        """Gestion mises à jour temps réel"""
        while self.is_running:
            try:
                for dashboard_id, connected_users in self.real_time_connections.items():
                    if connected_users:
                        await self._process_real_time_updates(dashboard_id, connected_users)
                await asyncio.sleep(5)  # Mises à jour toutes les 5 secondes
            except Exception as e:
                logger.error(f"❌ Erreur mises à jour temps réel: {e}")
                await asyncio.sleep(10)

    async def _run_cache_maintenance(self):
        """Maintenance cache dashboards"""
        while self.is_running:
            try:
                await self._clean_expired_dashboard_cache()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
                await asyncio.sleep(600)

    async def _run_render_queue_processor(self):
        """Processeur queue de rendu"""
        while self.is_running:
            try:
                if self.render_queue:
                    render_task = self.render_queue.popleft()
                    await self._process_render_task(render_task)
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"❌ Erreur processing rendu: {e}")
                await asyncio.sleep(1)

    async def _run_analytics_collector(self):
        """Collecteur analytics dashboards"""
        while self.is_running:
            try:
                await self._collect_dashboard_analytics()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur collection analytics: {e}")
                await asyncio.sleep(600)

    async def _run_subscription_manager(self):
        """Gestionnaire abonnements"""
        while self.is_running:
            try:
                await self._process_dashboard_subscriptions()
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"❌ Erreur gestion abonnements: {e}")
                await asyncio.sleep(1800)

    async def _run_recommendation_engine(self):
        """Moteur recommandations dashboards"""
        while self.is_running:
            try:
                await self._generate_dashboard_recommendations()
                await asyncio.sleep(1800)  # Toutes les 30 minutes
            except Exception as e:
                logger.error(f"❌ Erreur recommandations: {e}")
                await asyncio.sleep(3600)

    async def _run_performance_monitor(self):
        """Monitoring performance dashboards"""
        while self.is_running:
            try:
                await self._monitor_dashboard_performance()
                await asyncio.sleep(60)  # Toutes les minutes
            except Exception as e:
                logger.error(f"❌ Erreur monitoring performance: {e}")
                await asyncio.sleep(120)

    def _get_cache_ttl(self, update_frequency: UpdateFrequency) -> int:
        """Obtenir TTL cache selon fréquence"""
        ttl_map = {
            UpdateFrequency.REAL_TIME: 10,
            UpdateFrequency.HIGH: 30,
            UpdateFrequency.MEDIUM: 120,
            UpdateFrequency.LOW: 900,
            UpdateFrequency.ON_DEMAND: 3600
        }
        return ttl_map.get(update_frequency, self.cache_config["default_ttl"])

    async def _persist_dashboard(self, dashboard: Dashboard):
        """Persister dashboard"""
        try:
            if self.redis_client:
                key = f"dashboard:{dashboard.dashboard_id}"
                data = {
                    "name": dashboard.name,
                    "type": dashboard.dashboard_type.value,
                    "owner_id": dashboard.owner_id,
                    "created_at": dashboard.created_at.isoformat(),
                    "widget_count": len(dashboard.widgets)
                }
                await self.redis_client.hset(key, mapping=data)
                await self.redis_client.expire(key, 2592000)  # 30 jours
        except Exception as e:
            logger.error(f"❌ Erreur persistence dashboard: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Récupérer métriques orchestrateur"""
        return {
            "orchestrator_type": "dashboard_orchestrator",
            "status": "running" if self.is_running else "stopped",
            "dashboards_count": len(self.dashboards),
            "templates_count": len(self.dashboard_templates),
            "active_subscriptions": len(self.active_subscriptions),
            "real_time_connections": sum(len(users) for users in self.real_time_connections.values()),
            "performance_metrics": self.orchestrator_metrics,
            "cache_sizes": {
                "dashboard_cache": len(self.dashboard_cache),
                "render_queue": len(self.render_queue)
            }
        }