"""
IA Chérie - Creator Marketplace
Marketplace for Creator Services & Collaborations

© 2025 Fahed Mlaiel (mlaiel@live.de) - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random


class ServiceCategory(Enum):
    """
        Catégories services marketplace"""
    VIDEO_EDITING = "video_editing"
    GRAPHIC_DESIGN = "graphic_design"
    MUSIC_PRODUCTION = "music_production"
    VOICEOVER = "voiceover"
    SCRIPTWRITING = "scriptwriting"
    ANIMATION = "animation"
    CONSULTING = "consulting"


class ListingStatus(Enum):
    """Statuts annonces"""
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD_OUT = "sold_out"
    EXPIRED = "expired"


@dataclass
class ServiceListing:
    """Annonce service marketplace"""
    listing_id: str
    creator_id: str
    category: str
    title: str
    description: str
    price_usd: float
    delivery_days: int
    rating: float
    total_orders: int
    status: str
    created_at: datetime


@dataclass
class MarketplaceOrder:
    """
        Commande marketplace"""
    order_id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    amount_usd: float
    status: str
    ordered_at: datetime
    delivered_at: Optional[datetime]


class CreatorMarketplace:
    """
    Marketplace services créateurs
    Mise en relation, transactions, évaluations
    
    © 2025 Fahed Mlaiel - Creator Marketplace
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Données marketplace
        self.listings: Dict[str, ServiceListing] = {}
        self.orders: Dict[str, MarketplaceOrder] = {}
        
        # Statistiques
        self.total_listings_created = 0
        self.total_orders_placed = 0
        self.total_revenue_usd = 0.0
        
        self.logger.info("🏪 CreatorMarketplace initialized")
    
    async def create_listing(
        self,
        creator_id: str,
        category: str,
        title: str,
        description: str,
        price_usd: float,
        delivery_days: int
    ) -> ServiceListing:
        """
        Crée annonce service sur marketplace
        
        Args:
            creator_id: ID créateur vendeur
            category: Catégorie service
            title: Titre annonce
            description: Description détaillée
            price_usd: Prix en USD
            delivery_days: Délai livraison en jours
        
        Returns:
            Annonce créée
        """
        listing_id = f"listing-{self.total_listings_created + 1}"
        
        listing = ServiceListing(
            listing_id=listing_id,
            creator_id=creator_id,
            category=category,
            title=title,
            description=description,
            price_usd=price_usd,
            delivery_days=delivery_days,
            rating=5.0,
            total_orders=0,
            status=ListingStatus.ACTIVE.value,
            created_at=datetime.now()
        )

        
        self.listings[listing_id] = listing
        self.total_listings_created += 1
        
        self.logger.info(f"✅ Listing created: {listing_id} - {title}")
        return listing
    
    async def place_order(
        self,
        listing_id: str,
        buyer_id: str
    ) -> MarketplaceOrder:
        """
        Place commande sur listing
        
        Args:
            listing_id: ID annonce
            buyer_id: ID acheteur
        
        Returns:
            Commande créée
        """
        listing = self.listings.get(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        
        if listing.status != ListingStatus.ACTIVE.value:
            raise ValueError(f"Listing {listing_id} not available")


        
        order_id = f"order-{self.total_orders_placed + 1}"
        
        order = MarketplaceOrder(
            order_id=order_id,
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.creator_id,
            amount_usd=listing.price_usd,
            status="pending",
            ordered_at=datetime.now(),
            delivered_at=None
        )

        
        self.orders[order_id] = order
        self.total_orders_placed += 1
        self.total_revenue_usd += listing.price_usd
        
        # Mise à jour listing
        listing.total_orders += 1
        
        self.logger.info(f"✅ Order placed: {order_id} for ${listing.price_usd}")
        return order
    
    async def search_listings(
        self,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None
    ) -> List[ServiceListing]:
        """
        Recherche annonces marketplace
        
        Args:
            category: Filtrer par catégorie (optional)

            max_price: Prix maximum (optional)

            min_rating: Note minimum (optional)

        
        Returns:
            Liste annonces matchant critères
        """
        await asyncio.sleep(0.01)


        
        results = list(self.listings.values())
        
        # Filtres
        if category:
            results = [l for l in results if l.category == category]
        
        if max_price:
            results = [l for l in results if l.price_usd <= max_price]
        
        if min_rating:
            results = [l for l in results if l.rating >= min_rating]
        
        # Tri par popularité
        results.sort(key=lambda x: x.total_orders, reverse=True)

        
        self.logger.info(f"🔍 Search returned {len(results)} listings")
        return results
    
    async def complete_order(
        self,
        order_id: str
    ) -> MarketplaceOrder:
        """
        Marque commande comme livrée
        
        Args:
            order_id: ID commande
        
        Returns:
            Commande mise à jour
        """
        order = self.orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        
        order.status = "completed"
        order.delivered_at = datetime.now()

        
        self.logger.info(f"✅ Order completed: {order_id}")
        return order
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Récupère statistiques marketplace"""
        active_listings = sum(
            1 for l in self.listings.values()

            if l.status == ListingStatus.ACTIVE.value
        )

        
        return {
            "total_listings": len(self.listings),
            "active_listings": active_listings,
            "total_orders": self.total_orders_placed,
            "total_revenue_usd": round(self.total_revenue_usd, 2),
            "average_order_value": round(
                self.total_revenue_usd / max(1, self.total_orders_placed), 2
            ),
            "categories_count": len(ServiceCategory)
        }


__all__ = [
    'CreatorMarketplace',
    'ServiceCategory',
    'ListingStatus',
    'ServiceListing',
    'MarketplaceOrder'
]
