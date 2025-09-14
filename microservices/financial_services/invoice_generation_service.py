#!/usr/bin/env python3
"""
🧾 Invoice Generation Service - Enterprise Financial Services
============================================================

Advanced invoice generation service for enterprise financial operations.
Provides automated invoice creation, customization, and delivery capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
import json
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class InvoiceStatus(Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class InvoiceType(Enum):
    """Invoice type enumeration."""
    STANDARD = "standard"
    RECURRING = "recurring"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    PROFORMA = "proforma"


@dataclass
class InvoiceLineItem:
    """Invoice line item data structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    quantity: Decimal = Decimal('1')
    unit_price: Decimal = Decimal('0')
    discount_percent: Decimal = Decimal('0')
    tax_rate: Decimal = Decimal('0')
    product_id: Optional[str] = None
    service_id: Optional[str] = None
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate line item subtotal."""
        gross = self.quantity * self.unit_price
        discount = gross * (self.discount_percent / 100)
        return gross - discount
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate tax amount."""
        return self.subtotal * (self.tax_rate / 100)
    
    @property
    def total(self) -> Decimal:
        """Calculate line item total including tax."""
        return self.subtotal + self.tax_amount


@dataclass
class InvoiceData:
    """Invoice data structure."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""
    type: InvoiceType = InvoiceType.STANDARD
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    
    # Customer information
    customer_id: str = ""
    customer_name: str = ""
    customer_email: str = ""
    customer_address: Dict[str, str] = field(default_factory=dict)
    
    # Company information
    company_name: str = "Ainflue Platform"
    company_address: Dict[str, str] = field(default_factory=dict)
    company_tax_id: str = ""
    
    # Invoice items
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    
    # Financial details
    currency: str = "USD"
    tax_rate: Decimal = Decimal('0')
    discount_percent: Decimal = Decimal('0')
    
    # Additional details
    notes: str = ""
    terms: str = ""
    payment_methods: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate invoice subtotal."""
        return sum(item.subtotal for item in self.line_items)
    
    @property
    def discount_amount(self) -> Decimal:
        """Calculate discount amount."""
        return self.subtotal * (self.discount_percent / 100)
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        return sum(item.tax_amount for item in self.line_items)
    
    @property
    def total(self) -> Decimal:
        """Calculate invoice total."""
        return self.subtotal - self.discount_amount + self.tax_amount


class InvoiceGenerationService:
    """
    🧾 Enterprise Invoice Generation Service
    
    Provides comprehensive invoice generation, customization, and delivery
    capabilities for enterprise financial operations.
    """
    
    def __init__(self):
        """Initialize the invoice generation service."""
        self.invoices: Dict[str, InvoiceData] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.sequence_counters: Dict[str, int] = {
            'standard': 1000,
            'recurring': 2000,
            'credit_note': 3000,
            'debit_note': 4000,
            'proforma': 5000
        }
        
        # Setup default templates
        self._setup_default_templates()
        
        logger.info("🧾 Invoice Generation Service initialized")
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> InvoiceData:
        """Create a new invoice."""
        try:
            # Create invoice object
            invoice = InvoiceData()
            
            # Set basic information
            invoice.type = InvoiceType(invoice_data.get('type', 'standard'))
            invoice.customer_id = invoice_data.get('customer_id', '')
            invoice.customer_name = invoice_data.get('customer_name', '')
            invoice.customer_email = invoice_data.get('customer_email', '')
            invoice.customer_address = invoice_data.get('customer_address', {})
            
            # Set dates
            if 'due_date' in invoice_data:
                invoice.due_date = datetime.fromisoformat(invoice_data['due_date'])
            else:
                # Default to 30 days from issue date
                invoice.due_date = invoice.issue_date + timedelta(days=30)
            
            # Generate invoice number
            invoice.invoice_number = self._generate_invoice_number(invoice.type)
            
            # Add line items
            for item_data in invoice_data.get('line_items', []):
                line_item = InvoiceLineItem(
                    description=item_data.get('description', ''),
                    quantity=Decimal(str(item_data.get('quantity', 1))),
                    unit_price=Decimal(str(item_data.get('unit_price', 0))),
                    discount_percent=Decimal(str(item_data.get('discount_percent', 0))),
                    tax_rate=Decimal(str(item_data.get('tax_rate', 0))),
                    product_id=item_data.get('product_id'),
                    service_id=item_data.get('service_id')
                )
                invoice.line_items.append(line_item)
            
            # Set additional details
            invoice.currency = invoice_data.get('currency', 'USD')
            invoice.notes = invoice_data.get('notes', '')
            invoice.terms = invoice_data.get('terms', self._get_default_terms())
            invoice.payment_methods = invoice_data.get('payment_methods', ['credit_card', 'bank_transfer'])
            invoice.metadata = invoice_data.get('metadata', {})
            
            # Store invoice
            self.invoices[invoice.id] = invoice
            
            logger.info(f"📄 Created invoice: {invoice.invoice_number}")
            return invoice
            
        except Exception as e:
            logger.error(f"❌ Failed to create invoice: {e}")
            raise
    
    async def generate_pdf(self, invoice_id: str, template: str = "default") -> bytes:
        """Generate PDF for invoice."""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {invoice_id}")
            
            # Get template
            template_config = self.templates.get(template, self.templates['default'])
            
            # Generate PDF content (placeholder implementation)
            pdf_content = await self._generate_pdf_content(invoice, template_config)
            
            logger.info(f"📄 Generated PDF for invoice: {invoice.invoice_number}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"❌ Failed to generate PDF: {e}")
            raise
    
    async def send_invoice(self, invoice_id: str, delivery_method: str = "email") -> bool:
        """Send invoice to customer."""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {invoice_id}")
            
            if delivery_method == "email":
                await self._send_email_invoice(invoice)
            elif delivery_method == "portal":
                await self._send_portal_notification(invoice)
            else:
                raise ValueError(f"Unsupported delivery method: {delivery_method}")
            
            # Update invoice status
            invoice.status = InvoiceStatus.SENT
            invoice.sent_at = datetime.now()
            invoice.updated_at = datetime.now()
            
            logger.info(f"📤 Sent invoice: {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send invoice: {e}")
            return False
    
    async def mark_as_paid(self, invoice_id: str, payment_data: Dict[str, Any]) -> bool:
        """Mark invoice as paid."""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {invoice_id}")
            
            invoice.status = InvoiceStatus.PAID
            invoice.paid_at = datetime.now()
            invoice.updated_at = datetime.now()
            
            # Store payment data in metadata
            invoice.metadata['payment'] = payment_data
            
            logger.info(f"💰 Marked invoice as paid: {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark invoice as paid: {e}")
            return False
    
    async def get_invoice(self, invoice_id: str) -> Optional[InvoiceData]:
        """Get invoice by ID."""
        return self.invoices.get(invoice_id)
    
    async def list_invoices(self, filters: Optional[Dict[str, Any]] = None) -> List[InvoiceData]:
        """List invoices with optional filters."""
        invoices = list(self.invoices.values())
        
        if not filters:
            return invoices
        
        # Apply filters
        if 'status' in filters:
            status = InvoiceStatus(filters['status'])
            invoices = [inv for inv in invoices if inv.status == status]
        
        if 'customer_id' in filters:
            customer_id = filters['customer_id']
            invoices = [inv for inv in invoices if inv.customer_id == customer_id]
        
        if 'date_from' in filters:
            date_from = datetime.fromisoformat(filters['date_from'])
            invoices = [inv for inv in invoices if inv.issue_date >= date_from]
        
        if 'date_to' in filters:
            date_to = datetime.fromisoformat(filters['date_to'])
            invoices = [inv for inv in invoices if inv.issue_date <= date_to]
        
        return invoices
    
    async def get_invoice_summary(self, period: str = "month") -> Dict[str, Any]:
        """Get invoice summary statistics."""
        invoices = list(self.invoices.values())
        
        # Calculate period start
        now = datetime.now()
        if period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Filter invoices by period
        period_invoices = [inv for inv in invoices if inv.issue_date >= start_date]
        
        # Calculate statistics
        total_amount = sum(inv.total for inv in period_invoices)
        paid_amount = sum(inv.total for inv in period_invoices if inv.status == InvoiceStatus.PAID)
        pending_amount = sum(inv.total for inv in period_invoices if inv.status == InvoiceStatus.SENT)
        overdue_amount = sum(
            inv.total for inv in period_invoices 
            if inv.status == InvoiceStatus.OVERDUE or (
                inv.status == InvoiceStatus.SENT and 
                inv.due_date and 
                inv.due_date < now
            )
        )
        
        return {
            'period': period,
            'total_invoices': len(period_invoices),
            'total_amount': float(total_amount),
            'paid_amount': float(paid_amount),
            'pending_amount': float(pending_amount),
            'overdue_amount': float(overdue_amount),
            'payment_rate': float(paid_amount / total_amount * 100) if total_amount > 0 else 0,
            'status_breakdown': {
                status.value: len([inv for inv in period_invoices if inv.status == status])
                for status in InvoiceStatus
            }
        }
    
    def _generate_invoice_number(self, invoice_type: InvoiceType) -> str:
        """Generate unique invoice number."""
        type_key = invoice_type.value
        counter = self.sequence_counters[type_key]
        self.sequence_counters[type_key] += 1
        
        prefix_map = {
            'standard': 'INV',
            'recurring': 'REC',
            'credit_note': 'CN',
            'debit_note': 'DN',
            'proforma': 'PRO'
        }
        
        prefix = prefix_map.get(type_key, 'INV')
        year = datetime.now().year
        
        return f"{prefix}-{year}-{counter:06d}"
    
    def _setup_default_templates(self):
        """Setup default invoice templates."""
        self.templates['default'] = {
            'name': 'Default Invoice Template',
            'logo_url': 'https://ainflue.com/logo.png',
            'primary_color': '#007bff',
            'font_family': 'Arial, sans-serif',
            'layout': 'standard',
            'include_qr_code': True,
            'footer_text': 'Thank you for your business!'
        }
        
        self.templates['modern'] = {
            'name': 'Modern Invoice Template',
            'logo_url': 'https://ainflue.com/logo.png',
            'primary_color': '#6c757d',
            'font_family': 'Helvetica, sans-serif',
            'layout': 'modern',
            'include_qr_code': True,
            'footer_text': 'Powered by Ainflue Platform'
        }
    
    def _get_default_terms(self) -> str:
        """Get default payment terms."""
        return """Payment Terms:
        
1. Payment is due within 30 days of invoice date
2. Late payments may incur additional charges
3. All amounts are in USD unless otherwise specified
4. For questions, contact: billing@ainflue.com

Thank you for choosing Ainflue Platform!"""
    
    async def _generate_pdf_content(self, invoice: InvoiceData, template: Dict[str, Any]) -> bytes:
        """Generate PDF content (placeholder implementation)."""
        # In a real implementation, this would use a PDF library like ReportLab
        pdf_content = f"""
        Invoice: {invoice.invoice_number}
        Date: {invoice.issue_date.strftime('%Y-%m-%d')}
        Customer: {invoice.customer_name}
        Total: {invoice.currency} {invoice.total}
        
        Template: {template['name']}
        """.encode('utf-8')
        
        return pdf_content
    
    async def _send_email_invoice(self, invoice: InvoiceData):
        """Send invoice via email."""
        # Placeholder for email sending logic
        logger.info(f"📧 Sending invoice {invoice.invoice_number} to {invoice.customer_email}")
    
    async def _send_portal_notification(self, invoice: InvoiceData):
        """Send invoice notification via customer portal."""
        # Placeholder for portal notification logic
        logger.info(f"🔔 Sending portal notification for invoice {invoice.invoice_number}")


async def main():
    """Example usage of the Invoice Generation Service."""
    print("🧾 Invoice Generation Service Example")
    print("=" * 40)
    
    # Create service
    invoice_service = InvoiceGenerationService()
    
    # Create invoice
    invoice_data = {
        'type': 'standard',
        'customer_id': 'cust_123',
        'customer_name': 'Acme Creator Studio',
        'customer_email': 'billing@acme-creator.com',
        'customer_address': {
            'street': '123 Creator St',
            'city': 'Los Angeles',
            'state': 'CA',
            'zip': '90210',
            'country': 'USA'
        },
        'line_items': [
            {
                'description': 'Ainflue Platform - Pro Plan',
                'quantity': 1,
                'unit_price': 99.99,
                'tax_rate': 8.25
            },
            {
                'description': 'Additional Storage (100GB)',
                'quantity': 2,
                'unit_price': 9.99,
                'tax_rate': 8.25
            }
        ],
        'notes': 'Thank you for choosing Ainflue Platform!',
        'payment_methods': ['credit_card', 'paypal']
    }
    
    invoice = await invoice_service.create_invoice(invoice_data)
    print(f"📄 Created invoice: {invoice.invoice_number}")
    print(f"💰 Total amount: {invoice.currency} {invoice.total}")
    
    # Generate PDF
    pdf_content = await invoice_service.generate_pdf(invoice.id)
    print(f"📋 Generated PDF ({len(pdf_content)} bytes)")
    
    # Send invoice
    sent = await invoice_service.send_invoice(invoice.id, "email")
    if sent:
        print("📤 Invoice sent successfully")
    
    # Get summary
    summary = await invoice_service.get_invoice_summary("month")
    print(f"\n📊 Monthly Summary:")
    print(f"   Total invoices: {summary['total_invoices']}")
    print(f"   Total amount: ${summary['total_amount']:.2f}")
    print(f"   Payment rate: {summary['payment_rate']:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())