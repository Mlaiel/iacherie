"""
Creator Earnings Service - Enterprise Microservice
================================================

Advanced earnings management system for creators with real-time tracking,
multi-currency support, automated tax calculations, and comprehensive financial analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from decimal import Decimal, ROUND_HALF_UP
import json
from collections import defaultdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EarningType(str, Enum):
    """Types of earnings."""
    CONTENT_SALE = "content_sale"
    SUBSCRIPTION = "subscription"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    ROYALTY = "royalty"
    TIP_DONATION = "tip_donation"
    MERCHANDISE = "merchandise"
    LIVE_STREAM = "live_stream"
    COURSE_SALE = "course_sale"
    AFFILIATE = "affiliate"
    SPONSORSHIP = "sponsorship"
    AD_REVENUE = "ad_revenue"
    NFT_SALE = "nft_sale"
    CONSULTING = "consulting"
    EVENT_HOSTING = "event_hosting"


class PaymentStatus(str, Enum):
    """Payment processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"


class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    BRL = "BRL"
    MXN = "MXN"
    INR = "INR"
    CNY = "CNY"
    KRW = "KRW"
    BTC = "BTC"
    ETH = "ETH"


class TaxJurisdiction(str, Enum):
    """Tax jurisdictions."""
    US = "US"
    CA = "CA"
    GB = "GB"
    DE = "DE"
    FR = "FR"
    IT = "IT"
    ES = "ES"
    AU = "AU"
    JP = "JP"
    BR = "BR"
    MX = "MX"
    IN = "IN"
    CN = "CN"
    KR = "KR"


@dataclass
class EarningRecord:
    """Individual earning record."""
    id: str
    creator_id: str
    earning_type: EarningType
    gross_amount: Decimal
    currency: Currency
    net_amount: Decimal
    platform_fee: Decimal
    payment_processor_fee: Decimal
    tax_amount: Decimal
    tax_jurisdiction: TaxJurisdiction
    payment_status: PaymentStatus
    transaction_id: Optional[str]
    payment_method: Optional[str]
    source_platform: Optional[str]
    metadata: Dict[str, Any]
    earned_at: datetime
    processed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None


class TaxConfiguration(BaseModel):
    """Tax configuration for jurisdiction."""
    jurisdiction: TaxJurisdiction = Field(..., description="Tax jurisdiction")
    income_tax_rate: Decimal = Field(..., description="Income tax rate (%)")
    vat_tax_rate: Decimal = Field(default=Decimal("0"), description="VAT tax rate (%)")
    self_employment_tax_rate: Decimal = Field(default=Decimal("0"), description="Self-employment tax rate (%)")
    minimum_threshold: Decimal = Field(default=Decimal("0"), description="Minimum earning threshold")
    reporting_currency: Currency = Field(default=Currency.USD, description="Reporting currency")


class EarningsSummary(BaseModel):
    """Earnings summary for period."""
    creator_id: str = Field(..., description="Creator identifier")
    period_start: datetime = Field(..., description="Period start date")
    period_end: datetime = Field(..., description="Period end date")
    total_gross_earnings: Decimal = Field(..., description="Total gross earnings")
    total_net_earnings: Decimal = Field(..., description="Total net earnings")
    total_fees: Decimal = Field(..., description="Total fees deducted")
    total_taxes: Decimal = Field(..., description="Total taxes deducted")
    currency: Currency = Field(..., description="Summary currency")
    earnings_by_type: Dict[EarningType, Decimal] = Field(default_factory=dict)
    earnings_by_platform: Dict[str, Decimal] = Field(default_factory=dict)
    transaction_count: int = Field(default=0, description="Number of transactions")
    pending_amount: Decimal = Field(default=Decimal("0"), description="Pending earnings")


class FinancialAnalytics(BaseModel):
    """Financial analytics for creator."""
    creator_id: str
    analysis_period_days: int
    total_revenue: Decimal
    average_daily_revenue: Decimal
    revenue_growth_rate: Decimal
    top_earning_type: EarningType
    best_performing_platform: str
    revenue_diversification_score: float
    projected_monthly_earnings: Decimal
    tax_efficiency_score: float
    recommendations: List[str]


class CreatorEarningsService:
    """
    Enterprise Creator Earnings Service
    
    Manages comprehensive earnings tracking, tax calculations, multi-currency support,
    and advanced financial analytics for creators across multiple revenue streams.
    """
    
    def __init__(self) -> None:
        self.earning_records: Dict[str, EarningRecord] = {}
        self.creator_earnings: Dict[str, List[str]] = defaultdict(list)  # creator_id -> earning_ids
        self.tax_configurations: Dict[TaxJurisdiction, TaxConfiguration] = {}
        self.currency_exchange_rates: Dict[str, Decimal] = {}
        self.platform_fee_rates: Dict[str, Decimal] = {}
        self.payment_processor_fees: Dict[str, Decimal] = {}
        
        # Initialize system
        self._initialize_tax_configurations()
        self._initialize_exchange_rates()
        self._initialize_fee_structures()
        
        logger.info("CreatorEarningsService initialized successfully")
    
    def _initialize_tax_configurations(self) -> None:
        """Initialize default tax configurations."""
        tax_configs = [
            TaxConfiguration(
                jurisdiction=TaxJurisdiction.US,
                income_tax_rate=Decimal("24.0"),
                vat_tax_rate=Decimal("0.0"),
                self_employment_tax_rate=Decimal("15.3"),
                minimum_threshold=Decimal("600"),
                reporting_currency=Currency.USD
            ),
            TaxConfiguration(
                jurisdiction=TaxJurisdiction.GB,
                income_tax_rate=Decimal("20.0"),
                vat_tax_rate=Decimal("20.0"),
                self_employment_tax_rate=Decimal("9.0"),
                minimum_threshold=Decimal("1000"),
                reporting_currency=Currency.GBP
            ),
            TaxConfiguration(
                jurisdiction=TaxJurisdiction.DE,
                income_tax_rate=Decimal("25.0"),
                vat_tax_rate=Decimal("19.0"),
                self_employment_tax_rate=Decimal("0.0"),
                minimum_threshold=Decimal("410"),
                reporting_currency=Currency.EUR
            ),
            TaxConfiguration(
                jurisdiction=TaxJurisdiction.CA,
                income_tax_rate=Decimal("22.0"),
                vat_tax_rate=Decimal("13.0"),
                self_employment_tax_rate=Decimal("5.4"),
                minimum_threshold=Decimal("500"),
                reporting_currency=Currency.CAD
            ),
            TaxConfiguration(
                jurisdiction=TaxJurisdiction.AU,
                income_tax_rate=Decimal("25.0"),
                vat_tax_rate=Decimal("10.0"),
                self_employment_tax_rate=Decimal("0.0"),
                minimum_threshold=Decimal("450"),
                reporting_currency=Currency.AUD
            )
        ]
        
        for config in tax_configs:
            self.tax_configurations[config.jurisdiction] = config
    
    def _initialize_exchange_rates(self) -> None:
        """Initialize currency exchange rates (would integrate with real-time API)."""
        # Base rates to USD (example rates)
        self.currency_exchange_rates = {
            "EUR_USD": Decimal("1.08"),
            "GBP_USD": Decimal("1.26"),
            "CAD_USD": Decimal("0.74"),
            "AUD_USD": Decimal("0.66"),
            "JPY_USD": Decimal("0.0067"),
            "CHF_USD": Decimal("1.10"),
            "SEK_USD": Decimal("0.096"),
            "NOK_USD": Decimal("0.094"),
            "DKK_USD": Decimal("0.145"),
            "BRL_USD": Decimal("0.20"),
            "MXN_USD": Decimal("0.059"),
            "INR_USD": Decimal("0.012"),
            "CNY_USD": Decimal("0.138"),
            "KRW_USD": Decimal("0.00076"),
            "BTC_USD": Decimal("42000.00"),
            "ETH_USD": Decimal("2800.00")
        }
    
    def _initialize_fee_structures(self) -> None:
        """Initialize platform and payment processor fees."""
        # Platform fees (as percentage)
        self.platform_fee_rates = {
            "ainflue": Decimal("5.0"),  # 5%
            "youtube": Decimal("30.0"),  # 30%
            "spotify": Decimal("30.0"),  # 30%
            "instagram": Decimal("30.0"),  # 30%
            "tiktok": Decimal("50.0"),  # 50%
            "patreon": Decimal("8.0"),  # 8%
            "onlyfans": Decimal("20.0"),  # 20%
            "twitch": Decimal("50.0"),  # 50%
            "default": Decimal("10.0")  # 10%
        }
        
        # Payment processor fees (as percentage + fixed fee)
        self.payment_processor_fees = {
            "stripe": Decimal("2.9"),  # 2.9% + $0.30
            "paypal": Decimal("3.49"),  # 3.49% + $0.49
            "square": Decimal("2.6"),  # 2.6% + $0.10
            "crypto": Decimal("1.0"),  # 1.0%
            "bank_transfer": Decimal("0.5"),  # 0.5%
            "default": Decimal("3.0")  # 3.0%
        }
    
    async def record_earning(
        self,
        creator_id: str,
        earning_type: EarningType,
        gross_amount: Decimal,
        currency: Currency,
        tax_jurisdiction: TaxJurisdiction,
        source_platform: str = "ainflue",
        payment_method: str = "stripe",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record new earning for creator."""
        try:
            earning_id = str(uuid.uuid4())
            
            # Calculate fees and taxes
            platform_fee = self._calculate_platform_fee(gross_amount, source_platform)
            processor_fee = self._calculate_processor_fee(gross_amount, payment_method)
            tax_amount = self._calculate_tax_amount(gross_amount, earning_type, tax_jurisdiction)
            
            # Calculate net amount
            net_amount = gross_amount - platform_fee - processor_fee - tax_amount
            
            # Create earning record
            earning = EarningRecord(
                id=earning_id,
                creator_id=creator_id,
                earning_type=earning_type,
                gross_amount=gross_amount,
                currency=currency,
                net_amount=max(Decimal("0"), net_amount),
                platform_fee=platform_fee,
                payment_processor_fee=processor_fee,
                tax_amount=tax_amount,
                tax_jurisdiction=tax_jurisdiction,
                payment_status=PaymentStatus.PENDING,
                transaction_id=None,
                payment_method=payment_method,
                source_platform=source_platform,
                metadata=metadata or {},
                earned_at=datetime.now()
            )
            
            # Store earning record
            self.earning_records[earning_id] = earning
            self.creator_earnings[creator_id].append(earning_id)
            
            logger.info(f"Recorded earning {earning_id} for creator {creator_id}: "
                       f"{gross_amount} {currency} (net: {net_amount})")
            
            return earning_id
            
        except Exception as e:
            logger.error(f"Error recording earning: {e}")
            raise
    
    def _calculate_platform_fee(self, amount: Decimal, platform: str) -> Decimal:
        """Calculate platform fee."""
        fee_rate = self.platform_fee_rates.get(platform, self.platform_fee_rates["default"])
        return (amount * fee_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _calculate_processor_fee(self, amount: Decimal, payment_method: str) -> Decimal:
        """Calculate payment processor fee."""
        fee_rate = self.payment_processor_fees.get(payment_method, self.payment_processor_fees["default"])
        
        # Calculate percentage fee
        percentage_fee = (amount * fee_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Add fixed fee (simplified - would be based on payment method)
        fixed_fee = Decimal("0.30") if payment_method in ["stripe", "paypal"] else Decimal("0")
        
        return percentage_fee + fixed_fee
    
    def _calculate_tax_amount(
        self, 
        amount: Decimal, 
        earning_type: EarningType, 
        jurisdiction: TaxJurisdiction
    ) -> Decimal:
        """Calculate tax amount based on jurisdiction and earning type."""
        try:
            tax_config = self.tax_configurations.get(jurisdiction)
            if not tax_config:
                return Decimal("0")  # No tax configuration available
            
            # Check minimum threshold
            if amount < tax_config.minimum_threshold:
                return Decimal("0")
            
            total_tax_rate = Decimal("0")
            
            # Income tax
            total_tax_rate += tax_config.income_tax_rate
            
            # VAT (for certain earning types)
            vat_applicable_types = [
                EarningType.CONTENT_SALE,
                EarningType.COURSE_SALE,
                EarningType.MERCHANDISE,
                EarningType.CONSULTING
            ]
            if earning_type in vat_applicable_types:
                total_tax_rate += tax_config.vat_tax_rate
            
            # Self-employment tax (for freelance work)
            freelance_types = [
                EarningType.COLLABORATION,
                EarningType.CONSULTING,
                EarningType.SPONSORSHIP
            ]
            if earning_type in freelance_types:
                total_tax_rate += tax_config.self_employment_tax_rate
            
            # Calculate tax amount
            tax_amount = (amount * total_tax_rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            
            return tax_amount
            
        except Exception as e:
            logger.error(f"Error calculating tax: {e}")
            return Decimal("0")
    
    async def update_payment_status(
        self, 
        earning_id: str, 
        status: PaymentStatus, 
        transaction_id: Optional[str] = None
    ) -> bool:
        """Update payment status for earning."""
        try:
            if earning_id not in self.earning_records:
                return False
            
            earning = self.earning_records[earning_id]
            earning.payment_status = status
            
            if transaction_id:
                earning.transaction_id = transaction_id
            
            if status == PaymentStatus.PROCESSING:
                earning.processed_at = datetime.now()
            elif status == PaymentStatus.COMPLETED:
                earning.paid_at = datetime.now()
            
            logger.info(f"Updated payment status for earning {earning_id}: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating payment status: {e}")
            return False
    
    async def get_earnings_summary(
        self, 
        creator_id: str, 
        start_date: datetime, 
        end_date: datetime,
        currency: Currency = Currency.USD
    ) -> EarningsSummary:
        """Get earnings summary for creator in specified period."""
        try:
            creator_earning_ids = self.creator_earnings.get(creator_id, [])
            
            # Filter earnings by date range
            period_earnings = []
            for earning_id in creator_earning_ids:
                earning = self.earning_records[earning_id]
                if start_date <= earning.earned_at <= end_date:
                    period_earnings.append(earning)
            
            # Convert all amounts to target currency
            total_gross = Decimal("0")
            total_net = Decimal("0")
            total_fees = Decimal("0")
            total_taxes = Decimal("0")
            pending_amount = Decimal("0")
            
            earnings_by_type = defaultdict(Decimal)
            earnings_by_platform = defaultdict(Decimal)
            
            for earning in period_earnings:
                # Convert to target currency
                converted_gross = self._convert_currency(earning.gross_amount, earning.currency, currency)
                converted_net = self._convert_currency(earning.net_amount, earning.currency, currency)
                converted_fees = self._convert_currency(
                    earning.platform_fee + earning.payment_processor_fee, 
                    earning.currency, 
                    currency
                )
                converted_taxes = self._convert_currency(earning.tax_amount, earning.currency, currency)
                
                total_gross += converted_gross
                total_net += converted_net
                total_fees += converted_fees
                total_taxes += converted_taxes
                
                # Track pending amounts
                if earning.payment_status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                    pending_amount += converted_net
                
                # Aggregate by type and platform
                earnings_by_type[earning.earning_type] += converted_gross
                earnings_by_platform[earning.source_platform or "unknown"] += converted_gross
            
            return EarningsSummary(
                creator_id=creator_id,
                period_start=start_date,
                period_end=end_date,
                total_gross_earnings=total_gross,
                total_net_earnings=total_net,
                total_fees=total_fees,
                total_taxes=total_taxes,
                currency=currency,
                earnings_by_type=dict(earnings_by_type),
                earnings_by_platform=dict(earnings_by_platform),
                transaction_count=len(period_earnings),
                pending_amount=pending_amount
            )
            
        except Exception as e:
            logger.error(f"Error getting earnings summary: {e}")
            return EarningsSummary(
                creator_id=creator_id,
                period_start=start_date,
                period_end=end_date,
                total_gross_earnings=Decimal("0"),
                total_net_earnings=Decimal("0"),
                total_fees=Decimal("0"),
                total_taxes=Decimal("0"),
                currency=currency
            )
    
    def _convert_currency(self, amount: Decimal, from_currency: Currency, to_currency: Currency) -> Decimal:
        """Convert amount between currencies."""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target currency
        if from_currency != Currency.USD:
            rate_key = f"{from_currency.value}_USD"
            usd_rate = self.currency_exchange_rates.get(rate_key, Decimal("1"))
            amount_usd = amount * usd_rate
        else:
            amount_usd = amount
        
        if to_currency != Currency.USD:
            rate_key = f"{to_currency.value}_USD"
            target_rate = self.currency_exchange_rates.get(rate_key, Decimal("1"))
            final_amount = amount_usd / target_rate
        else:
            final_amount = amount_usd
        
        return final_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    async def get_financial_analytics(
        self, 
        creator_id: str, 
        analysis_days: int = 30
    ) -> Optional[FinancialAnalytics]:
        """Get comprehensive financial analytics for creator."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_days)
            
            # Get current period earnings
            current_summary = await self.get_earnings_summary(creator_id, start_date, end_date)
            
            # Get previous period for comparison
            prev_start = start_date - timedelta(days=analysis_days)
            prev_summary = await self.get_earnings_summary(creator_id, prev_start, start_date)
            
            # Calculate metrics
            total_revenue = current_summary.total_gross_earnings
            average_daily_revenue = total_revenue / Decimal(str(analysis_days))
            
            # Calculate growth rate
            if prev_summary.total_gross_earnings > 0:
                growth_rate = ((total_revenue - prev_summary.total_gross_earnings) / 
                              prev_summary.total_gross_earnings * Decimal("100"))
            else:
                growth_rate = Decimal("0") if total_revenue == 0 else Decimal("100")
            
            # Find top earning type and platform
            top_earning_type = max(
                current_summary.earnings_by_type.items(),
                key=lambda x: x[1],
                default=(EarningType.CONTENT_SALE, Decimal("0"))
            )[0]
            
            best_platform = max(
                current_summary.earnings_by_platform.items(),
                key=lambda x: x[1],
                default=("unknown", Decimal("0"))
            )[0]
            
            # Calculate revenue diversification score
            if current_summary.earnings_by_type:
                total_earnings = sum(current_summary.earnings_by_type.values())
                if total_earnings > 0:
                    # Calculate Herfindahl index (lower = more diversified)
                    shares = [amount / total_earnings for amount in current_summary.earnings_by_type.values()]
                    herfindahl = sum(share ** 2 for share in shares)
                    diversification_score = (1 - herfindahl) * 100  # Convert to 0-100 scale
                else:
                    diversification_score = 0.0
            else:
                diversification_score = 0.0
            
            # Project monthly earnings
            projected_monthly = average_daily_revenue * Decimal("30")
            
            # Calculate tax efficiency score
            if current_summary.total_gross_earnings > 0:
                tax_rate = (current_summary.total_taxes / current_summary.total_gross_earnings * 100)
                tax_efficiency_score = max(0, 100 - float(tax_rate))  # Higher score = lower tax rate
            else:
                tax_efficiency_score = 100.0
            
            # Generate recommendations
            recommendations = []
            
            if diversification_score < 30:
                recommendations.append("Diversify revenue streams to reduce risk")
            
            if growth_rate < 0:
                recommendations.append("Focus on growing existing revenue channels")
            
            if current_summary.total_taxes / current_summary.total_gross_earnings > Decimal("0.3"):
                recommendations.append("Consider tax optimization strategies")
            
            if len(current_summary.earnings_by_platform) == 1:
                recommendations.append("Expand to multiple platforms to increase reach")
            
            if current_summary.pending_amount > current_summary.total_net_earnings * Decimal("0.5"):
                recommendations.append("Monitor payment processing delays")
            
            return FinancialAnalytics(
                creator_id=creator_id,
                analysis_period_days=analysis_days,
                total_revenue=total_revenue,
                average_daily_revenue=average_daily_revenue,
                revenue_growth_rate=growth_rate,
                top_earning_type=top_earning_type,
                best_performing_platform=best_platform,
                revenue_diversification_score=diversification_score,
                projected_monthly_earnings=projected_monthly,
                tax_efficiency_score=tax_efficiency_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error getting financial analytics: {e}")
            return None
    
    async def get_tax_report(
        self, 
        creator_id: str, 
        tax_year: int, 
        jurisdiction: TaxJurisdiction
    ) -> Dict[str, Any]:
        """Generate tax report for creator."""
        try:
            # Get earnings for tax year
            start_date = datetime(tax_year, 1, 1)
            end_date = datetime(tax_year, 12, 31, 23, 59, 59)
            
            creator_earning_ids = self.creator_earnings.get(creator_id, [])
            
            # Filter by jurisdiction and date
            tax_earnings = []
            for earning_id in creator_earning_ids:
                earning = self.earning_records[earning_id]
                if (earning.tax_jurisdiction == jurisdiction and 
                    start_date <= earning.earned_at <= end_date):
                    tax_earnings.append(earning)
            
            # Get tax configuration
            tax_config = self.tax_configurations.get(jurisdiction)
            reporting_currency = tax_config.reporting_currency if tax_config else Currency.USD
            
            # Aggregate earnings by type
            earnings_by_type = defaultdict(Decimal)
            total_gross_income = Decimal("0")
            total_taxes_paid = Decimal("0")
            total_business_expenses = Decimal("0")  # Platform fees + processor fees
            
            for earning in tax_earnings:
                # Convert to reporting currency
                gross_amount = self._convert_currency(
                    earning.gross_amount, earning.currency, reporting_currency
                )
                tax_amount = self._convert_currency(
                    earning.tax_amount, earning.currency, reporting_currency
                )
                business_expenses = self._convert_currency(
                    earning.platform_fee + earning.payment_processor_fee,
                    earning.currency, reporting_currency
                )
                
                earnings_by_type[earning.earning_type] += gross_amount
                total_gross_income += gross_amount
                total_taxes_paid += tax_amount
                total_business_expenses += business_expenses
            
            # Calculate net taxable income
            net_taxable_income = total_gross_income - total_business_expenses
            
            return {
                "creator_id": creator_id,
                "tax_year": tax_year,
                "jurisdiction": jurisdiction.value,
                "reporting_currency": reporting_currency.value,
                "total_gross_income": float(total_gross_income),
                "total_business_expenses": float(total_business_expenses),
                "net_taxable_income": float(net_taxable_income),
                "total_taxes_paid": float(total_taxes_paid),
                "earnings_by_type": {k.value: float(v) for k, v in earnings_by_type.items()},
                "transaction_count": len(tax_earnings),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            return {}
    
    async def process_bulk_earnings(self, earnings_data: List[Dict[str, Any]]) -> List[str]:
        """Process multiple earnings in bulk."""
        earning_ids = []
        
        for earning_data in earnings_data:
            try:
                earning_id = await self.record_earning(
                    creator_id=earning_data["creator_id"],
                    earning_type=EarningType(earning_data["earning_type"]),
                    gross_amount=Decimal(str(earning_data["gross_amount"])),
                    currency=Currency(earning_data["currency"]),
                    tax_jurisdiction=TaxJurisdiction(earning_data["tax_jurisdiction"]),
                    source_platform=earning_data.get("source_platform", "ainflue"),
                    payment_method=earning_data.get("payment_method", "stripe"),
                    metadata=earning_data.get("metadata", {})
                )
                earning_ids.append(earning_id)
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error processing bulk earning: {e}")
                continue
        
        logger.info(f"Processed {len(earning_ids)} earnings in bulk")
        return earning_ids
    
    async def get_creator_earnings_by_status(
        self, 
        creator_id: str, 
        status: PaymentStatus
    ) -> List[EarningRecord]:
        """Get creator earnings filtered by payment status."""
        creator_earning_ids = self.creator_earnings.get(creator_id, [])
        
        filtered_earnings = []
        for earning_id in creator_earning_ids:
            earning = self.earning_records[earning_id]
            if earning.payment_status == status:
                filtered_earnings.append(earning)
        
        return filtered_earnings
    
    def update_exchange_rates(self, rates: Dict[str, Decimal]) -> bool:
        """Update currency exchange rates."""
        try:
            self.currency_exchange_rates.update(rates)
            logger.info(f"Updated {len(rates)} exchange rates")
            return True
        except Exception as e:
            logger.error(f"Error updating exchange rates: {e}")
            return False
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics."""
        total_earnings = len(self.earning_records)
        total_creators = len(self.creator_earnings)
        
        if total_earnings == 0:
            return {
                "total_earnings_recorded": 0,
                "total_creators": 0,
                "total_gross_revenue": 0,
                "total_net_revenue": 0,
                "average_earning_amount": 0,
                "status_distribution": {},
                "currency_distribution": {},
                "platform_distribution": {}
            }
        
        # Calculate totals and distributions
        total_gross = Decimal("0")
        total_net = Decimal("0")
        status_distribution = defaultdict(int)
        currency_distribution = defaultdict(int)
        platform_distribution = defaultdict(int)
        
        for earning in self.earning_records.values():
            # Convert to USD for totals
            gross_usd = self._convert_currency(earning.gross_amount, earning.currency, Currency.USD)
            net_usd = self._convert_currency(earning.net_amount, earning.currency, Currency.USD)
            
            total_gross += gross_usd
            total_net += net_usd
            
            status_distribution[earning.payment_status.value] += 1
            currency_distribution[earning.currency.value] += 1
            platform_distribution[earning.source_platform or "unknown"] += 1
        
        average_earning = total_gross / Decimal(str(total_earnings))
        
        return {
            "total_earnings_recorded": total_earnings,
            "total_creators": total_creators,
            "total_gross_revenue_usd": float(total_gross),
            "total_net_revenue_usd": float(total_net),
            "average_earning_amount_usd": float(average_earning),
            "status_distribution": dict(status_distribution),
            "currency_distribution": dict(currency_distribution),
            "platform_distribution": dict(platform_distribution),
            "supported_currencies": len(Currency),
            "supported_tax_jurisdictions": len(self.tax_configurations)
        }


# Global service instance
_earnings_service_instance = None

def get_creator_earnings_service() -> CreatorEarningsService:
    """Get singleton instance of CreatorEarningsService."""
    global _earnings_service_instance
    if _earnings_service_instance is None:
        _earnings_service_instance = CreatorEarningsService()
    return _earnings_service_instance


# Example usage and testing
async def example_usage() -> None:
    """Example usage of Creator Earnings Service."""
    service = get_creator_earnings_service()
    
    # Record various earnings
    earnings = [
        (EarningType.CONTENT_SALE, Decimal("29.99"), Currency.USD, TaxJurisdiction.US, "youtube"),
        (EarningType.SUBSCRIPTION, Decimal("9.99"), Currency.USD, TaxJurisdiction.US, "patreon"),
        (EarningType.LICENSING, Decimal("150.00"), Currency.EUR, TaxJurisdiction.DE, "ainflue"),
        (EarningType.TIP_DONATION, Decimal("5.00"), Currency.USD, TaxJurisdiction.US, "twitch"),
        (EarningType.SPONSORSHIP, Decimal("500.00"), Currency.USD, TaxJurisdiction.US, "instagram"),
    ]
    
    creator_id = "creator_123"
    earning_ids = []
    
    for earning_type, amount, currency, jurisdiction, platform in earnings:
        earning_id = await service.record_earning(
            creator_id=creator_id,
            earning_type=earning_type,
            gross_amount=amount,
            currency=currency,
            tax_jurisdiction=jurisdiction,
            source_platform=platform,
            metadata={"test": True}
        )
        earning_ids.append(earning_id)
        print(f"Recorded earning: {earning_id}")
    
    # Update payment status
    await service.update_payment_status(earning_ids[0], PaymentStatus.COMPLETED, "txn_12345")
    
    # Get earnings summary
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    summary = await service.get_earnings_summary(creator_id, start_date, end_date)
    
    print(f"Earnings Summary:")
    print(f"  Total Gross: {summary.total_gross_earnings} {summary.currency}")
    print(f"  Total Net: {summary.total_net_earnings} {summary.currency}")
    print(f"  Total Fees: {summary.total_fees} {summary.currency}")
    print(f"  Total Taxes: {summary.total_taxes} {summary.currency}")
    print(f"  Transactions: {summary.transaction_count}")
    
    # Get financial analytics
    analytics = await service.get_financial_analytics(creator_id, 30)
    if analytics:
        print(f"Financial Analytics:")
        print(f"  Revenue Growth: {analytics.revenue_growth_rate:.1f}%")
        print(f"  Diversification Score: {analytics.revenue_diversification_score:.1f}")
        print(f"  Projected Monthly: {analytics.projected_monthly_earnings} USD")
        print(f"  Recommendations: {analytics.recommendations}")
    
    # Get tax report
    tax_report = await service.get_tax_report(creator_id, 2024, TaxJurisdiction.US)
    print(f"Tax Report: {tax_report}")
    
    # Get service metrics
    metrics = service.get_service_metrics()
    print(f"Service Metrics: {metrics}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())