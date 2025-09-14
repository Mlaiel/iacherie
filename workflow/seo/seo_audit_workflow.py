"""SEO Audit Workflow - Comprehensive SEO analysis and optimization recommendations.

This module provides complete SEO auditing capabilities including technical analysis,
content evaluation, competitive assessment, and actionable improvement recommendations
for maximum search engine visibility and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import math


class AuditCategory(Enum):
    """SEO audit category classifications."""
    TECHNICAL = "technical"
    CONTENT = "content"
    ON_PAGE = "on_page"
    OFF_PAGE = "off_page"
    MOBILE = "mobile"
    PERFORMANCE = "performance"
    USER_EXPERIENCE = "user_experience"
    COMPETITIVE = "competitive"


class IssueSeverity(Enum):
    """SEO issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AuditStatus(Enum):
    """Audit item status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"
    NEEDS_REVIEW = "needs_review"


@dataclass
class AuditIssue:
    """Individual SEO audit issue."""
    category: AuditCategory
    severity: IssueSeverity
    title: str
    description: str
    impact: str
    recommendation: str
    how_to_fix: str
    priority_score: int
    estimated_effort: str  # "low", "medium", "high"
    estimated_impact: str  # "low", "medium", "high"
    resources: List[str] = field(default_factory=list)
    technical_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditScore:
    """SEO audit scoring breakdown."""
    overall_score: float
    technical_score: float
    content_score: float
    on_page_score: float
    mobile_score: float
    performance_score: float
    competitive_score: float
    category_scores: Dict[str, float] = field(default_factory=dict)
    improvement_potential: float = 0.0


@dataclass
class ActionableInsights:
    """Actionable insights and recommendations."""
    quick_wins: List[AuditIssue]
    high_impact_fixes: List[AuditIssue]
    long_term_improvements: List[AuditIssue]
    competitive_opportunities: List[str]
    content_gaps: List[str]
    technical_priorities: List[str]
    implementation_roadmap: Dict[str, List[str]]


@dataclass
class ComprehensiveAudit:
    """Complete SEO audit results."""
    audit_score: AuditScore
    audit_issues: List[AuditIssue]
    actionable_insights: ActionableInsights
    performance_metrics: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    content_analysis: Dict[str, Any]
    recommendations_summary: List[str]
    audit_timestamp: datetime
    next_audit_date: datetime


class SEOAuditWorkflow:
    """Comprehensive SEO audit workflow with detailed analysis and recommendations."""
    
    def __init__(self) -> None:
        """Initialize the SEO audit workflow."""
        self.audit_checkers = {
            AuditCategory.TECHNICAL: self._audit_technical_seo,
            AuditCategory.CONTENT: self._audit_content_seo,
            AuditCategory.ON_PAGE: self._audit_on_page_seo,
            AuditCategory.MOBILE: self._audit_mobile_seo,
            AuditCategory.PERFORMANCE: self._audit_performance,
            AuditCategory.USER_EXPERIENCE: self._audit_user_experience,
            AuditCategory.COMPETITIVE: self._audit_competitive_seo
        }
        
        self.scoring_weights = {
            AuditCategory.TECHNICAL: 0.25,
            AuditCategory.CONTENT: 0.20,
            AuditCategory.ON_PAGE: 0.20,
            AuditCategory.MOBILE: 0.15,
            AuditCategory.PERFORMANCE: 0.10,
            AuditCategory.USER_EXPERIENCE: 0.05,
            AuditCategory.COMPETITIVE: 0.05
        }
    
    async def execute(self, content_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """Execute comprehensive SEO audit workflow.
        
        Args:
            content_data: Content and website data for audit
            config: Workflow configuration
            
        Returns:
            Comprehensive SEO audit results and recommendations
        """
        try:
            # Extract audit parameters
            url = content_data.get("url", "")
            content_text = content_data.get("content", "")
            target_keywords = content_data.get("target_keywords", [])
            competitors = content_data.get("competitors", [])
            audit_scope = content_data.get("audit_scope", "comprehensive")
            target_platforms = content_data.get("target_platforms", ["google"])
            
            # Step 1: Initialize audit
            audit_timestamp = datetime.now()
            all_issues = []
            category_scores = {}
            
            # Step 2: Run category-specific audits
            for category, checker in self.audit_checkers.items():
                category_issues, category_score = await checker(
                    content_data, target_keywords, config
                )
                all_issues.extend(category_issues)
                category_scores[category.value] = category_score
            
            # Step 3: Calculate overall audit score
            audit_score = self._calculate_audit_score(category_scores)
            
            # Step 4: Generate actionable insights
            actionable_insights = await self._generate_actionable_insights(
                all_issues, content_data, competitors
            )
            
            # Step 5: Perform competitive analysis
            competitive_analysis = await self._perform_competitive_analysis(
                content_data, competitors, target_keywords
            )
            
            # Step 6: Generate performance metrics
            performance_metrics = await self._analyze_performance_metrics(
                content_data, url
            )
            
            # Step 7: Technical deep dive
            technical_analysis = await self._perform_technical_analysis(
                content_data, url
            )
            
            # Step 8: Content analysis
            content_analysis = await self._perform_content_analysis(
                content_text, target_keywords
            )
            
            # Step 9: Generate recommendations summary
            recommendations_summary = self._generate_recommendations_summary(
                actionable_insights, audit_score
            )
            
            # Step 10: Create comprehensive audit
            comprehensive_audit = ComprehensiveAudit(
                audit_score=audit_score,
                audit_issues=all_issues,
                actionable_insights=actionable_insights,
                performance_metrics=performance_metrics,
                competitive_analysis=competitive_analysis,
                technical_analysis=technical_analysis,
                content_analysis=content_analysis,
                recommendations_summary=recommendations_summary,
                audit_timestamp=audit_timestamp,
                next_audit_date=audit_timestamp + timedelta(days=30)
            )
            
            return {
                "status": "completed",
                "score": audit_score.overall_score,
                "comprehensive_audit": comprehensive_audit,
                "quick_wins": actionable_insights.quick_wins,
                "high_impact_fixes": actionable_insights.high_impact_fixes,
                "recommendations": recommendations_summary,
                "audit_report": self._generate_audit_report(comprehensive_audit),
                "metrics": {
                    "total_issues": len(all_issues),
                    "critical_issues": len([i for i in all_issues if i.severity == IssueSeverity.CRITICAL]),
                    "high_priority_issues": len([i for i in all_issues if i.severity == IssueSeverity.HIGH]),
                    "improvement_potential": audit_score.improvement_potential,
                    "audit_completeness": 100.0,  # All categories covered
                    "next_audit_in_days": 30
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "score": 0.0,
                "recommendations": [],
                "metrics": {}
            }
    
    async def _audit_technical_seo(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit technical SEO factors."""
        issues = []
        score = 100.0
        
        url = content_data.get("url", "")
        
        # URL Structure Audit
        if url:
            if not self._is_seo_friendly_url(url):
                issues.append(AuditIssue(
                    category=AuditCategory.TECHNICAL,
                    severity=IssueSeverity.MEDIUM,
                    title="Non-SEO Friendly URL Structure",
                    description="URL structure is not optimized for search engines",
                    impact="May reduce search engine crawlability and user understanding",
                    recommendation="Use descriptive, keyword-rich URLs with hyphens",
                    how_to_fix="Restructure URLs to include target keywords and use hyphens instead of underscores",
                    priority_score=70,
                    estimated_effort="medium",
                    estimated_impact="medium"
                ))
                score -= 15
        
        # HTTPS Check
        if url and not url.startswith('https://'):
            issues.append(AuditIssue(
                category=AuditCategory.TECHNICAL,
                severity=IssueSeverity.HIGH,
                title="Missing HTTPS Security",
                description="Website is not using HTTPS protocol",
                impact="Search engines prefer HTTPS sites and users may see security warnings",
                recommendation="Implement SSL certificate and redirect all HTTP traffic to HTTPS",
                how_to_fix="Purchase and install SSL certificate, update all internal links to HTTPS",
                priority_score=90,
                estimated_effort="medium",
                estimated_impact="high"
            ))
            score -= 25
        
        # Robots.txt Check
        robots_txt = content_data.get("robots_txt", "")
        if not robots_txt:
            issues.append(AuditIssue(
                category=AuditCategory.TECHNICAL,
                severity=IssueSeverity.MEDIUM,
                title="Missing Robots.txt File",
                description="No robots.txt file found",
                impact="Search engines may not crawl your site efficiently",
                recommendation="Create and upload a robots.txt file to guide search engine crawlers",
                how_to_fix="Create robots.txt file with proper directives and upload to root directory",
                priority_score=60,
                estimated_effort="low",
                estimated_impact="medium"
            ))
            score -= 10
        
        # XML Sitemap Check
        sitemap = content_data.get("sitemap", "")
        if not sitemap:
            issues.append(AuditIssue(
                category=AuditCategory.TECHNICAL,
                severity=IssueSeverity.HIGH,
                title="Missing XML Sitemap",
                description="No XML sitemap found or submitted",
                impact="Search engines may miss important pages during crawling",
                recommendation="Generate and submit XML sitemap to search engines",
                how_to_fix="Create XML sitemap and submit to Google Search Console and Bing Webmaster Tools",
                priority_score=85,
                estimated_effort="low",
                estimated_impact="high"
            ))
            score -= 20
        
        # Canonical URLs Check
        canonical_url = content_data.get("canonical_url", "")
        if not canonical_url:
            issues.append(AuditIssue(
                category=AuditCategory.TECHNICAL,
                severity=IssueSeverity.MEDIUM,
                title="Missing Canonical URLs",
                description="No canonical URLs specified",
                impact="May cause duplicate content issues",
                recommendation="Implement canonical URLs for all pages",
                how_to_fix="Add rel='canonical' tags to all pages pointing to preferred URL version",
                priority_score=75,
                estimated_effort="medium",
                estimated_impact="medium"
            ))
            score -= 15
        
        return issues, max(0, score)
    
    async def _audit_content_seo(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit content SEO factors."""
        issues = []
        score = 100.0
        
        content_text = content_data.get("content", "")
        title = content_data.get("title", "")
        meta_description = content_data.get("meta_description", "")
        
        # Content Length Check
        word_count = len(content_text.split()) if content_text else 0
        if word_count < 300:
            issues.append(AuditIssue(
                category=AuditCategory.CONTENT,
                severity=IssueSeverity.HIGH,
                title="Insufficient Content Length",
                description=f"Content is only {word_count} words",
                impact="Short content may not rank well for competitive keywords",
                recommendation="Expand content to at least 300-500 words with valuable information",
                how_to_fix="Add more detailed information, examples, and comprehensive coverage of the topic",
                priority_score=80,
                estimated_effort="high",
                estimated_impact="high"
            ))
            score -= 30
        
        # Keyword Usage Check
        if keywords and content_text:
            primary_keyword = keywords[0]
            keyword_density = self._calculate_keyword_density(content_text, primary_keyword)
            
            if keyword_density < 0.5:
                issues.append(AuditIssue(
                    category=AuditCategory.CONTENT,
                    severity=IssueSeverity.MEDIUM,
                    title="Low Keyword Density",
                    description=f"Primary keyword '{primary_keyword}' density is {keyword_density:.1f}%",
                    impact="May not signal relevance to search engines",
                    recommendation="Increase keyword usage to 1-3% density naturally",
                    how_to_fix="Include target keyword in title, headings, and naturally throughout content",
                    priority_score=70,
                    estimated_effort="medium",
                    estimated_impact="medium"
                ))
                score -= 15
            elif keyword_density > 5.0:
                issues.append(AuditIssue(
                    category=AuditCategory.CONTENT,
                    severity=IssueSeverity.HIGH,
                    title="Keyword Over-Optimization",
                    description=f"Primary keyword '{primary_keyword}' density is {keyword_density:.1f}%",
                    impact="May be penalized for keyword stuffing",
                    recommendation="Reduce keyword density to 1-3% and use synonyms",
                    how_to_fix="Replace some keyword instances with synonyms and related terms",
                    priority_score=85,
                    estimated_effort="medium",
                    estimated_impact="high"
                ))
                score -= 25
        
        # Heading Structure Check
        headings = self._extract_headings(content_text)
        if not headings:
            issues.append(AuditIssue(
                category=AuditCategory.CONTENT,
                severity=IssueSeverity.MEDIUM,
                title="Missing Heading Structure",
                description="No headings (H1, H2, H3) found in content",
                impact="Poor content structure affects readability and SEO",
                recommendation="Add hierarchical heading structure to organize content",
                how_to_fix="Add H1 for main title, H2 for sections, H3 for subsections",
                priority_score=65,
                estimated_effort="medium",
                estimated_impact="medium"
            ))
            score -= 20
        
        # Content Freshness Check
        last_modified = content_data.get("last_modified")
        if last_modified:
            days_old = (datetime.now() - last_modified).days
            if days_old > 365:
                issues.append(AuditIssue(
                    category=AuditCategory.CONTENT,
                    severity=IssueSeverity.LOW,
                    title="Outdated Content",
                    description=f"Content hasn't been updated in {days_old} days",
                    impact="Search engines prefer fresh, updated content",
                    recommendation="Review and update content regularly",
                    how_to_fix="Add recent information, update statistics, refresh examples",
                    priority_score=40,
                    estimated_effort="medium",
                    estimated_impact="low"
                ))
                score -= 10
        
        return issues, max(0, score)
    
    async def _audit_on_page_seo(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit on-page SEO factors."""
        issues = []
        score = 100.0
        
        title = content_data.get("title", "")
        meta_description = content_data.get("meta_description", "")
        
        # Title Tag Audit
        if not title:
            issues.append(AuditIssue(
                category=AuditCategory.ON_PAGE,
                severity=IssueSeverity.CRITICAL,
                title="Missing Title Tag",
                description="No title tag found",
                impact="Critical for search engine rankings and click-through rates",
                recommendation="Add descriptive title tag with target keywords",
                how_to_fix="Create unique, descriptive title tag 50-60 characters long",
                priority_score=100,
                estimated_effort="low",
                estimated_impact="high"
            ))
            score -= 40
        else:
            if len(title) > 60:
                issues.append(AuditIssue(
                    category=AuditCategory.ON_PAGE,
                    severity=IssueSeverity.MEDIUM,
                    title="Title Tag Too Long",
                    description=f"Title tag is {len(title)} characters",
                    impact="May be truncated in search results",
                    recommendation="Shorten title to 50-60 characters",
                    how_to_fix="Revise title to be more concise while keeping key information",
                    priority_score=60,
                    estimated_effort="low",
                    estimated_impact="medium"
                ))
                score -= 15
            
            if keywords and not any(kw.lower() in title.lower() for kw in keywords):
                issues.append(AuditIssue(
                    category=AuditCategory.ON_PAGE,
                    severity=IssueSeverity.HIGH,
                    title="Title Missing Target Keywords",
                    description="Title tag doesn't contain target keywords",
                    impact="Reduced relevance signals to search engines",
                    recommendation="Include primary keyword in title tag",
                    how_to_fix="Rewrite title to naturally include target keyword near the beginning",
                    priority_score=85,
                    estimated_effort="low",
                    estimated_impact="high"
                ))
                score -= 25
        
        # Meta Description Audit
        if not meta_description:
            issues.append(AuditIssue(
                category=AuditCategory.ON_PAGE,
                severity=IssueSeverity.HIGH,
                title="Missing Meta Description",
                description="No meta description found",
                impact="Missed opportunity for better click-through rates",
                recommendation="Add compelling meta description with target keywords",
                how_to_fix="Write unique meta description 150-160 characters long",
                priority_score=75,
                estimated_effort="low",
                estimated_impact="medium"
            ))
            score -= 20
        else:
            if len(meta_description) > 160:
                issues.append(AuditIssue(
                    category=AuditCategory.ON_PAGE,
                    severity=IssueSeverity.MEDIUM,
                    title="Meta Description Too Long",
                    description=f"Meta description is {len(meta_description)} characters",
                    impact="May be truncated in search results",
                    recommendation="Shorten meta description to 150-160 characters",
                    how_to_fix="Edit meta description to be more concise",
                    priority_score=50,
                    estimated_effort="low",
                    estimated_impact="low"
                ))
                score -= 10
        
        # Image Alt Text Check
        images = content_data.get("images", [])
        missing_alt_count = len([img for img in images if not img.get("alt_text")])
        if missing_alt_count > 0:
            issues.append(AuditIssue(
                category=AuditCategory.ON_PAGE,
                severity=IssueSeverity.MEDIUM,
                title="Missing Image Alt Text",
                description=f"{missing_alt_count} images missing alt text",
                impact="Poor accessibility and missed SEO opportunities",
                recommendation="Add descriptive alt text to all images",
                how_to_fix="Add relevant, descriptive alt text to each image",
                priority_score=65,
                estimated_effort="medium",
                estimated_impact="medium"
            ))
            score -= 15
        
        return issues, max(0, score)
    
    async def _audit_mobile_seo(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit mobile SEO factors."""
        issues = []
        score = 100.0
        
        # Mobile Viewport Check
        viewport_meta = content_data.get("viewport_meta", "")
        if not viewport_meta or "width=device-width" not in viewport_meta:
            issues.append(AuditIssue(
                category=AuditCategory.MOBILE,
                severity=IssueSeverity.HIGH,
                title="Missing Mobile Viewport Meta Tag",
                description="No proper viewport meta tag for mobile devices",
                impact="Poor mobile user experience and mobile search rankings",
                recommendation="Add viewport meta tag for responsive design",
                how_to_fix="Add <meta name='viewport' content='width=device-width, initial-scale=1'>",
                priority_score=90,
                estimated_effort="low",
                estimated_impact="high"
            ))
            score -= 30
        
        # Mobile Speed Check (simulated)
        mobile_speed = content_data.get("mobile_speed_score", 0)
        if mobile_speed < 50:
            issues.append(AuditIssue(
                category=AuditCategory.MOBILE,
                severity=IssueSeverity.HIGH,
                title="Poor Mobile Page Speed",
                description=f"Mobile speed score is {mobile_speed}/100",
                impact="High bounce rates and poor mobile search rankings",
                recommendation="Optimize images, minimize CSS/JS, enable compression",
                how_to_fix="Compress images, minify resources, use CDN, optimize critical rendering path",
                priority_score=85,
                estimated_effort="high",
                estimated_impact="high"
            ))
            score -= 25
        
        # Mobile-Friendly Design Check
        is_mobile_friendly = content_data.get("mobile_friendly", True)
        if not is_mobile_friendly:
            issues.append(AuditIssue(
                category=AuditCategory.MOBILE,
                severity=IssueSeverity.CRITICAL,
                title="Not Mobile-Friendly",
                description="Website fails mobile-friendly test",
                impact="Poor mobile user experience and search rankings",
                recommendation="Implement responsive design",
                how_to_fix="Use responsive CSS, flexible layouts, touch-friendly buttons",
                priority_score=95,
                estimated_effort="high",
                estimated_impact="high"
            ))
            score -= 40
        
        return issues, max(0, score)
    
    async def _audit_performance(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit performance factors."""
        issues = []
        score = 100.0
        
        # Page Speed Check
        page_speed = content_data.get("page_speed_score", 0)
        if page_speed < 70:
            severity = IssueSeverity.CRITICAL if page_speed < 30 else IssueSeverity.HIGH
            score_deduction = 35 if page_speed < 30 else 25
            
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=severity,
                title="Poor Page Speed Performance",
                description=f"Page speed score is {page_speed}/100",
                impact="High bounce rates and poor search rankings",
                recommendation="Optimize images, enable caching, minimize resources",
                how_to_fix="Compress images, enable GZIP, use browser caching, minimize HTTP requests",
                priority_score=90,
                estimated_effort="high",
                estimated_impact="high"
            ))
            score -= score_deduction
        
        # Core Web Vitals Check
        lcp = content_data.get("largest_contentful_paint", 0)
        if lcp > 2.5:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=IssueSeverity.HIGH,
                title="Poor Largest Contentful Paint (LCP)",
                description=f"LCP is {lcp} seconds (should be < 2.5s)",
                impact="Poor user experience and Core Web Vitals score",
                recommendation="Optimize loading of largest content element",
                how_to_fix="Optimize images, improve server response time, preload key resources",
                priority_score=85,
                estimated_effort="medium",
                estimated_impact="high"
            ))
            score -= 20
        
        # Image Optimization Check
        unoptimized_images = content_data.get("unoptimized_images", 0)
        if unoptimized_images > 0:
            issues.append(AuditIssue(
                category=AuditCategory.PERFORMANCE,
                severity=IssueSeverity.MEDIUM,
                title="Unoptimized Images",
                description=f"{unoptimized_images} images are not optimized",
                impact="Slower page loading and poor user experience",
                recommendation="Optimize all images for web",
                how_to_fix="Compress images, use modern formats (WebP), implement lazy loading",
                priority_score=60,
                estimated_effort="medium",
                estimated_impact="medium"
            ))
            score -= 15
        
        return issues, max(0, score)
    
    async def _audit_user_experience(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit user experience factors."""
        issues = []
        score = 100.0
        
        # Bounce Rate Check
        bounce_rate = content_data.get("bounce_rate", 0)
        if bounce_rate > 70:
            issues.append(AuditIssue(
                category=AuditCategory.USER_EXPERIENCE,
                severity=IssueSeverity.MEDIUM,
                title="High Bounce Rate",
                description=f"Bounce rate is {bounce_rate}%",
                impact="Indicates poor user engagement and content relevance",
                recommendation="Improve content quality and user experience",
                how_to_fix="Enhance content relevance, improve page speed, better call-to-actions",
                priority_score=70,
                estimated_effort="high",
                estimated_impact="medium"
            ))
            score -= 20
        
        # Navigation Check
        has_clear_navigation = content_data.get("has_clear_navigation", True)
        if not has_clear_navigation:
            issues.append(AuditIssue(
                category=AuditCategory.USER_EXPERIENCE,
                severity=IssueSeverity.MEDIUM,
                title="Poor Navigation Structure",
                description="Website navigation is unclear or confusing",
                impact="Poor user experience and increased bounce rate",
                recommendation="Implement clear, intuitive navigation",
                how_to_fix="Simplify menu structure, add breadcrumbs, improve internal linking",
                priority_score=65,
                estimated_effort="medium",
                estimated_impact="medium"
            ))
            score -= 15
        
        return issues, max(0, score)
    
    async def _audit_competitive_seo(
        self,
        content_data: Dict[str, Any],
        keywords: List[str],
        config: Any
    ) -> Tuple[List[AuditIssue], float]:
        """Audit competitive SEO factors."""
        issues = []
        score = 100.0
        
        competitors = content_data.get("competitors", [])
        
        if not competitors:
            issues.append(AuditIssue(
                category=AuditCategory.COMPETITIVE,
                severity=IssueSeverity.LOW,
                title="No Competitive Analysis",
                description="No competitor analysis has been performed",
                impact="Missing insights into competitive landscape",
                recommendation="Identify and analyze top competitors",
                how_to_fix="Research competitors, analyze their SEO strategies, identify gaps",
                priority_score=30,
                estimated_effort="medium",
                estimated_impact="low"
            ))
            score -= 10
        
        # Domain Authority Comparison (simulated)
        domain_authority = content_data.get("domain_authority", 0)
        avg_competitor_da = content_data.get("avg_competitor_domain_authority", 0)
        
        if avg_competitor_da > 0 and domain_authority < avg_competitor_da - 20:
            issues.append(AuditIssue(
                category=AuditCategory.COMPETITIVE,
                severity=IssueSeverity.MEDIUM,
                title="Low Domain Authority vs Competitors",
                description=f"Domain authority ({domain_authority}) is significantly lower than competitors ({avg_competitor_da})",
                impact="May struggle to rank against established competitors",
                recommendation="Focus on building high-quality backlinks",
                how_to_fix="Create linkable content, guest posting, broken link building",
                priority_score=50,
                estimated_effort="high",
                estimated_impact="medium"
            ))
            score -= 15
        
        return issues, max(0, score)
    
    def _calculate_audit_score(self, category_scores: Dict[str, float]) -> AuditScore:
        """Calculate comprehensive audit score."""
        # Calculate weighted overall score
        overall_score = 0
        for category, score in category_scores.items():
            category_enum = AuditCategory(category)
            weight = self.scoring_weights.get(category_enum, 0)
            overall_score += score * weight
        
        # Calculate improvement potential
        max_possible_score = 100
        improvement_potential = max_possible_score - overall_score
        
        return AuditScore(
            overall_score=round(overall_score, 1),
            technical_score=category_scores.get(AuditCategory.TECHNICAL.value, 0),
            content_score=category_scores.get(AuditCategory.CONTENT.value, 0),
            on_page_score=category_scores.get(AuditCategory.ON_PAGE.value, 0),
            mobile_score=category_scores.get(AuditCategory.MOBILE.value, 0),
            performance_score=category_scores.get(AuditCategory.PERFORMANCE.value, 0),
            competitive_score=category_scores.get(AuditCategory.COMPETITIVE.value, 0),
            category_scores=category_scores,
            improvement_potential=round(improvement_potential, 1)
        )
    
    async def _generate_actionable_insights(
        self,
        all_issues: List[AuditIssue],
        content_data: Dict[str, Any],
        competitors: List[str]
    ) -> ActionableInsights:
        """Generate actionable insights and recommendations."""
        
        # Categorize issues by effort and impact
        quick_wins = [
            issue for issue in all_issues 
            if issue.estimated_effort == "low" and issue.estimated_impact in ["medium", "high"]
        ]
        
        high_impact_fixes = [
            issue for issue in all_issues
            if issue.estimated_impact == "high" and issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]
        ]
        
        long_term_improvements = [
            issue for issue in all_issues
            if issue.estimated_effort == "high" and issue.estimated_impact in ["medium", "high"]
        ]
        
        # Sort by priority score
        quick_wins.sort(key=lambda x: x.priority_score, reverse=True)
        high_impact_fixes.sort(key=lambda x: x.priority_score, reverse=True)
        long_term_improvements.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Generate other insights
        competitive_opportunities = [
            "Analyze competitor content gaps",
            "Study competitor backlink profiles",
            "Monitor competitor keyword rankings",
            "Identify competitor technical weaknesses"
        ]
        
        content_gaps = [
            "Long-form comprehensive guides",
            "FAQ sections for common queries",
            "Video content for better engagement",
            "Regular blog updates and fresh content"
        ]
        
        technical_priorities = [
            "Implement HTTPS if not present",
            "Optimize Core Web Vitals",
            "Create XML sitemap",
            "Fix mobile responsiveness issues"
        ]
        
        # Create implementation roadmap
        implementation_roadmap = {
            "Week 1": [issue.title for issue in quick_wins[:3]],
            "Month 1": [issue.title for issue in high_impact_fixes[:5]],
            "Quarter 1": [issue.title for issue in long_term_improvements[:3]]
        }
        
        return ActionableInsights(
            quick_wins=quick_wins[:10],
            high_impact_fixes=high_impact_fixes[:10],
            long_term_improvements=long_term_improvements[:10],
            competitive_opportunities=competitive_opportunities,
            content_gaps=content_gaps,
            technical_priorities=technical_priorities,
            implementation_roadmap=implementation_roadmap
        )
    
    async def _perform_competitive_analysis(
        self,
        content_data: Dict[str, Any],
        competitors: List[str],
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Perform competitive analysis."""
        return {
            "analyzed_competitors": len(competitors),
            "keyword_overlap": 75.0,  # Simulated
            "content_gap_opportunities": 15,
            "backlink_gap": 150,
            "competitive_advantage_areas": [
                "Mobile optimization",
                "Page speed",
                "Content depth"
            ],
            "areas_to_improve": [
                "Domain authority",
                "Backlink profile",
                "Content frequency"
            ]
        }
    
    async def _analyze_performance_metrics(
        self,
        content_data: Dict[str, Any],
        url: str
    ) -> Dict[str, Any]:
        """Analyze performance metrics."""
        return {
            "page_speed_score": content_data.get("page_speed_score", 75),
            "mobile_speed_score": content_data.get("mobile_speed_score", 65),
            "core_web_vitals": {
                "lcp": content_data.get("largest_contentful_paint", 2.1),
                "fid": content_data.get("first_input_delay", 85),
                "cls": content_data.get("cumulative_layout_shift", 0.05)
            },
            "accessibility_score": content_data.get("accessibility_score", 85),
            "best_practices_score": content_data.get("best_practices_score", 90),
            "seo_score": content_data.get("technical_seo_score", 80)
        }
    
    async def _perform_technical_analysis(
        self,
        content_data: Dict[str, Any],
        url: str
    ) -> Dict[str, Any]:
        """Perform technical SEO analysis."""
        return {
            "crawlability": {
                "robots_txt_present": bool(content_data.get("robots_txt")),
                "xml_sitemap_present": bool(content_data.get("sitemap")),
                "internal_links_count": content_data.get("internal_links", 0),
                "broken_links_count": content_data.get("broken_links", 0)
            },
            "indexability": {
                "canonical_urls": bool(content_data.get("canonical_url")),
                "meta_robots": content_data.get("meta_robots", "index, follow"),
                "duplicate_content_issues": content_data.get("duplicate_content", 0)
            },
            "site_architecture": {
                "url_structure_score": 85,
                "navigation_depth": content_data.get("navigation_depth", 3),
                "breadcrumbs_present": content_data.get("breadcrumbs", False)
            }
        }
    
    async def _perform_content_analysis(
        self,
        content_text: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Perform content SEO analysis."""
        word_count = len(content_text.split()) if content_text else 0
        
        return {
            "content_quality": {
                "word_count": word_count,
                "readability_score": 75,  # Simulated Flesch score
                "keyword_density": self._calculate_keyword_density(content_text, keywords[0]) if keywords and content_text else 0,
                "heading_structure_score": 80
            },
            "content_optimization": {
                "keyword_usage": len(keywords),
                "semantic_keywords": 5,  # Simulated
                "content_freshness": "Updated within 6 months",
                "internal_linking": 3  # Simulated
            },
            "content_gaps": [
                "FAQ section",
                "Related articles",
                "User-generated content",
                "Video content"
            ]
        }
    
    def _generate_recommendations_summary(
        self,
        insights: ActionableInsights,
        audit_score: AuditScore
    ) -> List[str]:
        """Generate summary of key recommendations."""
        recommendations = []
        
        if audit_score.overall_score < 60:
            recommendations.append("URGENT: Address critical technical SEO issues immediately")
        
        if insights.quick_wins:
            recommendations.append(f"Implement {len(insights.quick_wins)} quick wins for immediate improvement")
        
        if insights.high_impact_fixes:
            recommendations.append(f"Focus on {len(insights.high_impact_fixes)} high-impact fixes this month")
        
        if audit_score.technical_score < 70:
            recommendations.append("Prioritize technical SEO improvements")
        
        if audit_score.content_score < 70:
            recommendations.append("Enhance content quality and keyword optimization")
        
        if audit_score.mobile_score < 80:
            recommendations.append("Improve mobile optimization and user experience")
        
        recommendations.extend([
            "Conduct regular SEO audits every 30 days",
            "Monitor competitor strategies and keyword rankings",
            "Focus on building high-quality backlinks",
            "Create fresh, valuable content regularly"
        ])
        
        return recommendations[:10]
    
    def _generate_audit_report(self, audit: ComprehensiveAudit) -> str:
        """Generate comprehensive audit report."""
        report_sections = []
        
        # Executive Summary
        report_sections.append(f"""
        SEO AUDIT EXECUTIVE SUMMARY
        ===========================
        Overall Score: {audit.audit_score.overall_score}/100
        Audit Date: {audit.audit_timestamp.strftime('%Y-%m-%d %H:%M')}
        
        Critical Issues: {len([i for i in audit.audit_issues if i.severity == IssueSeverity.CRITICAL])}
        High Priority Issues: {len([i for i in audit.audit_issues if i.severity == IssueSeverity.HIGH])}
        Total Issues Found: {len(audit.audit_issues)}
        
        Improvement Potential: {audit.audit_score.improvement_potential} points
        """)
        
        # Category Breakdown
        report_sections.append(f"""
        CATEGORY SCORES
        ===============
        Technical SEO: {audit.audit_score.technical_score}/100
        Content SEO: {audit.audit_score.content_score}/100
        On-Page SEO: {audit.audit_score.on_page_score}/100
        Mobile SEO: {audit.audit_score.mobile_score}/100
        Performance: {audit.audit_score.performance_score}/100
        """)
        
        # Quick Wins
        if audit.actionable_insights.quick_wins:
            report_sections.append("QUICK WINS (Implement First)")
            report_sections.append("=" * 35)
            for i, issue in enumerate(audit.actionable_insights.quick_wins[:5], 1):
                report_sections.append(f"{i}. {issue.title}")
                report_sections.append(f"   Impact: {issue.estimated_impact.title()}")
                report_sections.append(f"   How to fix: {issue.how_to_fix}")
                report_sections.append("")
        
        # Next Steps
        report_sections.append("RECOMMENDED NEXT STEPS")
        report_sections.append("=" * 25)
        for i, rec in enumerate(audit.recommendations_summary[:5], 1):
            report_sections.append(f"{i}. {rec}")
        
        return "\n".join(report_sections)
    
    # Helper methods
    
    def _is_seo_friendly_url(self, url: str) -> bool:
        """Check if URL is SEO-friendly."""
        # Simple check for SEO-friendly URL characteristics
        return bool(re.match(r'^https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9-/]*$', url))
    
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density as percentage."""
        if not content or not keyword:
            return 0.0
        
        words = content.lower().split()
        keyword_count = content.lower().count(keyword.lower())
        
        return (keyword_count / len(words)) * 100 if words else 0.0
    
    def _extract_headings(self, content: str) -> List[str]:
        """Extract headings from content."""
        # Simple heading extraction (in real implementation would parse HTML/Markdown)
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return headings