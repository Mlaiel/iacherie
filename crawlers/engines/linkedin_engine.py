"""
LinkedIn Crawling Engine
=======================

Advanced LinkedIn crawler for professional content discovery and business intelligence.
Handles posts, profiles, companies, and job data extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.

🏗️ Architecture Enterprise - Équipe Projet Spécialisée :
• Lead Developer IA : Fahed Mlaiel (mlaiel@live.de)
• Backend Senior Engineer : Architecture microservices & APIs
• ML/AI Engineer : Intelligence artificielle & algorithmes avancés
• Database Administrator : Optimisation données & performance
• Security Expert : Cybersécurité & protection contenu
• DevOps Engineer : Infrastructure cloud & déploiement
• Audio/Video Specialist : Traitement multimédia avancé
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time
from urllib.parse import urljoin, urlparse, quote

import aiohttp
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from linkedin_api import Linkedin
import pyautogui

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    PrivacyRestrictedError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import ProfessionalPost, ProfessionalProfile, BusinessProfile
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class LinkedInPostData:
    """LinkedIn post data structure"""
    post_id: str
    author_id: str
    author_name: str
    author_title: str
    author_company: str
    content: str
    published_at: datetime
    post_type: str  # article, status, image, video, document
    industry: str
    location: str
    likes: int
    comments: int
    shares: int
    reposts: int
    views: int
    engagement_rate: float
    hashtags: List[str]
    mentions: List[str]
    attachments: List[Dict[str, Any]]
    article_url: Optional[str] = None
    company_page: Optional[str] = None
    is_sponsored: bool = False
    targeting: Dict[str, Any] = None
    insights: Dict[str, Any] = None


@dataclass
class LinkedInProfileData:
    """LinkedIn profile data structure"""
    profile_id: str
    public_id: str
    first_name: str
    last_name: str
    headline: str
    summary: str
    location: str
    industry: str
    current_company: str
    current_position: str
    connections: int
    followers: int
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    endorsements: Dict[str, int]
    recommendations: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    publications: List[Dict[str, Any]]
    patents: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    volunteer_experience: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    honors_awards: List[Dict[str, Any]]
    profile_picture: str
    background_image: str
    contact_info: Dict[str, Any]
    activity_posts: List[LinkedInPostData] = None
    is_premium: bool = False
    is_verified: bool = False
    open_to_work: bool = False
    hiring: bool = False


@dataclass
class LinkedInCompanyData:
    """LinkedIn company data structure"""
    company_id: str
    universal_name: str
    name: str
    description: str
    website: str
    industry: str
    company_size: str
    company_type: str
    headquarters: Dict[str, Any]
    founded: int
    specialties: List[str]
    employees: int
    followers: int
    logo: str
    cover_image: str
    locations: List[Dict[str, Any]]
    affiliated_companies: List[Dict[str, Any]]
    updates: List[LinkedInPostData] = None
    jobs: List[Dict[str, Any]] = None
    insights: Dict[str, Any] = None
    is_verified: bool = False
    employee_stats: Dict[str, Any] = None


@dataclass
class LinkedInBusinessData:
    """LinkedIn business analytics data structure"""
    page_id: str
    page_name: str
    follower_count: int
    follower_demographics: Dict[str, Any]
    page_views: Dict[str, Any]
    post_analytics: List[Dict[str, Any]]
    visitor_analytics: Dict[str, Any]
    employee_advocacy: Dict[str, Any]
    competitor_analysis: Dict[str, Any]
    content_suggestions: List[Dict[str, Any]]
    trending_content: List[Dict[str, Any]]
    industry_insights: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    reach_metrics: Dict[str, Any]
    conversion_metrics: Dict[str, Any]


class LinkedInCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced LinkedIn crawler engine with professional networking focus.
    
    Features:
    - Official LinkedIn API integration
    - Selenium automation for extended data
    - Professional network analysis
    - Business intelligence gathering
    - Recruitment data mining
    - Industry trend analysis
    - Lead generation capabilities
    - Privacy-compliant data collection
    """

    def __init__(self, 
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 access_token: Optional[str] = None,
                 use_selenium: bool = True,
                 headless: bool = True,
                 proxy_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None):
        """
        Initialize LinkedIn crawler engine.
        
        Args:
            username: LinkedIn username/email
            password: LinkedIn password
            access_token: LinkedIn API access token
            use_selenium: Whether to use Selenium for scraping
            headless: Run browser in headless mode
            proxy_config: Proxy configuration
            rate_limit_config: Rate limiting configuration
        """
        super().__init__()
        
        # Authentication
        self.username = username or settings.LINKEDIN_USERNAME
        self.password = password or settings.LINKEDIN_PASSWORD
        self.access_token = access_token or settings.LINKEDIN_ACCESS_TOKEN
        
        # LinkedIn API client
        self.api_client = None
        if self.username and self.password:
            try:
                self.api_client = Linkedin(self.username, self.password)
            except Exception as e:
                logger.warning(f"Failed to initialize LinkedIn API client: {e}")
        
        # Selenium setup
        self.use_selenium = use_selenium
        self.headless = headless
        self.driver = None
        
        # Rate limiting (LinkedIn is very strict)
        rate_config = rate_limit_config or {
            'requests_per_hour': 100,  # Very conservative
            'requests_per_day': 1000,
            'burst_limit': 20,
            'delay_between_requests': 3
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=7200,  # 2 hour cache
            key_prefix='linkedin_'
        )
        
        # Proxy manager
        if proxy_config:
            self.proxy_manager = ProxyManager(proxy_config)
        else:
            self.proxy_manager = None

    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn"""
        try:
            if self.api_client:
                # Test API access
                profile = self.api_client.get_profile('me')
                logger.info(f"Authenticated LinkedIn user: {profile.get('firstName', '')} {profile.get('lastName', '')}")
                return True
            
            if self.use_selenium and self.username and self.password:
                await self._setup_selenium_driver()
                success = await self._selenium_login()
                if success:
                    logger.info("LinkedIn Selenium authentication successful")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            return False

    async def search_profiles(self, 
                            query: str,
                            filters: Optional[Dict] = None,
                            limit: int = 100) -> List[LinkedInProfileData]:
        """
        Search for LinkedIn profiles.
        
        Args:
            query: Search query (keywords, company, title)
            filters: Search filters (location, industry, current_company, etc.)
            limit: Maximum number of profiles to return
        
        Returns:
            List of LinkedInProfileData objects
        """
        cache_key = f"search_profiles_{hashlib.md5(query.encode()).hexdigest()}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [LinkedInProfileData(**profile) for profile in cached_result]

        profiles = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.api_client:
                # Use official API
                search_results = self.api_client.search_people(
                    keywords=query,
                    limit=limit,
                    **filters or {}
                )
                
                for result in search_results:
                    profile = await self._process_profile_data(result)
                    if profile:
                        profiles.append(profile)
            
            else:
                # Use Selenium for broader search
                profiles = await self._selenium_search_profiles(query, filters, limit)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(profile) for profile in profiles]
            )
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn profiles: {e}")
            raise CrawlerError(f"LinkedIn profile search failed: {e}")
        
        return profiles

    async def get_profile_details(self, profile_id: str) -> LinkedInProfileData:
        """
        Get detailed LinkedIn profile information.
        
        Args:
            profile_id: LinkedIn profile ID or public identifier
        
        Returns:
            LinkedInProfileData object
        """
        cache_key = f"profile_details_{profile_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return LinkedInProfileData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            if self.api_client:
                # Get comprehensive profile data
                profile_data = self.api_client.get_profile(profile_id)
                contact_info = self.api_client.get_profile_contact_info(profile_id)
                
                profile = LinkedInProfileData(
                    profile_id=profile_data.get('public_id', profile_id),
                    public_id=profile_data.get('public_id', ''),
                    first_name=profile_data.get('firstName', ''),
                    last_name=profile_data.get('lastName', ''),
                    headline=profile_data.get('headline', ''),
                    summary=profile_data.get('summary', ''),
                    location=profile_data.get('geoLocationName', ''),
                    industry=profile_data.get('industryName', ''),
                    current_company='',
                    current_position='',
                    connections=profile_data.get('numConnections', 0),
                    followers=profile_data.get('numFollowers', 0),
                    experience=profile_data.get('experience', []),
                    education=profile_data.get('education', []),
                    skills=profile_data.get('skills', []),
                    endorsements={},
                    recommendations=[],
                    certifications=profile_data.get('certifications', []),
                    publications=profile_data.get('publications', []),
                    patents=profile_data.get('patents', []),
                    projects=profile_data.get('projects', []),
                    volunteer_experience=profile_data.get('volunteer', []),
                    languages=profile_data.get('languages', []),
                    honors_awards=profile_data.get('honors', []),
                    profile_picture=profile_data.get('profile_pic_url', ''),
                    background_image=profile_data.get('background_pic_url', ''),
                    contact_info=contact_info or {},
                    is_premium=profile_data.get('premium', False),
                    is_verified=profile_data.get('verified', False)
                )
                
                # Extract current position and company
                if profile.experience:
                    current = profile.experience[0]
                    profile.current_position = current.get('title', '')
                    profile.current_company = current.get('companyName', '')
                
                # Cache result
                await self.cache_manager.set(cache_key, asdict(profile))
                
                return profile
            
            else:
                raise AuthenticationError("LinkedIn API client not available")
        
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile details: {e}")
            raise CrawlerError(f"LinkedIn profile details retrieval failed: {e}")

    async def get_company_info(self, company_id: str) -> LinkedInCompanyData:
        """
        Get LinkedIn company information.
        
        Args:
            company_id: LinkedIn company ID or universal name
        
        Returns:
            LinkedInCompanyData object
        """
        cache_key = f"company_info_{company_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return LinkedInCompanyData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            if self.api_client:
                company_data = self.api_client.get_company(company_id)
                
                company = LinkedInCompanyData(
                    company_id=str(company_data.get('id', company_id)),
                    universal_name=company_data.get('universalName', ''),
                    name=company_data.get('name', ''),
                    description=company_data.get('description', ''),
                    website=company_data.get('website', ''),
                    industry=company_data.get('industry', ''),
                    company_size=company_data.get('companySize', ''),
                    company_type=company_data.get('companyType', ''),
                    headquarters=company_data.get('headquarters', {}),
                    founded=company_data.get('founded', 0),
                    specialties=company_data.get('specialties', []),
                    employees=company_data.get('employeeCountRange', {}).get('end', 0),
                    followers=company_data.get('followerCount', 0),
                    logo=company_data.get('logo', ''),
                    cover_image=company_data.get('coverPhoto', ''),
                    locations=company_data.get('locations', []),
                    affiliated_companies=company_data.get('affiliatedCompanies', []),
                    is_verified=company_data.get('verified', False)
                )
                
                # Cache result
                await self.cache_manager.set(cache_key, asdict(company))
                
                return company
            
            else:
                raise AuthenticationError("LinkedIn API client not available")
        
        except Exception as e:
            logger.error(f"Error getting LinkedIn company info: {e}")
            raise CrawlerError(f"LinkedIn company info retrieval failed: {e}")

    async def get_company_posts(self, 
                              company_id: str, 
                              limit: int = 50) -> List[LinkedInPostData]:
        """
        Get posts from a LinkedIn company page.
        
        Args:
            company_id: LinkedIn company ID
            limit: Maximum number of posts to return
        
        Returns:
            List of LinkedInPostData objects
        """
        cache_key = f"company_posts_{company_id}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [LinkedInPostData(**post) for post in cached_result]

        posts = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.api_client:
                company_updates = self.api_client.get_company_updates(
                    company_id, 
                    max_results=limit
                )
                
                for update in company_updates:
                    post = await self._process_post_data(update)
                    if post:
                        posts.append(post)
                
                # Cache results
                await self.cache_manager.set(
                    cache_key, 
                    [asdict(post) for post in posts]
                )
            
            else:
                raise AuthenticationError("LinkedIn API client not available")
        
        except Exception as e:
            logger.error(f"Error getting LinkedIn company posts: {e}")
            raise CrawlerError(f"LinkedIn company posts retrieval failed: {e}")
        
        return posts

    async def search_jobs(self, 
                         keywords: str,
                         location: Optional[str] = None,
                         company: Optional[str] = None,
                         experience_level: Optional[str] = None,
                         job_type: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn job postings.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            company: Company filter
            experience_level: Experience level (entry, mid, senior, executive)
            job_type: Job type (full-time, part-time, contract, etc.)
            limit: Maximum number of jobs to return
        
        Returns:
            List of job posting dictionaries
        """
        cache_key = f"search_jobs_{hashlib.md5(keywords.encode()).hexdigest()}_{location}_{limit}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        jobs = []
        
        try:
            await self.rate_limiter.acquire()
            
            if self.api_client:
                search_params = {
                    'keywords': keywords,
                    'limit': limit
                }
                
                if location:
                    search_params['location_name'] = location
                if company:
                    search_params['company'] = company
                if experience_level:
                    search_params['experience'] = experience_level
                if job_type:
                    search_params['job_type'] = job_type
                
                job_results = self.api_client.search_jobs(**search_params)
                
                for job in job_results:
                    jobs.append({
                        'job_id': job.get('dashEntityUrn', ''),
                        'title': job.get('title', ''),
                        'company': job.get('companyDetails', {}).get('company', {}).get('name', ''),
                        'location': job.get('formattedLocation', ''),
                        'description': job.get('description', {}).get('text', ''),
                        'posted_date': job.get('listedAt', ''),
                        'application_url': job.get('applyMethod', {}).get('companyApplyUrl', ''),
                        'employment_type': job.get('employmentStatus', ''),
                        'seniority_level': job.get('seniorityLevel', ''),
                        'industries': job.get('industries', []),
                        'skills': job.get('skillMatchStatuses', [])
                    })
                
                # Cache results
                await self.cache_manager.set(cache_key, jobs)
            
            else:
                raise AuthenticationError("LinkedIn API client not available")
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
            raise CrawlerError(f"LinkedIn job search failed: {e}")
        
        return jobs

    async def monitor_professional_content(self, 
                                         targets: List[str],
                                         keywords: List[str],
                                         check_interval: int = 600) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor LinkedIn content for professional insights.
        
        Args:
            targets: List of profile IDs or company IDs to monitor
            keywords: Keywords to search for
            check_interval: Check interval in seconds (LinkedIn requires longer intervals)
        
        Yields:
            Dictionary containing monitoring results
        """
        logger.info(f"Starting LinkedIn professional content monitoring for {len(targets)} targets")
        
        while True:
            for target in targets:
                try:
                    # Determine if target is profile or company
                    if target.startswith('company_'):
                        company_id = target.replace('company_', '')
                        posts = await self.get_company_posts(company_id, limit=20)
                    else:
                        # Monitor profile posts would require additional API calls
                        continue
                    
                    for post in posts:
                        content = post.content.lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                yield {
                                    'type': 'professional_content_match',
                                    'platform': 'linkedin',
                                    'target': target,
                                    'post_id': post.post_id,
                                    'keyword': keyword,
                                    'content': content[:500],
                                    'author': post.author_name,
                                    'company': post.author_company,
                                    'engagement': {
                                        'likes': post.likes,
                                        'comments': post.comments,
                                        'shares': post.shares
                                    },
                                    'timestamp': datetime.now()
                                }
                
                except Exception as e:
                    logger.error(f"Error monitoring LinkedIn target {target}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'linkedin',
                        'target': target,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def _setup_selenium_driver(self):
        """Setup Selenium WebDriver for LinkedIn"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to appear more human-like
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    async def _selenium_login(self) -> bool:
        """Login to LinkedIn using Selenium"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            await asyncio.sleep(2)
            
            # Find and fill username
            username_field = self.driver.find_element(By.ID, 'username')
            username_field.send_keys(self.username)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            
            # Wait for login to complete
            await asyncio.sleep(5)
            
            # Check if we're on the feed page (successful login)
            current_url = self.driver.current_url
            if 'feed' in current_url or 'in/' in current_url:
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Selenium LinkedIn login failed: {e}")
            return False

    async def _selenium_search_profiles(self, 
                                      query: str, 
                                      filters: Optional[Dict],
                                      limit: int) -> List[LinkedInProfileData]:
        """Search profiles using Selenium"""
        # This would implement Selenium-based profile searching
        # Note: This requires careful implementation to avoid detection
        logger.warning("Selenium profile search requires careful anti-detection measures")
        return []

    async def _process_profile_data(self, profile_data: Dict[str, Any]) -> Optional[LinkedInProfileData]:
        """Process raw LinkedIn profile data"""
        try:
            return LinkedInProfileData(
                profile_id=profile_data.get('public_id', ''),
                public_id=profile_data.get('public_id', ''),
                first_name=profile_data.get('firstName', ''),
                last_name=profile_data.get('lastName', ''),
                headline=profile_data.get('headline', ''),
                summary=profile_data.get('summary', ''),
                location=profile_data.get('geoLocationName', ''),
                industry=profile_data.get('industryName', ''),
                current_company='',
                current_position='',
                connections=profile_data.get('numConnections', 0),
                followers=0,
                experience=[],
                education=[],
                skills=[],
                endorsements={},
                recommendations=[],
                certifications=[],
                publications=[],
                patents=[],
                projects=[],
                volunteer_experience=[],
                languages=[],
                honors_awards=[],
                profile_picture=profile_data.get('profile_pic_url', ''),
                background_image='',
                contact_info={}
            )
        
        except Exception as e:
            logger.error(f"Error processing LinkedIn profile data: {e}")
            return None

    async def _process_post_data(self, post_data: Dict[str, Any]) -> Optional[LinkedInPostData]:
        """Process raw LinkedIn post data"""
        try:
            content = post_data.get('commentary', {}).get('text', '')
            hashtags = re.findall(r'#(\w+)', content)
            mentions = re.findall(r'@(\w+)', content)
            
            return LinkedInPostData(
                post_id=post_data.get('id', ''),
                author_id=post_data.get('actor', {}).get('id', ''),
                author_name=post_data.get('actor', {}).get('name', ''),
                author_title='',
                author_company='',
                content=content,
                published_at=datetime.fromtimestamp(
                    post_data.get('createdAt', 0) / 1000
                ),
                post_type=post_data.get('type', ''),
                industry='',
                location='',
                likes=post_data.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numLikes', 0),
                comments=post_data.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numComments', 0),
                shares=post_data.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numShares', 0),
                reposts=0,
                views=post_data.get('socialDetail', {}).get('totalSocialActivityCounts', {}).get('numViews', 0),
                engagement_rate=0.0,
                hashtags=hashtags,
                mentions=mentions,
                attachments=[]
            )
        
        except Exception as e:
            logger.error(f"Error processing LinkedIn post data: {e}")
            return None

    def __del__(self):
        """Cleanup resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
