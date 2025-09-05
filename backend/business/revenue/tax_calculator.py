"""Tax Calculation Engine - IA Influencer Agent Platform
=====================================================

Advanced multi-jurisdiction tax calculation system for content creators
and influencers with comprehensive compliance and reporting capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TaxJurisdiction(Enum):
    """Tax jurisdictions supported."""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_VAT = "eu_vat"
    UK_VAT = "uk_vat"
    CANADA_GST = "canada_gst"
    AUSTRALIA_GST = "australia_gst"


class TaxType(Enum):
    """Types of taxes."""
    INCOME_TAX = "income_tax"
    VALUE_ADDED_TAX = "value_added_tax"
    SALES_TAX = "sales_tax"
    WITHHOLDING_TAX = "withholding_tax"
    SELF_EMPLOYMENT_TAX = "self_employment_tax"


@dataclass
class TaxCalculation:
    """Tax calculation result."""
    calculation_id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    gross_amount: Decimal
    taxable_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    deductions: List[Dict[str, Any]]
    calculation_date: datetime


class TaxCalculationEngine:
    """Advanced tax calculation engine with multi-jurisdiction support."""
    
    def __init__(self, creator_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize tax calculation engine."""
        self.creator_id = creator_id
        self.config = config or {}
        self.tax_rates = self._initialize_tax_rates()
        self.calculation_history: List[TaxCalculation] = []
        
    async def calculate_comprehensive_taxes(
        self,
        revenue_data: Dict[str, Any],
        jurisdictions: List[TaxJurisdiction],
        creator_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive tax obligations across multiple jurisdictions."""
        try:
            tax_calculations = []
            total_tax_liability = Decimal('0')
            
            for jurisdiction in jurisdictions:
                # Calculate taxes for each jurisdiction
                jurisdiction_calculations = await self._calculate_jurisdiction_taxes(
                    revenue_data, jurisdiction, creator_profile
                )
                
                tax_calculations.extend(jurisdiction_calculations)
                
                # Sum up tax liability
                for calc in jurisdiction_calculations:
                    total_tax_liability += calc.tax_amount
            
            # Generate tax optimization recommendations
            optimization_recommendations = await self._generate_tax_optimization_recommendations(
                tax_calculations, creator_profile
            )
            
            # Calculate effective tax rate
            gross_revenue = Decimal(str(revenue_data.get('gross_revenue', 0)))
            effective_tax_rate = (total_tax_liability / gross_revenue * 100) if gross_revenue > 0 else Decimal('0')
            
            return {
                "calculation_id": str(uuid.uuid4()),
                "creator_id": self.creator_id,
                "tax_calculations": [self._serialize_calculation(calc) for calc in tax_calculations],
                "total_tax_liability": float(total_tax_liability),
                "effective_tax_rate": float(effective_tax_rate),
                "net_revenue": float(gross_revenue - total_tax_liability),
                "optimization_recommendations": optimization_recommendations,
                "calculation_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Tax calculation failed: {e}")
            raise
    
    async def calculate_quarterly_estimates(
        self,
        projected_revenue: Decimal,
        jurisdiction: TaxJurisdiction,
        creator_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate quarterly tax estimates for planning purposes."""
        try:
            # Calculate annual projected taxes
            annual_revenue_data = {
                'gross_revenue': float(projected_revenue * 4),  # Quarterly to annual
                'business_expenses': creator_profile.get('projected_expenses', 0),
                'revenue_streams': creator_profile.get('revenue_streams', [])
            }
            
            annual_calculations = await self._calculate_jurisdiction_taxes(
                annual_revenue_data, jurisdiction, creator_profile
            )
            
            # Calculate quarterly amounts
            quarterly_estimates = []
            for calc in annual_calculations:
                quarterly_amount = calc.tax_amount / 4
                quarterly_estimates.append({
                    'tax_type': calc.tax_type.value,
                    'annual_estimate': float(calc.tax_amount),
                    'quarterly_estimate': float(quarterly_amount),
                    'due_dates': await self._get_quarterly_due_dates(jurisdiction, calc.tax_type)
                })
            
            total_quarterly_estimate = sum(est['quarterly_estimate'] for est in quarterly_estimates)
            
            return {
                "jurisdiction": jurisdiction.value,
                "projected_annual_revenue": float(projected_revenue * 4),
                "quarterly_estimates": quarterly_estimates,
                "total_quarterly_estimate": total_quarterly_estimate,
                "payment_schedule": await self._generate_payment_schedule(quarterly_estimates)
            }
            
        except Exception as e:
            logger.error(f"Quarterly tax estimation failed: {e}")
            raise
    
    def _initialize_tax_rates(self) -> Dict[str, Dict[str, float]]:
        """Initialize tax rates for different jurisdictions."""
        return {
            'us_federal': {
                'income_tax_brackets': [
                    {'min': 0, 'max': 10275, 'rate': 0.10},
                    {'min': 10275, 'max': 41775, 'rate': 0.12},
                    {'min': 41775, 'max': 89450, 'rate': 0.22},
                    {'min': 89450, 'max': 190750, 'rate': 0.24},
                    {'min': 190750, 'max': 364200, 'rate': 0.32},
                    {'min': 364200, 'max': 462550, 'rate': 0.35},
                    {'min': 462550, 'max': float('inf'), 'rate': 0.37}
                ],
                'self_employment_tax': 0.1413  # 14.13% for 2024
            },
            'eu_vat': {
                'standard_rate': 0.20,  # 20% standard VAT rate
                'reduced_rates': [0.05, 0.10],
                'threshold': 10000  # VAT registration threshold
            },
            'uk_vat': {
                'standard_rate': 0.20,  # 20% VAT
                'reduced_rate': 0.05,   # 5% reduced rate
                'threshold': 85000      # VAT registration threshold
            },
            'canada_gst': {
                'federal_gst': 0.05,    # 5% GST
                'provincial_rates': {
                    'ON': 0.08,  # HST Ontario
                    'BC': 0.07,  # PST British Columbia
                    'QC': 0.09975  # QST Quebec
                }
            }
        }
    
    async def _calculate_jurisdiction_taxes(
        self,
        revenue_data: Dict[str, Any],
        jurisdiction: TaxJurisdiction,
        creator_profile: Dict[str, Any]
    ) -> List[TaxCalculation]:
        """Calculate taxes for a specific jurisdiction."""
        calculations = []
        
        if jurisdiction == TaxJurisdiction.US_FEDERAL:
            calculations.extend(await self._calculate_us_federal_taxes(revenue_data, creator_profile))
        elif jurisdiction == TaxJurisdiction.EU_VAT:
            calculations.extend(await self._calculate_eu_vat_taxes(revenue_data, creator_profile))
        elif jurisdiction == TaxJurisdiction.UK_VAT:
            calculations.extend(await self._calculate_uk_vat_taxes(revenue_data, creator_profile))
        elif jurisdiction == TaxJurisdiction.CANADA_GST:
            calculations.extend(await self._calculate_canada_gst_taxes(revenue_data, creator_profile))
        
        return calculations
    
    async def _calculate_us_federal_taxes(
        self,
        revenue_data: Dict[str, Any],
        creator_profile: Dict[str, Any]
    ) -> List[TaxCalculation]:
        """Calculate US federal income and self-employment taxes."""
        calculations = []
        
        gross_revenue = Decimal(str(revenue_data.get('gross_revenue', 0)))
        business_expenses = Decimal(str(revenue_data.get('business_expenses', 0)))
        
        # Calculate taxable income
        taxable_income = gross_revenue - business_expenses
        
        # Apply standard deduction for self-employed
        standard_deduction = Decimal('13850')  # 2024 standard deduction (single)
        taxable_income_after_deduction = max(Decimal('0'), taxable_income - standard_deduction)
        
        # Calculate income tax using brackets
        income_tax = await self._calculate_progressive_tax(
            taxable_income_after_deduction,
            self.tax_rates['us_federal']['income_tax_brackets']
        )
        
        # Income tax calculation
        income_tax_calc = TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            jurisdiction=TaxJurisdiction.US_FEDERAL,
            tax_type=TaxType.INCOME_TAX,
            gross_amount=gross_revenue,
            taxable_amount=taxable_income_after_deduction,
            tax_rate=Decimal('0'),  # Progressive rate
            tax_amount=income_tax,
            net_amount=gross_revenue - income_tax,
            deductions=[
                {'type': 'business_expenses', 'amount': float(business_expenses)},
                {'type': 'standard_deduction', 'amount': float(standard_deduction)}
            ],
            calculation_date=datetime.utcnow()
        )
        calculations.append(income_tax_calc)
        
        # Calculate self-employment tax
        se_tax_rate = Decimal(str(self.tax_rates['us_federal']['self_employment_tax']))
        se_tax_amount = taxable_income * se_tax_rate
        
        se_tax_calc = TaxCalculation(
            calculation_id=str(uuid.uuid4()),
            jurisdiction=TaxJurisdiction.US_FEDERAL,
            tax_type=TaxType.SELF_EMPLOYMENT_TAX,
            gross_amount=gross_revenue,
            taxable_amount=taxable_income,
            tax_rate=se_tax_rate,
            tax_amount=se_tax_amount,
            net_amount=taxable_income - se_tax_amount,
            deductions=[],
            calculation_date=datetime.utcnow()
        )
        calculations.append(se_tax_calc)
        
        return calculations
    
    async def _calculate_progressive_tax(
        self,
        taxable_income: Decimal,
        tax_brackets: List[Dict[str, Any]]
    ) -> Decimal:
        """Calculate tax using progressive tax brackets."""
        total_tax = Decimal('0')
        
        for bracket in tax_brackets:
            bracket_min = Decimal(str(bracket['min']))
            bracket_max = Decimal(str(bracket['max']))
            rate = Decimal(str(bracket['rate']))
            
            if taxable_income <= bracket_min:
                break
            
            # Calculate taxable amount in this bracket
            if taxable_income <= bracket_max:
                bracket_taxable = taxable_income - bracket_min
            else:
                bracket_taxable = bracket_max - bracket_min
            
            # Calculate tax for this bracket
            bracket_tax = bracket_taxable * rate
            total_tax += bracket_tax
            
            if taxable_income <= bracket_max:
                break
        
        return total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_eu_vat_taxes(
        self,
        revenue_data: Dict[str, Any],
        creator_profile: Dict[str, Any]
    ) -> List[TaxCalculation]:
        """Calculate EU VAT taxes."""
        calculations = []
        
        gross_revenue = Decimal(str(revenue_data.get('gross_revenue', 0)))
        vat_threshold = Decimal(str(self.tax_rates['eu_vat']['threshold']))
        
        # Check if VAT registration is required
        if gross_revenue >= vat_threshold:
            vat_rate = Decimal(str(self.tax_rates['eu_vat']['standard_rate']))
            vat_amount = gross_revenue * vat_rate
            
            vat_calc = TaxCalculation(
                calculation_id=str(uuid.uuid4()),
                jurisdiction=TaxJurisdiction.EU_VAT,
                tax_type=TaxType.VALUE_ADDED_TAX,
                gross_amount=gross_revenue,
                taxable_amount=gross_revenue,
                tax_rate=vat_rate,
                tax_amount=vat_amount,
                net_amount=gross_revenue - vat_amount,
                deductions=[],
                calculation_date=datetime.utcnow()
            )
            calculations.append(vat_calc)
        
        return calculations
    
    async def _calculate_uk_vat_taxes(
        self,
        revenue_data: Dict[str, Any],
        creator_profile: Dict[str, Any]
    ) -> List[TaxCalculation]:
        """Calculate UK VAT taxes."""
        calculations = []
        
        gross_revenue = Decimal(str(revenue_data.get('gross_revenue', 0)))
        vat_threshold = Decimal(str(self.tax_rates['uk_vat']['threshold']))
        
        # Check if VAT registration is required
        if gross_revenue >= vat_threshold:
            # Determine VAT rate based on service type
            service_type = creator_profile.get('service_type', 'standard')
            if service_type in ['digital_content', 'standard']:
                vat_rate = Decimal(str(self.tax_rates['uk_vat']['standard_rate']))
            else:
                vat_rate = Decimal(str(self.tax_rates['uk_vat']['reduced_rate']))
            
            vat_amount = gross_revenue * vat_rate
            
            vat_calc = TaxCalculation(
                calculation_id=str(uuid.uuid4()),
                jurisdiction=TaxJurisdiction.UK_VAT,
                tax_type=TaxType.VALUE_ADDED_TAX,
                gross_amount=gross_revenue,
                taxable_amount=gross_revenue,
                tax_rate=vat_rate,
                tax_amount=vat_amount,
                net_amount=gross_revenue - vat_amount,
                deductions=[],
                calculation_date=datetime.utcnow()
            )
            calculations.append(vat_calc)
        
        return calculations
    
    async def _calculate_canada_gst_taxes(
        self,
        revenue_data: Dict[str, Any],
        creator_profile: Dict[str, Any]
    ) -> List[TaxCalculation]:
        """Calculate Canada GST/HST taxes."""
        calculations = []
        
        gross_revenue = Decimal(str(revenue_data.get('gross_revenue', 0)))
        province = creator_profile.get('province', 'ON')
        
        # GST threshold is $30,000 CAD
        gst_threshold = Decimal('30000')
        
        if gross_revenue >= gst_threshold:
            # Federal GST
            gst_rate = Decimal(str(self.tax_rates['canada_gst']['federal_gst']))
            gst_amount = gross_revenue * gst_rate
            
            gst_calc = TaxCalculation(
                calculation_id=str(uuid.uuid4()),
                jurisdiction=TaxJurisdiction.CANADA_GST,
                tax_type=TaxType.VALUE_ADDED_TAX,
                gross_amount=gross_revenue,
                taxable_amount=gross_revenue,
                tax_rate=gst_rate,
                tax_amount=gst_amount,
                net_amount=gross_revenue - gst_amount,
                deductions=[],
                calculation_date=datetime.utcnow()
            )
            calculations.append(gst_calc)
            
            # Provincial tax if applicable
            provincial_rates = self.tax_rates['canada_gst']['provincial_rates']
            if province in provincial_rates:
                provincial_rate = Decimal(str(provincial_rates[province]))
                provincial_amount = gross_revenue * provincial_rate
                
                provincial_calc = TaxCalculation(
                    calculation_id=str(uuid.uuid4()),
                    jurisdiction=TaxJurisdiction.CANADA_GST,
                    tax_type=TaxType.SALES_TAX,
                    gross_amount=gross_revenue,
                    taxable_amount=gross_revenue,
                    tax_rate=provincial_rate,
                    tax_amount=provincial_amount,
                    net_amount=gross_revenue - provincial_amount,
                    deductions=[],
                    calculation_date=datetime.utcnow()
                )
                calculations.append(provincial_calc)
        
        return calculations
    
    async def _generate_tax_optimization_recommendations(
        self,
        tax_calculations: List[TaxCalculation],
        creator_profile: Dict[str, Any]
    ) -> List[str]:
        """Generate tax optimization recommendations."""
        recommendations = []
        
        # Calculate total tax burden
        total_tax = sum(calc.tax_amount for calc in tax_calculations)
        total_gross = sum(calc.gross_amount for calc in tax_calculations)
        
        if total_gross > 0:
            effective_rate = float(total_tax / total_gross)
            
            if effective_rate > 0.30:  # High tax burden
                recommendations.extend([
                    "High tax burden detected - consider business expense optimization",
                    "Explore retirement account contributions for tax deferral",
                    "Investigate business entity restructuring options"
                ])
            
            # Business expense recommendations
            business_expenses = creator_profile.get('business_expenses', 0)
            if business_expenses < float(total_gross) * 0.20:  # Low business expenses
                recommendations.extend([
                    "Consider maximizing deductible business expenses",
                    "Track equipment, software, and professional development costs",
                    "Maintain detailed records for home office deductions"
                ])
        
        # Jurisdiction-specific recommendations
        jurisdictions = set(calc.jurisdiction for calc in tax_calculations)
        
        if TaxJurisdiction.US_FEDERAL in jurisdictions:
            recommendations.extend([
                "Consider quarterly estimated tax payments to avoid penalties",
                "Explore SEP-IRA or Solo 401(k) for retirement savings",
                "Track mileage and travel expenses for business use"
            ])
        
        if any(j in [TaxJurisdiction.EU_VAT, TaxJurisdiction.UK_VAT] for j in jurisdictions):
            recommendations.extend([
                "Monitor VAT thresholds for registration requirements",
                "Consider VAT-inclusive pricing strategies",
                "Maintain proper VAT records and invoicing"
            ])
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    async def _get_quarterly_due_dates(
        self,
        jurisdiction: TaxJurisdiction,
        tax_type: TaxType
    ) -> List[str]:
        """Get quarterly tax payment due dates."""
        if jurisdiction == TaxJurisdiction.US_FEDERAL:
            return [
                "2024-04-15",  # Q1
                "2024-06-17",  # Q2
                "2024-09-16",  # Q3
                "2025-01-15"   # Q4
            ]
        elif jurisdiction in [TaxJurisdiction.EU_VAT, TaxJurisdiction.UK_VAT]:
            return [
                "2024-05-07",   # Q1
                "2024-08-07",   # Q2
                "2024-11-07",   # Q3
                "2025-02-07"    # Q4
            ]
        else:
            # Default quarterly dates
            return [
                "2024-04-30",
                "2024-07-31",
                "2024-10-31",
                "2025-01-31"
            ]
    
    async def _generate_payment_schedule(
        self,
        quarterly_estimates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimal tax payment schedule."""
        payment_schedule = []
        
        for i, quarter in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
            quarter_total = sum(est['quarterly_estimate'] for est in quarterly_estimates)
            
            # Get the earliest due date for this quarter
            due_dates = []
            for est in quarterly_estimates:
                if est['due_dates'] and len(est['due_dates']) > i:
                    due_dates.append(est['due_dates'][i])
            
            earliest_due = min(due_dates) if due_dates else f"2024-{(i+1)*3:02d}-15"
            
            payment_schedule.append({
                'quarter': quarter,
                'total_amount': round(quarter_total, 2),
                'due_date': earliest_due,
                'payment_breakdown': [
                    {
                        'tax_type': est['tax_type'],
                        'amount': round(est['quarterly_estimate'], 2)
                    }
                    for est in quarterly_estimates
                ]
            })
        
        return payment_schedule
    
    def _serialize_calculation(self, calculation: TaxCalculation) -> Dict[str, Any]:
        """Serialize tax calculation for JSON output."""
        return {
            'calculation_id': calculation.calculation_id,
            'jurisdiction': calculation.jurisdiction.value,
            'tax_type': calculation.tax_type.value,
            'gross_amount': float(calculation.gross_amount),
            'taxable_amount': float(calculation.taxable_amount),
            'tax_rate': float(calculation.tax_rate),
            'tax_amount': float(calculation.tax_amount),
            'net_amount': float(calculation.net_amount),
            'deductions': calculation.deductions,
            'calculation_date': calculation.calculation_date.isoformat()
        }