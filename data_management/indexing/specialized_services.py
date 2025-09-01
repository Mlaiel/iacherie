"""IA Influencer Agent - Specialized Creator Services
==================================================

Specialized indexing services for different creator types:
musicians, bloggers, photographers, influencers, comedians with
optimized workflows and content-specific features.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import json

from .services import IndexingService, SearchService, IndexingRequest, SearchRequest
from .processors import AudioIndexProcessor, VideoIndexProcessor, ImageIndexProcessor, TextIndexProcessor
from .engines import VectorSearchEngine, ContentIndexEngine
from .analytics import ContentAnalyticsEngine

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """
Types of content creators"""

    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    PODCASTER = "podcaster"
    VIDEO_CREATOR = "video_creator"
    ARTIST = "artist"


class ContentCategory(Enum):
    """Content categories by creator type"""
    # Music
    SONG = "song"
    ALBUM = "album"
    LIVE_PERFORMANCE = "live_performance"
    MUSIC_VIDEO = "music_video"
    
    # Blog/Text
    ARTICLE = "article"
    TUTORIAL = "tutorial"
    REVIEW = "review"
    NEWS = "news"
    
    # Visual
    PHOTO = "photo"
    PORTFOLIO = "portfolio"
    ARTWORK = "artwork"
    DESIGN = "design"
    
    # Video
    VLOG = "vlog"
    SHORT_VIDEO = "short_video"
    DOCUMENTARY = "documentary"
    INTERVIEW = "interview"
    
    # Comedy
    STANDUP = "standup"
    SKETCH = "sketch"
    MEME = "meme"
    PARODY = "parody"


@dataclass
class CreatorProfile:
    """Creator profile with specialized metadata"""
    creator_id: str
    creator_type: CreatorType
    stage_name: str
    real_name: Optional[str]
    genres: List[str]
    platforms: List[str]
    follower_counts: Dict[str, int]
    content_categories: List[ContentCategory]
    collaboration_preferences: Dict[str, Any]
    monetization_settings: Dict[str, Any]
    protection_level: str = "premium"
    verified: bool = False


@dataclass
class ContentMetadata:
    """Enhanced content metadata for creators"""
    title: str
    description: str
    category: ContentCategory
    genres: List[str]
    mood_tags: List[str]
    technical_specs: Dict[str, Any]
    collaboration_info: Optional[Dict[str, Any]] = None
    licensing_terms: Optional[Dict[str, Any]] = None
    monetization_enabled: bool = True
    distribution_platforms: List[str] = None
    seo_keywords: List[str] = None


class SpecializedIndexingService:
    """
Base class for specialized creator indexing services"""
    
    def __init__(self, indexing_service: IndexingService, search_service: SearchService):
        self.indexing_service = indexing_service
        self.search_service = search_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def create_creator_profile(self, profile: CreatorProfile) -> bool:
        """
Create or update creator profile"""
        try:
            profile_data = {
                "creator_id": profile.creator_id,
                "creator_type": profile.creator_type.value,
                "stage_name": profile.stage_name,
                "real_name": profile.real_name,
                "genres": profile.genres,
                "platforms": profile.platforms,
                "follower_counts": profile.follower_counts,
                "content_categories": [cat.value for cat in profile.content_categories],
                "collaboration_preferences": profile.collaboration_preferences,
                "monetization_settings": profile.monetization_settings,
                "protection_level": profile.protection_level,
                "verified": profile.verified,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store in specialized creator index
            await self.indexing_service.engines["content"].add_to_index(
                f"creator_profile_{profile.creator_id}",
                profile_data,
                {"type": "creator_profile", "creator_type": profile.creator_type.value}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create creator profile: {e}")
            return False
    
    async def index_specialized_content(
        self, 
        creator_id: str,
        content_metadata: ContentMetadata,
        file_path: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Index content with creator-specific optimizations"""
        try:
            # Enhanced metadata with creator context
            enhanced_metadata = {
                "creator_id": creator_id,
                "category": content_metadata.category.value,
                "genres": content_metadata.genres,
                "mood_tags": content_metadata.mood_tags,
                "technical_specs": content_metadata.technical_specs,
                "collaboration_info": content_metadata.collaboration_info,
                "licensing_terms": content_metadata.licensing_terms,
                "monetization_enabled": content_metadata.monetization_enabled,
                "distribution_platforms": content_metadata.distribution_platforms or [],
                "seo_keywords": content_metadata.seo_keywords or [],
                "indexed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Create indexing request
            request = IndexingRequest(
                creator_id=creator_id,
                file_path=file_path,
                content_type=content_type,
                title=content_metadata.title,
                description=content_metadata.description,
                metadata=enhanced_metadata,
                protection_level="premium",
                process_embeddings=True,
                generate_fingerprints=True
            )
            
            # Process with specialized optimizations
            result = await self.indexing_service.index_content(request)
            
            # Add creator-specific enhancements
            if result.success:
                await self._add_creator_enhancements(creator_id, result.content_id, content_metadata)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to index specialized content: {e}")
            raise
    
    async def _add_creator_enhancements(
        self, 
        creator_id: str, 
        content_id: str, 
        metadata: ContentMetadata
    ) -> None:
        """Add creator-specific enhancements to indexed content"""
        # Auto-generate SEO tags if not provided
        if not metadata.seo_keywords:
            seo_tags = await self._generate_seo_tags(metadata)
            metadata.seo_keywords = seo_tags
        
        # Update collaboration opportunities
        if metadata.collaboration_info:
            await self._index_collaboration_opportunity(creator_id, content_id, metadata)
        
        # Update monetization tracking
        if metadata.monetization_enabled:
            await self._setup_monetization_tracking(creator_id, content_id, metadata)
    
    async def _generate_seo_tags(self, metadata: ContentMetadata) -> List[str]:
        """
Generate SEO-optimized tags"""
        seo_tags = []
        
        # Add category-based tags
        seo_tags.append(metadata.category.value)
        
        # Add genre tags
        seo_tags.extend(metadata.genres)
        
        # Add mood tags
        seo_tags.extend(metadata.mood_tags)
        
        # Extract keywords from title and description
        text_content = f"{metadata.title} {metadata.description}".lower()
        
        # Simple keyword extraction (can be enhanced with NLP)
        keywords = [word for word in text_content.split() 
                   if len(word) > 3 and word.isalpha()]
        seo_tags.extend(keywords[:10])  # Top 10 keywords
        
        return list(set(seo_tags))  # Remove duplicates
    
    async def _index_collaboration_opportunity(
        self, 
        creator_id: str, 
        content_id: str, 
        metadata: ContentMetadata
    ) -> None:
        """Index content for collaboration matching"""
        collab_data = {
            "creator_id": creator_id,
            "content_id": content_id,
            "genres": metadata.genres,
            "mood_tags": metadata.mood_tags,
            "collaboration_type": metadata.collaboration_info.get("type"),
            "requirements": metadata.collaboration_info.get("requirements", []),
            "compensation": metadata.collaboration_info.get("compensation"),
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.indexing_service.engines["content"].add_to_index(
            f"collaboration_{content_id}",
            collab_data,
            {"type": "collaboration_opportunity"}
        )
    
    async def _setup_monetization_tracking(
        self, 
        creator_id: str, 
        content_id: str, 
        metadata: ContentMetadata
    ) -> None:
        """Setup monetization tracking for content"""
        monetization_data = {
            "creator_id": creator_id,
            "content_id": content_id,
            "platforms": metadata.distribution_platforms,
            "licensing_terms": metadata.licensing_terms,
            "revenue_tracking_enabled": True,
            "protection_level": "premium",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.indexing_service.engines["content"].add_to_index(
            f"monetization_{content_id}",
            monetization_data,
            {"type": "monetization_tracking"}
        )


class MusicianIndexingService(SpecializedIndexingService):
    """Specialized indexing service for musicians"""
    
    async def index_music_content(
        self,
        creator_id: str,
        audio_file: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Index music content with specialized features"""
        
        # Enhanced music metadata
        music_metadata = ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            category=ContentCategory.SONG,
            genres=metadata.get("genres", []),
            mood_tags=metadata.get("mood_tags", []),
            technical_specs={
                "bpm": metadata.get("bpm"),
                "key": metadata.get("key"),
                "duration": metadata.get("duration"),
                "sample_rate": metadata.get("sample_rate", 44100),
                "bitrate": metadata.get("bitrate")
            },
            collaboration_info=metadata.get("collaboration_info"),
            licensing_terms=metadata.get("licensing_terms"),
            distribution_platforms=metadata.get("platforms", ["spotify", "apple_music", "youtube_music"])
        )
        
        return await self.index_specialized_content(
            creator_id, music_metadata, audio_file, "audio"
        )
    
    async def find_collaboration_matches(
        self, 
        creator_id: str, 
        preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find collaboration matches for musicians"""
        
        search_request = SearchRequest(
            filters={
                "type": "collaboration_opportunity",
                "genres": preferences.get("genres", []),
                "collaboration_type": preferences.get("collaboration_type")
            },
            content_types=["audio"],
            similarity_threshold=0.7,
            limit=20
        )
        
        results = await self.search_service.search(search_request)
        
        # Filter out own content and apply additional matching logic
        matches = []
        for result in results.results:
            if result.get("creator_id") != creator_id:
                compatibility_score = self._calculate_collaboration_compatibility(
                    preferences, result
                )
                if compatibility_score > 0.6:
                    result["compatibility_score"] = compatibility_score
                    matches.append(result)
        
        return sorted(matches, key=lambda x: x["compatibility_score"], reverse=True)
    
    def _calculate_collaboration_compatibility(
        self, 
        preferences: Dict[str, Any], 
        opportunity: Dict[str, Any]
    ) -> float:
        """Calculate collaboration compatibility score"""
        score = 0.0
        
        # Genre compatibility
        pref_genres = set(preferences.get("genres", []))
        opp_genres = set(opportunity.get("genres", []))
        if pref_genres and opp_genres:
            genre_overlap = len(pref_genres.intersection(opp_genres))
            score += (genre_overlap / max(len(pref_genres), len(opp_genres))) * 0.4
        
        # Mood compatibility
        pref_moods = set(preferences.get("mood_tags", []))
        opp_moods = set(opportunity.get("mood_tags", []))
        if pref_moods and opp_moods:
            mood_overlap = len(pref_moods.intersection(opp_moods))
            score += (mood_overlap / max(len(pref_moods), len(opp_moods))) * 0.3
        
        # Collaboration type match
        if preferences.get("collaboration_type") == opportunity.get("collaboration_type"):
            score += 0.3
        
        return min(score, 1.0)


class BloggerIndexingService(SpecializedIndexingService):
    """Specialized indexing service for bloggers and content writers"""
    
    async def index_article(
        self,
        creator_id: str,
        content_text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Index blog article with SEO optimization"""
        
        # Enhanced article metadata
        article_metadata = ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            category=ContentCategory.ARTICLE,
            genres=metadata.get("topics", []),
            mood_tags=metadata.get("tone_tags", []),
            technical_specs={
                "word_count": len(content_text.split()),
                "reading_time": self._calculate_reading_time(content_text),
                "language": metadata.get("language", "en"),
                "readability_score": self._calculate_readability(content_text)
            },
            seo_keywords=metadata.get("seo_keywords", []),
            distribution_platforms=metadata.get("platforms", ["medium", "substack", "wordpress"])
        )
        
        # Save content text temporarily for processing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content_text)
            temp_file = f.name
        
        try:
            result = await self.index_specialized_content(
                creator_id, article_metadata, temp_file, "text"
            )
            return result
        finally:
            import os
            os.unlink(temp_file)
    
    def _calculate_reading_time(self, text: str) -> int:
        """Calculate estimated reading time in minutes"""
        words = len(text.split())
        return max(1, words // 200)  # Assuming 200 words per minute
    
    def _calculate_readability(self, text: str) -> float:
        """
Calculate readability score (simplified)"""
        sentences = text.count('.') + text.count('!') + text.count('?')
        words = len(text.split())
        if sentences == 0:
            return 0.0
        return min(100.0, max(0.0, 206.835 - 1.015 * (words / sentences)))


class PhotographerIndexingService(SpecializedIndexingService):
    """
Specialized indexing service for photographers and visual artists"""
    
    async def index_photo(
        self,
        creator_id: str,
        image_file: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Index photograph with visual analysis"""
        
        # Enhanced photo metadata
        photo_metadata = ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            category=ContentCategory.PHOTO,
            genres=metadata.get("styles", []),
            mood_tags=metadata.get("mood_tags", []),
            technical_specs={
                "camera_model": metadata.get("camera_model"),
                "lens": metadata.get("lens"),
                "focal_length": metadata.get("focal_length"),
                "aperture": metadata.get("aperture"),
                "iso": metadata.get("iso"),
                "shutter_speed": metadata.get("shutter_speed"),
                "resolution": metadata.get("resolution"),
                "color_space": metadata.get("color_space", "sRGB")
            },
            licensing_terms=metadata.get("licensing_terms"),
            distribution_platforms=metadata.get("platforms", ["instagram", "pinterest", "behance"])
        )
        
        return await self.index_specialized_content(
            creator_id, photo_metadata, image_file, "image"
        )


class InfluencerIndexingService(SpecializedIndexingService):
    """Specialized indexing service for influencers and social media creators"""
    
    async def index_social_content(
        self,
        creator_id: str,
        content_file: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Index social media content with engagement optimization"""
        
        # Enhanced social metadata
        social_metadata = ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            category=ContentCategory.SHORT_VIDEO if content_type == "video" else ContentCategory.PHOTO,
            genres=metadata.get("niches", []),
            mood_tags=metadata.get("hashtags", []),
            technical_specs={
                "platform_optimized": metadata.get("platform", "instagram"),
                "aspect_ratio": metadata.get("aspect_ratio", "9:16"),
                "duration": metadata.get("duration"),
                "engagement_rate": metadata.get("historical_engagement", 0.0)
            },
            distribution_platforms=metadata.get("platforms", ["instagram", "tiktok", "youtube"])
        )
        
        return await self.index_specialized_content(
            creator_id, social_metadata, content_file, content_type
        )


class ComedianIndexingService(SpecializedIndexingService):
    """Specialized indexing service for comedians and entertainment creators"""
    
    async def index_comedy_content(
        self,
        creator_id: str,
        content_file: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Index comedy content with humor analysis"""
        
        # Enhanced comedy metadata
        comedy_metadata = ContentMetadata(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            category=ContentCategory.STANDUP if content_type == "audio" else ContentCategory.SKETCH,
            genres=metadata.get("comedy_styles", []),
            mood_tags=metadata.get("humor_tags", []),
            technical_specs={
                "content_rating": metadata.get("content_rating", "PG-13"),
                "language": metadata.get("language", "en"),
                "duration": metadata.get("duration"),
                "audience_type": metadata.get("audience_type", "general")
            },
            distribution_platforms=metadata.get("platforms", ["youtube", "instagram", "tiktok"])
        )
        
        return await self.index_specialized_content(
            creator_id, comedy_metadata, content_file, content_type
        )


class CreatorServiceFactory:
    """Factory for creating specialized creator services"""
    
    @staticmethod
    def create_service(
        creator_type: CreatorType,
        indexing_service: IndexingService,
        search_service: SearchService
    ) -> SpecializedIndexingService:
        """
Create appropriate specialized service for creator type"""
        
        services = {
            CreatorType.MUSICIAN: MusicianIndexingService,
            CreatorType.BLOGGER: BloggerIndexingService,
            CreatorType.PHOTOGRAPHER: PhotographerIndexingService,
            CreatorType.INFLUENCER: InfluencerIndexingService,
            CreatorType.COMEDIAN: ComedianIndexingService,
            CreatorType.PODCASTER: MusicianIndexingService,  # Similar to musician
            CreatorType.VIDEO_CREATOR: InfluencerIndexingService,  # Similar to influencer
            CreatorType.ARTIST: PhotographerIndexingService  # Similar to photographer
        }
        
        service_class = services.get(creator_type, SpecializedIndexingService)
        return service_class(indexing_service, search_service)
