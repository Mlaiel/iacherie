"""
Blockchain Analytics Suite - Advanced on-chain analytics & insights

Comprehensive blockchain analytics system for transaction analysis, wallet behavior tracking,
gas optimization, revenue analytics, and performance insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import hashlib
import json
import logging
import math
import statistics
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from uuid import uuid4, UUID

import aioredis
import numpy as np
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class AnalyticsTimeframe(Enum):
    """Analytics timeframe enumeration"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TransactionType(Enum):
    """Transaction type enumeration"""
    NFT_MINT = "nft_mint"
    NFT_TRANSFER = "nft_transfer"
    NFT_SALE = "nft_sale"
    TOKEN_TRANSFER = "token_transfer"
    STAKING = "staking"
    UNSTAKING = "unstaking"
    GOVERNANCE_VOTE = "governance_vote"
    DEFI_INTERACTION = "defi_interaction"
    CROSS_CHAIN = "cross_chain"
    CONTRACT_DEPLOYMENT = "contract_deployment"


class WalletBehaviorType(Enum):
    """Wallet behavior classification"""
    WHALE = "whale"
    TRADER = "trader"
    COLLECTOR = "collector"
    CREATOR = "creator"
    HODLER = "hodler"
    BOT = "bot"
    INFLUENCER = "influencer"
    INSTITUTIONAL = "institutional"


class MetricType(Enum):
    """Metric type enumeration"""
    VOLUME = "volume"
    COUNT = "count"
    AVERAGE = "average"
    MEDIAN = "median"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    GROWTH_RATE = "growth_rate"
    VOLATILITY = "volatility"


@dataclass
class TransactionAnalysis:
    """Transaction analysis data structure"""
    transaction_hash: str
    block_number: int
    timestamp: datetime
    from_address: str
    to_address: str
    value: Decimal
    gas_used: int
    gas_price: Decimal
    transaction_type: TransactionType
    contract_address: Optional[str] = None
    token_id: Optional[str] = None
    method_signature: Optional[str] = None
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WalletProfile:
    """Wallet behavior profile"""
    wallet_address: str
    behavior_type: WalletBehaviorType
    activity_score: float
    transaction_count: int
    total_volume: Decimal
    average_transaction_value: Decimal
    preferred_tokens: List[str]
    interaction_patterns: Dict[str, Any]
    risk_score: float
    reputation_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GasAnalytics:
    """Gas usage analytics"""
    timeframe: AnalyticsTimeframe
    average_gas_price: Decimal
    median_gas_price: Decimal
    gas_price_volatility: float
    total_gas_consumed: int
    gas_efficiency_score: float
    optimization_recommendations: List[str]
    cost_savings_potential: Decimal
    peak_usage_times: List[datetime]


@dataclass
class RevenueMetrics:
    """Revenue tracking metrics"""
    timeframe: AnalyticsTimeframe
    total_revenue: Decimal
    revenue_by_source: Dict[str, Decimal]
    revenue_growth_rate: float
    average_transaction_fee: Decimal
    fee_efficiency: float
    profit_margin: float
    projected_revenue: Decimal


class TransactionRecord(Base):
    """Database model for transaction records"""
    __tablename__ = "transaction_analytics"
    
    transaction_hash = Column(String, primary_key=True)
    block_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    value = Column(Numeric(precision=36, scale=18), nullable=False)
    gas_used = Column(Integer, nullable=False)
    gas_price = Column(Numeric(precision=36, scale=18), nullable=False)
    transaction_type = Column(String, nullable=False)
    contract_address = Column(String)
    token_id = Column(String)
    method_signature = Column(String)
    success = Column(Boolean, default=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class WalletAnalytics(Base):
    """Database model for wallet analytics"""
    __tablename__ = "wallet_analytics"
    
    wallet_address = Column(String, primary_key=True)
    behavior_type = Column(String, nullable=False)
    activity_score = Column(Float, nullable=False)
    transaction_count = Column(Integer, default=0)
    total_volume = Column(Numeric(precision=36, scale=18), default=0)
    average_transaction_value = Column(Numeric(precision=36, scale=18), default=0)
    preferred_tokens = Column(JSON, default=[])
    interaction_patterns = Column(JSON, default={})
    risk_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    last_analysis = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsMetrics(Base):
    """Database model for analytics metrics"""
    __tablename__ = "analytics_metrics"
    
    metric_id = Column(String, primary_key=True)
    metric_type = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    value = Column(Numeric(precision=36, scale=18), nullable=False)
    metadata = Column(JSON, default={})
    calculated_at = Column(DateTime, default=datetime.utcnow)
    date = Column(DateTime, nullable=False)


class TransactionFlowAnalyzer:
    """Analyzes transaction flows and patterns"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        self.flow_cache = {}
        
    async def analyze_transaction_flow(self, start_address: str, 
                                     depth: int = 3, 
                                     timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY) -> Dict[str, Any]:
        """Analyze transaction flow patterns from a starting address"""
        try:
            flow_graph = await self._build_flow_graph(start_address, depth, timeframe)
            flow_metrics = await self._calculate_flow_metrics(flow_graph)
            patterns = await self._identify_flow_patterns(flow_graph)
            
            analysis_result = {
                "start_address": start_address,
                "analysis_depth": depth,
                "timeframe": timeframe.value,
                "flow_graph": flow_graph,
                "flow_metrics": flow_metrics,
                "identified_patterns": patterns,
                "risk_indicators": await self._assess_flow_risks(flow_graph),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Cache results
            cache_key = f"flow_analysis:{hashlib.md5(f'{start_address}_{depth}_{timeframe.value}'.encode()).hexdigest()}"
            await self.redis.setex(cache_key, 3600, json.dumps(analysis_result, default=str))
            
            logger.info(f"Transaction flow analysis completed for {start_address}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Transaction flow analysis failed: {str(e)}")
            raise
    
    async def detect_suspicious_patterns(self, addresses: List[str], 
                                       timeframe: AnalyticsTimeframe = AnalyticsTimeframe.WEEKLY) -> Dict[str, Any]:
        """Detect suspicious transaction patterns"""
        try:
            suspicious_patterns = {
                "circular_transactions": [],
                "wash_trading": [],
                "pump_and_dump": [],
                "money_laundering": [],
                "bot_activity": [],
                "sybil_attacks": []
            }
            
            for address in addresses:
                # Analyze each address for suspicious patterns
                address_patterns = await self._analyze_address_patterns(address, timeframe)
                
                # Check for circular transactions
                if address_patterns.get("circular_ratio", 0) > 0.8:
                    suspicious_patterns["circular_transactions"].append({
                        "address": address,
                        "circular_ratio": address_patterns["circular_ratio"],
                        "confidence": address_patterns.get("confidence", 0.0)
                    })
                
                # Check for wash trading
                if address_patterns.get("self_trading_ratio", 0) > 0.5:
                    suspicious_patterns["wash_trading"].append({
                        "address": address,
                        "self_trading_ratio": address_patterns["self_trading_ratio"],
                        "volume": address_patterns.get("volume", 0)
                    })
                
                # Check for bot activity
                if address_patterns.get("bot_probability", 0) > 0.7:
                    suspicious_patterns["bot_activity"].append({
                        "address": address,
                        "bot_probability": address_patterns["bot_probability"],
                        "transaction_pattern": address_patterns.get("pattern_type", "unknown")
                    })
            
            detection_result = {
                "addresses_analyzed": len(addresses),
                "timeframe": timeframe.value,
                "suspicious_patterns": suspicious_patterns,
                "total_suspicious_count": sum(len(patterns) for patterns in suspicious_patterns.values()),
                "risk_level": await self._calculate_overall_risk_level(suspicious_patterns),
                "detected_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Suspicious pattern detection completed: {detection_result['total_suspicious_count']} patterns found")
            return detection_result
            
        except Exception as e:
            logger.error(f"Suspicious pattern detection failed: {str(e)}")
            raise
    
    async def _build_flow_graph(self, start_address: str, depth: int, 
                               timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Build transaction flow graph"""
        # Mock implementation - would build actual graph from blockchain data
        return {
            "nodes": [
                {"address": start_address, "level": 0, "transaction_count": 150, "volume": 25.5},
                {"address": "0x742d35Cc6635C0532925a3b8D29b6F25e19a1e7e", "level": 1, "transaction_count": 75, "volume": 12.3},
                {"address": "0x8ba1f109551bD432803012645Hac136c3c2b20f", "level": 1, "transaction_count": 90, "volume": 18.7}
            ],
            "edges": [
                {"from": start_address, "to": "0x742d35Cc6635C0532925a3b8D29b6F25e19a1e7e", "weight": 5.2, "transaction_count": 12},
                {"from": start_address, "to": "0x8ba1f109551bD432803012645Hac136c3c2b20f", "weight": 8.1, "transaction_count": 18}
            ]
        }
    
    async def _calculate_flow_metrics(self, flow_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate flow metrics from graph"""
        nodes = flow_graph.get("nodes", [])
        edges = flow_graph.get("edges", [])
        
        total_volume = sum(node.get("volume", 0) for node in nodes)
        total_transactions = sum(node.get("transaction_count", 0) for node in nodes)
        network_density = len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        
        return {
            "total_volume": total_volume,
            "total_transactions": total_transactions,
            "network_density": network_density,
            "average_transaction_value": total_volume / total_transactions if total_transactions > 0 else 0,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
    
    async def _identify_flow_patterns(self, flow_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns in transaction flow"""
        patterns = []
        
        # Pattern: High-frequency small transactions
        nodes = flow_graph.get("nodes", [])
        for node in nodes:
            if node.get("transaction_count", 0) > 100 and node.get("volume", 0) / node.get("transaction_count", 1) < 0.1:
                patterns.append({
                    "pattern_type": "high_frequency_small_transactions",
                    "address": node["address"],
                    "confidence": 0.8,
                    "description": "Address shows high-frequency, small-value transaction pattern"
                })
        
        # Pattern: Concentration of volume
        total_volume = sum(node.get("volume", 0) for node in nodes)
        for node in nodes:
            if node.get("volume", 0) / total_volume > 0.5:
                patterns.append({
                    "pattern_type": "volume_concentration",
                    "address": node["address"],
                    "confidence": 0.9,
                    "description": "Address concentrates significant portion of network volume"
                })
        
        return patterns
    
    async def _assess_flow_risks(self, flow_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks in transaction flow"""
        return {
            "money_laundering_risk": 0.2,
            "centralization_risk": 0.4,
            "manipulation_risk": 0.1,
            "overall_risk_score": 0.3,
            "risk_factors": [
                "High concentration of transactions in few addresses",
                "Some irregular transaction patterns detected"
            ]
        }
    
    async def _analyze_address_patterns(self, address: str, 
                                      timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Analyze patterns for specific address"""
        # Mock implementation - would analyze actual transaction data
        return {
            "circular_ratio": 0.1,
            "self_trading_ratio": 0.05,
            "bot_probability": 0.3,
            "confidence": 0.7,
            "volume": 15.5,
            "pattern_type": "normal"
        }
    
    async def _calculate_overall_risk_level(self, suspicious_patterns: Dict[str, List]) -> str:
        """Calculate overall risk level based on detected patterns"""
        total_patterns = sum(len(patterns) for patterns in suspicious_patterns.values())
        
        if total_patterns >= 10:
            return "high"
        elif total_patterns >= 5:
            return "medium"
        elif total_patterns >= 1:
            return "low"
        else:
            return "minimal"


class WalletBehaviorAnalyzer:
    """Analyzes wallet behavior patterns and classifications"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
        # Behavior classification thresholds
        self.classification_thresholds = {
            "whale": {"min_volume": 100.0, "min_transactions": 50},
            "trader": {"transaction_frequency": 10.0, "volume_variance": 0.8},
            "collector": {"nft_ratio": 0.7, "holding_period": 30},
            "creator": {"minting_ratio": 0.3, "royalty_income": 1.0},
            "hodler": {"holding_period": 180, "transaction_frequency": 0.1},
            "bot": {"regular_intervals": 0.9, "identical_amounts": 0.8}
        }
    
    async def analyze_wallet_behavior(self, wallet_address: str, 
                                    analysis_period: int = 90) -> WalletProfile:
        """Comprehensive wallet behavior analysis"""
        try:
            # Collect wallet transaction data
            transaction_data = await self._collect_wallet_transactions(wallet_address, analysis_period)
            
            # Calculate activity metrics
            activity_metrics = await self._calculate_activity_metrics(transaction_data)
            
            # Classify behavior type
            behavior_type = await self._classify_wallet_behavior(activity_metrics)
            
            # Calculate scores
            activity_score = await self._calculate_activity_score(activity_metrics)
            risk_score = await self._calculate_risk_score(transaction_data, activity_metrics)
            reputation_score = await self._calculate_reputation_score(transaction_data)
            
            # Identify interaction patterns
            interaction_patterns = await self._analyze_interaction_patterns(transaction_data)
            
            # Create wallet profile
            profile = WalletProfile(
                wallet_address=wallet_address,
                behavior_type=behavior_type,
                activity_score=activity_score,
                transaction_count=len(transaction_data),
                total_volume=sum(tx.get("value", 0) for tx in transaction_data),
                average_transaction_value=statistics.mean([tx.get("value", 0) for tx in transaction_data]) if transaction_data else 0,
                preferred_tokens=await self._identify_preferred_tokens(transaction_data),
                interaction_patterns=interaction_patterns,
                risk_score=risk_score,
                reputation_score=reputation_score
            )
            
            # Store profile in database
            await self._store_wallet_profile(profile)
            
            logger.info(f"Wallet behavior analysis completed for {wallet_address}: {behavior_type.value}")
            return profile
            
        except Exception as e:
            logger.error(f"Wallet behavior analysis failed for {wallet_address}: {str(e)}")
            raise
    
    async def generate_behavior_insights(self, wallet_addresses: List[str]) -> Dict[str, Any]:
        """Generate behavioral insights for multiple wallets"""
        try:
            profiles = []
            for address in wallet_addresses:
                try:
                    profile = await self.analyze_wallet_behavior(address)
                    profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Failed to analyze wallet {address}: {str(e)}")
            
            # Aggregate insights
            behavior_distribution = self._calculate_behavior_distribution(profiles)
            network_insights = await self._calculate_network_insights(profiles)
            risk_analysis = self._analyze_risk_distribution(profiles)
            
            insights = {
                "total_wallets_analyzed": len(profiles),
                "behavior_distribution": behavior_distribution,
                "network_insights": network_insights,
                "risk_analysis": risk_analysis,
                "top_performers": await self._identify_top_performers(profiles),
                "anomalies": await self._identify_behavioral_anomalies(profiles),
                "recommendations": await self._generate_behavioral_recommendations(profiles),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Behavior insights generated for {len(profiles)} wallets")
            return insights
            
        except Exception as e:
            logger.error(f"Behavior insights generation failed: {str(e)}")
            raise
    
    async def _collect_wallet_transactions(self, wallet_address: str, 
                                         period_days: int) -> List[Dict[str, Any]]:
        """Collect transaction data for wallet"""
        # Mock implementation - would query actual blockchain data
        return [
            {"hash": "0x123", "value": 1.5, "timestamp": datetime.utcnow() - timedelta(days=1), "type": "transfer"},
            {"hash": "0x456", "value": 2.3, "timestamp": datetime.utcnow() - timedelta(days=3), "type": "nft_purchase"},
            {"hash": "0x789", "value": 0.8, "timestamp": datetime.utcnow() - timedelta(days=7), "type": "stake"}
        ]
    
    async def _calculate_activity_metrics(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate activity metrics from transaction data"""
        if not transactions:
            return {}
        
        values = [tx.get("value", 0) for tx in transactions]
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        
        # Calculate time-based metrics
        if len(timestamps) > 1:
            intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
            avg_interval = statistics.mean(intervals) if intervals else 0
            interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        else:
            avg_interval = 0
            interval_variance = 0
        
        return {
            "transaction_count": len(transactions),
            "total_volume": sum(values),
            "average_value": statistics.mean(values) if values else 0,
            "median_value": statistics.median(values) if values else 0,
            "value_variance": statistics.variance(values) if len(values) > 1 else 0,
            "average_interval_hours": avg_interval / 3600,
            "interval_variance": interval_variance,
            "transaction_types": self._count_transaction_types(transactions),
            "active_days": len(set(tx.get("timestamp").date() for tx in timestamps)) if timestamps else 0
        }
    
    async def _classify_wallet_behavior(self, metrics: Dict[str, Any]) -> WalletBehaviorType:
        """Classify wallet behavior based on metrics"""
        total_volume = metrics.get("total_volume", 0)
        transaction_count = metrics.get("transaction_count", 0)
        avg_interval = metrics.get("average_interval_hours", 0)
        interval_variance = metrics.get("interval_variance", 0)
        transaction_types = metrics.get("transaction_types", {})
        
        # Whale classification
        if (total_volume >= self.classification_thresholds["whale"]["min_volume"] and 
            transaction_count >= self.classification_thresholds["whale"]["min_transactions"]):
            return WalletBehaviorType.WHALE
        
        # Bot classification (regular intervals, low variance)
        if interval_variance < 3600 and avg_interval > 0 and avg_interval < 24:  # Less than 1 hour variance, regular activity
            return WalletBehaviorType.BOT
        
        # Trader classification (high frequency, high variance)
        if (transaction_count > 20 and 
            metrics.get("value_variance", 0) > metrics.get("average_value", 0) * 0.5):
            return WalletBehaviorType.TRADER
        
        # Collector classification (NFT focus)
        nft_ratio = (transaction_types.get("nft_purchase", 0) + transaction_types.get("nft_transfer", 0)) / max(transaction_count, 1)
        if nft_ratio >= 0.5:
            return WalletBehaviorType.COLLECTOR
        
        # Creator classification (minting activity)
        mint_ratio = transaction_types.get("nft_mint", 0) / max(transaction_count, 1)
        if mint_ratio >= 0.2:
            return WalletBehaviorType.CREATOR
        
        # Hodler classification (low frequency, long intervals)
        if avg_interval > 168:  # More than a week between transactions
            return WalletBehaviorType.HODLER
        
        # Default to trader
        return WalletBehaviorType.TRADER
    
    async def _calculate_activity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate activity score (0-1)"""
        transaction_count = metrics.get("transaction_count", 0)
        total_volume = metrics.get("total_volume", 0)
        active_days = metrics.get("active_days", 0)
        
        # Normalize components
        frequency_score = min(transaction_count / 100, 1.0)  # Max score at 100 transactions
        volume_score = min(total_volume / 100, 1.0)         # Max score at 100 ETH
        consistency_score = min(active_days / 30, 1.0)      # Max score at 30 active days
        
        # Weighted average
        activity_score = (frequency_score * 0.4 + volume_score * 0.4 + consistency_score * 0.2)
        return round(activity_score, 3)
    
    async def _calculate_risk_score(self, transactions: List[Dict[str, Any]], 
                                  metrics: Dict[str, Any]) -> float:
        """Calculate risk score (0-1, higher = more risky)"""
        base_risk = 0.1
        
        # High transaction frequency risk
        if metrics.get("transaction_count", 0) > 200:
            base_risk += 0.2
        
        # High volume concentration risk
        if metrics.get("total_volume", 0) > 1000:
            base_risk += 0.3
        
        # Irregular pattern risk
        if metrics.get("interval_variance", 0) > 86400:  # High variance in timing
            base_risk += 0.2
        
        # Bot-like behavior risk
        if metrics.get("interval_variance", 0) < 3600:  # Very regular timing
            base_risk += 0.1
        
        return min(base_risk, 1.0)
    
    async def _calculate_reputation_score(self, transactions: List[Dict[str, Any]]) -> float:
        """Calculate reputation score (0-1)"""
        # Mock implementation - would consider factors like:
        # - Successful transaction rate
        # - No failed/reverted transactions
        # - No suspicious activity
        # - Community interactions
        
        base_reputation = 0.7
        
        # Check for failed transactions
        failed_count = sum(1 for tx in transactions if not tx.get("success", True))
        failure_penalty = min(failed_count * 0.1, 0.3)
        
        reputation = base_reputation - failure_penalty
        return max(0.0, min(1.0, reputation))
    
    async def _analyze_interaction_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze wallet interaction patterns"""
        # Analyze transaction timing patterns
        timestamps = [tx.get("timestamp") for tx in transactions if tx.get("timestamp")]
        
        if len(timestamps) < 2:
            return {"pattern_type": "insufficient_data"}
        
        # Calculate time intervals
        intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
        
        # Analyze patterns
        avg_interval = statistics.mean(intervals)
        interval_std = statistics.stdev(intervals) if len(intervals) > 1 else 0
        
        # Classify pattern
        if interval_std < avg_interval * 0.1:
            pattern_type = "highly_regular"
        elif interval_std < avg_interval * 0.5:
            pattern_type = "somewhat_regular"
        else:
            pattern_type = "irregular"
        
        return {
            "pattern_type": pattern_type,
            "average_interval_hours": avg_interval / 3600,
            "regularity_score": 1 - min(interval_std / avg_interval, 1) if avg_interval > 0 else 0,
            "peak_activity_hours": self._identify_peak_hours(timestamps),
            "transaction_clustering": self._analyze_transaction_clusters(timestamps)
        }
    
    async def _identify_preferred_tokens(self, transactions: List[Dict[str, Any]]) -> List[str]:
        """Identify preferred tokens based on transaction history"""
        token_counts = defaultdict(int)
        
        for tx in transactions:
            token = tx.get("token", "ETH")
            token_counts[token] += 1
        
        # Sort by frequency and return top 5
        sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
        return [token for token, count in sorted_tokens[:5]]
    
    def _count_transaction_types(self, transactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count transactions by type"""
        type_counts = defaultdict(int)
        for tx in transactions:
            tx_type = tx.get("type", "unknown")
            type_counts[tx_type] += 1
        return dict(type_counts)
    
    def _identify_peak_hours(self, timestamps: List[datetime]) -> List[int]:
        """Identify peak activity hours"""
        if not timestamps:
            return []
        
        hour_counts = defaultdict(int)
        for ts in timestamps:
            hour_counts[ts.hour] += 1
        
        # Return hours with above-average activity
        avg_activity = len(timestamps) / 24
        peak_hours = [hour for hour, count in hour_counts.items() if count > avg_activity]
        return sorted(peak_hours)
    
    def _analyze_transaction_clusters(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze transaction clustering patterns"""
        if len(timestamps) < 3:
            return {"clustering": "insufficient_data"}
        
        # Simple clustering analysis - transactions within 1 hour of each other
        clusters = []
        current_cluster = [timestamps[0]]
        
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i-1]).total_seconds() <= 3600:  # Within 1 hour
                current_cluster.append(timestamps[i])
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [timestamps[i]]
        
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        return {
            "cluster_count": len(clusters),
            "largest_cluster_size": max(len(cluster) for cluster in clusters) if clusters else 0,
            "clustering_tendency": len(clusters) / len(timestamps) if timestamps else 0
        }
    
    def _calculate_behavior_distribution(self, profiles: List[WalletProfile]) -> Dict[str, Any]:
        """Calculate distribution of behavior types"""
        behavior_counts = defaultdict(int)
        for profile in profiles:
            behavior_counts[profile.behavior_type.value] += 1
        
        total = len(profiles)
        return {
            behavior: {"count": count, "percentage": (count / total) * 100}
            for behavior, count in behavior_counts.items()
        }
    
    async def _calculate_network_insights(self, profiles: List[WalletProfile]) -> Dict[str, Any]:
        """Calculate network-level insights"""
        if not profiles:
            return {}
        
        total_volume = sum(float(profile.total_volume) for profile in profiles)
        avg_activity = statistics.mean([profile.activity_score for profile in profiles])
        avg_risk = statistics.mean([profile.risk_score for profile in profiles])
        
        return {
            "total_network_volume": total_volume,
            "average_activity_score": avg_activity,
            "average_risk_score": avg_risk,
            "network_health_score": (avg_activity * 0.6) + ((1 - avg_risk) * 0.4),
            "most_active_addresses": [p.wallet_address for p in sorted(profiles, key=lambda x: x.activity_score, reverse=True)[:5]]
        }
    
    def _analyze_risk_distribution(self, profiles: List[WalletProfile]) -> Dict[str, Any]:
        """Analyze risk distribution across wallets"""
        if not profiles:
            return {}
        
        risk_scores = [profile.risk_score for profile in profiles]
        
        # Categorize risk levels
        low_risk = sum(1 for score in risk_scores if score < 0.3)
        medium_risk = sum(1 for score in risk_scores if 0.3 <= score < 0.7)
        high_risk = sum(1 for score in risk_scores if score >= 0.7)
        
        return {
            "risk_distribution": {
                "low_risk": {"count": low_risk, "percentage": (low_risk / len(profiles)) * 100},
                "medium_risk": {"count": medium_risk, "percentage": (medium_risk / len(profiles)) * 100},
                "high_risk": {"count": high_risk, "percentage": (high_risk / len(profiles)) * 100}
            },
            "average_risk_score": statistics.mean(risk_scores),
            "risk_variance": statistics.variance(risk_scores) if len(risk_scores) > 1 else 0,
            "high_risk_addresses": [p.wallet_address for p in profiles if p.risk_score >= 0.7]
        }
    
    async def _identify_top_performers(self, profiles: List[WalletProfile]) -> List[Dict[str, Any]]:
        """Identify top performing wallets"""
        sorted_profiles = sorted(profiles, key=lambda x: x.activity_score * x.reputation_score, reverse=True)
        
        return [
            {
                "address": profile.wallet_address,
                "behavior_type": profile.behavior_type.value,
                "activity_score": profile.activity_score,
                "reputation_score": profile.reputation_score,
                "combined_score": profile.activity_score * profile.reputation_score
            }
            for profile in sorted_profiles[:10]
        ]
    
    async def _identify_behavioral_anomalies(self, profiles: List[WalletProfile]) -> List[Dict[str, Any]]:
        """Identify behavioral anomalies"""
        anomalies = []
        
        # Statistical anomalies in activity scores
        activity_scores = [p.activity_score for p in profiles]
        if len(activity_scores) > 1:
            mean_activity = statistics.mean(activity_scores)
            std_activity = statistics.stdev(activity_scores)
            
            for profile in profiles:
                if abs(profile.activity_score - mean_activity) > 2 * std_activity:
                    anomalies.append({
                        "address": profile.wallet_address,
                        "anomaly_type": "extreme_activity_score",
                        "score": profile.activity_score,
                        "deviation": abs(profile.activity_score - mean_activity) / std_activity
                    })
        
        return anomalies
    
    async def _generate_behavioral_recommendations(self, profiles: List[WalletProfile]) -> List[Dict[str, Any]]:
        """Generate behavioral recommendations"""
        recommendations = []
        
        # High-risk wallet recommendations
        high_risk_count = sum(1 for p in profiles if p.risk_score > 0.7)
        if high_risk_count > len(profiles) * 0.1:  # More than 10% high risk
            recommendations.append({
                "type": "risk_management",
                "priority": "high",
                "recommendation": "Implement enhanced monitoring for high-risk wallets",
                "affected_wallets": high_risk_count
            })
        
        # Bot activity recommendations
        bot_count = sum(1 for p in profiles if p.behavior_type == WalletBehaviorType.BOT)
        if bot_count > len(profiles) * 0.05:  # More than 5% bots
            recommendations.append({
                "type": "bot_management",
                "priority": "medium",
                "recommendation": "Consider implementing bot detection and rate limiting",
                "affected_wallets": bot_count
            })
        
        return recommendations
    
    async def _store_wallet_profile(self, profile: WalletProfile) -> None:
        """Store wallet profile in database"""
        wallet_analytics = WalletAnalytics(
            wallet_address=profile.wallet_address,
            behavior_type=profile.behavior_type.value,
            activity_score=profile.activity_score,
            transaction_count=profile.transaction_count,
            total_volume=profile.total_volume,
            average_transaction_value=profile.average_transaction_value,
            preferred_tokens=profile.preferred_tokens,
            interaction_patterns=profile.interaction_patterns,
            risk_score=profile.risk_score,
            reputation_score=profile.reputation_score
        )
        
        # Use merge to update if exists
        try:
            self.db.add(wallet_analytics)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            # Update existing record
            pass


class GasOptimizationAnalytics:
    """Advanced gas usage analytics and optimization"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def analyze_gas_patterns(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY) -> GasAnalytics:
        """Analyze gas usage patterns and optimization opportunities"""
        try:
            # Collect gas usage data
            gas_data = await self._collect_gas_data(timeframe)
            
            if not gas_data:
                return self._get_default_gas_analytics(timeframe)
            
            # Calculate gas metrics
            gas_prices = [entry["gas_price"] for entry in gas_data]
            gas_used = [entry["gas_used"] for entry in gas_data]
            
            avg_gas_price = statistics.mean(gas_prices)
            median_gas_price = statistics.median(gas_prices)
            gas_price_volatility = statistics.stdev(gas_prices) / avg_gas_price if avg_gas_price > 0 else 0
            
            total_gas_consumed = sum(gas_used)
            gas_efficiency_score = await self._calculate_gas_efficiency(gas_data)
            
            # Generate optimization recommendations
            optimization_recommendations = await self._generate_gas_optimization_recommendations(gas_data)
            
            # Calculate cost savings potential
            cost_savings_potential = await self._calculate_cost_savings_potential(gas_data)
            
            # Identify peak usage times
            peak_usage_times = await self._identify_peak_gas_usage_times(gas_data)
            
            analytics = GasAnalytics(
                timeframe=timeframe,
                average_gas_price=Decimal(str(avg_gas_price)),
                median_gas_price=Decimal(str(median_gas_price)),
                gas_price_volatility=gas_price_volatility,
                total_gas_consumed=total_gas_consumed,
                gas_efficiency_score=gas_efficiency_score,
                optimization_recommendations=optimization_recommendations,
                cost_savings_potential=cost_savings_potential,
                peak_usage_times=peak_usage_times
            )
            
            # Cache analytics
            cache_key = f"gas_analytics:{timeframe.value}:{datetime.utcnow().date()}"
            await self.redis.setex(cache_key, 3600, json.dumps({
                "average_gas_price": str(analytics.average_gas_price),
                "median_gas_price": str(analytics.median_gas_price),
                "gas_price_volatility": analytics.gas_price_volatility,
                "total_gas_consumed": analytics.total_gas_consumed,
                "gas_efficiency_score": analytics.gas_efficiency_score,
                "optimization_recommendations": analytics.optimization_recommendations,
                "cost_savings_potential": str(analytics.cost_savings_potential)
            }))
            
            logger.info(f"Gas analytics completed for {timeframe.value}")
            return analytics
            
        except Exception as e:
            logger.error(f"Gas analytics failed: {str(e)}")
            raise
    
    async def recommend_optimal_gas_price(self, transaction_urgency: str = "standard") -> Dict[str, Any]:
        """Recommend optimal gas price based on current network conditions"""
        try:
            # Get current gas price data
            current_gas_data = await self._get_current_gas_prices()
            
            # Calculate recommendations based on urgency
            urgency_multipliers = {
                "slow": 0.8,
                "standard": 1.0,
                "fast": 1.3,
                "instant": 1.8
            }
            
            base_price = current_gas_data.get("average_price", 20)  # 20 gwei default
            multiplier = urgency_multipliers.get(transaction_urgency, 1.0)
            recommended_price = base_price * multiplier
            
            # Estimate confirmation time
            confirmation_estimates = {
                "slow": "10-15 minutes",
                "standard": "3-5 minutes", 
                "fast": "1-2 minutes",
                "instant": "< 1 minute"
            }
            
            return {
                "recommended_gas_price": recommended_price,
                "estimated_confirmation_time": confirmation_estimates[transaction_urgency],
                "network_congestion": current_gas_data.get("congestion_level", "medium"),
                "price_trend": current_gas_data.get("price_trend", "stable"),
                "cost_estimate_usd": recommended_price * current_gas_data.get("eth_price_usd", 2000) / 1e9,
                "recommended_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gas price recommendation failed: {str(e)}")
            raise
    
    async def _collect_gas_data(self, timeframe: AnalyticsTimeframe) -> List[Dict[str, Any]]:
        """Collect gas usage data for specified timeframe"""
        # Mock implementation - would collect from blockchain
        return [
            {"gas_price": 25.5, "gas_used": 21000, "timestamp": datetime.utcnow() - timedelta(hours=1)},
            {"gas_price": 30.2, "gas_used": 45000, "timestamp": datetime.utcnow() - timedelta(hours=2)},
            {"gas_price": 22.8, "gas_used": 35000, "timestamp": datetime.utcnow() - timedelta(hours=3)}
        ]
    
    async def _calculate_gas_efficiency(self, gas_data: List[Dict[str, Any]]) -> float:
        """Calculate gas efficiency score"""
        if not gas_data:
            return 0.0
        
        # Calculate efficiency based on gas usage patterns
        total_transactions = len(gas_data)
        efficient_transactions = sum(1 for entry in gas_data if entry["gas_used"] < 50000)  # Efficient threshold
        
        efficiency_ratio = efficient_transactions / total_transactions if total_transactions > 0 else 0
        
        # Factor in gas price optimization
        gas_prices = [entry["gas_price"] for entry in gas_data]
        avg_price = statistics.mean(gas_prices)
        network_avg = 25.0  # Assume network average
        
        price_efficiency = min(network_avg / avg_price, 1.5) if avg_price > 0 else 1.0
        
        return min((efficiency_ratio * 0.6 + (price_efficiency - 1) * 0.4 + 0.4), 1.0)
    
    async def _generate_gas_optimization_recommendations(self, gas_data: List[Dict[str, Any]]) -> List[str]:
        """Generate gas optimization recommendations"""
        recommendations = []
        
        if not gas_data:
            return ["Insufficient data for recommendations"]
        
        # Analyze gas usage patterns
        gas_prices = [entry["gas_price"] for entry in gas_data]
        gas_used = [entry["gas_used"] for entry in gas_data]
        
        avg_gas_price = statistics.mean(gas_prices)
        avg_gas_used = statistics.mean(gas_used)
        
        # High gas price recommendations
        if avg_gas_price > 30:
            recommendations.append("Consider using lower gas prices during off-peak hours")
            recommendations.append("Implement gas price monitoring and dynamic adjustment")
        
        # High gas usage recommendations
        if avg_gas_used > 100000:
            recommendations.append("Optimize smart contract functions to reduce gas consumption")
            recommendations.append("Consider batching multiple operations into single transactions")
        
        # General recommendations
        recommendations.extend([
            "Use gas estimation tools before submitting transactions",
            "Monitor network congestion and adjust timing accordingly",
            "Consider Layer 2 solutions for high-frequency operations"
        ])
        
        return recommendations
    
    async def _calculate_cost_savings_potential(self, gas_data: List[Dict[str, Any]]) -> Decimal:
        """Calculate potential cost savings from optimization"""
        if not gas_data:
            return Decimal('0')
        
        # Current costs
        current_costs = sum(entry["gas_price"] * entry["gas_used"] for entry in gas_data)
        
        # Optimized costs (assume 20% reduction)
        optimized_costs = current_costs * 0.8
        
        savings = current_costs - optimized_costs
        return Decimal(str(savings / 1e9))  # Convert to ETH
    
    async def _identify_peak_gas_usage_times(self, gas_data: List[Dict[str, Any]]) -> List[datetime]:
        """Identify peak gas usage times"""
        if not gas_data:
            return []
        
        # Sort by gas price (higher prices indicate higher demand/usage)
        sorted_data = sorted(gas_data, key=lambda x: x["gas_price"], reverse=True)
        
        # Return top 3 peak times
        return [entry["timestamp"] for entry in sorted_data[:3]]
    
    async def _get_current_gas_prices(self) -> Dict[str, Any]:
        """Get current gas price data"""
        # Mock implementation - would connect to gas price APIs
        return {
            "average_price": 25.0,
            "fast_price": 35.0,
            "slow_price": 20.0,
            "congestion_level": "medium",
            "price_trend": "stable",
            "eth_price_usd": 2000.0
        }
    
    def _get_default_gas_analytics(self, timeframe: AnalyticsTimeframe) -> GasAnalytics:
        """Get default gas analytics when no data available"""
        return GasAnalytics(
            timeframe=timeframe,
            average_gas_price=Decimal('25.0'),
            median_gas_price=Decimal('24.0'),
            gas_price_volatility=0.1,
            total_gas_consumed=0,
            gas_efficiency_score=0.0,
            optimization_recommendations=["Insufficient data for analysis"],
            cost_savings_potential=Decimal('0'),
            peak_usage_times=[]
        )


class RevenueAnalyticsTracker:
    """Comprehensive revenue tracking and analytics"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
    async def track_revenue_metrics(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY) -> RevenueMetrics:
        """Track comprehensive revenue metrics"""
        try:
            # Collect revenue data
            revenue_data = await self._collect_revenue_data(timeframe)
            
            # Calculate metrics
            total_revenue = sum(entry.get("amount", 0) for entry in revenue_data)
            revenue_by_source = self._calculate_revenue_by_source(revenue_data)
            revenue_growth_rate = await self._calculate_revenue_growth_rate(timeframe)
            
            # Calculate fee metrics
            fee_data = [entry for entry in revenue_data if entry.get("type") == "fee"]
            average_transaction_fee = statistics.mean([entry.get("amount", 0) for entry in fee_data]) if fee_data else 0
            
            # Calculate efficiency and projections
            fee_efficiency = await self._calculate_fee_efficiency(revenue_data)
            profit_margin = await self._calculate_profit_margin(revenue_data)
            projected_revenue = await self._calculate_projected_revenue(revenue_data, timeframe)
            
            metrics = RevenueMetrics(
                timeframe=timeframe,
                total_revenue=Decimal(str(total_revenue)),
                revenue_by_source=revenue_by_source,
                revenue_growth_rate=revenue_growth_rate,
                average_transaction_fee=Decimal(str(average_transaction_fee)),
                fee_efficiency=fee_efficiency,
                profit_margin=profit_margin,
                projected_revenue=Decimal(str(projected_revenue))
            )
            
            # Store metrics
            await self._store_revenue_metrics(metrics)
            
            logger.info(f"Revenue metrics tracked for {timeframe.value}: {total_revenue} total revenue")
            return metrics
            
        except Exception as e:
            logger.error(f"Revenue tracking failed: {str(e)}")
            raise
    
    async def _collect_revenue_data(self, timeframe: AnalyticsTimeframe) -> List[Dict[str, Any]]:
        """Collect revenue data for specified timeframe"""
        # Mock implementation - would collect from actual revenue sources
        return [
            {"amount": 5.2, "source": "transaction_fees", "type": "fee", "timestamp": datetime.utcnow()},
            {"amount": 12.8, "source": "nft_royalties", "type": "royalty", "timestamp": datetime.utcnow()},
            {"amount": 3.5, "source": "staking_fees", "type": "fee", "timestamp": datetime.utcnow()},
            {"amount": 8.1, "source": "marketplace_fees", "type": "fee", "timestamp": datetime.utcnow()}
        ]
    
    def _calculate_revenue_by_source(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """Calculate revenue breakdown by source"""
        revenue_by_source = defaultdict(Decimal)
        
        for entry in revenue_data:
            source = entry.get("source", "unknown")
            amount = entry.get("amount", 0)
            revenue_by_source[source] += Decimal(str(amount))
        
        return dict(revenue_by_source)
    
    async def _calculate_revenue_growth_rate(self, timeframe: AnalyticsTimeframe) -> float:
        """Calculate revenue growth rate"""
        # Mock implementation - would compare with previous period
        return 0.15  # 15% growth
    
    async def _calculate_fee_efficiency(self, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculate fee collection efficiency"""
        # Mock implementation - ratio of collected to potential fees
        return 0.85  # 85% efficiency
    
    async def _calculate_profit_margin(self, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculate profit margin"""
        total_revenue = sum(entry.get("amount", 0) for entry in revenue_data)
        estimated_costs = total_revenue * 0.3  # Assume 30% costs
        profit_margin = (total_revenue - estimated_costs) / total_revenue if total_revenue > 0 else 0
        return profit_margin
    
    async def _calculate_projected_revenue(self, revenue_data: List[Dict[str, Any]], 
                                         timeframe: AnalyticsTimeframe) -> float:
        """Calculate projected revenue for next period"""
        current_revenue = sum(entry.get("amount", 0) for entry in revenue_data)
        growth_rate = await self._calculate_revenue_growth_rate(timeframe)
        return current_revenue * (1 + growth_rate)
    
    async def _store_revenue_metrics(self, metrics: RevenueMetrics) -> None:
        """Store revenue metrics in database"""
        # Implementation for storing metrics
        pass


class AnalyticsTracker:
    """Main blockchain analytics coordination system"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db = db_session
        self.redis = redis_client
        
        # Initialize sub-analyzers
        self.transaction_analyzer = TransactionFlowAnalyzer(db_session, redis_client)
        self.wallet_analyzer = WalletBehaviorAnalyzer(db_session, redis_client)
        self.gas_analyzer = GasOptimizationAnalytics(redis_client)
        self.revenue_tracker = RevenueAnalyticsTracker(db_session, redis_client)
    
    async def generate_comprehensive_report(self, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            report = {
                "report_id": str(uuid4()),
                "timeframe": timeframe.value,
                "generated_at": datetime.utcnow().isoformat(),
                "executive_summary": {},
                "detailed_analytics": {}
            }
            
            # Collect all analytics
            tasks = [
                self.gas_analyzer.analyze_gas_patterns(timeframe),
                self.revenue_tracker.track_revenue_metrics(timeframe),
                self._get_transaction_summary(timeframe),
                self._get_wallet_summary(timeframe)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            gas_analytics = results[0] if not isinstance(results[0], Exception) else None
            revenue_metrics = results[1] if not isinstance(results[1], Exception) else None
            transaction_summary = results[2] if not isinstance(results[2], Exception) else {}
            wallet_summary = results[3] if not isinstance(results[3], Exception) else {}
            
            # Build report
            report["detailed_analytics"] = {
                "gas_analytics": gas_analytics.__dict__ if gas_analytics else {},
                "revenue_metrics": revenue_metrics.__dict__ if revenue_metrics else {},
                "transaction_summary": transaction_summary,
                "wallet_summary": wallet_summary
            }
            
            # Generate executive summary
            report["executive_summary"] = await self._generate_executive_summary(
                gas_analytics, revenue_metrics, transaction_summary, wallet_summary
            )
            
            # Store report
            await self._store_analytics_report(report)
            
            logger.info(f"Comprehensive analytics report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {str(e)}")
            raise
    
    async def _get_transaction_summary(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Get transaction summary for timeframe"""
        # Mock implementation
        return {
            "total_transactions": 1250,
            "total_volume": 45.8,
            "average_transaction_value": 0.037,
            "success_rate": 0.98
        }
    
    async def _get_wallet_summary(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Get wallet activity summary for timeframe"""
        # Mock implementation
        return {
            "active_wallets": 850,
            "new_wallets": 75,
            "average_activity_score": 0.65,
            "behavior_distribution": {
                "traders": 45,
                "collectors": 25,
                "hodlers": 20,
                "whales": 5,
                "others": 5
            }
        }
    
    async def _generate_executive_summary(self, gas_analytics: Optional[GasAnalytics],
                                        revenue_metrics: Optional[RevenueMetrics],
                                        transaction_summary: Dict[str, Any],
                                        wallet_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from analytics"""
        summary = {
            "key_metrics": {},
            "performance_indicators": {},
            "recommendations": [],
            "alerts": []
        }
        
        # Key metrics
        if revenue_metrics:
            summary["key_metrics"]["total_revenue"] = str(revenue_metrics.total_revenue)
            summary["key_metrics"]["revenue_growth"] = f"{revenue_metrics.revenue_growth_rate:.1%}"
        
        if gas_analytics:
            summary["key_metrics"]["gas_efficiency"] = f"{gas_analytics.gas_efficiency_score:.1%}"
            summary["key_metrics"]["cost_savings_potential"] = str(gas_analytics.cost_savings_potential)
        
        # Performance indicators
        summary["performance_indicators"]["transaction_success_rate"] = transaction_summary.get("success_rate", 0)
        summary["performance_indicators"]["wallet_activity"] = wallet_summary.get("average_activity_score", 0)
        
        # Recommendations
        if gas_analytics and gas_analytics.gas_efficiency_score < 0.7:
            summary["recommendations"].append("Focus on gas optimization strategies")
        
        if revenue_metrics and revenue_metrics.revenue_growth_rate < 0.1:
            summary["recommendations"].append("Investigate revenue growth opportunities")
        
        return summary
    
    async def _store_analytics_report(self, report: Dict[str, Any]) -> None:
        """Store analytics report"""
        # Store in Redis for quick access
        cache_key = f"analytics_report:{report['report_id']}"
        await self.redis.setex(cache_key, 86400 * 7, json.dumps(report, default=str))  # 7 days


class ChainAnalytics:
    """High-level blockchain analytics interface"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.tracker = AnalyticsTracker(db_session, redis_client)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time blockchain metrics"""
        return await self.tracker.generate_comprehensive_report(AnalyticsTimeframe.REAL_TIME)
    
    async def get_daily_analytics(self) -> Dict[str, Any]:
        """Get daily analytics report"""
        return await self.tracker.generate_comprehensive_report(AnalyticsTimeframe.DAILY)
    
    async def get_performance_insights(self, days: int = 30) -> Dict[str, Any]:
        """Get performance insights over specified period"""
        # Implementation for multi-day analysis
        return await self.tracker.generate_comprehensive_report(AnalyticsTimeframe.MONTHLY)


# Export main classes
__all__ = [
    "AnalyticsTracker",
    "ChainAnalytics",
    "TransactionFlowAnalyzer",
    "WalletBehaviorAnalyzer", 
    "GasOptimizationAnalytics",
    "RevenueAnalyticsTracker",
    "AnalyticsTimeframe",
    "TransactionType",
    "WalletBehaviorType",
    "MetricType",
    "TransactionAnalysis",
    "WalletProfile",
    "GasAnalytics",
    "RevenueMetrics"
]
