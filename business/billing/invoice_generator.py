"""
Invoice Generator Engine - Automated billing and invoice generation system
==========================================================================

Advanced invoice generation system with AI-powered billing automation,
multi-currency support, and compliance with international tax regulations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class InvoiceStatus(Enum):
    """Invoice status types"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceType(Enum):
    """Invoice types"""
    STANDARD = "standard"
    RECURRING = "recurring"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    SUBSCRIPTION = "subscription"
    LICENSING = "licensing"

@dataclass
class InvoiceLineItem:
    """Individual line item on invoice"""
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    total: Decimal
    category: str
    content_id: Optional[str] = None

@dataclass
class InvoiceData:
    """Invoice data structure"""
    invoice_id: str
    customer_id: str
    invoice_number: str
    invoice_type: InvoiceType
    status: InvoiceStatus
    issue_date: datetime
    due_date: datetime
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    line_items: List[InvoiceLineItem]
    payment_terms: str
    notes: Optional[str] = None

class InvoiceGeneratorEngine:
    """
    Advanced invoice generation system with AI-powered billing automation
    for multi-format content creators and monetization platforms.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize invoice generator engine"""
        try:
            await self._setup_database_tables()
            await self._load_tax_configurations()
            logger.info("Invoice Generator Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Invoice Generator Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for invoice management"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id SERIAL PRIMARY KEY,
                    invoice_id VARCHAR(100) UNIQUE NOT NULL,
                    invoice_number VARCHAR(50) UNIQUE NOT NULL,
                    customer_id VARCHAR(255) NOT NULL,
                    invoice_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    subtotal DECIMAL(15,2) NOT NULL,
                    tax_amount DECIMAL(15,2) NOT NULL,
                    total_amount DECIMAL(15,2) NOT NULL,
                    payment_terms TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    paid_at TIMESTAMP,
                    INDEX idx_invoices_customer (customer_id, status),
                    INDEX idx_invoices_status (status, due_date)
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS invoice_line_items (
                    id SERIAL PRIMARY KEY,
                    invoice_id VARCHAR(100) REFERENCES invoices(invoice_id),
                    description TEXT NOT NULL,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit_price DECIMAL(15,2) NOT NULL,
                    tax_rate DECIMAL(5,4) NOT NULL,
                    total DECIMAL(15,2) NOT NULL,
                    category VARCHAR(50),
                    content_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def _load_tax_configurations(self) -> None:
        """Load tax configurations from database"""
        try:
            # Cache tax rates by country/region
            tax_rates = {
                'US': 0.0875,  # Average US sales tax
                'GB': 0.20,    # UK VAT
                'FR': 0.20,    # French VAT
                'DE': 0.19,    # German VAT
                'ES': 0.21,    # Spanish VAT
                'IT': 0.22,    # Italian VAT
                'CA': 0.13,    # Canadian GST/HST
                'AU': 0.10,    # Australian GST
                'JP': 0.10,    # Japanese consumption tax
                'BR': 0.17     # Brazilian ICMS
            }
            
            # Store in Redis for fast access
            for country, rate in tax_rates.items():
                self.redis.setex(f"tax_rate_{country}", 3600, str(rate))
                
        except Exception as e:
            logger.error(f"Failed to load tax configurations: {e}")

    async def generate_invoice(self, customer_id: str, invoice_type: InvoiceType,
                             line_items: List[Dict[str, Any]], 
                             payment_terms: str = "Net 30") -> InvoiceData:
        """Generate new invoice with automatic calculations"""
        try:
            # Generate unique invoice number
            invoice_number = await self._generate_invoice_number(invoice_type)
            invoice_id = f"inv_{customer_id}_{int(datetime.now().timestamp())}"
            
            # Get customer details for tax calculation
            customer_data = await self._get_customer_data(customer_id)
            tax_region = customer_data.get('tax_region', 'US')
            
            # Process line items with tax calculations
            processed_items = []
            subtotal = Decimal('0.00')
            
            for item_data in line_items:
                line_item = await self._process_line_item(item_data, tax_region)
                processed_items.append(line_item)
                subtotal += line_item.total
            
            # Calculate tax amount
            tax_rate = await self._get_tax_rate(tax_region)
            tax_amount = subtotal * Decimal(str(tax_rate))
            total_amount = subtotal + tax_amount
            
            # Create invoice data
            invoice_data = InvoiceData(
                invoice_id=invoice_id,
                customer_id=customer_id,
                invoice_number=invoice_number,
                invoice_type=invoice_type,
                status=InvoiceStatus.DRAFT,
                issue_date=datetime.now().date(),
                due_date=self._calculate_due_date(payment_terms),
                currency=customer_data.get('currency', 'USD'),
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                line_items=processed_items,
                payment_terms=payment_terms,
                notes=None
            )
            
            # Store invoice in database
            await self._store_invoice(invoice_data)
            
            # Generate PDF and send notifications if needed
            if invoice_type != InvoiceType.STANDARD:
                await self._generate_invoice_pdf(invoice_data)
                await self._send_invoice_notification(invoice_data)
            
            logger.info(f"Generated invoice {invoice_number} for customer {customer_id}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Failed to generate invoice: {e}")
            raise HTTPException(status_code=500, detail="Invoice generation failed")

    async def _generate_invoice_number(self, invoice_type: InvoiceType) -> str:
        """Generate unique invoice number"""
        try:
            # Get current year and month
            now = datetime.now()
            prefix = {
                InvoiceType.STANDARD: "INV",
                InvoiceType.RECURRING: "REC", 
                InvoiceType.COMMISSION: "COM",
                InvoiceType.ROYALTY: "ROY",
                InvoiceType.SUBSCRIPTION: "SUB",
                InvoiceType.LICENSING: "LIC"
            }[invoice_type]
            
            # Get sequence number from Redis
            key = f"invoice_seq_{prefix}_{now.year}_{now.month:02d}"
            sequence = self.redis.incr(key)
            self.redis.expire(key, 2678400)  # 31 days
            
            return f"{prefix}-{now.year}{now.month:02d}-{sequence:06d}"
            
        except Exception as e:
            logger.error(f"Failed to generate invoice number: {e}")
            raise

    async def _get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Get customer data for tax and billing purposes"""
        try:
            async with self.db_pool.acquire() as conn:
                customer = await conn.fetchrow("""
                    SELECT 
                        customer_id,
                        country_code,
                        tax_region,
                        currency,
                        billing_address,
                        tax_id,
                        company_name
                    FROM customers 
                    WHERE customer_id = $1
                """, customer_id)
                
                if not customer:
                    # Create default customer profile
                    await conn.execute("""
                        INSERT INTO customers 
                        (customer_id, country_code, tax_region, currency)
                        VALUES ($1, 'US', 'US', 'USD')
                    """, customer_id)
                    
                    return {
                        'customer_id': customer_id,
                        'country_code': 'US',
                        'tax_region': 'US',
                        'currency': 'USD'
                    }
                
                return dict(customer)
                
        except Exception as e:
            logger.error(f"Failed to get customer data: {e}")
            return {
                'customer_id': customer_id,
                'country_code': 'US',
                'tax_region': 'US',
                'currency': 'USD'
            }

    async def _process_line_item(self, item_data: Dict[str, Any], tax_region: str) -> InvoiceLineItem:
        """Process individual line item with tax calculations"""
        try:
            quantity = Decimal(str(item_data['quantity']))
            unit_price = Decimal(str(item_data['unit_price']))
            tax_rate = await self._get_tax_rate(tax_region)
            
            # Calculate totals
            line_total = quantity * unit_price
            
            return InvoiceLineItem(
                description=item_data['description'],
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=Decimal(str(tax_rate)),
                total=line_total,
                category=item_data.get('category', 'service'),
                content_id=item_data.get('content_id')
            )
            
        except Exception as e:
            logger.error(f"Failed to process line item: {e}")
            raise

    async def _get_tax_rate(self, tax_region: str) -> float:
        """Get tax rate for specific region"""
        try:
            cached_rate = self.redis.get(f"tax_rate_{tax_region}")
            if cached_rate:
                return float(cached_rate)
            
            # Default fallback
            return 0.0875  # 8.75% default
            
        except Exception as e:
            logger.error(f"Failed to get tax rate: {e}")
            return 0.0

    def _calculate_due_date(self, payment_terms: str) -> datetime.date:
        """Calculate due date based on payment terms"""
        now = datetime.now().date()
        
        if payment_terms == "Net 30":
            return now + timedelta(days=30)
        elif payment_terms == "Net 15":
            return now + timedelta(days=15)
        elif payment_terms == "Net 7":
            return now + timedelta(days=7)
        elif payment_terms == "Due on receipt":
            return now
        else:
            return now + timedelta(days=30)  # Default to Net 30

    async def _store_invoice(self, invoice_data: InvoiceData) -> None:
        """Store invoice and line items in database"""
        try:
            async with self.db_pool.acquire() as conn:
                # Insert main invoice record
                await conn.execute("""
                    INSERT INTO invoices 
                    (invoice_id, invoice_number, customer_id, invoice_type, status,
                     issue_date, due_date, currency, subtotal, tax_amount, total_amount,
                     payment_terms, notes)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                invoice_data.invoice_id,
                invoice_data.invoice_number,
                invoice_data.customer_id,
                invoice_data.invoice_type.value,
                invoice_data.status.value,
                invoice_data.issue_date,
                invoice_data.due_date,
                invoice_data.currency,
                invoice_data.subtotal,
                invoice_data.tax_amount,
                invoice_data.total_amount,
                invoice_data.payment_terms,
                invoice_data.notes
                )
                
                # Insert line items
                for item in invoice_data.line_items:
                    await conn.execute("""
                        INSERT INTO invoice_line_items 
                        (invoice_id, description, quantity, unit_price, tax_rate,
                         total, category, content_id)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    invoice_data.invoice_id,
                    item.description,
                    item.quantity,
                    item.unit_price,
                    item.tax_rate,
                    item.total,
                    item.category,
                    item.content_id
                    )
                    
        except Exception as e:
            logger.error(f"Failed to store invoice: {e}")
            raise

    async def _generate_invoice_pdf(self, invoice_data: InvoiceData) -> str:
        """Generate PDF invoice document"""
        try:
            # This would integrate with a PDF generation service
            # For now, return placeholder path
            pdf_path = f"/invoices/{invoice_data.invoice_number}.pdf"
            
            # Store PDF path in cache
            self.redis.setex(
                f"invoice_pdf_{invoice_data.invoice_id}",
                86400,  # 24 hours
                pdf_path
            )
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"Failed to generate invoice PDF: {e}")
            return ""

    async def _send_invoice_notification(self, invoice_data: InvoiceData) -> None:
        """Send invoice notification to customer"""
        try:
            # This would integrate with notification service
            notification_data = {
                'customer_id': invoice_data.customer_id,
                'invoice_number': invoice_data.invoice_number,
                'total_amount': float(invoice_data.total_amount),
                'due_date': invoice_data.due_date.isoformat(),
                'type': 'invoice_generated'
            }
            
            # Queue notification for processing
            self.redis.lpush("invoice_notifications", str(notification_data))
            
        except Exception as e:
            logger.error(f"Failed to send invoice notification: {e}")

    async def get_invoice_by_id(self, invoice_id: str) -> Optional[InvoiceData]:
        """Get invoice by ID"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get main invoice data
                invoice_row = await conn.fetchrow("""
                    SELECT * FROM invoices WHERE invoice_id = $1
                """, invoice_id)
                
                if not invoice_row:
                    return None
                
                # Get line items
                line_items_rows = await conn.fetch("""
                    SELECT * FROM invoice_line_items 
                    WHERE invoice_id = $1 
                    ORDER BY id
                """, invoice_id)
                
                # Convert to objects
                line_items = [
                    InvoiceLineItem(
                        description=row['description'],
                        quantity=row['quantity'],
                        unit_price=row['unit_price'],
                        tax_rate=row['tax_rate'],
                        total=row['total'],
                        category=row['category'],
                        content_id=row['content_id']
                    )
                    for row in line_items_rows
                ]
                
                return InvoiceData(
                    invoice_id=invoice_row['invoice_id'],
                    customer_id=invoice_row['customer_id'],
                    invoice_number=invoice_row['invoice_number'],
                    invoice_type=InvoiceType(invoice_row['invoice_type']),
                    status=InvoiceStatus(invoice_row['status']),
                    issue_date=invoice_row['issue_date'],
                    due_date=invoice_row['due_date'],
                    currency=invoice_row['currency'],
                    subtotal=invoice_row['subtotal'],
                    tax_amount=invoice_row['tax_amount'],
                    total_amount=invoice_row['total_amount'],
                    line_items=line_items,
                    payment_terms=invoice_row['payment_terms'],
                    notes=invoice_row['notes']
                )
                
        except Exception as e:
            logger.error(f"Failed to get invoice: {e}")
            return None

    async def update_invoice_status(self, invoice_id: str, status: InvoiceStatus) -> bool:
        """Update invoice status"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute("""
                    UPDATE invoices 
                    SET status = $1, updated_at = NOW()
                    WHERE invoice_id = $2
                """, status.value, invoice_id)
                
                # Mark as paid if status is PAID
                if status == InvoiceStatus.PAID:
                    await conn.execute("""
                        UPDATE invoices 
                        SET paid_at = NOW()
                        WHERE invoice_id = $1
                    """, invoice_id)
                
                return result == "UPDATE 1"
                
        except Exception as e:
            logger.error(f"Failed to update invoice status: {e}")
            return False

    async def get_overdue_invoices(self) -> List[InvoiceData]:
        """Get all overdue invoices"""
        try:
            async with self.db_pool.acquire() as conn:
                overdue_rows = await conn.fetch("""
                    SELECT invoice_id FROM invoices 
                    WHERE status IN ('sent', 'pending') 
                    AND due_date < CURRENT_DATE
                """)
                
                overdue_invoices = []
                for row in overdue_rows:
                    invoice = await self.get_invoice_by_id(row['invoice_id'])
                    if invoice:
                        # Update status to overdue
                        await self.update_invoice_status(invoice.invoice_id, InvoiceStatus.OVERDUE)
                        invoice.status = InvoiceStatus.OVERDUE
                        overdue_invoices.append(invoice)
                
                return overdue_invoices
                
        except Exception as e:
            logger.error(f"Failed to get overdue invoices: {e}")
            return []

    async def get_billing_dashboard_data(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive billing dashboard data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get invoice summary
                summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_invoices,
                        COALESCE(SUM(CASE WHEN status = 'paid' THEN total_amount ELSE 0 END), 0) as paid_amount,
                        COALESCE(SUM(CASE WHEN status IN ('sent', 'pending') THEN total_amount ELSE 0 END), 0) as pending_amount,
                        COALESCE(SUM(CASE WHEN status = 'overdue' THEN total_amount ELSE 0 END), 0) as overdue_amount
                    FROM invoices 
                    WHERE customer_id = $1
                    AND issue_date >= CURRENT_DATE - INTERVAL '12 months'
                """, customer_id)
                
                # Get recent invoices
                recent_invoices = await conn.fetch("""
                    SELECT invoice_id, invoice_number, status, total_amount, due_date
                    FROM invoices 
                    WHERE customer_id = $1
                    ORDER BY issue_date DESC 
                    LIMIT 10
                """, customer_id)
                
                # Get monthly billing trends
                monthly_trends = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', issue_date) as month,
                        COUNT(*) as invoice_count,
                        SUM(total_amount) as total_billed
                    FROM invoices 
                    WHERE customer_id = $1
                    AND issue_date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', issue_date)
                    ORDER BY month DESC
                """, customer_id)
                
                return {
                    'customer_id': customer_id,
                    'summary': {
                        'total_invoices': int(summary['total_invoices']) if summary else 0,
                        'paid_amount': float(summary['paid_amount']) if summary else 0,
                        'pending_amount': float(summary['pending_amount']) if summary else 0,
                        'overdue_amount': float(summary['overdue_amount']) if summary else 0
                    },
                    'recent_invoices': [
                        {
                            'invoice_id': inv['invoice_id'],
                            'invoice_number': inv['invoice_number'],
                            'status': inv['status'],
                            'total_amount': float(inv['total_amount']),
                            'due_date': inv['due_date'].isoformat()
                        }
                        for inv in recent_invoices
                    ],
                    'monthly_trends': [
                        {
                            'month': trend['month'].strftime('%Y-%m'),
                            'invoice_count': int(trend['invoice_count']),
                            'total_billed': float(trend['total_billed'])
                        }
                        for trend in monthly_trends
                    ],
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get billing dashboard data: {e}")
            raise HTTPException(status_code=500, detail="Billing dashboard data retrieval failed")
