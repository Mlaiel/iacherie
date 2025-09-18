"""Crawl Optimization Engine
Advanced robot optimization and crawl efficiency for Ainflue creator economy platform.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Technical SEO Expert: Advanced Technical Optimization
Crawl Intelligence Specialist: Robot Behavior Analysis
Performance Engineer: Crawl Budget & Efficiency Optimization
ML Engineer: AI-powered Crawl Pattern Recognition
DevOps Engineer: Infrastructure Optimization
"""

import asyncio
import time
import json
import re
import requests
import hashlib
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse
from urllib.robotparser import RobotFileParser
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter, deque
import sqlite3
import aiohttp
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns


class CrawlPriority(Enum):
    """Crawl priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"


class RobotType(Enum):
    """Types of web crawlers."""
    GOOGLEBOT = "googlebot"
    BINGBOT = "bingbot"
    YANDEXBOT = "yandexbot"
    BAIDUSPIDER = "baiduspider"
    FACEBOOKBOT = "facebookexternalhit"
    TWITTERBOT = "twitterbot"
    LINKEDINBOT = "linkedinbot"
    APPLEBOT = "applebot"
    GENERIC = "generic"


@dataclass
class CrawlRequest:
    """Individual crawl request data."""
    url: str
    user_agent: str
    timestamp: datetime
    response_code: int
    response_time: float
    content_type: str
    content_length: int
    referrer: Optional[str] = None
    ip_address: Optional[str] = None
    robot_type: Optional[RobotType] = None
    priority: CrawlPriority = CrawlPriority.MEDIUM


@dataclass
class CrawlPattern:
    """Identified crawl pattern."""
    pattern_id: str
    robot_type: RobotType
    frequency: float  # requests per hour
    url_patterns: List[str]
    time_patterns: List[str]
    behavior_score: float
    efficiency_score: float
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CrawlBudgetAnalysis:
    """Comprehensive crawl budget analysis."""
    domain: str
    analysis_period: timedelta
    total_crawl_requests: int
    unique_pages_crawled: int
    crawl_efficiency: float
    budget_utilization: float
    wasted_crawl_budget: float
    robot_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    optimization_opportunities: List[str]
    recommendations: List[str]


@dataclass
class CrawlOptimizationResult:
    """Crawl optimization results."""
    domain: str
    optimization_timestamp: datetime
    original_efficiency: float
    optimized_efficiency: float
    improvement_percentage: float
    optimized_robots_txt: str
    optimized_sitemap_structure: Dict[str, Any]
    crawl_directives: Dict[str, Any]
    monitoring_recommendations: List[str]
    implementation_steps: List[str]


class RobotBehaviorAnalyzer:
    """Analyze and understand robot crawling behavior."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.robot_signatures = {
            'googlebot': [
                'mozilla/5.0 (compatible; googlebot/',
                'googlebot/',
                'google'
            ],
            'bingbot': [
                'mozilla/5.0 (compatible; bingbot/',
                'bingbot/',
                'bing'
            ],
            'yandexbot': [
                'mozilla/5.0 (compatible; yandexbot/',
                'yandexbot/'
            ],
            'baiduspider': [
                'mozilla/5.0 (compatible; baiduspider/',
                'baiduspider/'
            ]
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.RobotBehaviorAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_crawl_logs(self, crawl_logs: List[Dict[str, Any]]) -> List[CrawlRequest]:
        """Parse and analyze crawl logs."""
        self.logger.info(f"Analyzing {len(crawl_logs)} crawl log entries")
        
        crawl_requests = []
        
        for log_entry in crawl_logs:
            try:
                # Parse log entry
                crawl_request = await self._parse_log_entry(log_entry)
                if crawl_request:
                    crawl_requests.append(crawl_request)
            except Exception as e:
                self.logger.error(f"Error parsing log entry: {e}")
        
        self.logger.info(f"Successfully parsed {len(crawl_requests)} crawl requests")
        return crawl_requests
    
    async def _parse_log_entry(self, log_entry: Dict[str, Any]) -> Optional[CrawlRequest]:
        """Parse individual log entry into CrawlRequest."""
        try:
            url = log_entry.get('url', '')
            user_agent = log_entry.get('user_agent', '').lower()
            
            # Identify robot type
            robot_type = await self._identify_robot_type(user_agent)
            
            # Determine priority based on URL and robot
            priority = await self._determine_crawl_priority(url, robot_type)
            
            crawl_request = CrawlRequest(
                url=url,
                user_agent=user_agent,
                timestamp=datetime.fromisoformat(log_entry.get('timestamp', datetime.now(timezone.utc).isoformat())),
                response_code=int(log_entry.get('response_code', 200)),
                response_time=float(log_entry.get('response_time', 0)),
                content_type=log_entry.get('content_type', 'text/html'),
                content_length=int(log_entry.get('content_length', 0)),
                referrer=log_entry.get('referrer'),
                ip_address=log_entry.get('ip_address'),
                robot_type=robot_type,
                priority=priority
            )
            
            return crawl_request
            
        except Exception as e:
            self.logger.error(f"Error parsing log entry: {e}")
            return None
    
    async def _identify_robot_type(self, user_agent: str) -> RobotType:
        """Identify robot type from user agent."""
        user_agent_lower = user_agent.lower()
        
        for robot_name, signatures in self.robot_signatures.items():
            for signature in signatures:
                if signature in user_agent_lower:
                    return RobotType(robot_name)
        
        # Check for other known bots
        if 'facebook' in user_agent_lower:
            return RobotType.FACEBOOKBOT
        elif 'twitter' in user_agent_lower:
            return RobotType.TWITTERBOT
        elif 'linkedin' in user_agent_lower:
            return RobotType.LINKEDINBOT
        elif 'apple' in user_agent_lower:
            return RobotType.APPLEBOT
        
        return RobotType.GENERIC
    
    async def _determine_crawl_priority(self, url: str, robot_type: RobotType) -> CrawlPriority:
        """Determine crawl priority based on URL and robot type."""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Critical pages
        if path in ['/', '/index.html', '/home', '/sitemap.xml', '/robots.txt']:
            return CrawlPriority.CRITICAL
        
        # High priority for main content
        if any(pattern in path for pattern in ['/creator/', '/content/', '/article/', '/post/']):
            return CrawlPriority.HIGH
        
        # Medium priority for category pages
        if any(pattern in path for pattern in ['/category/', '/tag/', '/archive/']):
            return CrawlPriority.MEDIUM
        
        # Low priority for admin/system pages
        if any(pattern in path for pattern in ['/admin/', '/api/', '/assets/', '/css/', '/js/']):
            return CrawlPriority.LOW
        
        # Deferred for development/test pages
        if any(pattern in path for pattern in ['/test/', '/dev/', '/staging/', '/temp/']):
            return CrawlPriority.DEFERRED
        
        return CrawlPriority.MEDIUM
    
    async def identify_crawl_patterns(self, crawl_requests: List[CrawlRequest]) -> List[CrawlPattern]:
        """Identify crawling patterns from request data."""
        self.logger.info("Identifying crawl patterns")
        
        patterns = []
        
        # Group requests by robot type
        robot_groups = defaultdict(list)
        for request in crawl_requests:
            robot_groups[request.robot_type].append(request)
        
        for robot_type, requests in robot_groups.items():
            if len(requests) < 10:  # Need minimum requests for pattern analysis
                continue
            
            pattern = await self._analyze_robot_pattern(robot_type, requests)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_robot_pattern(self, robot_type: RobotType, requests: List[CrawlRequest]) -> Optional[CrawlPattern]:
        """Analyze crawling pattern for specific robot."""
        if len(requests) < 10:
            return None
        
        # Sort requests by timestamp
        requests.sort(key=lambda x: x.timestamp)
        
        # Calculate frequency
        time_span = (requests[-1].timestamp - requests[0].timestamp).total_seconds() / 3600  # hours
        frequency = len(requests) / max(time_span, 1)
        
        # Analyze URL patterns
        url_patterns = await self._extract_url_patterns(requests)
        
        # Analyze time patterns
        time_patterns = await self._extract_time_patterns(requests)
        
        # Calculate behavior score
        behavior_score = await self._calculate_behavior_score(requests)
        
        # Calculate efficiency score
        efficiency_score = await self._calculate_efficiency_score(requests)
        
        # Generate recommendations
        recommendations = await self._generate_pattern_recommendations(robot_type, requests)
        
        pattern_id = f"{robot_type.value}_{hashlib.md5(str(requests[0].timestamp).encode()).hexdigest()[:8]}"
        
        return CrawlPattern(
            pattern_id=pattern_id,
            robot_type=robot_type,
            frequency=frequency,
            url_patterns=url_patterns,
            time_patterns=time_patterns,
            behavior_score=behavior_score,
            efficiency_score=efficiency_score,
            recommendations=recommendations
        )
    
    async def _extract_url_patterns(self, requests: List[CrawlRequest]) -> List[str]:
        """Extract common URL patterns from requests."""
        url_paths = [urlparse(req.url).path for req in requests]
        
        # Find common patterns
        patterns = []
        
        # Group by path segments
        path_segments = defaultdict(int)
        for path in url_paths:
            segments = [seg for seg in path.split('/') if seg]
            for i, segment in enumerate(segments):
                pattern = '/' + '/'.join(segments[:i+1])
                path_segments[pattern] += 1
        
        # Extract most common patterns
        sorted_patterns = sorted(path_segments.items(), key=lambda x: x[1], reverse=True)
        patterns = [pattern for pattern, count in sorted_patterns[:10] if count > 1]
        
        return patterns
    
    async def _extract_time_patterns(self, requests: List[CrawlRequest]) -> List[str]:
        """Extract temporal patterns from requests."""
        patterns = []
        
        # Analyze hourly distribution
        hourly_counts = defaultdict(int)
        for request in requests:
            hour = request.timestamp.hour
            hourly_counts[hour] += 1
        
        # Find peak hours
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for hour, count in peak_hours:
            patterns.append(f"peak_hour_{hour}:00")
        
        # Analyze daily patterns
        daily_counts = defaultdict(int)
        for request in requests:
            day = request.timestamp.weekday()
            daily_counts[day] += 1
        
        # Find peak days
        if daily_counts:
            peak_day = max(daily_counts.items(), key=lambda x: x[1])
            patterns.append(f"peak_day_{peak_day[0]}")
        
        return patterns
    
    async def _calculate_behavior_score(self, requests: List[CrawlRequest]) -> float:
        """Calculate behavior score based on crawling efficiency."""
        if not requests:
            return 0.0
        
        score = 100.0
        
        # Success rate
        successful_requests = [r for r in requests if r.response_code == 200]
        success_rate = len(successful_requests) / len(requests)
        score *= success_rate
        
        # Response time efficiency
        avg_response_time = sum(r.response_time for r in requests) / len(requests)
        if avg_response_time > 5.0:  # 5 seconds threshold
            score *= 0.8
        elif avg_response_time > 2.0:  # 2 seconds threshold
            score *= 0.9
        
        # Crawl politeness (request frequency)
        if len(requests) > 1:
            time_span = (requests[-1].timestamp - requests[0].timestamp).total_seconds()
            avg_interval = time_span / (len(requests) - 1)
            if avg_interval < 1.0:  # Less than 1 second between requests
                score *= 0.7
        
        return min(100.0, score)
    
    async def _calculate_efficiency_score(self, requests: List[CrawlRequest]) -> float:
        """Calculate crawl efficiency score."""
        if not requests:
            return 0.0
        
        # Unique pages vs total requests
        unique_urls = len(set(req.url for req in requests))
        efficiency = (unique_urls / len(requests)) * 100
        
        # Penalty for excessive error requests
        error_requests = [r for r in requests if r.response_code >= 400]
        error_rate = len(error_requests) / len(requests)
        efficiency *= (1 - error_rate)
        
        return min(100.0, efficiency)
    
    async def _generate_pattern_recommendations(self, robot_type: RobotType, requests: List[CrawlRequest]) -> List[str]:
        """Generate recommendations based on crawl pattern."""
        recommendations = []
        
        # Check for excessive crawling
        time_span_hours = (requests[-1].timestamp - requests[0].timestamp).total_seconds() / 3600
        if time_span_hours > 0:
            requests_per_hour = len(requests) / time_span_hours
            if requests_per_hour > 100:
                recommendations.append(f"Consider implementing crawl-delay for {robot_type.value} (current: {requests_per_hour:.1f} req/hr)")
        
        # Check error rates
        error_requests = [r for r in requests if r.response_code >= 400]
        error_rate = len(error_requests) / len(requests)
        if error_rate > 0.1:
            recommendations.append(f"High error rate for {robot_type.value} ({error_rate:.1%}) - review URL structure")
        
        # Check for duplicate crawling
        url_counts = Counter(req.url for req in requests)
        duplicates = [url for url, count in url_counts.items() if count > 5]
        if duplicates:
            recommendations.append(f"Prevent duplicate crawling of {len(duplicates)} URLs by {robot_type.value}")
        
        return recommendations


class CrawlBudgetOptimizer:
    """Optimize crawl budget allocation and efficiency."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.CrawlBudgetOptimizer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_crawl_budget(self, domain: str, crawl_requests: List[CrawlRequest], 
                                 analysis_period: timedelta) -> CrawlBudgetAnalysis:
        """Comprehensive crawl budget analysis."""
        self.logger.info(f"Analyzing crawl budget for {domain}")
        
        # Filter requests within analysis period
        end_time = max(req.timestamp for req in crawl_requests)
        start_time = end_time - analysis_period
        period_requests = [req for req in crawl_requests if req.timestamp >= start_time]
        
        # Basic metrics
        total_requests = len(period_requests)
        unique_pages = len(set(req.url for req in period_requests))
        
        # Calculate efficiency
        crawl_efficiency = (unique_pages / total_requests * 100) if total_requests > 0 else 0
        
        # Analyze budget utilization
        budget_utilization = await self._calculate_budget_utilization(period_requests)
        
        # Calculate wasted budget
        wasted_budget = await self._calculate_wasted_budget(period_requests)
        
        # Robot distribution
        robot_distribution = Counter(req.robot_type.value for req in period_requests)
        
        # Priority distribution
        priority_distribution = Counter(req.priority.value for req in period_requests)
        
        # Find optimization opportunities
        opportunities = await self._identify_optimization_opportunities(period_requests)
        
        # Generate recommendations
        recommendations = await self._generate_budget_recommendations(period_requests, crawl_efficiency)
        
        return CrawlBudgetAnalysis(
            domain=domain,
            analysis_period=analysis_period,
            total_crawl_requests=total_requests,
            unique_pages_crawled=unique_pages,
            crawl_efficiency=crawl_efficiency,
            budget_utilization=budget_utilization,
            wasted_crawl_budget=wasted_budget,
            robot_distribution=dict(robot_distribution),
            priority_distribution=dict(priority_distribution),
            optimization_opportunities=opportunities,
            recommendations=recommendations
        )
    
    async def _calculate_budget_utilization(self, requests: List[CrawlRequest]) -> float:
        """Calculate crawl budget utilization efficiency."""
        if not requests:
            return 0.0
        
        # Weighted scoring based on priority and success
        total_weight = 0
        utilized_weight = 0
        
        priority_weights = {
            CrawlPriority.CRITICAL: 5,
            CrawlPriority.HIGH: 4,
            CrawlPriority.MEDIUM: 3,
            CrawlPriority.LOW: 2,
            CrawlPriority.DEFERRED: 1
        }
        
        for request in requests:
            weight = priority_weights.get(request.priority, 1)
            total_weight += weight
            
            # Consider request successful if 2xx or 3xx
            if 200 <= request.response_code < 400:
                utilized_weight += weight
        
        return (utilized_weight / total_weight * 100) if total_weight > 0 else 0
    
    async def _calculate_wasted_budget(self, requests: List[CrawlRequest]) -> float:
        """Calculate percentage of wasted crawl budget."""
        if not requests:
            return 0.0
        
        wasted_requests = 0
        
        for request in requests:
            # Consider requests wasted if:
            # 1. 4xx or 5xx errors
            # 2. Duplicate crawling of same URL
            # 3. Low priority pages crawled excessively
            
            if request.response_code >= 400:
                wasted_requests += 1
            elif request.priority == CrawlPriority.DEFERRED:
                wasted_requests += 0.5  # Partial waste
        
        # Check for duplicate crawling
        url_counts = Counter(req.url for req in requests)
        for url, count in url_counts.items():
            if count > 3:  # More than 3 times is likely wasteful
                wasted_requests += count - 3
        
        return (wasted_requests / len(requests) * 100) if requests else 0
    
    async def _identify_optimization_opportunities(self, requests: List[CrawlRequest]) -> List[str]:
        """Identify crawl budget optimization opportunities."""
        opportunities = []
        
        # Check for excessive error crawling
        error_requests = [r for r in requests if r.response_code >= 400]
        if len(error_requests) > len(requests) * 0.1:
            opportunities.append(f"Reduce error page crawling: {len(error_requests)} error requests found")
        
        # Check for low-priority page crawling
        low_priority_requests = [r for r in requests if r.priority in [CrawlPriority.LOW, CrawlPriority.DEFERRED]]
        if len(low_priority_requests) > len(requests) * 0.3:
            opportunities.append(f"Limit low-priority page crawling: {len(low_priority_requests)} low-priority requests")
        
        # Check for duplicate crawling
        url_counts = Counter(req.url for req in requests)
        excessive_duplicates = [url for url, count in url_counts.items() if count > 5]
        if excessive_duplicates:
            opportunities.append(f"Prevent duplicate crawling of {len(excessive_duplicates)} URLs")
        
        # Check crawl frequency by robot
        robot_requests = defaultdict(list)
        for request in requests:
            robot_requests[request.robot_type].append(request)
        
        for robot_type, robot_reqs in robot_requests.items():
            if len(robot_reqs) > 1:
                time_span = (robot_reqs[-1].timestamp - robot_reqs[0].timestamp).total_seconds()
                if time_span > 0:
                    frequency = len(robot_reqs) / (time_span / 3600)  # requests per hour
                    if frequency > 50:  # Threshold for excessive crawling
                        opportunities.append(f"Implement crawl delay for {robot_type.value} (current: {frequency:.1f} req/hr)")
        
        return opportunities
    
    async def _generate_budget_recommendations(self, requests: List[CrawlRequest], efficiency: float) -> List[str]:
        """Generate crawl budget optimization recommendations."""
        recommendations = []
        
        if efficiency < 70:
            recommendations.append("Implement URL prioritization to improve crawl efficiency")
        
        if efficiency < 50:
            recommendations.append("Consider blocking low-value pages from crawling")
        
        # Check for specific issues
        error_rate = len([r for r in requests if r.response_code >= 400]) / len(requests) if requests else 0
        if error_rate > 0.1:
            recommendations.append("Fix broken pages and redirects to reduce wasted crawl budget")
        
        # Check robot distribution
        robot_counts = Counter(req.robot_type.value for req in requests)
        if len(robot_counts) > 5:
            recommendations.append("Consider implementing robot-specific crawl limits")
        
        return recommendations
    
    async def optimize_robots_txt(self, domain: str, crawl_analysis: CrawlBudgetAnalysis) -> str:
        """Generate optimized robots.txt based on crawl analysis."""
        self.logger.info(f"Generating optimized robots.txt for {domain}")
        
        robots_lines = [
            "# Optimized robots.txt for Ainflue Creator Economy Platform",
            "# Generated by Crawl Optimization Engine",
            f"# Optimization Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "# Main search engine bots",
            "User-agent: Googlebot",
            "Allow: /creator/",
            "Allow: /content/",
            "Allow: /article/",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Disallow: /temp/",
            "Crawl-delay: 1",
            "",
            "User-agent: Bingbot",
            "Allow: /creator/",
            "Allow: /content/",
            "Disallow: /admin/",
            "Disallow: /api/",
            "Crawl-delay: 2",
            "",
            "# Social media bots",
            "User-agent: facebookexternalhit",
            "Allow: /creator/",
            "Allow: /content/",
            "Disallow: /admin/",
            "",
            "User-agent: Twitterbot",
            "Allow: /creator/",
            "Allow: /content/",
            "Disallow: /admin/",
            ""
        ]
        
        # Add crawl delays based on analysis
        if crawl_analysis.wasted_crawl_budget > 20:
            robots_lines.extend([
                "# Implement stricter crawl delays due to budget waste",
                "User-agent: *",
                "Crawl-delay: 3",
                ""
            ])
        
        # Block problematic paths
        if crawl_analysis.total_crawl_requests > 10000:
            robots_lines.extend([
                "# Block resource-intensive paths",
                "User-agent: *",
                "Disallow: /assets/",
                "Disallow: /css/",
                "Disallow: /js/",
                "Disallow: /images/",
                ""
            ])
        
        # Add sitemaps
        robots_lines.extend([
            "# Sitemaps",
            f"Sitemap: https://{domain}/sitemap.xml",
            f"Sitemap: https://{domain}/creator-sitemap.xml",
            f"Sitemap: https://{domain}/content-sitemap.xml",
            ""
        ])
        
        return '\n'.join(robots_lines)


class CrawlOptimizationEngine:
    """Main crawl optimization engine for Ainflue platform."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize components
        self.behavior_analyzer = RobotBehaviorAnalyzer()
        self.budget_optimizer = CrawlBudgetOptimizer()
        
        # Database for tracking
        self._init_database()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _init_database(self):
        """Initialize SQLite database for crawl tracking."""
        with sqlite3.connect("crawl_optimization.db") as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    user_agent TEXT,
                    timestamp DATETIME,
                    response_code INTEGER,
                    response_time REAL,
                    content_type TEXT,
                    content_length INTEGER,
                    robot_type TEXT,
                    priority TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE,
                    robot_type TEXT,
                    frequency REAL,
                    behavior_score REAL,
                    efficiency_score REAL,
                    recommendations TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT,
                    original_efficiency REAL,
                    optimized_efficiency REAL,
                    improvement_percentage REAL,
                    optimized_robots_txt TEXT,
                    recommendations TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    async def run_crawl_optimization(self, domain: str, crawl_logs: List[Dict[str, Any]], 
                                   analysis_period_days: int = 7) -> CrawlOptimizationResult:
        """Run comprehensive crawl optimization."""
        self.logger.info(f"Starting crawl optimization for {domain}")
        
        start_time = datetime.now(timezone.utc)
        analysis_period = timedelta(days=analysis_period_days)
        
        try:
            # 1. Parse crawl logs
            self.logger.info("Parsing crawl logs...")
            crawl_requests = await self.behavior_analyzer.analyze_crawl_logs(crawl_logs)
            
            # Store requests in database
            await self._store_crawl_requests(crawl_requests)
            
            # 2. Analyze crawl patterns
            self.logger.info("Analyzing crawl patterns...")
            crawl_patterns = await self.behavior_analyzer.identify_crawl_patterns(crawl_requests)
            
            # Store patterns in database
            await self._store_crawl_patterns(crawl_patterns)
            
            # 3. Analyze crawl budget
            self.logger.info("Analyzing crawl budget...")
            budget_analysis = await self.budget_optimizer.analyze_crawl_budget(
                domain, crawl_requests, analysis_period
            )
            
            original_efficiency = budget_analysis.crawl_efficiency
            
            # 4. Generate optimizations
            self.logger.info("Generating optimizations...")
            
            # Optimize robots.txt
            optimized_robots_txt = await self.budget_optimizer.optimize_robots_txt(domain, budget_analysis)
            
            # Generate sitemap structure optimization
            optimized_sitemap = await self._optimize_sitemap_structure(crawl_requests)
            
            # Generate crawl directives
            crawl_directives = await self._generate_crawl_directives(crawl_patterns, budget_analysis)
            
            # 5. Calculate projected improvement
            optimized_efficiency = await self._calculate_projected_efficiency(
                original_efficiency, budget_analysis, crawl_patterns
            )
            
            improvement_percentage = ((optimized_efficiency - original_efficiency) / original_efficiency * 100) if original_efficiency > 0 else 0
            
            # 6. Generate monitoring recommendations
            monitoring_recommendations = await self._generate_monitoring_recommendations(domain, crawl_patterns)
            
            # 7. Generate implementation steps
            implementation_steps = await self._generate_implementation_steps(domain, budget_analysis)
            
            # Create optimization result
            result = CrawlOptimizationResult(
                domain=domain,
                optimization_timestamp=start_time,
                original_efficiency=original_efficiency,
                optimized_efficiency=optimized_efficiency,
                improvement_percentage=improvement_percentage,
                optimized_robots_txt=optimized_robots_txt,
                optimized_sitemap_structure=optimized_sitemap,
                crawl_directives=crawl_directives,
                monitoring_recommendations=monitoring_recommendations,
                implementation_steps=implementation_steps
            )
            
            # Store optimization result
            await self._store_optimization_result(result)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(f"Crawl optimization completed in {duration:.2f}s. Improvement: {improvement_percentage:.1f}%")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during crawl optimization: {e}")
            raise
    
    async def _store_crawl_requests(self, requests: List[CrawlRequest]):
        """Store crawl requests in database."""
        with sqlite3.connect("crawl_optimization.db") as conn:
            for request in requests:
                conn.execute("""
                    INSERT INTO crawl_requests 
                    (url, user_agent, timestamp, response_code, response_time, 
                     content_type, content_length, robot_type, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request.url,
                    request.user_agent,
                    request.timestamp.isoformat(),
                    request.response_code,
                    request.response_time,
                    request.content_type,
                    request.content_length,
                    request.robot_type.value,
                    request.priority.value
                ))
            conn.commit()
    
    async def _store_crawl_patterns(self, patterns: List[CrawlPattern]):
        """Store crawl patterns in database."""
        with sqlite3.connect("crawl_optimization.db") as conn:
            for pattern in patterns:
                conn.execute("""
                    INSERT OR REPLACE INTO crawl_patterns 
                    (pattern_id, robot_type, frequency, behavior_score, 
                     efficiency_score, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_id,
                    pattern.robot_type.value,
                    pattern.frequency,
                    pattern.behavior_score,
                    pattern.efficiency_score,
                    json.dumps(pattern.recommendations)
                ))
            conn.commit()
    
    async def _store_optimization_result(self, result: CrawlOptimizationResult):
        """Store optimization result in database."""
        with sqlite3.connect("crawl_optimization.db") as conn:
            conn.execute("""
                INSERT INTO optimization_results 
                (domain, original_efficiency, optimized_efficiency, 
                 improvement_percentage, optimized_robots_txt, recommendations)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                result.domain,
                result.original_efficiency,
                result.optimized_efficiency,
                result.improvement_percentage,
                result.optimized_robots_txt,
                json.dumps(result.monitoring_recommendations)
            ))
            conn.commit()
    
    async def _optimize_sitemap_structure(self, crawl_requests: List[CrawlRequest]) -> Dict[str, Any]:
        """Optimize sitemap structure based on crawl patterns."""
        url_priority_scores = defaultdict(float)
        url_crawl_counts = Counter(req.url for req in crawl_requests)
        
        # Calculate priority scores based on crawl frequency and success
        for request in crawl_requests:
            base_score = 0.5
            
            # Boost score based on priority
            priority_boost = {
                CrawlPriority.CRITICAL: 0.5,
                CrawlPriority.HIGH: 0.3,
                CrawlPriority.MEDIUM: 0.1,
                CrawlPriority.LOW: 0.0,
                CrawlPriority.DEFERRED: -0.1
            }
            base_score += priority_boost.get(request.priority, 0)
            
            # Boost score for successful requests
            if request.response_code == 200:
                base_score += 0.2
            
            # Boost score for frequently crawled URLs
            crawl_count = url_crawl_counts[request.url]
            if crawl_count > 5:
                base_score += 0.1
            
            url_priority_scores[request.url] = min(1.0, base_score)
        
        # Group URLs by pattern for sitemap organization
        sitemap_structure = {
            'main_sitemap': {
                'type': 'urlset',
                'urls': [],
                'priority_threshold': 0.8
            },
            'creator_sitemap': {
                'type': 'urlset', 
                'urls': [],
                'priority_threshold': 0.6
            },
            'content_sitemap': {
                'type': 'urlset',
                'urls': [],
                'priority_threshold': 0.4
            }
        }
        
        # Categorize URLs
        for url, priority in url_priority_scores.items():
            parsed_url = urlparse(url)
            path = parsed_url.path
            
            if priority >= 0.8:
                sitemap_structure['main_sitemap']['urls'].append({
                    'url': url,
                    'priority': priority,
                    'changefreq': 'weekly'
                })
            elif '/creator/' in path:
                sitemap_structure['creator_sitemap']['urls'].append({
                    'url': url,
                    'priority': priority,
                    'changefreq': 'weekly'
                })
            elif '/content/' in path or '/article/' in path:
                sitemap_structure['content_sitemap']['urls'].append({
                    'url': url,
                    'priority': priority,
                    'changefreq': 'monthly'
                })
        
        return sitemap_structure
    
    async def _generate_crawl_directives(self, patterns: List[CrawlPattern], 
                                       budget_analysis: CrawlBudgetAnalysis) -> Dict[str, Any]:
        """Generate crawl directives for different robots."""
        directives = {
            'crawl_delays': {},
            'allow_patterns': [],
            'disallow_patterns': [],
            'priority_rules': {}
        }
        
        # Set crawl delays based on patterns
        for pattern in patterns:
            if pattern.frequency > 100:  # More than 100 requests/hour
                directives['crawl_delays'][pattern.robot_type.value] = 3
            elif pattern.frequency > 50:
                directives['crawl_delays'][pattern.robot_type.value] = 2
            else:
                directives['crawl_delays'][pattern.robot_type.value] = 1
        
        # Allow patterns for important content
        directives['allow_patterns'] = [
            '/creator/',
            '/content/',
            '/article/',
            '/sitemap.xml'
        ]
        
        # Disallow patterns for problematic paths
        if budget_analysis.wasted_crawl_budget > 15:
            directives['disallow_patterns'].extend([
                '/admin/',
                '/api/',
                '/temp/',
                '/test/',
                '/assets/'
            ])
        
        # Priority rules
        directives['priority_rules'] = {
            'high_priority': ['/creator/', '/content/'],
            'medium_priority': ['/category/', '/tag/'],
            'low_priority': ['/admin/', '/assets/']
        }
        
        return directives
    
    async def _calculate_projected_efficiency(self, original_efficiency: float, 
                                            budget_analysis: CrawlBudgetAnalysis,
                                            patterns: List[CrawlPattern]) -> float:
        """Calculate projected efficiency after optimizations."""
        projected_efficiency = original_efficiency
        
        # Improvement from reducing wasted budget
        waste_reduction = min(budget_analysis.wasted_crawl_budget * 0.7, 20)  # Up to 20% improvement
        projected_efficiency += waste_reduction
        
        # Improvement from crawl delays (reduces server load, improves response times)
        if any(p.frequency > 50 for p in patterns):
            projected_efficiency += 5
        
        # Improvement from better URL prioritization
        if budget_analysis.crawl_efficiency < 70:
            projected_efficiency += 10
        
        return min(100.0, projected_efficiency)
    
    async def _generate_monitoring_recommendations(self, domain: str, patterns: List[CrawlPattern]) -> List[str]:
        """Generate monitoring recommendations."""
        recommendations = [
            f"Monitor crawl rate trends for {domain} weekly",
            "Set up alerts for crawl budget waste exceeding 20%",
            "Track robots.txt compliance across different bots",
            "Monitor server response times during peak crawl periods"
        ]
        
        # Pattern-specific recommendations
        for pattern in patterns:
            if pattern.behavior_score < 70:
                recommendations.append(f"Monitor {pattern.robot_type.value} behavior - low efficiency detected")
            
            if pattern.frequency > 100:
                recommendations.append(f"Monitor {pattern.robot_type.value} crawl rate - implement rate limiting if needed")
        
        return recommendations
    
    async def _generate_implementation_steps(self, domain: str, budget_analysis: CrawlBudgetAnalysis) -> List[str]:
        """Generate implementation steps for optimizations."""
        steps = [
            "1. Backup current robots.txt file",
            "2. Implement optimized robots.txt with crawl delays",
            "3. Update sitemap structure with priority-based organization",
            "4. Configure server-side crawl rate limiting",
            "5. Set up crawl budget monitoring dashboard",
            "6. Test optimizations with small-scale changes first",
            "7. Monitor impact for 2-4 weeks before full implementation",
            "8. Document changes and establish review schedule"
        ]
        
        # Add specific steps based on analysis
        if budget_analysis.wasted_crawl_budget > 25:
            steps.insert(3, "3.1. Block problematic URLs causing budget waste")
        
        if budget_analysis.crawl_efficiency < 60:
            steps.insert(4, "4.1. Implement URL canonicalization to reduce duplicate crawling")
        
        return steps
    
    async def generate_crawl_optimization_report(self, result: CrawlOptimizationResult) -> str:
        """Generate comprehensive crawl optimization report."""
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Crawl Optimization Report - {result.domain}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                .improvement {{ font-size: 48px; font-weight: bold; color: #28a745; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #e9ecef; }}
                .recommendations {{ background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .code-block {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin: 15px 0; }}
                .legal {{ font-size: 10px; color: #666; margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
                .section {{ margin: 30px 0; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Crawl Optimization Report</h1>
                <h2>{result.domain}</h2>
                <div class="improvement">+{result.improvement_percentage:.1f}%</div>
                <p>Projected Efficiency Improvement</p>
                <p>Report generated on {result.optimization_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>📊 Original Efficiency</h3>
                    <div style="font-size: 24px; font-weight: bold;">{result.original_efficiency:.1f}%</div>
                    <small>Current Crawl Efficiency</small>
                </div>
                <div class="metric-card">
                    <h3>⚡ Optimized Efficiency</h3>
                    <div style="font-size: 24px; font-weight: bold;">{result.optimized_efficiency:.1f}%</div>
                    <small>Projected After Optimization</small>
                </div>
                <div class="metric-card">
                    <h3>📈 Improvement</h3>
                    <div style="font-size: 24px; font-weight: bold;">+{result.improvement_percentage:.1f}%</div>
                    <small>Efficiency Gain</small>
                </div>
                <div class="metric-card">
                    <h3>🎯 Optimization Score</h3>
                    <div style="font-size: 24px; font-weight: bold;">{min(100, 50 + result.improvement_percentage):.0f}/100</div>
                    <small>Overall Optimization Quality</small>
                </div>
            </div>
        """
        
        # Add implementation steps
        if result.implementation_steps:
            report += """
            <div class="section">
                <h2>🛠️ Implementation Steps</h2>
                <div class="recommendations">
                    <ol>
            """
            
            for step in result.implementation_steps:
                report += f"<li>{step}</li>"
            
            report += """
                    </ol>
                </div>
            </div>
            """
        
        # Add monitoring recommendations
        if result.monitoring_recommendations:
            report += """
            <div class="section">
                <h2>📊 Monitoring Recommendations</h2>
                <div class="recommendations">
                    <ul>
            """
            
            for rec in result.monitoring_recommendations:
                report += f"<li>{rec}</li>"
            
            report += """
                    </ul>
                </div>
            </div>
            """
        
        # Add optimized robots.txt
        if result.optimized_robots_txt:
            report += f"""
            <div class="section">
                <h2>🤖 Optimized robots.txt</h2>
                <div class="code-block">{result.optimized_robots_txt}</div>
            </div>
            """
        
        report += f"""
            <div class="legal">
                <p>© 2025 Fahed Mlaiel (mlaiel@live.de) - Crawl Optimization Engine</p>
                <p>Advanced crawl intelligence report generated by Ainflue Crawl Optimization Engine</p>
                <p>🤖 Optimized for search engine efficiency and creator content discoverability</p>
                <p>📧 For enterprise crawl optimization consulting: mlaiel@live.de</p>
            </div>
        </body>
        </html>
        """
        
        return report


# Usage Example
async def main():
    """Example usage of Crawl Optimization Engine."""
    
    # Initialize crawl optimizer
    crawl_optimizer = CrawlOptimizationEngine()
    
    try:
        domain = "ainflue.com"
        
        # Example crawl logs (in production, these would come from server logs)
        crawl_logs = [
            {
                'url': 'https://ainflue.com/',
                'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'timestamp': (datetime.now(timezone.utc) - timedelta(hours=i)).isoformat(),
                'response_code': 200,
                'response_time': 0.5 + (i * 0.1),
                'content_type': 'text/html',
                'content_length': 15000
            }
            for i in range(100)
        ]
        
        # Add some variety to the logs
        for i in range(50):
            crawl_logs.append({
                'url': f'https://ainflue.com/creator/user{i}',
                'user_agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'timestamp': (datetime.now(timezone.utc) - timedelta(hours=i//2)).isoformat(),
                'response_code': 200 if i % 10 != 0 else 404,
                'response_time': 0.8,
                'content_type': 'text/html',
                'content_length': 12000
            })
        
        print(f"\n=== Crawl Optimization for {domain} ===")
        
        # Run crawl optimization
        result = await crawl_optimizer.run_crawl_optimization(domain, crawl_logs, 7)
        
        print(f"Domain: {result.domain}")
        print(f"Original Efficiency: {result.original_efficiency:.1f}%")
        print(f"Optimized Efficiency: {result.optimized_efficiency:.1f}%")
        print(f"Improvement: {result.improvement_percentage:.1f}%")
        
        # Show implementation steps
        if result.implementation_steps:
            print("\n=== Implementation Steps ===")
            for i, step in enumerate(result.implementation_steps[:5], 1):
                print(f"{i}. {step}")
        
        # Show monitoring recommendations
        if result.monitoring_recommendations:
            print("\n=== Monitoring Recommendations ===")
            for i, rec in enumerate(result.monitoring_recommendations[:3], 1):
                print(f"{i}. {rec}")
        
        # Generate comprehensive report
        report_html = await crawl_optimizer.generate_crawl_optimization_report(result)
        print("\n=== Crawl Optimization Report Generated ===")
        print(f"Report contains {len(report_html)} characters of detailed analysis")
        
    except Exception as e:
        print(f"Error during crawl optimization: {e}")


if __name__ == "__main__":
    asyncio.run(main())