"""Monetization Events Module

Revenue generation, payment processing, and financial events for the Ainflue platform.
Handles all monetization-related operations including payments, commissions, and payouts.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal

from .base_event import BaseEvent
from .event_priority import EventPriority
from .event_status import EventStatus

logger = logging.getLogger(__name__)


class PaymentMethod(Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    STRIPE = "stripe"
    PLATFORM_CREDITS = "platform_credits"


class RevenueType(Enum):
    """Revenue type classification"""
    SUBSCRIPTION = "subscription"
    COMMISSION = "commission"
    LICENSING = "licensing"
    ADVERTISING = "advertising"
    PREMIUM_FEATURES = "premium_features"
    CONTENT_SALES = "content_sales"
    COLLABORATION_FEES = "collaboration_fees"
    PLATFORM_FEES = "platform_fees"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class RevenueGeneratedEvent(BaseEvent):
    """Event triggered when revenue is generated on the platform"""
    
    def __init__(self,
                 revenue_id -> None: str,
                 user_id -> None: str,
                 content_id -> None: Optional[str],
                 amount -> None: Decimal,
                 currency -> None: str,
                 revenue_type -> None: RevenueType,
                 revenue_source -> None: str,
                 gross_amount -> None: Optional[Decimal] = None,
                 platform_fee -> None: Optional[Decimal] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'revenue_id': revenue_id,
            'user_id': user_id,
            'content_id': content_id,
            'amount': str(amount),
            'currency': currency,
            'revenue_type': revenue_type.value,
            'revenue_source': revenue_source,
            'gross_amount': str(gross_amount) if gross_amount else None,
            'platform_fee': str(platform_fee) if platform_fee else None,
            'revenue_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="monetization.revenue.generated",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class PaymentProcessedEvent(BaseEvent):
    """Event triggered when a payment is processed"""
    
    def __init__(self,
                 payment_id -> None: str,
                 payer_id -> None: str,
                 payee_id -> None: str,
                 amount -> None: Decimal,
                 currency -> None: str,
                 payment_method -> None: PaymentMethod,
                 payment_status -> None: PaymentStatus,
                 transaction_id -> None: Optional[str] = None,
                 gateway_response -> None: Optional[Dict[str, Any]] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'payment_id': payment_id,
            'payer_id': payer_id,
            'payee_id': payee_id,
            'amount': str(amount),
            'currency': currency,
            'payment_method': payment_method.value,
            'payment_status': payment_status.value,
            'transaction_id': transaction_id,
            'gateway_response': gateway_response,
            'processed_timestamp': datetime.utcnow().isoformat()
        }
        
        # Set priority based on payment status
        priority_map = {
            PaymentStatus.FAILED: EventPriority.CRITICAL,
            PaymentStatus.DISPUTED: EventPriority.CRITICAL,
            PaymentStatus.COMPLETED: EventPriority.HIGH,
            PaymentStatus.PROCESSING: EventPriority.MEDIUM
        }
        
        super().__init__(
            event_type="monetization.payment.processed",
            data=data,
            priority=priority_map.get(payment_status, EventPriority.MEDIUM),
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class CommissionCalculatedEvent(BaseEvent):
    """Event triggered when commission is calculated for a transaction"""
    
    def __init__(self,
                 commission_id -> None: str,
                 transaction_id -> None: str,
                 creator_id -> None: str,
                 content_id -> None: Optional[str],
                 gross_revenue -> None: Decimal,
                 commission_rate -> None: float,
                 commission_amount -> None: Decimal,
                 calculation_method -> None: str,
                 tier_level -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'commission_id': commission_id,
            'transaction_id': transaction_id,
            'creator_id': creator_id,
            'content_id': content_id,
            'gross_revenue': str(gross_revenue),
            'commission_rate': commission_rate,
            'commission_amount': str(commission_amount),
            'calculation_method': calculation_method,
            'tier_level': tier_level,
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="monetization.commission.calculated",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class PayoutScheduledEvent(BaseEvent):
    """Event triggered when a payout is scheduled"""
    
    def __init__(self,
                 payout_id -> None: str,
                 recipient_id -> None: str,
                 amount -> None: Decimal,
                 currency -> None: str,
                 payout_method -> None: PaymentMethod,
                 scheduled_date -> None: datetime,
                 included_transactions -> None: List[str],
                 payout_period -> None: Dict[str, str],
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'payout_id': payout_id,
            'recipient_id': recipient_id,
            'amount': str(amount),
            'currency': currency,
            'payout_method': payout_method.value,
            'scheduled_date': scheduled_date.isoformat(),
            'included_transactions': included_transactions,
            'payout_period': payout_period,
            'transaction_count': len(included_transactions),
            'scheduled_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="monetization.payout.scheduled",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.PENDING,
            metadata=metadata or {},
            **kwargs
        )


class SubscriptionEvent(BaseEvent):
    """Event triggered for subscription-related activities"""
    
    def __init__(self,
                 subscription_id -> None: str,
                 user_id -> None: str,
                 plan_id -> None: str,
                 action -> None: str,  # created, updated, cancelled, renewed
                 subscription_status -> None: str,
                 billing_amount -> None: Optional[Decimal] = None,
                 billing_currency -> None: Optional[str] = None,
                 billing_cycle -> None: Optional[str] = None,
                 next_billing_date -> None: Optional[datetime] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'subscription_id': subscription_id,
            'user_id': user_id,
            'plan_id': plan_id,
            'action': action,
            'subscription_status': subscription_status,
            'billing_amount': str(billing_amount) if billing_amount else None,
            'billing_currency': billing_currency,
            'billing_cycle': billing_cycle,
            'next_billing_date': next_billing_date.isoformat() if next_billing_date else None,
            'event_timestamp': datetime.utcnow().isoformat()
        }
        
        # Set priority based on action
        priority_map = {
            'cancelled': EventPriority.HIGH,
            'failed': EventPriority.CRITICAL,
            'created': EventPriority.HIGH,
            'renewed': EventPriority.MEDIUM,
            'updated': EventPriority.LOW
        }
        
        super().__init__(
            event_type=f"monetization.subscription.{action}",
            data=data,
            priority=priority_map.get(action, EventPriority.MEDIUM),
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class RefundProcessedEvent(BaseEvent):
    """Event triggered when a refund is processed"""
    
    def __init__(self,
                 refund_id -> None: str,
                 original_payment_id -> None: str,
                 refund_amount -> None: Decimal,
                 currency -> None: str,
                 refund_reason -> None: str,
                 refund_type -> None: str,  # full, partial
                 requester_id -> None: str,
                 approver_id -> None: Optional[str] = None,
                 gateway_response -> None: Optional[Dict[str, Any]] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'refund_id': refund_id,
            'original_payment_id': original_payment_id,
            'refund_amount': str(refund_amount),
            'currency': currency,
            'refund_reason': refund_reason,
            'refund_type': refund_type,
            'requester_id': requester_id,
            'approver_id': approver_id,
            'gateway_response': gateway_response,
            'refund_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="monetization.refund.processed",
            data=data,
            priority=EventPriority.HIGH,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class FinancialReportGeneratedEvent(BaseEvent):
    """Event triggered when financial reports are generated"""
    
    def __init__(self,
                 report_id -> None: str,
                 report_type -> None: str,
                 report_period -> None: Dict[str, str],
                 user_id -> None: Optional[str] = None,
                 report_data -> None: Optional[Dict[str, Any]] = None,
                 report_location -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'report_id': report_id,
            'report_type': report_type,
            'report_period': report_period,
            'user_id': user_id,
            'report_location': report_location,
            'generation_timestamp': datetime.utcnow().isoformat()
        }
        
        # Include summary data if provided
        if report_data:
            data['report_summary'] = {
                'total_revenue': report_data.get('total_revenue'),
                'transaction_count': report_data.get('transaction_count'),
                'currency': report_data.get('currency')
            }
        
        super().__init__(
            event_type="monetization.report.generated",
            data=data,
            priority=EventPriority.LOW,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class FraudDetectedEvent(BaseEvent):
    """Event triggered when fraudulent activity is detected"""
    
    def __init__(self,
                 detection_id -> None: str,
                 transaction_id -> None: str,
                 user_id -> None: str,
                 fraud_type -> None: str,
                 risk_score -> None: float,
                 detection_method -> None: str,
                 suspicious_patterns -> None: List[str],
                 recommended_action -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'detection_id': detection_id,
            'transaction_id': transaction_id,
            'user_id': user_id,
            'fraud_type': fraud_type,
            'risk_score': risk_score,
            'detection_method': detection_method,
            'suspicious_patterns': suspicious_patterns,
            'recommended_action': recommended_action,
            'detection_timestamp': datetime.utcnow().isoformat()
        }
        
        # Set priority based on risk score
        if risk_score >= 0.8:
            priority = EventPriority.EMERGENCY
        elif risk_score >= 0.6:
            priority = EventPriority.CRITICAL
        else:
            priority = EventPriority.HIGH
        
        super().__init__(
            event_type="monetization.fraud.detected",
            data=data,
            priority=priority,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


class TaxCalculatedEvent(BaseEvent):
    """Event triggered when taxes are calculated for transactions"""
    
    def __init__(self,
                 calculation_id -> None: str,
                 transaction_id -> None: str,
                 tax_jurisdiction -> None: str,
                 gross_amount -> None: Decimal,
                 tax_rate -> None: float,
                 tax_amount -> None: Decimal,
                 tax_type -> None: str,
                 calculation_method -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        data = {
            'calculation_id': calculation_id,
            'transaction_id': transaction_id,
            'tax_jurisdiction': tax_jurisdiction,
            'gross_amount': str(gross_amount),
            'tax_rate': tax_rate,
            'tax_amount': str(tax_amount),
            'tax_type': tax_type,
            'calculation_method': calculation_method,
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
        
        super().__init__(
            event_type="monetization.tax.calculated",
            data=data,
            priority=EventPriority.MEDIUM,
            status=EventStatus.COMPLETED,
            metadata=metadata or {},
            **kwargs
        )


# Export all monetization event classes
__all__ = [
    'PaymentMethod',
    'RevenueType',
    'PaymentStatus',
    'RevenueGeneratedEvent',
    'PaymentProcessedEvent',
    'CommissionCalculatedEvent',
    'PayoutScheduledEvent',
    'SubscriptionEvent',
    'RefundProcessedEvent',
    'FinancialReportGeneratedEvent',
    'FraudDetectedEvent',
    'TaxCalculatedEvent'
]

logger.info("Monetization events module initialized successfully")