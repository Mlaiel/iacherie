"""Currency Localization Engine - Ainflue Platform
================================================================================
Module: core/i18n/currency_localization.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Currency Localization Engine - Advanced Financial Processing
Responsibility: Multi-currency formatting, regional compliance, and financial localization
Technologies: Python, Currency APIs, Regional Standards, Financial Formatting
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Currency input → Regional detection → Format conversion → Cultural adaptation → 
Compliance validation → Exchange rate processing → Localized display
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
import re

logger = logging.getLogger(__name__)


class CurrencyCode(Enum):
    """ISO 4217 Currency Codes"""    # Major World Currencies
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    JPY = "JPY"  # Japanese Yen
    GBP = "GBP"  # British Pound Sterling
    CHF = "CHF"  # Swiss Franc
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CNY = "CNY"  # Chinese Yuan
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    
    # Middle East & Africa
    AED = "AED"  # UAE Dirham
    SAR = "SAR"  # Saudi Riyal
    QAR = "QAR"  # Qatari Riyal
    KWD = "KWD"  # Kuwaiti Dinar
    BHD = "BHD"  # Bahraini Dinar
    OMR = "OMR"  # Omani Rial
    EGP = "EGP"  # Egyptian Pound
    MAD = "MAD"  # Moroccan Dirham
    TND = "TND"  # Tunisian Dinar
    ZAR = "ZAR"  # South African Rand
    
    # European Currencies
    NOK = "NOK"  # Norwegian Krone
    SEK = "SEK"  # Swedish Krona
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    CZK = "CZK"  # Czech Koruna
    HUF = "HUF"  # Hungarian Forint
    
    # Asian Currencies
    KRW = "KRW"  # South Korean Won
    SGD = "SGD"  # Singapore Dollar
    THB = "THB"  # Thai Baht
    MYR = "MYR"  # Malaysian Ringgit
    IDR = "IDR"  # Indonesian Rupiah
    PHP = "PHP"  # Philippine Peso
    VND = "VND"  # Vietnamese Dong
    
    # Latin American Currencies
    MXN = "MXN"  # Mexican Peso
    ARS = "ARS"  # Argentine Peso
    CLP = "CLP"  # Chilean Peso
    COP = "COP"  # Colombian Peso
    PEN = "PEN"  # Peruvian Sol


class NumberingSystem(Enum):
    """Numbering systems for different locales"""    WESTERN = "western"      # 0123456789
    ARABIC_INDIC = "arabic"  # ٠١٢٣٤٥٦٧٨٩
    PERSIAN = "persian"      # ۰۱۲۳۴۵۶۷۸۹
    DEVANAGARI = "devanagari"  # ०१२३४५६७८९
    CHINESE = "chinese"      # 〇一二三四五六七八九
    HEBREW = "hebrew"        # Hebrew numerals


class CurrencyPosition(Enum):
    """Currency symbol position"""    BEFORE = "before"        # $100
    AFTER = "after"          # 100$
    BEFORE_WITH_SPACE = "before_space"  # $ 100
    AFTER_WITH_SPACE = "after_space"    # 100 $


class GroupingSeparator(Enum):
    """Thousands separator types"""    COMMA = ","      # 1,000
    PERIOD = "."     # 1.000
    SPACE = " "      # 1 000
    THIN_SPACE = "'"  # 1'000
    NONE = ""        # 1000


class DecimalSeparator(Enum):
    """Decimal separator types"""    PERIOD = "."     # 1.50
    COMMA = ","      # 1,50
    ARABIC = "٫"     # Arabic decimal separator


@dataclass
class CurrencyFormat:
    """Currency formatting configuration"""    code: CurrencyCode
    symbol: str
    name: str
    native_name: str
    decimal_places: int
    position: CurrencyPosition
    grouping_separator: GroupingSeparator
    decimal_separator: DecimalSeparator
    numbering_system: NumberingSystem
    negative_format: str  # Template for negative numbers
    zero_format: str     # Template for zero values
    rounding_mode: str   # Rounding behavior
    cultural_context: Dict[str, Any]


@dataclass
class RegionalCurrency:
    """Regional currency preferences"""    region_code: str
    country_codes: List[str]
    primary_currency: CurrencyCode
    accepted_currencies: List[CurrencyCode]
    currency_format: CurrencyFormat
    exchange_rate_source: str
    regulatory_requirements: List[str]
    taxation_rules: Dict[str, Any]
    payment_methods: List[str]
    banking_holidays: List[str]


@dataclass
class ExchangeRate:
    """Exchange rate information"""    from_currency: CurrencyCode
    to_currency: CurrencyCode
    rate: Decimal
    timestamp: datetime
    source: str
    bid_rate: Optional[Decimal] = None
    ask_rate: Optional[Decimal] = None
    spread: Optional[Decimal] = None
    volatility: Optional[float] = None


@dataclass
class CurrencyConversion:
    """Currency conversion result"""    original_amount: Decimal
    original_currency: CurrencyCode
    converted_amount: Decimal
    converted_currency: CurrencyCode
    exchange_rate: ExchangeRate
    conversion_fee: Optional[Decimal] = None
    formatted_original: str = ""
    formatted_converted: str = ""
    conversion_date: datetime = field(default_factory=datetime.now)


class CurrencyLocalization:
    """Advanced currency localization and formatting engine"""    
    def __init__(self):
        self.currency_formats: Dict[str, CurrencyFormat] = {}
        self.regional_currencies: Dict[str, RegionalCurrency] = {}
        self.exchange_rates: Dict[Tuple[CurrencyCode, CurrencyCode], ExchangeRate] = {}
        self.format_cache: Dict[str, str] = {}
        self.conversion_cache: Dict[str, CurrencyConversion] = {}
        
        # Initialize currency system
        self._initialize_currency_formats()
        self._initialize_regional_currencies()
        self._initialize_mock_exchange_rates()
        
        logger.info("Currency Localization Engine initialized")
    
    def _initialize_currency_formats(self):
        """Initialize currency format configurations"""        
        # US Dollar
        self.currency_formats["USD"] = CurrencyFormat(
            code=CurrencyCode.USD,
            symbol="$",
            name="US Dollar",
            native_name="US Dollar",
            decimal_places=2,
            position=CurrencyPosition.BEFORE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.WESTERN,
            negative_format="($#,##0.00)",
            zero_format="$0.00",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "global_reserve", "usage": "international"}
        )
        
        # Euro
        self.currency_formats["EUR"] = CurrencyFormat(
            code=CurrencyCode.EUR,
            symbol="€",
            name="Euro",
            native_name="Euro",
            decimal_places=2,
            position=CurrencyPosition.AFTER_WITH_SPACE,
            grouping_separator=GroupingSeparator.SPACE,
            decimal_separator=DecimalSeparator.COMMA,
            numbering_system=NumberingSystem.WESTERN,
            negative_format="-# ##0,00 €",
            zero_format="0,00 €",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "regional_reserve", "usage": "european_union"}
        )
        
        # Japanese Yen
        self.currency_formats["JPY"] = CurrencyFormat(
            code=CurrencyCode.JPY,
            symbol="¥",
            name="Japanese Yen",
            native_name="円",
            decimal_places=0,
            position=CurrencyPosition.BEFORE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.WESTERN,
            negative_format="-¥#,##0",
            zero_format="¥0",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "major_reserve", "usage": "east_asia"}
        )
        
        # British Pound
        self.currency_formats["GBP"] = CurrencyFormat(
            code=CurrencyCode.GBP,
            symbol="£",
            name="British Pound Sterling",
            native_name="Pound Sterling",
            decimal_places=2,
            position=CurrencyPosition.BEFORE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.WESTERN,
            negative_format="-£#,##0.00",
            zero_format="£0.00",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "historical_reserve", "usage": "commonwealth"}
        )
        
        # Chinese Yuan
        self.currency_formats["CNY"] = CurrencyFormat(
            code=CurrencyCode.CNY,
            symbol="¥",
            name="Chinese Yuan",
            native_name="人民币",
            decimal_places=2,
            position=CurrencyPosition.BEFORE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.WESTERN,
            negative_format="-¥#,##0.00",
            zero_format="¥0.00",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "emerging_reserve", "usage": "greater_china"}
        )
        
        # UAE Dirham
        self.currency_formats["AED"] = CurrencyFormat(
            code=CurrencyCode.AED,
            symbol="د.إ",
            name="UAE Dirham",
            native_name="درهم إماراتي",
            decimal_places=2,
            position=CurrencyPosition.AFTER_WITH_SPACE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.ARABIC_INDIC,
            negative_format="-#,##0.00 د.إ",
            zero_format="0.00 د.إ",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "regional", "usage": "gulf_cooperation"}
        )
        
        # Saudi Riyal
        self.currency_formats["SAR"] = CurrencyFormat(
            code=CurrencyCode.SAR,
            symbol="ر.س",
            name="Saudi Riyal",
            native_name="ريال سعودي",
            decimal_places=2,
            position=CurrencyPosition.AFTER_WITH_SPACE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.ARABIC_INDIC,
            negative_format="-#,##0.00 ر.س",
            zero_format="0.00 ر.س",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "oil_economy", "usage": "saudi_arabia"}
        )
        
        # Egyptian Pound
        self.currency_formats["EGP"] = CurrencyFormat(
            code=CurrencyCode.EGP,
            symbol="ج.م",
            name="Egyptian Pound",
            native_name="جنيه مصري",
            decimal_places=2,
            position=CurrencyPosition.AFTER_WITH_SPACE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.ARABIC_INDIC,
            negative_format="-#,##0.00 ج.م",
            zero_format="0.00 ج.م",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "regional", "usage": "north_africa"}
        )
        
        # Moroccan Dirham
        self.currency_formats["MAD"] = CurrencyFormat(
            code=CurrencyCode.MAD,
            symbol="د.م.",
            name="Moroccan Dirham",
            native_name="درهم مغربي",
            decimal_places=2,
            position=CurrencyPosition.AFTER_WITH_SPACE,
            grouping_separator=GroupingSeparator.SPACE,
            decimal_separator=DecimalSeparator.COMMA,
            numbering_system=NumberingSystem.WESTERN,  # Morocco uses Western numerals
            negative_format="-# ##0,00 د.م.",
            zero_format="0,00 د.م.",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "maghreb", "usage": "morocco"}
        )
        
        # Indian Rupee
        self.currency_formats["INR"] = CurrencyFormat(
            code=CurrencyCode.INR,
            symbol="₹",
            name="Indian Rupee",
            native_name="भारतीय रुपया",
            decimal_places=2,
            position=CurrencyPosition.BEFORE,
            grouping_separator=GroupingSeparator.COMMA,
            decimal_separator=DecimalSeparator.PERIOD,
            numbering_system=NumberingSystem.DEVANAGARI,
            negative_format="-₹#,##0.00",
            zero_format="₹0.00",
            rounding_mode="ROUND_HALF_UP",
            cultural_context={"importance": "south_asia", "usage": "india"}
        )
        
        logger.info(f"Initialized {len(self.currency_formats)} currency formats")
    
    def _initialize_regional_currencies(self):
        """Initialize regional currency configurations"""        
        # United States
        self.regional_currencies["US"] = RegionalCurrency(
            region_code="US",
            country_codes=["US"],
            primary_currency=CurrencyCode.USD,
            accepted_currencies=[CurrencyCode.USD],
            currency_format=self.currency_formats["USD"],
            exchange_rate_source="federal_reserve",
            regulatory_requirements=["sec_compliance", "tax_reporting"],
            taxation_rules={"sales_tax": "state_based", "income_tax": "federal_state"},
            payment_methods=["credit_card", "debit_card", "ach", "wire_transfer"],
            banking_holidays=["new_year", "independence_day", "thanksgiving", "christmas"]
        )
        
        # European Union
        self.regional_currencies["EU"] = RegionalCurrency(
            region_code="EU",
            country_codes=["DE", "FR", "IT", "ES", "NL", "BE", "AT", "PT", "IE", "FI", "GR"],
            primary_currency=CurrencyCode.EUR,
            accepted_currencies=[CurrencyCode.EUR, CurrencyCode.USD],
            currency_format=self.currency_formats["EUR"],
            exchange_rate_source="european_central_bank",
            regulatory_requirements=["mifid2", "gdpr_compliance", "psd2"],
            taxation_rules={"vat": "country_specific", "withholding": "eu_directive"},
            payment_methods=["sepa", "credit_card", "instant_payment"],
            banking_holidays=["new_year", "easter", "christmas", "national_days"]
        )
        
        # United Kingdom
        self.regional_currencies["GB"] = RegionalCurrency(
            region_code="GB",
            country_codes=["GB"],
            primary_currency=CurrencyCode.GBP,
            accepted_currencies=[CurrencyCode.GBP, CurrencyCode.USD, CurrencyCode.EUR],
            currency_format=self.currency_formats["GBP"],
            exchange_rate_source="bank_of_england",
            regulatory_requirements=["fca_compliance", "brexit_rules"],
            taxation_rules={"vat": "20_percent", "corporation_tax": "19_percent"},
            payment_methods=["faster_payments", "chaps", "credit_card"],
            banking_holidays=["new_year", "easter", "christmas", "bank_holidays"]
        )
        
        # UAE
        self.regional_currencies["AE"] = RegionalCurrency(
            region_code="AE",
            country_codes=["AE"],
            primary_currency=CurrencyCode.AED,
            accepted_currencies=[CurrencyCode.AED, CurrencyCode.USD],
            currency_format=self.currency_formats["AED"],
            exchange_rate_source="central_bank_uae",
            regulatory_requirements=["adgm_compliance", "islamic_finance"],
            taxation_rules={"vat": "5_percent", "corporate_tax": "varies_by_emirate"},
            payment_methods=["uae_switch", "credit_card", "digital_wallet"],
            banking_holidays=["eid_al_fitr", "eid_al_adha", "national_day", "ramadan"]
        )
        
        # Saudi Arabia
        self.regional_currencies["SA"] = RegionalCurrency(
            region_code="SA",
            country_codes=["SA"],
            primary_currency=CurrencyCode.SAR,
            accepted_currencies=[CurrencyCode.SAR, CurrencyCode.USD],
            currency_format=self.currency_formats["SAR"],
            exchange_rate_source="saudi_central_bank",
            regulatory_requirements=["sama_compliance", "islamic_finance", "anti_money_laundering"],
            taxation_rules={"vat": "15_percent", "zakat": "2.5_percent"},
            payment_methods=["mada", "sarie", "credit_card"],
            banking_holidays=["eid_al_fitr", "eid_al_adha", "national_day", "founding_day"]
        )
        
        # Egypt
        self.regional_currencies["EG"] = RegionalCurrency(
            region_code="EG",
            country_codes=["EG"],
            primary_currency=CurrencyCode.EGP,
            accepted_currencies=[CurrencyCode.EGP, CurrencyCode.USD],
            currency_format=self.currency_formats["EGP"],
            exchange_rate_source="central_bank_egypt",
            regulatory_requirements=["cbe_compliance", "foreign_exchange_controls"],
            taxation_rules={"vat": "14_percent", "withholding": "varies"},
            payment_methods=["meeza", "credit_card", "mobile_wallet"],
            banking_holidays=["eid_al_fitr", "eid_al_adha", "revolution_day", "sinai_liberation"]
        )
        
        # Morocco
        self.regional_currencies["MA"] = RegionalCurrency(
            region_code="MA",
            country_codes=["MA"],
            primary_currency=CurrencyCode.MAD,
            accepted_currencies=[CurrencyCode.MAD, CurrencyCode.EUR],
            currency_format=self.currency_formats["MAD"],
            exchange_rate_source="bank_al_maghrib",
            regulatory_requirements=["bam_compliance", "foreign_exchange_controls"],
            taxation_rules={"vat": "20_percent", "corporate_tax": "31_percent"},
            payment_methods=["cmi", "credit_card", "mobile_payment"],
            banking_holidays=["eid_al_fitr", "eid_al_adha", "independence_day", "throne_day"]
        )
        
        logger.info(f"Initialized {len(self.regional_currencies)} regional currencies")
    
    def _initialize_mock_exchange_rates(self):
        """Initialize mock exchange rates for development"""        # Mock rates - in production, these would come from real APIs
        base_rates = {
            (CurrencyCode.USD, CurrencyCode.EUR): Decimal("0.85"),
            (CurrencyCode.USD, CurrencyCode.GBP): Decimal("0.75"),
            (CurrencyCode.USD, CurrencyCode.JPY): Decimal("110.50"),
            (CurrencyCode.USD, CurrencyCode.CNY): Decimal("6.45"),
            (CurrencyCode.USD, CurrencyCode.AED): Decimal("3.67"),
            (CurrencyCode.USD, CurrencyCode.SAR): Decimal("3.75"),
            (CurrencyCode.USD, CurrencyCode.EGP): Decimal("30.85"),
            (CurrencyCode.USD, CurrencyCode.MAD): Decimal("10.15"),
            (CurrencyCode.USD, CurrencyCode.INR): Decimal("83.25"),
        }
        
        # Create exchange rate objects
        for (from_curr, to_curr), rate in base_rates.items():
            self.exchange_rates[(from_curr, to_curr)] = ExchangeRate(
                from_currency=from_curr,
                to_currency=to_curr,
                rate=rate,
                timestamp=datetime.now(),
                source="mock_provider",
                bid_rate=rate * Decimal("0.999"),
                ask_rate=rate * Decimal("1.001"),
                spread=rate * Decimal("0.002")
            )
            
            # Add reverse rate
            reverse_rate = Decimal("1") / rate
            self.exchange_rates[(to_curr, from_curr)] = ExchangeRate(
                from_currency=to_curr,
                to_currency=from_curr,
                rate=reverse_rate,
                timestamp=datetime.now(),
                source="mock_provider",
                bid_rate=reverse_rate * Decimal("0.999"),
                ask_rate=reverse_rate * Decimal("1.001"),
                spread=reverse_rate * Decimal("0.002")
            )
        
        logger.info(f"Initialized {len(self.exchange_rates)} exchange rates")
    
    async def format_currency(
        self,
        amount: Union[Decimal, float, int],
        currency_code: str,
        locale: str = None,
        custom_format: CurrencyFormat = None
    ) -> str:
        """Format currency amount according to locale and cultural standards"""        try:
            # Convert amount to Decimal for precision
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            # Get currency format
            currency_format = custom_format or self.currency_formats.get(currency_code)
            if not currency_format:
                logger.warning(f"No format found for currency: {currency_code}")
                return f"{amount} {currency_code}"
            
            # Round amount according to currency rules
            rounded_amount = amount.quantize(
                Decimal('0.01') if currency_format.decimal_places == 2 else Decimal('1'),
                rounding=ROUND_HALF_UP
            )
            
            # Handle zero and negative amounts
            if rounded_amount == 0:
                return self._apply_zero_format(currency_format)
            
            if rounded_amount < 0:
                return self._apply_negative_format(abs(rounded_amount), currency_format)
            
            # Convert to appropriate numbering system
            formatted_number = self._convert_numbering_system(
                rounded_amount, currency_format
            )
            
            # Apply grouping and decimal separators
            formatted_amount = self._apply_separators(formatted_number, currency_format)
            
            # Add currency symbol
            formatted_currency = self._add_currency_symbol(formatted_amount, currency_format)
            
            # Cache the result
            cache_key = f"{amount}_{currency_code}_{locale}"
            self.format_cache[cache_key] = formatted_currency
            
            return formatted_currency
            
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return f"{amount} {currency_code}"
    
    def _convert_numbering_system(self, amount: Decimal, currency_format: CurrencyFormat) -> str:
        """Convert number to appropriate numbering system"""        if currency_format.numbering_system == NumberingSystem.WESTERN:
            return str(amount)
        
        western_digits = "0123456789"
        amount_str = str(amount)
        
        if currency_format.numbering_system == NumberingSystem.ARABIC_INDIC:
            arabic_digits = "٠١٢٣٤٥٦٧٨٩"
            translation_table = str.maketrans(western_digits, arabic_digits)
            return amount_str.translate(translation_table)
        
        elif currency_format.numbering_system == NumberingSystem.PERSIAN:
            persian_digits = "۰۱۲۳۴۵۶۷۸۹"
            translation_table = str.maketrans(western_digits, persian_digits)
            return amount_str.translate(translation_table)
        
        elif currency_format.numbering_system == NumberingSystem.DEVANAGARI:
            devanagari_digits = "०१२३४५६७८९"
            translation_table = str.maketrans(western_digits, devanagari_digits)
            return amount_str.translate(translation_table)
        
        return amount_str
    
    def _apply_separators(self, formatted_number: str, currency_format: CurrencyFormat) -> str:
        """Apply grouping and decimal separators"""        # Split into integer and decimal parts
        if '.' in formatted_number:
            integer_part, decimal_part = formatted_number.split('.')
        else:
            integer_part, decimal_part = formatted_number, ""
        
        # Apply grouping separator to integer part
        if currency_format.grouping_separator != GroupingSeparator.NONE and len(integer_part) > 3:
            # Group digits in threes from right to left
            grouped_digits = []
            for i, digit in enumerate(reversed(integer_part)):
                if i > 0 and i % 3 == 0:
                    grouped_digits.append(currency_format.grouping_separator.value)
                grouped_digits.append(digit)
            integer_part = ''.join(reversed(grouped_digits))
        
        # Combine with decimal part
        if decimal_part and currency_format.decimal_places > 0:
            # Pad or truncate decimal part
            if len(decimal_part) < currency_format.decimal_places:
                decimal_part = decimal_part.ljust(currency_format.decimal_places, '0')
            else:
                decimal_part = decimal_part[:currency_format.decimal_places]
            
            return f"{integer_part}{currency_format.decimal_separator.value}{decimal_part}"
        else:
            return integer_part
    
    def _add_currency_symbol(self, formatted_amount: str, currency_format: CurrencyFormat) -> str:
        """Add currency symbol in the correct position"""        symbol = currency_format.symbol
        
        if currency_format.position == CurrencyPosition.BEFORE:
            return f"{symbol}{formatted_amount}"
        elif currency_format.position == CurrencyPosition.AFTER:
            return f"{formatted_amount}{symbol}"
        elif currency_format.position == CurrencyPosition.BEFORE_WITH_SPACE:
            return f"{symbol} {formatted_amount}"
        elif currency_format.position == CurrencyPosition.AFTER_WITH_SPACE:
            return f"{formatted_amount} {symbol}"
        
        return f"{symbol}{formatted_amount}"  # Default
    
    def _apply_negative_format(self, amount: Decimal, currency_format: CurrencyFormat) -> str:
        """Apply negative number formatting"""        # This is a simplified implementation
        # In production, this would parse the negative_format template
        formatted_positive = self._apply_separators(
            self._convert_numbering_system(amount, currency_format),
            currency_format
        )
        
        if "($" in currency_format.negative_format:
            return f"({currency_format.symbol}{formatted_positive})"
        else:
            return f"-{self._add_currency_symbol(formatted_positive, currency_format)}"
    
    def _apply_zero_format(self, currency_format: CurrencyFormat) -> str:
        """Apply zero value formatting"""        # Simple implementation of zero format
        if currency_format.decimal_places > 0:
            zero_amount = "0" + currency_format.decimal_separator.value + "0" * currency_format.decimal_places
        else:
            zero_amount = "0"
        
        return self._add_currency_symbol(zero_amount, currency_format)
    
    async def convert_currency(
        self,
        amount: Union[Decimal, float, int],
        from_currency: str,
        to_currency: str,
        use_cached_rate: bool = True
    ) -> CurrencyConversion:
        """Convert currency amount with exchange rate"""        try:
            # Convert to Decimal for precision
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            from_code = CurrencyCode(from_currency)
            to_code = CurrencyCode(to_currency)
            
            # Check for same currency
            if from_code == to_code:
                return CurrencyConversion(
                    original_amount=amount,
                    original_currency=from_code,
                    converted_amount=amount,
                    converted_currency=to_code,
                    exchange_rate=ExchangeRate(
                        from_currency=from_code,
                        to_currency=to_code,
                        rate=Decimal("1.0"),
                        timestamp=datetime.now(),
                        source="identity"
                    ),
                    formatted_original=await self.format_currency(amount, from_currency),
                    formatted_converted=await self.format_currency(amount, to_currency)
                )
            
            # Get exchange rate
            exchange_rate = await self._get_exchange_rate(from_code, to_code, use_cached_rate)
            
            # Perform conversion
            converted_amount = amount * exchange_rate.rate
            
            # Format both amounts
            formatted_original = await self.format_currency(amount, from_currency)
            formatted_converted = await self.format_currency(converted_amount, to_currency)
            
            conversion = CurrencyConversion(
                original_amount=amount,
                original_currency=from_code,
                converted_amount=converted_amount,
                converted_currency=to_code,
                exchange_rate=exchange_rate,
                formatted_original=formatted_original,
                formatted_converted=formatted_converted
            )
            
            # Cache conversion
            cache_key = f"{amount}_{from_currency}_{to_currency}_{exchange_rate.timestamp.date()}"
            self.conversion_cache[cache_key] = conversion
            
            return conversion
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            raise
    
    async def _get_exchange_rate(
        self,
        from_currency: CurrencyCode,
        to_currency: CurrencyCode,
        use_cached: bool = True
    ) -> ExchangeRate:
        """Get exchange rate between currencies"""        # Check cache first
        rate_key = (from_currency, to_currency)
        if use_cached and rate_key in self.exchange_rates:
            cached_rate = self.exchange_rates[rate_key]
            # Check if rate is not too old (in production, implement proper TTL)
            if (datetime.now() - cached_rate.timestamp).seconds < 3600:  # 1 hour
                return cached_rate
        
        # In production, this would fetch from real exchange rate APIs
        # For now, return mock rate or fetch from existing cache
        if rate_key in self.exchange_rates:
            return self.exchange_rates[rate_key]
        
        # If no direct rate, try to find indirect rate via USD
        if from_currency != CurrencyCode.USD and to_currency != CurrencyCode.USD:
            usd_from_key = (from_currency, CurrencyCode.USD)
            usd_to_key = (CurrencyCode.USD, to_currency)
            
            if usd_from_key in self.exchange_rates and usd_to_key in self.exchange_rates:
                rate_to_usd = self.exchange_rates[usd_from_key].rate
                rate_from_usd = self.exchange_rates[usd_to_key].rate
                indirect_rate = rate_to_usd * rate_from_usd
                
                # Create and cache the indirect rate
                exchange_rate = ExchangeRate(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    rate=indirect_rate,
                    timestamp=datetime.now(),
                    source="indirect_calculation"
                )
                
                self.exchange_rates[rate_key] = exchange_rate
                return exchange_rate
        
        # Fallback: return 1:1 rate with warning
        logger.warning(f"No exchange rate found for {from_currency} to {to_currency}, using 1:1")
        return ExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=Decimal("1.0"),
            timestamp=datetime.now(),
            source="fallback"
        )
    
    async def get_regional_currency_info(self, region_code: str) -> Optional[RegionalCurrency]:
        """Get regional currency information"""        return self.regional_currencies.get(region_code.upper())
    
    async def validate_currency_amount(
        self,
        amount: Union[Decimal, float, int],
        currency_code: str,
        region_code: str = None
    ) -> Dict[str, Any]:
        """Validate currency amount according to regional rules"""        try:
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            validation_result = {
                "is_valid": True,
                "issues": [],
                "recommendations": []
            }
            
            # Check currency format
            currency_format = self.currency_formats.get(currency_code)
            if not currency_format:
                validation_result["is_valid"] = False
                validation_result["issues"].append("unsupported_currency")
                return validation_result
            
            # Check decimal places
            decimal_places = len(str(amount).split('.')[-1]) if '.' in str(amount) else 0
            if decimal_places > currency_format.decimal_places:
                validation_result["issues"].append("excessive_decimal_places")
                validation_result["recommendations"].append(f"round_to_{currency_format.decimal_places}_places")
            
            # Check regional compliance
            if region_code:
                regional_info = await self.get_regional_currency_info(region_code)
                if regional_info:
                    if CurrencyCode(currency_code) not in regional_info.accepted_currencies:
                        validation_result["issues"].append("currency_not_accepted_in_region")
                        validation_result["recommendations"].append(f"use_{regional_info.primary_currency.value}")
            
            # Check for reasonable amount ranges
            if amount < 0:
                validation_result["issues"].append("negative_amount")
            
            if amount > Decimal("999999999999"):  # Arbitrary large limit
                validation_result["issues"].append("amount_too_large")
                validation_result["recommendations"].append("verify_amount_accuracy")
            
            validation_result["is_valid"] = len(validation_result["issues"]) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating currency amount: {e}")
            return {
                "is_valid": False,
                "issues": ["validation_error"],
                "error": str(e)
            }
    
    async def get_currency_statistics(self) -> Dict[str, Any]:
        """Get currency localization statistics"""        return {
            "supported_currencies": len(self.currency_formats),
            "regional_configurations": len(self.regional_currencies),
            "exchange_rates_cached": len(self.exchange_rates),
            "format_cache_size": len(self.format_cache),
            "conversion_cache_size": len(self.conversion_cache),
            "currency_codes": list(self.currency_formats.keys()),
            "supported_regions": list(self.regional_currencies.keys()),
            "numbering_systems": len(set(fmt.numbering_system for fmt in self.currency_formats.values()))
        }
    
    async def clear_cache(self, cache_type: str = "all"):
        """Clear currency caches"""        if cache_type in ["all", "format"]:
            self.format_cache.clear()
            logger.info("Cleared currency format cache")
        
        if cache_type in ["all", "conversion"]:
            self.conversion_cache.clear()
            logger.info("Cleared currency conversion cache")
        
        if cache_type in ["all", "exchange_rates"]:
            # In production, this would clear only old rates
            old_count = len(self.exchange_rates)
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            # Remove old rates
            old_rates = [
                key for key, rate in self.exchange_rates.items()
                if rate.timestamp < cutoff_time and rate.source != "mock_provider"
            ]
            
            for key in old_rates:
                del self.exchange_rates[key]
            
            logger.info(f"Cleared {len(old_rates)} old exchange rates")
    
    async def health_check(self) -> bool:
        """Health check for currency localization service"""        try:
            # Check if currency formats are loaded
            if not self.currency_formats:
                return False
            
            # Test basic formatting
            test_amount = Decimal("1234.56")
            formatted = await self.format_currency(test_amount, "USD")
            
            if not formatted or "1234" not in formatted:
                return False
            
            # Test currency conversion
            conversion = await self.convert_currency(100, "USD", "EUR")
            
            return conversion.success if hasattr(conversion, 'success') else True
            
        except Exception as e:
            logger.error(f"Currency localization health check failed: {e}")
            return False