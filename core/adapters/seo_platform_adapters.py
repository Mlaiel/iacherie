"""SEO Platform Adapters - Search Engine Optimization Integration

This module provides comprehensive adapter infrastructure for integrating with
SEO platforms, analytics tools, and search engine optimization services.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Multi-platform SEO monitoring (Google Search Console, SEMrush, Ahrefs, etc.)
- Keyword research and tracking automation
- Content optimization recommendations
- Backlink monitoring and analysis
- Technical SEO auditing
- Competitor analysis and tracking
"""

import asyncio
import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import aiohttp
from urllib.parse import urljoin, urlparse
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, PlatformError
)

logger = logging.getLogger(__name__)

class SEOPlatform(Enum):
    """
Supported SEO platforms and tools."""

    GOOGLE_SEARCH_CONSOLE = "google_search_console"
    GOOGLE_ANALYTICS = "google_analytics"
    SEMRUSH = "semrush"
    AHREFS = "ahrefs"
    MOZ = "moz"
    BRIGHTEDGE = "brightedge"
    CONDUCTOR = "conductor"
    SCREAMING_FROG = "screaming_frog"
    SERPSTAT = "serpstat"
    UBERSUGGEST = "ubersuggest"
    MAJESTIC = "majestic"
    SISTRIX = "sistrix"

class SEOMetricType(Enum):
    """Types of SEO metrics."""

    ORGANIC_TRAFFIC = "organic_traffic"
    KEYWORD_RANKINGS = "keyword_rankings"
    BACKLINKS = "backlinks"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_AUTHORITY = "page_authority"
    TECHNICAL_ISSUES = "technical_issues"
    CONTENT_GAPS = "content_gaps"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    LOCAL_SEO = "local_seo"
    MOBILE_USABILITY = "mobile_usability"
    CORE_WEB_VITALS = "core_web_vitals"
    SITE_SPEED = "site_speed"

class KeywordDifficulty(Enum):
    """Keyword difficulty levels."""

    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

@dataclass
class SEOKeyword:
    """Represents an SEO keyword with its metrics."""
    keyword: str
    search_volume: int
    keyword_difficulty: KeywordDifficulty
    cost_per_click: float
    competition: float
    current_position: Optional[int] = None
    best_position: Optional[int] = None
    url_ranking: Optional[str] = None
    intent: Optional[str] = None  # informational, commercial, transactional, navigational
    related_keywords: List[str] = field(default_factory=list)
    monthly_trend: List[int] = field(default_factory=list)  # 12 months of data
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BacklinkProfile:
    """
Represents a backlink profile."""
    referring_domains: int
    total_backlinks: int
    dofollow_links: int
    nofollow_links: int
    domain_rating: float
    url_rating: float
    organic_traffic: int
    organic_keywords: int
    top_backlinks: List[Dict[str, Any]] = field(default_factory=list)
    lost_backlinks: List[Dict[str, Any]] = field(default_factory=list)
    new_backlinks: List[Dict[str, Any]] = field(default_factory=list)
    toxic_backlinks: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TechnicalSEOIssue:
    """
Represents a technical SEO issue."""
    issue_type: str
    severity: str  # critical, high, medium, low
    affected_pages: List[str]
    description: str
    recommendation: str
    impact_score: float
    detected_at: datetime
    status: str = "open"  # open, in_progress, resolved, ignored

@dataclass
class ContentOptimization:
    """Content optimization recommendations."""
    target_keyword: str
    current_score: float
    potential_score: float
    recommendations: List[Dict[str, Any]]
    missing_keywords: List[str]
    content_length_recommendation: Optional[int] = None
    readability_score: Optional[float] = None
    semantic_keywords: List[str] = field(default_factory=list)

@dataclass
class CompetitorAnalysis:
    """
Competitor SEO analysis."""
    competitor_domain: str
    domain_authority: float
    organic_traffic: int
    organic_keywords: int
    backlinks: int
    content_gaps: List[str]
    top_keywords: List[SEOKeyword]
    backlink_gaps: List[Dict[str, Any]]
    last_analyzed: datetime = field(default_factory=datetime.utcnow)

class BaseSEOAdapter(BasePlatformAdapter):
    """
Base class for SEO platform adapters."""
    
    def __init__(
        self, 
        platform_name: str,
        seo_platform: SEOPlatform,
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ):
        super().__init__(
            platform_name=platform_name,
            platform_type=PlatformType.SEO_PLATFORM,
            credentials=credentials,
            rate_limit_config=RateLimitConfig(
                requests_per_minute=60,  # Most SEO tools have rate limits
                burst_limit=10,
                rate_limit_window=60
            )
        )
        self.seo_platform = seo_platform
        self.config = config
        self.tracked_domains: Set[str] = set()
        self.keyword_data: Dict[str, SEOKeyword] = {}
        self.backlink_profiles: Dict[str, BacklinkProfile] = {}
        self.technical_issues: List[TechnicalSEOIssue] = []
    
    @abstractmethod
    async def track_domain(self, domain: str) -> bool:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "track_domain",
                        "value": domain if domain else 0,
        try:
                    # Request validation
                    if not domain:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_keyword_rankings_request(domain)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
                    # Request validation
                    if not domain:
        try:
            logger.info(f"Executing audit_technical_seo")
            
            # Implementation for audit_technical_seo
            # TODO: Add specific business logic here
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess_analyze_competitors_input(domain)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_analyze_competitors_result(result)
            
                    logger.info(f"AI processing analyze_competitors completed")
                    return final_result
            
                except Exception as e:
        try:
            logger.info(f"Executing research_keywords")
            
            # Implementation for research_keywords
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"research_keywords completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"research_keywords failed: {e}")
            raise
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess_analyze_competitors_result(result)
            
                    logger.info(f"AI processing analyze_competitors completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing analyze_competitors failed: {e}")
                    raise
            logger.info(f"audit_technical_seo completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"audit_technical_seo failed: {e}")
            raise
                    result = await self._handle_get_backlink_profile_request(domain)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_backlink_profile failed: {e}")
                    return {"status": "error", "message": str(e)}
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_keyword_rankings failed: {e}")
                    return {"status": "error", "message": str(e)}
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric track_domain collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection track_domain failed: {e}")
                    return None
    @abstractmethod
    async def get_keyword_rankings(self, domain: str, keywords: List[str]) -> List[SEOKeyword]:
        """
Get keyword rankings for a domain."""
        pass
    
    @abstractmethod
    async def get_backlink_profile(self, domain: str) -> Optional[BacklinkProfile]:
        """
Get backlink profile for a domain."""
        pass
    
    @abstractmethod
    async def audit_technical_seo(self, domain: str) -> List[TechnicalSEOIssue]:
        """
Perform technical SEO audit."""
        pass
    
    @abstractmethod
    async def analyze_competitors(self, domain: str, competitors: List[str]) -> List[CompetitorAnalysis]:
        """
Analyze competitors for a domain."""
        pass
    
    @abstractmethod
    async def research_keywords(self, seed_keywords: List[str], location: str = "US") -> List[SEOKeyword]:
        """Research keywords based on seed keywords."""
        pass
    
    async def calculate_keyword_opportunity(self, keyword: SEOKeyword) -> float:
        """
Calculate keyword opportunity score."""
        # Factors: search volume, difficulty, current position, trend
        volume_score = min(keyword.search_volume / 10000, 1.0) * 0.3
        
        difficulty_scores = {
            KeywordDifficulty.VERY_EASY: 1.0,
            KeywordDifficulty.EASY: 0.8,
            KeywordDifficulty.MEDIUM: 0.6,
            KeywordDifficulty.HARD: 0.4,
            KeywordDifficulty.VERY_HARD: 0.2
        }
        difficulty_score = difficulty_scores.get(keyword.keyword_difficulty, 0.5) * 0.3
        
        position_score = 0.0
        if keyword.current_position:
            if keyword.current_position <= 3:
                position_score = 0.2
            elif keyword.current_position <= 10:
                position_score = 0.3
            elif keyword.current_position <= 20:
                position_score = 0.4
            else:
                position_score = 0.6  # High opportunity for improvement
        else:
            position_score = 0.8  # Not ranking yet, high opportunity
        
        # Trend analysis
        trend_score = 0.0
        if keyword.monthly_trend and len(keyword.monthly_trend) >= 3:
            recent_trend = sum(keyword.monthly_trend[-3:]) / 3
            overall_avg = sum(keyword.monthly_trend) / len(keyword.monthly_trend)
            if recent_trend > overall_avg:
                trend_score = 0.2
            else:
                trend_score = 0.1
        
        opportunity_score = volume_score + difficulty_score + position_score + trend_score
        return min(opportunity_score, 1.0)
    
    async def prioritize_keywords(self, keywords: List[SEOKeyword]) -> List[SEOKeyword]:
        """
Prioritize keywords based on opportunity score."""
        keyword_scores = []
        
        for keyword in keywords:
            opportunity_score = await self.calculate_keyword_opportunity(keyword)
            keyword_scores.append((keyword, opportunity_score))
        
        # Sort by opportunity score (descending)
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [keyword for keyword, score in keyword_scores]

class GoogleSearchConsoleAdapter(BaseSEOAdapter):
    """
Google Search Console API adapter."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="google_search_console",
            seo_platform=SEOPlatform.GOOGLE_SEARCH_CONSOLE,
            credentials=credentials,
            config=config
        )
        self.api_base_url = "https://www.googleapis.com/webmasters/v3"
    
    async def track_domain(self, domain: str) -> bool:
        """Add a domain to Google Search Console tracking."""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            # First verify if the site exists
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/sites/{domain}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        self.tracked_domains.add(domain)
                        logger.info(f"Domain verified in Google Search Console: {domain}")
                        return True
                    else:
                        logger.warning(f"Domain not verified in Google Search Console: {domain}")
                        return False
            
        except Exception as e:
        try:
            logger.info(f"Executing audit_technical_seo")
            
            # Implementation for audit_technical_seo
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"audit_technical_seo completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"audit_technical_seo failed: {e}")
            raise
                                    keyword=query,
                                    search_volume=impressions,  # Approximation
                                    keyword_difficulty=KeywordDifficulty.MEDIUM,  # GSC doesn't provide this
                                    cost_per_click=0.0,  # GSC doesn't provide this
                                    competition=0.0,  # GSC doesn't provide this
                                    current_position=int(position) if position else None,
                                    url_ranking=page
                                )
                                results.append(keyword_obj)
                                self.keyword_data[query] = keyword_obj
                    
        except Exception as e:
            logger.error(f"Google Search Console keyword rankings error: {str(e)}")
        
        return results
    
    async def get_backlink_profile(self, domain: str) -> Optional[BacklinkProfile]:
        """Google Search Console doesn't provide comprehensive backlink data."""
        # GSC has limited backlink data compared to dedicated tools
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/sites/{domain}/sitemaps",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        # GSC doesn't provide full backlink profile
                        # Return basic structure with limited data
                        profile = BacklinkProfile(
                            referring_domains=0,
                            total_backlinks=0,
                            dofollow_links=0,
                            nofollow_links=0,
                            domain_rating=0.0,
                            url_rating=0.0,
                            organic_traffic=0,
                            organic_keywords=0
                        )
                        return profile
                    
        except Exception as e:
            logger.error(f"Google Search Console backlink profile error: {str(e)}")
        
        return None
    
    async def audit_technical_seo(self, domain: str) -> List[TechnicalSEOIssue]:
        """Get technical SEO issues from Google Search Console."""
        issues = []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            # Check for crawl errors
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base_url}/sites/{domain}/crawlErrors",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for category, errors in data.items():
                            if isinstance(errors, list):
                                for error in errors:
                                    issue = TechnicalSEOIssue(
                                        issue_type=f"crawl_error_{category}",
                                        severity="high",
                                        affected_pages=[error.get('pageUrl', '')],
                                        description=f"Crawl error in {category}: {error.get('errorType', '')}",
                                        recommendation="Fix the URL or implement proper redirects",
                                        impact_score=0.8,
                                        detected_at=datetime.utcnow()
                                    )
                                    issues.append(issue)
                
                # Check Core Web Vitals
                async with session.get(
                    f"{self.api_base_url}/sites/{domain}/urlCrawlErrorsCounts",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        # Process Core Web Vitals data if available
                        pass
                    
        except Exception as e:
            logger.error(f"Google Search Console technical audit error: {str(e)}")
        
        return issues
    
    async def analyze_competitors(self, domain: str, competitors: List[str]) -> List[CompetitorAnalysis]:
        """Google Search Console doesn't provide competitor analysis."""
        # GSC is focused on your own domain, not competitors
        return []
    
    async def research_keywords(self, seed_keywords: List[str], location: str = "US") -> List[SEOKeyword]:
        """Google Search Console doesn't provide keyword research."""
        # Use existing performance data to suggest related keywords
        related_keywords = []
        
        for seed in seed_keywords:
            # Find related queries from existing data
            for keyword, data in self.keyword_data.items():
                if any(seed.lower() in keyword.lower() for seed in seed_keywords):
                    related_keywords.append(data)
        
        return related_keywords

class SEMrushAdapter(BaseSEOAdapter):
    """
SEMrush API adapter implementation."""
    
    def __init__(self, credentials: AdapterCredentials, config: Dict[str, Any]):
        super().__init__(
            platform_name="semrush",
            seo_platform=SEOPlatform.SEMRUSH,
            credentials=credentials,
            config=config
        )
        self.api_base_url = "https://api.semrush.com"
    
    async def track_domain(self, domain: str) -> bool:
        """Add domain to SEMrush tracking."""
        self.tracked_domains.add(domain)
        logger.info(f"Domain added to SEMrush tracking: {domain}")
        return True
    
    async def get_keyword_rankings(self, domain: str, keywords: List[str]) -> List[SEOKeyword]:
        """Get keyword rankings from SEMrush."""
        results = []
        
        try:
            params = {
                "type": "domain_organic",
                "key": self.credentials.api_key,
                "display_limit": 1000,
                "export_columns": "Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc",
                "domain": domain,
                "database": self.config.get('database', 'us')
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_base_url,
                    params=params
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        lines = text.strip().split('\n')
                        
                        if len(lines) > 1:  # Skip header
                            for line in lines[1:]:
                                parts = line.split(';')
                                if len(parts) >= 9:
                                    keyword = parts[0].strip('"')
                                    position = int(parts[1]) if parts[1].isdigit() else None
                                    previous_position = int(parts[2]) if parts[2].isdigit() else None
                                    search_volume = int(parts[4]) if parts[4].isdigit() else 0
                                    cpc = float(parts[5]) if parts[5].replace('.', '').isdigit() else 0.0
                                    url = parts[6].strip('"')
                                    traffic = int(parts[7]) if parts[7].isdigit() else 0
                                    competition = float(parts[8]) if parts[8].replace('.', '').isdigit() else 0.0
                                    
                                    # Determine keyword difficulty based on competition
                                    if competition <= 0.2:
                                        difficulty = KeywordDifficulty.EASY
                                    elif competition <= 0.4:
                                        difficulty = KeywordDifficulty.MEDIUM
                                    elif competition <= 0.6:
                                        difficulty = KeywordDifficulty.HARD
                                    else:
                                        difficulty = KeywordDifficulty.VERY_HARD
                                    
                                    # Filter by target keywords if provided
                                    if not keywords or any(target_keyword.lower() in keyword.lower() for target_keyword in keywords):
                                        keyword_obj = SEOKeyword(
                                            keyword=keyword,
                                            search_volume=search_volume,
                                            keyword_difficulty=difficulty,
                                            cost_per_click=cpc,
                                            competition=competition,
                                            current_position=position,
                                            best_position=previous_position,
                                            url_ranking=url
                                        )
                                        results.append(keyword_obj)
                                        self.keyword_data[keyword] = keyword_obj
                    else:
                        logger.error(f"SEMrush API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"SEMrush keyword rankings error: {str(e)}")
        
        return results
    
    async def get_backlink_profile(self, domain: str) -> Optional[BacklinkProfile]:
        """Get backlink profile from SEMrush."""
        try:
            params = {
                "type": "backlinks_overview",
                "key": self.credentials.api_key,
                "target": domain,
                "target_type": "root_domain"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_base_url,
                    params=params
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        lines = text.strip().split('\n')
                        
                        if len(lines) > 1:
                            data = lines[1].split(';')
                            if len(data) >= 8:
                                profile = BacklinkProfile(
                                    referring_domains=int(data[1]) if data[1].isdigit() else 0,
                                    total_backlinks=int(data[0]) if data[0].isdigit() else 0,
                                    dofollow_links=int(data[2]) if data[2].isdigit() else 0,
                                    nofollow_links=int(data[3]) if data[3].isdigit() else 0,
                                    domain_rating=float(data[4]) if data[4].replace('.', '').isdigit() else 0.0,
                                    url_rating=0.0,  # SEMrush doesn't provide URL rating like Ahrefs
                                    organic_traffic=int(data[6]) if data[6].isdigit() else 0,
                                    organic_keywords=int(data[7]) if data[7].isdigit() else 0
                                )
                                
                                self.backlink_profiles[domain] = profile
                                return profile
                    
        except Exception as e:
            logger.error(f"SEMrush backlink profile error: {str(e)}")
        
        return None
    
    async def audit_technical_seo(self, domain: str) -> List[TechnicalSEOIssue]:
        """SEMrush doesn't provide comprehensive technical SEO audit via API."""
        # SEMrush API is limited for technical audits
        # This would typically require Site Audit tool which has limited API access
        return []
    
    async def analyze_competitors(self, domain: str, competitors: List[str]) -> List[CompetitorAnalysis]:
        """
Analyze competitors using SEMrush."""
        analyses = []
        
        for competitor in competitors:
            try:
                # Get competitor organic data
                params = {
                    "type": "domain_organic",
                    "key": self.credentials.api_key,
                    "display_limit": 100,
                    "export_columns": "Ph,Po,Nq,Cp",
                    "domain": competitor,
                    "database": self.config.get('database', 'us')
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.api_base_url,
                        params=params
                    ) as response:
                        if response.status == 200:
                            text = await response.text()
                            lines = text.strip().split('\n')
                            
                            top_keywords = []
                            organic_traffic = 0
                            
                            if len(lines) > 1:
                                for line in lines[1:]:
                                    parts = line.split(';')
                                    if len(parts) >= 4:
                                        keyword = parts[0].strip('"')
                                        position = int(parts[1]) if parts[1].isdigit() else None
                                        search_volume = int(parts[2]) if parts[2].isdigit() else 0
                                        cpc = float(parts[3]) if parts[3].replace('.', '').isdigit() else 0.0
                                        
                                        keyword_obj = SEOKeyword(
                                            keyword=keyword,
                                            search_volume=search_volume,
                                            keyword_difficulty=KeywordDifficulty.MEDIUM,
                                            cost_per_click=cpc,
                                            competition=0.5,
                                            current_position=position
                                        )
                                        top_keywords.append(keyword_obj)
                                        
                                        # Estimate traffic
                                        if position and position <= 10:
                                            ctr_rates = {1: 0.32, 2: 0.24, 3: 0.18, 4: 0.13, 5: 0.09, 6: 0.06, 7: 0.04, 8: 0.03, 9: 0.02, 10: 0.02}
                                            estimated_traffic = search_volume * ctr_rates.get(position, 0.01)
                                            organic_traffic += int(estimated_traffic)
                            
                            # Get backlink data
                            backlink_profile = await self.get_backlink_profile(competitor)
                            
                            analysis = CompetitorAnalysis(
                                competitor_domain=competitor,
                                domain_authority=backlink_profile.domain_rating if backlink_profile else 0.0,
                                organic_traffic=organic_traffic,
                                organic_keywords=len(top_keywords),
                                backlinks=backlink_profile.total_backlinks if backlink_profile else 0,
                                content_gaps=[],  # Would need additional analysis
                                top_keywords=top_keywords[:20],  # Top 20 keywords
                                backlink_gaps=[]  # Would need additional analysis
                            )
                            analyses.append(analysis)
                            
            except Exception as e:
                logger.error(f"SEMrush competitor analysis error for {competitor}: {str(e)}")
        
        return analyses
    
    async def research_keywords(self, seed_keywords: List[str], location: str = "US") -> List[SEOKeyword]:
        """Research keywords using SEMrush."""
        all_keywords = []
        
        try:
            for seed in seed_keywords:
                params = {
                    "type": "phrase_related",
                    "key": self.credentials.api_key,
                    "phrase": seed,
                    "display_limit": 100,
                    "export_columns": "Ph,Nq,Cp,Co",
                    "database": self.config.get('database', 'us')
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.api_base_url,
                        params=params
                    ) as response:
                        if response.status == 200:
                            text = await response.text()
                            lines = text.strip().split('\n')
                            
                            if len(lines) > 1:
                                for line in lines[1:]:
                                    parts = line.split(';')
                                    if len(parts) >= 4:
                                        keyword = parts[0].strip('"')
                                        search_volume = int(parts[1]) if parts[1].isdigit() else 0
                                        cpc = float(parts[2]) if parts[2].replace('.', '').isdigit() else 0.0
                                        competition = float(parts[3]) if parts[3].replace('.', '').isdigit() else 0.0
                                        
                                        # Determine difficulty
                                        if competition <= 0.2:
                                            difficulty = KeywordDifficulty.EASY
                                        elif competition <= 0.4:
                                            difficulty = KeywordDifficulty.MEDIUM
                                        elif competition <= 0.6:
                                            difficulty = KeywordDifficulty.HARD
                                        else:
                                            difficulty = KeywordDifficulty.VERY_HARD
                                        
                                        keyword_obj = SEOKeyword(
                                            keyword=keyword,
                                            search_volume=search_volume,
                                            keyword_difficulty=difficulty,
                                            cost_per_click=cpc,
                                            competition=competition,
                                            related_keywords=[seed]
                                        )
                                        all_keywords.append(keyword_obj)
                        
        except Exception as e:
            logger.error(f"SEMrush keyword research error: {str(e)}")
        
        return all_keywords

class SEOAdapterFactory:
    """Factory for creating SEO platform adapters."""
    
    _adapters = {
        SEOPlatform.GOOGLE_SEARCH_CONSOLE: GoogleSearchConsoleAdapter,
        SEOPlatform.SEMRUSH: SEMrushAdapter
    }
    
    @classmethod
    def create_adapter(
        cls, 
        platform: SEOPlatform, 
        credentials: AdapterCredentials, 
        config: Dict[str, Any]
    ) -> BaseSEOAdapter:
        """
Create an SEO adapter instance."""
        adapter_class = cls._adapters.get(platform)
        if not adapter_class:
            raise ValueError(f"Unsupported SEO platform: {platform}")
        
        return adapter_class(credentials, config)
    
    @classmethod
    def get_supported_platforms(cls) -> List[SEOPlatform]:
        """Get list of supported SEO platforms."""
        return list(cls._adapters.keys())

class SEOAdapterManager:
    """
Manager for SEO adapter instances and comprehensive analysis."""
    
    def __init__(self):
        self.adapters: Dict[SEOPlatform, BaseSEOAdapter] = {}
        self.primary_platforms = [SEOPlatform.GOOGLE_SEARCH_CONSOLE, SEOPlatform.SEMRUSH]
        self.tracked_domains: Set[str] = set()
    
    def register_adapter(self, platform: SEOPlatform, adapter: BaseSEOAdapter):
        """
Register an SEO adapter."""
        self.adapters[platform] = adapter
        logger.info(f"Registered SEO adapter for platform: {platform.value}")
    
    async def comprehensive_domain_analysis(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis across all platforms."""
        results = {
            'domain': domain,
            'analysis_date': datetime.utcnow().isoformat(),
            'keyword_data': {},
            'backlink_profiles': {},
            'technical_issues': [],
            'competitor_analysis': {},
            'recommendations': []
        }
        
        # Track domain across all platforms
        for platform, adapter in self.adapters.items():
            try:
                await adapter.track_domain(domain)
            except Exception as e:
                logger.error(f"Failed to track domain on {platform.value}: {str(e)}")
        
        # Collect keyword data
        all_keywords = []
        for platform, adapter in self.adapters.items():
            try:
                keywords = await adapter.get_keyword_rankings(domain, [])
                results['keyword_data'][platform.value] = [
                    {
                        'keyword': kw.keyword,
                        'position': kw.current_position,
                        'search_volume': kw.search_volume,
                        'difficulty': kw.keyword_difficulty.value
                    } for kw in keywords
                ]
                all_keywords.extend(keywords)
            except Exception as e:
                logger.error(f"Failed to get keywords from {platform.value}: {str(e)}")
        
        # Collect backlink profiles
        for platform, adapter in self.adapters.items():
            try:
                backlink_profile = await adapter.get_backlink_profile(domain)
                if backlink_profile:
                    results['backlink_profiles'][platform.value] = {
                        'referring_domains': backlink_profile.referring_domains,
                        'total_backlinks': backlink_profile.total_backlinks,
                        'domain_rating': backlink_profile.domain_rating,
                        'organic_traffic': backlink_profile.organic_traffic
                    }
            except Exception as e:
                logger.error(f"Failed to get backlinks from {platform.value}: {str(e)}")
        
        # Collect technical issues
        for platform, adapter in self.adapters.items():
            try:
                issues = await adapter.audit_technical_seo(domain)
                results['technical_issues'].extend([
                    {
                        'platform': platform.value,
                        'issue_type': issue.issue_type,
                        'severity': issue.severity,
                        'affected_pages': len(issue.affected_pages),
                        'description': issue.description,
                        'recommendation': issue.recommendation
                    } for issue in issues
                ])
            except Exception as e:
                logger.error(f"Failed to get technical issues from {platform.value}: {str(e)}")
        
        # Generate recommendations
        results['recommendations'] = await self._generate_recommendations(all_keywords, results)
        
        return results
    
    async def keyword_gap_analysis(self, domain: str, competitors: List[str]) -> Dict[str, Any]:
        """Perform keyword gap analysis against competitors."""
        gap_analysis = {
            'domain': domain,
            'competitors': competitors,
            'keyword_gaps': [],
            'opportunity_score': 0.0
        }
        
        # Get domain keywords
        domain_keywords = set()
        for platform, adapter in self.adapters.items():
            try:
                keywords = await adapter.get_keyword_rankings(domain, [])
                domain_keywords.update(kw.keyword for kw in keywords)
            except Exception as e:
                logger.error(f"Failed to get domain keywords from {platform.value}: {str(e)}")
        
        # Analyze each competitor
        all_competitor_keywords = {}
        for competitor in competitors:
            competitor_keywords = set()
            for platform, adapter in self.adapters.items():
                try:
                    if hasattr(adapter, 'analyze_competitors'):
                        analyses = await adapter.analyze_competitors(domain, [competitor])
                        if analyses:
                            competitor_keywords.update(kw.keyword for kw in analyses[0].top_keywords)
                except Exception as e:
                    logger.error(f"Failed to analyze competitor {competitor} on {platform.value}: {str(e)}")
            
            all_competitor_keywords[competitor] = competitor_keywords
        
        # Find gaps
        for competitor, competitor_keywords in all_competitor_keywords.items():
            gaps = competitor_keywords - domain_keywords
            gap_analysis['keyword_gaps'].extend([
                {'keyword': gap, 'competitor': competitor} for gap in gaps
            ])
        
        # Calculate opportunity score
        gap_analysis['opportunity_score'] = len(gap_analysis['keyword_gaps']) / max(len(domain_keywords), 1)
        
        return gap_analysis
    
    async def _generate_recommendations(self, keywords: List[SEOKeyword], analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate SEO recommendations based on analysis."""
        recommendations = []
        
        # Keyword recommendations
        high_opportunity_keywords = []
        for platform, adapter in self.adapters.items():
            try:
                prioritized = await adapter.prioritize_keywords(keywords)
                high_opportunity_keywords.extend(prioritized[:10])  # Top 10 from each platform
            except Exception as e:
                logger.error(f"Failed to prioritize keywords on {platform.value}: {str(e)}")
        
        if high_opportunity_keywords:
            recommendations.append({
                'type': 'keyword_optimization',
                'priority': 'high',
                'title': 'High-Opportunity Keywords',
                'description': f'Focus on optimizing for {len(high_opportunity_keywords)} high-opportunity keywords',
                'action_items': [kw.keyword for kw in high_opportunity_keywords[:5]]
            })
        
        # Technical recommendations
        technical_issues = analysis_results.get('technical_issues', [])
        critical_issues = [issue for issue in technical_issues if issue.get('severity') == 'critical']
        if critical_issues:
            recommendations.append({
                'type': 'technical_seo',
                'priority': 'urgent',
                'title': 'Critical Technical Issues',
                'description': f'Fix {len(critical_issues)} critical technical SEO issues',
                'action_items': [issue.get('description', '') for issue in critical_issues[:3]]
            })
        
        # Backlink recommendations
        backlink_profiles = analysis_results.get('backlink_profiles', {})
        if backlink_profiles:
            avg_domain_rating = sum(
                profile.get('domain_rating', 0) for profile in backlink_profiles.values()
            ) / len(backlink_profiles)
            
            if avg_domain_rating < 30:
                recommendations.append({
                    'type': 'link_building',
                    'priority': 'medium',
                    'title': 'Improve Domain Authority',
                    'description': 'Focus on building high-quality backlinks to improve domain authority',
                    'action_items': ['Target industry publications', 'Guest posting strategy', 'Resource page outreach']
                })
        
        return recommendations

# Export all classes and functions
__all__ = [
    'SEOPlatform', 'SEOMetricType', 'KeywordDifficulty',
    'SEOKeyword', 'BacklinkProfile', 'TechnicalSEOIssue', 'ContentOptimization', 'CompetitorAnalysis',
    'BaseSEOAdapter', 'GoogleSearchConsoleAdapter', 'SEMrushAdapter',
    'SEOAdapterFactory', 'SEOAdapterManager'
]
