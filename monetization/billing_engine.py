"""Automated Billing Engine
Advanced billing automation system with intelligent retry logic and compliance features.

Author: Fahed Mlaiel <mlaiel@live.de>
⚠️ COPYRIGHT WARNING: Proprietary code - unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class InvoiceStatus(Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentAttemptStatus(Enum):
    """Payment attempt status."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class TaxType(Enum):
    """Tax type enumeration."""
    VAT = "vat"
    SALES_TAX = "sales_tax"
    GST = "gst"
    HST = "hst"
    EXEMPT = "exempt"


@dataclass
class TaxRate:
    """Tax rate configuration."""
    country_code: str
    region: Optional[str]
    tax_type: TaxType
    rate: Decimal
    description: str
    effective_date: datetime
    is_active: bool = True


@dataclass
class InvoiceLineItem:
    """Invoice line item."""
    description: str
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    tax_rate: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Invoice:
    """Invoice data structure."""
    invoice_id: str
    subscription_id: str
    user_id: str
    invoice_number: str
    status: InvoiceStatus
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    line_items: List[InvoiceLineItem]
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: datetime
    issued_date: datetime
    paid_date: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    tax_rates: List[TaxRate] = None
    billing_address: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class PaymentAttempt:
    """Payment attempt tracking."""
    attempt_id: str
    invoice_id: str
    payment_method_id: str
    amount: Decimal
    currency: str
    status: PaymentAttemptStatus
    error_message: Optional[str] = None
    payment_provider: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    attempted_at: datetime = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.attempted_at is None:
            self.attempted_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BillingSchedule:
    """Billing schedule configuration."""
    subscription_id: str
    next_billing_date: datetime
    retry_schedule: List[datetime]
    dunning_schedule: List[datetime]
    max_retry_attempts: int = 3
    grace_period_days: int = 3
    is_active: bool = True


class BillingEngine:
    """Advanced automated billing engine."""

    def __init__(self):
        """Initialize billing engine."""
        try:
            logger.info("Initializing BillingEngine")
            
            # Storage (in production, use database)
            self.invoices: Dict[str, Invoice] = {}
            self.payment_attempts: Dict[str, List[PaymentAttempt]] = {}
            self.billing_schedules: Dict[str, BillingSchedule] = {}
            self.tax_rates: Dict[str, List[TaxRate]] = {}
            
            # Configuration
            self.invoice_number_prefix = "INV"
            self.invoice_counter = 100000
            self.payment_terms_days = 30
            self.dunning_enabled = True
            self.auto_retry_enabled = True
            
            # Retry configuration
            self.retry_schedule = [
                1,    # 1 day after failure
                3,    # 3 days after failure
                7,    # 7 days after failure
                14,   # 14 days after failure
                21    # 21 days after failure (final attempt)
            ]
            
            # Dunning configuration
            self.dunning_schedule = [
                7,    # 7 days after due date
                14,   # 14 days after due date
                21,   # 21 days after due date
                30    # 30 days after due date (final notice)
            ]
            
            # Initialize tax rates
            self._initialize_tax_rates()
            
            # Supported currencies for billing
            self.supported_currencies = [
                "EUR", "USD", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK",
                "PLN", "CZK", "HUF", "BGN", "RON", "HRK", "BRL", "MXN", "ARS", "CLP"
            ]
            
            logger.info("BillingEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"BillingEngine initialization failed: {e}")
            raise

    def _initialize_tax_rates(self):
        """Initialize standard tax rates for different countries."""
        try:
            standard_tax_rates = [
                TaxRate("DE", None, TaxType.VAT, Decimal("19.00"), "German VAT", datetime.utcnow()),
                TaxRate("FR", None, TaxType.VAT, Decimal("20.00"), "French VAT", datetime.utcnow()),
                TaxRate("GB", None, TaxType.VAT, Decimal("20.00"), "UK VAT", datetime.utcnow()),
                TaxRate("US", "CA", TaxType.SALES_TAX, Decimal("7.25"), "California Sales Tax", datetime.utcnow()),
                TaxRate("US", "NY", TaxType.SALES_TAX, Decimal("8.00"), "New York Sales Tax", datetime.utcnow()),
                TaxRate("US", "TX", TaxType.SALES_TAX, Decimal("6.25"), "Texas Sales Tax", datetime.utcnow()),
                TaxRate("CA", "ON", TaxType.HST, Decimal("13.00"), "Ontario HST", datetime.utcnow()),
                TaxRate("CA", "BC", TaxType.GST, Decimal("12.00"), "BC PST + GST", datetime.utcnow()),
                TaxRate("AU", None, TaxType.GST, Decimal("10.00"), "Australian GST", datetime.utcnow()),
                TaxRate("JP", None, TaxType.VAT, Decimal("10.00"), "Japanese Consumption Tax", datetime.utcnow()),
                TaxRate("CH", None, TaxType.VAT, Decimal("7.70"), "Swiss VAT", datetime.utcnow()),
                TaxRate("SE", None, TaxType.VAT, Decimal("25.00"), "Swedish VAT", datetime.utcnow()),
                TaxRate("NO", None, TaxType.VAT, Decimal("25.00"), "Norwegian VAT", datetime.utcnow()),
                TaxRate("DK", None, TaxType.VAT, Decimal("25.00"), "Danish VAT", datetime.utcnow()),
            ]
            
            for tax_rate in standard_tax_rates:
                country_key = f"{tax_rate.country_code}_{tax_rate.region or 'default'}"
                if country_key not in self.tax_rates:
                    self.tax_rates[country_key] = []
                self.tax_rates[country_key].append(tax_rate)
                
            logger.info(f"Initialized {len(standard_tax_rates)} tax rates")
            
        except Exception as e:
            logger.error(f"Error initializing tax rates: {e}")

    async def create_invoice(
        self,
        subscription_id: str,
        user_id: str,
        line_items: List[InvoiceLineItem],
        billing_period_start: datetime,
        billing_period_end: datetime,
        billing_address: Optional[Dict[str, str]] = None,
        currency: str = "EUR",
        payment_method_id: Optional[str] = None
    ) -> Invoice:
        """Create a new invoice for a subscription."""
        try:
            invoice_id = str(uuid.uuid4())
            invoice_number = f"{self.invoice_number_prefix}-{self.invoice_counter:06d}"
            self.invoice_counter += 1
            
            # Calculate subtotal
            subtotal = sum(item.total_amount for item in line_items)
            
            # Calculate tax
            tax_amount, applicable_tax_rates = await self._calculate_tax(
                subtotal, billing_address, currency
            )
            
            # Update line items with tax information
            for item in line_items:
                if applicable_tax_rates:
                    tax_rate = applicable_tax_rates[0].rate  # Use first applicable rate
                    item.tax_rate = tax_rate
                    item.tax_amount = (item.total_amount * tax_rate) / Decimal('100')
            
            total_amount = subtotal + tax_amount
            
            # Set due date
            issued_date = datetime.utcnow()
            due_date = issued_date + timedelta(days=self.payment_terms_days)
            
            # Create invoice
            invoice = Invoice(
                invoice_id=invoice_id,
                subscription_id=subscription_id,
                user_id=user_id,
                invoice_number=invoice_number,
                status=InvoiceStatus.DRAFT,
                currency=currency,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                line_items=line_items,
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                due_date=due_date,
                issued_date=issued_date,
                payment_method_id=payment_method_id,
                tax_rates=applicable_tax_rates,
                billing_address=billing_address
            )
            
            # Store invoice
            self.invoices[invoice_id] = invoice
            
            logger.info(f"Created invoice {invoice_number} for subscription {subscription_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            raise

    async def send_invoice(self, invoice_id: str) -> bool:
        """Send invoice to customer."""
        try:
            if invoice_id not in self.invoices:
                raise ValueError(f"Invoice {invoice_id} not found")
                
            invoice = self.invoices[invoice_id]
            
            # Update status
            invoice.status = InvoiceStatus.SENT
            invoice.updated_at = datetime.utcnow()
            
            # In production, this would integrate with email service
            # For now, we'll simulate sending
            
            # Schedule automatic payment attempt if payment method is available
            if invoice.payment_method_id and self.auto_retry_enabled:
                await self._schedule_payment_attempt(invoice)
                
            # Create billing schedule
            await self._create_billing_schedule(invoice)
            
            logger.info(f"Sent invoice {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            return False

    async def process_payment(
        self,
        invoice_id: str,
        payment_method_id: str,
        payment_provider: str = "stripe"
    ) -> PaymentAttempt:
        """Process payment for an invoice."""
        try:
            if invoice_id not in self.invoices:
                raise ValueError(f"Invoice {invoice_id} not found")
                
            invoice = self.invoices[invoice_id]
            attempt_id = str(uuid.uuid4())
            
            # Create payment attempt
            attempt = PaymentAttempt(
                attempt_id=attempt_id,
                invoice_id=invoice_id,
                payment_method_id=payment_method_id,
                amount=invoice.total_amount,
                currency=invoice.currency,
                status=PaymentAttemptStatus.PENDING,
                payment_provider=payment_provider
            )
            
            # Store attempt
            if invoice_id not in self.payment_attempts:
                self.payment_attempts[invoice_id] = []
            self.payment_attempts[invoice_id].append(attempt)
            
            # Simulate payment processing
            # In production, this would integrate with payment providers
            payment_success = await self._simulate_payment_processing(attempt)
            
            if payment_success:
                attempt.status = PaymentAttemptStatus.SUCCESS
                attempt.completed_at = datetime.utcnow()
                attempt.provider_transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
                
                # Update invoice
                invoice.status = InvoiceStatus.PAID
                invoice.paid_date = datetime.utcnow()
                invoice.updated_at = datetime.utcnow()
                
                logger.info(f"Payment successful for invoice {invoice.invoice_number}")
            else:
                attempt.status = PaymentAttemptStatus.FAILED
                attempt.error_message = "Payment declined by provider"
                
                # Schedule retry if enabled
                if self.auto_retry_enabled:
                    await self._schedule_payment_retry(invoice)
                    
                logger.warning(f"Payment failed for invoice {invoice.invoice_number}")
                
            return attempt
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise

    async def _simulate_payment_processing(self, attempt: PaymentAttempt) -> bool:
        """Simulate payment processing (replace with real payment provider integration)."""
        try:
            # Simulate processing delay
            await asyncio.sleep(0.1)
            
            # Simulate 85% success rate
            import random
            return random.random() < 0.85
            
        except Exception as e:
            logger.error(f"Error in payment simulation: {e}")
            return False

    async def _calculate_tax(
        self,
        amount: Decimal,
        billing_address: Optional[Dict[str, str]],
        currency: str
    ) -> Tuple[Decimal, List[TaxRate]]:
        """Calculate tax amount and return applicable rates."""
        try:
            if not billing_address:
                return Decimal('0.00'), []
                
            country_code = billing_address.get('country', '').upper()
            region = billing_address.get('region', '').upper()
            
            # Look for specific region rate first, then country default
            tax_key = f"{country_code}_{region}"
            if tax_key not in self.tax_rates:
                tax_key = f"{country_code}_default"
                
            if tax_key not in self.tax_rates:
                return Decimal('0.00'), []  # No tax for unknown locations
                
            applicable_rates = [
                rate for rate in self.tax_rates[tax_key]
                if rate.is_active and rate.effective_date <= datetime.utcnow()
            ]
            
            if not applicable_rates:
                return Decimal('0.00'), []
                
            # Use the most recent rate
            latest_rate = max(applicable_rates, key=lambda x: x.effective_date)
            tax_amount = (amount * latest_rate.rate) / Decimal('100')
            
            return tax_amount, [latest_rate]
            
        except Exception as e:
            logger.error(f"Error calculating tax: {e}")
            return Decimal('0.00'), []

    async def _schedule_payment_attempt(self, invoice: Invoice):
        """Schedule automatic payment attempt."""
        try:
            # In production, this would use a job queue like Celery
            # For now, we'll simulate immediate attempt
            if invoice.payment_method_id:
                await self.process_payment(
                    invoice.invoice_id,
                    invoice.payment_method_id
                )
                
        except Exception as e:
            logger.error(f"Error scheduling payment attempt: {e}")

    async def _schedule_payment_retry(self, invoice: Invoice):
        """Schedule payment retry attempts."""
        try:
            current_attempts = len(self.payment_attempts.get(invoice.invoice_id, []))
            
            if current_attempts < len(self.retry_schedule):
                retry_days = self.retry_schedule[current_attempts]
                retry_date = datetime.utcnow() + timedelta(days=retry_days)
                
                # Store retry schedule
                if invoice.subscription_id in self.billing_schedules:
                    schedule = self.billing_schedules[invoice.subscription_id]
                    schedule.retry_schedule.append(retry_date)
                    
                logger.info(f"Scheduled payment retry for invoice {invoice.invoice_number} in {retry_days} days")
                
        except Exception as e:
            logger.error(f"Error scheduling payment retry: {e}")

    async def _create_billing_schedule(self, invoice: Invoice):
        """Create billing schedule for subscription."""
        try:
            schedule = BillingSchedule(
                subscription_id=invoice.subscription_id,
                next_billing_date=invoice.billing_period_end,
                retry_schedule=[],
                dunning_schedule=[]
            )
            
            # Create dunning schedule
            for days in self.dunning_schedule:
                dunning_date = invoice.due_date + timedelta(days=days)
                schedule.dunning_schedule.append(dunning_date)
                
            self.billing_schedules[invoice.subscription_id] = schedule
            
        except Exception as e:
            logger.error(f"Error creating billing schedule: {e}")

    async def process_dunning(self, invoice_id: str) -> bool:
        """Process dunning (overdue payment reminders)."""
        try:
            if invoice_id not in self.invoices:
                return False
                
            invoice = self.invoices[invoice_id]
            
            if invoice.status != InvoiceStatus.SENT or invoice.due_date > datetime.utcnow():
                return False
                
            # Update invoice status to overdue
            invoice.status = InvoiceStatus.OVERDUE
            invoice.updated_at = datetime.utcnow()
            
            # In production, this would send overdue notices
            logger.info(f"Processed dunning for overdue invoice {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing dunning: {e}")
            return False

    async def generate_billing_report(
        self,
        start_date: datetime,
        end_date: datetime,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Generate comprehensive billing report."""
        try:
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "currency": currency,
                "invoice_summary": {
                    "total_invoices": 0,
                    "paid_invoices": 0,
                    "overdue_invoices": 0,
                    "cancelled_invoices": 0
                },
                "revenue_summary": {
                    "gross_revenue": Decimal('0.00'),
                    "net_revenue": Decimal('0.00'),
                    "tax_collected": Decimal('0.00'),
                    "refunds": Decimal('0.00')
                },
                "payment_summary": {
                    "successful_payments": 0,
                    "failed_payments": 0,
                    "success_rate": 0.0,
                    "average_payment_amount": Decimal('0.00')
                },
                "aging_report": {
                    "current": Decimal('0.00'),      # Not due yet
                    "1_30_days": Decimal('0.00'),    # 1-30 days overdue
                    "31_60_days": Decimal('0.00'),   # 31-60 days overdue
                    "61_90_days": Decimal('0.00'),   # 61-90 days overdue
                    "over_90_days": Decimal('0.00')  # Over 90 days overdue
                }
            }
            
            total_payment_amount = Decimal('0.00')
            successful_payments = 0
            failed_payments = 0
            
            for invoice in self.invoices.values():
                # Filter by date range
                if not (start_date <= invoice.issued_date <= end_date):
                    continue
                    
                # Filter by currency
                if invoice.currency != currency:
                    continue
                    
                report["invoice_summary"]["total_invoices"] += 1
                
                # Count by status
                if invoice.status == InvoiceStatus.PAID:
                    report["invoice_summary"]["paid_invoices"] += 1
                    report["revenue_summary"]["gross_revenue"] += invoice.total_amount
                    report["revenue_summary"]["net_revenue"] += invoice.subtotal
                    report["revenue_summary"]["tax_collected"] += invoice.tax_amount
                elif invoice.status == InvoiceStatus.OVERDUE:
                    report["invoice_summary"]["overdue_invoices"] += 1
                elif invoice.status == InvoiceStatus.CANCELLED:
                    report["invoice_summary"]["cancelled_invoices"] += 1
                    
                # Aging analysis
                if invoice.status in [InvoiceStatus.SENT, InvoiceStatus.OVERDUE]:
                    days_overdue = (datetime.utcnow() - invoice.due_date).days
                    
                    if days_overdue <= 0:
                        report["aging_report"]["current"] += invoice.total_amount
                    elif days_overdue <= 30:
                        report["aging_report"]["1_30_days"] += invoice.total_amount
                    elif days_overdue <= 60:
                        report["aging_report"]["31_60_days"] += invoice.total_amount
                    elif days_overdue <= 90:
                        report["aging_report"]["61_90_days"] += invoice.total_amount
                    else:
                        report["aging_report"]["over_90_days"] += invoice.total_amount
                        
                # Payment analysis
                attempts = self.payment_attempts.get(invoice.invoice_id, [])
                for attempt in attempts:
                    if attempt.status == PaymentAttemptStatus.SUCCESS:
                        successful_payments += 1
                        total_payment_amount += attempt.amount
                    elif attempt.status == PaymentAttemptStatus.FAILED:
                        failed_payments += 1
                        
            # Calculate payment metrics
            total_attempts = successful_payments + failed_payments
            if total_attempts > 0:
                report["payment_summary"]["success_rate"] = (
                    successful_payments / total_attempts
                ) * 100
                
            if successful_payments > 0:
                report["payment_summary"]["average_payment_amount"] = (
                    total_payment_amount / successful_payments
                )
                
            report["payment_summary"]["successful_payments"] = successful_payments
            report["payment_summary"]["failed_payments"] = failed_payments
            
            logger.info(f"Generated billing report for period {start_date} to {end_date}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating billing report: {e}")
            return {}

    async def export_invoices_csv(
        self,
        start_date: datetime,
        end_date: datetime,
        file_path: Optional[str] = None
    ) -> str:
        """Export invoices to CSV format."""
        try:
            import csv
            import io
            
            if file_path is None:
                file_path = f"/tmp/invoices_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                
            # Filter invoices by date range
            filtered_invoices = [
                invoice for invoice in self.invoices.values()
                if start_date <= invoice.issued_date <= end_date
            ]
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Invoice Number', 'Customer ID', 'Subscription ID', 'Status',
                'Currency', 'Subtotal', 'Tax Amount', 'Total Amount',
                'Issued Date', 'Due Date', 'Paid Date', 'Billing Period Start',
                'Billing Period End'
            ])
            
            # Write data
            for invoice in filtered_invoices:
                writer.writerow([
                    invoice.invoice_number,
                    invoice.user_id,
                    invoice.subscription_id,
                    invoice.status.value,
                    invoice.currency,
                    float(invoice.subtotal),
                    float(invoice.tax_amount),
                    float(invoice.total_amount),
                    invoice.issued_date.strftime('%Y-%m-%d'),
                    invoice.due_date.strftime('%Y-%m-%d'),
                    invoice.paid_date.strftime('%Y-%m-%d') if invoice.paid_date else '',
                    invoice.billing_period_start.strftime('%Y-%m-%d'),
                    invoice.billing_period_end.strftime('%Y-%m-%d')
                ])
                
            # Write to file
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(output.getvalue())
                
            logger.info(f"Exported {len(filtered_invoices)} invoices to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting invoices to CSV: {e}")
            raise

    async def get_overdue_invoices(self) -> List[Invoice]:
        """Get all overdue invoices."""
        try:
            now = datetime.utcnow()
            overdue_invoices = [
                invoice for invoice in self.invoices.values()
                if invoice.status == InvoiceStatus.SENT and invoice.due_date < now
            ]
            
            # Sort by due date, oldest first
            overdue_invoices.sort(key=lambda x: x.due_date)
            
            return overdue_invoices
            
        except Exception as e:
            logger.error(f"Error getting overdue invoices: {e}")
            return []

    async def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by ID."""
        return self.invoices.get(invoice_id)

    async def get_invoices_by_subscription(self, subscription_id: str) -> List[Invoice]:
        """Get all invoices for a subscription."""
        try:
            subscription_invoices = [
                invoice for invoice in self.invoices.values()
                if invoice.subscription_id == subscription_id
            ]
            
            # Sort by issued date, newest first
            subscription_invoices.sort(key=lambda x: x.issued_date, reverse=True)
            
            return subscription_invoices
            
        except Exception as e:
            logger.error(f"Error getting subscription invoices: {e}")
            return []