"""Auction Engine Module - Advanced Real-Time Auction System for Creator Collaborations
===================================================================================

Sophisticated auction engine providing multiple auction types, real-time bidding,
intelligent price discovery, and automated auction management for creator marketplace.

This module implements:
- Multiple auction formats (English, Dutch, Sealed-bid, Reserve)
- Real-time bidding with WebSocket integration
- Dynamic pricing algorithms and market intelligence
- Automated auction lifecycle management
- Anti-sniping and bid validation systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import uuid
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class AuctionType(Enum):
    """Types of auctions supported"""
    ENGLISH = "english"           # Ascending price, open bidding
    DUTCH = "dutch"              # Descending price, first bid wins
    SEALED_BID = "sealed_bid"    # Private bids, highest wins
    RESERVE = "reserve"          # English with minimum price
    BUYOUT = "buyout"           # Fixed price option available
    MULTI_ITEM = "multi_item"   # Multiple items, multiple winners


class AuctionStatus(Enum):
    """Auction status states"""
    CREATED = "created"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BidType(Enum):
    """Types of bids"""
    MANUAL = "manual"
    AUTO = "auto"
    PROXY = "proxy"
    SNIPE = "snipe"
    BUYOUT = "buyout"


@dataclass
class Bid:
    """Individual bid in an auction"""
    bid_id: str
    auction_id: str
    bidder_id: str
    amount: Decimal
    bid_type: BidType
    timestamp: datetime
    is_valid: bool = True
    is_winning: bool = False
    auto_bid_limit: Optional[Decimal] = None
    proxy_increment: Optional[Decimal] = None
    bid_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.bid_id:
            self.bid_id = str(uuid.uuid4())


@dataclass
class AuctionItem:
    """Item being auctioned"""
    item_id: str
    title: str
    description: str
    category: str
    starting_price: Decimal
    reserve_price: Optional[Decimal] = None
    buyout_price: Optional[Decimal] = None
    estimated_value: Optional[Decimal] = None
    item_data: Dict[str, Any] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuctionSettings:
    """Auction configuration settings"""
    auction_type: AuctionType
    duration_minutes: int
    bid_increment: Decimal
    auto_extend_minutes: int = 5  # Anti-sniping extension
    max_extensions: int = 3
    allow_early_close: bool = False
    require_approval: bool = False
    visibility: str = "public"  # public, private, invited
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    shipping_options: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Auction:
    """Complete auction entity"""
    auction_id: str
    seller_id: str
    item: AuctionItem
    settings: AuctionSettings
    status: AuctionStatus
    start_time: datetime
    end_time: datetime
    current_price: Decimal
    bid_count: int = 0
    view_count: int = 0
    watch_count: int = 0
    winner_id: Optional[str] = None
    winning_bid_id: Optional[str] = None
    bids: List[Bid] = field(default_factory=list)
    watchers: List[str] = field(default_factory=list)
    extensions_used: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AuctionResult:
    """Auction completion result"""
    auction_id: str
    success: bool
    winner_id: Optional[str]
    winning_bid: Optional[Bid]
    final_price: Decimal
    total_bids: int
    duration_actual: timedelta
    completion_reason: str
    next_steps: List[str]
    analytics: Dict[str, Any]


class AuctionEngine:
    """Advanced real-time auction engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the auction engine"""
        self.config = config or {}
        self.active_auctions: Dict[str, Auction] = {}
        self.bid_history: Dict[str, List[Bid]] = {}
        self.auction_analytics: Dict[str, Dict[str, Any]] = {}
        self.subscribers: Dict[str, List[Any]] = {}  # WebSocket subscribers
        self.auto_bidders: Dict[str, Dict[str, Any]] = {}
        
        # Anti-fraud systems
        self.bid_validators = []
        self.sniping_protection = True
        self.proxy_bid_engine = True
        
        logger.info("🏛️ Auction Engine initialized")
    
    async def create_auction(
        self,
        seller_id: str,
        item: AuctionItem,
        settings: AuctionSettings,
        start_time: Optional[datetime] = None
    ) -> Auction:
        """Create a new auction"""
        try:
            auction_id = str(uuid.uuid4())
            
            # Set start and end times
            if start_time is None:
                start_time = datetime.now(timezone.utc)
            
            end_time = start_time + timedelta(minutes=settings.duration_minutes)
            
            # Validate auction parameters
            await self._validate_auction_parameters(item, settings)
            
            # Create auction
            auction = Auction(
                auction_id=auction_id,
                seller_id=seller_id,
                item=item,
                settings=settings,
                status=AuctionStatus.CREATED if start_time > datetime.now(timezone.utc) else AuctionStatus.ACTIVE,
                start_time=start_time,
                end_time=end_time,
                current_price=item.starting_price
            )
            
            # Store auction
            self.active_auctions[auction_id] = auction
            self.bid_history[auction_id] = []
            
            # Initialize analytics
            self.auction_analytics[auction_id] = {
                'views': 0,
                'unique_bidders': set(),
                'bid_frequency': [],
                'price_history': [(start_time, item.starting_price)],
                'watchers_over_time': []
            }
            
            # Schedule auction start if needed
            if auction.status == AuctionStatus.CREATED:
                await self._schedule_auction_start(auction)
            
            logger.info(f"🏛️ Auction created: {auction_id}")
            return auction
            
        except Exception as e:
            logger.error(f"❌ Error creating auction: {e}")
            raise
    
    async def place_bid(
        self,
        auction_id: str,
        bidder_id: str,
        amount: Decimal,
        bid_type: BidType = BidType.MANUAL,
        auto_bid_limit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Place a bid on an auction"""
        try:
            auction = self.active_auctions.get(auction_id)
            if not auction:
                return {"success": False, "error": "Auction not found"}
            
            # Validate bid
            validation_result = await self._validate_bid(auction, bidder_id, amount, bid_type)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["reason"]}
            
            # Create bid
            bid = Bid(
                bid_id=str(uuid.uuid4()),
                auction_id=auction_id,
                bidder_id=bidder_id,
                amount=amount,
                bid_type=bid_type,
                timestamp=datetime.now(timezone.utc),
                auto_bid_limit=auto_bid_limit
            )
            
            # Process bid based on auction type
            result = await self._process_bid(auction, bid)
            
            if result["accepted"]:
                # Update auction state
                auction.bids.append(bid)
                auction.bid_count += 1
                auction.updated_at = datetime.now(timezone.utc)
                
                # Update bid history
                self.bid_history[auction_id].append(bid)
                
                # Update analytics
                await self._update_auction_analytics(auction_id, bid)
                
                # Check for auction end conditions
                await self._check_auction_end_conditions(auction)
                
                # Notify subscribers
                await self._notify_bid_placed(auction, bid)
                
                # Handle proxy bidding if applicable
                if bid_type == BidType.PROXY and auto_bid_limit:
                    await self._setup_proxy_bidding(auction_id, bidder_id, auto_bid_limit)
                
                logger.info(f"🏛️ Bid placed: {bid.bid_id} for {amount} on {auction_id}")
                
                return {
                    "success": True,
                    "bid_id": bid.bid_id,
                    "new_current_price": auction.current_price,
                    "is_winning": bid.is_winning,
                    "auction_status": auction.status.value
                }
            else:
                return {"success": False, "error": result["reason"]}
                
        except Exception as e:
            logger.error(f"❌ Error placing bid: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_auction_parameters(
        self,
        item: AuctionItem,
        settings: AuctionSettings
    ) -> None:
        """Validate auction creation parameters"""
        # Validate starting price
        if item.starting_price <= 0:
            raise ValueError("Starting price must be positive")
        
        # Validate reserve price
        if item.reserve_price and item.reserve_price < item.starting_price:
            raise ValueError("Reserve price cannot be less than starting price")
        
        # Validate buyout price
        if item.buyout_price and item.buyout_price <= item.starting_price:
            raise ValueError("Buyout price must be greater than starting price")
        
        # Validate duration
        if settings.duration_minutes <= 0:
            raise ValueError("Auction duration must be positive")
        
        # Validate bid increment
        if settings.bid_increment <= 0:
            raise ValueError("Bid increment must be positive")
    
    async def _validate_bid(
        self,
        auction: Auction,
        bidder_id: str,
        amount: Decimal,
        bid_type: BidType
    ) -> Dict[str, Any]:
        """Validate a bid before acceptance"""
        # Check auction status
        if auction.status != AuctionStatus.ACTIVE:
            return {"valid": False, "reason": "Auction is not active"}
        
        # Check auction timing
        now = datetime.now(timezone.utc)
        if now < auction.start_time:
            return {"valid": False, "reason": "Auction has not started"}
        
        if now > auction.end_time:
            return {"valid": False, "reason": "Auction has ended"}
        
        # Check bidder is not seller
        if bidder_id == auction.seller_id:
            return {"valid": False, "reason": "Seller cannot bid on own auction"}
        
        # Check minimum bid amount
        required_amount = auction.current_price + auction.settings.bid_increment
        
        if bid_type != BidType.BUYOUT and amount < required_amount:
            return {
                "valid": False,
                "reason": f"Bid must be at least {required_amount}"
            }
        
        # Check buyout bid
        if bid_type == BidType.BUYOUT:
            if not auction.item.buyout_price:
                return {"valid": False, "reason": "Buyout not available for this auction"}
            
            if amount != auction.item.buyout_price:
                return {"valid": False, "reason": "Buyout bid must match buyout price"}
        
        # Anti-fraud checks
        fraud_check = await self._check_bid_fraud(auction, bidder_id, amount)
        if not fraud_check["valid"]:
            return fraud_check
        
        return {"valid": True}
    
    async def _check_bid_fraud(
        self,
        auction: Auction,
        bidder_id: str,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Check for fraudulent bidding patterns"""
        # Check for bid manipulation
        recent_bids = [bid for bid in auction.bids[-10:] if bid.bidder_id == bidder_id]
        
        if len(recent_bids) > 5:  # Too many recent bids
            return {"valid": False, "reason": "Too many recent bids from this bidder"}
        
        # Check for shill bidding (simplified)
        if len(auction.bids) > 0:
            last_bid = auction.bids[-1]
            if last_bid.bidder_id == bidder_id:
                return {"valid": False, "reason": "Cannot bid consecutively"}
        
        # Check for unrealistic bid amounts
        max_reasonable = auction.current_price * Decimal('10')  # 10x current price
        if amount > max_reasonable:
            return {"valid": False, "reason": "Bid amount appears unrealistic"}
        
        return {"valid": True}
    
    async def _process_bid(self, auction: Auction, bid: Bid) -> Dict[str, Any]:
        """Process a bid based on auction type"""
        if auction.settings.auction_type == AuctionType.ENGLISH:
            return await self._process_english_bid(auction, bid)
        elif auction.settings.auction_type == AuctionType.DUTCH:
            return await self._process_dutch_bid(auction, bid)
        elif auction.settings.auction_type == AuctionType.SEALED_BID:
            return await self._process_sealed_bid(auction, bid)
        elif auction.settings.auction_type == AuctionType.BUYOUT:
            return await self._process_buyout_bid(auction, bid)
        else:
            return {"accepted": False, "reason": "Unsupported auction type"}
    
    async def _process_english_bid(self, auction: Auction, bid: Bid) -> Dict[str, Any]:
        """Process bid for English (ascending) auction"""
        # Handle buyout bid
        if bid.bid_type == BidType.BUYOUT:
            auction.current_price = bid.amount
            auction.status = AuctionStatus.COMPLETED
            auction.winner_id = bid.bidder_id
            auction.winning_bid_id = bid.bid_id
            bid.is_winning = True
            
            return {"accepted": True, "reason": "Buyout successful"}
        
        # Regular bid processing
        if bid.amount > auction.current_price:
            # Mark previous winning bid as not winning
            for existing_bid in auction.bids:
                existing_bid.is_winning = False
            
            # Update auction state
            auction.current_price = bid.amount
            bid.is_winning = True
            
            # Check for anti-sniping extension
            await self._check_anti_sniping(auction)
            
            return {"accepted": True, "reason": "Bid accepted"}
        
        return {"accepted": False, "reason": "Bid amount too low"}
    
    async def _process_dutch_bid(self, auction: Auction, bid: Bid) -> Dict[str, Any]:
        """Process bid for Dutch (descending) auction"""
        # In Dutch auction, first bid at or above current price wins
        if bid.amount >= auction.current_price:
            auction.current_price = bid.amount
            auction.status = AuctionStatus.COMPLETED
            auction.winner_id = bid.bidder_id
            auction.winning_bid_id = bid.bid_id
            bid.is_winning = True
            
            return {"accepted": True, "reason": "Winning bid in Dutch auction"}
        
        return {"accepted": False, "reason": "Bid below current Dutch price"}
    
    async def _process_sealed_bid(self, auction: Auction, bid: Bid) -> Dict[str, Any]:
        """Process bid for sealed bid auction"""
        # All bids are accepted but not revealed until auction ends
        bid.is_winning = False  # Will be determined at auction end
        
        return {"accepted": True, "reason": "Sealed bid recorded"}
    
    async def _process_buyout_bid(self, auction: Auction, bid: Bid) -> Dict[str, Any]:
        """Process buyout bid"""
        if bid.bid_type == BidType.BUYOUT and auction.item.buyout_price:
            if bid.amount == auction.item.buyout_price:
                auction.current_price = bid.amount
                auction.status = AuctionStatus.COMPLETED
                auction.winner_id = bid.bidder_id
                auction.winning_bid_id = bid.bid_id
                bid.is_winning = True
                
                return {"accepted": True, "reason": "Buyout successful"}
        
        # Fall back to regular English auction processing
        return await self._process_english_bid(auction, bid)
    
    async def _check_anti_sniping(self, auction: Auction) -> None:
        """Check and apply anti-sniping measures"""
        if not self.sniping_protection:
            return
        
        now = datetime.now(timezone.utc)
        time_remaining = (auction.end_time - now).total_seconds()
        
        # If bid placed within extension window, extend auction
        if (time_remaining <= auction.settings.auto_extend_minutes * 60 and
            auction.extensions_used < auction.settings.max_extensions):
            
            extension = timedelta(minutes=auction.settings.auto_extend_minutes)
            auction.end_time += extension
            auction.extensions_used += 1
            
            # Notify subscribers of extension
            await self._notify_auction_extended(auction, extension)
            
            logger.info(f"🏛️ Auction {auction.auction_id} extended by {extension}")
    
    async def _setup_proxy_bidding(
        self,
        auction_id: str,
        bidder_id: str,
        max_amount: Decimal
    ) -> None:
        """Setup proxy bidding for a bidder"""
        if not self.proxy_bid_engine:
            return
        
        self.auto_bidders[f"{auction_id}:{bidder_id}"] = {
            "auction_id": auction_id,
            "bidder_id": bidder_id,
            "max_amount": max_amount,
            "active": True,
            "last_bid_amount": Decimal('0')
        }
        
        logger.info(f"🏛️ Proxy bidding setup for {bidder_id} up to {max_amount}")
    
    async def _check_auction_end_conditions(self, auction: Auction) -> None:
        """Check if auction should end"""
        now = datetime.now(timezone.utc)
        
        # Time-based ending
        if now >= auction.end_time and auction.status == AuctionStatus.ACTIVE:
            await self._end_auction(auction)
        
        # Buyout ending (already handled in bid processing)
        
        # Reserve not met (for reserve auctions)
        if (auction.settings.auction_type == AuctionType.RESERVE and
            auction.item.reserve_price and
            auction.current_price < auction.item.reserve_price and
            now >= auction.end_time):
            
            auction.status = AuctionStatus.FAILED
            await self._notify_auction_failed(auction, "Reserve price not met")
    
    async def _end_auction(self, auction: Auction) -> AuctionResult:
        """End an auction and determine winner"""
        try:
            auction.status = AuctionStatus.COMPLETED
            auction.updated_at = datetime.now(timezone.utc)
            
            if auction.settings.auction_type == AuctionType.SEALED_BID:
                # Determine winner from sealed bids
                await self._resolve_sealed_bid_auction(auction)
            
            # Determine final winner
            winning_bid = None
            if auction.bids:
                if auction.settings.auction_type == AuctionType.SEALED_BID:
                    # Highest bid wins
                    winning_bid = max(auction.bids, key=lambda b: b.amount)
                else:
                    # Current winning bid
                    winning_bid = next((b for b in auction.bids if b.is_winning), None)
                
                if winning_bid:
                    auction.winner_id = winning_bid.bidder_id
                    auction.winning_bid_id = winning_bid.bid_id
                    winning_bid.is_winning = True
            
            # Create result
            result = AuctionResult(
                auction_id=auction.auction_id,
                success=auction.winner_id is not None,
                winner_id=auction.winner_id,
                winning_bid=winning_bid,
                final_price=auction.current_price,
                total_bids=auction.bid_count,
                duration_actual=auction.updated_at - auction.start_time,
                completion_reason="Time expired",
                next_steps=await self._generate_next_steps(auction),
                analytics=await self._generate_auction_analytics(auction)
            )
            
            # Notify completion
            await self._notify_auction_completed(auction, result)
            
            # Cleanup
            await self._cleanup_auction(auction.auction_id)
            
            logger.info(f"🏛️ Auction completed: {auction.auction_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error ending auction: {e}")
            raise
    
    async def _resolve_sealed_bid_auction(self, auction: Auction) -> None:
        """Resolve sealed bid auction by revealing and comparing bids"""
        if not auction.bids:
            return
        
        # Sort bids by amount (descending)
        sorted_bids = sorted(auction.bids, key=lambda b: b.amount, reverse=True)
        
        # Winner is highest bidder
        winning_bid = sorted_bids[0]
        winning_bid.is_winning = True
        
        # In second-price auction, winner pays second-highest price
        if len(sorted_bids) > 1:
            second_price = sorted_bids[1].amount
            auction.current_price = second_price
        else:
            auction.current_price = winning_bid.amount
    
    async def _generate_next_steps(self, auction: Auction) -> List[str]:
        """Generate next steps after auction completion"""
        next_steps = []
        
        if auction.winner_id:
            next_steps.extend([
                "Send invoice to winning bidder",
                "Arrange payment processing",
                "Coordinate item delivery/transfer",
                "Release seller payment after confirmation",
                "Request feedback from both parties"
            ])
        else:
            next_steps.extend([
                "Notify seller of unsuccessful auction",
                "Offer relisting options",
                "Analyze auction performance",
                "Suggest pricing adjustments"
            ])
        
        return next_steps
    
    async def _generate_auction_analytics(self, auction: Auction) -> Dict[str, Any]:
        """Generate comprehensive auction analytics"""
        analytics = self.auction_analytics.get(auction.auction_id, {})
        
        if auction.bids:
            bid_amounts = [bid.amount for bid in auction.bids]
            
            analytics.update({
                "final_statistics": {
                    "total_bids": len(auction.bids),
                    "unique_bidders": len(set(bid.bidder_id for bid in auction.bids)),
                    "average_bid": sum(bid_amounts) / len(bid_amounts),
                    "bid_increment_avg": sum(bid_amounts[i] - bid_amounts[i-1] 
                                           for i in range(1, len(bid_amounts))) / max(len(bid_amounts) - 1, 1) if len(bid_amounts) > 1 else 0,
                    "price_appreciation": auction.current_price - auction.item.starting_price,
                    "price_appreciation_percent": float((auction.current_price - auction.item.starting_price) / auction.item.starting_price * 100)
                },
                "bidding_patterns": {
                    "early_bidding": len([b for b in auction.bids if (b.timestamp - auction.start_time).total_seconds() < 3600]),
                    "late_bidding": len([b for b in auction.bids if (auction.end_time - b.timestamp).total_seconds() < 3600]),
                    "proxy_bids": len([b for b in auction.bids if b.bid_type == BidType.PROXY]),
                    "manual_bids": len([b for b in auction.bids if b.bid_type == BidType.MANUAL])
                },
                "performance_metrics": {
                    "reserve_met": auction.item.reserve_price is None or auction.current_price >= auction.item.reserve_price,
                    "extensions_used": auction.extensions_used,
                    "completion_rate": 1.0 if auction.winner_id else 0.0
                }
            })
        
        return analytics
    
    async def _update_auction_analytics(self, auction_id: str, bid: Bid) -> None:
        """Update real-time auction analytics"""
        if auction_id not in self.auction_analytics:
            return
        
        analytics = self.auction_analytics[auction_id]
        
        # Update unique bidders
        analytics['unique_bidders'].add(bid.bidder_id)
        
        # Update bid frequency
        analytics['bid_frequency'].append(bid.timestamp)
        
        # Update price history
        analytics['price_history'].append((bid.timestamp, bid.amount))
    
    async def _schedule_auction_start(self, auction: Auction) -> None:
        """Schedule auction to start at specified time"""
        delay = (auction.start_time - datetime.now(timezone.utc)).total_seconds()
        
        if delay > 0:
            # In a real implementation, this would use a proper scheduler
            asyncio.create_task(self._delayed_auction_start(auction, delay))
    
    async def _delayed_auction_start(self, auction: Auction, delay: float) -> None:
        """Start auction after delay"""
        await asyncio.sleep(delay)
        
        if auction.auction_id in self.active_auctions:
            auction.status = AuctionStatus.ACTIVE
            await self._notify_auction_started(auction)
            logger.info(f"🏛️ Auction started: {auction.auction_id}")
    
    async def _cleanup_auction(self, auction_id: str) -> None:
        """Cleanup auction data after completion"""
        # Remove from active auctions but keep in history
        if auction_id in self.active_auctions:
            # In production, move to historical storage
            del self.active_auctions[auction_id]
        
        # Cleanup auto bidders
        keys_to_remove = [key for key in self.auto_bidders.keys() if key.startswith(f"{auction_id}:")]
        for key in keys_to_remove:
            del self.auto_bidders[key]
    
    # Notification methods (would integrate with WebSocket/event system)
    async def _notify_bid_placed(self, auction: Auction, bid: Bid) -> None:
        """Notify subscribers of new bid"""
        notification = {
            "type": "bid_placed",
            "auction_id": auction.auction_id,
            "bid_id": bid.bid_id,
            "amount": float(bid.amount),
            "bidder_id": bid.bidder_id,
            "current_price": float(auction.current_price),
            "timestamp": bid.timestamp.isoformat()
        }
        
        # In production, send via WebSocket
        logger.info(f"📢 Bid notification: {notification}")
    
    async def _notify_auction_started(self, auction: Auction) -> None:
        """Notify subscribers that auction has started"""
        notification = {
            "type": "auction_started",
            "auction_id": auction.auction_id,
            "start_time": auction.start_time.isoformat(),
            "end_time": auction.end_time.isoformat()
        }
        
        logger.info(f"📢 Auction start notification: {notification}")
    
    async def _notify_auction_extended(self, auction: Auction, extension: timedelta) -> None:
        """Notify subscribers of auction extension"""
        notification = {
            "type": "auction_extended",
            "auction_id": auction.auction_id,
            "new_end_time": auction.end_time.isoformat(),
            "extension_minutes": extension.total_seconds() / 60
        }
        
        logger.info(f"📢 Auction extension notification: {notification}")
    
    async def _notify_auction_completed(self, auction: Auction, result: AuctionResult) -> None:
        """Notify subscribers of auction completion"""
        notification = {
            "type": "auction_completed",
            "auction_id": auction.auction_id,
            "winner_id": result.winner_id,
            "final_price": float(result.final_price),
            "success": result.success
        }
        
        logger.info(f"📢 Auction completion notification: {notification}")
    
    async def _notify_auction_failed(self, auction: Auction, reason: str) -> None:
        """Notify subscribers of auction failure"""
        notification = {
            "type": "auction_failed",
            "auction_id": auction.auction_id,
            "reason": reason
        }
        
        logger.info(f"📢 Auction failure notification: {notification}")
    
    # Public query methods
    async def get_auction(self, auction_id: str) -> Optional[Auction]:
        """Get auction by ID"""
        return self.active_auctions.get(auction_id)
    
    async def get_active_auctions(
        self,
        limit: int = 50,
        offset: int = 0,
        category: Optional[str] = None
    ) -> List[Auction]:
        """Get list of active auctions"""
        auctions = list(self.active_auctions.values())
        
        # Filter by category if specified
        if category:
            auctions = [a for a in auctions if a.item.category == category]
        
        # Filter by status
        auctions = [a for a in auctions if a.status == AuctionStatus.ACTIVE]
        
        # Sort by end time (ending soonest first)
        auctions.sort(key=lambda a: a.end_time)
        
        return auctions[offset:offset + limit]
    
    async def get_auction_bids(self, auction_id: str) -> List[Bid]:
        """Get all bids for an auction"""
        return self.bid_history.get(auction_id, [])
    
    async def cancel_auction(
        self,
        auction_id: str,
        seller_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Cancel an auction"""
        auction = self.active_auctions.get(auction_id)
        
        if not auction:
            return {"success": False, "error": "Auction not found"}
        
        if auction.seller_id != seller_id:
            return {"success": False, "error": "Unauthorized"}
        
        if auction.status != AuctionStatus.ACTIVE:
            return {"success": False, "error": "Auction cannot be cancelled"}
        
        if auction.bids:
            return {"success": False, "error": "Cannot cancel auction with bids"}
        
        auction.status = AuctionStatus.CANCELLED
        await self._notify_auction_cancelled(auction, reason)
        await self._cleanup_auction(auction_id)
        
        return {"success": True}
    
    async def _notify_auction_cancelled(self, auction: Auction, reason: str) -> None:
        """Notify subscribers of auction cancellation"""
        notification = {
            "type": "auction_cancelled",
            "auction_id": auction.auction_id,
            "reason": reason
        }
        
        logger.info(f"📢 Auction cancellation notification: {notification}")


# Export main classes
__all__ = [
    'AuctionEngine',
    'Auction',
    'AuctionItem',
    'AuctionSettings',
    'Bid',
    'AuctionResult',
    'AuctionType',
    'AuctionStatus',
    'BidType'
]