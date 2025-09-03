"""Content Marketplace - Advanced Content Trading Platform
========================================================

Comprehensive marketplace for content creators to sell, license,
and distribute their digital content across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import uuid
import hashlib

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """Content type categories."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    TEMPLATE = "template"
    PRESET = "preset"
    FILTER = "filter"
    ANIMATION = "animation"


class ContentStatus(str, Enum):
    """Content status in marketplace."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    SOLD_OUT = "sold_out"
    ARCHIVED = "archived"


class LicenseType(str, Enum):
    """License types for content."""
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    EXCLUSIVE = "exclusive"
    EXTENDED = "extended"
    EDITORIAL = "editorial"
    COMMERCIAL = "commercial"


class MarketplaceCategory(str, Enum):
    """Marketplace categories."""
    PHOTOGRAPHY = "photography"
    VIDEOGRAPHY = "videography"
    MUSIC = "music"
    SOUND_EFFECTS = "sound_effects"
    TEMPLATES = "templates"
    GRAPHICS = "graphics"
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"


@dataclass
class ContentItem:
    """Content item in marketplace."""
    id: str
    creator_id: str
    title: str
    description: str
    content_type: ContentType
    category: MarketplaceCategory
    tags: List[str]
    price: Decimal
    license_type: LicenseType
    status: ContentStatus
    file_url: str
    preview_url: str
    thumbnail_url: str
    file_size: int
    dimensions: Optional[Dict[str, int]] = None
    duration: Optional[int] = None  # For video/audio in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    download_count: int = 0
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContentPurchase:
    """Content purchase record."""
    id: str
    content_id: str
    buyer_id: str
    license_type: LicenseType
    price_paid: Decimal
    usage_rights: Dict[str, Any]
    download_url: str
    license_agreement_url: str
    purchase_date: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


@dataclass
class MarketplaceStats:
    """Marketplace statistics."""
    total_content: int
    total_creators: int
    total_sales: int
    total_revenue: Decimal
    top_categories: List[Dict[str, Any]]
    trending_content: List[str]
    updated_at: datetime = field(default_factory=datetime.now)


class ContentMarketplace:
    """Advanced content marketplace management system."""
    
    def __init__(self):
        """Initialize content marketplace."""
        self.content_items: Dict[str, ContentItem] = {}
        self.purchases: Dict[str, ContentPurchase] = {}
        self.creator_earnings: Dict[str, Decimal] = {}
        self.marketplace_commission = Decimal("0.30")  # 30% commission
        
        logger.info("Content marketplace initialized")
    
    async def submit_content(
        self,
        creator_id: str,
        title: str,
        description: str,
        content_type: ContentType,
        category: MarketplaceCategory,
        file_url: str,
        price: Decimal,
        license_type: LicenseType = LicenseType.ROYALTY_FREE,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentItem:
        """Submit content to marketplace for review.
        
        Args:
            creator_id: Content creator identifier
            title: Content title
            description: Content description
            content_type: Type of content
            category: Marketplace category
            file_url: URL to content file
            price: Content price
            license_type: License type
            tags: Content tags
            metadata: Additional metadata
            
        Returns:
            Created content item
        """
        try:
            content_id = str(uuid.uuid4())
            
            # Generate preview and thumbnail URLs (in real implementation, would process files)
            preview_url = f"{file_url}_preview"
            thumbnail_url = f"{file_url}_thumbnail"
            
            content_item = ContentItem(
                id=content_id,
                creator_id=creator_id,
                title=title,
                description=description,
                content_type=content_type,
                category=category,
                tags=tags or [],
                price=price,
                license_type=license_type,
                status=ContentStatus.PENDING_REVIEW,
                file_url=file_url,
                preview_url=preview_url,
                thumbnail_url=thumbnail_url,
                file_size=0,  # Would be calculated from actual file
                metadata=metadata or {}
            )
            
            self.content_items[content_id] = content_item
            
            # Schedule review process
            asyncio.create_task(self._schedule_content_review(content_id))
            
            logger.info(f"Content submitted for review: {content_id}")
            return content_item
            
        except Exception as e:
            logger.error(f"Failed to submit content: {e}")
            raise
    
    async def _schedule_content_review(self, content_id: str) -> None:
        """Schedule automated content review.
        
        Args:
            content_id: Content identifier
        """
        try:
            # Simulate review delay
            await asyncio.sleep(2)  # 2 seconds for demo
            
            if content_id not in self.content_items:
                return
            
            content = self.content_items[content_id]
            
            # Automated review checks (simplified)
            review_passed = await self._perform_content_review(content)
            
            if review_passed:
                content.status = ContentStatus.APPROVED
                # Auto-activate approved content
                await asyncio.sleep(1)
                content.status = ContentStatus.ACTIVE
                logger.info(f"Content approved and activated: {content_id}")
            else:
                content.status = ContentStatus.REJECTED
                logger.info(f"Content rejected: {content_id}")
            
            content.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to review content: {e}")
    
    async def _perform_content_review(self, content: ContentItem) -> bool:
        """Perform automated content review.
        
        Args:
            content: Content to review
            
        Returns:
            True if content passes review
        """
        try:
            # Simplified review criteria
            checks = [
                len(content.title) >= 3,  # Title length
                len(content.description) >= 10,  # Description length
                content.price >= Decimal("0.99"),  # Minimum price
                len(content.tags) > 0,  # Has tags
                content.file_url.startswith("http"),  # Valid URL
            ]
            
            # 90% pass rate for demo
            import random
            automated_check = random.random() > 0.1
            
            return all(checks) and automated_check
            
        except Exception as e:
            logger.error(f"Review error: {e}")
            return False
    
    async def purchase_content(
        self,
        content_id: str,
        buyer_id: str,
        license_type: Optional[LicenseType] = None
    ) -> ContentPurchase:
        """Purchase content from marketplace.
        
        Args:
            content_id: Content identifier
            buyer_id: Buyer identifier
            license_type: Specific license type (if different from default)
            
        Returns:
            Purchase record
        """
        try:
            if content_id not in self.content_items:
                raise ValueError(f"Content not found: {content_id}")
            
            content = self.content_items[content_id]
            
            if content.status != ContentStatus.ACTIVE:
                raise ValueError(f"Content not available for purchase: {content.status}")
            
            purchase_id = str(uuid.uuid4())
            effective_license = license_type or content.license_type
            
            # Calculate price based on license type
            price_multiplier = {
                LicenseType.ROYALTY_FREE: Decimal("1.0"),
                LicenseType.RIGHTS_MANAGED: Decimal("1.5"),
                LicenseType.EXCLUSIVE: Decimal("5.0"),
                LicenseType.EXTENDED: Decimal("2.0"),
                LicenseType.EDITORIAL: Decimal("0.8"),
                LicenseType.COMMERCIAL: Decimal("2.5")
            }
            
            final_price = content.price * price_multiplier.get(effective_license, Decimal("1.0"))
            
            # Generate download URL (in real implementation, would be secure temporary URL)
            download_url = f"{content.file_url}?purchase={purchase_id}&buyer={buyer_id}"
            license_agreement_url = f"/licenses/{purchase_id}/agreement"
            
            # Set expiration for certain license types
            expires_at = None
            if effective_license == LicenseType.RIGHTS_MANAGED:
                expires_at = datetime.now() + timedelta(days=365)  # 1 year
            
            purchase = ContentPurchase(
                id=purchase_id,
                content_id=content_id,
                buyer_id=buyer_id,
                license_type=effective_license,
                price_paid=final_price,
                usage_rights={
                    "commercial_use": effective_license in [LicenseType.COMMERCIAL, LicenseType.EXTENDED],
                    "exclusive": effective_license == LicenseType.EXCLUSIVE,
                    "unlimited_use": effective_license == LicenseType.ROYALTY_FREE,
                    "territory": "worldwide",
                    "media": "all"
                },
                download_url=download_url,
                license_agreement_url=license_agreement_url,
                expires_at=expires_at
            )
            
            self.purchases[purchase_id] = purchase
            
            # Update content stats
            content.download_count += 1
            content.updated_at = datetime.now()
            
            # Calculate earnings
            creator_share = final_price * (Decimal("1.0") - self.marketplace_commission)
            if content.creator_id not in self.creator_earnings:
                self.creator_earnings[content.creator_id] = Decimal("0")
            self.creator_earnings[content.creator_id] += creator_share
            
            logger.info(f"Content purchased: {content_id} by {buyer_id} for ${final_price}")
            return purchase
            
        except Exception as e:
            logger.error(f"Failed to purchase content: {e}")
            raise
    
    async def search_content(
        self,
        query: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        category: Optional[MarketplaceCategory] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        license_type: Optional[LicenseType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[ContentItem]:
        """Search content in marketplace.
        
        Args:
            query: Search query
            content_type: Filter by content type
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            license_type: Filter by license type
            tags: Filter by tags
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of matching content items
        """
        try:
            results = []
            
            for content in self.content_items.values():
                # Only include active content
                if content.status != ContentStatus.ACTIVE:
                    continue
                
                # Apply filters
                if content_type and content.content_type != content_type:
                    continue
                
                if category and content.category != category:
                    continue
                
                if min_price and content.price < min_price:
                    continue
                
                if max_price and content.price > max_price:
                    continue
                
                if license_type and content.license_type != license_type:
                    continue
                
                if tags and not any(tag in content.tags for tag in tags):
                    continue
                
                # Text search in title and description
                if query:
                    search_text = f"{content.title} {content.description}".lower()
                    if query.lower() not in search_text:
                        continue
                
                results.append(content)
            
            # Sort by relevance (simplified: by download count and rating)
            results.sort(key=lambda x: (x.download_count, x.rating), reverse=True)
            
            # Apply pagination
            return results[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return []
    
    async def get_trending_content(self, limit: int = 10) -> List[ContentItem]:
        """Get trending content based on recent downloads and ratings.
        
        Args:
            limit: Maximum number of items
            
        Returns:
            List of trending content items
        """
        try:
            active_content = [
                content for content in self.content_items.values()
                if content.status == ContentStatus.ACTIVE
            ]
            
            # Sort by a combination of recent downloads and rating
            # Simplified trending algorithm
            def trending_score(content: ContentItem) -> float:
                recency_factor = max(0, 30 - (datetime.now() - content.updated_at).days) / 30
                download_score = min(content.download_count, 1000) / 1000  # Normalize
                rating_score = content.rating / 5.0 if content.rating > 0 else 0
                
                return (download_score * 0.4 + rating_score * 0.3 + recency_factor * 0.3)
            
            active_content.sort(key=trending_score, reverse=True)
            
            return active_content[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get trending content: {e}")
            return []
    
    async def rate_content(
        self,
        content_id: str,
        buyer_id: str,
        rating: float,
        review: Optional[str] = None
    ) -> bool:
        """Rate purchased content.
        
        Args:
            content_id: Content identifier
            buyer_id: Buyer identifier
            rating: Rating (1-5)
            review: Optional review text
            
        Returns:
            True if rating was recorded
        """
        try:
            if content_id not in self.content_items:
                raise ValueError(f"Content not found: {content_id}")
            
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")
            
            # Verify buyer has purchased this content
            has_purchased = any(
                p.content_id == content_id and p.buyer_id == buyer_id
                for p in self.purchases.values()
            )
            
            if not has_purchased:
                raise ValueError("Can only rate purchased content")
            
            content = self.content_items[content_id]
            
            # Simple rating calculation (in real implementation, would store individual ratings)
            total_rating = content.rating * content.review_count + rating
            content.review_count += 1
            content.rating = total_rating / content.review_count
            content.updated_at = datetime.now()
            
            logger.info(f"Content rated: {content_id} - {rating} stars")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rate content: {e}")
            return False
    
    async def get_creator_earnings(self, creator_id: str) -> Dict[str, Any]:
        """Get creator earnings summary.
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Earnings summary
        """
        try:
            total_earnings = self.creator_earnings.get(creator_id, Decimal("0"))
            
            # Get creator's content stats
            creator_content = [
                content for content in self.content_items.values()
                if content.creator_id == creator_id
            ]
            
            total_downloads = sum(content.download_count for content in creator_content)
            active_content_count = sum(
                1 for content in creator_content
                if content.status == ContentStatus.ACTIVE
            )
            
            return {
                "creator_id": creator_id,
                "total_earnings": total_earnings,
                "total_content": len(creator_content),
                "active_content": active_content_count,
                "total_downloads": total_downloads,
                "average_rating": sum(content.rating for content in creator_content) / len(creator_content) if creator_content else 0,
                "commission_rate": self.marketplace_commission
            }
            
        except Exception as e:
            logger.error(f"Failed to get creator earnings: {e}")
            return {}
    
    async def get_marketplace_stats(self) -> MarketplaceStats:
        """Get marketplace statistics.
        
        Returns:
            Marketplace statistics
        """
        try:
            total_content = len(self.content_items)
            total_creators = len(set(content.creator_id for content in self.content_items.values()))
            total_sales = len(self.purchases)
            total_revenue = sum(purchase.price_paid for purchase in self.purchases.values())
            
            # Top categories by content count
            category_counts = {}
            for content in self.content_items.values():
                category_counts[content.category.value] = category_counts.get(content.category.value, 0) + 1
            
            top_categories = [
                {"category": cat, "count": count}
                for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Trending content IDs
            trending = await self.get_trending_content(5)
            trending_content = [content.id for content in trending]
            
            return MarketplaceStats(
                total_content=total_content,
                total_creators=total_creators,
                total_sales=total_sales,
                total_revenue=total_revenue,
                top_categories=top_categories,
                trending_content=trending_content
            )
            
        except Exception as e:
            logger.error(f"Failed to get marketplace stats: {e}")
            return MarketplaceStats(0, 0, 0, Decimal("0"), [], [])
    
    async def get_content(self, content_id: str) -> Optional[ContentItem]:
        """Get content item by ID.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Content item if found
        """
        return self.content_items.get(content_id)
    
    async def get_purchase(self, purchase_id: str) -> Optional[ContentPurchase]:
        """Get purchase record by ID.
        
        Args:
            purchase_id: Purchase identifier
            
        Returns:
            Purchase record if found
        """
        return self.purchases.get(purchase_id)