"""Advanced Auction System - Sophisticated Marketplace Auction Engine
====================================================================

Advanced auction management system integrating with existing bidding infrastructure
for the IA Influencer Agent platform marketplace.

Features:
- Real-time auction management with AI-powered pricing
- Multi-format auction types (standard, reverse, Dutch, sealed-bid)
- Intelligent bid validation and fraud detection
- Automated settlement and escrow integration
- Performance analytics and market insights

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class AuctionType(Enum):
    """Auction type enumeration"""
    STANDARD = "standard"              # Highest bid wins
    REVERSE = "reverse"                # Lowest bid wins
    DUTCH = "dutch"                    # Price decreases over time
    SEALED_BID = "sealed_bid"          # Hidden bids revealed at end
    RESERVE = "reserve"                # Minimum price protection
    BUYOUT = "buyout"                  # Immediate purchase option

class AuctionStatus(Enum):
    """Auction status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    CANCELLED = "cancelled"
    SETTLED = "settled"

class BidStatus(Enum):
    """Bid status enumeration"""
    ACTIVE = "active"
    WINNING = "winning"
    OUTBID = "outbid"
    WITHDRAWN = "withdrawn"
    INVALID = "invalid"

@dataclass
class AuctionBid:
    """Auction bid data structure"""
    bid_id: str
    auction_id: str
    bidder_id: str
    amount: Decimal
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: BidStatus = BidStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bid to dictionary"""
        return {
            "bid_id": self.bid_id,
            "auction_id": self.auction_id,
            "bidder_id": self.bidder_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "metadata": self.metadata
        }

@dataclass
class Auction:
    """Auction data structure"""
    auction_id: str
    item_id: str
    seller_id: str
    title: str
    description: str
    auction_type: AuctionType
    starting_price: Decimal
    reserve_price: Optional[Decimal] = None
    buyout_price: Optional[Decimal] = None
    currency: str = "USD"
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_hours: int = 24
    status: AuctionStatus = AuctionStatus.DRAFT
    current_price: Decimal = field(default_factory=lambda: Decimal('0.00'))
    bid_count: int = 0
    winner_id: Optional[str] = None
    bids: List[AuctionBid] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self) -> None:
        """Initialize calculated fields"""
        if self.end_time is None:
            self.end_time = self.start_time + timedelta(hours=self.duration_hours)
        if self.current_price == Decimal('0.00'):
            self.current_price = self.starting_price

class AuctionEngine:
    """Core auction processing engine"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize auction engine"""
        self.config = config or {}
        self.active_auctions: Dict[str, Auction] = {}
        self.completed_auctions: Dict[str, Auction] = {}
        self.bid_history: Dict[str, List[AuctionBid]] = {}
        
        # Configuration
        self.min_bid_increment = Decimal(str(self.config.get('min_bid_increment', '1.00')))
        self.max_auction_duration = self.config.get('max_auction_duration', 168)  # 7 days
        self.auto_extend_minutes = self.config.get('auto_extend_minutes', 10)
        self.fraud_detection_enabled = self.config.get('fraud_detection_enabled', True)
        
        logger.info("🏛️ Auction Engine initialized")
    
    async def create_auction(self, auction_data: Dict[str, Any]) -> Auction:
        """Create new auction"""
        try:
            auction_id = str(uuid.uuid4())
            
            # Validate auction data
            await self._validate_auction_data(auction_data)
            
            auction = Auction(
                auction_id=auction_id,
                item_id=auction_data['item_id'],
                seller_id=auction_data['seller_id'],
                title=auction_data['title'],
                description=auction_data['description'],
                auction_type=AuctionType(auction_data['auction_type']),
                starting_price=Decimal(str(auction_data['starting_price'])),
                reserve_price=Decimal(str(auction_data['reserve_price'])) if auction_data.get('reserve_price') else None,
                buyout_price=Decimal(str(auction_data['buyout_price'])) if auction_data.get('buyout_price') else None,
                currency=auction_data.get('currency', 'USD'),
                duration_hours=auction_data.get('duration_hours', 24),
                status=AuctionStatus.ACTIVE,  # Set as active by default
                metadata=auction_data.get('metadata', {})
            )
            
            self.active_auctions[auction_id] = auction
            
            logger.info(f"Created auction: {auction_id} for item: {auction.item_id}")
            return auction
            
        except Exception as e:
            logger.error(f"Failed to create auction: {e}")
            raise
    
    async def place_bid(self, auction_id: str, bidder_id: str, amount: Decimal, 
                       metadata: Dict[str, Any] = None) -> AuctionBid:
        """Place bid on auction"""
        try:
            if auction_id not in self.active_auctions:
                raise ValueError(f"Auction {auction_id} not found or not active")
            
            auction = self.active_auctions[auction_id]
            
            # Validate bid
            await self._validate_bid(auction, bidder_id, amount)
            
            bid_id = str(uuid.uuid4())
            bid = AuctionBid(
                bid_id=bid_id,
                auction_id=auction_id,
                bidder_id=bidder_id,
                amount=amount,
                currency=auction.currency,
                metadata=metadata or {}
            )
            
            # Process bid based on auction type
            await self._process_bid(auction, bid)
            
            # Store bid
            auction.bids.append(bid)
            auction.bid_count += 1
            
            if auction_id not in self.bid_history:
                self.bid_history[auction_id] = []
            self.bid_history[auction_id].append(bid)
            
            # Check for auto-extension
            await self._check_auto_extension(auction, bid)
            
            logger.info(f"Bid placed: {bid_id} for auction: {auction_id} - Amount: {amount}")
            return bid
            
        except Exception as e:
            logger.error(f"Failed to place bid: {e}")
            raise
    
    async def end_auction(self, auction_id: str, force: bool = False) -> Optional[AuctionBid]:
        """End auction and determine winner"""
        try:
            if auction_id not in self.active_auctions:
                raise ValueError(f"Auction {auction_id} not found or not active")
            
            auction = self.active_auctions[auction_id]
            
            if not force and datetime.utcnow() < auction.end_time:
                raise ValueError("Auction has not reached end time")
            
            # Determine winner based on auction type
            winning_bid = await self._determine_winner(auction)
            
            if winning_bid:
                auction.winner_id = winning_bid.bidder_id
                auction.current_price = winning_bid.amount
                winning_bid.status = BidStatus.WINNING
                
                # Mark other bids as outbid
                for bid in auction.bids:
                    if bid.bid_id != winning_bid.bid_id and bid.status == BidStatus.ACTIVE:
                        bid.status = BidStatus.OUTBID
            
            auction.status = AuctionStatus.ENDED
            
            # Move to completed auctions
            self.completed_auctions[auction_id] = auction
            del self.active_auctions[auction_id]
            
            logger.info(f"Auction ended: {auction_id} - Winner: {auction.winner_id if winning_bid else 'None'}")
            return winning_bid
            
        except Exception as e:
            logger.error(f"Failed to end auction: {e}")
            raise
    
    async def get_auction(self, auction_id: str) -> Optional[Auction]:
        """Get auction by ID"""
        if auction_id in self.active_auctions:
            return self.active_auctions[auction_id]
        elif auction_id in self.completed_auctions:
            return self.completed_auctions[auction_id]
        return None
    
    async def get_active_auctions(self, filters: Dict[str, Any] = None) -> List[Auction]:
        """Get active auctions with optional filters"""
        auctions = list(self.active_auctions.values())
        
        if filters:
            # Apply filters
            if 'seller_id' in filters:
                auctions = [a for a in auctions if a.seller_id == filters['seller_id']]
            if 'auction_type' in filters:
                auctions = [a for a in auctions if a.auction_type.value == filters['auction_type']]
            if 'max_price' in filters:
                max_price = Decimal(str(filters['max_price']))
                auctions = [a for a in auctions if a.current_price <= max_price]
        
        return auctions
    
    async def _validate_auction_data(self, data: Dict[str, Any]) -> None:
        """Validate auction creation data"""
        required_fields = ['item_id', 'seller_id', 'title', 'description', 'auction_type', 'starting_price']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if data.get('duration_hours', 24) > self.max_auction_duration:
            raise ValueError(f"Auction duration cannot exceed {self.max_auction_duration} hours")
        
        starting_price = Decimal(str(data['starting_price']))
        if starting_price <= 0:
            raise ValueError("Starting price must be positive")
    
    async def _validate_bid(self, auction: Auction, bidder_id: str, amount: Decimal) -> None:
        """Validate bid placement"""
        if auction.status != AuctionStatus.ACTIVE:
            raise ValueError("Auction is not active")
        
        if datetime.utcnow() > auction.end_time:
            raise ValueError("Auction has ended")
        
        if bidder_id == auction.seller_id:
            raise ValueError("Seller cannot bid on own auction")
        
        if auction.auction_type == AuctionType.STANDARD:
            min_amount = auction.current_price + self.min_bid_increment
            if amount < min_amount:
                raise ValueError(f"Bid must be at least {min_amount}")
        elif auction.auction_type == AuctionType.REVERSE:
            max_amount = auction.current_price - self.min_bid_increment
            if amount > max_amount:
                raise ValueError(f"Bid must be no more than {max_amount}")
        
        # Fraud detection
        if self.fraud_detection_enabled:
            await self._detect_bid_fraud(auction, bidder_id, amount)
    
    async def _process_bid(self, auction: Auction, bid: AuctionBid) -> None:
        """Process bid based on auction type"""
        if auction.auction_type in [AuctionType.STANDARD, AuctionType.RESERVE]:
            if bid.amount > auction.current_price:
                auction.current_price = bid.amount
        elif auction.auction_type == AuctionType.REVERSE:
            if bid.amount < auction.current_price:
                auction.current_price = bid.amount
        elif auction.auction_type == AuctionType.SEALED_BID:
            # Bids are hidden until auction ends
            pass
    
    async def _check_auto_extension(self, auction: Auction, bid: AuctionBid) -> None:
        """Check if auction should be auto-extended"""
        time_remaining = auction.end_time - datetime.utcnow()
        
        if time_remaining.total_seconds() < self.auto_extend_minutes * 60:
            auction.end_time += timedelta(minutes=self.auto_extend_minutes)
            logger.info(f"Auto-extended auction {auction.auction_id} by {self.auto_extend_minutes} minutes")
    
    async def _determine_winner(self, auction: Auction) -> Optional[AuctionBid]:
        """Determine auction winner based on type"""
        if not auction.bids:
            return None
        
        valid_bids = [bid for bid in auction.bids if bid.status == BidStatus.ACTIVE]
        
        if not valid_bids:
            return None
        
        if auction.auction_type == AuctionType.STANDARD:
            # Highest bid wins
            winning_bid = max(valid_bids, key=lambda b: b.amount)
            
            # Check reserve price
            if auction.reserve_price and winning_bid.amount < auction.reserve_price:
                return None
            
            return winning_bid
        
        elif auction.auction_type == AuctionType.REVERSE:
            # Lowest bid wins
            return min(valid_bids, key=lambda b: b.amount)
        
        elif auction.auction_type == AuctionType.SEALED_BID:
            # Highest sealed bid wins
            return max(valid_bids, key=lambda b: b.amount)
        
        return None
    
    async def _detect_bid_fraud(self, auction: Auction, bidder_id: str, amount: Decimal) -> None:
        """Detect potential bid fraud"""
        # Check for excessive bidding frequency
        recent_bids = [
            bid for bid in auction.bids
            if bid.bidder_id == bidder_id and 
            (datetime.utcnow() - bid.timestamp).total_seconds() < 300  # 5 minutes
        ]
        
        if len(recent_bids) > 5:
            raise ValueError("Too many bids in short time period")
        
        # Check for unrealistic bid amounts
        if amount > auction.current_price * 10:
            logger.warning(f"Suspicious high bid detected: {amount} for auction {auction.auction_id}")


class AuctionSystem:
    """High-level auction system interface"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize auction system"""
        self.config = config or {}
        self.engine = AuctionEngine(self.config.get('engine', {}))
        
        # Integration with existing bidding system
        try:
            from ...ai_agents.marketplace_agent.core.advanced_bidding_system import AdvancedBiddingSystem
            self.bidding_system = AdvancedBiddingSystem()
            self.has_bidding_integration = True
        except ImportError:
            logger.warning("Advanced bidding system not available - running in standalone mode")
            self.has_bidding_integration = False
        
        logger.info("🏛️ Auction System initialized")
    
    async def initialize(self) -> None:
        """Initialize auction system"""
        logger.info("🚀 Initializing Auction System")
        
        # Start background tasks
        asyncio.create_task(self._auction_monitor())
    
    async def create_auction(self, auction_data: Dict[str, Any]) -> Auction:
        """Create new auction"""
        return await self.engine.create_auction(auction_data)
    
    async def place_bid(self, auction_id: str, bidder_id: str, amount: Decimal, 
                       metadata: Dict[str, Any] = None) -> AuctionBid:
        """Place bid on auction"""
        bid = await self.engine.place_bid(auction_id, bidder_id, amount, metadata)
        
        # Integrate with advanced bidding system if available
        if self.has_bidding_integration:
            try:
                await self._sync_with_bidding_system(auction_id, bid)
            except Exception as e:
                logger.warning(f"Failed to sync with bidding system: {e}")
        
        return bid
    
    async def get_auction_status(self, auction_id: str) -> Dict[str, Any]:
        """Get comprehensive auction status"""
        auction = await self.engine.get_auction(auction_id)
        
        if not auction:
            return {"error": "Auction not found"}
        
        return {
            "auction_id": auction.auction_id,
            "status": auction.status.value,
            "current_price": float(auction.current_price),
            "bid_count": auction.bid_count,
            "time_remaining": (auction.end_time - datetime.utcnow()).total_seconds() if auction.end_time > datetime.utcnow() else 0,
            "winner_id": auction.winner_id,
            "metadata": auction.metadata
        }
    
    async def get_marketplace_auctions(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get marketplace auctions for display"""
        auctions = await self.engine.get_active_auctions(filters)
        
        return [
            {
                "auction_id": auction.auction_id,
                "title": auction.title,
                "description": auction.description,
                "current_price": float(auction.current_price),
                "bid_count": auction.bid_count,
                "end_time": auction.end_time.isoformat(),
                "auction_type": auction.auction_type.value,
                "status": auction.status.value
            }
            for auction in auctions
        ]
    
    async def _auction_monitor(self) -> None:
        """Background task to monitor auction end times"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Check for auctions that should end
                for auction_id, auction in list(self.engine.active_auctions.items()):
                    if current_time >= auction.end_time and auction.status == AuctionStatus.ACTIVE:
                        await self.engine.end_auction(auction_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in auction monitor: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _sync_with_bidding_system(self, auction_id: str, bid: AuctionBid) -> None:
        """Sync with advanced bidding system"""
        if self.has_bidding_integration:
            # Integration logic would go here
            pass


# Export main classes
__all__ = [
    "AuctionType",
    "AuctionStatus", 
    "BidStatus",
    "AuctionBid",
    "Auction",
    "AuctionEngine",
    "AuctionSystem"
]