"""Oracle Connector Contract - IA-Influencer-Agent Platform

This module provides oracle connectivity for external data feeds including
price data, market information, content verification, and cross-chain data
integration with multiple oracle providers.

Features:
- Multi-oracle data aggregation
- Price feed integration
- Content verification oracles
- Cross-chain data feeds
- Data quality validation
- Oracle reputation management

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class OracleType(Enum):
    """Types of oracle data sources"""
    PRICE_FEED = "price_feed"
    CONTENT_VERIFICATION = "content_verification"
    MARKET_DATA = "market_data"
    WEATHER = "weather"
    RANDOM_NUMBER = "random_number"
    CROSS_CHAIN = "cross_chain"
    API_DATA = "api_data"


class DataStatus(Enum):
    """Oracle data status"""
    FRESH = "fresh"
    STALE = "stale"
    INVALID = "invalid"
    PENDING = "pending"


@dataclass
class OracleDataPoint:
    """Single oracle data point"""
    data_id: str
    oracle_id: str
    data_type: OracleType
    value: Any
    confidence: Decimal
    timestamp: datetime
    status: DataStatus
    metadata: Dict[str, Any]


@dataclass
class OracleProvider:
    """Oracle provider configuration"""
    provider_id: str
    name: str
    endpoint_url: str
    api_key: Optional[str]
    supported_types: List[OracleType]
    reputation_score: Decimal
    response_time_ms: int
    reliability_percentage: Decimal
    is_active: bool


class OracleConnector:
    """
    Oracle Connector for external data integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Oracle Connector"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.oracle_providers: Dict[str, OracleProvider] = {}
        self.data_cache: Dict[str, OracleDataPoint] = {}
        self.aggregated_data: Dict[str, Dict[str, Any]] = {}
        
        # System settings
        self.cache_ttl_seconds = config.get("cache_ttl", 300)  # 5 minutes
        self.min_oracle_consensus = config.get("min_consensus", 3)
        self.max_price_deviation = Decimal(config.get("max_deviation", "5.0"))  # 5%
        
        # Initialize oracle providers
        self._init_oracle_providers()
    
    def _init_oracle_providers(self):
        """Initialize oracle provider registry"""
        providers = [
            OracleProvider(
                provider_id="chainlink_mainnet",
                name="Chainlink Price Feeds",
                endpoint_url="https://api.chain.link/v1/feeds",
                api_key=None,
                supported_types=[OracleType.PRICE_FEED, OracleType.MARKET_DATA],
                reputation_score=Decimal("98.5"),
                response_time_ms=150,
                reliability_percentage=Decimal("99.9"),
                is_active=True
            ),
            OracleProvider(
                provider_id="band_protocol",
                name="Band Protocol",
                endpoint_url="https://api.bandprotocol.com/v1/oracle",
                api_key=None,
                supported_types=[OracleType.PRICE_FEED, OracleType.API_DATA],
                reputation_score=Decimal("96.2"),
                response_time_ms=200,
                reliability_percentage=Decimal("99.5"),
                is_active=True
            ),
            OracleProvider(
                provider_id="tellor_network",
                name="Tellor Network",
                endpoint_url="https://api.tellor.io/v1/data",
                api_key=None,
                supported_types=[OracleType.PRICE_FEED, OracleType.CONTENT_VERIFICATION],
                reputation_score=Decimal("94.8"),
                response_time_ms=250,
                reliability_percentage=Decimal("98.8"),
                is_active=True
            ),
            OracleProvider(
                provider_id="content_validator",
                name="AI Content Validator",
                endpoint_url="https://api.ainflue.com/v1/validate",
                api_key="internal",
                supported_types=[OracleType.CONTENT_VERIFICATION],
                reputation_score=Decimal("97.5"),
                response_time_ms=500,
                reliability_percentage=Decimal("99.2"),
                is_active=True
            )
        ]
        
        for provider in providers:
            self.oracle_providers[provider.provider_id] = provider
    
    async def request_data(
        self,
        data_type: OracleType,
        query_params: Dict[str, Any],
        min_oracles: Optional[int] = None
    ) -> Dict[str, Any]:
        """Request data from multiple oracles"""
        try:
            request_id = str(uuid.uuid4())
            min_oracles = min_oracles or self.min_oracle_consensus
            
            self.logger.info(f"Requesting oracle data: {data_type.value}")
            
            # Find compatible oracles
            compatible_oracles = [
                provider for provider in self.oracle_providers.values()
                if data_type in provider.supported_types and provider.is_active
            ]
            
            if len(compatible_oracles) < min_oracles:
                raise ValueError(f"Insufficient oracles available: {len(compatible_oracles)} < {min_oracles}")
            
            # Query oracles in parallel
            oracle_responses = await self._query_oracles_parallel(
                compatible_oracles, data_type, query_params
            )
            
            # Validate and aggregate responses
            aggregated_result = await self._aggregate_oracle_responses(
                oracle_responses, data_type, query_params
            )
            
            # Cache result
            cache_key = self._generate_cache_key(data_type, query_params)
            self.aggregated_data[cache_key] = {
                "result": aggregated_result,
                "cached_at": datetime.utcnow(),
                "request_id": request_id
            }
            
            result = {
                "request_id": request_id,
                "data_type": data_type.value,
                "query_params": query_params,
                "result": aggregated_result,
                "oracle_count": len(oracle_responses),
                "consensus_reached": aggregated_result["consensus"]["reached"],
                "confidence_score": aggregated_result["confidence"],
                "requested_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Oracle data request completed: {request_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Oracle data request failed: {e}")
            raise
    
    async def _query_oracles_parallel(
        self,
        oracles: List[OracleProvider],
        data_type: OracleType,
        query_params: Dict[str, Any]
    ) -> List[OracleDataPoint]:
        """Query multiple oracles in parallel"""
        tasks = []
        
        for oracle in oracles:
            task = asyncio.create_task(
                self._query_single_oracle(oracle, data_type, query_params)
            )
            tasks.append(task)
        
        # Wait for all responses with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            self.logger.warning("Oracle query timeout")
            responses = []
        
        # Filter successful responses
        valid_responses = []
        for response in responses:
            if isinstance(response, OracleDataPoint):
                valid_responses.append(response)
            elif isinstance(response, Exception):
                self.logger.error(f"Oracle query failed: {response}")
        
        return valid_responses
    
    async def _query_single_oracle(
        self,
        oracle: OracleProvider,
        data_type: OracleType,
        query_params: Dict[str, Any]
    ) -> OracleDataPoint:
        """Query single oracle provider"""
        try:
            data_id = str(uuid.uuid4())
            
            # Mock oracle response based on data type
            if data_type == OracleType.PRICE_FEED:
                value = await self._mock_price_data(query_params)
            elif data_type == OracleType.CONTENT_VERIFICATION:
                value = await self._mock_content_verification(query_params)
            elif data_type == OracleType.MARKET_DATA:
                value = await self._mock_market_data(query_params)
            else:
                value = await self._mock_generic_data(query_params)
            
            data_point = OracleDataPoint(
                data_id=data_id,
                oracle_id=oracle.provider_id,
                data_type=data_type,
                value=value,
                confidence=oracle.reputation_score,
                timestamp=datetime.utcnow(),
                status=DataStatus.FRESH,
                metadata={
                    "provider_name": oracle.name,
                    "response_time_ms": oracle.response_time_ms,
                    "query_params": query_params
                }
            )
            
            # Cache data point
            self.data_cache[data_id] = data_point
            
            return data_point
            
        except Exception as e:
            self.logger.error(f"Oracle query failed for {oracle.name}: {e}")
            raise
    
    async def _mock_price_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock price feed data"""
        symbol = query_params.get("symbol", "ETH/USD")
        
        # Mock price data
        base_prices = {
            "ETH/USD": 2500.00,
            "BTC/USD": 45000.00,
            "MATIC/USD": 1.20,
            "BNB/USD": 350.00,
            "USDC/USD": 1.00,
            "USDT/USD": 1.00
        }
        
        base_price = base_prices.get(symbol, 100.00)
        # Add some random variation
        import random
        variation = random.uniform(-0.05, 0.05)  # ±5% variation
        current_price = base_price * (1 + variation)
        
        return {
            "symbol": symbol,
            "price": current_price,
            "timestamp": datetime.utcnow().isoformat(),
            "volume_24h": base_price * 1000000,
            "change_24h": variation * 100
        }
    
    async def _mock_content_verification(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock content verification data"""
        content_hash = query_params.get("content_hash", "")
        
        # Mock verification result
        import random
        authenticity_score = random.uniform(85, 99)
        
        return {
            "content_hash": content_hash,
            "authenticity_score": authenticity_score,
            "ai_generated_probability": random.uniform(5, 15),
            "similarity_matches": random.randint(0, 3),
            "verification_timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "verification_model": "ContentValidator-v2.1",
                "confidence_level": "high" if authenticity_score > 90 else "medium"
            }
        }
    
    async def _mock_market_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock market data"""
        market = query_params.get("market", "crypto")
        
        import random
        return {
            "market": market,
            "total_market_cap": random.uniform(1.5e12, 2.5e12),
            "trading_volume_24h": random.uniform(50e9, 150e9),
            "market_sentiment": random.choice(["bullish", "bearish", "neutral"]),
            "fear_greed_index": random.randint(20, 80),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _mock_generic_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock generic oracle data"""
        return {
            "query_params": query_params,
            "response": "mock_data",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _aggregate_oracle_responses(
        self,
        responses: List[OracleDataPoint],
        data_type: OracleType,
        query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate responses from multiple oracles"""
        if not responses:
            raise ValueError("No oracle responses to aggregate")
        
        if data_type == OracleType.PRICE_FEED:
            return await self._aggregate_price_data(responses)
        elif data_type == OracleType.CONTENT_VERIFICATION:
            return await self._aggregate_verification_data(responses)
        else:
            return await self._aggregate_generic_data(responses)
    
    async def _aggregate_price_data(self, responses: List[OracleDataPoint]) -> Dict[str, Any]:
        """Aggregate price feed data"""
        prices = []
        total_confidence = Decimal("0")
        
        for response in responses:
            price_data = response.value
            prices.append(Decimal(str(price_data["price"])))
            total_confidence += response.confidence
        
        if not prices:
            raise ValueError("No valid price data")
        
        # Calculate weighted average
        avg_confidence = total_confidence / len(responses)
        median_price = sorted(prices)[len(prices) // 2]
        mean_price = sum(prices) / len(prices)
        
        # Check for consensus (prices within acceptable deviation)
        consensus_reached = all(
            abs(price - median_price) / median_price <= (self.max_price_deviation / 100)
            for price in prices
        )
        
        return {
            "aggregated_price": float(median_price),
            "mean_price": float(mean_price),
            "price_range": {
                "min": float(min(prices)),
                "max": float(max(prices))
            },
            "oracle_count": len(responses),
            "confidence": float(avg_confidence),
            "consensus": {
                "reached": consensus_reached,
                "deviation_threshold": float(self.max_price_deviation)
            },
            "individual_prices": [float(p) for p in prices]
        }
    
    async def _aggregate_verification_data(self, responses: List[OracleDataPoint]) -> Dict[str, Any]:
        """Aggregate content verification data"""
        authenticity_scores = []
        ai_probabilities = []
        
        for response in responses:
            verification_data = response.value
            authenticity_scores.append(verification_data["authenticity_score"])
            ai_probabilities.append(verification_data["ai_generated_probability"])
        
        avg_authenticity = sum(authenticity_scores) / len(authenticity_scores)
        avg_ai_probability = sum(ai_probabilities) / len(ai_probabilities)
        
        # Simple consensus: majority agreement on authenticity
        authentic_count = sum(1 for score in authenticity_scores if score > 80)
        consensus_reached = authentic_count >= len(responses) / 2
        
        return {
            "average_authenticity_score": avg_authenticity,
            "average_ai_probability": avg_ai_probability,
            "consensus": {
                "reached": consensus_reached,
                "authentic_oracle_count": authentic_count,
                "total_oracles": len(responses)
            },
            "confidence": min(authenticity_scores),  # Conservative approach
            "verification_result": "authentic" if consensus_reached else "questionable"
        }
    
    async def _aggregate_generic_data(self, responses: List[OracleDataPoint]) -> Dict[str, Any]:
        """Aggregate generic oracle data"""
        return {
            "oracle_count": len(responses),
            "responses": [response.value for response in responses],
            "confidence": float(sum(r.confidence for r in responses) / len(responses)),
            "consensus": {
                "reached": len(responses) >= self.min_oracle_consensus,
                "oracle_count": len(responses)
            }
        }
    
    def _generate_cache_key(self, data_type: OracleType, query_params: Dict[str, Any]) -> str:
        """Generate cache key for data request"""
        key_data = {
            "type": data_type.value,
            "params": query_params
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def get_cached_data(
        self,
        data_type: OracleType,
        query_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached oracle data if available and fresh"""
        cache_key = self._generate_cache_key(data_type, query_params)
        
        if cache_key in self.aggregated_data:
            cached_entry = self.aggregated_data[cache_key]
            cached_at = cached_entry["cached_at"]
            
            # Check if cache is still fresh
            if datetime.utcnow() - cached_at < timedelta(seconds=self.cache_ttl_seconds):
                return cached_entry["result"]
        
        return None
    
    async def update_oracle_reputation(
        self,
        oracle_id: str,
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update oracle provider reputation based on performance"""
        try:
            if oracle_id not in self.oracle_providers:
                raise ValueError(f"Oracle provider not found: {oracle_id}")
            
            oracle = self.oracle_providers[oracle_id]
            
            # Calculate new reputation score
            accuracy = Decimal(str(performance_metrics.get("accuracy", 0)))
            response_time = performance_metrics.get("response_time_ms", oracle.response_time_ms)
            uptime = Decimal(str(performance_metrics.get("uptime_percentage", 0)))
            
            # Simple reputation calculation
            new_reputation = (accuracy * Decimal("0.5") + 
                            uptime * Decimal("0.3") + 
                            (Decimal("100") - min(Decimal(str(response_time)), Decimal("1000")) / 10) * Decimal("0.2"))
            
            # Apply smoothing factor to prevent dramatic changes
            smoothing_factor = Decimal("0.1")
            oracle.reputation_score = (oracle.reputation_score * (1 - smoothing_factor) + 
                                     new_reputation * smoothing_factor)
            
            oracle.response_time_ms = int((oracle.response_time_ms + response_time) / 2)
            oracle.reliability_percentage = (oracle.reliability_percentage + uptime) / 2
            
            result = {
                "oracle_id": oracle_id,
                "old_reputation": float(oracle.reputation_score),
                "new_reputation": float(oracle.reputation_score),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Oracle reputation updated: {oracle_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Oracle reputation update failed: {e}")
            raise
    
    async def get_oracle_analytics(self) -> Dict[str, Any]:
        """Get oracle system analytics"""
        active_oracles = len([o for o in self.oracle_providers.values() if o.is_active])
        total_oracles = len(self.oracle_providers)
        
        avg_reputation = sum(o.reputation_score for o in self.oracle_providers.values()) / total_oracles
        avg_response_time = sum(o.response_time_ms for o in self.oracle_providers.values()) / total_oracles
        
        data_type_support = {}
        for oracle in self.oracle_providers.values():
            for data_type in oracle.supported_types:
                data_type_support[data_type.value] = data_type_support.get(data_type.value, 0) + 1
        
        return {
            "total_oracles": total_oracles,
            "active_oracles": active_oracles,
            "average_reputation": float(avg_reputation),
            "average_response_time_ms": avg_response_time,
            "cached_data_points": len(self.data_cache),
            "aggregated_queries": len(self.aggregated_data),
            "data_type_support": data_type_support,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "min_oracle_consensus": self.min_oracle_consensus
        }


class OracleManager:
    """High-level manager for oracle operations"""
    
    def __init__(self, oracle_connector: OracleConnector):
        self.oracle_connector = oracle_connector
        self.logger = logging.getLogger(__name__)
    
    async def get_token_price(
        self,
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get current token price from price oracles"""
        query_params = {"symbol": symbol}
        
        if use_cache:
            cached_data = await self.oracle_connector.get_cached_data(
                OracleType.PRICE_FEED, query_params
            )
            if cached_data:
                return {
                    "symbol": symbol,
                    "price": cached_data["aggregated_price"],
                    "cached": True,
                    "confidence": cached_data["confidence"]
                }
        
        result = await self.oracle_connector.request_data(
            OracleType.PRICE_FEED, query_params
        )
        
        return {
            "symbol": symbol,
            "price": result["result"]["aggregated_price"],
            "cached": False,
            "confidence": result["confidence_score"],
            "oracle_count": result["oracle_count"]
        }
    
    async def verify_content_authenticity(
        self,
        content_hash: str
    ) -> Dict[str, Any]:
        """Verify content authenticity using verification oracles"""
        query_params = {"content_hash": content_hash}
        
        result = await self.oracle_connector.request_data(
            OracleType.CONTENT_VERIFICATION, query_params
        )
        
        return {
            "content_hash": content_hash,
            "authenticity_score": result["result"]["average_authenticity_score"],
            "verification_result": result["result"]["verification_result"],
            "confidence": result["confidence_score"],
            "consensus_reached": result["result"]["consensus"]["reached"]
        }