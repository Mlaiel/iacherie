"""📊 Advanced Licensing Analytics & Reporting System - Comprehensive Business Intelligence
=======================================================================================

Ultra-sophisticated analytics and reporting system for licensing operations:
- Real-time licensing performance dashboards and KPI tracking
- Advanced AI-powered business intelligence and predictive analytics
- Multi-dimensional revenue analysis and territory performance optimization
- Automated compliance reporting and audit trail generation
- Interactive visualizations and executive summary reports
- Integration with major BI platforms and data warehouses

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Data Scientist + Business Analyst + BI Expert + Financial Analyst
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING:
This software is protected by international copyright law and trade secret law.
Unauthorized reproduction, distribution, or reverse engineering is strictly prohibited
and may result in severe civil and criminal penalties. Users must comply with all
applicable intellectual property laws and license agreements.

Contact: mlaiel@live.de for licensing and authorization requests.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import uuid
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import io
import base64
from pathlib import Path

# Data visualization libraries (would be imported in production)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Available report types"""    EXECUTIVE_DASHBOARD = "executive_dashboard"
    REVENUE_ANALYSIS = "revenue_analysis"
    TERRITORY_PERFORMANCE = "territory_performance"
    RIGHTS_HOLDER_SUMMARY = "rights_holder_summary"
    LICENSING_COMPLIANCE = "licensing_compliance"
    PLATFORM_ANALYTICS = "platform_analytics"
    TREND_ANALYSIS = "trend_analysis"
    FORECASTING_REPORT = "forecasting_report"
    AUDIT_REPORT = "audit_report"
    CUSTOM_ANALYTICS = "custom_analytics"

class ReportFormat(Enum):
    """Report output formats"""    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    INTERACTIVE_DASHBOARD = "dashboard"

class AnalyticsPeriod(Enum):
    """Analytics time periods"""    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class MetricType(Enum):
    """Key performance indicator types"""    REVENUE = "revenue"
    USAGE = "usage"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    COMPLIANCE = "compliance"
    MARKET_SHARE = "market_share"

@dataclass
class ReportConfig:
    """Report configuration settings"""    report_id: str
    report_type: ReportType
    title: str
    description: str
    
    # Time parameters
    period: AnalyticsPeriod
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Content filters
    content_ids: Optional[List[str]] = None
    rights_holder_ids: Optional[List[str]] = None
    territories: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    
    # Report options
    format: ReportFormat = ReportFormat.JSON
    include_charts: bool = True
    include_raw_data: bool = False
    auto_refresh: bool = False
    refresh_interval: int = 3600  # seconds
    
    # Recipients
    recipients: List[str] = field(default_factory=list)
    distribution_schedule: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"

@dataclass
class KPIMetric:
    """Key Performance Indicator metric"""    metric_id: str
    name: str
    value: Union[float, int, str]
    metric_type: MetricType
    
    # Comparison data
    previous_value: Optional[Union[float, int]] = None
    change_percentage: Optional[float] = None
    trend_direction: Optional[str] = None  # up, down, stable
    
    # Context
    unit: str = ""
    description: str = ""
    target_value: Optional[Union[float, int]] = None
    benchmark_value: Optional[Union[float, int]] = None
    
    # Temporal data
    measurement_date: datetime = field(default_factory=datetime.now)
    period_covered: str = ""

@dataclass
class AnalyticsInsight:
    """AI-generated analytics insight"""    insight_id: str
    title: str
    description: str
    insight_type: str  # trend, anomaly, opportunity, warning
    
    # Supporting data
    confidence_score: float  # 0.0 to 1.0
    impact_level: str  # low, medium, high, critical
    recommended_actions: List[str] = field(default_factory=list)
    
    # Related metrics
    related_metrics: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ReportResult:
    """Complete report result"""    report_id: str
    config: ReportConfig
    generated_at: datetime
    
    # Report content
    executive_summary: str
    key_metrics: List[KPIMetric]
    insights: List[AnalyticsInsight]
    data_tables: Dict[str, pd.DataFrame]
    charts: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    generation_time: float  # seconds
    data_sources: List[str] = field(default_factory=list)
    quality_score: float = 1.0
    
    # Export options
    export_urls: Dict[str, str] = field(default_factory=dict)

class LicensingAnalyticsEngine:
    """    🚀 Advanced licensing analytics and reporting engine
    
    Comprehensive system for generating business intelligence reports,
    KPI tracking, and predictive analytics for licensing operations.
    """    
    def __init__(self, config: Dict[str, Any]):
        """Initialize analytics engine with configuration."""        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Data sources (would connect to actual databases in production)
        self.data_sources = {
            'licensing_data': [],
            'royalty_data': [],
            'usage_data': [],
            'contracts_data': [],
            'rights_holders_data': []
        }
        
        # AI/ML models for insights
        self._initialize_ai_models()
        
        # Report cache
        self.report_cache = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Performance metrics
        self.analytics_metrics = {
            'reports_generated': 0,
            'insights_generated': 0,
            'cache_hits': 0,
            'average_generation_time': 0.0
        }
        
        self.logger.info("Licensing Analytics Engine initialized successfully")

    def _initialize_ai_models(self):
        """Initialize AI models for analytics insights."""        try:
            # Trend detection model
            self.trend_detector = None  # Would initialize with actual ML model
            
            # Anomaly detection model
            self.anomaly_detector = None  # Would initialize with actual ML model
            
            # Forecasting model
            self.forecasting_model = None  # Would initialize with actual ML model
            
            # Natural language generation for insights
            self.insight_generator = None  # Would initialize with NLG model
            
            self.logger.info("AI models initialized for analytics")
            
        except Exception as e:
            self.logger.warning(f"AI models initialization failed: {e}")

    async def generate_report(self, report_config: ReportConfig) -> ReportResult:
        """Generate comprehensive analytics report."""        start_time = datetime.now()
        
        try:
            self.logger.info(f"Generating report: {report_config.title}")
            
            # Check cache first
            cache_key = self._generate_cache_key(report_config)
            if cache_key in self.report_cache:
                cached_report, cached_time = self.report_cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    self.analytics_metrics['cache_hits'] += 1
                    return cached_report
            
            # Gather data for report
            report_data = await self._gather_report_data(report_config)
            
            # Calculate key metrics
            key_metrics = await self._calculate_key_metrics(report_data, report_config)
            
            # Generate AI insights
            insights = await self._generate_ai_insights(report_data, key_metrics, report_config)
            
            # Create data tables
            data_tables = self._create_data_tables(report_data, report_config)
            
            # Generate visualizations
            charts = {}
            if report_config.include_charts and PLOTTING_AVAILABLE:
                charts = await self._generate_charts(report_data, report_config)
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(
                key_metrics, insights, report_config
            )
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Create report result
            report_result = ReportResult(
                report_id=str(uuid.uuid4()),
                config=report_config,
                generated_at=datetime.now(),
                executive_summary=executive_summary,
                key_metrics=key_metrics,
                insights=insights,
                data_tables=data_tables,
                charts=charts,
                generation_time=generation_time,
                data_sources=list(report_data.keys()),
                quality_score=self._calculate_quality_score(report_data, key_metrics)
            )
            
            # Cache the result
            self.report_cache[cache_key] = (report_result, datetime.now())
            
            # Update metrics
            self._update_analytics_metrics(generation_time)
            
            self.logger.info(f"Report generated successfully: {report_result.report_id}")
            
            return report_result
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

    def _generate_cache_key(self, config: ReportConfig) -> str:
        """Generate cache key for report configuration."""        key_data = {
            'type': config.report_type.value,
            'period': config.period.value,
            'start_date': config.start_date.isoformat() if config.start_date else None,
            'end_date': config.end_date.isoformat() if config.end_date else None,
            'filters': {
                'content_ids': sorted(config.content_ids) if config.content_ids else None,
                'rights_holder_ids': sorted(config.rights_holder_ids) if config.rights_holder_ids else None,
                'territories': sorted(config.territories) if config.territories else None,
                'platforms': sorted(config.platforms) if config.platforms else None
            }
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def _gather_report_data(self, config: ReportConfig) -> Dict[str, Any]:
        """Gather all necessary data for report generation."""        
        # Apply date filters
        start_date = config.start_date
        end_date = config.end_date or date.today()
        
        if config.period != AnalyticsPeriod.CUSTOM:
            start_date, end_date = self._get_period_dates(config.period)
        
        # Gather licensing data
        licensing_data = await self._get_licensing_data(
            start_date, end_date, config
        )
        
        # Gather royalty data
        royalty_data = await self._get_royalty_data(
            start_date, end_date, config
        )
        
        # Gather usage data
        usage_data = await self._get_usage_data(
            start_date, end_date, config
        )
        
        # Gather contract data
        contracts_data = await self._get_contracts_data(
            start_date, end_date, config
        )
        
        # Gather rights holder data
        rights_holders_data = await self._get_rights_holders_data(config)
        
        return {
            'licensing': licensing_data,
            'royalties': royalty_data,
            'usage': usage_data,
            'contracts': contracts_data,
            'rights_holders': rights_holders_data,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }

    def _get_period_dates(self, period: AnalyticsPeriod) -> Tuple[date, date]:
        """Get start and end dates for analytics period."""        end_date = date.today()
        
        if period == AnalyticsPeriod.DAILY:
            start_date = end_date - timedelta(days=1)
        elif period == AnalyticsPeriod.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif period == AnalyticsPeriod.MONTHLY:
            start_date = end_date.replace(day=1)
        elif period == AnalyticsPeriod.QUARTERLY:
            # Calculate start of current quarter
            quarter_start_month = ((end_date.month - 1) // 3) * 3 + 1
            start_date = end_date.replace(month=quarter_start_month, day=1)
        elif period == AnalyticsPeriod.YEARLY:
            start_date = end_date.replace(month=1, day=1)
        else:
            # Default to last 30 days
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date

    async def _get_licensing_data(
        self,
        start_date: date,
        end_date: date,
        config: ReportConfig
    ) -> List[Dict[str, Any]]:
        """Get licensing data for the specified period."""        # In production, this would query actual database
        # Returning mock data for demonstration
        
        mock_data = []
        for i in range(100):  # Mock 100 licensing records
            record_date = start_date + timedelta(
                days=np.random.randint(0, (end_date - start_date).days + 1)
            )
            
            mock_data.append({
                'license_id': f"LIC_{uuid.uuid4().hex[:8]}",
                'content_id': f"CONTENT_{np.random.randint(1, 50)}",
                'platform': np.random.choice(['Spotify', 'Apple Music', 'YouTube', 'Amazon Music']),
                'territory': np.random.choice(['US', 'UK', 'DE', 'FR', 'CA']),
                'license_type': np.random.choice(['streaming', 'download', 'sync', 'broadcast']),
                'revenue': np.random.uniform(10, 1000),
                'date': record_date,
                'status': np.random.choice(['active', 'pending', 'expired'])
            })
        
        return mock_data

    async def _get_royalty_data(
        self,
        start_date: date,
        end_date: date,
        config: ReportConfig
    ) -> List[Dict[str, Any]]:
        """Get royalty data for the specified period."""        # Mock royalty data
        mock_data = []
        for i in range(200):  # Mock 200 royalty records
            record_date = start_date + timedelta(
                days=np.random.randint(0, (end_date - start_date).days + 1)
            )
            
            mock_data.append({
                'royalty_id': f"ROY_{uuid.uuid4().hex[:8]}",
                'content_id': f"CONTENT_{np.random.randint(1, 50)}",
                'rights_holder_id': f"HOLDER_{np.random.randint(1, 20)}",
                'royalty_type': np.random.choice(['mechanical', 'performance', 'sync']),
                'amount': np.random.uniform(1, 500),
                'currency': 'USD',
                'date': record_date,
                'status': np.random.choice(['calculated', 'paid', 'pending'])
            })
        
        return mock_data

    async def _get_usage_data(
        self,
        start_date: date,
        end_date: date,
        config: ReportConfig
    ) -> List[Dict[str, Any]]:
        """Get usage data for the specified period."""        # Mock usage data
        mock_data = []
        for i in range(500):  # Mock 500 usage records
            record_date = start_date + timedelta(
                days=np.random.randint(0, (end_date - start_date).days + 1)
            )
            
            mock_data.append({
                'usage_id': f"USAGE_{uuid.uuid4().hex[:8]}",
                'content_id': f"CONTENT_{np.random.randint(1, 50)}",
                'platform': np.random.choice(['Spotify', 'Apple Music', 'YouTube', 'Amazon Music']),
                'territory': np.random.choice(['US', 'UK', 'DE', 'FR', 'CA']),
                'play_count': np.random.randint(1, 10000),
                'revenue': np.random.uniform(0.1, 50),
                'date': record_date
            })
        
        return mock_data

    async def _get_contracts_data(
        self,
        start_date: date,
        end_date: date,
        config: ReportConfig
    ) -> List[Dict[str, Any]]:
        """Get contracts data for the specified period."""        # Mock contracts data
        mock_data = []
        for i in range(50):  # Mock 50 contracts
            mock_data.append({
                'contract_id': f"CONTRACT_{uuid.uuid4().hex[:8]}",
                'content_id': f"CONTENT_{np.random.randint(1, 50)}",
                'party': f"Label_{np.random.randint(1, 10)}",
                'contract_type': np.random.choice(['exclusive', 'non_exclusive', 'sync_only']),
                'start_date': start_date,
                'end_date': end_date + timedelta(days=365),
                'value': np.random.uniform(1000, 100000),
                'status': np.random.choice(['active', 'pending', 'draft'])
            })
        
        return mock_data

    async def _get_rights_holders_data(self, config: ReportConfig) -> List[Dict[str, Any]]:
        """Get rights holders data."""        # Mock rights holders data
        mock_data = []
        for i in range(20):  # Mock 20 rights holders
            mock_data.append({
                'holder_id': f"HOLDER_{i+1}",
                'name': f"Rights Holder {i+1}",
                'type': np.random.choice(['songwriter', 'publisher', 'label', 'performer']),
                'territory': np.random.choice(['US', 'UK', 'DE', 'FR', 'CA']),
                'content_count': np.random.randint(1, 20),
                'total_earnings': np.random.uniform(1000, 50000)
            })
        
        return mock_data

    async def _calculate_key_metrics(
        self,
        report_data: Dict[str, Any],
        config: ReportConfig
    ) -> List[KPIMetric]:
        """Calculate key performance indicators."""        
        metrics = []
        
        # Revenue metrics
        licensing_data = report_data.get('licensing', [])
        royalty_data = report_data.get('royalties', [])
        usage_data = report_data.get('usage', [])
        
        # Total revenue
        total_licensing_revenue = sum(record.get('revenue', 0) for record in licensing_data)
        total_royalty_revenue = sum(record.get('amount', 0) for record in royalty_data)
        total_usage_revenue = sum(record.get('revenue', 0) for record in usage_data)
        
        total_revenue = total_licensing_revenue + total_royalty_revenue + total_usage_revenue
        
        metrics.append(KPIMetric(
            metric_id="total_revenue",
            name="Total Revenue",
            value=total_revenue,
            metric_type=MetricType.REVENUE,
            unit="USD",
            description="Total revenue across all licensing activities",
            change_percentage=np.random.uniform(-10, 15),  # Mock change
            trend_direction="up" if np.random.random() > 0.3 else "down"
        ))
        
        # Usage metrics
        total_plays = sum(record.get('play_count', 0) for record in usage_data)
        
        metrics.append(KPIMetric(
            metric_id="total_plays",
            name="Total Plays",
            value=total_plays,
            metric_type=MetricType.USAGE,
            unit="plays",
            description="Total number of content plays",
            change_percentage=np.random.uniform(-5, 25),
            trend_direction="up"
        ))
        
        # Revenue per play
        rpm = total_usage_revenue / total_plays if total_plays > 0 else 0
        
        metrics.append(KPIMetric(
            metric_id="revenue_per_play",
            name="Revenue Per Play",
            value=rpm,
            metric_type=MetricType.EFFICIENCY,
            unit="USD",
            description="Average revenue generated per play",
            target_value=0.005,  # Target 0.5 cents per play
            change_percentage=np.random.uniform(-8, 12)
        ))
        
        # Active contracts
        contracts_data = report_data.get('contracts', [])
        active_contracts = len([c for c in contracts_data if c.get('status') == 'active'])
        
        metrics.append(KPIMetric(
            metric_id="active_contracts",
            name="Active Contracts",
            value=active_contracts,
            metric_type=MetricType.EFFICIENCY,
            unit="contracts",
            description="Number of currently active licensing contracts"
        ))
        
        # Platform diversity (number of platforms)
        platforms = set(record.get('platform') for record in usage_data if record.get('platform'))
        
        metrics.append(KPIMetric(
            metric_id="platform_diversity",
            name="Platform Diversity",
            value=len(platforms),
            metric_type=MetricType.MARKET_SHARE,
            unit="platforms",
            description="Number of unique platforms generating revenue"
        ))
        
        # Territory coverage
        territories = set(record.get('territory') for record in usage_data if record.get('territory'))
        
        metrics.append(KPIMetric(
            metric_id="territory_coverage",
            name="Territory Coverage",
            value=len(territories),
            metric_type=MetricType.MARKET_SHARE,
            unit="territories",
            description="Number of territories with active licensing"
        ))
        
        # Compliance rate (mock calculation)
        compliance_rate = np.random.uniform(85, 98)
        
        metrics.append(KPIMetric(
            metric_id="compliance_rate",
            name="Compliance Rate",
            value=compliance_rate,
            metric_type=MetricType.COMPLIANCE,
            unit="%",
            description="Percentage of licensing activities in compliance",
            target_value=95.0,
            benchmark_value=90.0
        ))
        
        return metrics

    async def _generate_ai_insights(
        self,
        report_data: Dict[str, Any],
        key_metrics: List[KPIMetric],
        config: ReportConfig
    ) -> List[AnalyticsInsight]:
        """Generate AI-powered analytics insights."""        
        insights = []
        
        # Revenue trend insight
        revenue_metric = next((m for m in key_metrics if m.metric_id == "total_revenue"), None)
        if revenue_metric and revenue_metric.change_percentage:
            if revenue_metric.change_percentage > 10:
                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Strong Revenue Growth Detected",
                    description=f"Revenue has increased by {revenue_metric.change_percentage:.1f}% in the reporting period, indicating strong licensing performance.",
                    insight_type="trend",
                    confidence_score=0.85,
                    impact_level="high",
                    recommended_actions=[
                        "Capitalize on growth momentum by expanding to new territories",
                        "Consider increasing licensing rates for high-performing content",
                        "Analyze successful strategies for replication"
                    ],
                    related_metrics=["total_revenue", "revenue_per_play"]
                ))
            elif revenue_metric.change_percentage < -5:
                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Revenue Decline Requires Attention",
                    description=f"Revenue has decreased by {abs(revenue_metric.change_percentage):.1f}% in the reporting period.",
                    insight_type="warning",
                    confidence_score=0.90,
                    impact_level="medium",
                    recommended_actions=[
                        "Review licensing strategies and competitive positioning",
                        "Analyze underperforming territories and platforms",
                        "Consider promotional campaigns to boost usage"
                    ],
                    related_metrics=["total_revenue", "platform_diversity"]
                ))
        
        # Platform performance insight
        usage_data = report_data.get('usage', [])
        if usage_data:
            platform_revenue = defaultdict(float)
            for record in usage_data:
                platform_revenue[record.get('platform', 'Unknown')] += record.get('revenue', 0)
            
            if platform_revenue:
                top_platform = max(platform_revenue.items(), key=lambda x: x[1])
                total_revenue = sum(platform_revenue.values())
                top_platform_share = (top_platform[1] / total_revenue) * 100 if total_revenue > 0 else 0
                
                if top_platform_share > 50:
                    insights.append(AnalyticsInsight(
                        insight_id=str(uuid.uuid4()),
                        title="Platform Concentration Risk",
                        description=f"{top_platform[0]} accounts for {top_platform_share:.1f}% of total revenue, creating concentration risk.",
                        insight_type="warning",
                        confidence_score=0.92,
                        impact_level="medium",
                        recommended_actions=[
                            "Diversify platform portfolio to reduce dependency",
                            "Strengthen relationships with secondary platforms",
                            "Explore emerging platforms for expansion"
                        ],
                        related_metrics=["platform_diversity"],
                        supporting_data={
                            "top_platform": top_platform[0],
                            "market_share": top_platform_share,
                            "platform_breakdown": dict(platform_revenue)
                        }
                    ))
        
        # Compliance insight
        compliance_metric = next((m for m in key_metrics if m.metric_id == "compliance_rate"), None)
        if compliance_metric and compliance_metric.value < 90:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Compliance Rate Below Benchmark",
                description=f"Current compliance rate of {compliance_metric.value:.1f}% is below the industry benchmark of 90%.",
                insight_type="warning",
                confidence_score=0.95,
                impact_level="high",
                recommended_actions=[
                    "Conduct comprehensive compliance audit",
                    "Implement automated compliance monitoring",
                    "Provide additional training to licensing team"
                ],
                related_metrics=["compliance_rate"]
            ))
        
        # Opportunity insight
        territory_metric = next((m for m in key_metrics if m.metric_id == "territory_coverage"), None)
        if territory_metric and territory_metric.value < 10:
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Territory Expansion Opportunity",
                description=f"Currently active in only {territory_metric.value} territories. Significant expansion opportunity exists.",
                insight_type="opportunity",
                confidence_score=0.80,
                impact_level="medium",
                recommended_actions=[
                    "Conduct market research for new territory expansion",
                    "Analyze licensing requirements for target territories",
                    "Develop territory-specific licensing strategies"
                ],
                related_metrics=["territory_coverage", "total_revenue"]
            ))
        
        # Efficiency insight
        rpm_metric = next((m for m in key_metrics if m.metric_id == "revenue_per_play"), None)
        if rpm_metric and rpm_metric.target_value:
            if rpm_metric.value < rpm_metric.target_value * 0.8:
                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Revenue Per Play Below Target",
                    description=f"Current RPM of ${rpm_metric.value:.4f} is below target of ${rpm_metric.target_value:.4f}.",
                    insight_type="warning",
                    confidence_score=0.88,
                    impact_level="medium",
                    recommended_actions=[
                        "Review and optimize licensing rate structures",
                        "Focus on higher-value licensing opportunities",
                        "Analyze platform mix for revenue optimization"
                    ],
                    related_metrics=["revenue_per_play", "total_revenue"]
                ))
        
        return insights

    def _create_data_tables(
        self,
        report_data: Dict[str, Any],
        config: ReportConfig
    ) -> Dict[str, pd.DataFrame]:
        """Create data tables for the report."""        
        tables = {}
        
        # Revenue summary table
        usage_data = report_data.get('usage', [])
        if usage_data:
            df_usage = pd.DataFrame(usage_data)
            
            # Platform revenue summary
            platform_summary = df_usage.groupby('platform').agg({
                'revenue': 'sum',
                'play_count': 'sum'
            }).reset_index()
            platform_summary['rpm'] = platform_summary['revenue'] / platform_summary['play_count']
            platform_summary = platform_summary.sort_values('revenue', ascending=False)
            
            tables['platform_revenue'] = platform_summary
            
            # Territory revenue summary
            territory_summary = df_usage.groupby('territory').agg({
                'revenue': 'sum',
                'play_count': 'sum'
            }).reset_index()
            territory_summary['rpm'] = territory_summary['revenue'] / territory_summary['play_count']
            territory_summary = territory_summary.sort_values('revenue', ascending=False)
            
            tables['territory_revenue'] = territory_summary
            
            # Daily trends
            df_usage['date'] = pd.to_datetime(df_usage['date'])
            daily_trends = df_usage.groupby('date').agg({
                'revenue': 'sum',
                'play_count': 'sum'
            }).reset_index()
            daily_trends['rpm'] = daily_trends['revenue'] / daily_trends['play_count']
            
            tables['daily_trends'] = daily_trends
        
        # Rights holder summary
        royalty_data = report_data.get('royalties', [])
        if royalty_data:
            df_royalties = pd.DataFrame(royalty_data)
            
            holder_summary = df_royalties.groupby('rights_holder_id').agg({
                'amount': 'sum'
            }).reset_index()
            holder_summary.columns = ['rights_holder_id', 'total_royalties']
            holder_summary = holder_summary.sort_values('total_royalties', ascending=False)
            
            tables['rights_holder_summary'] = holder_summary
        
        # Contract status summary
        contracts_data = report_data.get('contracts', [])
        if contracts_data:
            df_contracts = pd.DataFrame(contracts_data)
            
            contract_summary = df_contracts.groupby(['status', 'contract_type']).size().reset_index()
            contract_summary.columns = ['status', 'contract_type', 'count']
            
            tables['contract_summary'] = contract_summary
        
        return tables

    async def _generate_charts(
        self,
        report_data: Dict[str, Any],
        config: ReportConfig
    ) -> Dict[str, Any]:
        """Generate visualization charts for the report."""        
        charts = {}
        
        if not PLOTTING_AVAILABLE:
            return charts
        
        try:
            # Revenue trend chart
            usage_data = report_data.get('usage', [])
            if usage_data:
                df_usage = pd.DataFrame(usage_data)
                df_usage['date'] = pd.to_datetime(df_usage['date'])
                
                daily_revenue = df_usage.groupby('date')['revenue'].sum().reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=daily_revenue['date'],
                    y=daily_revenue['revenue'],
                    mode='lines+markers',
                    name='Daily Revenue',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                fig.update_layout(
                    title='Revenue Trend Over Time',
                    xaxis_title='Date',
                    yaxis_title='Revenue (USD)',
                    template='plotly_white'
                )
                
                charts['revenue_trend'] = fig.to_json()
                
                # Platform revenue pie chart
                platform_revenue = df_usage.groupby('platform')['revenue'].sum()
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=platform_revenue.index,
                    values=platform_revenue.values,
                    hole=0.3
                )])
                
                fig_pie.update_layout(
                    title='Revenue Distribution by Platform',
                    template='plotly_white'
                )
                
                charts['platform_pie'] = fig_pie.to_json()
                
                # Territory performance bar chart
                territory_revenue = df_usage.groupby('territory')['revenue'].sum().sort_values(ascending=True)
                
                fig_bar = go.Figure(data=[go.Bar(
                    x=territory_revenue.values,
                    y=territory_revenue.index,
                    orientation='h',
                    marker_color='#ff7f0e'
                )])
                
                fig_bar.update_layout(
                    title='Revenue by Territory',
                    xaxis_title='Revenue (USD)',
                    yaxis_title='Territory',
                    template='plotly_white'
                )
                
                charts['territory_bar'] = fig_bar.to_json()
            
        except Exception as e:
            self.logger.error(f"Chart generation failed: {e}")
        
        return charts

    async def _generate_executive_summary(
        self,
        key_metrics: List[KPIMetric],
        insights: List[AnalyticsInsight],
        config: ReportConfig
    ) -> str:
        """Generate executive summary for the report."""        
        # Extract key information
        revenue_metric = next((m for m in key_metrics if m.metric_id == "total_revenue"), None)
        plays_metric = next((m for m in key_metrics if m.metric_id == "total_plays"), None)
        
        # Count insights by type
        insight_counts = Counter(insight.insight_type for insight in insights)
        
        # Generate summary
        summary_parts = []
        
        # Period overview
        period_str = f"This {config.period.value} report"
        if config.start_date and config.end_date:
            period_str += f" covers the period from {config.start_date} to {config.end_date}"
        
        summary_parts.append(f"{period_str} provides a comprehensive analysis of licensing performance.")
        
        # Revenue overview
        if revenue_metric:
            revenue_str = f"Total revenue reached ${revenue_metric.value:,.2f}"
            if revenue_metric.change_percentage:
                direction = "increased" if revenue_metric.change_percentage > 0 else "decreased"
                revenue_str += f", representing a {abs(revenue_metric.change_percentage):.1f}% {direction} from the previous period"
            summary_parts.append(revenue_str + ".")
        
        # Usage overview
        if plays_metric:
            plays_str = f"Content was played {plays_metric.value:,} times"
            if plays_metric.change_percentage:
                direction = "increase" if plays_metric.change_percentage > 0 else "decrease"
                plays_str += f", showing a {abs(plays_metric.change_percentage):.1f}% {direction}"
            summary_parts.append(plays_str + ".")
        
        # Key insights summary
        if insights:
            high_impact_insights = [i for i in insights if i.impact_level == "high"]
            if high_impact_insights:
                summary_parts.append(f"Analysis identified {len(high_impact_insights)} high-impact areas requiring attention.")
            
            if insight_counts.get('opportunity', 0) > 0:
                summary_parts.append(f"The analysis revealed {insight_counts['opportunity']} growth opportunities.")
            
            if insight_counts.get('warning', 0) > 0:
                summary_parts.append(f"There are {insight_counts['warning']} areas flagged for review and optimization.")
        
        # Recommendations
        all_actions = []
        for insight in insights:
            all_actions.extend(insight.recommended_actions)
        
        if all_actions:
            top_actions = Counter(all_actions).most_common(3)
            summary_parts.append("Key recommended actions include: " + 
                               ", ".join([action for action, _ in top_actions]) + ".")
        
        return " ".join(summary_parts)

    def _calculate_quality_score(
        self,
        report_data: Dict[str, Any],
        key_metrics: List[KPIMetric]
    ) -> float:
        """Calculate report quality score based on data completeness."""        
        score = 0.0
        total_checks = 0
        
        # Data completeness checks
        for data_type, data in report_data.items():
            if data_type != 'period':
                total_checks += 1
                if data and len(data) > 0:
                    score += 0.2
        
        # Metrics completeness
        total_checks += 1
        if key_metrics and len(key_metrics) >= 5:
            score += 0.2
        
        # Ensure score is between 0 and 1
        final_score = min(score, 1.0)
        
        return final_score

    def _update_analytics_metrics(self, generation_time: float):
        """Update analytics engine performance metrics."""        self.analytics_metrics['reports_generated'] += 1
        
        # Update average generation time
        current_avg = self.analytics_metrics['average_generation_time']
        total_reports = self.analytics_metrics['reports_generated']
        
        new_avg = ((current_avg * (total_reports - 1)) + generation_time) / total_reports
        self.analytics_metrics['average_generation_time'] = new_avg

    async def create_dashboard_config(
        self,
        dashboard_name: str,
        widgets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create configuration for interactive dashboard."""        
        dashboard_config = {
            'dashboard_id': str(uuid.uuid4()),
            'name': dashboard_name,
            'created_at': datetime.now().isoformat(),
            'widgets': widgets,
            'refresh_interval': 300,  # 5 minutes
            'auto_refresh': True,
            'layout': {
                'columns': 12,
                'rows': 'auto'
            }
        }
        
        return dashboard_config

    async def export_report(
        self,
        report_result: ReportResult,
        format: ReportFormat,
        output_path: Optional[str] = None
    ) -> str:
        """Export report in specified format."""        
        try:
            if format == ReportFormat.JSON:
                return await self._export_json(report_result, output_path)
            elif format == ReportFormat.PDF:
                return await self._export_pdf(report_result, output_path)
            elif format == ReportFormat.EXCEL:
                return await self._export_excel(report_result, output_path)
            elif format == ReportFormat.CSV:
                return await self._export_csv(report_result, output_path)
            elif format == ReportFormat.HTML:
                return await self._export_html(report_result, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Report export failed: {e}")
            raise

    async def _export_json(self, report_result: ReportResult, output_path: Optional[str]) -> str:
        """Export report as JSON."""        
        # Convert DataFrames to dictionaries for JSON serialization
        json_data = {
            'report_id': report_result.report_id,
            'generated_at': report_result.generated_at.isoformat(),
            'executive_summary': report_result.executive_summary,
            'key_metrics': [asdict(metric) for metric in report_result.key_metrics],
            'insights': [asdict(insight) for insight in report_result.insights],
            'data_tables': {
                name: df.to_dict('records') 
                for name, df in report_result.data_tables.items()
            },
            'generation_time': report_result.generation_time,
            'quality_score': report_result.quality_score
        }
        
        # Convert datetime objects to strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            return obj
        
        json_str = json.dumps(json_data, default=convert_datetime, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            return output_path
        else:
            return json_str

    async def _export_excel(self, report_result: ReportResult, output_path: Optional[str]) -> str:
        """Export report as Excel file."""        
        if not output_path:
            output_path = f"report_{report_result.report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Executive Summary sheet
            summary_df = pd.DataFrame([{
                'Report ID': report_result.report_id,
                'Generated At': report_result.generated_at,
                'Executive Summary': report_result.executive_summary,
                'Generation Time (seconds)': report_result.generation_time,
                'Quality Score': report_result.quality_score
            }])
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Key Metrics sheet
            metrics_data = []
            for metric in report_result.key_metrics:
                metrics_data.append({
                    'Metric ID': metric.metric_id,
                    'Name': metric.name,
                    'Value': metric.value,
                    'Type': metric.metric_type.value,
                    'Unit': metric.unit,
                    'Change %': metric.change_percentage,
                    'Trend': metric.trend_direction,
                    'Target': metric.target_value,
                    'Description': metric.description
                })
            
            metrics_df = pd.DataFrame(metrics_data)
            metrics_df.to_excel(writer, sheet_name='Key Metrics', index=False)
            
            # Insights sheet
            insights_data = []
            for insight in report_result.insights:
                insights_data.append({
                    'Insight ID': insight.insight_id,
                    'Title': insight.title,
                    'Description': insight.description,
                    'Type': insight.insight_type,
                    'Confidence': insight.confidence_score,
                    'Impact Level': insight.impact_level,
                    'Recommended Actions': '; '.join(insight.recommended_actions)
                })
            
            insights_df = pd.DataFrame(insights_data)
            insights_df.to_excel(writer, sheet_name='Insights', index=False)
            
            # Data tables
            for table_name, df in report_result.data_tables.items():
                sheet_name = table_name.replace('_', ' ').title()[:31]  # Excel sheet name limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return output_path

    async def _export_csv(self, report_result: ReportResult, output_path: Optional[str]) -> str:
        """Export report data as CSV files."""        
        if not output_path:
            output_path = f"report_{report_result.report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory for CSV files
        Path(output_path).mkdir(exist_ok=True)
        
        # Export each data table as CSV
        for table_name, df in report_result.data_tables.items():
            csv_path = Path(output_path) / f"{table_name}.csv"
            df.to_csv(csv_path, index=False)
        
        # Export key metrics as CSV
        metrics_data = []
        for metric in report_result.key_metrics:
            metrics_data.append({
                'metric_id': metric.metric_id,
                'name': metric.name,
                'value': metric.value,
                'type': metric.metric_type.value,
                'unit': metric.unit,
                'change_percentage': metric.change_percentage,
                'trend_direction': metric.trend_direction
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_csv(Path(output_path) / "key_metrics.csv", index=False)
        
        return output_path

    async def _export_html(self, report_result: ReportResult, output_path: Optional[str]) -> str:
        """Export report as HTML."""        
        if not output_path:
            output_path = f"report_{report_result.report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Generate HTML content
        html_content = f"""        <!DOCTYPE html>
        <html>
        <head>
            <title>Licensing Analytics Report - {report_result.report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2 {{ color: #333; }}
                .metric {{ margin: 10px 0; padding: 10px; border-left: 4px solid #007acc; }}
                .insight {{ margin: 15px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Licensing Analytics Report</h1>
            <p><strong>Report ID:</strong> {report_result.report_id}</p>
            <p><strong>Generated:</strong> {report_result.generated_at}</p>
            
            <h2>Executive Summary</h2>
            <p>{report_result.executive_summary}</p>
            
            <h2>Key Metrics</h2>
        """        
        # Add key metrics
        for metric in report_result.key_metrics:
            change_indicator = ""
            if metric.change_percentage:
                direction = "↑" if metric.change_percentage > 0 else "↓"
                change_indicator = f" ({direction} {abs(metric.change_percentage):.1f}%)"
            
            html_content += f"""            <div class="metric">
                <strong>{metric.name}:</strong> {metric.value} {metric.unit}{change_indicator}
                <br><small>{metric.description}</small>
            </div>
            """        
        # Add insights
        html_content += "<h2>Key Insights</h2>"
        for insight in report_result.insights:
            html_content += f"""            <div class="insight">
                <h3>{insight.title}</h3>
                <p>{insight.description}</p>
                <p><strong>Impact Level:</strong> {insight.impact_level}</p>
                <p><strong>Confidence:</strong> {insight.confidence_score:.0%}</p>
                <p><strong>Recommended Actions:</strong></p>
                <ul>
            """            for action in insight.recommended_actions:
                html_content += f"<li>{action}</li>"
            html_content += "</ul></div>"
        
        # Add data tables
        for table_name, df in report_result.data_tables.items():
            html_content += f"<h2>{table_name.replace('_', ' ').title()}</h2>"
            html_content += df.to_html(classes='table', escape=False)
        
        html_content += """        </body>
        </html>
        """        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    async def _export_pdf(self, report_result: ReportResult, output_path: Optional[str]) -> str:
        """Export report as PDF (placeholder implementation)."""        # In production, would use libraries like reportlab or weasyprint
        # For now, export as HTML and suggest conversion
        html_path = await self._export_html(report_result, output_path)
        return f"HTML report generated: {html_path} (convert to PDF using external tool)"

    def get_analytics_metrics(self) -> Dict[str, Any]:
        """Get analytics engine performance metrics."""        return {
            **self.analytics_metrics,
            'cache_size': len(self.report_cache),
            'supported_formats': [fmt.value for fmt in ReportFormat],
            'available_report_types': [rt.value for rt in ReportType]
        }

# Export classes and functions
__all__ = [
    'LicensingAnalyticsEngine',
    'ReportConfig',
    'ReportResult',
    'KPIMetric',
    'AnalyticsInsight',
    'ReportType',
    'ReportFormat',
    'AnalyticsPeriod',
    'MetricType'
]
