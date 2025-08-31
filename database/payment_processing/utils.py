"""Payment Processing Database Utilities - Enterprise Grade

Advanced utility functions for payment processing operations,
including validation, formatting, encryption, integrations, currency conversion,
financial calculations, and comprehensive reporting tools.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE UTILITY FEATURES:
- Advanced payment validation and verification
- Real-time currency conversion with multiple providers
- Comprehensive financial calculations and analytics
- Multi-format report generation (PDF, Excel, JSON)
- Advanced encryption and tokenization utilities
- AI-powered fraud detection helpers
- International payment format validation
- Performance optimization tools
"""
import re
import hashlib
import hmac
import secrets
import base64
import json
import asyncio
import aiohttp
import csv
from io import StringIO, BytesIO
from typing import Dict, Any, Optional, List, Union, Tuple, Callable
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, getcontext
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from functools import wraps, lru_cache
from enum import Enum
import logging
import uuid
import calendar
import math

# Optional imports for advanced features
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import qrcode
    QR_CODE_AVAILABLE = True
except ImportError:
    QR_CODE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Set decimal precision for financial calculations
getcontext().prec = 28


class PaymentValidationError(Exception):
    """Exception for payment validation errors"""    pass


class CurrencyConversionError(Exception):
    """Exception for currency conversion errors"""    pass


class ReportGenerationError(Exception):
    """Exception for report generation errors"""    pass


class CurrencyCode(Enum):
    """Extended ISO 4217 Currency Codes with crypto support"""    # Major Fiat Currencies
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound Sterling
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    SEK = "SEK"  # Swedish Krona
    NOK = "NOK"  # Norwegian Krone
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    CZK = "CZK"  # Czech Koruna
    HUF = "HUF"  # Hungarian Forint
    RUB = "RUB"  # Russian Ruble
    INR = "INR"  # Indian Rupee
    BRL = "BRL"  # Brazilian Real
    MXN = "MXN"  # Mexican Peso
    KRW = "KRW"  # South Korean Won
    SGD = "SGD"  # Singapore Dollar
    
    # Cryptocurrencies
    BTC = "BTC"   # Bitcoin
    ETH = "ETH"   # Ethereum
    USDC = "USDC" # USD Coin
    USDT = "USDT" # Tether
    BNB = "BNB"   # Binance Coin
    ADA = "ADA"   # Cardano
    DOT = "DOT"   # Polkadot
    MATIC = "MATIC" # Polygon
    LTC = "LTC"   # Litecoin
    XRP = "XRP"   # Ripple


class PaymentMethodType(Enum):
    """Extended payment method types"""    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    SEPA_TRANSFER = "sepa_transfer"
    WIRE_TRANSFER = "wire_transfer"
    ACH_TRANSFER = "ach_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SAMSUNG_PAY = "samsung_pay"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    PREPAID_CARD = "prepaid_card"
    GIFT_CARD = "gift_card"
    BUY_NOW_PAY_LATER = "buy_now_pay_later"


class ReportFormat(Enum):
    """Supported report formats"""    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "xlsx"
    XML = "xml"
    HTML = "html"


@dataclass
class ValidationResult:
    """Payment validation result container"""    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CurrencyRate:
    """Currency exchange rate container"""    from_currency: str
    to_currency: str
    rate: Decimal
    timestamp: datetime
    provider: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinancialSummary:
    """Financial summary container"""    total_amount: Decimal
    currency: str
    transaction_count: int
    average_amount: Decimal
    min_amount: Decimal
    max_amount: Decimal
    fees_total: Decimal
    net_amount: Decimal
    period_start: datetime
    period_end: datetime


def performance_monitor(func):
    """Decorator to monitor function performance"""    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        try:
            result = func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


class PaymentUtils:
    """Comprehensive payment utility functions"""    
    @staticmethod
    def generate_transaction_id(prefix: str = "TXN") -> str:
        """Generate unique transaction ID"""        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(4).upper()
        return f"{prefix}_{timestamp}_{random_part}"
    
    @staticmethod
    def generate_reference_number(length: int = 12) -> str:
        """Generate payment reference number"""        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """Mask credit card number for display"""        if not card_number:
            return ""
        
        # Remove non-digit characters
        digits_only = re.sub(r'\D', '', card_number)
        
        if len(digits_only) < 6:
            return "*" * len(digits_only)
        
        # Show first 4 and last 4 digits
        masked = digits_only[:4] + "*" * (len(digits_only) - 8) + digits_only[-4:]
        
        # Add spacing for readability
        return ' '.join(masked[i:i+4] for i in range(0, len(masked), 4))
    
    @staticmethod
    def format_amount(amount: Union[Decimal, float, str], currency: str = "EUR", decimal_places: int = 2) -> str:
        """Format amount with currency symbol and proper decimal places"""        try:
            if isinstance(amount, str):
                amount = Decimal(amount)
            elif isinstance(amount, float):
                amount = Decimal(str(amount))
            
            # Round to specified decimal places
            rounded_amount = amount.quantize(Decimal('0.01') if decimal_places == 2 else Decimal(f'0.{"0" * decimal_places}'))
            
            # Currency symbols
            symbols = {
                "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
                "CAD": "C$", "AUD": "A$", "CHF": "CHF", "CNY": "¥",
                "BTC": "₿", "ETH": "Ξ", "USDC": "USDC", "USDT": "₮"
            }
            
            symbol = symbols.get(currency, currency)
            
            # Format with thousands separator
            formatted = f"{rounded_amount:,.{decimal_places}f}"
            
            return f"{symbol}{formatted}"
            
        except Exception as e:
            logger.error(f"Amount formatting failed: {str(e)}")
            return f"{currency} {amount}"
    
    @staticmethod
    def parse_amount(amount_string: str) -> Tuple[Decimal, str]:
        """Parse amount string and extract amount and currency"""        try:
            # Remove currency symbols and spaces
            clean_amount = re.sub(r'[€$£¥₿Ξ₮,\s]', '', amount_string)
            
            # Extract currency code if present
            currency_match = re.search(r'[A-Z]{3}', amount_string)
            currency = currency_match.group() if currency_match else "EUR"
            
            # Extract numeric amount
            amount_match = re.search(r'[\d.,]+', clean_amount)
            if not amount_match:
                raise ValueError("No numeric amount found")
            
            amount_str = amount_match.group().replace(',', '')
            amount = Decimal(amount_str)
            
            return amount, currency
            
        except Exception as e:
            logger.error(f"Amount parsing failed: {str(e)}")
            raise PaymentValidationError(f"Invalid amount format: {amount_string}")
    
    @staticmethod
    def calculate_percentage_fee(amount: Decimal, percentage: Decimal) -> Decimal:
        """Calculate percentage-based fee"""        return (amount * percentage / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_tiered_fee(amount: Decimal, fee_tiers: List[Dict[str, Any]]) -> Decimal:
        """Calculate tiered fee based on amount"""        total_fee = Decimal('0')
        remaining_amount = amount
        
        for tier in fee_tiers:
            min_amount = Decimal(str(tier.get('min_amount', 0)))
            max_amount = Decimal(str(tier.get('max_amount', float('inf'))))
            rate = Decimal(str(tier.get('rate', 0)))
            
            if remaining_amount <= 0:
                break
            
            tier_amount = min(remaining_amount, max_amount - min_amount)
            tier_fee = tier_amount * rate / 100
            total_fee += tier_fee
            remaining_amount -= tier_amount
        
        return total_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def is_weekend(date: datetime) -> bool:
        """Check if date falls on weekend"""        return date.weekday() >= 5  # Saturday = 5, Sunday = 6
    
    @staticmethod
    def is_business_day(date: datetime, holidays: Optional[List[datetime]] = None) -> bool:
        """Check if date is a business day"""        if PaymentUtils.is_weekend(date):
            return False
        
        if holidays:
            date_only = date.date()
            holiday_dates = [h.date() if isinstance(h, datetime) else h for h in holidays]
            if date_only in holiday_dates:
                return False
        
        return True
    
    @staticmethod
    def next_business_day(date: datetime, holidays: Optional[List[datetime]] = None) -> datetime:
        """Get next business day"""        next_day = date + timedelta(days=1)
        
        while not PaymentUtils.is_business_day(next_day, holidays):
            next_day += timedelta(days=1)
        
        return next_day
    
    @staticmethod
    def generate_payment_qr_code(payment_data: Dict[str, Any]) -> Optional[bytes]:
        """Generate QR code for payment data"""        if not QR_CODE_AVAILABLE:
            logger.warning("QR code generation not available - qrcode library not installed")
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Create payment URL or data string
            payment_string = json.dumps(payment_data, sort_keys=True)
            qr.add_data(payment_string)
            qr.make(fit=True)
            
            # Generate image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"QR code generation failed: {str(e)}")
            return None


class PaymentValidator:
    """Advanced payment validation utilities"""    
    @staticmethod
    def validate_amount(amount: Union[Decimal, float, str], currency: str = "EUR") -> ValidationResult:
        """Comprehensive amount validation"""        try:
            if isinstance(amount, str):
                amount = Decimal(amount)
            elif isinstance(amount, float):
                amount = Decimal(str(amount))
            
            warnings = []
            
            # Basic validations
            if amount <= 0:
                return ValidationResult(False, "Amount must be positive")
            
            # Currency-specific validations
            if currency in ["BTC", "ETH"]:
                # Crypto currencies can have very small amounts
                min_amount = Decimal('0.00000001')
                max_amount = Decimal('1000000')
            else:
                # Fiat currencies
                min_amount = Decimal('0.01')
                max_amount = Decimal('999999999.99')
                
                # Check for unusual amounts
                if amount > Decimal('100000'):
                    warnings.append("Large transaction amount - may require additional verification")
            
            if amount < min_amount:
                return ValidationResult(False, f"Amount below minimum ({min_amount} {currency})")
            
            if amount > max_amount:
                return ValidationResult(False, f"Amount exceeds maximum ({max_amount} {currency})")
            
            # Check decimal places
            decimal_places = abs(amount.as_tuple().exponent)
            max_decimals = 8 if currency in ["BTC", "ETH"] else 2
            
            if decimal_places > max_decimals:
                return ValidationResult(False, f"Too many decimal places for {currency}")
            
            return ValidationResult(True, warnings=warnings)
            
        except Exception as e:
            return ValidationResult(False, f"Amount validation error: {str(e)}")
    
    @staticmethod
    def validate_card_number(card_number: str) -> ValidationResult:
        """Validate credit card number using Luhn algorithm"""        try:
            # Remove spaces and non-digit characters
            clean_number = re.sub(r'\D', '', card_number)
            
            if len(clean_number) < 13 or len(clean_number) > 19:
                return ValidationResult(False, "Invalid card number length")
            
            # Luhn algorithm
            checksum = 0
            reverse_digits = clean_number[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:  # Every second digit from right
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                checksum += n
            
            if checksum % 10 != 0:
                return ValidationResult(False, "Invalid card number (failed Luhn check)")
            
            # Identify card type
            card_type = PaymentValidator._identify_card_type(clean_number)
            metadata = {"card_type": card_type, "masked_number": PaymentUtils.mask_card_number(clean_number)}
            
            return ValidationResult(True, metadata=metadata)
            
        except Exception as e:
            return ValidationResult(False, f"Card validation error: {str(e)}")
    
    @staticmethod
    def _identify_card_type(card_number: str) -> str:
        """Identify card type from card number"""        if card_number.startswith('4'):
            return "Visa"
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            return "Mastercard"
        elif card_number.startswith(('34', '37')):
            return "American Express"
        elif card_number.startswith('6'):
            return "Discover"
        else:
            return "Unknown"
    
    @staticmethod
    def validate_expiry_date(month: int, year: int) -> ValidationResult:
        """Validate card expiry date"""        try:
            if not (1 <= month <= 12):
                return ValidationResult(False, "Invalid month")
            
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            # Handle 2-digit years
            if year < 100:
                year += 2000
            
            if year < current_year:
                return ValidationResult(False, "Card has expired")
            
            if year == current_year and month < current_month:
                return ValidationResult(False, "Card has expired")
            
            # Warn if card expires soon
            expiry_date = datetime(year, month, calendar.monthrange(year, month)[1])
            days_to_expiry = (expiry_date - current_date).days
            
            warnings = []
            if days_to_expiry <= 30:
                warnings.append("Card expires within 30 days")
            
            return ValidationResult(True, warnings=warnings)
            
        except Exception as e:
            return ValidationResult(False, f"Expiry date validation error: {str(e)}")
    
    @staticmethod
    def validate_cvv(cvv: str, card_type: str = "Unknown") -> ValidationResult:
        """Validate card CVV/CVC"""        try:
            if not cvv.isdigit():
                return ValidationResult(False, "CVV must contain only digits")
            
            # American Express uses 4-digit CVV, others use 3-digit
            expected_length = 4 if card_type == "American Express" else 3
            
            if len(cvv) != expected_length:
                return ValidationResult(False, f"CVV must be {expected_length} digits for {card_type}")
            
            return ValidationResult(True)
            
        except Exception as e:
            return ValidationResult(False, f"CVV validation error: {str(e)}")
    
    @staticmethod
    def validate_iban(iban: str) -> ValidationResult:
        """Validate International Bank Account Number"""        try:
            # Remove spaces and convert to uppercase
            clean_iban = re.sub(r'\s', '', iban).upper()
            
            if len(clean_iban) < 15 or len(clean_iban) > 34:
                return ValidationResult(False, "Invalid IBAN length")
            
            # Check country code
            country_code = clean_iban[:2]
            if not country_code.isalpha():
                return ValidationResult(False, "Invalid country code")
            
            # Move first 4 characters to end
            rearranged = clean_iban[4:] + clean_iban[:4]
            
            # Replace letters with numbers (A=10, B=11, ..., Z=35)
            numeric_string = ''
            for char in rearranged:
                if char.isalpha():
                    numeric_string += str(ord(char) - ord('A') + 10)
                else:
                    numeric_string += char
            
            # Check if mod 97 equals 1
            if int(numeric_string) % 97 != 1:
                return ValidationResult(False, "Invalid IBAN checksum")
            
            metadata = {"country_code": country_code, "formatted_iban": PaymentValidator._format_iban(clean_iban)}
            return ValidationResult(True, metadata=metadata)
            
        except Exception as e:
            return ValidationResult(False, f"IBAN validation error: {str(e)}")
    
    @staticmethod
    def _format_iban(iban: str) -> str:
        """Format IBAN with spaces for readability"""        return ' '.join(iban[i:i+4] for i in range(0, len(iban), 4))
    
    @staticmethod
    def validate_swift_code(swift_code: str) -> ValidationResult:
        """Validate SWIFT/BIC code"""        try:
            clean_swift = swift_code.upper().strip()
            
            if len(clean_swift) not in [8, 11]:
                return ValidationResult(False, "SWIFT code must be 8 or 11 characters")
            
            # Format: AAAA BB CC DDD
            # AAAA = Bank code (4 letters)
            # BB = Country code (2 letters)
            # CC = Location code (2 characters)
            # DDD = Branch code (3 characters, optional)
            
            if not clean_swift[:4].isalpha():
                return ValidationResult(False, "Invalid bank code (first 4 characters)")
            
            if not clean_swift[4:6].isalpha():
                return ValidationResult(False, "Invalid country code (characters 5-6)")
            
            if not clean_swift[6:8].isalnum():
                return ValidationResult(False, "Invalid location code (characters 7-8)")
            
            if len(clean_swift) == 11 and not clean_swift[8:11].isalnum():
                return ValidationResult(False, "Invalid branch code (characters 9-11)")
            
            metadata = {
                "bank_code": clean_swift[:4],
                "country_code": clean_swift[4:6],
                "location_code": clean_swift[6:8],
                "branch_code": clean_swift[8:11] if len(clean_swift) == 11 else None
            }
            
            return ValidationResult(True, metadata=metadata)
            
        except Exception as e:
            return ValidationResult(False, f"SWIFT code validation error: {str(e)}")


class CurrencyConverter:
    """Advanced currency conversion with multiple providers"""    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache rates for 5 minutes
        self.providers = [
            "exchangerate-api.com",
            "fixer.io",
            "currencylayer.com"
        ]
    
    @performance_monitor
    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        provider: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> Decimal:
        """Get exchange rate between currencies"""        try:
            if from_currency == to_currency:
                return Decimal('1.0')
            
            # Check cache first
            cache_key = f"{from_currency}_{to_currency}_{date or 'current'}"
            if cache_key in self.cache:
                cached_rate, cached_time = self.cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_duration:
                    return cached_rate
            
            # Get rate from provider
            rate = await self._fetch_rate_from_provider(from_currency, to_currency, provider, date)
            
            # Cache the result
            self.cache[cache_key] = (rate, datetime.utcnow())
            
            return rate
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {str(e)}")
            raise CurrencyConversionError(f"Failed to get exchange rate: {str(e)}")
    
    async def _fetch_rate_from_provider(
        self,
        from_currency: str,
        to_currency: str,
        provider: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> Decimal:
        """Fetch exchange rate from external provider"""        try:
            # For demo purposes, return mock rates
            # In production, this would call actual exchange rate APIs
            
            mock_rates = {
                ("USD", "EUR"): Decimal('0.85'),
                ("EUR", "USD"): Decimal('1.18'),
                ("GBP", "USD"): Decimal('1.25'),
                ("USD", "GBP"): Decimal('0.80'),
                ("BTC", "USD"): Decimal('45000.00'),
                ("USD", "BTC"): Decimal('0.000022'),
                ("ETH", "USD"): Decimal('3000.00'),
                ("USD", "ETH"): Decimal('0.000333'),
            }
            
            rate = mock_rates.get((from_currency, to_currency))
            if rate:
                return rate
            
            # Try reverse rate
            reverse_rate = mock_rates.get((to_currency, from_currency))
            if reverse_rate:
                return Decimal('1') / reverse_rate
            
            # Default fallback rate
            return Decimal('1.0')
            
        except Exception as e:
            logger.error(f"Provider rate fetch failed: {str(e)}")
            raise
    
    @performance_monitor
    async def convert_amount(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        provider: Optional[str] = None,
        include_fee: bool = False,
        fee_percentage: Decimal = Decimal('0.5')
    ) -> Dict[str, Any]:
        """Convert amount between currencies with optional fees"""        try:
            rate = await self.get_exchange_rate(from_currency, to_currency, provider)
            converted_amount = amount * rate
            
            fee = Decimal('0')
            if include_fee:
                fee = converted_amount * fee_percentage / 100
                converted_amount -= fee
            
            return {
                "original_amount": amount,
                "converted_amount": converted_amount.quantize(Decimal('0.01')),
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": rate,
                "fee": fee.quantize(Decimal('0.01')),
                "fee_percentage": fee_percentage,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Amount conversion failed: {str(e)}")
            raise CurrencyConversionError(f"Failed to convert amount: {str(e)}")
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""        return [currency.value for currency in CurrencyCode]
    
    def clear_cache(self):
        """Clear exchange rate cache"""        self.cache.clear()
        logger.info("Currency conversion cache cleared")


class FinancialCalculator:
    """Advanced financial calculations for payment processing"""    
    @staticmethod
    def calculate_compound_interest(
        principal: Decimal,
        annual_rate: Decimal,
        compounding_frequency: int,
        years: Decimal
    ) -> Decimal:
        """Calculate compound interest"""        try:
            # A = P(1 + r/n)^(nt)
            rate_per_period = annual_rate / (100 * compounding_frequency)
            num_periods = compounding_frequency * years
            
            amount = principal * (1 + rate_per_period) ** num_periods
            return amount.quantize(Decimal('0.01'))
            
        except Exception as e:
            logger.error(f"Compound interest calculation failed: {str(e)}")
            return principal
    
    @staticmethod
    def calculate_payment_schedule(
        loan_amount: Decimal,
        annual_rate: Decimal,
        num_payments: int,
        payment_frequency: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Calculate loan payment schedule"""        try:
            frequency_map = {
                "monthly": 12,
                "quarterly": 4,
                "annually": 1,
                "weekly": 52
            }
            
            periods_per_year = frequency_map.get(payment_frequency, 12)
            period_rate = annual_rate / (100 * periods_per_year)
            
            # Calculate payment amount using PMT formula
            if period_rate == 0:
                payment_amount = loan_amount / num_payments
            else:
                payment_amount = loan_amount * (
                    period_rate * (1 + period_rate) ** num_payments
                ) / ((1 + period_rate) ** num_payments - 1)
            
            schedule = []
            remaining_balance = loan_amount
            
            for payment_num in range(1, num_payments + 1):
                interest_payment = remaining_balance * period_rate
                principal_payment = payment_amount - interest_payment
                remaining_balance -= principal_payment
                
                schedule.append({
                    "payment_number": payment_num,
                    "payment_amount": payment_amount.quantize(Decimal('0.01')),
                    "principal_payment": principal_payment.quantize(Decimal('0.01')),
                    "interest_payment": interest_payment.quantize(Decimal('0.01')),
                    "remaining_balance": max(Decimal('0'), remaining_balance.quantize(Decimal('0.01')))
                })
            
            return schedule
            
        except Exception as e:
            logger.error(f"Payment schedule calculation failed: {str(e)}")
            return []
    
    @staticmethod
    def calculate_roi(initial_investment: Decimal, final_value: Decimal) -> Decimal:
        """Calculate Return on Investment"""        try:
            if initial_investment == 0:
                return Decimal('0')
            
            roi = ((final_value - initial_investment) / initial_investment) * 100
            return roi.quantize(Decimal('0.01'))
            
        except Exception as e:
            logger.error(f"ROI calculation failed: {str(e)}")
            return Decimal('0')
    
    @staticmethod
    def calculate_net_present_value(
        cash_flows: List[Decimal],
        discount_rate: Decimal
    ) -> Decimal:
        """Calculate Net Present Value"""        try:
            npv = Decimal('0')
            
            for i, cash_flow in enumerate(cash_flows):
                present_value = cash_flow / ((1 + discount_rate / 100) ** i)
                npv += present_value
            
            return npv.quantize(Decimal('0.01'))
            
        except Exception as e:
            logger.error(f"NPV calculation failed: {str(e)}")
            return Decimal('0')
    
    @staticmethod
    def calculate_platform_fee(amount: Decimal, platform: str) -> Decimal:
        """Calculate platform-specific fees"""        fee_structures = {
            "youtube": {"percentage": Decimal('30'), "min_fee": Decimal('0.30')},
            "instagram": {"percentage": Decimal('5'), "min_fee": Decimal('0.05')},
            "spotify": {"percentage": Decimal('70'), "min_fee": Decimal('0.01')},
            "tiktok": {"percentage": Decimal('50'), "min_fee": Decimal('0.02')},
            "default": {"percentage": Decimal('10'), "min_fee": Decimal('0.10')}
        }
        
        fee_config = fee_structures.get(platform.lower(), fee_structures["default"])
        calculated_fee = amount * fee_config["percentage"] / 100
        
        return max(calculated_fee, fee_config["min_fee"]).quantize(Decimal('0.01'))
    
    @staticmethod
    def calculate_our_commission(amount: Decimal, platform: str) -> Decimal:
        """Calculate our commission from platform revenue"""        commission_rates = {
            "youtube": Decimal('15'),
            "instagram": Decimal('10'),
            "spotify": Decimal('20'),
            "tiktok": Decimal('12'),
            "default": Decimal('15')
        }
        
        rate = commission_rates.get(platform.lower(), commission_rates["default"])
        return (amount * rate / 100).quantize(Decimal('0.01'))


class ReportGenerator:
    """Advanced report generation utilities"""    
    @staticmethod
    @performance_monitor
    async def generate_financial_report(
        data: List[Dict[str, Any]],
        report_format: ReportFormat,
        title: str = "Financial Report",
        include_charts: bool = False
    ) -> bytes:
        """Generate financial report in various formats"""        try:
            if report_format == ReportFormat.JSON:
                return ReportGenerator._generate_json_report(data, title)
            elif report_format == ReportFormat.CSV:
                return ReportGenerator._generate_csv_report(data)
            elif report_format == ReportFormat.PDF:
                return ReportGenerator._generate_pdf_report(data, title, include_charts)
            elif report_format == ReportFormat.EXCEL:
                return ReportGenerator._generate_excel_report(data, title)
            else:
                raise ReportGenerationError(f"Unsupported report format: {report_format}")
                
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ReportGenerationError(f"Failed to generate report: {str(e)}")
    
    @staticmethod
    def _generate_json_report(data: List[Dict[str, Any]], title: str) -> bytes:
        """Generate JSON report"""        report = {
            "title": title,
            "generated_at": datetime.utcnow().isoformat(),
            "data_count": len(data),
            "data": data
        }
        return json.dumps(report, indent=2, default=str).encode('utf-8')
    
    @staticmethod
    def _generate_csv_report(data: List[Dict[str, Any]]) -> bytes:
        """Generate CSV report"""        if not data:
            return b"No data available"
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue().encode('utf-8')
    
    @staticmethod
    def _generate_pdf_report(data: List[Dict[str, Any]], title: str, include_charts: bool) -> bytes:
        """Generate PDF report"""        if not PDF_AVAILABLE:
            raise ReportGenerationError("PDF generation not available - reportlab not installed")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        story.append(Paragraph(title, title_style))
        
        # Add generation timestamp
        timestamp = f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        story.append(Paragraph(timestamp, styles['Normal']))
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Add data table
        if data:
            headers = list(data[0].keys())
            table_data = [headers] + [[str(row.get(key, '')) for key in headers] for row in data]
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        doc.build(story)
        return buffer.getvalue()
    
    @staticmethod
    def _generate_excel_report(data: List[Dict[str, Any]], title: str) -> bytes:
        """Generate Excel report"""        if not PANDAS_AVAILABLE:
            raise ReportGenerationError("Excel generation not available - pandas not installed")
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            if data:
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name='Report', index=False)
                
                # Add metadata sheet
                metadata = pd.DataFrame([
                    {"Property": "Title", "Value": title},
                    {"Property": "Generated At", "Value": datetime.utcnow().isoformat()},
                    {"Property": "Record Count", "Value": len(data)}
                ])
                metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        return buffer.getvalue()
    
    @staticmethod
    def calculate_financial_summary(transactions: List[Dict[str, Any]]) -> FinancialSummary:
        """Calculate financial summary from transaction data"""        if not transactions:
            return FinancialSummary(
                total_amount=Decimal('0'),
                currency="EUR",
                transaction_count=0,
                average_amount=Decimal('0'),
                min_amount=Decimal('0'),
                max_amount=Decimal('0'),
                fees_total=Decimal('0'),
                net_amount=Decimal('0'),
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow()
            )
        
        amounts = [Decimal(str(t.get('amount', 0))) for t in transactions]
        fees = [Decimal(str(t.get('fee', 0))) for t in transactions]
        
        return FinancialSummary(
            total_amount=sum(amounts),
            currency=transactions[0].get('currency', 'EUR'),
            transaction_count=len(transactions),
            average_amount=sum(amounts) / len(amounts),
            min_amount=min(amounts),
            max_amount=max(amounts),
            fees_total=sum(fees),
            net_amount=sum(amounts) - sum(fees),
            period_start=min(datetime.fromisoformat(t.get('created_at', datetime.utcnow().isoformat())) for t in transactions),
            period_end=max(datetime.fromisoformat(t.get('created_at', datetime.utcnow().isoformat())) for t in transactions)
        )


class PaymentFormatter:
    """Payment data formatting utilities"""    
    @staticmethod
    def format_transaction_for_display(transaction: Dict[str, Any]) -> Dict[str, str]:
        """Format transaction data for display purposes"""        formatted = {}
        
        # Format amount
        amount = transaction.get('amount', 0)
        currency = transaction.get('currency', 'EUR')
        formatted['amount'] = PaymentUtils.format_amount(amount, currency)
        
        # Format dates
        created_at = transaction.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted['date'] = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format status
        status = transaction.get('status', '').replace('_', ' ').title()
        formatted['status'] = status
        
        # Format transaction ID
        txn_id = transaction.get('transaction_id', '')
        formatted['transaction_id'] = txn_id[:8] + '...' if len(txn_id) > 8 else txn_id
        
        # Format payment method
        payment_method = transaction.get('payment_method', {})
        if isinstance(payment_method, dict):
            method_type = payment_method.get('type', 'Unknown')
            last_four = payment_method.get('last_four', '')
            formatted['payment_method'] = f"{method_type.title()} ****{last_four}" if last_four else method_type.title()
        
        return formatted
    
    @staticmethod
    def format_currency_list() -> List[Dict[str, str]]:
        """Get formatted list of supported currencies"""        currencies = []
        
        for currency in CurrencyCode:
            currency_info = {
                "code": currency.value,
                "name": PaymentFormatter._get_currency_name(currency.value),
                "symbol": PaymentFormatter._get_currency_symbol(currency.value),
                "is_crypto": currency.value in ["BTC", "ETH", "USDC", "USDT", "BNB", "ADA", "DOT", "MATIC", "LTC", "XRP"]
            }
            currencies.append(currency_info)
        
        return currencies
    
    @staticmethod
    def _get_currency_name(code: str) -> str:
        """Get currency name from code"""        names = {
            "USD": "US Dollar", "EUR": "Euro", "GBP": "British Pound Sterling",
            "JPY": "Japanese Yen", "CAD": "Canadian Dollar", "AUD": "Australian Dollar",
            "CHF": "Swiss Franc", "CNY": "Chinese Yuan", "SEK": "Swedish Krona",
            "NOK": "Norwegian Krone", "DKK": "Danish Krone", "PLN": "Polish Zloty",
            "CZK": "Czech Koruna", "HUF": "Hungarian Forint", "RUB": "Russian Ruble",
            "INR": "Indian Rupee", "BRL": "Brazilian Real", "MXN": "Mexican Peso",
            "KRW": "South Korean Won", "SGD": "Singapore Dollar",
            "BTC": "Bitcoin", "ETH": "Ethereum", "USDC": "USD Coin", "USDT": "Tether",
            "BNB": "Binance Coin", "ADA": "Cardano", "DOT": "Polkadot", "MATIC": "Polygon",
            "LTC": "Litecoin", "XRP": "Ripple"
        }
        return names.get(code, code)
    
    @staticmethod
    def _get_currency_symbol(code: str) -> str:
        """Get currency symbol from code"""        symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$",
            "AUD": "A$", "CHF": "CHF", "CNY": "¥", "SEK": "kr", "NOK": "kr",
            "DKK": "kr", "PLN": "zł", "CZK": "Kč", "HUF": "Ft", "RUB": "₽",
            "INR": "₹", "BRL": "R$", "MXN": "$", "KRW": "₩", "SGD": "S$",
            "BTC": "₿", "ETH": "Ξ", "USDC": "USDC", "USDT": "₮", "BNB": "BNB",
            "ADA": "ADA", "DOT": "DOT", "MATIC": "MATIC", "LTC": "Ł", "XRP": "XRP"
        }
        return symbols.get(code, code)
    USDC = "USDC"
    USDT = "USDT"


class CardType(Enum):
    """Credit card types"""    VISA = "visa"
    MASTERCARD = "mastercard"
    AMERICAN_EXPRESS = "amex"
    DISCOVER = "discover"
    JCB = "jcb"
    DINERS_CLUB = "diners"
    UNKNOWN = "unknown"


class PaymentValidator:
    """Payment data validation utilities"""    
    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm"""        if not card_number:
            return False
        
        # Remove all non-digits
        clean_number = re.sub(r'\D', '', card_number)
        
        # Check length
        if len(clean_number) < 13 or len(clean_number) > 19:
            return False
        
        # Luhn algorithm
        def luhn_checksum(num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10
        
        return luhn_checksum(clean_number) == 0
    
    @staticmethod
    def get_card_type(card_number: str) -> CardType:
        """Identify credit card type from card number"""        if not card_number:
            return CardType.UNKNOWN
        
        # Remove all non-digits
        clean_number = re.sub(r'\D', '', card_number)
        
        # Card type patterns
        patterns = {
            CardType.VISA: [r'^4[0-9]{12}(?:[0-9]{3})?$'],
            CardType.MASTERCARD: [
                r'^5[1-5][0-9]{14}$',
                r'^2(?:2(?:2[1-9]|[3-9][0-9])|[3-6][0-9][0-9]|7(?:[01][0-9]|20))[0-9]{12}$'
            ],
            CardType.AMERICAN_EXPRESS: [r'^3[47][0-9]{13}$'],
            CardType.DISCOVER: [r'^6(?:011|5[0-9]{2})[0-9]{12}$'],
            CardType.JCB: [r'^(?:2131|1800|35\d{3})\d{11}$'],
            CardType.DINERS_CLUB: [r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$']
        }
        
        for card_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                if re.match(pattern, clean_number):
                    return card_type
        
        return CardType.UNKNOWN
    
    @staticmethod
    def validate_expiry_date(month: int, year: int) -> bool:
        """Validate credit card expiry date"""        try:
            if not (1 <= month <= 12):
                return False
            
            # Handle 2-digit years
            if year < 100:
                year += 2000
            
            current_date = datetime.now()
            expiry_date = datetime(year, month, 1)
            
            # Card expires at end of month
            if expiry_date.year == current_date.year and expiry_date.month == current_date.month:
                return True
            
            return expiry_date > current_date
            
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_cvv(cvv: str, card_type: CardType) -> bool:
        """Validate CVV code"""        if not cvv or not cvv.isdigit():
            return False
        
        # American Express uses 4-digit CVV, others use 3
        if card_type == CardType.AMERICAN_EXPRESS:
            return len(cvv) == 4
        else:
            return len(cvv) == 3
    
    @staticmethod
    def validate_amount(amount: Union[str, int, float, Decimal]) -> bool:
        """Validate payment amount"""        try:
            decimal_amount = Decimal(str(amount))
            return decimal_amount > 0 and decimal_amount <= Decimal('999999.99')
        except (ValueError, TypeError, OverflowError):
            return False
    
    @staticmethod
    def validate_currency(currency: str) -> bool:
        """Validate currency code"""        try:
            CurrencyCode(currency.upper())
            return True
        except ValueError:
            return False


class PaymentIDGenerator:
    """Generate unique payment-related IDs"""    
    @staticmethod
    def generate_transaction_id(prefix: str = "txn") -> str:
        """Generate unique transaction ID"""        timestamp = int(datetime.now().timestamp() * 1000)
        random_part = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{random_part}"
    
    @staticmethod
    def generate_payment_token(length: int = 32) -> str:
        """Generate secure payment token"""        return uuid.uuid4().hex + uuid.uuid4().hex[:length-32] if length > 32 else uuid.uuid4().hex[:length]
    
    @staticmethod
    def generate_reference_number(prefix: str = "REF") -> str:
        """Generate human-readable reference number"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = str(uuid.uuid4().int)[:6]
        return f"{prefix}{timestamp}{random_part}"
    
    @staticmethod
    def generate_invoice_number(prefix: str = "INV") -> str:
        """Generate invoice number"""        date_part = datetime.now().strftime("%Y%m%d")
        sequence = str(uuid.uuid4().int)[:8]
        return f"{prefix}-{date_part}-{sequence}"


class PaymentDataMasker:
    """Utilities for masking sensitive payment data"""    
    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """Mask credit card number showing only last 4 digits"""        if not card_number:
            return ""
        
        clean_number = re.sub(r'\D', '', card_number)
        
        if len(clean_number) < 4:
            return "*" * len(clean_number)
        
        return "*" * (len(clean_number) - 4) + clean_number[-4:]
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""        if not email or '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""        if not phone:
            return ""
        
        clean_phone = re.sub(r'\D', '', phone)
        
        if len(clean_phone) < 4:
            return "*" * len(clean_phone)
        
        return "*" * (len(clean_phone) - 4) + clean_phone[-4:]


class CurrencyConverter:
    """Currency conversion utilities"""    
    # Mock exchange rates - in production, would fetch from external API
    EXCHANGE_RATES = {
        'USD': {
            'EUR': Decimal('0.85'),
            'GBP': Decimal('0.73'),
            'CAD': Decimal('1.25'),
            'AUD': Decimal('1.35'),
            'JPY': Decimal('110.0'),
            'CHF': Decimal('0.92')
        },
        'EUR': {
            'USD': Decimal('1.18'),
            'GBP': Decimal('0.86'),
            'CAD': Decimal('1.47'),
            'AUD': Decimal('1.59'),
            'JPY': Decimal('129.5'),
            'CHF': Decimal('1.08')
        },
        'GBP': {
            'USD': Decimal('1.37'),
            'EUR': Decimal('1.16'),
            'CAD': Decimal('1.71'),
            'AUD': Decimal('1.85'),
            'JPY': Decimal('150.6'),
            'CHF': Decimal('1.26')
        }
    }
    
    @classmethod
    def convert_currency(
        cls,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> Tuple[Decimal, Decimal]:
        """        Convert amount from one currency to another
        
        Returns:
            Tuple[converted_amount, exchange_rate]
        """        if from_currency == to_currency:
            return amount, Decimal('1.0')
        
        try:
            rate = cls.EXCHANGE_RATES.get(from_currency, {}).get(to_currency)
            if not rate:
                # Try reverse conversion
                reverse_rate = cls.EXCHANGE_RATES.get(to_currency, {}).get(from_currency)
                if reverse_rate:
                    rate = Decimal('1.0') / reverse_rate
                else:
                    raise PaymentValidationError(f"Exchange rate not found: {from_currency} to {to_currency}")
            
            converted_amount = (amount * rate).quantize(
                Decimal('0.01'), 
                rounding=ROUND_HALF_UP
            )
            
            return converted_amount, rate
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {str(e)}")
            raise PaymentValidationError(f"Currency conversion error: {str(e)}")
    
    @classmethod
    def get_currency_symbol(cls, currency_code: str) -> str:
        """Get currency symbol for display"""        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'CAD': 'C$',
            'AUD': 'A$',
            'JPY': '¥',
            'CHF': 'CHF',
            'BTC': '₿',
            'ETH': 'Ξ'
        }
        return symbols.get(currency_code.upper(), currency_code)


class PaymentValidator:
    """Validation utilities for payment data"""    
    @staticmethod
    def validate_credit_card_number(card_number: str) -> Dict[str, Any]:
        """        Validate credit card number using Luhn algorithm
        
        Returns:
            Dict with validation result and card type
        """        # Remove spaces and non-digits
        card_number = re.sub(r'[^\d]', '', card_number)
        
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return {'valid': False, 'error': 'Invalid card number length'}
        
        # Luhn algorithm
        def luhn_check(number):
            digits = [int(d) for d in number]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0
        
        if not luhn_check(card_number):
            return {'valid': False, 'error': 'Invalid card number (Luhn check failed)'}
        
        # Detect card type
        card_type = PaymentValidator._detect_card_type(card_number)
        
        return {
            'valid': True,
            'card_type': card_type,
            'last_four': card_number[-4:],
            'masked_number': f"****-****-****-{card_number[-4:]}"
        }
    
    @staticmethod
    def _detect_card_type(card_number: str) -> str:
        """Detect credit card type from number"""        patterns = {
            'visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'mastercard': r'^5[1-5][0-9]{14}$|^2(?:2(?:2[1-9]|[3-9][0-9])|[3-6][0-9][0-9]|7(?:[01][0-9]|20))[0-9]{12}$',
            'amex': r'^3[47][0-9]{13}$',
            'discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
            'diners': r'^3[0689][0-9]{11}$',
            'jcb': r'^(?:2131|1800|35[0-9]{3})[0-9]{11}$'
        }
        
        for card_type, pattern in patterns.items():
            if re.match(pattern, card_number):
                return card_type
        
        return 'unknown'
    
    @staticmethod
    def validate_expiry_date(exp_month: int, exp_year: int) -> Dict[str, Any]:
        """Validate credit card expiry date"""        if not (1 <= exp_month <= 12):
            return {'valid': False, 'error': 'Invalid expiry month'}
        
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Convert 2-digit year to 4-digit
        if exp_year < 100:
            exp_year += 2000
        
        if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
            return {'valid': False, 'error': 'Card has expired'}
        
        if exp_year > current_year + 20:
            return {'valid': False, 'error': 'Invalid expiry year'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_cvv(cvv: str, card_type: str) -> Dict[str, Any]:
        """Validate CVV/CVC code"""        if not cvv.isdigit():
            return {'valid': False, 'error': 'CVV must contain only digits'}
        
        expected_length = 4 if card_type == 'amex' else 3
        
        if len(cvv) != expected_length:
            return {'valid': False, 'error': f'CVV must be {expected_length} digits for {card_type}'}
        
        return {'valid': True}
    
    @staticmethod
    def validate_iban(iban: str) -> Dict[str, Any]:
        """Validate International Bank Account Number (IBAN)"""        # Remove spaces and convert to uppercase
        iban = re.sub(r'[^A-Z0-9]', '', iban.upper())
        
        if len(iban) < 15 or len(iban) > 34:
            return {'valid': False, 'error': 'Invalid IBAN length'}
        
        # Move first 4 characters to the end
        rearranged = iban[4:] + iban[:4]
        
        # Convert letters to numbers (A=10, B=11, ..., Z=35)
        numeric_string = ''
        for char in rearranged:
            if char.isalpha():
                numeric_string += str(ord(char) - ord('A') + 10)
            else:
                numeric_string += char
        
        # Check mod 97
        if int(numeric_string) % 97 != 1:
            return {'valid': False, 'error': 'Invalid IBAN checksum'}
        
        return {
            'valid': True,
            'country_code': iban[:2],
            'check_digits': iban[2:4],
            'bank_code': iban[4:8] if len(iban) > 8 else '',
            'masked_iban': f"{iban[:4]}****{iban[-4:]}"
        }
    
    @staticmethod
    def validate_routing_number(routing_number: str) -> Dict[str, Any]:
        """Validate US bank routing number"""        # Remove non-digits
        routing_number = re.sub(r'[^\d]', '', routing_number)
        
        if len(routing_number) != 9:
            return {'valid': False, 'error': 'Routing number must be 9 digits'}
        
        # ABA routing number check digit algorithm
        weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
        total = sum(int(digit) * weight for digit, weight in zip(routing_number, weights))
        
        if total % 10 != 0:
            return {'valid': False, 'error': 'Invalid routing number checksum'}
        
        return {
            'valid': True,
            'bank_code': routing_number[:4],
            'masked_routing': f"****{routing_number[-4:]}"
        }


class PaymentSecurityUtils:
    """Security utilities for payment processing"""    
    @staticmethod
    def generate_payment_token(length: int = 32) -> str:
        """Generate secure payment token"""        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_payment_data(data: str, salt: Optional[str] = None) -> str:
        """Hash sensitive payment data"""        if salt is None:
            salt = secrets.token_hex(16)
        
        return hashlib.pbkdf2_hmac(
            'sha256',
            data.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
    
    @staticmethod
    def verify_webhook_signature(
        payload: str,
        signature: str,
        secret: str,
        algorithm: str = 'sha256'
    ) -> bool:
        """Verify webhook signature from payment processor"""        try:
            expected_signature = hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                getattr(hashlib, algorithm)
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data for logging/display"""        if len(data) <= visible_chars:
            return '*' * len(data)
        
        return '*' * (len(data) - visible_chars) + data[-visible_chars:]
    
    @staticmethod
    def generate_fingerprint(data: Dict[str, Any]) -> str:
        """Generate fingerprint for payment method"""        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()


class PaymentFormatter:
    """Formatting utilities for payment display"""    
    @staticmethod
    def format_amount(
        amount: Union[Decimal, float],
        currency: str,
        locale: str = 'en_US'
    ) -> str:
        """Format amount for display with currency symbol"""        try:
            symbol = CurrencyConverter.get_currency_symbol(currency)
            
            if currency in ['JPY', 'KRW']:  # No decimal places for these currencies
                formatted_amount = f"{symbol}{int(amount):,}"
            else:
                formatted_amount = f"{symbol}{float(amount):,.2f}"
            
            return formatted_amount
            
        except Exception as e:
            logger.error(f"Amount formatting failed: {str(e)}")
            return f"{currency} {amount}"
    
    @staticmethod
    def format_payment_method(payment_method: Dict[str, Any]) -> str:
        """Format payment method for display"""        method_type = payment_method.get('method_type', '')
        
        if method_type in ['credit_card', 'debit_card']:
            brand = payment_method.get('brand', '').title()
            last_four = payment_method.get('last_four_digits', '')
            return f"{brand} ending in {last_four}"
        
        elif method_type == 'bank_transfer':
            bank_name = payment_method.get('bank_name', '')
            last_four = payment_method.get('routing_number_last_four', '')
            return f"{bank_name} account ending in {last_four}"
        
        elif method_type in ['paypal', 'stripe', 'wise']:
            return method_type.title()
        
        else:
            return method_type.replace('_', ' ').title()
    
    @staticmethod
    def format_transaction_reference(
        transaction_id: uuid.UUID,
        prefix: str = 'TXN'
    ) -> str:
        """Format transaction reference for display"""        return f"{prefix}-{str(transaction_id)[:8].upper()}"


class PaymentAnalytics:
    """Analytics utilities for payment processing"""    
    @staticmethod
    def calculate_conversion_rate(
        successful_transactions: int,
        total_attempts: int
    ) -> Decimal:
        """Calculate payment conversion rate"""        if total_attempts == 0:
            return Decimal('0')
        
        return (Decimal(successful_transactions) / Decimal(total_attempts) * 100).quantize(
            Decimal('0.01')
        )
    
    @staticmethod
    def calculate_average_transaction_value(
        transactions: List[Dict[str, Any]]
    ) -> Decimal:
        """Calculate average transaction value"""        if not transactions:
            return Decimal('0')
        
        total_amount = sum(
            Decimal(str(txn.get('amount', 0))) 
            for txn in transactions
        )
        
        return (total_amount / len(transactions)).quantize(Decimal('0.01'))
    
    @staticmethod
    def calculate_revenue_growth(
        current_period_revenue: Decimal,
        previous_period_revenue: Decimal
    ) -> Decimal:
        """Calculate revenue growth percentage"""        if previous_period_revenue == 0:
            return Decimal('0') if current_period_revenue == 0 else Decimal('100')
        
        growth = ((current_period_revenue - previous_period_revenue) / previous_period_revenue * 100)
        return growth.quantize(Decimal('0.01'))


class PaymentIntegrationHelpers:
    """Helper functions for payment processor integrations"""    
    @staticmethod
    def normalize_processor_response(
        response: Dict[str, Any],
        processor: str
    ) -> Dict[str, Any]:
        """Normalize response from different payment processors"""        normalized = {
            'transaction_id': '',
            'status': 'unknown',
            'amount': Decimal('0'),
            'currency': 'USD',
            'fees': Decimal('0'),
            'created_at': datetime.utcnow(),
            'metadata': {}
        }
        
        if processor == 'stripe':
            normalized.update({
                'transaction_id': response.get('id', ''),
                'status': PaymentIntegrationHelpers._map_stripe_status(response.get('status', '')),
                'amount': Decimal(str(response.get('amount', 0))) / 100,  # Stripe uses cents
                'currency': response.get('currency', 'usd').upper(),
                'fees': Decimal(str(response.get('application_fee_amount', 0))) / 100,
                'created_at': datetime.fromtimestamp(response.get('created', 0)),
                'metadata': response.get('metadata', {})
            })
        
        elif processor == 'paypal':
            normalized.update({
                'transaction_id': response.get('id', ''),
                'status': PaymentIntegrationHelpers._map_paypal_status(response.get('state', '')),
                'amount': Decimal(str(response.get('transactions', [{}])[0].get('amount', {}).get('total', 0))),
                'currency': response.get('transactions', [{}])[0].get('amount', {}).get('currency', 'USD'),
                'metadata': response.get('custom', {})
            })
        
        return normalized
    
    @staticmethod
    def _map_stripe_status(stripe_status: str) -> str:
        """Map Stripe status to internal status"""        mapping = {
            'succeeded': 'completed',
            'pending': 'processing',
            'failed': 'failed',
            'canceled': 'cancelled',
            'requires_payment_method': 'failed',
            'requires_confirmation': 'pending',
            'requires_action': 'pending'
        }
        return mapping.get(stripe_status, 'unknown')
    
    @staticmethod
    def _map_paypal_status(paypal_status: str) -> str:
        """Map PayPal status to internal status"""        mapping = {
            'approved': 'completed',
            'created': 'pending',
            'cancelled': 'cancelled',
            'failed': 'failed',
            'expired': 'failed'
        }
        return mapping.get(paypal_status, 'unknown')


# Decorator for payment operation logging
def log_payment_operation(operation_name: str):
    """Decorator to log payment operations"""    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Payment operation '{operation_name}' completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"Payment operation '{operation_name}' failed after {duration:.2f}s: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Payment operation '{operation_name}' completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"Payment operation '{operation_name}' failed after {duration:.2f}s: {str(e)}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Utility functions for common operations
def generate_invoice_number(user_id: int, billing_record_id: uuid.UUID) -> str:
    """Generate unique invoice number"""    timestamp = datetime.utcnow().strftime('%Y%m%d')
    user_code = f"{user_id:06d}"
    record_code = str(billing_record_id)[:8].upper()
    return f"INV-{timestamp}-{user_code}-{record_code}"


def validate_payment_amount(amount: Decimal, currency: str) -> bool:
    """Validate payment amount based on currency constraints"""    min_amounts = {
        'USD': Decimal('0.50'),
        'EUR': Decimal('0.50'),
        'GBP': Decimal('0.30'),
        'JPY': Decimal('50.00'),
        'CAD': Decimal('0.50'),
        'AUD': Decimal('0.50')
    }
    
    max_amounts = {
        'USD': Decimal('999999.99'),
        'EUR': Decimal('999999.99'),
        'GBP': Decimal('999999.99'),
        'JPY': Decimal('99999999.00'),
        'CAD': Decimal('999999.99'),
        'AUD': Decimal('999999.99')
    }
    
    min_amount = min_amounts.get(currency, Decimal('0.50'))
    max_amount = max_amounts.get(currency, Decimal('999999.99'))
    
    return min_amount <= amount <= max_amount


def calculate_processing_time_estimate(
    processor: str,
    payment_method_type: str
) -> timedelta:
    """Estimate processing time for different payment methods"""    estimates = {
        'stripe': {
            'credit_card': timedelta(seconds=30),
            'bank_transfer': timedelta(days=3),
            'cryptocurrency': timedelta(hours=1)
        },
        'paypal': {
            'credit_card': timedelta(minutes=1),
            'bank_transfer': timedelta(days=5),
            'paypal': timedelta(seconds=10)
        },
        'wise': {
            'bank_transfer': timedelta(hours=24),
            'credit_card': timedelta(minutes=5)
        }
    }
    
    return estimates.get(processor, {}).get(
        payment_method_type, 
        timedelta(hours=24)  # Default estimate
    )
