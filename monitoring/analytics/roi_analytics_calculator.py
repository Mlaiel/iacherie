"""
🔍 MONITORING ANALYTICS - ROI Analytics Calculator
Advanced ROI calculation and analysis for Ainflue creator ecosystem
Business Analytics + ML Engineer Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ROICategory(Enum):
    """ROI calculation categories"""
    CREATOR_ACQUISITION = "creator_acquisition"
    CONTENT_PROMOTION = "content_promotion"
    PLATFORM_FEATURES = "platform_features"
    MARKETING_CAMPAIGNS = "marketing_campaigns"
    INFRASTRUCTURE = "infrastructure"
    AI_DEVELOPMENT = "ai_development"
    COLLABORATION_TOOLS = "collaboration_tools"
    MONETIZATION_FEATURES = "monetization_features"

class InvestmentType(Enum):
    """Types of investments to track"""
    DEVELOPMENT_COST = "development_cost"
    MARKETING_SPEND = "marketing_spend"
    INFRASTRUCTURE_COST = "infrastructure_cost"
    PERSONNEL_COST = "personnel_cost"
    TOOLS_AND_LICENSES = "tools_and_licenses"
    CLOUD_SERVICES = "cloud_services"
    THIRD_PARTY_APIs = "third_party_apis"
    EQUIPMENT = "equipment"

class RevenueStream(Enum):
    """Revenue streams to track"""
    SUBSCRIPTION_FEES = "subscription_fees"
    TRANSACTION_FEES = "transaction_fees"
    PREMIUM_FEATURES = "premium_features"
    ADVERTISING_REVENUE = "advertising_revenue"
    PARTNERSHIP_REVENUE = "partnership_revenue"
    API_LICENSING = "api_licensing"
    DATA_ANALYTICS = "data_analytics"
    CONTENT_LICENSING = "content_licensing"

@dataclass
class Investment:
    """Investment record"""
    investment_id: str
    category: ROICategory
    investment_type: InvestmentType
    amount: Decimal
    date: datetime
    description: str
    expected_duration_months: int
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Revenue:
    """Revenue record"""
    revenue_id: str
    revenue_stream: RevenueStream
    amount: Decimal
    date: datetime
    attribution_sources: List[str] = field(default_factory=list)
    creator_id: Optional[str] = None
    campaign_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ROICalculation:
    """ROI calculation result"""
    roi_id: str
    category: ROICategory
    time_period: str
    total_investment: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: float
    payback_period_months: Optional[float]
    npv: Optional[Decimal]
    irr: Optional[float]
    confidence_score: float
    calculation_timestamp: datetime
    breakdown: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ROIForecast:
    """ROI forecast result"""
    category: ROICategory
    forecast_period_months: int
    predicted_roi: float
    confidence_interval: Tuple[float, float]
    expected_revenue: Decimal
    expected_investment: Decimal
    risk_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class ROIAnalyticsCalculator:
    """
    💰 Advanced ROI Analytics Calculator for Ainflue Platform
    
    Comprehensive ROI analysis with:
    - Multi-category ROI tracking and calculation
    - Advanced financial metrics (NPV, IRR, Payback Period)
    - ML-powered ROI forecasting and prediction
    - Attribution-based revenue mapping
    - Cross-category investment optimization
    - Risk-adjusted ROI calculations
    - Real-time ROI monitoring and alerting
    """
    
    def __init__(self, db_url -> None: str, discount_rate -> None: float = 0.1) -> None:
        """Initialize ROI analytics calculator"""
        self.db_url = db_url
        self.discount_rate = discount_rate  # For NPV calculations
        
        # Data storage
        self.investments: List[Investment] = []
        self.revenues: List[Revenue] = []
        self.roi_calculations: List[ROICalculation] = []
        self.roi_forecasts: List[ROIForecast] = []
        
        # ML models for forecasting
        self.revenue_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.investment_predictor = LinearRegression()
        self.scaler = StandardScaler()
        
        # ROI calculation cache
        self.roi_cache: Dict[str, ROICalculation] = {}
        
        # Configuration
        self.min_data_points = 10
        self.confidence_threshold = 0.7
        
        logger.info("💰 ROI Analytics Calculator initialized")

    async def record_investment(
        self,
        category: ROICategory,
        investment_type: InvestmentType,
        amount: Union[float, Decimal],
        description: str,
        expected_duration_months: int = 12,
        date: datetime = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        📊 Record new investment
        
        Track investments across different categories
        """
        try:
            if date is None:
                date = datetime.now()
            
            if tags is None:
                tags = []
            
            if metadata is None:
                metadata = {}
            
            investment_id = f"inv_{category.value}_{date.strftime('%Y%m%d_%H%M%S')}"
            
            investment = Investment(
                investment_id=investment_id,
                category=category,
                investment_type=investment_type,
                amount=Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                date=date,
                description=description,
                expected_duration_months=expected_duration_months,
                tags=tags,
                metadata=metadata
            )
            
            self.investments.append(investment)
            
            logger.info(f"📊 Recorded investment: {investment_id} - ${amount} for {category.value}")
            return investment_id
            
        except Exception as e:
            logger.error(f"❌ Error recording investment: {e}")
            raise

    async def record_revenue(
        self,
        revenue_stream: RevenueStream,
        amount: Union[float, Decimal],
        attribution_sources: List[str] = None,
        creator_id: str = None,
        campaign_id: str = None,
        date: datetime = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        💰 Record new revenue
        
        Track revenue with attribution to investment sources
        """
        try:
            if date is None:
                date = datetime.now()
            
            if attribution_sources is None:
                attribution_sources = []
            
            if metadata is None:
                metadata = {}
            
            revenue_id = f"rev_{revenue_stream.value}_{date.strftime('%Y%m%d_%H%M%S')}"
            
            revenue = Revenue(
                revenue_id=revenue_id,
                revenue_stream=revenue_stream,
                amount=Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                date=date,
                attribution_sources=attribution_sources,
                creator_id=creator_id,
                campaign_id=campaign_id,
                metadata=metadata
            )
            
            self.revenues.append(revenue)
            
            logger.info(f"💰 Recorded revenue: {revenue_id} - ${amount} from {revenue_stream.value}")
            return revenue_id
            
        except Exception as e:
            logger.error(f"❌ Error recording revenue: {e}")
            raise

    async def calculate_category_roi(
        self,
        category: ROICategory,
        start_date: datetime,
        end_date: datetime,
        include_forecasting: bool = True
    ) -> ROICalculation:
        """
        📈 Calculate ROI for specific category
        
        Comprehensive ROI analysis with advanced metrics
        """
        try:
            logger.info(f"📈 Calculating ROI for {category.value}: {start_date} to {end_date}")
            
            # Get investments for category and period
            category_investments = [
                inv for inv in self.investments
                if inv.category == category and start_date <= inv.date <= end_date
            ]
            
            # Get attributed revenues for category
            category_revenues = await self._get_attributed_revenues(
                category, start_date, end_date
            )
            
            # Calculate totals
            total_investment = sum(inv.amount for inv in category_investments)
            total_revenue = sum(rev.amount for rev in category_revenues)
            net_profit = total_revenue - total_investment
            
            # Calculate ROI percentage
            roi_percentage = float(
                (net_profit / total_investment * 100) if total_investment > 0 else 0
            )
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(
                category_investments, category_revenues
            )
            
            # Calculate NPV
            npv = await self._calculate_npv(category_investments, category_revenues)
            
            # Calculate IRR
            irr = await self._calculate_irr(category_investments, category_revenues)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                len(category_investments), len(category_revenues), roi_percentage
            )
            
            # Create detailed breakdown
            breakdown = {
                'investment_breakdown': self._create_investment_breakdown(category_investments),
                'revenue_breakdown': self._create_revenue_breakdown(category_revenues),
                'monthly_trend': await self._calculate_monthly_roi_trend(
                    category, start_date, end_date
                ),
                'comparison_metrics': {
                    'roi_vs_benchmark': await self._compare_to_benchmark(category, roi_percentage),
                    'performance_quartile': await self._calculate_performance_quartile(category, roi_percentage)
                }
            }
            
            # Create ROI calculation
            roi_calculation = ROICalculation(
                roi_id=f"roi_{category.value}_{start_date.strftime('%Y%m')}_{end_date.strftime('%Y%m')}",
                category=category,
                time_period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                total_investment=total_investment,
                total_revenue=total_revenue,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period,
                npv=npv,
                irr=irr,
                confidence_score=confidence_score,
                calculation_timestamp=datetime.now(),
                breakdown=breakdown
            )
            
            self.roi_calculations.append(roi_calculation)
            
            # Cache result
            cache_key = f"{category.value}_{start_date}_{end_date}"
            self.roi_cache[cache_key] = roi_calculation
            
            logger.info(f"✅ ROI calculated: {roi_percentage:.2f}% for {category.value}")
            return roi_calculation
            
        except Exception as e:
            logger.error(f"❌ Error calculating ROI for {category.value}: {e}")
            raise

    async def forecast_roi(
        self,
        category: ROICategory,
        forecast_months: int = 12
    ) -> ROIForecast:
        """
        🔮 Forecast future ROI using ML models
        
        Predict future ROI based on historical patterns
        """
        try:
            logger.info(f"🔮 Forecasting ROI for {category.value} - {forecast_months} months")
            
            # Prepare historical data
            historical_data = await self._prepare_forecasting_data(category)
            
            if len(historical_data) < self.min_data_points:
                logger.warning(f"Insufficient data for forecasting {category.value}")
                return self._create_default_forecast(category, forecast_months)
            
            # Prepare features and targets
            X, y_revenue, y_investment = self._prepare_ml_features(historical_data)
            
            if len(X) < self.min_data_points:
                return self._create_default_forecast(category, forecast_months)
            
            # Train models
            X_scaled = self.scaler.fit_transform(X)
            
            # Revenue prediction model
            self.revenue_predictor.fit(X_scaled, y_revenue)
            revenue_score = self.revenue_predictor.score(X_scaled, y_revenue)
            
            # Investment prediction model
            self.investment_predictor.fit(X_scaled, y_investment)
            investment_score = self.investment_predictor.score(X_scaled, y_investment)
            
            # Generate future features
            future_features = self._generate_future_features(
                historical_data, forecast_months
            )
            future_features_scaled = self.scaler.transform(future_features)
            
            # Make predictions
            predicted_revenue = self.revenue_predictor.predict(future_features_scaled)
            predicted_investment = self.investment_predictor.predict(future_features_scaled)
            
            # Calculate forecast ROI
            total_predicted_revenue = Decimal(str(np.sum(predicted_revenue)))
            total_predicted_investment = Decimal(str(np.sum(predicted_investment)))
            
            predicted_roi = float(
                ((total_predicted_revenue - total_predicted_investment) / 
                 total_predicted_investment * 100) if total_predicted_investment > 0 else 0
            )
            
            # Calculate confidence interval
            confidence_interval = self._calculate_forecast_confidence_interval(
                predicted_roi, revenue_score, investment_score
            )
            
            # Identify risk factors
            risk_factors = await self._identify_roi_risk_factors(category, historical_data)
            
            # Generate recommendations
            recommendations = await self._generate_roi_recommendations(
                category, predicted_roi, risk_factors
            )
            
            forecast = ROIForecast(
                category=category,
                forecast_period_months=forecast_months,
                predicted_roi=predicted_roi,
                confidence_interval=confidence_interval,
                expected_revenue=total_predicted_revenue,
                expected_investment=total_predicted_investment,
                risk_factors=risk_factors,
                recommendations=recommendations
            )
            
            self.roi_forecasts.append(forecast)
            
            logger.info(f"✅ ROI forecast: {predicted_roi:.2f}% for {category.value}")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error forecasting ROI for {category.value}: {e}")
            return self._create_default_forecast(category, forecast_months)

    async def analyze_cross_category_roi(self) -> Dict[str, Any]:
        """
        🔍 Analyze ROI across all categories
        
        Compare performance and identify optimization opportunities
        """
        try:
            logger.info("🔍 Analyzing cross-category ROI performance")
            
            # Calculate ROI for all categories
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Last year
            
            category_rois = {}
            for category in ROICategory:
                try:
                    roi_calc = await self.calculate_category_roi(
                        category, start_date, end_date, include_forecasting=False
                    )
                    category_rois[category.value] = roi_calc
                except Exception as e:
                    logger.warning(f"Could not calculate ROI for {category.value}: {e}")
                    continue
            
            if not category_rois:
                return {}
            
            # Analysis results
            analysis = {
                'analysis_timestamp': datetime.now().isoformat(),
                'category_performance': {},
                'top_performers': [],
                'underperformers': [],
                'roi_distribution': {},
                'optimization_opportunities': [],
                'portfolio_metrics': {},
                'recommendations': []
            }
            
            # Category performance summary
            for category, roi_calc in category_rois.items():
                analysis['category_performance'][category] = {
                    'roi_percentage': roi_calc.roi_percentage,
                    'total_investment': float(roi_calc.total_investment),
                    'total_revenue': float(roi_calc.total_revenue),
                    'net_profit': float(roi_calc.net_profit),
                    'payback_period_months': roi_calc.payback_period_months,
                    'confidence_score': roi_calc.confidence_score,
                    'npv': float(roi_calc.npv) if roi_calc.npv else None,
                    'irr': roi_calc.irr
                }
            
            # Identify top performers and underperformers
            sorted_categories = sorted(
                category_rois.items(),
                key=lambda x: x[1].roi_percentage,
                reverse=True
            )
            
            analysis['top_performers'] = [
                {
                    'category': cat,
                    'roi_percentage': roi_calc.roi_percentage,
                    'net_profit': float(roi_calc.net_profit)
                }
                for cat, roi_calc in sorted_categories[:3]
                if roi_calc.roi_percentage > 0
            ]
            
            analysis['underperformers'] = [
                {
                    'category': cat,
                    'roi_percentage': roi_calc.roi_percentage,
                    'net_profit': float(roi_calc.net_profit)
                }
                for cat, roi_calc in sorted_categories[-3:]
                if roi_calc.roi_percentage < 0
            ]
            
            # ROI distribution analysis
            roi_values = [roi_calc.roi_percentage for roi_calc in category_rois.values()]
            analysis['roi_distribution'] = {
                'mean_roi': np.mean(roi_values),
                'median_roi': np.median(roi_values),
                'std_roi': np.std(roi_values),
                'min_roi': np.min(roi_values),
                'max_roi': np.max(roi_values),
                'categories_profitable': len([roi for roi in roi_values if roi > 0]),
                'categories_total': len(roi_values)
            }
            
            # Portfolio metrics
            total_investment = sum(float(roi_calc.total_investment) for roi_calc in category_rois.values())
            total_revenue = sum(float(roi_calc.total_revenue) for roi_calc in category_rois.values())
            total_profit = total_revenue - total_investment
            
            analysis['portfolio_metrics'] = {
                'total_investment': total_investment,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'portfolio_roi': (total_profit / total_investment * 100) if total_investment > 0 else 0,
                'investment_concentration': self._calculate_investment_concentration(category_rois),
                'revenue_diversification': self._calculate_revenue_diversification(category_rois)
            }
            
            # Optimization opportunities
            analysis['optimization_opportunities'] = await self._identify_optimization_opportunities(
                category_rois
            )
            
            # Generate recommendations
            analysis['recommendations'] = await self._generate_portfolio_recommendations(
                analysis
            )
            
            logger.info("✅ Cross-category ROI analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in cross-category ROI analysis: {e}")
            return {}

    async def calculate_attribution_roi(
        self,
        attribution_source: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        🎯 Calculate ROI based on attribution sources
        
        Track ROI for specific campaigns or initiatives
        """
        try:
            logger.info(f"🎯 Calculating attribution ROI for: {attribution_source}")
            
            # Get revenues attributed to this source
            attributed_revenues = [
                rev for rev in self.revenues
                if attribution_source in rev.attribution_sources and
                start_date <= rev.date <= end_date
            ]
            
            # Find related investments (would use more sophisticated matching in production)
            related_investments = [
                inv for inv in self.investments
                if attribution_source in inv.tags or
                attribution_source in inv.description.lower() and
                start_date <= inv.date <= end_date
            ]
            
            # Calculate metrics
            total_attributed_revenue = sum(rev.amount for rev in attributed_revenues)
            total_related_investment = sum(inv.amount for inv in related_investments)
            net_profit = total_attributed_revenue - total_related_investment
            
            roi_percentage = float(
                (net_profit / total_related_investment * 100) if total_related_investment > 0 else 0
            )
            
            # Revenue breakdown by stream
            revenue_by_stream = {}
            for rev in attributed_revenues:
                stream = rev.revenue_stream.value
                if stream not in revenue_by_stream:
                    revenue_by_stream[stream] = Decimal('0')
                revenue_by_stream[stream] += rev.amount
            
            # Investment breakdown by type
            investment_by_type = {}
            for inv in related_investments:
                inv_type = inv.investment_type.value
                if inv_type not in investment_by_type:
                    investment_by_type[inv_type] = Decimal('0')
                investment_by_type[inv_type] += inv.amount
            
            result = {
                'attribution_source': attribution_source,
                'time_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'total_attributed_revenue': float(total_attributed_revenue),
                'total_related_investment': float(total_related_investment),
                'net_profit': float(net_profit),
                'roi_percentage': roi_percentage,
                'revenue_count': len(attributed_revenues),
                'investment_count': len(related_investments),
                'revenue_breakdown': {stream: float(amount) for stream, amount in revenue_by_stream.items()},
                'investment_breakdown': {inv_type: float(amount) for inv_type, amount in investment_by_type.items()},
                'calculation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Attribution ROI: {roi_percentage:.2f}% for {attribution_source}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating attribution ROI: {e}")
            return {}

    async def generate_roi_dashboard_data(self) -> Dict[str, Any]:
        """
        📊 Generate comprehensive ROI dashboard data
        
        Prepare data for ROI monitoring and visualization
        """
        try:
            logger.info("📊 Generating ROI dashboard data")
            
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'summary_metrics': {},
                'category_performance': {},
                'trend_analysis': {},
                'forecasts': {},
                'alerts': [],
                'recommendations': []
            }
            
            # Summary metrics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days
            
            total_investment_30d = sum(
                inv.amount for inv in self.investments
                if start_date <= inv.date <= end_date
            )
            total_revenue_30d = sum(
                rev.amount for rev in self.revenues
                if start_date <= rev.date <= end_date
            )
            
            dashboard['summary_metrics'] = {
                'total_investment_30d': float(total_investment_30d),
                'total_revenue_30d': float(total_revenue_30d),
                'net_profit_30d': float(total_revenue_30d - total_investment_30d),
                'roi_30d': float(
                    ((total_revenue_30d - total_investment_30d) / total_investment_30d * 100)
                    if total_investment_30d > 0 else 0
                ),
                'active_categories': len(set(inv.category for inv in self.investments)),
                'revenue_streams': len(set(rev.revenue_stream for rev in self.revenues))
            }
            
            # Category performance (last 90 days)
            ninety_days_ago = end_date - timedelta(days=90)
            for category in ROICategory:
                try:
                    roi_calc = await self.calculate_category_roi(
                        category, ninety_days_ago, end_date, include_forecasting=False
                    )
                    dashboard['category_performance'][category.value] = {
                        'roi_percentage': roi_calc.roi_percentage,
                        'total_investment': float(roi_calc.total_investment),
                        'total_revenue': float(roi_calc.total_revenue),
                        'confidence_score': roi_calc.confidence_score
                    }
                except Exception:
                    continue
            
            # Trend analysis
            dashboard['trend_analysis'] = await self._calculate_roi_trends()
            
            # Forecasts
            for category in ROICategory:
                try:
                    forecast = await self.forecast_roi(category, forecast_months=6)
                    dashboard['forecasts'][category.value] = {
                        'predicted_roi': forecast.predicted_roi,
                        'confidence_interval': forecast.confidence_interval,
                        'expected_revenue': float(forecast.expected_revenue),
                        'expected_investment': float(forecast.expected_investment)
                    }
                except Exception:
                    continue
            
            # Alerts and recommendations
            dashboard['alerts'] = await self._generate_roi_alerts()
            dashboard['recommendations'] = await self._generate_dashboard_recommendations(dashboard)
            
            logger.info("✅ ROI dashboard data generated")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error generating ROI dashboard data: {e}")
            return {}

    # Helper methods
    
    async def _get_attributed_revenues(
        self,
        category: ROICategory,
        start_date: datetime,
        end_date: datetime
    ) -> List[Revenue]:
        """Get revenues attributed to a specific category"""
        # In production, this would use sophisticated attribution logic
        # For now, use simple heuristics
        
        attributed_revenues = []
        category_keywords = {
            ROICategory.CREATOR_ACQUISITION: ['signup', 'onboarding', 'acquisition'],
            ROICategory.CONTENT_PROMOTION: ['content', 'promotion', 'discovery'],
            ROICategory.MARKETING_CAMPAIGNS: ['campaign', 'marketing', 'advertising'],
            ROICategory.AI_DEVELOPMENT: ['ai', 'ml', 'algorithm'],
            # Add more category mappings
        }
        
        keywords = category_keywords.get(category, [])
        
        for revenue in self.revenues:
            if start_date <= revenue.date <= end_date:
                # Check if revenue is attributed to category
                if any(keyword in source.lower() for source in revenue.attribution_sources for keyword in keywords):
                    attributed_revenues.append(revenue)
                elif any(keyword in revenue.metadata.get('description', '').lower() for keyword in keywords):
                    attributed_revenues.append(revenue)
        
        return attributed_revenues

    async def _calculate_payback_period(
        self,
        investments: List[Investment],
        revenues: List[Revenue]
    ) -> Optional[float]:
        """Calculate payback period in months"""
        if not investments or not revenues:
            return None
        
        try:
            # Sort by date
            investments.sort(key=lambda x: x.date)
            revenues.sort(key=lambda x: x.date)
            
            total_investment = sum(inv.amount for inv in investments)
            cumulative_revenue = Decimal('0')
            
            start_date = investments[0].date
            
            for revenue in revenues:
                cumulative_revenue += revenue.amount
                if cumulative_revenue >= total_investment:
                    # Calculate months from start to payback
                    payback_date = revenue.date
                    months = (payback_date - start_date).days / 30.44  # Average days per month
                    return float(months)
            
            return None  # Payback not yet achieved
            
        except Exception as e:
            logger.error(f"Error calculating payback period: {e}")
            return None

    async def _calculate_npv(
        self,
        investments: List[Investment],
        revenues: List[Revenue]
    ) -> Optional[Decimal]:
        """Calculate Net Present Value"""
        if not investments and not revenues:
            return None
        
        try:
            npv = Decimal('0')
            base_date = min(
                [inv.date for inv in investments] + [rev.date for rev in revenues]
            )
            
            # Discount investments (cash outflows)
            for investment in investments:
                years = (investment.date - base_date).days / 365.25
                discounted_value = investment.amount / ((1 + self.discount_rate) ** years)
                npv -= discounted_value
            
            # Discount revenues (cash inflows)
            for revenue in revenues:
                years = (revenue.date - base_date).days / 365.25
                discounted_value = revenue.amount / ((1 + self.discount_rate) ** years)
                npv += discounted_value
            
            return npv.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating NPV: {e}")
            return None

    async def _calculate_irr(
        self,
        investments: List[Investment],
        revenues: List[Revenue]
    ) -> Optional[float]:
        """Calculate Internal Rate of Return"""
        # Simplified IRR calculation
        # In production, would use more sophisticated numerical methods
        
        if not investments or not revenues:
            return None
        
        try:
            # Create cash flow series
            all_transactions = [(inv.date, -float(inv.amount)) for inv in investments]
            all_transactions.extend([(rev.date, float(rev.amount)) for rev in revenues])
            all_transactions.sort(key=lambda x: x[0])
            
            if len(all_transactions) < 2:
                return None
            
            # Simple approximation - would use Newton-Raphson in production
            cash_flows = [cf[1] for cf in all_transactions]
            
            # Try different discount rates to find IRR
            for rate in np.arange(0.01, 1.0, 0.01):
                npv_test = sum(
                    cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows)
                )
                if abs(npv_test) < 1.0:  # Close to zero
                    return float(rate)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating IRR: {e}")
            return None

    def _calculate_confidence_score(
        self,
        investment_count: int,
        revenue_count: int,
        roi_percentage: float
    ) -> float:
        """Calculate confidence score for ROI calculation"""
        # Base confidence on data quantity and ROI magnitude
        data_confidence = min(1.0, (investment_count + revenue_count) / 20)
        magnitude_factor = min(1.0, abs(roi_percentage) / 100)
        
        return (data_confidence * 0.7 + magnitude_factor * 0.3)

    def _create_investment_breakdown(self, investments: List[Investment]) -> Dict[str, Any]:
        """Create detailed investment breakdown"""
        breakdown = {
            'by_type': {},
            'by_month': {},
            'total_count': len(investments)
        }
        
        for inv in investments:
            # By type
            inv_type = inv.investment_type.value
            if inv_type not in breakdown['by_type']:
                breakdown['by_type'][inv_type] = {'amount': 0, 'count': 0}
            breakdown['by_type'][inv_type]['amount'] += float(inv.amount)
            breakdown['by_type'][inv_type]['count'] += 1
            
            # By month
            month_key = inv.date.strftime('%Y-%m')
            if month_key not in breakdown['by_month']:
                breakdown['by_month'][month_key] = 0
            breakdown['by_month'][month_key] += float(inv.amount)
        
        return breakdown

    def _create_revenue_breakdown(self, revenues: List[Revenue]) -> Dict[str, Any]:
        """Create detailed revenue breakdown"""
        breakdown = {
            'by_stream': {},
            'by_month': {},
            'total_count': len(revenues)
        }
        
        for rev in revenues:
            # By stream
            stream = rev.revenue_stream.value
            if stream not in breakdown['by_stream']:
                breakdown['by_stream'][stream] = {'amount': 0, 'count': 0}
            breakdown['by_stream'][stream]['amount'] += float(rev.amount)
            breakdown['by_stream'][stream]['count'] += 1
            
            # By month
            month_key = rev.date.strftime('%Y-%m')
            if month_key not in breakdown['by_month']:
                breakdown['by_month'][month_key] = 0
            breakdown['by_month'][month_key] += float(rev.amount)
        
        return breakdown

    async def _calculate_monthly_roi_trend(
        self,
        category: ROICategory,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate monthly ROI trend"""
        monthly_roi = {}
        
        current_date = start_date.replace(day=1)  # Start of month
        while current_date <= end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            month_key = current_date.strftime('%Y-%m')
            
            try:
                month_roi = await self.calculate_category_roi(
                    category, current_date, min(month_end, end_date), include_forecasting=False
                )
                monthly_roi[month_key] = month_roi.roi_percentage
            except Exception:
                monthly_roi[month_key] = 0.0
            
            current_date = next_month
        
        return monthly_roi

    async def _compare_to_benchmark(self, category: ROICategory, roi_percentage: float) -> Dict[str, Any]:
        """Compare ROI to industry benchmarks"""
        # Simplified benchmark comparison
        benchmarks = {
            ROICategory.CREATOR_ACQUISITION: 25.0,
            ROICategory.MARKETING_CAMPAIGNS: 15.0,
            ROICategory.AI_DEVELOPMENT: 40.0,
            ROICategory.INFRASTRUCTURE: 10.0,
            # Add more benchmarks
        }
        
        benchmark = benchmarks.get(category, 20.0)
        
        return {
            'benchmark_roi': benchmark,
            'performance_vs_benchmark': roi_percentage - benchmark,
            'performance_ratio': roi_percentage / benchmark if benchmark != 0 else 0,
            'performance_category': (
                'above_benchmark' if roi_percentage > benchmark else
                'at_benchmark' if abs(roi_percentage - benchmark) < 1 else
                'below_benchmark'
            )
        }

    async def _calculate_performance_quartile(self, category: ROICategory, roi_percentage: float) -> int:
        """Calculate performance quartile (1-4, where 4 is best)"""
        # Get all ROI calculations for this category
        category_rois = [
            calc.roi_percentage for calc in self.roi_calculations
            if calc.category == category
        ]
        
        if len(category_rois) < 4:
            return 2  # Default to median
        
        quartiles = np.percentile(category_rois, [25, 50, 75])
        
        if roi_percentage >= quartiles[2]:
            return 4
        elif roi_percentage >= quartiles[1]:
            return 3
        elif roi_percentage >= quartiles[0]:
            return 2
        else:
            return 1

    async def _prepare_forecasting_data(self, category: ROICategory) -> List[Dict[str, Any]]:
        """Prepare historical data for forecasting"""
        # Aggregate monthly data for the category
        monthly_data = {}
        
        # Get investments
        category_investments = [inv for inv in self.investments if inv.category == category]
        for inv in category_investments:
            month_key = inv.date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': inv.date.replace(day=1),
                    'investment': Decimal('0'),
                    'revenue': Decimal('0')
                }
            monthly_data[month_key]['investment'] += inv.amount
        
        # Get attributed revenues
        for revenue in self.revenues:
            # Simplified attribution - would be more sophisticated in production
            month_key = revenue.date.strftime('%Y-%m')
            if month_key in monthly_data:
                monthly_data[month_key]['revenue'] += revenue.amount
        
        return list(monthly_data.values())

    def _prepare_ml_features(self, historical_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare features for ML models"""
        if not historical_data:
            return np.array([]), np.array([]), np.array([])
        
        # Sort by month
        historical_data.sort(key=lambda x: x['month'])
        
        features = []
        revenue_targets = []
        investment_targets = []
        
        for i, data in enumerate(historical_data):
            # Features: month index, previous months' data, trends
            feature_vector = [
                i,  # Month index
                float(data['investment']),
                float(data['revenue']),
                float(data['revenue'] - data['investment']),  # Profit
            ]
            
            # Add trend features if we have enough history
            if i >= 2:
                prev_investment = float(historical_data[i-1]['investment'])
                prev_revenue = float(historical_data[i-1]['revenue'])
                
                feature_vector.extend([
                    float(data['investment']) - prev_investment,  # Investment trend
                    float(data['revenue']) - prev_revenue,  # Revenue trend
                ])
            else:
                feature_vector.extend([0, 0])
            
            features.append(feature_vector)
            revenue_targets.append(float(data['revenue']))
            investment_targets.append(float(data['investment']))
        
        return np.array(features), np.array(revenue_targets), np.array(investment_targets)

    def _generate_future_features(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_months: int
    ) -> np.ndarray:
        """Generate features for future predictions"""
        if not historical_data:
            return np.array([])
        
        last_data = historical_data[-1]
        future_features = []
        
        for i in range(forecast_months):
            month_index = len(historical_data) + i
            
            # Use trends from historical data
            if len(historical_data) >= 2:
                recent_investment_trend = (
                    float(historical_data[-1]['investment']) - 
                    float(historical_data[-2]['investment'])
                )
                recent_revenue_trend = (
                    float(historical_data[-1]['revenue']) - 
                    float(historical_data[-2]['revenue'])
                )
            else:
                recent_investment_trend = 0
                recent_revenue_trend = 0
            
            # Project future values
            projected_investment = max(0, float(last_data['investment']) + recent_investment_trend * (i + 1))
            projected_revenue = max(0, float(last_data['revenue']) + recent_revenue_trend * (i + 1))
            
            feature_vector = [
                month_index,
                projected_investment,
                projected_revenue,
                projected_revenue - projected_investment,
                recent_investment_trend,
                recent_revenue_trend
            ]
            
            future_features.append(feature_vector)
        
        return np.array(future_features)

    def _calculate_forecast_confidence_interval(
        self,
        predicted_roi: float,
        revenue_score: float,
        investment_score: float
    ) -> Tuple[float, float]:
        """Calculate confidence interval for forecast"""
        model_confidence = (revenue_score + investment_score) / 2
        uncertainty = (1 - model_confidence) * abs(predicted_roi) * 0.5
        
        lower_bound = predicted_roi - uncertainty
        upper_bound = predicted_roi + uncertainty
        
        return (lower_bound, upper_bound)

    async def _identify_roi_risk_factors(
        self,
        category: ROICategory,
        historical_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify risk factors for ROI forecast"""
        risk_factors = []
        
        if len(historical_data) < 6:
            risk_factors.append("Limited historical data available")
        
        # Volatility analysis
        if historical_data:
            profits = [float(data['revenue'] - data['investment']) for data in historical_data]
            if len(profits) > 1:
                volatility = np.std(profits) / max(1, np.mean(profits))
                if volatility > 0.5:
                    risk_factors.append("High profit volatility detected")
        
        # Category-specific risks
        category_risks = {
            ROICategory.AI_DEVELOPMENT: ["Technology risk", "Model performance uncertainty"],
            ROICategory.MARKETING_CAMPAIGNS: ["Market saturation", "Competition increase"],
            ROICategory.INFRASTRUCTURE: ["Scaling costs", "Technology obsolescence"],
        }
        
        risk_factors.extend(category_risks.get(category, []))
        
        return risk_factors

    async def _generate_roi_recommendations(
        self,
        category: ROICategory,
        predicted_roi: float,
        risk_factors: List[str]
    ) -> List[str]:
        """Generate ROI optimization recommendations"""
        recommendations = []
        
        if predicted_roi < 10:
            recommendations.append(f"Consider optimizing {category.value} investments for better ROI")
        elif predicted_roi > 50:
            recommendations.append(f"Excellent ROI predicted for {category.value} - consider increasing investment")
        
        if "High profit volatility detected" in risk_factors:
            recommendations.append("Implement risk management strategies to reduce volatility")
        
        if "Limited historical data available" in risk_factors:
            recommendations.append("Improve data collection for better forecasting accuracy")
        
        # Category-specific recommendations
        if category == ROICategory.CREATOR_ACQUISITION:
            recommendations.append("Focus on creator lifetime value optimization")
        elif category == ROICategory.AI_DEVELOPMENT:
            recommendations.append("Monitor model performance metrics closely")
        
        return recommendations

    def _create_default_forecast(self, category: ROICategory, forecast_months: int) -> ROIForecast:
        """Create default forecast when insufficient data"""
        return ROIForecast(
            category=category,
            forecast_period_months=forecast_months,
            predicted_roi=0.0,
            confidence_interval=(0.0, 0.0),
            expected_revenue=Decimal('0'),
            expected_investment=Decimal('0'),
            risk_factors=["Insufficient historical data for forecasting"],
            recommendations=["Collect more investment and revenue data before forecasting"]
        )

    def _calculate_investment_concentration(self, category_rois: Dict[str, ROICalculation]) -> float:
        """Calculate investment concentration (Herfindahl index)"""
        total_investment = sum(float(roi.total_investment) for roi in category_rois.values())
        
        if total_investment == 0:
            return 0.0
        
        concentration = sum(
            (float(roi.total_investment) / total_investment) ** 2
            for roi in category_rois.values()
        )
        
        return concentration

    def _calculate_revenue_diversification(self, category_rois: Dict[str, ROICalculation]) -> float:
        """Calculate revenue diversification index"""
        total_revenue = sum(float(roi.total_revenue) for roi in category_rois.values())
        
        if total_revenue == 0:
            return 0.0
        
        # Shannon diversity index
        diversity = -sum(
            (float(roi.total_revenue) / total_revenue) * 
            np.log(float(roi.total_revenue) / total_revenue + 1e-10)
            for roi in category_rois.values()
            if roi.total_revenue > 0
        )
        
        return diversity

    async def _identify_optimization_opportunities(
        self,
        category_rois: Dict[str, ROICalculation]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        opportunities = []
        
        for category, roi_calc in category_rois.items():
            if roi_calc.roi_percentage < 0:
                opportunities.append({
                    'type': 'underperforming_category',
                    'category': category,
                    'current_roi': roi_calc.roi_percentage,
                    'potential_impact': 'high',
                    'action': f'Review and optimize {category} investments'
                })
            
            elif roi_calc.roi_percentage > 100 and roi_calc.confidence_score > 0.8:
                opportunities.append({
                    'type': 'high_performing_category',
                    'category': category,
                    'current_roi': roi_calc.roi_percentage,
                    'potential_impact': 'medium',
                    'action': f'Consider increasing investment in {category}'
                })
        
        return opportunities

    async def _generate_portfolio_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        portfolio_roi = analysis['portfolio_metrics']['portfolio_roi']
        
        if portfolio_roi < 0:
            recommendations.append("Portfolio ROI is negative - immediate review required")
        elif portfolio_roi < 10:
            recommendations.append("Portfolio ROI is below industry average - optimization needed")
        
        concentration = analysis['portfolio_metrics']['investment_concentration']
        if concentration > 0.5:
            recommendations.append("High investment concentration - consider diversification")
        
        profitable_ratio = (
            analysis['roi_distribution']['categories_profitable'] /
            analysis['roi_distribution']['categories_total']
        )
        
        if profitable_ratio < 0.5:
            recommendations.append("Less than 50% of categories are profitable - review strategy")
        
        return recommendations

    async def _calculate_roi_trends(self) -> Dict[str, Any]:
        """Calculate ROI trends over time"""
        # Simplified trend calculation
        trends = {}
        
        # Calculate monthly portfolio ROI for the last 12 months
        end_date = datetime.now()
        monthly_rois = []
        
        for i in range(12):
            month_end = end_date - timedelta(days=30 * i)
            month_start = month_end - timedelta(days=30)
            
            month_investments = sum(
                inv.amount for inv in self.investments
                if month_start <= inv.date <= month_end
            )
            month_revenues = sum(
                rev.amount for rev in self.revenues
                if month_start <= rev.date <= month_end
            )
            
            month_roi = float(
                ((month_revenues - month_investments) / month_investments * 100)
                if month_investments > 0 else 0
            )
            
            monthly_rois.append({
                'month': month_end.strftime('%Y-%m'),
                'roi': month_roi
            })
        
        monthly_rois.reverse()  # Chronological order
        
        trends['monthly_trend'] = monthly_rois
        
        # Calculate trend direction
        if len(monthly_rois) >= 2:
            recent_roi = monthly_rois[-1]['roi']
            previous_roi = monthly_rois[-2]['roi']
            trends['trend_direction'] = 'up' if recent_roi > previous_roi else 'down'
        else:
            trends['trend_direction'] = 'stable'
        
        return trends

    async def _generate_roi_alerts(self) -> List[Dict[str, Any]]:
        """Generate ROI-based alerts"""
        alerts = []
        
        # Recent negative ROI alert
        recent_date = datetime.now() - timedelta(days=7)
        recent_investments = sum(
            inv.amount for inv in self.investments
            if inv.date >= recent_date
        )
        recent_revenues = sum(
            rev.amount for rev in self.revenues
            if rev.date >= recent_date
        )
        
        if recent_investments > 0:
            recent_roi = float((recent_revenues - recent_investments) / recent_investments * 100)
            if recent_roi < -10:
                alerts.append({
                    'type': 'negative_roi',
                    'severity': 'warning',
                    'message': f'Recent 7-day ROI is negative: {recent_roi:.1f}%',
                    'recommendation': 'Review recent investments and revenue attribution'
                })
        
        return alerts

    async def _generate_dashboard_recommendations(self, dashboard: Dict[str, Any]) -> List[str]:
        """Generate recommendations for dashboard"""
        recommendations = []
        
        summary = dashboard.get('summary_metrics', {})
        roi_30d = summary.get('roi_30d', 0)
        
        if roi_30d < 0:
            recommendations.append("🚨 30-day ROI is negative - immediate action required")
        elif roi_30d < 10:
            recommendations.append("📈 Consider optimizing investment allocation for better ROI")
        
        # Category performance recommendations
        category_performance = dashboard.get('category_performance', {})
        best_category = max(
            category_performance.items(),
            key=lambda x: x[1]['roi_percentage'],
            default=(None, None)
        )
        
        if best_category[0]:
            recommendations.append(f"💰 {best_category[0]} shows best ROI - consider increasing investment")
        
        recommendations.append("📊 Review monthly ROI trends for pattern identification")
        recommendations.append("🎯 Set up automated ROI monitoring alerts")
        
        return recommendations

# Usage example
async def main() -> None:
    """Test the ROI analytics calculator"""
    try:
        # Initialize calculator
        calculator = ROIAnalyticsCalculator("postgresql://user:pass@localhost/ainflue")
        
        # Record some investments
        await calculator.record_investment(
            ROICategory.CREATOR_ACQUISITION,
            InvestmentType.MARKETING_SPEND,
            5000.0,
            "Creator onboarding campaign",
            expected_duration_months=6,
            tags=["campaign_2025_q1"]
        )
        
        # Record some revenue
        await calculator.record_revenue(
            RevenueStream.SUBSCRIPTION_FEES,
            8000.0,
            attribution_sources=["campaign_2025_q1", "organic"]
        )
        
        # Calculate ROI
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        roi_result = await calculator.calculate_category_roi(
            ROICategory.CREATOR_ACQUISITION,
            start_date,
            end_date
        )
        
        print(f"ROI for Creator Acquisition: {roi_result.roi_percentage:.2f}%")
        
        # Generate forecast
        forecast = await calculator.forecast_roi(ROICategory.CREATOR_ACQUISITION)
        print(f"Forecasted ROI: {forecast.predicted_roi:.2f}%")
        
        # Cross-category analysis
        analysis = await calculator.analyze_cross_category_roi()
        print(f"Portfolio ROI: {analysis.get('portfolio_metrics', {}).get('portfolio_roi', 0):.2f}%")
        
    except Exception as e:
        print(f"Error in ROI analytics: {e}")

if __name__ == "__main__":
    asyncio.run(main())