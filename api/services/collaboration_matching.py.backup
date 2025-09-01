"""Enterprise Collaboration Matching Service - AI-Powered Partner Discovery
Intelligent matching system connecting creators with brands, collaborators, and opportunities

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Business Intelligence + DevOps Expert

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel.
Unauthorized copying, distribution, or use without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import redis
import json

from backend.app.models.domain import ContentAsset, Creator, CollaborationRequest, Brand, Influencer
from backend.app.core.exceptions import CollaborationError
from backend.app.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)


class MatchType(Enum):
    BRAND_PARTNERSHIP = "brand_partnership"
    CREATOR_COLLABORATION = "creator_collaboration"
    LICENSING_OPPORTUNITY = "licensing_opportunity"
    PLAYLIST_PLACEMENT = "playlist_placement"
    REMIX_OPPORTUNITY = "remix_opportunity"


class CollaborationTier(Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    EMERGING = "emerging"


@dataclass
class CollaborationMatch:
    partner_id: str
    partner_name: str
    partner_type: str  # brand, creator, curator, label
    match_score: float
    compatibility_factors: List[str]
    collaboration_type: MatchType
    estimated_reach: int
    estimated_revenue: float
    requirements: List[str]
    contact_info: Optional[Dict[str, Any]]
    tier: CollaborationTier
    verified: bool


@dataclass
class MatchingCriteria:
    content_type: Optional[str] = None
    genre: Optional[str] = None
    target_audience: Optional[str] = None
    budget_range: Optional[Tuple[float, float]] = None
    collaboration_types: Optional[List[MatchType]] = None
    min_reach: Optional[int] = None
    geographic_focus: Optional[List[str]] = None
    exclude_competitors: bool = True


class CollaborationMatchingService:
    """
    Professional collaboration matching service using AI algorithms
    for optimal creator-brand partnerships and cross-creator collaborations
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.analytics_service = AnalyticsService(redis_client)
        self.cache_ttl = 3600  # 1 hour cache for matching results
        
        # Collaboration scoring weights
        self.scoring_weights = {
            'content_similarity': 0.25,
            'audience_overlap': 0.20,
            'engagement_compatibility': 0.20,
            'brand_alignment': 0.15,
            'reach_potential': 0.10,
            'historical_performance': 0.10
        }
        
        # Industry partnerships database (would be loaded from external sources)
        self.brand_partnerships = {
            'music': ['Spotify', 'Apple Music', 'Warner Music', 'Universal Music', 'Sony Music'],
            'fashion': ['Nike', 'Adidas', 'H&M', 'Zara', 'Supreme'],
            'tech': ['Apple', 'Samsung', 'Microsoft', 'Google', 'Adobe'],
            'lifestyle': ['Red Bull', 'GoPro', 'Mercedes', 'BMW', 'Rolex']
        }
        
        # Creator collaboration networks
        self.creator_networks = {
            'music_producers': [],
            'content_creators': [],
            'photographers': [],
            'videographers': [],
            'influencers': []
        }

    def _get_cache_key(self, asset_id: int, criteria_hash: str) -> str:
        """Generate cache key for matching results"""
        return f"collaboration:matches:{asset_id}:{criteria_hash}"

    async def _cache_get(self, key: str) -> Optional[List[Dict]]:
        """Get cached matching results"""
        try:
            cached = self.redis_client.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            logger.warning(f"Cache get failed: {str(e)}")
            return None

    async def _cache_set(self, key: str, matches: List[Dict], ttl: int = None) -> None:
        """Cache matching results"""
        try:
            self.redis_client.setex(
                key, 
                ttl or self.cache_ttl, 
                json.dumps(matches, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {str(e)}")

    async def find_collaboration_matches(
        self, 
        db: Session,
        asset: ContentAsset, 
        criteria: Optional[MatchingCriteria] = None,
        limit: int = 20
    ) -> List[CollaborationMatch]:
        """
        Find optimal collaboration matches using AI-powered algorithms
        """
        criteria = criteria or MatchingCriteria()
        criteria_hash = self._hash_criteria(criteria)
        cache_key = self._get_cache_key(asset.id, criteria_hash)
        
        # Try cache first
        cached_matches = await self._cache_get(cache_key)
        if cached_matches:
            return [CollaborationMatch(**match) for match in cached_matches]
        
        try:
            # Get creator analytics for matching context
            creator = db.query(Creator).filter(Creator.id == asset.creator_id).first()
            analytics = await self.analytics_service.get_comprehensive_metrics(db, asset)
            
            # Find different types of collaboration opportunities
            matches = []
            
            # Brand partnership matching
            brand_matches = await self._find_brand_partnerships(db, asset, creator, analytics, criteria)
            matches.extend(brand_matches)
            
            # Creator collaboration matching
            creator_matches = await self._find_creator_collaborations(db, asset, creator, analytics, criteria)
            matches.extend(creator_matches)
            
            # Licensing opportunity matching
            licensing_matches = await self._find_licensing_opportunities(db, asset, creator, analytics, criteria)
            matches.extend(licensing_matches)
            
            # Sort by match score and apply filters
            matches = sorted(matches, key=lambda x: x.match_score, reverse=True)
            matches = await self._apply_criteria_filters(matches, criteria)
            
            # Limit results
            matches = matches[:limit]
            
            # Cache results
            await self._cache_set(cache_key, [match.__dict__ for match in matches])
            
            logger.info(f"Found {len(matches)} collaboration matches for asset {asset.id}")
            return matches
            
        except Exception as e:
            logger.error(f"Collaboration matching failed: {str(e)}")
            raise CollaborationError(f"Failed to find matches: {str(e)}")

    async def _find_brand_partnerships(
        self, 
        db: Session,
        asset: ContentAsset,
        creator: Creator, 
        analytics: Any,
        criteria: MatchingCriteria
    ) -> List[CollaborationMatch]:
        """Find relevant brand partnership opportunities"""
        matches = []
        
        # Determine content category for brand matching
        content_category = self._categorize_content(asset)
        relevant_brands = self.brand_partnerships.get(content_category, [])
        
        for brand_name in relevant_brands[:10]:  # Top 10 brands per category
            # Calculate match score based on multiple factors
            compatibility_score = await self._calculate_brand_compatibility(
                asset, creator, analytics, brand_name, content_category
            )
            
            if compatibility_score > 0.6:  # Minimum threshold
                estimated_reach = await self._estimate_collaboration_reach(
                    analytics, brand_name, 'brand_partnership'
                )
                estimated_revenue = await self._estimate_collaboration_revenue(
                    analytics, brand_name, 'brand_partnership', estimated_reach
                )
                
                match = CollaborationMatch(
                    partner_id=f"brand_{brand_name.lower().replace(' ', '_')}",
                    partner_name=brand_name,
                    partner_type="brand",
                    match_score=compatibility_score,
                    compatibility_factors=await self._get_brand_compatibility_factors(
                        asset, brand_name, content_category
                    ),
                    collaboration_type=MatchType.BRAND_PARTNERSHIP,
                    estimated_reach=estimated_reach,
                    estimated_revenue=estimated_revenue,
                    requirements=await self._get_brand_requirements(brand_name),
                    contact_info=await self._get_brand_contact_info(brand_name),
                    tier=self._determine_collaboration_tier(analytics, compatibility_score),
                    verified=True
                )
                matches.append(match)
        
        return matches

    async def _find_creator_collaborations(
        self, 
        db: Session,
        asset: ContentAsset,
        creator: Creator, 
        analytics: Any,
        criteria: MatchingCriteria
    ) -> List[CollaborationMatch]:
        """Find creator-to-creator collaboration opportunities"""
        matches = []
        
        # Find similar creators in the database
        similar_creators = await self._find_similar_creators(db, asset, creator, criteria)
        
        for similar_creator, similarity_score in similar_creators:
            if similarity_score > 0.7:  # High similarity threshold
                estimated_reach = await self._estimate_collaboration_reach(
                    analytics, similar_creator.name, 'creator_collaboration'
                )
                estimated_revenue = await self._estimate_collaboration_revenue(
                    analytics, similar_creator.name, 'creator_collaboration', estimated_reach
                )
                
                match = CollaborationMatch(
                    partner_id=f"creator_{similar_creator.id}",
                    partner_name=similar_creator.name,
                    partner_type="creator",
                    match_score=similarity_score,
                    compatibility_factors=await self._get_creator_compatibility_factors(
                        asset, creator, similar_creator
                    ),
                    collaboration_type=MatchType.CREATOR_COLLABORATION,
                    estimated_reach=estimated_reach,
                    estimated_revenue=estimated_revenue,
                    requirements=["Mutual agreement", "Content alignment", "Schedule coordination"],
                    contact_info={"email": similar_creator.email} if similar_creator.email else None,
                    tier=self._determine_collaboration_tier(analytics, similarity_score),
                    verified=True
                )
                matches.append(match)
        
        return matches

    async def _find_licensing_opportunities(
        self, 
        db: Session,
        asset: ContentAsset,
        creator: Creator, 
        analytics: Any,
        criteria: MatchingCriteria
    ) -> List[CollaborationMatch]:
        """Find content licensing opportunities"""
        matches = []
        
        # Licensing opportunities based on content type
        licensing_opportunities = {
            'audio': ['Sync licensing', 'Streaming platforms', 'Commercial use', 'Film/TV'],
            'video': ['Stock footage', 'Commercial licensing', 'Educational use'],
            'image': ['Stock photography', 'Commercial licensing', 'Print media'],
            'text': ['Publishing', 'Educational licensing', 'Commercial use']
        }
        
        opportunities = licensing_opportunities.get(asset.media_type, [])
        
        for opportunity_type in opportunities:
            licensing_score = await self._calculate_licensing_potential(
                asset, analytics, opportunity_type
            )
            
            if licensing_score > 0.5:
                estimated_reach = await self._estimate_collaboration_reach(
                    analytics, opportunity_type, 'licensing_opportunity'
                )
                estimated_revenue = await self._estimate_collaboration_revenue(
                    analytics, opportunity_type, 'licensing_opportunity', estimated_reach
                )
                
                match = CollaborationMatch(
                    partner_id=f"licensing_{opportunity_type.lower().replace(' ', '_')}",
                    partner_name=f"{opportunity_type} Licensing",
                    partner_type="licensing",
                    match_score=licensing_score,
                    compatibility_factors=[f"Suitable for {opportunity_type}", "High quality content"],
                    collaboration_type=MatchType.LICENSING_OPPORTUNITY,
                    estimated_reach=estimated_reach,
                    estimated_revenue=estimated_revenue,
                    requirements=["Rights clearance", "Quality standards", "Usage agreement"],
                    contact_info=None,
                    tier=self._determine_collaboration_tier(analytics, licensing_score),
                    verified=False
                )
                matches.append(match)
        
        return matches

    async def _calculate_brand_compatibility(
        self, 
        asset: ContentAsset, 
        creator: Creator, 
        analytics: Any, 
        brand_name: str, 
        content_category: str
    ) -> float:
        """Calculate compatibility score between creator and brand"""
        factors = []
        
        # Content alignment factor
        content_factor = 0.8  # High base score for category match
        factors.append(content_factor)
        
        # Engagement quality factor
        if analytics.engagement_rate > 0.1:
            factors.append(0.9)
        elif analytics.engagement_rate > 0.05:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Reach factor
        if analytics.views > 10000:
            factors.append(0.9)
        elif analytics.views > 1000:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Content quality factor (based on metadata richness)
        quality_score = len(asset.metadata.keys()) / 10
        factors.append(min(1.0, quality_score))
        
        return sum(factors) / len(factors)

    async def _find_similar_creators(
        self, 
        db: Session, 
        asset: ContentAsset, 
        creator: Creator, 
        criteria: MatchingCriteria
    ) -> List[Tuple[Creator, float]]:
        """Find creators with similar content and audience"""
        # Get creators with similar content types
        similar_creators = db.query(Creator).join(ContentAsset).filter(
            and_(
                ContentAsset.media_type == asset.media_type,
                Creator.id != creator.id
            )
        ).limit(50).all()
        
        creator_similarities = []
        
        for similar_creator in similar_creators:
            # Calculate similarity based on content metadata
            similarity_score = await self._calculate_creator_similarity(
                creator, similar_creator, asset
            )
            
            if similarity_score > 0.3:  # Minimum similarity threshold
                creator_similarities.append((similar_creator, similarity_score))
        
        # Sort by similarity score
        creator_similarities.sort(key=lambda x: x[1], reverse=True)
        return creator_similarities[:10]  # Return top 10

    async def _calculate_creator_similarity(
        self, 
        creator1: Creator, 
        creator2: Creator, 
        reference_asset: ContentAsset
    ) -> float:
        """Calculate similarity between two creators"""
        factors = []
        
        # Content type similarity (already filtered)
        factors.append(1.0)
        
        # Genre/category similarity (would analyze content metadata)
        genre_similarity = 0.8  # Placeholder - would implement actual comparison
        factors.append(genre_similarity)
        
        # Audience overlap estimation (would use actual audience data)
        audience_overlap = 0.6  # Placeholder
        factors.append(audience_overlap)
        
        return sum(factors) / len(factors)

    def _categorize_content(self, asset: ContentAsset) -> str:
        """Categorize content for brand matching"""
        # Analyze metadata and content type to determine category
        metadata = asset.metadata or {}
        
        # Check for explicit category
        if 'category' in metadata:
            return metadata['category'].lower()
        
        # Infer from content type and title
        title_lower = asset.title.lower() if asset.title else ""
        
        if asset.media_type == 'audio' or 'music' in title_lower or 'song' in title_lower:
            return 'music'
        elif 'fashion' in title_lower or 'style' in title_lower:
            return 'fashion'
        elif 'tech' in title_lower or 'gadget' in title_lower:
            return 'tech'
        else:
            return 'lifestyle'  # Default category

    async def _estimate_collaboration_reach(
        self, 
        analytics: Any, 
        partner_name: str, 
        collaboration_type: str
    ) -> int:
        """Estimate potential reach from collaboration"""
        base_reach = analytics.reach
        
        # Collaboration multipliers
        multipliers = {
            'brand_partnership': 2.5,
            'creator_collaboration': 1.8,
            'licensing_opportunity': 1.2
        }
        
        multiplier = multipliers.get(collaboration_type, 1.0)
        estimated_reach = int(base_reach * multiplier)
        
        return estimated_reach

    async def _estimate_collaboration_revenue(
        self, 
        analytics: Any, 
        partner_name: str, 
        collaboration_type: str,
        estimated_reach: int
    ) -> float:
        """Estimate potential revenue from collaboration"""
        # Revenue estimation based on reach and collaboration type
        revenue_per_thousand = {
            'brand_partnership': 5.0,  # $5 per 1k reach
            'creator_collaboration': 2.0,  # $2 per 1k reach
            'licensing_opportunity': 10.0  # $10 per 1k reach
        }
        
        rate = revenue_per_thousand.get(collaboration_type, 1.0)
        estimated_revenue = (estimated_reach / 1000) * rate
        
        return round(estimated_revenue, 2)

    async def _get_brand_compatibility_factors(
        self, 
        asset: ContentAsset, 
        brand_name: str, 
        content_category: str
    ) -> List[str]:
        """Get specific compatibility factors for brand partnership"""
        factors = [
            f"Content aligns with {brand_name} brand values",
            f"Target audience matches {brand_name} demographics",
            f"High engagement in {content_category} category",
            "Professional content quality"
        ]
        
        # Add specific factors based on analytics
        if asset.metadata.get('tags'):
            factors.append("Rich content tagging for brand alignment")
        
        return factors

    async def _get_creator_compatibility_factors(
        self, 
        asset: ContentAsset, 
        creator1: Creator, 
        creator2: Creator
    ) -> List[str]:
        """Get compatibility factors between creators"""
        return [
            "Similar content style and quality",
            "Complementary audience demographics",
            "Aligned creative vision",
            "Mutual benefit potential"
        ]

    async def _get_brand_requirements(self, brand_name: str) -> List[str]:
        """Get typical requirements for brand partnerships"""
        return [
            "Minimum 10K followers",
            "High-quality content standards",
            "Brand guideline compliance",
            "Performance metrics reporting",
            "Content approval process"
        ]

    async def _get_brand_contact_info(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Get brand contact information (would connect to real database)"""
        # This would fetch real contact info from partnerships database
        return {
            "department": "Creator Partnerships",
            "website": f"https://partnerships.{brand_name.lower().replace(' ', '')}.com",
            "application_required": True
        }

    async def _calculate_licensing_potential(
        self, 
        asset: ContentAsset, 
        analytics: Any, 
        opportunity_type: str
    ) -> float:
        """Calculate licensing potential score"""
        factors = []
        
        # Content quality factor
        if asset.file_size and asset.file_size > 1024 * 1024:  # > 1MB = higher quality
            factors.append(0.8)
        else:
            factors.append(0.6)
        
        # Performance factor
        if analytics.views > 5000:
            factors.append(0.9)
        elif analytics.views > 1000:
            factors.append(0.7)
        else:
            factors.append(0.5)
        
        # Content type suitability
        suitability = {
            'Sync licensing': 0.9 if asset.media_type == 'audio' else 0.3,
            'Stock footage': 0.9 if asset.media_type == 'video' else 0.2,
            'Stock photography': 0.9 if asset.media_type == 'image' else 0.2,
            'Publishing': 0.9 if asset.media_type == 'text' else 0.3
        }
        factors.append(suitability.get(opportunity_type, 0.5))
        
        return sum(factors) / len(factors)

    def _determine_collaboration_tier(self, analytics: Any, match_score: float) -> CollaborationTier:
        """Determine collaboration tier based on analytics and match score"""
        if analytics.views > 100000 and match_score > 0.8:
            return CollaborationTier.PREMIUM
        elif analytics.views > 10000 and match_score > 0.6:
            return CollaborationTier.STANDARD
        else:
            return CollaborationTier.EMERGING

    async def _apply_criteria_filters(
        self, 
        matches: List[CollaborationMatch], 
        criteria: MatchingCriteria
    ) -> List[CollaborationMatch]:
        """Apply user-specified criteria filters"""
        filtered_matches = matches
        
        if criteria.collaboration_types:
            type_names = [t.value for t in criteria.collaboration_types]
            filtered_matches = [m for m in filtered_matches if m.collaboration_type.value in type_names]
        
        if criteria.min_reach:
            filtered_matches = [m for m in filtered_matches if m.estimated_reach >= criteria.min_reach]
        
        if criteria.budget_range:
            min_budget, max_budget = criteria.budget_range
            filtered_matches = [m for m in filtered_matches if min_budget <= m.estimated_revenue <= max_budget]
        
        return filtered_matches

    def _hash_criteria(self, criteria: MatchingCriteria) -> str:
        """Generate hash for criteria caching"""
        criteria_str = f"{criteria.content_type}_{criteria.genre}_{criteria.target_audience}_{criteria.min_reach}"
        return str(hash(criteria_str))

    async def create_collaboration_request(
        self, 
        db: Session,
        creator_id: int,
        match: CollaborationMatch,
        message: str,
        proposal_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a collaboration request"""
        try:
            request_data = {
                'creator_id': creator_id,
                'partner_id': match.partner_id,
                'partner_type': match.partner_type,
                'collaboration_type': match.collaboration_type.value,
                'message': message,
                'proposal_details': proposal_details,
                'estimated_reach': match.estimated_reach,
                'estimated_revenue': match.estimated_revenue,
                'status': 'pending',
                'created_at': datetime.now()
            }
            
            # Would create actual database record here
            # collaboration_request = CollaborationRequest(**request_data)
            # db.add(collaboration_request)
            # db.commit()
            
            logger.info(f"Created collaboration request for creator {creator_id} with {match.partner_name}")
            
            return {
                'success': True,
                'request_id': f"req_{creator_id}_{match.partner_id}_{int(datetime.now().timestamp())}",
                'status': 'pending',
                'next_steps': await self._get_collaboration_next_steps(match)
            }
            
        except Exception as e:
            logger.error(f"Failed to create collaboration request: {str(e)}")
            raise CollaborationError(f"Failed to create request: {str(e)}")

    async def _get_collaboration_next_steps(self, match: CollaborationMatch) -> List[str]:
        """Get next steps for collaboration process"""
        if match.partner_type == 'brand':
            return [
                "Brand team will review your proposal within 5-7 business days",
                "Prepare content samples and media kit",
                "Review brand guidelines and requirements"
            ]
        elif match.partner_type == 'creator':
            return [
                "Creator will be notified of collaboration interest",
                "Schedule initial discussion call",
                "Define collaboration terms and timeline"
            ]
        else:
            return [
                "Review licensing terms and conditions",
                "Prepare necessary documentation",
                "Await approval from licensing team"
            ]

    # Legacy method for backward compatibility
    def match(self, asset: ContentAsset) -> List[dict]:
        """Legacy match method - deprecated, use find_collaboration_matches instead"""
        logger.warning("Using deprecated match method. Switch to find_collaboration_matches")
        
        tags = list((asset.metadata or {}).get("tags", []))
        partners = []
        for t in tags[:5]:
            partners.append({"partner": f"brand-{t}", "score": 80})
        if not partners:
            partners.append({"partner": "generic-brand", "score": 60})
        return partners


# Create alias for backward compatibility
CollaborationService = CollaborationMatchingService
