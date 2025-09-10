"""
Tax Calculator Core - Advanced Tax Calculation and Compliance System
====================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for tax calculation, tax compliance,
multi-jurisdiction tax handling, and automated tax reporting.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid

# Get logger
logger = logging.getLogger(__name__)

class TaxType(Enum):
    """Types of taxes"""
    INCOME = "income"
    VAT = "vat"
    GST = "gst"
    SALES = "sales"
    WITHHOLDING = "withholding"
    DIGITAL_SERVICES = "digital_services"
    CARBON = "carbon"

class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    US = "us"
    EU = "eu"
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GERMANY = "germany"
    FRANCE = "france"
    NETHERLANDS = "netherlands"

class TaxableEntity(Enum):
    """Taxable entity types"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    NON_PROFIT = "non_profit"

@dataclass
class TaxRate:
    """Tax rate information"""
    rate_id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    rate_percentage: Decimal
    threshold_amount: Decimal
    effective_date: datetime
    expiry_date: Optional[datetime]
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaxCalculationResult:
    """Tax calculation result"""
    calculation_id: str
    gross_amount: Decimal
    net_amount: Decimal
    total_tax: Decimal
    tax_breakdown: Dict[str, Decimal]
    jurisdiction: TaxJurisdiction
    entity_type: TaxableEntity
    calculation_date: datetime
    applicable_rates: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class TaxCalculatorCore:
    """Advanced Tax Calculator Core System"""
    
    def __init__(self, level: str = "enterprise"):
        self.version = "2.1.0"
        self.level = level
        self.tax_rates = {}
        self.calculation_history = {}
        self.tax_rules = {}
        self.compliance_cache = {}
        
        # Initialize default tax rates
        self._initialize_default_rates()
        
        logger.info(f"Tax Calculator Core initialized - Level: {level}")

    def _initialize_default_rates(self):
        """Initialize default tax rates for common jurisdictions"""
        default_rates = [
            # US rates
            TaxRate("us_income_standard", TaxJurisdiction.US, TaxType.INCOME, 
                   Decimal("22.0"), Decimal("0"), datetime(2024, 1, 1), None, "US Standard Income Tax"),
            TaxRate("us_sales_standard", TaxJurisdiction.US, TaxType.SALES, 
                   Decimal("8.5"), Decimal("0"), datetime(2024, 1, 1), None, "US Average Sales Tax"),
            
            # EU rates
            TaxRate("eu_vat_standard", TaxJurisdiction.EU, TaxType.VAT, 
                   Decimal("20.0"), Decimal("0"), datetime(2024, 1, 1), None, "EU Standard VAT"),
            TaxRate("eu_digital_services", TaxJurisdiction.EU, TaxType.DIGITAL_SERVICES, 
                   Decimal("3.0"), Decimal("750000"), datetime(2024, 1, 1), None, "EU Digital Services Tax"),
            
            # Germany rates
            TaxRate("de_vat_standard", TaxJurisdiction.GERMANY, TaxType.VAT, 
                   Decimal("19.0"), Decimal("0"), datetime(2024, 1, 1), None, "German Standard VAT"),
            TaxRate("de_income_standard", TaxJurisdiction.GERMANY, TaxType.INCOME, 
                   Decimal("42.0"), Decimal("58596"), datetime(2024, 1, 1), None, "German Income Tax"),
            
            # UK rates
            TaxRate("uk_vat_standard", TaxJurisdiction.UK, TaxType.VAT, 
                   Decimal("20.0"), Decimal("0"), datetime(2024, 1, 1), None, "UK Standard VAT"),
            TaxRate("uk_income_basic", TaxJurisdiction.UK, TaxType.INCOME, 
                   Decimal("20.0"), Decimal("12570"), datetime(2024, 1, 1), None, "UK Basic Rate Income Tax"),
        ]
        
        for rate in default_rates:
            self.tax_rates[rate.rate_id] = rate

    async def calculate_tax(self, amount: Decimal, jurisdiction: TaxJurisdiction, 
                           entity_type: TaxableEntity, tax_types: List[TaxType] = None) -> TaxCalculationResult:
        """Calculate tax for given amount and parameters"""
        try:
            calculation_id = f"calc_{uuid.uuid4().hex[:12]}"
            
            if tax_types is None:
                tax_types = [TaxType.VAT, TaxType.INCOME]
            
            tax_breakdown = {}
            total_tax = Decimal("0")
            applicable_rates = []
            
            for tax_type in tax_types:
                tax_amount = await self._calculate_tax_by_type(amount, jurisdiction, entity_type, tax_type)
                if tax_amount > 0:
                    tax_breakdown[tax_type.value] = tax_amount
                    total_tax += tax_amount
                    
                    # Find applicable rate
                    rate = self._find_applicable_rate(jurisdiction, tax_type, amount)
                    if rate:
                        applicable_rates.append(rate.rate_id)
            
            # Apply rounding
            total_tax = total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            net_amount = amount - total_tax
            
            result = TaxCalculationResult(
                calculation_id=calculation_id,
                gross_amount=amount,
                net_amount=net_amount,
                total_tax=total_tax,
                tax_breakdown=tax_breakdown,
                jurisdiction=jurisdiction,
                entity_type=entity_type,
                calculation_date=datetime.now(),
                applicable_rates=applicable_rates,
                metadata={
                    "calculation_method": "standard",
                    "tax_types_applied": [t.value for t in tax_types]
                }
            )
            
            # Store calculation
            self.calculation_history[calculation_id] = result
            
            logger.info(f"Tax calculated: {calculation_id}, Amount: {amount}, Tax: {total_tax}")
            return result
            
        except Exception as e:
            logger.error(f"Tax calculation failed: {str(e)}")
            return TaxCalculationResult(
                calculation_id="error",
                gross_amount=amount,
                net_amount=amount,
                total_tax=Decimal("0"),
                tax_breakdown={},
                jurisdiction=jurisdiction,
                entity_type=entity_type,
                calculation_date=datetime.now(),
                applicable_rates=[]
            )

    async def _calculate_tax_by_type(self, amount: Decimal, jurisdiction: TaxJurisdiction, 
                                    entity_type: TaxableEntity, tax_type: TaxType) -> Decimal:
        """Calculate tax for specific tax type"""
        try:
            rate = self._find_applicable_rate(jurisdiction, tax_type, amount)
            if not rate:
                return Decimal("0")
            
            # Check if amount meets threshold
            if amount < rate.threshold_amount:
                return Decimal("0")
            
            # Calculate taxable amount (amount above threshold)
            taxable_amount = amount - rate.threshold_amount
            
            # Apply progressive tax rules for income tax
            if tax_type == TaxType.INCOME:
                return await self._calculate_progressive_tax(taxable_amount, jurisdiction, entity_type)
            else:
                # Simple percentage calculation for other taxes
                tax_amount = taxable_amount * (rate.rate_percentage / Decimal("100"))
                return tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Tax calculation by type failed: {str(e)}")
            return Decimal("0")

    def _find_applicable_rate(self, jurisdiction: TaxJurisdiction, tax_type: TaxType, amount: Decimal) -> Optional[TaxRate]:
        """Find applicable tax rate"""
        # Find rates for jurisdiction and tax type
        applicable_rates = [
            rate for rate in self.tax_rates.values()
            if rate.jurisdiction == jurisdiction and rate.tax_type == tax_type
            and (rate.expiry_date is None or rate.expiry_date > datetime.now())
            and rate.effective_date <= datetime.now()
        ]
        
        if not applicable_rates:
            return None
        
        # Return the most applicable rate (highest threshold that amount meets)
        valid_rates = [rate for rate in applicable_rates if amount >= rate.threshold_amount]
        if not valid_rates:
            return applicable_rates[0]  # Return lowest threshold rate
        
        return max(valid_rates, key=lambda r: r.threshold_amount)

    async def _calculate_progressive_tax(self, amount: Decimal, jurisdiction: TaxJurisdiction, 
                                        entity_type: TaxableEntity) -> Decimal:
        """Calculate progressive tax (for income tax)"""
        try:
            # Progressive tax brackets (simplified)
            brackets = {
                TaxJurisdiction.US: [
                    (Decimal("10275"), Decimal("10.0")),
                    (Decimal("41775"), Decimal("12.0")),
                    (Decimal("89450"), Decimal("22.0")),
                    (Decimal("190750"), Decimal("24.0")),
                    (Decimal("float('inf')"), Decimal("37.0"))
                ],
                TaxJurisdiction.GERMANY: [
                    (Decimal("10908"), Decimal("14.0")),
                    (Decimal("15999"), Decimal("24.0")),
                    (Decimal("62809"), Decimal("42.0")),
                    (Decimal("float('inf')"), Decimal("45.0"))
                ],
                TaxJurisdiction.UK: [
                    (Decimal("37700"), Decimal("20.0")),
                    (Decimal("125140"), Decimal("40.0")),
                    (Decimal("float('inf')"), Decimal("45.0"))
                ]
            }
            
            jurisdiction_brackets = brackets.get(jurisdiction, [(Decimal("float('inf')"), Decimal("20.0"))])
            
            total_tax = Decimal("0")
            remaining_amount = amount
            
            for threshold, rate in jurisdiction_brackets:
                if remaining_amount <= 0:
                    break
                
                taxable_in_bracket = min(remaining_amount, threshold)
                tax_in_bracket = taxable_in_bracket * (rate / Decimal("100"))
                total_tax += tax_in_bracket
                remaining_amount -= taxable_in_bracket
            
            return total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Progressive tax calculation failed: {str(e)}")
            return amount * Decimal("0.2")  # Fallback to 20%

    async def get_tax_compliance_status(self, entity_id: str, jurisdiction: TaxJurisdiction) -> Dict[str, Any]:
        """Get tax compliance status for entity"""
        try:
            # Find calculations for entity
            entity_calculations = [
                calc for calc in self.calculation_history.values()
                if calc.metadata.get("entity_id") == entity_id and calc.jurisdiction == jurisdiction
            ]
            
            if not entity_calculations:
                return {"status": "no_data", "compliance_score": 0}
            
            # Calculate compliance metrics
            total_calculations = len(entity_calculations)
            total_tax_calculated = sum(calc.total_tax for calc in entity_calculations)
            avg_tax_rate = (total_tax_calculated / sum(calc.gross_amount for calc in entity_calculations)) * 100
            
            # Mock compliance score
            compliance_score = min(100, 70 + (total_calculations * 2))  # Improve with more calculations
            
            compliance_status = {
                "entity_id": entity_id,
                "jurisdiction": jurisdiction.value,
                "status": "compliant" if compliance_score >= 80 else "needs_attention",
                "compliance_score": compliance_score,
                "total_calculations": total_calculations,
                "total_tax_calculated": float(total_tax_calculated),
                "average_tax_rate": float(avg_tax_rate),
                "last_calculation": max(calc.calculation_date for calc in entity_calculations).isoformat(),
                "recommendations": self._generate_compliance_recommendations(compliance_score, jurisdiction)
            }
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Failed to get tax compliance status: {str(e)}")
            return {"status": "error", "compliance_score": 0}

    def _generate_compliance_recommendations(self, score: float, jurisdiction: TaxJurisdiction) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.extend([
                "Implement automated tax calculation",
                "Review tax filing requirements",
                "Consider professional tax consultation"
            ])
        elif score < 80:
            recommendations.extend([
                "Optimize tax calculation accuracy",
                "Implement tax rate monitoring",
                "Review quarterly tax obligations"
            ])
        else:
            recommendations.extend([
                "Maintain current compliance standards",
                "Monitor regulatory changes",
                "Consider tax optimization strategies"
            ])
        
        # Jurisdiction-specific recommendations
        if jurisdiction == TaxJurisdiction.EU:
            recommendations.append("Monitor VAT MOSS requirements")
        elif jurisdiction == TaxJurisdiction.US:
            recommendations.append("Track sales tax nexus requirements")
        
        return recommendations

    async def generate_tax_report(self, entity_id: str, time_period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate tax report for entity and time period"""
        try:
            # Filter calculations for entity and time period
            relevant_calculations = [
                calc for calc in self.calculation_history.values()
                if calc.metadata.get("entity_id") == entity_id
                and time_period[0] <= calc.calculation_date <= time_period[1]
            ]
            
            if not relevant_calculations:
                return {"error": "No calculations found for specified period"}
            
            # Aggregate data
            total_gross = sum(calc.gross_amount for calc in relevant_calculations)
            total_net = sum(calc.net_amount for calc in relevant_calculations)
            total_tax = sum(calc.total_tax for calc in relevant_calculations)
            
            # Tax breakdown by type
            tax_by_type = {}
            for calc in relevant_calculations:
                for tax_type, amount in calc.tax_breakdown.items():
                    tax_by_type[tax_type] = tax_by_type.get(tax_type, Decimal("0")) + amount
            
            # Tax breakdown by jurisdiction
            tax_by_jurisdiction = {}
            for calc in relevant_calculations:
                jurisdiction = calc.jurisdiction.value
                tax_by_jurisdiction[jurisdiction] = tax_by_jurisdiction.get(jurisdiction, Decimal("0")) + calc.total_tax
            
            report = {
                "entity_id": entity_id,
                "report_period": {
                    "start": time_period[0].isoformat(),
                    "end": time_period[1].isoformat()
                },
                "summary": {
                    "total_transactions": len(relevant_calculations),
                    "total_gross_amount": float(total_gross),
                    "total_net_amount": float(total_net),
                    "total_tax_amount": float(total_tax),
                    "average_tax_rate": float((total_tax / total_gross * 100)) if total_gross > 0 else 0
                },
                "tax_breakdown_by_type": {k: float(v) for k, v in tax_by_type.items()},
                "tax_breakdown_by_jurisdiction": {k: float(v) for k, v in tax_by_jurisdiction.items()},
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Tax report generated for entity {entity_id}")
            return report
            
        except Exception as e:
            logger.error(f"Tax report generation failed: {str(e)}")
            return {"error": str(e)}

# Module exports
__all__ = [
    "TaxCalculatorCore",
    "TaxType",
    "TaxJurisdiction", 
    "TaxableEntity",
    "TaxRate",
    "TaxCalculationResult"
]

logger.info("💰 Tax Calculator Core module loaded")