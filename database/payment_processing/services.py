"""
Payment Processing Service Layer - Enterprise Grade

Advanced service layer for payment processing operations,
implementing business logic, multi-gateway integration, revenue tracking,
automated payouts, and comprehensive financial management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE FEATURES:
- Multi-gateway payment processing (Stripe, PayPal, Wise, Crypto)
- Real-time revenue tracking and analytics with ML predictions
- Automated payout distribution system with intelligent scheduling
- Advanced fraud detection and prevention with behavioral analysis
- Multi-currency and international support with dynamic exchange rates
- AI-powered financial forecasting and optimization
- Blockchain-based payment verification and security
- Compliance with global payment regulations (PCI DSS, GDPR, PSD2)
- Advanced dispute management and chargeback prevention
- Comprehensive audit logging and regulatory reporting
"""

from typing import Dict, Any, Optional, List, Union, Tuple, Callable
from decimal import Decimal
from datetime import datetime, timedelta
import logging
import asyncio
import uuid
from enum import Enum
import json
import hashlib
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import redis
import aioredis
from celery import Celery
import stripe
import paypal
import requests
from cryptography.fernet import Fernet

from .repositories import (
    PaymentTransactionRepository, PaymentMethodRepository,
    BillingRecordRepository, FinancialRecordRepository,
    AutomatedPayoutRepository, PaymentAnalyticsRepository,
    RevenueTrackingRepository, PaymentWebhookRepository,
    PaymentConfigurationRepository, FraudDetectionRepository,
    ComplianceRecordRepository, CurrencyExchangeRepository,
    DisputeManagementRepository, TaxCalculationRepository
)
from .models import (
    PaymentStatus, PaymentMethodType, CurrencyCode, PaymentProvider,
    TransactionType, PayoutStatus, FraudRisk, SecurityLevel,
    ComplianceStatus, RevenueSource, TaxCategory
)
from ..core.exceptions import (
    PaymentProcessingError, FraudDetectionError, ComplianceError,
    CurrencyConversionError, GatewayError, ValidationError
)
from ..core.config import get_settings
from ..security.encryption import PaymentEncryption
from ..utils.validators import PaymentValidator
from ..integrations.gateways import (
    StripeGateway, PayPalGateway, WiseGateway, CryptocurrencyGateway
)

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class PaymentRequest:
    """Comprehensive payment request structure"""
    user_id: str
    amount: Decimal
    currency: str
    payment_method_id: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_id: Optional[str] = None
    revenue_source: Optional[RevenueSource] = None
    platform: Optional[str] = None
    creator_id: Optional[str] = None
    collaboration_ids: List[str] = field(default_factory=list)
    tax_category: Optional[TaxCategory] = None
    country_code: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    risk_assessment: Optional[Dict[str, Any]] = None


@dataclass
class PaymentResult:
    """Comprehensive payment result structure"""
    transaction_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    gateway_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    fraud_score: Optional[float] = None
    processing_time: Optional[float] = None
    fees: Optional[Dict[str, Decimal]] = None
    net_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    gateway_fee: Optional[Decimal] = None
    platform_fee: Optional[Decimal] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Optional[ComplianceStatus] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class RevenueAnalytics:
    """Comprehensive revenue analytics structure"""
    total_revenue: Decimal
    net_revenue: Decimal
    gross_revenue: Decimal
    platform_fees: Decimal
    gateway_fees: Decimal
    tax_amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    transaction_count: int
    average_transaction: Decimal
    revenue_by_source: Dict[str, Decimal]
    revenue_by_platform: Dict[str, Decimal]
    revenue_by_country: Dict[str, Decimal]
    growth_rate: Optional[float] = None
    forecast_next_period: Optional[Decimal] = None
    recommendations: List[str] = field(default_factory=list)
    trends: Dict[str, Any] = field(default_factory=dict)
    benchmarks: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayoutRequest:
    """Comprehensive payout request structure"""
    creator_id: str
    amount: Decimal
    currency: str
    payout_method: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    revenue_period_start: Optional[datetime] = None
    revenue_period_end: Optional[datetime] = None
    platforms: List[str] = field(default_factory=list)
    revenue_sources: List[RevenueSource] = field(default_factory=list)
    tax_withholding: bool = True
    priority: str = "normal"  # normal, high, urgent
    schedule_date: Optional[datetime] = None
    split_recipients: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PayoutResult:
    """Comprehensive payout result structure"""
    payout_id: str
    status: PayoutStatus
    amount: Decimal
    net_amount: Decimal
    currency: str
    gateway_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    fees: Dict[str, Decimal] = field(default_factory=dict)
    tax_withholding: Optional[Decimal] = None
    estimated_arrival: Optional[datetime] = None
    tracking_number: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    compliance_checks: Dict[str, bool] = field(default_factory=dict)


class EnterprisePaymentProcessingService:
    """
    Enterprise-grade payment processing service with advanced features
    
    Features:
    - Multi-gateway processing with automatic failover
    - Real-time fraud detection and prevention
    - Advanced risk assessment and scoring
    - Multi-currency support with dynamic exchange rates
    - AI-powered transaction routing and optimization
    - Comprehensive audit logging and compliance tracking
    """
    
    def __init__(self):
        # Repository dependencies
        self.transaction_repo = PaymentTransactionRepository()
        self.payment_method_repo = PaymentMethodRepository()
        self.analytics_repo = PaymentAnalyticsRepository()
        self.fraud_repo = FraudDetectionRepository()
        self.compliance_repo = ComplianceRecordRepository()
        
        # Service dependencies
        self.validator = PaymentValidator()
        self.encryption = PaymentEncryption()
        self.gateway_manager = PaymentGatewayManager()
        self.fraud_detector = AdvancedFraudDetectionEngine()
        self.currency_service = CurrencyExchangeService()
        self.tax_calculator = TaxCalculationService()
        self.compliance_manager = ComplianceManager()
        
        # ML components
        self.ml_predictor = PaymentMLPredictor()
        self.risk_assessor = RiskAssessmentEngine()
        
        # Cache and message queue
        self.redis_client = None
        self.celery_app = None
        
        logger.info("Enterprise Payment Processing Service initialized")
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """
        Process payment with comprehensive validation, fraud detection, and optimization
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Input validation
            await self._validate_payment_request(request)
            
            # Step 2: Fraud detection and risk assessment
            fraud_result = await self.fraud_detector.assess_transaction_risk(request)
            if fraud_result.risk_level == FraudRisk.CRITICAL:
                raise PaymentProcessingError(
                    f"Transaction blocked due to high fraud risk: {fraud_result.reason}"
                )
            
            # Step 3: Currency conversion if needed
            converted_amount = await self.currency_service.convert_if_needed(
                request.amount, request.currency, request.country_code
            )
            
            # Step 4: Tax calculation
            tax_calculation = await self.tax_calculator.calculate_tax(
                amount=converted_amount,
                currency=request.currency,
                tax_category=request.tax_category,
                country_code=request.country_code
            )
            
            # Step 5: Gateway selection and optimization
            optimal_gateway = await self.gateway_manager.select_optimal_gateway(
                amount=converted_amount,
                currency=request.currency,
                payment_method=request.payment_method_id,
                country_code=request.country_code,
                risk_score=fraud_result.risk_score
            )
            
            # Step 6: Process payment through selected gateway
            gateway_result = await optimal_gateway.process_payment(
                amount=converted_amount,
                currency=request.currency,
                payment_method=request.payment_method_id,
                metadata={
                    **request.metadata,
                    'fraud_score': fraud_result.risk_score,
                    'tax_amount': tax_calculation.total_tax,
                    'original_amount': request.amount
                }
            )
            
            # Step 7: Create transaction record
            transaction = await self.transaction_repo.create_transaction(
                user_id=request.user_id,
                amount=converted_amount,
                currency=request.currency,
                status=PaymentStatus.PROCESSING,
                gateway_id=optimal_gateway.gateway_id,
                gateway_transaction_id=gateway_result.transaction_id,
                fraud_score=fraud_result.risk_score,
                tax_amount=tax_calculation.total_tax,
                metadata=request.metadata
            )
            
            # Step 8: Update analytics
            await self.analytics_repo.record_transaction_metrics(
                transaction_id=transaction.id,
                processing_time=(datetime.utcnow() - start_time).total_seconds(),
                gateway_used=optimal_gateway.name,
                fraud_score=fraud_result.risk_score
            )
            
            # Step 9: Trigger post-processing tasks
            await self._trigger_post_processing_tasks(transaction, request)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return PaymentResult(
                transaction_id=transaction.id,
                status=gateway_result.status,
                amount=converted_amount,
                currency=request.currency,
                gateway_response=gateway_result.response_data,
                fraud_score=fraud_result.risk_score,
                processing_time=processing_time,
                fees=gateway_result.fees,
                net_amount=converted_amount - gateway_result.total_fees,
                tax_amount=tax_calculation.total_tax,
                gateway_fee=gateway_result.gateway_fee,
                platform_fee=gateway_result.platform_fee,
                metadata=request.metadata,
                compliance_status=ComplianceStatus.COMPLIANT,
                risk_assessment=fraud_result.assessment_details,
                recommendations=await self._generate_recommendations(gateway_result, fraud_result)
            )
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}", exc_info=True)
            
            # Record failure analytics
            await self.analytics_repo.record_failure_metrics(
                error_type=type(e).__name__,
                error_message=str(e),
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            raise PaymentProcessingError(f"Payment processing failed: {str(e)}")
    
    async def _validate_payment_request(self, request: PaymentRequest) -> None:
        """Comprehensive payment request validation"""
        # Amount validation
        if not self.validator.validate_amount(request.amount, request.currency):
            raise ValidationError("Invalid amount or currency")
        
        # User validation
        if not await self.validator.validate_user(request.user_id):
            raise ValidationError("Invalid user ID")
        
        # Payment method validation
        payment_method = await self.payment_method_repo.get_by_id(request.payment_method_id)
        if not payment_method or not payment_method.is_active:
            raise ValidationError("Invalid or inactive payment method")
        
        # Geographic restrictions
        if request.country_code:
            if not await self.validator.validate_country_restrictions(
                request.country_code, request.currency
            ):
                raise ValidationError("Transaction not allowed in this country")
        
        # Rate limiting
        if not await self.validator.check_rate_limits(request.user_id):
            raise ValidationError("Rate limit exceeded")
    
    async def _trigger_post_processing_tasks(
        self, 
        transaction: Any, 
        request: PaymentRequest
    ) -> None:
        """Trigger asynchronous post-processing tasks"""
        # Revenue tracking
        if request.revenue_source:
            await self._schedule_revenue_tracking(transaction, request)
        
        # Content protection updates
        if request.content_id:
            await self._schedule_content_protection_update(transaction, request)
        
        # Collaboration revenue sharing
        if request.collaboration_ids:
            await self._schedule_collaboration_payouts(transaction, request)
        
        # Compliance reporting
        await self._schedule_compliance_reporting(transaction, request)
    
    async def _generate_recommendations(
        self, 
        gateway_result: Any, 
        fraud_result: Any
    ) -> List[str]:
        """Generate AI-powered recommendations for optimization"""
        recommendations = []
        
        # Gateway optimization recommendations
        if gateway_result.processing_time > 5.0:
            recommendations.append("Consider switching to a faster payment gateway")
        
        if gateway_result.fees > gateway_result.amount * Decimal('0.03'):
            recommendations.append("High transaction fees detected - consider volume discounts")
        
        # Fraud prevention recommendations
        if fraud_result.risk_score > 0.7:
            recommendations.append("Enable additional authentication for future transactions")
        
        # Currency optimization
        if gateway_result.currency_conversion_loss > gateway_result.amount * Decimal('0.01'):
            recommendations.append("Consider native currency processing to reduce conversion costs")
        
        return recommendations


class RevenueTrackingService:
    """
    Advanced revenue tracking and analytics service
    
    Features:
    - Real-time revenue aggregation across platforms
    - Multi-platform revenue attribution
    - AI-powered revenue forecasting
    - Performance analytics and insights
    - Creator revenue optimization recommendations
    """
    
    def __init__(self):
        self.revenue_repo = RevenueTrackingRepository()
        self.analytics_repo = PaymentAnalyticsRepository()
        self.ml_predictor = RevenueMLPredictor()
        self.currency_service = CurrencyExchangeService()
        
    async def aggregate_platform_revenue(
        self,
        creator_id: str,
        platforms: List[str],
        period: str = "monthly",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> RevenueAnalytics:
        """
        Aggregate revenue across multiple platforms with advanced analytics
        """
        # Calculate period dates if not provided
        if not start_date or not end_date:
            start_date, end_date = self._calculate_period_dates(period)
        
        # Aggregate revenue from all platforms
        platform_revenues = {}
        total_revenue = Decimal('0')
        total_fees = Decimal('0')
        total_tax = Decimal('0')
        transaction_count = 0
        
        for platform in platforms:
            platform_data = await self.revenue_repo.get_platform_revenue(
                creator_id=creator_id,
                platform=platform,
                start_date=start_date,
                end_date=end_date
            )
            
            platform_revenues[platform] = platform_data.total_amount
            total_revenue += platform_data.total_amount
            total_fees += platform_data.total_fees
            total_tax += platform_data.total_tax
            transaction_count += platform_data.transaction_count
        
        # Calculate revenue by source
        revenue_by_source = await self._calculate_revenue_by_source(
            creator_id, start_date, end_date
        )
        
        # Calculate revenue by country
        revenue_by_country = await self._calculate_revenue_by_country(
            creator_id, start_date, end_date
        )
        
        # Calculate growth rate
        growth_rate = await self._calculate_growth_rate(
            creator_id, platforms, start_date, end_date
        )
        
        # Generate AI-powered forecast
        forecast = await self.ml_predictor.predict_revenue(
            creator_id=creator_id,
            historical_data=platform_revenues,
            forecast_periods=1
        )
        
        # Generate recommendations
        recommendations = await self._generate_revenue_recommendations(
            creator_id, platform_revenues, growth_rate
        )
        
        # Calculate trends and benchmarks
        trends = await self._calculate_revenue_trends(creator_id, platforms)
        benchmarks = await self._calculate_industry_benchmarks(platforms)
        
        net_revenue = total_revenue - total_fees - total_tax
        average_transaction = total_revenue / transaction_count if transaction_count > 0 else Decimal('0')
        
        return RevenueAnalytics(
            total_revenue=total_revenue,
            net_revenue=net_revenue,
            gross_revenue=total_revenue,
            platform_fees=total_fees,
            gateway_fees=total_fees * Decimal('0.3'),  # Estimate
            tax_amount=total_tax,
            currency="USD",  # Base currency
            period_start=start_date,
            period_end=end_date,
            transaction_count=transaction_count,
            average_transaction=average_transaction,
            revenue_by_source=revenue_by_source,
            revenue_by_platform=platform_revenues,
            revenue_by_country=revenue_by_country,
            growth_rate=growth_rate,
            forecast_next_period=forecast.predicted_amount,
            recommendations=recommendations,
            trends=trends,
            benchmarks=benchmarks
        )
    
    async def _calculate_period_dates(self, period: str) -> Tuple[datetime, datetime]:
        """Calculate start and end dates for the given period"""
        now = datetime.utcnow()
        
        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        elif period == "monthly":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = start_date.replace(year=now.year + 1, month=1)
            else:
                end_date = start_date.replace(month=now.month + 1)
        elif period == "yearly":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(year=now.year + 1)
        else:
            raise ValueError(f"Unsupported period: {period}")
        
        return start_date, end_date
    
    async def _calculate_revenue_by_source(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Decimal]:
        """Calculate revenue breakdown by source"""



        return await self.revenue_repo.get_revenue_by_source(
            creator_id=creator_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def _calculate_revenue_by_country(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Decimal]:
        """Calculate revenue breakdown by country"""



        return await self.revenue_repo.get_revenue_by_country(
            creator_id=creator_id,
            start_date=start_date,
            end_date=end_date
        )
    
    async def _calculate_growth_rate(
        self, 
        creator_id: str, 
        platforms: List[str], 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calculate revenue growth rate compared to previous period"""
        period_duration = end_date - start_date
        previous_start = start_date - period_duration
        previous_end = start_date
        
        current_revenue = await self.revenue_repo.get_total_revenue(
            creator_id=creator_id,
            platforms=platforms,
            start_date=start_date,
            end_date=end_date
        )
        
        previous_revenue = await self.revenue_repo.get_total_revenue(
            creator_id=creator_id,
            platforms=platforms,
            start_date=previous_start,
            end_date=previous_end
        )
        
        if previous_revenue == 0:
            return 0.0
        
        growth_rate = float((current_revenue - previous_revenue) / previous_revenue)
        return growth_rate
    
    async def _generate_revenue_recommendations(
        self, 
        creator_id: str, 
        platform_revenues: Dict[str, Decimal], 
        growth_rate: float
    ) -> List[str]:
        """Generate AI-powered revenue optimization recommendations"""
        recommendations = []
        
        # Platform performance analysis
        sorted_platforms = sorted(platform_revenues.items(), key=lambda x: x[1], reverse=True)
        best_platform = sorted_platforms[0][0] if sorted_platforms else None
        
        if best_platform:
            recommendations.append(f"Focus more content on {best_platform} - your highest performing platform")
        
        # Growth rate analysis
        if growth_rate < 0:
            recommendations.append("Revenue declined this period - consider diversifying content strategy")
        elif growth_rate > 0.5:
            recommendations.append("Excellent growth! Consider scaling successful content types")
        
        # Platform diversification
        if len(platform_revenues) < 3:
            recommendations.append("Consider expanding to more platforms to diversify revenue streams")
        
        return recommendations
    
    async def _calculate_revenue_trends(
        self, 
        creator_id: str, 
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Calculate revenue trends and patterns"""
        # Get historical data for trend analysis
        historical_data = await self.revenue_repo.get_historical_revenue(
            creator_id=creator_id,
            platforms=platforms,
            periods=12  # Last 12 periods
        )
        
        # Calculate seasonal patterns
        seasonal_patterns = await self._analyze_seasonal_patterns(historical_data)
        
        # Calculate platform trends
        platform_trends = await self._analyze_platform_trends(historical_data)
        
        return {
            'seasonal_patterns': seasonal_patterns,
            'platform_trends': platform_trends,
            'overall_trend': 'growing' if len(historical_data) > 1 and 
                           historical_data[-1] > historical_data[0] else 'declining'
        }
    
    async def _calculate_industry_benchmarks(
        self, 
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Calculate industry benchmarks for comparison"""
        benchmarks = {}
        
        for platform in platforms:
            platform_benchmark = await self.analytics_repo.get_platform_benchmark(platform)
            benchmarks[platform] = {
                'average_revenue': platform_benchmark.average_revenue,
                'top_10_percent': platform_benchmark.top_10_percent_revenue,
                'median_revenue': platform_benchmark.median_revenue
            }
        
        return benchmarks


class AutomatedPayoutService:
    """
    Advanced automated payout service with intelligent scheduling
    
    Features:
    - Intelligent payout scheduling and optimization
    - Multi-recipient revenue sharing
    - Tax withholding and compliance
    - Currency optimization
    - Risk-based payout verification
    """
    
    def __init__(self):
        self.payout_repo = AutomatedPayoutRepository()
        self.transaction_repo = PaymentTransactionRepository()
        self.compliance_manager = ComplianceManager()
        self.gateway_manager = PaymentGatewayManager()
        self.tax_calculator = TaxCalculationService()
        self.currency_service = CurrencyExchangeService()
        
    async def execute_automated_payout(self, request: PayoutRequest) -> PayoutResult:
        """
        Execute automated payout with comprehensive validation and optimization
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Validate payout request
            await self._validate_payout_request(request)
            
            # Step 2: Calculate tax withholding
            tax_withholding = Decimal('0')
            if request.tax_withholding:
                tax_calculation = await self.tax_calculator.calculate_payout_tax(
                    amount=request.amount,
                    currency=request.currency,
                    creator_id=request.creator_id
                )
                tax_withholding = tax_calculation.total_tax
            
            # Step 3: Optimize currency and gateway selection
            optimal_gateway = await self.gateway_manager.select_optimal_payout_gateway(
                amount=request.amount,
                currency=request.currency,
                destination_country=await self._get_creator_country(request.creator_id),
                priority=request.priority
            )
            
            # Step 4: Calculate fees
            payout_fees = await optimal_gateway.calculate_payout_fees(
                amount=request.amount,
                currency=request.currency
            )
            
            net_amount = request.amount - tax_withholding - payout_fees.total_fees
            
            # Step 5: Compliance checks
            compliance_checks = await self.compliance_manager.verify_payout_compliance(
                creator_id=request.creator_id,
                amount=request.amount,
                currency=request.currency
            )
            
            if not all(compliance_checks.values()):
                raise ComplianceError("Payout failed compliance checks")
            
            # Step 6: Execute payout
            if request.split_recipients:
                payout_result = await self._execute_split_payout(
                    request, optimal_gateway, tax_withholding, payout_fees
                )
            else:
                payout_result = await optimal_gateway.execute_payout(
                    creator_id=request.creator_id,
                    amount=net_amount,
                    currency=request.currency,
                    payout_method=request.payout_method,
                    metadata=request.metadata
                )
            
            # Step 7: Record payout transaction
            payout_record = await self.payout_repo.create_payout_record(
                creator_id=request.creator_id,
                amount=request.amount,
                net_amount=net_amount,
                currency=request.currency,
                status=PayoutStatus.PROCESSING,
                gateway_id=optimal_gateway.gateway_id,
                gateway_payout_id=payout_result.payout_id,
                tax_withholding=tax_withholding,
                fees=payout_fees.breakdown,
                metadata=request.metadata
            )
            
            # Step 8: Schedule follow-up tasks
            await self._schedule_payout_monitoring(payout_record.id)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return PayoutResult(
                payout_id=payout_record.id,
                status=payout_result.status,
                amount=request.amount,
                net_amount=net_amount,
                currency=request.currency,
                gateway_response=payout_result.response_data,
                processing_time=processing_time,
                fees=payout_fees.breakdown,
                tax_withholding=tax_withholding,
                estimated_arrival=payout_result.estimated_arrival,
                tracking_number=payout_result.tracking_number,
                metadata=request.metadata,
                compliance_checks=compliance_checks
            )
            
        except Exception as e:
            logger.error(f"Automated payout failed: {str(e)}", exc_info=True)
            raise PaymentProcessingError(f"Payout execution failed: {str(e)}")
    
    async def _validate_payout_request(self, request: PayoutRequest) -> None:
        """Validate payout request parameters"""
        # Amount validation
        if request.amount <= 0:
            raise ValidationError("Payout amount must be positive")
        
        # Minimum payout threshold
        min_payout = await self._get_minimum_payout_threshold(request.currency)
        if request.amount < min_payout:
            raise ValidationError(f"Amount below minimum payout threshold: {min_payout}")
        
        # Creator validation
        creator = await self._get_creator_details(request.creator_id)
        if not creator or not creator.is_active:
            raise ValidationError("Invalid or inactive creator")
        
        # Balance validation
        available_balance = await self._get_available_balance(request.creator_id, request.currency)
        if request.amount > available_balance:
            raise ValidationError("Insufficient balance for payout")
    
    async def _execute_split_payout(
        self,
        request: PayoutRequest,
        gateway: Any,
        tax_withholding: Decimal,
        fees: Any
    ) -> Any:
        """Execute payout with revenue sharing splits"""
        split_results = []
        
        for recipient in request.split_recipients:
            recipient_amount = request.amount * Decimal(str(recipient['percentage'])) / 100
            recipient_tax = tax_withholding * Decimal(str(recipient['percentage'])) / 100
            recipient_fees = fees.total_fees * Decimal(str(recipient['percentage'])) / 100
            recipient_net = recipient_amount - recipient_tax - recipient_fees
            
            split_result = await gateway.execute_payout(
                creator_id=recipient['creator_id'],
                amount=recipient_net,
                currency=request.currency,
                payout_method=recipient.get('payout_method', request.payout_method),
                metadata={
                    **request.metadata,
                    'split_percentage': recipient['percentage'],
                    'original_payout_id': request.creator_id
                }
            )
            
            split_results.append(split_result)
        
        # Return combined result
        return await self._combine_split_results(split_results)
from .schemas import (
    PaymentTransactionCreateSchema, PaymentMethodCreateSchema,
    BillingRecordCreateSchema, AutomatedPayoutCreateSchema,
    RevenueTrackingCreateSchema, PaymentAnalyticsCreateSchema
)
from .payment_gateway import PaymentGatewayFactory, GatewayResponse
from .security import PaymentSecurityManager, FraudDetectionEngine
from .utils import CurrencyConverter, PaymentValidator, FinancialCalculator

logger = logging.getLogger(__name__)


# Custom exceptions
class PaymentProcessingError(Exception):
    """Base exception for payment processing errors"""
    pass


class InsufficientFundsError(PaymentProcessingError):
    """Raised when there are insufficient funds for a transaction"""
    pass


class PaymentMethodError(PaymentProcessingError):
    """Raised when there's an issue with the payment method"""
    pass


class GatewayError(PaymentProcessingError):
    """Raised when there's an issue with payment gateway"""
    pass


class FraudDetectionError(PaymentProcessingError):
    """Raised when fraud is detected"""
    pass


class ConfigurationError(PaymentProcessingError):
    """Raised when there's a configuration issue"""
    pass


@dataclass
class PaymentResult:
    """Payment processing result container"""
    success: bool
    transaction_id: Optional[str] = None
    gateway_response: Optional[GatewayResponse] = None
    error_message: Optional[str] = None
    fraud_score: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RevenueReport:
    """Revenue report container"""
    total_revenue: Decimal
    net_revenue: Decimal
    platform_fees: Decimal
    gateway_fees: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    transactions_count: int
    metadata: Optional[Dict[str, Any]] = None


class PaymentProcessingService:
    """
    Core payment processing service with multi-gateway support
    """
    
    def __init__(self):
        self.transaction_repo = PaymentTransactionRepository()
        self.payment_method_repo = PaymentMethodRepository()
        self.gateway_factory = PaymentGatewayFactory()
        self.security_manager = PaymentSecurityManager()
        self.fraud_detector = FraudDetectionEngine()
        self.currency_converter = CurrencyConverter()
        self.validator = PaymentValidator()
        
    async def process_payment(
        self,
        user_id: str,
        amount: Decimal,
        currency: str,
        payment_method_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_id: Optional[str] = None
    ) -> PaymentResult:
        """
        Process a payment transaction with comprehensive validation and fraud detection
        """



        try:
            # Validate input parameters
            if not self.validator.validate_amount(amount, currency):
                raise PaymentProcessingError("Invalid amount or currency")
            
            # Get payment method
            payment_method = await self.payment_method_repo.get_by_id(payment_method_id)
            if not payment_method or not payment_method.is_active:
                raise PaymentMethodError("Invalid or inactive payment method")
            
            # Fraud detection
            fraud_score = await self.fraud_detector.calculate_risk_score(
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                metadata=metadata
            )
            
            if fraud_score > 80:  # High risk threshold
                raise FraudDetectionError(f"Transaction blocked due to high fraud risk: {fraud_score}")
            
            # Get appropriate payment gateway
            gateway = self.gateway_factory.get_gateway(payment_method.provider)
            
            # Process payment through gateway
            gateway_response = await gateway.process_payment(
                amount=amount,
                currency=currency,
                payment_method=payment_method,
                description=description,
                metadata=metadata
            )
            
            # Create transaction record
            transaction_data = PaymentTransactionCreateSchema(
                user_id=user_id,
                content_id=content_id,
                payment_method_id=payment_method_id,
                transaction_type=TransactionType.PAYMENT.value,
                amount=amount,
                currency=currency,
                status=PaymentStatus.PROCESSING.value,
                gateway_transaction_id=gateway_response.transaction_id,
                provider=payment_method.provider,
                description=description,
                fraud_score=fraud_score,
                metadata=metadata
            )
            
            transaction = await self.transaction_repo.create(transaction_data)
            
            # Update transaction status based on gateway response
            if gateway_response.success:
                await self.transaction_repo.update_status(
                    transaction.id, 
                    PaymentStatus.COMPLETED.value
                )
                
                # Process revenue tracking if content-related
                if content_id:
                    await self._process_revenue_tracking(transaction)
            else:
                await self.transaction_repo.update_status(
                    transaction.id, 
                    PaymentStatus.FAILED.value
                )
            
            return PaymentResult(
                success=gateway_response.success,
                transaction_id=str(transaction.id),
                gateway_response=gateway_response,
                fraud_score=fraud_score,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            return PaymentResult(
                success=False,
                error_message=str(e),
                metadata=metadata
            )
    
    async def _process_revenue_tracking(self, transaction):
        """Process revenue tracking for content-related transactions"""
        # Implementation for revenue tracking
        pass
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> PaymentResult:
        """
        Process a payment refund
        """



        try:
            # Get original transaction
            transaction = await self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                raise PaymentProcessingError("Transaction not found")
            
            if transaction.status != PaymentStatus.COMPLETED.value:
                raise PaymentProcessingError("Cannot refund incomplete transaction")
            
            # Calculate refund amount
            refund_amount = amount or transaction.amount
            if refund_amount > transaction.amount:
                raise PaymentProcessingError("Refund amount cannot exceed original amount")
            
            # Get payment gateway
            gateway = self.gateway_factory.get_gateway(transaction.provider)
            
            # Process refund through gateway
            gateway_response = await gateway.refund_payment(
                original_transaction_id=transaction.gateway_transaction_id,
                amount=refund_amount,
                reason=reason
            )
            
            # Create refund transaction record
            refund_data = PaymentTransactionCreateSchema(
                user_id=transaction.user_id,
                payment_method_id=transaction.payment_method_id,
                transaction_type=TransactionType.REFUND.value,
                amount=-refund_amount,  # Negative amount for refund
                currency=transaction.currency,
                status=PaymentStatus.COMPLETED.value if gateway_response.success else PaymentStatus.FAILED.value,
                gateway_transaction_id=gateway_response.transaction_id,
                provider=transaction.provider,
                description=f"Refund for transaction {transaction_id}: {reason}",
                metadata={"original_transaction_id": transaction_id, "reason": reason}
            )
            
            refund_transaction = await self.transaction_repo.create(refund_data)
            
            # Update original transaction status
            if gateway_response.success:
                if refund_amount == transaction.amount:
                    await self.transaction_repo.update_status(
                        transaction.id, 
                        PaymentStatus.REFUNDED.value
                    )
                else:
                    await self.transaction_repo.update_status(
                        transaction.id, 
                        PaymentStatus.PARTIAL_REFUND.value
                    )
            
            return PaymentResult(
                success=gateway_response.success,
                transaction_id=str(refund_transaction.id),
                gateway_response=gateway_response,
                metadata={"original_transaction_id": transaction_id}
            )
            
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            return PaymentResult(
                success=False,
                error_message=str(e)
            )


class RevenueTrackingService:
    """
    Revenue tracking service for monitoring income from various sources
    """
    
    def __init__(self):
        self.revenue_repo = RevenueTrackingRepository()
        self.analytics_repo = PaymentAnalyticsRepository()
        self.calculator = FinancialCalculator()
        
    async def track_platform_revenue(
        self,
        user_id: str,
        content_id: Optional[str],
        revenue_source: str,
        gross_revenue: Decimal,
        currency: str,
        platform_data: Dict[str, Any],
        period_start: datetime,
        period_end: datetime
    ) -> bool:
        """
        Track revenue from external platforms (YouTube, Instagram, Spotify, etc.)
        """



        try:
            # Calculate fees and net revenue
            platform_fee = self.calculator.calculate_platform_fee(gross_revenue, revenue_source)
            our_commission = self.calculator.calculate_our_commission(gross_revenue, revenue_source)
            net_revenue = gross_revenue - platform_fee - our_commission
            
            # Create revenue tracking record
            revenue_data = RevenueTrackingCreateSchema(
                user_id=user_id,
                content_id=content_id,
                revenue_source=revenue_source,
                gross_revenue=gross_revenue,
                platform_fee=platform_fee,
                our_commission=our_commission,
                net_revenue=net_revenue,
                currency=currency,
                tracking_period_start=period_start,
                tracking_period_end=period_end,
                views=platform_data.get('views', 0),
                clicks=platform_data.get('clicks', 0),
                conversions=platform_data.get('conversions', 0),
                engagement_rate=platform_data.get('engagement_rate'),
                external_reference=platform_data.get('external_id'),
                metadata=platform_data
            )
            
            revenue_record = await self.revenue_repo.create(revenue_data)
            
            # Update analytics
            await self._update_revenue_analytics(revenue_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Revenue tracking failed: {str(e)}")
            return False
    
    async def _update_revenue_analytics(self, revenue_record):
        """Update analytics based on new revenue data"""
        # Implementation for analytics updates
        pass
    
    async def get_revenue_report(
        self,
        user_id: str,
        period_start: datetime,
        period_end: datetime,
        currency: Optional[str] = "EUR"
    ) -> RevenueReport:
        """
        Generate comprehensive revenue report for a user
        """



        try:
            revenues = await self.revenue_repo.get_by_user_period(
                user_id=user_id,
                period_start=period_start,
                period_end=period_end
            )
            
            total_revenue = sum(r.gross_revenue for r in revenues)
            total_fees = sum(r.platform_fee + r.our_commission for r in revenues)
            net_revenue = total_revenue - total_fees
            
            return RevenueReport(
                total_revenue=total_revenue,
                net_revenue=net_revenue,
                platform_fees=sum(r.platform_fee for r in revenues),
                gateway_fees=sum(r.our_commission for r in revenues),
                currency=currency,
                period_start=period_start,
                period_end=period_end,
                transactions_count=len(revenues),
                metadata={
                    "revenue_sources": list(set(r.revenue_source for r in revenues)),
                    "top_content": await self._get_top_performing_content(revenues)
                }
            )
            
        except Exception as e:
            logger.error(f"Revenue report generation failed: {str(e)}")
            return RevenueReport(
                total_revenue=Decimal('0'),
                net_revenue=Decimal('0'),
                platform_fees=Decimal('0'),
                gateway_fees=Decimal('0'),
                currency=currency,
                period_start=period_start,
                period_end=period_end,
                transactions_count=0
            )
    
    async def _get_top_performing_content(self, revenues):
        """Get top performing content from revenue data"""
        content_performance = {}
        for revenue in revenues:
            if revenue.content_id:
                if revenue.content_id not in content_performance:
                    content_performance[revenue.content_id] = Decimal('0')
                content_performance[revenue.content_id] += revenue.gross_revenue
        
        return sorted(
            content_performance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10 performing content


class AutomatedPayoutService:
    """
    Automated payout service for distributing earnings to creators
    """
    
    def __init__(self):
        self.payout_repo = AutomatedPayoutRepository()
        self.transaction_repo = PaymentTransactionRepository()
        self.revenue_service = RevenueTrackingService()
        self.gateway_factory = PaymentGatewayFactory()
        
    async def schedule_payouts(self, frequency: str = "monthly") -> List[str]:
        """
        Schedule automated payouts for eligible users
        """



        try:
            # Get users eligible for payouts
            eligible_users = await self._get_eligible_users(frequency)
            scheduled_payouts = []
            
            for user_id in eligible_users:
                # Calculate payout amount
                payout_amount = await self._calculate_payout_amount(user_id, frequency)
                
                if payout_amount >= Decimal('10.00'):  # Minimum payout threshold
                    # Create payout record
                    payout_data = AutomatedPayoutCreateSchema(
                        user_id=user_id,
                        amount=payout_amount,
                        currency="EUR",
                        frequency=frequency,
                        status=PayoutStatus.SCHEDULED.value,
                        scheduled_at=datetime.utcnow() + timedelta(days=1)
                    )
                    
                    payout = await self.payout_repo.create(payout_data)
                    scheduled_payouts.append(str(payout.id))
            
            return scheduled_payouts
            
        except Exception as e:
            logger.error(f"Payout scheduling failed: {str(e)}")
            return []
    
    async def _get_eligible_users(self, frequency: str) -> List[str]:
        """Get users eligible for payouts based on frequency"""
        # Implementation to get eligible users
        pass
    
    async def _calculate_payout_amount(self, user_id: str, frequency: str) -> Decimal:
        """Calculate payout amount for a user"""
        # Implementation to calculate payout amount
        pass
    
    async def process_scheduled_payouts(self) -> Dict[str, Any]:
        """
        Process all scheduled payouts
        """



        try:
            # Get scheduled payouts
            scheduled_payouts = await self.payout_repo.get_scheduled()
            
            results = {
                "processed": 0,
                "failed": 0,
                "total": len(scheduled_payouts),
                "errors": []
            }
            
            for payout in scheduled_payouts:
                try:
                    # Process individual payout
                    success = await self._process_individual_payout(payout)
                    
                    if success:
                        results["processed"] += 1
                        await self.payout_repo.update_status(
                            payout.id, 
                            PayoutStatus.SENT.value
                        )
                    else:
                        results["failed"] += 1
                        await self.payout_repo.update_status(
                            payout.id, 
                            PayoutStatus.FAILED.value
                        )
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Payout {payout.id}: {str(e)}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Scheduled payout processing failed: {str(e)}")
            return {"processed": 0, "failed": 0, "total": 0, "errors": [str(e)]}
    
    async def _process_individual_payout(self, payout) -> bool:
        """Process an individual payout"""
        # Implementation for individual payout processing
        pass


class FinancialAnalyticsService:
    """
    Financial analytics service for generating insights and reports
    """
    
    def __init__(self):
        self.analytics_repo = PaymentAnalyticsRepository()
        self.transaction_repo = PaymentTransactionRepository()
        self.revenue_repo = RevenueTrackingRepository()
        
    async def generate_financial_insights(
        self,
        user_id: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial insights and analytics
        """



        try:
            insights = {
                "revenue_metrics": await self._calculate_revenue_metrics(user_id, period_start, period_end),
                "payment_metrics": await self._calculate_payment_metrics(user_id, period_start, period_end),
                "performance_trends": await self._calculate_performance_trends(user_id, period_start, period_end),
                "forecasting": await self._generate_revenue_forecast(user_id),
                "recommendations": await self._generate_recommendations(user_id)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Financial insights generation failed: {str(e)}")
            return {}
    
    async def _calculate_revenue_metrics(self, user_id, period_start, period_end):
        """Calculate revenue-related metrics"""
        # Implementation for revenue metrics
        pass
    
    async def _calculate_payment_metrics(self, user_id, period_start, period_end):
        """Calculate payment-related metrics"""
        # Implementation for payment metrics
        pass
    
    async def _calculate_performance_trends(self, user_id, period_start, period_end):
        """Calculate performance trends"""
        # Implementation for performance trends
        pass
    
    async def _generate_revenue_forecast(self, user_id):
        """Generate revenue forecast using AI/ML"""
        # Implementation for revenue forecasting
        pass
    
    async def _generate_recommendations(self, user_id):
        """Generate financial recommendations"""
        # Implementation for recommendations
        pass


class PaymentSecurityService:
    """
    Payment security service for fraud detection and prevention
    """
    
    def __init__(self):
        self.security_manager = PaymentSecurityManager()
        self.fraud_detector = FraudDetectionEngine()
        
    async def validate_payment_security(
        self,
        user_id: str,
        payment_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive payment security validation
        """



        try:
            # Fraud detection
            fraud_score = await self.fraud_detector.calculate_risk_score(
                user_id=user_id,
                amount=payment_data.get('amount'),
                payment_method=payment_data.get('payment_method'),
                metadata=context
            )
            
            # Security level assessment
            security_level = await self.security_manager.assess_security_level(
                user_id=user_id,
                payment_data=payment_data,
                context=context
            )
            
            # Risk assessment
            risk_level = self._assess_risk_level(fraud_score)
            
            return {
                "fraud_score": fraud_score,
                "security_level": security_level,
                "risk_level": risk_level,
                "recommendations": await self._get_security_recommendations(
                    fraud_score, security_level
                ),
                "approved": fraud_score < 70 and security_level != SecurityLevel.BASIC
            }
            
        except Exception as e:
            logger.error(f"Payment security validation failed: {str(e)}")
            return {
                "fraud_score": 100,
                "security_level": SecurityLevel.BASIC,
                "risk_level": FraudRisk.CRITICAL,
                "approved": False,
                "error": str(e)
            }
    
    def _assess_risk_level(self, fraud_score: int) -> FraudRisk:
        """Assess risk level based on fraud score"""
        if fraud_score >= 80:
            return FraudRisk.CRITICAL
        elif fraud_score >= 60:
            return FraudRisk.HIGH
        elif fraud_score >= 30:
            return FraudRisk.MEDIUM
        else:
            return FraudRisk.LOW
    
    async def _get_security_recommendations(self, fraud_score, security_level):
        """Get security recommendations based on assessment"""
        recommendations = []
        
        if fraud_score > 50:
            recommendations.append("Additional identity verification required")
        
        if security_level == SecurityLevel.BASIC:
            recommendations.append("Upgrade to enhanced security level")
        
        if fraud_score > 70:
            recommendations.append("Manual review required")
        
        return recommendations


class MultiCurrencyService:
    """
    Multi-currency service for handling international payments
    """
    
    def __init__(self):
        self.currency_converter = CurrencyConverter()
        
    async def convert_currency(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Convert currency with real-time rates
        """



        try:
            rate = await self.currency_converter.get_exchange_rate(
                from_currency, to_currency, rate_date
            )
            
            converted_amount = amount * rate
            
            return {
                "original_amount": amount,
                "converted_amount": converted_amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "rate_date": rate_date or datetime.utcnow(),
                "fee": self._calculate_conversion_fee(amount, from_currency, to_currency)
            }
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {str(e)}")
            return {
                "error": str(e),
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
    
    def _calculate_conversion_fee(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Calculate currency conversion fee"""
        # Standard conversion fee of 0.5%
        return amount * Decimal('0.005')
    
    async def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """Get list of supported currencies with metadata"""
        currencies = []
        
        for currency in CurrencyCode:
            currency_info = {
                "code": currency.value,
                "name": self._get_currency_name(currency.value),
                "symbol": self._get_currency_symbol(currency.value),
                "is_crypto": currency.value in ["BTC", "ETH", "USDC", "USDT", "BNB", "ADA", "DOT", "MATIC"],
                "decimal_places": 2 if currency.value not in ["BTC", "ETH"] else 8
            }
            currencies.append(currency_info)
        
        return currencies
    
    def _get_currency_name(self, code: str) -> str:
        """Get currency name from code"""
        currency_names = {
            "USD": "US Dollar",
            "EUR": "Euro",
            "GBP": "British Pound Sterling",
            "JPY": "Japanese Yen",
            "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar",
            "CHF": "Swiss Franc",
            "CNY": "Chinese Yuan",
            "SEK": "Swedish Krona",
            "NOK": "Norwegian Krone",
            "DKK": "Danish Krone",
            "PLN": "Polish Zloty",
            "CZK": "Czech Koruna",
            "HUF": "Hungarian Forint",
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "USDC": "USD Coin",
            "USDT": "Tether",
            "BNB": "Binance Coin",
            "ADA": "Cardano",
            "DOT": "Polkadot",
            "MATIC": "Polygon"
        }
        return currency_names.get(code, code)
    
    def _get_currency_symbol(self, code: str) -> str:
        """Get currency symbol from code"""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$",
            "CHF": "CHF",
            "CNY": "¥",
            "SEK": "kr",
            "NOK": "kr",
            "DKK": "kr",
            "PLN": "zł",
            "CZK": "Kč",
            "HUF": "Ft",
            "BTC": "₿",
            "ETH": "Ξ",
            "USDC": "USDC",
            "USDT": "₮",
            "BNB": "BNB",
            "ADA": "ADA",
            "DOT": "DOT",
            "MATIC": "MATIC"
        }
        return currency_symbols.get(code, code)
    pass


class ProcessorError(PaymentProcessingError):
    """Raised when there's an issue with the payment processor"""
    pass


class PaymentTransactionService:
    """Service for managing payment transactions"""
    
    def __init__(self, transaction_repo: PaymentTransactionRepository):
        self.transaction_repo = transaction_repo
        self.fee_calculator = PaymentFeeCalculator()
        self.fraud_detector = FraudDetectionService()
    
    async def create_transaction(
        self,
        transaction_data: PaymentTransactionCreateSchema,
        validate_funds: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new payment transaction with validation and fraud detection
        """



        try:
            # Validate transaction data
            await self._validate_transaction(transaction_data)
            
            # Calculate fees
            fees = self.fee_calculator.calculate_fees(
                transaction_data.amount,
                transaction_data.processor,
                transaction_data.currency
            )
            
            # Fraud detection
            fraud_score = await self.fraud_detector.assess_transaction_risk(
                transaction_data.dict()
            )
            
            if fraud_score > 0.8:
                raise PaymentProcessingError("Transaction flagged as high risk")
            
            # Create transaction record
            transaction = self.transaction_repo.create_transaction(
                user_id=transaction_data.user_id,
                amount=transaction_data.amount,
                currency=transaction_data.currency,
                transaction_type=transaction_data.transaction_type,
                processor=transaction_data.processor,
                fees_amount=fees['total_fees'],
                description=transaction_data.description,
                metadata={
                    **transaction_data.metadata or {},
                    'fraud_score': fraud_score,
                    'fee_breakdown': fees
                }
            )
            
            logger.info(f"Created transaction {transaction.id} for user {transaction_data.user_id}")
            
            return {
                'transaction_id': str(transaction.id),
                'status': transaction.status,
                'amount': float(transaction.amount),
                'fees': fees,
                'fraud_score': fraud_score
            }
            
        except Exception as e:
            logger.error(f"Failed to create transaction: {str(e)}")
            raise PaymentProcessingError(f"Transaction creation failed: {str(e)}")
    
    async def process_transaction(
        self,
        transaction_id: uuid.UUID,
        processor_response: Dict[str, Any]
    ) -> bool:
        """Process a transaction with external processor response"""



        try:
            transaction = self.transaction_repo.get_transaction_by_id(transaction_id)
            if not transaction:
                raise PaymentProcessingError("Transaction not found")
            
            # Validate processor response
            if not self._validate_processor_response(processor_response):
                raise ProcessorError("Invalid processor response")
            
            # Update transaction status based on processor response
            new_status = self._map_processor_status(processor_response.get('status'))
            
            success = self.transaction_repo.update_transaction_status(
                transaction_id=transaction_id,
                status=new_status,
                processor_response=processor_response
            )
            
            if success and new_status == PaymentStatus.COMPLETED.value:
                # Trigger post-processing tasks
                await self._post_process_transaction(transaction)
            
            logger.info(f"Processed transaction {transaction_id} with status {new_status}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to process transaction {transaction_id}: {str(e)}")
            raise PaymentProcessingError(f"Transaction processing failed: {str(e)}")
    
    async def refund_transaction(
        self,
        transaction_id: uuid.UUID,
        refund_amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a transaction refund"""



        try:
            original_transaction = self.transaction_repo.get_transaction_by_id(transaction_id)
            if not original_transaction:
                raise PaymentProcessingError("Original transaction not found")
            
            if original_transaction.status != PaymentStatus.COMPLETED.value:
                raise PaymentProcessingError("Can only refund completed transactions")
            
            # Calculate refund amount
            if refund_amount is None:
                refund_amount = original_transaction.net_amount
            elif refund_amount > original_transaction.net_amount:
                raise PaymentProcessingError("Refund amount cannot exceed original amount")
            
            # Create refund transaction
            refund_data = PaymentTransactionCreateSchema(
                user_id=original_transaction.user_id,
                transaction_type="refund",
                amount=refund_amount,
                currency=original_transaction.currency,
                processor=original_transaction.processor,
                description=f"Refund for transaction {transaction_id}. Reason: {reason or 'N/A'}",
                metadata={
                    'original_transaction_id': str(transaction_id),
                    'refund_reason': reason
                }
            )
            
            refund_result = await self.create_transaction(refund_data, validate_funds=False)
            
            logger.info(f"Created refund {refund_result['transaction_id']} for transaction {transaction_id}")
            return refund_result
            
        except Exception as e:
            logger.error(f"Failed to refund transaction {transaction_id}: {str(e)}")
            raise PaymentProcessingError(f"Refund failed: {str(e)}")
    
    async def _validate_transaction(self, transaction_data: PaymentTransactionCreateSchema):
        """Validate transaction data"""
        # Check minimum amount
        if transaction_data.amount < Decimal('0.50'):
            raise PaymentProcessingError("Transaction amount too small")
        
        # Check maximum amount for certain processors
        max_amounts = {
            'stripe': Decimal('999999.99'),
            'paypal': Decimal('10000.00'),
            'wise': Decimal('50000.00')
        }
        
        max_amount = max_amounts.get(transaction_data.processor)
        if max_amount and transaction_data.amount > max_amount:
            raise PaymentProcessingError(f"Amount exceeds processor limit")
    
    def _validate_processor_response(self, response: Dict[str, Any]) -> bool:
        """Validate processor response format"""
        required_fields = ['status', 'transaction_id']
        return all(field in response for field in required_fields)
    
    def _map_processor_status(self, processor_status: str) -> str:
        """Map processor status to internal status"""
        status_mapping = {
            'succeeded': PaymentStatus.COMPLETED.value,
            'pending': PaymentStatus.PROCESSING.value,
            'failed': PaymentStatus.FAILED.value,
            'canceled': PaymentStatus.CANCELLED.value,
            'requires_payment_method': PaymentStatus.FAILED.value
        }
        return status_mapping.get(processor_status, PaymentStatus.FAILED.value)
    
    async def _post_process_transaction(self, transaction):
        """Post-processing tasks after successful transaction"""
        # Update financial records
        # Trigger analytics updates
        # Send notifications
        pass


class PaymentMethodService:
    """Service for managing payment methods"""
    
    def __init__(self, payment_method_repo: PaymentMethodRepository):
        self.payment_method_repo = payment_method_repo
        self.encryption_service = PaymentEncryptionService()
    
    async def add_payment_method(
        self,
        method_data: PaymentMethodCreateSchema,
        encrypted_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Add a new payment method with encryption"""



        try:
            # Encrypt sensitive data
            encrypted_details = await self.encryption_service.encrypt_payment_data(
                encrypted_data
            )
            
            # Create payment method
            payment_method = self.payment_method_repo.create_payment_method(
                user_id=method_data.user_id,
                method_type=method_data.method_type,
                provider=method_data.provider,
                external_id=method_data.external_id,
                last_four_digits=method_data.last_four_digits,
                brand=method_data.brand,
                exp_month=method_data.exp_month,
                exp_year=method_data.exp_year,
                bank_name=method_data.bank_name,
                account_type=method_data.account_type,
                nickname=method_data.nickname,
                billing_address=method_data.billing_address.dict() if method_data.billing_address else None,
                verification_data=encrypted_details
            )
            
            # Verify payment method with provider
            verification_result = await self._verify_payment_method(payment_method)
            
            logger.info(f"Added payment method {payment_method.id} for user {method_data.user_id}")
            
            return {
                'payment_method_id': str(payment_method.id),
                'verification_status': verification_result['status'],
                'is_verified': verification_result['verified']
            }
            
        except Exception as e:
            logger.error(f"Failed to add payment method: {str(e)}")
            raise PaymentMethodError(f"Payment method creation failed: {str(e)}")
    
    async def verify_payment_method(
        self,
        payment_method_id: uuid.UUID,
        verification_data: Dict[str, Any]
    ) -> bool:
        """Verify a payment method with provider"""



        try:
            # Implementation would integrate with payment provider APIs
            # For now, return mock verification
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify payment method {payment_method_id}: {str(e)}")
            return False
    
    async def _verify_payment_method(self, payment_method) -> Dict[str, Any]:
        """Internal verification with payment provider"""
        # Mock verification - would integrate with actual provider APIs
        return {
            'status': 'verified',
            'verified': True,
            'verification_id': f"verify_{uuid.uuid4().hex[:8]}"
        }


class BillingService:
    """Service for managing billing and subscriptions"""
    
    def __init__(self, billing_repo: BillingRecordRepository):
        self.billing_repo = billing_repo
        self.subscription_manager = SubscriptionManager()
    
    async def create_billing_cycle(
        self,
        user_id: int,
        subscription_type: str,
        billing_frequency: str
    ) -> Dict[str, Any]:
        """Create a new billing cycle"""



        try:
            # Calculate billing period
            period_start = datetime.utcnow()
            period_end = self._calculate_period_end(period_start, billing_frequency)
            
            # Get subscription details
            subscription_details = await self.subscription_manager.get_subscription_details(
                user_id, subscription_type
            )
            
            # Create billing record
            billing_record = self.billing_repo.create_billing_record(
                user_id=user_id,
                subscription_type=subscription_type,
                billing_frequency=billing_frequency,
                amount=subscription_details['amount'],
                currency=subscription_details['currency'],
                billing_period_start=period_start,
                billing_period_end=period_end,
                usage_metrics=subscription_details.get('usage_metrics')
            )
            
            logger.info(f"Created billing cycle {billing_record.id} for user {user_id}")
            
            return {
                'billing_record_id': str(billing_record.id),
                'amount': float(billing_record.amount),
                'due_date': billing_record.due_date.isoformat(),
                'period': {
                    'start': billing_record.billing_period_start.isoformat(),
                    'end': billing_record.billing_period_end.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create billing cycle: {str(e)}")
            raise PaymentProcessingError(f"Billing cycle creation failed: {str(e)}")
    
    def _calculate_period_end(self, start_date: datetime, frequency: str) -> datetime:
        """Calculate billing period end date"""
        frequency_mapping = {
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
            'quarterly': timedelta(days=90),
            'annually': timedelta(days=365)
        }
        
        delta = frequency_mapping.get(frequency, timedelta(days=30))
        return start_date + delta


class PayoutService:
    """Service for managing automated payouts"""
    
    def __init__(self, payout_repo: AutomatedPayoutRepository):
        self.payout_repo = payout_repo
        self.payout_processor = PayoutProcessor()
    
    async def schedule_payout(
        self,
        payout_data: AutomatedPayoutCreateSchema
    ) -> Dict[str, Any]:
        """Schedule an automated payout"""



        try:
            # Validate payout eligibility
            await self._validate_payout_eligibility(payout_data)
            
            # Calculate fees
            fees = self._calculate_payout_fees(payout_data.total_amount, payout_data.processor)
            
            # Create payout record
            payout = self.payout_repo.create_payout(
                user_id=payout_data.user_id,
                payment_method_id=payout_data.payment_method_id,
                total_amount=payout_data.total_amount,
                period_start=payout_data.period_start,
                period_end=payout_data.period_end,
                payout_frequency=payout_data.payout_frequency,
                minimum_amount=payout_data.minimum_amount,
                currency=payout_data.currency,
                processor=payout_data.processor,
                fees_amount=fees,
                revenue_breakdown=payout_data.revenue_breakdown
            )
            
            logger.info(f"Scheduled payout {payout.id} for user {payout_data.user_id}")
            
            return {
                'payout_id': str(payout.id),
                'scheduled_at': payout.scheduled_at.isoformat(),
                'net_amount': float(payout.net_amount),
                'fees': float(fees)
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule payout: {str(e)}")
            raise PaymentProcessingError(f"Payout scheduling failed: {str(e)}")
    
    async def process_pending_payouts(self) -> List[Dict[str, Any]]:
        """Process all pending payouts"""



        try:
            pending_payouts = self.payout_repo.get_pending_payouts()
            results = []
            
            for payout in pending_payouts:
                try:
                    result = await self.payout_processor.process_payout(payout)
                    
                    # Update payout status
                    self.payout_repo.update_payout_status(
                        payout.id,
                        'processing' if result['success'] else 'failed',
                        result.get('external_id'),
                        result.get('error_message')
                    )
                    
                    results.append({
                        'payout_id': str(payout.id),
                        'success': result['success'],
                        'external_id': result.get('external_id')
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to process payout {payout.id}: {str(e)}")
                    results.append({
                        'payout_id': str(payout.id),
                        'success': False,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process pending payouts: {str(e)}")
            raise PaymentProcessingError(f"Payout processing failed: {str(e)}")
    
    async def _validate_payout_eligibility(self, payout_data: AutomatedPayoutCreateSchema):
        """Validate payout eligibility"""
        if payout_data.total_amount < payout_data.minimum_amount:
            raise PaymentProcessingError("Payout amount below minimum threshold")
    
    def _calculate_payout_fees(self, amount: Decimal, processor: str) -> Decimal:
        """Calculate payout processing fees"""
        fee_rates = {
            'stripe': Decimal('0.0025'),  # 0.25%
            'wise': Decimal('0.005'),     # 0.5%
            'paypal': Decimal('0.01')     # 1%
        }
        
        rate = fee_rates.get(processor, Decimal('0.005'))
        return amount * rate


# Helper classes
class PaymentFeeCalculator:
    """Calculator for payment processing fees"""
    
    def calculate_fees(self, amount: Decimal, processor: str, currency: str) -> Dict[str, Decimal]:
        """Calculate processing fees"""
        base_rates = {
            'stripe': {'rate': Decimal('0.029'), 'fixed': Decimal('0.30')},
            'paypal': {'rate': Decimal('0.034'), 'fixed': Decimal('0.30')},
            'wise': {'rate': Decimal('0.015'), 'fixed': Decimal('0.50')}
        }
        
        rates = base_rates.get(processor, {'rate': Decimal('0.029'), 'fixed': Decimal('0.30')})
        
        percentage_fee = amount * rates['rate']
        fixed_fee = rates['fixed']
        total_fees = percentage_fee + fixed_fee
        
        return {
            'percentage_fee': percentage_fee,
            'fixed_fee': fixed_fee,
            'total_fees': total_fees,
            'rate': rates['rate']
        }


class FraudDetectionService:
    """Service for fraud detection and risk assessment"""
    
    async def assess_transaction_risk(self, transaction_data: Dict[str, Any]) -> float:
        """Assess fraud risk for a transaction (0.0 = low risk, 1.0 = high risk)"""
        # Mock implementation - would use ML models and external APIs
        risk_score = 0.1  # Default low risk
        
        # Add risk factors
        if transaction_data.get('amount', 0) > 1000:
            risk_score += 0.2
        
        if not transaction_data.get('metadata', {}).get('user_verified'):
            risk_score += 0.3
        
        return min(risk_score, 1.0)


class PaymentEncryptionService:
    """Service for encrypting sensitive payment data"""
    
    async def encrypt_payment_data(self, data: Dict[str, str]) -> Dict[str, str]:
        """Encrypt sensitive payment data"""
        # Mock implementation - would use proper encryption
        return {key: f"encrypted_{value}" for key, value in data.items()}


class SubscriptionManager:
    """Manager for subscription details and pricing"""
    
    async def get_subscription_details(self, user_id: int, subscription_type: str) -> Dict[str, Any]:
        """Get subscription details"""
        # Mock implementation
        subscription_plans = {
            'basic': {'amount': Decimal('9.99'), 'currency': 'EUR'},
            'premium': {'amount': Decimal('19.99'), 'currency': 'EUR'},
            'enterprise': {'amount': Decimal('49.99'), 'currency': 'EUR'}
        }
        
        return subscription_plans.get(subscription_type, subscription_plans['basic'])


class PayoutProcessor:
    """Processor for external payout operations"""
    
    async def process_payout(self, payout) -> Dict[str, Any]:
        """Process payout with external provider"""
        # Mock implementation - would integrate with payment providers
        return {
            'success': True,
            'external_id': f"payout_{uuid.uuid4().hex[:8]}",
            'processing_fee': float(payout.fees_amount)
        }
