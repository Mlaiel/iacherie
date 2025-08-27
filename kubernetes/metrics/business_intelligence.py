"""
IA Influencer Agent - Business Intelligence Engine
Advanced business intelligence with ML-powered analytics and revenue optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Advanced business intelligence with predictive analytics
- Revenue optimization and forecasting models
- Customer behavior analysis and segmentation
- Churn prediction and retention strategies
- Performance KPI tracking and optimization
- Real-time business metrics and alerts
- Competitive analysis and market insights
- ROI analysis and cost optimization
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, classification_report
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.security import SecurityManager
from backend.models.analytics import BusinessReport, RevenueAnalysis
from backend.models.business_intelligence import BusinessMetricModel, RevenueModel
from backend.utils.database import get_database_session
from .config import get_metrics_config, MetricsConfiguration

logger = get_logger(__name__)
settings = get_settings()


class BusinessMetricType(Enum):
    """Business metric types"""
    REVENUE = "revenue"
    CUSTOMER_ACQUISITION_COST = "cac"
    CUSTOMER_LIFETIME_VALUE = "clv"
    CHURN_RATE = "churn_rate"
    MONTHLY_RECURRING_REVENUE = "mrr"
    ANNUAL_RECURRING_REVENUE = "arr"
    GROSS_MARGIN = "gross_margin"
    NET_PROMOTER_SCORE = "nps"
    CONVERSION_RATE = "conversion_rate"
    ENGAGEMENT_SCORE = "engagement_score"
    RETENTION_RATE = "retention_rate"
    ARPU = "average_revenue_per_user"
    DAU = "daily_active_users"
    MAU = "monthly_active_users"
    PAYBACK_PERIOD = "payback_period"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_PERFORMANCE = "content_performance"
    GROWTH = "growth"
    ROI = "roi"


class AnalysisType(Enum):
    """Analysis types for business intelligence"""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    REAL_TIME = "real_time"
    COMPARATIVE = "comparative"
    COHORT = "cohort"
    FUNNEL = "funnel"
    SEGMENTATION = "segmentation"
    FORECASTING = "forecasting"


class CustomerSegment(Enum):
    """Customer segmentation categories"""
    HIGH_VALUE = "high_value"
    GROWING = "growing"
    AT_RISK = "at_risk"
    NEW_CUSTOMER = "new_customer"
    CHURNED = "churned"
    DORMANT = "dormant"
    CHAMPION = "champion"
    LOYAL = "loyal"
    POTENTIAL_LOYALIST = "potential_loyalist"


class RevenueMetric(Enum):
    """Revenue metric types"""
    TOTAL_REVENUE = "total_revenue"
    RECURRING_REVENUE = "recurring_revenue"
    AVERAGE_REVENUE_PER_USER = "arpu"
    LIFETIME_VALUE = "ltv"
    CHURN_RATE = "churn_rate"
    REVENUE_GROWTH = "revenue_growth"


@dataclass
class BusinessKPI:
    """Business KPI definition"""
    name: str
    metric_type: BusinessMetricType
    current_value: float
    target_value: float
    previous_value: Optional[float] = None
    unit: str = "number"
    trend: str = "stable"  # up, down, stable
    variance_percentage: float = 0.0
    calculation_method: str = ""
    data_sources: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    confidence_score: float = 0.95
    business_impact: str = "medium"  # low, medium, high, critical
    health_status: str = "good"  # excellent, good, warning, critical
    description: str = ""


@dataclass
class CustomerInsight:
    """Customer behavior insight"""
    customer_id: str
    segment: CustomerSegment
    clv_prediction: float
    churn_probability: float
    engagement_score: float
    revenue_contribution: float
    acquisition_date: datetime
    last_activity: datetime
    recommended_actions: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    satisfaction_score: float = 0.0
    support_tickets: int = 0
    feature_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class RevenueAnalysis:
    """Revenue analysis results"""
    current_revenue: float
    projected_revenue: float
    revenue_growth_rate: float
    seasonal_patterns: Dict[str, float]
    revenue_by_segment: Dict[str, float]
    revenue_forecast: List[Tuple[datetime, float]]
    optimization_recommendations: List[str]
    risk_factors: List[str]
    confidence_interval: Tuple[float, float]
    market_share: float = 0.0
    competitive_position: str = "unknown"


@dataclass
class RevenueBreakdown:
    """Revenue breakdown analysis"""
    total_revenue: float
    revenue_by_platform: Dict[str, float]
    revenue_by_content_type: Dict[str, float]
    revenue_by_tenant: Dict[str, float]
    growth_rate: float
    forecast: Dict[str, float]
    currency: str = "EUR"
    recurring_revenue: float = 0.0
    one_time_revenue: float = 0.0
    subscription_revenue: float = 0.0
    transaction_revenue: float = 0.0


@dataclass
class MarketAnalysis:
    """Market and competitive analysis"""
    market_size: float
    market_growth_rate: float
    competitive_position: str
    market_share: float
    competitive_advantages: List[str]
    threats: List[str]
    opportunities: List[str]
    trend_analysis: Dict[str, Any]
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    market_segments: List[str] = field(default_factory=list)
    pricing_analysis: Dict[str, float] = field(default_factory=dict)


@dataclass
class BusinessMetrics:
    """Comprehensive business metrics"""
    revenue_metrics: RevenueBreakdown
    customer_metrics: Dict[str, Any]
    operational_metrics: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    growth_metrics: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    content_metrics: Dict[str, Any]
    ai_performance_metrics: Dict[str, Any]


class BusinessIntelligenceEngine:
    """
    Advanced Business Intelligence Engine
    
    Features:
    - Real-time business metrics tracking and analysis
    - Predictive analytics for revenue and customer behavior
    - Customer segmentation and lifecycle analysis
    - Churn prediction and retention optimization
    - Revenue forecasting and optimization
    - Competitive analysis and market insights
    - KPI monitoring with automated alerts
    - ML-powered recommendations and insights
    - ROI analysis and cost optimization
    - Performance benchmarking and trend analysis
    """
    
    def __init__(self, config: Optional[MetricsConfiguration] = None):
        self.config = config or get_metrics_config()
        self.logger = logger
        
        # Core components
        self.redis_manager = RedisManager()
        self.security_manager = SecurityManager()
        
        # ML models
        self.revenue_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.churn_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.segmentation_model = KMeans(n_clusters=8, random_state=42)
        
        # Data preprocessing
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Business metrics cache
        self.kpi_cache: Dict[str, BusinessKPI] = {}
        self.customer_insights_cache: Dict[str, CustomerInsight] = {}
        
        # Analysis tasks
        self._analysis_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        
        # Business intelligence data
        self.revenue_data = []
        self.customer_data = []
        self.market_data = {}
        
        # Business targets and thresholds
        self.business_targets = self._initialize_business_targets()
        self.kpi_thresholds = self._initialize_kpi_thresholds()
        
        # Initialize ML models
        self._initialize_ml_models()
    
    async def start(self) -> None:
        """Start business intelligence engine"""
        try:
            if self._running:
                self.logger.warning("Business Intelligence Engine already running")
                return
            
            self._running = True
            
            # Initialize security
            await self.security_manager.initialize()
            
            # Start analysis tasks
            self._analysis_tasks["revenue_analysis"] = asyncio.create_task(
                self._revenue_analysis_loop()
            )
            
            self._analysis_tasks["customer_analysis"] = asyncio.create_task(
                self._customer_analysis_loop()
            )
            
            self._analysis_tasks["kpi_monitoring"] = asyncio.create_task(
                self._kpi_monitoring_loop()
            )
            
            self._analysis_tasks["market_analysis"] = asyncio.create_task(
                self._market_analysis_loop()
            )
            
            self._analysis_tasks["predictive_modeling"] = asyncio.create_task(
                self._predictive_modeling_loop()
            )
            
            # Load historical data for ML models
            await self._load_historical_data()
            
            # Train initial models
            await self._train_ml_models()
            
            self.logger.info("Advanced Business Intelligence Engine started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting BI engine: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop business intelligence engine"""
        try:
            self._running = False
            
            # Stop all analysis tasks
            for task_name, task in self._analysis_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Save ML models
            await self._save_ml_models()
            
            # Save cached insights
            await self._save_insights_cache()
            
            self.logger.info("Business Intelligence Engine stopped gracefully")
            
        except Exception as e:
            self.logger.error(f"Error stopping BI engine: {e}")
    
    async def calculate_business_kpis(
        self,
        tenant_id: Optional[str] = None,
        time_range: str = "30d"
    ) -> Dict[str, BusinessKPI]:
        """Calculate comprehensive business KPIs"""
        try:
            kpis = {}
            
            # Revenue KPIs
            revenue_kpi = await self._calculate_revenue_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.REVENUE.value] = revenue_kpi
            
            # Customer KPIs
            cac_kpi = await self._calculate_cac_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.CUSTOMER_ACQUISITION_COST.value] = cac_kpi
            
            clv_kpi = await self._calculate_clv_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.CUSTOMER_LIFETIME_VALUE.value] = clv_kpi
            
            churn_kpi = await self._calculate_churn_rate_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.CHURN_RATE.value] = churn_kpi
            
            # Engagement KPIs
            engagement_kpi = await self._calculate_engagement_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.ENGAGEMENT_SCORE.value] = engagement_kpi
            
            # User activity KPIs
            dau_kpi = await self._calculate_dau_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.DAU.value] = dau_kpi
            
            mau_kpi = await self._calculate_mau_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.MAU.value] = mau_kpi
            
            # Business performance KPIs
            arpu_kpi = await self._calculate_arpu_kpi(tenant_id, time_range)
            kpis[BusinessMetricType.ARPU.value] = arpu_kpi
            
            # Cache KPIs
            cache_key = f"business_kpis:{tenant_id}:{time_range}"
            await self.redis_manager.set_json(cache_key, {
                k: {
                    "name": v.name,
                    "current_value": v.current_value,
                    "target_value": v.target_value,
                    "trend": v.trend,
                    "variance_percentage": v.variance_percentage,
                    "business_impact": v.business_impact,
                    "health_status": v.health_status,
                    "last_updated": v.last_updated.isoformat()
                }
                for k, v in kpis.items()
            }, expire=3600)
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Error calculating business KPIs: {e}")
            return {}
    
    async def analyze_customer_behavior(
        self,
        tenant_id: Optional[str] = None,
        analysis_type: AnalysisType = AnalysisType.DESCRIPTIVE
    ) -> Dict[str, Any]:
        """Analyze customer behavior patterns"""
        try:
            # Get customer data
            customer_data = await self._get_customer_data(tenant_id)
            
            if not customer_data:
                return {"error": "No customer data available"}
            
            analysis_results = {
                "analysis_type": analysis_type.value,
                "tenant_id": tenant_id,
                "total_customers": len(customer_data),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            if analysis_type == AnalysisType.DESCRIPTIVE:
                analysis_results.update(await self._descriptive_customer_analysis(customer_data))
            
            elif analysis_type == AnalysisType.PREDICTIVE:
                analysis_results.update(await self._predictive_customer_analysis(customer_data))
            
            elif analysis_type == AnalysisType.SEGMENTATION:
                analysis_results.update(await self._customer_segmentation_analysis(customer_data))
            
            elif analysis_type == AnalysisType.COHORT:
                analysis_results.update(await self._cohort_analysis(customer_data))
            
            elif analysis_type == AnalysisType.FUNNEL:
                analysis_results.update(await self._funnel_analysis(customer_data))
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing customer behavior: {e}")
            return {"error": str(e)}
    
    async def predict_revenue(
        self,
        tenant_id: Optional[str] = None,
        forecast_days: int = 30
    ) -> RevenueAnalysis:
        """Predict revenue using ML models"""
        try:
            # Get historical revenue data
            revenue_data = await self._get_revenue_data(tenant_id)
            
            if len(revenue_data) < 30:  # Need minimum data for prediction
                raise ValueError("Insufficient data for revenue prediction")
            
            # Prepare data for ML model
            df = pd.DataFrame(revenue_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Feature engineering
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['day_of_month'] = df['date'].dt.day
            df['revenue_lag_1'] = df['revenue'].shift(1)
            df['revenue_lag_7'] = df['revenue'].shift(7)
            df['revenue_ma_7'] = df['revenue'].rolling(window=7).mean()
            
            # Remove NaN values
            df = df.dropna()
            
            # Prepare features and target
            features = ['day_of_week', 'month', 'day_of_month', 'revenue_lag_1', 
                       'revenue_lag_7', 'revenue_ma_7']
            X = df[features]
            y = df['revenue']
            
            # Train model
            self.revenue_model.fit(X, y)
            
            # Generate predictions
            predictions = []
            last_date = df['date'].max()
            
            for i in range(forecast_days):
                future_date = last_date + timedelta(days=i+1)
                
                # Create features for prediction
                future_features = [
                    future_date.weekday(),
                    future_date.month,
                    future_date.day,
                    df['revenue'].iloc[-1] if i == 0 else predictions[-1],
                    df['revenue'].iloc[-7] if len(df) >= 7 else df['revenue'].mean(),
                    df['revenue'].tail(7).mean()
                ]
                
                # Predict
                predicted_revenue = self.revenue_model.predict([future_features])[0]
                predictions.append(predicted_revenue)
            
            # Calculate current metrics
            current_revenue = df['revenue'].tail(30).sum()
            projected_revenue = sum(predictions)
            growth_rate = ((projected_revenue - current_revenue) / current_revenue) * 100
            
            # Seasonal analysis
            seasonal_patterns = await self._analyze_seasonal_patterns(df)
            
            # Revenue by segment
            revenue_by_segment = await self._calculate_revenue_by_segment(tenant_id)
            
            # Generate recommendations
            optimization_recommendations = await self._generate_revenue_optimization_recommendations(
                df, predictions
            )
            
            return RevenueAnalysis(
                current_revenue=current_revenue,
                projected_revenue=projected_revenue,
                revenue_growth_rate=growth_rate,
                seasonal_patterns=seasonal_patterns,
                revenue_by_segment=revenue_by_segment,
                revenue_forecast=[(last_date + timedelta(days=i+1), pred) 
                                 for i, pred in enumerate(predictions)],
                optimization_recommendations=optimization_recommendations,
                risk_factors=await self._identify_revenue_risk_factors(df),
                confidence_interval=(projected_revenue * 0.85, projected_revenue * 1.15)
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting revenue: {e}")
            raise
    
    async def predict_customer_churn(
        self,
        tenant_id: Optional[str] = None
    ) -> Dict[str, CustomerInsight]:
        """Predict customer churn using ML models"""
        try:
            # Get customer data
            customer_data = await self._get_customer_data(tenant_id)
            
            if not customer_data:
                return {}
            
            insights = {}
            
            for customer in customer_data:
                try:
                    # Extract features for churn prediction
                    features = await self._extract_churn_features(customer)
                    
                    # Predict churn probability
                    churn_probability = self.churn_model.predict_proba([features])[0][1]
                    
                    # Calculate CLV
                    clv_prediction = await self._predict_customer_clv(customer)
                    
                    # Calculate engagement score
                    engagement_score = await self._calculate_engagement_score(customer)
                    
                    # Determine customer segment
                    segment = await self._determine_customer_segment(customer, churn_probability)
                    
                    # Generate recommendations
                    recommendations = await self._generate_customer_recommendations(
                        customer, churn_probability, segment
                    )
                    
                    # Identify risk factors
                    risk_factors = await self._identify_customer_risk_factors(customer)
                    
                    # Identify opportunities
                    opportunities = await self._identify_customer_opportunities(customer)
                    
                    insight = CustomerInsight(
                        customer_id=customer['customer_id'],
                        segment=segment,
                        clv_prediction=clv_prediction,
                        churn_probability=churn_probability,
                        engagement_score=engagement_score,
                        revenue_contribution=customer.get('total_revenue', 0),
                        acquisition_date=datetime.fromisoformat(customer['acquisition_date']),
                        last_activity=datetime.fromisoformat(customer['last_activity']),
                        recommended_actions=recommendations,
                        risk_factors=risk_factors,
                        opportunities=opportunities
                    )
                    
                    insights[customer['customer_id']] = insight
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing customer {customer.get('customer_id')}: {e}")
                    continue
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error predicting customer churn: {e}")
            return {}
    
    async def analyze_revenue_performance(
        self,
        time_period: timedelta = timedelta(days=30),
        tenant_id: Optional[str] = None
    ) -> RevenueBreakdown:
        """Analyze revenue performance and trends"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_period
            
            # Get revenue data
            revenue_data = await self._get_revenue_data(start_time, end_time, tenant_id)
            
            if not revenue_data:
                return self._create_empty_revenue_breakdown()
            
            # Calculate total revenue
            total_revenue = sum(data["amount"] for data in revenue_data)
            
            # Revenue by platform
            revenue_by_platform = {}
            for data in revenue_data:
                platform = data.get("platform", "unknown")
                revenue_by_platform[platform] = revenue_by_platform.get(platform, 0) + data["amount"]
            
            # Revenue by content type
            revenue_by_content_type = {}
            for data in revenue_data:
                content_type = data.get("content_type", "unknown")
                revenue_by_content_type[content_type] = revenue_by_content_type.get(content_type, 0) + data["amount"]
            
            # Revenue by tenant (if not filtered)
            revenue_by_tenant = {}
            if not tenant_id:
                for data in revenue_data:
                    tenant = data.get("tenant_id", "unknown")
                    revenue_by_tenant[tenant] = revenue_by_tenant.get(tenant, 0) + data["amount"]
            
            # Calculate growth rate
            growth_rate = await self._calculate_revenue_growth_rate(tenant_id, time_period)
            
            # Generate forecast
            forecast = await self._forecast_revenue(revenue_data, days=30)
            
            return RevenueBreakdown(
                total_revenue=total_revenue,
                revenue_by_platform=revenue_by_platform,
                revenue_by_content_type=revenue_by_content_type,
                revenue_by_tenant=revenue_by_tenant,
                growth_rate=growth_rate,
                forecast=forecast
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing revenue performance: {e}")
            return self._create_empty_revenue_breakdown()
    
    async def analyze_user_engagement(
        self,
        time_period: timedelta = timedelta(days=30),
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze user engagement metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_period
            
            # Get user activity data
            activity_data = await self._get_user_activity_data(start_time, end_time, tenant_id)
            
            if not activity_data:
                return {"error": "No user activity data available"}
            
            # Calculate engagement metrics
            total_users = len(set(data["user_id"] for data in activity_data))
            total_sessions = len(activity_data)
            total_duration = sum(data.get("duration", 0) for data in activity_data)
            
            # Daily active users
            daily_active_users = self._calculate_daily_active_users(activity_data)
            
            # Session duration analysis
            session_durations = [data.get("duration", 0) for data in activity_data if data.get("duration")]
            avg_session_duration = statistics.mean(session_durations) if session_durations else 0
            
            # Activity type breakdown
            activity_breakdown = {}
            for data in activity_data:
                activity_type = data.get("activity_type", "unknown")
                activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
            
            # Engagement trends
            engagement_trend = await self._calculate_engagement_trend(tenant_id, time_period)
            
            return {
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": time_period.days
                },
                "total_users": total_users,
                "total_sessions": total_sessions,
                "total_duration_hours": total_duration / 3600,
                "average_session_duration_minutes": avg_session_duration / 60,
                "daily_active_users": daily_active_users,
                "activity_breakdown": activity_breakdown,
                "engagement_trend": engagement_trend,
                "user_retention": await self._calculate_user_retention(tenant_id, time_period)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user engagement: {e}")
            return {}
    
    async def analyze_content_performance(
        self,
        time_period: timedelta = timedelta(days=30),
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze content performance metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_period
            
            # Get content data
            content_data = await self._get_content_data(start_time, end_time, tenant_id)
            
            if not content_data:
                return {"error": "No content data available"}
            
            # Content creation metrics
            total_content = len(content_data)
            content_by_type = {}
            for data in content_data:
                content_type = data.get("content_type", "unknown")
                content_by_type[content_type] = content_by_type.get(content_type, 0) + 1
            
            # Content protection metrics
            protection_data = await self._get_content_protection_data(start_time, end_time, tenant_id)
            total_fingerprints = len(protection_data) if protection_data else 0
            matches_detected = len([d for d in protection_data if d.get("match_detected")]) if protection_data else 0
            
            # Content monetization
            content_revenue = await self._get_content_revenue_data(start_time, end_time, tenant_id)
            revenue_per_content = {}
            for revenue in content_revenue:
                content_id = revenue.get("content_id")
                if content_id:
                    revenue_per_content[content_id] = revenue_per_content.get(content_id, 0) + revenue["amount"]
            
            # Performance trends
            content_trend = await self._calculate_content_performance_trend(tenant_id, time_period)
            
            return {
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": time_period.days
                },
                "content_creation": {
                    "total_content": total_content,
                    "content_by_type": content_by_type,
                    "daily_average": total_content / max(time_period.days, 1)
                },
                "content_protection": {
                    "total_fingerprints": total_fingerprints,
                    "matches_detected": matches_detected,
                    "protection_rate": (matches_detected / max(total_fingerprints, 1)) * 100
                },
                "content_monetization": {
                    "revenue_generating_content": len(revenue_per_content),
                    "total_content_revenue": sum(revenue_per_content.values()),
                    "average_revenue_per_content": statistics.mean(revenue_per_content.values()) if revenue_per_content else 0
                },
                "performance_trend": content_trend
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing content performance: {e}")
            return {}
    
    async def calculate_business_kpis(
        self,
        tenant_id: Optional[str] = None
    ) -> List[BusinessKPI]:
        """Calculate key business KPIs"""
        try:
            kpis = []
            
            # Revenue KPIs
            revenue_analysis = await self.analyze_revenue_performance(timedelta(days=30), tenant_id)
            
            # Total Revenue
            revenue_kpi = BusinessKPI(
                name="Monthly Revenue",
                current_value=revenue_analysis.total_revenue,
                target_value=self.business_targets.get("monthly_revenue", 100000),
                trend=self._determine_trend(revenue_analysis.growth_rate),
                health_status=self._determine_health_status(
                    revenue_analysis.total_revenue,
                    self.business_targets.get("monthly_revenue", 100000)
                ),
                unit="EUR",
                description="Total revenue generated in the last 30 days"
            )
            kpis.append(revenue_kpi)
            
            # User Engagement KPIs
            engagement_data = await self.analyze_user_engagement(timedelta(days=30), tenant_id)
            
            if engagement_data and "total_users" in engagement_data:
                user_engagement_kpi = BusinessKPI(
                    name="Monthly Active Users",
                    current_value=engagement_data["total_users"],
                    target_value=self.business_targets.get("monthly_active_users", 10000),
                    health_status=self._determine_health_status(
                        engagement_data["total_users"],
                        self.business_targets.get("monthly_active_users", 10000)
                    ),
                    unit="users",
                    description="Number of active users in the last 30 days"
                )
                kpis.append(user_engagement_kpi)
            
            # Content Performance KPIs
            content_data = await self.analyze_content_performance(timedelta(days=30), tenant_id)
            
            if content_data and "content_creation" in content_data:
                content_kpi = BusinessKPI(
                    name="Content Creation Rate",
                    current_value=content_data["content_creation"]["daily_average"],
                    target_value=self.business_targets.get("daily_content_target", 100),
                    health_status=self._determine_health_status(
                        content_data["content_creation"]["daily_average"],
                        self.business_targets.get("daily_content_target", 100)
                    ),
                    unit="content/day",
                    description="Average content pieces created per day"
                )
                kpis.append(content_kpi)
            
            # AI Model Performance KPI
            ai_performance = await self._get_ai_performance_metrics(tenant_id)
            if ai_performance:
                ai_kpi = BusinessKPI(
                    name="AI Model Accuracy",
                    current_value=ai_performance.get("average_accuracy", 0) * 100,
                    target_value=90.0,
                    health_status=self._determine_health_status(
                        ai_performance.get("average_accuracy", 0) * 100,
                        90.0
                    ),
                    unit="percent",
                    description="Average accuracy of AI models"
                )
                kpis.append(ai_kpi)
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Error calculating business KPIs: {e}")
            return []
    
    async def generate_business_report(
        self,
        report_type: str = "comprehensive",
        time_period: timedelta = timedelta(days=30),
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive business report"""
        try:
            report = {
                "report_type": report_type,
                "tenant_id": tenant_id,
                "time_period": {
                    "days": time_period.days,
                    "start": (datetime.utcnow() - time_period).isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "generated_at": datetime.utcnow().isoformat(),
                "sections": {}
            }
            
            # Revenue Analysis
            revenue_analysis = await self.analyze_revenue_performance(time_period, tenant_id)
            report["sections"]["revenue"] = {
                "total_revenue": revenue_analysis.total_revenue,
                "growth_rate": revenue_analysis.growth_rate,
                "revenue_by_platform": revenue_analysis.revenue_by_platform,
                "revenue_by_content_type": revenue_analysis.revenue_by_content_type,
                "forecast": revenue_analysis.forecast
            }
            
            # User Engagement
            engagement_data = await self.analyze_user_engagement(time_period, tenant_id)
            report["sections"]["user_engagement"] = engagement_data
            
            # Content Performance
            content_data = await self.analyze_content_performance(time_period, tenant_id)
            report["sections"]["content_performance"] = content_data
            
            # Business KPIs
            kpis = await self.calculate_business_kpis(tenant_id)
            report["sections"]["kpis"] = [
                {
                    "name": kpi.name,
                    "current_value": kpi.current_value,
                    "target_value": kpi.target_value,
                    "trend": kpi.trend,
                    "health_status": kpi.health_status,
                    "unit": kpi.unit,
                    "description": kpi.description
                }
                for kpi in kpis
            ]
            
            # Market Analysis (if applicable)
            if not tenant_id:  # Global analysis
                market_analysis = await self._analyze_market_trends()
                report["sections"]["market_analysis"] = market_analysis
            
            # Executive Summary
            report["executive_summary"] = self._generate_executive_summary(report)
            
            # Recommendations
            report["recommendations"] = await self._generate_business_recommendations(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating business report: {e}")
            return {}
    
    async def forecast_business_metrics(
        self,
        metric_type: BusinessMetricType,
        forecast_days: int = 30,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Forecast business metrics using machine learning"""
        try:
            # Get historical data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=90)  # 3 months of history
            
            if metric_type == BusinessMetricType.REVENUE:
                historical_data = await self._get_revenue_data(start_time, end_time, tenant_id)
                values = [data["amount"] for data in historical_data]
            elif metric_type == BusinessMetricType.USER_ENGAGEMENT:
                historical_data = await self._get_user_activity_data(start_time, end_time, tenant_id)
                # Daily user counts
                daily_users = self._calculate_daily_active_users(historical_data)
                values = list(daily_users.values())
            else:
                return {"error": f"Forecasting not implemented for {metric_type.value}"}
            
            if len(values) < 10:
                return {"error": "Insufficient historical data for forecasting"}
            
            # Prepare data for ML model
            X = np.array(range(len(values))).reshape(-1, 1)
            y = np.array(values)
            
            # Use polynomial features for better fit
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            
            # Train model
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Generate forecast
            future_X = np.array(range(len(values), len(values) + forecast_days)).reshape(-1, 1)
            future_X_poly = poly_features.transform(future_X)
            forecast_values = model.predict(future_X_poly)
            
            # Calculate confidence intervals (simplified)
            residuals = y - model.predict(X_poly)
            std_error = np.std(residuals)
            
            forecast_data = []
            for i, value in enumerate(forecast_values):
                forecast_date = end_time + timedelta(days=i+1)
                forecast_data.append({
                    "date": forecast_date.isoformat(),
                    "predicted_value": max(0, value),  # Ensure non-negative
                    "confidence_interval": {
                        "lower": max(0, value - 2 * std_error),
                        "upper": value + 2 * std_error
                    }
                })
            
            return {
                "metric_type": metric_type.value,
                "tenant_id": tenant_id,
                "forecast_days": forecast_days,
                "historical_data_points": len(values),
                "model_accuracy": model.score(X_poly, y),
                "forecast": forecast_data,
                "trends": {
                    "direction": "increasing" if forecast_values[-1] > values[-1] else "decreasing",
                    "growth_rate": ((forecast_values[-1] - values[-1]) / values[-1] * 100) if values[-1] != 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error forecasting business metrics: {e}")
            return {}
    
    async def compare_tenant_performance(
        self,
        tenant_ids: List[str],
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Compare performance across multiple tenants"""
        try:
            comparison = {
                "time_period": {
                    "days": time_period.days,
                    "start": (datetime.utcnow() - time_period).isoformat(),
                    "end": datetime.utcnow().isoformat()
                },
                "tenant_performance": {}
            }
            
            tenant_data = {}
            
            for tenant_id in tenant_ids:
                # Get key metrics for each tenant
                revenue = await self.analyze_revenue_performance(time_period, tenant_id)
                engagement = await self.analyze_user_engagement(time_period, tenant_id)
                content = await self.analyze_content_performance(time_period, tenant_id)
                
                tenant_data[tenant_id] = {
                    "revenue": {
                        "total": revenue.total_revenue,
                        "growth_rate": revenue.growth_rate
                    },
                    "engagement": {
                        "total_users": engagement.get("total_users", 0),
                        "total_sessions": engagement.get("total_sessions", 0)
                    },
                    "content": {
                        "total_content": content.get("content_creation", {}).get("total_content", 0),
                        "revenue_generating": content.get("content_monetization", {}).get("revenue_generating_content", 0)
                    }
                }
            
            comparison["tenant_performance"] = tenant_data
            
            # Rankings
            comparison["rankings"] = {
                "by_revenue": sorted(tenant_ids, key=lambda t: tenant_data[t]["revenue"]["total"], reverse=True),
                "by_users": sorted(tenant_ids, key=lambda t: tenant_data[t]["engagement"]["total_users"], reverse=True),
                "by_content": sorted(tenant_ids, key=lambda t: tenant_data[t]["content"]["total_content"], reverse=True)
            }
            
            # Performance gaps
            revenues = [tenant_data[t]["revenue"]["total"] for t in tenant_ids]
            comparison["performance_gaps"] = {
                "revenue_gap": max(revenues) - min(revenues) if revenues else 0,
                "top_performer": tenant_ids[0] if tenant_ids else None,
                "improvement_opportunities": [
                    t for t in tenant_ids
                    if tenant_data[t]["revenue"]["total"] < statistics.mean(revenues)
                ] if len(revenues) > 1 else []
            }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing tenant performance: {e}")
            return {}
    
    async def _get_revenue_data(
        self,
        start_time: datetime,
        end_time: datetime,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get revenue data from storage"""
        try:
            # This would fetch from actual revenue tracking storage
            # Placeholder implementation
            revenue_data = []
            
            current_time = start_time
            while current_time <= end_time:
                timestamp_key = current_time.strftime("%Y%m%d%H%M")
                
                if tenant_id:
                    key = f"metrics:tenant:{tenant_id}:revenue_tracked_total:{timestamp_key}"
                else:
                    key = f"metrics:global:revenue_tracked_total:{timestamp_key}"
                
                data = await self.redis_manager.lrange(key, 0, -1)
                
                for item in data:
                    try:
                        metric_data = json.loads(item)
                        if start_time <= datetime.fromisoformat(metric_data["timestamp"]) <= end_time:
                            revenue_data.append({
                                "amount": metric_data["value"],
                                "platform": metric_data.get("labels", {}).get("platform", "unknown"),
                                "content_type": metric_data.get("labels", {}).get("content_type", "unknown"),
                                "currency": metric_data.get("labels", {}).get("currency", "EUR"),
                                "tenant_id": metric_data.get("tenant_id"),
                                "timestamp": metric_data["timestamp"]
                            })
                    except Exception as e:
                        self.logger.error(f"Error parsing revenue data: {e}")
                
                current_time += timedelta(minutes=1)
            
            return revenue_data
            
        except Exception as e:
            self.logger.error(f"Error getting revenue data: {e}")
            return []
    
    async def _get_user_activity_data(
        self,
        start_time: datetime,
        end_time: datetime,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user activity data"""
        try:
            # This would fetch from actual user activity storage
            # Placeholder implementation
            activity_data = []
            
            current_time = start_time
            while current_time <= end_time:
                timestamp_key = current_time.strftime("%Y%m%d%H%M")
                
                if tenant_id:
                    key = f"metrics:tenant:{tenant_id}:user_activities_total:{timestamp_key}"
                else:
                    key = f"metrics:global:user_activities_total:{timestamp_key}"
                
                data = await self.redis_manager.lrange(key, 0, -1)
                
                for item in data:
                    try:
                        metric_data = json.loads(item)
                        if start_time <= datetime.fromisoformat(metric_data["timestamp"]) <= end_time:
                            activity_data.append({
                                "user_id": metric_data.get("metadata", {}).get("user_id", "unknown"),
                                "activity_type": metric_data.get("labels", {}).get("activity_type", "unknown"),
                                "duration": metric_data.get("metadata", {}).get("duration", 0),
                                "timestamp": metric_data["timestamp"]
                            })
                    except Exception as e:
                        self.logger.error(f"Error parsing activity data: {e}")
                
                current_time += timedelta(minutes=1)
            
            return activity_data
            
        except Exception as e:
            self.logger.error(f"Error getting user activity data: {e}")
            return []
    
    def _calculate_daily_active_users(self, activity_data: List[Dict]) -> Dict[str, int]:
        """Calculate daily active users from activity data"""
        try:
            daily_users = {}
            
            for activity in activity_data:
                date = datetime.fromisoformat(activity["timestamp"]).date().isoformat()
                user_id = activity["user_id"]
                
                if date not in daily_users:
                    daily_users[date] = set()
                
                daily_users[date].add(user_id)
            
            # Convert sets to counts
            return {date: len(users) for date, users in daily_users.items()}
            
        except Exception as e:
            self.logger.error(f"Error calculating daily active users: {e}")
            return {}
    
    def _create_empty_revenue_breakdown(self) -> RevenueBreakdown:
        """Create empty revenue breakdown"""
        return RevenueBreakdown(
            total_revenue=0.0,
            revenue_by_platform={},
            revenue_by_content_type={},
            revenue_by_tenant={},
            growth_rate=0.0,
            forecast={}
        )
    
    def _determine_trend(self, growth_rate: float) -> str:
        """Determine trend from growth rate"""
        if growth_rate > 0.05:  # 5% growth
            return "increasing"
        elif growth_rate < -0.05:  # 5% decline
            return "decreasing"
        else:
            return "stable"
    
    def _determine_health_status(self, current_value: float, target_value: float) -> str:
        """Determine health status from current vs target value"""
        ratio = current_value / target_value if target_value > 0 else 0
        
        if ratio >= 1.2:  # 120% of target
            return "excellent"
        elif ratio >= 1.0:  # 100% of target
            return "good"
        elif ratio >= 0.8:  # 80% of target
            return "warning"
        else:
            return "critical"
    
    def _initialize_business_targets(self) -> Dict[str, float]:
        """Initialize business targets"""
        return {
            "monthly_revenue": 100000.0,  # EUR
            "monthly_active_users": 10000,
            "daily_content_target": 100,
            "user_retention_rate": 0.85,  # 85%
            "content_monetization_rate": 0.15,  # 15%
            "ai_model_accuracy": 0.90  # 90%
        }
    
    def _initialize_kpi_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize KPI thresholds"""
        return {
            "revenue": {
                "excellent": 1.2,
                "good": 1.0,
                "warning": 0.8,
                "critical": 0.6
            },
            "users": {
                "excellent": 1.2,
                "good": 1.0,
                "warning": 0.8,
                "critical": 0.6
            },
            "content": {
                "excellent": 1.2,
                "good": 1.0,
                "warning": 0.8,
                "critical": 0.6
            }
        }
