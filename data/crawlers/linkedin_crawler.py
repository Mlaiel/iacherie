"""
LinkedIn Crawler Implementation
==============================

Professional LinkedIn content monitoring and discovery system.
Implements advanced crawling for professional content and influencer tracking.

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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class LinkedInProfile:
    """LinkedIn profile information"""
    profile_id: str
    username: str
    display_name: str
    headline: str
    location: str
    industry: str
    connections_count: int
    followers_count: int
    profile_url: str
    avatar_url: Optional[str]
    background_url: Optional[str]
    about_section: str
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[str]
    languages: List[str]
    certifications: List[Dict[str, Any]]
    volunteer_experience: List[Dict[str, Any]]
    recommendations_count: int
    profile_completeness: float
    is_premium: bool
    is_influencer: bool
    last_activity: Optional[datetime]
    engagement_rate: float
    content_themes: List[str]


@dataclass
class LinkedInPost:
    """LinkedIn post information"""
    post_id: str
    author_profile: LinkedInProfile
    content: str
    post_type: str  # article, image, video, document, poll, carousel
    publish_date: datetime
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    engagement_rate: float
    hashtags: List[str]
    mentions: List[str]
    media_urls: List[str]
    article_url: Optional[str]
    poll_data: Optional[Dict[str, Any]]
    document_title: Optional[str]
    video_duration: Optional[int]
    location: Optional[str]
    is_sponsored: bool
    company_page: Optional[str]
    industry_tags: List[str]
    content_language: str
    sentiment_score: float
    topics: List[str]


@dataclass
class LinkedInCompany:
    """LinkedIn company page information"""
    company_id: str
    name: str
    tagline: str
    description: str
    industry: str
    company_size: str
    headquarters: str
    founded_year: Optional[int]
    website: str
    phone: Optional[str]
    specialties: List[str]
    employees_count: int
    followers_count: int
    logo_url: Optional[str]
    cover_image_url: Optional[str]
    company_url: str
    recent_posts: List[LinkedInPost]
    employee_profiles: List[LinkedInProfile]
    job_openings: List[Dict[str, Any]]
    company_updates: List[Dict[str, Any]]
    is_verified: bool
    engagement_metrics: Dict[str, float]


class LinkedInCrawler(PlatformCrawler):
    """
    Professional LinkedIn crawler for content monitoring and discovery.
    
    Features:
    - Profile monitoring and analysis
    - Content discovery and engagement tracking
    - Company page monitoring
    - Job posting analysis
    - Industry trend detection
    - Influencer identification
    - Content performance analytics
    - Professional network mapping
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "linkedin"
        self.base_url = "https://www.linkedin.com"
        self.api_base_url = "https://api.linkedin.com/v2"
        
        # LinkedIn-specific configuration
        self.session_cookies = {}
        self.csrf_token = None
        self.client_page_instance_id = None
        
        # Rate limiting (LinkedIn is very strict)
        self.min_delay = 3.0
        self.max_delay = 8.0
        self.requests_per_minute = 10
        self.daily_request_limit = 500
        
        # Content type mappings
        self.content_types = {
            'profile': self._crawl_profile,
            'posts': self._crawl_posts,
            'company': self._crawl_company,
            'jobs': self._crawl_jobs,
            'articles': self._crawl_articles,
            'search': self._crawl_search
        }
        
        # Tracking
        self.daily_requests = 0
        self.last_request_time = 0
        
        # Initialize session
        asyncio.create_task(self._initialize_session())
    
    async def _initialize_session(self):
        """Initialize LinkedIn session with proper authentication"""
        try:
            # Set up session with realistic headers
            self.session_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            # Get initial page to establish session
            async with self.session.get(
                f"{self.base_url}/", 
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    # Extract session tokens
                    content = await response.text()
                    self._extract_session_tokens(content)
                    
                    self.logger.info("LinkedIn session initialized successfully")
                else:
                    self.logger.error(f"Failed to initialize LinkedIn session: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error initializing LinkedIn session: {str(e)}")
    
    def _extract_session_tokens(self, content: str):
        """Extract necessary session tokens from LinkedIn page"""
        try:
            # Extract CSRF token
            csrf_match = re.search(r'"csrfToken":"([^"]+)"', content)
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
            
            # Extract client page instance ID
            instance_match = re.search(r'"clientPageInstanceId":"([^"]+)"', content)
            if instance_match:
                self.client_page_instance_id = instance_match.group(1)
                
        except Exception as e:
            self.logger.error(f"Error extracting session tokens: {str(e)}")
    
    async def search_content(self, query: str, content_type: str = "posts", 
                           max_results: int = 50) -> List[CrawlerResult]:
        """
        Search for content on LinkedIn.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results)
            
            self.logger.info(f"Found {len(results)} LinkedIn {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching LinkedIn content: {str(e)}")
            return []
    
    async def _crawl_profile(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl LinkedIn profiles"""
        try:
            results = []
            
            # Search for profiles
            search_url = f"{self.base_url}/search/results/people/"
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER'
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    profile_urls = self._extract_profile_urls(content)
                    
                    # Crawl individual profiles
                    for profile_url in profile_urls[:max_results]:
                        profile_data = await self._get_profile_details(profile_url)
                        if profile_data:
                            result = CrawlerResult(
                                url=profile_url,
                                title=profile_data.display_name,
                                content=f"{profile_data.headline} - {profile_data.about_section}",
                                metadata={
                                    'profile_data': asdict(profile_data),
                                    'platform': 'linkedin',
                                    'content_type': 'profile',
                                    'engagement_rate': profile_data.engagement_rate,
                                    'followers_count': profile_data.followers_count,
                                    'is_influencer': profile_data.is_influencer
                                },
                                timestamp=datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling LinkedIn profiles: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl LinkedIn posts"""
        try:
            results = []
            
            # Search for posts
            search_url = f"{self.base_url}/search/results/content/"
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER'
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    post_data = self._extract_posts_from_search(content)
                    
                    for post in post_data[:max_results]:
                        # Get detailed post information
                        detailed_post = await self._get_post_details(post['post_id'])
                        if detailed_post:
                            result = CrawlerResult(
                                url=f"{self.base_url}/feed/update/{post['post_id']}",
                                title=f"Post by {detailed_post.author_profile.display_name}",
                                content=detailed_post.content,
                                metadata={
                                    'post_data': asdict(detailed_post),
                                    'platform': 'linkedin',
                                    'content_type': 'post',
                                    'engagement_rate': detailed_post.engagement_rate,
                                    'likes_count': detailed_post.likes_count,
                                    'comments_count': detailed_post.comments_count,
                                    'shares_count': detailed_post.shares_count,
                                    'hashtags': detailed_post.hashtags,
                                    'mentions': detailed_post.mentions
                                },
                                timestamp=detailed_post.publish_date,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling LinkedIn posts: {str(e)}")
            return []
    
    async def _crawl_company(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl LinkedIn company pages"""
        try:
            results = []
            
            # Search for companies
            search_url = f"{self.base_url}/search/results/companies/"
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER'
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    company_urls = self._extract_company_urls(content)
                    
                    # Crawl individual company pages
                    for company_url in company_urls[:max_results]:
                        company_data = await self._get_company_details(company_url)
                        if company_data:
                            result = CrawlerResult(
                                url=company_url,
                                title=company_data.name,
                                content=f"{company_data.tagline} - {company_data.description}",
                                metadata={
                                    'company_data': asdict(company_data),
                                    'platform': 'linkedin',
                                    'content_type': 'company',
                                    'employees_count': company_data.employees_count,
                                    'followers_count': company_data.followers_count,
                                    'industry': company_data.industry,
                                    'engagement_metrics': company_data.engagement_metrics
                                },
                                timestamp=datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling LinkedIn companies: {str(e)}")
            return []
    
    async def _crawl_jobs(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl LinkedIn job postings"""
        try:
            results = []
            
            # Search for jobs
            search_url = f"{self.base_url}/jobs/search/"
            params = {
                'keywords': query,
                'location': 'Worldwide',
                'trk': 'public_jobs_jobs-search-bar_search-submit',
                'position': 1,
                'pageNum': 0
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    job_data = self._extract_jobs_from_search(content)
                    
                    for job in job_data[:max_results]:
                        result = CrawlerResult(
                            url=job['job_url'],
                            title=job['title'],
                            content=job['description'],
                            metadata={
                                'job_data': job,
                                'platform': 'linkedin',
                                'content_type': 'job',
                                'company': job['company'],
                                'location': job['location'],
                                'employment_type': job['employment_type'],
                                'seniority_level': job['seniority_level'],
                                'industry': job['industry'],
                                'posted_date': job['posted_date']
                            },
                            timestamp=datetime.utcnow(),
                            similarity_score=0.0
                        )
                        results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling LinkedIn jobs: {str(e)}")
            return []
    
    async def _crawl_articles(self, query: str, max_results: int) -> List[CrawlerResult]:
        """Crawl LinkedIn articles"""
        try:
            results = []
            
            # Search for articles (LinkedIn Pulse)
            search_url = f"{self.base_url}/search/results/content/"
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER',
                'content': 'articles'
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    article_data = self._extract_articles_from_search(content)
                    
                    for article in article_data[:max_results]:
                        # Get full article content
                        article_content = await self._get_article_content(article['article_url'])
                        if article_content:
                            result = CrawlerResult(
                                url=article['article_url'],
                                title=article['title'],
                                content=article_content['content'],
                                metadata={
                                    'article_data': article_content,
                                    'platform': 'linkedin',
                                    'content_type': 'article',
                                    'author': article['author'],
                                    'publish_date': article['publish_date'],
                                    'reading_time': article_content.get('reading_time'),
                                    'tags': article_content.get('tags', []),
                                    'engagement_stats': article_content.get('engagement_stats', {})
                                },
                                timestamp=datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            # Rate limiting
                            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling LinkedIn articles: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int) -> List[CrawlerResult]:
        """General LinkedIn search"""
        try:
            results = []
            
            # General search
            search_url = f"{self.base_url}/search/results/all/"
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER'
            }
            
            async with self.session.get(
                search_url, 
                params=params,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract different types of content
                    all_results = []
                    all_results.extend(self._extract_posts_from_search(content))
                    all_results.extend(self._extract_profile_urls(content))
                    all_results.extend(self._extract_company_urls(content))
                    
                    for item in all_results[:max_results]:
                        result = CrawlerResult(
                            url=item.get('url', ''),
                            title=item.get('title', ''),
                            content=item.get('content', ''),
                            metadata={
                                'platform': 'linkedin',
                                'content_type': 'search_result',
                                'item_data': item
                            },
                            timestamp=datetime.utcnow(),
                            similarity_score=0.0
                        )
                        results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing LinkedIn search: {str(e)}")
            return []
    
    # Helper methods for data extraction
    
    def _extract_profile_urls(self, content: str) -> List[str]:
        """Extract profile URLs from search results"""
        try:
            profile_urls = []
            
            # Pattern for LinkedIn profile URLs
            profile_pattern = r'href="(/in/[^"]+)"'
            matches = re.findall(profile_pattern, content)
            
            for match in matches:
                full_url = urljoin(self.base_url, match)
                if full_url not in profile_urls:
                    profile_urls.append(full_url)
            
            return profile_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting profile URLs: {str(e)}")
            return []
    
    def _extract_company_urls(self, content: str) -> List[str]:
        """Extract company URLs from search results"""
        try:
            company_urls = []
            
            # Pattern for LinkedIn company URLs
            company_pattern = r'href="(/company/[^"]+)"'
            matches = re.findall(company_pattern, content)
            
            for match in matches:
                full_url = urljoin(self.base_url, match)
                if full_url not in company_urls:
                    company_urls.append(full_url)
            
            return company_urls
            
        except Exception as e:
            self.logger.error(f"Error extracting company URLs: {str(e)}")
            return []
    
    def _extract_posts_from_search(self, content: str) -> List[Dict[str, Any]]:
        """Extract post data from search results"""
        try:
            posts = []
            
            # Extract post data using regex patterns
            # This is a simplified extraction - real implementation would be more sophisticated
            post_pattern = r'"urn:li:activity:(\d+)"'
            matches = re.findall(post_pattern, content)
            
            for match in matches:
                posts.append({
                    'post_id': match,
                    'url': f"{self.base_url}/feed/update/urn:li:activity:{match}"
                })
            
            return posts
            
        except Exception as e:
            self.logger.error(f"Error extracting posts from search: {str(e)}")
            return []
    
    def _extract_jobs_from_search(self, content: str) -> List[Dict[str, Any]]:
        """Extract job data from search results"""
        try:
            jobs = []
            
            # Extract job data using regex patterns
            # This would need to be more sophisticated in real implementation
            job_pattern = r'"jobPosting":\s*{[^}]+}'
            matches = re.findall(job_pattern, content)
            
            for match in matches:
                try:
                    job_data = json.loads(match.split(':', 1)[1])
                    jobs.append({
                        'job_id': job_data.get('identifier', {}).get('value', ''),
                        'title': job_data.get('title', ''),
                        'company': job_data.get('hiringOrganization', {}).get('name', ''),
                        'location': job_data.get('jobLocation', {}).get('address', {}).get('addressLocality', ''),
                        'description': job_data.get('description', ''),
                        'employment_type': job_data.get('employmentType', ''),
                        'posted_date': job_data.get('datePosted', ''),
                        'job_url': job_data.get('url', '')
                    })
                except:
                    continue
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error extracting jobs from search: {str(e)}")
            return []
    
    def _extract_articles_from_search(self, content: str) -> List[Dict[str, Any]]:
        """Extract article data from search results"""
        try:
            articles = []
            
            # Extract article data
            article_pattern = r'"pulse/([^"]+)"'
            matches = re.findall(article_pattern, content)
            
            for match in matches:
                articles.append({
                    'article_id': match,
                    'article_url': f"{self.base_url}/pulse/{match}",
                    'title': '',  # Would extract from detailed parsing
                    'author': '',
                    'publish_date': ''
                })
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error extracting articles from search: {str(e)}")
            return []
    
    async def _get_profile_details(self, profile_url: str) -> Optional[LinkedInProfile]:
        """Get detailed profile information"""
        try:
            async with self.session.get(
                profile_url,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_profile_data(content, profile_url)
                
        except Exception as e:
            self.logger.error(f"Error getting profile details: {str(e)}")
            return None
    
    async def _get_post_details(self, post_id: str) -> Optional[LinkedInPost]:
        """Get detailed post information"""
        try:
            post_url = f"{self.base_url}/feed/update/urn:li:activity:{post_id}"
            
            async with self.session.get(
                post_url,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_post_data(content, post_id)
                
        except Exception as e:
            self.logger.error(f"Error getting post details: {str(e)}")
            return None
    
    async def _get_company_details(self, company_url: str) -> Optional[LinkedInCompany]:
        """Get detailed company information"""
        try:
            async with self.session.get(
                company_url,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_company_data(content, company_url)
                
        except Exception as e:
            self.logger.error(f"Error getting company details: {str(e)}")
            return None
    
    async def _get_article_content(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Get full article content"""
        try:
            async with self.session.get(
                article_url,
                headers=self.session_headers
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_article_data(content, article_url)
                
        except Exception as e:
            self.logger.error(f"Error getting article content: {str(e)}")
            return None
    
    def _parse_profile_data(self, content: str, profile_url: str) -> LinkedInProfile:
        """Parse profile data from HTML content"""
        try:
            # Extract profile information using regex and parsing
            # This is a simplified implementation
            
            # Extract basic profile info
            name_match = re.search(r'"name":"([^"]+)"', content)
            headline_match = re.search(r'"headline":"([^"]+)"', content)
            location_match = re.search(r'"locationName":"([^"]+)"', content)
            
            # Create profile object with extracted data
            profile = LinkedInProfile(
                profile_id=self._extract_profile_id(profile_url),
                username=self._extract_username_from_url(profile_url),
                display_name=name_match.group(1) if name_match else "",
                headline=headline_match.group(1) if headline_match else "",
                location=location_match.group(1) if location_match else "",
                industry="",
                connections_count=0,
                followers_count=0,
                profile_url=profile_url,
                avatar_url=None,
                background_url=None,
                about_section="",
                experience=[],
                education=[],
                skills=[],
                languages=[],
                certifications=[],
                volunteer_experience=[],
                recommendations_count=0,
                profile_completeness=0.0,
                is_premium=False,
                is_influencer=False,
                last_activity=None,
                engagement_rate=0.0,
                content_themes=[]
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error parsing profile data: {str(e)}")
            return None
    
    def _parse_post_data(self, content: str, post_id: str) -> LinkedInPost:
        """Parse post data from HTML content"""
        try:
            # Simplified post parsing
            # Real implementation would be much more sophisticated
            
            post = LinkedInPost(
                post_id=post_id,
                author_profile=None,  # Would extract author profile
                content="",
                post_type="text",
                publish_date=datetime.utcnow(),
                likes_count=0,
                comments_count=0,
                shares_count=0,
                views_count=0,
                engagement_rate=0.0,
                hashtags=[],
                mentions=[],
                media_urls=[],
                article_url=None,
                poll_data=None,
                document_title=None,
                video_duration=None,
                location=None,
                is_sponsored=False,
                company_page=None,
                industry_tags=[],
                content_language="en",
                sentiment_score=0.0,
                topics=[]
            )
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    def _parse_company_data(self, content: str, company_url: str) -> LinkedInCompany:
        """Parse company data from HTML content"""
        try:
            # Simplified company parsing
            
            company = LinkedInCompany(
                company_id=self._extract_company_id(company_url),
                name="",
                tagline="",
                description="",
                industry="",
                company_size="",
                headquarters="",
                founded_year=None,
                website="",
                phone=None,
                specialties=[],
                employees_count=0,
                followers_count=0,
                logo_url=None,
                cover_image_url=None,
                company_url=company_url,
                recent_posts=[],
                employee_profiles=[],
                job_openings=[],
                company_updates=[],
                is_verified=False,
                engagement_metrics={}
            )
            
            return company
            
        except Exception as e:
            self.logger.error(f"Error parsing company data: {str(e)}")
            return None
    
    def _parse_article_data(self, content: str, article_url: str) -> Dict[str, Any]:
        """Parse article data from HTML content"""
        try:
            # Simplified article parsing
            return {
                'content': '',
                'reading_time': 0,
                'tags': [],
                'engagement_stats': {}
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing article data: {str(e)}")
            return {}
    
    def _extract_profile_id(self, profile_url: str) -> str:
        """Extract profile ID from URL"""
        try:
            # Extract from URL pattern
            match = re.search(r'/in/([^/?]+)', profile_url)
            return match.group(1) if match else ""
        except:
            return ""
    
    def _extract_company_id(self, company_url: str) -> str:
        """Extract company ID from URL"""
        try:
            match = re.search(r'/company/([^/?]+)', company_url)
            return match.group(1) if match else ""
        except:
            return ""
    
    def _extract_username_from_url(self, profile_url: str) -> str:
        """Extract username from profile URL"""
        try:
            match = re.search(r'/in/([^/?]+)', profile_url)
            return match.group(1) if match else ""
        except:
            return ""
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            
            # Check daily limit
            if self.daily_requests >= self.daily_request_limit:
                raise Exception("Daily request limit exceeded")
            
            # Check time-based rate limiting
            time_since_last = current_time - self.last_request_time
            min_interval = 60.0 / self.requests_per_minute
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request_time = current_time
            self.daily_requests += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
            raise
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from LinkedIn content"""
        try:
            # Determine content type from URL
            if '/in/' in url:
                content_type = 'profile'
            elif '/company/' in url:
                content_type = 'company'
            elif '/pulse/' in url:
                content_type = 'article'
            elif '/jobs/' in url:
                content_type = 'job'
            else:
                content_type = 'unknown'
            
            metadata = {
                'platform': 'linkedin',
                'content_type': content_type,
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Get content-specific metadata
            if content_type == 'profile':
                profile_data = await self._get_profile_details(url)
                if profile_data:
                    metadata.update(asdict(profile_data))
            
            elif content_type == 'company':
                company_data = await self._get_company_details(url)
                if company_data:
                    metadata.update(asdict(company_data))
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting LinkedIn metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get LinkedIn platform information"""
        return {
            'platform_name': 'LinkedIn',
            'base_url': self.base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'daily_request_limit': self.daily_request_limit,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Profile monitoring',
                'Content discovery',
                'Company page analysis',
                'Job posting tracking',
                'Article crawling',
                'Professional network mapping',
                'Industry trend detection',
                'Influencer identification'
            ],
            'limitations': [
                'Requires authentication for detailed data',
                'Strict rate limiting',
                'Anti-bot measures',
                'Limited API access without premium'
            ]
        }
