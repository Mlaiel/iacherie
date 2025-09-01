"""Medium Platform Crawler - Ultra-Advanced Implementation
Professional Publishing Platform Content Monitoring System

This module provides comprehensive crawling capabilities for Medium platform,
focusing on article content, author analytics, and publication monitoring.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher
import re
from bs4 import BeautifulSoup

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter

logger = logging.getLogger(__name__)


class MediumMembershipType(str, Enum):
    """
Medium membership types"""

    FREE = "free"
    MEMBER = "member"
    FRIEND_OF_MEDIUM = "friend"
    WRITER = "writer"


class MediumContentType(str, Enum):
    """Medium content types"""

    STORY = "story"
    SERIES = "series"
    PUBLICATION = "publication"
    LIST = "list"
    NEWSLETTER = "newsletter"


class MediumReadingTime(BaseModel):
    """Medium reading time data model"""
    text: str
    minutes: int
    words: int


class MediumVirtue(BaseModel):
    """
Medium virtue/category data model"""
    slug: str
    name: str


class MediumTag(BaseModel):
    """
Medium tag data model"""
    slug: str
    name: str
    post_count: Optional[int] = None
    follower_count: Optional[int] = None


class MediumUser(BaseModel):
    """
Medium user data model"""
    user_id: str
    username: str
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    medium_member_at: Optional[datetime] = None
    is_writer_program_enrolled: bool = False
    is_suspended: bool = False
    has_list: bool = False
    is_newsletter_viable: bool = False
    membership_type: MediumMembershipType = MediumMembershipType.FREE
    follower_count: int = 0
    following_count: int = 0
    twitter_screen_name: Optional[str] = None
    facebook_account_url: Optional[str] = None
    allow_notes: bool = True
    medium_url: Optional[str] = None
    custom_domain_state: Dict[str, Any] = Field(default_factory=dict)
    has_subdomain: bool = False
    created_at: datetime
    last_posted_at: Optional[datetime] = None
    total_stories: int = 0
    total_responses: int = 0


class MediumPublication(BaseModel):
    """
Medium publication data model"""
    publication_id: str
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    favicon_url: Optional[str] = None
    domain: Optional[str] = None
    follower_count: int = 0
    story_count: int = 0
    creator: Optional[MediumUser] = None
    editors: List[MediumUser] = Field(default_factory=list)
    writers: List[MediumUser] = Field(default_factory=list)
    navigation_items: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[MediumTag] = Field(default_factory=list)
    created_at: datetime
    is_accepting_submissions: bool = True
    submission_guidelines: Optional[str] = None


class MediumStory(BaseModel):
    """
Medium story data model"""
    story_id: str
    title: str
    subtitle: Optional[str] = None
    content: str
    content_preview: str
    author: MediumUser
    publication: Optional[MediumPublication] = None
    published_at: datetime
    updated_at: Optional[datetime] = None
    last_modified_at: datetime
    first_published_at: datetime
    latest_version: str
    slug: str
    unique_slug: str
    medium_url: str
    canonical_url: Optional[str] = None
    short_url: Optional[str] = None
    reading_time: MediumReadingTime
    clap_count: int = 0
    voter_count: int = 0
    response_count: int = 0
    reading_list_count: int = 0
    word_count: int = 0
    tags: List[MediumTag] = Field(default_factory=list)
    virtues: List[MediumVirtue] = Field(default_factory=list)
    is_locked: bool = False
    is_member_only: bool = False
    is_series: bool = False
    is_shortform: bool = False
    language: str = "en"
    license: str = "all-rights-reserved"
    license_url: Optional[str] = None
    visibility: str = "public"
    monetization_state: str = "not_eligible"
    is_eligible_for_revenue: bool = False
    is_bookmarked: bool = False
    is_featured: bool = False
    collection_ids: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class MediumResponse(BaseModel):
    """Medium response/comment data model"""
    response_id: str
    author: MediumUser
    story: MediumStory
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    clap_count: int = 0
    response_count: int = 0
    is_public: bool = True
    highlighted_quote: Optional[str] = None
    paragraph_index: Optional[int] = None


class MediumList(BaseModel):
    """
Medium list data model"""
    list_id: str
    name: str
    description: Optional[str] = None
    author: MediumUser
    story_count: int = 0
    follower_count: int = 0
    created_at: datetime
    updated_at: datetime
    thumbnail_url: Optional[str] = None
    is_public: bool = True
    stories: List[MediumStory] = Field(default_factory=list)


class MediumSearchResults(BaseModel):
    """
Medium search results data model"""
    query: str
    total_results: int
    stories: List[MediumStory] = Field(default_factory=list)
    users: List[MediumUser] = Field(default_factory=list)
    publications: List[MediumPublication] = Field(default_factory=list)
    tags: List[MediumTag] = Field(default_factory=list)
    lists: List[MediumList] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class MediumAnalytics(BaseModel):
    """
Medium analytics data model"""
    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_stories_published: int
    total_responses_written: int
    total_claps_received: int
    total_followers_gained: int
    average_reading_time: float
    most_popular_story: Optional[str] = None
    most_clapped_story: Optional[str] = None
    top_performing_tags: List[str]
    publication_distribution: Dict[str, int]
    reading_ratio: float
    engagement_rate: float
    member_content_ratio: float
    series_completion_rate: float
    cross_publication_reach: int
    estimated_earnings: float
    content_quality_score: float
    similarity_violations: int
    protection_violations: int


class MediumCrawler(BaseCrawler):
    """
    Ultra-Advanced Medium Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Medium platform,
    specializing in article content, author analytics, and publication monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://medium.com"
        self.api_base = "https://medium.com/api"
        self.gql_endpoint = "https://medium.com/_/graphql"
        
        # Authentication
        self.session_id: Optional[str] = None
        self.uid: Optional[str] = None
        self.sid: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # Rate limiting - Medium has moderate limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_limit=20
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=600,  # 10 minutes for articles
            max_cache_size=3000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_authors: Set[str] = set()
        self.monitored_publications: Set[str] = set()
        self.monitored_tags: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # Medium-specific settings
        self.enable_member_content = config.get('enable_member_content', True)
        self.monitor_publications = config.get('monitor_publications', True)
        self.track_claps = config.get('track_claps', True)
        self.analyze_reading_time = config.get('analyze_reading_time', True)
        
        logger.info("Medium crawler initialized with ultra-advanced content monitoring")

    async def authenticate(self, email: str = None, password: str = None, session_cookies: Dict[str, str] = None) -> bool:
        """
        Authenticate with Medium platform
        
        Args:
            email: User email (for login)
            password: User password (for login)
            session_cookies: Pre-existing session cookies
            
        Returns:
            bool: Authentication success status
        """
        try:
            if session_cookies:
                # Use provided session cookies
                for name, value in session_cookies.items():
                    self.session.cookie_jar.update_cookies({name: value})
                
                # Verify session
                async with self.session.get(f"{self.base_url}/me") as response:
                    if response.status == 200:
                        # Extract user info from response
                        html_content = await response.text()
                        await self._extract_user_info_from_html(html_content)
                        logger.info("Medium session authentication successful")
                        return True
                    else:
                        logger.error("Session verification failed")
                        return False
            
            elif email and password:
                # Perform login (simplified - actual implementation would need CSRF handling)
                login_data = {
                    "email": email,
                    "password": password
                }
                
                # This would require implementing full login flow with CSRF protection
                logger.info("Email/password login not fully implemented. Use session_cookies instead.")
                return False
            
            else:
                logger.error("No authentication credentials provided")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def _extract_user_info_from_html(self, html_content: str):
        """Extract user information from HTML page"""
        try:
            # Look for embedded user data in script tags
            soup = BeautifulSoup(html_content, 'html.parser')
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string and 'window.__APOLLO_STATE__' in script.string:
                    # Extract user ID from Apollo state
                    script_content = script.string
                    # Parse user data (simplified)
                    if '"viewerEdge"' in script_content:
                        # Extract user ID using regex
                        import re
                        user_match = re.search(r'"User:([^"]+)"', script_content)
                        if user_match:
                            self.user_id = user_match.group(1)
                            break
                            
        except Exception as e:
            logger.warning(f"Error extracting user info: {str(e)}")

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[MediumContentType] = None,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        publication: Optional[str] = None,
        limit: int = 50
    ) -> MediumSearchResults:
        """
        Search Medium content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            tag: Tag filter
            author: Author filter
            publication: Publication filter
            limit: Maximum results
            
        Returns:
            MediumSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"search_{hashlib.md5(f'{query}_{content_type}_{tag}_{author}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return MediumSearchResults(**cached_result)
            
            results = MediumSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "tag": tag,
                    "author": author,
                    "publication": publication
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search stories
            if not content_type or content_type == MediumContentType.STORY:
                stories = await self._search_stories(query, tag, author, publication, limit // 2)
                results.stories = stories
                results.total_results += len(stories)
            
            # Search users
            if not content_type:
                users = await self._search_users(query, limit // 4)
                results.users = users
                results.total_results += len(users)
            
            # Search publications
            if not content_type or content_type == MediumContentType.PUBLICATION:
                publications = await self._search_publications(query, limit // 4)
                results.publications = publications
                results.total_results += len(publications)
            
            # Search tags
            tags = await self._search_tags(query, limit // 4)
            results.tags = tags
            results.total_results += len(tags)
            
            # Process content for protection
            for story in results.stories:
                story.similarity_score = await self._calculate_similarity(story)
                story.protection_status = await self._check_protection_status(story)
            
            # Cache results
            await self.cache_manager.set(cache_key, results.dict())
            
            logger.info(f"Medium search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return MediumSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def _search_stories(
        self,
        query: str,
        tag: Optional[str],
        author: Optional[str],
        publication: Optional[str],
        limit: int
    ) -> List[MediumStory]:
        """Search for Medium stories"""
        try:
            # Use GraphQL search
            search_query = {
                "operationName": "SearchQuery",
                "variables": {
                    "query": query,
                    "pagingOptions": {
                        "limit": limit,
                        "page": 1
                    },
                    "searchInCollection": None,
                    "domain": None,
                    "tags": [tag] if tag else [],
                    "authorNames": [author] if author else []
                },
                "query": """
                query SearchQuery($query: String!, $pagingOptions: PagingOptions!, $searchInCollection: ID, $domain: String, $tags: [String!], $authorNames: [String!]) {
                  search(query: $query, searchInCollection: $searchInCollection, domain: $domain, tags: $tags, authorNames: $authorNames) {
                    posts(pagingOptions: $pagingOptions) {
                      ...PostPreview
                    }
                  }
                }
                fragment PostPreview on Post {
                  id
                  title
                  mediumUrl
                  author {
                    id
                    name
                    username
                  }
                  firstPublishedAt
                  readingTime
                  clapCount
                  voterCount
                }
                """
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with self.session.post(
                self.gql_endpoint,
                json=search_query,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    posts_data = data.get("data", {}).get("search", {}).get("posts", [])
                    
                    stories = []
                    for post_data in posts_data:
                        try:
                            story = await self._parse_story_summary(post_data)
                            stories.append(story)
                        except Exception as e:
                            logger.warning(f"Error parsing story data: {str(e)}")
                            continue
                    
                    return stories
                else:
                    logger.error(f"Search stories failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Story search error: {str(e)}")
            return []

    async def _search_users(self, query: str, limit: int) -> List[MediumUser]:
        """Search for Medium users"""
        try:
            # Simple search using web scraping
            search_url = f"{self.base_url}/search/users"
            params = {"q": query}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    users = await self._parse_users_from_html(html_content, limit)
                    return users
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"User search error: {str(e)}")
            return []

    async def _search_publications(self, query: str, limit: int) -> List[MediumPublication]:
        """Search for Medium publications"""
        try:
            # Search publications using web scraping
            search_url = f"{self.base_url}/search/publications"
            params = {"q": query}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    publications = await self._parse_publications_from_html(html_content, limit)
                    return publications
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Publication search error: {str(e)}")
            return []

    async def _search_tags(self, query: str, limit: int) -> List[MediumTag]:
        """Search for Medium tags"""
        try:
            # Search tags using API
            search_url = f"{self.base_url}/search/tags"
            params = {"q": query}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    tags = await self._parse_tags_from_html(html_content, limit)
                    return tags
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Tag search error: {str(e)}")
            return []

    async def get_content_details(self, story_url: str) -> Optional[MediumStory]:
        """
        Get detailed information about specific Medium story
        
        Args:
            story_url: Medium story URL
            
        Returns:
            Optional[MediumStory]: Detailed story information
        """
        await self.rate_limiter.acquire()
        
        try:
            # Extract story ID from URL
            story_id = self._extract_story_id_from_url(story_url)
            
            # Check cache first
            cache_key = f"story_{story_id}"
            cached_content = await self.cache_manager.get(cache_key)
            if cached_content:
                return MediumStory(**cached_content)
            
            async with self.session.get(story_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    story = await self._parse_story_from_html(html_content, story_url)
                    
                    if story:
                        # Enhanced analysis
                        story.similarity_score = await self._calculate_similarity(story)
                        story.protection_status = await self._check_protection_status(story)
                        
                        # Cache the result
                        await self.cache_manager.set(cache_key, story.dict())
                        
                        logger.info(f"Retrieved Medium story details: {story_id}")
                        return story
                    else:
                        return None
                else:
                    logger.warning(f"Story not accessible: {story_url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting story details: {str(e)}")
            return None

    async def monitor_content(
        self,
        author_usernames: List[str] = None,
        publications: List[str] = None,
        tags: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 3600
    ) -> AsyncGenerator[MediumStory, None]:
        """
        Real-time content monitoring for Medium
        
        Args:
            author_usernames: Authors to monitor
            publications: Publications to monitor
            tags: Tags to monitor
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            MediumStory: New stories detected
        """
        author_usernames = author_usernames or []
        publications = publications or []
        tags = tags or []
        keywords = keywords or []
        
        self.monitored_authors.update(author_usernames)
        self.monitored_publications.update(publications)
        self.monitored_tags.update(tags)
        
        logger.info(f"Starting Medium monitoring for {len(author_usernames)} authors, {len(publications)} publications")
        
        last_check = datetime.utcnow()
        seen_stories = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Monitor specific authors
                for username in author_usernames:
                    try:
                        author_stories = await self._get_author_recent_stories(username, last_check)
                        
                        for story in author_stories:
                            if story.story_id not in seen_stories:
                                # Enhanced monitoring analysis
                                story.similarity_score = await self._calculate_similarity(story)
                                story.protection_status = await self._check_protection_status(story)
                                
                                seen_stories.add(story.story_id)
                                
                                logger.info(f"New story from {username}: {story.title}")
                                yield story
                    
                    except Exception as e:
                        logger.error(f"Error monitoring author {username}: {str(e)}")
                        continue
                
                # Monitor publications
                for publication in publications:
                    try:
                        pub_stories = await self._get_publication_recent_stories(publication, last_check)
                        
                        for story in pub_stories:
                            if story.story_id not in seen_stories:
                                story.similarity_score = await self._calculate_similarity(story)
                                story.protection_status = await self._check_protection_status(story)
                                
                                seen_stories.add(story.story_id)
                                yield story
                    
                    except Exception as e:
                        logger.error(f"Error monitoring publication {publication}: {str(e)}")
                        continue
                
                # Monitor tags
                for tag in tags:
                    try:
                        tag_stories = await self._get_tag_recent_stories(tag, last_check)
                        
                        for story in tag_stories:
                            if story.story_id not in seen_stories:
                                story.similarity_score = await self._calculate_similarity(story)
                                story.protection_status = await self._check_protection_status(story)
                                
                                seen_stories.add(story.story_id)
                                yield story
                    
                    except Exception as e:
                        logger.error(f"Error monitoring tag {tag}: {str(e)}")
                        continue
                
                last_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(300)

    async def detect_similarity(
        self,
        target_story: MediumStory,
        comparison_set: List[MediumStory],
        threshold: float = None
    ) -> List[Tuple[MediumStory, float]]:
        """
        Detect story similarity
        
        Args:
            target_story: Story to compare
            comparison_set: Stories to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[MediumStory, float]]: Similar stories with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_stories = []
        
        try:
            target_features = await self._extract_story_features(target_story)
            
            for story in comparison_set:
                if story.story_id == target_story.story_id:
                    continue
                
                comp_features = await self._extract_story_features(story)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_stories.append((story, similarity_score))
            
            similar_stories.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_stories)} matches found")
            return similar_stories
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def _extract_story_features(self, story: MediumStory) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "title": story.title.lower(),
            "subtitle": (story.subtitle or "").lower(),
            "content_preview": story.content_preview.lower(),
            "tags": set(tag.slug.lower() for tag in story.tags),
            "author_id": story.author.user_id,
            "publication_id": story.publication.publication_id if story.publication else None,
            "word_count": story.word_count,
            "reading_time": story.reading_time.minutes,
            "is_member_only": story.is_member_only,
            "is_series": story.is_series,
            "language": story.language
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between story features"""
        try:
            scores = []
            
            # Title similarity
            title_sim = SequenceMatcher(
                None, features1.get("title", ""), features2.get("title", "")
            ).ratio()
            scores.append(title_sim * 0.35)  # 35% weight
            
            # Content similarity
            content_sim = SequenceMatcher(
                None, features1.get("content_preview", ""), features2.get("content_preview", "")
            ).ratio()
            scores.append(content_sim * 0.3)  # 30% weight
            
            # Tags overlap
            tags1 = features1.get("tags", set())
            tags2 = features2.get("tags", set())
            if tags1 and tags2:
                tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
                scores.append(tag_overlap * 0.25)  # 25% weight
            
            # Reading time similarity
            rt1 = features1.get("reading_time", 0)
            rt2 = features2.get("reading_time", 0)
            if rt1 > 0 and rt2 > 0:
                rt_sim = 1 - abs(rt1 - rt2) / max(rt1, rt2)
                scores.append(rt_sim * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def get_analytics(
        self,
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> MediumAnalytics:
        """
        Generate comprehensive analytics for Medium user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            MediumAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            
            # Get user's stories in the period
            user_stories = await self._get_user_stories_in_period(user_id, start_time, end_time)
            
            if not user_stories:
                return MediumAnalytics(
                    user_id=user_id,
                    analysis_period=analysis_period,
                    total_stories_published=0,
                    total_responses_written=0,
                    total_claps_received=0,
                    total_followers_gained=0,
                    average_reading_time=0.0,
                    top_performing_tags=[],
                    publication_distribution={},
                    reading_ratio=0.0,
                    engagement_rate=0.0,
                    member_content_ratio=0.0,
                    series_completion_rate=0.0,
                    cross_publication_reach=0,
                    estimated_earnings=0.0,
                    content_quality_score=0.0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate analytics metrics
            total_stories_published = len(user_stories)
            total_claps_received = sum(story.clap_count for story in user_stories)
            average_reading_time = sum(story.reading_time.minutes for story in user_stories) / total_stories_published
            
            # Tag analysis
            tag_counts = {}
            for story in user_stories:
                for tag in story.tags:
                    tag_counts[tag.slug] = tag_counts.get(tag.slug, 0) + 1
            
            top_performing_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_performing_tags = [tag[0] for tag in top_performing_tags]
            
            # Publication distribution
            publication_distribution = {}
            for story in user_stories:
                pub_name = story.publication.name if story.publication else "Personal"
                publication_distribution[pub_name] = publication_distribution.get(pub_name, 0) + 1
            
            # Member content analysis
            member_stories = sum(1 for story in user_stories if story.is_member_only)
            member_content_ratio = member_stories / total_stories_published if total_stories_published > 0 else 0.0
            
            # Engagement rate
            total_responses = sum(story.response_count for story in user_stories)
            engagement_rate = (total_claps_received + total_responses) / total_stories_published if total_stories_published > 0 else 0.0
            
            # Content quality score (simplified)
            avg_claps = total_claps_received / total_stories_published if total_stories_published > 0 else 0.0
            avg_responses = total_responses / total_stories_published if total_stories_published > 0 else 0.0
            content_quality_score = min(100, (avg_claps * 0.6 + avg_responses * 0.4) / 10)
            
            # Protection metrics
            similarity_violations = sum(1 for story in user_stories if (story.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for story in user_stories if story.protection_status == "violation")
            
            analytics = MediumAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_stories_published=total_stories_published,
                total_responses_written=0,  # Would need additional API calls
                total_claps_received=total_claps_received,
                total_followers_gained=0,  # Would need historical data
                average_reading_time=average_reading_time,
                top_performing_tags=top_performing_tags,
                publication_distribution=publication_distribution,
                reading_ratio=0.0,  # Would need reading data
                engagement_rate=engagement_rate,
                member_content_ratio=member_content_ratio,
                series_completion_rate=0.0,  # Would need series data
                cross_publication_reach=len(publication_distribution),
                estimated_earnings=0.0,  # Would need earnings API
                content_quality_score=content_quality_score,
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for user {user_id}: {total_stories_published} stories analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return MediumAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_stories_published=0,
                total_responses_written=0,
                total_claps_received=0,
                total_followers_gained=0,
                average_reading_time=0.0,
                top_performing_tags=[],
                publication_distribution={},
                reading_ratio=0.0,
                engagement_rate=0.0,
                member_content_ratio=0.0,
                series_completion_rate=0.0,
                cross_publication_reach=0,
                estimated_earnings=0.0,
                content_quality_score=0.0,
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods for parsing and data extraction
    
    async def _parse_story_summary(self, data: Dict[str, Any]) -> MediumStory:
        """Parse story summary from GraphQL response"""
        # Simplified parsing - actual implementation would be more comprehensive
        author_data = data.get("author", {})
        author = MediumUser(
            user_id=author_data.get("id", ""),
            username=author_data.get("username", ""),
            name=author_data.get("name", ""),
            created_at=datetime.utcnow(),
            membership_type=MediumMembershipType.FREE
        )
        
        reading_time = MediumReadingTime(
            text=f"{data.get('readingTime', 0)} min read",
            minutes=data.get('readingTime', 0),
            words=data.get('readingTime', 0) * 200  # Approximate
        )
        
        return MediumStory(
            story_id=data.get("id", ""),
            title=data.get("title", ""),
            content="",
            content_preview="",
            author=author,
            published_at=datetime.fromisoformat(data.get("firstPublishedAt", datetime.utcnow().isoformat())),
            last_modified_at=datetime.utcnow(),
            first_published_at=datetime.fromisoformat(data.get("firstPublishedAt", datetime.utcnow().isoformat())),
            latest_version="1",
            slug="",
            unique_slug="",
            medium_url=data.get("mediumUrl", ""),
            reading_time=reading_time,
            clap_count=data.get("clapCount", 0),
            voter_count=data.get("voterCount", 0),
            word_count=0
        )

    def _extract_story_id_from_url(self, url: str) -> str:
        """Extract story ID from Medium URL"""
        # Medium URLs have format: https://medium.com/@author/title-story_id
        parts = url.split('-')
        if parts:
            return parts[-1]
        return hashlib.md5(url.encode()).hexdigest()[:12]

    async def _parse_story_from_html(self, html_content: str, url: str) -> Optional[MediumStory]:
        """
Parse story from HTML page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text().strip() if title_elem else "Untitled"
            
            # Extract content (simplified)
            content_elem = soup.find('article')
            content = content_elem.get_text().strip() if content_elem else ""
            
            # Create basic story object
            story = MediumStory(
                story_id=self._extract_story_id_from_url(url),
                title=title,
                content=content,
                content_preview=content[:200] + "..." if len(content) > 200 else content,
                author=MediumUser(
                    user_id="unknown",
                    username="unknown",
                    name="Unknown Author",
                    created_at=datetime.utcnow(),
                    membership_type=MediumMembershipType.FREE
                ),
                published_at=datetime.utcnow(),
                last_modified_at=datetime.utcnow(),
                first_published_at=datetime.utcnow(),
                latest_version="1",
                slug="",
                unique_slug="",
                medium_url=url,
                reading_time=MediumReadingTime(
                    text="5 min read",
                    minutes=5,
                    words=len(content.split())
                ),
                word_count=len(content.split())
            )
            
            return story
            
        except Exception as e:
            logger.error(f"Error parsing story from HTML: {str(e)}")
            return None

    async def _parse_users_from_html(self, html_content: str, limit: int) -> List[MediumUser]:
        """Parse users from search results HTML"""
        # Simplified implementation
        return []

    async def _parse_publications_from_html(self, html_content: str, limit: int) -> List[MediumPublication]:
        """
Parse publications from search results HTML"""
        # Simplified implementation
        return []

    async def _parse_tags_from_html(self, html_content: str, limit: int) -> List[MediumTag]:
        """
Parse tags from search results HTML"""
        # Simplified implementation
        return []

    async def _get_author_recent_stories(self, username: str, since: datetime) -> List[MediumStory]:
        """
Get recent stories from author"""
        # Simplified implementation
        return []

    async def _get_publication_recent_stories(self, publication: str, since: datetime) -> List[MediumStory]:
        """
Get recent stories from publication"""
        # Simplified implementation
        return []

    async def _get_tag_recent_stories(self, tag: str, since: datetime) -> List[MediumStory]:
        """
Get recent stories for tag"""
        # Simplified implementation
        return []

    async def _get_user_stories_in_period(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[MediumStory]:
        """
Get user's stories in specific time period"""
        # Simplified implementation
        return []

    async def _calculate_similarity(self, story: MediumStory) -> float:
        """
Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, story: MediumStory) -> str:
        """
Check protection status of story"""
        if story.story_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> bool:
        """Handle rate limiting responses"""
        if response.status == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return True
        return False

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Medium crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
