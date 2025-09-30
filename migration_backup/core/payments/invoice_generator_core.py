"""
Ainflue Core Payments - Invoice Generator Core
==============================================

Enterprise-grade invoice generation system with automated billing,
multi-currency support, tax calculations, and compliance features.
Provides comprehensive invoicing for creators and businesses.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceType(str, Enum):
    """Invoice types"""
    STANDARD = "standard"
    RECURRING = "recurring"
    PROFORMA = "proforma"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"

@dataclass
class InvoiceItem:
    """Invoice line item"""
    item_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal = Decimal("0.00")
    discount_rate: Decimal = Decimal("0.00")
    
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self) -> Decimal:
        return self.subtotal * (self.discount_rate / 100)
    
    @property
    def taxable_amount(self) -> Decimal:
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> Decimal:
        return self.taxable_amount * (self.tax_rate / 100)
    
    @property
    def total(self) -> Decimal:
        return self.taxable_amount + self.tax_amount

@dataclass
class Invoice:
    """Invoice entity"""
    invoice_id: str
    invoice_number: str
    invoice_type: InvoiceType
    status: InvoiceStatus
    issue_date: datetime
    due_date: datetime
    currency: str
    items: List[InvoiceItem]
    customer_id: str
    customer_details: Dict[str, Any]
    billing_address: Dict[str, str]
    notes: str = ""
    terms: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def subtotal(self) -> Decimal:
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_discount(self) -> Decimal:
        return sum(item.discount_amount for item in self.items)
    
    @property
    def total_tax(self) -> Decimal:
        return sum(item.tax_amount for item in self.items)
    
    @property
    def total_amount(self) -> Decimal:
        return sum(item.total for item in self.items)

class InvoiceGeneratorCore:
    """Enterprise invoice generation system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize invoice generator core"""
        self.level = level
        self.invoices: Dict[str, Invoice] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.invoice_counter = 1000
        
        # Configuration
        self.config = {
            "default_currency": "USD",
            "default_payment_terms": "Net 30",
            "tax_rates": {
                "US": Decimal("8.25"),
                "EU": Decimal("21.00"),
                "UK": Decimal("20.00")
            },
            "invoice_prefix": "INV",
            "auto_send": False,
            "late_fee_rate": Decimal("1.5"),  # Monthly
            "reminder_days": [7, 3, 1]  # Days before due date
        }
        
        # Initialize default templates
        self._initialize_templates()
        
        logger.info(f"📄 Invoice Generator Core initialized - Level: {level}")

    def _initialize_templates(self):
        """Initialize default invoice templates"""
        
        self.templates["standard"] = {
            "name": "Standard Invoice",
            "header": "INVOICE",
            "fields": [
                "invoice_number", "issue_date", "due_date",
                "customer_details", "billing_address",
                "items", "subtotal", "tax", "total"
            ],
            "footer": "Thank you for your business!",
            "style": "professional"
        }
        
        self.templates["minimal"] = {
            "name": "Minimal Invoice",
            "header": "Invoice",
            "fields": ["invoice_number", "customer_details", "items", "total"],
            "footer": "",
            "style": "clean"
        }

    async def create_invoice(
        self,
        customer_id: str,
        customer_details: Dict[str, Any],
        items: List[Dict[str, Any]],
        invoice_type: InvoiceType = InvoiceType.STANDARD,
        currency: str = None,
        due_days: int = 30,
        billing_address: Optional[Dict[str, str]] = None,
        notes: str = "",
        terms: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new invoice"""
        
        try:
            # Generate invoice ID and number
            invoice_id = str(uuid.uuid4())
            invoice_number = f"{self.config['invoice_prefix']}-{self.invoice_counter:06d}"
            self.invoice_counter += 1
            
            # Process items
            invoice_items = []
            for item_data in items:
                item = InvoiceItem(
                    item_id=item_data.get("item_id", str(uuid.uuid4())),
                    description=item_data["description"],
                    quantity=Decimal(str(item_data["quantity"])),
                    unit_price=Decimal(str(item_data["unit_price"])),
                    tax_rate=Decimal(str(item_data.get("tax_rate", "0.00"))),
                    discount_rate=Decimal(str(item_data.get("discount_rate", "0.00")))
                )
                invoice_items.append(item)
            
            # Create invoice
            invoice = Invoice(
                invoice_id=invoice_id,
                invoice_number=invoice_number,
                invoice_type=invoice_type,
                status=InvoiceStatus.DRAFT,
                issue_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=due_days),
                currency=currency or self.config["default_currency"],
                items=invoice_items,
                customer_id=customer_id,
                customer_details=customer_details,
                billing_address=billing_address or {},
                notes=notes,
                terms=terms or self.config["default_payment_terms"],
                metadata=metadata or {}
            )
            
            # Store invoice
            self.invoices[invoice_id] = invoice
            
            logger.info(f"Created invoice {invoice_number} for customer {customer_id}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {str(e)}")
            raise

    async def generate_invoice_pdf(
        self,
        invoice_id: str,
        template: str = "standard"
    ) -> bytes:
        """Generate PDF for invoice"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        # Generate HTML first
        html_content = await self.generate_invoice_html(invoice_id, template)
        
        # Convert to PDF (placeholder - would use proper PDF library)
        pdf_content = self._html_to_pdf(html_content)
        
        return pdf_content

    async def generate_invoice_html(
        self,
        invoice_id: str,
        template: str = "standard"
    ) -> str:
        """Generate HTML for invoice"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        template_config = self.templates.get(template, self.templates["standard"])
        
        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice {invoice.invoice_number}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .invoice-details {{ margin-bottom: 30px; }}
                .customer-info {{ margin-bottom: 30px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                .items-table th, .items-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .items-table th {{ background-color: #f2f2f2; }}
                .totals {{ text-align: right; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{template_config['header']}</h1>
            </div>
            
            <div class="invoice-details">
                <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
                <p><strong>Issue Date:</strong> {invoice.issue_date.strftime('%Y-%m-%d')}</p>
                <p><strong>Due Date:</strong> {invoice.due_date.strftime('%Y-%m-%d')}</p>
                <p><strong>Status:</strong> {invoice.status.value.title()}</p>
            </div>
            
            <div class="customer-info">
                <h3>Bill To:</h3>
                <p><strong>{invoice.customer_details.get('name', 'Customer')}</strong></p>
                <p>{invoice.customer_details.get('email', '')}</p>
                {self._format_address(invoice.billing_address)}
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Tax Rate</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {self._format_invoice_items(invoice.items, invoice.currency)}
                </tbody>
            </table>
            
            <div class="totals">
                <p><strong>Subtotal: {self._format_currency(invoice.subtotal, invoice.currency)}</strong></p>
                <p><strong>Tax: {self._format_currency(invoice.total_tax, invoice.currency)}</strong></p>
                <p><strong>Total: {self._format_currency(invoice.total_amount, invoice.currency)}</strong></p>
            </div>
            
            {f'<div class="notes"><h4>Notes:</h4><p>{invoice.notes}</p></div>' if invoice.notes else ''}
            {f'<div class="terms"><h4>Terms:</h4><p>{invoice.terms}</p></div>' if invoice.terms else ''}
            
            <div class="footer">
                <p>{template_config['footer']}</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def _format_address(self, address: Dict[str, str]) -> str:
        """Format address for display"""
        if not address:
            return ""
        
        parts = []
        if address.get("street"):
            parts.append(f"<p>{address['street']}</p>")
        if address.get("city") or address.get("state") or address.get("zip"):
            city_line = ", ".join(filter(None, [
                address.get("city"),
                address.get("state"),
                address.get("zip")
            ]))
            if city_line:
                parts.append(f"<p>{city_line}</p>")
        if address.get("country"):
            parts.append(f"<p>{address['country']}</p>")
        
        return "".join(parts)

    def _format_invoice_items(self, items: List[InvoiceItem], currency: str) -> str:
        """Format invoice items as HTML table rows"""
        rows = []
        
        for item in items:
            row = f"""
            <tr>
                <td>{item.description}</td>
                <td>{item.quantity}</td>
                <td>{self._format_currency(item.unit_price, currency)}</td>
                <td>{item.tax_rate}%</td>
                <td>{self._format_currency(item.total, currency)}</td>
            </tr>
            """
            rows.append(row)
        
        return "".join(rows)

    def _format_currency(self, amount: Decimal, currency: str) -> str:
        """Format currency amount"""
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥"
        }
        
        symbol = symbols.get(currency, currency)
        return f"{symbol}{amount:.2f}"

    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF (placeholder)"""
        # In production, would use library like weasyprint or pdfkit
        return html_content.encode('utf-8')

    async def update_invoice_status(self, invoice_id: str, status: InvoiceStatus):
        """Update invoice status"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        old_status = invoice.status
        invoice.status = status
        
        logger.info(f"Updated invoice {invoice.invoice_number} status: {old_status.value} -> {status.value}")

    async def send_invoice(self, invoice_id: str, recipient_email: str = None) -> bool:
        """Send invoice to customer"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        try:
            # Generate PDF
            pdf_content = await self.generate_invoice_pdf(invoice_id)
            
            # Send email (placeholder)
            email = recipient_email or invoice.customer_details.get("email")
            if not email:
                raise ValueError("No recipient email available")
            
            # In production, would integrate with email service
            logger.info(f"Sending invoice {invoice.invoice_number} to {email}")
            
            # Update status
            await self.update_invoice_status(invoice_id, InvoiceStatus.SENT)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send invoice: {str(e)}")
            return False

    async def process_payment(
        self,
        invoice_id: str,
        payment_amount: Decimal,
        payment_method: str,
        transaction_id: str
    ) -> bool:
        """Process payment for invoice"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        try:
            # Validate payment amount
            if payment_amount != invoice.total_amount:
                logger.warning(f"Payment amount mismatch for invoice {invoice.invoice_number}")
            
            # Update invoice
            invoice.metadata.update({
                "payment_amount": str(payment_amount),
                "payment_method": payment_method,
                "transaction_id": transaction_id,
                "payment_date": datetime.utcnow().isoformat()
            })
            
            # Update status
            await self.update_invoice_status(invoice_id, InvoiceStatus.PAID)
            
            logger.info(f"Payment processed for invoice {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process payment: {str(e)}")
            return False

    async def get_overdue_invoices(self) -> List[Invoice]:
        """Get overdue invoices"""
        
        overdue = []
        current_date = datetime.utcnow()
        
        for invoice in self.invoices.values():
            if (invoice.status in [InvoiceStatus.SENT, InvoiceStatus.PENDING] and
                invoice.due_date < current_date):
                
                # Update status to overdue
                invoice.status = InvoiceStatus.OVERDUE
                overdue.append(invoice)
        
        return overdue

    async def calculate_late_fees(self, invoice_id: str) -> Decimal:
        """Calculate late fees for overdue invoice"""
        
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")
        
        if invoice.status != InvoiceStatus.OVERDUE:
            return Decimal("0.00")
        
        # Calculate months overdue
        days_overdue = (datetime.utcnow() - invoice.due_date).days
        months_overdue = max(1, days_overdue // 30)
        
        # Calculate late fee
        late_fee_rate = self.config["late_fee_rate"]
        late_fee = invoice.total_amount * (late_fee_rate / 100) * months_overdue
        
        return late_fee

    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID"""
        return self.invoices.get(invoice_id)

    def list_invoices(
        self,
        customer_id: Optional[str] = None,
        status: Optional[InvoiceStatus] = None,
        limit: int = 100
    ) -> List[Invoice]:
        """List invoices with filters"""
        
        invoices = list(self.invoices.values())
        
        # Apply filters
        if customer_id:
            invoices = [inv for inv in invoices if inv.customer_id == customer_id]
        
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        
        # Sort by creation date (newest first)
        invoices.sort(key=lambda x: x.created_at, reverse=True)
        
        return invoices[:limit]

    async def health_check(self) -> bool:
        """Health check for invoice generator"""
        try:
            # Test invoice creation
            test_items = [{
                "description": "Test Item",
                "quantity": 1,
                "unit_price": "10.00"
            }]
            
            invoice_id = await self.create_invoice(
                customer_id="test_customer",
                customer_details={"name": "Test Customer"},
                items=test_items
            )
            
            # Clean up test invoice
            self.invoices.pop(invoice_id, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Invoice generator health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "InvoiceGeneratorCore", "Invoice", "InvoiceItem", 
    "InvoiceStatus", "InvoiceType"
]

logger.info("📄 Invoice Generator Core module loaded")