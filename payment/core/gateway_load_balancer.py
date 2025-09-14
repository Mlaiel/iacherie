"""⚖️ Gateway Load Balancer
==========================

Enterprise load balancer for payment gateway traffic distribution.
Handles provider selection, geographic routing, capacity management,
and performance-based load distribution.

Features:
- Traffic distribution across providers
- Geographic routing optimization
- Provider capacity management
- Performance-based load distribution
- Health-based routing decisions
- Real-time load monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
import hashlib
import random
import numpy as np
from collections import defaultdict, deque
import aioredis
try:
    import geoip2.database
    import geoip2.errors
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    geoip2 = None

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    GEOGRAPHIC = "geographic"
    PERFORMANCE_BASED = "performance_based"
    COST_OPTIMIZED = "cost_optimized"
    INTELLIGENT = "intelligent"


class ProviderStatus(Enum):
    """Provider status for load balancing"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    OVERLOADED = "overloaded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


class TrafficType(Enum):
    """Types of traffic for routing decisions"""
    HIGH_VALUE = "high_value"
    STANDARD = "standard"
    BULK = "bulk"
    REAL_TIME = "real_time"
    CRYPTO = "crypto"
    INTERNATIONAL = "international"


@dataclass
class ProviderCapacity:
    """Provider capacity information"""
    provider_id: str
    max_transactions_per_second: int
    current_load: int
    response_time_avg: float
    success_rate: float
    cost_per_transaction: Decimal
    geographic_regions: List[str]
    supported_currencies: List[str]
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class LoadBalancingRule:
    """Load balancing rule configuration"""
    rule_id: str
    name: str
    strategy: LoadBalancingStrategy
    conditions: Dict[str, Any]
    provider_weights: Dict[str, float]
    priority: int
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingDecision:
    """Routing decision result"""
    transaction_id: str
    selected_provider: str
    strategy_used: LoadBalancingStrategy
    routing_reason: str
    confidence_score: float
    alternative_providers: List[str]
    decision_time: datetime = field(default_factory=datetime.now)


@dataclass
class TrafficMetrics:
    """Traffic metrics for monitoring"""
    provider_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    current_load: float
    timestamp: datetime = field(default_factory=datetime.now)


class GatewayLoadBalancer:
    """Enterprise load balancer for payment gateway"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.redis_client = None
        self.providers: Dict[str, ProviderCapacity] = {}
        self.routing_rules: Dict[str, LoadBalancingRule] = {}
        self.traffic_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.routing_history: deque = deque(maxlen=10000)
        self.round_robin_counter = 0
        self.is_initialized = False
        
        # Load balancing configuration
        self.default_strategy = LoadBalancingStrategy(
            config.get('default_strategy', 'intelligent')
        )
        self.health_check_interval = config.get('health_check_interval', 60)
        self.metrics_collection_interval = config.get('metrics_collection_interval', 30)
        
        # Geographic routing (requires GeoLite2 database)
        self.geoip_db_path = config.get('geoip_db_path', './GeoLite2-City.mmdb')
        self.geoip_reader = None
        
        # Performance thresholds
        self.performance_thresholds = config.get('performance_thresholds', {
            'max_response_time': 3000,  # milliseconds
            'min_success_rate': 95.0,   # percentage
            'max_load_percentage': 80.0  # percentage
        })
        
    async def initialize(self) -> None:
        """Initialize the load balancer"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = aioredis.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}"
            )
            
            # Initialize GeoIP database
            if GEOIP_AVAILABLE:
                try:
                    self.geoip_reader = geoip2.database.Reader(self.geoip_db_path)
                    logger.info("GeoIP database loaded successfully")
                except Exception as e:
                    logger.warning(f"GeoIP database not available: {e}")
            else:
                logger.warning("GeoIP2 library not available - geographic routing disabled")
            
            # Load existing configuration
            await self._load_configuration()
            
            # Initialize default providers
            await self._initialize_default_providers()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_provider_health())
            asyncio.create_task(self._collect_traffic_metrics())
            
            self.is_initialized = True
            logger.info("Gateway Load Balancer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gateway Load Balancer: {e}")
            raise
    
    async def _load_configuration(self) -> None:
        """Load existing configuration from storage"""
        try:
            # Load providers
            providers_data = await self.redis_client.get("loadbalancer:providers")
            if providers_data:
                providers_dict = json.loads(providers_data.decode())
                for provider_id, provider_info in providers_dict.items():
                    self.providers[provider_id] = ProviderCapacity(
                        provider_id=provider_info['provider_id'],
                        max_transactions_per_second=provider_info['max_transactions_per_second'],
                        current_load=provider_info['current_load'],
                        response_time_avg=provider_info['response_time_avg'],
                        success_rate=provider_info['success_rate'],
                        cost_per_transaction=Decimal(str(provider_info['cost_per_transaction'])),
                        geographic_regions=provider_info['geographic_regions'],
                        supported_currencies=provider_info['supported_currencies'],
                        last_updated=datetime.fromisoformat(provider_info['last_updated'])
                    )
            
            # Load routing rules
            rules_data = await self.redis_client.get("loadbalancer:rules")
            if rules_data:
                rules_dict = json.loads(rules_data.decode())
                for rule_id, rule_info in rules_dict.items():
                    self.routing_rules[rule_id] = LoadBalancingRule(
                        rule_id=rule_info['rule_id'],
                        name=rule_info['name'],
                        strategy=LoadBalancingStrategy(rule_info['strategy']),
                        conditions=rule_info['conditions'],
                        provider_weights=rule_info['provider_weights'],
                        priority=rule_info['priority'],
                        is_active=rule_info['is_active'],
                        created_at=datetime.fromisoformat(rule_info['created_at'])
                    )
                    
            logger.info("Load balancer configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def _initialize_default_providers(self) -> None:
        """Initialize default provider configurations"""
        try:
            default_providers = [
                {
                    "provider_id": "stripe",
                    "max_transactions_per_second": 1000,
                    "response_time_avg": 450.0,
                    "success_rate": 98.5,
                    "cost_per_transaction": "0.029",
                    "geographic_regions": ["US", "EU", "CA", "AU"],
                    "supported_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"]
                },
                {
                    "provider_id": "paypal",
                    "max_transactions_per_second": 800,
                    "response_time_avg": 680.0,
                    "success_rate": 97.8,
                    "cost_per_transaction": "0.034",
                    "geographic_regions": ["US", "EU", "GLOBAL"],
                    "supported_currencies": ["USD", "EUR", "GBP", "JPY", "CAD"]
                },
                {
                    "provider_id": "wise",
                    "max_transactions_per_second": 500,
                    "response_time_avg": 320.0,
                    "success_rate": 99.1,
                    "cost_per_transaction": "0.015",
                    "geographic_regions": ["EU", "UK", "GLOBAL"],
                    "supported_currencies": ["USD", "EUR", "GBP", "CHF", "JPY"]
                },
                {
                    "provider_id": "crypto",
                    "max_transactions_per_second": 200,
                    "response_time_avg": 1200.0,
                    "success_rate": 96.2,
                    "cost_per_transaction": "0.008",
                    "geographic_regions": ["GLOBAL"],
                    "supported_currencies": ["BTC", "ETH", "USDC", "USDT"]
                }
            ]
            
            for provider_config in default_providers:
                if provider_config["provider_id"] not in self.providers:
                    self.providers[provider_config["provider_id"]] = ProviderCapacity(
                        provider_id=provider_config["provider_id"],
                        max_transactions_per_second=provider_config["max_transactions_per_second"],
                        current_load=0,
                        response_time_avg=provider_config["response_time_avg"],
                        success_rate=provider_config["success_rate"],
                        cost_per_transaction=Decimal(provider_config["cost_per_transaction"]),
                        geographic_regions=provider_config["geographic_regions"],
                        supported_currencies=provider_config["supported_currencies"]
                    )
            
            await self._save_providers()
            
        except Exception as e:
            logger.error(f"Failed to initialize default providers: {e}")
    
    async def route_transaction(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        client_ip: Optional[str] = None,
        traffic_type: TrafficType = TrafficType.STANDARD,
        preferred_providers: Optional[List[str]] = None
    ) -> RoutingDecision:
        """Route a transaction to the best available provider"""
        try:
            # Determine geographic region from IP
            geographic_region = await self._get_geographic_region(client_ip)
            
            # Get available providers
            available_providers = await self._get_available_providers(
                currency, geographic_region, traffic_type
            )
            
            if not available_providers:
                raise ValueError("No available providers for this transaction")
            
            # Apply routing rules
            selected_provider, strategy, reason, confidence = await self._apply_routing_logic(
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                geographic_region=geographic_region,
                traffic_type=traffic_type,
                available_providers=available_providers,
                preferred_providers=preferred_providers
            )
            
            # Create routing decision
            decision = RoutingDecision(
                transaction_id=transaction_id,
                selected_provider=selected_provider,
                strategy_used=strategy,
                routing_reason=reason,
                confidence_score=confidence,
                alternative_providers=[p for p in available_providers if p != selected_provider]
            )
            
            # Record routing decision
            self.routing_history.append(decision)
            await self._update_provider_load(selected_provider, 1)
            
            logger.info(f"Transaction {transaction_id} routed to {selected_provider} "
                       f"using {strategy.value} strategy")
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to route transaction {transaction_id}: {e}")
            raise
    
    async def _get_geographic_region(self, client_ip: Optional[str]) -> Optional[str]:
        """Get geographic region from client IP"""
        try:
            if not client_ip or not self.geoip_reader:
                return None
                
            response = self.geoip_reader.city(client_ip)
            country_code = response.country.iso_code
            
            # Map country codes to regions
            region_mapping = {
                'US': 'US',
                'CA': 'CA',
                'GB': 'UK',
                'DE': 'EU', 'FR': 'EU', 'IT': 'EU', 'ES': 'EU', 'NL': 'EU',
                'AU': 'AU', 'NZ': 'AU',
                'JP': 'APAC', 'SG': 'APAC', 'HK': 'APAC'
            }
            
            return region_mapping.get(country_code, 'GLOBAL')
            
        except (geoip2.errors.AddressNotFoundError, Exception) as e:
            logger.debug(f"Could not determine geographic region for IP {client_ip}: {e}")
            return None
    
    async def _get_available_providers(
        self,
        currency: str,
        geographic_region: Optional[str],
        traffic_type: TrafficType
    ) -> List[str]:
        """Get list of available providers for the given criteria"""
        try:
            available_providers = []
            
            for provider_id, provider in self.providers.items():
                # Check currency support
                if currency not in provider.supported_currencies:
                    continue
                
                # Check geographic support
                if geographic_region and geographic_region not in provider.geographic_regions:
                    if 'GLOBAL' not in provider.geographic_regions:
                        continue
                
                # Check provider health
                if await self._is_provider_healthy(provider_id):
                    available_providers.append(provider_id)
            
            return available_providers
            
        except Exception as e:
            logger.error(f"Failed to get available providers: {e}")
            return []
    
    async def _apply_routing_logic(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        geographic_region: Optional[str],
        traffic_type: TrafficType,
        available_providers: List[str],
        preferred_providers: Optional[List[str]]
    ) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Apply routing logic to select the best provider"""
        try:
            # Check for applicable routing rules
            applicable_rule = await self._find_applicable_rule(
                amount, currency, geographic_region, traffic_type
            )
            
            if applicable_rule:
                strategy = applicable_rule.strategy
            else:
                strategy = self.default_strategy
            
            # Apply the selected strategy
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return await self._route_round_robin(available_providers)
                
            elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                weights = applicable_rule.provider_weights if applicable_rule else {}
                return await self._route_weighted_round_robin(available_providers, weights)
                
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return await self._route_least_connections(available_providers)
                
            elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return await self._route_least_response_time(available_providers)
                
            elif strategy == LoadBalancingStrategy.GEOGRAPHIC:
                return await self._route_geographic(available_providers, geographic_region)
                
            elif strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
                return await self._route_performance_based(available_providers)
                
            elif strategy == LoadBalancingStrategy.COST_OPTIMIZED:
                return await self._route_cost_optimized(available_providers, amount)
                
            elif strategy == LoadBalancingStrategy.INTELLIGENT:
                return await self._route_intelligent(
                    available_providers, amount, currency, geographic_region, traffic_type
                )
            
            else:
                # Default to round robin
                return await self._route_round_robin(available_providers)
                
        except Exception as e:
            logger.error(f"Failed to apply routing logic: {e}")
            # Fallback to first available provider
            return available_providers[0], LoadBalancingStrategy.ROUND_ROBIN, "Fallback", 0.5
    
    async def _route_round_robin(self, providers: List[str]) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Round robin routing"""
        selected = providers[self.round_robin_counter % len(providers)]
        self.round_robin_counter += 1
        return selected, LoadBalancingStrategy.ROUND_ROBIN, "Round robin selection", 1.0
    
    async def _route_weighted_round_robin(
        self, 
        providers: List[str], 
        weights: Dict[str, float]
    ) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Weighted round robin routing"""
        # Calculate weighted selection
        total_weight = sum(weights.get(p, 1.0) for p in providers)
        random_value = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for provider in providers:
            cumulative_weight += weights.get(provider, 1.0)
            if random_value <= cumulative_weight:
                return provider, LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN, \
                       f"Weighted selection (weight: {weights.get(provider, 1.0)})", 0.9
        
        # Fallback to first provider
        return providers[0], LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN, "Fallback weighted", 0.5
    
    async def _route_least_connections(self, providers: List[str]) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Route to provider with least current load"""
        min_load = float('inf')
        selected_provider = providers[0]
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            if provider.current_load < min_load:
                min_load = provider.current_load
                selected_provider = provider_id
        
        return selected_provider, LoadBalancingStrategy.LEAST_CONNECTIONS, \
               f"Least connections (load: {min_load})", 0.9
    
    async def _route_least_response_time(self, providers: List[str]) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Route to provider with best response time"""
        min_response_time = float('inf')
        selected_provider = providers[0]
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            if provider.response_time_avg < min_response_time:
                min_response_time = provider.response_time_avg
                selected_provider = provider_id
        
        return selected_provider, LoadBalancingStrategy.LEAST_RESPONSE_TIME, \
               f"Best response time ({min_response_time:.0f}ms)", 0.9
    
    async def _route_geographic(
        self, 
        providers: List[str], 
        geographic_region: Optional[str]
    ) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Route based on geographic preference"""
        if not geographic_region:
            return await self._route_round_robin(providers)
        
        # Prefer providers with specific regional support
        regional_providers = []
        global_providers = []
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            if geographic_region in provider.geographic_regions:
                regional_providers.append(provider_id)
            elif 'GLOBAL' in provider.geographic_regions:
                global_providers.append(provider_id)
        
        if regional_providers:
            selected = random.choice(regional_providers)
            return selected, LoadBalancingStrategy.GEOGRAPHIC, \
                   f"Regional preference ({geographic_region})", 0.95
        elif global_providers:
            selected = random.choice(global_providers)
            return selected, LoadBalancingStrategy.GEOGRAPHIC, \
                   f"Global provider for {geographic_region}", 0.7
        else:
            return await self._route_round_robin(providers)
    
    async def _route_performance_based(self, providers: List[str]) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Route based on overall performance score"""
        best_score = -1
        selected_provider = providers[0]
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            
            # Calculate performance score (higher is better)
            # Factors: success rate, response time, current load
            success_score = provider.success_rate / 100.0
            response_score = 1.0 - min(provider.response_time_avg / 5000.0, 1.0)  # Normalize to 5s max
            load_score = 1.0 - min(provider.current_load / provider.max_transactions_per_second, 1.0)
            
            overall_score = (success_score * 0.4) + (response_score * 0.3) + (load_score * 0.3)
            
            if overall_score > best_score:
                best_score = overall_score
                selected_provider = provider_id
        
        return selected_provider, LoadBalancingStrategy.PERFORMANCE_BASED, \
               f"Best performance score ({best_score:.3f})", 0.95
    
    async def _route_cost_optimized(
        self, 
        providers: List[str], 
        amount: Decimal
    ) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Route based on cost optimization"""
        min_cost = Decimal('inf')
        selected_provider = providers[0]
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            transaction_cost = provider.cost_per_transaction * amount
            
            if transaction_cost < min_cost:
                min_cost = transaction_cost
                selected_provider = provider_id
        
        return selected_provider, LoadBalancingStrategy.COST_OPTIMIZED, \
               f"Lowest cost (${min_cost:.4f})", 0.9
    
    async def _route_intelligent(
        self,
        providers: List[str],
        amount: Decimal,
        currency: str,
        geographic_region: Optional[str],
        traffic_type: TrafficType
    ) -> Tuple[str, LoadBalancingStrategy, str, float]:
        """Intelligent routing using ML-like scoring"""
        best_score = -1
        selected_provider = providers[0]
        scoring_details = []
        
        for provider_id in providers:
            provider = self.providers[provider_id]
            
            # Multi-factor scoring algorithm
            scores = {}
            
            # Performance factors (40% weight)
            scores['success_rate'] = (provider.success_rate / 100.0) * 0.20
            scores['response_time'] = (1.0 - min(provider.response_time_avg / 3000.0, 1.0)) * 0.20
            
            # Load factors (25% weight)
            load_ratio = provider.current_load / provider.max_transactions_per_second
            scores['load'] = (1.0 - min(load_ratio, 1.0)) * 0.25
            
            # Cost factors (20% weight)
            # Normalize cost (assuming max cost per transaction is $0.10)
            cost_score = 1.0 - min(float(provider.cost_per_transaction) / 0.10, 1.0)
            scores['cost'] = cost_score * 0.20
            
            # Geographic factors (10% weight)
            if geographic_region in provider.geographic_regions:
                scores['geographic'] = 0.10
            elif 'GLOBAL' in provider.geographic_regions:
                scores['geographic'] = 0.05
            else:
                scores['geographic'] = 0.0
            
            # Traffic type factors (5% weight)
            traffic_multiplier = {
                TrafficType.HIGH_VALUE: 1.2 if provider.success_rate > 98.0 else 0.8,
                TrafficType.REAL_TIME: 1.2 if provider.response_time_avg < 500 else 0.8,
                TrafficType.BULK: 1.2 if load_ratio < 0.7 else 0.8,
                TrafficType.CRYPTO: 1.3 if provider_id == 'crypto' else 0.9,
                TrafficType.INTERNATIONAL: 1.2 if 'GLOBAL' in provider.geographic_regions else 0.9,
                TrafficType.STANDARD: 1.0
            }
            scores['traffic_type'] = 0.05 * traffic_multiplier.get(traffic_type, 1.0)
            
            # Calculate total score
            total_score = sum(scores.values())
            scoring_details.append({
                'provider': provider_id,
                'total_score': total_score,
                'scores': scores
            })
            
            if total_score > best_score:
                best_score = total_score
                selected_provider = provider_id
        
        # Log scoring details for debugging
        logger.debug(f"Intelligent routing scores: {scoring_details}")
        
        return selected_provider, LoadBalancingStrategy.INTELLIGENT, \
               f"Intelligent routing (score: {best_score:.3f})", 0.98
    
    async def _find_applicable_rule(
        self,
        amount: Decimal,
        currency: str,
        geographic_region: Optional[str],
        traffic_type: TrafficType
    ) -> Optional[LoadBalancingRule]:
        """Find applicable routing rule for the transaction"""
        try:
            applicable_rules = []
            
            for rule in self.routing_rules.values():
                if not rule.is_active:
                    continue
                
                conditions = rule.conditions
                matches = True
                
                # Check amount conditions
                if 'min_amount' in conditions and amount < Decimal(str(conditions['min_amount'])):
                    matches = False
                if 'max_amount' in conditions and amount > Decimal(str(conditions['max_amount'])):
                    matches = False
                
                # Check currency conditions
                if 'currencies' in conditions and currency not in conditions['currencies']:
                    matches = False
                
                # Check geographic conditions
                if 'regions' in conditions and geographic_region not in conditions['regions']:
                    matches = False
                
                # Check traffic type conditions
                if 'traffic_types' in conditions and traffic_type.value not in conditions['traffic_types']:
                    matches = False
                
                if matches:
                    applicable_rules.append(rule)
            
            # Return highest priority rule
            if applicable_rules:
                return max(applicable_rules, key=lambda r: r.priority)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find applicable rule: {e}")
            return None
    
    async def _is_provider_healthy(self, provider_id: str) -> bool:
        """Check if provider is healthy for routing"""
        try:
            if provider_id not in self.providers:
                return False
            
            provider = self.providers[provider_id]
            
            # Check performance thresholds
            if provider.response_time_avg > self.performance_thresholds['max_response_time']:
                return False
            
            if provider.success_rate < self.performance_thresholds['min_success_rate']:
                return False
            
            # Check load
            load_percentage = (provider.current_load / provider.max_transactions_per_second) * 100
            if load_percentage > self.performance_thresholds['max_load_percentage']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check provider health for {provider_id}: {e}")
            return False
    
    async def _monitor_provider_health(self) -> None:
        """Monitor provider health continuously"""
        while True:
            try:
                for provider_id in self.providers:
                    # Simulate health checks (in real implementation, ping actual endpoints)
                    await self._perform_health_check(provider_id)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in provider health monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self, provider_id -> None: str) -> None:
        """Perform health check for a specific provider"""
        try:
            # Simulate health check (in real implementation, make actual API calls)
            provider = self.providers[provider_id]
            
            # Simulate some variation in metrics
            provider.response_time_avg += random.uniform(-50, 50)
            provider.response_time_avg = max(100, provider.response_time_avg)  # Minimum 100ms
            
            provider.success_rate += random.uniform(-0.5, 0.5)
            provider.success_rate = max(90.0, min(99.9, provider.success_rate))
            
            provider.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to perform health check for {provider_id}: {e}")
    
    async def _collect_traffic_metrics(self) -> None:
        """Collect traffic metrics continuously"""
        while True:
            try:
                for provider_id in self.providers:
                    await self._collect_provider_metrics(provider_id)
                
                await asyncio.sleep(self.metrics_collection_interval)
                
            except Exception as e:
                logger.error(f"Error in traffic metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def _collect_provider_metrics(self, provider_id -> None: str) -> None:
        """Collect metrics for a specific provider"""
        try:
            provider = self.providers[provider_id]
            
            # Create metrics entry
            metrics = TrafficMetrics(
                provider_id=provider_id,
                total_requests=provider.current_load,
                successful_requests=int(provider.current_load * (provider.success_rate / 100)),
                failed_requests=int(provider.current_load * ((100 - provider.success_rate) / 100)),
                average_response_time=provider.response_time_avg,
                current_load=float(provider.current_load) / provider.max_transactions_per_second
            )
            
            # Store metrics
            self.traffic_metrics[provider_id].append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect metrics for {provider_id}: {e}")
    
    async def _update_provider_load(self, provider_id -> None: str, load_change -> None: int) -> None:
        """Update provider current load"""
        try:
            if provider_id in self.providers:
                self.providers[provider_id].current_load += load_change
                self.providers[provider_id].current_load = max(0, self.providers[provider_id].current_load)
                
        except Exception as e:
            logger.error(f"Failed to update provider load for {provider_id}: {e}")
    
    async def add_routing_rule(self, rule: LoadBalancingRule) -> bool:
        """Add a new routing rule"""
        try:
            self.routing_rules[rule.rule_id] = rule
            await self._save_routing_rules()
            
            logger.info(f"Added routing rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add routing rule: {e}")
            return False
    
    async def update_provider_capacity(self, provider_id: str, capacity: ProviderCapacity) -> bool:
        """Update provider capacity information"""
        try:
            self.providers[provider_id] = capacity
            await self._save_providers()
            
            logger.info(f"Updated provider capacity: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update provider capacity: {e}")
            return False
    
    async def get_load_balancer_status(self) -> Dict[str, Any]:
        """Get load balancer status and metrics"""
        try:
            # Calculate aggregate metrics
            total_capacity = sum(p.max_transactions_per_second for p in self.providers.values())
            total_current_load = sum(p.current_load for p in self.providers.values())
            average_success_rate = np.mean([p.success_rate for p in self.providers.values()])
            average_response_time = np.mean([p.response_time_avg for p in self.providers.values()])
            
            # Recent routing decisions
            recent_decisions = [
                {
                    'transaction_id': d.transaction_id,
                    'provider': d.selected_provider,
                    'strategy': d.strategy_used.value,
                    'confidence': d.confidence_score,
                    'timestamp': d.decision_time.isoformat()
                }
                for d in list(self.routing_history)[-10:]  # Last 10 decisions
            ]
            
            return {
                'is_initialized': self.is_initialized,
                'total_providers': len(self.providers),
                'healthy_providers': len([p for p in self.providers if await self._is_provider_healthy(p)]),
                'total_capacity': total_capacity,
                'current_load': total_current_load,
                'load_percentage': (total_current_load / total_capacity * 100) if total_capacity > 0 else 0,
                'average_success_rate': average_success_rate,
                'average_response_time': average_response_time,
                'active_rules': len([r for r in self.routing_rules.values() if r.is_active]),
                'recent_decisions': recent_decisions,
                'default_strategy': self.default_strategy.value,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get load balancer status: {e}")
            return {'error': str(e)}
    
    async def _save_providers(self) -> None:
        """Save providers configuration to storage"""
        try:
            providers_dict = {}
            for provider_id, provider in self.providers.items():
                providers_dict[provider_id] = {
                    'provider_id': provider.provider_id,
                    'max_transactions_per_second': provider.max_transactions_per_second,
                    'current_load': provider.current_load,
                    'response_time_avg': provider.response_time_avg,
                    'success_rate': provider.success_rate,
                    'cost_per_transaction': str(provider.cost_per_transaction),
                    'geographic_regions': provider.geographic_regions,
                    'supported_currencies': provider.supported_currencies,
                    'last_updated': provider.last_updated.isoformat()
                }
            
            await self.redis_client.set(
                "loadbalancer:providers",
                json.dumps(providers_dict),
                ex=86400  # 1 day expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save providers: {e}")
    
    async def _save_routing_rules(self) -> None:
        """Save routing rules to storage"""
        try:
            rules_dict = {}
            for rule_id, rule in self.routing_rules.items():
                rules_dict[rule_id] = {
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'strategy': rule.strategy.value,
                    'conditions': rule.conditions,
                    'provider_weights': rule.provider_weights,
                    'priority': rule.priority,
                    'is_active': rule.is_active,
                    'created_at': rule.created_at.isoformat()
                }
            
            await self.redis_client.set(
                "loadbalancer:rules",
                json.dumps(rules_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save routing rules: {e}")
    
    async def close(self) -> None:
        """Close the load balancer and cleanup resources"""
        try:
            if self.geoip_reader:
                self.geoip_reader.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Gateway Load Balancer closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Gateway Load Balancer: {e}")