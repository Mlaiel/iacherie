"""Backlink Analyzer - Advanced Backlink Profile Analysis and Monitoring

This module provides comprehensive backlink analysis including link quality assessment,
competitor backlink analysis, and link building opportunity identification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter
import statistics
import numpy as np
from urllib.parse import urlparse, urljoin
import re
import hashlib

logger = logging.getLogger(__name__)


class LinkType(Enum):
    """Types of backlinks"""
    DOFOLLOW = "dofollow"
    NOFOLLOW = "nofollow"
    SPONSORED = "sponsored"
    UGC = "ugc"


class LinkQuality(Enum):
    """Link quality classification"""
    EXCELLENT = "excellent"     # DA 80+, highly relevant
    GOOD = "good"              # DA 60-79, relevant
    AVERAGE = "average"        # DA 40-59, somewhat relevant
    POOR = "poor"             # DA 20-39, low relevance
    TOXIC = "toxic"           # Spam, penalized domains


class LinkStatus(Enum):
    """Link status"""
    ACTIVE = "active"
    BROKEN = "broken"
    REDIRECTED = "redirected"
    REMOVED = "removed"
    MONITORED = "monitored"


@dataclass
class BacklinkProfile:
    """Represents a backlink"""
    link_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str = ""
    target_url: str = ""
    anchor_text: str = ""
    link_type: LinkType = LinkType.DOFOLLOW
    link_quality: LinkQuality = LinkQuality.AVERAGE
    link_status: LinkStatus = LinkStatus.ACTIVE
    domain_authority: float = 0.0
    page_authority: float = 0.0
    trust_flow: float = 0.0
    citation_flow: float = 0.0
    referring_domain: str = ""
    ip_address: str = ""
    link_context: str = ""
    discovery_date: datetime = field(default_factory=datetime.now)
    last_checked: datetime = field(default_factory=datetime.now)
    position_on_page: int = 0
    is_image_link: bool = False
    image_alt_text: str = ""
    social_signals: Dict[str, int] = field(default_factory=dict)
    spam_score: float = 0.0
    relevance_score: float = 0.0
    traffic_estimate: float = 0.0
    geographic_location: str = ""
    language: str = "en"
    industry_category: str = ""


@dataclass
class CompetitorBacklinkAnalysis:
    """Competitor backlink analysis results"""
    competitor_domain: str
    total_backlinks: int = 0
    referring_domains: int = 0
    dofollow_links: int = 0
    nofollow_links: int = 0
    average_domain_authority: float = 0.0
    top_linking_domains: List[str] = field(default_factory=list)
    common_anchor_texts: List[str] = field(default_factory=list)
    link_building_opportunities: List[str] = field(default_factory=list)
    toxic_links: int = 0
    quality_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class LinkOpportunity:
    """Link building opportunity"""
    opportunity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_domain: str = ""
    opportunity_type: str = ""  # guest_post, broken_link, resource_page, etc.
    priority_score: float = 0.0
    domain_authority: float = 0.0
    relevance_score: float = 0.0
    contact_info: Dict[str, str] = field(default_factory=dict)
    outreach_status: str = "not_contacted"
    estimated_success_rate: float = 0.0
    notes: str = ""
    discovered_date: datetime = field(default_factory=datetime.now)


class BacklinkAnalyzer:
    """Advanced backlink analysis and monitoring system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Backlink Analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.backlinks_database: Dict[str, BacklinkProfile] = {}
        self.competitor_analysis: Dict[str, CompetitorBacklinkAnalysis] = {}
        self.link_opportunities: Dict[str, LinkOpportunity] = {}
        self.monitored_domains: Set[str] = set()
        
        # Configuration parameters
        self.min_domain_authority = self.config.get('min_domain_authority', 20)
        self.max_spam_score = self.config.get('max_spam_score', 5)
        self.check_frequency_hours = self.config.get('check_frequency_hours', 24)
        self.quality_thresholds = self.config.get('quality_thresholds', {
            'excellent': 80,
            'good': 60,
            'average': 40,
            'poor': 20
        })
    
    async def analyze_backlink_profile(
        self,
        domain: str,
        include_competitors: bool = True,
        competitors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive backlink profile analysis
        
        Args:
            domain: Domain to analyze
            include_competitors: Whether to include competitor analysis
            competitors: List of competitor domains
            
        Returns:
            Complete backlink analysis results
        """
        try:
            logger.info(f"Starting backlink analysis for {domain}")
            
            # Discover backlinks
            backlinks = await self._discover_backlinks(domain)
            
            # Analyze link quality
            quality_analysis = await self._analyze_link_quality(backlinks)
            
            # Check for toxic links
            toxic_analysis = await self._detect_toxic_links(backlinks)
            
            # Analyze anchor text distribution
            anchor_analysis = await self._analyze_anchor_texts(backlinks)
            
            # Geographic and language analysis
            geo_analysis = await self._analyze_geographic_distribution(backlinks)
            
            # Link velocity analysis
            velocity_analysis = await self._analyze_link_velocity(domain)
            
            # Competitor analysis
            competitor_analysis = {}
            if include_competitors and competitors:
                competitor_analysis = await self._analyze_competitors_backlinks(competitors)
            
            # Identify link opportunities
            opportunities = await self._identify_link_opportunities(domain, backlinks)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(
                backlinks, quality_analysis, toxic_analysis, competitor_analysis
            )
            
            # Store results
            for backlink in backlinks:
                self.backlinks_database[backlink.link_id] = backlink
            
            results = {
                "domain": domain,
                "analysis_date": datetime.now().isoformat(),
                "total_backlinks": len(backlinks),
                "referring_domains": len(set(b.referring_domain for b in backlinks)),
                "quality_analysis": quality_analysis,
                "toxic_analysis": toxic_analysis,
                "anchor_analysis": anchor_analysis,
                "geographic_analysis": geo_analysis,
                "velocity_analysis": velocity_analysis,
                "competitor_analysis": competitor_analysis,
                "link_opportunities": [self._opportunity_to_dict(opp) for opp in opportunities],
                "insights": insights
            }
            
            logger.info(f"Backlink analysis completed for {domain}")
            return results
            
        except Exception as e:
            logger.error(f"Error in backlink analysis: {str(e)}")
            return {}
    
    async def _discover_backlinks(self, domain: str) -> List[BacklinkProfile]:
        """Discover backlinks for domain"""
        try:
            backlinks = []
            
            # Simulate backlink discovery
            # In production, this would integrate with SEO tools APIs
            num_backlinks = np.random.randint(50, 500)
            
            for i in range(num_backlinks):
                backlink = BacklinkProfile(
                    source_url=f"https://example{i}.com/page{i}",
                    target_url=f"https://{domain}/page{np.random.randint(1, 20)}",
                    anchor_text=self._generate_anchor_text(domain),
                    link_type=np.random.choice(list(LinkType)),
                    referring_domain=f"example{i}.com",
                    domain_authority=np.random.uniform(10, 95),
                    page_authority=np.random.uniform(5, 80),
                    trust_flow=np.random.uniform(0, 100),
                    citation_flow=np.random.uniform(0, 100),
                    spam_score=np.random.uniform(0, 10),
                    relevance_score=np.random.uniform(0.1, 1.0),
                    traffic_estimate=np.random.uniform(0, 10000),
                    position_on_page=np.random.randint(1, 20),
                    geographic_location=np.random.choice(["US", "UK", "CA", "AU", "DE", "FR"]),
                    language=np.random.choice(["en", "es", "fr", "de", "it"]),
                    industry_category=np.random.choice([
                        "technology", "marketing", "business", "health", "education", "entertainment"
                    ])
                )
                
                # Set link quality based on domain authority
                backlink.link_quality = await self._classify_link_quality(backlink)
                
                # Set link status
                backlink.link_status = np.random.choice(
                    [LinkStatus.ACTIVE, LinkStatus.BROKEN, LinkStatus.REDIRECTED],
                    p=[0.85, 0.10, 0.05]
                )
                
                backlinks.append(backlink)
            
            return backlinks
            
        except Exception as e:
            logger.error(f"Error discovering backlinks: {str(e)}")
            return []
    
    async def _analyze_link_quality(self, backlinks: List[BacklinkProfile]) -> Dict[str, Any]:
        """Analyze overall link quality"""
        try:
            quality_distribution = Counter()
            domain_authority_stats = []
            trust_flow_stats = []
            relevance_stats = []
            
            for backlink in backlinks:
                quality_distribution[backlink.link_quality.value] += 1
                domain_authority_stats.append(backlink.domain_authority)
                trust_flow_stats.append(backlink.trust_flow)
                relevance_stats.append(backlink.relevance_score)
            
            return {
                "quality_distribution": dict(quality_distribution),
                "domain_authority_stats": {
                    "mean": statistics.mean(domain_authority_stats),
                    "median": statistics.median(domain_authority_stats),
                    "max": max(domain_authority_stats),
                    "min": min(domain_authority_stats)
                },
                "trust_flow_stats": {
                    "mean": statistics.mean(trust_flow_stats),
                    "median": statistics.median(trust_flow_stats)
                },
                "relevance_stats": {
                    "mean": statistics.mean(relevance_stats),
                    "median": statistics.median(relevance_stats)
                },
                "high_quality_percentage": (
                    quality_distribution["excellent"] + quality_distribution["good"]
                ) / len(backlinks) * 100 if backlinks else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing link quality: {str(e)}")
            return {}
    
    async def _detect_toxic_links(self, backlinks: List[BacklinkProfile]) -> Dict[str, Any]:
        """Detect potentially toxic or harmful links"""
        try:
            toxic_links = []
            suspicious_patterns = []
            
            for backlink in backlinks:
                toxicity_score = 0
                toxicity_reasons = []
                
                # High spam score
                if backlink.spam_score > self.max_spam_score:
                    toxicity_score += 30
                    toxicity_reasons.append("High spam score")
                
                # Very low domain authority
                if backlink.domain_authority < 10:
                    toxicity_score += 20
                    toxicity_reasons.append("Very low domain authority")
                
                # Suspicious anchor text patterns
                if await self._is_suspicious_anchor_text(backlink.anchor_text):
                    toxicity_score += 25
                    toxicity_reasons.append("Suspicious anchor text")
                
                # Suspicious domain patterns
                if await self._is_suspicious_domain(backlink.referring_domain):
                    toxicity_score += 35
                    toxicity_reasons.append("Suspicious domain pattern")
                
                # Low relevance
                if backlink.relevance_score < 0.2:
                    toxicity_score += 15
                    toxicity_reasons.append("Low relevance")
                
                if toxicity_score >= 50:
                    toxic_links.append({
                        "link_id": backlink.link_id,
                        "source_url": backlink.source_url,
                        "referring_domain": backlink.referring_domain,
                        "toxicity_score": toxicity_score,
                        "reasons": toxicity_reasons
                    })
            
            return {
                "total_toxic_links": len(toxic_links),
                "toxic_percentage": len(toxic_links) / len(backlinks) * 100 if backlinks else 0,
                "toxic_links": toxic_links[:20],  # Return top 20 for review
                "disavow_recommendations": len(toxic_links),
                "risk_level": self._calculate_risk_level(len(toxic_links), len(backlinks))
            }
            
        except Exception as e:
            logger.error(f"Error detecting toxic links: {str(e)}")
            return {}
    
    async def _analyze_anchor_texts(self, backlinks: List[BacklinkProfile]) -> Dict[str, Any]:
        """Analyze anchor text distribution"""
        try:
            anchor_counter = Counter()
            anchor_types = {
                "branded": 0,
                "exact_match": 0,
                "partial_match": 0,
                "generic": 0,
                "naked_url": 0,
                "image": 0
            }
            
            for backlink in backlinks:
                anchor_text = backlink.anchor_text.lower().strip()
                anchor_counter[anchor_text] += 1
                
                # Classify anchor type
                if backlink.is_image_link:
                    anchor_types["image"] += 1
                elif self._is_url(anchor_text):
                    anchor_types["naked_url"] += 1
                elif self._is_branded_anchor(anchor_text):
                    anchor_types["branded"] += 1
                elif self._is_generic_anchor(anchor_text):
                    anchor_types["generic"] += 1
                else:
                    # Simple keyword classification
                    anchor_types["partial_match"] += 1
            
            # Calculate percentages
            total_links = len(backlinks)
            anchor_distribution = {
                key: (count / total_links * 100) if total_links > 0 else 0
                for key, count in anchor_types.items()
            }
            
            return {
                "anchor_distribution": anchor_distribution,
                "top_anchors": dict(anchor_counter.most_common(20)),
                "diversity_score": len(anchor_counter) / total_links if total_links > 0 else 0,
                "over_optimization_risk": self._calculate_over_optimization_risk(anchor_distribution),
                "recommendations": self._generate_anchor_recommendations(anchor_distribution)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing anchor texts: {str(e)}")
            return {}
    
    async def _analyze_geographic_distribution(self, backlinks: List[BacklinkProfile]) -> Dict[str, Any]:
        """Analyze geographic distribution of backlinks"""
        try:
            geo_counter = Counter()
            language_counter = Counter()
            
            for backlink in backlinks:
                if backlink.geographic_location:
                    geo_counter[backlink.geographic_location] += 1
                if backlink.language:
                    language_counter[backlink.language] += 1
            
            return {
                "geographic_distribution": dict(geo_counter.most_common()),
                "language_distribution": dict(language_counter.most_common()),
                "geographic_diversity": len(geo_counter),
                "primary_markets": list(geo_counter.most_common(5))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing geographic distribution: {str(e)}")
            return {}
    
    async def _analyze_link_velocity(self, domain: str) -> Dict[str, Any]:
        """Analyze link acquisition velocity"""
        try:
            # Simulate historical link data
            current_date = datetime.now()
            velocity_data = {}
            
            for i in range(12):  # Last 12 months
                month_date = current_date - timedelta(days=30 * i)
                month_key = month_date.strftime("%Y-%m")
                velocity_data[month_key] = np.random.randint(5, 50)
            
            velocities = list(velocity_data.values())
            average_velocity = statistics.mean(velocities)
            velocity_trend = "increasing" if velocities[0] > velocities[-1] else "decreasing"
            
            return {
                "monthly_velocity": velocity_data,
                "average_monthly_links": average_velocity,
                "velocity_trend": velocity_trend,
                "velocity_consistency": statistics.stdev(velocities),
                "natural_pattern_score": self._calculate_natural_pattern_score(velocities)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing link velocity: {str(e)}")
            return {}
    
    async def _analyze_competitors_backlinks(self, competitors: List[str]) -> Dict[str, CompetitorBacklinkAnalysis]:
        """Analyze competitor backlink profiles"""
        try:
            competitor_results = {}
            
            for competitor in competitors:
                # Simulate competitor backlink data
                analysis = CompetitorBacklinkAnalysis(
                    competitor_domain=competitor,
                    total_backlinks=np.random.randint(100, 2000),
                    referring_domains=np.random.randint(50, 500),
                    dofollow_links=np.random.randint(80, 1500),
                    nofollow_links=np.random.randint(20, 500),
                    average_domain_authority=np.random.uniform(30, 85),
                    toxic_links=np.random.randint(0, 50)
                )
                
                # Generate top linking domains
                analysis.top_linking_domains = [
                    f"authority{i}.com" for i in range(1, 11)
                ]
                
                # Generate common anchor texts
                analysis.common_anchor_texts = [
                    f"{competitor}", f"click here", "read more", f"visit {competitor}"
                ]
                
                # Quality distribution
                analysis.quality_distribution = {
                    "excellent": np.random.randint(5, 20),
                    "good": np.random.randint(20, 40),
                    "average": np.random.randint(30, 50),
                    "poor": np.random.randint(10, 30),
                    "toxic": np.random.randint(0, 10)
                }
                
                competitor_results[competitor] = analysis
                self.competitor_analysis[competitor] = analysis
            
            return competitor_results
            
        except Exception as e:
            logger.error(f"Error analyzing competitor backlinks: {str(e)}")
            return {}
    
    async def _identify_link_opportunities(
        self,
        domain: str,
        backlinks: List[BacklinkProfile]
    ) -> List[LinkOpportunity]:
        """Identify link building opportunities"""
        try:
            opportunities = []
            
            # Extract referring domains for analysis
            referring_domains = set(b.referring_domain for b in backlinks)
            
            # Generate different types of opportunities
            opportunity_types = [
                "guest_post", "broken_link", "resource_page", "competitor_backlink",
                "brand_mention", "directory_listing", "industry_forum", "podcast_interview"
            ]
            
            for opp_type in opportunity_types:
                num_opportunities = np.random.randint(5, 20)
                
                for i in range(num_opportunities):
                    opportunity = LinkOpportunity(
                        target_domain=f"{opp_type}_target_{i}.com",
                        opportunity_type=opp_type,
                        domain_authority=np.random.uniform(20, 90),
                        relevance_score=np.random.uniform(0.4, 1.0),
                        estimated_success_rate=np.random.uniform(0.1, 0.8)
                    )
                    
                    # Calculate priority score
                    opportunity.priority_score = await self._calculate_opportunity_priority(opportunity)
                    
                    # Generate contact info
                    opportunity.contact_info = {
                        "email": f"contact@{opportunity.target_domain}",
                        "social": f"@{opportunity.target_domain.split('.')[0]}"
                    }
                    
                    opportunities.append(opportunity)
                    self.link_opportunities[opportunity.opportunity_id] = opportunity
            
            # Sort by priority score
            return sorted(opportunities, key=lambda x: x.priority_score, reverse=True)[:50]
            
        except Exception as e:
            logger.error(f"Error identifying link opportunities: {str(e)}")
            return []
    
    async def _generate_insights(
        self,
        backlinks: List[BacklinkProfile],
        quality_analysis: Dict[str, Any],
        toxic_analysis: Dict[str, Any],
        competitor_analysis: Dict[str, CompetitorBacklinkAnalysis]
    ) -> List[str]:
        """Generate actionable insights and recommendations"""
        try:
            insights = []
            
            # Quality insights
            high_quality_pct = quality_analysis.get("high_quality_percentage", 0)
            if high_quality_pct < 30:
                insights.append("Focus on acquiring higher quality backlinks - currently only {:.1f}% are high quality".format(high_quality_pct))
            
            # Toxic link insights
            toxic_pct = toxic_analysis.get("toxic_percentage", 0)
            if toxic_pct > 5:
                insights.append("Consider disavowing {:.1f}% of toxic backlinks to protect domain health".format(toxic_pct))
            
            # Domain authority insights
            avg_da = quality_analysis.get("domain_authority_stats", {}).get("mean", 0)
            if avg_da < 40:
                insights.append("Target higher authority domains - current average DA is {:.1f}".format(avg_da))
            
            # Competitor insights
            if competitor_analysis:
                for competitor, analysis in competitor_analysis.items():
                    if analysis.total_backlinks > len(backlinks):
                        insights.append(f"Competitor {competitor} has {analysis.total_backlinks} backlinks vs your {len(backlinks)} - opportunity for growth")
            
            # Geographic insights
            insights.append("Diversify geographic sources for better global reach")
            
            # Anchor text insights
            insights.append("Maintain natural anchor text distribution to avoid over-optimization penalties")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    # Helper methods
    async def _classify_link_quality(self, backlink: BacklinkProfile) -> LinkQuality:
        """Classify link quality based on various factors"""
        da = backlink.domain_authority
        spam_score = backlink.spam_score
        relevance = backlink.relevance_score
        
        # Calculate quality score
        quality_score = (da / 100 * 0.4) + (relevance * 0.4) + ((10 - spam_score) / 10 * 0.2)
        
        if quality_score >= 0.8 and da >= 80:
            return LinkQuality.EXCELLENT
        elif quality_score >= 0.6 and da >= 60:
            return LinkQuality.GOOD
        elif quality_score >= 0.4 and da >= 40:
            return LinkQuality.AVERAGE
        elif quality_score >= 0.2 and da >= 20:
            return LinkQuality.POOR
        else:
            return LinkQuality.TOXIC
    
    async def _is_suspicious_anchor_text(self, anchor_text: str) -> bool:
        """Check if anchor text appears suspicious"""
        suspicious_patterns = [
            r"cheap\s+\w+", r"buy\s+\w+", r"discount\s+\w+",
            r"\d+%\s+off", r"free\s+\w+", r"click\s+here"
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, anchor_text, re.IGNORECASE):
                return True
        return False
    
    async def _is_suspicious_domain(self, domain: str) -> bool:
        """Check if domain appears suspicious"""
        suspicious_indicators = [
            len(domain) > 50,  # Very long domains
            domain.count('-') > 3,  # Too many hyphens
            bool(re.search(r'\d{4,}', domain)),  # Long number sequences
            domain.endswith('.tk'),  # Free domains
        ]
        
        return any(suspicious_indicators)
    
    def _generate_anchor_text(self, domain: str) -> str:
        """Generate realistic anchor text"""
        anchors = [
            domain,
            f"visit {domain}",
            "click here",
            "read more",
            "learn more",
            f"check out {domain}",
            domain.split('.')[0],
            "this site",
            "website"
        ]
        return np.random.choice(anchors)
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a URL"""
        return bool(re.match(r'https?://', text))
    
    def _is_branded_anchor(self, text: str) -> bool:
        """Check if anchor text is branded"""
        branded_indicators = ["company", "brand", "site", "official"]
        return any(indicator in text.lower() for indicator in branded_indicators)
    
    def _is_generic_anchor(self, text: str) -> bool:
        """Check if anchor text is generic"""
        generic_anchors = ["click here", "read more", "learn more", "visit", "website", "link"]
        return text.lower() in generic_anchors
    
    def _calculate_over_optimization_risk(self, anchor_distribution: Dict[str, float]) -> str:
        """Calculate over-optimization risk level"""
        exact_match_pct = anchor_distribution.get("exact_match", 0)
        partial_match_pct = anchor_distribution.get("partial_match", 0)
        
        total_optimized = exact_match_pct + partial_match_pct
        
        if total_optimized > 60:
            return "high"
        elif total_optimized > 40:
            return "medium"
        else:
            return "low"
    
    def _generate_anchor_recommendations(self, anchor_distribution: Dict[str, float]) -> List[str]:
        """Generate anchor text recommendations"""
        recommendations = []
        
        branded_pct = anchor_distribution.get("branded", 0)
        generic_pct = anchor_distribution.get("generic", 0)
        exact_match_pct = anchor_distribution.get("exact_match", 0)
        
        if branded_pct < 30:
            recommendations.append("Increase branded anchor text percentage to 30-40%")
        
        if generic_pct < 20:
            recommendations.append("Use more generic anchor text for natural link profile")
        
        if exact_match_pct > 10:
            recommendations.append("Reduce exact match anchor text to avoid over-optimization")
        
        return recommendations
    
    def _calculate_risk_level(self, toxic_count: int, total_count: int) -> str:
        """Calculate overall risk level"""
        if total_count == 0:
            return "unknown"
        
        toxic_percentage = toxic_count / total_count * 100
        
        if toxic_percentage > 15:
            return "high"
        elif toxic_percentage > 8:
            return "medium"
        elif toxic_percentage > 3:
            return "low"
        else:
            return "minimal"
    
    def _calculate_natural_pattern_score(self, velocities: List[float]) -> float:
        """Calculate how natural the link velocity pattern appears"""
        # Check for sudden spikes or unnatural patterns
        if len(velocities) < 3:
            return 0.5
        
        # Calculate coefficient of variation
        mean_velocity = statistics.mean(velocities)
        std_velocity = statistics.stdev(velocities)
        
        if mean_velocity == 0:
            return 0.0
        
        cv = std_velocity / mean_velocity
        
        # Natural patterns typically have moderate variation
        if 0.2 <= cv <= 0.8:
            return 1.0
        elif cv < 0.2:
            return 0.6  # Too consistent, might be artificial
        else:
            return 0.3  # Too variable, might indicate manipulation
    
    async def _calculate_opportunity_priority(self, opportunity: LinkOpportunity) -> float:
        """Calculate priority score for link opportunity"""
        # Normalize domain authority (0-1)
        da_score = opportunity.domain_authority / 100
        
        # Weight factors
        priority_score = (
            da_score * 0.4 +
            opportunity.relevance_score * 0.3 +
            opportunity.estimated_success_rate * 0.3
        )
        
        return min(priority_score, 1.0)
    
    def _opportunity_to_dict(self, opportunity: LinkOpportunity) -> Dict[str, Any]:
        """Convert opportunity to dictionary"""
        return {
            "opportunity_id": opportunity.opportunity_id,
            "target_domain": opportunity.target_domain,
            "opportunity_type": opportunity.opportunity_type,
            "priority_score": opportunity.priority_score,
            "domain_authority": opportunity.domain_authority,
            "relevance_score": opportunity.relevance_score,
            "estimated_success_rate": opportunity.estimated_success_rate,
            "contact_info": opportunity.contact_info,
            "outreach_status": opportunity.outreach_status
        }
    
    def get_backlink_summary(self) -> Dict[str, Any]:
        """Get summary of backlink analysis"""
        try:
            if not self.backlinks_database:
                return {}
            
            total_backlinks = len(self.backlinks_database)
            active_links = len([b for b in self.backlinks_database.values() if b.link_status == LinkStatus.ACTIVE])
            broken_links = len([b for b in self.backlinks_database.values() if b.link_status == LinkStatus.BROKEN])
            
            quality_distribution = Counter([b.link_quality.value for b in self.backlinks_database.values()])
            
            avg_domain_authority = statistics.mean([b.domain_authority for b in self.backlinks_database.values()])
            
            return {
                "total_backlinks": total_backlinks,
                "active_links": active_links,
                "broken_links": broken_links,
                "quality_distribution": dict(quality_distribution),
                "average_domain_authority": avg_domain_authority,
                "referring_domains": len(set(b.referring_domain for b in self.backlinks_database.values())),
                "link_opportunities": len(self.link_opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error generating backlink summary: {str(e)}")
            return {}


# Example usage
async def main() -> None:
    """Example usage of Backlink Analyzer"""
    try:
        # Initialize analyzer
        config = {
            'min_domain_authority': 25,
            'max_spam_score': 5,
            'check_frequency_hours': 24
        }
        
        analyzer = BacklinkAnalyzer(config)
        
        # Analyze backlink profile
        domain = "example.com"
        competitors = ["competitor1.com", "competitor2.com"]
        
        print(f"🔍 Analyzing backlink profile for {domain}...")
        
        results = await analyzer.analyze_backlink_profile(
            domain=domain,
            include_competitors=True,
            competitors=competitors
        )
        
        # Print summary
        print(f"\n📊 Backlink Analysis Results:")
        print(f"   Total Backlinks: {results.get('total_backlinks', 0)}")
        print(f"   Referring Domains: {results.get('referring_domains', 0)}")
        
        quality_analysis = results.get('quality_analysis', {})
        print(f"   Average Domain Authority: {quality_analysis.get('domain_authority_stats', {}).get('mean', 0):.1f}")
        print(f"   High Quality Links: {quality_analysis.get('high_quality_percentage', 0):.1f}%")
        
        toxic_analysis = results.get('toxic_analysis', {})
        print(f"   Toxic Links: {toxic_analysis.get('total_toxic_links', 0)} ({toxic_analysis.get('toxic_percentage', 0):.1f}%)")
        print(f"   Risk Level: {toxic_analysis.get('risk_level', 'unknown')}")
        
        print(f"\n🎯 Link Opportunities: {len(results.get('link_opportunities', []))}")
        
        # Show insights
        insights = results.get('insights', [])
        print(f"\n💡 Key Insights:")
        for insight in insights[:5]:
            print(f"   • {insight}")
        
        # Get summary
        summary = analyzer.get_backlink_summary()
        print(f"\n📈 Summary:")
        print(f"   Total Monitored Links: {summary.get('total_backlinks', 0)}")
        print(f"   Active Links: {summary.get('active_links', 0)}")
        print(f"   Broken Links: {summary.get('broken_links', 0)}")
        
        print("\n✅ Backlink Analysis completed!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())