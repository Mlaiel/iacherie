"""Automated Tax Calculator - Intelligent Tax Computation System
=============================================================

Advanced tax calculation system providing automated tax computation,
multi-jurisdiction support, compliance management, and comprehensive
tax reporting for content creators and businesses.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class TaxJurisdiction(str, Enum):
    """Tax jurisdictions."""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    CANADA = "canada"
    UK = "uk"
    GERMANY = "germany"
    FRANCE = "france"
    AUSTRALIA = "australia"
    EU = "eu"


class IncomeType(str, Enum):
    """Types of income for tax purposes."""
    SELF_EMPLOYMENT = "self_employment"
    ROYALTIES = "royalties"
    CAPITAL_GAINS = "capital_gains"
    ORDINARY_INCOME = "ordinary_income"
    BUSINESS_INCOME = "business_income"
    INVESTMENT_INCOME = "investment_income"


class TaxPeriod(str, Enum):
    """Tax reporting periods."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


@dataclass
class TaxRate:
    """Tax rate configuration."""
    jurisdiction: TaxJurisdiction
    income_type: IncomeType
    min_income: Decimal
    max_income: Optional[Decimal]
    rate: Decimal
    description: str


@dataclass
class TaxDeduction:
    """Tax deduction item."""
    id: str
    description: str
    amount: Decimal
    category: str
    date: datetime
    supporting_documents: List[str] = field(default_factory=list)


@dataclass
class IncomeEntry:
    """Income entry for tax calculation."""
    id: str
    amount: Decimal
    income_type: IncomeType
    source: str
    date: datetime
    jurisdiction: TaxJurisdiction
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaxCalculation:
    """Tax calculation result."""
    id: str
    user_id: str
    period: TaxPeriod
    year: int
    quarter: Optional[int]
    month: Optional[int]
    total_income: Decimal
    total_deductions: Decimal
    taxable_income: Decimal
    tax_owed: Decimal
    effective_rate: Decimal
    breakdown_by_jurisdiction: Dict[str, Decimal]
    breakdown_by_income_type: Dict[str, Decimal]
    recommended_payments: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class TaxCalculator:
    """
    Automated tax calculation system providing intelligent tax computation
    and compliance management for content creators and businesses.
    """
    
    def __init__(self):
        """Initialize the tax calculator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.tax_rates: Dict[str, List[TaxRate]] = {}
        self.income_entries: Dict[str, List[IncomeEntry]] = {}
        self.deductions: Dict[str, List[TaxDeduction]] = {}
        self.calculations: Dict[str, TaxCalculation] = {}
        self._initialize_tax_rates()
        
        self.logger.info("TaxCalculator initialized")
    
    def _initialize_tax_rates(self):
        """Initialize tax rates for different jurisdictions."""
        # US Federal tax rates (simplified 2024 rates)
        self.tax_rates["us_federal"] = [
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('0'), Decimal('11000'), Decimal('0.10'), "10% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('11000'), Decimal('44725'), Decimal('0.12'), "12% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('44725'), Decimal('95375'), Decimal('0.22'), "22% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('95375'), Decimal('182050'), Decimal('0.24'), "24% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('182050'), Decimal('231250'), Decimal('0.32'), "32% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('231250'), Decimal('578125'), Decimal('0.35'), "35% bracket"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.ORDINARY_INCOME, Decimal('578125'), None, Decimal('0.37'), "37% bracket"),
            
            # Self-employment tax
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.SELF_EMPLOYMENT, Decimal('0'), Decimal('147000'), Decimal('0.1413'), "SE tax (Social Security + Medicare)"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.SELF_EMPLOYMENT, Decimal('147000'), None, Decimal('0.029'), "SE tax (Medicare only)"),
            
            # Capital gains
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.CAPITAL_GAINS, Decimal('0'), Decimal('44625'), Decimal('0.00'), "0% capital gains"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.CAPITAL_GAINS, Decimal('44625'), Decimal('492300'), Decimal('0.15'), "15% capital gains"),
            TaxRate(TaxJurisdiction.US_FEDERAL, IncomeType.CAPITAL_GAINS, Decimal('492300'), None, Decimal('0.20'), "20% capital gains"),
        ]
        
        # UK tax rates (simplified)
        self.tax_rates["uk"] = [
            TaxRate(TaxJurisdiction.UK, IncomeType.ORDINARY_INCOME, Decimal('0'), Decimal('12570'), Decimal('0.00'), "Personal allowance"),
            TaxRate(TaxJurisdiction.UK, IncomeType.ORDINARY_INCOME, Decimal('12570'), Decimal('50270'), Decimal('0.20'), "Basic rate"),
            TaxRate(TaxJurisdiction.UK, IncomeType.ORDINARY_INCOME, Decimal('50270'), Decimal('150000'), Decimal('0.40'), "Higher rate"),
            TaxRate(TaxJurisdiction.UK, IncomeType.ORDINARY_INCOME, Decimal('150000'), None, Decimal('0.45'), "Additional rate"),
        ]
        
        # Germany tax rates (simplified)
        self.tax_rates["germany"] = [
            TaxRate(TaxJurisdiction.GERMANY, IncomeType.ORDINARY_INCOME, Decimal('0'), Decimal('10908'), Decimal('0.00'), "Tax-free allowance"),
            TaxRate(TaxJurisdiction.GERMANY, IncomeType.ORDINARY_INCOME, Decimal('10908'), Decimal('62810'), Decimal('0.14'), "Progressive zone 1"),
            TaxRate(TaxJurisdiction.GERMANY, IncomeType.ORDINARY_INCOME, Decimal('62810'), Decimal('277826'), Decimal('0.42'), "Progressive zone 2"),
            TaxRate(TaxJurisdiction.GERMANY, IncomeType.ORDINARY_INCOME, Decimal('277826'), None, Decimal('0.45'), "Top rate"),
        ]
    
    async def add_income_entry(
        self,
        user_id: str,
        amount: Decimal,
        income_type: IncomeType,
        source: str,
        jurisdiction: TaxJurisdiction,
        date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add income entry for tax calculation."""
        try:
            entry_id = str(uuid4())
            
            income_entry = IncomeEntry(
                id=entry_id,
                amount=amount,
                income_type=income_type,
                source=source,
                date=date or datetime.utcnow(),
                jurisdiction=jurisdiction,
                metadata=metadata or {}
            )
            
            if user_id not in self.income_entries:
                self.income_entries[user_id] = []
            
            self.income_entries[user_id].append(income_entry)
            
            self.logger.info(f"💰 Income entry added: {amount} {income_type.value} for {user_id}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Error adding income entry: {e}")
            raise
    
    async def add_deduction(
        self,
        user_id: str,
        description: str,
        amount: Decimal,
        category: str,
        date: Optional[datetime] = None,
        supporting_documents: Optional[List[str]] = None
    ) -> str:
        """Add tax deduction."""
        try:
            deduction_id = str(uuid4())
            
            deduction = TaxDeduction(
                id=deduction_id,
                description=description,
                amount=amount,
                category=category,
                date=date or datetime.utcnow(),
                supporting_documents=supporting_documents or []
            )
            
            if user_id not in self.deductions:
                self.deductions[user_id] = []
            
            self.deductions[user_id].append(deduction)
            
            self.logger.info(f"📝 Deduction added: {amount} ({category}) for {user_id}")
            return deduction_id
            
        except Exception as e:
            self.logger.error(f"Error adding deduction: {e}")
            raise
    
    async def calculate_taxes(
        self,
        user_id: str,
        period: TaxPeriod,
        year: int,
        quarter: Optional[int] = None,
        month: Optional[int] = None
    ) -> TaxCalculation:
        """Calculate taxes for specified period."""
        try:
            calculation_id = str(uuid4())
            
            # Filter income entries for the period
            income_entries = self._filter_entries_by_period(
                self.income_entries.get(user_id, []), period, year, quarter, month
            )
            
            # Filter deductions for the period
            deductions = self._filter_deductions_by_period(
                self.deductions.get(user_id, []), period, year, quarter, month
            )
            
            # Calculate totals
            total_income = sum(entry.amount for entry in income_entries)
            total_deductions = sum(deduction.amount for deduction in deductions)
            taxable_income = max(Decimal('0'), total_income - total_deductions)
            
            # Calculate taxes by jurisdiction and income type
            tax_breakdown_jurisdiction = {}
            tax_breakdown_income_type = {}
            total_tax = Decimal('0')
            
            # Group income by jurisdiction and type
            income_by_jurisdiction = {}
            income_by_type = {}
            
            for entry in income_entries:
                # By jurisdiction
                jurisdiction = entry.jurisdiction.value
                if jurisdiction not in income_by_jurisdiction:
                    income_by_jurisdiction[jurisdiction] = Decimal('0')
                income_by_jurisdiction[jurisdiction] += entry.amount
                
                # By income type
                income_type = entry.income_type.value
                if income_type not in income_by_type:
                    income_by_type[income_type] = Decimal('0')
                income_by_type[income_type] += entry.amount
            
            # Calculate tax for each jurisdiction
            for jurisdiction, amount in income_by_jurisdiction.items():
                if amount > 0:
                    jurisdiction_tax = await self._calculate_jurisdiction_tax(
                        jurisdiction, amount, income_entries
                    )
                    tax_breakdown_jurisdiction[jurisdiction] = jurisdiction_tax
                    total_tax += jurisdiction_tax
            
            # Calculate tax for each income type
            for income_type, amount in income_by_type.items():
                if amount > 0:
                    type_tax = await self._calculate_income_type_tax(income_type, amount)
                    tax_breakdown_income_type[income_type] = type_tax
            
            # Calculate effective rate
            effective_rate = (total_tax / taxable_income * 100) if taxable_income > 0 else Decimal('0')
            
            # Generate payment recommendations
            payment_recommendations = await self._generate_payment_recommendations(
                total_tax, period, year, quarter, month
            )
            
            calculation = TaxCalculation(
                id=calculation_id,
                user_id=user_id,
                period=period,
                year=year,
                quarter=quarter,
                month=month,
                total_income=total_income,
                total_deductions=total_deductions,
                taxable_income=taxable_income,
                tax_owed=total_tax,
                effective_rate=effective_rate,
                breakdown_by_jurisdiction=tax_breakdown_jurisdiction,
                breakdown_by_income_type=tax_breakdown_income_type,
                recommended_payments=payment_recommendations
            )
            
            self.calculations[calculation_id] = calculation
            
            self.logger.info(f"🧮 Tax calculated: {total_tax} on {taxable_income} taxable income")
            return calculation
            
        except Exception as e:
            self.logger.error(f"Error calculating taxes: {e}")
            raise
    
    def _filter_entries_by_period(
        self,
        entries: List[IncomeEntry],
        period: TaxPeriod,
        year: int,
        quarter: Optional[int],
        month: Optional[int]
    ) -> List[IncomeEntry]:
        """Filter income entries by tax period."""
        filtered = []
        
        for entry in entries:
            if entry.date.year != year:
                continue
            
            if period == TaxPeriod.ANNUALLY:
                filtered.append(entry)
            elif period == TaxPeriod.QUARTERLY and quarter:
                entry_quarter = (entry.date.month - 1) // 3 + 1
                if entry_quarter == quarter:
                    filtered.append(entry)
            elif period == TaxPeriod.MONTHLY and month:
                if entry.date.month == month:
                    filtered.append(entry)
        
        return filtered
    
    def _filter_deductions_by_period(
        self,
        deductions: List[TaxDeduction],
        period: TaxPeriod,
        year: int,
        quarter: Optional[int],
        month: Optional[int]
    ) -> List[TaxDeduction]:
        """Filter deductions by tax period."""
        filtered = []
        
        for deduction in deductions:
            if deduction.date.year != year:
                continue
            
            if period == TaxPeriod.ANNUALLY:
                filtered.append(deduction)
            elif period == TaxPeriod.QUARTERLY and quarter:
                deduction_quarter = (deduction.date.month - 1) // 3 + 1
                if deduction_quarter == quarter:
                    filtered.append(deduction)
            elif period == TaxPeriod.MONTHLY and month:
                if deduction.date.month == month:
                    filtered.append(deduction)
        
        return filtered
    
    async def _calculate_jurisdiction_tax(
        self,
        jurisdiction: str,
        income: Decimal,
        income_entries: List[IncomeEntry]
    ) -> Decimal:
        """Calculate tax for specific jurisdiction."""
        try:
            if jurisdiction not in self.tax_rates:
                return Decimal('0')
            
            total_tax = Decimal('0')
            remaining_income = income
            
            # Get relevant tax rates
            tax_rates = self.tax_rates[jurisdiction]
            
            # Group rates by income type
            rates_by_type = {}
            for rate in tax_rates:
                income_type = rate.income_type.value
                if income_type not in rates_by_type:
                    rates_by_type[income_type] = []
                rates_by_type[income_type].append(rate)
            
            # Calculate tax for each income type
            for entry in income_entries:
                if entry.jurisdiction.value == jurisdiction:
                    income_type_rates = rates_by_type.get(entry.income_type.value, [])
                    
                    if income_type_rates:
                        income_type_tax = self._apply_progressive_rates(entry.amount, income_type_rates)
                        total_tax += income_type_tax
            
            return total_tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            self.logger.error(f"Error calculating jurisdiction tax: {e}")
            return Decimal('0')
    
    def _apply_progressive_rates(self, income: Decimal, rates: List[TaxRate]) -> Decimal:
        """Apply progressive tax rates to income."""
        try:
            total_tax = Decimal('0')
            remaining_income = income
            
            # Sort rates by minimum income
            sorted_rates = sorted(rates, key=lambda r: r.min_income)
            
            for rate in sorted_rates:
                if remaining_income <= 0:
                    break
                
                # Calculate taxable amount in this bracket
                bracket_min = rate.min_income
                bracket_max = rate.max_income or income
                
                if income <= bracket_min:
                    continue
                
                taxable_in_bracket = min(remaining_income, bracket_max - bracket_min)
                if taxable_in_bracket > 0:
                    bracket_tax = taxable_in_bracket * rate.rate
                    total_tax += bracket_tax
                    remaining_income -= taxable_in_bracket
            
            return total_tax
            
        except Exception as e:
            self.logger.error(f"Error applying progressive rates: {e}")
            return Decimal('0')
    
    async def _calculate_income_type_tax(self, income_type: str, amount: Decimal) -> Decimal:
        """Calculate tax for specific income type."""
        try:
            # Simplified calculation - would be more complex in real implementation
            return amount * Decimal('0.25')  # 25% average rate
        except Exception as e:
            self.logger.error(f"Error calculating income type tax: {e}")
            return Decimal('0')
    
    async def _generate_payment_recommendations(
        self,
        total_tax: Decimal,
        period: TaxPeriod,
        year: int,
        quarter: Optional[int],
        month: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Generate tax payment recommendations."""
        try:
            recommendations = []
            
            if period == TaxPeriod.QUARTERLY:
                # Quarterly estimated payment
                due_date = datetime(year, quarter * 3, 15) if quarter else datetime.utcnow()
                recommendations.append({
                    "type": "quarterly_estimated",
                    "amount": float(total_tax),
                    "due_date": due_date.isoformat(),
                    "description": f"Q{quarter} {year} estimated tax payment"
                })
            
            elif period == TaxPeriod.ANNUALLY:
                # Annual tax return
                due_date = datetime(year + 1, 4, 15)  # April 15th
                recommendations.append({
                    "type": "annual_return",
                    "amount": float(total_tax),
                    "due_date": due_date.isoformat(),
                    "description": f"{year} annual tax return"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating payment recommendations: {e}")
            return []
    
    async def get_tax_summary(self, user_id: str, year: int) -> Dict[str, Any]:
        """Get comprehensive tax summary for user."""
        try:
            # Get all calculations for the year
            user_calculations = [
                calc for calc in self.calculations.values()
                if calc.user_id == user_id and calc.year == year
            ]
            
            if not user_calculations:
                return {"year": year, "no_data": True}
            
            # Aggregate data
            total_income = sum(calc.total_income for calc in user_calculations)
            total_deductions = sum(calc.total_deductions for calc in user_calculations)
            total_tax_owed = sum(calc.tax_owed for calc in user_calculations)
            
            effective_rate = (total_tax_owed / total_income * 100) if total_income > 0 else Decimal('0')
            
            summary = {
                "year": year,
                "total_income": float(total_income),
                "total_deductions": float(total_deductions),
                "taxable_income": float(total_income - total_deductions),
                "total_tax_owed": float(total_tax_owed),
                "effective_rate": float(effective_rate),
                "calculations_count": len(user_calculations),
                "last_updated": max(calc.created_at for calc in user_calculations).isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting tax summary: {e}")
            return {"error": str(e)}


# Global tax calculator instance
_tax_calculator: Optional[TaxCalculator] = None


async def get_tax_calculator() -> TaxCalculator:
    """Get global tax calculator instance."""
    global _tax_calculator
    
    if _tax_calculator is None:
        _tax_calculator = TaxCalculator()
    
    return _tax_calculator