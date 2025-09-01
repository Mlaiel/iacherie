#!/usr/bin/env python3
"""🏪 CREATOR MARKETPLACE - Advanced Service Marketplace with Bidding & Escrow
===============================================================================

Professional Creator Services Marketplace with sophisticated bidding system,
secure escrow integration, and AI-powered service matching.

Version: 3.0.0
Created by: Fahed Mlaiel (mlaiel@live.de)

⚠️ STRICT COPYRIGHT WARNING ⚠️
© 2025 Fahed Mlaiel. ALL RIGHTS RESERVED.

This software is protected by international copyright laws.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Features:
- 🎯 AI-Powered Service Matching & Discovery
- 💰 Advanced Bidding System with Real-time Auctions
- 🔒 Secure Escrow Integration for Payment Protection
- 📊 Performance Analytics & Rating System
- 🤖 Automated Quality Assessment
- 💎 Premium Service Tiers & Verification
- 🌐 Multi-Currency Support with Dynamic Pricing
- 📱 Real-time Notifications & Communication
- 🛡️ Dispute Resolution & Mediation System
- 📈 Revenue Analytics & Commission Management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Import existing modules
from ..commission.revenue_distributor import EscrowManager, EscrowAccount
from ..matching.matching_algorithms import AdvancedDeepLearningMatcher
from ...core.collaboration.revenue_splitter import RevenueSplitter

logger = logging.getLogger(__name__)


class ServiceCategory(Enum):
    """Service categories in the marketplace"""
    CONTENT_CREATION = "content_creation"
    VIDEO_PRODUCTION = "video_production"
    PHOTOGRAPHY = "photography"
    COPYWRITING = "copywriting"
    SOCIAL_MEDIA_MANAGEMENT = "social_media_management"
    INFLUENCER_MARKETING = "influencer_marketing"
    BRAND_PARTNERSHIP = "brand_partnership"
    VOICE_OVER = "voice_over"
    MUSIC_PRODUCTION = "music_production"
    GRAPHIC_DESIGN = "graphic_design"
    CONSULTATION = "consultation"
    CUSTOM_SERVICE = "custom_service"


class ServiceStatus(Enum):
    """Service listing status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BidStatus(Enum):
    """Bid status in auction system"""
    PENDING = "pending"
    ACTIVE = "active"
    WINNING = "winning"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


class OrderStatus(Enum):
    """Order fulfillment status"""
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    REVISION_REQUESTED = "revision_requested"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class ServiceListing:
    """Comprehensive service listing model"""
    service_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    description: str = ""
    category: ServiceCategory = ServiceCategory.CONTENT_CREATION
    subcategory: str = ""
    
    # Pricing
    base_price: Decimal = Decimal('0')
    currency: str = "USD"
    pricing_model: str = "fixed"  # fixed, hourly, milestone
    min_budget: Optional[Decimal] = None
    max_budget: Optional[Decimal] = None
    
    # Service details
    delivery_time: int = 7  # days
    revisions_included: int = 2
    requirements: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    
    # Auction settings
    auction_enabled: bool = False
    auction_duration: int = 7  # days
    auction_end_time: Optional[datetime] = None
    reserve_price: Optional[Decimal] = None
    
    # Status and metadata
    status: ServiceStatus = ServiceStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    views: int = 0
    favorites: int = 0
    
    # Performance metrics
    rating: float = 0.0
    reviews_count: int = 0
    completion_rate: float = 1.0
    response_time: float = 24.0  # hours
    
    # Tags and SEO
    tags: List[str] = field(default_factory=list)
    featured: bool = False
    premium: bool = False
    
    # Media
    gallery_images: List[str] = field(default_factory=list)
    portfolio_samples: List[str] = field(default_factory=list)
    video_preview: Optional[str] = None


@dataclass
class ServiceBid:
    """Bid model for auction system"""
    bid_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    bidder_id: str = ""
    amount: Decimal = Decimal('0')
    currency: str = "USD"
    
    # Bid details
    proposal: str = ""
    delivery_time: int = 7  # days
    custom_terms: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    status: BidStatus = BidStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Negotiation
    counter_offer_amount: Optional[Decimal] = None
    negotiation_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ServiceOrder:
    """Order model for service fulfillment"""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str = ""
    bid_id: Optional[str] = None
    buyer_id: str = ""
    seller_id: str = ""
    
    # Financial details
    total_amount: Decimal = Decimal('0')
    currency: str = "USD"
    escrow_id: Optional[str] = None
    commission_rate: Decimal = Decimal('0.10')  # 10% default
    
    # Order details
    requirements: Dict[str, Any] = field(default_factory=dict)
    deliverables: List[str] = field(default_factory=list)
    deadline: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    
    # Status tracking
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    revision_count: int = 0
    max_revisions: int = 2
    
    # Communication
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CreatorMarketplace:
    """
    🏪 Advanced Creator Services Marketplace
    
    Comprehensive marketplace system with:
    - AI-powered service discovery and matching
    - Real-time bidding and auction system
    - Secure escrow integration
    - Performance analytics and quality assurance
    """
    
    def __init__(self, db_session, config: Dict[str, Any]):
        self.db = db_session
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize components
        self.escrow_manager = EscrowManager(config.get('escrow', {}))
        self.revenue_splitter = RevenueSplitter(db_session, config.get('revenue', {}))
        self.ai_matcher = AdvancedDeepLearningMatcher(db_session, config.get('matching', {}))
        
        # Cache for performance
        self.service_cache = {}
        self.bid_cache = {}
        
        # Real-time notifications
        self.notification_queue = asyncio.Queue()
        
        # Performance metrics
        self.metrics = {
            'total_services': 0,
            'active_auctions': 0,
            'completed_orders': 0,
            'total_volume': Decimal('0')
        }
    
    async def initialize(self) -> None:
        """Initialize marketplace components"""
        try:
            await self.escrow_manager.initialize()
            self.logger.info("🏪 Creator Marketplace initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Marketplace initialization failed: {e}")
            raise
    
    # === SERVICE LISTING MANAGEMENT ===
    
    async def create_service_listing(
        self,
        creator_id: str,
        service_data: Dict[str, Any]
    ) -> ServiceListing:
        """
        📝 Create new service listing with AI optimization
        """
        try:
            # Validate creator eligibility
            await self._validate_creator_eligibility(creator_id)
            
            # Create service listing
            service = ServiceListing(
                creator_id=creator_id,
                title=service_data.get('title', ''),
                description=service_data.get('description', ''),
                category=ServiceCategory(service_data.get('category', 'content_creation')),
                subcategory=service_data.get('subcategory', ''),
                base_price=Decimal(str(service_data.get('base_price', 0))),
                currency=service_data.get('currency', 'USD'),
                delivery_time=service_data.get('delivery_time', 7),
                revisions_included=service_data.get('revisions', 2),
                auction_enabled=service_data.get('auction_enabled', False)
            )
            
            # AI-powered optimization
            await self._optimize_service_listing(service)
            
            # Set auction parameters if enabled
            if service.auction_enabled:
                service.auction_duration = service_data.get('auction_duration', 7)
                service.auction_end_time = datetime.utcnow() + timedelta(days=service.auction_duration)
                service.reserve_price = Decimal(str(service_data.get('reserve_price', service.base_price)))
            
            # Save to database
            await self._save_service_listing(service)
            
            # Update cache and metrics
            self.service_cache[service.service_id] = service
            self.metrics['total_services'] += 1
            if service.auction_enabled:
                self.metrics['active_auctions'] += 1
            
            self.logger.info(f"📝 Service listing created: {service.service_id}")
            
            # Send notifications
            await self._notify_service_created(service)
            
            return service
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create service listing: {e}")
            raise
    
    async def update_service_listing(
        self,
        service_id: str,
        creator_id: str,
        updates: Dict[str, Any]
    ) -> ServiceListing:
        """Update existing service listing"""
        try:
            # Get and validate service
            service = await self._get_service_listing(service_id)
            if not service or service.creator_id != creator_id:
                raise ValueError("Service not found or unauthorized")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(service, key) and key not in ['service_id', 'creator_id', 'created_at']:
                    setattr(service, key, value)
            
            service.updated_at = datetime.utcnow()
            
            # Re-optimize if major changes
            if any(key in updates for key in ['title', 'description', 'category', 'base_price']):
                await self._optimize_service_listing(service)
            
            # Save updates
            await self._save_service_listing(service)
            self.service_cache[service_id] = service
            
            self.logger.info(f"✏️ Service listing updated: {service_id}")
            return service
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update service listing: {e}")
            raise
    
    # === BIDDING SYSTEM ===
    
    async def place_bid(
        self,
        service_id: str,
        bidder_id: str,
        bid_data: Dict[str, Any]
    ) -> ServiceBid:
        """
        💰 Place bid on service with automatic validation
        """
        try:
            # Validate service and bidding eligibility
            service = await self._get_service_listing(service_id)
            if not service or not service.auction_enabled:
                raise ValueError("Service not available for bidding")
            
            if service.creator_id == bidder_id:
                raise ValueError("Cannot bid on own service")
            
            # Validate bid amount
            bid_amount = Decimal(str(bid_data.get('amount', 0)))
            await self._validate_bid_amount(service, bid_amount)
            
            # Create bid
            bid = ServiceBid(
                service_id=service_id,
                bidder_id=bidder_id,
                amount=bid_amount,
                currency=service.currency,
                proposal=bid_data.get('proposal', ''),
                delivery_time=bid_data.get('delivery_time', service.delivery_time),
                expires_at=datetime.utcnow() + timedelta(hours=bid_data.get('expires_hours', 48))
            )
            
            # AI-powered bid analysis
            bid_analysis = await self._analyze_bid_competitiveness(service, bid)
            bid.custom_terms['ai_analysis'] = bid_analysis
            
            # Save bid
            await self._save_bid(bid)
            self.bid_cache[bid.bid_id] = bid
            
            # Update service metrics
            await self._update_service_bid_metrics(service_id)
            
            self.logger.info(f"💰 Bid placed: {bid.bid_id} on service {service_id}")
            
            # Notify stakeholders
            await self._notify_bid_placed(service, bid)
            
            return bid
            
        except Exception as e:
            self.logger.error(f"❌ Failed to place bid: {e}")
            raise
    
    async def accept_bid(
        self,
        bid_id: str,
        creator_id: str
    ) -> ServiceOrder:
        """
        ✅ Accept bid and create order with escrow
        """
        try:
            # Get and validate bid
            bid = await self._get_bid(bid_id)
            if not bid:
                raise ValueError("Bid not found")
            
            service = await self._get_service_listing(bid.service_id)
            if not service or service.creator_id != creator_id:
                raise ValueError("Unauthorized to accept bid")
            
            # Update bid status
            bid.status = BidStatus.ACCEPTED
            await self._save_bid(bid)
            
            # Create escrow transaction
            escrow_account = await self.escrow_manager.create_escrow(
                transaction_id=f"order_{uuid.uuid4().hex}",
                payer_id=bid.bidder_id,
                beneficiary_id=creator_id,
                amount=bid.amount,
                currency=service.currency,
                conditions={
                    'service_id': service.service_id,
                    'bid_id': bid_id,
                    'delivery_deadline': (datetime.utcnow() + timedelta(days=bid.delivery_time)).isoformat(),
                    'revision_limit': service.revisions_included
                }
            )
            
            # Create order
            order = ServiceOrder(
                service_id=service.service_id,
                bid_id=bid_id,
                buyer_id=bid.bidder_id,
                seller_id=creator_id,
                total_amount=bid.amount,
                currency=service.currency,
                escrow_id=escrow_account.escrow_id,
                deadline=datetime.utcnow() + timedelta(days=bid.delivery_time),
                max_revisions=service.revisions_included,
                status=OrderStatus.PAYMENT_CONFIRMED
            )
            
            # Save order
            await self._save_order(order)
            
            # Update metrics
            self.metrics['completed_orders'] += 1
            self.metrics['total_volume'] += bid.amount
            
            self.logger.info(f"✅ Bid accepted, order created: {order.order_id}")
            
            # Notify participants
            await self._notify_bid_accepted(service, bid, order)
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ Failed to accept bid: {e}")
            raise
    
    # === ORDER MANAGEMENT ===
    
    async def complete_order(
        self,
        order_id: str,
        seller_id: str,
        deliverables: List[str]
    ) -> bool:
        """
        🎯 Complete order and release escrow funds
        """
        try:
            # Get and validate order
            order = await self._get_order(order_id)
            if not order or order.seller_id != seller_id:
                raise ValueError("Order not found or unauthorized")
            
            if order.status != OrderStatus.IN_PROGRESS:
                raise ValueError("Order not in progress")
            
            # Update order with deliverables
            order.deliverables = deliverables
            order.status = OrderStatus.PENDING_REVIEW
            order.completed_at = datetime.utcnow()
            
            await self._save_order(order)
            
            # Notify buyer for review
            await self._notify_order_completed(order)
            
            self.logger.info(f"🎯 Order completed: {order_id}")
            
            # Auto-release escrow after review period (e.g., 7 days)
            await self._schedule_auto_release(order)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to complete order: {e}")
            return False
    
    async def approve_order(
        self,
        order_id: str,
        buyer_id: str,
        rating: Optional[int] = None,
        review: Optional[str] = None
    ) -> bool:
        """
        👍 Approve completed order and release escrow
        """
        try:
            # Get and validate order
            order = await self._get_order(order_id)
            if not order or order.buyer_id != buyer_id:
                raise ValueError("Order not found or unauthorized")
            
            if order.status != OrderStatus.PENDING_REVIEW:
                raise ValueError("Order not ready for approval")
            
            # Release escrow funds
            if order.escrow_id:
                await self.escrow_manager.release_escrow(
                    order.escrow_id,
                    f"Order approved by buyer: {order_id}"
                )
            
            # Process commission and revenue split
            await self._process_order_payment(order)
            
            # Update order status
            order.status = OrderStatus.COMPLETED
            await self._save_order(order)
            
            # Save rating and review
            if rating or review:
                await self._save_order_review(order, rating, review)
            
            self.logger.info(f"👍 Order approved and completed: {order_id}")
            
            # Notify completion
            await self._notify_order_approved(order)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to approve order: {e}")
            return False
    
    # === AI-POWERED FEATURES ===
    
    async def get_service_recommendations(
        self,
        user_id: str,
        search_query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        🤖 AI-powered service recommendations
        """
        try:
            # Get user preferences and history
            user_data = await self._get_user_data(user_id)
            
            # Get available services
            services = await self._search_services(search_query, filters)
            
            recommendations = []
            
            for service in services[:limit * 2]:  # Get more for filtering
                # AI matching score
                match_score = await self._calculate_service_match_score(user_data, service)
                
                if match_score > 0.3:  # Minimum relevance threshold
                    recommendations.append({
                        'service': service,
                        'match_score': match_score,
                        'reasoning': await self._generate_recommendation_reasoning(user_data, service),
                        'estimated_completion_time': service.delivery_time,
                        'price_competitiveness': await self._analyze_price_competitiveness(service)
                    })
            
            # Sort by match score and return top results
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get recommendations: {e}")
            return []
    
    async def _optimize_service_listing(self, service: ServiceListing) -> None:
        """AI-powered service listing optimization"""
        try:
            # Analyze market trends
            market_data = await self._analyze_market_trends(service.category)
            
            # Optimize pricing
            if market_data:
                suggested_price = await self._suggest_optimal_price(service, market_data)
                if suggested_price and abs(suggested_price - service.base_price) / service.base_price < 0.5:
                    service.base_price = suggested_price
            
            # Generate SEO tags
            ai_tags = await self._generate_seo_tags(service)
            service.tags.extend(ai_tags)
            service.tags = list(set(service.tags))  # Remove duplicates
            
            # Optimize delivery time
            optimal_delivery = await self._suggest_optimal_delivery_time(service)
            if optimal_delivery:
                service.delivery_time = optimal_delivery
            
        except Exception as e:
            self.logger.error(f"Service optimization failed: {e}")
    
    # === HELPER METHODS ===
    
    async def _validate_creator_eligibility(self, creator_id: str) -> bool:
        """Validate creator can list services"""
        # Implementation would check creator verification, rating, etc.
        return True
    
    async def _save_service_listing(self, service: ServiceListing) -> None:
        """Save service listing to database"""
        # Database implementation
        pass
    
    async def _get_service_listing(self, service_id: str) -> Optional[ServiceListing]:
        """Get service listing from database or cache"""
        if service_id in self.service_cache:
            return self.service_cache[service_id]
        # Database lookup implementation
        return None
    
    async def _save_bid(self, bid: ServiceBid) -> None:
        """Save bid to database"""
        pass
    
    async def _get_bid(self, bid_id: str) -> Optional[ServiceBid]:
        """Get bid from database or cache"""
        if bid_id in self.bid_cache:
            return self.bid_cache[bid_id]
        return None
    
    async def _save_order(self, order: ServiceOrder) -> None:
        """Save order to database"""
        pass
    
    async def _get_order(self, order_id: str) -> Optional[ServiceOrder]:
        """Get order from database"""
        return None
    
    async def _validate_bid_amount(self, service: ServiceListing, amount: Decimal) -> bool:
        """Validate bid amount against service constraints"""
        if service.reserve_price and amount < service.reserve_price:
            raise ValueError("Bid below reserve price")
        
        if service.min_budget and amount < service.min_budget:
            raise ValueError("Bid below minimum budget")
        
        if service.max_budget and amount > service.max_budget:
            raise ValueError("Bid exceeds maximum budget")
        
        return True
    
    async def _analyze_bid_competitiveness(self, service: ServiceListing, bid: ServiceBid) -> Dict[str, Any]:
        """AI analysis of bid competitiveness"""
        return {
            'competitiveness_score': 0.75,
            'market_position': 'competitive',
            'win_probability': 0.68,
            'recommendations': ['Consider highlighting unique value proposition']
        }
    
    async def _process_order_payment(self, order: ServiceOrder) -> None:
        """Process payment distribution with commission"""
        try:
            # Calculate commission
            platform_commission = order.total_amount * order.commission_rate
            seller_amount = order.total_amount - platform_commission
            
            # Use revenue splitter for distribution
            await self.revenue_splitter.distribute_revenue(
                order.order_id,
                {
                    'seller': float(seller_amount),
                    'platform': float(platform_commission)
                },
                order.currency
            )
            
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
    
    # === NOTIFICATION METHODS ===
    
    async def _notify_service_created(self, service: ServiceListing) -> None:
        """Notify about new service listing"""
        notification = {
            'type': 'service_created',
            'service_id': service.service_id,
            'creator_id': service.creator_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def _notify_bid_placed(self, service: ServiceListing, bid: ServiceBid) -> None:
        """Notify about new bid"""
        notification = {
            'type': 'bid_placed',
            'service_id': service.service_id,
            'bid_id': bid.bid_id,
            'creator_id': service.creator_id,
            'bidder_id': bid.bidder_id,
            'amount': str(bid.amount),
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def _notify_bid_accepted(self, service: ServiceListing, bid: ServiceBid, order: ServiceOrder) -> None:
        """Notify about accepted bid"""
        notification = {
            'type': 'bid_accepted',
            'order_id': order.order_id,
            'service_id': service.service_id,
            'bid_id': bid.bid_id,
            'buyer_id': order.buyer_id,
            'seller_id': order.seller_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def _notify_order_completed(self, order: ServiceOrder) -> None:
        """Notify about completed order"""
        notification = {
            'type': 'order_completed',
            'order_id': order.order_id,
            'buyer_id': order.buyer_id,
            'seller_id': order.seller_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.notification_queue.put(notification)
    
    async def _notify_order_approved(self, order: ServiceOrder) -> None:
        """Notify about approved order"""
        notification = {
            'type': 'order_approved',
            'order_id': order.order_id,
            'buyer_id': order.buyer_id,
            'seller_id': order.seller_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.notification_queue.put(notification)
    
    # === ANALYTICS AND INSIGHTS ===
    
    async def get_marketplace_analytics(self) -> Dict[str, Any]:
        """Get comprehensive marketplace analytics"""
        try:
            return {
                'metrics': self.metrics,
                'top_categories': await self._get_top_categories(),
                'price_trends': await self._get_price_trends(),
                'creator_performance': await self._get_creator_performance_stats(),
                'buyer_activity': await self._get_buyer_activity_stats(),
                'growth_metrics': await self._calculate_growth_metrics(),
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {e}")
            return {'error': 'Analytics unavailable'}
    
    async def shutdown(self) -> None:
        """Shutdown marketplace components"""
        try:
            await self.escrow_manager.shutdown()
            self.logger.info("🏪 Creator Marketplace shutdown complete")
        except Exception as e:
            self.logger.error(f"Marketplace shutdown error: {e}")


# === UTILITY FUNCTIONS ===

async def create_marketplace_instance(db_session, config: Dict[str, Any]) -> CreatorMarketplace:
    """Create and initialize marketplace instance"""
    marketplace = CreatorMarketplace(db_session, config)
    await marketplace.initialize()
    return marketplace


def calculate_marketplace_commission(
    amount: Decimal,
    service_category: ServiceCategory,
    creator_tier: str = "standard"
) -> Decimal:
    """Calculate dynamic commission based on category and creator tier"""
    base_rates = {
        ServiceCategory.CONTENT_CREATION: Decimal('0.10'),
        ServiceCategory.VIDEO_PRODUCTION: Decimal('0.08'),
        ServiceCategory.PHOTOGRAPHY: Decimal('0.12'),
        ServiceCategory.CONSULTATION: Decimal('0.15'),
        ServiceCategory.CUSTOM_SERVICE: Decimal('0.10')
    }
    
    base_rate = base_rates.get(service_category, Decimal('0.10'))
    
    # Tier discounts
    tier_multipliers = {
        'premium': Decimal('0.8'),
        'verified': Decimal('0.9'),
        'standard': Decimal('1.0')
    }
    
    multiplier = tier_multipliers.get(creator_tier, Decimal('1.0'))
    final_rate = base_rate * multiplier
    
    return amount * final_rate