"""
💰 TAX CALCULATION SERVICE - ENTERPRISE MICROSERVICE
Comprehensive tax calculation service for creator monetization platform.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import aioredis
import aiohttp

logger = logging.getLogger(__name__)

class TaxType(Enum):
    """Tax types supported"""
    VAT = "vat"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"
    WITHHOLDING_TAX = "withholding_tax"
    DIGITAL_SERVICES_TAX = "digital_services_tax"
    CREATOR_TAX = "creator_tax"

class TaxStatus(Enum):
    """Tax status for entities"""
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    NON_PROFIT = "non_profit"
    EXEMPT = "exempt"

@dataclass
class TaxJurisdiction:
    """Tax jurisdiction information"""
    country_code: str
    state_province: str = ""
    city: str = ""
    tax_id: str = ""
    vat_number: str = ""
    
@dataclass
class TaxRate:
    """Tax rate configuration"""
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    rate: Decimal
    threshold: Decimal = Decimal('0')
    effective_date: datetime = None
    expiry_date: Optional[datetime] = None
    description: str = ""
    
    def __post_init__(self):
        if self.effective_date is None:
            self.effective_date = datetime.utcnow()
            
@dataclass
class TaxableItem:
    """Item subject to taxation"""
    item_id: str
    description: str
    amount: Decimal
    currency: str
    item_type: str  # revenue, royalty, commission, etc.
    creator_id: str
    buyer_jurisdiction: TaxJurisdiction
    seller_jurisdiction: TaxJurisdiction
    transaction_date: datetime
    
@dataclass
class TaxCalculation:
    """Tax calculation result"""
    calculation_id: str
    item: TaxableItem
    applicable_taxes: List[Dict[str, Any]]
    total_tax_amount: Decimal
    net_amount: Decimal
    gross_amount: Decimal
    tax_breakdown: Dict[str, Decimal]
    calculation_date: datetime
    rules_applied: List[str]
    
class TaxCalculationService:
    """
    💰 Tax Calculation Service
    
    Comprehensive tax calculation service supporting multiple jurisdictions,
    tax types, and creator monetization scenarios for the Ainflue platform.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
        # Tax rate cache
        self.tax_rates: Dict[str, List[TaxRate]] = {}
        self.jurisdiction_cache: Dict[str, TaxJurisdiction] = {}
        
        # Tax calculation cache
        self.calculation_cache: Dict[str, TaxCalculation] = {}
        
        # External tax service configurations
        self.tax_services = {
            'avalara': {
                'base_url': 'https://rest.avatax.com',
                'enabled': False
            },
            'taxjar': {
                'base_url': 'https://api.taxjar.com',
                'enabled': False
            }
        }
        
        # Creator-specific tax rules
        self.creator_tax_rules = {
            'digital_content': {
                'threshold': Decimal('600'),  # US 1099 threshold
                'withholding_required': False
            },
            'physical_products': {
                'threshold': Decimal('0'),
                'withholding_required': False
            },
            'services': {
                'threshold': Decimal('600'),
                'withholding_required': True
            }
        }
        
        self.running = False
        
    async def initialize(self):
        """Initialize tax calculation service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            
            # Load tax rates from cache/database
            await self._load_tax_rates()
            
            # Initialize default tax jurisdictions
            await self._initialize_default_jurisdictions()
            
            # Start background tasks
            asyncio.create_task(self._tax_rate_update_task())
            asyncio.create_task(self._cache_cleanup_task())
            
            self.running = True
            logger.info("Tax Calculation service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize tax calculation service: {e}")
            raise
            
    async def _load_tax_rates(self):
        """Load tax rates from Redis cache"""
        try:
            tax_rates_data = await self.redis.get("tax:rates")
            if tax_rates_data:
                rates_config = json.loads(tax_rates_data)
                for jurisdiction, rates in rates_config.items():
                    self.tax_rates[jurisdiction] = [
                        TaxRate(**rate) for rate in rates
                    ]
                    
        except Exception as e:
            logger.error(f"Failed to load tax rates: {e}")
            # Initialize with default rates if loading fails
            await self._initialize_default_tax_rates()
            
    async def _initialize_default_jurisdictions(self):
        """Initialize default tax jurisdictions"""
        default_jurisdictions = {
            'US': TaxJurisdiction(country_code='US', tax_id='US_TAX'),
            'CA': TaxJurisdiction(country_code='CA', tax_id='CA_TAX'),
            'GB': TaxJurisdiction(country_code='GB', tax_id='GB_TAX'),
            'DE': TaxJurisdiction(country_code='DE', tax_id='DE_TAX'),
            'FR': TaxJurisdiction(country_code='FR', tax_id='FR_TAX'),
            'AU': TaxJurisdiction(country_code='AU', tax_id='AU_TAX'),
            'JP': TaxJurisdiction(country_code='JP', tax_id='JP_TAX')
        }
        
        self.jurisdiction_cache.update(default_jurisdictions)
        
    async def _initialize_default_tax_rates(self):
        """Initialize default tax rates for major jurisdictions"""
        default_rates = {
            'US': [
                TaxRate(
                    jurisdiction=self.jurisdiction_cache['US'],
                    tax_type=TaxType.SALES_TAX,
                    rate=Decimal('8.25'),  # Average US sales tax
                    threshold=Decimal('0')
                ),
                TaxRate(
                    jurisdiction=self.jurisdiction_cache['US'],
                    tax_type=TaxType.DIGITAL_SERVICES_TAX,
                    rate=Decimal('0'),
                    threshold=Decimal('600')
                )
            ],
            'GB': [
                TaxRate(
                    jurisdiction=self.jurisdiction_cache['GB'],
                    tax_type=TaxType.VAT,
                    rate=Decimal('20'),
                    threshold=Decimal('85000')  # VAT threshold
                )
            ],
            'DE': [
                TaxRate(
                    jurisdiction=self.jurisdiction_cache['DE'],
                    tax_type=TaxType.VAT,
                    rate=Decimal('19'),
                    threshold=Decimal('22000')  # Small business threshold
                )
            ],
            'CA': [
                TaxRate(
                    jurisdiction=self.jurisdiction_cache['CA'],
                    tax_type=TaxType.VAT,  # GST/HST
                    rate=Decimal('13'),  # Ontario HST
                    threshold=Decimal('30000')
                )
            ]
        }
        
        self.tax_rates.update(default_rates)
        
        # Save to Redis
        await self._save_tax_rates()
        
    async def calculate_tax(self, item: TaxableItem) -> TaxCalculation:
        """Calculate tax for a taxable item"""
        calculation_id = f"tax_calc_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{item.item_id}"
        
        # Check cache first
        if calculation_id in self.calculation_cache:
            return self.calculation_cache[calculation_id]
            
        applicable_taxes = []
        tax_breakdown = {}
        total_tax_amount = Decimal('0')
        rules_applied = []
        
        try:
            # Determine applicable tax jurisdictions
            jurisdictions = await self._determine_tax_jurisdictions(item)
            
            for jurisdiction in jurisdictions:
                jurisdiction_key = f"{jurisdiction.country_code}_{jurisdiction.state_province}"
                tax_rates = self.tax_rates.get(jurisdiction_key, [])
                
                if not tax_rates:
                    # Try country-level rates
                    tax_rates = self.tax_rates.get(jurisdiction.country_code, [])
                    
                for tax_rate in tax_rates:
                    if await self._is_tax_applicable(item, tax_rate):
                        tax_amount = await self._calculate_tax_amount(item, tax_rate)
                        
                        if tax_amount > 0:
                            tax_info = {
                                'tax_type': tax_rate.tax_type.value,
                                'jurisdiction': asdict(tax_rate.jurisdiction),
                                'rate': float(tax_rate.rate),
                                'amount': float(tax_amount),
                                'description': tax_rate.description
                            }
                            
                            applicable_taxes.append(tax_info)
                            tax_breakdown[f"{tax_rate.tax_type.value}_{jurisdiction.country_code}"] = tax_amount
                            total_tax_amount += tax_amount
                            rules_applied.append(f"Rule: {tax_rate.tax_type.value} for {jurisdiction.country_code}")
                            
            # Apply creator-specific tax rules
            creator_taxes = await self._apply_creator_tax_rules(item)
            for creator_tax in creator_taxes:
                applicable_taxes.append(creator_tax)
                total_tax_amount += Decimal(str(creator_tax['amount']))
                rules_applied.append(f"Creator rule: {creator_tax['tax_type']}")
                
            # Create calculation result
            calculation = TaxCalculation(
                calculation_id=calculation_id,
                item=item,
                applicable_taxes=applicable_taxes,
                total_tax_amount=total_tax_amount,
                net_amount=item.amount - total_tax_amount,
                gross_amount=item.amount,
                tax_breakdown=tax_breakdown,
                calculation_date=datetime.utcnow(),
                rules_applied=rules_applied
            )
            
            # Cache the calculation
            self.calculation_cache[calculation_id] = calculation
            
            return calculation
            
        except Exception as e:
            logger.error(f"Tax calculation failed for item {item.item_id}: {e}")
            raise
            
    async def _determine_tax_jurisdictions(self, item: TaxableItem) -> List[TaxJurisdiction]:
        """Determine applicable tax jurisdictions"""
        jurisdictions = []
        
        # Add buyer jurisdiction (where tax is typically owed)
        jurisdictions.append(item.buyer_jurisdiction)
        
        # Add seller jurisdiction if different and has nexus
        if (item.seller_jurisdiction.country_code != item.buyer_jurisdiction.country_code and
            await self._has_tax_nexus(item.seller_jurisdiction, item.buyer_jurisdiction)):
            jurisdictions.append(item.seller_jurisdiction)
            
        return jurisdictions
        
    async def _has_tax_nexus(self, seller_jurisdiction: TaxJurisdiction, 
                           buyer_jurisdiction: TaxJurisdiction) -> bool:
        """Check if seller has tax nexus in buyer jurisdiction"""
        # Simplified nexus determination
        # In reality, this would involve complex business logic
        
        # Same country = nexus
        if seller_jurisdiction.country_code == buyer_jurisdiction.country_code:
            return True
            
        # Digital services may create nexus
        digital_nexus_countries = ['US', 'GB', 'FR', 'IT', 'ES']
        if buyer_jurisdiction.country_code in digital_nexus_countries:
            return True
            
        return False
        
    async def _is_tax_applicable(self, item: TaxableItem, tax_rate: TaxRate) -> bool:
        """Check if tax rate is applicable to the item"""
        # Check effective dates
        current_date = datetime.utcnow()
        if tax_rate.effective_date > current_date:
            return False
            
        if tax_rate.expiry_date and tax_rate.expiry_date < current_date:
            return False
            
        # Check threshold
        if item.amount < tax_rate.threshold:
            return False
            
        # Check tax type applicability
        if tax_rate.tax_type == TaxType.VAT:
            # VAT applies to most digital services in EU
            eu_countries = ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'IE', 'PT', 'FI', 'GR']
            return tax_rate.jurisdiction.country_code in eu_countries
            
        elif tax_rate.tax_type == TaxType.SALES_TAX:
            # Sales tax primarily in US
            return tax_rate.jurisdiction.country_code == 'US'
            
        elif tax_rate.tax_type == TaxType.DIGITAL_SERVICES_TAX:
            # Applies to digital content
            return item.item_type in ['digital_content', 'subscription', 'commission']
            
        return True
        
    async def _calculate_tax_amount(self, item: TaxableItem, tax_rate: TaxRate) -> Decimal:
        """Calculate tax amount for specific tax rate"""
        if tax_rate.rate == 0:
            return Decimal('0')
            
        # Standard percentage calculation
        tax_amount = item.amount * (tax_rate.rate / Decimal('100'))
        
        # Round to 2 decimal places
        return tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    async def _apply_creator_tax_rules(self, item: TaxableItem) -> List[Dict[str, Any]]:
        """Apply creator-specific tax rules"""
        creator_taxes = []
        
        # Get creator tax status and annual earnings
        creator_status = await self._get_creator_tax_status(item.creator_id)
        annual_earnings = await self._get_creator_annual_earnings(item.creator_id)
        
        # Check if withholding tax is required
        item_rules = self.creator_tax_rules.get(item.item_type, {})
        threshold = item_rules.get('threshold', Decimal('0'))
        
        if annual_earnings >= threshold and item_rules.get('withholding_required'):
            # Calculate withholding tax (simplified)
            withholding_rate = Decimal('10')  # 10% default withholding
            withholding_amount = item.amount * (withholding_rate / Decimal('100'))
            
            creator_taxes.append({
                'tax_type': 'withholding_tax',
                'jurisdiction': asdict(item.seller_jurisdiction),
                'rate': float(withholding_rate),
                'amount': float(withholding_amount),
                'description': f'Creator withholding tax ({creator_status})'
            })
            
        return creator_taxes
        
    async def _get_creator_tax_status(self, creator_id: str) -> str:
        """Get creator tax status"""
        try:
            # This would typically query a creator database
            creator_data = await self.redis.get(f"creator:tax_status:{creator_id}")
            if creator_data:
                return json.loads(creator_data).get('status', 'individual')
        except Exception:
            pass
            
        return 'individual'  # Default
        
    async def _get_creator_annual_earnings(self, creator_id: str) -> Decimal:
        """Get creator annual earnings for tax threshold calculations"""
        try:
            # This would typically query earnings from the database
            earnings_data = await self.redis.get(f"creator:annual_earnings:{creator_id}")
            if earnings_data:
                return Decimal(str(json.loads(earnings_data).get('amount', 0)))
        except Exception:
            pass
            
        return Decimal('0')
        
    async def calculate_quarterly_taxes(self, creator_id: str, quarter: int, year: int) -> Dict[str, Any]:
        """Calculate quarterly tax estimates for a creator"""
        try:
            # Get quarterly earnings
            quarterly_earnings = await self._get_quarterly_earnings(creator_id, quarter, year)
            
            # Project annual earnings
            annual_projection = quarterly_earnings * Decimal('4')
            
            # Calculate estimated taxes
            estimated_taxes = {
                'quarterly_earnings': float(quarterly_earnings),
                'annual_projection': float(annual_projection),
                'estimated_quarterly_tax': 0,
                'tax_breakdown': {},
                'recommendations': []
            }
            
            # Calculate different tax scenarios
            tax_scenarios = [
                ('individual', TaxType.INCOME_TAX),
                ('business', TaxType.INCOME_TAX),
                ('self_employed', TaxType.INCOME_TAX)
            ]
            
            for status, tax_type in tax_scenarios:
                scenario_tax = await self._calculate_income_tax_estimate(
                    annual_projection, status, creator_id
                )
                estimated_taxes['tax_breakdown'][f'{status}_{tax_type.value}'] = scenario_tax
                
            # Add recommendations
            if annual_projection > Decimal('50000'):
                estimated_taxes['recommendations'].append(
                    'Consider quarterly estimated tax payments'
                )
                
            if annual_projection > Decimal('100000'):
                estimated_taxes['recommendations'].append(
                    'Consult with a tax professional for business entity optimization'
                )
                
            return estimated_taxes
            
        except Exception as e:
            logger.error(f"Quarterly tax calculation failed for creator {creator_id}: {e}")
            raise
            
    async def _get_quarterly_earnings(self, creator_id: str, quarter: int, year: int) -> Decimal:
        """Get creator earnings for specific quarter"""
        try:
            earnings_key = f"creator:quarterly_earnings:{creator_id}:{year}:{quarter}"
            earnings_data = await self.redis.get(earnings_key)
            if earnings_data:
                return Decimal(str(json.loads(earnings_data).get('amount', 0)))
        except Exception:
            pass
            
        return Decimal('0')
        
    async def _calculate_income_tax_estimate(self, annual_income: Decimal, 
                                           status: str, creator_id: str) -> float:
        """Calculate estimated income tax"""
        # Simplified income tax calculation (US-based)
        # This would be much more complex in reality
        
        if status == 'individual':
            # Progressive tax brackets (simplified)
            if annual_income <= Decimal('10275'):
                tax_rate = Decimal('10')
            elif annual_income <= Decimal('41775'):
                tax_rate = Decimal('12')
            elif annual_income <= Decimal('89450'):
                tax_rate = Decimal('22')
            else:
                tax_rate = Decimal('24')
                
        elif status == 'business':
            tax_rate = Decimal('21')  # Corporate rate
            
        else:  # self_employed
            tax_rate = Decimal('15.3')  # Self-employment tax
            
        estimated_tax = annual_income * (tax_rate / Decimal('100'))
        return float(estimated_tax)
        
    async def generate_tax_report(self, creator_id: str, year: int) -> Dict[str, Any]:
        """Generate annual tax report for creator"""
        try:
            # Get all calculations for the year
            calculations = await self._get_creator_calculations(creator_id, year)
            
            # Aggregate tax data
            total_earnings = Decimal('0')
            total_taxes = Decimal('0')
            tax_by_type = {}
            tax_by_jurisdiction = {}
            
            for calc in calculations:
                total_earnings += calc.gross_amount
                total_taxes += calc.total_tax_amount
                
                for tax_type, amount in calc.tax_breakdown.items():
                    if tax_type not in tax_by_type:
                        tax_by_type[tax_type] = Decimal('0')
                    tax_by_type[tax_type] += amount
                    
                for tax_info in calc.applicable_taxes:
                    jurisdiction = tax_info['jurisdiction']['country_code']
                    if jurisdiction not in tax_by_jurisdiction:
                        tax_by_jurisdiction[jurisdiction] = Decimal('0')
                    tax_by_jurisdiction[jurisdiction] += Decimal(str(tax_info['amount']))
                    
            # Generate report
            report = {
                'creator_id': creator_id,
                'year': year,
                'total_earnings': float(total_earnings),
                'total_taxes_collected': float(total_taxes),
                'net_earnings': float(total_earnings - total_taxes),
                'tax_by_type': {k: float(v) for k, v in tax_by_type.items()},
                'tax_by_jurisdiction': {k: float(v) for k, v in tax_by_jurisdiction.items()},
                'transactions_count': len(calculations),
                'report_generated': datetime.utcnow().isoformat(),
                'tax_documents_required': []
            }
            
            # Determine required tax documents
            if total_earnings >= Decimal('600'):
                report['tax_documents_required'].append('1099-NEC')
                
            if any(j in ['US'] for j in tax_by_jurisdiction.keys()):
                report['tax_documents_required'].append('US Tax Return')
                
            return report
            
        except Exception as e:
            logger.error(f"Tax report generation failed for creator {creator_id}: {e}")
            raise
            
    async def _get_creator_calculations(self, creator_id: str, year: int) -> List[TaxCalculation]:
        """Get all tax calculations for creator in given year"""
        # In a real implementation, this would query the database
        # For now, return cached calculations that match
        
        matching_calculations = []
        for calc in self.calculation_cache.values():
            if (calc.item.creator_id == creator_id and 
                calc.calculation_date.year == year):
                matching_calculations.append(calc)
                
        return matching_calculations
        
    async def _save_tax_rates(self):
        """Save tax rates to Redis"""
        try:
            rates_data = {}
            for jurisdiction, rates in self.tax_rates.items():
                rates_data[jurisdiction] = [asdict(rate) for rate in rates]
                
            await self.redis.set(
                "tax:rates", 
                json.dumps(rates_data, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to save tax rates: {e}")
            
    async def _tax_rate_update_task(self):
        """Background task for updating tax rates"""
        while self.running:
            try:
                # Check for tax rate updates from external services
                await self._update_tax_rates_from_external_services()
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                logger.error(f"Error in tax rate update task: {e}")
                await asyncio.sleep(3600)
                
    async def _update_tax_rates_from_external_services(self):
        """Update tax rates from external tax services"""
        # This would integrate with services like Avalara, TaxJar, etc.
        # For now, just a placeholder
        pass
        
    async def _cache_cleanup_task(self):
        """Background task for cleaning up old calculations"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=90)
                
                # Clean up old calculations
                to_remove = []
                for calc_id, calc in self.calculation_cache.items():
                    if calc.calculation_date < cutoff_time:
                        to_remove.append(calc_id)
                        
                for calc_id in to_remove:
                    del self.calculation_cache[calc_id]
                    
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error in cache cleanup task: {e}")
                await asyncio.sleep(3600)
                
    async def health_check(self) -> Dict[str, Any]:
        """Health check for tax calculation service"""
        try:
            await self.redis.ping()
            redis_status = "healthy"
        except Exception as e:
            redis_status = f"unhealthy: {e}"
            
        return {
            'service': 'tax_calculation',
            'status': 'healthy' if redis_status == "healthy" else 'degraded',
            'redis': redis_status,
            'tax_rates_loaded': len(self.tax_rates),
            'cached_calculations': len(self.calculation_cache),
            'supported_jurisdictions': len(self.jurisdiction_cache)
        }
        
    async def shutdown(self):
        """Shutdown tax calculation service"""
        self.running = False
        
        if self.redis:
            await self.redis.close()
            
        logger.info("Tax Calculation service shut down")

# Example usage
async def create_tax_calculation_service():
    """Factory function to create tax calculation service"""
    service = TaxCalculationService()
    await service.initialize()
    return service

if __name__ == "__main__":
    async def main():
        tax_service = await create_tax_calculation_service()
        
        # Example usage
        buyer_jurisdiction = TaxJurisdiction(country_code='US', state_province='CA')
        seller_jurisdiction = TaxJurisdiction(country_code='US', state_province='NY')
        
        taxable_item = TaxableItem(
            item_id='item_123',
            description='Digital artwork sale',
            amount=Decimal('100.00'),
            currency='USD',
            item_type='digital_content',
            creator_id='creator_456',
            buyer_jurisdiction=buyer_jurisdiction,
            seller_jurisdiction=seller_jurisdiction,
            transaction_date=datetime.utcnow()
        )
        
        # Calculate tax
        calculation = await tax_service.calculate_tax(taxable_item)
        print(f"Tax Calculation: {calculation.total_tax_amount}")
        print(f"Net Amount: {calculation.net_amount}")
        
        # Generate quarterly estimate
        quarterly_taxes = await tax_service.calculate_quarterly_taxes('creator_456', 1, 2024)
        print(f"Quarterly Tax Estimate: {quarterly_taxes}")
        
        await tax_service.shutdown()
        
    asyncio.run(main())