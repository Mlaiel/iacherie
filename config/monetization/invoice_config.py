"""
Invoice Configuration Module
============================

Professional invoice generation and management system for IA-Influencer platform.
Advanced billing, tax compliance, and automated invoice processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + Finance Expert

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class InvoiceType(str, Enum):
    """Types of invoices in the system."""
    STANDARD = "standard"  # Regular subscription/service invoice
    PROFORMA = "proforma"  # Pro forma invoice
    CREDIT_NOTE = "credit_note"  # Credit note for refunds
    DEBIT_NOTE = "debit_note"  # Additional charges
    RECURRING = "recurring"  # Subscription-based recurring invoice
    ONE_TIME = "one_time"  # One-time service/product
    USAGE_BASED = "usage_based"  # Based on usage metrics
    MILESTONE = "milestone"  # Project milestone billing
    RETAINER = "retainer"  # Retainer/advance payment
    COMMISSION = "commission"  # Commission-based billing
    ROYALTY = "royalty"  # Royalty payments
    SETTLEMENT = "settlement"  # Legal settlements
    CUSTOM = "custom"  # Custom invoice type


class InvoiceStatus(str, Enum):
    """Invoice processing status."""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    VIEWED = "viewed"
    APPROVED = "approved"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    VOID = "void"
    WRITTEN_OFF = "written_off"


class PaymentTerms(str, Enum):
    """Standard payment terms."""
    IMMEDIATE = "immediate"  # Payment due immediately
    NET_7 = "net_7"  # 7 days
    NET_15 = "net_15"  # 15 days  
    NET_30 = "net_30"  # 30 days
    NET_45 = "net_45"  # 45 days
    NET_60 = "net_60"  # 60 days
    NET_90 = "net_90"  # 90 days
    EOM = "eom"  # End of month
    COD = "cod"  # Cash on delivery
    PREPAID = "prepaid"  # Prepayment required
    CUSTOM = "custom"  # Custom terms


class TaxType(str, Enum):
    """Types of taxes applicable to invoices."""
    VAT = "vat"  # Value Added Tax
    GST = "gst"  # Goods and Services Tax
    SALES_TAX = "sales_tax"  # Sales tax
    WITHHOLDING_TAX = "withholding_tax"  # Withholding tax
    EXCISE_TAX = "excise_tax"  # Excise tax
    CUSTOM_DUTY = "custom_duty"  # Import duties
    SERVICE_TAX = "service_tax"  # Service tax
    DIGITAL_SERVICE_TAX = "digital_service_tax"  # DST
    NONE = "none"  # No tax applicable


class InvoiceFormat(str, Enum):
    """Supported invoice formats."""
    PDF = "pdf"
    HTML = "html"
    XML = "xml"  # For automated processing
    JSON = "json"  # API format
    CSV = "csv"  # Bulk export
    EXCEL = "excel"  # Spreadsheet format


class DeliveryMethod(str, Enum):
    """Invoice delivery methods."""
    EMAIL = "email"
    API_WEBHOOK = "api_webhook"
    DOWNLOAD_LINK = "download_link"
    POSTAL_MAIL = "postal_mail"
    PORTAL = "portal"  # Customer portal
    FTP = "ftp"  # File transfer
    EDI = "edi"  # Electronic Data Interchange


@dataclass
class TaxConfiguration:
    """Tax configuration for different jurisdictions."""
    tax_type: TaxType
    tax_rate: Decimal
    tax_name: str
    jurisdiction: str  # Country/state code
    
    # Tax calculation rules
    inclusive: bool = False  # Tax included in price
    compound: bool = False  # Compound tax calculation
    reverse_charge: bool = False  # Reverse charge mechanism
    
    # Exemption rules
    b2b_exempt: bool = False  # B2B transactions exempt
    threshold_amount: Optional[Decimal] = None  # Tax threshold
    
    # Reporting requirements
    tax_id_required: bool = True
    monthly_reporting: bool = True
    quarterly_reporting: bool = False


@dataclass
class InvoiceLineItem:
    """Individual line item on an invoice."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    currency: str
    
    # Item classification
    item_code: Optional[str] = None
    category: Optional[str] = None
    
    # Tax configuration
    tax_rate: Decimal = Decimal("0.00")
    tax_exempt: bool = False
    
    # Discounts
    discount_percentage: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    
    # Billing period (for subscriptions)
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None


@dataclass
class PaymentInformation:
    """Payment details and instructions."""
    payment_methods: List[str]  # Accepted payment methods
    bank_details: Dict[str, str] = field(default_factory=dict)
    
    # Payment processing
    payment_processor: Optional[str] = None
    payment_link: Optional[str] = None
    qr_code_data: Optional[str] = None
    
    # Terms and conditions
    late_fee_rate: Decimal = Decimal("0.00")
    early_payment_discount: Decimal = Decimal("0.00")
    early_payment_days: int = 0


@dataclass
class CompanyInformation:
    """Company/organization information for invoices."""
    name: str
    legal_name: Optional[str] = None
    
    # Address information
    address_line1: str = ""
    address_line2: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""
    
    # Contact information
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Legal and tax identifiers
    tax_id: Optional[str] = None
    vat_number: Optional[str] = None
    business_registration: Optional[str] = None
    
    # Banking information
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None


@dataclass
class InvoiceTemplate:
    """Invoice template configuration."""
    template_id: str
    template_name: str
    template_type: InvoiceType
    
    # Visual design
    logo_url: Optional[str] = None
    color_scheme: Dict[str, str] = field(default_factory=dict)
    font_family: str = "Arial"
    
    # Layout configuration
    show_line_numbers: bool = True
    show_item_codes: bool = False
    show_tax_breakdown: bool = True
    show_payment_instructions: bool = True
    
    # Language and localization
    language: str = "en"
    currency_format: str = "symbol"  # symbol, code, name
    date_format: str = "YYYY-MM-DD"
    number_format: str = "#,##0.00"
    
    # Legal requirements
    required_fields: List[str] = field(default_factory=list)
    footer_text: Optional[str] = None
    terms_and_conditions: Optional[str] = None


@dataclass
class AutomationRule:
    """Invoice automation rules."""
    rule_id: str
    rule_name: str
    trigger: str  # subscription_renewal, usage_threshold, etc.
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Actions
    auto_generate: bool = True
    auto_send: bool = False
    auto_follow_up: bool = True
    follow_up_days: List[int] = field(default_factory=lambda: [7, 14, 30])
    
    # Escalation
    escalate_overdue: bool = True
    escalation_days: int = 30
    escalation_contact: Optional[str] = None


@dataclass
class InvoiceConfig:
    """Professional invoice management configuration."""
    
    # Global Invoice Settings
    ENABLE_INVOICING: bool = True
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_LANGUAGE: str = "en"
    
    # Numbering System
    INVOICE_NUMBER_PREFIX: str = "INV"
    INVOICE_NUMBER_FORMAT: str = "INV-{year}-{sequence:06d}"  # INV-2025-000001
    RESET_SEQUENCE_ANNUALLY: bool = True
    STARTING_SEQUENCE_NUMBER: int = 1
    
    # Default Payment Terms
    DEFAULT_PAYMENT_TERMS: PaymentTerms = PaymentTerms.NET_30
    DEFAULT_GRACE_PERIOD_DAYS: int = 5
    
    # Company Information (Platform details)
    COMPANY_INFO: CompanyInformation = CompanyInformation(
        name="IA-Influencer Agent Platform",
        legal_name="IA-Influencer Technologies GmbH",
        address_line1="Musterstraße 123",
        city="Berlin",
        state="Berlin",
        postal_code="10117",
        country="DE",
        phone="+49 30 12345678",
        email="billing@ia-influencer.com",
        website="https://ia-influencer.com",
        tax_id="DE123456789",
        vat_number="DE123456789",
        business_registration="HRB 12345 B"
    )
    
    # Tax Configuration by Jurisdiction
    TAX_CONFIGURATIONS: Dict[str, List[TaxConfiguration]] = field(
        default_factory=lambda: {
            "DE": [  # Germany
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    tax_rate=Decimal("19.0"),
                    tax_name="MwSt.",
                    jurisdiction="DE",
                    inclusive=False,
                    b2b_exempt=True,
                    reverse_charge=True
                )
            ],
            "US": [  # United States
                TaxConfiguration(
                    tax_type=TaxType.SALES_TAX,
                    tax_rate=Decimal("8.5"),
                    tax_name="Sales Tax",
                    jurisdiction="US",
                    inclusive=False,
                    threshold_amount=Decimal("100000.00")  # Economic nexus
                )
            ],
            "GB": [  # United Kingdom
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    tax_rate=Decimal("20.0"),
                    tax_name="VAT",
                    jurisdiction="GB",
                    inclusive=False,
                    b2b_exempt=True,
                    threshold_amount=Decimal("85000.00")  # VAT threshold
                )
            ],
            "FR": [  # France
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    tax_rate=Decimal("20.0"),
                    tax_name="TVA",
                    jurisdiction="FR",
                    inclusive=False,
                    b2b_exempt=True,
                    reverse_charge=True
                )
            ],
            "CA": [  # Canada
                TaxConfiguration(
                    tax_type=TaxType.GST,
                    tax_rate=Decimal("5.0"),
                    tax_name="GST",
                    jurisdiction="CA",
                    inclusive=False
                )
            ]
        }
    )
    
    # Invoice Templates
    INVOICE_TEMPLATES: Dict[str, InvoiceTemplate] = field(
        default_factory=lambda: {
            "standard": InvoiceTemplate(
                template_id="standard",
                template_name="Standard Invoice",
                template_type=InvoiceType.STANDARD,
                color_scheme={
                    "primary": "#2563eb",
                    "secondary": "#64748b",
                    "accent": "#10b981"
                },
                required_fields=["invoice_number", "issue_date", "due_date", "total_amount"],
                terms_and_conditions="Payment is due within the specified terms. Late payments may incur additional fees."
            ),
            "subscription": InvoiceTemplate(
                template_id="subscription",
                template_name="Subscription Invoice",
                template_type=InvoiceType.RECURRING,
                show_tax_breakdown=True,
                required_fields=["subscription_period", "next_billing_date"],
                footer_text="This is an automated recurring invoice for your subscription service."
            ),
            "usage_based": InvoiceTemplate(
                template_id="usage_based",
                template_name="Usage-Based Invoice",
                template_type=InvoiceType.USAGE_BASED,
                show_line_numbers=True,
                show_item_codes=True,
                required_fields=["usage_period", "usage_details"]
            ),
            "credit_note": InvoiceTemplate(
                template_id="credit_note",
                template_name="Credit Note",
                template_type=InvoiceType.CREDIT_NOTE,
                color_scheme={
                    "primary": "#dc2626",
                    "secondary": "#64748b"
                },
                required_fields=["original_invoice_number", "reason"]
            )
        }
    )
    
    # Payment Information
    PAYMENT_INFO: PaymentInformation = PaymentInformation(
        payment_methods=["bank_transfer", "credit_card", "paypal", "stripe"],
        bank_details={
            "bank_name": "Deutsche Bank AG",
            "account_holder": "IA-Influencer Technologies GmbH",
            "iban": "DE89370400440532013000",
            "bic": "COBADEFFXXX"
        },
        late_fee_rate=Decimal("1.5"),  # 1.5% per month
        early_payment_discount=Decimal("2.0"),  # 2% for payments within 10 days
        early_payment_days=10
    )
    
    # Automation Rules
    AUTOMATION_RULES: List[AutomationRule] = field(
        default_factory=lambda: [
            AutomationRule(
                rule_id="subscription_renewal",
                rule_name="Subscription Renewal Invoicing",
                trigger="subscription_renewal",
                auto_generate=True,
                auto_send=True,
                follow_up_days=[7, 14, 21]
            ),
            AutomationRule(
                rule_id="usage_billing",
                rule_name="Monthly Usage Billing",
                trigger="monthly_usage",
                conditions={"min_usage_amount": Decimal("1.00")},
                auto_generate=True,
                auto_send=True
            ),
            AutomationRule(
                rule_id="overdue_follow_up",
                rule_name="Overdue Payment Follow-up",
                trigger="payment_overdue",
                auto_follow_up=True,
                follow_up_days=[1, 7, 14, 30],
                escalate_overdue=True,
                escalation_days=45
            )
        ]
    )
    
    # Delivery and Distribution
    DELIVERY_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "default_delivery_method": DeliveryMethod.EMAIL,
        "supported_formats": [InvoiceFormat.PDF, InvoiceFormat.HTML],
        "email_settings": {
            "from_email": "billing@ia-influencer.com",
            "from_name": "IA-Influencer Billing",
            "subject_template": "Invoice {invoice_number} from IA-Influencer",
            "reply_to": "support@ia-influencer.com"
        },
        "portal_settings": {
            "enable_customer_portal": True,
            "portal_url": "https://billing.ia-influencer.com",
            "allow_online_payment": True,
            "payment_methods": ["stripe", "paypal"]
        },
        "api_settings": {
            "webhook_enabled": True,
            "webhook_events": ["invoice.created", "invoice.paid", "invoice.overdue"],
            "webhook_retries": 3,
            "webhook_timeout": 30
        }
    })
    
    # Compliance and Legal
    COMPLIANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "gdpr_compliant": True,
        "data_retention_years": 10,  # Legal requirement for financial records
        "archive_paid_invoices": True,
        "electronic_signature": True,
        "audit_trail": True,
        "immutable_invoices": True,  # Prevent modification after sending
        
        # Reporting requirements
        "monthly_tax_reporting": True,
        "quarterly_vat_reporting": True,
        "annual_financial_reporting": True,
        
        # Anti-money laundering
        "aml_screening": True,
        "suspicious_activity_threshold": Decimal("10000.00")
    })
    
    # Performance and Scalability
    PERFORMANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "batch_invoice_generation": True,
        "max_batch_size": 1000,
        "async_processing": True,
        "pdf_generation_timeout": 30,
        "cache_generated_pdfs": True,
        "cache_ttl_hours": 24,
        
        # Rate limiting
        "rate_limit_per_hour": 1000,
        "burst_limit": 100,
        
        # Background processing
        "queue_processing": True,
        "queue_priority_levels": 3,
        "max_retry_attempts": 3
    })
    
    # Multi-language Support
    LOCALIZATION: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "en": {
            "invoice": "Invoice",
            "credit_note": "Credit Note", 
            "due_date": "Due Date",
            "payment_terms": "Payment Terms",
            "tax_rate": "Tax Rate",
            "total": "Total",
            "subtotal": "Subtotal"
        },
        "de": {
            "invoice": "Rechnung",
            "credit_note": "Gutschrift",
            "due_date": "Fälligkeitsdatum",
            "payment_terms": "Zahlungsbedingungen", 
            "tax_rate": "Steuersatz",
            "total": "Gesamt",
            "subtotal": "Zwischensumme"
        },
        "fr": {
            "invoice": "Facture",
            "credit_note": "Note de crédit",
            "due_date": "Date d'échéance",
            "payment_terms": "Conditions de paiement",
            "tax_rate": "Taux de taxe",
            "total": "Total",
            "subtotal": "Sous-total"
        }
    })
    
    # Integration Settings
    INTEGRATION_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "accounting_software": {
            "quickbooks_enabled": False,
            "xero_enabled": False,
            "sage_enabled": False,
            "auto_sync": False
        },
        "payment_processors": {
            "stripe_enabled": True,
            "paypal_enabled": True,
            "wise_enabled": True,
            "auto_reconciliation": True
        },
        "erp_integration": {
            "sap_enabled": False,
            "oracle_enabled": False,
            "custom_api": True
        }
    })
    
    def get_tax_configuration(self, jurisdiction: str) -> List[TaxConfiguration]:
        """Get tax configuration for a specific jurisdiction."""



        return self.TAX_CONFIGURATIONS.get(jurisdiction.upper(), [])
    
    def get_invoice_template(self, template_id: str) -> Optional[InvoiceTemplate]:
        """Get invoice template by ID."""



        return self.INVOICE_TEMPLATES.get(template_id)
    
    def calculate_tax(self, amount: Decimal, jurisdiction: str, 
                     b2b_transaction: bool = False) -> Dict[str, Decimal]:
        """Calculate applicable taxes for an amount."""
        tax_configs = self.get_tax_configuration(jurisdiction)
        tax_breakdown = {}
        total_tax = Decimal("0.00")
        
        for tax_config in tax_configs:
            if b2b_transaction and tax_config.b2b_exempt:
                continue
                
            if tax_config.threshold_amount and amount < tax_config.threshold_amount:
                continue
            
            if tax_config.inclusive:
                # Tax is included in the amount
                tax_amount = amount * tax_config.tax_rate / (Decimal("100.0") + tax_config.tax_rate)
            else:
                # Tax is additional to the amount
                tax_amount = amount * tax_config.tax_rate / Decimal("100.0")
            
            tax_breakdown[tax_config.tax_name] = tax_amount
            total_tax += tax_amount
        
        tax_breakdown["total_tax"] = total_tax
        return tax_breakdown
    
    def generate_invoice_number(self, invoice_type: InvoiceType = InvoiceType.STANDARD,
                               sequence: Optional[int] = None) -> str:
        """Generate unique invoice number."""
        current_year = datetime.now().year
        
        if sequence is None:
            # In a real implementation, this would fetch from database
            sequence = self.STARTING_SEQUENCE_NUMBER
        
        # Handle different invoice types
        type_prefix = {
            InvoiceType.STANDARD: "INV",
            InvoiceType.CREDIT_NOTE: "CN",
            InvoiceType.PROFORMA: "PF",
            InvoiceType.RECURRING: "SUB"
        }.get(invoice_type, "INV")
        
        return f"{type_prefix}-{current_year}-{sequence:06d}"
    
    def get_payment_terms_days(self, payment_terms: PaymentTerms) -> int:
        """Convert payment terms enum to number of days."""
        terms_mapping = {
            PaymentTerms.IMMEDIATE: 0,
            PaymentTerms.NET_7: 7,
            PaymentTerms.NET_15: 15,
            PaymentTerms.NET_30: 30,
            PaymentTerms.NET_45: 45,
            PaymentTerms.NET_60: 60,
            PaymentTerms.NET_90: 90
        }
        return terms_mapping.get(payment_terms, 30)
    
    def calculate_due_date(self, issue_date: datetime, 
                          payment_terms: PaymentTerms) -> datetime:
        """Calculate invoice due date based on payment terms."""
        days = self.get_payment_terms_days(payment_terms)
        return issue_date + timedelta(days=days)


# Global configuration instance
invoice_config = InvoiceConfig()

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class InvoiceStatus(str, Enum):
    """Invoice status types."""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    VOID = "void"


class InvoiceType(str, Enum):
    """Invoice types."""
    STANDARD = "standard"
    RECURRING = "recurring"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    PROFORMA = "proforma"
    ESTIMATE = "estimate"
    QUOTE = "quote"
    RECEIPT = "receipt"
    STATEMENT = "statement"


class PaymentTerms(str, Enum):
    """Payment terms options."""
    NET_0 = "net_0"      # Due immediately
    NET_7 = "net_7"      # Due in 7 days
    NET_14 = "net_14"    # Due in 14 days
    NET_30 = "net_30"    # Due in 30 days
    NET_45 = "net_45"    # Due in 45 days
    NET_60 = "net_60"    # Due in 60 days
    NET_90 = "net_90"    # Due in 90 days
    CUSTOM = "custom"    # Custom terms


class TaxType(str, Enum):
    """Tax types for invoicing."""
    VAT = "vat"
    GST = "gst"
    PST = "pst"
    HST = "hst"
    SALES_TAX = "sales_tax"
    WITHHOLDING = "withholding"
    NONE = "none"


@dataclass
class InvoiceLineItem:
    """Invoice line item configuration."""
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percentage: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("0.00")
    tax_type: TaxType = TaxType.NONE
    product_code: Optional[str] = None
    category: Optional[str] = None


@dataclass
class TaxConfiguration:
    """Tax configuration for invoices."""
    tax_type: TaxType
    rate: Decimal
    description: str
    tax_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    is_compound: bool = False
    is_inclusive: bool = False


@dataclass
class CompanyDetails:
    """Company details for invoice generation."""
    name: str
    legal_name: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    state_province: str
    postal_code: str
    country: str
    tax_number: Optional[str]
    registration_number: Optional[str]
    phone: Optional[str]
    email: str
    website: Optional[str]
    logo_url: Optional[str]


@dataclass
class InvoiceTemplate:
    """Invoice template configuration."""
    template_id: str
    name: str
    description: str
    html_template: str
    css_styles: str
    default_language: str
    supported_languages: List[str]
    logo_position: str = "top_left"
    color_scheme: str = "default"
    show_payment_instructions: bool = True
    show_terms_conditions: bool = True


@dataclass
class InvoiceConfig:
    """Main invoice configuration class."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "INVOICE_DB_URL", 
        "postgresql://user:pass@localhost:5432/invoice_db"
    )
    
    # Default Settings
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_PAYMENT_TERMS: PaymentTerms = PaymentTerms.NET_30
    DEFAULT_LANGUAGE: str = "en"
    
    # Company Details
    COMPANY_DETAILS: CompanyDetails = CompanyDetails(
        name="IA-Influencer Agent Platform",
        legal_name="IA-Influencer Agent GmbH",
        address_line1="Musterstraße 123",
        address_line2=None,
        city="Berlin",
        state_province="Berlin",
        postal_code="10115",
        country="Germany",
        tax_number="DE123456789",
        registration_number="HRB 123456",
        phone="+49 30 12345678",
        email="billing@ia-influencer.de",
        website="https://ia-influencer.de",
        logo_url="/assets/logo/company-logo.png"
    )
    
    # Tax Configuration by Country
    TAX_CONFIGURATIONS: Dict[str, List[TaxConfiguration]] = field(
        default_factory=lambda: {
            "DE": [
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    rate=Decimal("19.0"),
                    description="German VAT (Mehrwertsteuer)",
                    tax_number="DE123456789",
                    jurisdiction="Germany",
                    is_inclusive=False
                ),
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    rate=Decimal("7.0"),
                    description="German Reduced VAT",
                    tax_number="DE123456789",
                    jurisdiction="Germany",
                    is_inclusive=False
                )
            ],
            "US": [
                TaxConfiguration(
                    tax_type=TaxType.SALES_TAX,
                    rate=Decimal("8.25"),  # Varies by state
                    description="Sales Tax",
                    jurisdiction="California",
                    is_inclusive=False
                ),
                TaxConfiguration(
                    tax_type=TaxType.WITHHOLDING,
                    rate=Decimal("30.0"),
                    description="Non-resident Withholding Tax",
                    jurisdiction="United States",
                    is_inclusive=False
                )
            ],
            "GB": [
                TaxConfiguration(
                    tax_type=TaxType.VAT,
                    rate=Decimal("20.0"),
                    description="UK VAT",
                    tax_number="GB123456789",
                    jurisdiction="United Kingdom",
                    is_inclusive=False
                )
            ],
            "CA": [
                TaxConfiguration(
                    tax_type=TaxType.GST,
                    rate=Decimal("5.0"),
                    description="Goods and Services Tax",
                    jurisdiction="Canada",
                    is_inclusive=False
                ),
                TaxConfiguration(
                    tax_type=TaxType.PST,
                    rate=Decimal("7.0"),
                    description="Provincial Sales Tax (BC)",
                    jurisdiction="British Columbia",
                    is_inclusive=False
                )
            ]
        }
    )
    
    # Invoice Templates
    INVOICE_TEMPLATES: Dict[str, InvoiceTemplate] = field(
        default_factory=lambda: {
            "standard": InvoiceTemplate(
                template_id="standard",
                name="Standard Invoice",
                description="Default professional invoice template",
                html_template="templates/invoices/standard.html",
                css_styles="templates/invoices/standard.css",
                default_language="en",
                supported_languages=["en", "de", "fr", "es", "it"],
                logo_position="top_left",
                color_scheme="blue",
                show_payment_instructions=True,
                show_terms_conditions=True
            ),
            "minimal": InvoiceTemplate(
                template_id="minimal",
                name="Minimal Invoice",
                description="Clean and minimal invoice design",
                html_template="templates/invoices/minimal.html",
                css_styles="templates/invoices/minimal.css",
                default_language="en",
                supported_languages=["en", "de", "fr"],
                logo_position="top_center",
                color_scheme="gray",
                show_payment_instructions=True,
                show_terms_conditions=False
            ),
            "premium": InvoiceTemplate(
                template_id="premium",
                name="Premium Invoice",
                description="Premium branded invoice template",
                html_template="templates/invoices/premium.html",
                css_styles="templates/invoices/premium.css",
                default_language="en",
                supported_languages=["en", "de", "fr", "es", "it", "nl"],
                logo_position="top_left",
                color_scheme="gradient",
                show_payment_instructions=True,
                show_terms_conditions=True
            ),
            "enterprise": InvoiceTemplate(
                template_id="enterprise",
                name="Enterprise Invoice",
                description="Corporate enterprise invoice template",
                html_template="templates/invoices/enterprise.html",
                css_styles="templates/invoices/enterprise.css",
                default_language="en",
                supported_languages=["en", "de", "fr", "es", "it", "nl", "pt"],
                logo_position="header",
                color_scheme="corporate",
                show_payment_instructions=True,
                show_terms_conditions=True
            )
        }
    )
    
    # Invoice Numbering Configuration
    NUMBERING_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "prefix": "INV",
        "suffix": "",
        "separator": "-",
        "padding": 6,  # Number of digits (e.g., 000001)
        "include_year": True,
        "include_month": False,
        "reset_annually": True,
        "format_template": "{prefix}{separator}{year}{separator}{number:0{padding}d}",
        "custom_sequences": {
            "standard": {"prefix": "INV", "start": 1},
            "recurring": {"prefix": "REC", "start": 1000},
            "credit_note": {"prefix": "CN", "start": 1},
            "proforma": {"prefix": "PRO", "start": 1}
        }
    })
    
    # Payment Configuration
    PAYMENT_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "accepted_methods": [
            "credit_card", "bank_transfer", "paypal", "stripe", "wire_transfer"
        ],
        "online_payments_enabled": True,
        "partial_payments_allowed": True,
        "payment_instructions": {
            "bank_transfer": {
                "bank_name": "Deutsche Bank AG",
                "account_holder": "IA-Influencer Agent GmbH",
                "iban": "DE89 3704 0044 0532 0130 00",
                "bic": "COBADEFFXXX",
                "reference_required": True
            },
            "paypal": {
                "email": "payments@ia-influencer.de",
                "merchant_id": "merchant_123456"
            }
        },
        "late_payment_fee": Decimal("25.00"),
        "early_payment_discount": Decimal("2.0"),  # 2% discount
        "early_payment_days": 10,
        "payment_reminders": [7, 14, 30]  # Days after due date
    })
    
    # Automation Configuration
    AUTOMATION_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "auto_send_invoices": True,
        "auto_send_reminders": True,
        "auto_generate_recurring": True,
        "auto_apply_late_fees": False,  # Requires manual approval
        "auto_mark_paid": True,  # When payment detected
        "auto_reconciliation": True,
        "batch_processing": True,
        "scheduled_generation": True,
        "webhook_notifications": True,
        "email_confirmations": True
    })
    
    # Localization Configuration
    LOCALIZATION_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "supported_languages": ["en", "de", "fr", "es", "it", "nl", "pt"],
        "default_language": "en",
        "currency_formats": {
            "EUR": {"symbol": "€", "position": "after", "decimal_places": 2},
            "USD": {"symbol": "$", "position": "before", "decimal_places": 2},
            "GBP": {"symbol": "£", "position": "before", "decimal_places": 2},
            "CHF": {"symbol": "CHF", "position": "after", "decimal_places": 2}
        },
        "date_formats": {
            "en": "MM/DD/YYYY",
            "de": "DD.MM.YYYY",
            "fr": "DD/MM/YYYY",
            "es": "DD/MM/YYYY"
        },
        "number_formats": {
            "en": {"decimal": ".", "thousand": ","},
            "de": {"decimal": ",", "thousand": "."},
            "fr": {"decimal": ",", "thousand": " "},
            "es": {"decimal": ",", "thousand": "."}
        }
    })
    
    # Compliance Configuration
    COMPLIANCE_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "gdpr_compliant": True,
        "data_retention_years": 7,
        "audit_trail_enabled": True,
        "digital_signatures": False,  # Optional premium feature
        "archive_invoices": True,
        "backup_frequency": "daily",
        "encryption_enabled": True,
        "access_controls": True,
        "regulatory_requirements": {
            "DE": ["GoBD", "AO", "UStG"],
            "US": ["SOX", "GAAP"],
            "GB": ["HMRC", "Companies House"],
            "FR": ["DGFiP", "RGPD"]
        }
    })
    
    # Export and Integration Configuration
    EXPORT_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "supported_formats": ["PDF", "HTML", "CSV", "JSON", "XML"],
        "default_format": "PDF",
        "pdf_settings": {
            "page_size": "A4",
            "orientation": "portrait",
            "margins": {"top": 20, "right": 20, "bottom": 20, "left": 20},
            "font_family": "Arial",
            "font_size": 11
        },
        "batch_export_enabled": True,
        "api_integration": True,
        "webhook_endpoints": {
            "invoice_created": "/webhooks/invoice/created",
            "invoice_paid": "/webhooks/invoice/paid",
            "payment_failed": "/webhooks/invoice/payment_failed"
        },
        "third_party_integrations": ["QuickBooks", "Xero", "Sage", "DATEV"]
    })
    
    # Performance and Caching
    PERFORMANCE_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "cache_invoices": True,
        "cache_ttl_hours": 24,
        "async_generation": True,
        "bulk_operations": True,
        "pdf_generation_timeout": 30,  # seconds
        "max_concurrent_generations": 10,
        "optimize_images": True,
        "compress_pdfs": True,
        "cdn_enabled": True
    })
    
    def get_tax_config(self, country_code: str) -> List[TaxConfiguration]:
        """Get tax configuration for a specific country."""



        return self.TAX_CONFIGURATIONS.get(country_code.upper(), [])
    
    def get_template(self, template_id: str) -> Optional[InvoiceTemplate]:
        """Get invoice template configuration."""



        return self.INVOICE_TEMPLATES.get(template_id)
    
    def calculate_tax_amount(
        self, 
        subtotal: Decimal, 
        tax_rate: Decimal, 
        is_inclusive: bool = False
    ) -> Decimal:
        """Calculate tax amount from subtotal and rate."""
        if is_inclusive:
            # Tax is included in the subtotal
            tax_amount = subtotal - (subtotal / (Decimal("1") + (tax_rate / Decimal("100"))))
        else:
            # Tax is added to the subtotal
            tax_amount = subtotal * (tax_rate / Decimal("100"))
        
        return tax_amount.quantize(Decimal("0.01"))
    
    def generate_invoice_number(self, invoice_type: InvoiceType = InvoiceType.STANDARD) -> str:
        """Generate next invoice number based on configuration."""
        config = self.NUMBERING_CONFIG
        
        # Get type-specific configuration
        type_config = config.get("custom_sequences", {}).get(
            invoice_type.value, 
            {"prefix": config["prefix"], "start": 1}
        )
        
        # This would normally query the database for the next number
        # For configuration purposes, we'll return a template
        import datetime
        current_year = datetime.datetime.now().year
        
        if config["include_year"]:
            if config["include_month"]:
                current_month = datetime.datetime.now().month
                return f"{type_config['prefix']}{config['separator']}{current_year}{current_month:02d}{config['separator']}000001"
            else:
                return f"{type_config['prefix']}{config['separator']}{current_year}{config['separator']}000001"
        else:
            return f"{type_config['prefix']}{config['separator']}000001"
    
    def get_payment_terms_days(self, terms: PaymentTerms) -> int:
        """Get number of days for payment terms."""
        terms_mapping = {
            PaymentTerms.NET_0: 0,
            PaymentTerms.NET_7: 7,
            PaymentTerms.NET_14: 14,
            PaymentTerms.NET_30: 30,
            PaymentTerms.NET_45: 45,
            PaymentTerms.NET_60: 60,
            PaymentTerms.NET_90: 90
        }
        return terms_mapping.get(terms, 30)  # Default to 30 days
    
    def calculate_line_item_total(self, line_item: InvoiceLineItem) -> Dict[str, Decimal]:
        """Calculate totals for an invoice line item."""
        subtotal = line_item.quantity * line_item.unit_price
        
        # Apply discount
        discount_amount = subtotal * (line_item.discount_percentage / Decimal("100"))
        discounted_subtotal = subtotal - discount_amount
        
        # Calculate tax
        tax_amount = self.calculate_tax_amount(
            discounted_subtotal, 
            line_item.tax_rate, 
            is_inclusive=False
        )
        
        total = discounted_subtotal + tax_amount
        
        return {
            "subtotal": subtotal.quantize(Decimal("0.01")),
            "discount_amount": discount_amount.quantize(Decimal("0.01")),
            "discounted_subtotal": discounted_subtotal.quantize(Decimal("0.01")),
            "tax_amount": tax_amount.quantize(Decimal("0.01")),
            "total": total.quantize(Decimal("0.01"))
        }


# Global configuration instance
invoice_config = InvoiceConfig()
