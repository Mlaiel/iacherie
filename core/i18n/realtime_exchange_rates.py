"""Real-time Exchange Rate Engine - Ainflue Platform
================================================================================
Module: core/i18n/realtime_exchange_rates.py  
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Real-time Exchange Rate Engine - Financial Data Processing
Responsibility: Multi-provider exchange rate aggregation, real-time updates, financial calculations
Technologies: Python, Financial APIs, WebSocket connections, Rate caching, Currency conversion
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Rate request → Provider aggregation → Real-time fetch → Rate validation → 
Cache update → Conversion calculation → Historical tracking → Alert generation
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import time
import hashlib

logger = logging.getLogger(__name__)


class ExchangeRateProvider(Enum):
    """Exchange rate data providers"""
    CENTRAL_BANK_ECB = "ecb"                    # European Central Bank
    FEDERAL_RESERVE = "fed"                     # US Federal Reserve
    BANK_OF_ENGLAND = "boe"                     # Bank of England
    BANK_OF_JAPAN = "boj"                       # Bank of Japan
    SWISS_NATIONAL_BANK = "snb"                 # Swiss National Bank
    BANK_OF_CANADA = "boc"                      # Bank of Canada
    RESERVE_BANK_AUSTRALIA = "rba"              # Reserve Bank of Australia
    PEOPLES_BANK_CHINA = "pboc"                 # People's Bank of China
    
    # Commercial Providers
    FIXER_IO = "fixer"                          # Fixer.io API
    EXCHANGE_RATES_API = "exchangerates"        # ExchangeRates API
    CURRENCYLAYER = "currencylayer"             # CurrencyLayer API
    OPENEXCHANGERATES = "openexchange"          # Open Exchange Rates
    ALPHA_VANTAGE = "alphavantage"              # Alpha Vantage
    FOREX_API = "forexapi"                      # Forex API
    
    # Crypto Providers
    COINBASE_API = "coinbase"                   # Coinbase API
    BINANCE_API = "binance"                     # Binance API
    KRAKEN_API = "kraken"                       # Kraken API
    
    # Regional Specialists
    BANK_AL_MAGHRIB = "bam"                     # Morocco Central Bank
    CENTRAL_BANK_UAE = "cbuae"                  # UAE Central Bank
    SAUDI_MONETARY_AUTHORITY = "sama"           # Saudi Arabia
    CENTRAL_BANK_EGYPT = "cbe"                  # Central Bank of Egypt
    SOUTH_AFRICAN_RESERVE_BANK = "sarb"         # South African Reserve Bank


@dataclass
class ExchangeRate:
    """Exchange rate data structure"""
    from_currency: str
    to_currency: str
    rate: Decimal
    timestamp: datetime
    provider: ExchangeRateProvider
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    spread: Optional[Decimal] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CurrencyConversion:
    """Currency conversion result"""
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    exchange_rate: Decimal
    conversion_fee: Decimal
    total_cost: Decimal
    timestamp: datetime
    provider_used: ExchangeRateProvider
    rate_age_seconds: int


class RealtimeExchangeRateEngine:
    """Advanced real-time exchange rate engine with multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self.rate_cache = {}
        self.historical_rates = {}
        self.provider_weights = {}
        self.update_intervals = {}
        self.last_updates = {}
        self.conversion_fees = {}
        self.alert_thresholds = {}
        self.fallback_chain = []
        
        # Initialize providers
        self._initialize_providers()
        self._initialize_conversion_fees()
        self._initialize_update_intervals()
        
        # Start background tasks
        self.update_task = None
        self.monitoring_task = None
    
    def _initialize_providers(self):
        """Initialize exchange rate providers configuration"""
        
        self.providers = {
            ExchangeRateProvider.CENTRAL_BANK_ECB: {
                "url": "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml",
                "api_key": None,
                "currencies": ["EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "SEK", "NOK", "DKK"],
                "base_currency": "EUR",
                "format": "xml",
                "reliability": 0.95,
                "latency_ms": 500,
                "free_tier": True,
                "rate_limit": "unlimited"
            },
            
            ExchangeRateProvider.FIXER_IO: {
                "url": "https://api.fixer.io/latest",
                "api_key": None,  # Set from environment
                "currencies": ["all"],
                "base_currency": "EUR",
                "format": "json",
                "reliability": 0.92,
                "latency_ms": 200,
                "free_tier": True,
                "rate_limit": "1000/month"
            },
            
            ExchangeRateProvider.EXCHANGE_RATES_API: {
                "url": "https://api.exchangerate-api.com/v4/latest/",
                "api_key": None,
                "currencies": ["all"],
                "base_currency": "configurable",
                "format": "json", 
                "reliability": 0.88,
                "latency_ms": 300,
                "free_tier": True,
                "rate_limit": "1500/month"
            },
            
            ExchangeRateProvider.OPENEXCHANGERATES: {
                "url": "https://openexchangerates.org/api/latest.json",
                "api_key": None,  # Set from environment
                "currencies": ["all"],
                "base_currency": "USD",
                "format": "json",
                "reliability": 0.94,
                "latency_ms": 150,
                "free_tier": True,
                "rate_limit": "1000/month"
            },
            
            ExchangeRateProvider.ALPHA_VANTAGE: {
                "url": "https://www.alphavantage.co/query",
                "api_key": None,  # Set from environment
                "currencies": ["all"],
                "base_currency": "configurable",
                "format": "json",
                "reliability": 0.93,
                "latency_ms": 400,
                "free_tier": True,
                "rate_limit": "5/minute"
            },
            
            ExchangeRateProvider.COINBASE_API: {
                "url": "https://api.coinbase.com/v2/exchange-rates",
                "api_key": None,
                "currencies": ["BTC", "ETH", "USDC", "USDT", "USD", "EUR", "GBP"],
                "base_currency": "USD",
                "format": "json",
                "reliability": 0.91,
                "latency_ms": 250,
                "free_tier": True,
                "rate_limit": "10000/hour"
            },
            
            ExchangeRateProvider.BANK_AL_MAGHRIB: {
                "url": "https://www.bkam.ma/Marches/Principaux-indicateurs/Cours-de-change/Cours-de-reference",
                "api_key": None,
                "currencies": ["MAD", "EUR", "USD", "GBP", "CHF", "JPY", "SAR", "AED"],
                "base_currency": "MAD",
                "format": "json",
                "reliability": 0.97,
                "latency_ms": 800,
                "free_tier": True,
                "rate_limit": "unlimited"
            },
            
            ExchangeRateProvider.CENTRAL_BANK_UAE: {
                "url": "https://www.centralbank.ae/en/forex-eibor/exchange-rates",
                "api_key": None,
                "currencies": ["AED", "USD", "EUR", "GBP", "JPY", "SAR", "KWD", "QAR", "OMR"],
                "base_currency": "AED",
                "format": "json",
                "reliability": 0.96,
                "latency_ms": 600,
                "free_tier": True,
                "rate_limit": "unlimited"
            }
        }
        
        # Set provider weights based on reliability
        self.provider_weights = {
            provider: config["reliability"] 
            for provider, config in self.providers.items()
        }
        
        # Define fallback chain
        self.fallback_chain = [
            ExchangeRateProvider.CENTRAL_BANK_ECB,
            ExchangeRateProvider.FIXER_IO,
            ExchangeRateProvider.OPENEXCHANGERATES,
            ExchangeRateProvider.EXCHANGE_RATES_API,
            ExchangeRateProvider.ALPHA_VANTAGE
        ]
    
    def _initialize_conversion_fees(self):
        """Initialize conversion fees by provider and currency pair"""
        
        self.conversion_fees = {
            # Major currency pairs (lower fees)
            ("USD", "EUR"): Decimal("0.0025"),  # 0.25%
            ("EUR", "USD"): Decimal("0.0025"),
            ("GBP", "USD"): Decimal("0.003"),   # 0.3%
            ("USD", "GBP"): Decimal("0.003"),
            ("JPY", "USD"): Decimal("0.0035"),  # 0.35%
            ("USD", "JPY"): Decimal("0.0035"),
            
            # Regional currencies (moderate fees)
            ("AED", "USD"): Decimal("0.005"),   # 0.5%
            ("USD", "AED"): Decimal("0.005"),
            ("SAR", "USD"): Decimal("0.005"),
            ("USD", "SAR"): Decimal("0.005"),
            ("MAD", "EUR"): Decimal("0.006"),   # 0.6%
            ("EUR", "MAD"): Decimal("0.006"),
            
            # Exotic pairs (higher fees)
            ("default"): Decimal("0.01")        # 1% default fee
        }
    
    def _initialize_update_intervals(self):
        """Initialize update intervals for different providers"""
        
        self.update_intervals = {
            ExchangeRateProvider.CENTRAL_BANK_ECB: 3600,     # 1 hour
            ExchangeRateProvider.FIXER_IO: 300,              # 5 minutes
            ExchangeRateProvider.EXCHANGE_RATES_API: 600,    # 10 minutes
            ExchangeRateProvider.OPENEXCHANGERATES: 300,     # 5 minutes
            ExchangeRateProvider.ALPHA_VANTAGE: 900,         # 15 minutes
            ExchangeRateProvider.COINBASE_API: 60,           # 1 minute (crypto)
            ExchangeRateProvider.BANK_AL_MAGHRIB: 3600,      # 1 hour
            ExchangeRateProvider.CENTRAL_BANK_UAE: 3600      # 1 hour
        }
    
    async def start_realtime_updates(self):
        """Start real-time exchange rate updates"""
        try:
            self.update_task = asyncio.create_task(self._update_rates_continuously())
            self.monitoring_task = asyncio.create_task(self._monitor_rate_health())
            logger.info("Real-time exchange rate updates started")
        except Exception as e:
            logger.error(f"Failed to start real-time updates: {e}")
    
    async def stop_realtime_updates(self):
        """Stop real-time exchange rate updates"""
        try:
            if self.update_task:
                self.update_task.cancel()
            if self.monitoring_task:
                self.monitoring_task.cancel()
            logger.info("Real-time exchange rate updates stopped")
        except Exception as e:
            logger.error(f"Failed to stop real-time updates: {e}")
    
    async def _update_rates_continuously(self):
        """Continuously update exchange rates from all providers"""
        while True:
            try:
                current_time = datetime.now()
                
                # Update rates from each provider based on their interval
                for provider, interval in self.update_intervals.items():
                    last_update = self.last_updates.get(provider, datetime.min)
                    
                    if (current_time - last_update).total_seconds() >= interval:
                        await self._update_rates_from_provider(provider)
                        self.last_updates[provider] = current_time
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in continuous rate updates: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _monitor_rate_health(self):
        """Monitor exchange rate data health and alert on issues"""
        while True:
            try:
                await self._check_rate_staleness()
                await self._check_rate_anomalies()
                await self._check_provider_availability()
                
                # Check every 5 minutes
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in rate health monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _update_rates_from_provider(self, provider: ExchangeRateProvider):
        """Update exchange rates from a specific provider"""
        try:
            provider_config = self.providers[provider]
            
            async with aiohttp.ClientSession() as session:
                if provider == ExchangeRateProvider.CENTRAL_BANK_ECB:
                    rates = await self._fetch_ecb_rates(session, provider_config)
                elif provider == ExchangeRateProvider.FIXER_IO:
                    rates = await self._fetch_fixer_rates(session, provider_config)
                elif provider == ExchangeRateProvider.EXCHANGE_RATES_API:
                    rates = await self._fetch_exchangerates_api(session, provider_config)
                elif provider == ExchangeRateProvider.OPENEXCHANGERATES:
                    rates = await self._fetch_openexchange_rates(session, provider_config)
                elif provider == ExchangeRateProvider.COINBASE_API:
                    rates = await self._fetch_coinbase_rates(session, provider_config)
                else:
                    rates = await self._fetch_generic_rates(session, provider_config)
                
                # Store rates in cache
                for rate in rates:
                    cache_key = f"{rate.from_currency}_{rate.to_currency}_{provider.value}"
                    self.rate_cache[cache_key] = rate
                    
                    # Store in historical data
                    historical_key = f"{rate.from_currency}_{rate.to_currency}"
                    if historical_key not in self.historical_rates:
                        self.historical_rates[historical_key] = []
                    
                    self.historical_rates[historical_key].append(rate)
                    
                    # Keep only last 1000 historical entries per pair
                    if len(self.historical_rates[historical_key]) > 1000:
                        self.historical_rates[historical_key] = self.historical_rates[historical_key][-1000:]
                
                logger.info(f"Updated {len(rates)} rates from {provider.value}")
                
        except Exception as e:
            logger.error(f"Failed to update rates from {provider.value}: {e}")
    
    async def _fetch_fixer_rates(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Fetch rates from Fixer.io API"""
        rates = []
        try:
            url = config["url"]
            if config.get("api_key"):
                url += f"?access_key={config['api_key']}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        base_currency = data["base"]
                        timestamp = datetime.fromtimestamp(data["timestamp"])
                        
                        for currency, rate in data["rates"].items():
                            rates.append(ExchangeRate(
                                from_currency=base_currency,
                                to_currency=currency,
                                rate=Decimal(str(rate)),
                                timestamp=timestamp,
                                provider=ExchangeRateProvider.FIXER_IO,
                                confidence=0.92
                            ))
                    
        except Exception as e:
            logger.error(f"Error fetching Fixer.io rates: {e}")
        
        return rates
    
    async def _fetch_openexchange_rates(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Fetch rates from Open Exchange Rates API"""
        rates = []
        try:
            url = config["url"]
            if config.get("api_key"):
                url += f"?app_id={config['api_key']}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    base_currency = data["base"]
                    timestamp = datetime.fromtimestamp(data["timestamp"])
                    
                    for currency, rate in data["rates"].items():
                        rates.append(ExchangeRate(
                            from_currency=base_currency,
                            to_currency=currency,
                            rate=Decimal(str(rate)),
                            timestamp=timestamp,
                            provider=ExchangeRateProvider.OPENEXCHANGERATES,
                            confidence=0.94
                        ))
                    
        except Exception as e:
            logger.error(f"Error fetching Open Exchange Rates: {e}")
        
        return rates
    
    async def _fetch_coinbase_rates(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Fetch rates from Coinbase API"""
        rates = []
        try:
            url = config["url"]
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data"):
                        base_currency = data["data"]["currency"]
                        timestamp = datetime.now()  # Coinbase doesn't provide timestamp
                        
                        for currency, rate in data["data"]["rates"].items():
                            rates.append(ExchangeRate(
                                from_currency=base_currency,
                                to_currency=currency,
                                rate=Decimal(str(rate)),
                                timestamp=timestamp,
                                provider=ExchangeRateProvider.COINBASE_API,
                                confidence=0.91
                            ))
                    
        except Exception as e:
            logger.error(f"Error fetching Coinbase rates: {e}")
        
        return rates
    
    async def _fetch_ecb_rates(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Fetch rates from European Central Bank"""
        rates = []
        try:
            # ECB provides XML format, would need XML parsing
            # For now, implementing a placeholder
            timestamp = datetime.now()
            
            # Sample ECB rates (in production, parse XML)
            sample_rates = {
                "USD": "1.0850",
                "GBP": "0.8650", 
                "JPY": "159.50",
                "CHF": "0.9320",
                "CAD": "1.4720",
                "AUD": "1.6180"
            }
            
            for currency, rate in sample_rates.items():
                rates.append(ExchangeRate(
                    from_currency="EUR",
                    to_currency=currency,
                    rate=Decimal(rate),
                    timestamp=timestamp,
                    provider=ExchangeRateProvider.CENTRAL_BANK_ECB,
                    confidence=0.95
                ))
                
        except Exception as e:
            logger.error(f"Error fetching ECB rates: {e}")
        
        return rates
    
    async def _fetch_exchangerates_api(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Fetch rates from ExchangeRates API"""
        rates = []
        try:
            # Can specify base currency
            base_currencies = ["USD", "EUR", "GBP"]
            
            for base in base_currencies:
                url = f"{config['url']}{base}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        timestamp = datetime.now()
                        
                        for currency, rate in data["rates"].items():
                            rates.append(ExchangeRate(
                                from_currency=base,
                                to_currency=currency,
                                rate=Decimal(str(rate)),
                                timestamp=timestamp,
                                provider=ExchangeRateProvider.EXCHANGE_RATES_API,
                                confidence=0.88
                            ))
                        
                        # Rate limit consideration
                        await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error fetching ExchangeRates API: {e}")
        
        return rates
    
    async def _fetch_generic_rates(self, session: aiohttp.ClientSession, config: Dict) -> List[ExchangeRate]:
        """Generic rate fetching for other providers"""
        rates = []
        try:
            # Implementation depends on specific provider format
            # This is a placeholder for extensibility
            pass
        except Exception as e:
            logger.error(f"Error fetching generic rates: {e}")
        
        return rates
    
    async def get_exchange_rate(
        self, 
        from_currency: str, 
        to_currency: str,
        preferred_provider: Optional[ExchangeRateProvider] = None
    ) -> Optional[ExchangeRate]:
        """Get current exchange rate between two currencies"""
        
        # Direct rate lookup
        cache_key = f"{from_currency}_{to_currency}"
        
        # Try preferred provider first
        if preferred_provider:
            provider_key = f"{cache_key}_{preferred_provider.value}"
            if provider_key in self.rate_cache:
                rate = self.rate_cache[provider_key]
                if self._is_rate_fresh(rate):
                    return rate
        
        # Try all providers by weight/reliability
        for provider in sorted(self.provider_weights.keys(), 
                             key=lambda p: self.provider_weights[p], reverse=True):
            provider_key = f"{cache_key}_{provider.value}"
            if provider_key in self.rate_cache:
                rate = self.rate_cache[provider_key]
                if self._is_rate_fresh(rate):
                    return rate
        
        # Try inverse rate
        inverse_key = f"{to_currency}_{from_currency}"
        for provider in sorted(self.provider_weights.keys(), 
                             key=lambda p: self.provider_weights[p], reverse=True):
            provider_key = f"{inverse_key}_{provider.value}"
            if provider_key in self.rate_cache:
                rate = self.rate_cache[provider_key]
                if self._is_rate_fresh(rate):
                    # Calculate inverse rate
                    return ExchangeRate(
                        from_currency=from_currency,
                        to_currency=to_currency,
                        rate=Decimal("1") / rate.rate,
                        timestamp=rate.timestamp,
                        provider=rate.provider,
                        confidence=rate.confidence * 0.95  # Slightly lower confidence for inverse
                    )
        
        # If no cached rate, try to fetch immediately
        try:
            await self._update_rates_from_provider(self.fallback_chain[0])
            return await self.get_exchange_rate(from_currency, to_currency, preferred_provider)
        except Exception as e:
            logger.error(f"Failed to fetch immediate rate for {from_currency}/{to_currency}: {e}")
            return None
    
    async def convert_currency(
        self,
        amount: Union[int, float, Decimal],
        from_currency: str,
        to_currency: str,
        include_fees: bool = True,
        preferred_provider: Optional[ExchangeRateProvider] = None
    ) -> Optional[CurrencyConversion]:
        """Convert amount from one currency to another"""
        
        try:
            # Get exchange rate
            rate_info = await self.get_exchange_rate(from_currency, to_currency, preferred_provider)
            if not rate_info:
                logger.warning(f"No exchange rate available for {from_currency}/{to_currency}")
                return None
            
            # Convert amount to Decimal for precision
            original_amount = Decimal(str(amount))
            
            # Calculate converted amount
            converted_amount = original_amount * rate_info.rate
            
            # Calculate conversion fee
            conversion_fee = Decimal("0")
            if include_fees:
                fee_key = (from_currency, to_currency)
                fee_rate = self.conversion_fees.get(fee_key, self.conversion_fees["default"])
                conversion_fee = converted_amount * fee_rate
            
            # Calculate total cost
            total_cost = converted_amount + conversion_fee
            
            # Calculate rate age
            rate_age = int((datetime.now() - rate_info.timestamp).total_seconds())
            
            return CurrencyConversion(
                original_amount=original_amount,
                converted_amount=converted_amount,
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=rate_info.rate,
                conversion_fee=conversion_fee,
                total_cost=total_cost,
                timestamp=datetime.now(),
                provider_used=rate_info.provider,
                rate_age_seconds=rate_age
            )
            
        except Exception as e:
            logger.error(f"Error converting {amount} {from_currency} to {to_currency}: {e}")
            return None
    
    def _is_rate_fresh(self, rate: ExchangeRate, max_age_seconds: int = 3600) -> bool:
        """Check if exchange rate is fresh enough to use"""
        age = (datetime.now() - rate.timestamp).total_seconds()
        return age <= max_age_seconds
    
    async def _check_rate_staleness(self):
        """Check for stale exchange rates and alert"""
        stale_threshold = 7200  # 2 hours
        current_time = datetime.now()
        
        stale_rates = []
        for key, rate in self.rate_cache.items():
            if (current_time - rate.timestamp).total_seconds() > stale_threshold:
                stale_rates.append(key)
        
        if stale_rates:
            logger.warning(f"Found {len(stale_rates)} stale exchange rates")
    
    async def _check_rate_anomalies(self):
        """Check for unusual rate movements and alert"""
        anomaly_threshold = 0.05  # 5% change threshold
        
        for pair_key, historical_data in self.historical_rates.items():
            if len(historical_data) >= 2:
                latest_rate = historical_data[-1].rate
                previous_rate = historical_data[-2].rate
                
                change_pct = abs(latest_rate - previous_rate) / previous_rate
                
                if change_pct > anomaly_threshold:
                    logger.warning(f"Anomalous rate change detected for {pair_key}: {change_pct:.2%}")
    
    async def _check_provider_availability(self):
        """Check provider availability and switch if needed"""
        unavailable_providers = []
        
        for provider, last_update in self.last_updates.items():
            expected_interval = self.update_intervals.get(provider, 3600)
            if (datetime.now() - last_update).total_seconds() > expected_interval * 2:
                unavailable_providers.append(provider)
        
        if unavailable_providers:
            logger.warning(f"Providers may be unavailable: {[p.value for p in unavailable_providers]}")
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of all supported currencies"""
        currencies = set()
        
        for provider_config in self.providers.values():
            if provider_config["currencies"] == ["all"]:
                # Major world currencies
                currencies.update([
                    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "SEK", "NOK", "DKK",
                    "CNY", "INR", "BRL", "MXN", "AED", "SAR", "MAD", "EGP", "ZAR", "TRY", "RUB",
                    "KRW", "SGD", "HKD", "THB", "MYR", "IDR", "PHP", "VND", "PKR", "BDT",
                    "BTC", "ETH", "USDC", "USDT", "ADA", "DOT", "SOL", "AVAX", "MATIC", "LINK"
                ])
            else:
                currencies.update(provider_config["currencies"])
        
        return sorted(list(currencies))
    
    def get_rate_statistics(self) -> Dict[str, Any]:
        """Get statistics about exchange rate data"""
        total_rates = len(self.rate_cache)
        
        provider_counts = {}
        for key in self.rate_cache.keys():
            provider = key.split("_")[-1]
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        fresh_rates = sum(1 for rate in self.rate_cache.values() if self._is_rate_fresh(rate))
        
        return {
            "total_cached_rates": total_rates,
            "fresh_rates": fresh_rates,
            "stale_rates": total_rates - fresh_rates,
            "rates_by_provider": provider_counts,
            "supported_currencies": len(self.get_supported_currencies()),
            "last_update_times": {p.value: t.isoformat() for p, t in self.last_updates.items()},
            "provider_weights": {p.value: w for p, w in self.provider_weights.items()}
        }