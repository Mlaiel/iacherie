"""
Currency Conversion Service for Ainflue Microservices
Real-time currency conversion and exchange rate management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import httpx
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
import aiofiles
import os

logger = logging.getLogger(__name__)


@dataclass
class ExchangeRate:
    """Exchange rate information"""
    base_currency: str
    target_currency: str
    rate: Decimal
    timestamp: datetime
    source: str
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None


@dataclass
class ConversionRequest:
    """Currency conversion request"""
    amount: Decimal
    from_currency: str
    to_currency: str
    timestamp: datetime = None
    precision: int = 2


@dataclass
class ConversionResult:
    """Currency conversion result"""
    original_amount: Decimal
    converted_amount: Decimal
    from_currency: str
    to_currency: str
    exchange_rate: Decimal
    timestamp: datetime
    fee_amount: Decimal = Decimal('0')
    total_amount: Decimal = None


class CurrencyConversionService:
    """Enterprise currency conversion service"""

    def __init__(self):
        self.exchange_rates = {}
        self.supported_currencies = set()
        self.rate_cache_ttl = timedelta(minutes=5)
        self.conversion_history = []
        self.fee_schedule = {}
        self.api_keys = {
            "exchangerate_api": os.getenv("EXCHANGERATE_API_KEY"),
            "fixer_io": os.getenv("FIXER_IO_API_KEY"),
            "currencylayer": os.getenv("CURRENCYLAYER_API_KEY")
        }
        self.base_currency = "USD"
        self.max_history = 10000
        
        # Initialize supported currencies
        self._initialize_currencies()
        
        # Schedule rate updates
        asyncio.create_task(self._schedule_rate_updates())

    def _initialize_currencies(self):
        """Initialize supported currencies"""
        self.supported_currencies = {
            # Major currencies
            "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
            # Crypto currencies (common ones)
            "BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "XRP", "BNB",
            # Regional currencies
            "CNY", "INR", "KRW", "SGD", "HKD", "MXN", "BRL", "RUB",
            "ZAR", "TRY", "PLN", "SEK", "NOK", "DKK", "CZK", "HUF",
            # Middle East & Africa
            "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "EGP", "MAD",
            # Creator economy tokens (example)
            "CREATOR", "INFLUENCE", "CONTENT"
        }

    async def _schedule_rate_updates(self):
        """Schedule periodic exchange rate updates"""
        while True:
            try:
                await self.update_exchange_rates()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Error in scheduled rate update: {str(e)}")
                await asyncio.sleep(60)  # Retry after 1 minute on error

    async def update_exchange_rates(self) -> bool:
        """Update exchange rates from external APIs"""
        try:
            success = False
            
            # Try multiple sources for redundancy
            sources = [
                self._fetch_rates_exchangerate_api,
                self._fetch_rates_fixer_io,
                self._fetch_rates_currencylayer
            ]
            
            for source_func in sources:
                try:
                    rates = await source_func()
                    if rates:
                        self._update_rate_cache(rates)
                        success = True
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch rates from source: {str(e)}")
                    continue
            
            if success:
                logger.info(f"Updated exchange rates for {len(self.exchange_rates)} currency pairs")
                return True
            else:
                logger.error("Failed to update exchange rates from all sources")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update exchange rates: {str(e)}")
            return False

    async def _fetch_rates_exchangerate_api(self) -> Optional[Dict[str, ExchangeRate]]:
        """Fetch rates from ExchangeRate-API"""
        if not self.api_keys.get("exchangerate_api"):
            return None
        
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.api_keys['exchangerate_api']}/latest/{self.base_currency}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data["result"] == "success":
                rates = {}
                timestamp = datetime.utcnow()
                
                for currency, rate in data["conversion_rates"].items():
                    rate_obj = ExchangeRate(
                        base_currency=self.base_currency,
                        target_currency=currency,
                        rate=Decimal(str(rate)),
                        timestamp=timestamp,
                        source="exchangerate_api"
                    )
                    rates[f"{self.base_currency}_{currency}"] = rate_obj
                
                return rates
                
        except Exception as e:
            logger.error(f"ExchangeRate-API fetch failed: {str(e)}")
            return None

    async def _fetch_rates_fixer_io(self) -> Optional[Dict[str, ExchangeRate]]:
        """Fetch rates from Fixer.io"""
        if not self.api_keys.get("fixer_io"):
            return None
        
        try:
            url = f"http://data.fixer.io/api/latest?access_key={self.api_keys['fixer_io']}&base={self.base_currency}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data["success"]:
                rates = {}
                timestamp = datetime.utcnow()
                
                for currency, rate in data["rates"].items():
                    rate_obj = ExchangeRate(
                        base_currency=self.base_currency,
                        target_currency=currency,
                        rate=Decimal(str(rate)),
                        timestamp=timestamp,
                        source="fixer_io"
                    )
                    rates[f"{self.base_currency}_{currency}"] = rate_obj
                
                return rates
                
        except Exception as e:
            logger.error(f"Fixer.io fetch failed: {str(e)}")
            return None

    async def _fetch_rates_currencylayer(self) -> Optional[Dict[str, ExchangeRate]]:
        """Fetch rates from CurrencyLayer"""
        if not self.api_keys.get("currencylayer"):
            return None
        
        try:
            url = f"http://api.currencylayer.com/live?access_key={self.api_keys['currencylayer']}&source={self.base_currency}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data["success"]:
                rates = {}
                timestamp = datetime.utcnow()
                
                for pair, rate in data["quotes"].items():
                    # Remove base currency prefix (e.g., "USDEUR" -> "EUR")
                    target_currency = pair[3:]
                    
                    rate_obj = ExchangeRate(
                        base_currency=self.base_currency,
                        target_currency=target_currency,
                        rate=Decimal(str(rate)),
                        timestamp=timestamp,
                        source="currencylayer"
                    )
                    rates[f"{self.base_currency}_{target_currency}"] = rate_obj
                
                return rates
                
        except Exception as e:
            logger.error(f"CurrencyLayer fetch failed: {str(e)}")
            return None

    def _update_rate_cache(self, rates: Dict[str, ExchangeRate]):
        """Update internal rate cache"""
        self.exchange_rates.update(rates)
        
        # Add reverse rates
        reverse_rates = {}
        for rate_key, rate_obj in rates.items():
            if rate_obj.rate != 0:
                reverse_key = f"{rate_obj.target_currency}_{rate_obj.base_currency}"
                reverse_rate = ExchangeRate(
                    base_currency=rate_obj.target_currency,
                    target_currency=rate_obj.base_currency,
                    rate=Decimal('1') / rate_obj.rate,
                    timestamp=rate_obj.timestamp,
                    source=rate_obj.source
                )
                reverse_rates[reverse_key] = reverse_rate
        
        self.exchange_rates.update(reverse_rates)

    async def convert_currency(self, request: ConversionRequest) -> ConversionResult:
        """Convert currency amount"""
        try:
            if request.from_currency == request.to_currency:
                # Same currency, no conversion needed
                return ConversionResult(
                    original_amount=request.amount,
                    converted_amount=request.amount,
                    from_currency=request.from_currency,
                    to_currency=request.to_currency,
                    exchange_rate=Decimal('1'),
                    timestamp=datetime.utcnow(),
                    total_amount=request.amount
                )
            
            # Get exchange rate
            exchange_rate = await self.get_exchange_rate(request.from_currency, request.to_currency)
            
            if not exchange_rate:
                raise ValueError(f"Exchange rate not available for {request.from_currency} to {request.to_currency}")
            
            # Calculate conversion
            converted_amount = request.amount * exchange_rate.rate
            
            # Round to specified precision
            converted_amount = converted_amount.quantize(
                Decimal('0.01') if request.precision == 2 else Decimal('0.1') ** request.precision,
                rounding=ROUND_HALF_UP
            )
            
            # Calculate fees
            fee_amount = await self._calculate_conversion_fee(
                request.amount, request.from_currency, request.to_currency
            )
            
            total_amount = converted_amount - fee_amount
            
            result = ConversionResult(
                original_amount=request.amount,
                converted_amount=converted_amount,
                from_currency=request.from_currency,
                to_currency=request.to_currency,
                exchange_rate=exchange_rate.rate,
                timestamp=datetime.utcnow(),
                fee_amount=fee_amount,
                total_amount=total_amount
            )
            
            # Store in history
            self._store_conversion_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Currency conversion failed: {str(e)}")
            raise

    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[ExchangeRate]:
        """Get exchange rate between two currencies"""
        try:
            # Direct rate
            rate_key = f"{from_currency}_{to_currency}"
            if rate_key in self.exchange_rates:
                rate = self.exchange_rates[rate_key]
                
                # Check if rate is fresh
                if datetime.utcnow() - rate.timestamp < self.rate_cache_ttl:
                    return rate
            
            # Try cross rates through base currency
            if from_currency != self.base_currency and to_currency != self.base_currency:
                base_to_from = f"{self.base_currency}_{from_currency}"
                base_to_to = f"{self.base_currency}_{to_currency}"
                
                if base_to_from in self.exchange_rates and base_to_to in self.exchange_rates:
                    rate_from = self.exchange_rates[base_to_from]
                    rate_to = self.exchange_rates[base_to_to]
                    
                    # Calculate cross rate
                    cross_rate = rate_to.rate / rate_from.rate
                    
                    return ExchangeRate(
                        base_currency=from_currency,
                        target_currency=to_currency,
                        rate=cross_rate,
                        timestamp=min(rate_from.timestamp, rate_to.timestamp),
                        source="cross_rate"
                    )
            
            # Rate not found, try to update
            await self.update_exchange_rates()
            
            # Try again after update
            if rate_key in self.exchange_rates:
                return self.exchange_rates[rate_key]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get exchange rate {from_currency} to {to_currency}: {str(e)}")
            return None

    async def _calculate_conversion_fee(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """Calculate conversion fee"""
        try:
            fee_key = f"{from_currency}_{to_currency}"
            
            # Default fee structure
            default_fee_rate = Decimal('0.002')  # 0.2%
            min_fee = Decimal('0.01')
            max_fee = Decimal('100.00')
            
            # Get specific fee rate if configured
            fee_rate = self.fee_schedule.get(fee_key, {}).get('rate', default_fee_rate)
            
            # Calculate fee
            fee_amount = amount * fee_rate
            
            # Apply min/max limits
            fee_amount = max(min_fee, min(fee_amount, max_fee))
            
            return fee_amount
            
        except Exception as e:
            logger.error(f"Failed to calculate conversion fee: {str(e)}")
            return Decimal('0')

    def _store_conversion_history(self, result: ConversionResult):
        """Store conversion in history"""
        try:
            self.conversion_history.append(result)
            
            # Limit history size
            if len(self.conversion_history) > self.max_history:
                self.conversion_history = self.conversion_history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Failed to store conversion history: {str(e)}")

    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return sorted(list(self.supported_currencies))

    async def get_conversion_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversion history"""
        try:
            recent_history = self.conversion_history[-limit:] if limit else self.conversion_history
            
            return [
                {
                    "original_amount": float(conv.original_amount),
                    "converted_amount": float(conv.converted_amount),
                    "from_currency": conv.from_currency,
                    "to_currency": conv.to_currency,
                    "exchange_rate": float(conv.exchange_rate),
                    "fee_amount": float(conv.fee_amount),
                    "total_amount": float(conv.total_amount),
                    "timestamp": conv.timestamp.isoformat()
                }
                for conv in recent_history
            ]
            
        except Exception as e:
            logger.error(f"Failed to get conversion history: {str(e)}")
            return []

    async def get_rate_summary(self) -> Dict[str, Any]:
        """Get exchange rate summary"""
        try:
            summary = {
                "base_currency": self.base_currency,
                "total_rates": len(self.exchange_rates),
                "supported_currencies": len(self.supported_currencies),
                "last_update": None,
                "rates": {},
                "sources": set(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            latest_update = None
            
            for rate_key, rate in self.exchange_rates.items():
                if rate.base_currency == self.base_currency:
                    summary["rates"][rate.target_currency] = {
                        "rate": float(rate.rate),
                        "timestamp": rate.timestamp.isoformat(),
                        "source": rate.source
                    }
                    
                    summary["sources"].add(rate.source)
                    
                    if not latest_update or rate.timestamp > latest_update:
                        latest_update = rate.timestamp
            
            summary["sources"] = list(summary["sources"])
            summary["last_update"] = latest_update.isoformat() if latest_update else None
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get rate summary: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Currency conversion service health check"""
        try:
            # Check rate freshness
            fresh_rates = 0
            stale_rates = 0
            cutoff_time = datetime.utcnow() - self.rate_cache_ttl
            
            for rate in self.exchange_rates.values():
                if rate.timestamp > cutoff_time:
                    fresh_rates += 1
                else:
                    stale_rates += 1
            
            return {
                "status": "healthy" if fresh_rates > 0 else "degraded",
                "supported_currencies": len(self.supported_currencies),
                "cached_rates": len(self.exchange_rates),
                "fresh_rates": fresh_rates,
                "stale_rates": stale_rates,
                "conversion_history_count": len(self.conversion_history),
                "api_keys_configured": sum(1 for key in self.api_keys.values() if key),
                "base_currency": self.base_currency,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Currency conversion health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global currency conversion service instance
currency_service = CurrencyConversionService()


async def convert_currency(amount: float, from_currency: str, to_currency: str) -> ConversionResult:
    """Convert currency amount"""
    request = ConversionRequest(
        amount=Decimal(str(amount)),
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper()
    )
    return await currency_service.convert_currency(request)


async def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """Get exchange rate between currencies"""
    rate = await currency_service.get_exchange_rate(from_currency.upper(), to_currency.upper())
    return float(rate.rate) if rate else None


if __name__ == "__main__":
    async def test_currency_service():
        """Test currency conversion service"""
        print("Testing Currency Conversion Service...")
        
        # Test conversion
        try:
            result = await convert_currency(100.0, "USD", "EUR")
            print(f"Conversion result: {result}")
        except Exception as e:
            print(f"Conversion failed: {e}")
        
        # Get supported currencies
        currencies = await currency_service.get_supported_currencies()
        print(f"Supported currencies: {currencies[:10]}...")
        
        # Health check
        health = await currency_service.health_check()
        print(f"Health: {health}")
    
    asyncio.run(test_currency_service())