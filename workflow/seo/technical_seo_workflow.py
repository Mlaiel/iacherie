"""Technical SEO Workflow

AI-powered technical SEO analysis and optimization workflow.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from urllib.parse import urlparse

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIssue:
    """Technical SEO issue"""
    issue_type: str
    severity: str  # critical, high, medium, low
    url: str
    description: str
    recommendation: str
    impact_score: float
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PageSpeedMetrics:
    """Page speed performance metrics"""
    url: str
    load_time: float
    first_contentful_paint: float
    largest_contentful_paint: float
    cumulative_layout_shift: float
    first_input_delay: float
    performance_score: float
    measured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TechnicalSEOAudit:
    """Technical SEO audit result"""
    audit_id: str
    domain: str
    pages_analyzed: int
    issues_found: List[TechnicalIssue]
    page_speed_metrics: List[PageSpeedMetrics]
    crawlability_score: float
    indexability_score: float
    mobile_friendliness_score: float
    security_score: float
    overall_score: float
    priority_issues: List[TechnicalIssue]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class TechnicalSEOWorkflow:
    """AI-powered technical SEO workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager()
        self.audit_history: List[TechnicalSEOAudit] = []
        
    async def perform_technical_audit(
        self,
        domain: str,
        pages_to_analyze: List[str] = None,
        audit_depth: str = "comprehensive"
    ) -> TechnicalSEOAudit:
        """
        Perform comprehensive technical SEO audit
        
        Args:
            domain: Domain to audit
            pages_to_analyze: Specific pages to analyze (if None, discovers pages)
            audit_depth: Audit depth (basic/standard/comprehensive)
            
        Returns:
            TechnicalSEOAudit with issues and recommendations
        """
        try:
            start_time = datetime.utcnow()
            audit_id = f"tech_audit_{int(start_time.timestamp())}"
            
            logger.info(f"Starting technical SEO audit for {domain}")
            
            # Discover pages if not provided
            if pages_to_analyze is None:
                pages_to_analyze = await self._discover_pages(domain)
            
            # Analyze each page
            all_issues = []
            page_speed_metrics = []
            
            for page_url in pages_to_analyze:
                # Technical analysis
                page_issues = await self._analyze_page_technical_issues(page_url)
                all_issues.extend(page_issues)
                
                # Page speed analysis
                speed_metrics = await self._analyze_page_speed(page_url)
                page_speed_metrics.append(speed_metrics)
            
            # Site-wide technical analysis
            site_issues = await self._analyze_site_technical_issues(domain)
            all_issues.extend(site_issues)
            
            # Calculate scores
            crawlability_score = await self._calculate_crawlability_score(domain, all_issues)
            indexability_score = await self._calculate_indexability_score(domain, all_issues)
            mobile_friendliness_score = await self._calculate_mobile_score(all_issues)
            security_score = await self._calculate_security_score(domain, all_issues)
            overall_score = await self._calculate_overall_technical_score(
                crawlability_score, indexability_score, mobile_friendliness_score, security_score
            )
            
            # Identify priority issues
            priority_issues = await self._identify_priority_issues(all_issues)
            
            # Generate recommendations
            recommendations = await self._generate_technical_recommendations(all_issues, priority_issues)
            
            # Create audit result
            audit = TechnicalSEOAudit(
                audit_id=audit_id,
                domain=domain,
                pages_analyzed=len(pages_to_analyze),
                issues_found=all_issues,
                page_speed_metrics=page_speed_metrics,
                crawlability_score=crawlability_score,
                indexability_score=indexability_score,
                mobile_friendliness_score=mobile_friendliness_score,
                security_score=security_score,
                overall_score=overall_score,
                priority_issues=priority_issues,
                recommendations=recommendations
            )
            
            # Store in history
            self.audit_history.append(audit)
            
            # Cache result
            await self._cache_audit_result(audit)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric("technical_audit_duration", duration)
            await self.metrics_collector.record_metric("technical_overall_score", overall_score)
            await self.metrics_collector.record_metric("technical_issues_count", len(all_issues))
            
            logger.info(f"Technical audit completed. Overall score: {overall_score:.2f}")
            return audit
            
        except Exception as e:
            logger.error(f"Technical SEO audit failed: {e}")
            raise WorkflowError(f"Technical SEO audit failed: {e}")
    
    async def _discover_pages(self, domain: str) -> List[str]:
        """Discover pages to analyze from sitemap and crawling"""
        # Simulate page discovery
        pages = [
            f"https://{domain}/",
            f"https://{domain}/about",
            f"https://{domain}/products",
            f"https://{domain}/services",
            f"https://{domain}/blog",
            f"https://{domain}/contact"
        ]
        
        logger.info(f"Discovered {len(pages)} pages for analysis")
        return pages
    
    async def _analyze_page_technical_issues(self, url: str) -> List[TechnicalIssue]:
        """Analyze technical issues for a specific page"""
        issues = []
        
        # Simulate various technical checks
        import random
        
        # Title tag issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="title_tag",
                severity="high",
                url=url,
                description="Missing or duplicate title tag",
                recommendation="Add unique, descriptive title tag under 60 characters",
                impact_score=0.8
            ))
        
        # Meta description issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="meta_description",
                severity="medium",
                url=url,
                description="Missing meta description",
                recommendation="Add compelling meta description under 160 characters",
                impact_score=0.6
            ))
        
        # H1 tag issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="h1_tag",
                severity="high",
                url=url,
                description="Missing or multiple H1 tags",
                recommendation="Use exactly one H1 tag that describes the page content",
                impact_score=0.7
            ))
        
        # Image alt text issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="image_alt_text",
                severity="medium",
                url=url,
                description="Images missing alt text",
                recommendation="Add descriptive alt text to all images",
                impact_score=0.5
            ))
        
        # Internal linking issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="internal_links",
                severity="low",
                url=url,
                description="Poor internal linking structure",
                recommendation="Add relevant internal links to related content",
                impact_score=0.4
            ))
        
        return issues
    
    async def _analyze_site_technical_issues(self, domain: str) -> List[TechnicalIssue]:
        """Analyze site-wide technical issues"""
        issues = []
        
        # Simulate site-wide checks
        import random
        
        # SSL/HTTPS issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="ssl_certificate",
                severity="critical",
                url=f"https://{domain}",
                description="SSL certificate issues or mixed content",
                recommendation="Fix SSL certificate and eliminate mixed content warnings",
                impact_score=0.9
            ))
        
        # Robots.txt issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="robots_txt",
                severity="medium",
                url=f"https://{domain}/robots.txt",
                description="Robots.txt blocking important pages",
                recommendation="Review and optimize robots.txt file",
                impact_score=0.6
            ))
        
        # XML sitemap issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="xml_sitemap",
                severity="medium",
                url=f"https://{domain}/sitemap.xml",
                description="XML sitemap missing or outdated",
                recommendation="Create and submit updated XML sitemap",
                impact_score=0.7
            ))
        
        # Canonical tag issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="canonical_tags",
                severity="high",
                url=f"https://{domain}",
                description="Missing or incorrect canonical tags",
                recommendation="Implement proper canonical tags to prevent duplicate content",
                impact_score=0.8
            ))
        
        # Mobile responsiveness issues
        if random.choice([True, False]):
            issues.append(TechnicalIssue(
                issue_type="mobile_responsive",
                severity="high",
                url=f"https://{domain}",
                description="Site not mobile-friendly",
                recommendation="Implement responsive design for all devices",
                impact_score=0.8
            ))
        
        return issues
    
    async def _analyze_page_speed(self, url: str) -> PageSpeedMetrics:
        """Analyze page speed performance"""
        import random
        
        # Simulate page speed metrics
        load_time = random.uniform(1.0, 8.0)
        fcp = random.uniform(0.8, 4.0)
        lcp = random.uniform(1.5, 6.0)
        cls = random.uniform(0.0, 0.5)
        fid = random.uniform(10, 300)
        
        # Calculate performance score based on metrics
        performance_score = max(0, min(1, (10 - load_time) / 10))
        
        return PageSpeedMetrics(
            url=url,
            load_time=load_time,
            first_contentful_paint=fcp,
            largest_contentful_paint=lcp,
            cumulative_layout_shift=cls,
            first_input_delay=fid,
            performance_score=performance_score
        )
    
    async def _calculate_crawlability_score(self, domain: str, issues: List[TechnicalIssue]) -> float:
        """Calculate crawlability score"""
        crawl_issues = [i for i in issues if i.issue_type in ["robots_txt", "xml_sitemap", "internal_links"]]
        base_score = 1.0
        
        for issue in crawl_issues:
            penalty = 0.1 if issue.severity == "low" else 0.2 if issue.severity == "medium" else 0.3
            base_score -= penalty
        
        return max(0.0, base_score)
    
    async def _calculate_indexability_score(self, domain: str, issues: List[TechnicalIssue]) -> float:
        """Calculate indexability score"""
        index_issues = [i for i in issues if i.issue_type in ["canonical_tags", "meta_description", "title_tag"]]
        base_score = 1.0
        
        for issue in index_issues:
            penalty = 0.1 if issue.severity == "low" else 0.15 if issue.severity == "medium" else 0.25
            base_score -= penalty
        
        return max(0.0, base_score)
    
    async def _calculate_mobile_score(self, issues: List[TechnicalIssue]) -> float:
        """Calculate mobile-friendliness score"""
        mobile_issues = [i for i in issues if i.issue_type in ["mobile_responsive"]]
        return 1.0 if not mobile_issues else 0.3
    
    async def _calculate_security_score(self, domain: str, issues: List[TechnicalIssue]) -> float:
        """Calculate security score"""
        security_issues = [i for i in issues if i.issue_type in ["ssl_certificate"]]
        return 1.0 if not security_issues else 0.2
    
    async def _calculate_overall_technical_score(
        self, crawlability: float, indexability: float, mobile: float, security: float
    ) -> float:
        """Calculate overall technical SEO score"""
        # Weighted average
        weights = {"crawlability": 0.3, "indexability": 0.3, "mobile": 0.2, "security": 0.2}
        
        overall = (
            crawlability * weights["crawlability"] +
            indexability * weights["indexability"] +
            mobile * weights["mobile"] +
            security * weights["security"]
        )
        
        return overall
    
    async def _identify_priority_issues(self, issues: List[TechnicalIssue]) -> List[TechnicalIssue]:
        """Identify priority issues that need immediate attention"""
        # Sort by severity and impact
        priority_issues = sorted(
            [i for i in issues if i.severity in ["critical", "high"]],
            key=lambda x: (x.severity == "critical", x.impact_score),
            reverse=True
        )[:10]  # Top 10 priority issues
        
        return priority_issues
    
    async def _generate_technical_recommendations(
        self, all_issues: List[TechnicalIssue], priority_issues: List[TechnicalIssue]
    ) -> List[str]:
        """Generate actionable technical recommendations"""
        recommendations = [
            f"Fix {len(priority_issues)} critical/high priority technical issues immediately",
            "Implement comprehensive SSL/HTTPS across all pages",
            "Optimize page loading speeds to under 3 seconds",
            "Ensure all pages are mobile-responsive and mobile-friendly",
            "Create and maintain up-to-date XML sitemaps",
            "Review and optimize robots.txt file for proper crawling",
            "Implement proper canonical tags to prevent duplicate content issues",
            "Add descriptive title tags and meta descriptions to all pages",
            "Optimize images with appropriate alt text and compression",
            "Improve internal linking structure for better navigation and crawling"
        ]
        
        # Add specific recommendations based on issue types
        issue_types = set(issue.issue_type for issue in all_issues)
        
        if "ssl_certificate" in issue_types:
            recommendations.append("Immediately resolve SSL certificate issues for security and SEO")
        
        if "mobile_responsive" in issue_types:
            recommendations.append("Implement responsive design as a top priority for mobile users")
        
        if "page_speed" in issue_types:
            recommendations.append("Optimize page speed through image compression, minification, and CDN")
        
        return recommendations
    
    async def _cache_audit_result(self, audit: TechnicalSEOAudit):
        """Cache audit result for quick access"""
        cache_key = f"technical_audit_{audit.audit_id}"
        await self.cache_manager.set(cache_key, audit, ttl=3600)  # Cache for 1 hour
    
    async def get_audit_history(self, limit: int = 10) -> List[TechnicalSEOAudit]:
        """Get recent audit history"""
        return self.audit_history[-limit:]
    
    async def monitor_technical_health(self, domain: str) -> Dict[str, Any]:
        """Monitor ongoing technical health of a domain"""
        # Get latest audit data
        latest_audits = [audit for audit in self.audit_history if audit.domain == domain]
        
        if not latest_audits:
            return {"error": f"No audit data available for {domain}"}
        
        latest_audit = latest_audits[-1]
        
        health_status = {
            "domain": domain,
            "last_audit": latest_audit.created_at,
            "overall_score": latest_audit.overall_score,
            "health_status": "excellent" if latest_audit.overall_score >= 0.9 else
                            "good" if latest_audit.overall_score >= 0.7 else
                            "needs_attention" if latest_audit.overall_score >= 0.5 else "poor",
            "critical_issues": len([i for i in latest_audit.issues_found if i.severity == "critical"]),
            "high_priority_issues": len([i for i in latest_audit.issues_found if i.severity == "high"]),
            "scores": {
                "crawlability": latest_audit.crawlability_score,
                "indexability": latest_audit.indexability_score,
                "mobile_friendliness": latest_audit.mobile_friendliness_score,
                "security": latest_audit.security_score
            },
            "next_audit_recommended": datetime.utcnow() + timedelta(days=30)
        }
        
        return health_status