"""Influencer Trading Platform
============================

Advanced influencer trading engine for the IA Influencer Agent platform,
enabling influencer profile trading, collaboration contracts, and
performance-based asset exchanges.

Features:
- Influencer profile tokenization and trading
- Performance-based valuation and pricing
- Smart contract automation for collaborations
- Reputation and social metrics tracking
- Risk assessment and fraud prevention

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
import json
import hashlib

logger = logging.getLogger(__name__)

class AssetType(Enum):
    """Trading asset type enumeration"""
    INFLUENCER_PROFILE = "influencer_profile"
    COLLABORATION_CONTRACT = "collaboration_contract"
    CONTENT_RIGHTS = "content_rights"
    AUDIENCE_ACCESS = "audience_access"
    BRAND_PARTNERSHIP = "brand_partnership"
    PERFORMANCE_METRIC = "performance_metric"
    SOCIAL_CURRENCY = "social_currency"

class TradingStatus(Enum):
    """Trading transaction status"""
    DRAFT = "draft"
    LISTED = "listed"
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class MarketRole(Enum):
    """Market participant role"""
    BUYER = "buyer"
    SELLER = "seller"
    MARKET_MAKER = "market_maker"
    BROKER = "broker"
    VALIDATOR = "validator"
    ARBITRATOR = "arbitrator"

class RiskLevel(Enum):
    """Risk assessment level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class InfluencerMetrics:
    """Influencer performance metrics"""
    follower_count: int
    engagement_rate: Decimal
    reach_per_post: int
    average_likes: int
    average_comments: int
    average_shares: int
    brand_safety_score: Decimal
    audience_quality_score: Decimal
    growth_rate_monthly: Decimal
    collaboration_completion_rate: Decimal
    response_time_hours: Decimal
    content_quality_score: Decimal
    niche_authority_score: Decimal
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_influence_score(self) -> Decimal:
        """Calculate overall influence score"""
        weights = {
            'engagement': Decimal('0.25'),
            'reach': Decimal('0.20'),
            'quality': Decimal('0.20'),
            'reliability': Decimal('0.15'),
            'growth': Decimal('0.10'),
            'safety': Decimal('0.10')
        }
        
        # Normalize metrics to 0-100 scale
        normalized_engagement = min(self.engagement_rate, Decimal('20.0')) * Decimal('5.0')
        normalized_reach = min(Decimal(str(self.reach_per_post / 1000)), Decimal('100.0'))
        normalized_quality = self.content_quality_score
        normalized_reliability = self.collaboration_completion_rate
        normalized_growth = min(self.growth_rate_monthly * Decimal('10.0'), Decimal('100.0'))
        normalized_safety = self.brand_safety_score
        
        influence_score = (
            normalized_engagement * weights['engagement'] +
            normalized_reach * weights['reach'] +
            normalized_quality * weights['quality'] +
            normalized_reliability * weights['reliability'] +
            normalized_growth * weights['growth'] +
            normalized_safety * weights['safety']
        )
        
        return min(influence_score, Decimal('100.0'))

@dataclass
class TradableAsset:
    """Tradable influencer asset"""
    asset_id: str
    asset_type: AssetType
    owner_id: str
    title: str
    description: str
    base_value: Decimal
    current_price: Decimal
    currency: str = "USD"
    metrics: Optional[InfluencerMetrics] = None
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    terms_and_conditions: Dict[str, Any] = field(default_factory=dict)
    expiration_date: Optional[datetime] = None
    transferable: bool = True
    divisible: bool = False
    minimum_trade_amount: Decimal = Decimal('1.0')
    risk_level: RiskLevel = RiskLevel.MEDIUM
    compliance_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_market_value(self) -> Decimal:
        """Calculate current market value based on metrics"""
        if not self.metrics:
            return self.base_value
        
        influence_score = self.metrics.calculate_influence_score()
        
        # Value multiplier based on influence score
        multiplier = Decimal('1.0') + (influence_score / Decimal('100.0'))
        
        # Apply risk adjustment
        risk_adjustments = {
            RiskLevel.LOW: Decimal('1.1'),
            RiskLevel.MEDIUM: Decimal('1.0'),
            RiskLevel.HIGH: Decimal('0.9'),
            RiskLevel.CRITICAL: Decimal('0.7')
        }
        
        risk_multiplier = risk_adjustments.get(self.risk_level, Decimal('1.0'))
        
        return (self.base_value * multiplier * risk_multiplier).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

@dataclass
class TradingTransaction:
    """Trading transaction record"""
    transaction_id: str
    asset_id: str
    buyer_id: str
    seller_id: str
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    currency: str = "USD"
    status: TradingStatus = TradingStatus.DRAFT
    negotiation_terms: Dict[str, Any] = field(default_factory=dict)
    execution_date: Optional[datetime] = None
    settlement_date: Optional[datetime] = None
    commission_rate: Decimal = Decimal('5.0')  # 5% default commission
    escrow_amount: Decimal = Decimal('0.00')
    performance_bond: Decimal = Decimal('0.00')
    smart_contract_hash: Optional[str] = None
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    compliance_check: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_total_cost(self) -> Decimal:
        """Calculate total cost including fees"""
        commission = self.total_amount * (self.commission_rate / Decimal('100'))
        return self.total_amount + commission + self.escrow_amount + self.performance_bond

@dataclass
class MarketOrder:
    """Market order for trading"""
    order_id: str
    user_id: str
    asset_id: str
    order_type: str  # "buy" or "sell"
    quantity: Decimal
    price_limit: Optional[Decimal] = None
    order_mode: str = "market"  # "market" or "limit"
    time_in_force: str = "GTC"  # "GTC", "IOC", "FOK"
    status: str = "active"
    filled_quantity: Decimal = Decimal('0.0')
    average_fill_price: Decimal = Decimal('0.0')
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class RiskAssessment:
    """Risk assessment engine for trading"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize risk assessment"""
        self.config = config or {}
        self.risk_thresholds = {
            'high_value_transaction': Decimal('10000.0'),
            'new_trader_limit': Decimal('1000.0'),
            'volatility_threshold': Decimal('20.0'),
            'liquidity_threshold': Decimal('0.1')
        }
    
    async def assess_transaction_risk(
        self, 
        transaction: TradingTransaction, 
        asset: TradableAsset,
        trader_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for trading transaction"""
        risk_factors = []
        risk_score = 0
        
        try:
            # High value transaction risk
            if transaction.total_amount > self.risk_thresholds['high_value_transaction']:
                risk_factors.append("High value transaction")
                risk_score += 20
            
            # New trader risk
            if trader_history.get('total_trades', 0) < 5:
                risk_factors.append("Limited trading history")
                risk_score += 15
            
            # Asset volatility risk
            if asset.performance_history:
                price_changes = [
                    float(record.get('price_change_percentage', 0))
                    for record in asset.performance_history[-10:]  # Last 10 records
                ]
                if price_changes:
                    volatility = Decimal(str(abs(sum(price_changes) / len(price_changes))))
                    if volatility > self.risk_thresholds['volatility_threshold']:
                        risk_factors.append("High asset volatility")
                        risk_score += 25
            
            # Compliance risk
            if not asset.compliance_data.get('verified', False):
                risk_factors.append("Unverified asset compliance")
                risk_score += 10
            
            # Determine risk level
            if risk_score >= 50:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 30:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 15:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            return {
                "risk_level": risk_level.value,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "recommended_actions": self._get_risk_recommendations(risk_level),
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                "risk_level": RiskLevel.CRITICAL.value,
                "risk_score": 100,
                "risk_factors": [f"Assessment error: {e}"],
                "recommended_actions": ["Manual review required"],
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_risk_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """Get recommendations based on risk level"""
        recommendations = {
            RiskLevel.LOW: ["Standard processing"],
            RiskLevel.MEDIUM: ["Enhanced verification", "Monitor transaction"],
            RiskLevel.HIGH: ["Manual review required", "Enhanced escrow", "Additional verification"],
            RiskLevel.CRITICAL: ["Manual approval required", "Maximum escrow", "Legal review", "Identity verification"]
        }
        
        return recommendations.get(risk_level, ["Manual review required"])

class MarketMaker:
    """Market making engine for liquidity provision"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize market maker"""
        self.config = config or {}
        self.spread_percentage = Decimal(str(self.config.get('spread_percentage', '2.0')))
        self.max_position_size = Decimal(str(self.config.get('max_position_size', '100000.0')))
        self.inventory_target = Decimal(str(self.config.get('inventory_target', '50.0')))
        
        self.positions: Dict[str, Decimal] = {}  # asset_id -> quantity
        self.quotes: Dict[str, Dict[str, Decimal]] = {}  # asset_id -> {bid, ask}
    
    async def provide_liquidity(self, asset_id: str, current_price: Decimal) -> Dict[str, Decimal]:
        """Provide liquidity by quoting bid/ask prices"""
        try:
            spread = current_price * (self.spread_percentage / Decimal('100'))
            
            bid_price = current_price - (spread / Decimal('2'))
            ask_price = current_price + (spread / Decimal('2'))
            
            self.quotes[asset_id] = {
                'bid': bid_price,
                'ask': ask_price,
                'mid': current_price,
                'spread': spread,
                'timestamp': Decimal(str(datetime.utcnow().timestamp()))
            }
            
            return self.quotes[asset_id]
            
        except Exception as e:
            logger.error(f"Failed to provide liquidity for {asset_id}: {e}")
            return {}
    
    async def execute_market_making_trade(
        self, 
        asset_id: str, 
        side: str, 
        quantity: Decimal, 
        price: Decimal
    ) -> bool:
        """Execute market making trade"""
        try:
            current_position = self.positions.get(asset_id, Decimal('0'))
            
            if side == "buy":
                new_position = current_position + quantity
            else:
                new_position = current_position - quantity
            
            # Check position limits
            if abs(new_position) > self.max_position_size:
                return False
            
            self.positions[asset_id] = new_position
            
            logger.info(f"Market maker executed {side} of {quantity} {asset_id} at {price}")
            return True
            
        except Exception as e:
            logger.error(f"Market making trade failed: {e}")
            return False

class InfluencerTradingEngine:
    """Core influencer trading engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize trading engine"""
        self.config = config or {}
        
        # Core components
        self.assets: Dict[str, TradableAsset] = {}
        self.transactions: Dict[str, TradingTransaction] = {}
        self.orders: Dict[str, MarketOrder] = {}
        self.user_portfolios: Dict[str, Dict[str, Decimal]] = {}
        
        # Trading components
        self.risk_assessor = RiskAssessment(self.config.get('risk_assessment', {}))
        self.market_maker = MarketMaker(self.config.get('market_maker', {}))
        
        # Configuration
        self.trading_enabled = self.config.get('trading_enabled', True)
        self.max_transaction_size = Decimal(str(self.config.get('max_transaction_size', '1000000.0')))
        self.minimum_trade_amount = Decimal(str(self.config.get('minimum_trade_amount', '1.0')))
        
        logger.info("🎯 Influencer Trading Engine initialized")
    
    async def initialize(self) -> None:
        """Initialize trading engine"""
        logger.info("🚀 Initializing Influencer Trading Engine")
        
        # Start background tasks
        asyncio.create_task(self._order_matching_engine())
        asyncio.create_task(self._market_data_updater())
        asyncio.create_task(self._risk_monitor())
    
    async def create_tradable_asset(self, asset_data: Dict[str, Any]) -> TradableAsset:
        """Create new tradable asset"""
        try:
            asset_id = str(uuid.uuid4())
            
            # Parse metrics if provided
            metrics = None
            if 'metrics' in asset_data:
                metrics_data = asset_data['metrics']
                metrics = InfluencerMetrics(
                    follower_count=metrics_data.get('follower_count', 0),
                    engagement_rate=Decimal(str(metrics_data.get('engagement_rate', '0.0'))),
                    reach_per_post=metrics_data.get('reach_per_post', 0),
                    average_likes=metrics_data.get('average_likes', 0),
                    average_comments=metrics_data.get('average_comments', 0),
                    average_shares=metrics_data.get('average_shares', 0),
                    brand_safety_score=Decimal(str(metrics_data.get('brand_safety_score', '100.0'))),
                    audience_quality_score=Decimal(str(metrics_data.get('audience_quality_score', '100.0'))),
                    growth_rate_monthly=Decimal(str(metrics_data.get('growth_rate_monthly', '0.0'))),
                    collaboration_completion_rate=Decimal(str(metrics_data.get('collaboration_completion_rate', '100.0'))),
                    response_time_hours=Decimal(str(metrics_data.get('response_time_hours', '24.0'))),
                    content_quality_score=Decimal(str(metrics_data.get('content_quality_score', '100.0'))),
                    niche_authority_score=Decimal(str(metrics_data.get('niche_authority_score', '100.0')))
                )
            
            asset = TradableAsset(
                asset_id=asset_id,
                asset_type=AssetType(asset_data['asset_type']),
                owner_id=asset_data['owner_id'],
                title=asset_data['title'],
                description=asset_data['description'],
                base_value=Decimal(str(asset_data['base_value'])),
                current_price=Decimal(str(asset_data.get('current_price', asset_data['base_value']))),
                currency=asset_data.get('currency', 'USD'),
                metrics=metrics,
                terms_and_conditions=asset_data.get('terms_and_conditions', {}),
                expiration_date=asset_data.get('expiration_date'),
                transferable=asset_data.get('transferable', True),
                divisible=asset_data.get('divisible', False),
                minimum_trade_amount=Decimal(str(asset_data.get('minimum_trade_amount', '1.0'))),
                risk_level=RiskLevel(asset_data.get('risk_level', 'medium')),
                compliance_data=asset_data.get('compliance_data', {}),
                metadata=asset_data.get('metadata', {})
            )
            
            # Update current price based on metrics
            asset.current_price = asset.calculate_market_value()
            
            self.assets[asset_id] = asset
            
            # Initialize user portfolio
            if asset.owner_id not in self.user_portfolios:
                self.user_portfolios[asset.owner_id] = {}
            
            self.user_portfolios[asset.owner_id][asset_id] = Decimal('1.0') if not asset.divisible else Decimal(str(asset_data.get('initial_quantity', '1.0')))
            
            logger.info(f"Created tradable asset: {asset_id} - {asset.title}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to create tradable asset: {e}")
            raise
    
    async def create_trade(self, trade_data: Dict[str, Any]) -> TradingTransaction:
        """Create new trading transaction"""
        try:
            if not self.trading_enabled:
                raise ValueError("Trading is currently disabled")
            
            transaction_id = str(uuid.uuid4())
            asset_id = trade_data['asset_id']
            
            if asset_id not in self.assets:
                raise ValueError(f"Asset {asset_id} not found")
            
            asset = self.assets[asset_id]
            quantity = Decimal(str(trade_data['quantity']))
            unit_price = Decimal(str(trade_data['unit_price']))
            total_amount = quantity * unit_price
            
            # Validate trade
            await self._validate_trade(trade_data, asset, total_amount)
            
            transaction = TradingTransaction(
                transaction_id=transaction_id,
                asset_id=asset_id,
                buyer_id=trade_data['buyer_id'],
                seller_id=trade_data['seller_id'],
                quantity=quantity,
                unit_price=unit_price,
                total_amount=total_amount,
                currency=trade_data.get('currency', 'USD'),
                negotiation_terms=trade_data.get('negotiation_terms', {}),
                commission_rate=Decimal(str(trade_data.get('commission_rate', '5.0'))),
                escrow_amount=Decimal(str(trade_data.get('escrow_amount', '0.0'))),
                performance_bond=Decimal(str(trade_data.get('performance_bond', '0.0')))
            )
            
            # Risk assessment
            trader_history = await self._get_trader_history(transaction.buyer_id)
            risk_assessment = await self.risk_assessor.assess_transaction_risk(
                transaction, asset, trader_history
            )
            transaction.risk_assessment = risk_assessment
            
            # Generate smart contract hash
            transaction.smart_contract_hash = self._generate_contract_hash(transaction)
            
            self.transactions[transaction_id] = transaction
            
            logger.info(f"Created trade: {transaction_id} - {asset.title}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to create trade: {e}")
            raise
    
    async def execute_trade(self, transaction_id: str) -> bool:
        """Execute trading transaction"""
        try:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            transaction = self.transactions[transaction_id]
            asset = self.assets[transaction.asset_id]
            
            if transaction.status != TradingStatus.AGREED:
                raise ValueError("Transaction must be agreed before execution")
            
            # Check seller has sufficient quantity
            seller_portfolio = self.user_portfolios.get(transaction.seller_id, {})
            seller_quantity = seller_portfolio.get(transaction.asset_id, Decimal('0'))
            
            if seller_quantity < transaction.quantity:
                raise ValueError("Insufficient asset quantity for sale")
            
            # Execute transfer
            transaction.status = TradingStatus.EXECUTING
            
            # Update portfolios
            if transaction.buyer_id not in self.user_portfolios:
                self.user_portfolios[transaction.buyer_id] = {}
            
            # Transfer assets
            seller_portfolio[transaction.asset_id] -= transaction.quantity
            self.user_portfolios[transaction.buyer_id][transaction.asset_id] = (
                self.user_portfolios[transaction.buyer_id].get(transaction.asset_id, Decimal('0')) + transaction.quantity
            )
            
            # Update asset ownership if fully transferred
            if seller_portfolio[transaction.asset_id] == Decimal('0') and not asset.divisible:
                asset.owner_id = transaction.buyer_id
            
            # Complete transaction
            transaction.status = TradingStatus.COMPLETED
            transaction.execution_date = datetime.utcnow()
            transaction.settlement_date = datetime.utcnow() + timedelta(days=1)  # T+1 settlement
            
            logger.info(f"Executed trade: {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            transaction.status = TradingStatus.DISPUTED
            return False
    
    async def get_market_data(self, asset_id: str) -> Dict[str, Any]:
        """Get market data for asset"""
        try:
            if asset_id not in self.assets:
                return {"error": "Asset not found"}
            
            asset = self.assets[asset_id]
            
            # Get recent transactions
            recent_transactions = [
                t for t in self.transactions.values()
                if t.asset_id == asset_id and t.status == TradingStatus.COMPLETED
                and (datetime.utcnow() - t.execution_date).days <= 30
            ]
            
            # Calculate market metrics
            if recent_transactions:
                recent_prices = [float(t.unit_price) for t in recent_transactions]
                volume = sum(float(t.quantity) for t in recent_transactions)
                
                market_data = {
                    "asset_id": asset_id,
                    "current_price": float(asset.current_price),
                    "market_value": float(asset.calculate_market_value()),
                    "last_trade_price": recent_prices[-1] if recent_prices else float(asset.current_price),
                    "price_change_24h": recent_prices[-1] - recent_prices[0] if len(recent_prices) > 1 else 0,
                    "volume_30d": volume,
                    "num_trades_30d": len(recent_transactions),
                    "high_30d": max(recent_prices) if recent_prices else float(asset.current_price),
                    "low_30d": min(recent_prices) if recent_prices else float(asset.current_price),
                    "market_cap": float(asset.calculate_market_value()) * float(self._get_total_supply(asset_id)),
                    "liquidity_score": self._calculate_liquidity_score(asset_id),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                market_data = {
                    "asset_id": asset_id,
                    "current_price": float(asset.current_price),
                    "market_value": float(asset.calculate_market_value()),
                    "last_trade_price": float(asset.current_price),
                    "price_change_24h": 0,
                    "volume_30d": 0,
                    "num_trades_30d": 0,
                    "high_30d": float(asset.current_price),
                    "low_30d": float(asset.current_price),
                    "market_cap": float(asset.calculate_market_value()),
                    "liquidity_score": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Add market maker quotes if available
            quotes = await self.market_maker.provide_liquidity(asset_id, asset.current_price)
            if quotes:
                market_data.update({
                    "bid": float(quotes['bid']),
                    "ask": float(quotes['ask']),
                    "spread": float(quotes['spread'])
                })
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return {"error": f"Market data unavailable: {e}"}
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's trading portfolio"""
        try:
            portfolio = self.user_portfolios.get(user_id, {})
            
            portfolio_data = {
                "user_id": user_id,
                "assets": [],
                "total_value": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            total_value = Decimal('0.0')
            
            for asset_id, quantity in portfolio.items():
                if asset_id in self.assets:
                    asset = self.assets[asset_id]
                    market_value = asset.calculate_market_value()
                    position_value = quantity * market_value
                    total_value += position_value
                    
                    portfolio_data["assets"].append({
                        "asset_id": asset_id,
                        "title": asset.title,
                        "asset_type": asset.asset_type.value,
                        "quantity": float(quantity),
                        "unit_price": float(market_value),
                        "position_value": float(position_value),
                        "currency": asset.currency
                    })
            
            portfolio_data["total_value"] = float(total_value)
            
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Failed to get user portfolio: {e}")
            return {"error": f"Portfolio unavailable: {e}"}
    
    async def _validate_trade(self, trade_data: Dict[str, Any], asset: TradableAsset, total_amount: Decimal) -> None:
        """Validate trade parameters"""
        # Check trading limits
        if total_amount > self.max_transaction_size:
            raise ValueError(f"Transaction size exceeds limit: {total_amount}")
        
        if total_amount < self.minimum_trade_amount:
            raise ValueError(f"Transaction size below minimum: {total_amount}")
        
        # Check asset transferability
        if not asset.transferable:
            raise ValueError("Asset is not transferable")
        
        # Check minimum trade amount for asset
        quantity = Decimal(str(trade_data['quantity']))
        if quantity < asset.minimum_trade_amount:
            raise ValueError(f"Quantity below asset minimum: {asset.minimum_trade_amount}")
        
        # Check expiration
        if asset.expiration_date and datetime.utcnow() > asset.expiration_date:
            raise ValueError("Asset has expired")
    
    async def _get_trader_history(self, user_id: str) -> Dict[str, Any]:
        """Get trader's historical data"""
        user_transactions = [
            t for t in self.transactions.values()
            if t.buyer_id == user_id or t.seller_id == user_id
        ]
        
        completed_transactions = [
            t for t in user_transactions
            if t.status == TradingStatus.COMPLETED
        ]
        
        return {
            "total_trades": len(user_transactions),
            "completed_trades": len(completed_transactions),
            "total_volume": sum(float(t.total_amount) for t in completed_transactions),
            "success_rate": len(completed_transactions) / len(user_transactions) if user_transactions else 1.0,
            "account_age_days": 30  # Placeholder
        }
    
    def _generate_contract_hash(self, transaction: TradingTransaction) -> str:
        """Generate smart contract hash"""
        contract_data = {
            "transaction_id": transaction.transaction_id,
            "asset_id": transaction.asset_id,
            "buyer_id": transaction.buyer_id,
            "seller_id": transaction.seller_id,
            "quantity": str(transaction.quantity),
            "unit_price": str(transaction.unit_price),
            "timestamp": transaction.created_at.isoformat()
        }
        
        contract_string = json.dumps(contract_data, sort_keys=True)
        return hashlib.sha256(contract_string.encode()).hexdigest()
    
    def _get_total_supply(self, asset_id: str) -> Decimal:
        """Get total supply of asset"""
        total = Decimal('0')
        for portfolio in self.user_portfolios.values():
            total += portfolio.get(asset_id, Decimal('0'))
        return total
    
    def _calculate_liquidity_score(self, asset_id: str) -> float:
        """Calculate liquidity score for asset"""
        # Simple liquidity score based on trading activity
        recent_transactions = [
            t for t in self.transactions.values()
            if t.asset_id == asset_id and t.status == TradingStatus.COMPLETED
            and (datetime.utcnow() - t.execution_date).days <= 7
        ]
        
        return min(len(recent_transactions) * 10, 100)  # Score 0-100
    
    async def _order_matching_engine(self) -> None:
        """Background order matching"""
        while True:
            try:
                # Match orders logic would go here
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in order matching: {e}")
                await asyncio.sleep(10)
    
    async def _market_data_updater(self) -> None:
        """Background market data updates"""
        while True:
            try:
                # Update market prices based on trading activity
                for asset_id, asset in self.assets.items():
                    new_price = asset.calculate_market_value()
                    if new_price != asset.current_price:
                        asset.current_price = new_price
                        asset.updated_at = datetime.utcnow()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating market data: {e}")
                await asyncio.sleep(300)
    
    async def _risk_monitor(self) -> None:
        """Background risk monitoring"""
        while True:
            try:
                # Monitor for high-risk transactions
                for transaction in self.transactions.values():
                    if (transaction.status in [TradingStatus.PENDING, TradingStatus.NEGOTIATING] and
                        transaction.risk_assessment.get('risk_level') == 'critical'):
                        logger.warning(f"High-risk transaction detected: {transaction.transaction_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in risk monitoring: {e}")
                await asyncio.sleep(600)


# Export main classes
__all__ = [
    "AssetType",
    "TradingStatus",
    "MarketRole",
    "RiskLevel",
    "InfluencerMetrics",
    "TradableAsset",
    "TradingTransaction",
    "MarketOrder",
    "RiskAssessment",
    "MarketMaker",
    "InfluencerTradingEngine"
]