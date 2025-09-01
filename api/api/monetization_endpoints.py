"""Monetization and revenue tracking endpoints for IA Influencer Agent platform.

This module handles comprehensive revenue optimization, automated licensing,
and multi-platform monetization analytics for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import logging
from uuid import uuid4
from decimal import Decimal
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import numpy as np

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.monetization import RevenueTracking, LicensingDeal, PayoutRecord, RevenueSource
from ..models.fingerprint import ContentFingerprint
from ..business.monetization_service import MonetizationService
from ..business.revenue_service import RevenueService
from ..business.licensing_service import LicensingService
from ..business.payment_service import PaymentService
from ..business.analytics_service import AnalyticsService
from ..utils.financial_calculator import FinancialCalculator
from ..utils.response_handler import ResponseHandler

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/monetization", tags=["Monetization & Revenue"])

class ForecastHorizon(str, Enum):
    SHORT_TERM = "30_days"
    MEDIUM_TERM = "90_days"
    LONG_TERM = "365_days"

class RevenueType(str, Enum):
    STREAMING = "streaming"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    LIVE_EVENTS = "live_events"
    SPONSORSHIPS = "sponsorships"
    DIRECT_SALES = "direct_sales"

# Pydantic models for request/response validation
class RevenueTrackingRequest(BaseModel):
    """Request model for revenue tracking setup"""
    content_ids: List[str] = Field(..., description="List of content fingerprint IDs to track")
    platforms: List[str] = Field(..., description="Platforms for revenue tracking")
    tracking_frequency: str = Field("daily", description="Tracking frequency: hourly, daily, weekly")
    currency: str = Field("EUR", description="Primary currency for reporting")
    enable_forecasting: bool = Field(True, description="Enable AI-powered revenue forecasting")

class RevenueAnalyticsResponse(BaseModel):
    """Response model for revenue analytics"""
    total_revenue: Decimal = Field(..., description="Total revenue across all sources")
    revenue_by_platform: Dict[str, Decimal] = Field(..., description="Revenue breakdown by platform")
    revenue_by_type: Dict[str, Decimal] = Field(..., description="Revenue breakdown by type")
    growth_rate: float = Field(..., description="Month-over-month growth rate")
    top_earning_content: List[Dict[str, Any]] = Field(..., description="Top earning content items")
    revenue_trend: List[Dict[str, Any]] = Field(..., description="Revenue trend data")
    forecasted_revenue: Optional[Dict[str, Any]] = Field(None, description="AI-generated revenue forecast")

class LicensingDealRequest(BaseModel):
    """Request model for licensing deal creation"""
    content_id: str = Field(..., description="Content fingerprint ID to license")
    licensee_name: str = Field(..., description="Name of licensee")
    licensee_email: str = Field(..., description="Contact email of licensee")
    usage_type: str = Field(..., description="Type of usage: commercial, non-commercial, exclusive")
    territory: List[str] = Field(..., description="Geographic territories for license")
    duration_months: int = Field(..., description="License duration in months")
    fee_amount: Decimal = Field(..., description="License fee amount")
    royalty_percentage: Optional[float] = Field(None, description="Royalty percentage if applicable")
    terms_conditions: Dict[str, Any] = Field(..., description="Additional terms and conditions")

class PayoutRequest(BaseModel):
    """Request model for payout processing"""
    amount: Decimal = Field(..., description="Payout amount")
    currency: str = Field("EUR", description="Payout currency")
    payment_method: str = Field(..., description="Payment method: bank_transfer, paypal, stripe")
    payment_details: Dict[str, Any] = Field(..., description="Payment method specific details")
    notes: Optional[str] = Field(None, description="Optional notes for payout")

class RevenueForecastRequest(BaseModel):
    """Request model for revenue forecasting"""
    content_ids: Optional[List[str]] = Field(None, description="Specific content IDs to forecast")
    forecast_horizon: ForecastHorizon = Field(ForecastHorizon.MEDIUM_TERM, description="Forecasting time horizon")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99, description="Statistical confidence level")
    include_seasonality: bool = Field(True, description="Include seasonal patterns in forecast")
    scenario_analysis: bool = Field(False, description="Include best/worst case scenarios")

# Core monetization endpoints
@router.post("/setup", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def setup_revenue_tracking(
    tracking_request: RevenueTrackingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    monetization_service: MonetizationService = Depends(),
    revenue_service: RevenueService = Depends()
):
    """
    Setup comprehensive revenue tracking for content portfolio.
    
    Features:
    - Multi-platform revenue aggregation (Spotify, YouTube, Instagram, TikTok, etc.)
    - Real-time revenue monitoring and alerts
    - AI-powered revenue forecasting and optimization
    - Automated reporting and tax documentation
    """
    try:
        # Validate content IDs belong to user
        fingerprints = db.query(ContentFingerprint).filter(
            ContentFingerprint.id.in_(tracking_request.content_ids),
            ContentFingerprint.user_id == current_user.id
        ).all()
        
        if len(fingerprints) != len(tracking_request.content_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more content items not found"
            )
        
        # Validate supported platforms
        supported_platforms = settings.SUPPORTED_MONETIZATION_PLATFORMS
        invalid_platforms = set(tracking_request.platforms) - set(supported_platforms)
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platforms: {list(invalid_platforms)}"
            )
        
        # Create revenue tracking configuration
        tracking_config_id = str(uuid4())
        
        # Setup revenue tracking for each content item
        tracking_records = []
        for fingerprint in fingerprints:
            for platform in tracking_request.platforms:
                tracking_record = RevenueTracking(
                    id=str(uuid4()),
                    config_id=tracking_config_id,
                    user_id=current_user.id,
                    content_id=fingerprint.id,
                    platform=platform,
                    currency=tracking_request.currency,
                    tracking_frequency=tracking_request.tracking_frequency,
                    current_revenue=Decimal('0.00'),
                    last_updated=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                tracking_records.append(tracking_record)
                db.add(tracking_record)
        
        db.commit()
        
        # Setup platform API integrations in background
        for platform in tracking_request.platforms:
            background_tasks.add_task(
                revenue_service.setup_platform_integration,
                current_user.id,
                platform,
                tracking_config_id
            )
        
        # Enable AI forecasting if requested
        if tracking_request.enable_forecasting:
            background_tasks.add_task(
                monetization_service.setup_forecasting_models,
                tracking_config_id,
                [fp.id for fp in fingerprints]
            )
        
        # Start automated revenue collection
        background_tasks.add_task(
            revenue_service.start_revenue_collection,
            tracking_config_id,
            tracking_request.tracking_frequency
        )
        
        logger.info(f"Revenue tracking setup completed: {tracking_config_id} for {len(fingerprints)} content items")
        
        return {
            "tracking_config_id": tracking_config_id,
            "status": "active",
            "tracked_content_count": len(fingerprints),
            "platforms_count": len(tracking_request.platforms),
            "platforms": tracking_request.platforms,
            "tracking_frequency": tracking_request.tracking_frequency,
            "currency": tracking_request.currency,
            "forecasting_enabled": tracking_request.enable_forecasting,
            "estimated_setup_time": "2-5 minutes",
            "next_data_collection": "within 1 hour",
            "features_enabled": [
                "Real-time revenue monitoring",
                "Multi-platform data aggregation",
                "Automated tax reporting",
                "Performance analytics dashboard"
            ] + (["AI revenue forecasting"] if tracking_request.enable_forecasting else [])
        }
        
    except Exception as e:
        logger.error(f"Error setting up revenue tracking: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revenue tracking setup failed: {str(e)}"
        )

@router.get("/analytics", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    platforms: Optional[List[str]] = Query(None, description="Filter by specific platforms"),
    content_ids: Optional[List[str]] = Query(None, description="Filter by specific content"),
    currency: str = Query("EUR", description="Currency for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends(),
    monetization_service: MonetizationService = Depends()
):
    """
    Get comprehensive revenue analytics with AI-powered insights.
    
    Features:
    - Real-time revenue aggregation across all platforms
    - Advanced performance metrics and KPIs
    - AI-powered trend analysis and recommendations
    - Comparative analytics and benchmarking
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get user's revenue data
        revenue_query = db.query(RevenueTracking).filter(
            RevenueTracking.user_id == current_user.id,
            RevenueTracking.last_updated >= start_date,
            RevenueTracking.last_updated <= end_date
        )
        
        # Apply filters
        if platforms:
            revenue_query = revenue_query.filter(RevenueTracking.platform.in_(platforms))
        if content_ids:
            revenue_query = revenue_query.filter(RevenueTracking.content_id.in_(content_ids))
        
        revenue_records = revenue_query.all()
        
        if not revenue_records:
            return RevenueAnalyticsResponse(
                total_revenue=Decimal('0.00'),
                revenue_by_platform={},
                revenue_by_type={},
                growth_rate=0.0,
                top_earning_content=[],
                revenue_trend=[]
            )
        
        # Calculate total revenue
        total_revenue = sum(record.current_revenue for record in revenue_records)
        
        # Revenue breakdown by platform
        revenue_by_platform = {}
        for record in revenue_records:
            if record.platform not in revenue_by_platform:
                revenue_by_platform[record.platform] = Decimal('0.00')
            revenue_by_platform[record.platform] += record.current_revenue
        
        # Revenue breakdown by type (requires classification)
        revenue_by_type = await analytics_service.classify_revenue_by_type(revenue_records)
        
        # Calculate growth rate
        previous_period_start = start_date - (end_date - start_date)
        growth_rate = await analytics_service.calculate_growth_rate(
            current_user.id,
            previous_period_start,
            start_date,
            end_date
        )
        
        # Get top earning content
        top_earning_content = await analytics_service.get_top_earning_content(
            current_user.id,
            start_date,
            end_date,
            limit=10
        )
        
        # Get revenue trend data
        revenue_trend = await analytics_service.get_revenue_trend(
            current_user.id,
            start_date,
            end_date,
            granularity='daily'
        )
        
        # Generate AI-powered forecast
        forecasted_revenue = await monetization_service.generate_revenue_forecast(
            current_user.id,
            horizon_days=30,
            confidence_level=0.9
        )
        
        logger.info(f"Revenue analytics generated for user: {current_user.id}, total revenue: {total_revenue}")
        
        return RevenueAnalyticsResponse(
            total_revenue=total_revenue,
            revenue_by_platform=revenue_by_platform,
            revenue_by_type=revenue_by_type,
            growth_rate=growth_rate,
            top_earning_content=top_earning_content,
            revenue_trend=revenue_trend,
            forecasted_revenue=forecasted_revenue
        )
        
    except Exception as e:
        logger.error(f"Error generating revenue analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate revenue analytics: {str(e)}"
        )

@router.post("/licensing/create", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_licensing_deal(
    licensing_request: LicensingDealRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    licensing_service: LicensingService = Depends()
):
    """
    Create automated licensing deal with smart contract generation.
    
    Features:
    - Automated legal document generation
    - Multi-jurisdiction compliance
    - Smart contract integration (blockchain-based)
    - Royalty calculation and distribution
    - Usage monitoring and compliance tracking
    """
    try:
        # Validate content belongs to user
        fingerprint = db.query(ContentFingerprint).filter(
            ContentFingerprint.id == licensing_request.content_id,
            ContentFingerprint.user_id == current_user.id
        ).first()
        
        if not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Generate licensing deal ID
        deal_id = str(uuid4())
        
        # Create licensing agreement documents
        legal_documents = await licensing_service.generate_licensing_agreement(
            deal_id=deal_id,
            licensor=current_user,
            licensee_info={
                'name': licensing_request.licensee_name,
                'email': licensing_request.licensee_email
            },
            content=fingerprint,
            terms={
                'usage_type': licensing_request.usage_type,
                'territory': licensing_request.territory,
                'duration_months': licensing_request.duration_months,
                'fee_amount': licensing_request.fee_amount,
                'royalty_percentage': licensing_request.royalty_percentage,
                'terms_conditions': licensing_request.terms_conditions
            }
        )
        
        # Calculate payment schedule
        payment_schedule = await licensing_service.calculate_payment_schedule(
            fee_amount=licensing_request.fee_amount,
            duration_months=licensing_request.duration_months,
            royalty_percentage=licensing_request.royalty_percentage
        )
        
        # Create licensing deal record
        licensing_deal = LicensingDeal(
            id=deal_id,
            user_id=current_user.id,
            content_id=licensing_request.content_id,
            licensee_name=licensing_request.licensee_name,
            licensee_email=licensing_request.licensee_email,
            usage_type=licensing_request.usage_type,
            territory=licensing_request.territory,
            fee_amount=licensing_request.fee_amount,
            royalty_percentage=licensing_request.royalty_percentage,
            duration_months=licensing_request.duration_months,
            legal_documents=legal_documents,
            payment_schedule=payment_schedule,
            status="pending_signature",
            created_at=datetime.utcnow()
        )
        
        db.add(licensing_deal)
        db.commit()
        
        # Send licensing agreement to licensee
        background_tasks.add_task(
            licensing_service.send_licensing_agreement,
            deal_id,
            licensing_request.licensee_email
        )
        
        # Setup usage monitoring
        background_tasks.add_task(
            licensing_service.setup_usage_monitoring,
            deal_id,
            licensing_request.content_id
        )
        
        # Create blockchain smart contract if enabled
        if settings.BLOCKCHAIN_ENABLED:
            background_tasks.add_task(
                licensing_service.deploy_smart_contract,
                deal_id,
                legal_documents
            )
        
        logger.info(f"Licensing deal created: {deal_id} for content: {licensing_request.content_id}")
        
        return {
            "deal_id": deal_id,
            "status": "pending_signature",
            "licensee": licensing_request.licensee_name,
            "content_id": licensing_request.content_id,
            "fee_amount": float(licensing_request.fee_amount),
            "duration_months": licensing_request.duration_months,
            "territory": licensing_request.territory,
            "usage_type": licensing_request.usage_type,
            "payment_schedule": payment_schedule,
            "legal_documents_generated": len(legal_documents),
            "blockchain_contract": "deploying" if settings.BLOCKCHAIN_ENABLED else "disabled",
            "next_steps": [
                "Legal agreement sent to licensee",
                "Awaiting digital signature",
                "Usage monitoring activated",
                "Payment tracking enabled"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating licensing deal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Licensing deal creation failed: {str(e)}"
        )

@router.post("/payout", response_model=Dict[str, Any])
async def process_payout(
    payout_request: PayoutRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    payment_service: PaymentService = Depends()
):
    """
    Process revenue payout with multi-currency and multi-method support.
    
    Features:
    - Multiple payment methods (bank transfer, PayPal, Stripe, crypto)
    - Multi-currency support with real-time exchange rates
    - Tax calculation and withholding
    - Automated invoicing and documentation
    - Fraud detection and security validation
    """
    try:
        # Validate user has sufficient balance
        available_balance = await payment_service.get_available_balance(
            current_user.id,
            payout_request.currency
        )
        
        if available_balance < payout_request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: {available_balance} {payout_request.currency}"
            )
        
        # Validate payment method and details
        payment_validation = await payment_service.validate_payment_method(
            payout_request.payment_method,
            payout_request.payment_details
        )
        
        if not payment_validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment method: {payment_validation['error']}"
            )
        
        # Generate payout ID
        payout_id = str(uuid4())
        
        # Calculate fees and taxes
        fee_calculation = await payment_service.calculate_payout_fees(
            amount=payout_request.amount,
            currency=payout_request.currency,
            payment_method=payout_request.payment_method,
            user_location=current_user.location
        )
        
        # Create payout record
        payout_record = PayoutRecord(
            id=payout_id,
            user_id=current_user.id,
            amount=payout_request.amount,
            currency=payout_request.currency,
            payment_method=payout_request.payment_method,
            payment_details=payout_request.payment_details,
            fees=fee_calculation['total_fees'],
            taxes=fee_calculation['taxes'],
            net_amount=fee_calculation['net_amount'],
            status="processing",
            notes=payout_request.notes,
            created_at=datetime.utcnow()
        )
        
        db.add(payout_record)
        db.commit()
        
        # Process payout in background
        background_tasks.add_task(
            payment_service.execute_payout,
            payout_id,
            current_user.id
        )
        
        # Generate invoice and tax documents
        background_tasks.add_task(
            payment_service.generate_payout_documentation,
            payout_id,
            current_user.id
        )
        
        logger.info(f"Payout processing initiated: {payout_id} for user: {current_user.id}")
        
        return {
            "payout_id": payout_id,
            "status": "processing",
            "gross_amount": float(payout_request.amount),
            "fees": float(fee_calculation['total_fees']),
            "taxes": float(fee_calculation['taxes']),
            "net_amount": float(fee_calculation['net_amount']),
            "currency": payout_request.currency,
            "payment_method": payout_request.payment_method,
            "estimated_completion": fee_calculation['estimated_completion'],
            "tracking_number": fee_calculation.get('tracking_number'),
            "fee_breakdown": fee_calculation['fee_breakdown']
        }
        
    except Exception as e:
        logger.error(f"Error processing payout: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payout processing failed: {str(e)}"
        )

@router.post("/forecast", response_model=Dict[str, Any])
async def generate_revenue_forecast(
    forecast_request: RevenueForecastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    monetization_service: MonetizationService = Depends()
):
    """
    Generate AI-powered revenue forecasts with advanced modeling.
    
    Features:
    - Machine learning ensemble models (LSTM, ARIMA, Prophet)
    - Seasonal pattern recognition and adjustment
    - Market trend integration and external factor analysis
    - Scenario analysis with confidence intervals
    - Platform-specific forecasting with cross-correlation
    """
    try:
        # Validate content IDs if provided
        if forecast_request.content_ids:
            fingerprints = db.query(ContentFingerprint).filter(
                ContentFingerprint.id.in_(forecast_request.content_ids),
                ContentFingerprint.user_id == current_user.id
            ).all()
            
            if len(fingerprints) != len(forecast_request.content_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more content items not found"
                )
        
        # Generate forecasts using AI models
        forecast_data = await monetization_service.generate_comprehensive_forecast(
            user_id=current_user.id,
            content_ids=forecast_request.content_ids,
            horizon=forecast_request.forecast_horizon.value,
            confidence_level=forecast_request.confidence_level,
            include_seasonality=forecast_request.include_seasonality,
            scenario_analysis=forecast_request.scenario_analysis
        )
        
        # Calculate forecast accuracy metrics from historical data
        accuracy_metrics = await monetization_service.calculate_forecast_accuracy(
            current_user.id,
            forecast_request.forecast_horizon.value
        )
        
        # Generate actionable insights and recommendations
        insights = await monetization_service.generate_forecast_insights(
            forecast_data,
            current_user.id
        )
        
        logger.info(f"Revenue forecast generated for user: {current_user.id}, horizon: {forecast_request.forecast_horizon.value}")
        
        return {
            "forecast_id": str(uuid4()),
            "user_id": current_user.id,
            "forecast_horizon": forecast_request.forecast_horizon.value,
            "confidence_level": forecast_request.confidence_level,
            "generated_at": datetime.utcnow(),
            "forecast_data": forecast_data,
            "accuracy_metrics": accuracy_metrics,
            "insights": insights,
            "model_performance": {
                "primary_model": forecast_data.get('primary_model'),
                "ensemble_weight": forecast_data.get('ensemble_weight'),
                "seasonality_detected": forecast_data.get('seasonality_detected'),
                "trend_direction": forecast_data.get('trend_direction')
            },
            "recommendations": insights.get('recommendations', [])
        }
        
    except Exception as e:
        logger.error(f"Error generating revenue forecast: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revenue forecast generation failed: {str(e)}"
        )

@router.get("/deals", response_model=List[Dict[str, Any]])
async def get_licensing_deals(
    status: Optional[str] = Query(None, description="Filter by deal status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all licensing deals for the current user."""
    try:
        query = db.query(LicensingDeal).filter(
            LicensingDeal.user_id == current_user.id
        )
        
        if status:
            query = query.filter(LicensingDeal.status == status)
        
        deals = query.order_by(LicensingDeal.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for deal in deals:
            result.append({
                "deal_id": deal.id,
                "licensee_name": deal.licensee_name,
                "content_id": deal.content_id,
                "usage_type": deal.usage_type,
                "fee_amount": float(deal.fee_amount),
                "status": deal.status,
                "created_at": deal.created_at,
                "territory": deal.territory,
                "duration_months": deal.duration_months
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving licensing deals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve licensing deals: {str(e)}"
        )

@router.get("/balance", response_model=Dict[str, Any])
async def get_account_balance(
    currency: str = Query("EUR", description="Currency for balance display"),
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends()
):
    """Get current account balance and payout information."""
    try:
        balance_info = await payment_service.get_comprehensive_balance_info(
            current_user.id,
            currency
        )
        
        return {
            "user_id": current_user.id,
            "primary_currency": currency,
            "available_balance": balance_info['available_balance'],
            "pending_balance": balance_info['pending_balance'],
            "total_earnings": balance_info['total_earnings'],
            "last_payout": balance_info['last_payout'],
            "next_payout_eligible": balance_info['next_payout_eligible'],
            "minimum_payout": balance_info['minimum_payout'],
            "supported_currencies": balance_info['supported_currencies'],
            "payment_methods": balance_info['payment_methods']
        }
        
    except Exception as e:
        logger.error(f"Error retrieving account balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve account balance: {str(e)}"
        )

__all__ = ["router"]
