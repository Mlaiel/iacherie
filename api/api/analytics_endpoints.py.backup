"""Analytics and intelligence endpoints for IA Influencer Agent platform.

This module provides comprehensive analytics, business intelligence,
and performance insights for content creators and their portfolios.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import logging
from uuid import uuid4
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import numpy as np

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.analytics import AnalyticsReport, PerformanceMetric, InsightData
from ..models.fingerprint import ContentFingerprint
from ..business.analytics_service import AnalyticsService
from ..business.intelligence_service import IntelligenceService
from ..business.performance_service import PerformanceService
from ..business.recommendation_service import RecommendationService
from ..utils.data_processor import DataProcessor
from ..utils.visualization_generator import VisualizationGenerator
from ..utils.response_handler import ResponseHandler

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/analytics", tags=["Analytics & Intelligence"])

class AnalyticsTimeframe(str, Enum):
    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    LAST_90D = "90d"
    LAST_YEAR = "365d"
    CUSTOM = "custom"

class MetricType(str, Enum):
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    PROTECTION = "protection"
    COLLABORATIONS = "collaborations"
    GROWTH = "growth"

# Pydantic models for request/response validation
class AnalyticsRequest(BaseModel):
    """Request model for analytics generation"""
    timeframe: AnalyticsTimeframe = Field(..., description="Timeframe for analytics")
    start_date: Optional[datetime] = Field(None, description="Custom start date")
    end_date: Optional[datetime] = Field(None, description="Custom end date")
    content_ids: Optional[List[str]] = Field(None, description="Specific content to analyze")
    platforms: Optional[List[str]] = Field(None, description="Specific platforms to analyze")
    metrics: List[MetricType] = Field(..., description="Metrics to include in analysis")
    include_predictions: bool = Field(True, description="Include AI predictions")
    granularity: str = Field("daily", description="Data granularity: hourly, daily, weekly")

class PerformanceInsights(BaseModel):
    """Model for performance insights response"""
    content_id: str = Field(..., description="Content fingerprint ID")
    content_title: Optional[str] = Field(None, description="Content title")
    performance_score: float = Field(..., description="Overall performance score (0-100)")
    views_total: int = Field(..., description="Total views across platforms")
    engagement_rate: float = Field(..., description="Average engagement rate")
    revenue_generated: float = Field(..., description="Total revenue generated")
    protection_alerts: int = Field(..., description="Number of protection alerts")
    top_platforms: List[str] = Field(..., description="Top performing platforms")
    growth_trend: str = Field(..., description="Growth trend: ascending, stable, declining")
    recommendations: List[str] = Field(..., description="AI-generated recommendations")

class MarketIntelligence(BaseModel):
    """Model for market intelligence response"""
    market_segment: str = Field(..., description="Market segment analysis")
    competitive_position: str = Field(..., description="Competitive positioning")
    market_opportunities: List[Dict[str, Any]] = Field(..., description="Identified opportunities")
    trend_analysis: Dict[str, Any] = Field(..., description="Market trend analysis")
    benchmark_data: Dict[str, Any] = Field(..., description="Industry benchmark comparison")
    success_factors: List[str] = Field(..., description="Key success factors identified")
    risk_assessment: Dict[str, Any] = Field(..., description="Market risk assessment")

class PredictiveAnalytics(BaseModel):
    """Model for predictive analytics response"""
    forecast_horizon: str = Field(..., description="Forecast time horizon")
    predicted_metrics: Dict[str, Any] = Field(..., description="Predicted performance metrics")
    confidence_levels: Dict[str, float] = Field(..., description="Prediction confidence levels")
    scenario_analysis: Dict[str, Any] = Field(..., description="Best/worst case scenarios")
    actionable_insights: List[str] = Field(..., description="Actionable insights for optimization")
    market_timing: Dict[str, Any] = Field(..., description="Optimal timing recommendations")

# Core analytics endpoints
@router.post("/generate", response_model=Dict[str, Any])
async def generate_comprehensive_analytics(
    analytics_request: AnalyticsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends(),
    intelligence_service: IntelligenceService = Depends()
):
    """
    Generate comprehensive analytics report with AI-powered insights.
    
    Features:
    - Multi-platform performance analysis
    - AI-powered trend detection and pattern recognition
    - Competitive intelligence and market positioning
    - Predictive analytics and forecasting
    - Actionable recommendations for optimization
    """
    try:
        # Determine date range
        if analytics_request.timeframe == AnalyticsTimeframe.CUSTOM:
            if not analytics_request.start_date or not analytics_request.end_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom timeframe requires start_date and end_date"
                )
            start_date = analytics_request.start_date
            end_date = analytics_request.end_date
        else:
            end_date = datetime.utcnow()
            timeframe_days = {
                "24h": 1, "7d": 7, "30d": 30, "90d": 90, "365d": 365
            }
            start_date = end_date - timedelta(days=timeframe_days[analytics_request.timeframe.value])
        
        # Validate content IDs if provided
        if analytics_request.content_ids:
            fingerprints = db.query(ContentFingerprint).filter(
                ContentFingerprint.id.in_(analytics_request.content_ids),
                ContentFingerprint.user_id == current_user.id
            ).all()
            
            if len(fingerprints) != len(analytics_request.content_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more content items not found"
                )
        else:
            # Get all user's content
            fingerprints = db.query(ContentFingerprint).filter(
                ContentFingerprint.user_id == current_user.id
            ).all()
        
        content_ids = [fp.id for fp in fingerprints]
        
        if not content_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No content found for analytics"
            )
        
        # Generate analytics report ID
        report_id = str(uuid4())
        
        # Collect data for requested metrics
        analytics_data = {}
        
        for metric in analytics_request.metrics:
            if metric == MetricType.VIEWS:
                analytics_data['views'] = await analytics_service.get_views_analytics(
                    content_ids, start_date, end_date, analytics_request.platforms
                )
            elif metric == MetricType.ENGAGEMENT:
                analytics_data['engagement'] = await analytics_service.get_engagement_analytics(
                    content_ids, start_date, end_date, analytics_request.platforms
                )
            elif metric == MetricType.REVENUE:
                analytics_data['revenue'] = await analytics_service.get_revenue_analytics(
                    content_ids, start_date, end_date, analytics_request.platforms
                )
            elif metric == MetricType.PROTECTION:
                analytics_data['protection'] = await analytics_service.get_protection_analytics(
                    content_ids, start_date, end_date
                )
            elif metric == MetricType.COLLABORATIONS:
                analytics_data['collaborations'] = await analytics_service.get_collaboration_analytics(
                    content_ids, start_date, end_date
                )
            elif metric == MetricType.GROWTH:
                analytics_data['growth'] = await analytics_service.get_growth_analytics(
                    content_ids, start_date, end_date, analytics_request.granularity
                )
        
        # Generate AI insights and recommendations
        ai_insights = await intelligence_service.generate_performance_insights(
            analytics_data,
            current_user.id,
            content_ids
        )
        
        # Generate predictions if requested
        predictions = {}
        if analytics_request.include_predictions:
            predictions = await intelligence_service.generate_predictive_analytics(
                analytics_data,
                current_user.id,
                forecast_days=30
            )
        
        # Generate visualizations
        visualizations = await VisualizationGenerator.create_analytics_charts(
            analytics_data,
            analytics_request.metrics
        )
        
        # Create analytics report record
        analytics_report = AnalyticsReport(
            id=report_id,
            user_id=current_user.id,
            timeframe=analytics_request.timeframe.value,
            start_date=start_date,
            end_date=end_date,
            metrics=analytics_request.metrics,
            content_ids=content_ids,
            platforms=analytics_request.platforms or [],
            analytics_data=analytics_data,
            ai_insights=ai_insights,
            predictions=predictions,
            created_at=datetime.utcnow()
        )
        
        db.add(analytics_report)
        db.commit()
        
        logger.info(f"Comprehensive analytics generated: {report_id} for user: {current_user.id}")
        
        return {
            "report_id": report_id,
            "timeframe": analytics_request.timeframe.value,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "content_analyzed": len(content_ids),
            "metrics_included": analytics_request.metrics,
            "analytics_data": analytics_data,
            "ai_insights": ai_insights,
            "predictions": predictions,
            "visualizations": visualizations,
            "generated_at": datetime.utcnow(),
            "report_summary": {
                "key_findings": ai_insights.get('key_findings', []),
                "performance_score": ai_insights.get('overall_score', 0),
                "top_recommendations": ai_insights.get('top_recommendations', []),
                "growth_opportunities": ai_insights.get('growth_opportunities', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics generation failed: {str(e)}"
        )

@router.get("/performance/{content_id}", response_model=PerformanceInsights)
async def get_content_performance(
    content_id: str,
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30D,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    performance_service: PerformanceService = Depends()
):
    """
    Get detailed performance insights for specific content.
    
    Features:
    - Comprehensive performance scoring algorithm
    - Cross-platform performance comparison
    - AI-generated optimization recommendations
    - Trend analysis and growth trajectory
    """
    try:
        # Validate content belongs to user
        fingerprint = db.query(ContentFingerprint).filter(
            ContentFingerprint.id == content_id,
            ContentFingerprint.user_id == current_user.id
        ).first()
        
        if not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Calculate date range
        end_date = datetime.utcnow()
        timeframe_days = {"24h": 1, "7d": 7, "30d": 30, "90d": 90, "365d": 365}
        start_date = end_date - timedelta(days=timeframe_days[timeframe.value])
        
        # Get comprehensive performance data
        performance_data = await performance_service.get_comprehensive_performance(
            content_id,
            start_date,
            end_date
        )
        
        # Generate AI recommendations
        recommendations = await performance_service.generate_optimization_recommendations(
            content_id,
            performance_data
        )
        
        return PerformanceInsights(
            content_id=content_id,
            content_title=fingerprint.metadata.get('file_info', {}).get('filename'),
            performance_score=performance_data['performance_score'],
            views_total=performance_data['views_total'],
            engagement_rate=performance_data['engagement_rate'],
            revenue_generated=performance_data['revenue_generated'],
            protection_alerts=performance_data['protection_alerts'],
            top_platforms=performance_data['top_platforms'],
            growth_trend=performance_data['growth_trend'],
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error retrieving content performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve content performance: {str(e)}"
        )

@router.get("/market-intelligence", response_model=MarketIntelligence)
async def get_market_intelligence(
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    platforms: Optional[List[str]] = Query(None, description="Specific platforms to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    intelligence_service: IntelligenceService = Depends()
):
    """
    Get comprehensive market intelligence and competitive analysis.
    
    Features:
    - Real-time market trend analysis
    - Competitive positioning and benchmarking
    - Opportunity identification and market gaps
    - Industry-specific insights and recommendations
    """
    try:
        # Get user's content for market analysis
        query = db.query(ContentFingerprint).filter(
            ContentFingerprint.user_id == current_user.id
        )
        
        if content_type:
            query = query.filter(ContentFingerprint.content_type == content_type)
        
        user_content = query.all()
        
        if not user_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No content found for market analysis"
            )
        
        # Analyze market segment
        market_segment = await intelligence_service.determine_market_segment(
            user_content,
            current_user.role
        )
        
        # Competitive analysis
        competitive_analysis = await intelligence_service.perform_competitive_analysis(
            market_segment,
            platforms or []
        )
        
        # Identify market opportunities
        opportunities = await intelligence_service.identify_market_opportunities(
            market_segment,
            competitive_analysis,
            user_content
        )
        
        # Market trend analysis
        trend_analysis = await intelligence_service.analyze_market_trends(
            market_segment,
            timeframe_days=90
        )
        
        # Benchmark against industry
        benchmark_data = await intelligence_service.generate_industry_benchmarks(
            market_segment,
            user_content
        )
        
        # Risk assessment
        risk_assessment = await intelligence_service.assess_market_risks(
            market_segment,
            competitive_analysis
        )
        
        logger.info(f"Market intelligence generated for user: {current_user.id}, segment: {market_segment}")
        
        return MarketIntelligence(
            market_segment=market_segment,
            competitive_position=competitive_analysis['position'],
            market_opportunities=opportunities,
            trend_analysis=trend_analysis,
            benchmark_data=benchmark_data,
            success_factors=competitive_analysis['success_factors'],
            risk_assessment=risk_assessment
        )
        
    except Exception as e:
        logger.error(f"Error generating market intelligence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market intelligence generation failed: {str(e)}"
        )

@router.post("/predictive", response_model=PredictiveAnalytics)
async def generate_predictive_analytics(
    forecast_days: int = Query(30, ge=7, le=365),
    confidence_level: float = Query(0.9, ge=0.5, le=0.99),
    include_scenarios: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    intelligence_service: IntelligenceService = Depends()
):
    """
    Generate advanced predictive analytics with machine learning models.
    
    Features:
    - Multi-model ensemble forecasting (LSTM, ARIMA, Prophet)
    - Scenario analysis with confidence intervals
    - Market timing optimization
    - Actionable insights for strategic planning
    """
    try:
        # Get user's historical data
        user_content = db.query(ContentFingerprint).filter(
            ContentFingerprint.user_id == current_user.id
        ).all()
        
        if not user_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insufficient data for predictive analysis"
            )
        
        content_ids = [fp.id for fp in user_content]
        
        # Generate predictions using ensemble models
        predictions = await intelligence_service.generate_ensemble_predictions(
            user_id=current_user.id,
            content_ids=content_ids,
            forecast_days=forecast_days,
            confidence_level=confidence_level
        )
        
        # Scenario analysis
        scenarios = {}
        if include_scenarios:
            scenarios = await intelligence_service.perform_scenario_analysis(
                predictions,
                confidence_level
            )
        
        # Generate actionable insights
        insights = await intelligence_service.generate_strategic_insights(
            predictions,
            scenarios,
            current_user.id
        )
        
        # Market timing recommendations
        market_timing = await intelligence_service.optimize_market_timing(
            predictions,
            current_user.id
        )
        
        logger.info(f"Predictive analytics generated for user: {current_user.id}, forecast: {forecast_days} days")
        
        return PredictiveAnalytics(
            forecast_horizon=f"{forecast_days} days",
            predicted_metrics=predictions,
            confidence_levels=predictions.get('confidence_levels', {}),
            scenario_analysis=scenarios,
            actionable_insights=insights,
            market_timing=market_timing
        )
        
    except Exception as e:
        logger.error(f"Error generating predictive analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Predictive analytics generation failed: {str(e)}"
        )

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends()
):
    """Get real-time analytics dashboard with key metrics and insights."""
    try:
        # Get dashboard metrics
        dashboard_data = await analytics_service.generate_dashboard_data(current_user.id)
        
        return {
            "user_id": current_user.id,
            "generated_at": datetime.utcnow(),
            "dashboard_data": dashboard_data,
            "refresh_interval": "5 minutes",
            "last_updated": dashboard_data.get('last_updated')
        }
        
    except Exception as e:
        logger.error(f"Error generating analytics dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard generation failed: {str(e)}"
        )

@router.get("/reports", response_model=List[Dict[str, Any]])
async def get_analytics_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical analytics reports for the user."""
    try:
        reports = db.query(AnalyticsReport).filter(
            AnalyticsReport.user_id == current_user.id
        ).order_by(AnalyticsReport.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for report in reports:
            result.append({
                "report_id": report.id,
                "timeframe": report.timeframe,
                "date_range": {
                    "start_date": report.start_date,
                    "end_date": report.end_date
                },
                "metrics": report.metrics,
                "content_count": len(report.content_ids),
                "created_at": report.created_at,
                "summary": {
                    "key_finding": report.ai_insights.get('key_findings', [])[:1],
                    "performance_score": report.ai_insights.get('overall_score', 0)
                }
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving analytics reports: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics reports: {str(e)}"
        )

__all__ = ["router"]
