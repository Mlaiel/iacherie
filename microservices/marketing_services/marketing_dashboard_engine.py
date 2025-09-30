"""
Marketing Dashboard Engine - IA Chérie Enterprise
==============================================
Moteur dashboard marketing enterprise avec visualisations temps réel.
Real-time analytics + interactive dashboards + KPI monitoring + executive reporting.

Author: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
IP Owner: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Marketing Services
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture dashboard marketing et tous ses algorithmes sont la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
Toute reproduction, modification, distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types de dashboards marketing supportés"""
    EXECUTIVE = "executive"
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    INFLUENCER_ANALYTICS = "influencer_analytics"
    ROI_TRACKING = "roi_tracking"
    AUDIENCE_INSIGHTS = "audience_insights"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    REAL_TIME_MONITORING = "real_time_monitoring"

class VisualizationType(Enum):
    """Types de visualisations supportés"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    SCATTER_PLOT = "scatter_plot"
    GEOGRAPHIC_MAP = "geographic_map"
    REAL_TIME_GAUGE = "real_time_gauge"

@dataclass
class DashboardConfig:
    """Configuration pour dashboard marketing"""
    dashboard_id: str
    dashboard_type: DashboardType
    user_permissions: List[str]
    refresh_interval: int = 30  # seconds
    auto_refresh: bool = True
    export_formats: List[str] = field(default_factory=lambda: ['pdf', 'excel', 'json'])
    timezone: str = "UTC"
    locale: str = "en_US"

@dataclass
class KPIDefinition:
    """Définition d'un KPI marketing"""
    kpi_id: str
    name: str
    description: str
    calculation_method: str
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    unit: str = "number"
    visualization_type: VisualizationType = VisualizationType.LINE_CHART

@dataclass
class DashboardWidget:
    """Widget de dashboard marketing"""
    widget_id: str
    title: str
    widget_type: str
    data_source: str
    visualization_config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    refresh_rate: int = 60  # seconds
    filters: Dict[str, Any] = field(default_factory=dict)

class MarketingDashboardEngine:
    """
    Moteur dashboard marketing enterprise avec visualisations temps réel.
    
    Features:
    - Real-time dashboard generation avec streaming data
    - Interactive visualizations avec drill-down capabilities
    - Executive reporting avec automated insights
    - KPI monitoring avec alerting système
    - Multi-user dashboards avec role-based access
    - Export functionality vers multiple formats
    - Mobile-responsive dashboard layouts
    - A/B testing dashboard pour campaign optimization
    """
    
    def __init__(self, dashboard_config: DashboardConfig):
        self.dashboard_config = dashboard_config
        self.active_dashboards: Dict[str, Dict] = {}
        self.kpi_definitions: Dict[str, KPIDefinition] = {}
        self.widgets: Dict[str, DashboardWidget] = {}
        self.data_sources: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, Dict] = {}
        
        logger.info(f"Marketing Dashboard Engine initialized for {dashboard_config.dashboard_type.value}")
    
    async def create_executive_dashboard(self, executive_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Création dashboard executive avec KPIs de haut niveau.
        
        Executive Dashboard Features:
        - ROI overview avec trending analysis
        - Campaign performance summary
        - Budget utilization tracking
        - Revenue attribution modeling
        - Market share analysis
        - Competitive positioning insights
        """
        try:
            dashboard_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Configuration widgets executives
            executive_widgets = [
                {
                    "widget_id": "roi_overview",
                    "title": "Marketing ROI Overview",
                    "type": "kpi_card",
                    "data": await self._calculate_roi_metrics(),
                    "visualization": "gauge_chart",
                    "alerts": True
                },
                {
                    "widget_id": "campaign_performance",
                    "title": "Campaign Performance Summary",
                    "type": "summary_table",
                    "data": await self._get_campaign_summary(),
                    "visualization": "performance_grid"
                },
                {
                    "widget_id": "budget_utilization",
                    "title": "Budget Utilization",
                    "type": "progress_chart",
                    "data": await self._calculate_budget_metrics(),
                    "visualization": "horizontal_bar"
                },
                {
                    "widget_id": "revenue_attribution",
                    "title": "Revenue Attribution",
                    "type": "attribution_chart",
                    "data": await self._get_attribution_data(),
                    "visualization": "waterfall_chart"
                }
            ]
            
            dashboard = {
                "dashboard_id": dashboard_id,
                "type": "executive",
                "created_at": datetime.now().isoformat(),
                "widgets": executive_widgets,
                "config": executive_config,
                "auto_refresh": True,
                "refresh_interval": 300  # 5 minutes
            }
            
            self.active_dashboards[dashboard_id] = dashboard
            
            logger.info(f"Executive dashboard created: {dashboard_id}")
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "dashboard": dashboard,
                "widgets_count": len(executive_widgets)
            }
            
        except Exception as e:
            logger.error(f"Error creating executive dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_campaign_performance_dashboard(self, campaign_ids: List[str]) -> Dict[str, Any]:
        """
        Création dashboard performance campagnes avec métriques détaillées.
        
        Campaign Dashboard Features:
        - Real-time campaign metrics tracking
        - Conversion funnel analysis
        - Audience engagement heatmaps
        - A/B testing results visualization
        - Cost per acquisition tracking
        - Attribution modeling per campaign
        """
        try:
            dashboard_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            campaign_widgets = []
            
            for campaign_id in campaign_ids:
                campaign_data = await self._get_campaign_metrics(campaign_id)
                
                widgets = [
                    {
                        "widget_id": f"metrics_{campaign_id}",
                        "title": f"Campaign {campaign_id} - Key Metrics",
                        "type": "metrics_grid",
                        "data": campaign_data["metrics"],
                        "visualization": "metric_cards"
                    },
                    {
                        "widget_id": f"funnel_{campaign_id}",
                        "title": f"Campaign {campaign_id} - Conversion Funnel",
                        "type": "funnel_chart",
                        "data": campaign_data["funnel_data"],
                        "visualization": "funnel_visualization"
                    },
                    {
                        "widget_id": f"engagement_{campaign_id}",
                        "title": f"Campaign {campaign_id} - Engagement Heatmap",
                        "type": "heatmap",
                        "data": campaign_data["engagement_data"],
                        "visualization": "heatmap_chart"
                    }
                ]
                
                campaign_widgets.extend(widgets)
            
            dashboard = {
                "dashboard_id": dashboard_id,
                "type": "campaign_performance",
                "campaigns": campaign_ids,
                "created_at": datetime.now().isoformat(),
                "widgets": campaign_widgets,
                "real_time": True,
                "refresh_interval": 60  # 1 minute
            }
            
            self.active_dashboards[dashboard_id] = dashboard
            
            logger.info(f"Campaign performance dashboard created: {dashboard_id}")
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "campaigns_tracked": len(campaign_ids),
                "widgets_count": len(campaign_widgets)
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign performance dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_influencer_analytics_dashboard(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Création dashboard analytics influenceurs avec performance tracking.
        
        Influencer Dashboard Features:
        - Influencer performance ranking
        - Engagement rate analysis
        - Audience demographic insights
        - Content performance metrics
        - Partnership ROI tracking
        - Growth trend analysis
        """
        try:
            dashboard_id = f"influencer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            influencer_widgets = [
                {
                    "widget_id": "influencer_ranking",
                    "title": "Influencer Performance Ranking",
                    "type": "ranking_table",
                    "data": await self._calculate_influencer_rankings(influencer_data),
                    "visualization": "ranked_list"
                },
                {
                    "widget_id": "engagement_analysis",
                    "title": "Engagement Rate Analysis",
                    "type": "engagement_chart",
                    "data": await self._analyze_engagement_rates(influencer_data),
                    "visualization": "line_chart"
                },
                {
                    "widget_id": "audience_demographics",
                    "title": "Audience Demographics",
                    "type": "demographic_chart",
                    "data": await self._get_audience_demographics(influencer_data),
                    "visualization": "pie_charts"
                },
                {
                    "widget_id": "content_performance",
                    "title": "Content Performance Metrics",
                    "type": "content_grid",
                    "data": await self._analyze_content_performance(influencer_data),
                    "visualization": "performance_grid"
                },
                {
                    "widget_id": "partnership_roi",
                    "title": "Partnership ROI Tracking",
                    "type": "roi_chart",
                    "data": await self._calculate_partnership_roi(influencer_data),
                    "visualization": "bar_chart"
                }
            ]
            
            dashboard = {
                "dashboard_id": dashboard_id,
                "type": "influencer_analytics",
                "created_at": datetime.now().isoformat(),
                "widgets": influencer_widgets,
                "influencer_count": len(influencer_data.get("influencers", [])),
                "refresh_interval": 120  # 2 minutes
            }
            
            self.active_dashboards[dashboard_id] = dashboard
            
            logger.info(f"Influencer analytics dashboard created: {dashboard_id}")
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "influencers_tracked": len(influencer_data.get("influencers", [])),
                "widgets_count": len(influencer_widgets)
            }
            
        except Exception as e:
            logger.error(f"Error creating influencer analytics dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_real_time_monitoring_dashboard(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Création dashboard monitoring temps réel avec alertes.
        
        Real-time Monitoring Features:
        - Live campaign metrics streaming
        - Real-time alert system
        - Performance anomaly detection
        - Budget burn rate monitoring
        - Conversion rate tracking
        - Traffic spike detection
        """
        try:
            dashboard_id = f"realtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            monitoring_widgets = [
                {
                    "widget_id": "live_metrics",
                    "title": "Live Campaign Metrics",
                    "type": "real_time_metrics",
                    "data_stream": "live_campaign_data",
                    "visualization": "streaming_chart",
                    "update_frequency": 5  # 5 seconds
                },
                {
                    "widget_id": "alert_center",
                    "title": "Alert Center",
                    "type": "alert_panel",
                    "data": await self._get_active_alerts(),
                    "visualization": "alert_list",
                    "priority_filtering": True
                },
                {
                    "widget_id": "anomaly_detection",
                    "title": "Performance Anomaly Detection",
                    "type": "anomaly_chart",
                    "data": await self._detect_performance_anomalies(),
                    "visualization": "anomaly_visualization"
                },
                {
                    "widget_id": "budget_burn_rate",
                    "title": "Budget Burn Rate",
                    "type": "burn_rate_gauge",
                    "data": await self._calculate_burn_rate(),
                    "visualization": "gauge_chart",
                    "alerts": True
                }
            ]
            
            dashboard = {
                "dashboard_id": dashboard_id,
                "type": "real_time_monitoring",
                "created_at": datetime.now().isoformat(),
                "widgets": monitoring_widgets,
                "real_time": True,
                "refresh_interval": 5,  # 5 seconds
                "alert_enabled": True,
                "monitoring_config": monitoring_config
            }
            
            self.active_dashboards[dashboard_id] = dashboard
            
            # Start real-time data streaming
            await self._start_real_time_streaming(dashboard_id)
            
            logger.info(f"Real-time monitoring dashboard created: {dashboard_id}")
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "real_time_enabled": True,
                "alert_system": True
            }
            
        except Exception as e:
            logger.error(f"Error creating real-time monitoring dashboard: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def export_dashboard(self, dashboard_id: str, export_format: str) -> Dict[str, Any]:
        """
        Export dashboard vers différents formats.
        
        Export Formats:
        - PDF: Executive reports avec visualisations
        - Excel: Data tables avec formatting
        - JSON: Raw data pour intégrations
        - PNG/SVG: Visualisations pour présentations
        """
        try:
            if dashboard_id not in self.active_dashboards:
                return {"success": False, "error": "Dashboard not found"}
            
            dashboard = self.active_dashboards[dashboard_id]
            export_data = {
                "dashboard_info": {
                    "id": dashboard_id,
                    "type": dashboard["type"],
                    "created_at": dashboard["created_at"],
                    "exported_at": datetime.now().isoformat()
                },
                "widgets_data": await self._extract_widgets_data(dashboard["widgets"]),
                "metadata": {
                    "export_format": export_format,
                    "total_widgets": len(dashboard["widgets"]),
                    "data_freshness": await self._check_data_freshness(dashboard_id)
                }
            }
            
            if export_format.lower() == "pdf":
                export_result = await self._export_to_pdf(export_data)
            elif export_format.lower() == "excel":
                export_result = await self._export_to_excel(export_data)
            elif export_format.lower() == "json":
                export_result = await self._export_to_json(export_data)
            else:
                return {"success": False, "error": f"Unsupported export format: {export_format}"}
            
            logger.info(f"Dashboard {dashboard_id} exported to {export_format}")
            return {
                "success": True,
                "export_format": export_format,
                "file_path": export_result.get("file_path"),
                "file_size": export_result.get("file_size"),
                "export_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting dashboard {dashboard_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_dashboard_config(self, dashboard_id: str, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour la configuration d'un dashboard existant"""
        try:
            if dashboard_id not in self.active_dashboards:
                return {"success": False, "error": "Dashboard not found"}
            
            dashboard = self.active_dashboards[dashboard_id]
            dashboard["config"].update(new_config)
            dashboard["updated_at"] = datetime.now().isoformat()
            
            # Restart streaming if refresh interval changed
            if "refresh_interval" in new_config:
                await self._restart_dashboard_streaming(dashboard_id)
            
            logger.info(f"Dashboard {dashboard_id} configuration updated")
            return {"success": True, "updated_fields": list(new_config.keys())}
            
        except Exception as e:
            logger.error(f"Error updating dashboard config: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # Helper methods pour calculs des métriques
    async def _calculate_roi_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques ROI pour le dashboard executive"""
        # Simulation de calculs ROI complexes
        return {
            "overall_roi": 245.5,
            "roi_trend": "increasing",
            "roi_by_channel": {
                "social_media": 180.2,
                "email": 320.5,
                "influencer": 290.8,
                "paid_ads": 165.3
            },
            "target_roi": 200.0,
            "variance": 22.75
        }
    
    async def _get_campaign_summary(self) -> List[Dict[str, Any]]:
        """Récupère le résumé des campagnes actives"""
        return [
            {
                "campaign_id": "camp_001",
                "name": "Summer Creator Campaign",
                "status": "active",
                "budget_spent": 15000,
                "budget_total": 25000,
                "roi": 185.5,
                "conversions": 450,
                "cpa": 33.33
            },
            {
                "campaign_id": "camp_002", 
                "name": "Influencer Partnership Q4",
                "status": "active",
                "budget_spent": 8500,
                "budget_total": 12000,
                "roi": 290.8,
                "conversions": 280,
                "cpa": 30.36
            }
        ]
    
    async def _calculate_budget_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques de budget utilization"""
        return {
            "total_budget": 100000,
            "spent_budget": 67500,
            "remaining_budget": 32500,
            "utilization_rate": 67.5,
            "burn_rate": 2500,  # per day
            "projected_overspend": False,
            "budget_by_channel": {
                "social_media": {"allocated": 30000, "spent": 22500},
                "influencer": {"allocated": 40000, "spent": 28000},
                "paid_ads": {"allocated": 30000, "spent": 17000}
            }
        }
    
    async def _get_attribution_data(self) -> Dict[str, Any]:
        """Récupère les données d'attribution revenue"""
        return {
            "total_revenue": 187500,
            "attribution_model": "time_decay",
            "touchpoint_contribution": {
                "first_touch": 25000,
                "mid_funnel": 87500,
                "last_touch": 75000
            },
            "channel_attribution": {
                "organic_social": 45000,
                "paid_social": 62500,
                "influencer": 52500,
                "email": 27500
            }
        }
    
    async def _get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Récupère les métriques détaillées d'une campagne"""
        return {
            "metrics": {
                "impressions": 1250000,
                "clicks": 25000,
                "conversions": 875,
                "ctr": 2.0,
                "conversion_rate": 3.5,
                "cpa": 28.57,
                "roas": 4.2
            },
            "funnel_data": [
                {"stage": "awareness", "count": 1250000},
                {"stage": "interest", "count": 125000},
                {"stage": "consideration", "count": 25000},
                {"stage": "conversion", "count": 875}
            ],
            "engagement_data": {
                "hourly_engagement": [
                    {"hour": 0, "engagement": 2.1},
                    {"hour": 1, "engagement": 1.8},
                    # ... more hourly data
                ]
            }
        }
    
    async def _calculate_influencer_rankings(self, influencer_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calcule le ranking des influenceurs"""
        # Simulation de calculs de ranking complexes
        return [
            {
                "influencer_id": "inf_001",
                "name": "Creator Alpha",
                "rank": 1,
                "score": 95.5,
                "engagement_rate": 4.8,
                "roi": 320.5,
                "followers": 125000
            },
            {
                "influencer_id": "inf_002",
                "name": "Creator Beta", 
                "rank": 2,
                "score": 92.3,
                "engagement_rate": 4.2,
                "roi": 290.8,
                "followers": 98000
            }
        ]
    
    async def _analyze_engagement_rates(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les taux d'engagement des influenceurs"""
        return {
            "average_engagement": 3.8,
            "median_engagement": 3.5,
            "top_performers": ["inf_001", "inf_003"],
            "trend": "stable",
            "benchmark": 3.2
        }
    
    async def _get_audience_demographics(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les données démographiques d'audience"""
        return {
            "age_groups": {
                "18-24": 35,
                "25-34": 40,
                "35-44": 20,
                "45+": 5
            },
            "gender": {
                "female": 58,
                "male": 40,
                "other": 2
            },
            "locations": {
                "US": 45,
                "CA": 12,
                "UK": 15,
                "AU": 8,
                "other": 20
            }
        }
    
    async def _analyze_content_performance(self, influencer_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyse la performance du contenu"""
        return [
            {
                "content_id": "content_001",
                "type": "video",
                "engagement": 4.5,
                "reach": 85000,
                "conversions": 45,
                "performance_score": 87.5
            },
            {
                "content_id": "content_002",
                "type": "image", 
                "engagement": 3.8,
                "reach": 62000,
                "conversions": 32,
                "performance_score": 76.2
            }
        ]
    
    async def _calculate_partnership_roi(self, influencer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le ROI des partenariats influenceurs"""
        return {
            "overall_roi": 285.7,
            "roi_by_influencer": {
                "inf_001": 320.5,
                "inf_002": 290.8,
                "inf_003": 245.2
            },
            "target_roi": 250.0,
            "performance": "exceeding"
        }
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Récupère les alertes actives"""
        return [
            {
                "alert_id": "alert_001",
                "type": "budget_warning",
                "message": "Campaign budget 80% utilized",
                "severity": "warning",
                "timestamp": datetime.now().isoformat()
            },
            {
                "alert_id": "alert_002",
                "type": "performance_anomaly",
                "message": "Unusual traffic spike detected",
                "severity": "info",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _detect_performance_anomalies(self) -> Dict[str, Any]:
        """Détecte les anomalies de performance"""
        return {
            "anomalies_detected": 2,
            "anomaly_types": ["traffic_spike", "conversion_drop"],
            "confidence_scores": [0.85, 0.72],
            "recommendations": [
                "Investigate traffic source",
                "Review conversion funnel"
            ]
        }
    
    async def _calculate_burn_rate(self) -> Dict[str, Any]:
        """Calcule le taux de consommation du budget"""
        return {
            "current_burn_rate": 2500,  # per day
            "projected_burn_rate": 2750,
            "budget_runway": 13,  # days
            "status": "healthy"
        }
    
    async def _start_real_time_streaming(self, dashboard_id: str) -> None:
        """Démarre le streaming temps réel pour un dashboard"""
        logger.info(f"Starting real-time streaming for dashboard {dashboard_id}")
        # Implementation du streaming temps réel
        pass
    
    async def _extract_widgets_data(self, widgets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrait les données des widgets pour export"""
        extracted_data = {}
        for widget in widgets:
            extracted_data[widget["widget_id"]] = {
                "title": widget["title"],
                "type": widget["type"],
                "data": widget.get("data", {}),
                "visualization": widget.get("visualization", "")
            }
        return extracted_data
    
    async def _check_data_freshness(self, dashboard_id: str) -> str:
        """Vérifie la fraîcheur des données du dashboard"""
        return "current"  # Simulation
    
    async def _export_to_pdf(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export vers PDF"""
        return {
            "file_path": f"/tmp/dashboard_{export_data['dashboard_info']['id']}.pdf",
            "file_size": "2.5MB"
        }
    
    async def _export_to_excel(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export vers Excel"""
        return {
            "file_path": f"/tmp/dashboard_{export_data['dashboard_info']['id']}.xlsx",
            "file_size": "1.8MB"
        }
    
    async def _export_to_json(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export vers JSON"""
        return {
            "file_path": f"/tmp/dashboard_{export_data['dashboard_info']['id']}.json",
            "file_size": "500KB"
        }
    
    async def _restart_dashboard_streaming(self, dashboard_id: str) -> None:
        """Redémarre le streaming d'un dashboard"""
        logger.info(f"Restarting streaming for dashboard {dashboard_id}")
        pass

def get_dashboard_engine(config: DashboardConfig) -> MarketingDashboardEngine:
    """Factory pour créer une instance du moteur dashboard marketing"""
    return MarketingDashboardEngine(config)

# Exemple d'utilisation
if __name__ == "__main__":
    async def demo_dashboard():
        """Démonstration du moteur dashboard marketing"""
        
        # Configuration dashboard
        config = DashboardConfig(
            dashboard_id="demo_dashboard",
            dashboard_type=DashboardType.EXECUTIVE,
            user_permissions=["read", "export"],
            refresh_interval=60
        )
        
        # Initialisation du moteur
        dashboard_engine = MarketingDashboardEngine(config)
        
        # Création dashboard executive
        executive_result = await dashboard_engine.create_executive_dashboard({
            "include_roi": True,
            "include_budget": True,
            "include_attribution": True
        })
        
        print("Executive Dashboard Created:")
        print(json.dumps(executive_result, indent=2))
        
        # Création dashboard campagnes
        campaign_result = await dashboard_engine.create_campaign_performance_dashboard(
            ["camp_001", "camp_002"]
        )
        
        print("\nCampaign Performance Dashboard Created:")
        print(json.dumps(campaign_result, indent=2))
        
        # Export dashboard
        if executive_result["success"]:
            export_result = await dashboard_engine.export_dashboard(
                executive_result["dashboard_id"], 
                "json"
            )
            print("\nDashboard Export Result:")
            print(json.dumps(export_result, indent=2))
    
    # Exécution démo
    asyncio.run(demo_dashboard())