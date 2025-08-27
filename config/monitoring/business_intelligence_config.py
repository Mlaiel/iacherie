"""
Business Intelligence Monitoring Configuration for IA-Influencer Agent Platform
===============================================================================

Professional business intelligence and KPI monitoring configuration for
comprehensive business metrics monitoring and intelligence with advanced analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal
import pandas as pd
import numpy as np


class BusinessMetricCategory(Enum):
    """Business metric categories"""
    REVENUE = "revenue"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    PLATFORM_GROWTH = "platform_growth"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    MARKET_PENETRATION = "market_penetration"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"


class KPIType(Enum):
    """Key Performance Indicator types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    RATE = "rate"
    RATIO = "ratio"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DURATION = "duration"
    SCORE = "score"


class BusinessDimension(Enum):
    """Business analysis dimensions"""
    TIME = "time"
    GEOGRAPHY = "geography"
    USER_SEGMENT = "user_segment"
    CONTENT_TYPE = "content_type"
    PLATFORM = "platform"
    SUBSCRIPTION_TIER = "subscription_tier"
    ACQUISITION_CHANNEL = "acquisition_channel"
    DEVICE_TYPE = "device_type"


@dataclass
class BusinessKPI:
    """Business Key Performance Indicator definition"""
    name: str
    category: BusinessMetricCategory
    kpi_type: KPIType
    description: str
    calculation_formula: str
    target_value: Optional[float] = None
    benchmark_value: Optional[float] = None
    dimensions: List[BusinessDimension] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    refresh_frequency: str = "hourly"
    business_owner: str = ""
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    seasonal_adjustment: bool = False


@dataclass
class BusinessReport:
    """Business intelligence report configuration"""
    name: str
    report_type: str
    description: str
    kpis: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    time_range: str = "last_30_days"
    granularity: str = "daily"
    format: str = "pdf"
    distribution_list: List[str] = field(default_factory=list)
    schedule: str = "weekly"
    automated: bool = True


@dataclass
class CompetitiveIntelligence:
    """Competitive intelligence monitoring"""
    competitor_name: str
    monitoring_areas: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    update_frequency: str = "daily"
    alert_on_changes: bool = True
    benchmark_metrics: Dict[str, float] = field(default_factory=dict)


class BusinessIntelligenceConfig:
    """
    Professional business intelligence monitoring configuration
    
    Manages comprehensive business KPIs, competitive intelligence,
    and automated business reporting with advanced analytics.
    """
    
    def __init__(self):
        """Initialize business intelligence configuration"""
        self._kpis = {}
        self._reports = {}
        self._competitive_intelligence = {}
        self._dashboards = {}
        
        # Configuration from environment
        self.config = {
            "bi_database_url": os.getenv("BI_DATABASE_URL", "postgresql://bi_user:password@localhost:5432/business_intelligence"),
            "data_warehouse_url": os.getenv("DATA_WAREHOUSE_URL", "postgresql://dw_user:password@localhost:5432/data_warehouse"),
            "analytics_api_key": os.getenv("ANALYTICS_API_KEY", ""),
            
            # Business configuration
            "company_name": os.getenv("COMPANY_NAME", "IA-Influencer Agent"),
            "fiscal_year_start": os.getenv("FISCAL_YEAR_START", "01-01"),
            "reporting_currency": os.getenv("REPORTING_CURRENCY", "EUR"),
            "business_timezone": os.getenv("BUSINESS_TIMEZONE", "Europe/Berlin"),
            
            # Reporting settings
            "report_storage_path": os.getenv("REPORT_STORAGE_PATH", "/opt/reports"),
            "report_retention_days": int(os.getenv("REPORT_RETENTION_DAYS", "365")),
            "automated_reporting": os.getenv("AUTOMATED_REPORTING", "true").lower() == "true",
            
            # Data processing
            "etl_schedule": os.getenv("ETL_SCHEDULE", "0 2 * * *"),  # Daily at 2 AM
            "data_quality_threshold": float(os.getenv("DATA_QUALITY_THRESHOLD", "0.95")),
            "outlier_detection_threshold": float(os.getenv("OUTLIER_DETECTION_THRESHOLD", "3.0")),
            
            # External integrations
            "google_analytics_id": os.getenv("GOOGLE_ANALYTICS_ID", ""),
            "mixpanel_project_id": os.getenv("MIXPANEL_PROJECT_ID", ""),
            "segment_write_key": os.getenv("SEGMENT_WRITE_KEY", ""),
            "hubspot_api_key": os.getenv("HUBSPOT_API_KEY", ""),
        }
        
        self._setup_revenue_kpis()
        self._setup_user_engagement_kpis()
        self._setup_content_performance_kpis()
        self._setup_growth_kpis()
        self._setup_operational_kpis()
        self._setup_customer_satisfaction_kpis()
        self._setup_business_reports()
        self._setup_competitive_intelligence()
    
    def _setup_revenue_kpis(self):
        """Setup revenue-related KPIs"""
        # Monthly Recurring Revenue
        self.register_kpi(BusinessKPI(
            name="monthly_recurring_revenue",
            category=BusinessMetricCategory.REVENUE,
            kpi_type=KPIType.CURRENCY,
            description="Total monthly recurring revenue from all subscription tiers",
            calculation_formula="""
                SELECT SUM(amount) as mrr
                FROM subscriptions s
                JOIN subscription_plans sp ON s.plan_id = sp.id
                WHERE s.status = 'active'
                AND sp.billing_cycle = 'monthly'
            """,
            target_value=100000.0,  # €100K per month
            dimensions=[BusinessDimension.TIME, BusinessDimension.SUBSCRIPTION_TIER, BusinessDimension.GEOGRAPHY],
            data_sources=["subscription_database", "payment_processor"],
            refresh_frequency="daily",
            business_owner="CFO",
            alert_thresholds={"warning": -5.0, "critical": -10.0}  # % change
        ))
        
        # Average Revenue Per User
        self.register_kpi(BusinessKPI(
            name="average_revenue_per_user",
            category=BusinessMetricCategory.REVENUE,
            kpi_type=KPIType.CURRENCY,
            description="Average revenue generated per active user",
            calculation_formula="""
                WITH monthly_revenue AS (
                    SELECT SUM(amount) as total_revenue
                    FROM revenue_transactions
                    WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
                ),
                active_users AS (
                    SELECT COUNT(DISTINCT user_id) as user_count
                    FROM user_sessions
                    WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
                )
                SELECT (mr.total_revenue / au.user_count) as arpu
                FROM monthly_revenue mr, active_users au
            """,
            target_value=25.0,  # €25 per user per month
            dimensions=[BusinessDimension.TIME, BusinessDimension.USER_SEGMENT, BusinessDimension.ACQUISITION_CHANNEL],
            data_sources=["revenue_database", "user_analytics"],
            refresh_frequency="daily",
            business_owner="Head of Revenue"
        ))
        
        # Customer Lifetime Value
        self.register_kpi(BusinessKPI(
            name="customer_lifetime_value",
            category=BusinessMetricCategory.REVENUE,
            kpi_type=KPIType.CURRENCY,
            description="Predicted lifetime value of customers",
            calculation_formula="""
                WITH user_metrics AS (
                    SELECT 
                        user_id,
                        SUM(amount) as total_revenue,
                        EXTRACT(DAYS FROM (MAX(created_at) - MIN(created_at))) as tenure_days
                    FROM revenue_transactions
                    GROUP BY user_id
                )
                SELECT AVG(total_revenue / (tenure_days / 30.0)) * 12 as clv
                FROM user_metrics
                WHERE tenure_days > 0
            """,
            target_value=300.0,  # €300 lifetime value
            dimensions=[BusinessDimension.USER_SEGMENT, BusinessDimension.ACQUISITION_CHANNEL],
            data_sources=["revenue_database", "user_database"],
            refresh_frequency="weekly",
            business_owner="Head of Revenue"
        ))
        
        # Revenue Growth Rate
        self.register_kpi(BusinessKPI(
            name="revenue_growth_rate",
            category=BusinessMetricCategory.REVENUE,
            kpi_type=KPIType.PERCENTAGE,
            description="Month-over-month revenue growth rate",
            calculation_formula="""
                WITH monthly_revenue AS (
                    SELECT 
                        DATE_TRUNC('month', created_at) as month,
                        SUM(amount) as revenue
                    FROM revenue_transactions
                    WHERE created_at >= CURRENT_DATE - INTERVAL '2 months'
                    GROUP BY DATE_TRUNC('month', created_at)
                    ORDER BY month
                )
                SELECT 
                    ((LAG(revenue) OVER (ORDER BY month) - revenue) / revenue) * 100 as growth_rate
                FROM monthly_revenue
                LIMIT 1
            """,
            target_value=15.0,  # 15% monthly growth
            dimensions=[BusinessDimension.TIME, BusinessDimension.GEOGRAPHY],
            data_sources=["revenue_database"],
            refresh_frequency="daily",
            business_owner="CEO",
            seasonal_adjustment=True
        ))
    
    def _setup_user_engagement_kpis(self):
        """Setup user engagement KPIs"""
        # Daily Active Users
        self.register_kpi(BusinessKPI(
            name="daily_active_users",
            category=BusinessMetricCategory.USER_ENGAGEMENT,
            kpi_type=KPIType.COUNTER,
            description="Number of unique users active daily",
            calculation_formula="""
                SELECT COUNT(DISTINCT user_id) as dau
                FROM user_sessions
                WHERE DATE(created_at) = CURRENT_DATE
            """,
            target_value=10000.0,  # 10K DAU
            dimensions=[BusinessDimension.TIME, BusinessDimension.PLATFORM, BusinessDimension.GEOGRAPHY],
            data_sources=["user_analytics"],
            refresh_frequency="hourly",
            business_owner="Head of Product"
        ))
        
        # User Retention Rate
        self.register_kpi(BusinessKPI(
            name="user_retention_rate_30d",
            category=BusinessMetricCategory.USER_ENGAGEMENT,
            kpi_type=KPIType.PERCENTAGE,
            description="Percentage of users returning within 30 days",
            calculation_formula="""
                WITH new_users AS (
                    SELECT user_id, MIN(created_at) as first_session
                    FROM user_sessions
                    WHERE created_at >= CURRENT_DATE - INTERVAL '60 days'
                    GROUP BY user_id
                ),
                returning_users AS (
                    SELECT DISTINCT nu.user_id
                    FROM new_users nu
                    JOIN user_sessions us ON nu.user_id = us.user_id
                    WHERE us.created_at > nu.first_session + INTERVAL '1 day'
                    AND us.created_at <= nu.first_session + INTERVAL '30 days'
                )
                SELECT (COUNT(ru.user_id) * 100.0 / COUNT(nu.user_id)) as retention_rate
                FROM new_users nu
                LEFT JOIN returning_users ru ON nu.user_id = ru.user_id
            """,
            target_value=40.0,  # 40% retention
            dimensions=[BusinessDimension.TIME, BusinessDimension.USER_SEGMENT],
            data_sources=["user_analytics"],
            refresh_frequency="daily",
            business_owner="Head of Product"
        ))
        
        # Average Session Duration
        self.register_kpi(BusinessKPI(
            name="average_session_duration",
            category=BusinessMetricCategory.USER_ENGAGEMENT,
            kpi_type=KPIType.DURATION,
            description="Average time users spend in each session",
            calculation_formula="""
                SELECT AVG(EXTRACT(EPOCH FROM (ended_at - created_at))) as avg_duration
                FROM user_sessions
                WHERE DATE(created_at) = CURRENT_DATE
                AND ended_at IS NOT NULL
            """,
            target_value=1800.0,  # 30 minutes
            dimensions=[BusinessDimension.TIME, BusinessDimension.DEVICE_TYPE, BusinessDimension.USER_SEGMENT],
            data_sources=["user_analytics"],
            refresh_frequency="hourly",
            business_owner="Head of Product"
        ))
    
    def _setup_content_performance_kpis(self):
        """Setup content performance KPIs"""
        # Content Upload Rate
        self.register_kpi(BusinessKPI(
            name="content_upload_rate",
            category=BusinessMetricCategory.CONTENT_PERFORMANCE,
            kpi_type=KPIType.RATE,
            description="Number of content pieces uploaded per day",
            calculation_formula="""
                SELECT COUNT(*) as upload_count
                FROM content_uploads
                WHERE DATE(created_at) = CURRENT_DATE
            """,
            target_value=1000.0,  # 1K uploads per day
            dimensions=[BusinessDimension.TIME, BusinessDimension.CONTENT_TYPE, BusinessDimension.USER_SEGMENT],
            data_sources=["content_database"],
            refresh_frequency="hourly",
            business_owner="Head of Content"
        ))
        
        # Content Processing Success Rate
        self.register_kpi(BusinessKPI(
            name="content_processing_success_rate",
            category=BusinessMetricCategory.CONTENT_PERFORMANCE,
            kpi_type=KPIType.PERCENTAGE,
            description="Percentage of content processed successfully",
            calculation_formula="""
                SELECT 
                    (COUNT(*) FILTER (WHERE status = 'completed') * 100.0 / COUNT(*)) as success_rate
                FROM content_processing_jobs
                WHERE DATE(created_at) = CURRENT_DATE
            """,
            target_value=98.0,  # 98% success rate
            dimensions=[BusinessDimension.TIME, BusinessDimension.CONTENT_TYPE],
            data_sources=["processing_database"],
            refresh_frequency="hourly",
            business_owner="Head of Engineering"
        ))
        
        # Content Protection Effectiveness
        self.register_kpi(BusinessKPI(
            name="content_protection_effectiveness",
            category=BusinessMetricCategory.CONTENT_PERFORMANCE,
            kpi_type=KPIType.PERCENTAGE,
            description="Percentage of unauthorized content usage detected",
            calculation_formula="""
                WITH total_protected AS (
                    SELECT COUNT(*) as protected_count
                    FROM content_fingerprints
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                ),
                violations_detected AS (
                    SELECT COUNT(*) as violation_count
                    FROM protection_violations
                    WHERE detected_at >= CURRENT_DATE - INTERVAL '30 days'
                    AND confidence_level >= 0.8
                )
                SELECT (vd.violation_count * 100.0 / tp.protected_count) as effectiveness
                FROM total_protected tp, violations_detected vd
            """,
            target_value=85.0,  # 85% detection rate
            dimensions=[BusinessDimension.TIME, BusinessDimension.CONTENT_TYPE, BusinessDimension.PLATFORM],
            data_sources=["protection_database"],
            refresh_frequency="daily",
            business_owner="Head of Security"
        ))
    
    def _setup_growth_kpis(self):
        """Setup platform growth KPIs"""
        # New User Acquisition Rate
        self.register_kpi(BusinessKPI(
            name="new_user_acquisition_rate",
            category=BusinessMetricCategory.PLATFORM_GROWTH,
            kpi_type=KPIType.COUNTER,
            description="Number of new users acquired daily",
            calculation_formula="""
                SELECT COUNT(*) as new_users
                FROM users
                WHERE DATE(created_at) = CURRENT_DATE
            """,
            target_value=500.0,  # 500 new users per day
            dimensions=[BusinessDimension.TIME, BusinessDimension.ACQUISITION_CHANNEL, BusinessDimension.GEOGRAPHY],
            data_sources=["user_database"],
            refresh_frequency="hourly",
            business_owner="Head of Growth"
        ))
        
        # Conversion Rate
        self.register_kpi(BusinessKPI(
            name="signup_to_subscription_conversion_rate",
            category=BusinessMetricCategory.PLATFORM_GROWTH,
            kpi_type=KPIType.PERCENTAGE,
            description="Percentage of signups that convert to paid subscriptions",
            calculation_formula="""
                WITH signups AS (
                    SELECT COUNT(*) as signup_count
                    FROM users
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                ),
                conversions AS (
                    SELECT COUNT(DISTINCT user_id) as conversion_count
                    FROM subscriptions
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                    AND status = 'active'
                )
                SELECT (c.conversion_count * 100.0 / s.signup_count) as conversion_rate
                FROM signups s, conversions c
            """,
            target_value=5.0,  # 5% conversion rate
            dimensions=[BusinessDimension.TIME, BusinessDimension.ACQUISITION_CHANNEL],
            data_sources=["user_database", "subscription_database"],
            refresh_frequency="daily",
            business_owner="Head of Growth"
        ))
    
    def _setup_operational_kpis(self):
        """Setup operational efficiency KPIs"""
        # System Uptime
        self.register_kpi(BusinessKPI(
            name="system_uptime",
            category=BusinessMetricCategory.OPERATIONAL_EFFICIENCY,
            kpi_type=KPIType.PERCENTAGE,
            description="System availability percentage",
            calculation_formula="""
                WITH uptime_data AS (
                    SELECT 
                        COUNT(*) as total_checks,
                        COUNT(*) FILTER (WHERE status = 'up') as up_checks
                    FROM health_checks
                    WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
                )
                SELECT (up_checks * 100.0 / total_checks) as uptime
                FROM uptime_data
            """,
            target_value=99.9,  # 99.9% uptime
            dimensions=[BusinessDimension.TIME],
            data_sources=["monitoring_database"],
            refresh_frequency="hourly",
            business_owner="Head of Engineering"
        ))
        
        # Customer Support Response Time
        self.register_kpi(BusinessKPI(
            name="support_response_time",
            category=BusinessMetricCategory.OPERATIONAL_EFFICIENCY,
            kpi_type=KPIType.DURATION,
            description="Average time to first response for support tickets",
            calculation_formula="""
                SELECT AVG(EXTRACT(EPOCH FROM (first_response_at - created_at))) as avg_response_time
                FROM support_tickets
                WHERE DATE(created_at) = CURRENT_DATE
                AND first_response_at IS NOT NULL
            """,
            target_value=3600.0,  # 1 hour
            dimensions=[BusinessDimension.TIME],
            data_sources=["support_database"],
            refresh_frequency="hourly",
            business_owner="Head of Support"
        ))
    
    def _setup_customer_satisfaction_kpis(self):
        """Setup customer satisfaction KPIs"""
        # Net Promoter Score
        self.register_kpi(BusinessKPI(
            name="net_promoter_score",
            category=BusinessMetricCategory.CUSTOMER_SATISFACTION,
            kpi_type=KPIType.SCORE,
            description="Customer satisfaction and loyalty score",
            calculation_formula="""
                WITH nps_scores AS (
                    SELECT 
                        score,
                        CASE 
                            WHEN score >= 9 THEN 'promoter'
                            WHEN score <= 6 THEN 'detractor'
                            ELSE 'passive'
                        END as category
                    FROM customer_surveys
                    WHERE survey_type = 'nps'
                    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                )
                SELECT 
                    (COUNT(*) FILTER (WHERE category = 'promoter') * 100.0 / COUNT(*)) -
                    (COUNT(*) FILTER (WHERE category = 'detractor') * 100.0 / COUNT(*)) as nps
                FROM nps_scores
            """,
            target_value=50.0,  # NPS of 50
            dimensions=[BusinessDimension.TIME, BusinessDimension.USER_SEGMENT],
            data_sources=["survey_database"],
            refresh_frequency="weekly",
            business_owner="Head of Customer Success"
        ))
    
    def _setup_business_reports(self):
        """Setup automated business reports"""
        # Executive Summary Report
        self.register_report(BusinessReport(
            name="executive_summary",
            report_type="executive",
            description="Weekly executive summary with key business metrics",
            kpis=[
                "monthly_recurring_revenue",
                "revenue_growth_rate",
                "daily_active_users",
                "new_user_acquisition_rate",
                "system_uptime",
                "net_promoter_score"
            ],
            time_range="last_7_days",
            granularity="daily",
            format="pdf",
            distribution_list=["ceo@company.com", "cfo@company.com", "coo@company.com"],
            schedule="weekly",
            automated=True
        ))
        
        # Revenue Analysis Report
        self.register_report(BusinessReport(
            name="revenue_analysis",
            report_type="financial",
            description="Detailed revenue analysis and forecasting",
            kpis=[
                "monthly_recurring_revenue",
                "average_revenue_per_user",
                "customer_lifetime_value",
                "revenue_growth_rate",
                "signup_to_subscription_conversion_rate"
            ],
            filters={"subscription_tier": ["premium", "enterprise"]},
            time_range="last_30_days",
            granularity="daily",
            format="excel",
            distribution_list=["cfo@company.com", "head-of-revenue@company.com"],
            schedule="monthly",
            automated=True
        ))
    
    def _setup_competitive_intelligence(self):
        """Setup competitive intelligence monitoring"""
        self.register_competitive_intelligence(CompetitiveIntelligence(
            competitor_name="Spotify for Artists",
            monitoring_areas=["pricing", "features", "user_acquisition", "market_share"],
            data_sources=["web_scraping", "public_apis", "social_media"],
            update_frequency="daily",
            alert_on_changes=True,
            benchmark_metrics={
                "user_base": 50000000,  # 50M creators
                "market_share": 0.35,  # 35%
                "average_pricing": 15.99  # €15.99/month
            }
        ))
        
        self.register_competitive_intelligence(CompetitiveIntelligence(
            competitor_name="YouTube Content ID",
            monitoring_areas=["content_protection", "detection_accuracy", "false_positive_rate"],
            data_sources=["industry_reports", "user_feedback", "technical_analysis"],
            update_frequency="weekly",
            alert_on_changes=True,
            benchmark_metrics={
                "detection_accuracy": 0.92,  # 92%
                "false_positive_rate": 0.08,  # 8%
                "processing_time": 300  # 5 minutes
            }
        ))
    
    def register_kpi(self, kpi: BusinessKPI):
        """Register business KPI"""
        self._kpis[kpi.name] = kpi
        logging.info(f"Registered business KPI: {kpi.name}")
    
    def register_report(self, report: BusinessReport):
        """Register business report"""
        self._reports[report.name] = report
        logging.info(f"Registered business report: {report.name}")
    
    def register_competitive_intelligence(self, competitive_intel: CompetitiveIntelligence):
        """Register competitive intelligence monitoring"""
        self._competitive_intelligence[competitive_intel.competitor_name] = competitive_intel
        logging.info(f"Registered competitive intelligence: {competitive_intel.competitor_name}")
    
    def get_kpi(self, name: str) -> Optional[BusinessKPI]:
        """Get KPI by name"""
        return self._kpis.get(name)
    
    def get_report(self, name: str) -> Optional[BusinessReport]:
        """Get report by name"""
        return self._reports.get(name)
    
    def get_competitive_intelligence(self, competitor: str) -> Optional[CompetitiveIntelligence]:
        """Get competitive intelligence by competitor name"""
        return self._competitive_intelligence.get(competitor)
    
    def get_kpis_by_category(self, category: BusinessMetricCategory) -> List[BusinessKPI]:
        """Get KPIs by category"""
        return [kpi for kpi in self._kpis.values() if kpi.category == category]
    
    def get_kpis_by_owner(self, owner: str) -> List[BusinessKPI]:
        """Get KPIs by business owner"""
        return [kpi for kpi in self._kpis.values() if kpi.business_owner == owner]
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export complete business intelligence configuration"""
        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "company": self.config["company_name"],
                "currency": self.config["reporting_currency"]
            },
            "config": self.config,
            "kpis": {
                name: {
                    "name": kpi.name,
                    "category": kpi.category.value,
                    "type": kpi.kpi_type.value,
                    "description": kpi.description,
                    "target_value": kpi.target_value,
                    "dimensions": [dim.value for dim in kpi.dimensions],
                    "refresh_frequency": kpi.refresh_frequency,
                    "business_owner": kpi.business_owner
                }
                for name, kpi in self._kpis.items()
            },
            "reports": {
                name: {
                    "name": report.name,
                    "type": report.report_type,
                    "description": report.description,
                    "kpis": report.kpis,
                    "schedule": report.schedule,
                    "automated": report.automated
                }
                for name, report in self._reports.items()
            },
            "competitive_intelligence": {
                name: {
                    "competitor": comp_intel.competitor_name,
                    "monitoring_areas": comp_intel.monitoring_areas,
                    "update_frequency": comp_intel.update_frequency,
                    "benchmark_metrics": comp_intel.benchmark_metrics
                }
                for name, comp_intel in self._competitive_intelligence.items()
            }
        }


# Global business intelligence configuration instance
business_intelligence_config = BusinessIntelligenceConfig()

# Export key components for easy import
__all__ = [
    'BusinessIntelligenceConfig',
    'BusinessMetricCategory',
    'KPIType',
    'BusinessDimension',
    'BusinessKPI',
    'BusinessReport',
    'CompetitiveIntelligence',
    'business_intelligence_config'
]
