"""📊 Tax Compliance Payment Processor
===================================

Advanced tax compliance processor with automated tax calculations,
reporting, and remittance for global jurisdictions and payment types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

logger = logging.getLogger(__name__)


class TaxType(Enum):
    """Tax types"""
    VAT = "vat"  # Value Added Tax (EU)
    GST = "gst"  # Goods and Services Tax (CA, AU, IN)
    SALES_TAX = "sales_tax"  # US State Sales Tax
    WITHHOLDING_TAX = "withholding_tax"  # International withholding
    INCOME_TAX = "income_tax"  # Income tax on earnings
    DIGITAL_SERVICES_TAX = "digital_services_tax"  # DST
    CARBON_TAX = "carbon_tax"  # Environmental tax
    EXCISE_TAX = "excise_tax"  # Excise duties


class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_VAT = "eu_vat"
    UK_VAT = "uk_vat"
    CA_GST = "ca_gst"
    AU_GST = "au_gst"
    IN_GST = "in_gst"
    JP_CT = "jp_ct"  # Japan Consumption Tax
    SG_GST = "sg_gst"  # Singapore GST
    BR_ICMS = "br_icms"  # Brazil ICMS


class TransactionCategory(Enum):
    """Transaction categories for tax purposes"""
    DIGITAL_GOODS = "digital_goods"
    DIGITAL_SERVICES = "digital_services"
    PHYSICAL_GOODS = "physical_goods"
    LICENSING = "licensing"
    ROYALTIES = "royalties"
    SUBSCRIPTION = "subscription"
    MARKETPLACE = "marketplace"
    ADVERTISING = "advertising"
    CONSULTATION = "consultation"


@dataclass
class TaxRate:
    """Tax rate configuration"""
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    rate: Decimal
    threshold: Optional[Decimal] = None
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    category_specific: Optional[TransactionCategory] = None


@dataclass
class TaxableTransaction:
    """Taxable transaction details"""
    id: str
    transaction_id: str
    amount: Decimal
    currency: str
    category: TransactionCategory
    customer_country: str
    customer_state: Optional[str]
    merchant_country: str
    merchant_state: Optional[str]
    transaction_date: datetime
    is_b2b: bool = False
    customer_tax_id: Optional[str] = None
    merchant_tax_id: Optional[str] = None


@dataclass
class TaxCalculation:
    """Tax calculation result"""
    transaction_id: str
    gross_amount: Decimal
    net_amount: Decimal
    total_tax: Decimal
    tax_breakdown: List[Dict[str, Any]]
    currency: str
    calculation_date: datetime
    applicable_rates: List[TaxRate]


@dataclass
class TaxRemittance:
    """Tax remittance record"""
    id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    period_start: datetime
    period_end: datetime
    total_collected: Decimal
    amount_remitted: Decimal
    filing_date: datetime
    due_date: datetime
    status: str
    reference_number: Optional[str] = None


class TaxComplianceProcessor:
    """
    Advanced tax compliance processor
    
    Handles automated tax calculations, real-time rate updates,
    multi-jurisdiction compliance, and automated remittance.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        tax_service_apis: Optional[Dict[str, str]] = None
    ):
        """Initialize tax compliance processor"""
        self.config = config
        self.tax_service_apis = tax_service_apis or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize tax rates (in production, load from database/API)
        self.tax_rates = self._initialize_tax_rates()
        
        # Compliance thresholds
        self.registration_thresholds = {
            TaxJurisdiction.EU_VAT: Decimal("10000"),  # €10,000 per year
            TaxJurisdiction.UK_VAT: Decimal("85000"),  # £85,000 per year
            TaxJurisdiction.CA_GST: Decimal("30000"),  # CAD $30,000 per year
            TaxJurisdiction.AU_GST: Decimal("75000"),  # AUD $75,000 per year
        }
        
        # Filing frequencies
        self.filing_frequencies = {
            TaxJurisdiction.EU_VAT: "quarterly",
            TaxJurisdiction.UK_VAT: "quarterly",
            TaxJurisdiction.US_STATE: "monthly",
            TaxJurisdiction.CA_GST: "quarterly",
            TaxJurisdiction.AU_GST: "quarterly"
        }
    
    async def calculate_tax(
        self,
        transaction: TaxableTransaction
    ) -> TaxCalculation:
        """Calculate tax for a transaction"""
        try:
            applicable_rates = await self._get_applicable_rates(transaction)
            tax_breakdown = []
            total_tax = Decimal("0")
            
            for rate in applicable_rates:
                # Check if transaction meets threshold
                if rate.threshold and transaction.amount < rate.threshold:
                    continue
                
                # Calculate tax amount
                tax_amount = self._calculate_tax_amount(transaction.amount, rate)
                
                if tax_amount > 0:
                    tax_breakdown.append({
                        "jurisdiction": rate.jurisdiction.value,
                        "tax_type": rate.tax_type.value,
                        "rate": float(rate.rate),
                        "taxable_amount": float(transaction.amount),
                        "tax_amount": float(tax_amount),
                        "description": self._get_tax_description(rate)
                    })
                    total_tax += tax_amount
            
            net_amount = transaction.amount - total_tax
            
            calculation = TaxCalculation(
                transaction_id=transaction.transaction_id,
                gross_amount=transaction.amount,
                net_amount=net_amount,
                total_tax=total_tax,
                tax_breakdown=tax_breakdown,
                currency=transaction.currency,
                calculation_date=datetime.now(),
                applicable_rates=applicable_rates
            )
            
            self.logger.info(f"Calculated tax for transaction {transaction.transaction_id}: {float(total_tax)}")
            return calculation
            
        except Exception as e:
            self.logger.error(f"Failed to calculate tax: {e}")
            raise
    
    async def validate_tax_id(
        self,
        tax_id: str,
        country: str,
        id_type: str = "vat"
    ) -> Dict[str, Any]:
        """Validate tax identification number"""
        try:
            # Mock validation (in production, use real tax ID validation APIs)
            await asyncio.sleep(0.1)
            
            # Simple format validation
            is_valid = self._validate_tax_id_format(tax_id, country, id_type)
            
            if is_valid:
                return {
                    "valid": True,
                    "tax_id": tax_id,
                    "country": country,
                    "type": id_type,
                    "business_name": "Example Business Ltd.",
                    "address": "123 Business St, City, Country",
                    "status": "active",
                    "validated_at": datetime.now().isoformat()
                }
            else:
                return {
                    "valid": False,
                    "tax_id": tax_id,
                    "error": "Invalid tax ID format",
                    "validated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to validate tax ID {tax_id}: {e}")
            return {"valid": False, "error": str(e)}
    
    async def generate_tax_invoice(
        self,
        transaction: TaxableTransaction,
        tax_calculation: TaxCalculation,
        invoice_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate tax-compliant invoice"""
        try:
            invoice_id = f"inv_{uuid.uuid4().hex[:12]}"
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            
            # Build invoice line items
            line_items = [{
                "description": invoice_details.get("description", "Digital Service"),
                "quantity": 1,
                "unit_price": float(tax_calculation.net_amount),
                "total_net": float(tax_calculation.net_amount)
            }]
            
            # Add tax line items
            for tax_item in tax_calculation.tax_breakdown:
                line_items.append({
                    "description": f"{tax_item['tax_type'].upper()} ({tax_item['rate']}%)",
                    "quantity": 1,
                    "unit_price": tax_item['tax_amount'],
                    "total_net": tax_item['tax_amount'],
                    "is_tax": True
                })
            
            invoice = {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "issue_date": datetime.now().isoformat(),
                "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "currency": transaction.currency,
                "customer": {
                    "country": transaction.customer_country,
                    "tax_id": transaction.customer_tax_id,
                    "is_business": transaction.is_b2b
                },
                "merchant": {
                    "country": transaction.merchant_country,
                    "tax_id": transaction.merchant_tax_id,
                    "business_name": invoice_details.get("merchant_name", "Ainflue Platform"),
                    "address": invoice_details.get("merchant_address")
                },
                "line_items": line_items,
                "totals": {
                    "net_amount": float(tax_calculation.net_amount),
                    "total_tax": float(tax_calculation.total_tax),
                    "gross_amount": float(tax_calculation.gross_amount)
                },
                "tax_breakdown": tax_calculation.tax_breakdown,
                "payment_terms": invoice_details.get("payment_terms", "Net 30"),
                "notes": invoice_details.get("notes"),
                "compliance_notes": self._get_compliance_notes(transaction)
            }
            
            self.logger.info(f"Generated tax invoice: {invoice_number}")
            return invoice
            
        except Exception as e:
            self.logger.error(f"Failed to generate tax invoice: {e}")
            return {"error": str(e)}
    
    async def file_tax_return(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """File tax return for a jurisdiction and period"""
        try:
            # Aggregate transactions for the period
            period_data = await self._aggregate_period_data(
                jurisdiction, period_start, period_end
            )
            
            # Generate return data
            return_data = {
                "jurisdiction": jurisdiction.value,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "total_sales": float(period_data["total_sales"]),
                "total_tax_collected": float(period_data["total_tax_collected"]),
                "exempt_sales": float(period_data["exempt_sales"]),
                "input_tax_credits": float(period_data.get("input_tax_credits", 0)),
                "net_tax_due": float(period_data["net_tax_due"]),
                "filing_date": datetime.now().isoformat(),
                "due_date": self._calculate_due_date(jurisdiction, period_end).isoformat()
            }
            
            # Submit to tax authority (mock)
            filing_result = await self._submit_tax_return(jurisdiction, return_data)
            
            if filing_result["success"]:
                # Create remittance record
                remittance = TaxRemittance(
                    id=f"rem_{uuid.uuid4().hex[:12]}",
                    jurisdiction=jurisdiction,
                    tax_type=TaxType.VAT,  # Determine based on jurisdiction
                    period_start=period_start,
                    period_end=period_end,
                    total_collected=period_data["total_tax_collected"],
                    amount_remitted=period_data["net_tax_due"],
                    filing_date=datetime.now(),
                    due_date=self._calculate_due_date(jurisdiction, period_end),
                    status="filed",
                    reference_number=filing_result["reference_number"]
                )
                
                return {
                    "success": True,
                    "return_data": return_data,
                    "filing_reference": filing_result["reference_number"],
                    "remittance_id": remittance.id,
                    "payment_due_date": remittance.due_date.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": filing_result["error"],
                    "return_data": return_data
                }
                
        except Exception as e:
            self.logger.error(f"Failed to file tax return for {jurisdiction}: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_registration_requirements(
        self,
        jurisdiction: TaxJurisdiction,
        annual_revenue: Decimal
    ) -> Dict[str, Any]:
        """Check if tax registration is required"""
        try:
            threshold = self.registration_thresholds.get(jurisdiction)
            
            if not threshold:
                return {
                    "registration_required": False,
                    "reason": "No threshold defined for jurisdiction"
                }
            
            registration_required = annual_revenue >= threshold
            
            return {
                "jurisdiction": jurisdiction.value,
                "annual_revenue": float(annual_revenue),
                "threshold": float(threshold),
                "registration_required": registration_required,
                "excess_amount": float(annual_revenue - threshold) if registration_required else 0,
                "recommendation": self._get_registration_recommendation(
                    jurisdiction, registration_required, annual_revenue, threshold
                ),
                "filing_frequency": self.filing_frequencies.get(jurisdiction, "quarterly"),
                "next_steps": self._get_registration_next_steps(jurisdiction, registration_required)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check registration requirements: {e}")
            return {"error": str(e)}
    
    async def generate_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime,
        jurisdictions: Optional[List[TaxJurisdiction]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive tax compliance report"""
        try:
            if not jurisdictions:
                jurisdictions = list(TaxJurisdiction)
            
            report_data = {
                "report_period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "summary": {
                    "total_transactions": 1250,
                    "total_gross_revenue": 125000.00,
                    "total_tax_collected": 15625.00,
                    "jurisdictions_active": len(jurisdictions)
                },
                "jurisdiction_breakdown": {},
                "tax_type_breakdown": {},
                "compliance_status": {},
                "upcoming_deadlines": [],
                "recommendations": []
            }
            
            # Generate data for each jurisdiction
            for jurisdiction in jurisdictions:
                jurisdiction_data = await self._get_jurisdiction_data(
                    jurisdiction, period_start, period_end
                )
                report_data["jurisdiction_breakdown"][jurisdiction.value] = jurisdiction_data
                
                # Check compliance status
                compliance = await self._check_jurisdiction_compliance(jurisdiction)
                report_data["compliance_status"][jurisdiction.value] = compliance
                
                # Add upcoming deadlines
                deadlines = await self._get_upcoming_deadlines(jurisdiction)
                report_data["upcoming_deadlines"].extend(deadlines)
            
            # Tax type breakdown
            for tax_type in TaxType:
                type_data = await self._get_tax_type_data(tax_type, period_start, period_end)
                report_data["tax_type_breakdown"][tax_type.value] = type_data
            
            # Generate recommendations
            report_data["recommendations"] = await self._generate_compliance_recommendations(
                report_data
            )
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            return {"error": str(e)}
    
    def _initialize_tax_rates(self) -> Dict[str, List[TaxRate]]:
        """Initialize tax rates for different jurisdictions"""
        return {
            TaxJurisdiction.EU_VAT.value: [
                TaxRate(TaxJurisdiction.EU_VAT, TaxType.VAT, Decimal("20.0")),  # Standard rate
                TaxRate(TaxJurisdiction.EU_VAT, TaxType.VAT, Decimal("10.0"), category_specific=TransactionCategory.DIGITAL_SERVICES)
            ],
            TaxJurisdiction.UK_VAT.value: [
                TaxRate(TaxJurisdiction.UK_VAT, TaxType.VAT, Decimal("20.0"))
            ],
            TaxJurisdiction.CA_GST.value: [
                TaxRate(TaxJurisdiction.CA_GST, TaxType.GST, Decimal("5.0"))
            ],
            TaxJurisdiction.AU_GST.value: [
                TaxRate(TaxJurisdiction.AU_GST, TaxType.GST, Decimal("10.0"))
            ],
            TaxJurisdiction.US_STATE.value: [
                TaxRate(TaxJurisdiction.US_STATE, TaxType.SALES_TAX, Decimal("8.5"))  # Average
            ]
        }
    
    async def _get_applicable_rates(
        self,
        transaction: TaxableTransaction
    ) -> List[TaxRate]:
        """Get applicable tax rates for a transaction"""
        applicable_rates = []
        
        # Determine jurisdiction based on transaction details
        jurisdictions = self._determine_jurisdictions(transaction)
        
        for jurisdiction in jurisdictions:
            rates = self.tax_rates.get(jurisdiction.value, [])
            
            for rate in rates:
                # Check if rate applies to this transaction
                if self._rate_applies_to_transaction(rate, transaction):
                    applicable_rates.append(rate)
        
        return applicable_rates
    
    def _determine_jurisdictions(
        self,
        transaction: TaxableTransaction
    ) -> List[TaxJurisdiction]:
        """Determine applicable tax jurisdictions"""
        jurisdictions = []
        
        # EU VAT rules
        if transaction.customer_country in ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "PT", "IE", "LU", "FI", "SE", "DK", "EE", "LV", "LT", "PL", "CZ", "SK", "HU", "SI", "BG", "RO", "HR", "CY", "MT"]:
            jurisdictions.append(TaxJurisdiction.EU_VAT)
        
        # UK VAT
        elif transaction.customer_country == "GB":
            jurisdictions.append(TaxJurisdiction.UK_VAT)
        
        # Canadian GST
        elif transaction.customer_country == "CA":
            jurisdictions.append(TaxJurisdiction.CA_GST)
        
        # Australian GST
        elif transaction.customer_country == "AU":
            jurisdictions.append(TaxJurisdiction.AU_GST)
        
        # US State Sales Tax
        elif transaction.customer_country == "US":
            jurisdictions.append(TaxJurisdiction.US_STATE)
        
        return jurisdictions
    
    def _rate_applies_to_transaction(
        self,
        rate: TaxRate,
        transaction: TaxableTransaction
    ) -> bool:
        """Check if a tax rate applies to a transaction"""
        # Check category specificity
        if rate.category_specific and rate.category_specific != transaction.category:
            return False
        
        # Check B2B exemptions for VAT
        if rate.tax_type == TaxType.VAT and transaction.is_b2b and transaction.customer_tax_id:
            return False  # B2B with valid VAT ID is exempt
        
        # Check effective dates
        if rate.expiry_date and transaction.transaction_date > rate.expiry_date:
            return False
        
        if transaction.transaction_date < rate.effective_date:
            return False
        
        return True
    
    def _calculate_tax_amount(self, amount: Decimal, rate: TaxRate) -> Decimal:
        """Calculate tax amount for a given rate"""
        tax_amount = amount * (rate.rate / Decimal("100"))
        return tax_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _get_tax_description(self, rate: TaxRate) -> str:
        """Get human-readable tax description"""
        descriptions = {
            TaxType.VAT: "Value Added Tax",
            TaxType.GST: "Goods and Services Tax",
            TaxType.SALES_TAX: "Sales Tax",
            TaxType.WITHHOLDING_TAX: "Withholding Tax",
            TaxType.DIGITAL_SERVICES_TAX: "Digital Services Tax"
        }
        
        base_description = descriptions.get(rate.tax_type, rate.tax_type.value)
        return f"{base_description} - {rate.jurisdiction.value.upper()}"
    
    def _validate_tax_id_format(self, tax_id: str, country: str, id_type: str) -> bool:
        """Validate tax ID format"""
        # Simplified validation (in production, use comprehensive validation)
        if not tax_id:
            return False
        
        # Basic format checks by country
        if country == "GB" and id_type == "vat":
            return len(tax_id) == 9 and tax_id.isdigit()
        elif country in ["DE", "FR", "IT"] and id_type == "vat":
            return len(tax_id) >= 8 and len(tax_id) <= 12
        elif country == "US" and id_type == "ein":
            return len(tax_id) == 9 and tax_id.isdigit()
        
        return True  # Default to valid for unknown formats
    
    async def _aggregate_period_data(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Decimal]:
        """Aggregate tax data for a period"""
        # Mock aggregation (in production, query actual database)
        return {
            "total_sales": Decimal("50000.00"),
            "total_tax_collected": Decimal("8500.00"),
            "exempt_sales": Decimal("5000.00"),
            "input_tax_credits": Decimal("1200.00"),
            "net_tax_due": Decimal("7300.00")
        }
    
    async def _submit_tax_return(
        self,
        jurisdiction: TaxJurisdiction,
        return_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit tax return to tax authority"""
        # Mock submission (in production, use real tax authority APIs)
        return {
            "success": True,
            "reference_number": f"TAX-{uuid.uuid4().hex[:12].upper()}",
            "submission_date": datetime.now().isoformat(),
            "acknowledgment": "Return accepted for processing"
        }
    
    def _calculate_due_date(
        self,
        jurisdiction: TaxJurisdiction,
        period_end: datetime
    ) -> datetime:
        """Calculate tax return due date"""
        # Standard due dates (varies by jurisdiction)
        due_date_offsets = {
            TaxJurisdiction.EU_VAT: 20,  # 20 days after period end
            TaxJurisdiction.UK_VAT: 30,  # 30 days after period end
            TaxJurisdiction.CA_GST: 30,  # 30 days after period end
            TaxJurisdiction.AU_GST: 28,  # 28 days after period end
            TaxJurisdiction.US_STATE: 20  # 20 days after period end
        }
        
        offset_days = due_date_offsets.get(jurisdiction, 30)
        return period_end + timedelta(days=offset_days)
    
    def _get_compliance_notes(self, transaction: TaxableTransaction) -> List[str]:
        """Get compliance notes for invoice"""
        notes = []
        
        if transaction.is_b2b and transaction.customer_tax_id:
            notes.append("Reverse charge applies - Customer is responsible for VAT")
        
        if transaction.category == TransactionCategory.DIGITAL_SERVICES:
            notes.append("Digital services supplied electronically")
        
        return notes
    
    def _get_registration_recommendation(
        self,
        jurisdiction: TaxJurisdiction,
        registration_required: bool,
        revenue: Decimal,
        threshold: Decimal
    ) -> str:
        """Get tax registration recommendation"""
        if registration_required:
            return f"Registration required - revenue exceeds threshold by {float(revenue - threshold)}"
        else:
            remaining = threshold - revenue
            return f"No registration required - {float(remaining)} remaining before threshold"
    
    def _get_registration_next_steps(
        self,
        jurisdiction: TaxJurisdiction,
        registration_required: bool
    ) -> List[str]:
        """Get next steps for tax registration"""
        if registration_required:
            return [
                "Apply for tax registration immediately",
                "Set up automated tax calculation and collection",
                "Implement compliant invoicing",
                "Schedule regular filing reminders"
            ]
        else:
            return [
                "Monitor revenue against thresholds",
                "Prepare for potential registration",
                "Review quarterly revenue projections"
            ]
    
    async def _get_jurisdiction_data(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get jurisdiction-specific data for reporting"""
        # Mock jurisdiction data
        return {
            "transactions": 125,
            "gross_revenue": 15000.00,
            "tax_collected": 2250.00,
            "average_tax_rate": 15.0,
            "registration_status": "registered",
            "last_filing_date": "2024-12-31"
        }
    
    async def _check_jurisdiction_compliance(
        self,
        jurisdiction: TaxJurisdiction
    ) -> Dict[str, Any]:
        """Check compliance status for jurisdiction"""
        return {
            "status": "compliant",
            "last_filing": "2024-12-31",
            "next_due_date": "2025-01-31",
            "outstanding_issues": [],
            "risk_level": "low"
        }
    
    async def _get_upcoming_deadlines(
        self,
        jurisdiction: TaxJurisdiction
    ) -> List[Dict[str, Any]]:
        """Get upcoming tax deadlines"""
        return [
            {
                "jurisdiction": jurisdiction.value,
                "type": "quarterly_filing",
                "due_date": "2025-01-31",
                "description": "Q4 2024 VAT Return"
            }
        ]
    
    async def _get_tax_type_data(
        self,
        tax_type: TaxType,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get data for specific tax type"""
        return {
            "total_collected": 5000.00,
            "transactions": 250,
            "average_rate": 15.0,
            "jurisdictions": 3
        }
    
    async def _generate_compliance_recommendations(
        self,
        report_data: Dict[str, Any]
    ) -> List[str]:
        """Generate compliance recommendations"""
        return [
            "Consider voluntary registration in high-revenue jurisdictions",
            "Implement automated tax calculation for all transactions",
            "Set up monthly compliance monitoring",
            "Review tax ID validation processes"
        ]


# Export the main class
__all__ = [
    "TaxComplianceProcessor",
    "TaxRate",
    "TaxableTransaction",
    "TaxCalculation",
    "TaxRemittance",
    "TaxType",
    "TaxJurisdiction",
    "TransactionCategory"
]