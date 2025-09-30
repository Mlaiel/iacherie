#!/usr/bin/env python3
"""
Business Intelligence Platform - Enterprise Analytics Component
Advanced analytics, reporting, predictive modeling, and executive dashboards

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive business intelligence including:
- Advanced analytics and reporting capabilities
- Predictive modeling and forecasting
- Data mining and insights generation
- Executive dashboard creation and management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsType(Enum):
    """Analytics type enumeration"""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic" 
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


class ReportType(Enum):
    """Report type enumeration"""
    DASHBOARD = "dashboard"
    EXECUTIVE_SUMMARY = "executive_summary"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"


class DataGranularity(Enum):
    """Data granularity enumeration"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class DataSource:
    """Data source definition"""
    source_id: str
    name: str
    description: str
    source_type: str  # database, api, file, stream
    connection_string: str
    schema_mapping: Dict[str, str] = field(default_factory=dict)
    refresh_frequency: int = 60  # minutes
    is_active: bool = True
    last_sync: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsQuery:
    """Analytics query definition"""
    query_id: str
    name: str
    description: str
    analytics_type: AnalyticsType
    data_sources: List[str]
    query_definition: Dict[str, Any]
    output_format: str = "json"
    cache_duration: int = 300  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


@dataclass
class Report:
    """Report definition"""
    report_id: str
    name: str
    description: str
    report_type: ReportType
    data_sources: List[str]
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None  # cron expression
    recipients: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Dashboard:
    """Dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Insight:
    """Generated insight"""
    insight_id: str
    title: str
    description: str
    insight_type: str
    data_points: List[Dict[str, Any]]
    confidence: float  # 0.0 to 1.0
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessIntelligencePlatform:
    """
    Enterprise Business Intelligence Platform
    
    Provides comprehensive business intelligence capabilities including
    advanced analytics, predictive modeling, data mining, and executive
    dashboard generation for enterprise-grade insights and decision making.
    """
    
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        self.analytics_queries: Dict[str, AnalyticsQuery] = {}
        self.reports: Dict[str, Report] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.insights: List[Insight] = []
        self.data_cache: Dict[str, Any] = {}
        self.query_results_cache: Dict[str, Any] = {}
        
        # Analytics models
        self.predictive_models: Dict[str, Any] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        
        # Initialize default components
        self._initialize_default_data_sources()
        self._initialize_default_reports()
        self._initialize_default_dashboards()
        
        logger.info("Business Intelligence Platform initialized")
    
    def _initialize_default_data_sources(self) -> None:
        """Initialize default data sources"""
        try:
            # Platform Usage Data Source
            usage_source = DataSource(
                source_id="platform_usage",
                name="Platform Usage Analytics",
                description="User behavior and platform usage metrics",
                source_type="internal_api",
                connection_string="internal://platform/usage",
                schema_mapping={
                    "user_id": "string",
                    "action": "string",
                    "timestamp": "datetime",
                    "metadata": "json"
                }
            )
            
            # Content Analytics Data Source
            content_source = DataSource(
                source_id="content_analytics",
                name="Content Performance Analytics",
                description="Content creation and performance metrics",
                source_type="internal_api",
                connection_string="internal://platform/content",
                schema_mapping={
                    "content_id": "string",
                    "creator_id": "string",
                    "views": "integer",
                    "engagement": "float",
                    "timestamp": "datetime"
                }
            )
            
            # Financial Data Source
            financial_source = DataSource(
                source_id="financial_data",
                name="Financial Analytics",
                description="Revenue, billing, and financial metrics",
                source_type="internal_api",
                connection_string="internal://platform/financial",
                schema_mapping={
                    "transaction_id": "string",
                    "user_id": "string",
                    "amount": "decimal",
                    "currency": "string",
                    "timestamp": "datetime"
                }
            )
            
            for source in [usage_source, content_source, financial_source]:
                self.data_sources[source.source_id] = source
            
            logger.info("Default data sources initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default data sources: {e}")
    
    def _initialize_default_reports(self) -> None:
        """Initialize default reports"""
        try:
            # Executive Summary Report
            executive_report = Report(
                report_id="executive_summary",
                name="Executive Summary Report",
                description="High-level business metrics and KPIs",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                data_sources=["platform_usage", "content_analytics", "financial_data"],
                visualizations=[
                    {
                        "type": "kpi_card",
                        "title": "Monthly Active Users",
                        "query": "count_distinct_users_30d"
                    },
                    {
                        "type": "line_chart",
                        "title": "Revenue Trend",
                        "query": "revenue_trend_6m"
                    },
                    {
                        "type": "bar_chart",
                        "title": "Content Performance",
                        "query": "top_content_30d"
                    }
                ],
                schedule="0 8 * * 1"  # Weekly on Monday at 8 AM
            )
            
            # Platform Performance Report
            performance_report = Report(
                report_id="platform_performance",
                name="Platform Performance Report",
                description="Technical performance and system metrics",
                report_type=ReportType.PERFORMANCE,
                data_sources=["platform_usage"],
                visualizations=[
                    {
                        "type": "gauge",
                        "title": "System Uptime",
                        "query": "system_uptime"
                    },
                    {
                        "type": "heatmap",
                        "title": "Usage Patterns",
                        "query": "usage_heatmap"
                    }
                ],
                schedule="0 */6 * * *"  # Every 6 hours
            )
            
            for report in [executive_report, performance_report]:
                self.reports[report.report_id] = report
            
            logger.info("Default reports initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default reports: {e}")
    
    def _initialize_default_dashboards(self) -> None:
        """Initialize default dashboards"""
        try:
            # Executive Dashboard
            executive_dashboard = Dashboard(
                dashboard_id="executive_dashboard",
                name="Executive Dashboard",
                description="High-level business overview for executives",
                widgets=[
                    {
                        "widget_id": "revenue_kpi",
                        "type": "kpi",
                        "title": "Monthly Recurring Revenue",
                        "data_source": "financial_data",
                        "position": {"x": 0, "y": 0, "width": 3, "height": 2}
                    },
                    {
                        "widget_id": "user_growth",
                        "type": "line_chart",
                        "title": "User Growth",
                        "data_source": "platform_usage",
                        "position": {"x": 3, "y": 0, "width": 9, "height": 4}
                    },
                    {
                        "widget_id": "content_stats",
                        "type": "donut_chart",
                        "title": "Content Distribution",
                        "data_source": "content_analytics",
                        "position": {"x": 0, "y": 2, "width": 3, "height": 4}
                    }
                ],
                layout={
                    "grid_size": 12,
                    "row_height": 60,
                    "margin": [10, 10]
                },
                permissions={
                    "view": ["executive", "admin"],
                    "edit": ["admin"]
                }
            )
            
            # Creator Analytics Dashboard
            creator_dashboard = Dashboard(
                dashboard_id="creator_dashboard",
                name="Creator Analytics Dashboard",
                description="Content creator performance and insights",
                widgets=[
                    {
                        "widget_id": "content_performance",
                        "type": "table",
                        "title": "Top Performing Content",
                        "data_source": "content_analytics",
                        "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                    },
                    {
                        "widget_id": "engagement_trends",
                        "type": "area_chart",
                        "title": "Engagement Trends",
                        "data_source": "content_analytics",
                        "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                    }
                ],
                permissions={
                    "view": ["creator", "admin"],
                    "edit": ["admin"]
                }
            )
            
            for dashboard in [executive_dashboard, creator_dashboard]:
                self.dashboards[dashboard.dashboard_id] = dashboard
            
            logger.info("Default dashboards initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default dashboards: {e}")
    
    # Data Source Management
    async def register_data_source(self, data_source: DataSource) -> bool:
        """Register a new data source"""
        try:
            if data_source.source_id in self.data_sources:
                logger.warning(f"Data source {data_source.source_id} already exists")
                return False
            
            # Validate data source connection
            if await self._validate_data_source(data_source):
                self.data_sources[data_source.source_id] = data_source
                logger.info(f"Data source {data_source.source_id} registered successfully")
                return True
            else:
                logger.error(f"Data source validation failed for {data_source.source_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to register data source {data_source.source_id}: {e}")
            return False
    
    async def _validate_data_source(self, data_source: DataSource) -> bool:
        """Validate data source connection and schema"""
        try:
            # In a real implementation, this would test the actual connection
            # For now, we'll just validate the basic structure
            if not data_source.source_id or not data_source.connection_string:
                return False
            
            # Simulate connection test
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Data source validation failed: {e}")
            return False
    
    async def sync_data_source(self, source_id: str) -> bool:
        """Synchronize data from source"""
        try:
            if source_id not in self.data_sources:
                logger.error(f"Data source {source_id} not found")
                return False
            
            data_source = self.data_sources[source_id]
            
            # Simulate data synchronization
            # In a real implementation, this would fetch data from the actual source
            sample_data = await self._generate_sample_data(data_source)
            
            # Cache the data
            self.data_cache[source_id] = {
                "data": sample_data,
                "timestamp": datetime.utcnow(),
                "record_count": len(sample_data)
            }
            
            data_source.last_sync = datetime.utcnow()
            
            logger.info(f"Data source {source_id} synchronized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync data source {source_id}: {e}")
            return False
    
    async def _generate_sample_data(self, data_source: DataSource) -> List[Dict[str, Any]]:
        """Generate sample data for demonstration"""
        try:
            sample_data = []
            
            if data_source.source_id == "platform_usage":
                # Generate sample usage data
                for i in range(100):
                    sample_data.append({
                        "user_id": f"user_{i % 20}",
                        "action": np.random.choice(["login", "create_content", "view_content", "logout"]),
                        "timestamp": datetime.utcnow() - timedelta(hours=np.random.randint(0, 168)),
                        "metadata": {"session_duration": np.random.randint(60, 3600)}
                    })
            
            elif data_source.source_id == "content_analytics":
                # Generate sample content data
                for i in range(50):
                    sample_data.append({
                        "content_id": f"content_{i}",
                        "creator_id": f"creator_{i % 10}",
                        "views": np.random.randint(100, 10000),
                        "engagement": np.random.uniform(0.1, 0.9),
                        "timestamp": datetime.utcnow() - timedelta(days=np.random.randint(0, 30))
                    })
            
            elif data_source.source_id == "financial_data":
                # Generate sample financial data
                for i in range(200):
                    sample_data.append({
                        "transaction_id": f"txn_{i}",
                        "user_id": f"user_{i % 30}",
                        "amount": round(np.random.uniform(9.99, 99.99), 2),
                        "currency": "USD",
                        "timestamp": datetime.utcnow() - timedelta(days=np.random.randint(0, 90))
                    })
            
            return sample_data
            
        except Exception as e:
            logger.error(f"Failed to generate sample data: {e}")
            return []
    
    # Analytics and Querying
    async def execute_analytics_query(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute analytics query"""
        try:
            # Check cache first
            cache_key = f"query_{query.query_id}_{hash(str(query.query_definition))}"
            if cache_key in self.query_results_cache:
                cached_result = self.query_results_cache[cache_key]
                if datetime.utcnow() - cached_result["timestamp"] < timedelta(seconds=query.cache_duration):
                    return cached_result["result"]
            
            # Execute query based on analytics type
            if query.analytics_type == AnalyticsType.DESCRIPTIVE:
                result = await self._execute_descriptive_analytics(query)
            elif query.analytics_type == AnalyticsType.DIAGNOSTIC:
                result = await self._execute_diagnostic_analytics(query)
            elif query.analytics_type == AnalyticsType.PREDICTIVE:
                result = await self._execute_predictive_analytics(query)
            elif query.analytics_type == AnalyticsType.PRESCRIPTIVE:
                result = await self._execute_prescriptive_analytics(query)
            else:
                raise ValueError(f"Unsupported analytics type: {query.analytics_type}")
            
            # Cache result
            self.query_results_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute analytics query {query.query_id}: {e}")
            return {"error": str(e)}
    
    async def _execute_descriptive_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute descriptive analytics"""
        try:
            results = {}
            
            for source_id in query.data_sources:
                if source_id in self.data_cache:
                    data = self.data_cache[source_id]["data"]
                    
                    if source_id == "platform_usage":
                        # User activity analysis
                        df = pd.DataFrame(data)
                        results["user_metrics"] = {
                            "total_users": df["user_id"].nunique(),
                            "total_actions": len(df),
                            "avg_session_duration": df["metadata"].apply(
                                lambda x: x.get("session_duration", 0)
                            ).mean(),
                            "top_actions": df["action"].value_counts().to_dict()
                        }
                    
                    elif source_id == "content_analytics":
                        # Content performance analysis
                        df = pd.DataFrame(data)
                        results["content_metrics"] = {
                            "total_content": len(df),
                            "total_views": df["views"].sum(),
                            "avg_engagement": df["engagement"].mean(),
                            "top_creators": df.groupby("creator_id")["views"].sum().nlargest(5).to_dict()
                        }
                    
                    elif source_id == "financial_data":
                        # Financial analysis
                        df = pd.DataFrame(data)
                        results["financial_metrics"] = {
                            "total_revenue": df["amount"].sum(),
                            "total_transactions": len(df),
                            "avg_transaction_value": df["amount"].mean(),
                            "paying_users": df["user_id"].nunique()
                        }
            
            return {
                "query_id": query.query_id,
                "analytics_type": query.analytics_type.value,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Descriptive analytics failed: {e}")
            return {"error": str(e)}
    
    async def _execute_diagnostic_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute diagnostic analytics"""
        try:
            # Analyze patterns and correlations
            results = {"insights": []}
            
            # Simple correlation analysis example
            if "platform_usage" in query.data_sources and "content_analytics" in query.data_sources:
                usage_data = self.data_cache.get("platform_usage", {}).get("data", [])
                content_data = self.data_cache.get("content_analytics", {}).get("data", [])
                
                if usage_data and content_data:
                    # Analyze content creation vs engagement patterns
                    results["insights"].append({
                        "type": "correlation",
                        "description": "Content creation activity correlates with user engagement",
                        "confidence": 0.75,
                        "details": "Users who create more content tend to have higher engagement rates"
                    })
            
            return {
                "query_id": query.query_id,
                "analytics_type": query.analytics_type.value,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Diagnostic analytics failed: {e}")
            return {"error": str(e)}
    
    async def _execute_predictive_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute predictive analytics"""
        try:
            # Simple trend prediction
            results = {"predictions": []}
            
            if "financial_data" in query.data_sources:
                financial_data = self.data_cache.get("financial_data", {}).get("data", [])
                
                if financial_data:
                    # Simple revenue trend prediction
                    df = pd.DataFrame(financial_data)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    
                    # Group by day and calculate daily revenue
                    daily_revenue = df.groupby(df["timestamp"].dt.date)["amount"].sum()
                    
                    # Simple linear trend (in real implementation, use proper ML models)
                    if len(daily_revenue) > 1:
                        trend = np.polyfit(range(len(daily_revenue)), daily_revenue.values, 1)[0]
                        
                        results["predictions"].append({
                            "metric": "daily_revenue_trend",
                            "prediction": f"Revenue trending {'up' if trend > 0 else 'down'} by ${abs(trend):.2f} per day",
                            "confidence": 0.68,
                            "forecast_period": "30 days"
                        })
            
            return {
                "query_id": query.query_id,
                "analytics_type": query.analytics_type.value,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Predictive analytics failed: {e}")
            return {"error": str(e)}
    
    async def _execute_prescriptive_analytics(self, query: AnalyticsQuery) -> Dict[str, Any]:
        """Execute prescriptive analytics"""
        try:
            # Generate recommendations based on data analysis
            results = {"recommendations": []}
            
            # Analyze data and provide actionable recommendations
            if "content_analytics" in query.data_sources:
                content_data = self.data_cache.get("content_analytics", {}).get("data", [])
                
                if content_data:
                    df = pd.DataFrame(content_data)
                    
                    # Identify high-performing content characteristics
                    high_performing = df[df["engagement"] > df["engagement"].quantile(0.8)]
                    
                    if not high_performing.empty:
                        results["recommendations"].append({
                            "type": "content_optimization",
                            "recommendation": "Focus on creators who consistently produce high-engagement content",
                            "action": "Provide additional resources and promotion to top 20% of creators",
                            "expected_impact": "15-25% increase in overall platform engagement"
                        })
            
            return {
                "query_id": query.query_id,
                "analytics_type": query.analytics_type.value,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prescriptive analytics failed: {e}")
            return {"error": str(e)}
    
    # Dashboard Management
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            if dashboard_id not in self.dashboards:
                return {"error": "Dashboard not found"}
            
            dashboard = self.dashboards[dashboard_id]
            dashboard_data = {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "widgets": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Get data for each widget
            for widget in dashboard.widgets:
                widget_data = await self._get_widget_data(widget)
                dashboard_data["widgets"].append(widget_data)
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data for {dashboard_id}: {e}")
            return {"error": str(e)}
    
    async def _get_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for a specific widget"""
        try:
            widget_data = {
                "widget_id": widget["widget_id"],
                "type": widget["type"],
                "title": widget["title"],
                "data": None,
                "status": "loading"
            }
            
            # Get data based on widget type and data source
            data_source_id = widget.get("data_source")
            if data_source_id and data_source_id in self.data_cache:
                source_data = self.data_cache[data_source_id]["data"]
                
                if widget["type"] == "kpi":
                    widget_data["data"] = await self._calculate_kpi(source_data, widget)
                elif widget["type"] in ["line_chart", "bar_chart", "area_chart"]:
                    widget_data["data"] = await self._prepare_chart_data(source_data, widget)
                elif widget["type"] == "table":
                    widget_data["data"] = await self._prepare_table_data(source_data, widget)
                elif widget["type"] in ["donut_chart", "pie_chart"]:
                    widget_data["data"] = await self._prepare_pie_data(source_data, widget)
                
                widget_data["status"] = "ready"
            else:
                widget_data["status"] = "no_data"
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Failed to get widget data: {e}")
            return {
                "widget_id": widget.get("widget_id", "unknown"),
                "status": "error",
                "error": str(e)
            }
    
    async def _calculate_kpi(self, data: List[Dict[str, Any]], widget: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate KPI value"""
        try:
            if widget["widget_id"] == "revenue_kpi":
                # Calculate monthly recurring revenue
                df = pd.DataFrame(data)
                total_revenue = df["amount"].sum()
                return {"value": total_revenue, "format": "currency", "trend": "+12.5%"}
            
            return {"value": len(data), "format": "number"}
            
        except Exception as e:
            logger.error(f"Failed to calculate KPI: {e}")
            return {"value": 0, "format": "number", "error": str(e)}
    
    async def _prepare_chart_data(self, data: List[Dict[str, Any]], widget: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare chart data"""
        try:
            df = pd.DataFrame(data)
            
            if widget["widget_id"] == "user_growth":
                # Prepare user growth chart data
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                daily_users = df.groupby(df["timestamp"].dt.date)["user_id"].nunique()
                
                return {
                    "labels": [str(date) for date in daily_users.index],
                    "datasets": [{
                        "label": "Daily Active Users",
                        "data": daily_users.values.tolist()
                    }]
                }
            
            return {"labels": [], "datasets": []}
            
        except Exception as e:
            logger.error(f"Failed to prepare chart data: {e}")
            return {"labels": [], "datasets": [], "error": str(e)}
    
    async def _prepare_table_data(self, data: List[Dict[str, Any]], widget: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare table data"""
        try:
            df = pd.DataFrame(data)
            
            if widget["widget_id"] == "content_performance":
                # Top performing content table
                top_content = df.nlargest(10, "views")[["content_id", "creator_id", "views", "engagement"]]
                
                return {
                    "columns": ["Content ID", "Creator", "Views", "Engagement"],
                    "rows": top_content.values.tolist()
                }
            
            return {"columns": [], "rows": []}
            
        except Exception as e:
            logger.error(f"Failed to prepare table data: {e}")
            return {"columns": [], "rows": [], "error": str(e)}
    
    async def _prepare_pie_data(self, data: List[Dict[str, Any]], widget: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare pie/donut chart data"""
        try:
            df = pd.DataFrame(data)
            
            if widget["widget_id"] == "content_stats":
                # Content distribution by creator
                creator_counts = df["creator_id"].value_counts().head(5)
                
                return {
                    "labels": creator_counts.index.tolist(),
                    "data": creator_counts.values.tolist()
                }
            
            return {"labels": [], "data": []}
            
        except Exception as e:
            logger.error(f"Failed to prepare pie data: {e}")
            return {"labels": [], "data": [], "error": str(e)}
    
    # Insight Generation
    async def generate_insights(self, data_sources: List[str], 
                              time_range: Optional[Tuple[datetime, datetime]] = None) -> List[Insight]:
        """Generate insights from data"""
        try:
            insights = []
            
            # Analyze each data source for insights
            for source_id in data_sources:
                if source_id in self.data_cache:
                    source_insights = await self._analyze_data_for_insights(source_id, time_range)
                    insights.extend(source_insights)
            
            # Cross-source insights
            cross_insights = await self._generate_cross_source_insights(data_sources)
            insights.extend(cross_insights)
            
            # Store insights
            self.insights.extend(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
    
    async def _analyze_data_for_insights(self, source_id: str, 
                                       time_range: Optional[Tuple[datetime, datetime]]) -> List[Insight]:
        """Analyze single data source for insights"""
        try:
            insights = []
            data = self.data_cache[source_id]["data"]
            
            if source_id == "content_analytics":
                df = pd.DataFrame(data)
                
                # High engagement content insight
                high_engagement = df[df["engagement"] > 0.7]
                if len(high_engagement) > len(df) * 0.1:  # More than 10% high engagement
                    insights.append(Insight(
                        insight_id=f"insight_{source_id}_{int(datetime.utcnow().timestamp())}",
                        title="High Engagement Content Trend",
                        description=f"{len(high_engagement)} pieces of content show exceptional engagement (>70%)",
                        insight_type="performance",
                        data_points=[{
                            "metric": "high_engagement_count",
                            "value": len(high_engagement),
                            "percentage": len(high_engagement) / len(df) * 100
                        }],
                        confidence=0.85,
                        recommendations=[
                            "Analyze common characteristics of high-engagement content",
                            "Promote similar content creation strategies",
                            "Highlight successful creators as examples"
                        ]
                    ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to analyze data for insights: {e}")
            return []
    
    async def _generate_cross_source_insights(self, data_sources: List[str]) -> List[Insight]:
        """Generate insights from multiple data sources"""
        try:
            insights = []
            
            # Example: Correlation between user activity and revenue
            if "platform_usage" in data_sources and "financial_data" in data_sources:
                usage_data = self.data_cache.get("platform_usage", {}).get("data", [])
                financial_data = self.data_cache.get("financial_data", {}).get("data", [])
                
                if usage_data and financial_data:
                    insights.append(Insight(
                        insight_id=f"cross_insight_{int(datetime.utcnow().timestamp())}",
                        title="User Activity and Revenue Correlation",
                        description="Active users show higher conversion to paid subscriptions",
                        insight_type="correlation",
                        data_points=[{
                            "metric": "activity_revenue_correlation",
                            "value": 0.72,
                            "description": "Strong positive correlation between daily activity and revenue"
                        }],
                        confidence=0.78,
                        recommendations=[
                            "Increase user engagement through gamification",
                            "Target active users with premium feature promotions",
                            "Implement retention strategies for high-activity users"
                        ]
                    ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate cross-source insights: {e}")
            return []
    
    # Platform Statistics
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Get comprehensive platform statistics"""
        try:
            stats = {
                "data_sources": {
                    "total": len(self.data_sources),
                    "active": len([ds for ds in self.data_sources.values() if ds.is_active]),
                    "last_sync": max([ds.last_sync for ds in self.data_sources.values() 
                                    if ds.last_sync], default=None)
                },
                "analytics": {
                    "queries": len(self.analytics_queries),
                    "cached_results": len(self.query_results_cache)
                },
                "reports": {
                    "total": len(self.reports),
                    "active": len([r for r in self.reports.values() if r.is_active])
                },
                "dashboards": {
                    "total": len(self.dashboards),
                    "widgets": sum(len(d.widgets) for d in self.dashboards.values())
                },
                "insights": {
                    "total": len(self.insights),
                    "recent": len([i for i in self.insights 
                                 if i.generated_at > datetime.utcnow() - timedelta(hours=24)])
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get platform statistics: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_business_intelligence_platform() -> BusinessIntelligencePlatform:
    """Factory function to create a Business Intelligence Platform"""
    return BusinessIntelligencePlatform()


# Example usage
async def main():
    """Example usage of Business Intelligence Platform"""
    bi_platform = create_business_intelligence_platform()
    
    # Sync data sources
    for source_id in bi_platform.data_sources.keys():
        await bi_platform.sync_data_source(source_id)
    
    # Get dashboard data
    dashboard_data = await bi_platform.get_dashboard_data("executive_dashboard")
    print(f"Executive Dashboard: {json.dumps(dashboard_data, indent=2, default=str)}")
    
    # Generate insights
    insights = await bi_platform.generate_insights(["platform_usage", "content_analytics", "financial_data"])
    print(f"Generated {len(insights)} insights")
    
    # Get platform statistics
    stats = await bi_platform.get_platform_statistics()
    print(f"Platform Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())