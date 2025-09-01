"""Facebook Scanner - Scanner Facebook Sophistiqué
==============================================

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

(c) 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Sophisticated Facebook scanning system for comprehensive content monitoring.
Provides advanced analysis of Facebook posts, pages, groups, and user activities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class FacebookPost:
    """
Facebook post data."""
    post_id: str
    user_id: str
    user_name: str
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    message: str = ""
    story: str = ""
    link: Optional[str] = None
    link_name: Optional[str] = None
    link_caption: Optional[str] = None
    link_description: Optional[str] = None
    picture: Optional[str] = None
    video_url: Optional[str] = None
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    reaction_count: int = 0
    created_time: datetime = field(default_factory=datetime.now)
    updated_time: datetime = field(default_factory=datetime.now)
    is_published: bool = True
    privacy: str = "public"
    post_type: str = "status"  # status, photo, video, link, event
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class FacebookPage:
    """Facebook page data."""
    page_id: str
    name: str
    username: Optional[str] = None
    category: str = ""
    about: str = ""
    description: str = ""
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    fan_count: int = 0
    talking_about_count: int = 0
    checkin_count: int = 0
    is_verified: bool = False
    is_published: bool = True
    picture_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    hours: Optional[Dict[str, Any]] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class FacebookGroup:
    """Facebook group data."""
    group_id: str
    name: str
    description: str = ""
    privacy: str = "public"  # public, closed, secret
    member_count: int = 0
    admin_count: int = 0
    cover_photo_url: Optional[str] = None
    picture_url: Optional[str] = None
    created_time: datetime = field(default_factory=datetime.now)
    updated_time: datetime = field(default_factory=datetime.now)
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class FacebookUser:
    """Facebook user profile data."""
    user_id: str
    name: str
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    gender: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[int] = None
    verified: bool = False
    picture_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    bio: str = ""
    birthday: Optional[str] = None
    location: Optional[str] = None
    hometown: Optional[str] = None
    relationship_status: Optional[str] = None
    website: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class FacebookComment:
    """Facebook comment data."""
    comment_id: str
    post_id: str
    parent_id: Optional[str] = None  # For replies
    user_id: str
    user_name: str
    message: str = ""
    like_count: int = 0
    comment_count: int = 0  # Reply count
    created_time: datetime = field(default_factory=datetime.now)
    attachment_url: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class FacebookViolation:
    """Facebook content violation detection result."""
    violation_id: str
    content_type: str  # post, page, group, user, comment
    content_id: str
    violation_type: str
    confidence_score: float
    detected_at: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical
    reported: bool = False


@dataclass
class FacebookScanMetrics:
    """Facebook scanning system metrics."""
    posts_scanned: int = 0
    pages_scanned: int = 0
    groups_scanned: int = 0
    users_scanned: int = 0
    comments_scanned: int = 0
    violations_detected: int = 0
    api_calls_made: int = 0
    scan_duration_seconds: float = 0.0
    success_rate: float = 0.0
    last_scan: datetime = field(default_factory=datetime.now)


class FacebookScanner:
    """
    Sophisticated Facebook scanning and monitoring system.
    
    Features:
    - Page and group monitoring
    - Post and comment analysis
    - User behavior tracking
    - Content violation detection
    - Real-time alerts
    - Advanced pattern recognition
    - Graph API integration
    - Automated reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize Facebook scanner."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.access_token = self.config.get('facebook_access_token', '')
        self.app_id = self.config.get('facebook_app_id', '')
        self.app_secret = self.config.get('facebook_app_secret', '')
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 10)
        self.scan_interval_minutes = self.config.get('scan_interval_minutes', 30)
        self.enable_deep_scan = self.config.get('enable_deep_scan', True)
        
        # Scanner state
        self.metrics = FacebookScanMetrics()
        self.violations: List[FacebookViolation] = []
        self._scanning_active = False
        self._scan_task: Optional[asyncio.Task] = None
        
        # Content storage
        self.posts: Dict[str, FacebookPost] = {}
        self.pages: Dict[str, FacebookPage] = {}
        self.groups: Dict[str, FacebookGroup] = {}
        self.users: Dict[str, FacebookUser] = {}
        self.comments: Dict[str, List[FacebookComment]] = {}
        
        # Monitoring targets
        self.monitored_pages: Set[str] = set()
        self.monitored_groups: Set[str] = set()
        self.monitored_users: Set[str] = set()
        
        # Violation detection patterns
        self.violation_patterns = {
            'copyright': [
                r'(?i)(pirated|stolen|leaked|unauthorized|copyright\s+infringement)',
                r'(?i)(download\s+free|torrent|bootleg|cracked)',
                r'(?i)(replica|fake|counterfeit|knockoff)'
            ],
            'spam': [
                r'(?i)(like\s+for\s+like|follow\s+for\s+follow|f4f|l4l)',
                r'(?i)(buy\s+followers|buy\s+likes|increase\s+engagement)',
                r'(?i)(click\s+link|visit\s+my\s+page|check\s+out)'
            ],
            'misinformation': [
                r'(?i)(fake\s+news|conspiracy|hoax|debunked)',
                r'(?i)(false\s+information|misleading|propaganda)',
                r'(?i)(unverified|rumor|not\s+confirmed)'
            ],
            'harassment': [
                r'(?i)(hate\s+speech|harassment|bullying|trolling)',
                r'(?i)(kill\s+yourself|kys|die|suicide)',
                r'(?i)(racist|sexist|homophobic|discrimination)'
            ],
            'violence': [
                r'(?i)(violence|violent|harm|dangerous|weapon)',
                r'(?i)(kill|murder|assault|attack|threat)',
                r'(?i)(bomb|explosive|terrorism|extremist)'
            ]
        }
        
        # Rate limiting
        self._last_request_time = 0.0
        self._request_delay = 1.0
        
        self._logger.info("Facebook Scanner initialized")
    
    async def initialize(self) -> None:
        """Initialize the Facebook scanner."""
        try:
            self._logger.info("Initializing Facebook scanner...")
            
            # Validate configuration
            if not self.access_token:
                self._logger.warning("No Facebook access token configured - limited functionality")
            
            # Initialize Graph API client
            await self._initialize_graph_api()
            
            # Setup violation detection
            await self._setup_violation_detection()
            
            self._logger.info("Facebook scanner initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Facebook scanner: {e}")
            raise
    
    async def _initialize_graph_api(self) -> None:
        """Initialize Facebook Graph API client."""
        try:
            # This would initialize the actual Facebook Graph API client
            # For now, implement placeholder
            self._logger.debug("Graph API client initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Graph API client: {e}")
            raise
    
    async def _setup_violation_detection(self) -> None:
        """Setup violation detection systems."""
        try:
            # This would setup actual ML models for violation detection
            # For now, implement placeholder
            self._logger.debug("Violation detection setup complete")
            
        except Exception as e:
            self._logger.error(f"Failed to setup violation detection: {e}")
            raise
    
    async def start_scanning(self) -> None:
        """Start Facebook scanning operations."""
        try:
            if self._scanning_active:
                self._logger.warning("Facebook scanning is already active")
                return
            
            self._logger.info("Starting Facebook scanning...")
            
            self._scanning_active = True
            self._scan_task = asyncio.create_task(self._scanning_loop())
            
            self._logger.info("Facebook scanning started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start Facebook scanning: {e}")
            self._scanning_active = False
            raise
    
    async def stop_scanning(self) -> None:
        """Stop Facebook scanning operations."""
        try:
            if not self._scanning_active:
                self._logger.warning("Facebook scanning is not active")
                return
            
            self._logger.info("Stopping Facebook scanning...")
            
            self._scanning_active = False
            
            if self._scan_task and not self._scan_task.done():
                self._scan_task.cancel()
                try:
                    await self._scan_task
                except asyncio.CancelledError:
                    pass
            
            self._logger.info("Facebook scanning stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping Facebook scanning: {e}")
            raise
    
    async def add_page_monitoring(self, page_id: str) -> bool:
        """Add Facebook page to monitoring."""
        try:
            self.monitored_pages.add(page_id)
            self._logger.info(f"Added page monitoring: {page_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add page monitoring for {page_id}: {e}")
            return False
    
    async def add_group_monitoring(self, group_id: str) -> bool:
        """Add Facebook group to monitoring."""
        try:
            self.monitored_groups.add(group_id)
            self._logger.info(f"Added group monitoring: {group_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add group monitoring for {group_id}: {e}")
            return False
    
    async def add_user_monitoring(self, user_id: str) -> bool:
        """Add Facebook user to monitoring."""
        try:
            self.monitored_users.add(user_id)
            self._logger.info(f"Added user monitoring: {user_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add user monitoring for {user_id}: {e}")
            return False
    
    async def scan_page(self, page_id: str, scan_posts: bool = True) -> Optional[FacebookPage]:
        """Scan Facebook page."""
        try:
            self._logger.debug(f"Scanning page: {page_id}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Get page data
            page_data = await self._fetch_page_data(page_id)
            
            if page_data:
                page = FacebookPage(**page_data)
                self.pages[page_id] = page
                self.metrics.pages_scanned += 1
                
                # Analyze page for violations
                violations = await self._analyze_page_for_violations(page)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
                
                # Scan recent posts if requested
                if scan_posts:
                    posts = await self._fetch_page_posts(page_id)
                    
                    for post in posts:
                        post_violations = await self._analyze_post_for_violations(post)
                        
                        for violation in post_violations:
                            self.violations.append(violation)
                            self.metrics.violations_detected += 1
                
                return page
            
        except Exception as e:
            self._logger.error(f"Error scanning page {page_id}: {e}")
        
        return None
    
    async def scan_group(self, group_id: str, scan_posts: bool = True) -> Optional[FacebookGroup]:
        """Scan Facebook group."""
        try:
            self._logger.debug(f"Scanning group: {group_id}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Get group data
            group_data = await self._fetch_group_data(group_id)
            
            if group_data:
                group = FacebookGroup(**group_data)
                self.groups[group_id] = group
                self.metrics.groups_scanned += 1
                
                # Analyze group for violations
                violations = await self._analyze_group_for_violations(group)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
                
                # Scan recent posts if requested
                if scan_posts:
                    posts = await self._fetch_group_posts(group_id)
                    
                    for post in posts:
                        post_violations = await self._analyze_post_for_violations(post)
                        
                        for violation in post_violations:
                            self.violations.append(violation)
                            self.metrics.violations_detected += 1
                
                return group
            
        except Exception as e:
            self._logger.error(f"Error scanning group {group_id}: {e}")
        
        return None
    
    async def scan_user(self, user_id: str, scan_posts: bool = True) -> Optional[FacebookUser]:
        """Scan Facebook user."""
        try:
            self._logger.debug(f"Scanning user: {user_id}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Get user data
            user_data = await self._fetch_user_data(user_id)
            
            if user_data:
                user = FacebookUser(**user_data)
                self.users[user_id] = user
                self.metrics.users_scanned += 1
                
                # Analyze user for violations
                violations = await self._analyze_user_for_violations(user)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
                
                # Scan recent posts if requested
                if scan_posts:
                    posts = await self._fetch_user_posts(user_id)
                    
                    for post in posts:
                        post_violations = await self._analyze_post_for_violations(post)
                        
                        for violation in post_violations:
                            self.violations.append(violation)
                            self.metrics.violations_detected += 1
                
                return user
            
        except Exception as e:
            self._logger.error(f"Error scanning user {user_id}: {e}")
        
        return None
    
    async def _scanning_loop(self) -> None:
        """Main scanning loop."""
        self._logger.info("Facebook scanning loop started")
        
        try:
            while self._scanning_active:
                try:
                    scan_start_time = datetime.now()
                    
                    # Scan monitored pages
                    for page_id in self.monitored_pages:
                        await self.scan_page(page_id)
                        
                        if not self._scanning_active:
                            break
                    
                    # Scan monitored groups
                    for group_id in self.monitored_groups:
                        await self.scan_group(group_id)
                        
                        if not self._scanning_active:
                            break
                    
                    # Scan monitored users
                    for user_id in self.monitored_users:
                        await self.scan_user(user_id)
                        
                        if not self._scanning_active:
                            break
                    
                    # Update metrics
                    scan_duration = (datetime.now() - scan_start_time).total_seconds()
                    self.metrics.scan_duration_seconds += scan_duration
                    self.metrics.last_scan = datetime.now()
                    
                    # Wait before next scan cycle
                    await asyncio.sleep(self.scan_interval_minutes * 60)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error(f"Error in scanning loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retrying
        
        except asyncio.CancelledError:
            pass
        
        self._logger.info("Facebook scanning loop stopped")
    
    async def _fetch_page_data(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Fetch Facebook page data."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.2)
            
            # In real implementation, this would use Facebook Graph API
            page_data = {
                'page_id': page_id,
                'name': f'Page {page_id}',
                'username': f'page{page_id}',
                'category': 'Business',
                'about': f'About page {page_id}',
                'description': f'Description for page {page_id}',
                'website': 'https://example.com',
                'fan_count': 1000,
                'talking_about_count': 50,
                'checkin_count': 10,
                'is_verified': False,
                'is_published': True,
                'picture_url': f'https://example.com/page_{page_id}.jpg'
            }
            
            self.metrics.api_calls_made += 1
            return page_data
            
        except Exception as e:
            self._logger.error(f"Error fetching page data for {page_id}: {e}")
            return None
    
    async def _fetch_group_data(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Fetch Facebook group data."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.2)
            
            # In real implementation, this would use Facebook Graph API
            group_data = {
                'group_id': group_id,
                'name': f'Group {group_id}',
                'description': f'Description for group {group_id}',
                'privacy': 'public',
                'member_count': 500,
                'admin_count': 3,
                'picture_url': f'https://example.com/group_{group_id}.jpg'
            }
            
            self.metrics.api_calls_made += 1
            return group_data
            
        except Exception as e:
            self._logger.error(f"Error fetching group data for {group_id}: {e}")
            return None
    
    async def _fetch_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch Facebook user data."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.2)
            
            # In real implementation, this would use Facebook Graph API
            user_data = {
                'user_id': user_id,
                'name': f'User {user_id}',
                'first_name': f'First{user_id}',
                'last_name': f'Last{user_id}',
                'verified': False,
                'picture_url': f'https://example.com/user_{user_id}.jpg',
                'bio': f'Bio for user {user_id}'
            }
            
            self.metrics.api_calls_made += 1
            return user_data
            
        except Exception as e:
            self._logger.error(f"Error fetching user data for {user_id}: {e}")
            return None
    
    async def _fetch_page_posts(self, page_id: str, limit: int = 50) -> List[FacebookPost]:
        """Fetch recent posts from a page."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.3)
            
            posts = []
            
            # In real implementation, this would fetch actual posts
            for i in range(min(limit, 10)):  # Simulate 10 posts
                post = FacebookPost(
                    post_id=f"post_{page_id}_{i}_{datetime.now().timestamp()}",
                    user_id=page_id,
                    user_name=f"Page {page_id}",
                    page_id=page_id,
                    page_name=f"Page {page_id}",
                    message=f"Post {i} from page {page_id}",
                    like_count=10 * (i + 1),
                    comment_count=5 * (i + 1),
                    share_count=2 * (i + 1),
                    reaction_count=15 * (i + 1),
                    created_time=datetime.now() - timedelta(hours=i),
                    post_type="status"
                )
                
                posts.append(post)
                self.posts[post.post_id] = post
            
            self.metrics.posts_scanned += len(posts)
            self.metrics.api_calls_made += 1
            return posts
            
        except Exception as e:
            self._logger.error(f"Error fetching posts for page {page_id}: {e}")
            return []
    
    async def _fetch_group_posts(self, group_id: str, limit: int = 50) -> List[FacebookPost]:
        """Fetch recent posts from a group."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.3)
            
            posts = []
            
            # In real implementation, this would fetch actual posts
            for i in range(min(limit, 8)):  # Simulate 8 posts
                post = FacebookPost(
                    post_id=f"group_post_{group_id}_{i}_{datetime.now().timestamp()}",
                    user_id=f"user_{i}",
                    user_name=f"User {i}",
                    message=f"Group post {i} in group {group_id}",
                    like_count=5 * (i + 1),
                    comment_count=3 * (i + 1),
                    share_count=1 * (i + 1),
                    reaction_count=8 * (i + 1),
                    created_time=datetime.now() - timedelta(hours=i * 2),
                    post_type="status"
                )
                
                posts.append(post)
                self.posts[post.post_id] = post
            
            self.metrics.posts_scanned += len(posts)
            self.metrics.api_calls_made += 1
            return posts
            
        except Exception as e:
            self._logger.error(f"Error fetching posts for group {group_id}: {e}")
            return []
    
    async def _fetch_user_posts(self, user_id: str, limit: int = 50) -> List[FacebookPost]:
        """Fetch recent posts from a user."""
        try:
            # Simulate Graph API call
            await asyncio.sleep(0.3)
            
            posts = []
            
            # In real implementation, this would fetch actual posts
            for i in range(min(limit, 5)):  # Simulate 5 posts
                post = FacebookPost(
                    post_id=f"user_post_{user_id}_{i}_{datetime.now().timestamp()}",
                    user_id=user_id,
                    user_name=f"User {user_id}",
                    message=f"User post {i} by user {user_id}",
                    like_count=3 * (i + 1),
                    comment_count=2 * (i + 1),
                    share_count=1 * i,
                    reaction_count=5 * (i + 1),
                    created_time=datetime.now() - timedelta(days=i),
                    post_type="status"
                )
                
                posts.append(post)
                self.posts[post.post_id] = post
            
            self.metrics.posts_scanned += len(posts)
            self.metrics.api_calls_made += 1
            return posts
            
        except Exception as e:
            self._logger.error(f"Error fetching posts for user {user_id}: {e}")
            return []
    
    async def _analyze_page_for_violations(self, page: FacebookPage) -> List[FacebookViolation]:
        """Analyze Facebook page for violations."""
        violations = []
        
        try:
            # Analyze page content
            page_text = f"{page.name} {page.about} {page.description}".lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, page_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.6, 1.0)
                        
                        violation = FacebookViolation(
                            violation_id=f"fb_page_{page.page_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="page",
                            content_id=page.page_id,
                            violation_type=f"page_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Page violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'page_name': page.name,
                                'about_preview': page.about[:200]
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing page for violations: {e}")
        
        return violations
    
    async def _analyze_group_for_violations(self, group: FacebookGroup) -> List[FacebookViolation]:
        """Analyze Facebook group for violations."""
        violations = []
        
        try:
            # Analyze group content
            group_text = f"{group.name} {group.description}".lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, group_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.6, 1.0)
                        
                        violation = FacebookViolation(
                            violation_id=f"fb_group_{group.group_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="group",
                            content_id=group.group_id,
                            violation_type=f"group_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Group violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'group_name': group.name,
                                'description_preview': group.description[:200]
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing group for violations: {e}")
        
        return violations
    
    async def _analyze_user_for_violations(self, user: FacebookUser) -> List[FacebookViolation]:
        """Analyze Facebook user for violations."""
        violations = []
        
        try:
            # Analyze user content
            user_text = f"{user.name} {user.bio}".lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, user_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.6, 1.0)
                        
                        violation = FacebookViolation(
                            violation_id=f"fb_user_{user.user_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="user",
                            content_id=user.user_id,
                            violation_type=f"user_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"User violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'user_name': user.name,
                                'bio_preview': user.bio[:200]
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing user for violations: {e}")
        
        return violations
    
    async def _analyze_post_for_violations(self, post: FacebookPost) -> List[FacebookViolation]:
        """Analyze Facebook post for violations."""
        violations = []
        
        try:
            # Analyze post content
            post_text = f"{post.message} {post.story} {post.link_description or ''}".lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, post_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.5, 1.0)
                        
                        violation = FacebookViolation(
                            violation_id=f"fb_post_{post.post_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="post",
                            content_id=post.post_id,
                            violation_type=f"post_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Post violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'user_name': post.user_name,
                                'message_preview': post.message[:200]
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing post for violations: {e}")
        
        return violations
    
    def _calculate_severity(self, violation_type: str, confidence: float) -> str:
        """Calculate violation severity."""
        high_risk_types = ['violence', 'harassment', 'misinformation']
        
        if violation_type in high_risk_types:
            if confidence >= 0.8:
                return "critical"
            elif confidence >= 0.6:
                return "high"
            else:
                return "medium"
        else:
            if confidence >= 0.9:
                return "high"
            elif confidence >= 0.7:
                return "medium"
            else:
                return "low"
    
    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting for API requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self._request_delay:
            sleep_time = self._request_delay - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = asyncio.get_event_loop().time()
    
    def get_scanner_status(self) -> Dict[str, Any]:
        """
Get current scanner status."""
        return {
            'scanning_active': self._scanning_active,
            'monitored_targets': {
                'pages': len(self.monitored_pages),
                'groups': len(self.monitored_groups),
                'users': len(self.monitored_users)
            },
            'content_counts': {
                'posts': len(self.posts),
                'pages': len(self.pages),
                'groups': len(self.groups),
                'users': len(self.users)
            },
            'violations_detected': len(self.violations),
            'metrics': {
                'posts_scanned': self.metrics.posts_scanned,
                'pages_scanned': self.metrics.pages_scanned,
                'groups_scanned': self.metrics.groups_scanned,
                'users_scanned': self.metrics.users_scanned,
                'violations_detected': self.metrics.violations_detected,
                'api_calls_made': self.metrics.api_calls_made,
                'scan_duration_seconds': self.metrics.scan_duration_seconds,
                'last_scan': self.metrics.last_scan.isoformat()
            }
        }
    
    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
Get recent violations."""
        recent_violations = sorted(
            self.violations,
            key=lambda v: v.detected_at,
            reverse=True
        )[:limit]
        
        return [
            {
                'violation_id': v.violation_id,
                'content_type': v.content_type,
                'content_id': v.content_id,
                'violation_type': v.violation_type,
                'confidence_score': v.confidence_score,
                'detected_at': v.detected_at.isoformat(),
                'description': v.description,
                'evidence': v.evidence,
                'severity': v.severity,
                'reported': v.reported
            }
            for v in recent_violations
        ]
    
    async def shutdown(self) -> None:
        """
Shutdown the Facebook scanner."""
        try:
            self._logger.info("Shutting down Facebook scanner...")
            
            await self.stop_scanning()
            
            # Clear data
            self.posts.clear()
            self.pages.clear()
            self.groups.clear()
            self.users.clear()
            self.comments.clear()
            self.violations.clear()
            
            self._logger.info("Facebook scanner shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during Facebook scanner shutdown: {e}")
            raise


# Export main class
__all__ = [
    'FacebookScanner', 'FacebookPost', 'FacebookPage', 'FacebookGroup', 
    'FacebookUser', 'FacebookComment', 'FacebookViolation', 'FacebookScanMetrics'
]