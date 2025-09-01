"""Comprehensive Billing Engine
Complete billing and monetization solution with advanced features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import hmac
import hashlib
from collections import defaultdict

from .payment_processor import PaymentProcessor, PaymentTransaction, PaymentProvider, PaymentStatus, PaymentType
from .enhanced_payment_providers import EnhancedMultiProviderPaymentService, ExtendedPaymentProvider

logger = logging.getLogger(__name__)


class BillingCycle(Enum):
    """Billing cycle options for subscriptions"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    WEEKLY = "weekly"
    DAILY = "daily"


class InvoiceStatus(Enum):
    """Invoice status options"""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatus(Enum):
    """Subscription status options"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    PENDING = "pending"
    PAST_DUE = "past_due"


class FraudRiskLevel(Enum):
    """Fraud risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaxRate:
    """Tax rate configuration for different jurisdictions"""
    jurisdiction: str
    rate: Decimal
    type: str  # "VAT", "GST", "SALES_TAX", etc.
    threshold: Optional[Decimal] = None
    applicable_services: List[str] = field(default_factory=list)


@dataclass
class Invoice:
    """Invoice data structure"""
    id: str
    customer_id: str
    subscription_id: Optional[str]
    amount: Decimal
    currency: str
    tax_amount: Decimal
    total_amount: Decimal
    status: InvoiceStatus
    due_date: datetime
    line_items: List[Dict[str, Any]]
    tax_breakdown: Dict[str, Decimal]
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription:
    """Subscription data structure"""
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
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    proration_amount: Decimal = Decimal('0')
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FraudAnalysis:
    """Fraud detection analysis result"""
    transaction_id: str
    risk_level: FraudRiskLevel
    risk_score: float  # 0-100
    flags: List[str]
    recommended_action: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    additional_checks: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueRecognition:
    """Revenue recognition record for accounting compliance"""
    id: str
    transaction_id: str
    subscription_id: Optional[str]
    recognition_date: datetime
    amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    status: str  # "recognized", "deferred", "adjusted"
    accounting_period: str
    notes: str = ""


class ComprehensiveBillingEngine:
    """Advanced billing engine with complete monetization features"""
    
    def __init__(self):
        self.payment_processor = PaymentProcessor()
        self.multi_provider_service = EnhancedMultiProviderPaymentService()
        
        # Storage for billing data
        self.invoices: Dict[str, Invoice] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.tax_rates: Dict[str, List[TaxRate]] = defaultdict(list)
        self.revenue_recognition_records: Dict[str, RevenueRecognition] = {}
        self.fraud_analyses: Dict[str, FraudAnalysis] = {}
        
        # Configuration
        self.provider_priority: List[ExtendedPaymentProvider] = [
            ExtendedPaymentProvider.STRIPE,
            ExtendedPaymentProvider.PAYPAL,
            ExtendedPaymentProvider.WISE
        ]
        self.retry_attempts = 3
        self.dunning_sequence = [1, 3, 7, 14]  # Days after failed payment
        
        # Initialize default tax rates
        self._initialize_tax_rates()
    
    def _initialize_tax_rates(self):
        """Initialize default tax rates for various jurisdictions"""
        # European Union VAT rates
        eu_countries = {
            "DE": Decimal("19.0"),  # Germany
            "FR": Decimal("20.0"),  # France
            "IT": Decimal("22.0"),  # Italy
            "ES": Decimal("21.0"),  # Spain
            "NL": Decimal("21.0"),  # Netherlands
            "BE": Decimal("21.0"),  # Belgium
            "AT": Decimal("20.0"),  # Austria
            "PT": Decimal("23.0"),  # Portugal
            "IE": Decimal("23.0"),  # Ireland
            "FI": Decimal("24.0"),  # Finland
            "SE": Decimal("25.0"),  # Sweden
            "DK": Decimal("25.0"),  # Denmark
        }
        
        for country, rate in eu_countries.items():
            self.tax_rates[country].append(
                TaxRate(
                    jurisdiction=country,
                    rate=rate,
                    type="VAT",
                    applicable_services=["digital_services", "subscriptions"]
                )
            )
        
        # Other jurisdictions
        other_rates = {
            "US": (Decimal("8.5"), "SALES_TAX"),  # Average US sales tax
            "CA": (Decimal("13.0"), "HST"),       # Canada HST
            "GB": (Decimal("20.0"), "VAT"),       # UK VAT
            "AU": (Decimal("10.0"), "GST"),       # Australia GST
            "JP": (Decimal("10.0"), "VAT"),       # Japan consumption tax
        }
        
        for country, (rate, tax_type) in other_rates.items():
            self.tax_rates[country].append(
                TaxRate(
                    jurisdiction=country,
                    rate=rate,
                    type=tax_type,
                    applicable_services=["digital_services", "subscriptions"]
                )
            )
    
    async def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        amount: Decimal,
        currency: str = "EUR",
        trial_days: Optional[int] = None,
        payment_method_id: Optional[str] = None
    ) -> Subscription:
        """Create a new subscription with automatic billing"""
        subscription_id = str(uuid.uuid4())
        
        # Calculate billing periods
        current_period_start = datetime.now()
        
        if billing_cycle == BillingCycle.MONTHLY:
            period_delta = timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            period_delta = timedelta(days=90)
        elif billing_cycle == BillingCycle.SEMI_ANNUAL:
            period_delta = timedelta(days=180)
        elif billing_cycle == BillingCycle.ANNUAL:
            period_delta = timedelta(days=365)
        elif billing_cycle == BillingCycle.WEEKLY:
            period_delta = timedelta(days=7)
        else:  # DAILY
            period_delta = timedelta(days=1)
        
        current_period_end = current_period_start + period_delta
        
        # Handle trial period
        trial_end = None
        if trial_days:
            trial_end = current_period_start + timedelta(days=trial_days)
            next_billing_date = trial_end
        else:
            next_billing_date = current_period_end
        
        subscription = Subscription(
            id=subscription_id,
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=billing_cycle,
            amount=amount,
            currency=currency,
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            next_billing_date=next_billing_date,
            trial_end=trial_end
        )
        
        self.subscriptions[subscription_id] = subscription
        
        # Create initial invoice if not in trial
        if not trial_days:
            await self.generate_invoice(subscription_id)
        
        logger.info(f"Created subscription {subscription_id} for customer {customer_id}")
        return subscription
    
    async def generate_invoice(
        self,
        subscription_id: str,
        custom_amount: Optional[Decimal] = None,
        custom_due_date: Optional[datetime] = None
    ) -> Invoice:
        """Generate an invoice for a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        invoice_id = str(uuid.uuid4())
        amount = custom_amount or subscription.amount
        
        # Calculate tax
        tax_breakdown = await self._calculate_taxes(
            amount, subscription.currency, subscription.customer_id
        )
        tax_amount = sum(tax_breakdown.values())
        total_amount = amount + tax_amount
        
        # Set due date
        due_date = custom_due_date or (datetime.now() + timedelta(days=30))
        
        # Create line items
        line_items = [
            {
                "description": f"Subscription {subscription.plan_id}",
                "quantity": 1,
                "unit_price": float(amount),
                "total": float(amount),
                "period_start": subscription.current_period_start.isoformat(),
                "period_end": subscription.current_period_end.isoformat()
            }
        ]
        
        # Add proration if applicable
        if subscription.proration_amount > 0:
            line_items.append({
                "description": "Proration adjustment",
                "quantity": 1,
                "unit_price": float(subscription.proration_amount),
                "total": float(subscription.proration_amount),
                "type": "proration"
            })
            total_amount += subscription.proration_amount
        
        invoice = Invoice(
            id=invoice_id,
            customer_id=subscription.customer_id,
            subscription_id=subscription_id,
            amount=amount,
            currency=subscription.currency,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=InvoiceStatus.PENDING,
            due_date=due_date,
            line_items=line_items,
            tax_breakdown=tax_breakdown
        )
        
        self.invoices[invoice_id] = invoice
        
        logger.info(f"Generated invoice {invoice_id} for subscription {subscription_id}")
        return invoice
    
    async def process_payment_with_failover(
        self,
        invoice_id: str,
        payment_method_id: Optional[str] = None,
        preferred_provider: Optional[ExtendedPaymentProvider] = None
    ) -> Dict[str, Any]:
        """Process payment with automatic provider failover"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Fraud detection
        fraud_analysis = await self._analyze_fraud_risk(invoice)
        if fraud_analysis.risk_level == FraudRiskLevel.CRITICAL:
            logger.warning(f"Payment blocked due to high fraud risk: {invoice_id}")
            return {
                "success": False,
                "error": "Payment blocked due to security concerns",
                "fraud_analysis": asdict(fraud_analysis)
            }
        
        # Determine provider order
        providers_to_try = self.provider_priority.copy()
        if preferred_provider and preferred_provider in providers_to_try:
            providers_to_try.remove(preferred_provider)
            providers_to_try.insert(0, preferred_provider)
        
        last_error = None
        
        # Try each provider
        for provider in providers_to_try:
            try:
                result = await self.multi_provider_service.process_payment(
                    provider=provider,
                    amount=invoice.total_amount,
                    currency=invoice.currency,
                    creator_id=invoice.customer_id,
                    metadata={
                        "invoice_id": invoice_id,
                        "subscription_id": invoice.subscription_id,
                        "fraud_score": fraud_analysis.risk_score
                    }
                )
                
                if result["success"]:
                    # Update invoice
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.now()
                    invoice.payment_method_id = payment_method_id
                    
                    # Record revenue recognition
                    await self._record_revenue_recognition(invoice)
                    
                    logger.info(f"Payment successful for invoice {invoice_id} via {provider.value}")
                    return {
                        "success": True,
                        "provider_used": provider.value,
                        "transaction_id": result["transaction_id"],
                        "fraud_analysis": asdict(fraud_analysis)
                    }
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Payment failed with {provider.value}: {e}")
                continue
        
        # All providers failed
        logger.error(f"Payment failed for invoice {invoice_id} with all providers")
        await self._initiate_dunning_process(invoice_id)
        
        return {
            "success": False,
            "error": f"Payment failed with all providers. Last error: {last_error}",
            "fraud_analysis": asdict(fraud_analysis)
        }
    
    async def process_refund(
        self,
        invoice_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """Process automated refund with workflow"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        if invoice.status != InvoiceStatus.PAID:
            return {"success": False, "error": "Invoice is not paid"}
        
        refund_amount = amount or invoice.total_amount
        
        # Validate refund amount
        if refund_amount > invoice.total_amount:
            return {"success": False, "error": "Refund amount exceeds invoice total"}
        
        # Process refund (simplified - would integrate with actual payment provider)
        refund_id = str(uuid.uuid4())
        
        # Update invoice status
        if refund_amount == invoice.total_amount:
            invoice.status = InvoiceStatus.REFUNDED
        
        # Record revenue recognition adjustment
        await self._record_revenue_adjustment(invoice_id, -refund_amount, reason)
        
        logger.info(f"Processed refund {refund_id} for invoice {invoice_id}")
        
        return {
            "success": True,
            "refund_id": refund_id,
            "amount": float(refund_amount),
            "status": "processed"
        }
    
    async def calculate_proration(
        self,
        subscription_id: str,
        new_amount: Decimal,
        change_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate proration amount for subscription changes"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        change_date = change_date or datetime.now()
        
        # Calculate remaining days in current period
        total_period_days = (subscription.current_period_end - subscription.current_period_start).days
        remaining_days = (subscription.current_period_end - change_date).days
        
        if remaining_days <= 0:
            return Decimal('0')
        
        # Calculate proration
        daily_old_rate = subscription.amount / total_period_days
        daily_new_rate = new_amount / total_period_days
        
        proration = (daily_new_rate - daily_old_rate) * remaining_days
        
        # Update subscription
        subscription.proration_amount = proration
        subscription.amount = new_amount
        
        logger.info(f"Calculated proration {proration} for subscription {subscription_id}")
        return proration
    
    async def _calculate_taxes(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str
    ) -> Dict[str, Decimal]:
        """Calculate taxes based on customer location and jurisdiction"""
        # Simplified customer location lookup (would integrate with customer database)
        customer_country = await self._get_customer_country(customer_id)
        
        tax_breakdown = {}
        applicable_rates = self.tax_rates.get(customer_country, [])
        
        for tax_rate in applicable_rates:
            if "subscriptions" in tax_rate.applicable_services:
                tax_amount = amount * (tax_rate.rate / Decimal('100'))
                tax_breakdown[f"{tax_rate.type}_{tax_rate.jurisdiction}"] = tax_amount
        
        return tax_breakdown
    
    async def _get_customer_country(self, customer_id: str) -> str:
        """Get customer country for tax calculation (simplified)"""
        # This would integrate with customer database
        # For now, return default
        return "DE"  # Default to Germany
    
    async def _analyze_fraud_risk(self, invoice: Invoice) -> FraudAnalysis:
        """Analyze fraud risk for payment"""
        risk_score = 0.0
        flags = []
        
        # Check amount anomalies
        if invoice.total_amount > Decimal('1000'):
            risk_score += 20
            flags.append("high_amount")
        
        # Check rapid successive payments (simplified)
        recent_invoices = [
            inv for inv in self.invoices.values()
            if inv.customer_id == invoice.customer_id and
            inv.created_at > datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent_invoices) > 3:
            risk_score += 30
            flags.append("rapid_payments")
        
        # Check geographic anomalies (simplified)
        customer_country = await self._get_customer_country(invoice.customer_id)
        if customer_country in ["XX", "Unknown"]:  # High-risk countries
            risk_score += 40
            flags.append("high_risk_geography")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = FraudRiskLevel.CRITICAL
            recommended_action = "block_payment"
        elif risk_score >= 50:
            risk_level = FraudRiskLevel.HIGH
            recommended_action = "manual_review"
        elif risk_score >= 30:
            risk_level = FraudRiskLevel.MEDIUM
            recommended_action = "enhanced_verification"
        else:
            risk_level = FraudRiskLevel.LOW
            recommended_action = "proceed"
        
        analysis = FraudAnalysis(
            transaction_id=invoice.id,
            risk_level=risk_level,
            risk_score=risk_score,
            flags=flags,
            recommended_action=recommended_action
        )
        
        self.fraud_analyses[invoice.id] = analysis
        return analysis
    
    async def _record_revenue_recognition(self, invoice: Invoice):
        """Record revenue recognition for accounting compliance"""
        recognition_id = str(uuid.uuid4())
        
        # For subscriptions, recognize revenue over the service period
        if invoice.subscription_id:
            subscription = self.subscriptions[invoice.subscription_id]
            recognition = RevenueRecognition(
                id=recognition_id,
                transaction_id=invoice.id,
                subscription_id=invoice.subscription_id,
                recognition_date=datetime.now(),
                amount=invoice.amount,
                currency=invoice.currency,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                status="recognized",
                accounting_period=f"{datetime.now().year}-{datetime.now().month:02d}"
            )
        else:
            # One-time payment - recognize immediately
            recognition = RevenueRecognition(
                id=recognition_id,
                transaction_id=invoice.id,
                subscription_id=None,
                recognition_date=datetime.now(),
                amount=invoice.amount,
                currency=invoice.currency,
                period_start=datetime.now(),
                period_end=datetime.now(),
                status="recognized",
                accounting_period=f"{datetime.now().year}-{datetime.now().month:02d}"
            )
        
        self.revenue_recognition_records[recognition_id] = recognition
        logger.info(f"Recorded revenue recognition {recognition_id}")
    
    async def _record_revenue_adjustment(
        self,
        invoice_id: str,
        adjustment_amount: Decimal,
        reason: str
    ):
        """Record revenue recognition adjustment"""
        adjustment_id = str(uuid.uuid4())
        
        recognition = RevenueRecognition(
            id=adjustment_id,
            transaction_id=invoice_id,
            subscription_id=None,
            recognition_date=datetime.now(),
            amount=adjustment_amount,
            currency="EUR",  # Would get from invoice
            period_start=datetime.now(),
            period_end=datetime.now(),
            status="adjusted",
            accounting_period=f"{datetime.now().year}-{datetime.now().month:02d}",
            notes=f"Adjustment: {reason}"
        )
        
        self.revenue_recognition_records[adjustment_id] = recognition
        logger.info(f"Recorded revenue adjustment {adjustment_id}")
    
    async def _initiate_dunning_process(self, invoice_id: str):
        """Initiate dunning management for failed payments"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return
        
        # Update invoice status
        if invoice.due_date < datetime.now():
            invoice.status = InvoiceStatus.OVERDUE
        
        # Schedule dunning emails (simplified)
        for day_offset in self.dunning_sequence:
            scheduled_date = datetime.now() + timedelta(days=day_offset)
            logger.info(f"Scheduled dunning reminder for {invoice_id} on {scheduled_date}")
            # Would integrate with email service
    
    async def get_revenue_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Generate real-time revenue analytics with predictions"""
        # Filter recognized revenue within date range
        relevant_records = [
            record for record in self.revenue_recognition_records.values()
            if start_date <= record.recognition_date <= end_date and
            record.currency == currency and
            record.status == "recognized"
        ]
        
        total_revenue = sum(record.amount for record in relevant_records)
        subscription_revenue = sum(
            record.amount for record in relevant_records
            if record.subscription_id
        )
        one_time_revenue = total_revenue - subscription_revenue
        
        # Simple prediction based on historical data
        days_in_period = (end_date - start_date).days
        daily_average = total_revenue / days_in_period if days_in_period > 0 else 0
        
        # Predict next 30 days
        predicted_monthly = daily_average * 30
        
        analytics = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "currency": currency,
            "total_revenue": float(total_revenue),
            "subscription_revenue": float(subscription_revenue),
            "one_time_revenue": float(one_time_revenue),
            "daily_average": float(daily_average),
            "predicted_next_30_days": float(predicted_monthly),
            "revenue_records_count": len(relevant_records),
            "generated_at": datetime.now().isoformat()
        }
        
        return analytics
    
    async def generate_financial_report(
        self,
        report_type: str = "monthly",
        year: int = None,
        month: int = None
    ) -> Dict[str, Any]:
        """Generate automatic financial reports with audit trail"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        report_id = str(uuid.uuid4())
        
        # Filter data for reporting period
        if report_type == "monthly":
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
        else:  # annual
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
        
        # Collect financial data
        period_invoices = [
            inv for inv in self.invoices.values()
            if start_date <= inv.created_at < end_date
        ]
        
        period_revenue_records = [
            record for record in self.revenue_recognition_records.values()
            if start_date <= record.recognition_date < end_date
        ]
        
        # Calculate metrics
        total_invoiced = sum(inv.total_amount for inv in period_invoices)
        total_paid = sum(
            inv.total_amount for inv in period_invoices
            if inv.status == InvoiceStatus.PAID
        )
        total_recognized_revenue = sum(
            record.amount for record in period_revenue_records
            if record.status == "recognized"
        )
        
        outstanding_amount = sum(
            inv.total_amount for inv in period_invoices
            if inv.status in [InvoiceStatus.PENDING, InvoiceStatus.OVERDUE]
        )
        
        # Generate report
        report = {
            "report_id": report_id,
            "report_type": report_type,
            "period": f"{year}-{month:02d}" if report_type == "monthly" else str(year),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "summary": {
                "total_invoiced": float(total_invoiced),
                "total_paid": float(total_paid),
                "total_recognized_revenue": float(total_recognized_revenue),
                "outstanding_amount": float(outstanding_amount),
                "payment_success_rate": float(total_paid / total_invoiced) if total_invoiced > 0 else 0
            },
            "invoices_count": len(period_invoices),
            "revenue_records_count": len(period_revenue_records),
            "generated_at": datetime.now().isoformat(),
            "generated_by": "automated_billing_engine"
        }
        
        logger.info(f"Generated financial report {report_id} for {report_type} period")
        return report