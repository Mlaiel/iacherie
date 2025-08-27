"""
Medium Crawler Implementation
=============================

Advanced Medium platform crawler for publishing and content monitoring.
Implements comprehensive Article, Author, Publication, and Topic tracking.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class MediumArticle:
    """Medium article information"""
    article_id: str
    title: str
    subtitle: str
    content: str
    content_preview: str
    author_id: str
    author_name: str
    author_username: str
    publication_id: Optional[str]
    publication_name: Optional[str]
    published_at: datetime
    updated_at: Optional[datetime]
    url: str
    canonical_url: Optional[str]
    featured_image_url: Optional[str]
    reading_time_minutes: int
    word_count: int
    clap_count: int
    response_count: int
    voter_count: int
    is_locked: bool
    is_member_only: bool
    is_shortform: bool
    tags: List[str]
    topics: List[str]
    language: str
    license: str
    seo_title: str
    meta_description: str
    social_title: str
    social_description: str
    visibility: str  # public, unlisted, member_only
    monetization_enabled: bool
    import_source: Optional[str]


@dataclass
class MediumAuthor:
    """Medium author information"""
    author_id: str
    username: str
    name: str
    bio: str
    image_url: str
    url: str
    follower_count: int
    following_count: int
    is_writer_program_enrolled: bool
    is_suspended: bool
    has_list: bool
    is_blocking: bool
    is_blocked_by: bool
    social_stats: Dict[str, int]
    twitter_username: Optional[str]
    facebook_profile: Optional[str]
    linkedin_profile: Optional[str]
    website_url: Optional[str]
    location: Optional[str]
    publication_ids: List[str]
    top_tags: List[str]
    total_stories: int
    total_responses: int
    total_claps_received: int
    joined_at: datetime
    last_active: Optional[datetime]
    medium_member_at: Optional[datetime]
    stripe_customer_id: Optional[str]


@dataclass
class MediumPublication:
    """Medium publication information"""
    publication_id: str
    name: str
    description: str
    url: str
    slug: str
    image_url: str
    creator_id: str
    follower_count: int
    story_count: int
    tags: List[str]
    topics: List[str]
    created_at: datetime
    updated_at: datetime
    domain: Optional[str]
    email: Optional[str]
    facebook_page_name: Optional[str]
    twitter_username: Optional[str]
    instagram_username: Optional[str]
    newsletter_enabled: bool
    allow_notes: bool
    editors: List[str]
    writers: List[str]
    submission_guidelines: str
    navigation_links: List[Dict[str, str]]
    custom_styles: Dict[str, str]
    membership_required: bool
    monetization_enabled: bool


@dataclass
class MediumTopic:
    """Medium topic information"""
    topic_id: str
    name: str
    slug: str
    description: str
    image_url: str
    follower_count: int
    story_count: int
    created_at: datetime
    is_following: bool
    related_topics: List[str]
    trending_stories: List[str]
    featured_stories: List[str]
    top_writers: List[str]
    weekly_stats: Dict[str, int]


@dataclass
class MediumResponse:
    """Medium response (comment) information"""
    response_id: str
    content: str
    author_id: str
    author_name: str
    author_username: str
    story_id: str
    parent_response_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    clap_count: int
    is_private_note: bool
    preview_content: str
    selected_range: Optional[Dict[str, int]]
    mentioned_users: List[str]


class MediumCrawler(PlatformCrawler):
    """
    Advanced Medium crawler for publishing and content monitoring.
    
    Features:
    - Article content tracking
    - Author profile analysis
    - Publication monitoring
    - Topic trend analysis
    - Response and engagement tracking
    - Reading time and metrics analysis
    - Member-only content detection
    - SEO and metadata extraction
    - Social sharing analysis
    - Monetization tracking
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "medium"
        self.base_url = "https://medium.com"
        self.api_base_url = "https://medium.com/_/api"
        
        # Rate limiting (Medium has moderate limits)
        self.requests_per_minute = 20
        self.min_delay = 3.0
        self.max_delay = 6.0
        
        # Content type mappings
        self.content_types = {
            'articles': self._crawl_articles,
            'authors': self._crawl_authors,
            'publications': self._crawl_publications,
            'topics': self._crawl_topics,
            'responses': self._crawl_responses,
            'trending': self._crawl_trending,
            'featured': self._crawl_featured,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Medium-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://medium.com/',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "articles", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on Medium.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Medium {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Medium content: {str(e)}")
            return []
    
    async def _crawl_articles(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Medium articles"""
        try:
            results = []
            
            # Mock article data
            mock_articles = await self._get_mock_articles(query, max_results)
            
            for article_data in mock_articles:
                article = await self._parse_article_data(article_data)
                if article:
                    result = CrawlerResult(
                        url=article.url,
                        title=article.title,
                        content=article.content_preview,
                        metadata={
                            'article_data': asdict(article),
                            'platform': 'medium',
                            'content_type': 'article',
                            'author_name': article.author_name,
                            'author_username': article.author_username,
                            'publication_name': article.publication_name,
                            'reading_time_minutes': article.reading_time_minutes,
                            'word_count': article.word_count,
                            'clap_count': article.clap_count,
                            'response_count': article.response_count,
                            'is_locked': article.is_locked,
                            'is_member_only': article.is_member_only,
                            'is_shortform': article.is_shortform,
                            'tags': article.tags,
                            'topics': article.topics,
                            'language': article.language,
                            'visibility': article.visibility,
                            'monetization_enabled': article.monetization_enabled
                        },
                        timestamp=article.published_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Medium articles: {str(e)}")
            return []
    
    async def _crawl_authors(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Medium authors"""
        try:
            results = []
            
            # Mock author data
            mock_authors = await self._get_mock_authors(query, max_results)
            
            for author_data in mock_authors:
                author = await self._parse_author_data(author_data)
                if author:
                    result = CrawlerResult(
                        url=author.url,
                        title=f"{author.name} (@{author.username})",
                        content=author.bio,
                        metadata={
                            'author_data': asdict(author),
                            'platform': 'medium',
                            'content_type': 'author',
                            'username': author.username,
                            'name': author.name,
                            'follower_count': author.follower_count,
                            'following_count': author.following_count,
                            'is_writer_program_enrolled': author.is_writer_program_enrolled,
                            'total_stories': author.total_stories,
                            'total_responses': author.total_responses,
                            'total_claps_received': author.total_claps_received,
                            'top_tags': author.top_tags,
                            'publication_ids': author.publication_ids,
                            'location': author.location,
                            'social_stats': author.social_stats,
                            'medium_member_at': author.medium_member_at.isoformat() if author.medium_member_at else None
                        },
                        timestamp=author.joined_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Medium authors: {str(e)}")
            return []
    
    async def _crawl_publications(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Medium publications"""
        try:
            results = []
            
            # Mock publication data
            mock_publications = await self._get_mock_publications(query, max_results)
            
            for publication_data in mock_publications:
                publication = await self._parse_publication_data(publication_data)
                if publication:
                    result = CrawlerResult(
                        url=publication.url,
                        title=publication.name,
                        content=publication.description,
                        metadata={
                            'publication_data': asdict(publication),
                            'platform': 'medium',
                            'content_type': 'publication',
                            'name': publication.name,
                            'slug': publication.slug,
                            'follower_count': publication.follower_count,
                            'story_count': publication.story_count,
                            'tags': publication.tags,
                            'topics': publication.topics,
                            'domain': publication.domain,
                            'newsletter_enabled': publication.newsletter_enabled,
                            'allow_notes': publication.allow_notes,
                            'editors': publication.editors,
                            'writers': publication.writers,
                            'membership_required': publication.membership_required,
                            'monetization_enabled': publication.monetization_enabled
                        },
                        timestamp=publication.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Medium publications: {str(e)}")
            return []
    
    async def _crawl_topics(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Medium topics"""
        try:
            results = []
            
            # Mock topic data
            mock_topics = await self._get_mock_topics(query, max_results)
            
            for topic_data in mock_topics:
                topic = await self._parse_topic_data(topic_data)
                if topic:
                    result = CrawlerResult(
                        url=f"{self.base_url}/topic/{topic.slug}",
                        title=topic.name,
                        content=topic.description,
                        metadata={
                            'topic_data': asdict(topic),
                            'platform': 'medium',
                            'content_type': 'topic',
                            'name': topic.name,
                            'slug': topic.slug,
                            'follower_count': topic.follower_count,
                            'story_count': topic.story_count,
                            'is_following': topic.is_following,
                            'related_topics': topic.related_topics,
                            'trending_stories': topic.trending_stories,
                            'featured_stories': topic.featured_stories,
                            'top_writers': topic.top_writers,
                            'weekly_stats': topic.weekly_stats
                        },
                        timestamp=topic.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Medium topics: {str(e)}")
            return []
    
    async def _crawl_responses(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Medium responses"""
        try:
            results = []
            
            # Mock response data
            mock_responses = await self._get_mock_responses(query, max_results)
            
            for response_data in mock_responses:
                response = await self._parse_response_data(response_data)
                if response:
                    result = CrawlerResult(
                        url=f"{self.base_url}/@{response.author_username}/{response.response_id}",
                        title=f"Response by {response.author_name}",
                        content=response.content,
                        metadata={
                            'response_data': asdict(response),
                            'platform': 'medium',
                            'content_type': 'response',
                            'author_name': response.author_name,
                            'author_username': response.author_username,
                            'story_id': response.story_id,
                            'parent_response_id': response.parent_response_id,
                            'clap_count': response.clap_count,
                            'is_private_note': response.is_private_note,
                            'mentioned_users': response.mentioned_users
                        },
                        timestamp=response.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Medium responses: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending Medium content"""
        try:
            results = []
            
            # Get trending content
            trending_content = await self._get_trending_content(query, max_results, filters)
            
            for content in trending_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[TRENDING] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'trending_data': content,
                        'platform': 'medium',
                        'content_type': 'trending',
                        'is_trending': True,
                        'trend_score': content.get('trend_score', 0),
                        'category': content.get('category', 'general')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling trending Medium content: {str(e)}")
            return []
    
    async def _crawl_featured(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl featured Medium content"""
        try:
            results = []
            
            # Get featured content
            featured_content = await self._get_featured_content(query, max_results, filters)
            
            for content in featured_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[FEATURED] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'featured_data': content,
                        'platform': 'medium',
                        'content_type': 'featured',
                        'is_featured': True,
                        'feature_score': content.get('feature_score', 0),
                        'featured_by': content.get('featured_by', 'medium')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling featured Medium content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Medium search"""
        try:
            results = []
            
            # Search across different content types
            articles = await self._crawl_articles(query, max_results // 2, filters)
            authors = await self._crawl_authors(query, max_results // 4, filters)
            publications = await self._crawl_publications(query, max_results // 4, filters)
            
            results.extend(articles)
            results.extend(authors)
            results.extend(publications)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Medium search: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_articles(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock article data"""
        articles = []
        
        for i in range(min(max_results, 25)):
            published_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            articles.append({
                'id': f'article_{i}',
                'title': f'{query}: A Comprehensive Guide {i}' if query else f'Article Title {i}',
                'subtitle': f'Exploring {query} in depth' if query else f'Article subtitle {i}',
                'content': f'Detailed analysis of {query} with practical insights...' if query else f'Article content {i}',
                'content_preview': f'In this article, we explore {query}...' if query else f'Preview content {i}',
                'author_id': f'author_{i}',
                'author_name': f'{query} Expert {i}' if query else f'Author {i}',
                'author_username': f'{query.lower() if query else "author"}{i}',
                'publication_id': f'pub_{i % 5}' if random.choice([True, False]) else None,
                'publication_name': f'{query} Publication' if query and random.choice([True, False]) else None,
                'published_at': published_at.isoformat(),
                'url': f'{self.base_url}/@{query.lower() if query else "author"}{i}/{query.lower() if query else "article"}-{i}',
                'reading_time_minutes': random.randint(3, 30),
                'word_count': random.randint(500, 5000),
                'clap_count': random.randint(10, 1000),
                'response_count': random.randint(0, 50),
                'voter_count': random.randint(5, 500),
                'is_locked': random.choice([True, False]),
                'is_member_only': random.choice([True, False]),
                'is_shortform': random.choice([True, False]),
                'tags': [query] if query else ['technology', 'writing', 'medium'],
                'topics': [query] if query else ['Technology', 'Writing'],
                'language': 'en',
                'visibility': random.choice(['public', 'unlisted', 'member_only']),
                'monetization_enabled': random.choice([True, False])
            })
        
        return articles
    
    async def _get_mock_authors(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock author data"""
        authors = []
        
        for i in range(min(max_results, 15)):
            joined_at = datetime.utcnow() - timedelta(days=random.randint(365, 2555))
            medium_member_at = joined_at + timedelta(days=random.randint(1, 365)) if random.choice([True, False]) else None
            authors.append({
                'id': f'author_{i}',
                'username': f'{query.lower() if query else "writer"}{i}',
                'name': f'{query} Writer {i}' if query else f'Writer {i}',
                'bio': f'Passionate {query} expert and writer' if query else f'Writer bio {i}',
                'url': f'{self.base_url}/@{query.lower() if query else "writer"}{i}',
                'follower_count': random.randint(100, 50000),
                'following_count': random.randint(50, 1000),
                'is_writer_program_enrolled': random.choice([True, False]),
                'total_stories': random.randint(10, 500),
                'total_responses': random.randint(5, 200),
                'total_claps_received': random.randint(100, 10000),
                'top_tags': [query] if query else ['technology', 'writing', 'productivity'],
                'publication_ids': [f'pub_{j}' for j in range(random.randint(0, 3))],
                'location': random.choice(['San Francisco, CA', 'New York, NY', 'London, UK', None]),
                'social_stats': {
                    'twitter_followers': random.randint(100, 10000),
                    'linkedin_connections': random.randint(50, 5000)
                },
                'joined_at': joined_at.isoformat(),
                'medium_member_at': medium_member_at.isoformat() if medium_member_at else None
            })
        
        return authors
    
    async def _get_mock_publications(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock publication data"""
        publications = []
        
        for i in range(min(max_results, 10)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            publications.append({
                'id': f'publication_{i}',
                'name': f'{query} Publication {i}' if query else f'Publication {i}',
                'description': f'A publication focused on {query}' if query else f'Publication description {i}',
                'url': f'{self.base_url}/publication/{query.lower() if query else "pub"}{i}',
                'slug': f'{query.lower() if query else "publication"}-{i}',
                'creator_id': f'author_{i}',
                'follower_count': random.randint(1000, 100000),
                'story_count': random.randint(50, 5000),
                'tags': [query] if query else ['technology', 'business', 'startup'],
                'topics': [query] if query else ['Technology', 'Business'],
                'created_at': created_at.isoformat(),
                'newsletter_enabled': random.choice([True, False]),
                'allow_notes': random.choice([True, False]),
                'editors': [f'editor_{j}' for j in range(random.randint(1, 5))],
                'writers': [f'writer_{j}' for j in range(random.randint(5, 50))],
                'membership_required': random.choice([True, False]),
                'monetization_enabled': random.choice([True, False])
            })
        
        return publications
    
    async def _get_mock_topics(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock topic data"""
        topics = []
        
        for i in range(min(max_results, 20)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            topics.append({
                'id': f'topic_{i}',
                'name': f'{query}' if query else f'Topic {i}',
                'slug': f'{query.lower() if query else "topic"}-{i}',
                'description': f'Everything about {query}' if query else f'Topic description {i}',
                'follower_count': random.randint(1000, 100000),
                'story_count': random.randint(100, 10000),
                'created_at': created_at.isoformat(),
                'is_following': random.choice([True, False]),
                'related_topics': [f'related_{j}' for j in range(random.randint(3, 8))],
                'trending_stories': [f'story_{j}' for j in range(5)],
                'featured_stories': [f'featured_{j}' for j in range(3)],
                'top_writers': [f'writer_{j}' for j in range(10)],
                'weekly_stats': {
                    'new_stories': random.randint(10, 100),
                    'total_claps': random.randint(1000, 10000),
                    'new_followers': random.randint(50, 500)
                }
            })
        
        return topics
    
    async def _get_mock_responses(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock response data"""
        responses = []
        
        for i in range(min(max_results, 30)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 168))
            responses.append({
                'id': f'response_{i}',
                'content': f'Great insights about {query}! Thank you for sharing.' if query else f'Response content {i}',
                'author_id': f'author_{i}',
                'author_name': f'{query} Reader {i}' if query else f'Reader {i}',
                'author_username': f'{query.lower() if query else "reader"}{i}',
                'story_id': f'story_{i % 10}',
                'parent_response_id': f'response_{i-1}' if i > 0 and random.choice([True, False]) else None,
                'created_at': created_at.isoformat(),
                'clap_count': random.randint(0, 50),
                'is_private_note': random.choice([True, False]),
                'preview_content': f'Great insights about {query}...' if query else f'Preview {i}',
                'mentioned_users': [f'@user{j}' for j in range(random.randint(0, 3))]
            })
        
        return responses
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Content {i}',
                'url': f'{self.base_url}/trending/{i}',
                'description': f'Trending content about {query}' if query else f'Trending description {i}',
                'trend_score': random.randint(80, 100),
                'category': random.choice(['technology', 'business', 'health', 'culture'])
            })
        
        return content
    
    async def _get_featured_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get featured content"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Featured: {query} {i}' if query else f'Featured Content {i}',
                'url': f'{self.base_url}/featured/{i}',
                'description': f'Featured content about {query}' if query else f'Featured description {i}',
                'feature_score': random.randint(90, 100),
                'featured_by': random.choice(['medium', 'publication', 'editor'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_article_data(self, article_data: Dict[str, Any]) -> Optional[MediumArticle]:
        """Parse article data"""
        try:
            published_at = datetime.fromisoformat(article_data.get('published_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            article = MediumArticle(
                article_id=article_data.get('id', ''),
                title=article_data.get('title', ''),
                subtitle=article_data.get('subtitle', ''),
                content=article_data.get('content', ''),
                content_preview=article_data.get('content_preview', ''),
                author_id=article_data.get('author_id', ''),
                author_name=article_data.get('author_name', ''),
                author_username=article_data.get('author_username', ''),
                publication_id=article_data.get('publication_id'),
                publication_name=article_data.get('publication_name'),
                published_at=published_at,
                updated_at=None,
                url=article_data.get('url', ''),
                canonical_url=article_data.get('canonical_url'),
                featured_image_url=article_data.get('featured_image_url'),
                reading_time_minutes=article_data.get('reading_time_minutes', 0),
                word_count=article_data.get('word_count', 0),
                clap_count=article_data.get('clap_count', 0),
                response_count=article_data.get('response_count', 0),
                voter_count=article_data.get('voter_count', 0),
                is_locked=article_data.get('is_locked', False),
                is_member_only=article_data.get('is_member_only', False),
                is_shortform=article_data.get('is_shortform', False),
                tags=article_data.get('tags', []),
                topics=article_data.get('topics', []),
                language=article_data.get('language', 'en'),
                license='',
                seo_title=article_data.get('seo_title', ''),
                meta_description=article_data.get('meta_description', ''),
                social_title=article_data.get('social_title', ''),
                social_description=article_data.get('social_description', ''),
                visibility=article_data.get('visibility', 'public'),
                monetization_enabled=article_data.get('monetization_enabled', False),
                import_source=article_data.get('import_source')
            )
            
            return article
            
        except Exception as e:
            self.logger.error(f"Error parsing article data: {str(e)}")
            return None
    
    async def _parse_author_data(self, author_data: Dict[str, Any]) -> Optional[MediumAuthor]:
        """Parse author data"""
        try:
            joined_at = datetime.fromisoformat(author_data.get('joined_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            medium_member_at = None
            if author_data.get('medium_member_at'):
                medium_member_at = datetime.fromisoformat(author_data['medium_member_at'].replace('Z', '+00:00'))
            
            author = MediumAuthor(
                author_id=author_data.get('id', ''),
                username=author_data.get('username', ''),
                name=author_data.get('name', ''),
                bio=author_data.get('bio', ''),
                image_url='',
                url=author_data.get('url', ''),
                follower_count=author_data.get('follower_count', 0),
                following_count=author_data.get('following_count', 0),
                is_writer_program_enrolled=author_data.get('is_writer_program_enrolled', False),
                is_suspended=author_data.get('is_suspended', False),
                has_list=author_data.get('has_list', False),
                is_blocking=author_data.get('is_blocking', False),
                is_blocked_by=author_data.get('is_blocked_by', False),
                social_stats=author_data.get('social_stats', {}),
                twitter_username=author_data.get('twitter_username'),
                facebook_profile=author_data.get('facebook_profile'),
                linkedin_profile=author_data.get('linkedin_profile'),
                website_url=author_data.get('website_url'),
                location=author_data.get('location'),
                publication_ids=author_data.get('publication_ids', []),
                top_tags=author_data.get('top_tags', []),
                total_stories=author_data.get('total_stories', 0),
                total_responses=author_data.get('total_responses', 0),
                total_claps_received=author_data.get('total_claps_received', 0),
                joined_at=joined_at,
                last_active=None,
                medium_member_at=medium_member_at,
                stripe_customer_id=author_data.get('stripe_customer_id')
            )
            
            return author
            
        except Exception as e:
            self.logger.error(f"Error parsing author data: {str(e)}")
            return None
    
    async def _parse_publication_data(self, publication_data: Dict[str, Any]) -> Optional[MediumPublication]:
        """Parse publication data"""
        try:
            created_at = datetime.fromisoformat(publication_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            publication = MediumPublication(
                publication_id=publication_data.get('id', ''),
                name=publication_data.get('name', ''),
                description=publication_data.get('description', ''),
                url=publication_data.get('url', ''),
                slug=publication_data.get('slug', ''),
                image_url='',
                creator_id=publication_data.get('creator_id', ''),
                follower_count=publication_data.get('follower_count', 0),
                story_count=publication_data.get('story_count', 0),
                tags=publication_data.get('tags', []),
                topics=publication_data.get('topics', []),
                created_at=created_at,
                updated_at=datetime.utcnow(),
                domain=publication_data.get('domain'),
                email=publication_data.get('email'),
                facebook_page_name=publication_data.get('facebook_page_name'),
                twitter_username=publication_data.get('twitter_username'),
                instagram_username=publication_data.get('instagram_username'),
                newsletter_enabled=publication_data.get('newsletter_enabled', False),
                allow_notes=publication_data.get('allow_notes', True),
                editors=publication_data.get('editors', []),
                writers=publication_data.get('writers', []),
                submission_guidelines=publication_data.get('submission_guidelines', ''),
                navigation_links=publication_data.get('navigation_links', []),
                custom_styles=publication_data.get('custom_styles', {}),
                membership_required=publication_data.get('membership_required', False),
                monetization_enabled=publication_data.get('monetization_enabled', False)
            )
            
            return publication
            
        except Exception as e:
            self.logger.error(f"Error parsing publication data: {str(e)}")
            return None
    
    async def _parse_topic_data(self, topic_data: Dict[str, Any]) -> Optional[MediumTopic]:
        """Parse topic data"""
        try:
            created_at = datetime.fromisoformat(topic_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            topic = MediumTopic(
                topic_id=topic_data.get('id', ''),
                name=topic_data.get('name', ''),
                slug=topic_data.get('slug', ''),
                description=topic_data.get('description', ''),
                image_url='',
                follower_count=topic_data.get('follower_count', 0),
                story_count=topic_data.get('story_count', 0),
                created_at=created_at,
                is_following=topic_data.get('is_following', False),
                related_topics=topic_data.get('related_topics', []),
                trending_stories=topic_data.get('trending_stories', []),
                featured_stories=topic_data.get('featured_stories', []),
                top_writers=topic_data.get('top_writers', []),
                weekly_stats=topic_data.get('weekly_stats', {})
            )
            
            return topic
            
        except Exception as e:
            self.logger.error(f"Error parsing topic data: {str(e)}")
            return None
    
    async def _parse_response_data(self, response_data: Dict[str, Any]) -> Optional[MediumResponse]:
        """Parse response data"""
        try:
            created_at = datetime.fromisoformat(response_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            response = MediumResponse(
                response_id=response_data.get('id', ''),
                content=response_data.get('content', ''),
                author_id=response_data.get('author_id', ''),
                author_name=response_data.get('author_name', ''),
                author_username=response_data.get('author_username', ''),
                story_id=response_data.get('story_id', ''),
                parent_response_id=response_data.get('parent_response_id'),
                created_at=created_at,
                updated_at=None,
                clap_count=response_data.get('clap_count', 0),
                is_private_note=response_data.get('is_private_note', False),
                preview_content=response_data.get('preview_content', ''),
                selected_range=response_data.get('selected_range'),
                mentioned_users=response_data.get('mentioned_users', [])
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error parsing response data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Medium content"""
        try:
            # Parse Medium URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'medium',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Medium URLs
            if 'medium.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    if path_parts[0].startswith('@'):
                        # User profile: /@username
                        metadata.update({
                            'content_type': 'user',
                            'username': path_parts[0][1:]
                        })
                        
                        # Article URL: /@username/article-slug-id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'article',
                                'article_slug': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'topic':
                        # Topic URL: /topic/topic-slug
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'topic',
                                'topic_slug': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'publication':
                        # Publication URL: /publication/publication-slug
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'publication',
                                'publication_slug': path_parts[1]
                            })
                    
                    else:
                        # Custom domain publication: /article-slug-id
                        metadata.update({
                            'content_type': 'article',
                            'article_slug': path_parts[0]
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Medium metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Medium platform information"""
        return {
            'platform_name': 'Medium',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Article content tracking',
                'Author profile analysis',
                'Publication monitoring',
                'Topic trend analysis',
                'Response and engagement tracking',
                'Reading time and metrics analysis',
                'Member-only content detection',
                'SEO and metadata extraction',
                'Social sharing analysis',
                'Monetization tracking'
            ],
            'authentication': {
                'required': False,
                'type': 'API Key (Optional)',
                'scope': 'Public and private content access'
            },
            'content_characteristics': {
                'long_form_content': True,
                'professional_writing': True,
                'member_paywall': True,
                'curation_system': True
            },
            'limitations': [
                'Member-only content restrictions',
                'Limited public API',
                'Rate limiting enforced',
                'Content may be paywalled',
                'Some features require authentication'
            ]
        }
