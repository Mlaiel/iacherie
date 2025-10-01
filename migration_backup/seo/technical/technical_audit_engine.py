"""Technical SEO Audit Engine
Comprehensive technical SEO audit automation for IA Chéries creator economy platform.

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
Security Expert: SEO Security Implementation
DevOps Engineer: Technical Infrastructure
Full-Stack Developer: Frontend/Backend Technical SEO
"""

import asyncio
import time
import json
import re
import ssl
import socket
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import dns.resolver
import whois
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import hashlib


@dataclass
class TechnicalIssue:
    """Technical SEO issue data structure."""
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    url: str
    impact: str
    recommendation: str
    code: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AuditResults:
    """Comprehensive audit results structure."""
    domain: str
    audit_timestamp: datetime
    overall_score: float
    issues: List[TechnicalIssue]
    performance_metrics: Dict[str, Any]
    crawlability_score: float
    indexation_score: float
    technical_score: float
    security_score: float
    mobile_score: float
    page_count: int
    audit_duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CrawlabilityAnalyzer:
    """Advanced crawlability analysis engine."""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.user_agents = {
            'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'bingbot': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.CrawlabilityAnalyzer')
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
        """Analyze robots.txt file comprehensively."""
        robots_url = f"https://{domain}/robots.txt"
        issues = []
        
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 404:
                issues.append({
                    'type': 'missing_robots',
                    'severity': 'medium',
                    'description': 'robots.txt file not found',
                    'recommendation': 'Create robots.txt file with proper directives'
                })
                return {'status': 'missing', 'issues': issues}
            
            if response.status_code != 200:
                issues.append({
                    'type': 'robots_error',
                    'severity': 'high',
                    'description': f'robots.txt returns {response.status_code}',
                    'recommendation': 'Fix robots.txt accessibility'
                })
                return {'status': 'error', 'issues': issues, 'code': response.status_code}
            
            robots_content = response.text
            lines = robots_content.strip().split('\n')
            
            # Analyze robots.txt structure
            user_agents_found = []
            sitemaps_found = []
            disallow_rules = []
            allow_rules = []
            crawl_delay_found = False
            
            current_user_agent = None
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                
                if line.lower().startswith('user-agent:'):
                    current_user_agent = line.split(':', 1)[1].strip()
                    user_agents_found.append(current_user_agent)
                elif line.lower().startswith('disallow:'):
                    disallow_path = line.split(':', 1)[1].strip()
                    disallow_rules.append({
                        'user_agent': current_user_agent,
                        'path': disallow_path
                    })
                elif line.lower().startswith('allow:'):
                    allow_path = line.split(':', 1)[1].strip()
                    allow_rules.append({
                        'user_agent': current_user_agent,
                        'path': allow_path
                    })
                elif line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemaps_found.append(sitemap_url)
                elif line.lower().startswith('crawl-delay:'):
                    crawl_delay_found = True
            
            # Check for common issues
            if not user_agents_found:
                issues.append({
                    'type': 'no_user_agent',
                    'severity': 'high',
                    'description': 'No User-agent directives found',
                    'recommendation': 'Add User-agent directives'
                })
            
            if not sitemaps_found:
                issues.append({
                    'type': 'no_sitemap',
                    'severity': 'medium',
                    'description': 'No sitemap directives found in robots.txt',
                    'recommendation': 'Add sitemap references to robots.txt'
                })
            
            # Check for overly restrictive rules
            for rule in disallow_rules:
                if rule['path'] == '/':
                    issues.append({
                        'type': 'blocking_all',
                        'severity': 'critical',
                        'description': f'Blocking all crawling for {rule["user_agent"]}',
                        'recommendation': 'Review disallow rules - blocking entire site'
                    })
            
            return {
                'status': 'valid',
                'content': robots_content,
                'user_agents': user_agents_found,
                'sitemaps': sitemaps_found,
                'disallow_rules': disallow_rules,
                'allow_rules': allow_rules,
                'crawl_delay': crawl_delay_found,
                'issues': issues
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing robots.txt: {e}")
            issues.append({
                'type': 'analysis_error',
                'severity': 'high',
                'description': f'Failed to analyze robots.txt: {str(e)}',
                'recommendation': 'Check network connectivity and domain accessibility'
            })
            return {'status': 'error', 'issues': issues}
    
    async def analyze_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """Analyze XML sitemap comprehensively."""
        issues = []
        
        try:
            response = requests.get(sitemap_url, timeout=15)
            if response.status_code != 200:
                return {
                    'status': 'error',
                    'code': response.status_code,
                    'issues': [{
                        'type': 'sitemap_error',
                        'severity': 'high',
                        'description': f'Sitemap returns {response.status_code}',
                        'recommendation': 'Fix sitemap accessibility'
                    }]
                }
            
            try:
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                # Check if it's a sitemap index
                if root.tag.endswith('sitemapindex'):
                    sitemaps = root.findall('.//ns:sitemap', namespace)
                    sitemap_urls = []
                    for sitemap in sitemaps:
                        loc = sitemap.find('ns:loc', namespace)
                        if loc is not None:
                            sitemap_urls.append(loc.text)
                    
                    return {
                        'status': 'index',
                        'type': 'sitemap_index',
                        'sitemap_count': len(sitemap_urls),
                        'sitemaps': sitemap_urls,
                        'issues': issues
                    }
                
                # Regular sitemap analysis
                urls = root.findall('.//ns:url', namespace)
                total_urls = len(urls)
                
                if total_urls == 0:
                    issues.append({
                        'type': 'empty_sitemap',
                        'severity': 'medium',
                        'description': 'Sitemap contains no URLs',
                        'recommendation': 'Add URLs to sitemap or remove empty sitemap'
                    })
                
                if total_urls > 50000:
                    issues.append({
                        'type': 'oversized_sitemap',
                        'severity': 'high',
                        'description': f'Sitemap contains {total_urls} URLs (limit: 50,000)',
                        'recommendation': 'Split sitemap or use sitemap index'
                    })
                
                # Analyze URL patterns
                url_analysis = {
                    'total_urls': total_urls,
                    'with_lastmod': 0,
                    'with_changefreq': 0,
                    'with_priority': 0,
                    'https_urls': 0,
                    'duplicate_urls': 0
                }
                
                seen_urls = set()
                for url_elem in urls:
                    loc = url_elem.find('ns:loc', namespace)
                    if loc is not None:
                        url = loc.text
                        if url in seen_urls:
                            url_analysis['duplicate_urls'] += 1
                        seen_urls.add(url)
                        
                        if url.startswith('https://'):
                            url_analysis['https_urls'] += 1
                    
                    if url_elem.find('ns:lastmod', namespace) is not None:
                        url_analysis['with_lastmod'] += 1
                    if url_elem.find('ns:changefreq', namespace) is not None:
                        url_analysis['with_changefreq'] += 1
                    if url_elem.find('ns:priority', namespace) is not None:
                        url_analysis['with_priority'] += 1
                
                if url_analysis['duplicate_urls'] > 0:
                    issues.append({
                        'type': 'duplicate_urls',
                        'severity': 'medium',
                        'description': f'{url_analysis["duplicate_urls"]} duplicate URLs found',
                        'recommendation': 'Remove duplicate URLs from sitemap'
                    })
                
                return {
                    'status': 'valid',
                    'type': 'urlset',
                    'analysis': url_analysis,
                    'issues': issues
                }
                
            except ET.ParseError as e:
                issues.append({
                    'type': 'xml_parse_error',
                    'severity': 'critical',
                    'description': f'Invalid XML structure: {str(e)}',
                    'recommendation': 'Fix XML syntax errors in sitemap'
                })
                return {'status': 'invalid_xml', 'issues': issues}
        
        except Exception as e:
            self.logger.error(f"Error analyzing sitemap: {e}")
            return {
                'status': 'error',
                'issues': [{
                    'type': 'analysis_error',
                    'severity': 'high',
                    'description': f'Failed to analyze sitemap: {str(e)}',
                    'recommendation': 'Check sitemap URL and network connectivity'
                }]
            }


class IndexationAnalyzer:
    """Advanced indexation status analysis."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.IndexationAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def check_indexation_status(self, urls: List[str]) -> Dict[str, Any]:
        """Check indexation status for multiple URLs."""
        results = {
            'total_checked': len(urls),
            'indexed': 0,
            'not_indexed': 0,
            'errors': 0,
            'url_results': {}
        }
        
        for url in urls[:100]:  # Limit to 100 URLs to avoid rate limiting
            try:
                # Check if URL is indexed using site: search
                search_query = f"site:{urlparse(url).netloc} inurl:{urlparse(url).path}"
                
                # Simulate indexation check (in real implementation, use Search Console API)
                indexed = await self._check_url_indexed(url)
                
                results['url_results'][url] = {
                    'indexed': indexed,
                    'checked_at': datetime.now(timezone.utc).isoformat()
                }
                
                if indexed:
                    results['indexed'] += 1
                else:
                    results['not_indexed'] += 1
                    
            except Exception as e:
                self.logger.error(f"Error checking indexation for {url}: {e}")
                results['errors'] += 1
                results['url_results'][url] = {
                    'error': str(e),
                    'checked_at': datetime.now(timezone.utc).isoformat()
                }
        
        return results
    
    async def _check_url_indexed(self, url: str) -> bool:
        """Check if a specific URL is indexed."""
        try:
            # Simplified check - in production, use Google Search Console API
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def analyze_meta_directives(self, html_content: str, url: str) -> Dict[str, Any]:
        """Analyze meta robots and indexation directives."""
        soup = BeautifulSoup(html_content, 'html.parser')
        issues = []
        
        # Check meta robots
        meta_robots = soup.find('meta', attrs={'name': re.compile(r'^robots$', re.I)})
        robots_content = ''
        if meta_robots:
            robots_content = meta_robots.get('content', '').lower()
        
        # Check X-Robots-Tag header would be checked in HTTP headers
        
        analysis = {
            'meta_robots_found': bool(meta_robots),
            'robots_content': robots_content,
            'blocking_indexation': False,
            'blocking_following': False,
            'issues': []
        }
        
        if 'noindex' in robots_content:
            analysis['blocking_indexation'] = True
            issues.append({
                'type': 'noindex_directive',
                'severity': 'high',
                'description': 'Page has noindex directive',
                'recommendation': 'Remove noindex if page should be indexed'
            })
        
        if 'nofollow' in robots_content:
            analysis['blocking_following'] = True
            issues.append({
                'type': 'nofollow_directive',
                'severity': 'medium',
                'description': 'Page has nofollow directive',
                'recommendation': 'Review nofollow usage for link equity'
            })
        
        # Check canonical tag
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            canonical_url = canonical.get('href', '')
            if canonical_url and canonical_url != url:
                analysis['canonical_different'] = True
                analysis['canonical_url'] = canonical_url
                # This might not be an issue if it's intentional
        
        analysis['issues'] = issues
        return analysis


class SecurityAnalyzer:
    """Advanced security analysis for SEO impact."""
    
    def __init__(self):
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.SecurityAnalyzer')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def analyze_ssl_certificate(self, domain: str) -> Dict[str, Any]:
        """Comprehensive SSL certificate analysis."""
        issues = []
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Analyze certificate details
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    now = datetime.now()
                    
                    days_until_expiry = (not_after - now).days
                    
                    if days_until_expiry < 30:
                        issues.append({
                            'type': 'ssl_expiring_soon',
                            'severity': 'high',
                            'description': f'SSL certificate expires in {days_until_expiry} days',
                            'recommendation': 'Renew SSL certificate before expiration'
                        })
                    elif days_until_expiry < 90:
                        issues.append({
                            'type': 'ssl_expiring',
                            'severity': 'medium',
                            'description': f'SSL certificate expires in {days_until_expiry} days',
                            'recommendation': 'Plan SSL certificate renewal'
                        })
                    
                    # Check subject alternative names
                    san_list = []
                    for san in cert.get('subjectAltName', []):
                        if san[0] == 'DNS':
                            san_list.append(san[1])
                    
                    return {
                        'valid': True,
                        'issuer': dict(cert.get('issuer', [])),
                        'subject': dict(cert.get('subject', [])),
                        'expires': not_after.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'san_list': san_list,
                        'issues': issues
                    }
                    
        except ssl.SSLError as e:
            issues.append({
                'type': 'ssl_error',
                'severity': 'critical',
                'description': f'SSL certificate error: {str(e)}',
                'recommendation': 'Fix SSL certificate configuration'
            })
            return {'valid': False, 'error': str(e), 'issues': issues}
        except Exception as e:
            self.logger.error(f"Error analyzing SSL: {e}")
            issues.append({
                'type': 'ssl_analysis_error',
                'severity': 'high',
                'description': f'Failed to analyze SSL: {str(e)}',
                'recommendation': 'Check domain accessibility and SSL configuration'
            })
            return {'valid': False, 'error': str(e), 'issues': issues}
    
    async def analyze_security_headers(self, url: str) -> Dict[str, Any]:
        """Analyze security headers impact on SEO."""
        issues = []
        
        try:
            response = requests.head(url, timeout=10)
            headers = response.headers
            
            security_headers = {
                'strict-transport-security': headers.get('Strict-Transport-Security'),
                'content-security-policy': headers.get('Content-Security-Policy'),
                'x-frame-options': headers.get('X-Frame-Options'),
                'x-content-type-options': headers.get('X-Content-Type-Options'),
                'referrer-policy': headers.get('Referrer-Policy'),
                'x-robots-tag': headers.get('X-Robots-Tag')
            }
            
            # Check for missing security headers
            if not security_headers['strict-transport-security']:
                issues.append({
                    'type': 'missing_hsts',
                    'severity': 'medium',
                    'description': 'Missing HSTS header',
                    'recommendation': 'Implement HSTS for better security and SEO trust'
                })
            
            if not security_headers['x-frame-options']:
                issues.append({
                    'type': 'missing_xframe',
                    'severity': 'low',
                    'description': 'Missing X-Frame-Options header',
                    'recommendation': 'Add X-Frame-Options to prevent clickjacking'
                })
            
            # Check X-Robots-Tag for SEO impact
            if security_headers['x-robots-tag']:
                x_robots = security_headers['x-robots-tag'].lower()
                if 'noindex' in x_robots:
                    issues.append({
                        'type': 'xrobots_noindex',
                        'severity': 'high',
                        'description': 'X-Robots-Tag contains noindex',
                        'recommendation': 'Review X-Robots-Tag directive for indexation'
                    })
            
            return {
                'headers': security_headers,
                'secure': len([h for h in security_headers.values() if h]) >= 3,
                'issues': issues
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing security headers: {e}")
            return {
                'error': str(e),
                'issues': [{
                    'type': 'header_analysis_error',
                    'severity': 'medium',
                    'description': f'Failed to analyze security headers: {str(e)}',
                    'recommendation': 'Check URL accessibility'
                }]
            }


class TechnicalAuditEngine:
    """Comprehensive technical SEO audit engine for IA Chéries creator economy."""
    
    def __init__(self, max_workers: int = 10, selenium_headless: bool = True):
        self.max_workers = max_workers
        self.selenium_headless = selenium_headless
        self.logger = self._setup_logging()
        
        # Initialize analyzers
        self.crawlability_analyzer = CrawlabilityAnalyzer()
        self.indexation_analyzer = IndexationAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        
        # Performance tracking
        self.start_time = None
        self.pages_audited = 0
        
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
    
    async def run_comprehensive_audit(self, domain: str, 
                                    urls: Optional[List[str]] = None,
                                    max_pages: int = 100) -> AuditResults:
        """Run comprehensive technical SEO audit."""
        self.start_time = time.time()
        self.logger.info(f"Starting comprehensive technical audit for {domain}")
        
        all_issues = []
        performance_metrics = {}
        
        try:
            # 1. Crawlability Analysis
            self.logger.info("Analyzing crawlability...")
            robots_analysis = await self.crawlability_analyzer.analyze_robots_txt(domain)
            crawlability_issues = robots_analysis.get('issues', [])
            
            # Analyze sitemaps
            if 'sitemaps' in robots_analysis:
                for sitemap_url in robots_analysis['sitemaps']:
                    sitemap_analysis = await self.crawlability_analyzer.analyze_sitemap(sitemap_url)
                    crawlability_issues.extend(sitemap_analysis.get('issues', []))
            
            # 2. Security Analysis
            self.logger.info("Analyzing security...")
            ssl_analysis = await self.security_analyzer.analyze_ssl_certificate(domain)
            security_headers = await self.security_analyzer.analyze_security_headers(f"https://{domain}")
            
            security_issues = ssl_analysis.get('issues', []) + security_headers.get('issues', [])
            
            # 3. Page-level Analysis
            if urls is None:
                # Discover URLs from sitemap or crawl
                urls = await self._discover_urls(domain, max_pages)
            
            page_issues = await self._analyze_pages(urls[:max_pages])
            
            # 4. Indexation Analysis
            self.logger.info("Analyzing indexation...")
            indexation_results = await self.indexation_analyzer.check_indexation_status(urls[:50])
            
            # Combine all issues
            all_issues.extend([
                TechnicalIssue(
                    category='crawlability',
                    severity=issue.get('severity', 'medium'),
                    title=issue.get('type', 'Unknown Issue'),
                    description=issue.get('description', ''),
                    url=f"https://{domain}",
                    impact=self._calculate_impact(issue.get('severity', 'medium')),
                    recommendation=issue.get('recommendation', ''),
                    code=issue.get('code')
                ) for issue in crawlability_issues
            ])
            
            all_issues.extend([
                TechnicalIssue(
                    category='security',
                    severity=issue.get('severity', 'medium'),
                    title=issue.get('type', 'Unknown Issue'),
                    description=issue.get('description', ''),
                    url=f"https://{domain}",
                    impact=self._calculate_impact(issue.get('severity', 'medium')),
                    recommendation=issue.get('recommendation', ''),
                    code=issue.get('code')
                ) for issue in security_issues
            ])
            
            all_issues.extend(page_issues)
            
            # Calculate scores
            crawlability_score = self._calculate_score(crawlability_issues)
            security_score = self._calculate_score(security_issues)
            indexation_score = max(0, 100 - (indexation_results['not_indexed'] / max(1, indexation_results['total_checked']) * 100))
            
            # Overall performance metrics
            performance_metrics = {
                'robots_analysis': robots_analysis,
                'ssl_analysis': ssl_analysis,
                'security_headers': security_headers,
                'indexation_results': indexation_results,
                'pages_analyzed': len(urls)
            }
            
            # Calculate scores
            technical_score = (crawlability_score + security_score) / 2
            overall_score = (crawlability_score + security_score + indexation_score) / 3
            
            audit_duration = time.time() - self.start_time
            
            return AuditResults(
                domain=domain,
                audit_timestamp=datetime.now(timezone.utc),
                overall_score=overall_score,
                issues=all_issues,
                performance_metrics=performance_metrics,
                crawlability_score=crawlability_score,
                indexation_score=indexation_score,
                technical_score=technical_score,
                security_score=security_score,
                mobile_score=85.0,  # Placeholder - would be calculated from actual mobile analysis
                page_count=len(urls),
                audit_duration=audit_duration
            )
            
        except Exception as e:
            self.logger.error(f"Error during comprehensive audit: {e}")
            raise
    
    async def _discover_urls(self, domain: str, max_urls: int) -> List[str]:
        """Discover URLs to audit."""
        urls = [f"https://{domain}"]
        
        # Try to get URLs from sitemap
        try:
            robots_response = requests.get(f"https://{domain}/robots.txt", timeout=10)
            if robots_response.status_code == 200:
                for line in robots_response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemap_urls = await self._extract_urls_from_sitemap(sitemap_url)
                        urls.extend(sitemap_urls[:max_urls-1])
                        break
        except:
            pass
        
        return urls[:max_urls]
    
    async def _extract_urls_from_sitemap(self, sitemap_url: str) -> List[str]:
        """Extract URLs from sitemap."""
        urls = []
        try:
            response = requests.get(sitemap_url, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                
                for url_elem in root.findall('.//ns:url', namespace):
                    loc = url_elem.find('ns:loc', namespace)
                    if loc is not None:
                        urls.append(loc.text)
        except:
            pass
        
        return urls
    
    async def _analyze_pages(self, urls: List[str]) -> List[TechnicalIssue]:
        """Analyze individual pages for technical issues."""
        issues = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self._analyze_single_page, url): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    page_issues = future.result()
                    issues.extend(page_issues)
                    self.pages_audited += 1
                except Exception as e:
                    self.logger.error(f"Error analyzing {url}: {e}")
                    issues.append(TechnicalIssue(
                        category='page_analysis',
                        severity='medium',
                        title='Page Analysis Error',
                        description=f'Failed to analyze page: {str(e)}',
                        url=url,
                        impact='Medium - Page cannot be fully audited',
                        recommendation='Check page accessibility and network connectivity'
                    ))
        
        return issues
    
    def _analyze_single_page(self, url: str) -> List[TechnicalIssue]:
        """Analyze a single page for technical issues."""
        issues = []
        
        try:
            # Basic HTTP analysis
            response = requests.get(url, timeout=15)
            
            # Check status code
            if response.status_code != 200:
                issues.append(TechnicalIssue(
                    category='http_status',
                    severity='high' if response.status_code >= 400 else 'medium',
                    title=f'HTTP {response.status_code} Error',
                    description=f'Page returns {response.status_code} status code',
                    url=url,
                    impact=f'{"High" if response.status_code >= 400 else "Medium"} - Page not accessible',
                    recommendation='Fix server configuration or redirect issues',
                    code=str(response.status_code)
                ))
                return issues
            
            # Analyze HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check title tag
            title = soup.find('title')
            if not title or not title.get_text().strip():
                issues.append(TechnicalIssue(
                    category='meta_tags',
                    severity='high',
                    title='Missing Title Tag',
                    description='Page is missing title tag',
                    url=url,
                    impact='High - Critical for SEO rankings',
                    recommendation='Add unique, descriptive title tag'
                ))
            elif len(title.get_text()) > 60:
                issues.append(TechnicalIssue(
                    category='meta_tags',
                    severity='medium',
                    title='Title Tag Too Long',
                    description=f'Title tag is {len(title.get_text())} characters (recommended: <60)',
                    url=url,
                    impact='Medium - May be truncated in search results',
                    recommendation='Shorten title tag to under 60 characters'
                ))
            
            # Check meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc or not meta_desc.get('content', '').strip():
                issues.append(TechnicalIssue(
                    category='meta_tags',
                    severity='medium',
                    title='Missing Meta Description',
                    description='Page is missing meta description',
                    url=url,
                    impact='Medium - Missed opportunity for click-through optimization',
                    recommendation='Add compelling meta description (150-160 characters)'
                ))
            elif len(meta_desc.get('content', '')) > 160:
                issues.append(TechnicalIssue(
                    category='meta_tags',
                    severity='low',
                    title='Meta Description Too Long',
                    description=f'Meta description is {len(meta_desc.get("content", ""))} characters',
                    url=url,
                    impact='Low - May be truncated in search results',
                    recommendation='Shorten meta description to 150-160 characters'
                ))
            
            # Check heading structure
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 0:
                issues.append(TechnicalIssue(
                    category='content_structure',
                    severity='medium',
                    title='Missing H1 Tag',
                    description='Page is missing H1 heading tag',
                    url=url,
                    impact='Medium - Important for content hierarchy and SEO',
                    recommendation='Add descriptive H1 tag for main page topic'
                ))
            elif len(h1_tags) > 1:
                issues.append(TechnicalIssue(
                    category='content_structure',
                    severity='low',
                    title='Multiple H1 Tags',
                    description=f'Page has {len(h1_tags)} H1 tags (recommended: 1)',
                    url=url,
                    impact='Low - May dilute topic focus',
                    recommendation='Use only one H1 tag per page'
                ))
            
            # Check images for alt text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if images_without_alt:
                issues.append(TechnicalIssue(
                    category='accessibility',
                    severity='medium',
                    title='Images Missing Alt Text',
                    description=f'{len(images_without_alt)} images missing alt text',
                    url=url,
                    impact='Medium - Poor accessibility and missed SEO opportunity',
                    recommendation='Add descriptive alt text to all images'
                ))
            
            # Check internal links
            internal_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/') or urlparse(url).netloc in href:
                    internal_links.append(href)
            
            if len(internal_links) < 3:
                issues.append(TechnicalIssue(
                    category='internal_linking',
                    severity='low',
                    title='Few Internal Links',
                    description=f'Page has only {len(internal_links)} internal links',
                    url=url,
                    impact='Low - May impact crawlability and user navigation',
                    recommendation='Add relevant internal links to improve navigation'
                ))
            
        except Exception as e:
            issues.append(TechnicalIssue(
                category='page_analysis',
                severity='medium',
                title='Page Analysis Error',
                description=f'Failed to analyze page: {str(e)}',
                url=url,
                impact='Medium - Page cannot be fully audited',
                recommendation='Check page accessibility and network connectivity'
            ))
        
        return issues
    
    def _calculate_impact(self, severity: str) -> str:
        """Calculate impact description based on severity."""
        impact_map = {
            'critical': 'Critical - Immediate action required',
            'high': 'High - Significant SEO impact',
            'medium': 'Medium - Moderate SEO impact',
            'low': 'Low - Minor SEO impact'
        }
        return impact_map.get(severity, 'Unknown impact')
    
    def _calculate_score(self, issues: List[Dict]) -> float:
        """Calculate score based on issues."""
        if not issues:
            return 100.0
        
        severity_weights = {
            'critical': 20,
            'high': 10,
            'medium': 5,
            'low': 1
        }
        
        total_penalty = sum(severity_weights.get(issue.get('severity', 'medium'), 5) for issue in issues)
        score = max(0, 100 - total_penalty)
        return score
    
    async def export_audit_results(self, results: AuditResults, format: str = 'json') -> str:
        """Export audit results to various formats."""
        if format == 'json':
            return await self._export_json(results)
        elif format == 'html':
            return await self._export_html(results)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def _export_json(self, results: AuditResults) -> str:
        """Export results as JSON."""
        data = {
            'domain': results.domain,
            'audit_timestamp': results.audit_timestamp.isoformat(),
            'overall_score': results.overall_score,
            'scores': {
                'crawlability': results.crawlability_score,
                'indexation': results.indexation_score,
                'technical': results.technical_score,
                'security': results.security_score,
                'mobile': results.mobile_score
            },
            'issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'title': issue.title,
                    'description': issue.description,
                    'url': issue.url,
                    'impact': issue.impact,
                    'recommendation': issue.recommendation,
                    'timestamp': issue.timestamp.isoformat()
                } for issue in results.issues
            ],
            'performance_metrics': results.performance_metrics,
            'summary': {
                'page_count': results.page_count,
                'audit_duration': results.audit_duration,
                'total_issues': len(results.issues),
                'critical_issues': len([i for i in results.issues if i.severity == 'critical']),
                'high_issues': len([i for i in results.issues if i.severity == 'high']),
                'medium_issues': len([i for i in results.issues if i.severity == 'medium']),
                'low_issues': len([i for i in results.issues if i.severity == 'low'])
            }
        }
        return json.dumps(data, indent=2)
    
    async def _export_html(self, results: AuditResults) -> str:
        """Export results as HTML report."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technical SEO Audit Report - {results.domain}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .score {{ font-size: 48px; font-weight: bold; color: #2E8B57; }}
                .scores-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
                .score-card {{ background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }}
                .issues {{ margin-top: 40px; }}
                .issue {{ margin: 20px 0; padding: 15px; border-left: 4px solid #ccc; background: #fafafa; }}
                .critical {{ border-color: #d32f2f; }}
                .high {{ border-color: #f57c00; }}
                .medium {{ border-color: #fbc02d; }}
                .low {{ border-color: #388e3c; }}
                .legal {{ font-size: 10px; color: #666; margin-top: 40px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Technical SEO Audit Report</h1>
                <h2>{results.domain}</h2>
                <div class="score">{results.overall_score:.1f}/100</div>
                <p>Audit completed on {results.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="scores-grid">
                <div class="score-card">
                    <h3>Crawlability</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.crawlability_score:.1f}</div>
                </div>
                <div class="score-card">
                    <h3>Indexation</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.indexation_score:.1f}</div>
                </div>
                <div class="score-card">
                    <h3>Technical</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.technical_score:.1f}</div>
                </div>
                <div class="score-card">
                    <h3>Security</h3>
                    <div style="font-size: 24px; font-weight: bold;">{results.security_score:.1f}</div>
                </div>
            </div>
            
            <div class="issues">
                <h2>Issues Found ({len(results.issues)})</h2>
        """
        
        for issue in sorted(results.issues, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x.severity]):
            html_template += f"""
                <div class="issue {issue.severity}">
                    <h3>{issue.title}</h3>
                    <p><strong>Severity:</strong> {issue.severity.title()}</p>
                    <p><strong>URL:</strong> {issue.url}</p>
                    <p><strong>Description:</strong> {issue.description}</p>
                    <p><strong>Impact:</strong> {issue.impact}</p>
                    <p><strong>Recommendation:</strong> {issue.recommendation}</p>
                </div>
            """
        
        html_template += f"""
            </div>
            
            <div class="legal">
                <p>© 2025 Fahed Mlaiel (mlaiel@live.de) - Technical SEO Audit Engine</p>
                <p>Report generated by IA Chéries Technical SEO Audit Engine - All rights reserved</p>
                <p>Audit Duration: {results.audit_duration:.2f} seconds | Pages Analyzed: {results.page_count}</p>
            </div>
        </body>
        </html>
        """
        
        return html_template


class AuditScheduler:
    """Automated audit scheduling for continuous monitoring."""
    
    def __init__(self, audit_engine: TechnicalAuditEngine):
        self.audit_engine = audit_engine
        self.logger = self._setup_logging()
        self.scheduled_audits = {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(f'{__name__}.AuditScheduler')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    async def schedule_audit(self, domain: str, interval_hours: int = 24) -> str:
        """Schedule regular audits for a domain."""
        audit_id = hashlib.md5(f"{domain}_{interval_hours}".encode()).hexdigest()[:8]
        
        self.scheduled_audits[audit_id] = {
            'domain': domain,
            'interval_hours': interval_hours,
            'last_run': None,
            'next_run': datetime.now(timezone.utc),
            'enabled': True
        }
        
        self.logger.info(f"Scheduled audit {audit_id} for {domain} every {interval_hours} hours")
        return audit_id
    
    async def run_scheduled_audits(self) -> Dict[str, Any]:
        """Run all due scheduled audits."""
        now = datetime.now(timezone.utc)
        results = {}
        
        for audit_id, schedule in self.scheduled_audits.items():
            if schedule['enabled'] and now >= schedule['next_run']:
                try:
                    self.logger.info(f"Running scheduled audit {audit_id} for {schedule['domain']}")
                    
                    audit_results = await self.audit_engine.run_comprehensive_audit(
                        schedule['domain']
                    )
                    
                    schedule['last_run'] = now
                    schedule['next_run'] = now + timedelta(hours=schedule['interval_hours'])
                    
                    results[audit_id] = {
                        'status': 'completed',
                        'results': audit_results,
                        'next_run': schedule['next_run'].isoformat()
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error in scheduled audit {audit_id}: {e}")
                    results[audit_id] = {
                        'status': 'error',
                        'error': str(e),
                        'next_run': schedule['next_run'].isoformat()
                    }
        
        return results


# Usage Example and Testing
async def main():
    """Example usage of Technical Audit Engine."""
    
    # Initialize audit engine
    audit_engine = TechnicalAuditEngine(max_workers=5)
    
    # Run comprehensive audit
    try:
        domain = "example.com"  # Replace with actual domain
        results = await audit_engine.run_comprehensive_audit(domain, max_pages=50)
        
        print(f"\n=== Technical SEO Audit Results for {domain} ===")
        print(f"Overall Score: {results.overall_score:.1f}/100")
        print(f"Issues Found: {len(results.issues)}")
        print(f"Audit Duration: {results.audit_duration:.2f} seconds")
        
        # Export results
        json_report = await audit_engine.export_audit_results(results, 'json')
        html_report = await audit_engine.export_audit_results(results, 'html')
        
        print("\n=== JSON Report Generated ===")
        print("HTML Report Generated")
        
        # Setup scheduled audits
        scheduler = AuditScheduler(audit_engine)
        audit_id = await scheduler.schedule_audit(domain, interval_hours=24)
        print(f"\n=== Scheduled Audit Created: {audit_id} ===")
        
    except Exception as e:
        print(f"Error during audit: {e}")


if __name__ == "__main__":
    asyncio.run(main())