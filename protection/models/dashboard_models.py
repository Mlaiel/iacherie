"""
Dashboard Models - Modèles pour les tableaux de bord de protection
==================================================================

Modèles de données pour les interfaces de tableau de bord et les métriques
de protection avec visualisation en temps réel.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# Import TimeSeriesData from monitoring module
try:
    from monitoring.intelligence.predictive_intelligence_forecasting_engine import TimeSeriesData
except ImportError:
    # Fallback TimeSeriesData definition
    @dataclass
    class TimeSeriesData:
        """Time series data point"""
        timestamp: datetime
        value: float
        metric_name: str
        metadata: Dict[str, Any] = field(default_factory=dict)


class DashboardType(Enum):
    """Types de tableaux de bord"""
    SECURITY = "security"
    ANALYTICS = "analytics"
    MONITORING = "monitoring"
    ALERTS = "alerts"
    PERFORMANCE = "performance"


class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"


@dataclass
class DashboardWidget:
    """Widget de tableau de bord"""
    id: str
    title: str
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 4, "height": 3})
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Met à jour les données du widget"""
        self.data.update(new_data)


@dataclass
class DashboardMetric:
    """Métrique pour tableau de bord"""
    name: str
    value: Union[int, float, str]
    type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la métrique en dictionnaire"""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "tags": self.tags
        }


@dataclass
class DashboardPanel:
    """Panneau de tableau de bord"""
    id: str
    title: str
    widgets: List[DashboardWidget] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    visible: bool = True
    
    def add_widget(self, widget: DashboardWidget) -> None:
        """Ajoute un widget au panneau"""
        self.widgets.append(widget)
    
    def remove_widget(self, widget_id: str) -> bool:
        """Supprime un widget du panneau"""
        for i, widget in enumerate(self.widgets):
            if widget.id == widget_id:
                del self.widgets[i]
                return True
        return False


@dataclass
class Dashboard:
    """Tableau de bord principal"""
    id: str
    name: str
    type: DashboardType
    panels: List[DashboardPanel] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_panel(self, panel: DashboardPanel) -> None:
        """Ajoute un panneau au tableau de bord"""
        self.panels.append(panel)
        self.updated_at = datetime.now()
    
    def get_panel(self, panel_id: str) -> Optional[DashboardPanel]:
        """Récupère un panneau par son ID"""
        for panel in self.panels:
            if panel.id == panel_id:
                return panel
        return None


@dataclass
class AlertDefinition:
    """Définition d'alerte pour dashboard"""
    id: str
    name: str
    metric_name: str
    condition: str
    threshold: Union[int, float]
    severity: str = "medium"
    enabled: bool = True
    
    def evaluate(self, metric_value: Union[int, float]) -> bool:
        """Évalue si l'alerte doit être déclenchée"""
        try:
            if self.condition == "greater_than":
                return metric_value > self.threshold
            elif self.condition == "less_than":
                return metric_value < self.threshold
            elif self.condition == "equals":
                return metric_value == self.threshold
            return False
        except (TypeError, ValueError):
            return False


@dataclass
class DashboardAlert:
    """Alerte de tableau de bord"""
    id: str
    definition: AlertDefinition
    triggered_at: datetime
    metric_value: Union[int, float]
    message: str
    acknowledged: bool = False
    
    def acknowledge(self) -> None:
        """Marque l'alerte comme acquittée"""
        self.acknowledged = True


@dataclass
class DashboardLayout:
    """Layout de tableau de bord"""
    id: str
    name: str
    grid_size: Dict[str, int] = field(default_factory=lambda: {"columns": 12, "rows": 12})
    widget_positions: Dict[str, Dict[str, int]] = field(default_factory=dict)
    responsive: bool = True
    
    def set_widget_position(self, widget_id: str, x: int, y: int, width: int, height: int) -> None:
        """Définit la position d'un widget"""
        self.widget_positions[widget_id] = {
            "x": x, "y": y, "width": width, "height": height
        }
    
    def get_widget_position(self, widget_id: str) -> Optional[Dict[str, int]]:
        """Récupère la position d'un widget"""
        return self.widget_positions.get(widget_id)


@dataclass
class UserPreferences:
    """Préférences utilisateur pour le tableau de bord"""
    user_id: str
    theme: str = "light"  # light, dark, auto
    language: str = "en"
    timezone: str = "UTC"
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "email": True,
        "push": True,
        "sms": False,
        "desktop": True
    })
    dashboard_layout: Optional[Dict[str, Any]] = None
    favorite_widgets: List[str] = field(default_factory=list)
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    auto_refresh: bool = True
    refresh_interval: int = 30  # seconds
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlertMetrics:
    """Métriques d'alertes pour le tableau de bord"""
    total_alerts: int = 0
    active_alerts: int = 0
    resolved_alerts: int = 0
    high_priority_alerts: int = 0
    medium_priority_alerts: int = 0
    low_priority_alerts: int = 0
    alerts_24h: int = 0
    alerts_7d: int = 0
    alerts_30d: int = 0
    average_resolution_time: float = 0.0  # hours
    false_positive_rate: float = 0.0
    alert_types: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PlatformMetrics:
    """Métriques de plateforme pour le tableau de bord"""
    total_users: int = 0
    active_users: int = 0
    total_content: int = 0
    protected_content: int = 0
    violation_rate: float = 0.0
    detection_accuracy: float = 0.0
    system_uptime: float = 100.0  # percentage
    avg_response_time: float = 0.0  # milliseconds
    storage_usage: Dict[str, float] = field(default_factory=dict)  # GB
    bandwidth_usage: float = 0.0  # GB
    api_calls_24h: int = 0
    errors_24h: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


# Export des modèles principaux
__all__ = [
    "DashboardType",
    "MetricType", 
    "DashboardWidget",
    "DashboardMetric",
    "DashboardPanel", 
    "Dashboard",
    "AlertDefinition",
    "DashboardAlert",
    "DashboardLayout",
    "UserPreferences",
    "AlertMetrics",
    "PlatformMetrics"
]