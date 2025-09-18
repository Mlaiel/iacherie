#!/usr/bin/env python3
"""📊 Dashboard Orchestrator - Dynamic Dashboard Management System
================================================================
Expert: FRONTEND ARCHITECT + BACKEND SENIOR + DATA VISUALIZATION + UX ENGINEER
Technologies: Real-Time Dashboards + Data Visualization + Interactive Analytics + Dashboard Builder
Architecture: Level 3 - Dashboard Intelligence Layer
Date: 2025-01-14

Ultra-advanced dashboard orchestration system with real-time data visualization,
interactive dashboard builder, and intelligent layout management.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
import statistics
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types de dashboard"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICS = "analytics"
    CREATOR_INSIGHTS = "creator_insights"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    REAL_TIME_MONITORING = "real_time_monitoring"
    CUSTOM = "custom"

class WidgetType(Enum):
    """Types de widgets"""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    LIST = "list"
    MAP = "map"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    CALENDAR = "calendar"
    TIMELINE = "timeline"

class LayoutType(Enum):
    """Types de layout"""
    GRID = "grid"
    FLUID = "fluid"
    FIXED = "fixed"
    RESPONSIVE = "responsive"
    MASONRY = "masonry"
    TABS = "tabs"

class RefreshMode(Enum):
    """Modes de rafraîchissement"""
    MANUAL = "manual"
    AUTO = "auto"
    REAL_TIME = "real_time"
    ON_DEMAND = "on_demand"
    SCHEDULED = "scheduled"

class ThemeType(Enum):
    """Types de thème"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    CUSTOM = "custom"
    BRAND = "brand"

@dataclass
class DashboardWidget:
    """Widget de dashboard"""
    widget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    widget_type: WidgetType = WidgetType.METRIC_CARD
    data_source: str = ""
    query: str = ""
    refresh_interval: timedelta = timedelta(minutes=5)
    refresh_mode: RefreshMode = RefreshMode.AUTO
    position: Dict[str, int] = field(default_factory=dict)  # x, y, width, height
    styling: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    drill_down: Optional[str] = None
    is_visible: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = None

@dataclass
class DashboardLayout:
    """Layout de dashboard"""
    layout_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    layout_type: LayoutType = LayoutType.GRID
    grid_config: Dict[str, Any] = field(default_factory=dict)
    responsive_breakpoints: Dict[str, Dict] = field(default_factory=dict)
    widget_positions: List[Dict[str, Any]] = field(default_factory=list)
    is_responsive: bool = True
    auto_arrange: bool = True

@dataclass
class DashboardTheme:
    """Thème de dashboard"""
    theme_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    theme_type: ThemeType = ThemeType.LIGHT
    colors: Dict[str, str] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    spacing: Dict[str, int] = field(default_factory=dict)
    borders: Dict[str, str] = field(default_factory=dict)
    shadows: Dict[str, str] = field(default_factory=dict)
    animations: Dict[str, Any] = field(default_factory=dict)
    custom_css: str = ""

@dataclass
class Dashboard:
    """Dashboard complet"""
    dashboard_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    dashboard_type: DashboardType = DashboardType.OPERATIONAL
    layout: DashboardLayout = field(default_factory=DashboardLayout)
    theme: DashboardTheme = field(default_factory=DashboardTheme)
    widgets: List[str] = field(default_factory=list)  # Widget IDs
    filters: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    refresh_mode: RefreshMode = RefreshMode.AUTO
    refresh_interval: timedelta = timedelta(minutes=5)
    is_public: bool = False
    is_active: bool = True
    tags: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0

@dataclass
class DashboardSession:
    """Session de dashboard"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dashboard_id: str = ""
    user_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    current_filters: Dict[str, Any] = field(default_factory=dict)
    view_state: Dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    is_active: bool = True

@dataclass
class WidgetData:
    """Données d'un widget"""
    widget_id: str = ""
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    cache_key: str = ""
    refresh_needed: bool = False
    error: Optional[str] = None

@dataclass
class DashboardOrchestratorConfig:
    """Configuration de l'orchestrateur de dashboard"""
    max_widgets_per_dashboard: int = 50
    max_concurrent_dashboards: int = 100
    default_refresh_interval: timedelta = timedelta(minutes=5)
    max_refresh_interval: timedelta = timedelta(hours=24)
    enable_real_time: bool = True
    enable_caching: bool = True
    cache_duration: timedelta = timedelta(minutes=5)
    enable_websockets: bool = True
    websocket_heartbeat: timedelta = timedelta(seconds=30)
    session_timeout: timedelta = timedelta(hours=8)
    max_data_points: int = 1000
    enable_drill_down: bool = True
    enable_export: bool = True

class DataProvider(ABC):
    """Interface abstraite pour les fournisseurs de données"""
    
    @abstractmethod
    async def get_data(self, query: str, filters: Dict[str, Any] = None) -> Any:
        """Récupère les données selon la requête"""
        pass

class RedisDataProvider(DataProvider):
    """Fournisseur de données Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def get_data(self, query: str, filters: Dict[str, Any] = None) -> Any:
        """Récupère les données depuis Redis"""
        try:
            # Simulation d'une requête Redis
            if query == "total_events":
                return np.random.randint(1000, 10000)
            elif query == "active_users":
                return np.random.randint(100, 1000)
            elif query == "performance_metrics":
                return {
                    'cpu_usage': np.random.uniform(20, 80),
                    'memory_usage': np.random.uniform(30, 70),
                    'response_time': np.random.uniform(50, 200)
                }
            elif query == "time_series_data":
                # Générer des données de série temporelle
                now = datetime.now()
                data = []
                for i in range(24):
                    timestamp = now - timedelta(hours=23-i)
                    value = np.random.uniform(50, 150) + 10 * np.sin(i * 0.5)
                    data.append({
                        'timestamp': timestamp.isoformat(),
                        'value': round(value, 2)
                    })
                return data
            elif query == "creator_analytics":
                return {
                    'total_creators': np.random.randint(500, 2000),
                    'active_creators': np.random.randint(200, 800),
                    'content_uploads': np.random.randint(1000, 5000),
                    'engagement_rate': np.random.uniform(0.05, 0.15),
                    'revenue': np.random.uniform(10000, 50000)
                }
            else:
                return {"message": "No data available"}
                
        except Exception as e:
            logger.error(f"❌ Failed to get data from Redis: {e}")
            return None

class WebSocketManager:
    """Gestionnaire WebSocket pour les mises à jour temps réel"""
    
    def __init__(self):
        self.connections = {}
        self.subscriptions = defaultdict(set)
    
    async def connect(self, session_id: str, dashboard_id: str):
        """Connecte une session WebSocket"""
        self.connections[session_id] = {
            'dashboard_id': dashboard_id,
            'connected_at': datetime.now(),
            'last_ping': datetime.now()
        }
        self.subscriptions[dashboard_id].add(session_id)
        logger.info(f"🔗 WebSocket connected: {session_id} to dashboard {dashboard_id}")
    
    async def disconnect(self, session_id: str):
        """Déconnecte une session WebSocket"""
        if session_id in self.connections:
            dashboard_id = self.connections[session_id]['dashboard_id']
            self.subscriptions[dashboard_id].discard(session_id)
            del self.connections[session_id]
            logger.info(f"❌ WebSocket disconnected: {session_id}")
    
    async def broadcast_to_dashboard(self, dashboard_id: str, message: Dict[str, Any]):
        """Diffuse un message à toutes les sessions d'un dashboard"""
        sessions = self.subscriptions.get(dashboard_id, set())
        for session_id in sessions:
            await self._send_message(session_id, message)
    
    async def _send_message(self, session_id: str, message: Dict[str, Any]):
        """Envoie un message à une session (simulation)"""
        logger.debug(f"📤 Sending WebSocket message to {session_id}: {json.dumps(message)[:100]}...")

class RedisDashboardOrchestrator:
    """Orchestrateur de dashboard Redis enterprise"""
    
    def __init__(self, config: DashboardOrchestratorConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client or redis.Redis()
        self.is_running = False
        
        # Composants internes
        self.dashboards = {}
        self.widgets = {}
        self.active_sessions = {}
        self.data_cache = {}
        
        # Providers et managers
        self.data_provider = RedisDataProvider(self.redis_client)
        self.websocket_manager = WebSocketManager()
        
        # Métriques de l'orchestrateur
        self.orchestrator_metrics = {
            'dashboards_created': 0,
            'widgets_created': 0,
            'sessions_active': 0,
            'data_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'websocket_connections': 0,
            'avg_response_time': 0,
            'last_activity': None
        }
        
        # Tâches asynchrones
        self.refresh_task = None
        self.session_cleanup_task = None
        self.websocket_heartbeat_task = None
    
    async def initialize(self) -> bool:
        """Initialise l'orchestrateur de dashboard"""
        try:
            logger.info("📊 Initializing Dashboard Orchestrator...")
            
            # Charger les dashboards existants
            await self._load_dashboards()
            
            # Charger les widgets
            await self._load_widgets()
            
            # Créer des dashboards par défaut si aucun n'existe
            if not self.dashboards:
                await self._create_default_dashboards()
            
            # Démarrer les tâches de fond
            await self._start_background_tasks()
            
            self.is_running = True
            logger.info("✅ Dashboard Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dashboard Orchestrator: {e}")
            return False
    
    async def _load_dashboards(self):
        """Charge les dashboards existants"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("dashboard:dashboards:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    dashboard_data = json.loads(data)
                    dashboard = Dashboard(**dashboard_data)
                    self.dashboards[dashboard.dashboard_id] = dashboard
            
            logger.info(f"✅ Loaded {len(self.dashboards)} dashboards")
            
        except Exception as e:
            logger.error(f"❌ Failed to load dashboards: {e}")
    
    async def _load_widgets(self):
        """Charge les widgets existants"""
        try:
            keys = [key.decode() for key in self.redis_client.keys("dashboard:widgets:*")]
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    widget_data = json.loads(data)
                    widget = DashboardWidget(**widget_data)
                    self.widgets[widget.widget_id] = widget
            
            logger.info(f"✅ Loaded {len(self.widgets)} widgets")
            
        except Exception as e:
            logger.error(f"❌ Failed to load widgets: {e}")
    
    async def _create_default_dashboards(self):
        """Crée les dashboards par défaut"""
        try:
            # Dashboard exécutif
            executive_dashboard = await self.create_dashboard(
                name="Executive Overview",
                description="High-level business metrics and KPIs",
                dashboard_type=DashboardType.EXECUTIVE,
                created_by="system"
            )
            
            # Widgets pour le dashboard exécutif
            await self._create_executive_widgets(executive_dashboard.dashboard_id)
            
            # Dashboard opérationnel
            operational_dashboard = await self.create_dashboard(
                name="Operational Monitoring",
                description="Real-time system performance and health",
                dashboard_type=DashboardType.OPERATIONAL,
                created_by="system"
            )
            
            # Widgets pour le dashboard opérationnel
            await self._create_operational_widgets(operational_dashboard.dashboard_id)
            
            # Dashboard créateurs
            creator_dashboard = await self.create_dashboard(
                name="Creator Analytics",
                description="Creator economy insights and metrics",
                dashboard_type=DashboardType.CREATOR_INSIGHTS,
                created_by="system"
            )
            
            # Widgets pour le dashboard créateurs
            await self._create_creator_widgets(creator_dashboard.dashboard_id)
            
            logger.info("✅ Created default dashboards")
            
        except Exception as e:
            logger.error(f"❌ Failed to create default dashboards: {e}")
    
    async def _create_executive_widgets(self, dashboard_id: str):
        """Crée les widgets pour le dashboard exécutif"""
        widgets = [
            {
                'title': 'Total Revenue',
                'widget_type': WidgetType.METRIC_CARD,
                'data_source': 'redis',
                'query': 'total_revenue',
                'position': {'x': 0, 'y': 0, 'width': 3, 'height': 2}
            },
            {
                'title': 'Active Users',
                'widget_type': WidgetType.METRIC_CARD,
                'data_source': 'redis',
                'query': 'active_users',
                'position': {'x': 3, 'y': 0, 'width': 3, 'height': 2}
            },
            {
                'title': 'Growth Trend',
                'widget_type': WidgetType.LINE_CHART,
                'data_source': 'redis',
                'query': 'time_series_data',
                'position': {'x': 0, 'y': 2, 'width': 6, 'height': 4}
            }
        ]
        
        for widget_config in widgets:
            widget = await self.create_widget(
                title=widget_config['title'],
                widget_type=widget_config['widget_type'],
                data_source=widget_config['data_source'],
                query=widget_config['query'],
                position=widget_config['position']
            )
            await self.add_widget_to_dashboard(dashboard_id, widget.widget_id)
    
    async def _create_operational_widgets(self, dashboard_id: str):
        """Crée les widgets pour le dashboard opérationnel"""
        widgets = [
            {
                'title': 'System Health',
                'widget_type': WidgetType.GAUGE,
                'data_source': 'redis',
                'query': 'system_health',
                'position': {'x': 0, 'y': 0, 'width': 4, 'height': 3}
            },
            {
                'title': 'Performance Metrics',
                'widget_type': WidgetType.TABLE,
                'data_source': 'redis',
                'query': 'performance_metrics',
                'position': {'x': 4, 'y': 0, 'width': 4, 'height': 3}
            },
            {
                'title': 'Response Time',
                'widget_type': WidgetType.LINE_CHART,
                'data_source': 'redis',
                'query': 'response_time_series',
                'position': {'x': 0, 'y': 3, 'width': 8, 'height': 3}
            }
        ]
        
        for widget_config in widgets:
            widget = await self.create_widget(
                title=widget_config['title'],
                widget_type=widget_config['widget_type'],
                data_source=widget_config['data_source'],
                query=widget_config['query'],
                position=widget_config['position']
            )
            await self.add_widget_to_dashboard(dashboard_id, widget.widget_id)
    
    async def _create_creator_widgets(self, dashboard_id: str):
        """Crée les widgets pour le dashboard créateurs"""
        widgets = [
            {
                'title': 'Creator Analytics',
                'widget_type': WidgetType.BAR_CHART,
                'data_source': 'redis',
                'query': 'creator_analytics',
                'position': {'x': 0, 'y': 0, 'width': 6, 'height': 4}
            },
            {
                'title': 'Top Creators',
                'widget_type': WidgetType.LIST,
                'data_source': 'redis',
                'query': 'top_creators',
                'position': {'x': 6, 'y': 0, 'width': 3, 'height': 4}
            },
            {
                'title': 'Content Distribution',
                'widget_type': WidgetType.PIE_CHART,
                'data_source': 'redis',
                'query': 'content_types',
                'position': {'x': 0, 'y': 4, 'width': 4, 'height': 3}
            }
        ]
        
        for widget_config in widgets:
            widget = await self.create_widget(
                title=widget_config['title'],
                widget_type=widget_config['widget_type'],
                data_source=widget_config['data_source'],
                query=widget_config['query'],
                position=widget_config['position']
            )
            await self.add_widget_to_dashboard(dashboard_id, widget.widget_id)
    
    async def _start_background_tasks(self):
        """Démarre les tâches de fond"""
        self.refresh_task = asyncio.create_task(self._refresh_loop())
        self.session_cleanup_task = asyncio.create_task(self._session_cleanup_loop())
        
        if self.config.enable_websockets:
            self.websocket_heartbeat_task = asyncio.create_task(self._websocket_heartbeat_loop())
    
    async def create_dashboard(self, name: str, description: str,
                             dashboard_type: DashboardType = DashboardType.CUSTOM,
                             created_by: str = "") -> Dashboard:
        """Crée un nouveau dashboard"""
        try:
            # Créer le thème par défaut
            theme = DashboardTheme(
                name=f"{name} Theme",
                theme_type=ThemeType.LIGHT,
                colors={
                    'primary': '#007bff',
                    'secondary': '#6c757d',
                    'success': '#28a745',
                    'warning': '#ffc107',
                    'danger': '#dc3545',
                    'background': '#ffffff',
                    'text': '#212529'
                }
            )
            
            # Créer le layout par défaut
            layout = DashboardLayout(
                name=f"{name} Layout",
                layout_type=LayoutType.GRID,
                grid_config={
                    'columns': 12,
                    'row_height': 60,
                    'margin': [10, 10],
                    'container_padding': [20, 20]
                },
                is_responsive=True,
                auto_arrange=True
            )
            
            # Créer le dashboard
            dashboard = Dashboard(
                name=name,
                description=description,
                dashboard_type=dashboard_type,
                layout=layout,
                theme=theme,
                created_by=created_by
            )
            
            # Stocker le dashboard
            self.dashboards[dashboard.dashboard_id] = dashboard
            await self._store_dashboard(dashboard)
            
            # Mettre à jour les métriques
            self.orchestrator_metrics['dashboards_created'] += 1
            
            logger.info(f"✅ Created dashboard: {name}")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard: {e}")
            raise
    
    async def create_widget(self, title: str, widget_type: WidgetType,
                          data_source: str, query: str,
                          position: Optional[Dict[str, int]] = None,
                          configuration: Optional[Dict[str, Any]] = None) -> DashboardWidget:
        """Crée un nouveau widget"""
        try:
            widget = DashboardWidget(
                title=title,
                widget_type=widget_type,
                data_source=data_source,
                query=query,
                position=position or {'x': 0, 'y': 0, 'width': 4, 'height': 3},
                configuration=configuration or {}
            )
            
            # Stocker le widget
            self.widgets[widget.widget_id] = widget
            await self._store_widget(widget)
            
            # Mettre à jour les métriques
            self.orchestrator_metrics['widgets_created'] += 1
            
            logger.info(f"✅ Created widget: {title}")
            return widget
            
        except Exception as e:
            logger.error(f"❌ Failed to create widget: {e}")
            raise
    
    async def add_widget_to_dashboard(self, dashboard_id: str, widget_id: str) -> bool:
        """Ajoute un widget à un dashboard"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if widget_id not in self.widgets:
                raise ValueError(f"Widget {widget_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            
            # Vérifier la limite de widgets
            if len(dashboard.widgets) >= self.config.max_widgets_per_dashboard:
                raise ValueError(f"Maximum {self.config.max_widgets_per_dashboard} widgets per dashboard")
            
            # Ajouter le widget
            if widget_id not in dashboard.widgets:
                dashboard.widgets.append(widget_id)
                await self._store_dashboard(dashboard)
                
                logger.info(f"✅ Added widget {widget_id} to dashboard {dashboard_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to add widget to dashboard: {e}")
            return False
    
    async def start_dashboard_session(self, dashboard_id: str, user_id: str) -> DashboardSession:
        """Démarre une session de dashboard"""
        try:
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            session = DashboardSession(
                dashboard_id=dashboard_id,
                user_id=user_id
            )
            
            self.active_sessions[session.session_id] = session
            
            # Connecter WebSocket si activé
            if self.config.enable_websockets:
                await self.websocket_manager.connect(session.session_id, dashboard_id)
                self.orchestrator_metrics['websocket_connections'] += 1
            
            # Mettre à jour les métriques du dashboard
            dashboard = self.dashboards[dashboard_id]
            dashboard.last_accessed = datetime.now()
            dashboard.access_count += 1
            await self._store_dashboard(dashboard)
            
            # Mettre à jour les métriques de l'orchestrateur
            self.orchestrator_metrics['sessions_active'] = len(self.active_sessions)
            self.orchestrator_metrics['last_activity'] = datetime.now()
            
            logger.info(f"🚀 Started dashboard session: {session.session_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to start dashboard session: {e}")
            raise
    
    async def get_dashboard_data(self, dashboard_id: str, 
                               filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Récupère les données complètes d'un dashboard"""
        try:
            start_time = time.time()
            
            if dashboard_id not in self.dashboards:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            dashboard = self.dashboards[dashboard_id]
            dashboard_data = {
                'dashboard': self._serialize_dashboard(dashboard),
                'widgets': {},
                'layout': dashboard.layout,
                'theme': dashboard.theme,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'filters_applied': filters or {}
                }
            }
            
            # Récupérer les données de chaque widget
            for widget_id in dashboard.widgets:
                if widget_id in self.widgets:
                    widget = self.widgets[widget_id]
                    widget_data = await self._get_widget_data(widget, filters)
                    dashboard_data['widgets'][widget_id] = {
                        'widget': self._serialize_widget(widget),
                        'data': widget_data.data,
                        'metadata': widget_data.metadata,
                        'timestamp': widget_data.timestamp.isoformat(),
                        'error': widget_data.error
                    }
            
            # Mettre à jour les métriques
            response_time = time.time() - start_time
            self.orchestrator_metrics['data_requests'] += 1
            self.orchestrator_metrics['avg_response_time'] = (
                (self.orchestrator_metrics['avg_response_time'] * 
                 (self.orchestrator_metrics['data_requests'] - 1) + response_time) /
                self.orchestrator_metrics['data_requests']
            )
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard data: {e}")
            raise
    
    async def _get_widget_data(self, widget: DashboardWidget, 
                             filters: Optional[Dict[str, Any]] = None) -> WidgetData:
        """Récupère les données d'un widget"""
        try:
            # Créer la clé de cache
            cache_key = f"{widget.widget_id}:{hash(str(filters))}"
            
            # Vérifier le cache
            if self.config.enable_caching and cache_key in self.data_cache:
                cache_entry = self.data_cache[cache_key]
                if datetime.now() - cache_entry.timestamp < self.config.cache_duration:
                    self.orchestrator_metrics['cache_hits'] += 1
                    return cache_entry
            
            # Récupérer les données fraîches
            data = await self.data_provider.get_data(widget.query, filters)
            
            widget_data = WidgetData(
                widget_id=widget.widget_id,
                data=data,
                metadata={
                    'widget_type': widget.widget_type.value,
                    'query': widget.query,
                    'filters': filters or {},
                    'refresh_interval': widget.refresh_interval.total_seconds()
                },
                cache_key=cache_key
            )
            
            # Mettre en cache
            if self.config.enable_caching:
                self.data_cache[cache_key] = widget_data
                self.orchestrator_metrics['cache_misses'] += 1
            
            return widget_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get widget data: {e}")
            return WidgetData(
                widget_id=widget.widget_id,
                error=str(e)
            )
    
    def _serialize_dashboard(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Sérialise un dashboard"""
        return {
            'dashboard_id': dashboard.dashboard_id,
            'name': dashboard.name,
            'description': dashboard.description,
            'dashboard_type': dashboard.dashboard_type.value,
            'widgets': dashboard.widgets,
            'filters': dashboard.filters,
            'refresh_mode': dashboard.refresh_mode.value,
            'refresh_interval': dashboard.refresh_interval.total_seconds(),
            'is_public': dashboard.is_public,
            'is_active': dashboard.is_active,
            'tags': dashboard.tags,
            'created_by': dashboard.created_by,
            'created_at': dashboard.created_at.isoformat(),
            'access_count': dashboard.access_count
        }
    
    def _serialize_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Sérialise un widget"""
        return {
            'widget_id': widget.widget_id,
            'title': widget.title,
            'description': widget.description,
            'widget_type': widget.widget_type.value,
            'data_source': widget.data_source,
            'query': widget.query,
            'refresh_interval': widget.refresh_interval.total_seconds(),
            'refresh_mode': widget.refresh_mode.value,
            'position': widget.position,
            'styling': widget.styling,
            'configuration': widget.configuration,
            'filters': widget.filters,
            'is_visible': widget.is_visible,
            'created_at': widget.created_at.isoformat()
        }
    
    async def _store_dashboard(self, dashboard: Dashboard):
        """Stocke un dashboard dans Redis"""
        try:
            key = f"dashboard:dashboards:{dashboard.dashboard_id}"
            data = self._serialize_dashboard(dashboard)
            data['layout'] = {
                'layout_id': dashboard.layout.layout_id,
                'name': dashboard.layout.name,
                'layout_type': dashboard.layout.layout_type.value,
                'grid_config': dashboard.layout.grid_config,
                'responsive_breakpoints': dashboard.layout.responsive_breakpoints,
                'widget_positions': dashboard.layout.widget_positions,
                'is_responsive': dashboard.layout.is_responsive,
                'auto_arrange': dashboard.layout.auto_arrange
            }
            data['theme'] = {
                'theme_id': dashboard.theme.theme_id,
                'name': dashboard.theme.name,
                'theme_type': dashboard.theme.theme_type.value,
                'colors': dashboard.theme.colors,
                'fonts': dashboard.theme.fonts,
                'spacing': dashboard.theme.spacing,
                'borders': dashboard.theme.borders,
                'shadows': dashboard.theme.shadows,
                'animations': dashboard.theme.animations,
                'custom_css': dashboard.theme.custom_css
            }
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store dashboard: {e}")
    
    async def _store_widget(self, widget: DashboardWidget):
        """Stocke un widget dans Redis"""
        try:
            key = f"dashboard:widgets:{widget.widget_id}"
            data = self._serialize_widget(widget)
            
            self.redis_client.setex(key, 30 * 24 * 3600, json.dumps(data))
            
        except Exception as e:
            logger.error(f"❌ Failed to store widget: {e}")
    
    async def _refresh_loop(self):
        """Boucle de rafraîchissement des données"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Rafraîchir les widgets qui en ont besoin
                for widget in self.widgets.values():
                    if (widget.refresh_mode == RefreshMode.AUTO and
                        (not widget.last_updated or 
                         current_time - widget.last_updated >= widget.refresh_interval)):
                        
                        await self._refresh_widget(widget)
                
                # Diffuser les mises à jour via WebSocket
                if self.config.enable_websockets:
                    await self._broadcast_updates()
                
                await asyncio.sleep(10)  # Vérifier toutes les 10 secondes
                
            except Exception as e:
                logger.error(f"❌ Error in refresh loop: {e}")
                await asyncio.sleep(30)
    
    async def _refresh_widget(self, widget: DashboardWidget):
        """Rafraîchit les données d'un widget"""
        try:
            # Invalider le cache
            cache_keys_to_remove = [key for key in self.data_cache.keys() 
                                  if key.startswith(widget.widget_id)]
            for key in cache_keys_to_remove:
                del self.data_cache[key]
            
            # Marquer comme rafraîchi
            widget.last_updated = datetime.now()
            await self._store_widget(widget)
            
            logger.debug(f"🔄 Refreshed widget: {widget.title}")
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh widget {widget.widget_id}: {e}")
    
    async def _broadcast_updates(self):
        """Diffuse les mises à jour via WebSocket"""
        try:
            # Identifier les dashboards avec des sessions actives
            active_dashboard_ids = set()
            for session in self.active_sessions.values():
                if session.is_active:
                    active_dashboard_ids.add(session.dashboard_id)
            
            # Diffuser les mises à jour pour chaque dashboard actif
            for dashboard_id in active_dashboard_ids:
                update_message = {
                    'type': 'data_update',
                    'dashboard_id': dashboard_id,
                    'timestamp': datetime.now().isoformat(),
                    'widgets_updated': []  # En production, liste des widgets mis à jour
                }
                
                await self.websocket_manager.broadcast_to_dashboard(dashboard_id, update_message)
            
        except Exception as e:
            logger.error(f"❌ Failed to broadcast updates: {e}")
    
    async def _session_cleanup_loop(self):
        """Boucle de nettoyage des sessions"""
        while self.is_running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if (current_time - session.last_activity > self.config.session_timeout):
                        expired_sessions.append(session_id)
                
                # Nettoyer les sessions expirées
                for session_id in expired_sessions:
                    await self._cleanup_session(session_id)
                
                # Mettre à jour les métriques
                self.orchestrator_metrics['sessions_active'] = len(self.active_sessions)
                
                if expired_sessions:
                    logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in session cleanup loop: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_session(self, session_id: str):
        """Nettoie une session expirée"""
        try:
            if session_id in self.active_sessions:
                # Déconnecter WebSocket
                if self.config.enable_websockets:
                    await self.websocket_manager.disconnect(session_id)
                
                # Supprimer la session
                del self.active_sessions[session_id]
                
                logger.debug(f"🗑️ Cleaned up session: {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup session {session_id}: {e}")
    
    async def _websocket_heartbeat_loop(self):
        """Boucle de heartbeat WebSocket"""
        while self.is_running:
            try:
                heartbeat_message = {
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Envoyer heartbeat à toutes les connexions
                for session_id in list(self.websocket_manager.connections.keys()):
                    await self.websocket_manager._send_message(session_id, heartbeat_message)
                
                await asyncio.sleep(self.config.websocket_heartbeat.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Error in WebSocket heartbeat loop: {e}")
                await asyncio.sleep(30)
    
    async def get_dashboard_list(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère la liste des dashboards"""
        try:
            dashboard_list = []
            
            for dashboard in self.dashboards.values():
                if dashboard.is_active:
                    # Vérifier les permissions si un utilisateur est spécifié
                    if user_id and not self._check_dashboard_permission(dashboard, user_id):
                        continue
                    
                    dashboard_summary = {
                        'dashboard_id': dashboard.dashboard_id,
                        'name': dashboard.name,
                        'description': dashboard.description,
                        'dashboard_type': dashboard.dashboard_type.value,
                        'widget_count': len(dashboard.widgets),
                        'is_public': dashboard.is_public,
                        'tags': dashboard.tags,
                        'created_by': dashboard.created_by,
                        'created_at': dashboard.created_at.isoformat(),
                        'last_accessed': (dashboard.last_accessed.isoformat() 
                                        if dashboard.last_accessed else None),
                        'access_count': dashboard.access_count
                    }
                    dashboard_list.append(dashboard_summary)
            
            # Trier par accès récent
            dashboard_list.sort(key=lambda x: x['access_count'], reverse=True)
            
            return dashboard_list
            
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard list: {e}")
            return []
    
    def _check_dashboard_permission(self, dashboard: Dashboard, user_id: str) -> bool:
        """Vérifie les permissions d'accès à un dashboard"""
        # Si le dashboard est public, autoriser l'accès
        if dashboard.is_public:
            return True
        
        # Si l'utilisateur est le créateur, autoriser l'accès
        if dashboard.created_by == user_id:
            return True
        
        # Vérifier les permissions explicites
        allowed_users = dashboard.permissions.get('read', [])
        return user_id in allowed_users
    
    async def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de l'orchestrateur"""
        try:
            return {
                'dashboards_created': self.orchestrator_metrics['dashboards_created'],
                'widgets_created': self.orchestrator_metrics['widgets_created'],
                'sessions_active': len(self.active_sessions),
                'data_requests': self.orchestrator_metrics['data_requests'],
                'cache_hit_rate': (self.orchestrator_metrics['cache_hits'] / 
                                 (self.orchestrator_metrics['cache_hits'] + 
                                  self.orchestrator_metrics['cache_misses'])
                                 if self.orchestrator_metrics['cache_hits'] + 
                                    self.orchestrator_metrics['cache_misses'] > 0 else 0),
                'websocket_connections': len(self.websocket_manager.connections),
                'avg_response_time_ms': self.orchestrator_metrics['avg_response_time'] * 1000,
                'last_activity': (self.orchestrator_metrics['last_activity'].isoformat() 
                                if self.orchestrator_metrics['last_activity'] else None),
                'total_dashboards': len(self.dashboards),
                'total_widgets': len(self.widgets),
                'cache_size': len(self.data_cache),
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get orchestrator metrics: {e}")
            return {}
    
    async def shutdown(self):
        """Arrête l'orchestrateur de dashboard"""
        try:
            logger.info("🛑 Shutting down Dashboard Orchestrator...")
            
            self.is_running = False
            
            # Arrêter toutes les tâches
            tasks = [self.refresh_task, self.session_cleanup_task, self.websocket_heartbeat_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Nettoyer toutes les sessions
            for session_id in list(self.active_sessions.keys()):
                await self._cleanup_session(session_id)
            
            logger.info("✅ Dashboard Orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Factory function pour créer l'orchestrateur
async def create_dashboard_orchestrator(
    config: Optional[DashboardOrchestratorConfig] = None,
    redis_client: Optional[redis.Redis] = None
) -> RedisDashboardOrchestrator:
    """Crée et initialise un orchestrateur de dashboard"""
    
    if config is None:
        config = DashboardOrchestratorConfig()
    
    orchestrator = RedisDashboardOrchestrator(config, redis_client)
    
    if await orchestrator.initialize():
        return orchestrator
    else:
        raise RuntimeError("Failed to initialize Dashboard Orchestrator")

__all__ = [
    'RedisDashboardOrchestrator',
    'DashboardOrchestratorConfig',
    'Dashboard',
    'DashboardWidget',
    'DashboardLayout',
    'DashboardTheme',
    'DashboardSession',
    'WidgetData',
    'DashboardType',
    'WidgetType',
    'LayoutType',
    'RefreshMode',
    'ThemeType',
    'DataProvider',
    'RedisDataProvider',
    'WebSocketManager',
    'create_dashboard_orchestrator'
]
