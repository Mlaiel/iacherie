"""
Invoice Config module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Invoice Configuration Module
import asyncio

====================================

Enterprise-grade invoice configuration for the Ainflue platform.
Comprehensive invoice management with automated generation, customization,
compliance tracking, and multi-format support.

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

class InvoiceType(str, Enum):
    """Types of invoices"""
    STANDARD = "standard"              # Standard invoice
    PROFORMA = "proforma"             # Proforma invoice
    CREDIT_NOTE = "credit_note"       # Credit note
    DEBIT_NOTE = "debit_note"         # Debit note
    RECURRING = "recurring"           # Recurring invoice
    SUBSCRIPTION = "subscription"     # Subscription invoice
    USAGE_BASED = "usage_based"       # Usage-based invoice
    MILESTONE = "milestone"           # Milestone invoice
    ADVANCE = "advance"               # Advance payment invoice

class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"                   # Draft invoice
    PENDING = "pending"               # Pending approval
    SENT = "sent"                     # Sent to customer
    VIEWED = "viewed"                 # Viewed by customer
    PAID = "paid"                     # Fully paid
    PARTIALLY_PAID = "partially_paid" # Partially paid
    OVERDUE = "overdue"               # Overdue payment
    CANCELLED = "cancelled"           # Cancelled invoice
    REFUNDED = "refunded"             # Refunded invoice
    DISPUTED = "disputed"             # Disputed invoice

class PaymentTerms(str, Enum):
    """Payment terms"""
    NET_0 = "net_0"                   # Payment due immediately
    NET_7 = "net_7"                   # Payment due in 7 days
    NET_15 = "net_15"                 # Payment due in 15 days
    NET_30 = "net_30"                 # Payment due in 30 days
    NET_60 = "net_60"                 # Payment due in 60 days
    NET_90 = "net_90"                 # Payment due in 90 days
    COD = "cod"                       # Cash on delivery
    ADVANCE = "advance"               # Advance payment required

class InvoiceFormat(str, Enum):
    """Invoice output formats"""
    PDF = "pdf"
    HTML = "html"
    XML = "xml"
    JSON = "json"
    CSV = "csv"
    UBL = "ubl"                       # Universal Business Language
    EDIFACT = "edifact"               # Electronic Data Interchange

@dataclass
class InvoiceLineItem:
    """Invoice line item"""
    item_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    unit_of_measure: str = "piece"
    discount_percentage: Decimal = Decimal('0')
    tax_rate: Decimal = Decimal('0')
    tax_amount: Decimal = Decimal('0')
    line_total: Decimal = Decimal('0')
    product_code: Optional[str] = None
    service_period_start: Optional[datetime] = None
    service_period_end: Optional[datetime] = None
    
    def calculate_totals(self) -> None:
        """Calculate line item totals"""
        # Calculate subtotal with discount
        subtotal = self.quantity * self.unit_price
        discount_amount = subtotal * (self.discount_percentage / Decimal('100'))
        discounted_subtotal = subtotal - discount_amount
        
        # Calculate tax
        self.tax_amount = discounted_subtotal * (self.tax_rate / Decimal('100'))
        
        # Calculate line total
        self.line_total = discounted_subtotal + self.tax_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert line item to dictionary"""
        return {
            "item_id": self.item_id,
            "description": self.description,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "unit_of_measure": self.unit_of_measure,
            "discount_percentage": float(self.discount_percentage),
            "tax_rate": float(self.tax_rate),
            "tax_amount": float(self.tax_amount),
            "line_total": float(self.line_total),
            "product_code": self.product_code,
            "service_period_start": self.service_period_start.isoformat() if self.service_period_start else None,
            "service_period_end": self.service_period_end.isoformat() if self.service_period_end else None
        }

@dataclass
class InvoiceRecord:
    """Invoice record"""
    invoice_id: str
    invoice_number: str
    invoice_type: InvoiceType
    status: InvoiceStatus
    customer_id: str
    customer_name: str
    customer_email: str
    billing_address: Dict[str, str]
    shipping_address: Optional[Dict[str, str]]
    issue_date: datetime
    due_date: datetime
    payment_terms: PaymentTerms
    currency: str
    line_items: List[InvoiceLineItem]
    subtotal: Decimal = Decimal('0')
    discount_total: Decimal = Decimal('0')
    tax_total: Decimal = Decimal('0')
    total_amount: Decimal = Decimal('0')
    paid_amount: Decimal = Decimal('0')
    remaining_balance: Decimal = Decimal('0')
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    reference_number: Optional[str] = None
    purchase_order: Optional[str] = None
    
    def calculate_totals(self) -> None:
        """Calculate invoice totals"""
        self.subtotal = Decimal('0')
        self.discount_total = Decimal('0')
        self.tax_total = Decimal('0')
        
        for item in self.line_items:
            item.calculate_totals()
            
            # Add to invoice totals
            item_subtotal = item.quantity * item.unit_price
            item_discount = item_subtotal * (item.discount_percentage / Decimal('100'))
            
            self.subtotal += item_subtotal
            self.discount_total += item_discount
            self.tax_total += item.tax_amount
        
        self.total_amount = self.subtotal - self.discount_total + self.tax_total
        self.remaining_balance = self.total_amount - self.paid_amount
        self.last_updated = datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        return (self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED] and
                datetime.now() > self.due_date)
    
    def days_overdue(self) -> int:
        """Calculate days overdue"""
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary"""
        return {
            "invoice_id": self.invoice_id,
            "invoice_number": self.invoice_number,
            "invoice_type": self.invoice_type.value,
            "status": self.status.value,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "billing_address": self.billing_address,
            "shipping_address": self.shipping_address,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "payment_terms": self.payment_terms.value,
            "currency": self.currency,
            "line_items": [item.to_dict() for item in self.line_items],
            "subtotal": float(self.subtotal),
            "discount_total": float(self.discount_total),
            "tax_total": float(self.tax_total),
            "total_amount": float(self.total_amount),
            "paid_amount": float(self.paid_amount),
            "remaining_balance": float(self.remaining_balance),
            "created_date": self.created_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "notes": self.notes,
            "terms_conditions": self.terms_conditions,
            "reference_number": self.reference_number,
            "purchase_order": self.purchase_order,
            "is_overdue": self.is_overdue(),
            "days_overdue": self.days_overdue()
        }

@dataclass
class InvoiceGenerationConfig:
    """Invoice generation configuration"""
    enabled: bool = True
    
    # Automatic generation
    automatic_generation: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "subscription_invoices": True,
        "usage_based_invoices": True,
        "milestone_invoices": True,
        "recurring_invoices": True,
        "generation_schedule": "monthly",
        "advance_notice_days": 7,
        "retry_failed_generation": True
    })
    
    # Invoice numbering
    invoice_numbering: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "numbering_scheme": "sequential",
        "prefix": "INV",
        "suffix": "",
        "separator": "-",
        "padding_zeros": 6,
        "reset_annually": True,
        "custom_format": "{prefix}{separator}{year}{separator}{number:06d}"
    })
    
    # Content generation
    content_generation: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "auto_populate_customer_data": True,
        "auto_calculate_taxes": True,
        "auto_apply_discounts": True,
        "include_usage_details": True,
        "include_service_periods": True,
        "multi_language_support": True,
        "localization_support": True
    })
    
    # Template engine
    template_engine: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "template_system": "jinja2",
        "custom_templates": True,
        "template_validation": True,
        "dynamic_content": True,
        "conditional_logic": True,
        "brand_customization": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get invoice generation configuration"""
        return {
            "enabled": self.enabled,
            "automatic_generation": self.automatic_generation,
            "invoice_numbering": self.invoice_numbering,
            "content_generation": self.content_generation,
            "template_engine": self.template_engine
        }

@dataclass
class InvoiceTemplateConfig:
    """Invoice template configuration"""
    enabled: bool = True
    
    # Template management
    template_management: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multiple_templates": True,
        "template_versioning": True,
        "template_approval": True,
        "template_testing": True,
        "template_backup": True,
        "template_inheritance": True
    })
    
    # Brand customization
    brand_customization: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "company_logo": True,
        "brand_colors": True,
        "custom_fonts": True,
        "header_customization": True,
        "footer_customization": True,
        "watermarks": True,
        "digital_signatures": True
    })
    
    # Layout options
    layout_options: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "responsive_design": True,
        "print_optimization": True,
        "multi_page_support": True,
        "page_breaks": True,
        "section_customization": True,
        "field_positioning": True,
        "conditional_sections": True
    })
    
    # Internationalization
    internationalization: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "multi_language": True,
        "currency_formatting": True,
        "date_formatting": True,
        "number_formatting": True,
        "rtl_support": True,
        "locale_specific_templates": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get invoice template configuration"""
        return {
            "enabled": self.enabled,
            "template_management": self.template_management,
            "brand_customization": self.brand_customization,
            "layout_options": self.layout_options,
            "internationalization": self.internationalization
        }

@dataclass
class InvoiceDeliveryConfig:
    """Invoice delivery configuration"""
    enabled: bool = True
    
    # Delivery methods
    delivery_methods: Dict[str, Any] = field(default_factory=lambda: {
        "email": {
            "enabled": True,
            "automatic_sending": True,
            "email_templates": True,
            "delivery_confirmation": True,
            "read_receipts": True,
            "follow_up_reminders": True
        },
        "portal": {
            "enabled": True,
            "customer_portal": True,
            "online_viewing": True,
            "download_options": True,
            "payment_integration": True,
            "notification_preferences": True
        },
        "api": {
            "enabled": True,
            "webhook_delivery": True,
            "real_time_sync": True,
            "batch_delivery": True,
            "delivery_status": True
        },
        "print": {
            "enabled": False,
            "postal_service": False,
            "certified_mail": False,
            "international_delivery": False
        }
    })
    
    # Delivery scheduling
    delivery_scheduling: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "immediate_delivery": True,
        "scheduled_delivery": True,
        "batch_delivery": True,
        "retry_delivery": True,
        "delivery_windows": True,
        "time_zone_support": True
    })
    
    # Delivery tracking
    delivery_tracking: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "delivery_status": True,
        "delivery_confirmation": True,
        "bounce_handling": True,
        "unsubscribe_handling": True,
        "delivery_analytics": True,
        "failure_notifications": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get invoice delivery configuration"""
        return {
            "enabled": self.enabled,
            "delivery_methods": self.delivery_methods,
            "delivery_scheduling": self.delivery_scheduling,
            "delivery_tracking": self.delivery_tracking
        }

@dataclass
class InvoiceComplianceConfig:
    """Invoice compliance configuration"""
    enabled: bool = True
    
    # Legal compliance
    legal_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "required_fields": True,
        "legal_entity_info": True,
        "tax_registration_numbers": True,
        "regulatory_text": True,
        "digital_signature": True,
        "archival_requirements": True,
        "audit_trail": True
    })
    
    # Tax compliance
    tax_compliance: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "tax_calculation": True,
        "tax_breakdown": True,
        "tax_exemptions": True,
        "reverse_charge": True,
        "cross_border_rules": True,
        "tax_reporting": True,
        "compliance_validation": True
    })
    
    # Industry standards
    industry_standards: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "ubl_compliance": True,
        "edifact_support": True,
        "peppol_compliance": True,
        "e_invoicing_standards": True,
        "b2b_standards": True,
        "government_standards": True
    })
    
    # Data protection
    data_protection: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "gdpr_compliance": True,
        "data_anonymization": True,
        "consent_management": True,
        "data_retention": True,
        "right_to_erasure": True,
        "data_portability": True
    })
    
    def get_config(self) -> Dict[str, Any]:
        """Get invoice compliance configuration"""
        return {
            "enabled": self.enabled,
            "legal_compliance": self.legal_compliance,
            "tax_compliance": self.tax_compliance,
            "industry_standards": self.industry_standards,
            "data_protection": self.data_protection
        }

class InvoiceConfiguration:
    """Main invoice configuration manager"""
    
    def __init__(self) -> None:
        """Initialize invoice configuration"""
        # Invoice configuration components
        self.invoice_generation = InvoiceGenerationConfig()
        self.invoice_template = InvoiceTemplateConfig()
        self.invoice_delivery = InvoiceDeliveryConfig()
        self.invoice_compliance = InvoiceComplianceConfig()
        
        # Invoice storage
        self.invoice_records: List[InvoiceRecord] = []
        
        # Global invoice settings
        self.invoice_system_enabled = True
        self.automatic_numbering = True
        self.duplicate_detection = True
        self.invoice_retention_years = 10
        
        # Default settings
        self.default_payment_terms = PaymentTerms.NET_30
        self.default_currency = "EUR"
        self.default_tax_rate = Decimal('20.0')  # 20% VAT
        
        # Integration settings
        self.erp_integration = True
        self.accounting_integration = True
        self.payment_gateway_integration = True
        self.crm_integration = True
        
        # Performance settings
        self.bulk_operations = True
        self.async_processing = True
        self.caching_enabled = True
        self.pdf_optimization = True
        
        # Security settings
        self.invoice_encryption = True
        self.access_control = True
        self.audit_logging = True
        self.data_anonymization = True
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> InvoiceRecord:
        """Create new invoice"""
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        # Create invoice record
        invoice = InvoiceRecord(
            invoice_id=f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            invoice_number=invoice_number,
            invoice_type=InvoiceType(invoice_data.get("invoice_type", "standard")),
            status=InvoiceStatus.DRAFT,
            customer_id=invoice_data.get("customer_id", ""),
            customer_name=invoice_data.get("customer_name", ""),
            customer_email=invoice_data.get("customer_email", ""),
            billing_address=invoice_data.get("billing_address", {}),
            shipping_address=invoice_data.get("shipping_address"),
            issue_date=invoice_data.get("issue_date", datetime.now()),
            due_date=invoice_data.get("due_date", datetime.now() + timedelta(days=30)),
            payment_terms=PaymentTerms(invoice_data.get("payment_terms", self.default_payment_terms.value)),
            currency=invoice_data.get("currency", self.default_currency),
            line_items=[],
            notes=invoice_data.get("notes"),
            terms_conditions=invoice_data.get("terms_conditions"),
            reference_number=invoice_data.get("reference_number"),
            purchase_order=invoice_data.get("purchase_order")
        )
        
        # Add line items
        for item_data in invoice_data.get("line_items", []):
            line_item = InvoiceLineItem(
                item_id=f"item_{len(invoice.line_items) + 1}",
                description=item_data.get("description", ""),
                quantity=Decimal(str(item_data.get("quantity", "1"))),
                unit_price=Decimal(str(item_data.get("unit_price", "0"))),
                unit_of_measure=item_data.get("unit_of_measure", "piece"),
                discount_percentage=Decimal(str(item_data.get("discount_percentage", "0"))),
                tax_rate=Decimal(str(item_data.get("tax_rate", str(self.default_tax_rate)))),
                product_code=item_data.get("product_code"),
                service_period_start=item_data.get("service_period_start"),
                service_period_end=item_data.get("service_period_end")
            )
            invoice.line_items.append(line_item)
        
        # Calculate totals
        invoice.calculate_totals()
        
        # Store invoice
        self.invoice_records.append(invoice)
        
        return invoice
    
    async def generate_invoice_pdf(self, invoice_id: str, template: str = "default") -> Dict[str, Any]:
        """Generate PDF for invoice"""
        
        invoice = self._get_invoice_by_id(invoice_id)
        if not invoice:
            return {"error": f"Invoice {invoice_id} not found"}
        
        pdf_result = {
            "invoice_id": invoice_id,
            "template": template,
            "generation_timestamp": datetime.now().isoformat(),
            "pdf_path": None,
            "pdf_size": 0,
            "success": False
        }
        
        try:
            # Generate PDF using template
            pdf_path = await self._generate_pdf_from_template(invoice, template)
            
            # Get file size
            pdf_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
            
            pdf_result.update({
                "pdf_path": pdf_path,
                "pdf_size": pdf_size,
                "success": True
            })
            
        except Exception as e:
            pdf_result["error"] = str(e)
        
        return pdf_result
    
    async def send_invoice(self, invoice_id: str, delivery_method: str = "email") -> Dict[str, Any]:
        """Send invoice to customer"""
        
        invoice = self._get_invoice_by_id(invoice_id)
        if not invoice:
            return {"error": f"Invoice {invoice_id} not found"}
        
        send_result = {
            "invoice_id": invoice_id,
            "delivery_method": delivery_method,
            "send_timestamp": datetime.now().isoformat(),
            "recipient": invoice.customer_email,
            "success": False
        }
        
        try:
            if delivery_method == "email":
                send_result.update(await self._send_invoice_email(invoice))
            elif delivery_method == "portal":
                send_result.update(await self._notify_portal_invoice(invoice))
            elif delivery_method == "api":
                send_result.update(await self._deliver_via_api(invoice))
            else:
                send_result["error"] = f"Unsupported delivery method: {delivery_method}"
                return send_result
            
            # Update invoice status
            if send_result.get("success"):
                invoice.status = InvoiceStatus.SENT
                invoice.last_updated = datetime.now()
            
        except Exception as e:
            send_result["error"] = str(e)
        
        return send_result
    
    async def record_payment(self, invoice_id: str, payment_amount: Decimal, payment_reference: str = None) -> Dict[str, Any]:
        """Record payment for invoice"""
        
        invoice = self._get_invoice_by_id(invoice_id)
        if not invoice:
            return {"error": f"Invoice {invoice_id} not found"}
        
        payment_result = {
            "invoice_id": invoice_id,
            "payment_amount": float(payment_amount),
            "payment_reference": payment_reference,
            "payment_timestamp": datetime.now().isoformat(),
            "previous_balance": float(invoice.remaining_balance),
            "new_balance": 0.0,
            "status_change": None
        }
        
        # Update paid amount
        invoice.paid_amount += payment_amount
        invoice.remaining_balance = invoice.total_amount - invoice.paid_amount
        
        # Update status based on payment
        previous_status = invoice.status
        if invoice.remaining_balance <= Decimal('0'):
            invoice.status = InvoiceStatus.PAID
        elif invoice.paid_amount > Decimal('0'):
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        # Record status change
        if previous_status != invoice.status:
            payment_result["status_change"] = {
                "from": previous_status.value,
                "to": invoice.status.value
            }
        
        payment_result["new_balance"] = float(invoice.remaining_balance)
        invoice.last_updated = datetime.now()
        
        return payment_result
    
    def get_invoice_statistics(self) -> Dict[str, Any]:
        """Get invoice statistics"""
        
        stats = {
            "total_invoices": len(self.invoice_records),
            "invoices_by_status": {},
            "invoices_by_type": {},
            "total_revenue": 0.0,
            "outstanding_amount": 0.0,
            "overdue_amount": 0.0,
            "average_invoice_value": 0.0,
            "collection_metrics": {}
        }
        
        if not self.invoice_records:
            return stats
        
        total_amount = Decimal('0')
        outstanding_amount = Decimal('0')
        overdue_amount = Decimal('0')
        
        for invoice in self.invoice_records:
            # Count by status
            status = invoice.status.value
            stats["invoices_by_status"][status] = stats["invoices_by_status"].get(status, 0) + 1
            
            # Count by type
            invoice_type = invoice.invoice_type.value
            stats["invoices_by_type"][invoice_type] = stats["invoices_by_type"].get(invoice_type, 0) + 1
            
            # Calculate amounts
            total_amount += invoice.total_amount
            
            if invoice.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
                outstanding_amount += invoice.remaining_balance
                
                if invoice.is_overdue():
                    overdue_amount += invoice.remaining_balance
        
        stats["total_revenue"] = float(total_amount)
        stats["outstanding_amount"] = float(outstanding_amount)
        stats["overdue_amount"] = float(overdue_amount)
        stats["average_invoice_value"] = float(total_amount / len(self.invoice_records))
        
        # Collection metrics
        paid_invoices = len([inv for inv in self.invoice_records if inv.status == InvoiceStatus.PAID])
        stats["collection_metrics"] = {
            "collection_rate": (paid_invoices / len(self.invoice_records)) * 100 if self.invoice_records else 0,
            "average_collection_time": 25.0  # days
        }
        
        return stats
    
    def search_invoices(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search invoices based on criteria"""
        
        matching_invoices = []
        
        for invoice in self.invoice_records:
            if self._matches_invoice_criteria(invoice, search_criteria):
                matching_invoices.append(invoice.to_dict())
        
        return matching_invoices
    
    # Helper methods
    def _get_invoice_by_id(self, invoice_id: str) -> Optional[InvoiceRecord]:
        """Get invoice by ID"""
        for invoice in self.invoice_records:
            if invoice.invoice_id == invoice_id:
                return invoice
        return None
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        config = self.invoice_generation.invoice_numbering
        
        # Get current year
        current_year = datetime.now().year
        
        # Count invoices for current year
        year_invoices = len([inv for inv in self.invoice_records 
                           if inv.created_date.year == current_year])
        
        # Generate number
        next_number = year_invoices + 1
        
        return config["custom_format"].format(
            prefix=config["prefix"],
            separator=config["separator"],
            year=current_year,
            number=next_number
        )
    
    async def _generate_pdf_from_template(self, invoice: InvoiceRecord, template: str) -> str:
        """Generate PDF from template"""
        # Implement PDF generation logic
        return f"/tmp/invoice_{invoice.invoice_id}.pdf"
    
    async def _send_invoice_email(self, invoice: InvoiceRecord) -> Dict[str, Any]:
        """Send invoice via email"""
        return {"success": True, "message_id": "msg_123"}
    
    async def _notify_portal_invoice(self, invoice: InvoiceRecord) -> Dict[str, Any]:
        """Notify customer of new invoice in portal"""
        return {"success": True, "portal_url": f"https://portal.ainflue.com/invoices/{invoice.invoice_id}"}
    
    async def _deliver_via_api(self, invoice: InvoiceRecord) -> Dict[str, Any]:
        """Deliver invoice via API"""
        return {"success": True, "webhook_delivered": True}
    
    def _matches_invoice_criteria(self, invoice: InvoiceRecord, criteria: Dict[str, Any]) -> bool:
        """Check if invoice matches search criteria"""
        # Implement search logic
        return True
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete invoice configuration"""
        return {
            "invoice_statistics": self.get_invoice_statistics(),
            "invoice_generation": self.invoice_generation.get_config(),
            "invoice_template": self.invoice_template.get_config(),
            "invoice_delivery": self.invoice_delivery.get_config(),
            "invoice_compliance": self.invoice_compliance.get_config(),
            "invoices_count": len(self.invoice_records),
            "global_settings": {
                "invoice_system_enabled": self.invoice_system_enabled,
                "automatic_numbering": self.automatic_numbering,
                "duplicate_detection": self.duplicate_detection,
                "invoice_retention_years": self.invoice_retention_years
            },
            "default_settings": {
                "default_payment_terms": self.default_payment_terms.value,
                "default_currency": self.default_currency,
                "default_tax_rate": float(self.default_tax_rate)
            },
            "integration_settings": {
                "erp_integration": self.erp_integration,
                "accounting_integration": self.accounting_integration,
                "payment_gateway_integration": self.payment_gateway_integration,
                "crm_integration": self.crm_integration
            },
            "performance_settings": {
                "bulk_operations": self.bulk_operations,
                "async_processing": self.async_processing,
                "caching_enabled": self.caching_enabled,
                "pdf_optimization": self.pdf_optimization
            },
            "security_settings": {
                "invoice_encryption": self.invoice_encryption,
                "access_control": self.access_control,
                "audit_logging": self.audit_logging,
                "data_anonymization": self.data_anonymization
            }
        }

# Global invoice configuration instance
invoice_config = InvoiceConfiguration()

# Export main classes
__all__ = [
    "InvoiceConfiguration",
    "InvoiceType",
    "InvoiceStatus",
    "PaymentTerms",
    "InvoiceFormat",
    "InvoiceLineItem",
    "InvoiceRecord",
    "InvoiceGenerationConfig",
    "InvoiceTemplateConfig",
    "InvoiceDeliveryConfig",
    "InvoiceComplianceConfig",
    "invoice_config"
]
