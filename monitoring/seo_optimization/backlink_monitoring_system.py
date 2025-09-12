"""
Backlink Monitoring System - Enterprise Link Building & Authority Tracking

This module implements comprehensive backlink monitoring for the Ainflue platform,
tracking link authority, analyzing link quality, and optimizing link building strategies.

Author: Fahed Mlaiel
Role: Lead Dev IA + SEO Expert + Link Building Specialist + Data Analyst
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from urllib.parse import urlparse, urljoin
import requests
import re
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkType(Enum):
    """Types of backlinks"""
    FOLLOW = "follow"
    NOFOLLOW = "nofollow"
    SPONSORED = "sponsored"
    UGC = "ugc"

class LinkQuality(Enum):
    """Link quality classification"""
    TOXIC = "toxic"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXCELLENT = "excellent"

class LinkStatus(Enum):
    """Link status"""
    ACTIVE = "active"
    BROKEN = "broken"
    REDIRECTED = "redirected"
    REMOVED = "removed"
    PENDING = "pending"

class AnchorTextType(Enum):
    """Types of anchor text"""
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    BRANDED = "branded"
    GENERIC = "generic"
    URL = "url"
    IMAGE = "image"

@dataclass
class Backlink:
    """Backlink data structure"""
    link_id: str
    source_url: str
    target_url: str
    source_domain: str
    anchor_text: str
    anchor_text_type: AnchorTextType
    link_type: LinkType
    link_quality: LinkQuality
    link_status: LinkStatus
    domain_authority: float
    page_authority: float
    trust_flow: float
    citation_flow: float
    discovered_date: datetime
    last_checked: datetime
    context: str
    surrounding_text: str
    link_position: str
    referring_ips: Set[str]
    social_signals: Dict[str, int]

@dataclass
class DomainProfile:
    """Domain authority profile"""
    domain: str
    domain_authority: float
    page_authority: float
    trust_flow: float
    citation_flow: float
    spam_score: float
    organic_traffic: int
    backlink_count: int
    referring_domains: int
    social_authority: float
    content_quality_score: float
    niche_relevance: float
    geographic_relevance: float

@dataclass
class LinkBuildingOpportunity:
    """Link building opportunity"""
    opportunity_id: str
    target_domain: str
    opportunity_type: str
    authority_score: float
    relevance_score: float
    competition_level: float
    success_probability: float
    effort_required: str
    contact_information: Dict[str, str]
    content_gaps: List[str]
    outreach_strategy: str
    estimated_timeline: int

class BacklinkMonitoringSystem:
    """
    Enterprise backlink monitoring system for Ainflue platform.
    
    Features:
    - Real-time backlink discovery and tracking
    - Link quality assessment and classification
    - Domain authority analysis
    - Toxic link detection and disavowal
    - Competitor backlink analysis
    - Link building opportunity identification
    - Anchor text distribution analysis
    - Link velocity monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize backlink monitoring system"""
        self.config = config or {}
        self.backlinks: Dict[str, Backlink] = {}
        self.domain_profiles: Dict[str, DomainProfile] = {}
        self.link_opportunities: List[LinkBuildingOpportunity] = []
        self.competitor_backlinks: Dict[str, List[Backlink]] = defaultdict(list)
        self.toxic_domains: Set[str] = set()
        
        # Monitoring configuration
        self.monitoring_config = {
            "check_frequency": 3600,  # seconds
            "quality_thresholds": {
                "domain_authority_min": 30,
                "trust_flow_min": 20,
                "spam_score_max": 30
            },
            "anchor_text_diversity": {
                "exact_match_max": 0.15,  # 15% max
                "branded_min": 0.30,      # 30% min
                "generic_max": 0.20       # 20% max
            }
        }
        
        # Initialize monitoring system
        self._initialize_backlink_monitoring()
        logger.info("Backlink Monitoring System initialized")
    
    def _initialize_backlink_monitoring(self):
        """Initialize backlink monitoring components"""
        try:
            # Setup link quality analyzers
            self._setup_quality_analyzers()
            
            # Initialize domain authority tracking
            self._setup_domain_authority_tracking()
            
            # Setup competitor analysis
            self._setup_competitor_analysis()
            
            # Initialize toxic link detection
            self._setup_toxic_link_detection()
            
            logger.info("Backlink monitoring initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize backlink monitoring: {e}")
            raise
    
    def _setup_quality_analyzers(self):
        """Setup link quality analysis algorithms"""
        self.quality_factors = {
            "domain_authority": {"weight": 0.25, "threshold": 50},
            "trust_flow": {"weight": 0.20, "threshold": 30},
            "relevance": {"weight": 0.20, "threshold": 0.7},
            "content_quality": {"weight": 0.15, "threshold": 0.8},
            "anchor_text_quality": {"weight": 0.10, "threshold": 0.6},
            "link_placement": {"weight": 0.10, "threshold": 0.7}
        }
        
        # Toxic link indicators
        self.toxic_indicators = {
            "spam_score_threshold": 70,
            "low_quality_domains": ["spammy-site.com", "link-farm.net"],
            "suspicious_patterns": [
                r".*casino.*", r".*poker.*", r".*pharmacy.*", 
                r".*loan.*", r".*payday.*"
            ],
            "link_schemes": ["private-blog-networks", "link-exchanges"]
        }
    
    def _setup_domain_authority_tracking(self):
        """Setup domain authority tracking system"""
        self.authority_metrics = {
            "moz_da": {"api_endpoint": "moz_api", "weight": 0.4},
            "ahrefs_dr": {"api_endpoint": "ahrefs_api", "weight": 0.3},
            "semrush_as": {"api_endpoint": "semrush_api", "weight": 0.3}
        }
    
    def _setup_competitor_analysis(self):
        """Setup competitor backlink analysis"""
        self.competitor_config = {
            "max_competitors": 10,
            "analysis_depth": 1000,  # top 1000 backlinks
            "gap_analysis_threshold": 0.3,
            "opportunity_scoring": {
                "authority_weight": 0.4,
                "relevance_weight": 0.3,
                "availability_weight": 0.3
            }
        }
    
    def _setup_toxic_link_detection(self):
        """Setup toxic link detection algorithms"""
        self.toxic_detection_config = {
            "spam_score_api": "moz_spam_score",
            "pattern_analysis": True,
            "manual_review_threshold": 50,
            "auto_disavow_threshold": 80
        }
    
    async def discover_backlinks(self, target_domain: str, depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Discover backlinks for target domain
        
        Args:
            target_domain: Domain to analyze
            depth: Analysis depth (quick, standard, comprehensive)
            
        Returns:
            Discovered backlinks and analysis
        """
        try:
            # Configure discovery based on depth
            discovery_config = self._get_discovery_config(depth)
            
            # Discover backlinks from multiple sources
            discovered_links = await self._discover_from_sources(target_domain, discovery_config)
            
            # Analyze link quality
            analyzed_links = await self._analyze_link_quality(discovered_links)
            
            # Update backlink database
            await self._update_backlink_database(analyzed_links)
            
            # Perform anchor text analysis
            anchor_analysis = await self._analyze_anchor_text_distribution(target_domain)
            
            # Detect toxic links
            toxic_analysis = await self._detect_toxic_links(analyzed_links)
            
            # Calculate link velocity
            velocity_analysis = await self._calculate_link_velocity(target_domain)
            
            result = {
                "target_domain": target_domain,
                "discovery_summary": {
                    "total_backlinks": len(analyzed_links),
                    "new_backlinks": len([link for link in analyzed_links if link.discovered_date >= datetime.now() - timedelta(days=7)]),
                    "high_quality_links": len([link for link in analyzed_links if link.link_quality in [LinkQuality.HIGH, LinkQuality.EXCELLENT]]),
                    "toxic_links": len([link for link in analyzed_links if link.link_quality == LinkQuality.TOXIC])
                },
                "anchor_text_analysis": anchor_analysis,
                "toxic_link_analysis": toxic_analysis,
                "link_velocity": velocity_analysis,
                "top_referring_domains": await self._get_top_referring_domains(analyzed_links),
                "recommendations": await self._generate_backlink_recommendations(target_domain, analyzed_links),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Backlink discovery completed for {target_domain}: {len(analyzed_links)} links analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to discover backlinks for {target_domain}: {e}")
            return {"error": str(e)}
    
    def _get_discovery_config(self, depth: str) -> Dict[str, Any]:
        """Get discovery configuration based on depth"""
        configs = {
            "quick": {
                "sources": ["ahrefs", "moz"],
                "max_links": 100,
                "timeout": 30
            },
            "standard": {
                "sources": ["ahrefs", "moz", "semrush"],
                "max_links": 500,
                "timeout": 120
            },
            "comprehensive": {
                "sources": ["ahrefs", "moz", "semrush", "majestic", "manual"],
                "max_links": 2000,
                "timeout": 300
            }
        }
        
        return configs.get(depth, configs["standard"])
    
    async def _discover_from_sources(self, target_domain: str, config: Dict[str, Any]) -> List[Backlink]:
        """Discover backlinks from multiple sources"""
        discovered_links = []
        
        # Simulate backlink discovery from various sources
        # In a real implementation, this would integrate with APIs
        
        for source in config["sources"]:
            source_links = await self._discover_from_source(target_domain, source, config)
            discovered_links.extend(source_links)
        
        # Remove duplicates based on source URL and target URL
        unique_links = {}
        for link in discovered_links:
            key = f"{link.source_url}_{link.target_url}"
            if key not in unique_links:
                unique_links[key] = link
        
        return list(unique_links.values())
    
    async def _discover_from_source(self, target_domain: str, source: str, config: Dict[str, Any]) -> List[Backlink]:
        """Discover backlinks from specific source"""
        # Simulate API calls to backlink sources
        simulated_links = []
        
        # Generate simulated backlinks for testing
        for i in range(min(config["max_links"] // len(config["sources"]), 50)):
            source_domain = f"example{i}.com"
            link = Backlink(
                link_id=hashlib.md5(f"{source_domain}_{target_domain}_{i}".encode()).hexdigest(),
                source_url=f"https://{source_domain}/page{i}",
                target_url=f"https://{target_domain}",
                source_domain=source_domain,
                anchor_text=f"Quality content from {target_domain}",
                anchor_text_type=AnchorTextType.PARTIAL_MATCH,
                link_type=LinkType.FOLLOW,
                link_quality=LinkQuality.MEDIUM,  # Will be updated in analysis
                link_status=LinkStatus.ACTIVE,
                domain_authority=np.random.uniform(20, 80),
                page_authority=np.random.uniform(15, 60),
                trust_flow=np.random.uniform(10, 50),
                citation_flow=np.random.uniform(15, 60),
                discovered_date=datetime.now() - timedelta(days=np.random.randint(1, 365)),
                last_checked=datetime.now(),
                context="article",
                surrounding_text=f"This is a great resource about {target_domain} content.",
                link_position="content",
                referring_ips={f"192.168.1.{i}"},
                social_signals={"shares": np.random.randint(0, 100), "likes": np.random.randint(0, 50)}
            )
            simulated_links.append(link)
        
        return simulated_links
    
    async def _analyze_link_quality(self, links: List[Backlink]) -> List[Backlink]:
        """Analyze quality of discovered backlinks"""
        analyzed_links = []
        
        for link in links:
            # Calculate quality score
            quality_score = await self._calculate_link_quality_score(link)
            
            # Classify link quality
            link.link_quality = self._classify_link_quality(quality_score)
            
            # Update domain profile
            await self._update_domain_profile(link.source_domain, link)
            
            analyzed_links.append(link)
        
        return analyzed_links
    
    async def _calculate_link_quality_score(self, link: Backlink) -> float:
        """Calculate comprehensive link quality score"""
        score = 0.0
        
        # Domain authority factor
        da_score = min(link.domain_authority / 100, 1.0)
        score += da_score * self.quality_factors["domain_authority"]["weight"]
        
        # Trust flow factor
        tf_score = min(link.trust_flow / 100, 1.0)
        score += tf_score * self.quality_factors["trust_flow"]["weight"]
        
        # Relevance factor (simplified)
        relevance_score = self._calculate_relevance_score(link)
        score += relevance_score * self.quality_factors["relevance"]["weight"]
        
        # Content quality factor
        content_quality = self._assess_content_quality(link)
        score += content_quality * self.quality_factors["content_quality"]["weight"]
        
        # Anchor text quality
        anchor_quality = self._assess_anchor_text_quality(link)
        score += anchor_quality * self.quality_factors["anchor_text_quality"]["weight"]
        
        # Link placement quality
        placement_quality = self._assess_link_placement(link)
        score += placement_quality * self.quality_factors["link_placement"]["weight"]
        
        return min(score, 1.0)
    
    def _calculate_relevance_score(self, link: Backlink) -> float:
        """Calculate relevance score between source and target"""
        # Simplified relevance calculation
        # In a real implementation, this would use NLP and topic modeling
        
        source_domain = link.source_domain.lower()
        target_context = link.context.lower()
        
        # Check for relevant keywords
        relevant_keywords = [
            "content", "creator", "social", "media", "influencer", 
            "video", "audio", "platform", "community"
        ]
        
        relevance_score = 0.0
        for keyword in relevant_keywords:
            if keyword in source_domain or keyword in target_context:
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _assess_content_quality(self, link: Backlink) -> float:
        """Assess content quality of linking page"""
        # Simplified content quality assessment
        quality_indicators = {
            "word_count": len(link.surrounding_text.split()) > 300,
            "social_signals": sum(link.social_signals.values()) > 10,
            "context_relevance": len(link.context) > 50,
            "anchor_context": len(link.surrounding_text) > 100
        }
        
        quality_score = sum(quality_indicators.values()) / len(quality_indicators)
        return quality_score
    
    def _assess_anchor_text_quality(self, link: Backlink) -> float:
        """Assess anchor text quality"""
        anchor_text = link.anchor_text.lower()
        
        # Quality factors
        quality_score = 0.0
        
        # Natural anchor text (not over-optimized)
        if not self._is_over_optimized_anchor(anchor_text):
            quality_score += 0.3
        
        # Appropriate length
        if 2 <= len(anchor_text.split()) <= 8:
            quality_score += 0.3
        
        # Contextual relevance
        if any(word in anchor_text for word in ["quality", "great", "excellent", "helpful"]):
            quality_score += 0.2
        
        # Brand mention
        if any(brand in anchor_text for brand in ["ainflue", "platform", "content"]):
            quality_score += 0.2
        
        return quality_score
    
    def _is_over_optimized_anchor(self, anchor_text: str) -> bool:
        """Check if anchor text is over-optimized"""
        # Simple over-optimization detection
        over_optimization_indicators = [
            len(anchor_text.split()) == 1 and len(anchor_text) > 15,  # Single long keyword
            anchor_text.count(" ") == 0 and len(anchor_text) > 20,    # No spaces, long
            anchor_text.lower() in ["click here", "read more", "visit site"]  # Generic spam
        ]
        
        return any(over_optimization_indicators)
    
    def _assess_link_placement(self, link: Backlink) -> float:
        """Assess link placement quality"""
        placement_scores = {
            "content": 1.0,      # In main content
            "sidebar": 0.6,      # In sidebar
            "footer": 0.3,       # In footer
            "comment": 0.4,      # In comments
            "author_bio": 0.7,   # In author bio
            "navigation": 0.5    # In navigation
        }
        
        return placement_scores.get(link.link_position, 0.5)
    
    def _classify_link_quality(self, quality_score: float) -> LinkQuality:
        """Classify link quality based on score"""
        if quality_score >= 0.8:
            return LinkQuality.EXCELLENT
        elif quality_score >= 0.6:
            return LinkQuality.HIGH
        elif quality_score >= 0.4:
            return LinkQuality.MEDIUM
        elif quality_score >= 0.2:
            return LinkQuality.LOW
        else:
            return LinkQuality.TOXIC
    
    async def _update_domain_profile(self, domain: str, link: Backlink):
        """Update domain authority profile"""
        if domain not in self.domain_profiles:
            self.domain_profiles[domain] = DomainProfile(
                domain=domain,
                domain_authority=link.domain_authority,
                page_authority=link.page_authority,
                trust_flow=link.trust_flow,
                citation_flow=link.citation_flow,
                spam_score=0.0,  # Would be fetched from API
                organic_traffic=0,
                backlink_count=1,
                referring_domains=1,
                social_authority=0.0,
                content_quality_score=0.0,
                niche_relevance=0.0,
                geographic_relevance=0.0
            )
        else:
            # Update existing profile
            profile = self.domain_profiles[domain]
            profile.backlink_count += 1
            profile.domain_authority = max(profile.domain_authority, link.domain_authority)
            profile.page_authority = max(profile.page_authority, link.page_authority)
    
    async def _update_backlink_database(self, links: List[Backlink]):
        """Update backlink database"""
        for link in links:
            self.backlinks[link.link_id] = link
    
    async def _analyze_anchor_text_distribution(self, target_domain: str) -> Dict[str, Any]:
        """Analyze anchor text distribution for target domain"""
        domain_links = [link for link in self.backlinks.values() if target_domain in link.target_url]
        
        if not domain_links:
            return {"total_links": 0}
        
        # Categorize anchor texts
        anchor_distribution = defaultdict(int)
        anchor_texts = defaultdict(int)
        
        for link in domain_links:
            anchor_distribution[link.anchor_text_type.value] += 1
            anchor_texts[link.anchor_text] += 1
        
        total_links = len(domain_links)
        
        # Calculate percentages
        anchor_percentages = {}
        for anchor_type, count in anchor_distribution.items():
            anchor_percentages[anchor_type] = (count / total_links) * 100
        
        # Get top anchor texts
        top_anchors = sorted(anchor_texts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Check anchor text health
        health_issues = []
        if anchor_percentages.get("exact_match", 0) > 15:
            health_issues.append("High exact match anchor text percentage (>15%)")
        
        if anchor_percentages.get("generic", 0) > 25:
            health_issues.append("High generic anchor text percentage (>25%)")
        
        if anchor_percentages.get("branded", 0) < 30:
            health_issues.append("Low branded anchor text percentage (<30%)")
        
        return {
            "total_links": total_links,
            "anchor_type_distribution": anchor_percentages,
            "top_anchor_texts": top_anchors,
            "anchor_text_diversity": len(anchor_texts),
            "health_issues": health_issues,
            "diversity_score": min(len(anchor_texts) / total_links, 1.0) if total_links > 0 else 0
        }
    
    async def _detect_toxic_links(self, links: List[Backlink]) -> Dict[str, Any]:
        """Detect toxic and potentially harmful links"""
        toxic_links = []
        suspicious_links = []
        
        for link in links:
            toxicity_score = await self._calculate_toxicity_score(link)
            
            if toxicity_score >= 0.8:
                toxic_links.append({
                    "link_id": link.link_id,
                    "source_url": link.source_url,
                    "toxicity_score": toxicity_score,
                    "toxicity_reasons": self._get_toxicity_reasons(link)
                })
                link.link_quality = LinkQuality.TOXIC
                self.toxic_domains.add(link.source_domain)
            
            elif toxicity_score >= 0.5:
                suspicious_links.append({
                    "link_id": link.link_id,
                    "source_url": link.source_url,
                    "toxicity_score": toxicity_score,
                    "review_reasons": self._get_toxicity_reasons(link)
                })
        
        return {
            "toxic_links": toxic_links,
            "suspicious_links": suspicious_links,
            "toxic_domains": list(self.toxic_domains),
            "disavow_recommendations": [link["source_url"] for link in toxic_links],
            "manual_review_needed": len(suspicious_links)
        }
    
    async def _calculate_toxicity_score(self, link: Backlink) -> float:
        """Calculate toxicity score for link"""
        toxicity_score = 0.0
        
        # Domain-based factors
        if any(pattern in link.source_domain for pattern in ["casino", "poker", "loan", "pharmacy"]):
            toxicity_score += 0.4
        
        # Spam score factor (simulated)
        spam_score = np.random.uniform(0, 100)  # Would come from API
        if spam_score > 70:
            toxicity_score += 0.3
        
        # Low authority factor
        if link.domain_authority < 20:
            toxicity_score += 0.2
        
        # Poor anchor text patterns
        if self._is_spammy_anchor_text(link.anchor_text):
            toxicity_score += 0.2
        
        # Link farm indicators
        if self._is_link_farm(link):
            toxicity_score += 0.3
        
        return min(toxicity_score, 1.0)
    
    def _is_spammy_anchor_text(self, anchor_text: str) -> bool:
        """Check if anchor text appears spammy"""
        spammy_patterns = [
            r"click here", r"read more", r"visit site", r"check this",
            r"buy now", r"get discount", r"free trial"
        ]
        
        anchor_lower = anchor_text.lower()
        return any(re.search(pattern, anchor_lower) for pattern in spammy_patterns)
    
    def _is_link_farm(self, link: Backlink) -> bool:
        """Check if link appears to be from a link farm"""
        # Simple link farm detection
        link_farm_indicators = [
            len(link.surrounding_text) < 50,  # Very short content
            link.link_position in ["footer", "sidebar"],  # Poor placement
            "directory" in link.source_url.lower(),  # Directory sites
            len(link.source_domain.split('.')[0]) > 20  # Very long domain names
        ]
        
        return sum(link_farm_indicators) >= 2
    
    def _get_toxicity_reasons(self, link: Backlink) -> List[str]:
        """Get reasons why link is considered toxic"""
        reasons = []
        
        if link.domain_authority < 20:
            reasons.append("Low domain authority")
        
        if any(pattern in link.source_domain for pattern in ["casino", "poker", "loan"]):
            reasons.append("Suspicious domain category")
        
        if self._is_spammy_anchor_text(link.anchor_text):
            reasons.append("Spammy anchor text")
        
        if self._is_link_farm(link):
            reasons.append("Potential link farm")
        
        return reasons
    
    async def _calculate_link_velocity(self, target_domain: str) -> Dict[str, Any]:
        """Calculate link building velocity"""
        domain_links = [link for link in self.backlinks.values() if target_domain in link.target_url]
        
        if not domain_links:
            return {"velocity": 0}
        
        # Sort links by discovery date
        sorted_links = sorted(domain_links, key=lambda x: x.discovered_date)
        
        # Calculate velocity for different time periods
        now = datetime.now()
        
        periods = {
            "last_7_days": 7,
            "last_30_days": 30,
            "last_90_days": 90,
            "last_365_days": 365
        }
        
        velocity_data = {}
        
        for period_name, days in periods.items():
            cutoff_date = now - timedelta(days=days)
            period_links = [link for link in sorted_links if link.discovered_date >= cutoff_date]
            
            velocity_data[period_name] = {
                "new_links": len(period_links),
                "links_per_day": len(period_links) / days,
                "quality_distribution": self._get_quality_distribution(period_links)
            }
        
        # Calculate velocity trend
        recent_velocity = velocity_data["last_30_days"]["links_per_day"]
        older_velocity = velocity_data["last_90_days"]["links_per_day"]
        
        if older_velocity > 0:
            velocity_trend = ((recent_velocity - older_velocity) / older_velocity) * 100
        else:
            velocity_trend = 0
        
        return {
            "velocity_data": velocity_data,
            "velocity_trend": velocity_trend,
            "velocity_health": self._assess_velocity_health(velocity_data)
        }
    
    def _get_quality_distribution(self, links: List[Backlink]) -> Dict[str, int]:
        """Get quality distribution for links"""
        distribution = defaultdict(int)
        for link in links:
            distribution[link.link_quality.value] += 1
        return dict(distribution)
    
    def _assess_velocity_health(self, velocity_data: Dict[str, Any]) -> str:
        """Assess link velocity health"""
        recent_velocity = velocity_data["last_30_days"]["links_per_day"]
        
        if recent_velocity > 10:
            return "potentially_suspicious"  # Too fast
        elif recent_velocity > 2:
            return "healthy_growth"
        elif recent_velocity > 0.5:
            return "moderate_growth"
        else:
            return "slow_growth"
    
    async def _get_top_referring_domains(self, links: List[Backlink]) -> List[Dict[str, Any]]:
        """Get top referring domains by authority and count"""
        domain_stats = defaultdict(lambda: {"count": 0, "max_authority": 0, "quality_score": 0})
        
        for link in links:
            domain = link.source_domain
            domain_stats[domain]["count"] += 1
            domain_stats[domain]["max_authority"] = max(domain_stats[domain]["max_authority"], link.domain_authority)
            
            # Calculate average quality score
            quality_scores = {"excellent": 5, "high": 4, "medium": 3, "low": 2, "toxic": 1}
            domain_stats[domain]["quality_score"] += quality_scores.get(link.link_quality.value, 3)
        
        # Calculate average quality scores
        for domain, stats in domain_stats.items():
            stats["avg_quality_score"] = stats["quality_score"] / stats["count"]
        
        # Sort by authority and count
        top_domains = sorted(
            domain_stats.items(),
            key=lambda x: (x[1]["max_authority"], x[1]["count"]),
            reverse=True
        )[:20]
        
        return [
            {
                "domain": domain,
                "link_count": stats["count"],
                "max_authority": stats["max_authority"],
                "avg_quality_score": stats["avg_quality_score"]
            }
            for domain, stats in top_domains
        ]
    
    async def _generate_backlink_recommendations(self, target_domain: str, links: List[Backlink]) -> List[Dict[str, Any]]:
        """Generate backlink optimization recommendations"""
        recommendations = []
        
        # Analyze current link profile
        anchor_analysis = await self._analyze_anchor_text_distribution(target_domain)
        toxic_analysis = await self._detect_toxic_links(links)
        
        # Anchor text diversity recommendations
        if anchor_analysis.get("diversity_score", 0) < 0.5:
            recommendations.append({
                "type": "anchor_text_diversity",
                "priority": "high",
                "recommendation": "Improve anchor text diversity",
                "details": "Current anchor text diversity is low. Focus on building links with varied, natural anchor texts.",
                "action_items": [
                    "Target branded anchor texts",
                    "Use partial match keywords",
                    "Include natural, contextual anchor texts"
                ]
            })
        
        # Toxic link cleanup
        if len(toxic_analysis.get("toxic_links", [])) > 0:
            recommendations.append({
                "type": "toxic_link_cleanup",
                "priority": "critical",
                "recommendation": "Remove toxic backlinks",
                "details": f"Found {len(toxic_analysis['toxic_links'])} toxic links that may harm rankings.",
                "action_items": [
                    "Contact webmasters for link removal",
                    "Submit disavow file to Google",
                    "Monitor for new toxic links"
                ]
            })
        
        # Link building opportunities
        high_quality_ratio = len([link for link in links if link.link_quality in [LinkQuality.HIGH, LinkQuality.EXCELLENT]]) / max(len(links), 1)
        
        if high_quality_ratio < 0.3:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "medium",
                "recommendation": "Focus on high-quality link building",
                "details": "Only {:.1%} of links are high quality. Target authoritative, relevant domains.".format(high_quality_ratio),
                "action_items": [
                    "Research high-authority domains in your niche",
                    "Create linkable assets",
                    "Implement outreach campaigns"
                ]
            })
        
        return recommendations
    
    def get_backlink_profile(self, target_domain: str) -> Dict[str, Any]:
        """Get comprehensive backlink profile for domain"""
        domain_links = [link for link in self.backlinks.values() if target_domain in link.target_url]
        
        if not domain_links:
            return {"domain": target_domain, "total_backlinks": 0}
        
        # Calculate profile metrics
        total_links = len(domain_links)
        unique_domains = len(set(link.source_domain for link in domain_links))
        avg_authority = sum(link.domain_authority for link in domain_links) / total_links
        
        quality_distribution = self._get_quality_distribution(domain_links)
        
        return {
            "domain": target_domain,
            "total_backlinks": total_links,
            "unique_referring_domains": unique_domains,
            "average_domain_authority": avg_authority,
            "quality_distribution": quality_distribution,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "total_backlinks_tracked": len(self.backlinks),
            "unique_domains_tracked": len(self.domain_profiles),
            "toxic_domains_identified": len(self.toxic_domains),
            "link_opportunities": len(self.link_opportunities),
            "last_updated": datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_backlink_monitoring():
        """Test backlink monitoring functionality"""
        monitor = BacklinkMonitoringSystem()
        
        # Test backlink discovery
        target_domain = "ainflue.com"
        discovery_result = await monitor.discover_backlinks(target_domain, "comprehensive")
        print(f"Backlink discovery result: {discovery_result}")
        
        # Test backlink profile
        profile = monitor.get_backlink_profile(target_domain)
        print(f"Backlink profile: {profile}")
        
        # Test monitoring status
        status = monitor.get_monitoring_status()
        print(f"Monitoring status: {status}")
    
    # Run test
    asyncio.run(test_backlink_monitoring())