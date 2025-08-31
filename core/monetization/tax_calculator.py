"""Advanced Tax Calculator System
Multi-jurisdiction tax calculation and compliance management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ...database.models import User, TaxRecord


class TaxJurisdiction(Enum):
    """Supported tax jurisdictions"""
    GERMANY = "DE"
    UNITED_STATES = "US"
    UNITED_KINGDOM = "GB"
    FRANCE = "FR"
    CANADA = "CA"
    AUSTRALIA = "AU"
    NETHERLANDS = "NL"
    SWEDEN = "SE"
    NORWAY = "NO"
    DENMARK = "DK"


class TaxType(Enum):
    """Types of taxes"""
    INCOME_TAX = "income_tax"
    VAT = "vat"
    WITHHOLDING_TAX = "withholding_tax"
    SOCIAL_SECURITY = "social_security"
    SOLIDARITY_SURCHARGE = "solidarity_surcharge"
    CHURCH_TAX = "church_tax"
    TRADE_TAX = "trade_tax"


class BusinessType(Enum):
    """Business entity types"""
    INDIVIDUAL = "individual"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    LLC = "llc"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    FREELANCER = "freelancer"


@dataclass
class TaxRate:
    """Tax rate configuration"""
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    rate_percentage: Decimal
    threshold_min: Decimal = Decimal("0")
    threshold_max: Optional[Decimal] = None
    flat_amount: Optional[Decimal] = None
    progressive_brackets: List[Dict[str, Decimal]] = field(default_factory=list)
    effective_date: datetime = field(default_factory=datetime.now)
    
    def applies_to_amount(self, amount: Decimal) -> bool:
        """Check if tax rate applies to given amount"""
        if amount < self.threshold_min:
            return False
        if self.threshold_max and amount > self.threshold_max:
            return False
        return True


@dataclass
class TaxConfiguration:
    """Tax configuration for user"""
    user_id: int
    jurisdiction: TaxJurisdiction
    business_type: BusinessType
    tax_id_number: Optional[str] = None
    vat_number: Optional[str] = None
    church_tax_applicable: bool = False
    church_tax_rate: Decimal = Decimal("8.0")
    trade_tax_applicable: bool = False
    trade_tax_rate: Decimal = Decimal("14.0")
    estimated_annual_income: Optional[Decimal] = None
    deductions_enabled: bool = True
    professional_expenses_rate: Decimal = Decimal("30.0")  # % of income
    
    def __post_init__(self):
        """Validate configuration"""
        if self.church_tax_rate < 0 or self.church_tax_rate > 10:
            raise ValueError("Church tax rate must be between 0 and 10%")


class TaxCalculationRequest(BaseModel):
    """Tax calculation request"""
    user_id: int
    gross_amount: Decimal = Field(..., gt=0)
    income_type: str = "self_employment"  # employment, self_employment, royalties, etc.
    period_start: datetime
    period_end: datetime
    deductions: Dict[str, Decimal] = Field(default_factory=dict)
    foreign_tax_credits: Decimal = Decimal("0")
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }


class TaxCalculationResult(BaseModel):
    """Tax calculation result"""
    gross_amount: Decimal
    total_tax: Decimal
    net_amount: Decimal
    effective_tax_rate: Decimal
    tax_breakdown: Dict[str, Decimal]
    deductions_applied: Dict[str, Decimal]
    jurisdiction: str
    calculation_date: datetime
    
    def get_summary(self) -> Dict[str, Any]:
        """Get calculation summary"""
        return {
            "gross_amount": float(self.gross_amount),
            "total_tax": float(self.total_tax),
            "net_amount": float(self.net_amount),
            "effective_tax_rate": float(self.effective_tax_rate),
            "jurisdiction": self.jurisdiction,
            "calculation_date": self.calculation_date.isoformat()
        }


class TaxCalculator:
    """Advanced multi-jurisdiction tax calculator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tax_rates: Dict[TaxJurisdiction, Dict[TaxType, List[TaxRate]]] = {}
        self._initialize_tax_rates()
        
    def _initialize_tax_rates(self) -> None:
        """Initialize tax rates for supported jurisdictions"""
        
        # Germany tax rates (2025)
        germany_rates = {
            TaxType.INCOME_TAX: [
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("0"),
                    threshold_max=Decimal("11604")  # Basic allowance
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("14"),  # Entry rate
                    threshold_min=Decimal("11604"),
                    threshold_max=Decimal("66760")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("42"),  # Top rate
                    threshold_min=Decimal("66760"),
                    threshold_max=Decimal("277825")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("45"),  # Rich tax
                    threshold_min=Decimal("277825")
                )
            ],
            TaxType.SOLIDARITY_SURCHARGE: [
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.SOLIDARITY_SURCHARGE,
                    rate_percentage=Decimal("5.5")  # 5.5% of income tax
                )
            ],
            TaxType.VAT: [
                TaxRate(
                    jurisdiction=TaxJurisdiction.GERMANY,
                    tax_type=TaxType.VAT,
                    rate_percentage=Decimal("19")  # Standard VAT rate
                )
            ]
        }
        
        # United States tax rates (2025)
        us_rates = {
            TaxType.INCOME_TAX: [
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("10"),
                    threshold_max=Decimal("11000")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("12"),
                    threshold_min=Decimal("11000"),
                    threshold_max=Decimal("44725")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("22"),
                    threshold_min=Decimal("44725"),
                    threshold_max=Decimal("95375")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("24"),
                    threshold_min=Decimal("95375"),
                    threshold_max=Decimal("182050")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("32"),
                    threshold_min=Decimal("182050"),
                    threshold_max=Decimal("231250")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("35"),
                    threshold_min=Decimal("231250"),
                    threshold_max=Decimal("578125")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_STATES,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("37"),
                    threshold_min=Decimal("578125")
                )
            ]
        }
        
        # UK tax rates (2025)
        uk_rates = {
            TaxType.INCOME_TAX: [
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_KINGDOM,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("0"),
                    threshold_max=Decimal("12570")  # Personal allowance
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_KINGDOM,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("20"),  # Basic rate
                    threshold_min=Decimal("12570"),
                    threshold_max=Decimal("50270")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_KINGDOM,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("40"),  # Higher rate
                    threshold_min=Decimal("50270"),
                    threshold_max=Decimal("125140")
                ),
                TaxRate(
                    jurisdiction=TaxJurisdiction.UNITED_KINGDOM,
                    tax_type=TaxType.INCOME_TAX,
                    rate_percentage=Decimal("45"),  # Additional rate
                    threshold_min=Decimal("125140")
                )
            ]
        }
        
        self.tax_rates[TaxJurisdiction.GERMANY] = germany_rates
        self.tax_rates[TaxJurisdiction.UNITED_STATES] = us_rates
        self.tax_rates[TaxJurisdiction.UNITED_KINGDOM] = uk_rates
    
    async def calculate_tax(
        self,
        request: TaxCalculationRequest,
        session: AsyncSession
    ) -> TaxCalculationResult:
        """Calculate comprehensive tax liability"""
        try:
            # Get user tax configuration
            tax_config = await self._get_tax_configuration(request.user_id, session)
            
            if not tax_config:
                # Create default configuration
                user = await session.get(User, request.user_id)
                jurisdiction = self._determine_jurisdiction_from_country(user.country if user else "DE")
                tax_config = TaxConfiguration(
                    user_id=request.user_id,
                    jurisdiction=jurisdiction,
                    business_type=BusinessType.FREELANCER
                )
            
            # Calculate deductions
            total_deductions = await self._calculate_deductions(request, tax_config)
            
            # Calculate taxable income
            taxable_income = request.gross_amount - total_deductions
            taxable_income = max(taxable_income, Decimal("0"))
            
            # Calculate taxes by type
            tax_breakdown = {}
            
            # Income tax
            income_tax = await self._calculate_income_tax(
                taxable_income, tax_config.jurisdiction
            )
            tax_breakdown[TaxType.INCOME_TAX.value] = income_tax
            
            # Solidarity surcharge (Germany)
            if tax_config.jurisdiction == TaxJurisdiction.GERMANY:
                solidarity_surcharge = income_tax * Decimal("0.055")  # 5.5% of income tax
                tax_breakdown[TaxType.SOLIDARITY_SURCHARGE.value] = solidarity_surcharge
                
                # Church tax (if applicable)
                if tax_config.church_tax_applicable:
                    church_tax = income_tax * (tax_config.church_tax_rate / 100)
                    tax_breakdown[TaxType.CHURCH_TAX.value] = church_tax
                
                # Trade tax (if applicable)
                if tax_config.trade_tax_applicable:
                    trade_tax = taxable_income * (tax_config.trade_tax_rate / 100)
                    tax_breakdown[TaxType.TRADE_TAX.value] = trade_tax
            
            # Social security (self-employment)
            if tax_config.business_type in [BusinessType.FREELANCER, BusinessType.SOLE_PROPRIETORSHIP]:
                social_security = await self._calculate_social_security(
                    taxable_income, tax_config.jurisdiction
                )
                tax_breakdown[TaxType.SOCIAL_SECURITY.value] = social_security
            
            # VAT (if applicable)
            vat = await self._calculate_vat(request.gross_amount, tax_config)
            if vat > 0:
                tax_breakdown[TaxType.VAT.value] = vat
            
            # Apply foreign tax credits
            total_tax_before_credits = sum(tax_breakdown.values())
            foreign_tax_credits = min(request.foreign_tax_credits, total_tax_before_credits)
            
            # Calculate final amounts
            total_tax = total_tax_before_credits - foreign_tax_credits
            net_amount = request.gross_amount - total_tax
            effective_tax_rate = (total_tax / request.gross_amount) * 100 if request.gross_amount > 0 else Decimal("0")
            
            return TaxCalculationResult(
                gross_amount=request.gross_amount,
                total_tax=total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                net_amount=net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                effective_tax_rate=effective_tax_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                tax_breakdown={k: v.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) for k, v in tax_breakdown.items()},
                deductions_applied=total_deductions,
                jurisdiction=tax_config.jurisdiction.value,
                calculation_date=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Tax calculation failed: {str(e)}")
            raise
    
    async def _calculate_income_tax(
        self,
        taxable_income: Decimal,
        jurisdiction: TaxJurisdiction
    ) -> Decimal:
        """Calculate progressive income tax"""
        if jurisdiction not in self.tax_rates or TaxType.INCOME_TAX not in self.tax_rates[jurisdiction]:
            # Fallback to flat 25% rate
            return taxable_income * Decimal("0.25")
        
        tax_brackets = self.tax_rates[jurisdiction][TaxType.INCOME_TAX]
        total_tax = Decimal("0")
        remaining_income = taxable_income
        
        for bracket in sorted(tax_brackets, key=lambda b: b.threshold_min):
            if remaining_income <= 0:
                break
            
            # Determine income amount for this bracket
            bracket_min = bracket.threshold_min
            bracket_max = bracket.threshold_max or taxable_income
            
            if remaining_income > bracket_min:
                taxable_in_bracket = min(remaining_income, bracket_max) - bracket_min
                
                if taxable_in_bracket > 0:
                    bracket_tax = taxable_in_bracket * (bracket.rate_percentage / 100)
                    total_tax += bracket_tax
                    remaining_income -= taxable_in_bracket
        
        return total_tax
    
    async def _calculate_social_security(
        self,
        income: Decimal,
        jurisdiction: TaxJurisdiction
    ) -> Decimal:
        """Calculate social security contributions"""
        rates = {
            TaxJurisdiction.GERMANY: Decimal("18.6"),  # Health + pension insurance
            TaxJurisdiction.UNITED_STATES: Decimal("15.3"),  # FICA
            TaxJurisdiction.UNITED_KINGDOM: Decimal("9.0"),  # National Insurance
            TaxJurisdiction.FRANCE: Decimal("22.0"),  # Social charges
            TaxJurisdiction.CANADA: Decimal("5.95")   # CPP + EI
        }
        
        rate = rates.get(jurisdiction, Decimal("15.0"))  # Default 15%
        
        # Apply income caps where applicable
        if jurisdiction == TaxJurisdiction.GERMANY:
            max_income = Decimal("87600")  # 2025 contribution ceiling
            income = min(income, max_income)
        elif jurisdiction == TaxJurisdiction.UNITED_STATES:
            max_income = Decimal("168600")  # 2025 Social Security wage base
            income = min(income, max_income)
        
        return income * (rate / 100)
    
    async def _calculate_vat(
        self,
        gross_amount: Decimal,
        tax_config: TaxConfiguration
    ) -> Decimal:
        """Calculate VAT if applicable"""
        # VAT typically applies to business-to-consumer sales
        if tax_config.business_type in [BusinessType.CORPORATION, BusinessType.LLC]:
            vat_rates = {
                TaxJurisdiction.GERMANY: Decimal("19"),
                TaxJurisdiction.UNITED_KINGDOM: Decimal("20"),
                TaxJurisdiction.FRANCE: Decimal("20"),
                TaxJurisdiction.NETHERLANDS: Decimal("21")
            }
            
            vat_rate = vat_rates.get(tax_config.jurisdiction, Decimal("0"))
            return gross_amount * (vat_rate / 100)
        
        return Decimal("0")
    
    async def _calculate_deductions(
        self,
        request: TaxCalculationRequest,
        tax_config: TaxConfiguration
    ) -> Dict[str, Decimal]:
        """Calculate allowable deductions"""
        deductions = {}
        
        # Professional expenses
        if tax_config.deductions_enabled:
            professional_expenses = request.gross_amount * (tax_config.professional_expenses_rate / 100)
            deductions["professional_expenses"] = professional_expenses
        
        # Standard deductions by jurisdiction
        standard_deductions = {
            TaxJurisdiction.GERMANY: Decimal("1230"),  # Werbungskosten
            TaxJurisdiction.UNITED_STATES: Decimal("14600"),  # Standard deduction 2025
            TaxJurisdiction.UNITED_KINGDOM: Decimal("12570"),  # Personal allowance
            TaxJurisdiction.CANADA: Decimal("15000")   # Basic personal amount
        }
        
        standard_deduction = standard_deductions.get(tax_config.jurisdiction, Decimal("0"))
        if standard_deduction > 0:
            deductions["standard_deduction"] = standard_deduction
        
        # Custom deductions from request
        for deduction_type, amount in request.deductions.items():
            deductions[f"custom_{deduction_type}"] = amount
        
        return deductions
    
    async def _get_tax_configuration(
        self,
        user_id: int,
        session: AsyncSession
    ) -> Optional[TaxConfiguration]:
        """Get user's tax configuration"""
        # This would typically fetch from database
        # For now, return None to use defaults
        return None
    
    def _determine_jurisdiction_from_country(self, country_code: str) -> TaxJurisdiction:
        """Determine tax jurisdiction from country code"""
        mapping = {
            "DE": TaxJurisdiction.GERMANY,
            "US": TaxJurisdiction.UNITED_STATES,
            "GB": TaxJurisdiction.UNITED_KINGDOM,
            "UK": TaxJurisdiction.UNITED_KINGDOM,
            "FR": TaxJurisdiction.FRANCE,
            "CA": TaxJurisdiction.CANADA,
            "AU": TaxJurisdiction.AUSTRALIA,
            "NL": TaxJurisdiction.NETHERLANDS,
            "SE": TaxJurisdiction.SWEDEN,
            "NO": TaxJurisdiction.NORWAY,
            "DK": TaxJurisdiction.DENMARK
        }
        
        return mapping.get(country_code.upper(), TaxJurisdiction.GERMANY)  # Default to Germany
    
    async def estimate_quarterly_tax(
        self,
        user_id: int,
        estimated_annual_income: Decimal,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Estimate quarterly tax payments"""
        try:
            # Calculate annual tax
            annual_request = TaxCalculationRequest(
                user_id=user_id,
                gross_amount=estimated_annual_income,
                income_type="self_employment",
                period_start=datetime.now().replace(month=1, day=1),
                period_end=datetime.now().replace(month=12, day=31)
            )
            
            annual_tax_result = await self.calculate_tax(annual_request, session)
            
            # Calculate quarterly amounts
            quarterly_tax = annual_tax_result.total_tax / 4
            
            # Safe harbor rule (pay 100% of prior year tax)
            safe_harbor_payment = quarterly_tax * Decimal("1.1")  # 110% to be safe
            
            return {
                "estimated_annual_income": float(estimated_annual_income),
                "estimated_annual_tax": float(annual_tax_result.total_tax),
                "quarterly_payment": float(quarterly_tax),
                "safe_harbor_payment": float(safe_harbor_payment),
                "effective_tax_rate": float(annual_tax_result.effective_tax_rate),
                "payment_dates": self._get_quarterly_payment_dates(),
                "tax_breakdown": {k: float(v) for k, v in annual_tax_result.tax_breakdown.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Quarterly tax estimation failed: {str(e)}")
            return {}
    
    def _get_quarterly_payment_dates(self) -> List[str]:
        """Get quarterly tax payment dates"""
        current_year = datetime.now().year
        return [
            f"{current_year}-01-15",  # Q4 of previous year
            f"{current_year}-04-15",  # Q1
            f"{current_year}-06-15",  # Q2
            f"{current_year}-09-15"   # Q3
        ]
    
    async def generate_tax_report(
        self,
        user_id: int,
        year: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Generate comprehensive annual tax report"""
        try:
            from ...database.models import RevenueRecord
            from sqlalchemy import select, func, extract
            
            # Get annual revenue data
            result = await session.execute(
                select(
                    func.sum(RevenueRecord.amount).label('total_revenue'),
                    RevenueRecord.source,
                    RevenueRecord.platform
                ).where(
                    RevenueRecord.user_id == user_id,
                    extract('year', RevenueRecord.date) == year,
                    RevenueRecord.status == "confirmed"
                ).group_by(RevenueRecord.source, RevenueRecord.platform)
            )
            
            revenue_breakdown = []
            total_annual_revenue = Decimal("0")
            
            for row in result:
                revenue_breakdown.append({
                    "source": row.source,
                    "platform": row.platform,
                    "amount": float(row.total_revenue)
                })
                total_annual_revenue += Decimal(str(row.total_revenue))
            
            # Calculate annual tax
            annual_request = TaxCalculationRequest(
                user_id=user_id,
                gross_amount=total_annual_revenue,
                income_type="self_employment",
                period_start=datetime(year, 1, 1),
                period_end=datetime(year, 12, 31)
            )
            
            tax_calculation = await self.calculate_tax(annual_request, session)
            
            return {
                "user_id": user_id,
                "tax_year": year,
                "total_revenue": float(total_annual_revenue),
                "tax_calculation": tax_calculation.get_summary(),
                "tax_breakdown": {k: float(v) for k, v in tax_calculation.tax_breakdown.items()},
                "revenue_breakdown": revenue_breakdown,
                "effective_tax_rate": float(tax_calculation.effective_tax_rate),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Tax report generation failed: {str(e)}")
            return {}
    
    def get_supported_jurisdictions(self) -> List[Dict[str, Any]]:
        """Get list of supported tax jurisdictions"""
        return [
            {
                "jurisdiction": jurisdiction.value,
                "name": jurisdiction.name.replace("_", " ").title(),
                "supported_tax_types": list(self.tax_rates.get(jurisdiction, {}).keys())
            }
            for jurisdiction in TaxJurisdiction
        ]
