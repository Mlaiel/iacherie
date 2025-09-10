#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Refund Configuration Module
====================================

Enterprise-grade refund configuration for the Ainflue platform.
Comprehensive refund management with automated processing, compliance tracking,
multi-reason support, and analytics capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal

class RefundType(str, Enum):
    """Types of refunds"""
    FULL_REFUND = "full_refund"             # Full refund of payment
    PARTIAL_REFUND = "partial_refund"       # Partial refund
    CREDIT_REFUND = "credit_refund"         # Refund as credit
    CHARGEBACK = "chargeback"               # Bank chargeback
    REVERSAL = "reversal"                   # Payment reversal
    CANCELLATION = "cancellation"           # Service cancellation refund
    SUBSCRIPTION = "subscription"           # Subscription refund
    PRORATION = "proration"                 # Prorated refund
    UPGRADE_REFUND = "upgrade_refund"       # Upgrade difference refund

class RefundStatus(str, Enum):
    """Refund status"""
    PENDING = "pending"                     # Pending approval
    APPROVED = "approved"                   # Approved for processing
    PROCESSING = "processing"               # Being processed
    COMPLETED = "completed"                 # Successfully completed
    FAILED = "failed"                       # Failed to process
    CANCELLED = "cancelled"                 # Cancelled by user/admin
    DISPUTED = "disputed"                   # Under dispute
    REVERSED = "reversed"                   # Reversed refund
    EXPIRED = "expired"                     # Refund request expired

class RefundReason(str, Enum):
    """Refund reason codes"""
    CUSTOMER_REQUEST = "customer_request"           # Customer requested
    DUPLICATE_PAYMENT = "duplicate_payment"         # Duplicate payment
    DEFECTIVE_PRODUCT = "defective_product"         # Product defect
    NOT_AS_DESCRIBED = "not_as_described"          # Not as described
    BILLING_ERROR = "billing_error"                # Billing error
    UNAUTHORIZED_CHARGE = "unauthorized_charge"     # Unauthorized charge
    SERVICE_UNAVAILABLE = "service_unavailable"     # Service not available
    TECHNICAL_ERROR = "technical_error"             # Technical error
    FRAUDULENT_ACTIVITY = "fraudulent_activity"     # Fraud detected
    POLICY_VIOLATION = "policy_violation"           # Policy violation
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"  # Subscription cancelled
    CONTENT_REMOVED = "content_removed"             # Content removed
    QUALITY_ISSUE = "quality_issue"                 # Quality issue

class RefundMethod(str, Enum):
    """Refund methods"""
    ORIGINAL_PAYMENT_METHOD = "original_payment_method"  # Original payment method
    BANK_TRANSFER = "bank_transfer"                      # Bank transfer
    CREDIT_CARD = "credit_card"                         # Credit card
    PAYPAL = "paypal"                                   # PayPal
    WALLET_CREDIT = "wallet_credit"                     # Wallet credit
    STORE_CREDIT = "store_credit"                       # Store credit
    CRYPTO = "crypto"                                   # Cryptocurrency
    CHECK = "check"                                     # Physical check
    GIFT_CARD = "gift_card"                            # Gift card

@dataclass
class RefundEligibility:
    """Refund eligibility criteria"""
    is_eligible: bool = False
    eligibility_window_days: int = 30
    reasons: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def check_eligibility(self, payment_date: datetime, reason: RefundReason) -> Dict[str, Any]:
        """Check refund eligibility"""
        result = {
            "is_eligible": False,
            "reasons": [],
            "restrictions": []
        }
        
        # Check time window
        days_since_payment = (datetime.now() - payment_date).days
        if days_since_payment > self.eligibility_window_days:
            result["restrictions"].append(f"Refund window expired (>{self.eligibility_window_days} days)")
            return result
        
        # Check reason eligibility
        if reason.value not in self.reasons and self.reasons:
            result["restrictions"].append(f"Reason '{reason.value}' not eligible for refund")
            return result
        
        result["is_eligible"] = True
        result["reasons"].append("Within refund window")
        result["reasons"].append("Valid refund reason")
        
        return result

@dataclass
class RefundRecord:
    """Refund record"""
    refund_id: str
    payment_id: str
    transaction_id: str
    customer_id: str
    refund_type: RefundType
    refund_status: RefundStatus
    refund_reason: RefundReason
    refund_method: RefundMethod
    original_amount: Decimal
    refund_amount: Decimal
    currency: str
    initiated_date: datetime
    completed_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    customer_reason: Optional[str] = None
    internal_reference: Optional[str] = None
    external_reference: Optional[str] = None
    processing_fee: Decimal = Decimal('0')
    net_refund_amount: Decimal = Decimal('0')
    
    def calculate_net_refund(self) -> Decimal:
        """Calculate net refund amount after fees"""
        self.net_refund_amount = self.refund_amount - self.processing_fee
        return self.net_refund_amount
    
    def get_processing_time(self) -> Optional[int]:
        """Get processing time in hours"""
        if self.completed_date and self.initiated_date:
            return int((self.completed_date - self.initiated_date).total_seconds() / 3600)
        return None
    
    def is_expired(self, expiry_days: int = 30) -> bool:
        """Check if refund request is expired"""
        if self.refund_status in [RefundStatus.COMPLETED, RefundStatus.CANCELLED, RefundStatus.FAILED]:
            return False
        
        expiry_date = self.initiated_date + timedelta(days=expiry_days)
        return datetime.now() > expiry_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert refund to dictionary"""
        return {
            "refund_id": self.refund_id,
            "payment_id": self.payment_id,
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "refund_type": self.refund_type.value,
            "refund_status": self.refund_status.value,
            "refund_reason": self.refund_reason.value,
            "refund_method": self.refund_method.value,
            "original_amount": float(self.original_amount),
            "refund_amount": float(self.refund_amount),
            "currency": self.currency,
            "initiated_date": self.initiated_date.isoformat(),
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "approved_date": self.approved_date.isoformat() if self.approved_date else None,
            "created_date": self.created_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "notes": self.notes,
            "admin_notes": self.admin_notes,
            "customer_reason": self.customer_reason,
            "internal_reference": self.internal_reference,
            "external_reference": self.external_reference,
            "processing_fee": float(self.processing_fee),
            "net_refund_amount": float(self.net_refund_amount),
            "processing_time_hours": self.get_processing_time(),
            "is_expired": self.is_expired()
        }

@dataclass
class RefundPolicyConfig:
    """Refund policy configuration"""
    enabled: bool = True
    
    # Policy settings
    policy_settings: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "default_window_days": 30,
        "partial_refunds_allowed": True,
        "automatic_refunds_enabled": True,
        "admin_approval_required": False,
        "customer_initiated_refunds": True,
        "refund_reason_required": True,
        "supporting_documentation": False
    })
    
    # Eligibility rules
    eligibility_rules: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "time_based_eligibility": True,
        "reason_based_eligibility": True,
        "amount_based_eligibility": True,
        "customer_history_check": True,
        "fraud_check": True,
        "product_specific_rules": True,
        "subscription_rules": True
    })
    
    # Approval workflow
    approval_workflow: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automatic_approval_threshold": 100.0,  # EUR
        "manager_approval_threshold": 1000.0,   # EUR
        "director_approval_threshold": 5000.0,  # EUR
        "escalation_enabled": True,
        "approval_timeout_hours": 48,
        "auto_approve_trusted_customers": True
    })
    
    # Processing rules
    processing_rules: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "same_day_processing": True,
        "business_days_only": False,
        "processing_cutoff_time": "16:00",
        "batch_processing": True,
        "priority_processing": True,
        "weekend_processing": False
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get refund policy configuration"""
        return {
            "enabled": self.enabled,
            "policy_settings": self.policy_settings,
            "eligibility_rules": self.eligibility_rules,
            "approval_workflow": self.approval_workflow,
            "processing_rules": self.processing_rules
        }

@dataclass
class RefundProcessingConfig:
    """Refund processing configuration"""
    enabled: bool = True
    
    # Processing engine
    processing_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automatic_processing": True,
        "batch_processing": True,
        "real_time_processing": True,
        "retry_failed_refunds": True,
        "max_retry_attempts": 3,
        "retry_delay_minutes": 30,
        "processing_timeout_minutes": 60
    })
    
    # Payment gateway integration
    gateway_integration: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multi_gateway_support": True,
        "gateway_failover": True,
        "gateway_routing": True,
        "gateway_fees_handling": True,
        "gateway_response_handling": True,
        "webhook_processing": True
    })
    
    # Anti-fraud
    anti_fraud: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "fraud_detection": True,
        "velocity_checks": True,
        "pattern_analysis": True,
        "machine_learning_models": True,
        "risk_scoring": True,
        "blacklist_checking": True,
        "suspicious_activity_alerts": True
    })
    
    # Compliance
    compliance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "pci_compliance": True,
        "gdpr_compliance": True,
        "audit_trail": True,
        "transaction_logging": True,
        "data_retention": True,
        "regulatory_reporting": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get refund processing configuration"""
        return {
            "enabled": self.enabled,
            "processing_engine": self.processing_engine,
            "gateway_integration": self.gateway_integration,
            "anti_fraud": self.anti_fraud,
            "compliance": self.compliance
        }

@dataclass
class RefundNotificationConfig:
    """Refund notification configuration"""
    enabled: bool = True
    
    # Customer notifications
    customer_notifications: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "refund_requested": True,
        "refund_approved": True,
        "refund_processing": True,
        "refund_completed": True,
        "refund_failed": True,
        "refund_cancelled": True,
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "in_app_notifications": True
    })
    
    # Admin notifications
    admin_notifications: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "new_refund_requests": True,
        "approval_required": True,
        "high_value_refunds": True,
        "failed_refunds": True,
        "suspicious_refunds": True,
        "bulk_refund_requests": True,
        "daily_summary": True,
        "slack_integration": True,
        "email_alerts": True
    })
    
    # Notification templates
    notification_templates: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "customizable_templates": True,
        "multi_language_support": True,
        "dynamic_content": True,
        "brand_customization": True,
        "template_versioning": True,
        "a_b_testing": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get refund notification configuration"""
        return {
            "enabled": self.enabled,
            "customer_notifications": self.customer_notifications,
            "admin_notifications": self.admin_notifications,
            "notification_templates": self.notification_templates
        }

@dataclass
class RefundAnalyticsConfig:
    """Refund analytics configuration"""
    enabled: bool = True
    
    # Analytics engine
    analytics_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "real_time_analytics": True,
        "batch_analytics": True,
        "predictive_analytics": True,
        "trend_analysis": True,
        "anomaly_detection": True,
        "machine_learning": True,
        "data_visualization": True
    })
    
    # Metrics tracking
    metrics_tracking: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "refund_rate": True,
        "refund_volume": True,
        "processing_time": True,
        "success_rate": True,
        "customer_satisfaction": True,
        "cost_analysis": True,
        "fraud_detection": True,
        "reason_analysis": True
    })
    
    # Reporting
    reporting: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "automated_reports": True,
        "custom_reports": True,
        "scheduled_reports": True,
        "real_time_dashboards": True,
        "executive_summaries": True,
        "compliance_reports": True,
        "financial_reports": True
    })
    
    # Data export
    data_export: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "csv_export": True,
        "json_export": True,
        "xlsx_export": True,
        "api_access": True,
        "scheduled_exports": True,
        "filtered_exports": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get refund analytics configuration"""
        return {
            "enabled": self.enabled,
            "analytics_engine": self.analytics_engine,
            "metrics_tracking": self.metrics_tracking,
            "reporting": self.reporting,
            "data_export": self.data_export
        }

class RefundConfiguration:
    """Main refund configuration manager"""
    
    def __init__(self):
        """Initialize refund configuration"""
        # Refund configuration components
        self.refund_policy = RefundPolicyConfig()
        self.refund_processing = RefundProcessingConfig()
        self.refund_notification = RefundNotificationConfig()
        self.refund_analytics = RefundAnalyticsConfig()
        
        # Refund storage
        self.refund_records: List[RefundRecord] = []
        
        # Global refund settings
        self.refund_system_enabled = True
        self.automatic_processing = True
        self.fraud_detection_enabled = True
        self.compliance_mode = True
        
        # Processing limits
        self.daily_refund_limit = Decimal('50000.0')  # EUR
        self.single_refund_limit = Decimal('10000.0')  # EUR
        self.customer_daily_limit = Decimal('5000.0')  # EUR
        
        # Processing fees
        self.processing_fees = {
            "credit_card": Decimal('2.50'),     # EUR
            "bank_transfer": Decimal('1.00'),   # EUR
            "paypal": Decimal('3.00'),          # EUR
            "wallet": Decimal('0.00'),          # EUR
            "crypto": Decimal('5.00')           # EUR
        }
        
        # SLA settings
        self.sla_hours = 24
        self.priority_sla_hours = 2
        self.weekend_processing = False
        
        # Integration settings
        self.payment_gateway_integration = True
        self.accounting_integration = True
        self.crm_integration = True
        self.fraud_service_integration = True
        
        # Security settings
        self.encryption_enabled = True
        self.audit_logging = True
        self.two_factor_approval = True
        self.ip_restriction = True
    
    def initiate_refund(self, refund_data: Dict[str, Any]) -> RefundRecord:
        """Initiate new refund"""
        
        # Create refund record
        refund = RefundRecord(
            refund_id=f"ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            payment_id=refund_data.get("payment_id", ""),
            transaction_id=refund_data.get("transaction_id", ""),
            customer_id=refund_data.get("customer_id", ""),
            refund_type=RefundType(refund_data.get("refund_type", "full_refund")),
            refund_status=RefundStatus.PENDING,
            refund_reason=RefundReason(refund_data.get("refund_reason", "customer_request")),
            refund_method=RefundMethod(refund_data.get("refund_method", "original_payment_method")),
            original_amount=Decimal(str(refund_data.get("original_amount", "0"))),
            refund_amount=Decimal(str(refund_data.get("refund_amount", "0"))),
            currency=refund_data.get("currency", "EUR"),
            initiated_date=datetime.now(),
            notes=refund_data.get("notes"),
            customer_reason=refund_data.get("customer_reason"),
            processing_fee=self.processing_fees.get(refund_data.get("refund_method", "credit_card"), Decimal('2.50'))
        )
        
        # Calculate net refund amount
        refund.calculate_net_refund()
        
        # Store refund
        self.refund_records.append(refund)
        
        return refund
    
    async def process_refund(self, refund_id: str) -> Dict[str, Any]:
        """Process refund"""
        
        refund = self._get_refund_by_id(refund_id)
        if not refund:
            return {"error": f"Refund {refund_id} not found"}
        
        processing_result = {
            "refund_id": refund_id,
            "processing_started": datetime.now().isoformat(),
            "success": False,
            "transaction_id": None,
            "gateway_response": None
        }
        
        try:
            # Check if refund is eligible for processing
            if refund.refund_status != RefundStatus.APPROVED:
                processing_result["error"] = f"Refund not approved for processing: {refund.refund_status.value}"
                return processing_result
            
            # Update status to processing
            refund.refund_status = RefundStatus.PROCESSING
            refund.last_updated = datetime.now()
            
            # Simulate payment gateway processing
            gateway_response = await self._process_gateway_refund(refund)
            
            if gateway_response.get("success"):
                refund.refund_status = RefundStatus.COMPLETED
                refund.completed_date = datetime.now()
                refund.external_reference = gateway_response.get("transaction_id")
                
                processing_result.update({
                    "success": True,
                    "transaction_id": gateway_response.get("transaction_id"),
                    "gateway_response": gateway_response,
                    "completed_date": refund.completed_date.isoformat()
                })
            else:
                refund.refund_status = RefundStatus.FAILED
                processing_result["error"] = gateway_response.get("error", "Unknown gateway error")
            
            refund.last_updated = datetime.now()
            
        except Exception as e:
            refund.refund_status = RefundStatus.FAILED
            refund.last_updated = datetime.now()
            processing_result["error"] = str(e)
        
        return processing_result
    
    async def approve_refund(self, refund_id: str, approver_id: str, notes: str = None) -> Dict[str, Any]:
        """Approve refund"""
        
        refund = self._get_refund_by_id(refund_id)
        if not refund:
            return {"error": f"Refund {refund_id} not found"}
        
        approval_result = {
            "refund_id": refund_id,
            "approved_by": approver_id,
            "approval_date": datetime.now().isoformat(),
            "success": False
        }
        
        if refund.refund_status != RefundStatus.PENDING:
            approval_result["error"] = f"Refund not in pending status: {refund.refund_status.value}"
            return approval_result
        
        # Update refund status
        refund.refund_status = RefundStatus.APPROVED
        refund.approved_date = datetime.now()
        refund.admin_notes = notes
        refund.last_updated = datetime.now()
        
        approval_result["success"] = True
        
        # Auto-process if enabled
        if self.automatic_processing:
            processing_result = await self.process_refund(refund_id)
            approval_result["auto_processing"] = processing_result
        
        return approval_result
    
    def cancel_refund(self, refund_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel refund"""
        
        refund = self._get_refund_by_id(refund_id)
        if not refund:
            return {"error": f"Refund {refund_id} not found"}
        
        cancellation_result = {
            "refund_id": refund_id,
            "cancellation_date": datetime.now().isoformat(),
            "reason": reason,
            "success": False
        }
        
        if refund.refund_status in [RefundStatus.COMPLETED, RefundStatus.PROCESSING]:
            cancellation_result["error"] = f"Cannot cancel refund in status: {refund.refund_status.value}"
            return cancellation_result
        
        # Update refund status
        refund.refund_status = RefundStatus.CANCELLED
        refund.notes = f"Cancelled: {reason}" if reason else "Cancelled"
        refund.last_updated = datetime.now()
        
        cancellation_result["success"] = True
        
        return cancellation_result
    
    def get_refund_statistics(self) -> Dict[str, Any]:
        """Get refund statistics"""
        
        stats = {
            "total_refunds": len(self.refund_records),
            "refunds_by_status": {},
            "refunds_by_type": {},
            "refunds_by_reason": {},
            "total_refund_amount": 0.0,
            "average_refund_amount": 0.0,
            "average_processing_time": 0.0,
            "success_rate": 0.0,
            "period_stats": {}
        }
        
        if not self.refund_records:
            return stats
        
        total_amount = Decimal('0')
        total_processing_times = []
        completed_refunds = 0
        
        for refund in self.refund_records:
            # Count by status
            status = refund.refund_status.value
            stats["refunds_by_status"][status] = stats["refunds_by_status"].get(status, 0) + 1
            
            # Count by type
            refund_type = refund.refund_type.value
            stats["refunds_by_type"][refund_type] = stats["refunds_by_type"].get(refund_type, 0) + 1
            
            # Count by reason
            reason = refund.refund_reason.value
            stats["refunds_by_reason"][reason] = stats["refunds_by_reason"].get(reason, 0) + 1
            
            # Calculate amounts
            total_amount += refund.refund_amount
            
            # Processing time
            processing_time = refund.get_processing_time()
            if processing_time is not None:
                total_processing_times.append(processing_time)
            
            if refund.refund_status == RefundStatus.COMPLETED:
                completed_refunds += 1
        
        stats["total_refund_amount"] = float(total_amount)
        stats["average_refund_amount"] = float(total_amount / len(self.refund_records))
        
        if total_processing_times:
            stats["average_processing_time"] = sum(total_processing_times) / len(total_processing_times)
        
        stats["success_rate"] = (completed_refunds / len(self.refund_records)) * 100 if self.refund_records else 0
        
        return stats
    
    def search_refunds(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search refunds based on criteria"""
        
        matching_refunds = []
        
        for refund in self.refund_records:
            if self._matches_refund_criteria(refund, search_criteria):
                matching_refunds.append(refund.to_dict())
        
        return matching_refunds
    
    def get_customer_refund_history(self, customer_id: str) -> Dict[str, Any]:
        """Get customer refund history"""
        
        customer_refunds = [r for r in self.refund_records if r.customer_id == customer_id]
        
        history = {
            "customer_id": customer_id,
            "total_refunds": len(customer_refunds),
            "total_refund_amount": 0.0,
            "refunds_by_status": {},
            "recent_refunds": [],
            "refund_frequency": {}
        }
        
        if not customer_refunds:
            return history
        
        total_amount = Decimal('0')
        
        for refund in customer_refunds:
            total_amount += refund.refund_amount
            
            # Count by status
            status = refund.refund_status.value
            history["refunds_by_status"][status] = history["refunds_by_status"].get(status, 0) + 1
        
        history["total_refund_amount"] = float(total_amount)
        
        # Get recent refunds (last 10)
        recent_refunds = sorted(customer_refunds, key=lambda x: x.initiated_date, reverse=True)[:10]
        history["recent_refunds"] = [r.to_dict() for r in recent_refunds]
        
        return history
    
    # Helper methods
    def _get_refund_by_id(self, refund_id: str) -> Optional[RefundRecord]:
        """Get refund by ID"""
        for refund in self.refund_records:
            if refund.refund_id == refund_id:
                return refund
        return None
    
    async def _process_gateway_refund(self, refund: RefundRecord) -> Dict[str, Any]:
        """Process refund through payment gateway"""
        # Simulate gateway processing
        return {
            "success": True,
            "transaction_id": f"gw_txn_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "gateway": "stripe",
            "processing_time": 2.5,
            "fee": float(refund.processing_fee)
        }
    
    def _matches_refund_criteria(self, refund: RefundRecord, criteria: Dict[str, Any]) -> bool:
        """Check if refund matches search criteria"""
        # Implement search logic
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete refund configuration"""
        return {
            "refund_statistics": self.get_refund_statistics(),
            "refund_policy": self.refund_policy.get_config(),
            "refund_processing": self.refund_processing.get_config(),
            "refund_notification": self.refund_notification.get_config(),
            "refund_analytics": self.refund_analytics.get_config(),
            "refunds_count": len(self.refund_records),
            "global_settings": {
                "refund_system_enabled": self.refund_system_enabled,
                "automatic_processing": self.automatic_processing,
                "fraud_detection_enabled": self.fraud_detection_enabled,
                "compliance_mode": self.compliance_mode
            },
            "processing_limits": {
                "daily_refund_limit": float(self.daily_refund_limit),
                "single_refund_limit": float(self.single_refund_limit),
                "customer_daily_limit": float(self.customer_daily_limit)
            },
            "processing_fees": {k: float(v) for k, v in self.processing_fees.items()},
            "sla_settings": {
                "sla_hours": self.sla_hours,
                "priority_sla_hours": self.priority_sla_hours,
                "weekend_processing": self.weekend_processing
            },
            "integration_settings": {
                "payment_gateway_integration": self.payment_gateway_integration,
                "accounting_integration": self.accounting_integration,
                "crm_integration": self.crm_integration,
                "fraud_service_integration": self.fraud_service_integration
            },
            "security_settings": {
                "encryption_enabled": self.encryption_enabled,
                "audit_logging": self.audit_logging,
                "two_factor_approval": self.two_factor_approval,
                "ip_restriction": self.ip_restriction
            }
        }

# Global refund configuration instance
refund_config = RefundConfiguration()

# Export main classes
__all__ = [
    "RefundConfiguration",
    "RefundType",
    "RefundStatus", 
    "RefundReason",
    "RefundMethod",
    "RefundEligibility",
    "RefundRecord",
    "RefundPolicyConfig",
    "RefundProcessingConfig",
    "RefundNotificationConfig",
    "RefundAnalyticsConfig",
    "refund_config"
]
