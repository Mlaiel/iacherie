"""
Currency Exchange & Conversion Utilities - Industrial Financial Engine

Advanced currency conversion system with real-time exchange rates, 
historical data, multi-provider support, and caching for performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json

from .cache import PerformanceCache, generate_cache_key
from .exceptions import PaymentProcessingError, CurrencyNotSupportedError
from .config import PaymentConfig

logger = logging.getLogger(__name__)


class CurrencyProvider(str, Enum):
    """Currency exchange rate providers"""
    FIXER_IO = "fixer_io"
    EXCHANGE_RATES_API = "exchange_rates_api"
    OPENEXCHANGERATES = "openexchangerates"
    CURRENCYLAYER = "currencylayer"
    MOCK = "mock"  # For testing


class CurrencyCode(str, Enum):
    """Supported currency codes (ISO 4217)"""
    # Major currencies
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    
    # Regional currencies
    CNY = "CNY"  # Chinese Yuan
    INR = "INR"  # Indian Rupee
    KRW = "KRW"  # South Korean Won
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    NOK = "NOK"  # Norwegian Krone
    SEK = "SEK"  # Swedish Krona
    DKK = "DKK"  # Danish Krone
    
    # Emerging markets
    BRL = "BRL"  # Brazilian Real
    MXN = "MXN"  # Mexican Peso
    RUB = "RUB"  # Russian Ruble
    ZAR = "ZAR"  # South African Rand
    TRY = "TRY"  # Turkish Lira
    PLN = "PLN"  # Polish Zloty
    
    # Cryptocurrencies
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum
    USDT = "USDT"  # Tether


class ExchangeRate:
    """Exchange rate data model"""
    
    def __init__(
        self,
        from_currency: str,
        to_currency: str,
        rate: Decimal,
        timestamp: datetime,
        provider: str,
        bid: Optional[Decimal] = None,
        ask: Optional[Decimal] = None
    ):
        self.from_currency = from_currency.upper()
        self.to_currency = to_currency.upper()
        self.rate = Decimal(str(rate))
        self.timestamp = timestamp
        self.provider = provider
        self.bid = Decimal(str(bid)) if bid else None
        self.ask = Decimal(str(ask)) if ask else None
    
    def is_expired(self, max_age_minutes: int = 15) -> bool:
        """Check if exchange rate is expired"""
        age = datetime.utcnow() - self.timestamp
        return age > timedelta(minutes=max_age_minutes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "rate": str(self.rate),
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider,
            "bid": str(self.bid) if self.bid else None,
            "ask": str(self.ask) if self.ask else None
        }


class CurrencyConverter:
    """
    Industrial currency conversion engine with multiple providers,
    caching, and fallback mechanisms for high availability.
    """
    
    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        cache: Optional[PerformanceCache] = None,
        primary_provider: CurrencyProvider = CurrencyProvider.EXCHANGE_RATES_API,
        fallback_providers: Optional[List[CurrencyProvider]] = None
    ):
        self.config = config or PaymentConfig()
        self.cache = cache
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or [
            CurrencyProvider.FIXER_IO,
            CurrencyProvider.OPENEXCHANGERATES
        ]
        
        # Provider configurations
        self.provider_configs = {
            CurrencyProvider.EXCHANGE_RATES_API: {
                "url": "https://api.exchangerate-api.com/v4/latest/{base}",
                "requires_key": False
            },
            CurrencyProvider.FIXER_IO: {
                "url": "https://api.fixer.io/latest",
                "requires_key": True
            },
            CurrencyProvider.OPENEXCHANGERATES: {
                "url": "https://openexchangerates.org/api/latest.json",
                "requires_key": True
            },
            CurrencyProvider.CURRENCYLAYER: {
                "url": "http://api.currencylayer.com/live",
                "requires_key": True
            }
        }
        
        # Session for HTTP requests
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Supported currencies
        self.supported_currencies = set(code.value for code in CurrencyCode)
        
        # Rate limits and caching
        self.rate_cache_ttl = 900  # 15 minutes
        self.request_timeout = 10  # seconds
        self.max_retries = 3

    async def initialize(self):
        """Initialize currency converter"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "PaymentProcessor/1.0"}
            )
        
        logger.info("Currency converter initialized")

    async def shutdown(self):
        """Shutdown currency converter"""
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("Currency converter shutdown")

    async def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> Tuple[Decimal, ExchangeRate]:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            use_cache: Whether to use cached rates
            
        Returns:
            Tuple of (converted_amount, exchange_rate)
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Validate currencies
        if from_currency not in self.supported_currencies:
            raise CurrencyNotSupportedError(f"Currency not supported: {from_currency}")
        
        if to_currency not in self.supported_currencies:
            raise CurrencyNotSupportedError(f"Currency not supported: {to_currency}")
        
        # Same currency - no conversion needed
        if from_currency == to_currency:
            mock_rate = ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal("1.0"),
                timestamp=datetime.utcnow(),
                provider="direct"
            )
            return amount, mock_rate
        
        # Get exchange rate
        exchange_rate = await self.get_exchange_rate(
            from_currency=from_currency,
            to_currency=to_currency,
            use_cache=use_cache
        )
        
        # Convert amount
        converted_amount = (amount * exchange_rate.rate).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )
        
        logger.debug(
            f"Converted {amount} {from_currency} to {converted_amount} {to_currency} "
            f"at rate {exchange_rate.rate}"
        )
        
        return converted_amount, exchange_rate

    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        use_cache: bool = True
    ) -> ExchangeRate:
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            use_cache: Whether to use cached rates
            
        Returns:
            ExchangeRate object
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Try cache first
        if use_cache and self.cache:
            cache_key = generate_cache_key("exchange_rate", from_currency, to_currency)
            cached_rate_data = await self.cache.get(cache_key)
            
            if cached_rate_data:
                # Reconstruct ExchangeRate from cached data
                rate = ExchangeRate(
                    from_currency=cached_rate_data["from_currency"],
                    to_currency=cached_rate_data["to_currency"],
                    rate=Decimal(cached_rate_data["rate"]),
                    timestamp=datetime.fromisoformat(cached_rate_data["timestamp"]),
                    provider=cached_rate_data["provider"],
                    bid=Decimal(cached_rate_data["bid"]) if cached_rate_data.get("bid") else None,
                    ask=Decimal(cached_rate_data["ask"]) if cached_rate_data.get("ask") else None
                )
                
                if not rate.is_expired():
                    logger.debug(f"Using cached exchange rate: {from_currency} -> {to_currency}")
                    return rate
        
        # Fetch fresh rate from providers
        providers_to_try = [self.primary_provider] + self.fallback_providers
        
        for provider in providers_to_try:
            try:
                rate = await self._fetch_rate_from_provider(
                    provider=provider,
                    from_currency=from_currency,
                    to_currency=to_currency
                )
                
                if rate:
                    # Cache the rate
                    if use_cache and self.cache:
                        cache_key = generate_cache_key("exchange_rate", from_currency, to_currency)
                        await self.cache.set(
                            key=cache_key,
                            value=rate.to_dict(),
                            ttl=self.rate_cache_ttl
                        )
                    
                    return rate
                    
            except Exception as e:
                logger.warning(
                    f"Failed to fetch rate from {provider.value}: {str(e)}"
                )
                continue
        
        # All providers failed
        raise PaymentProcessingError(
            f"Failed to get exchange rate for {from_currency} -> {to_currency}"
        )

    async def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: List[str],
        use_cache: bool = True
    ) -> Dict[str, ExchangeRate]:
        """
        Get exchange rates for multiple currency pairs.
        
        Args:
            base_currency: Base currency code
            target_currencies: List of target currency codes
            use_cache: Whether to use cached rates
            
        Returns:
            Dictionary mapping currency codes to exchange rates
        """
        rates = {}
        
        # Create tasks for concurrent rate fetching
        tasks = []
        for target_currency in target_currencies:
            task = self.get_exchange_rate(
                from_currency=base_currency,
                to_currency=target_currency,
                use_cache=use_cache
            )
            tasks.append((target_currency, task))
        
        # Execute tasks concurrently
        for target_currency, task in tasks:
            try:
                rate = await task
                rates[target_currency] = rate
            except Exception as e:
                logger.error(
                    f"Failed to get rate for {base_currency} -> {target_currency}: {str(e)}"
                )
                continue
        
        return rates

    async def convert_to_base_currency(
        self,
        amounts: Dict[str, Decimal],
        base_currency: str = "USD"
    ) -> Dict[str, Decimal]:
        """
        Convert amounts in multiple currencies to base currency.
        
        Args:
            amounts: Dictionary mapping currency codes to amounts
            base_currency: Target base currency
            
        Returns:
            Dictionary mapping currency codes to converted amounts
        """
        converted_amounts = {}
        
        # Get all required exchange rates
        source_currencies = [curr for curr in amounts.keys() if curr != base_currency]
        rates = await self.get_multiple_rates(base_currency, source_currencies)
        
        # Convert each amount
        for currency, amount in amounts.items():
            if currency == base_currency:
                converted_amounts[currency] = amount
            else:
                # Get inverse rate (we have base->currency, need currency->base)
                if currency in rates:
                    inverse_rate = Decimal("1.0") / rates[currency].rate
                    converted_amount = (amount * inverse_rate).quantize(
                        Decimal("0.00"), rounding=ROUND_HALF_UP
                    )
                    converted_amounts[currency] = converted_amount
                else:
                    logger.warning(f"No exchange rate available for {currency}")
        
        return converted_amounts

    async def _fetch_rate_from_provider(
        self,
        provider: CurrencyProvider,
        from_currency: str,
        to_currency: str
    ) -> Optional[ExchangeRate]:
        """Fetch exchange rate from specific provider"""
        if provider == CurrencyProvider.MOCK:
            return await self._fetch_mock_rate(from_currency, to_currency)
        
        if not self.session:
            await self.initialize()
        
        provider_config = self.provider_configs.get(provider)
        if not provider_config:
            logger.error(f"Unknown provider: {provider}")
            return None
        
        try:
            # Build request URL and parameters
            url = provider_config["url"]
            params = {}
            
            if provider == CurrencyProvider.EXCHANGE_RATES_API:
                url = url.format(base=from_currency)
            elif provider == CurrencyProvider.FIXER_IO:
                params = {
                    "base": from_currency,
                    "symbols": to_currency
                }
                if provider_config["requires_key"]:
                    params["access_key"] = self.config.fixer_io_api_key
            elif provider == CurrencyProvider.OPENEXCHANGERATES:
                params = {
                    "base": from_currency,
                    "symbols": to_currency
                }
                if provider_config["requires_key"]:
                    params["app_id"] = self.config.openexchangerates_api_key
            elif provider == CurrencyProvider.CURRENCYLAYER:
                params = {
                    "source": from_currency,
                    "currencies": to_currency
                }
                if provider_config["requires_key"]:
                    params["access_key"] = self.config.currencylayer_api_key
            
            # Make HTTP request
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_provider_response(
                        provider=provider,
                        data=data,
                        from_currency=from_currency,
                        to_currency=to_currency
                    )
                else:
                    logger.error(
                        f"Provider {provider.value} returned status {response.status}"
                    )
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching rate from {provider.value}")
            return None
        except Exception as e:
            logger.error(f"Error fetching rate from {provider.value}: {str(e)}")
            return None

    def _parse_provider_response(
        self,
        provider: CurrencyProvider,
        data: Dict[str, Any],
        from_currency: str,
        to_currency: str
    ) -> Optional[ExchangeRate]:
        """Parse provider response into ExchangeRate object"""
        try:
            if provider == CurrencyProvider.EXCHANGE_RATES_API:
                if "rates" in data and to_currency in data["rates"]:
                    rate = Decimal(str(data["rates"][to_currency]))
                    timestamp = datetime.utcnow()  # API doesn't provide timestamp
                    
                    return ExchangeRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=rate,
                        timestamp=timestamp,
                        provider=provider.value
                    )
            
            elif provider == CurrencyProvider.FIXER_IO:
                if "rates" in data and to_currency in data["rates"]:
                    rate = Decimal(str(data["rates"][to_currency]))
                    timestamp = datetime.fromisoformat(data.get("date", datetime.utcnow().isoformat()))
                    
                    return ExchangeRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=rate,
                        timestamp=timestamp,
                        provider=provider.value
                    )
            
            elif provider == CurrencyProvider.OPENEXCHANGERATES:
                if "rates" in data and to_currency in data["rates"]:
                    rate = Decimal(str(data["rates"][to_currency]))
                    timestamp = datetime.fromtimestamp(data.get("timestamp", datetime.utcnow().timestamp()))
                    
                    return ExchangeRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=rate,
                        timestamp=timestamp,
                        provider=provider.value
                    )
            
            elif provider == CurrencyProvider.CURRENCYLAYER:
                quotes_key = f"{from_currency}{to_currency}"
                if "quotes" in data and quotes_key in data["quotes"]:
                    rate = Decimal(str(data["quotes"][quotes_key]))
                    timestamp = datetime.fromtimestamp(data.get("timestamp", datetime.utcnow().timestamp()))
                    
                    return ExchangeRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=rate,
                        timestamp=timestamp,
                        provider=provider.value
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing {provider.value} response: {str(e)}")
            return None

    async def _fetch_mock_rate(self, from_currency: str, to_currency: str) -> ExchangeRate:
        """Fetch mock exchange rate for testing"""
        # Mock exchange rates (not for production use)
        mock_rates = {
            ("USD", "EUR"): Decimal("0.85"),
            ("EUR", "USD"): Decimal("1.18"),
            ("USD", "GBP"): Decimal("0.73"),
            ("GBP", "USD"): Decimal("1.37"),
            ("USD", "JPY"): Decimal("110.0"),
            ("JPY", "USD"): Decimal("0.009"),
        }
        
        rate_key = (from_currency, to_currency)
        reverse_key = (to_currency, from_currency)
        
        if rate_key in mock_rates:
            rate = mock_rates[rate_key]
        elif reverse_key in mock_rates:
            rate = Decimal("1.0") / mock_rates[reverse_key]
        else:
            # Generate pseudo-random rate based on currency codes
            hash_val = hash(f"{from_currency}{to_currency}")
            rate = Decimal("1.0") + (Decimal(str(abs(hash_val % 100))) / Decimal("1000"))
        
        return ExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate,
            timestamp=datetime.utcnow(),
            provider="mock"
        )

    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currency codes"""
        return sorted(list(self.supported_currencies))

    async def validate_currency_pair(self, from_currency: str, to_currency: str) -> bool:
        """Validate if currency pair is supported"""
        try:
            await self.get_exchange_rate(from_currency, to_currency, use_cache=False)
            return True
        except Exception:
            return False


# Utility functions
def format_currency(amount: Decimal, currency: str, locale: str = "en_US") -> str:
    """Format amount with currency symbol"""
    # Simplified formatting (in production, use babel or locale-specific formatting)
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "CHF": "CHF",
        "BTC": "₿",
        "ETH": "Ξ"
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    if currency == "JPY":  # Japanese Yen has no decimal places
        formatted_amount = f"{amount:.0f}"
    else:
        formatted_amount = f"{amount:.2f}"
    
    return f"{symbol}{formatted_amount}"


def parse_currency_amount(amount_str: str) -> Tuple[Decimal, Optional[str]]:
    """Parse currency amount string into amount and currency"""
    # This is a simplified parser
    import re
    
    # Remove whitespace
    amount_str = amount_str.strip()
    
    # Try to extract currency symbol/code
    currency_patterns = [
        (r'^\$(\d+(?:\.\d{2})?)', 'USD'),
        (r'^€(\d+(?:\.\d{2})?)', 'EUR'),
        (r'^£(\d+(?:\.\d{2})?)', 'GBP'),
        (r'^¥(\d+(?:\.\d{2})?)', 'JPY'),
        (r'^(\d+(?:\.\d{2})?)\s*([A-Z]{3})$', None),  # Amount followed by currency code
    ]
    
    for pattern, default_currency in currency_patterns:
        match = re.match(pattern, amount_str)
        if match:
            if default_currency:
                amount = Decimal(match.group(1))
                currency = default_currency
            else:
                amount = Decimal(match.group(1))
                currency = match.group(2)
            return amount, currency
    
    # Default: assume it's just a number
    try:
        amount = Decimal(amount_str)
        return amount, None
    except:
        raise ValueError(f"Cannot parse currency amount: {amount_str}")
