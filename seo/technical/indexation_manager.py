"""Indexation Manager
Advanced indexation management and optimization for Ainflue creator economy platform.

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
Performance Engineer: Core Web Vitals & Speed Optimization
DevOps Engineer: Technical Infrastructure
Full-Stack Developer: Frontend/Backend Technical SEO
"""

import asyncio
import time
import json
import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse
from urllib.robotparser import RobotFileParser
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import hashlib
import sqlite3
import aiohttp
import asyncio
from collections import defaultdict, Counter
import math


@dataclass
class IndexationStatus:
    """Individual URL indexation status."""
    url: str
    indexed: bool
    last_crawled: Optional[datetime] = None
    indexation_issues: List[str] = field(default_factory=list)
    crawl_errors: List[str] = field(default_factory=list)
    meta_robots: Optional[str] = None
    http_status: Optional[int] = None
    redirect_chain: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    content_hash: Optional[str] = None
    page_depth: Optional[int] = None
    internal_links_count: Optional[int] = None
    external_links_count: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CrawlBudgetAnalysis:
    """Crawl budget analysis results."""
    domain: str
    total_pages: int
    crawlable_pages: int
    blocked_pages: int
    orphaned_pages: int
    redirect_pages: int
    error_pages: int
    crawl_efficiency: float
    budget_utilization: float
    recommendations: List[str] = field(default_factory=list)
    page_depth_distribution: Dict[int, int] = field(default_factory=dict)
    url_parameters_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexationReport:
    """Comprehensive indexation report."""
    domain: str
    report_timestamp: datetime
    total_urls: int
    indexed_urls: int
    not_indexed_urls: int
    indexation_rate: float
    crawl_budget_analysis: CrawlBudgetAnalysis
    indexation_issues: List[Dict[str, Any]]
    url_statuses: List[IndexationStatus]
    recommendations: List[str]
    technical_issues: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]


class RobotsTxtAnalyzer:
    """Advanced robots.txt analysis for crawl optimization."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.RobotsTxtAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_robots_txt(self, domain: str) -> Dict[str, Any]:
        """Comprehensive robots.txt analysis."""
        self.logger.info(f"Analyzing robots.txt for {domain}")
        
        robots_url = f"https://{domain}/robots.txt"
        analysis = {
            'domain': domain,
            'robots_url': robots_url,
            'exists': False,
            'valid': False,
            'user_agents': {},
            'sitemaps': [],
            'disallow_rules': [],
            'allow_rules': [],
            'crawl_delays': {},
            'issues': [],
            'recommendations': [],
            'crawl_budget_impact': {}
        }
        
        try:
            response = requests.get(robots_url, timeout=10)
            
            if response.status_code == 404:
                analysis['issues'].append({
                    'type': 'missing_robots',
                    'severity': 'medium',
                    'description': 'No robots.txt file found',
                    'impact': 'Search engines may crawl inefficiently'
                })
                analysis['recommendations'].append('Create robots.txt file to guide search engine crawling')
                return analysis
            
            if response.status_code != 200:
                analysis['issues'].append({
                    'type': 'robots_error',
                    'severity': 'high',
                    'description': f'robots.txt returns HTTP {response.status_code}',
                    'impact': 'Search engines cannot access crawl instructions'
                })
                return analysis
            
            analysis['exists'] = True
            robots_content = response.text
            
            # Parse robots.txt using robotparser
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Manual parsing for detailed analysis
            detailed_analysis = await self._parse_robots_detailed(robots_content, domain)
            analysis.update(detailed_analysis)
            
            # Analyze crawl budget impact
            budget_impact = await self._analyze_crawl_budget_impact(analysis)
            analysis['crawl_budget_impact'] = budget_impact
            
            analysis['valid'] = True
            
        except Exception as e:
            self.logger.error(f"Error analyzing robots.txt: {e}")
            analysis['issues'].append({
                'type': 'analysis_error',
                'severity': 'high',
                'description': f'Failed to analyze robots.txt: {str(e)}',
                'impact': 'Cannot assess crawl directives'
            })
        
        return analysis
    
    async def _parse_robots_detailed(self, content: str, domain: str) -> Dict[str, Any]:
        """Detailed robots.txt parsing."""
        lines = content.strip().split('\n')
        
        user_agents = {}
        current_user_agent = None
        sitemaps = []
        disallow_rules = []
        allow_rules = []
        crawl_delays = {}
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse directives
            if ':' not in line:
                issues.append({
                    'type': 'syntax_error',
                    'severity': 'medium',
                    'description': f'Line {line_num}: Invalid syntax - missing colon',
                    'line': line
                })
                continue
            
            directive, value = line.split(':', 1)
            directive = directive.strip().lower()
            value = value.strip()
            
            if directive == 'user-agent':
                current_user_agent = value
                if current_user_agent not in user_agents:
                    user_agents[current_user_agent] = {
                        'disallow': [],
                        'allow': [],
                        'crawl_delay': None
                    }
            
            elif directive == 'disallow':
                if current_user_agent:
                    user_agents[current_user_agent]['disallow'].append(value)
                    disallow_rules.append({
                        'user_agent': current_user_agent,
                        'path': value,
                        'line': line_num
                    })
                else:
                    issues.append({
                        'type': 'missing_user_agent',
                        'severity': 'high',
                        'description': f'Line {line_num}: Disallow directive without User-agent',
                        'line': line
                    })
            
            elif directive == 'allow':
                if current_user_agent:
                    user_agents[current_user_agent]['allow'].append(value)
                    allow_rules.append({
                        'user_agent': current_user_agent,
                        'path': value,
                        'line': line_num
                    })
                else:
                    issues.append({
                        'type': 'missing_user_agent',
                        'severity': 'high',
                        'description': f'Line {line_num}: Allow directive without User-agent',
                        'line': line
                    })
            
            elif directive == 'crawl-delay':
                if current_user_agent:
                    try:
                        delay = float(value)
                        user_agents[current_user_agent]['crawl_delay'] = delay
                        crawl_delays[current_user_agent] = delay
                        
                        if delay > 10:
                            issues.append({
                                'type': 'high_crawl_delay',
                                'severity': 'medium',
                                'description': f'High crawl delay ({delay}s) may slow indexation',
                                'user_agent': current_user_agent
                            })
                    except ValueError:
                        issues.append({
                            'type': 'invalid_crawl_delay',
                            'severity': 'medium',
                            'description': f'Line {line_num}: Invalid crawl-delay value',
                            'line': line
                        })
            
            elif directive == 'sitemap':
                sitemaps.append(value)
                # Validate sitemap URL
                if not value.startswith(('http://', 'https://')):
                    issues.append({
                        'type': 'invalid_sitemap_url',
                        'severity': 'medium',
                        'description': f'Line {line_num}: Sitemap URL should be absolute',
                        'line': line
                    })
            
            else:
                # Unknown directive
                issues.append({
                    'type': 'unknown_directive',
                    'severity': 'low',
                    'description': f'Line {line_num}: Unknown directive "{directive}"',
                    'line': line
                })
        
        # Check for common issues
        if not user_agents:
            issues.append({
                'type': 'no_user_agents',
                'severity': 'high',
                'description': 'No User-agent directives found',
                'impact': 'No crawl rules defined for search engines'
            })
        
        # Check for overly restrictive rules
        for ua, rules in user_agents.items():
            if '/' in rules['disallow']:
                issues.append({
                    'type': 'blocking_all_crawling',
                    'severity': 'critical',
                    'description': f'User-agent "{ua}" blocks all crawling',
                    'impact': 'Search engines cannot crawl any content'
                })
        
        return {
            'user_agents': user_agents,
            'sitemaps': sitemaps,
            'disallow_rules': disallow_rules,
            'allow_rules': allow_rules,
            'crawl_delays': crawl_delays,
            'issues': issues
        }
    
    async def _analyze_crawl_budget_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze impact on crawl budget."""
        impact = {
            'efficiency_score': 100,
            'blocked_percentage': 0,
            'crawl_delay_impact': 'none',
            'recommendations': []
        }
        
        user_agents = analysis.get('user_agents', {})
        
        # Analyze blocking rules
        total_rules = 0
        blocking_rules = 0
        
        for ua, rules in user_agents.items():
            if ua == '*' or 'googlebot' in ua.lower():
                total_rules += len(rules['disallow']) + len(rules['allow'])
                blocking_rules += len(rules['disallow'])
        
        if total_rules > 0:
            impact['blocked_percentage'] = (blocking_rules / total_rules) * 100
            
            if impact['blocked_percentage'] > 50:
                impact['efficiency_score'] -= 30
                impact['recommendations'].append('High percentage of blocked content may waste crawl budget')
        
        # Analyze crawl delays
        crawl_delays = analysis.get('crawl_delays', {})
        max_delay = max(crawl_delays.values()) if crawl_delays else 0
        
        if max_delay > 5:
            impact['crawl_delay_impact'] = 'high'
            impact['efficiency_score'] -= 20
            impact['recommendations'].append('High crawl delays may slow down indexation')
        elif max_delay > 1:
            impact['crawl_delay_impact'] = 'medium'
            impact['efficiency_score'] -= 10
        
        return impact


class SitemapAnalyzer:
    """Advanced XML sitemap analysis for indexation optimization."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.SitemapAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_sitemaps(self, domain: str, sitemap_urls: List[str] = None) -> Dict[str, Any]:
        """Comprehensive sitemap analysis."""
        self.logger.info(f"Analyzing sitemaps for {domain}")
        
        if sitemap_urls is None:
            # Discover sitemaps from robots.txt
            sitemap_urls = await self._discover_sitemaps(domain)
        
        analysis = {
            'domain': domain,
            'sitemaps_found': len(sitemap_urls),
            'sitemap_analyses': [],
            'total_urls': 0,
            'issues': [],
            'recommendations': [],
            'indexation_potential': 0
        }
        
        for sitemap_url in sitemap_urls:
            sitemap_analysis = await self._analyze_single_sitemap(sitemap_url)
            analysis['sitemap_analyses'].append(sitemap_analysis)
            analysis['total_urls'] += sitemap_analysis.get('url_count', 0)
        
        # Generate overall recommendations
        recommendations = await self._generate_sitemap_recommendations(analysis)
        analysis['recommendations'] = recommendations
        
        # Calculate indexation potential
        indexation_potential = await self._calculate_indexation_potential(analysis)
        analysis['indexation_potential'] = indexation_potential
        
        return analysis
    
    async def _discover_sitemaps(self, domain: str) -> List[str]:
        """Discover sitemaps from robots.txt and common locations."""
        sitemap_urls = []
        
        # Check robots.txt
        try:
            robots_url = f"https://{domain}/robots.txt"
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().strip().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemap_urls.append(sitemap_url)
        except:
            pass
        
        # Check common sitemap locations
        common_locations = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemaps/sitemap.xml"
        ]
        
        for url in common_locations:
            if url not in sitemap_urls:
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        sitemap_urls.append(url)
                except:
                    pass
        
        return sitemap_urls
    
    async def _analyze_single_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """Analyze a single sitemap file."""
        analysis = {
            'url': sitemap_url,
            'type': 'unknown',
            'url_count': 0,
            'issues': [],
            'last_modified': None,
            'size_bytes': 0,
            'urls_analysis': {}
        }
        
        try:
            response = requests.get(sitemap_url, timeout=15)
            
            if response.status_code != 200:
                analysis['issues'].append({
                    'type': 'sitemap_error',
                    'severity': 'high',
                    'description': f'Sitemap returns HTTP {response.status_code}'
                })
                return analysis
            
            analysis['size_bytes'] = len(response.content)
            
            # Check if sitemap is too large
            if analysis['size_bytes'] > 50 * 1024 * 1024:  # 50MB
                analysis['issues'].append({
                    'type': 'oversized_sitemap',
                    'severity': 'high',
                    'description': f'Sitemap size ({analysis["size_bytes"]} bytes) exceeds 50MB limit'
                })
            
            # Parse XML
            try:
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Determine sitemap type
                if root.tag.endswith('sitemapindex'):
                    analysis['type'] = 'sitemap_index'
                    sitemaps = root.findall('.//ns:sitemap', namespace)
                    analysis['url_count'] = len(sitemaps)
                    
                    # Analyze each sub-sitemap
                    sub_sitemaps = []
                    for sitemap in sitemaps:
                        loc = sitemap.find('ns:loc', namespace)
                        lastmod = sitemap.find('ns:lastmod', namespace)
                        
                        if loc is not None:
                            sub_sitemap_info = {'url': loc.text}
                            if lastmod is not None:
                                sub_sitemap_info['lastmod'] = lastmod.text
                            sub_sitemaps.append(sub_sitemap_info)
                    
                    analysis['sub_sitemaps'] = sub_sitemaps
                
                elif root.tag.endswith('urlset'):
                    analysis['type'] = 'urlset'
                    urls = root.findall('.//ns:url', namespace)
                    analysis['url_count'] = len(urls)
                    
                    if analysis['url_count'] > 50000:
                        analysis['issues'].append({
                            'type': 'too_many_urls',
                            'severity': 'high',
                            'description': f'Sitemap contains {analysis["url_count"]} URLs (limit: 50,000)'
                        })
                    
                    # Analyze URL quality
                    url_analysis = await self._analyze_sitemap_urls(urls, namespace)
                    analysis['urls_analysis'] = url_analysis
                
            except ET.ParseError as e:
                analysis['issues'].append({
                    'type': 'xml_parse_error',
                    'severity': 'critical',
                    'description': f'Invalid XML structure: {str(e)}'
                })
        
        except Exception as e:
            self.logger.error(f"Error analyzing sitemap {sitemap_url}: {e}")
            analysis['issues'].append({
                'type': 'analysis_error',
                'severity': 'high',
                'description': f'Failed to analyze sitemap: {str(e)}'
            })
        
        return analysis
    
    async def _analyze_sitemap_urls(self, urls, namespace) -> Dict[str, Any]:
        """Analyze URLs within a sitemap."""
        url_analysis = {
            'total_urls': len(urls),
            'with_lastmod': 0,
            'with_changefreq': 0,
            'with_priority': 0,
            'https_urls': 0,
            'duplicate_urls': 0,
            'invalid_urls': 0,
            'priority_distribution': defaultdict(int),
            'changefreq_distribution': defaultdict(int)
        }
        
        seen_urls = set()
        
        for url_elem in urls:
            loc = url_elem.find('ns:loc', namespace)
            
            if loc is not None:
                url = loc.text
                
                # Check for duplicates
                if url in seen_urls:
                    url_analysis['duplicate_urls'] += 1
                seen_urls.add(url)
                
                # Check URL validity
                try:
                    parsed = urlparse(url)
                    if not parsed.netloc:
                        url_analysis['invalid_urls'] += 1
                except:
                    url_analysis['invalid_urls'] += 1
                
                # Check HTTPS
                if url.startswith('https://'):
                    url_analysis['https_urls'] += 1
            
            # Check for lastmod
            lastmod = url_elem.find('ns:lastmod', namespace)
            if lastmod is not None:
                url_analysis['with_lastmod'] += 1
            
            # Check for changefreq
            changefreq = url_elem.find('ns:changefreq', namespace)
            if changefreq is not None:
                url_analysis['with_changefreq'] += 1
                url_analysis['changefreq_distribution'][changefreq.text] += 1
            
            # Check for priority
            priority = url_elem.find('ns:priority', namespace)
            if priority is not None:
                url_analysis['with_priority'] += 1
                try:
                    priority_val = float(priority.text)
                    priority_range = f"{int(priority_val * 10) / 10:.1f}"
                    url_analysis['priority_distribution'][priority_range] += 1
                except:
                    pass
        
        return url_analysis
    
    async def _generate_sitemap_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate sitemap optimization recommendations."""
        recommendations = []
        
        if analysis['sitemaps_found'] == 0:
            recommendations.append('Create XML sitemaps to help search engines discover your content')
            return recommendations
        
        # Analyze issues across all sitemaps
        all_issues = []
        for sitemap_analysis in analysis['sitemap_analyses']:
            all_issues.extend(sitemap_analysis.get('issues', []))
        
        # Group issues by type
        issue_types = Counter(issue['type'] for issue in all_issues)
        
        if 'oversized_sitemap' in issue_types:
            recommendations.append('Split large sitemaps into smaller files and use sitemap index')
        
        if 'too_many_urls' in issue_types:
            recommendations.append('Reduce URLs per sitemap to under 50,000 or split into multiple sitemaps')
        
        if 'xml_parse_error' in issue_types:
            recommendations.append('Fix XML syntax errors in sitemaps')
        
        # URL quality recommendations
        for sitemap_analysis in analysis['sitemap_analyses']:
            url_analysis = sitemap_analysis.get('urls_analysis', {})
            
            if url_analysis.get('duplicate_urls', 0) > 0:
                recommendations.append('Remove duplicate URLs from sitemaps')
            
            if url_analysis.get('invalid_urls', 0) > 0:
                recommendations.append('Fix invalid URLs in sitemaps')
            
            if url_analysis.get('https_urls', 0) < url_analysis.get('total_urls', 0) * 0.9:
                recommendations.append('Ensure all sitemap URLs use HTTPS')
        
        return recommendations
    
    async def _calculate_indexation_potential(self, analysis: Dict[str, Any]) -> float:
        """Calculate indexation potential based on sitemap quality."""
        if analysis['sitemaps_found'] == 0:
            return 0.0
        
        score = 100.0
        
        # Deduct points for issues
        all_issues = []
        for sitemap_analysis in analysis['sitemap_analyses']:
            all_issues.extend(sitemap_analysis.get('issues', []))
        
        critical_issues = len([i for i in all_issues if i.get('severity') == 'critical'])
        high_issues = len([i for i in all_issues if i.get('severity') == 'high'])
        medium_issues = len([i for i in all_issues if i.get('severity') == 'medium'])
        
        score -= critical_issues * 30
        score -= high_issues * 15
        score -= medium_issues * 5
        
        return max(0.0, score)


class IndexationTracker:
    """Track and monitor URL indexation status."""
    
    def __init__(self, db_path: str = "indexation_tracking.db"):
        self.db_path = db_path
        self.logger = self._setup_logging()
        self._init_database()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.IndexationTracker')
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
        """Initialize SQLite database for tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS indexation_status (
                    url TEXT PRIMARY KEY,
                    domain TEXT,
                    indexed BOOLEAN,
                    last_checked TIMESTAMP,
                    last_crawled TIMESTAMP,
                    http_status INTEGER,
                    meta_robots TEXT,
                    canonical_url TEXT,
                    content_hash TEXT,
                    page_depth INTEGER,
                    internal_links_count INTEGER,
                    external_links_count INTEGER,
                    indexation_issues TEXT,
                    crawl_errors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_budget_tracking (
                    domain TEXT,
                    date DATE,
                    pages_crawled INTEGER,
                    crawl_errors INTEGER,
                    indexation_rate REAL,
                    crawl_efficiency REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (domain, date)
                )
            """)
            conn.commit()
    
    async def track_url_indexation(self, url: str) -> IndexationStatus:
        """Track indexation status for a single URL."""
        self.logger.info(f"Tracking indexation for {url}")
        
        domain = urlparse(url).netloc
        
        # Check current status
        status = IndexationStatus(url=url)
        
        try:
            # Simulate indexation check (in production, use Search Console API)
            indexed = await self._check_url_indexed(url)
            status.indexed = indexed
            
            # Get page details
            page_details = await self._analyze_page_indexability(url)
            status.http_status = page_details.get('http_status')
            status.meta_robots = page_details.get('meta_robots')
            status.canonical_url = page_details.get('canonical_url')
            status.content_hash = page_details.get('content_hash')
            status.page_depth = page_details.get('page_depth')
            status.internal_links_count = page_details.get('internal_links_count')
            status.external_links_count = page_details.get('external_links_count')
            status.indexation_issues = page_details.get('indexation_issues', [])
            status.crawl_errors = page_details.get('crawl_errors', [])
            
            # Store in database
            await self._store_indexation_status(status)
            
        except Exception as e:
            self.logger.error(f"Error tracking URL {url}: {e}")
            status.crawl_errors.append(str(e))
        
        return status
    
    async def _check_url_indexed(self, url: str) -> bool:
        """Check if URL is indexed (simplified implementation)."""
        try:
            # In production, this would use Google Search Console API
            # or perform site: search queries
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def _analyze_page_indexability(self, url: str) -> Dict[str, Any]:
        """Analyze page for indexability factors."""
        analysis = {
            'http_status': None,
            'meta_robots': None,
            'canonical_url': None,
            'content_hash': None,
            'page_depth': None,
            'internal_links_count': 0,
            'external_links_count': 0,
            'indexation_issues': [],
            'crawl_errors': []
        }
        
        try:
            response = requests.get(url, timeout=15)
            analysis['http_status'] = response.status_code
            
            if response.status_code != 200:
                analysis['crawl_errors'].append(f'HTTP {response.status_code} error')
                return analysis
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check meta robots
            meta_robots = soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
            if meta_robots:
                robots_content = meta_robots.get('content', '').lower()
                analysis['meta_robots'] = robots_content
                
                if 'noindex' in robots_content:
                    analysis['indexation_issues'].append('Page has noindex directive')
            
            # Check canonical URL
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if canonical:
                analysis['canonical_url'] = canonical.get('href')
            
            # Calculate content hash
            content = soup.get_text()
            analysis['content_hash'] = hashlib.md5(content.encode()).hexdigest()
            
            # Count links
            domain = urlparse(url).netloc
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/') or domain in href:
                    analysis['internal_links_count'] += 1
                elif href.startswith('http'):
                    analysis['external_links_count'] += 1
            
            # Calculate page depth (simplified)
            path_parts = urlparse(url).path.strip('/').split('/')
            analysis['page_depth'] = len([part for part in path_parts if part])
            
        except Exception as e:
            analysis['crawl_errors'].append(str(e))
        
        return analysis
    
    async def _store_indexation_status(self, status: IndexationStatus):
        """Store indexation status in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO indexation_status 
                (url, domain, indexed, last_checked, http_status, meta_robots, 
                 canonical_url, content_hash, page_depth, internal_links_count, 
                 external_links_count, indexation_issues, crawl_errors, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                status.url,
                urlparse(status.url).netloc,
                status.indexed,
                status.timestamp.isoformat(),
                status.http_status,
                status.meta_robots,
                status.canonical_url,
                status.content_hash,
                status.page_depth,
                status.internal_links_count,
                status.external_links_count,
                json.dumps(status.indexation_issues),
                json.dumps(status.crawl_errors),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
    
    async def get_domain_indexation_report(self, domain: str) -> Dict[str, Any]:
        """Get comprehensive indexation report for domain."""
        with sqlite3.connect(self.db_path) as conn:
            # Get overall statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_urls,
                    SUM(CASE WHEN indexed THEN 1 ELSE 0 END) as indexed_urls,
                    AVG(CASE WHEN indexed THEN 1.0 ELSE 0.0 END) as indexation_rate
                FROM indexation_status 
                WHERE domain = ?
            """, (domain,))
            
            stats = cursor.fetchone()
            
            # Get page depth distribution
            cursor = conn.execute("""
                SELECT page_depth, COUNT(*) as count
                FROM indexation_status 
                WHERE domain = ? AND page_depth IS NOT NULL
                GROUP BY page_depth
                ORDER BY page_depth
            """, (domain,))
            
            depth_distribution = dict(cursor.fetchall())
            
            # Get common issues
            cursor = conn.execute("""
                SELECT indexation_issues, COUNT(*) as count
                FROM indexation_status 
                WHERE domain = ? AND indexation_issues != '[]'
                GROUP BY indexation_issues
                ORDER BY count DESC
                LIMIT 10
            """, (domain,))
            
            common_issues = []
            for issues_json, count in cursor.fetchall():
                try:
                    issues = json.loads(issues_json)
                    for issue in issues:
                        common_issues.append({'issue': issue, 'count': count})
                except:
                    pass
        
        return {
            'domain': domain,
            'total_urls': stats[0] if stats[0] else 0,
            'indexed_urls': stats[1] if stats[1] else 0,
            'indexation_rate': stats[2] if stats[2] else 0.0,
            'depth_distribution': depth_distribution,
            'common_issues': common_issues
        }


class IndexationManager:
    """Comprehensive indexation management for Ainflue creator economy."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Initialize components
        self.robots_analyzer = RobotsTxtAnalyzer()
        self.sitemap_analyzer = SitemapAnalyzer()
        self.indexation_tracker = IndexationTracker()
    
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
    
    async def run_comprehensive_indexation_audit(self, domain: str, 
                                                urls: Optional[List[str]] = None) -> IndexationReport:
        """Run comprehensive indexation audit."""
        self.logger.info(f"Starting comprehensive indexation audit for {domain}")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # 1. Analyze robots.txt
            self.logger.info("Analyzing robots.txt...")
            robots_analysis = await self.robots_analyzer.analyze_robots_txt(domain)
            
            # 2. Analyze sitemaps
            self.logger.info("Analyzing sitemaps...")
            sitemap_urls = robots_analysis.get('sitemaps', [])
            sitemap_analysis = await self.sitemap_analyzer.analyze_sitemaps(domain, sitemap_urls)
            
            # 3. Discover URLs if not provided
            if urls is None:
                urls = await self._discover_urls(domain, sitemap_analysis)
            
            # 4. Track indexation status
            self.logger.info(f"Tracking indexation for {len(urls)} URLs...")
            url_statuses = []
            
            # Process URLs in batches for better performance
            batch_size = 10
            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]
                batch_tasks = [self.indexation_tracker.track_url_indexation(url) for url in batch]
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, IndexationStatus):
                        url_statuses.append(result)
                    else:
                        self.logger.error(f"Error processing URL: {result}")
            
            # 5. Analyze crawl budget
            crawl_budget_analysis = await self._analyze_crawl_budget(domain, url_statuses, robots_analysis)
            
            # 6. Generate indexation issues
            indexation_issues = await self._identify_indexation_issues(url_statuses, robots_analysis, sitemap_analysis)
            
            # 7. Calculate metrics
            total_urls = len(url_statuses)
            indexed_urls = len([s for s in url_statuses if s.indexed])
            indexation_rate = (indexed_urls / total_urls * 100) if total_urls > 0 else 0
            
            # 8. Generate recommendations
            recommendations = await self._generate_indexation_recommendations(
                robots_analysis, sitemap_analysis, crawl_budget_analysis, indexation_issues
            )
            
            # 9. Identify technical issues
            technical_issues = await self._identify_technical_issues(url_statuses)
            
            # 10. Performance metrics
            performance_metrics = {
                'audit_duration': (datetime.now(timezone.utc) - start_time).total_seconds(),
                'urls_processed': len(url_statuses),
                'robots_score': robots_analysis.get('crawl_budget_impact', {}).get('efficiency_score', 0),
                'sitemap_score': sitemap_analysis.get('indexation_potential', 0)
            }
            
            # Create comprehensive report
            report = IndexationReport(
                domain=domain,
                report_timestamp=start_time,
                total_urls=total_urls,
                indexed_urls=indexed_urls,
                not_indexed_urls=total_urls - indexed_urls,
                indexation_rate=indexation_rate,
                crawl_budget_analysis=crawl_budget_analysis,
                indexation_issues=indexation_issues,
                url_statuses=url_statuses,
                recommendations=recommendations,
                technical_issues=technical_issues,
                performance_metrics=performance_metrics
            )
            
            self.logger.info(f"Indexation audit completed. Indexation rate: {indexation_rate:.1f}%")
            return report
            
        except Exception as e:
            self.logger.error(f"Error during indexation audit: {e}")
            raise
    
    async def _discover_urls(self, domain: str, sitemap_analysis: Dict[str, Any]) -> List[str]:
        """Discover URLs to analyze."""
        urls = [f"https://{domain}"]
        
        # Extract URLs from sitemaps
        for sitemap_info in sitemap_analysis.get('sitemap_analyses', []):
            if sitemap_info.get('type') == 'urlset':
                # In a real implementation, we would extract actual URLs from the sitemap
                # For now, we'll simulate by adding some common pages
                estimated_urls = sitemap_info.get('url_count', 0)
                for i in range(min(estimated_urls, 50)):  # Limit for demo
                    urls.append(f"https://{domain}/page-{i}")
        
        return urls[:100]  # Limit for performance
    
    async def _analyze_crawl_budget(self, domain: str, url_statuses: List[IndexationStatus], 
                                  robots_analysis: Dict[str, Any]) -> CrawlBudgetAnalysis:
        """Analyze crawl budget efficiency."""
        total_pages = len(url_statuses)
        crawlable_pages = 0
        blocked_pages = 0
        orphaned_pages = 0
        redirect_pages = 0
        error_pages = 0
        
        page_depth_distribution = defaultdict(int)
        
        for status in url_statuses:
            if status.http_status == 200:
                crawlable_pages += 1
            elif status.http_status in [301, 302, 307, 308]:
                redirect_pages += 1
            elif status.http_status and status.http_status >= 400:
                error_pages += 1
            
            if status.meta_robots and 'noindex' in status.meta_robots:
                blocked_pages += 1
            
            if status.internal_links_count == 0:
                orphaned_pages += 1
            
            if status.page_depth is not None:
                page_depth_distribution[status.page_depth] += 1
        
        crawl_efficiency = (crawlable_pages / total_pages * 100) if total_pages > 0 else 0
        budget_utilization = robots_analysis.get('crawl_budget_impact', {}).get('efficiency_score', 0)
        
        recommendations = []
        if blocked_pages > total_pages * 0.1:
            recommendations.append('High number of blocked pages may waste crawl budget')
        if orphaned_pages > 0:
            recommendations.append('Orphaned pages found - improve internal linking')
        if redirect_pages > total_pages * 0.05:
            recommendations.append('Many redirect pages - consider consolidating URLs')
        if error_pages > 0:
            recommendations.append('Fix pages returning HTTP errors')
        
        return CrawlBudgetAnalysis(
            domain=domain,
            total_pages=total_pages,
            crawlable_pages=crawlable_pages,
            blocked_pages=blocked_pages,
            orphaned_pages=orphaned_pages,
            redirect_pages=redirect_pages,
            error_pages=error_pages,
            crawl_efficiency=crawl_efficiency,
            budget_utilization=budget_utilization,
            recommendations=recommendations,
            page_depth_distribution=dict(page_depth_distribution)
        )
    
    async def _identify_indexation_issues(self, url_statuses: List[IndexationStatus], 
                                        robots_analysis: Dict[str, Any], 
                                        sitemap_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify indexation issues."""
        issues = []
        
        # Analyze URL-level issues
        not_indexed_count = len([s for s in url_statuses if not s.indexed])
        if not_indexed_count > 0:
            issues.append({
                'type': 'not_indexed_urls',
                'severity': 'high',
                'count': not_indexed_count,
                'description': f'{not_indexed_count} URLs are not indexed',
                'impact': 'Content not discoverable in search results'
            })
        
        # Check for meta robots issues
        noindex_count = len([s for s in url_statuses if s.meta_robots and 'noindex' in s.meta_robots])
        if noindex_count > 0:
            issues.append({
                'type': 'noindex_directives',
                'severity': 'medium',
                'count': noindex_count,
                'description': f'{noindex_count} URLs have noindex directives',
                'impact': 'Pages intentionally excluded from search results'
            })
        
        # Check for HTTP errors
        error_count = len([s for s in url_statuses if s.http_status and s.http_status >= 400])
        if error_count > 0:
            issues.append({
                'type': 'http_errors',
                'severity': 'high',
                'count': error_count,
                'description': f'{error_count} URLs return HTTP errors',
                'impact': 'Search engines cannot crawl error pages'
            })
        
        # Add robots.txt issues
        for issue in robots_analysis.get('issues', []):
            issues.append({
                'type': f"robots_{issue['type']}",
                'severity': issue['severity'],
                'description': issue['description'],
                'impact': issue.get('impact', 'May affect crawling efficiency')
            })
        
        # Add sitemap issues
        for sitemap_info in sitemap_analysis.get('sitemap_analyses', []):
            for issue in sitemap_info.get('issues', []):
                issues.append({
                    'type': f"sitemap_{issue['type']}",
                    'severity': issue['severity'],
                    'description': issue['description'],
                    'impact': 'May affect URL discovery and indexation'
                })
        
        return issues
    
    async def _identify_technical_issues(self, url_statuses: List[IndexationStatus]) -> List[Dict[str, Any]]:
        """Identify technical issues affecting indexation."""
        issues = []
        
        # Check for duplicate content
        content_hashes = defaultdict(list)
        for status in url_statuses:
            if status.content_hash:
                content_hashes[status.content_hash].append(status.url)
        
        duplicate_groups = {hash_val: urls for hash_val, urls in content_hashes.items() if len(urls) > 1}
        if duplicate_groups:
            issues.append({
                'type': 'duplicate_content',
                'severity': 'medium',
                'count': len(duplicate_groups),
                'description': f'{len(duplicate_groups)} groups of duplicate content found',
                'details': list(duplicate_groups.values())[:5]  # Show first 5 groups
            })
        
        # Check for deep page levels
        deep_pages = [s for s in url_statuses if s.page_depth and s.page_depth > 4]
        if deep_pages:
            issues.append({
                'type': 'deep_page_levels',
                'severity': 'low',
                'count': len(deep_pages),
                'description': f'{len(deep_pages)} pages are more than 4 levels deep',
                'impact': 'Deep pages may be crawled less frequently'
            })
        
        return issues
    
    async def _generate_indexation_recommendations(self, robots_analysis: Dict[str, Any], 
                                                 sitemap_analysis: Dict[str, Any],
                                                 crawl_budget_analysis: CrawlBudgetAnalysis,
                                                 indexation_issues: List[Dict[str, Any]]) -> List[str]:
        """Generate comprehensive indexation recommendations."""
        recommendations = []
        
        # High-priority recommendations
        critical_issues = [issue for issue in indexation_issues if issue.get('severity') == 'critical']
        if critical_issues:
            recommendations.append(f"CRITICAL: Fix {len(critical_issues)} critical indexation issues immediately")
        
        # Robots.txt recommendations
        recommendations.extend(robots_analysis.get('crawl_budget_impact', {}).get('recommendations', []))
        
        # Sitemap recommendations
        recommendations.extend(sitemap_analysis.get('recommendations', []))
        
        # Crawl budget recommendations
        recommendations.extend(crawl_budget_analysis.recommendations)
        
        # General recommendations
        if crawl_budget_analysis.crawl_efficiency < 80:
            recommendations.append('Improve crawl efficiency by fixing technical issues')
        
        if crawl_budget_analysis.orphaned_pages > 0:
            recommendations.append('Implement better internal linking strategy to reduce orphaned pages')
        
        return list(set(recommendations))  # Remove duplicates
    
    async def generate_indexation_report(self, report: IndexationReport, format: str = 'html') -> str:
        """Generate comprehensive indexation report."""
        if format == 'html':
            return await self._generate_html_report(report)
        elif format == 'json':
            return await self._generate_json_report(report)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    async def _generate_html_report(self, report: IndexationReport) -> str:
        """Generate HTML indexation report."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Indexation Audit Report - {report.domain}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                .score {{ font-size: 48px; font-weight: bold; color: #28a745; }}
                .score.warning {{ color: #ffc107; }}
                .score.danger {{ color: #dc3545; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 2px solid #e9ecef; }}
                .issues {{ margin-top: 40px; }}
                .issue {{ margin: 15px 0; padding: 15px; border-radius: 8px; border-left: 5px solid #ccc; background: #fafafa; }}
                .critical {{ border-color: #dc3545; background: #f8d7da; }}
                .high {{ border-color: #fd7e14; background: #ffeaa7; }}
                .medium {{ border-color: #ffc107; background: #fff3cd; }}
                .low {{ border-color: #28a745; background: #d1edff; }}
                .recommendations {{ background: #e7f3ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .legal {{ font-size: 10px; color: #666; margin-top: 40px; text-align: center; border-top: 1px solid #eee; padding-top: 20px; }}
                .section {{ margin: 30px 0; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Indexation Audit Report</h1>
                <h2>{report.domain}</h2>
                <div class="score {'danger' if report.indexation_rate < 50 else 'warning' if report.indexation_rate < 80 else ''}">{report.indexation_rate:.1f}%</div>
                <p>Indexation Rate - Report generated on {report.report_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>📈 Total URLs</h3>
                    <div style="font-size: 24px; font-weight: bold;">{report.total_urls}</div>
                    <small>URLs Analyzed</small>
                </div>
                <div class="metric-card">
                    <h3>✅ Indexed URLs</h3>
                    <div style="font-size: 24px; font-weight: bold;">{report.indexed_urls}</div>
                    <small>Successfully Indexed</small>
                </div>
                <div class="metric-card">
                    <h3>⚠️ Not Indexed</h3>
                    <div style="font-size: 24px; font-weight: bold;">{report.not_indexed_urls}</div>
                    <small>Needs Attention</small>
                </div>
                <div class="metric-card">
                    <h3>🎯 Crawl Efficiency</h3>
                    <div style="font-size: 24px; font-weight: bold;">{report.crawl_budget_analysis.crawl_efficiency:.1f}%</div>
                    <small>Budget Utilization</small>
                </div>
            </div>
            
            <div class="section">
                <h2>🏗️ Crawl Budget Analysis</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <p><strong>Crawlable Pages:</strong> {report.crawl_budget_analysis.crawlable_pages}</p>
                    <p><strong>Blocked Pages:</strong> {report.crawl_budget_analysis.blocked_pages}</p>
                    <p><strong>Orphaned Pages:</strong> {report.crawl_budget_analysis.orphaned_pages}</p>
                    <p><strong>Redirect Pages:</strong> {report.crawl_budget_analysis.redirect_pages}</p>
                    <p><strong>Error Pages:</strong> {report.crawl_budget_analysis.error_pages}</p>
                </div>
            </div>
        """
        
        # Add issues section
        if report.indexation_issues:
            html_template += f"""
                <div class="section">
                    <h2>🚨 Indexation Issues ({len(report.indexation_issues)})</h2>
                    <div class="issues">
            """
            
            for issue in report.indexation_issues:
                severity = issue.get('severity', 'medium')
                html_template += f"""
                    <div class="issue {severity}">
                        <h3>{issue.get('type', 'Unknown Issue').replace('_', ' ').title()}</h3>
                        <p><strong>Severity:</strong> {severity.title()}</p>
                        <p><strong>Description:</strong> {issue.get('description', '')}</p>
                        <p><strong>Impact:</strong> {issue.get('impact', '')}</p>
                """
                
                if 'count' in issue:
                    html_template += f"<p><strong>Affected URLs:</strong> {issue['count']}</p>"
                
                html_template += "</div>"
            
            html_template += "</div></div>"
        
        # Add recommendations section
        if report.recommendations:
            html_template += """
                <div class="section">
                    <h2>💡 Recommendations</h2>
                    <div class="recommendations">
                        <ul>
            """
            
            for recommendation in report.recommendations:
                html_template += f"<li>{recommendation}</li>"
            
            html_template += """
                        </ul>
                    </div>
                </div>
            """
        
        html_template += f"""
            <div class="legal">
                <p>© 2025 Fahed Mlaiel (mlaiel@live.de) - Indexation Manager</p>
                <p>This indexation audit report was generated by Ainflue Indexation Manager</p>
                <p>📊 Audit Duration: {report.performance_metrics.get('audit_duration', 0):.2f} seconds</p>
                <p>📧 For enterprise indexation consulting: mlaiel@live.de</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    async def _generate_json_report(self, report: IndexationReport) -> str:
        """Generate JSON indexation report."""
        data = {
            'domain': report.domain,
            'report_timestamp': report.report_timestamp.isoformat(),
            'indexation_metrics': {
                'total_urls': report.total_urls,
                'indexed_urls': report.indexed_urls,
                'not_indexed_urls': report.not_indexed_urls,
                'indexation_rate': report.indexation_rate
            },
            'crawl_budget_analysis': {
                'total_pages': report.crawl_budget_analysis.total_pages,
                'crawlable_pages': report.crawl_budget_analysis.crawlable_pages,
                'blocked_pages': report.crawl_budget_analysis.blocked_pages,
                'orphaned_pages': report.crawl_budget_analysis.orphaned_pages,
                'crawl_efficiency': report.crawl_budget_analysis.crawl_efficiency,
                'budget_utilization': report.crawl_budget_analysis.budget_utilization
            },
            'issues': report.indexation_issues,
            'recommendations': report.recommendations,
            'technical_issues': report.technical_issues,
            'performance_metrics': report.performance_metrics,
            'summary': {
                'indexation_status': 'good' if report.indexation_rate >= 80 else 'needs_improvement' if report.indexation_rate >= 50 else 'poor',
                'critical_issues': len([i for i in report.indexation_issues if i.get('severity') == 'critical']),
                'high_issues': len([i for i in report.indexation_issues if i.get('severity') == 'high']),
                'medium_issues': len([i for i in report.indexation_issues if i.get('severity') == 'medium']),
                'low_issues': len([i for i in report.indexation_issues if i.get('severity') == 'low'])
            }
        }
        return json.dumps(data, indent=2)


# Usage Example
async def main():
    """Example usage of Indexation Manager."""
    
    # Initialize indexation manager
    indexation_manager = IndexationManager()
    
    try:
        domain = "example.com"  # Replace with actual domain
        
        print(f"\n=== Indexation Audit for {domain} ===")
        
        # Run comprehensive indexation audit
        report = await indexation_manager.run_comprehensive_indexation_audit(domain)
        
        print(f"Indexation Rate: {report.indexation_rate:.1f}%")
        print(f"Total URLs: {report.total_urls}")
        print(f"Indexed URLs: {report.indexed_urls}")
        print(f"Crawl Efficiency: {report.crawl_budget_analysis.crawl_efficiency:.1f}%")
        print(f"Issues Found: {len(report.indexation_issues)}")
        
        # Generate reports
        html_report = await indexation_manager.generate_indexation_report(report, 'html')
        json_report = await indexation_manager.generate_indexation_report(report, 'json')
        
        print("\n=== Indexation Reports Generated ===")
        
        # Show top recommendations
        if report.recommendations:
            print("\n=== Top Indexation Recommendations ===")
            for i, rec in enumerate(report.recommendations[:5], 1):
                print(f"{i}. {rec}")
        
    except Exception as e:
        print(f"Error during indexation audit: {e}")


if __name__ == "__main__":
    asyncio.run(main())