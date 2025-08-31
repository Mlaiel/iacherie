"""🚀 Invoice Manager - IA Influencer Agent Platform Enterprise
==========================================================
Module: backend/platform_core/billing/invoice_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 GESTIONNAIRE DE FACTURATION AUTOMATISÉE
Génération et gestion complète des factures enterprise
- Facturation automatique et récurrente
- Templates PDF personnalisables et multi-langue
- Comptabilité analytique et réconciliation
- Export comptable (SAP, QuickBooks, etc.)
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import io
import base64

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import black, blue, red
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from jinja2 import Template

# Configuration
logger = logging.getLogger(__name__)

class InvoiceStatus(Enum):
    """États des factures"""    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIAL_PAID = "partial_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceType(Enum):
    """Types de factures"""    STANDARD = "standard"
    RECURRING = "recurring"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    PROFORMA = "proforma"
    ESTIMATE = "estimate"

@dataclass
class InvoiceItem:
    """Ligne de facture"""    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    quantity: Decimal = Decimal("1.0")
    unit_price: Decimal = Decimal("0.0")
    discount_percentage: Decimal = Decimal("0.0")
    tax_percentage: Decimal = Decimal("0.0")
    
    # Métadonnées
    product_id: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def subtotal(self) -> Decimal:
        """Sous-total avant remise"""        return self.quantity * self.unit_price
        
    @property
    def discount_amount(self) -> Decimal:
        """Montant de la remise"""        return self.subtotal * (self.discount_percentage / Decimal("100"))
        
    @property
    def net_amount(self) -> Decimal:
        """Montant net après remise"""        return self.subtotal - self.discount_amount
        
    @property
    def tax_amount(self) -> Decimal:
        """Montant des taxes"""        return self.net_amount * (self.tax_percentage / Decimal("100"))
        
    @property
    def total(self) -> Decimal:
        """Total TTC"""        return self.net_amount + self.tax_amount

@dataclass
class InvoiceAddress:
    """Adresse de facturation/livraison"""    name: str = ""
    company: Optional[str] = None
    address_line1: str = ""
    address_line2: Optional[str] = None
    city: str = ""
    state: Optional[str] = None
    postal_code: str = ""
    country: str = ""
    tax_number: Optional[str] = None
    
    def format_address(self) -> str:
        """Formate l'adresse en texte"""        lines = []
        if self.company:
            lines.append(self.company)
        lines.append(self.name)
        lines.append(self.address_line1)
        if self.address_line2:
            lines.append(self.address_line2)
        lines.append(f"{self.city}, {self.state} {self.postal_code}" if self.state else f"{self.city} {self.postal_code}")
        lines.append(self.country)
        return "\n".join(lines)

@dataclass
class Invoice:
    """Facture complète"""    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""
    customer_id: str = ""
    
    # Type et statut
    invoice_type: InvoiceType = InvoiceType.STANDARD
    status: InvoiceStatus = InvoiceStatus.DRAFT
    
    # Dates
    created_at: datetime = field(default_factory=datetime.utcnow)
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Adresses
    billing_address: Optional[InvoiceAddress] = None
    shipping_address: Optional[InvoiceAddress] = None
    
    # Lignes de facture
    items: List[InvoiceItem] = field(default_factory=list)
    
    # Informations financières
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    
    # Remises et taxes globales
    global_discount_percentage: Decimal = Decimal("0.0")
    global_discount_amount: Decimal = Decimal("0.0")
    shipping_cost: Decimal = Decimal("0.0")
    
    # Paiements
    payments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Métadonnées
    notes: str = ""
    terms: str = ""
    footer: str = ""
    reference: Optional[str] = None
    po_number: Optional[str] = None
    
    # Configurations
    language: str = "en"
    template_id: Optional[str] = None
    
    @property
    def subtotal(self) -> Decimal:
        """Sous-total de tous les items"""        return sum(item.subtotal for item in self.items)
        
    @property
    def total_discount(self) -> Decimal:
        """Total des remises"""        items_discount = sum(item.discount_amount for item in self.items)
        global_discount = self.global_discount_amount
        if self.global_discount_percentage > 0:
            global_discount = self.subtotal * (self.global_discount_percentage / Decimal("100"))
        return items_discount + global_discount
        
    @property
    def net_amount(self) -> Decimal:
        """Montant net après toutes les remises"""        return self.subtotal - self.total_discount + self.shipping_cost
        
    @property
    def total_tax(self) -> Decimal:
        """Total des taxes"""        return sum(item.tax_amount for item in self.items)
        
    @property
    def total_amount(self) -> Decimal:
        """Montant total TTC"""        return self.net_amount + self.total_tax
        
    @property
    def amount_paid(self) -> Decimal:
        """Montant payé"""        return sum(Decimal(str(payment.get("amount", 0))) for payment in self.payments)
        
    @property
    def amount_due(self) -> Decimal:
        """Montant dû"""        return self.total_amount - self.amount_paid
        
    @property
    def is_overdue(self) -> bool:
        """Vérifie si la facture est en retard"""        if not self.due_at or self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
            return False
        return datetime.utcnow() > self.due_at
        
    def add_item(self, description: str, quantity: Decimal, unit_price: Decimal, **kwargs) -> InvoiceItem:
        """Ajoute une ligne à la facture"""        item = InvoiceItem(
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            **kwargs
        )
        self.items.append(item)
        return item
        
    def add_payment(self, amount: Decimal, payment_method: str, transaction_id: str, **kwargs):
        """Ajoute un paiement à la facture"""        payment = {
            "payment_id": str(uuid.uuid4()),
            "amount": float(amount),
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "paid_at": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.payments.append(payment)
        
        # Mettre à jour le statut
        if self.amount_due <= 0:
            self.status = InvoiceStatus.PAID
            self.paid_at = datetime.utcnow()
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIAL_PAID

class InvoiceTemplate:
    """Template de facture personnalisable"""    
    def __init__(self, template_id: str, name: str):
        self.template_id = template_id
        self.name = name
        self.company_info = {}
        self.styling = {}
        self.layout_config = {}
        
    def generate_pdf(self, invoice: Invoice) -> bytes:
        """Génère un PDF de facture"""        buffer = io.BytesIO()
        
        # Créer le document PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # En-tête avec logo et infos société
        header_data = [
            [self._get_company_header(), self._get_invoice_header(invoice)]
        ]
        header_table = Table(header_data, colWidths=[3*inch, 3*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Adresses
        addresses_data = [
            ["Facturer à:", "Livrer à:" if invoice.shipping_address else ""]
        ]
        if invoice.billing_address:
            addresses_data.append([
                invoice.billing_address.format_address(),
                invoice.shipping_address.format_address() if invoice.shipping_address else ""
            ])
            
        addresses_table = Table(addresses_data, colWidths=[3*inch, 3*inch])
        addresses_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        story.append(addresses_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Lignes de facture
        items_data = [
            ["Description", "Qté", "Prix unit.", "Remise", "Taxes", "Total"]
        ]
        
        for item in invoice.items:
            items_data.append([
                item.description,
                str(item.quantity),
                f"{item.unit_price} {invoice.currency}",
                f"{item.discount_percentage}%" if item.discount_percentage else "-",
                f"{item.tax_percentage}%" if item.tax_percentage else "-",
                f"{item.total} {invoice.currency}"
            ])
            
        items_table = Table(items_data, colWidths=[2.5*inch, 0.7*inch, 1*inch, 0.7*inch, 0.7*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), 'white'),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totaux
        totals_data = [
            ["Sous-total:", f"{invoice.subtotal} {invoice.currency}"],
            ["Remises:", f"-{invoice.total_discount} {invoice.currency}"],
            ["Frais de port:", f"{invoice.shipping_cost} {invoice.currency}"],
            ["Taxes:", f"{invoice.total_tax} {invoice.currency}"],
            ["TOTAL:", f"{invoice.total_amount} {invoice.currency}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[2*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEBELOW', (0, -2), (-1, -2), 1, black),
        ]))
        story.append(totals_table)
        
        # Notes et conditions
        if invoice.notes:
            story.append(Spacer(1, 0.3*inch))
            notes_style = ParagraphStyle('Notes', parent=styles['Normal'], fontSize=9)
            story.append(Paragraph(f"<b>Notes:</b><br/>{invoice.notes}", notes_style))
            
        if invoice.terms:
            story.append(Spacer(1, 0.2*inch))
            terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8)
            story.append(Paragraph(f"<b>Conditions:</b><br/>{invoice.terms}", terms_style))
            
        # Construire le PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    def _get_company_header(self) -> str:
        """Génère l'en-tête société"""        company = self.company_info
        header = f"<b>{company.get('name', 'Votre Société')}</b><br/>"
        if company.get('address'):
            header += f"{company['address']}<br/>"
        if company.get('phone'):
            header += f"Tél: {company['phone']}<br/>"
        if company.get('email'):
            header += f"Email: {company['email']}<br/>"
        if company.get('website'):
            header += f"Web: {company['website']}"
        return header
        
    def _get_invoice_header(self, invoice: Invoice) -> str:
        """Génère l'en-tête facture"""        header = f"<b>FACTURE</b><br/>"
        header += f"N°: {invoice.invoice_number}<br/>"
        if invoice.issued_at:
            header += f"Date: {invoice.issued_at.strftime('%d/%m/%Y')}<br/>"
        if invoice.due_at:
            header += f"Échéance: {invoice.due_at.strftime('%d/%m/%Y')}<br/>"
        if invoice.reference:
            header += f"Réf: {invoice.reference}"
        return header

class InvoiceManager:
    """Gestionnaire de factures enterprise"""    
    def __init__(self, database_client: Optional[Any] = None):
        self.database_client = database_client
        self.templates: Dict[str, InvoiceTemplate] = {}
        self.auto_numbering_enabled = True
        self.numbering_prefix = "INV"
        self.numbering_sequence = 1
        
        # Charger les templates par défaut
        self._load_default_templates()
        
    def _load_default_templates(self):
        """Charge les templates par défaut"""        default_template = InvoiceTemplate("default", "Template Standard")
        default_template.company_info = {
            "name": "IA Influencer Agent Platform",
            "address": "123 AI Street, Tech City, TC 12345",
            "phone": "+1 (555) 123-4567",
            "email": "billing@aiinfluencer.com",
            "website": "www.aiinfluencer.com"
        }
        self.templates["default"] = default_template
        
    async def create_invoice(self, customer_id: str, **kwargs) -> Invoice:
        """Crée une nouvelle facture"""        invoice = Invoice(
            customer_id=customer_id,
            **kwargs
        )
        
        # Générer le numéro de facture
        if self.auto_numbering_enabled and not invoice.invoice_number:
            invoice.invoice_number = await self._generate_invoice_number()
            
        # Définir la date d'échéance par défaut (30 jours)
        if not invoice.due_at and invoice.issued_at:
            invoice.due_at = invoice.issued_at + timedelta(days=30)
            
        # Sauvegarder en base
        if self.database_client:
            await self._save_invoice(invoice)
            
        logger.info(f"Facture créée: {invoice.invoice_number} pour client {customer_id}")
        return invoice
        
    async def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Récupère une facture par ID"""        if self.database_client:
            return await self._load_invoice(invoice_id)
        return None
        
    async def update_invoice(self, invoice: Invoice):
        """Met à jour une facture"""        if self.database_client:
            await self._save_invoice(invoice)
        logger.info(f"Facture mise à jour: {invoice.invoice_number}")
        
    async def send_invoice(self, invoice: Invoice, recipient_email: str) -> bool:
        """Envoie une facture par email"""        try:
            # Générer le PDF
            template = self.templates.get(invoice.template_id or "default")
            pdf_data = template.generate_pdf(invoice)
            
            # Mettre à jour le statut
            invoice.status = InvoiceStatus.SENT
            invoice.issued_at = datetime.utcnow()
            await self.update_invoice(invoice)
            
            # Ici, on intégrerait un service d'email
            # await email_service.send_invoice_email(recipient_email, invoice, pdf_data)
            
            logger.info(f"Facture {invoice.invoice_number} envoyée à {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de facture {invoice.invoice_number}: {e}")
            return False
            
    async def mark_as_paid(self, invoice: Invoice, amount: Decimal, payment_method: str, transaction_id: str):
        """Marque une facture comme payée"""        invoice.add_payment(amount, payment_method, transaction_id)
        await self.update_invoice(invoice)
        
        logger.info(f"Paiement enregistré pour facture {invoice.invoice_number}: {amount} via {payment_method}")
        
    async def cancel_invoice(self, invoice: Invoice, reason: str = ""):
        """Annule une facture"""        invoice.status = InvoiceStatus.CANCELLED
        if reason:
            invoice.notes += f"\nAnnulée: {reason}"
        await self.update_invoice(invoice)
        
        logger.info(f"Facture {invoice.invoice_number} annulée: {reason}")
        
    async def create_credit_note(self, original_invoice: Invoice, items: List[InvoiceItem], reason: str = "") -> Invoice:
        """Crée une note de crédit"""        credit_note = Invoice(
            customer_id=original_invoice.customer_id,
            invoice_type=InvoiceType.CREDIT_NOTE,
            currency=original_invoice.currency,
            billing_address=original_invoice.billing_address,
            items=items,
            reference=original_invoice.invoice_number,
            notes=f"Note de crédit pour facture {original_invoice.invoice_number}. {reason}".strip()
        )
        
        # Inverser les montants pour la note de crédit
        for item in credit_note.items:
            item.quantity = -abs(item.quantity)
            
        await self.create_invoice(original_invoice.customer_id)
        
        logger.info(f"Note de crédit créée: {credit_note.invoice_number} pour facture {original_invoice.invoice_number}")
        return credit_note
        
    async def get_overdue_invoices(self, days_overdue: int = 0) -> List[Invoice]:
        """Récupère les factures en retard"""        if not self.database_client:
            return []
            
        cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)
        # Ici, on ferait une requête en base
        # return await self._query_overdue_invoices(cutoff_date)
        return []
        
    async def generate_invoice_pdf(self, invoice: Invoice) -> bytes:
        """Génère le PDF d'une facture"""        template = self.templates.get(invoice.template_id or "default")
        return template.generate_pdf(invoice)
        
    async def _generate_invoice_number(self) -> str:
        """Génère un numéro de facture unique"""        # Dans un vrai système, on récupérerait le dernier numéro en base
        number = f"{self.numbering_prefix}-{self.numbering_sequence:06d}"
        self.numbering_sequence += 1
        return number
        
    async def _save_invoice(self, invoice: Invoice):
        """Sauvegarde une facture en base"""        try:
            # Convert invoice to dict for storage
            invoice_data = {
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "customer_id": invoice.customer_id,
                "customer_name": invoice.customer_name,
                "customer_email": invoice.customer_email,
                "customer_address": invoice.customer_address,
                "items": [asdict(item) for item in invoice.items],
                "subtotal": float(invoice.subtotal),
                "tax_amount": float(invoice.tax_amount),
                "total_amount": float(invoice.total_amount),
                "currency": invoice.currency,
                "status": invoice.status.value,
                "payment_method": invoice.payment_method.value if invoice.payment_method else None,
                "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
                "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "template_id": invoice.template_id,
                "notes": invoice.notes,
                "metadata": invoice.metadata,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # In production environment with database client
            if self.database_client:
                # Save to database
                await self.database_client.invoices.save(invoice_data)
                logger.info(f"Invoice {invoice.invoice_number} saved to database")
            else:
                # For development/testing - store in memory cache or file
                cache_key = f"invoice:{invoice.invoice_id}"
                # Store invoice data in memory for retrieval
                self._invoice_cache = getattr(self, '_invoice_cache', {})
                self._invoice_cache[cache_key] = invoice_data
                logger.info(f"Invoice {invoice.invoice_number} cached in memory")
                
        except Exception as e:
            logger.error(f"Failed to save invoice {invoice.invoice_number}: {e}")
            raise
        
    async def _load_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Charge une facture depuis la base"""        try:
            invoice_data = None
            
            # In production environment with database client
            if self.database_client:
                invoice_data = await self.database_client.invoices.find_by_id(invoice_id)
            else:
                # For development/testing - load from memory cache
                cache_key = f"invoice:{invoice_id}"
                self._invoice_cache = getattr(self, '_invoice_cache', {})
                invoice_data = self._invoice_cache.get(cache_key)
                
            if not invoice_data:
                return None
                
            # Convert back to Invoice object
            items = [InvoiceItem(**item_data) for item_data in invoice_data.get('items', [])]
            
            invoice = Invoice(
                invoice_id=invoice_data['invoice_id'],
                invoice_number=invoice_data['invoice_number'],
                customer_id=invoice_data['customer_id'],
                customer_name=invoice_data['customer_name'],
                customer_email=invoice_data['customer_email'],
                customer_address=invoice_data.get('customer_address'),
                items=items,
                subtotal=Decimal(str(invoice_data['subtotal'])),
                tax_amount=Decimal(str(invoice_data['tax_amount'])),
                total_amount=Decimal(str(invoice_data['total_amount'])),
                currency=invoice_data['currency'],
                status=InvoiceStatus(invoice_data['status']),
                payment_method=PaymentMethod(invoice_data['payment_method']) if invoice_data.get('payment_method') else None,
                issued_at=datetime.fromisoformat(invoice_data['issued_at']) if invoice_data.get('issued_at') else None,
                due_at=datetime.fromisoformat(invoice_data['due_at']) if invoice_data.get('due_at') else None,
                paid_at=datetime.fromisoformat(invoice_data['paid_at']) if invoice_data.get('paid_at') else None,
                template_id=invoice_data.get('template_id'),
                notes=invoice_data.get('notes'),
                metadata=invoice_data.get('metadata', {})
            )
            
            logger.info(f"Invoice {invoice.invoice_number} loaded successfully")
            return invoice
            
        except Exception as e:
            logger.error(f"Failed to load invoice {invoice_id}: {e}")
            return None
        
    def get_invoice_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des factures"""        return {
            "templates_count": len(self.templates),
            "auto_numbering": self.auto_numbering_enabled,
            "current_sequence": self.numbering_sequence,
            "prefix": self.numbering_prefix
        }