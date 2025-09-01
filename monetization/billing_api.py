"""Billing API Endpoints
FastAPI endpoints for comprehensive billing and monetization functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .billing_engine import (
    ComprehensiveBillingEngine, 
    BillingCycle, 
    InvoiceStatus, 
    SubscriptionStatus
)
from .subscription_manager import (
    AdvancedSubscriptionManager, 
    SubscriptionAction, 
    ProrationMethod
)
from .fraud_detector import (
    AdvancedFraudDetector, 
    TransactionContext, 
    FraudRiskLevel
)

logger = logging.getLogger(__name__)

# Initialize services
billing_engine = ComprehensiveBillingEngine()
subscription_manager = AdvancedSubscriptionManager(billing_engine)
fraud_detector = AdvancedFraudDetector()

# Create router
billing_router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


# Request/Response Models
class CreateSubscriptionRequest(BaseModel):
    customer_id: str
    plan_id: str
    billing_cycle: BillingCycle
    custom_pricing: Optional[Decimal] = None
    coupon_code: Optional[str] = None
    payment_method_id: Optional[str] = None
    trial_days: Optional[int] = None


class SubscriptionResponse(BaseModel):
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    amount: Decimal
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    trial_end: Optional[datetime] = None
    created_at: datetime


class ModifySubscriptionRequest(BaseModel):
    new_plan_id: str
    proration_method: ProrationMethod = ProrationMethod.IMMEDIATE
    effective_date: Optional[datetime] = None
    reason: str = "customer_request"


class ProcessPaymentRequest(BaseModel):
    invoice_id: str
    payment_method_id: Optional[str] = None
    preferred_provider: Optional[str] = None
    fraud_context: Optional[Dict[str, Any]] = None


class RefundRequest(BaseModel):
    invoice_id: str
    amount: Optional[Decimal] = None
    reason: str = "requested_by_customer"


class FraudAnalysisRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: Decimal
    currency: str
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    billing_country: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Subscription Endpoints
@billing_router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a new subscription"""
    try:
        subscription = await subscription_manager.create_subscription_with_plan(
            customer_id=request.customer_id,
            plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
            custom_pricing=request.custom_pricing,
            coupon_code=request.coupon_code,
            payment_method_id=request.payment_method_id
        )
        
        return SubscriptionResponse(
            id=subscription.id,
            customer_id=subscription.customer_id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            amount=subscription.amount,
            currency=subscription.currency,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            next_billing_date=subscription.next_billing_date,
            trial_end=subscription.trial_end,
            created_at=subscription.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: str):
    """Get subscription details"""
    subscription = billing_engine.subscriptions.get(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return SubscriptionResponse(
        id=subscription.id,
        customer_id=subscription.customer_id,
        plan_id=subscription.plan_id,
        status=subscription.status,
        billing_cycle=subscription.billing_cycle,
        amount=subscription.amount,
        currency=subscription.currency,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        next_billing_date=subscription.next_billing_date,
        trial_end=subscription.trial_end,
        created_at=subscription.created_at
    )


@billing_router.post("/subscriptions/{subscription_id}/upgrade")
async def upgrade_subscription(subscription_id: str, request: ModifySubscriptionRequest):
    """Upgrade subscription to higher tier"""
    try:
        result = await subscription_manager.upgrade_subscription(
            subscription_id=subscription_id,
            new_plan_id=request.new_plan_id,
            proration_method=request.proration_method,
            effective_date=request.effective_date
        )
        return result
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.post("/subscriptions/{subscription_id}/downgrade")
async def downgrade_subscription(subscription_id: str, request: ModifySubscriptionRequest):
    """Downgrade subscription to lower tier"""
    try:
        result = await subscription_manager.downgrade_subscription(
            subscription_id=subscription_id,
            new_plan_id=request.new_plan_id,
            proration_method=request.proration_method
        )
        return result
        
    except Exception as e:
        logger.error(f"Error downgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.post("/subscriptions/{subscription_id}/pause")
async def pause_subscription(
    subscription_id: str, 
    pause_until: Optional[datetime] = None,
    reason: str = "customer_request"
):
    """Pause subscription billing"""
    try:
        result = await subscription_manager.pause_subscription(
            subscription_id=subscription_id,
            pause_until=pause_until,
            reason=reason
        )
        return result
        
    except Exception as e:
        logger.error(f"Error pausing subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    cancel_immediately: bool = False,
    reason: str = "customer_request"
):
    """Cancel subscription"""
    try:
        result = await subscription_manager.cancel_subscription(
            subscription_id=subscription_id,
            cancel_immediately=cancel_immediately,
            reason=reason
        )
        return result
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Invoice Endpoints
@billing_router.post("/invoices/generate")
async def generate_invoice(
    subscription_id: str,
    custom_amount: Optional[Decimal] = None,
    custom_due_date: Optional[datetime] = None
):
    """Generate invoice for subscription"""
    try:
        invoice = await billing_engine.generate_invoice(
            subscription_id=subscription_id,
            custom_amount=custom_amount,
            custom_due_date=custom_due_date
        )
        
        return {
            "invoice_id": invoice.id,
            "customer_id": invoice.customer_id,
            "subscription_id": invoice.subscription_id,
            "amount": invoice.amount,
            "tax_amount": invoice.tax_amount,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "status": invoice.status.value,
            "due_date": invoice.due_date,
            "line_items": invoice.line_items,
            "tax_breakdown": {k: float(v) for k, v in invoice.tax_breakdown.items()},
            "created_at": invoice.created_at
        }
        
    except Exception as e:
        logger.error(f"Error generating invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get invoice details"""
    invoice = billing_engine.invoices.get(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return {
        "invoice_id": invoice.id,
        "customer_id": invoice.customer_id,
        "subscription_id": invoice.subscription_id,
        "amount": invoice.amount,
        "tax_amount": invoice.tax_amount,
        "total_amount": invoice.total_amount,
        "currency": invoice.currency,
        "status": invoice.status.value,
        "due_date": invoice.due_date,
        "line_items": invoice.line_items,
        "tax_breakdown": {k: float(v) for k, v in invoice.tax_breakdown.items()},
        "created_at": invoice.created_at,
        "paid_at": invoice.paid_at
    }


# Payment Endpoints
@billing_router.post("/payments/process")
async def process_payment(request: ProcessPaymentRequest):
    """Process payment with fraud detection and failover"""
    try:
        # Perform fraud analysis if context provided
        if request.fraud_context:
            context = TransactionContext(
                transaction_id=request.fraud_context.get("transaction_id", request.invoice_id),
                customer_id=request.fraud_context["customer_id"],
                amount=Decimal(str(request.fraud_context["amount"])),
                currency=request.fraud_context["currency"],
                timestamp=datetime.now(),
                ip_address=request.fraud_context.get("ip_address"),
                device_fingerprint=request.fraud_context.get("device_fingerprint"),
                billing_country=request.fraud_context.get("billing_country"),
                email=request.fraud_context.get("email")
            )
            
            fraud_analysis = await fraud_detector.analyze_transaction(context)
            
            if fraud_analysis.risk_level == FraudRiskLevel.CRITICAL:
                return {
                    "success": False,
                    "error": "Payment blocked due to high fraud risk",
                    "fraud_analysis": {
                        "risk_level": fraud_analysis.risk_level.value,
                        "risk_score": fraud_analysis.risk_score,
                        "flags": fraud_analysis.flags,
                        "recommended_action": fraud_analysis.recommended_action
                    }
                }
        
        # Process payment
        result = await billing_engine.process_payment_with_failover(
            invoice_id=request.invoice_id,
            payment_method_id=request.payment_method_id,
            preferred_provider=None  # Would map from string to enum
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.post("/payments/refund")
async def process_refund(request: RefundRequest):
    """Process payment refund"""
    try:
        result = await billing_engine.process_refund(
            invoice_id=request.invoice_id,
            amount=request.amount,
            reason=request.reason
        )
        return result
        
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Fraud Detection Endpoints
@billing_router.post("/fraud/analyze")
async def analyze_fraud_risk(request: FraudAnalysisRequest):
    """Analyze fraud risk for a transaction"""
    try:
        context = TransactionContext(
            transaction_id=request.transaction_id,
            customer_id=request.customer_id,
            amount=request.amount,
            currency=request.currency,
            timestamp=datetime.now(),
            ip_address=request.ip_address,
            device_fingerprint=request.device_fingerprint,
            billing_country=request.billing_country,
            email=request.email,
            metadata=request.metadata or {}
        )
        
        analysis = await fraud_detector.analyze_transaction(context)
        
        return {
            "transaction_id": analysis.transaction_id,
            "risk_level": analysis.risk_level.value,
            "risk_score": analysis.risk_score,
            "flags": analysis.flags,
            "recommended_action": analysis.recommended_action,
            "analysis_timestamp": analysis.analysis_timestamp,
            "additional_checks": analysis.additional_checks
        }
        
    except Exception as e:
        logger.error(f"Error analyzing fraud risk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@billing_router.get("/fraud/statistics")
async def get_fraud_statistics(days: int = 30):
    """Get fraud detection statistics"""
    try:
        stats = await fraud_detector.get_fraud_statistics(days=days)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting fraud statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Analytics Endpoints
@billing_router.get("/analytics/revenue")
async def get_revenue_analytics(
    start_date: datetime,
    end_date: datetime,
    currency: str = "EUR"
):
    """Get revenue analytics"""
    try:
        analytics = await billing_engine.get_revenue_analytics(
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@billing_router.get("/analytics/subscriptions")
async def get_subscription_analytics(
    customer_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get subscription analytics"""
    try:
        analytics = await subscription_manager.get_subscription_analytics(
            customer_id=customer_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        )
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting subscription analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Reporting Endpoints
@billing_router.get("/reports/financial")
async def generate_financial_report(
    report_type: str = "monthly",
    year: Optional[int] = None,
    month: Optional[int] = None
):
    """Generate financial reports"""
    try:
        report = await billing_engine.generate_financial_report(
            report_type=report_type,
            year=year,
            month=month
        )
        return report
        
    except Exception as e:
        logger.error(f"Error generating financial report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Plans Endpoints
@billing_router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    plans = []
    for plan in subscription_manager.plans.values():
        plans.append({
            "id": plan.id,
            "name": plan.name,
            "description": plan.description,
            "base_price": float(plan.base_price),
            "currency": plan.currency,
            "billing_cycles": [cycle.value for cycle in plan.billing_cycles],
            "features": plan.features,
            "trial_days": plan.trial_days,
            "setup_fee": float(plan.setup_fee),
            "usage_limits": plan.usage_limits
        })
    
    return {"plans": plans}


@billing_router.get("/plans/{plan_id}")
async def get_subscription_plan(plan_id: str):
    """Get specific subscription plan details"""
    plan = subscription_manager.plans.get(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "base_price": float(plan.base_price),
        "currency": plan.currency,
        "billing_cycles": [cycle.value for cycle in plan.billing_cycles],
        "features": plan.features,
        "trial_days": plan.trial_days,
        "setup_fee": float(plan.setup_fee),
        "usage_limits": plan.usage_limits,
        "metadata": plan.metadata
    }


# Health Check
@billing_router.get("/health")
async def billing_health_check():
    """Billing system health check"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "services": {
                "billing_engine": "active",
                "subscription_manager": "active",
                "fraud_detector": "active"
            },
            "statistics": {
                "total_subscriptions": len(billing_engine.subscriptions),
                "total_invoices": len(billing_engine.invoices),
                "fraud_rules_enabled": sum(1 for rule in fraud_detector.rules.values() if rule.enabled)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing system unhealthy"
        )