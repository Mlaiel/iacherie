"""Service Catalog Module - Creator Service Management and Discovery Platform
===========================================================================

Advanced service catalog system providing service management, discovery,
categorization, template creation, and marketplace organization for creators.

This module implements:
- Comprehensive service categorization and tagging
- Service template creation and customization
- Advanced search and discovery algorithms
- Service package and bundle management
- Pricing tier configuration
- Quality assurance and verification

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
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import json
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class ServiceCategory(Enum):
    """Main service categories"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CONTENT = "video_content"
    GRAPHIC_DESIGN = "graphic_design"
    WRITING_CONTENT = "writing_content"
    VOICE_ACTING = "voice_acting"
    DIGITAL_MARKETING = "digital_marketing"
    SOCIAL_MEDIA = "social_media"
    PHOTOGRAPHY = "photography"
    ANIMATION = "animation"
    WEB_DEVELOPMENT = "web_development"
    CONSULTING = "consulting"
    TRANSLATION = "translation"


class ServiceType(Enum):
    """Service delivery types"""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    SUBSCRIPTION = "subscription"
    PROJECT_BASED = "project_based"
    HOURLY = "hourly"
    PACKAGE = "package"
    CUSTOM = "custom"


class ServiceStatus(Enum):
    """Service availability status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    DRAFT = "draft"
    ARCHIVED = "archived"


class QualityTier(Enum):
    """Service quality tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class DeliverySpeed(Enum):
    """Service delivery speed options"""
    EXPRESS = "express"  # 24 hours
    FAST = "fast"        # 1-3 days
    STANDARD = "standard" # 3-7 days
    EXTENDED = "extended" # 1-2 weeks
    CUSTOM = "custom"     # Negotiable


@dataclass
class ServiceTag:
    """Service tag for categorization"""
    tag_id: str
    name: str
    category: str
    weight: float = 1.0
    synonyms: List[str] = field(default_factory=list)


@dataclass
class PricingTier:
    """Service pricing tier"""
    tier_id: str
    name: str
    description: str
    price: Decimal
    currency: str = "USD"
    features: List[str] = field(default_factory=list)
    delivery_time: timedelta = field(default_factory=lambda: timedelta(days=7))
    revisions_included: int = 1
    extras: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class ServiceRequirement:
    """Service requirement specification"""
    requirement_id: str
    title: str
    description: str
    type: str  # "text", "file", "choice", "number", "boolean"
    required: bool = True
    options: List[str] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceDeliverable:
    """Service deliverable specification"""
    deliverable_id: str
    name: str
    description: str
    file_types: List[str] = field(default_factory=list)
    quantity: int = 1
    quality_requirements: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceReview:
    """Service review and rating"""
    review_id: str
    service_id: str
    buyer_id: str
    rating: float  # 1-5
    title: str
    content: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified_purchase: bool = False
    helpful_votes: int = 0


@dataclass
class Service:
    """Complete service definition"""
    service_id: str
    creator_id: str
    title: str
    description: str
    category: ServiceCategory
    subcategory: str
    tags: List[ServiceTag]
    service_type: ServiceType
    status: ServiceStatus
    quality_tier: QualityTier
    
    # Pricing and packages
    pricing_tiers: List[PricingTier]
    base_price: Decimal
    currency: str = "USD"
    
    # Service specifications
    requirements: List[ServiceRequirement]
    deliverables: List[ServiceDeliverable]
    delivery_speed: DeliverySpeed
    typical_delivery_time: timedelta
    
    # Content and media
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    portfolio_samples: List[str] = field(default_factory=list)
    
    # Performance metrics
    reviews: List[ServiceReview] = field(default_factory=list)
    average_rating: float = 0.0
    total_orders: int = 0
    completion_rate: float = 100.0
    response_time: timedelta = field(default_factory=lambda: timedelta(hours=24))
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_order_date: Optional[datetime] = None
    featured: bool = False
    verified: bool = False
    
    # Search and discovery
    search_keywords: List[str] = field(default_factory=list)
    seo_title: str = ""
    seo_description: str = ""
    view_count: int = 0
    favorite_count: int = 0


@dataclass
class ServiceTemplate:
    """Reusable service template"""
    template_id: str
    name: str
    description: str
    category: ServiceCategory
    template_data: Dict[str, Any]
    usage_count: int = 0
    created_by: str = "system"
    is_public: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceBundle:
    """Bundle of related services"""
    bundle_id: str
    name: str
    description: str
    service_ids: List[str]
    discount_percentage: float
    total_value: Decimal
    bundle_price: Decimal
    validity_period: timedelta
    created_by: str
    active: bool = True


class ServiceCatalog:
    """Advanced service catalog and discovery system"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.templates: Dict[str, ServiceTemplate] = {}
        self.bundles: Dict[str, ServiceBundle] = {}
        self.categories: Dict[ServiceCategory, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.tags: Dict[str, ServiceTag] = {}
        self.search_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Initialize default tags and templates
        self._initialize_default_tags()
        self._initialize_service_templates()
        
        logger.info("🗂️ Service Catalog initialized with advanced discovery system")
    
    def _initialize_default_tags(self):
        """Initialize default service tags"""
        default_tags = [
            # Music Production
            ("music_mixing", "Music Production", ["audio mixing", "mix", "mixing"]),
            ("music_mastering", "Music Production", ["audio mastering", "master", "mastering"]),
            ("beat_making", "Music Production", ["beats", "instrumentals", "backing tracks"]),
            ("songwriting", "Music Production", ["lyrics", "composition", "song creation"]),
            
            # Video Content
            ("video_editing", "Video Content", ["editing", "post-production", "montage"]),
            ("motion_graphics", "Video Content", ["animation", "graphics", "motion design"]),
            ("color_grading", "Video Content", ["color correction", "grading", "color"]),
            ("video_production", "Video Content", ["filming", "cinematography", "production"]),
            
            # Graphic Design
            ("logo_design", "Graphic Design", ["logo", "branding", "identity"]),
            ("web_design", "Graphic Design", ["website", "ui", "interface"]),
            ("print_design", "Graphic Design", ["flyer", "poster", "brochure"]),
            ("illustration", "Graphic Design", ["drawing", "artwork", "digital art"]),
            
            # Writing
            ("copywriting", "Writing", ["copy", "marketing copy", "sales copy"]),
            ("content_writing", "Writing", ["articles", "blog posts", "content"]),
            ("technical_writing", "Writing", ["documentation", "manuals", "guides"]),
            ("creative_writing", "Writing", ["stories", "fiction", "creative"]),
        ]
        
        for tag_name, category, synonyms in default_tags:
            tag_id = str(uuid.uuid4())
            self.tags[tag_id] = ServiceTag(
                tag_id=tag_id,
                name=tag_name,
                category=category,
                synonyms=synonyms
            )
    
    def _initialize_service_templates(self):
        """Initialize common service templates"""
        templates = [
            {
                "name": "Basic Music Production",
                "category": ServiceCategory.MUSIC_PRODUCTION,
                "data": {
                    "title": "Professional Music Production Services",
                    "description": "High-quality music production including mixing and mastering",
                    "pricing_tiers": [
                        {"name": "Basic", "price": 50, "features": ["Basic mixing", "1 revision"]},
                        {"name": "Standard", "price": 100, "features": ["Advanced mixing", "Mastering", "3 revisions"]},
                        {"name": "Premium", "price": 200, "features": ["Full production", "Mastering", "Unlimited revisions"]}
                    ],
                    "requirements": [
                        {"title": "Audio Files", "type": "file", "required": True},
                        {"title": "Style Preference", "type": "text", "required": False}
                    ]
                }
            },
            {
                "name": "Video Editing Service",
                "category": ServiceCategory.VIDEO_CONTENT,
                "data": {
                    "title": "Professional Video Editing",
                    "description": "Expert video editing and post-production services",
                    "pricing_tiers": [
                        {"name": "Basic", "price": 25, "features": ["Basic editing", "1 revision"]},
                        {"name": "Standard", "price": 75, "features": ["Advanced editing", "Color correction", "3 revisions"]},
                        {"name": "Premium", "price": 150, "features": ["Full post-production", "Motion graphics", "Unlimited revisions"]}
                    ]
                }
            },
            {
                "name": "Logo Design Package",
                "category": ServiceCategory.GRAPHIC_DESIGN,
                "data": {
                    "title": "Professional Logo Design",
                    "description": "Custom logo design for your brand",
                    "pricing_tiers": [
                        {"name": "Basic", "price": 30, "features": ["1 concept", "2 revisions"]},
                        {"name": "Standard", "price": 60, "features": ["3 concepts", "5 revisions", "Vector files"]},
                        {"name": "Premium", "price": 120, "features": ["5 concepts", "Unlimited revisions", "Brand package"]}
                    ]
                }
            }
        ]
        
        for template_data in templates:
            template_id = str(uuid.uuid4())
            self.templates[template_id] = ServiceTemplate(
                template_id=template_id,
                name=template_data["name"],
                description=template_data["data"]["description"],
                category=template_data["category"],
                template_data=template_data["data"]
            )
    
    async def create_service(
        self,
        creator_id: str,
        title: str,
        description: str,
        category: ServiceCategory,
        subcategory: str,
        service_type: ServiceType,
        base_price: Decimal,
        delivery_time: timedelta,
        template_id: Optional[str] = None
    ) -> Service:
        """Create a new service"""
        try:
            service_id = str(uuid.uuid4())
            
            # Use template if provided
            if template_id and template_id in self.templates:
                template = self.templates[template_id]
                template_data = template.template_data
                
                # Update template usage
                template.usage_count += 1
            else:
                template_data = {}
            
            # Generate SEO-friendly content
            seo_title = await self._generate_seo_title(title, category)
            seo_description = await self._generate_seo_description(description)
            search_keywords = await self._extract_keywords(title, description)
            
            # Create service
            service = Service(
                service_id=service_id,
                creator_id=creator_id,
                title=title,
                description=description,
                category=category,
                subcategory=subcategory,
                tags=[],
                service_type=service_type,
                status=ServiceStatus.DRAFT,
                quality_tier=QualityTier.STANDARD,
                pricing_tiers=[],
                base_price=base_price,
                requirements=[],
                deliverables=[],
                delivery_speed=DeliverySpeed.STANDARD,
                typical_delivery_time=delivery_time,
                seo_title=seo_title,
                seo_description=seo_description,
                search_keywords=search_keywords
            )
            
            # Apply template data if available
            if template_data:
                await self._apply_template_data(service, template_data)
            
            # Store service
            self.services[service_id] = service
            
            # Update search index
            await self._update_search_index(service)
            
            # Update category index
            self.categories[category][subcategory].append(service_id)
            
            logger.info(f"📝 Service created: {service_id} - {title}")
            return service
            
        except Exception as e:
            logger.error(f"❌ Error creating service: {e}")
            raise
    
    async def update_service(
        self,
        service_id: str,
        updates: Dict[str, Any],
        creator_id: Optional[str] = None
    ) -> Service:
        """Update existing service"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
            
            service = self.services[service_id]
            
            # Verify ownership if creator_id provided
            if creator_id and service.creator_id != creator_id:
                raise PermissionError("Not authorized to update this service")
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(service, field):
                    setattr(service, field, value)
            
            # Update timestamp
            service.updated_at = datetime.now(timezone.utc)
            
            # Regenerate SEO content if title or description changed
            if "title" in updates or "description" in updates:
                service.seo_title = await self._generate_seo_title(service.title, service.category)
                service.seo_description = await self._generate_seo_description(service.description)
                service.search_keywords = await self._extract_keywords(service.title, service.description)
            
            # Update search index
            await self._update_search_index(service)
            
            logger.info(f"✏️ Service updated: {service_id}")
            return service
            
        except Exception as e:
            logger.error(f"❌ Error updating service: {e}")
            raise
    
    async def add_pricing_tier(
        self,
        service_id: str,
        name: str,
        description: str,
        price: Decimal,
        features: List[str],
        delivery_time: Optional[timedelta] = None,
        revisions: int = 1
    ) -> PricingTier:
        """Add pricing tier to service"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
            
            service = self.services[service_id]
            tier_id = str(uuid.uuid4())
            
            pricing_tier = PricingTier(
                tier_id=tier_id,
                name=name,
                description=description,
                price=price,
                currency=service.currency,
                features=features,
                delivery_time=delivery_time or service.typical_delivery_time,
                revisions_included=revisions
            )
            
            service.pricing_tiers.append(pricing_tier)
            service.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"💰 Pricing tier added to {service_id}: {name}")
            return pricing_tier
            
        except Exception as e:
            logger.error(f"❌ Error adding pricing tier: {e}")
            raise
    
    async def add_service_requirement(
        self,
        service_id: str,
        title: str,
        description: str,
        requirement_type: str,
        required: bool = True,
        options: Optional[List[str]] = None,
        validation_rules: Optional[Dict[str, Any]] = None
    ) -> ServiceRequirement:
        """Add requirement to service"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
            
            service = self.services[service_id]
            requirement_id = str(uuid.uuid4())
            
            requirement = ServiceRequirement(
                requirement_id=requirement_id,
                title=title,
                description=description,
                type=requirement_type,
                required=required,
                options=options or [],
                validation_rules=validation_rules or {}
            )
            
            service.requirements.append(requirement)
            service.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"📋 Requirement added to {service_id}: {title}")
            return requirement
            
        except Exception as e:
            logger.error(f"❌ Error adding service requirement: {e}")
            raise
    
    async def search_services(
        self,
        query: str,
        category: Optional[ServiceCategory] = None,
        price_range: Optional[Tuple[Decimal, Decimal]] = None,
        delivery_speed: Optional[DeliverySpeed] = None,
        quality_tier: Optional[QualityTier] = None,
        rating_min: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Service]:
        """Advanced service search with filters"""
        try:
            # Start with all services
            candidate_services = list(self.services.values())
            
            # Apply basic filters
            if category:
                candidate_services = [s for s in candidate_services if s.category == category]
            
            if price_range:
                min_price, max_price = price_range
                candidate_services = [
                    s for s in candidate_services
                    if min_price <= s.base_price <= max_price
                ]
            
            if delivery_speed:
                candidate_services = [s for s in candidate_services if s.delivery_speed == delivery_speed]
            
            if quality_tier:
                candidate_services = [s for s in candidate_services if s.quality_tier == quality_tier]
            
            if rating_min:
                candidate_services = [s for s in candidate_services if s.average_rating >= rating_min]
            
            # Only active services
            candidate_services = [s for s in candidate_services if s.status == ServiceStatus.ACTIVE]
            
            # Apply text search
            if query.strip():
                scored_services = await self._score_services_by_query(query, candidate_services)
                # Sort by relevance score
                candidate_services = [service for service, score in scored_services if score > 0]
            
            # Apply pagination
            total_results = len(candidate_services)
            paginated_services = candidate_services[offset:offset + limit]
            
            logger.info(f"🔍 Search completed: {total_results} results for '{query}'")
            return paginated_services
            
        except Exception as e:
            logger.error(f"❌ Error searching services: {e}")
            return []
    
    async def get_trending_services(
        self,
        category: Optional[ServiceCategory] = None,
        time_period: timedelta = timedelta(days=7),
        limit: int = 10
    ) -> List[Service]:
        """Get trending services based on recent activity"""
        try:
            cutoff_date = datetime.now(timezone.utc) - time_period
            
            # Get services with recent activity
            active_services = [
                s for s in self.services.values()
                if s.status == ServiceStatus.ACTIVE and
                (s.last_order_date and s.last_order_date >= cutoff_date)
            ]
            
            if category:
                active_services = [s for s in active_services if s.category == category]
            
            # Calculate trending score
            trending_services = []
            for service in active_services:
                score = await self._calculate_trending_score(service, time_period)
                trending_services.append((service, score))
            
            # Sort by trending score
            trending_services.sort(key=lambda x: x[1], reverse=True)
            
            return [service for service, score in trending_services[:limit]]
            
        except Exception as e:
            logger.error(f"❌ Error getting trending services: {e}")
            return []
    
    async def get_recommended_services(
        self,
        user_id: str,
        based_on_history: bool = True,
        limit: int = 10
    ) -> List[Service]:
        """Get personalized service recommendations"""
        try:
            # Get user's order history and preferences
            user_preferences = await self._get_user_preferences(user_id)
            
            # Get services matching preferences
            recommended_services = []
            
            for service in self.services.values():
                if service.status != ServiceStatus.ACTIVE:
                    continue
                
                score = await self._calculate_recommendation_score(service, user_preferences)
                if score > 0:
                    recommended_services.append((service, score))
            
            # Sort by recommendation score
            recommended_services.sort(key=lambda x: x[1], reverse=True)
            
            return [service for service, score in recommended_services[:limit]]
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {e}")
            return []
    
    async def create_service_bundle(
        self,
        name: str,
        description: str,
        service_ids: List[str],
        discount_percentage: float,
        created_by: str,
        validity_days: int = 30
    ) -> ServiceBundle:
        """Create service bundle with discount"""
        try:
            # Validate service IDs
            for service_id in service_ids:
                if service_id not in self.services:
                    raise ValueError(f"Service {service_id} not found")
            
            # Calculate total value
            total_value = sum(
                self.services[service_id].base_price
                for service_id in service_ids
            )
            
            # Calculate bundle price with discount
            bundle_price = total_value * (1 - discount_percentage / 100)
            
            bundle_id = str(uuid.uuid4())
            bundle = ServiceBundle(
                bundle_id=bundle_id,
                name=name,
                description=description,
                service_ids=service_ids,
                discount_percentage=discount_percentage,
                total_value=total_value,
                bundle_price=bundle_price,
                validity_period=timedelta(days=validity_days),
                created_by=created_by
            )
            
            self.bundles[bundle_id] = bundle
            
            logger.info(f"📦 Service bundle created: {bundle_id} - {name}")
            return bundle
            
        except Exception as e:
            logger.error(f"❌ Error creating service bundle: {e}")
            raise
    
    async def add_service_review(
        self,
        service_id: str,
        buyer_id: str,
        rating: float,
        title: str,
        content: str,
        pros: Optional[List[str]] = None,
        cons: Optional[List[str]] = None,
        verified_purchase: bool = False
    ) -> ServiceReview:
        """Add review to service"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
            
            # Validate rating
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            review_id = str(uuid.uuid4())
            review = ServiceReview(
                review_id=review_id,
                service_id=service_id,
                buyer_id=buyer_id,
                rating=rating,
                title=title,
                content=content,
                pros=pros or [],
                cons=cons or [],
                verified_purchase=verified_purchase
            )
            
            service = self.services[service_id]
            service.reviews.append(review)
            
            # Update average rating
            service.average_rating = await self._calculate_average_rating(service)
            service.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"⭐ Review added to {service_id}: {rating} stars")
            return review
            
        except Exception as e:
            logger.error(f"❌ Error adding service review: {e}")
            raise
    
    async def get_service_analytics(
        self,
        service_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get service performance analytics"""
        try:
            if service_id not in self.services:
                raise ValueError(f"Service {service_id} not found")
            
            service = self.services[service_id]
            cutoff_date = datetime.now(timezone.utc) - time_period
            
            # Recent reviews
            recent_reviews = [
                r for r in service.reviews
                if r.created_at >= cutoff_date
            ]
            
            analytics = {
                "service_id": service_id,
                "period_days": time_period.days,
                "general_metrics": {
                    "total_orders": service.total_orders,
                    "completion_rate": service.completion_rate,
                    "average_rating": service.average_rating,
                    "total_reviews": len(service.reviews),
                    "view_count": service.view_count,
                    "favorite_count": service.favorite_count
                },
                "recent_performance": {
                    "recent_reviews": len(recent_reviews),
                    "recent_avg_rating": sum(r.rating for r in recent_reviews) / len(recent_reviews) if recent_reviews else 0,
                    "rating_distribution": await self._calculate_rating_distribution(recent_reviews),
                },
                "trending_score": await self._calculate_trending_score(service, time_period),
                "conversion_insights": await self._calculate_conversion_insights(service),
                "optimization_suggestions": await self._generate_optimization_suggestions(service)
            }
            
            logger.info(f"📊 Analytics generated for service {service_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting service analytics: {e}")
            return {}
    
    # Helper methods
    async def _apply_template_data(self, service: Service, template_data: Dict[str, Any]):
        """Apply template data to service"""
        if "pricing_tiers" in template_data:
            for tier_data in template_data["pricing_tiers"]:
                tier = PricingTier(
                    tier_id=str(uuid.uuid4()),
                    name=tier_data["name"],
                    description=tier_data.get("description", ""),
                    price=Decimal(str(tier_data["price"])),
                    features=tier_data.get("features", [])
                )
                service.pricing_tiers.append(tier)
        
        if "requirements" in template_data:
            for req_data in template_data["requirements"]:
                req = ServiceRequirement(
                    requirement_id=str(uuid.uuid4()),
                    title=req_data["title"],
                    description=req_data.get("description", ""),
                    type=req_data["type"],
                    required=req_data.get("required", True)
                )
                service.requirements.append(req)
    
    async def _generate_seo_title(self, title: str, category: ServiceCategory) -> str:
        """Generate SEO-optimized title"""
        # Add category context for better SEO
        category_keywords = {
            ServiceCategory.MUSIC_PRODUCTION: "Music Production",
            ServiceCategory.VIDEO_CONTENT: "Video Editing",
            ServiceCategory.GRAPHIC_DESIGN: "Graphic Design",
            ServiceCategory.WRITING_CONTENT: "Content Writing"
        }
        
        category_keyword = category_keywords.get(category, "Professional Services")
        
        if category_keyword.lower() not in title.lower():
            return f"{title} - {category_keyword} Services"
        
        return title
    
    async def _generate_seo_description(self, description: str) -> str:
        """Generate SEO-optimized description"""
        # Truncate and optimize for search
        if len(description) > 155:
            return description[:152] + "..."
        return description
    
    async def _extract_keywords(self, title: str, description: str) -> List[str]:
        """Extract search keywords from title and description"""
        text = f"{title} {description}".lower()
        
        # Remove common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Extract words (3+ characters)
        words = re.findall(r'\b\w{3,}\b', text)
        keywords = [word for word in words if word not in stop_words]
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for keyword in keywords:
            if keyword not in seen:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        return unique_keywords[:20]  # Limit to 20 keywords
    
    async def _update_search_index(self, service: Service):
        """Update search index for service"""
        # Clear existing entries for this service
        for keyword_set in self.search_index.values():
            keyword_set.discard(service.service_id)
        
        # Add new entries
        all_text = f"{service.title} {service.description} {' '.join(service.search_keywords)}"
        keywords = await self._extract_keywords(all_text, "")
        
        for keyword in keywords:
            self.search_index[keyword].add(service.service_id)
        
        # Add category and tags
        self.search_index[service.category.value].add(service.service_id)
        self.search_index[service.subcategory].add(service.service_id)
        
        for tag in service.tags:
            self.search_index[tag.name].add(service.service_id)
    
    async def _score_services_by_query(self, query: str, services: List[Service]) -> List[Tuple[Service, float]]:
        """Score services by search query relevance"""
        query_keywords = await self._extract_keywords(query, "")
        scored_services = []
        
        for service in services:
            score = 0.0
            
            # Title matches (highest weight)
            for keyword in query_keywords:
                if keyword in service.title.lower():
                    score += 10.0
            
            # Description matches
            for keyword in query_keywords:
                if keyword in service.description.lower():
                    score += 5.0
            
            # Tag matches
            for tag in service.tags:
                for keyword in query_keywords:
                    if keyword in tag.name.lower() or keyword in tag.synonyms:
                        score += 3.0
            
            # Category/subcategory matches
            for keyword in query_keywords:
                if keyword in service.category.value or keyword in service.subcategory.lower():
                    score += 2.0
            
            # Boost popular services
            score += service.average_rating * 0.5
            score += min(service.total_orders / 10, 5.0)  # Cap boost at 5 points
            
            if score > 0:
                scored_services.append((service, score))
        
        return sorted(scored_services, key=lambda x: x[1], reverse=True)
    
    async def _calculate_trending_score(self, service: Service, time_period: timedelta) -> float:
        """Calculate trending score for service"""
        score = 0.0
        
        # Recent orders weight
        if service.last_order_date:
            days_since_order = (datetime.now(timezone.utc) - service.last_order_date).days
            if days_since_order <= time_period.days:
                score += max(0, 10 - days_since_order)
        
        # View count weight
        score += min(service.view_count / 100, 5.0)
        
        # Rating weight
        score += service.average_rating
        
        # Favorite count weight
        score += min(service.favorite_count / 10, 3.0)
        
        return score
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for recommendations"""
        # In real implementation, would fetch from user service
        return {
            "preferred_categories": [ServiceCategory.MUSIC_PRODUCTION, ServiceCategory.VIDEO_CONTENT],
            "price_range": (Decimal("50"), Decimal("200")),
            "quality_preference": QualityTier.PREMIUM,
            "past_orders": []
        }
    
    async def _calculate_recommendation_score(self, service: Service, preferences: Dict[str, Any]) -> float:
        """Calculate recommendation score for user"""
        score = 0.0
        
        # Category preference
        if service.category in preferences.get("preferred_categories", []):
            score += 10.0
        
        # Price range preference
        price_range = preferences.get("price_range")
        if price_range and price_range[0] <= service.base_price <= price_range[1]:
            score += 5.0
        
        # Quality preference
        quality_pref = preferences.get("quality_preference")
        if quality_pref and service.quality_tier == quality_pref:
            score += 3.0
        
        # General quality indicators
        score += service.average_rating * 2
        score += min(service.completion_rate / 20, 5.0)
        
        return score
    
    async def _calculate_average_rating(self, service: Service) -> float:
        """Calculate average rating for service"""
        if not service.reviews:
            return 0.0
        
        total_rating = sum(review.rating for review in service.reviews)
        return total_rating / len(service.reviews)
    
    async def _calculate_rating_distribution(self, reviews: List[ServiceReview]) -> Dict[str, int]:
        """Calculate rating distribution"""
        distribution = {str(i): 0 for i in range(1, 6)}
        
        for review in reviews:
            rating_key = str(int(review.rating))
            distribution[rating_key] += 1
        
        return distribution
    
    async def _calculate_conversion_insights(self, service: Service) -> Dict[str, Any]:
        """Calculate conversion insights"""
        # In real implementation, would analyze view-to-order conversion
        view_to_order_rate = (service.total_orders / max(service.view_count, 1)) * 100
        
        return {
            "view_to_order_rate": view_to_order_rate,
            "favorite_rate": (service.favorite_count / max(service.view_count, 1)) * 100,
            "repeat_customer_rate": 15.0  # Placeholder
        }
    
    async def _generate_optimization_suggestions(self, service: Service) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if service.average_rating < 4.0:
            suggestions.append("Improve service quality to increase ratings")
        
        if len(service.images) < 3:
            suggestions.append("Add more portfolio images to showcase your work")
        
        if not service.videos:
            suggestions.append("Add video samples to increase engagement")
        
        if len(service.pricing_tiers) < 3:
            suggestions.append("Create multiple pricing tiers to cater to different budgets")
        
        if service.view_count > 100 and service.total_orders < 10:
            suggestions.append("Optimize pricing or service description to improve conversion")
        
        return suggestions[:5]


# Example usage
async def main():
    """Example usage of service catalog"""
    catalog = ServiceCatalog()
    
    # Create a service
    service = await catalog.create_service(
        creator_id="creator_001",
        title="Professional Music Production",
        description="High-quality music production, mixing, and mastering services for artists",
        category=ServiceCategory.MUSIC_PRODUCTION,
        subcategory="mixing_mastering",
        service_type=ServiceType.PROJECT_BASED,
        base_price=Decimal("100"),
        delivery_time=timedelta(days=7)
    )
    
    print(f"Service created: {service.service_id}")
    
    # Add pricing tiers
    basic_tier = await catalog.add_pricing_tier(
        service_id=service.service_id,
        name="Basic",
        description="Basic mixing only",
        price=Decimal("50"),
        features=["Basic mixing", "1 revision"],
        revisions=1
    )
    
    premium_tier = await catalog.add_pricing_tier(
        service_id=service.service_id,
        name="Premium",
        description="Full production package",
        price=Decimal("200"),
        features=["Advanced mixing", "Mastering", "Unlimited revisions"],
        revisions=-1  # Unlimited
    )
    
    # Add requirements
    await catalog.add_service_requirement(
        service_id=service.service_id,
        title="Audio Files",
        description="Please provide your audio files in WAV or AIFF format",
        requirement_type="file",
        required=True
    )
    
    # Search services
    results = await catalog.search_services(
        query="music production mixing",
        category=ServiceCategory.MUSIC_PRODUCTION,
        price_range=(Decimal("50"), Decimal("150"))
    )
    
    print(f"Search results: {len(results)} services found")
    
    # Add a review
    review = await catalog.add_service_review(
        service_id=service.service_id,
        buyer_id="buyer_001",
        rating=4.5,
        title="Great work!",
        content="Excellent mixing quality and fast delivery",
        pros=["Professional quality", "Fast turnaround"],
        cons=["Could be more affordable"],
        verified_purchase=True
    )
    
    print(f"Review added: {review.rating} stars")
    
    # Get analytics
    analytics = await catalog.get_service_analytics(service.service_id)
    print(f"Service analytics: {analytics['general_metrics']}")


if __name__ == "__main__":
    asyncio.run(main())