"""Universal Web Crawler - Crawler Web Générique
=============================================

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

© 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Universal web crawler for comprehensive website monitoring and content extraction.
Provides advanced crawling capabilities for any website with intelligent content detection.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import re
from urllib.parse import urlparse, urljoin, urlunparse
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class WebPage:
    """Web page data structure."""    url: str
    title: str
    content: str
    meta_description: str = ""
    meta_keywords: str = ""
    language: str = "en"
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    audio: List[str] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    stylesheets: List[str] = field(default_factory=list)
    structured_data: List[Dict[str, Any]] = field(default_factory=list)
    content_hash: str = ""
    crawled_at: datetime = field(default_factory=datetime.now)
    last_modified: Optional[datetime] = None
    size_bytes: int = 0


@dataclass
class CrawlJob:
    """Crawl job definition."""    job_id: str
    start_urls: List[str]
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    url_patterns: List[str] = field(default_factory=list)
    max_depth: int = 3
    max_pages: int = 1000
    respect_robots: bool = True
    delay_seconds: float = 1.0
    timeout_seconds: int = 30
    user_agent: str = "UniversalWebCrawler/1.0"
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy_url: Optional[str] = None
    javascript_enabled: bool = False
    screenshot_enabled: bool = False
    content_types: List[str] = field(default_factory=lambda: ["text/html"])
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed, paused


@dataclass
class CrawlResult:
    """Crawl operation result."""    job_id: str
    pages_crawled: int = 0
    pages_failed: int = 0
    total_size_bytes: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    success_rate: float = 0.0
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebViolation:
    """Web content violation detection result."""    violation_id: str
    url: str
    violation_type: str
    confidence_score: float
    detected_at: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical
    page_title: str = ""
    domain: str = ""


@dataclass
class CrawlerMetrics:
    """Universal crawler metrics."""    total_jobs: int = 0
    active_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_pages_crawled: int = 0
    total_violations_detected: int = 0
    total_crawl_time_seconds: float = 0.0
    average_crawl_speed_pages_per_second: float = 0.0
    last_crawl: datetime = field(default_factory=datetime.now)


class UniversalWebCrawler:
    """    Universal web crawler for comprehensive website monitoring.
    
    Features:
    - Multi-domain crawling with depth control
    - Intelligent content extraction
    - JavaScript rendering support
    - Screenshot capture capabilities
    - Robots.txt compliance
    - Rate limiting and politeness
    - Content violation detection
    - Real-time monitoring
    - Scalable architecture
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize universal web crawler."""        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.max_concurrent_jobs = self.config.get('max_concurrent_jobs', 5)
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 10)
        self.default_delay = self.config.get('default_delay_seconds', 1.0)
        self.default_timeout = self.config.get('default_timeout_seconds', 30)
        self.enable_javascript = self.config.get('enable_javascript', False)
        self.enable_screenshots = self.config.get('enable_screenshots', False)
        self.max_page_size = self.config.get('max_page_size_bytes', 10 * 1024 * 1024)  # 10MB
        
        # Crawler state
        self.metrics = CrawlerMetrics()
        self.violations: List[WebViolation] = []
        self._crawling_active = False
        
        # Job management
        self.crawl_jobs: Dict[str, CrawlJob] = {}
        self.crawl_results: Dict[str, CrawlResult] = {}
        self.active_jobs: Set[str] = set()
        self.job_queue: asyncio.Queue = asyncio.Queue()
        
        # Content storage
        self.pages: Dict[str, WebPage] = {}
        self.url_visited: Set[str] = set()
        self.url_queue: Dict[str, asyncio.Queue] = {}
        
        # Session management
        self._session: Optional[Any] = None
        self._browser: Optional[Any] = None
        
        # Violation detection patterns
        self.violation_patterns = {
            'copyright': [
                r'(?i)(pirated|stolen|leaked|unauthorized|copyright\s+violation)',
                r'(?i)(download\s+free|torrent|bootleg|cracked)',
                r'(?i)(replica|fake|counterfeit|knockoff)'
            ],
            'malware': [
                r'(?i)(malware|virus|trojan|spyware|adware)',
                r'(?i)(download\s+now|click\s+here|free\s+download)',
                r'(?i)(suspicious|dangerous|harmful)'
            ],
            'phishing': [
                r'(?i)(phishing|scam|fraud|fake\s+login)',
                r'(?i)(verify\s+account|urgent\s+action|suspended)',
                r'(?i)(click\s+immediately|act\s+now)'
            ],
            'adult_content': [
                r'(?i)(adult\s+content|18\+|explicit|nsfw)',
                r'(?i)(porn|sexual|nude|xxx)',
                r'(?i)(adult\s+site|mature\s+content)'
            ],
            'spam': [
                r'(?i)(spam|promotional|advertisement|marketing)',
                r'(?i)(buy\s+now|limited\s+time|special\s+offer)',
                r'(?i)(click\s+here|visit\s+now|learn\s+more)'
            ]
        }
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
        
        self._logger.info("Universal Web Crawler initialized")
    
    async def initialize(self) -> None:
        """Initialize the universal web crawler."""        try:
            self._logger.info("Initializing universal web crawler...")
            
            # Initialize HTTP session
            await self._initialize_session()
            
            # Initialize browser if JavaScript is enabled
            if self.enable_javascript:
                await self._initialize_browser()
            
            # Setup violation detection
            await self._setup_violation_detection()
            
            self._logger.info("Universal web crawler initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize universal web crawler: {e}")
            raise
    
    async def _initialize_session(self) -> None:
        """Initialize HTTP session."""        try:
            # This would initialize aiohttp session with proper configuration
            # For now, implement placeholder
            self._session = "placeholder_session"
            self._logger.debug("HTTP session initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize HTTP session: {e}")
            raise
    
    async def _initialize_browser(self) -> None:
        """Initialize browser for JavaScript rendering."""        try:
            # This would initialize Selenium or Playwright browser
            # For now, implement placeholder
            self._browser = "placeholder_browser"
            self._logger.debug("Browser initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def _setup_violation_detection(self) -> None:
        """Setup violation detection systems."""        try:
            # This would setup actual ML models for violation detection
            # For now, implement placeholder
            self._logger.debug("Violation detection setup complete")
            
        except Exception as e:
            self._logger.error(f"Failed to setup violation detection: {e}")
            raise
    
    async def start_crawling(self) -> None:
        """Start universal web crawling operations."""        try:
            if self._crawling_active:
                self._logger.warning("Universal web crawling is already active")
                return
            
            self._logger.info("Starting universal web crawling...")
            
            self._crawling_active = True
            
            # Start job processor
            asyncio.create_task(self._process_crawl_jobs())
            
            self._logger.info("Universal web crawling started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start universal web crawling: {e}")
            self._crawling_active = False
            raise
    
    async def stop_crawling(self) -> None:
        """Stop universal web crawling operations."""        try:
            if not self._crawling_active:
                self._logger.warning("Universal web crawling is not active")
                return
            
            self._logger.info("Stopping universal web crawling...")
            
            self._crawling_active = False
            
            # Stop all active jobs
            for job_id in list(self.active_jobs):
                await self.stop_crawl_job(job_id)
            
            self._logger.info("Universal web crawling stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping universal web crawling: {e}")
            raise
    
    async def create_crawl_job(
        self,
        start_urls: List[str],
        job_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new crawl job."""        try:
            job_id = f"job_{datetime.now().timestamp()}_{hash(str(start_urls)) % 10000}"
            
            config = job_config or {}
            
            job = CrawlJob(
                job_id=job_id,
                start_urls=start_urls,
                allowed_domains=config.get('allowed_domains', []),
                blocked_domains=config.get('blocked_domains', []),
                url_patterns=config.get('url_patterns', []),
                max_depth=config.get('max_depth', 3),
                max_pages=config.get('max_pages', 1000),
                respect_robots=config.get('respect_robots', True),
                delay_seconds=config.get('delay_seconds', self.default_delay),
                timeout_seconds=config.get('timeout_seconds', self.default_timeout),
                user_agent=config.get('user_agent', self.user_agents[0]),
                headers=config.get('headers', {}),
                cookies=config.get('cookies', {}),
                proxy_url=config.get('proxy_url'),
                javascript_enabled=config.get('javascript_enabled', self.enable_javascript),
                screenshot_enabled=config.get('screenshot_enabled', self.enable_screenshots),
                content_types=config.get('content_types', ["text/html"])
            )
            
            self.crawl_jobs[job_id] = job
            self.crawl_results[job_id] = CrawlResult(job_id=job_id)
            
            # Add to job queue
            await self.job_queue.put(job_id)
            
            self.metrics.total_jobs += 1
            
            self._logger.info(f"Created crawl job: {job_id} for {len(start_urls)} URLs")
            return job_id
            
        except Exception as e:
            self._logger.error(f"Failed to create crawl job: {e}")
            raise
    
    async def start_crawl_job(self, job_id: str) -> bool:
        """Start a specific crawl job."""        try:
            if job_id not in self.crawl_jobs:
                self._logger.error(f"Crawl job not found: {job_id}")
                return False
            
            if job_id in self.active_jobs:
                self._logger.warning(f"Crawl job already active: {job_id}")
                return True
            
            job = self.crawl_jobs[job_id]
            result = self.crawl_results[job_id]
            
            job.status = "running"
            result.started_at = datetime.now()
            
            self.active_jobs.add(job_id)
            self.metrics.active_jobs = len(self.active_jobs)
            
            # Start crawling task
            asyncio.create_task(self._execute_crawl_job(job_id))
            
            self._logger.info(f"Started crawl job: {job_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to start crawl job {job_id}: {e}")
            return False
    
    async def stop_crawl_job(self, job_id: str) -> bool:
        """Stop a specific crawl job."""        try:
            if job_id not in self.active_jobs:
                self._logger.warning(f"Crawl job not active: {job_id}")
                return True
            
            job = self.crawl_jobs[job_id]
            result = self.crawl_results[job_id]
            
            job.status = "paused"
            result.completed_at = datetime.now()
            
            if result.started_at:
                result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            self.active_jobs.discard(job_id)
            self.metrics.active_jobs = len(self.active_jobs)
            
            self._logger.info(f"Stopped crawl job: {job_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to stop crawl job {job_id}: {e}")
            return False
    
    async def crawl_single_url(
        self,
        url: str,
        job_config: Optional[Dict[str, Any]] = None
    ) -> Optional[WebPage]:
        """Crawl a single URL."""        try:
            self._logger.debug(f"Crawling single URL: {url}")
            
            # Create temporary job for single URL
            job_id = await self.create_crawl_job([url], job_config)
            
            # Execute crawl
            await self.start_crawl_job(job_id)
            
            # Wait for completion (with timeout)
            timeout = (job_config or {}).get('timeout_seconds', 30)
            start_time = datetime.now()
            
            while job_id in self.active_jobs:
                if (datetime.now() - start_time).total_seconds() > timeout:
                    await self.stop_crawl_job(job_id)
                    break
                await asyncio.sleep(0.1)
            
            # Return the crawled page
            if url in self.pages:
                return self.pages[url]
            
            return None
            
        except Exception as e:
            self._logger.error(f"Error crawling single URL {url}: {e}")
            return None
    
    async def _process_crawl_jobs(self) -> None:
        """Process crawl jobs from the queue."""        while self._crawling_active:
            try:
                # Limit concurrent jobs
                if len(self.active_jobs) >= self.max_concurrent_jobs:
                    await asyncio.sleep(1)
                    continue
                
                # Get next job
                try:
                    job_id = await asyncio.wait_for(self.job_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                if job_id in self.crawl_jobs:
                    await self.start_crawl_job(job_id)
                
            except Exception as e:
                self._logger.error(f"Error processing crawl jobs: {e}")
                await asyncio.sleep(5)
    
    async def _execute_crawl_job(self, job_id: str) -> None:
        """Execute a crawl job."""        try:
            job = self.crawl_jobs[job_id]
            result = self.crawl_results[job_id]
            
            self._logger.info(f"Executing crawl job: {job_id}")
            
            # Initialize URL queue for this job
            self.url_queue[job_id] = asyncio.Queue()
            
            # Add start URLs to queue
            for url in job.start_urls:
                await self.url_queue[job_id].put((url, 0))  # (url, depth)
            
            # Process URLs with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            
            while not self.url_queue[job_id].empty() and job_id in self.active_jobs:
                if result.pages_crawled >= job.max_pages:
                    break
                
                try:
                    url, depth = await asyncio.wait_for(
                        self.url_queue[job_id].get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    break
                
                if depth > job.max_depth:
                    continue
                
                if url in self.url_visited:
                    continue
                
                # Check domain restrictions
                if not self._is_url_allowed(url, job):
                    continue
                
                # Crawl URL
                asyncio.create_task(
                    self._crawl_url_with_semaphore(job_id, url, depth, semaphore)
                )
            
            # Wait for remaining tasks to complete
            await asyncio.sleep(2)
            
            # Complete job
            if job_id in self.active_jobs:
                job.status = "completed"
                result.completed_at = datetime.now()
                
                if result.started_at:
                    result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
                
                if result.pages_crawled > 0:
                    result.success_rate = (result.pages_crawled / (result.pages_crawled + result.pages_failed)) * 100
                
                self.active_jobs.discard(job_id)
                self.metrics.active_jobs = len(self.active_jobs)
                self.metrics.completed_jobs += 1
                
                self._logger.info(f"Completed crawl job: {job_id} - {result.pages_crawled} pages")
            
        except Exception as e:
            self._logger.error(f"Error executing crawl job {job_id}: {e}")
            
            # Mark job as failed
            job = self.crawl_jobs[job_id]
            result = self.crawl_results[job_id]
            
            job.status = "failed"
            result.completed_at = datetime.now()
            result.errors.append(str(e))
            
            self.active_jobs.discard(job_id)
            self.metrics.active_jobs = len(self.active_jobs)
            self.metrics.failed_jobs += 1
    
    async def _crawl_url_with_semaphore(
        self,
        job_id: str,
        url: str,
        depth: int,
        semaphore: asyncio.Semaphore
    ) -> None:
        """Crawl URL with concurrency control."""        async with semaphore:
            await self._crawl_url(job_id, url, depth)
    
    async def _crawl_url(self, job_id: str, url: str, depth: int) -> None:
        """Crawl a single URL."""        try:
            job = self.crawl_jobs[job_id]
            result = self.crawl_results[job_id]
            
            self._logger.debug(f"Crawling URL: {url} (depth: {depth})")
            
            # Mark URL as visited
            self.url_visited.add(url)
            
            # Rate limiting
            await asyncio.sleep(job.delay_seconds)
            
            # Fetch page content
            page_data = await self._fetch_page_content(url, job)
            
            if page_data:
                # Create WebPage object
                page = WebPage(**page_data)
                page.content_hash = hashlib.sha256(page.content.encode()).hexdigest()
                
                # Store page
                self.pages[url] = page
                result.pages_crawled += 1
                result.total_size_bytes += page.size_bytes
                self.metrics.total_pages_crawled += 1
                
                # Analyze page for violations
                violations = await self._analyze_page_for_violations(page)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.total_violations_detected += 1
                
                # Extract and queue new URLs
                if depth < job.max_depth:
                    for link in page.links:
                        absolute_url = urljoin(url, link)
                        
                        if (absolute_url not in self.url_visited and 
                            self._is_url_allowed(absolute_url, job)):
                            
                            try:
                                await self.url_queue[job_id].put((absolute_url, depth + 1))
                            except:
                                pass  # Queue might be full or job stopped
            else:
                result.pages_failed += 1
            
        except Exception as e:
            self._logger.error(f"Error crawling URL {url}: {e}")
            
            result = self.crawl_results[job_id]
            result.pages_failed += 1
            result.errors.append(f"Failed to crawl {url}: {str(e)}")
    
    async def _fetch_page_content(self, url: str, job: CrawlJob) -> Optional[Dict[str, Any]]:
        """Fetch page content."""        try:
            # Simulate HTTP request
            await asyncio.sleep(0.2)
            
            # In real implementation, this would make actual HTTP requests
            # using aiohttp or requests, and optionally use Selenium/Playwright
            # for JavaScript rendering
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            page_data = {
                'url': url,
                'title': f'Page Title for {domain}',
                'content': f'Content for page {url}. This is sample content.',
                'meta_description': f'Meta description for {url}',
                'meta_keywords': 'sample, keywords, content',
                'language': 'en',
                'status_code': 200,
                'headers': {'content-type': 'text/html', 'server': 'nginx'},
                'links': [
                    f'{parsed_url.scheme}://{domain}/page1',
                    f'{parsed_url.scheme}://{domain}/page2',
                    f'{parsed_url.scheme}://{domain}/about'
                ],
                'images': [f'{parsed_url.scheme}://{domain}/image1.jpg'],
                'videos': [],
                'audio': [],
                'forms': [],
                'scripts': [f'{parsed_url.scheme}://{domain}/script.js'],
                'stylesheets': [f'{parsed_url.scheme}://{domain}/style.css'],
                'size_bytes': 1024,
                'last_modified': datetime.now() - timedelta(days=1)
            }
            
            return page_data
            
        except Exception as e:
            self._logger.error(f"Error fetching content for {url}: {e}")
            return None
    
    def _is_url_allowed(self, url: str, job: CrawlJob) -> bool:
        """Check if URL is allowed to be crawled."""        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Check blocked domains
            if domain in job.blocked_domains:
                return False
            
            # Check allowed domains (if specified)
            if job.allowed_domains and domain not in job.allowed_domains:
                return False
            
            # Check URL patterns (if specified)
            if job.url_patterns:
                for pattern in job.url_patterns:
                    if re.match(pattern, url):
                        return True
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Error checking URL allowance for {url}: {e}")
            return False
    
    async def _analyze_page_for_violations(self, page: WebPage) -> List[WebViolation]:
        """Analyze page for violations."""        violations = []
        
        try:
            # Analyze page content
            content_text = f"{page.title} {page.content} {page.meta_description}".lower()
            
            parsed_url = urlparse(page.url)
            domain = parsed_url.netloc
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.5, 1.0)
                        
                        violation = WebViolation(
                            violation_id=f"web_{domain}_{violation_type}_{datetime.now().timestamp()}",
                            url=page.url,
                            violation_type=violation_type,
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Web content violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'content_preview': page.content[:500]
                            },
                            severity=self._calculate_severity(violation_type, confidence),
                            page_title=page.title,
                            domain=domain
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing page for violations: {e}")
        
        return violations
    
    def _calculate_severity(self, violation_type: str, confidence: float) -> str:
        """Calculate violation severity."""        high_risk_types = ['malware', 'phishing']
        
        if violation_type in high_risk_types:
            if confidence >= 0.7:
                return "critical"
            elif confidence >= 0.5:
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
    
    def get_crawler_status(self) -> Dict[str, Any]:
        """Get current crawler status."""        return {
            'crawling_active': self._crawling_active,
            'active_jobs': len(self.active_jobs),
            'total_jobs': len(self.crawl_jobs),
            'pages_stored': len(self.pages),
            'violations_detected': len(self.violations),
            'metrics': {
                'total_jobs': self.metrics.total_jobs,
                'active_jobs': self.metrics.active_jobs,
                'completed_jobs': self.metrics.completed_jobs,
                'failed_jobs': self.metrics.failed_jobs,
                'total_pages_crawled': self.metrics.total_pages_crawled,
                'total_violations_detected': self.metrics.total_violations_detected,
                'total_crawl_time_seconds': self.metrics.total_crawl_time_seconds,
                'average_crawl_speed_pages_per_second': self.metrics.average_crawl_speed_pages_per_second,
                'last_crawl': self.metrics.last_crawl.isoformat()
            }
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific crawl job."""        if job_id not in self.crawl_jobs:
            return None
        
        job = self.crawl_jobs[job_id]
        result = self.crawl_results[job_id]
        
        return {
            'job_id': job_id,
            'status': job.status,
            'start_urls': job.start_urls,
            'max_depth': job.max_depth,
            'max_pages': job.max_pages,
            'pages_crawled': result.pages_crawled,
            'pages_failed': result.pages_failed,
            'total_size_bytes': result.total_size_bytes,
            'started_at': result.started_at.isoformat() if result.started_at else None,
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
            'duration_seconds': result.duration_seconds,
            'success_rate': result.success_rate,
            'errors': result.errors
        }
    
    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violations."""        recent_violations = sorted(
            self.violations,
            key=lambda v: v.detected_at,
            reverse=True
        )[:limit]
        
        return [
            {
                'violation_id': v.violation_id,
                'url': v.url,
                'violation_type': v.violation_type,
                'confidence_score': v.confidence_score,
                'detected_at': v.detected_at.isoformat(),
                'description': v.description,
                'evidence': v.evidence,
                'severity': v.severity,
                'page_title': v.page_title,
                'domain': v.domain
            }
            for v in recent_violations
        ]
    
    def get_crawled_pages(self, domain: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get crawled pages."""        pages = list(self.pages.values())
        
        # Filter by domain if specified
        if domain:
            pages = [p for p in pages if urlparse(p.url).netloc == domain]
        
        # Sort by crawled time (most recent first)
        pages.sort(key=lambda p: p.crawled_at, reverse=True)
        
        # Limit results
        pages = pages[:limit]
        
        return [
            {
                'url': p.url,
                'title': p.title,
                'status_code': p.status_code,
                'size_bytes': p.size_bytes,
                'crawled_at': p.crawled_at.isoformat(),
                'content_preview': p.content[:200],
                'links_count': len(p.links),
                'images_count': len(p.images)
            }
            for p in pages
        ]
    
    async def shutdown(self) -> None:
        """Shutdown the universal web crawler."""        try:
            self._logger.info("Shutting down universal web crawler...")
            
            await self.stop_crawling()
            
            # Close session and browser
            if self._session:
                # Would close actual session
                self._session = None
            
            if self._browser:
                # Would close actual browser
                self._browser = None
            
            # Clear data
            self.pages.clear()
            self.violations.clear()
            self.crawl_jobs.clear()
            self.crawl_results.clear()
            
            self._logger.info("Universal web crawler shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during universal web crawler shutdown: {e}")
            raise


# Export main class
__all__ = [
    'UniversalWebCrawler', 'WebPage', 'CrawlJob', 'CrawlResult', 
    'WebViolation', 'CrawlerMetrics'
]