"""
Ainflue Platform - Currency Conversion Monitor
==============================================

Advanced currency conversion monitoring system for tracking exchange rates,
conversion performance, and cost optimization across global monetization
workflows for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import json
import requests
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class ConversionProvider(Enum):
    """Currency conversion service providers."""
    FIXER_IO = "fixer_io"
    EXCHANGE_RATE_API = "exchange_rate_api"
    OPEN_EXCHANGE_RATES = "open_exchange_rates"
    CURRENCYLAYER = "currencylayer"
    INTERNAL_BANK = "internal_bank"
    CRYPTO_EXCHANGE = "crypto_exchange"

class ConversionStatus(Enum):
    """Currency conversion status."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    EXPIRED = "expired"
    RATE_UNAVAILABLE = "rate_unavailable"
    PROVIDER_ERROR = "provider_error"

class ConversionPriority(Enum):
    """Conversion priority levels."""
    REAL_TIME = "real_time"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BATCH = "batch"

@dataclass
class ExchangeRate:
    """Exchange rate information."""
    from_currency: str
    to_currency: str
    rate: Decimal
    provider: ConversionProvider
    timestamp: datetime
    valid_until: datetime
    bid_rate: Optional[Decimal] = None
    ask_rate: Optional[Decimal] = None
    spread: Optional[Decimal] = None
    source: str = ""
    confidence: float = 1.0

@dataclass
class ConversionRequest:
    """Currency conversion request."""
    request_id: str
    from_currency: str
    to_currency: str
    amount: Decimal
    priority: ConversionPriority
    partnership_id: Optional[str]
    creator_id: Optional[str]
    transaction_id: Optional[str]
    request_timestamp: datetime
    required_by: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionResult:
    """Currency conversion result."""
    request_id: str
    from_currency: str
    to_currency: str
    from_amount: Decimal
    to_amount: Decimal
    exchange_rate: Decimal
    provider: ConversionProvider
    status: ConversionStatus
    processing_time_ms: float
    fees: Decimal
    net_amount: Decimal
    conversion_timestamp: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionMetrics:
    """Currency conversion performance metrics."""
    time_period: Tuple[datetime, datetime]
    total_conversions: int
    successful_conversions: int
    failed_conversions: int
    success_rate: float
    average_processing_time: float
    total_volume_converted: Dict[str, Decimal]
    total_fees_collected: Dict[str, Decimal]
    provider_performance: Dict[ConversionProvider, Dict[str, Any]]
    currency_pair_performance: Dict[str, Dict[str, Any]]
    cost_savings: Decimal
    accuracy_score: float
    timestamp: datetime = field(default_factory=datetime.now)

class CurrencyConversionMonitor:
    """
    Advanced currency conversion monitoring system for monetization workflows.
    
    Features:
    - Multi-provider exchange rate aggregation
    - Real-time rate monitoring and alerting
    - Conversion performance tracking
    - Cost optimization and fee analysis
    - Rate accuracy monitoring
    - Provider reliability assessment
    - Currency risk assessment
    - Automated fallback mechanisms
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.exchange_rates: Dict[str, ExchangeRate] = {}
        self.conversion_requests: Dict[str, ConversionRequest] = {}
        self.conversion_results: Dict[str, ConversionResult] = {}
        self.conversion_history: deque = deque(maxlen=10000)
        self.provider_configs: Dict[ConversionProvider, Dict[str, Any]] = {}
        
        # Rate caching
        self.rate_cache: Dict[str, ExchangeRate] = {}
        self.cache_duration = timedelta(minutes=5)  # 5-minute cache
        
        # Provider performance tracking
        self.provider_metrics: Dict[ConversionProvider, Dict[str, Any]] = defaultdict(
            lambda: {
                'total_requests': 0,
                'successful_requests': 0,
                'average_response_time': 0.0,
                'error_count': 0,
                'last_error': None,
                'uptime_percentage': 100.0,
                'rate_accuracy': 0.0
            }
        )
        
        # Conversion thresholds and alerts
        self.alert_thresholds = {
            'rate_change_percentage': 5.0,  # 5% rate change
            'success_rate_minimum': 0.95,   # 95% success rate
            'processing_time_maximum': 2000,  # 2 seconds
            'fee_percentage_maximum': 0.05   # 5% fees
        }
        
        # Performance metrics
        self.metrics = {
            'total_conversions_monitored': 0,
            'total_volume_converted': Decimal('0'),
            'total_fees_saved': Decimal('0'),
            'average_conversion_accuracy': 0.0,
            'provider_switches': 0,
            'rate_alerts_triggered': 0
        }
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info("CurrencyConversionMonitor initialized")

    def _initialize_providers(self) -> None:
        """Initialize currency conversion providers."""
        self.provider_configs = {
            ConversionProvider.FIXER_IO: {
                'api_url': 'http://data.fixer.io/api/latest',
                'api_key': self.config.get('fixer_api_key', ''),
                'rate_limit': 1000,  # requests per month
                'fee_percentage': 0.01  # 1%
            },
            ConversionProvider.EXCHANGE_RATE_API: {
                'api_url': 'https://api.exchangerate-api.com/v4/latest/',
                'api_key': self.config.get('exchangerate_api_key', ''),
                'rate_limit': 1500,
                'fee_percentage': 0.008  # 0.8%
            },
            ConversionProvider.OPEN_EXCHANGE_RATES: {
                'api_url': 'https://openexchangerates.org/api/latest.json',
                'api_key': self.config.get('oxr_api_key', ''),
                'rate_limit': 1000,
                'fee_percentage': 0.012  # 1.2%
            },
            ConversionProvider.INTERNAL_BANK: {
                'api_url': self.config.get('bank_api_url', ''),
                'api_key': self.config.get('bank_api_key', ''),
                'rate_limit': 10000,
                'fee_percentage': 0.005  # 0.5%
            }
        }

    async def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str,
        provider: Optional[ConversionProvider] = None,
        force_refresh: bool = False
    ) -> Optional[ExchangeRate]:
        """Get exchange rate for currency pair."""
        try:
            cache_key = f"{from_currency}_{to_currency}"
            
            # Check cache first
            if not force_refresh and cache_key in self.rate_cache:
                cached_rate = self.rate_cache[cache_key]
                if datetime.now() < cached_rate.valid_until:
                    return cached_rate
            
            # Determine provider
            if not provider:
                provider = self._select_best_provider(from_currency, to_currency)
            
            # Fetch rate from provider
            rate = await self._fetch_rate_from_provider(from_currency, to_currency, provider)
            
            if rate:
                # Cache the rate
                self.rate_cache[cache_key] = rate
                self.exchange_rates[cache_key] = rate
                
                # Check for significant rate changes
                await self._check_rate_change_alerts(from_currency, to_currency, rate)
                
                logger.debug(f"Retrieved rate: {from_currency}/{to_currency} = {rate.rate}")
                return rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return None

    def _select_best_provider(self, from_currency: str, to_currency: str) -> ConversionProvider:
        """Select the best provider based on performance metrics."""
        # Score providers based on performance
        provider_scores = {}
        
        for provider in ConversionProvider:
            metrics = self.provider_metrics[provider]
            
            # Calculate score based on multiple factors
            success_rate = metrics['successful_requests'] / max(metrics['total_requests'], 1)
            response_time_score = max(0, 1 - (metrics['average_response_time'] / 5000))  # 5s baseline
            uptime_score = metrics['uptime_percentage'] / 100
            accuracy_score = metrics['rate_accuracy']
            
            # Weight the factors
            overall_score = (
                0.3 * success_rate +
                0.2 * response_time_score +
                0.3 * uptime_score +
                0.2 * accuracy_score
            )
            
            provider_scores[provider] = overall_score
        
        # Select provider with highest score
        best_provider = max(provider_scores, key=provider_scores.get)
        return best_provider

    async def _fetch_rate_from_provider(
        self,
        from_currency: str,
        to_currency: str,
        provider: ConversionProvider
    ) -> Optional[ExchangeRate]:
        """Fetch exchange rate from specific provider."""
        start_time = datetime.now()
        
        try:
            provider_config = self.provider_configs[provider]
            
            if provider == ConversionProvider.FIXER_IO:
                rate = await self._fetch_from_fixer_io(from_currency, to_currency, provider_config)
            elif provider == ConversionProvider.EXCHANGE_RATE_API:
                rate = await self._fetch_from_exchange_rate_api(from_currency, to_currency, provider_config)
            elif provider == ConversionProvider.OPEN_EXCHANGE_RATES:
                rate = await self._fetch_from_oxr(from_currency, to_currency, provider_config)
            elif provider == ConversionProvider.INTERNAL_BANK:
                rate = await self._fetch_from_internal_bank(from_currency, to_currency, provider_config)
            else:
                return None
            
            # Update provider metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_provider_metrics(provider, True, processing_time)
            
            return rate
            
        except Exception as e:
            # Update provider metrics for failure
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_provider_metrics(provider, False, processing_time, str(e))
            
            logger.error(f"Error fetching rate from {provider.value}: {e}")
            return None

    async def _fetch_from_fixer_io(
        self,
        from_currency: str,
        to_currency: str,
        config: Dict[str, Any]
    ) -> Optional[ExchangeRate]:
        """Fetch rate from Fixer.io API."""
        try:
            url = config['api_url']
            params = {
                'access_key': config['api_key'],
                'base': from_currency,
                'symbols': to_currency
            }
            
            # Simulate API call (in real implementation, use actual HTTP request)
            # response = requests.get(url, params=params, timeout=5)
            
            # Mock response for demonstration
            mock_rate = Decimal('1.0850')  # EUR to USD example
            
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=mock_rate,
                provider=ConversionProvider.FIXER_IO,
                timestamp=datetime.now(),
                valid_until=datetime.now() + self.cache_duration,
                source="fixer.io"
            )
            
        except Exception as e:
            logger.error(f"Error fetching from Fixer.io: {e}")
            return None

    async def _fetch_from_exchange_rate_api(
        self,
        from_currency: str,
        to_currency: str,
        config: Dict[str, Any]
    ) -> Optional[ExchangeRate]:
        """Fetch rate from ExchangeRate-API."""
        try:
            # Mock implementation
            mock_rate = Decimal('1.0845')
            
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=mock_rate,
                provider=ConversionProvider.EXCHANGE_RATE_API,
                timestamp=datetime.now(),
                valid_until=datetime.now() + self.cache_duration,
                source="exchangerate-api.com"
            )
            
        except Exception as e:
            logger.error(f"Error fetching from ExchangeRate-API: {e}")
            return None

    async def _fetch_from_oxr(
        self,
        from_currency: str,
        to_currency: str,
        config: Dict[str, Any]
    ) -> Optional[ExchangeRate]:
        """Fetch rate from Open Exchange Rates."""
        try:
            # Mock implementation
            mock_rate = Decimal('1.0855')
            
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=mock_rate,
                provider=ConversionProvider.OPEN_EXCHANGE_RATES,
                timestamp=datetime.now(),
                valid_until=datetime.now() + self.cache_duration,
                source="openexchangerates.org"
            )
            
        except Exception as e:
            logger.error(f"Error fetching from OXR: {e}")
            return None

    async def _fetch_from_internal_bank(
        self,
        from_currency: str,
        to_currency: str,
        config: Dict[str, Any]
    ) -> Optional[ExchangeRate]:
        """Fetch rate from internal banking API."""
        try:
            # Mock implementation - would integrate with bank's API
            mock_rate = Decimal('1.0840')
            
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=mock_rate,
                provider=ConversionProvider.INTERNAL_BANK,
                timestamp=datetime.now(),
                valid_until=datetime.now() + self.cache_duration,
                bid_rate=Decimal('1.0835'),
                ask_rate=Decimal('1.0845'),
                spread=Decimal('0.0010'),
                source="internal_bank"
            )
            
        except Exception as e:
            logger.error(f"Error fetching from internal bank: {e}")
            return None

    def _update_provider_metrics(
        self,
        provider -> None: ConversionProvider,
        success -> None: bool,
        processing_time -> None: float,
        error_message -> None: Optional[str] = None
    ) -> None:
        """Update performance metrics for a provider."""
        metrics = self.provider_metrics[provider]
        
        metrics['total_requests'] += 1
        
        if success:
            metrics['successful_requests'] += 1
        else:
            metrics['error_count'] += 1
            metrics['last_error'] = error_message
        
        # Update average response time
        current_avg = metrics['average_response_time']
        total_requests = metrics['total_requests']
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        metrics['average_response_time'] = new_avg
        
        # Update uptime percentage
        success_rate = metrics['successful_requests'] / metrics['total_requests']
        metrics['uptime_percentage'] = success_rate * 100

    async def convert_currency(
        self,
        request: ConversionRequest
    ) -> ConversionResult:
        """Perform currency conversion with monitoring."""
        start_time = datetime.now()
        
        try:
            # Get exchange rate
            exchange_rate = await self.get_exchange_rate(
                request.from_currency,
                request.to_currency
            )
            
            if not exchange_rate:
                return ConversionResult(
                    request_id=request.request_id,
                    from_currency=request.from_currency,
                    to_currency=request.to_currency,
                    from_amount=request.amount,
                    to_amount=Decimal('0'),
                    exchange_rate=Decimal('0'),
                    provider=ConversionProvider.FIXER_IO,  # Default
                    status=ConversionStatus.RATE_UNAVAILABLE,
                    processing_time_ms=0,
                    fees=Decimal('0'),
                    net_amount=Decimal('0'),
                    conversion_timestamp=datetime.now(),
                    error_message="Exchange rate unavailable"
                )
            
            # Calculate conversion
            converted_amount = request.amount * exchange_rate.rate
            
            # Calculate fees
            provider_config = self.provider_configs[exchange_rate.provider]
            fee_percentage = Decimal(str(provider_config['fee_percentage']))
            fees = converted_amount * fee_percentage
            net_amount = converted_amount - fees
            
            # Processing time
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            result = ConversionResult(
                request_id=request.request_id,
                from_currency=request.from_currency,
                to_currency=request.to_currency,
                from_amount=request.amount,
                to_amount=converted_amount,
                exchange_rate=exchange_rate.rate,
                provider=exchange_rate.provider,
                status=ConversionStatus.SUCCESS,
                processing_time_ms=processing_time_ms,
                fees=fees,
                net_amount=net_amount,
                conversion_timestamp=datetime.now()
            )
            
            # Store results
            self.conversion_results[request.request_id] = result
            self.conversion_history.append(result)
            
            # Update metrics
            self.metrics['total_conversions_monitored'] += 1
            self.metrics['total_volume_converted'] += converted_amount
            
            # Check performance thresholds
            await self._check_conversion_alerts(result)
            
            logger.info(f"Converted {request.amount} {request.from_currency} to {net_amount} {request.to_currency}")
            return result
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return ConversionResult(
                request_id=request.request_id,
                from_currency=request.from_currency,
                to_currency=request.to_currency,
                from_amount=request.amount,
                to_amount=Decimal('0'),
                exchange_rate=Decimal('0'),
                provider=ConversionProvider.FIXER_IO,
                status=ConversionStatus.FAILED,
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                fees=Decimal('0'),
                net_amount=Decimal('0'),
                conversion_timestamp=datetime.now(),
                error_message=str(e)
            )

    async def _check_rate_change_alerts(
        self,
        from_currency -> None: str,
        to_currency -> None: str,
        new_rate -> None: ExchangeRate
    ) -> None:
        """Check for significant rate changes and trigger alerts."""
        try:
            cache_key = f"{from_currency}_{to_currency}"
            
            if cache_key in self.exchange_rates:
                old_rate = self.exchange_rates[cache_key]
                
                # Calculate percentage change
                rate_change = abs(new_rate.rate - old_rate.rate) / old_rate.rate * 100
                
                if rate_change >= self.alert_thresholds['rate_change_percentage']:
                    await self._trigger_rate_alert(
                        from_currency,
                        to_currency,
                        old_rate.rate,
                        new_rate.rate,
                        rate_change
                    )
                    
        except Exception as e:
            logger.error(f"Error checking rate change alerts: {e}")

    async def _trigger_rate_alert(
        self,
        from_currency -> None: str,
        to_currency -> None: str,
        old_rate -> None: Decimal,
        new_rate -> None: Decimal,
        change_percentage -> None: float
    ) -> None:
        """Trigger alert for significant rate change."""
        alert = {
            'type': 'rate_change',
            'currency_pair': f"{from_currency}/{to_currency}",
            'old_rate': float(old_rate),
            'new_rate': float(new_rate),
            'change_percentage': change_percentage,
            'timestamp': datetime.now(),
            'severity': 'high' if change_percentage > 10 else 'medium'
        }
        
        self.metrics['rate_alerts_triggered'] += 1
        
        logger.warning(f"Rate change alert: {from_currency}/{to_currency} changed by {change_percentage:.2f}%")
        
        # Here you would typically send notifications
        # await self._send_alert_notification(alert)

    async def _check_conversion_alerts(self, result -> None: ConversionResult) -> None:
        """Check conversion result against alert thresholds."""
        try:
            # Check processing time
            if result.processing_time_ms > self.alert_thresholds['processing_time_maximum']:
                await self._trigger_performance_alert(
                    'slow_conversion',
                    f"Conversion took {result.processing_time_ms:.0f}ms (threshold: {self.alert_thresholds['processing_time_maximum']}ms)",
                    result.request_id
                )
            
            # Check fee percentage
            if result.to_amount > 0:
                fee_percentage = (result.fees / result.to_amount) * 100
                if fee_percentage > self.alert_thresholds['fee_percentage_maximum'] * 100:
                    await self._trigger_performance_alert(
                        'high_fees',
                        f"Conversion fees {fee_percentage:.2f}% exceed threshold {self.alert_thresholds['fee_percentage_maximum'] * 100:.2f}%",
                        result.request_id
                    )
                    
        except Exception as e:
            logger.error(f"Error checking conversion alerts: {e}")

    async def _trigger_performance_alert(self, alert_type -> None: str, message -> None: str, request_id -> None: str) -> None:
        """Trigger performance-related alert."""
        alert = {
            'type': alert_type,
            'message': message,
            'request_id': request_id,
            'timestamp': datetime.now(),
            'severity': 'medium'
        }
        
        logger.warning(f"Performance alert: {alert_type} - {message}")

    async def get_conversion_metrics(
        self,
        time_period: Optional[Tuple[datetime, datetime]] = None,
        currency_filter: Optional[List[str]] = None
    ) -> ConversionMetrics:
        """Get comprehensive conversion metrics."""
        try:
            # Determine time period
            if not time_period:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=7)  # Last 7 days
                time_period = (start_time, end_time)
            else:
                start_time, end_time = time_period
            
            # Filter conversions by time period
            period_conversions = [
                result for result in self.conversion_history
                if start_time <= result.conversion_timestamp <= end_time
            ]
            
            # Apply currency filter if specified
            if currency_filter:
                period_conversions = [
                    result for result in period_conversions
                    if result.from_currency in currency_filter or result.to_currency in currency_filter
                ]
            
            # Calculate basic metrics
            total_conversions = len(period_conversions)
            successful_conversions = len([r for r in period_conversions if r.status == ConversionStatus.SUCCESS])
            failed_conversions = total_conversions - successful_conversions
            success_rate = successful_conversions / total_conversions if total_conversions > 0 else 0.0
            
            # Calculate processing time
            processing_times = [r.processing_time_ms for r in period_conversions if r.processing_time_ms > 0]
            average_processing_time = np.mean(processing_times) if processing_times else 0.0
            
            # Calculate volume by currency
            volume_by_currency = defaultdict(Decimal)
            fees_by_currency = defaultdict(Decimal)
            
            for result in period_conversions:
                if result.status == ConversionStatus.SUCCESS:
                    volume_by_currency[result.to_currency] += result.to_amount
                    fees_by_currency[result.to_currency] += result.fees
            
            # Provider performance analysis
            provider_performance = self._analyze_provider_performance(period_conversions)
            
            # Currency pair performance
            currency_pair_performance = self._analyze_currency_pair_performance(period_conversions)
            
            # Calculate cost savings (compared to worst performing provider)
            cost_savings = self._calculate_cost_savings(period_conversions)
            
            # Calculate accuracy score
            accuracy_score = self._calculate_accuracy_score(period_conversions)
            
            metrics = ConversionMetrics(
                time_period=time_period,
                total_conversions=total_conversions,
                successful_conversions=successful_conversions,
                failed_conversions=failed_conversions,
                success_rate=success_rate,
                average_processing_time=average_processing_time,
                total_volume_converted=dict(volume_by_currency),
                total_fees_collected=dict(fees_by_currency),
                provider_performance=provider_performance,
                currency_pair_performance=currency_pair_performance,
                cost_savings=cost_savings,
                accuracy_score=accuracy_score
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting conversion metrics: {e}")
            raise

    def _analyze_provider_performance(self, conversions: List[ConversionResult]) -> Dict[ConversionProvider, Dict[str, Any]]:
        """Analyze performance by provider."""
        provider_stats = defaultdict(lambda: {
            'total_conversions': 0,
            'successful_conversions': 0,
            'total_fees': Decimal('0'),
            'total_processing_time': 0.0,
            'success_rate': 0.0,
            'average_processing_time': 0.0,
            'average_fee_percentage': 0.0
        })
        
        for result in conversions:
            stats = provider_stats[result.provider]
            stats['total_conversions'] += 1
            stats['total_processing_time'] += result.processing_time_ms
            
            if result.status == ConversionStatus.SUCCESS:
                stats['successful_conversions'] += 1
                stats['total_fees'] += result.fees
        
        # Calculate derived metrics
        for provider, stats in provider_stats.items():
            if stats['total_conversions'] > 0:
                stats['success_rate'] = stats['successful_conversions'] / stats['total_conversions']
                stats['average_processing_time'] = stats['total_processing_time'] / stats['total_conversions']
                
                if stats['successful_conversions'] > 0:
                    # Calculate average fee percentage
                    successful_results = [r for r in conversions if r.provider == provider and r.status == ConversionStatus.SUCCESS]
                    fee_percentages = [(r.fees / r.to_amount * 100) for r in successful_results if r.to_amount > 0]
                    stats['average_fee_percentage'] = float(np.mean(fee_percentages)) if fee_percentages else 0.0
        
        return dict(provider_stats)

    def _analyze_currency_pair_performance(self, conversions: List[ConversionResult]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by currency pair."""
        pair_stats = defaultdict(lambda: {
            'total_conversions': 0,
            'successful_conversions': 0,
            'total_volume': Decimal('0'),
            'average_rate': Decimal('0'),
            'rate_volatility': 0.0
        })
        
        for result in conversions:
            pair_key = f"{result.from_currency}/{result.to_currency}"
            stats = pair_stats[pair_key]
            stats['total_conversions'] += 1
            
            if result.status == ConversionStatus.SUCCESS:
                stats['successful_conversions'] += 1
                stats['total_volume'] += result.to_amount
        
        return dict(pair_stats)

    def _calculate_cost_savings(self, conversions: List[ConversionResult]) -> Decimal:
        """Calculate cost savings from optimal provider selection."""
        try:
            total_savings = Decimal('0')
            
            # Group conversions by currency pair
            pair_conversions = defaultdict(list)
            for result in conversions:
                if result.status == ConversionStatus.SUCCESS:
                    pair_key = f"{result.from_currency}/{result.to_currency}"
                    pair_conversions[pair_key].append(result)
            
            # Calculate savings for each pair
            for pair, results in pair_conversions.items():
                if len(results) > 1:
                    # Find the provider with highest and lowest fees
                    fee_percentages = [(r.fees / r.to_amount) for r in results if r.to_amount > 0]
                    if fee_percentages:
                        max_fee_pct = max(fee_percentages)
                        min_fee_pct = min(fee_percentages)
                        
                        # Calculate potential savings
                        total_volume = sum(r.to_amount for r in results)
                        savings = total_volume * (max_fee_pct - min_fee_pct)
                        total_savings += savings
            
            return total_savings
            
        except Exception as e:
            logger.error(f"Error calculating cost savings: {e}")
            return Decimal('0')

    def _calculate_accuracy_score(self, conversions: List[ConversionResult]) -> float:
        """Calculate conversion accuracy score."""
        try:
            if not conversions:
                return 0.0
            
            # Calculate accuracy based on provider consensus
            successful_conversions = [r for r in conversions if r.status == ConversionStatus.SUCCESS]
            
            if len(successful_conversions) < 2:
                return 1.0  # Perfect score if only one conversion
            
            # Group by currency pair and time window
            pair_groups = defaultdict(list)
            
            for result in successful_conversions:
                pair_key = f"{result.from_currency}/{result.to_currency}"
                time_window = result.conversion_timestamp.replace(minute=0, second=0, microsecond=0)
                group_key = f"{pair_key}_{time_window}"
                pair_groups[group_key].append(result)
            
            accuracy_scores = []
            
            # Calculate accuracy for each group
            for group_results in pair_groups.values():
                if len(group_results) > 1:
                    rates = [float(r.exchange_rate) for r in group_results]
                    mean_rate = np.mean(rates)
                    std_rate = np.std(rates)
                    
                    # Accuracy is inverse of coefficient of variation
                    if mean_rate > 0:
                        cv = std_rate / mean_rate
                        accuracy = max(0, 1 - cv)
                        accuracy_scores.append(accuracy)
            
            return np.mean(accuracy_scores) if accuracy_scores else 1.0
            
        except Exception as e:
            logger.error(f"Error calculating accuracy score: {e}")
            return 0.0

    async def optimize_provider_selection(self) -> None:
        """Optimize provider selection based on performance metrics."""
        try:
            # Analyze provider performance
            recent_conversions = list(self.conversion_history)[-1000:]  # Last 1000 conversions
            provider_performance = self._analyze_provider_performance(recent_conversions)
            
            # Update provider rankings
            for provider, performance in provider_performance.items():
                metrics = self.provider_metrics[provider]
                metrics['rate_accuracy'] = performance.get('success_rate', 0.0)
                
                # Check if provider should be temporarily disabled
                if performance['success_rate'] < self.alert_thresholds['success_rate_minimum']:
                    logger.warning(f"Provider {provider.value} success rate below threshold: {performance['success_rate']:.3f}")
                    
        except Exception as e:
            logger.error(f"Error optimizing provider selection: {e}")

    async def get_monitor_metrics(self) -> Dict[str, Any]:
        """Get currency conversion monitor metrics."""
        try:
            return {
                'total_conversions_monitored': self.metrics['total_conversions_monitored'],
                'total_volume_converted': float(self.metrics['total_volume_converted']),
                'total_fees_saved': float(self.metrics['total_fees_saved']),
                'average_conversion_accuracy': self.metrics['average_conversion_accuracy'],
                'provider_switches': self.metrics['provider_switches'],
                'rate_alerts_triggered': self.metrics['rate_alerts_triggered'],
                'active_providers': len([p for p, m in self.provider_metrics.items() if m['total_requests'] > 0]),
                'cached_rates': len(self.rate_cache),
                'conversion_history_size': len(self.conversion_history),
                'provider_performance': {
                    provider.value: {
                        'success_rate': metrics['successful_requests'] / max(metrics['total_requests'], 1),
                        'average_response_time': metrics['average_response_time'],
                        'uptime_percentage': metrics['uptime_percentage']
                    }
                    for provider, metrics in self.provider_metrics.items()
                    if metrics['total_requests'] > 0
                },
                'alert_thresholds': self.alert_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error getting monitor metrics: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    async def test_currency_monitor() -> None:
        """Test currency conversion monitor."""
        monitor = CurrencyConversionMonitor()
        
        try:
            # Test getting exchange rate
            rate = await monitor.get_exchange_rate("EUR", "USD")
            if rate:
                print(f"Exchange rate EUR/USD: {rate.rate}")
            
            # Test currency conversion
            request = ConversionRequest(
                request_id=str(uuid.uuid4()),
                from_currency="EUR",
                to_currency="USD",
                amount=Decimal('1000.00'),
                priority=ConversionPriority.NORMAL,
                partnership_id="partnership_001",
                creator_id="creator_001",
                transaction_id="txn_001",
                request_timestamp=datetime.now()
            )
            
            result = await monitor.convert_currency(request)
            print(f"Conversion result: {result.from_amount} {result.from_currency} -> {result.net_amount} {result.to_currency}")
            print(f"Exchange rate: {result.exchange_rate}, Fees: {result.fees}")
            
            # Test metrics
            metrics = await monitor.get_conversion_metrics()
            print(f"Conversion metrics: {metrics.total_conversions} conversions, {metrics.success_rate:.3f} success rate")
            
            # Test monitor metrics
            monitor_metrics = await monitor.get_monitor_metrics()
            print(f"Monitor metrics: {monitor_metrics}")
            
        except Exception as e:
            print(f"Error in test: {e}")
    
    # Run test
    asyncio.run(test_currency_monitor())