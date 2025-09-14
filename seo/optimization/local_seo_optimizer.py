"""
Local SEO Optimizer for Ainflue Platform
========================================

Advanced local SEO optimization for creator businesses and location-based content.
Handles Google My Business optimization, local citations, and geo-targeting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime, timedelta
import re
import aiohttp
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

class BusinessType(Enum):
    """Types of creator businesses for local SEO."""
    MUSIC_VENUE = "music_venue"
    PHOTOGRAPHY_STUDIO = "photography_studio"
    CONTENT_CREATOR = "content_creator"
    PERFORMANCE_ARTIST = "performance_artist"
    DIGITAL_AGENCY = "digital_agency"
    PRODUCTION_COMPANY = "production_company"
    ENTERTAINMENT_BUSINESS = "entertainment_business"
    CREATIVE_SERVICES = "creative_services"

class CitationType(Enum):
    """Types of local citations."""
    GOOGLE_MY_BUSINESS = "google_my_business"
    YELP = "yelp"
    FACEBOOK = "facebook"
    APPLE_MAPS = "apple_maps"
    BING_PLACES = "bing_places"
    INDUSTRY_DIRECTORY = "industry_directory"
    LOCAL_DIRECTORY = "local_directory"
    SOCIAL_MEDIA = "social_media"

@dataclass
class LocalBusinessProfile:
    """Local business profile for SEO optimization."""
    business_id: str
    name: str
    business_type: BusinessType
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    phone: str
    website: str
    latitude: float
    longitude: float
    description: str
    categories: List[str]
    hours: Dict[str, str]
    created_at: datetime
    updated_at: datetime

@dataclass
class LocalCitation:
    """Local business citation information."""
    citation_id: str
    business_id: str
    platform: CitationType
    url: str
    name: str
    address: str
    phone: str
    website: str
    categories: List[str]
    rating: Optional[float]
    review_count: Optional[int]
    is_verified: bool
    last_updated: datetime
    created_at: datetime

@dataclass
class LocalSEOAnalysis:
    """Local SEO analysis result."""
    business_id: str
    citation_count: int
    consistency_score: float
    visibility_score: float
    review_score: float
    keyword_rankings: Dict[str, Dict[str, int]]
    competitor_analysis: Dict[str, Any]
    recommendations: List[str]
    local_search_volume: Dict[str, int]
    created_at: datetime

@dataclass
class LocalKeywordData:
    """Local keyword research data."""
    keyword: str
    location: str
    search_volume: int
    competition: str
    difficulty: int
    local_intent: bool
    suggested_bid: float
    trends: List[int]

class LocalSEOOptimizer:
    """
    Advanced Local SEO Optimizer
    
    Features:
    - Google My Business optimization
    - Local citation management
    - Geo-targeted keyword research
    - Local competitor analysis
    - Review management integration
    - Local schema markup
    - Location-based content optimization
    """
    
    def __init__(self, db_pool -> None: asyncpg.Pool, api_keys -> None: Dict[str, str]) -> None:
        self.db_pool = db_pool
        self.api_keys = api_keys
        self.geocoder = Nominatim(user_agent="ainflue_local_seo")
        self.session = None
        
    async def __aenter__(self) -> None:
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()
    
    async def create_business_profile(
        self,
        business_data: Dict[str, Any]
    ) -> LocalBusinessProfile:
        """
        Create and store a local business profile.
        
        Args:
            business_data: Business information dictionary
            
        Returns:
            LocalBusinessProfile object
        """
        try:
            # Geocode the address
            location = self.geocoder.geocode(
                f"{business_data['address']}, {business_data['city']}, {business_data['state']}"
            )
            
            latitude = location.latitude if location else 0.0
            longitude = location.longitude if location else 0.0
            
            profile = LocalBusinessProfile(
                business_id=business_data['business_id'],
                name=business_data['name'],
                business_type=BusinessType(business_data['business_type']),
                address=business_data['address'],
                city=business_data['city'],
                state=business_data['state'],
                zip_code=business_data['zip_code'],
                country=business_data['country'],
                phone=business_data['phone'],
                website=business_data['website'],
                latitude=latitude,
                longitude=longitude,
                description=business_data.get('description', ''),
                categories=business_data.get('categories', []),
                hours=business_data.get('hours', {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database
            await self._store_business_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating business profile: {e}")
            raise
    
    async def analyze_local_seo(
        self,
        business_id: str,
        target_keywords: List[str],
        radius_miles: int = 25
    ) -> LocalSEOAnalysis:
        """
        Perform comprehensive local SEO analysis.
        
        Args:
            business_id: Business identifier
            target_keywords: Keywords to analyze for local SEO
            radius_miles: Analysis radius in miles
            
        Returns:
            LocalSEOAnalysis object
        """
        try:
            # Get business profile
            profile = await self._get_business_profile(business_id)
            if not profile:
                raise ValueError(f"Business profile not found: {business_id}")
            
            # Get all citations for this business
            citations = await self._get_business_citations(business_id)
            
            # Calculate consistency score
            consistency_score = self._calculate_citation_consistency(citations, profile)
            
            # Calculate visibility score
            visibility_score = await self._calculate_visibility_score(business_id, citations)
            
            # Calculate review score
            review_score = await self._calculate_review_score(business_id)
            
            # Analyze keyword rankings
            keyword_rankings = await self._analyze_local_keyword_rankings(
                business_id, target_keywords, profile
            )
            
            # Competitor analysis
            competitor_analysis = await self._analyze_local_competitors(
                profile, target_keywords, radius_miles
            )
            
            # Generate recommendations
            recommendations = self._generate_local_seo_recommendations(
                consistency_score, visibility_score, review_score, citations
            )
            
            # Get local search volume
            local_search_volume = await self._get_local_search_volume(
                target_keywords, f"{profile.city}, {profile.state}"
            )
            
            analysis = LocalSEOAnalysis(
                business_id=business_id,
                citation_count=len(citations),
                consistency_score=consistency_score,
                visibility_score=visibility_score,
                review_score=review_score,
                keyword_rankings=keyword_rankings,
                competitor_analysis=competitor_analysis,
                recommendations=recommendations,
                local_search_volume=local_search_volume,
                created_at=datetime.utcnow()
            )
            
            # Store analysis
            await self._store_local_seo_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing local SEO: {e}")
            raise
    
    async def optimize_google_my_business(
        self,
        business_id: str,
        optimization_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize Google My Business listing.
        
        Args:
            business_id: Business identifier
            optimization_options: Optimization preferences
            
        Returns:
            Optimization results and recommendations
        """
        try:
            profile = await self._get_business_profile(business_id)
            if not profile:
                raise ValueError(f"Business profile not found: {business_id}")
            
            optimizations = {
                'title_optimization': self._optimize_gmb_title(profile),
                'description_optimization': self._optimize_gmb_description(profile),
                'category_optimization': await self._optimize_gmb_categories(profile),
                'hours_optimization': self._optimize_gmb_hours(profile),
                'photos_optimization': await self._optimize_gmb_photos(business_id),
                'posts_optimization': await self._generate_gmb_posts(profile),
                'q_and_a_optimization': await self._optimize_gmb_qa(profile)
            }
            
            # Calculate optimization score
            optimization_score = self._calculate_gmb_optimization_score(optimizations)
            
            result = {
                'business_id': business_id,
                'optimization_score': optimization_score,
                'optimizations': optimizations,
                'next_steps': self._generate_gmb_next_steps(optimizations),
                'estimated_impact': self._estimate_gmb_impact(optimization_score)
            }
            
            # Store optimization results
            await self._store_gmb_optimization(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing Google My Business: {e}")
            raise
    
    async def manage_local_citations(
        self,
        business_id: str,
        target_platforms: List[CitationType],
        auto_submit: bool = False
    ) -> Dict[str, Any]:
        """
        Manage local business citations across platforms.
        
        Args:
            business_id: Business identifier
            target_platforms: Platforms to manage citations on
            auto_submit: Whether to automatically submit citations
            
        Returns:
            Citation management results
        """
        try:
            profile = await self._get_business_profile(business_id)
            existing_citations = await self._get_business_citations(business_id)
            
            # Identify missing citations
            existing_platforms = {c.platform for c in existing_citations}
            missing_platforms = set(target_platforms) - existing_platforms
            
            # Identify inconsistent citations
            inconsistent_citations = self._find_inconsistent_citations(
                existing_citations, profile
            )
            
            # Generate citation opportunities
            citation_opportunities = await self._find_citation_opportunities(
                profile, missing_platforms
            )
            
            results = {
                'business_id': business_id,
                'existing_citations': len(existing_citations),
                'missing_platforms': list(missing_platforms),
                'inconsistent_citations': inconsistent_citations,
                'citation_opportunities': citation_opportunities,
                'priority_citations': self._prioritize_citations(citation_opportunities),
                'estimated_value': self._estimate_citation_value(citation_opportunities)
            }
            
            # Auto-submit if requested
            if auto_submit and citation_opportunities:
                submission_results = await self._auto_submit_citations(
                    profile, citation_opportunities[:5]  # Submit top 5
                )
                results['auto_submission'] = submission_results
            
            return results
            
        except Exception as e:
            logger.error(f"Error managing local citations: {e}")
            raise
    
    async def research_local_keywords(
        self,
        business_location: str,
        business_type: BusinessType,
        seed_keywords: List[str],
        radius_miles: int = 25
    ) -> List[LocalKeywordData]:
        """
        Research local keywords for business optimization.
        
        Args:
            business_location: Business location (city, state)
            business_type: Type of business
            seed_keywords: Initial keywords to expand
            radius_miles: Research radius in miles
            
        Returns:
            List of LocalKeywordData objects
        """
        try:
            # Expand seed keywords with local modifiers
            local_keywords = self._expand_keywords_with_local_modifiers(
                seed_keywords, business_location
            )
            
            # Add business type specific keywords
            local_keywords.extend(self._get_business_type_keywords(
                business_type, business_location
            ))
            
            # Research keyword data
            keyword_data = []
            for keyword in local_keywords:
                data = await self._research_keyword_data(keyword, business_location)
                if data:
                    keyword_data.append(data)
            
            # Sort by local intent and search volume
            keyword_data.sort(
                key=lambda x: (x.local_intent, x.search_volume), 
                reverse=True
            )
            
            return keyword_data
            
        except Exception as e:
            logger.error(f"Error researching local keywords: {e}")
            return []
    
    async def track_local_rankings(
        self,
        business_id: str,
        keywords: List[str],
        locations: List[str]
    ) -> Dict[str, Any]:
        """
        Track local search rankings for keywords and locations.
        
        Args:
            business_id: Business identifier
            keywords: Keywords to track
            locations: Locations to track rankings in
            
        Returns:
            Ranking tracking results
        """
        try:
            profile = await self._get_business_profile(business_id)
            
            tracking_results = {}
            
            for location in locations:
                location_results = {}
                
                for keyword in keywords:
                    # Simulate local search and find business ranking
                    ranking_data = await self._get_local_ranking(
                        keyword, location, profile.name, profile.website
                    )
                    location_results[keyword] = ranking_data
                
                tracking_results[location] = location_results
            
            # Store tracking results
            await self._store_ranking_data(business_id, tracking_results)
            
            # Generate ranking insights
            insights = self._analyze_ranking_trends(tracking_results)
            
            return {
                'business_id': business_id,
                'tracking_date': datetime.utcnow().isoformat(),
                'rankings': tracking_results,
                'insights': insights,
                'average_position': self._calculate_average_position(tracking_results),
                'visibility_score': self._calculate_local_visibility(tracking_results)
            }
            
        except Exception as e:
            logger.error(f"Error tracking local rankings: {e}")
            return {}
    
    def _calculate_citation_consistency(
        self,
        citations: List[LocalCitation],
        profile: LocalBusinessProfile
    ) -> float:
        """Calculate citation consistency score."""
        if not citations:
            return 0.0
        
        total_score = 0.0
        
        for citation in citations:
            score = 0.0
            
            # Name consistency (25 points)
            if citation.name.lower() == profile.name.lower():
                score += 25
            elif profile.name.lower() in citation.name.lower():
                score += 15
            
            # Address consistency (25 points)
            if self._addresses_match(citation.address, profile.address):
                score += 25
            elif profile.city.lower() in citation.address.lower():
                score += 15
            
            # Phone consistency (25 points)
            if self._phones_match(citation.phone, profile.phone):
                score += 25
            
            # Website consistency (25 points)
            if citation.website and citation.website == profile.website:
                score += 25
            
            total_score += score
        
        return total_score / len(citations)
    
    async def _calculate_visibility_score(
        self,
        business_id: str,
        citations: List[LocalCitation]
    ) -> float:
        """Calculate local visibility score."""
        # Base score from number of citations
        citation_score = min(len(citations) * 10, 50)
        
        # Platform diversity score
        platforms = {c.platform for c in citations}
        diversity_score = len(platforms) * 5
        
        # High-authority platform bonus
        high_authority_platforms = {
            CitationType.GOOGLE_MY_BUSINESS,
            CitationType.YELP,
            CitationType.FACEBOOK
        }
        authority_score = len(platforms & high_authority_platforms) * 10
        
        # Verification bonus
        verified_count = sum(1 for c in citations if c.is_verified)
        verification_score = verified_count * 5
        
        return min(citation_score + diversity_score + authority_score + verification_score, 100)
    
    async def _calculate_review_score(self, business_id: str) -> float:
        """Calculate review-based score."""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        AVG(rating) as avg_rating,
                        COUNT(*) as review_count,
                        COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as recent_reviews
                    FROM local_business_reviews 
                    WHERE business_id = $1
                """, business_id)
                
                if not result or not result['avg_rating']:
                    return 0.0
                
                # Rating score (60% of total)
                rating_score = (result['avg_rating'] / 5.0) * 60
                
                # Volume score (25% of total)
                volume_score = min(result['review_count'] / 50 * 25, 25)
                
                # Recency score (15% of total)
                recency_score = min(result['recent_reviews'] / 5 * 15, 15)
                
                return rating_score + volume_score + recency_score
                
        except Exception as e:
            logger.error(f"Error calculating review score: {e}")
            return 0.0
    
    def _optimize_gmb_title(self, profile: LocalBusinessProfile) -> Dict[str, Any]:
        """Optimize Google My Business title."""
        current_title = profile.name
        
        # Add location if not present
        optimized_title = current_title
        if profile.city.lower() not in current_title.lower():
            optimized_title = f"{current_title} - {profile.city}"
        
        # Add business type if space allows
        business_type_keywords = {
            BusinessType.MUSIC_VENUE: "Music Venue",
            BusinessType.PHOTOGRAPHY_STUDIO: "Photography Studio",
            BusinessType.CONTENT_CREATOR: "Content Creator",
            BusinessType.PERFORMANCE_ARTIST: "Performance Artist",
            BusinessType.DIGITAL_AGENCY: "Digital Agency",
            BusinessType.PRODUCTION_COMPANY: "Production Company"
        }
        
        type_keyword = business_type_keywords.get(profile.business_type, "")
        if type_keyword and len(optimized_title + f" | {type_keyword}") <= 50:
            optimized_title = f"{optimized_title} | {type_keyword}"
        
        return {
            'current': current_title,
            'optimized': optimized_title,
            'improvement': optimized_title != current_title,
            'character_count': len(optimized_title),
            'recommendations': [
                "Include location in business name for local SEO",
                "Add business type if character limit allows",
                "Keep under 50 characters for full display"
            ]
        }
    
    def _optimize_gmb_description(self, profile: LocalBusinessProfile) -> Dict[str, Any]:
        """Optimize Google My Business description."""
        current_description = profile.description
        
        # Generate optimized description
        location_keywords = [profile.city, profile.state]
        business_keywords = self._get_business_type_keywords(profile.business_type, "")
        
        optimized_description = self._generate_optimized_description(
            profile, location_keywords, business_keywords[:3]
        )
        
        return {
            'current': current_description,
            'optimized': optimized_description,
            'improvement': len(optimized_description) > len(current_description),
            'character_count': len(optimized_description),
            'keyword_density': self._calculate_keyword_density(
                optimized_description, location_keywords + business_keywords
            ),
            'recommendations': [
                "Include location keywords naturally",
                "Mention services and specialties",
                "Include call-to-action",
                "Stay under 750 characters"
            ]
        }
    
    async def _store_business_profile(self, profile -> None: LocalBusinessProfile) -> None:
        """Store business profile in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO local_business_profiles 
                    (business_id, name, business_type, address, city, state, zip_code,
                     country, phone, website, latitude, longitude, description,
                     categories, hours, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                    ON CONFLICT (business_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    business_type = EXCLUDED.business_type,
                    address = EXCLUDED.address,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    zip_code = EXCLUDED.zip_code,
                    country = EXCLUDED.country,
                    phone = EXCLUDED.phone,
                    website = EXCLUDED.website,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    description = EXCLUDED.description,
                    categories = EXCLUDED.categories,
                    hours = EXCLUDED.hours,
                    updated_at = EXCLUDED.updated_at
                """, 
                    profile.business_id, profile.name, profile.business_type.value,
                    profile.address, profile.city, profile.state, profile.zip_code,
                    profile.country, profile.phone, profile.website,
                    profile.latitude, profile.longitude, profile.description,
                    json.dumps(profile.categories), json.dumps(profile.hours),
                    profile.created_at, profile.updated_at
                )
        except Exception as e:
            logger.error(f"Error storing business profile: {e}")
    
    async def _get_business_profile(self, business_id: str) -> Optional[LocalBusinessProfile]:
        """Get business profile from database."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM local_business_profiles WHERE business_id = $1
                """, business_id)
                
                if row:
                    return LocalBusinessProfile(
                        business_id=row['business_id'],
                        name=row['name'],
                        business_type=BusinessType(row['business_type']),
                        address=row['address'],
                        city=row['city'],
                        state=row['state'],
                        zip_code=row['zip_code'],
                        country=row['country'],
                        phone=row['phone'],
                        website=row['website'],
                        latitude=row['latitude'],
                        longitude=row['longitude'],
                        description=row['description'],
                        categories=json.loads(row['categories']),
                        hours=json.loads(row['hours']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting business profile: {e}")
            return None
    
    def _addresses_match(self, addr1: str, addr2: str) -> bool:
        """Check if two addresses are similar."""
        # Normalize addresses for comparison
        norm1 = re.sub(r'[^\w\s]', '', addr1.lower())
        norm2 = re.sub(r'[^\w\s]', '', addr2.lower())
        
        # Simple similarity check
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union > 0.7 if union > 0 else False
    
    def _phones_match(self, phone1: str, phone2: str) -> bool:
        """Check if two phone numbers match."""
        # Extract digits only
        digits1 = re.sub(r'\D', '', phone1)
        digits2 = re.sub(r'\D', '', phone2)
        
        # Compare last 10 digits (US format)
        return digits1[-10:] == digits2[-10:] if len(digits1) >= 10 and len(digits2) >= 10 else False
    
    def _expand_keywords_with_local_modifiers(
        self,
        keywords: List[str],
        location: str
    ) -> List[str]:
        """Expand keywords with local modifiers."""
        modifiers = [
            "near me",
            f"in {location}",
            f"{location}",
            "local",
            "nearby",
            "best",
            "top rated"
        ]
        
        expanded = []
        for keyword in keywords:
            expanded.append(keyword)  # Original keyword
            for modifier in modifiers:
                if modifier == "near me":
                    expanded.append(f"{keyword} {modifier}")
                elif modifier in ["local", "nearby", "best", "top rated"]:
                    expanded.append(f"{modifier} {keyword}")
                    expanded.append(f"{modifier} {keyword} {location}")
                else:
                    expanded.append(f"{keyword} {modifier}")
        
        return list(set(expanded))  # Remove duplicates
    
    def _get_business_type_keywords(
        self,
        business_type: BusinessType,
        location: str
    ) -> List[str]:
        """Get keywords specific to business type."""
        keywords_map = {
            BusinessType.MUSIC_VENUE: [
                "music venue", "concert hall", "live music", "events venue",
                "entertainment venue", "music events", "live shows"
            ],
            BusinessType.PHOTOGRAPHY_STUDIO: [
                "photography studio", "photographer", "photo studio", "portrait studio",
                "wedding photographer", "commercial photography", "photo sessions"
            ],
            BusinessType.CONTENT_CREATOR: [
                "content creator", "social media creator", "video creator",
                "digital content", "content production", "creative services"
            ],
            BusinessType.PERFORMANCE_ARTIST: [
                "performance artist", "live performer", "entertainment",
                "artistic performances", "creative performances"
            ],
            BusinessType.DIGITAL_AGENCY: [
                "digital agency", "marketing agency", "creative agency",
                "digital marketing", "social media marketing", "content marketing"
            ],
            BusinessType.PRODUCTION_COMPANY: [
                "production company", "video production", "media production",
                "content production", "creative production", "multimedia production"
            ]
        }
        
        base_keywords = keywords_map.get(business_type, [])
        
        if location:
            return [f"{keyword} {location}" for keyword in base_keywords] + base_keywords
        
        return base_keywords
    
    async def _research_keyword_data(
        self,
        keyword: str,
        location: str
    ) -> Optional[LocalKeywordData]:
        """Research data for a specific local keyword."""
        try:
            # This would integrate with real keyword research APIs
            # For now, simulate keyword data
            
            # Determine if keyword has local intent
            local_indicators = [
                "near me", "in ", "local", "nearby", "best", "top rated",
                location.lower()
            ]
            local_intent = any(indicator in keyword.lower() for indicator in local_indicators)
            
            # Simulate search volume (would come from real API)
            base_volume = hash(keyword) % 1000 + 100
            local_modifier = 0.3 if local_intent else 1.0
            search_volume = int(base_volume * local_modifier)
            
            return LocalKeywordData(
                keyword=keyword,
                location=location,
                search_volume=search_volume,
                competition="medium",
                difficulty=hash(keyword) % 100,
                local_intent=local_intent,
                suggested_bid=1.50 + (hash(keyword) % 500) / 100,
                trends=[90, 95, 88, 92, 100, 85, 90]  # Simulated trend data
            )
            
        except Exception as e:
            logger.error(f"Error researching keyword data for {keyword}: {e}")
            return None
    
    def _generate_local_seo_recommendations(
        self,
        consistency_score: float,
        visibility_score: float,
        review_score: float,
        citations: List[LocalCitation]
    ) -> List[str]:
        """Generate local SEO recommendations."""
        recommendations = []
        
        # Citation consistency recommendations
        if consistency_score < 80:
            recommendations.append("Improve citation consistency across all platforms")
            recommendations.append("Standardize business name, address, and phone number (NAP)")
        
        # Visibility recommendations
        if visibility_score < 60:
            recommendations.append("Create more local business citations")
            recommendations.append("Focus on high-authority directories like Google My Business")
        
        # Review recommendations
        if review_score < 70:
            recommendations.append("Implement review generation strategy")
            recommendations.append("Respond to all customer reviews promptly")
        
        # Platform-specific recommendations
        citation_platforms = {c.platform for c in citations}
        missing_major_platforms = {
            CitationType.GOOGLE_MY_BUSINESS,
            CitationType.YELP,
            CitationType.FACEBOOK
        } - citation_platforms
        
        for platform in missing_major_platforms:
            recommendations.append(f"Create and optimize {platform.value} listing")
        
        # Additional recommendations
        recommendations.extend([
            "Optimize website for local keywords",
            "Create location-specific landing pages",
            "Build local backlinks from community organizations",
            "Participate in local events and sponsorships",
            "Use schema markup for local business information"
        ])
        
        return recommendations
    
    async def get_local_seo_dashboard(self, business_id: str) -> Dict[str, Any]:
        """Get comprehensive local SEO dashboard data."""
        try:
            # Get latest analysis
            analysis = await self._get_latest_analysis(business_id)
            
            # Get ranking trends
            ranking_trends = await self._get_ranking_trends(business_id, days=30)
            
            # Get review metrics
            review_metrics = await self._get_review_metrics(business_id)
            
            # Get citation status
            citation_status = await self._get_citation_status(business_id)
            
            return {
                'business_id': business_id,
                'overall_score': (analysis.consistency_score + analysis.visibility_score + analysis.review_score) / 3 if analysis else 0,
                'analysis': asdict(analysis) if analysis else None,
                'ranking_trends': ranking_trends,
                'review_metrics': review_metrics,
                'citation_status': citation_status,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting local SEO dashboard: {e}")
            return {}

# Export classes
__all__ = [
    'LocalSEOOptimizer',
    'LocalBusinessProfile',
    'LocalCitation',
    'LocalSEOAnalysis',
    'LocalKeywordData',
    'BusinessType',
    'CitationType'
]