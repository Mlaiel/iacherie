#!/usr/bin/env python3
"""
Ainflue Platform - Search Engines Integration Module
Enterprise-grade search engine APIs for SEO optimization and content discovery

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited

Integration-Level: Level 3 (integrations/third_party/)
Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
SEO Focus: Search optimization, keyword analysis, ranking monitoring, competitor analysis
"""

import asyncio
import logging
import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import aiohttp
import structlog
from pydantic import BaseModel, Field, validator
import requests
from urllib.parse import quote, urlencode
import xml.etree.ElementTree as ET

# Configure structured logging
logger = structlog.get_logger(__name__)

class SearchEngine(str, Enum):
    """Supported search engines"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"

class SearchType(str, Enum):
    """Types of search queries"""
    WEB = "web"
    IMAGES = "images"
    VIDEOS = "videos"
    NEWS = "news"
    SHOPPING = "shopping"
    ACADEMIC = "academic"
    SOCIAL = "social"
    LOCAL = "local"

class SEOMetric(str, Enum):
    """SEO metrics to track"""
    RANKING_POSITION = "ranking_position"
    SEARCH_VOLUME = "search_volume"
    KEYWORD_DIFFICULTY = "keyword_difficulty"
    CLICK_THROUGH_RATE = "click_through_rate"
    BACKLINKS_COUNT = "backlinks_count"
    DOMAIN_AUTHORITY = "domain_authority"
    PAGE_AUTHORITY = "page_authority"
    ORGANIC_TRAFFIC = "organic_traffic"

@dataclass
class SearchQuery:
    """Search query configuration"""
    query: str
    search_engine: SearchEngine = SearchEngine.GOOGLE
    search_type: SearchType = SearchType.WEB
    language: str = "en"
    country: str = "US"
    limit: int = 10
    offset: int = 0
    date_range: Optional[str] = None  # "day", "week", "month", "year"
    safe_search: bool = True
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    url: str
    description: str
    rank: int
    search_engine: SearchEngine
    search_type: SearchType
    domain: str = ""
    thumbnail: Optional[str] = None
    date_published: Optional[datetime] = None
    snippet: Optional[str] = None
    featured_snippet: bool = False
    local_pack: bool = False
    knowledge_panel: bool = False
    related_queries: List[str] = field(default_factory=list)
    
class SearchResponse(BaseModel):
    """Complete search response"""
    query: str
    search_engine: SearchEngine
    search_type: SearchType
    total_results: int = 0
    results: List[SearchResult] = Field(default_factory=list)
    related_searches: List[str] = Field(default_factory=list)
    auto_complete: List[str] = Field(default_factory=list)
    featured_snippets: List[Dict[str, Any]] = Field(default_factory=list)
    knowledge_graph: Optional[Dict[str, Any]] = None
    search_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class KeywordData:
    """Keyword analysis data"""
    keyword: str
    search_volume: int = 0
    keyword_difficulty: float = 0.0
    cost_per_click: float = 0.0
    competition_level: str = "unknown"  # low, medium, high
    trend_data: List[Tuple[str, int]] = field(default_factory=list)  # (date, volume)
    related_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    intent: str = "informational"  # informational, commercial, transactional, navigational

class GoogleSearchConsoleAPI:
    """Google Search Console API integration"""
    
    def __init__(self, api_key: str, property_url: str):
        self.api_key = api_key
        self.property_url = property_url
        self.base_url = "https://searchconsole.googleapis.com/webmasters/v3"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_search_analytics(self, start_date: str, end_date: str, 
                                 dimensions: List[str] = ["query"]) -> Dict[str, Any]:
        """Get search analytics data"""
        try:
            request_body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": dimensions,
                "dimensionFilterGroups": [],
                "rowLimit": 1000,
                "startRow": 0
            }
            
            url = f"{self.base_url}/sites/{quote(self.property_url, safe='')}/searchAnalytics/query"
            
            async with self.session.post(url, json=request_body) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("rows", []),
                        "total_rows": len(data.get("rows", []))
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error("Google Search Console analytics failed", error=str(e))
            return {"success": False, "error": str(e)}
            
    async def get_top_keywords(self, start_date: str, end_date: str, limit: int = 50) -> List[KeywordData]:
        """Get top performing keywords"""
        try:
            analytics_data = await self.get_search_analytics(
                start_date, end_date, ["query"]
            )
            
            if not analytics_data["success"]:
                return []
                
            keywords = []
            for row in analytics_data["data"][:limit]:
                keyword_data = KeywordData(
                    keyword=row["keys"][0],
                    search_volume=int(row.get("impressions", 0)),
                    cost_per_click=0.0,  # Not available in Search Console
                    competition_level="unknown"
                )
                keywords.append(keyword_data)
                
            return keywords
            
        except Exception as e:
            logger.error("Top keywords retrieval failed", error=str(e))
            return []

class GoogleCustomSearchAPI:
    """Google Custom Search API integration"""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://customsearch.googleapis.com/customsearch/v1"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform custom search"""
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query.query,
                "num": min(query.limit, 10),  # Max 10 per request
                "start": query.offset + 1,
                "lr": f"lang_{query.language}",
                "gl": query.country.lower(),
                "safe": "active" if query.safe_search else "off"
            }
            
            if query.search_type == SearchType.IMAGES:
                params["searchType"] = "image"
            elif query.date_range:
                params["dateRestrict"] = query.date_range
                
            start_time = time.time()
            
            async with self.session.get(self.base_url, params=params) as response:
                search_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    for i, item in enumerate(data.get("items", [])):
                        result = SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            description=item.get("snippet", ""),
                            rank=query.offset + i + 1,
                            search_engine=SearchEngine.GOOGLE,
                            search_type=query.search_type,
                            domain=self._extract_domain(item.get("link", "")),
                            thumbnail=item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src")
                        )
                        results.append(result)
                        
                    return SearchResponse(
                        query=query.query,
                        search_engine=SearchEngine.GOOGLE,
                        search_type=query.search_type,
                        total_results=int(data.get("searchInformation", {}).get("totalResults", 0)),
                        results=results,
                        search_time=search_time,
                        success=True
                    )
                else:
                    return SearchResponse(
                        query=query.query,
                        search_engine=SearchEngine.GOOGLE,
                        search_type=query.search_type,
                        success=False,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("Google custom search failed", error=str(e))
            return SearchResponse(
                query=query.query,
                search_engine=SearchEngine.GOOGLE,
                search_type=query.search_type,
                success=False,
                error_message=str(e)
            )
            
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""

class BingSearchAPI:
    """Microsoft Bing Search API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_urls = {
            SearchType.WEB: "https://api.bing.microsoft.com/v7.0/search",
            SearchType.IMAGES: "https://api.bing.microsoft.com/v7.0/images/search",
            SearchType.VIDEOS: "https://api.bing.microsoft.com/v7.0/videos/search",
            SearchType.NEWS: "https://api.bing.microsoft.com/v7.0/news/search"
        }
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Ocp-Apim-Subscription-Key": self.api_key
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform Bing search"""
        try:
            base_url = self.base_urls.get(query.search_type, self.base_urls[SearchType.WEB])
            
            params = {
                "q": query.query,
                "count": min(query.limit, 50),
                "offset": query.offset,
                "mkt": f"{query.language}-{query.country}",
                "safeSearch": "Strict" if query.safe_search else "Off"
            }
            
            if query.date_range:
                params["freshness"] = query.date_range
                
            start_time = time.time()
            
            async with self.session.get(base_url, params=params) as response:
                search_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    items_key = "webPages" if query.search_type == SearchType.WEB else query.search_type.value
                    items = data.get(items_key, {}).get("value", [])
                    
                    for i, item in enumerate(items):
                        result = SearchResult(
                            title=item.get("name", ""),
                            url=item.get("url", ""),
                            description=item.get("snippet", ""),
                            rank=query.offset + i + 1,
                            search_engine=SearchEngine.BING,
                            search_type=query.search_type,
                            domain=self._extract_domain(item.get("url", "")),
                            thumbnail=item.get("thumbnailUrl")
                        )
                        results.append(result)
                        
                    total_results = data.get(items_key, {}).get("totalEstimatedMatches", 0)
                    
                    return SearchResponse(
                        query=query.query,
                        search_engine=SearchEngine.BING,
                        search_type=query.search_type,
                        total_results=total_results,
                        results=results,
                        related_searches=[r.get("text", "") for r in data.get("relatedSearches", {}).get("value", [])],
                        search_time=search_time,
                        success=True
                    )
                else:
                    return SearchResponse(
                        query=query.query,
                        search_engine=SearchEngine.BING,
                        search_type=query.search_type,
                        success=False,
                        error_message=f"API error: {response.status}"
                    )
                    
        except Exception as e:
            logger.error("Bing search failed", error=str(e))
            return SearchResponse(
                query=query.query,
                search_engine=SearchEngine.BING,
                search_type=query.search_type,
                success=False,
                error_message=str(e)
            )
            
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""

class SEMrushAPI:
    """SEMrush API for keyword research and competitor analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.semrush.com/"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=45)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def get_keyword_data(self, keyword: str, database: str = "us") -> KeywordData:
        """Get comprehensive keyword data"""
        try:
            params = {
                "type": "phrase_all",
                "key": self.api_key,
                "phrase": keyword,
                "database": database,
                "export_columns": "Ph,Nq,Cp,Co,Nr,Td"
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.text()
                    lines = data.strip().split('\n')
                    
                    if len(lines) > 1:
                        values = lines[1].split(';')
                        
                        return KeywordData(
                            keyword=values[0],
                            search_volume=int(values[1]) if values[1] else 0,
                            cost_per_click=float(values[2]) if values[2] else 0.0,
                            competition_level=self._map_competition(float(values[3])) if values[3] else "unknown",
                            keyword_difficulty=float(values[3]) if values[3] else 0.0
                        )
                    else:
                        return KeywordData(keyword=keyword)
                else:
                    logger.error("SEMrush keyword data failed", status=response.status)
                    return KeywordData(keyword=keyword)
                    
        except Exception as e:
            logger.error("SEMrush keyword analysis failed", error=str(e))
            return KeywordData(keyword=keyword)
            
    async def get_related_keywords(self, keyword: str, limit: int = 20, database: str = "us") -> List[str]:
        """Get related keywords"""
        try:
            params = {
                "type": "phrase_related",
                "key": self.api_key,
                "phrase": keyword,
                "database": database,
                "display_limit": limit,
                "export_columns": "Ph,Nq"
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.text()
                    lines = data.strip().split('\n')[1:]  # Skip header
                    
                    related_keywords = []
                    for line in lines:
                        if line:
                            keyword_data = line.split(';')
                            if keyword_data[0]:
                                related_keywords.append(keyword_data[0])
                                
                    return related_keywords
                else:
                    return []
                    
        except Exception as e:
            logger.error("SEMrush related keywords failed", error=str(e))
            return []
            
    async def get_competitor_keywords(self, domain: str, limit: int = 50, database: str = "us") -> List[KeywordData]:
        """Get competitor's top keywords"""
        try:
            params = {
                "type": "domain_organic",
                "key": self.api_key,
                "domain": domain,
                "database": database,
                "display_limit": limit,
                "export_columns": "Ph,Po,Nq,Cp,Co,Tr,Tc"
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.text()
                    lines = data.strip().split('\n')[1:]  # Skip header
                    
                    keywords = []
                    for line in lines:
                        if line:
                            values = line.split(';')
                            if len(values) >= 6:
                                keyword_data = KeywordData(
                                    keyword=values[0],
                                    search_volume=int(values[2]) if values[2] else 0,
                                    cost_per_click=float(values[3]) if values[3] else 0.0,
                                    competition_level=self._map_competition(float(values[4])) if values[4] else "unknown"
                                )
                                keywords.append(keyword_data)
                                
                    return keywords
                else:
                    return []
                    
        except Exception as e:
            logger.error("SEMrush competitor analysis failed", error=str(e))
            return []
            
    def _map_competition(self, competition_value: float) -> str:
        """Map competition value to level"""
        if competition_value < 0.33:
            return "low"
        elif competition_value < 0.66:
            return "medium"
        else:
            return "high"

class RankingMonitor:
    """Monitor search engine rankings for keywords"""
    
    def __init__(self, search_apis: Dict[str, Any]):
        self.search_apis = search_apis
        self.tracking_data = {}
        
    async def track_keyword_rankings(self, domain: str, keywords: List[str], 
                                   search_engines: List[SearchEngine] = None) -> Dict[str, Any]:
        """Track rankings for keywords across search engines"""
        if search_engines is None:
            search_engines = [SearchEngine.GOOGLE, SearchEngine.BING]
            
        tracking_results = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "rankings": {},
            "summary": {
                "total_keywords": len(keywords),
                "ranking_keywords": 0,
                "average_position": 0.0,
                "top_10_count": 0,
                "top_3_count": 0
            }
        }
        
        all_positions = []
        ranking_count = 0
        
        for keyword in keywords:
            tracking_results["rankings"][keyword] = {}
            
            for search_engine in search_engines:
                try:
                    # Get search API for this engine
                    api = self.search_apis.get(search_engine.value)
                    if not api:
                        continue
                        
                    # Search for keyword
                    query = SearchQuery(
                        query=keyword,
                        search_engine=search_engine,
                        limit=50  # Check first 50 results
                    )
                    
                    async with api as search_api:
                        response = await search_api.search(query)
                        
                    # Find domain position
                    position = self._find_domain_position(domain, response.results)
                    
                    tracking_results["rankings"][keyword][search_engine.value] = {
                        "position": position,
                        "found": position > 0,
                        "url": self._get_ranking_url(domain, response.results, position) if position > 0 else None
                    }
                    
                    if position > 0:
                        all_positions.append(position)
                        ranking_count += 1
                        
                        if position <= 10:
                            tracking_results["summary"]["top_10_count"] += 1
                        if position <= 3:
                            tracking_results["summary"]["top_3_count"] += 1
                            
                except Exception as e:
                    logger.error("Ranking check failed", keyword=keyword, engine=search_engine.value, error=str(e))
                    tracking_results["rankings"][keyword][search_engine.value] = {
                        "position": 0,
                        "found": False,
                        "error": str(e)
                    }
                    
        # Calculate summary statistics
        tracking_results["summary"]["ranking_keywords"] = ranking_count
        if all_positions:
            tracking_results["summary"]["average_position"] = sum(all_positions) / len(all_positions)
            
        return tracking_results
        
    def _find_domain_position(self, domain: str, results: List[SearchResult]) -> int:
        """Find position of domain in search results"""
        for result in results:
            if domain.lower() in result.domain.lower() or domain.lower() in result.url.lower():
                return result.rank
        return 0
        
    def _get_ranking_url(self, domain: str, results: List[SearchResult], position: int) -> Optional[str]:
        """Get the URL that's ranking for the domain"""
        for result in results:
            if result.rank == position and (domain.lower() in result.domain.lower() or domain.lower() in result.url.lower()):
                return result.url
        return None
        
    async def generate_ranking_report(self, tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive ranking report"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "domain": tracking_data["domain"],
            "period": "current",
            "summary": tracking_data["summary"],
            "keyword_analysis": [],
            "recommendations": [],
            "opportunities": []
        }
        
        # Analyze each keyword
        for keyword, rankings in tracking_data["rankings"].items():
            analysis = {
                "keyword": keyword,
                "best_position": min([r["position"] for r in rankings.values() if r["position"] > 0] or [0]),
                "average_position": sum([r["position"] for r in rankings.values() if r["position"] > 0]) / max(len([r for r in rankings.values() if r["position"] > 0]), 1),
                "engines_ranking": len([r for r in rankings.values() if r["position"] > 0]),
                "improvement_potential": "high" if any(r["position"] > 10 for r in rankings.values() if r["position"] > 0) else "medium"
            }
            report["keyword_analysis"].append(analysis)
            
        # Generate recommendations
        avg_position = tracking_data["summary"]["average_position"]
        ranking_keywords = tracking_data["summary"]["ranking_keywords"]
        total_keywords = tracking_data["summary"]["total_keywords"]
        
        if avg_position > 20:
            report["recommendations"].append("Focus on improving overall SEO foundation and content quality")
        elif avg_position > 10:
            report["recommendations"].append("Optimize existing content and build more authoritative backlinks")
        else:
            report["recommendations"].append("Fine-tune content for featured snippets and user intent")
            
        if ranking_keywords / total_keywords < 0.5:
            report["recommendations"].append("Expand keyword targeting and create content for missing keywords")
            
        # Identify opportunities
        non_ranking_keywords = [k for k, r in tracking_data["rankings"].items() 
                              if not any(pos["position"] > 0 for pos in r.values())]
        if non_ranking_keywords:
            report["opportunities"].append({
                "type": "content_creation",
                "description": f"Create content for {len(non_ranking_keywords)} non-ranking keywords",
                "keywords": non_ranking_keywords[:10]  # Show first 10
            })
            
        return report

class SearchEngineManager:
    """Main manager for all search engine integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.search_apis = {}
        self.semrush_api = None
        self.ranking_monitor = None
        self._initialize_apis()
        
    def _initialize_apis(self):
        """Initialize search engine APIs"""
        try:
            # Google Custom Search
            if google_config := self.config.get("google_custom_search"):
                self.search_apis["google"] = GoogleCustomSearchAPI(
                    api_key=google_config["api_key"],
                    search_engine_id=google_config["search_engine_id"]
                )
                
            # Bing Search
            if bing_config := self.config.get("bing_search"):
                self.search_apis["bing"] = BingSearchAPI(
                    api_key=bing_config["api_key"]
                )
                
            # SEMrush
            if semrush_config := self.config.get("semrush"):
                self.semrush_api = SEMrushAPI(
                    api_key=semrush_config["api_key"]
                )
                
            # Initialize ranking monitor
            self.ranking_monitor = RankingMonitor(self.search_apis)
            
            logger.info("Search engine APIs initialized", apis=list(self.search_apis.keys()))
            
        except Exception as e:
            logger.error("Failed to initialize search APIs", error=str(e))
            
    async def search_multi_engine(self, query: SearchQuery, engines: List[SearchEngine] = None) -> Dict[str, SearchResponse]:
        """Search across multiple engines"""
        if engines is None:
            engines = [SearchEngine.GOOGLE, SearchEngine.BING]
            
        results = {}
        
        for engine in engines:
            try:
                api = self.search_apis.get(engine.value)
                if api:
                    query.search_engine = engine
                    async with api as search_api:
                        response = await search_api.search(query)
                    results[engine.value] = response
                else:
                    results[engine.value] = SearchResponse(
                        query=query.query,
                        search_engine=engine,
                        search_type=query.search_type,
                        success=False,
                        error_message=f"API not configured for {engine.value}"
                    )
                    
            except Exception as e:
                logger.error("Multi-engine search failed", engine=engine.value, error=str(e))
                results[engine.value] = SearchResponse(
                    query=query.query,
                    search_engine=engine,
                    search_type=query.search_type,
                    success=False,
                    error_message=str(e)
                )
                
        return results
        
    async def analyze_keyword_opportunities(self, seed_keywords: List[str], domain: str = None) -> Dict[str, Any]:
        """Analyze keyword opportunities for SEO"""
        if not self.semrush_api:
            return {"error": "SEMrush API not configured"}
            
        analysis = {
            "seed_keywords": seed_keywords,
            "domain": domain,
            "analyzed_at": datetime.utcnow().isoformat(),
            "keyword_data": [],
            "content_gaps": [],
            "competitor_insights": [],
            "recommendations": []
        }
        
        try:
            async with self.semrush_api as semrush:
                # Analyze each seed keyword
                for keyword in seed_keywords:
                    keyword_data = await semrush.get_keyword_data(keyword)
                    related_keywords = await semrush.get_related_keywords(keyword, limit=10)
                    
                    keyword_data.related_keywords = related_keywords
                    analysis["keyword_data"].append(asdict(keyword_data))
                    
                # Competitor analysis if domain provided
                if domain:
                    competitor_keywords = await semrush.get_competitor_keywords(domain, limit=30)
                    analysis["competitor_insights"] = [asdict(kw) for kw in competitor_keywords]
                    
            # Generate recommendations
            high_volume_keywords = [kw for kw in analysis["keyword_data"] if kw["search_volume"] > 1000]
            low_competition_keywords = [kw for kw in analysis["keyword_data"] if kw["competition_level"] == "low"]
            
            if high_volume_keywords:
                analysis["recommendations"].append({
                    "type": "high_volume_targeting",
                    "description": f"Target {len(high_volume_keywords)} high-volume keywords",
                    "keywords": [kw["keyword"] for kw in high_volume_keywords[:5]]
                })
                
            if low_competition_keywords:
                analysis["recommendations"].append({
                    "type": "quick_wins",
                    "description": f"Quick wins with {len(low_competition_keywords)} low-competition keywords",
                    "keywords": [kw["keyword"] for kw in low_competition_keywords[:5]]
                })
                
        except Exception as e:
            logger.error("Keyword opportunity analysis failed", error=str(e))
            analysis["error"] = str(e)
            
        return analysis
        
    async def monitor_rankings(self, domain: str, keywords: List[str]) -> Dict[str, Any]:
        """Monitor search rankings for domain and keywords"""
        if not self.ranking_monitor:
            return {"error": "Ranking monitor not initialized"}
            
        try:
            return await self.ranking_monitor.track_keyword_rankings(domain, keywords)
        except Exception as e:
            logger.error("Ranking monitoring failed", error=str(e))
            return {"error": str(e)}
            
    async def generate_seo_content_ideas(self, topic: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Generate SEO-optimized content ideas"""
        content_ideas = {
            "topic": topic,
            "target_keywords": target_keywords,
            "generated_at": datetime.utcnow().isoformat(),
            "content_suggestions": [],
            "question_keywords": [],
            "long_tail_opportunities": [],
            "content_formats": []
        }
        
        try:
            # Use search APIs to find related questions and content gaps
            for keyword in target_keywords:
                query = SearchQuery(
                    query=f"what is {keyword}",
                    search_type=SearchType.WEB,
                    limit=10
                )
                
                # Search for question-based content
                if "google" in self.search_apis:
                    async with self.search_apis["google"] as google_api:
                        response = await google_api.search(query)
                        
                    # Extract questions from titles and descriptions
                    for result in response.results:
                        if any(q in result.title.lower() for q in ["what", "how", "why", "when", "where"]):
                            content_ideas["question_keywords"].append(result.title)
                            
            # Generate content format suggestions
            content_ideas["content_formats"] = [
                {"format": "how-to guide", "target_keywords": target_keywords[:3], "estimated_length": "2000-3000 words"},
                {"format": "comparison article", "target_keywords": target_keywords[1:4], "estimated_length": "1500-2500 words"},
                {"format": "beginner's guide", "target_keywords": target_keywords[:2], "estimated_length": "3000-4000 words"},
                {"format": "FAQ page", "target_keywords": content_ideas["question_keywords"][:5], "estimated_length": "1000-1500 words"}
            ]
            
        except Exception as e:
            logger.error("Content idea generation failed", error=str(e))
            content_ideas["error"] = str(e)
            
        return content_ideas

# Factory function for easy integration
def create_search_engine_manager(config: Dict[str, Any]) -> SearchEngineManager:
    """Create configured search engine manager"""
    return SearchEngineManager(config)

# Example usage for Ainflue platform
async def ainflue_seo_optimization_workflow(content_topic: str, target_keywords: List[str], domain: str) -> Dict[str, Any]:
    """
    Complete SEO optimization workflow for Ainflue creators
    Business Logic: Creator→Upload→IA processing→Protection→Monetization→Collaboration→SEO→Distribution
    """
    
    # Example configuration
    config = {
        "google_custom_search": {
            "api_key": "your_google_api_key",
            "search_engine_id": "your_search_engine_id"
        },
        "bing_search": {
            "api_key": "your_bing_api_key"
        },
        "semrush": {
            "api_key": "your_semrush_api_key"
        }
    }
    
    # Initialize search engine manager
    search_manager = create_search_engine_manager(config)
    
    # Keyword opportunity analysis
    keyword_opportunities = await search_manager.analyze_keyword_opportunities(target_keywords, domain)
    
    # Ranking monitoring
    current_rankings = await search_manager.monitor_rankings(domain, target_keywords)
    
    # Content idea generation
    content_ideas = await search_manager.generate_seo_content_ideas(content_topic, target_keywords)
    
    # Multi-engine search for competitor analysis
    competitor_query = SearchQuery(
        query=f"{content_topic} {target_keywords[0]}",
        search_type=SearchType.WEB,
        limit=20
    )
    
    competitor_results = await search_manager.search_multi_engine(competitor_query)
    
    return {
        "keyword_opportunities": keyword_opportunities,
        "current_rankings": current_rankings,
        "content_ideas": content_ideas,
        "competitor_analysis": {
            "search_results": {engine: response.dict() for engine, response in competitor_results.items()},
            "top_competitors": [result.domain for response in competitor_results.values() for result in response.results[:5]]
        },
        "seo_recommendations": [
            "Optimize content for featured snippets to increase visibility",
            "Create comprehensive pillar content around main topics",
            "Build high-quality backlinks from relevant industry sites",
            "Monitor and improve page loading speed for better rankings",
            "Implement schema markup for enhanced search appearance"
        ]
    }

if __name__ == "__main__":
    # Test the search engines integration
    import asyncio
    
    async def test_search_engines():
        """Test search engines functionality"""
        
        test_topic = "AI content creation"
        test_keywords = ["ai content generator", "automated content creation", "ai writing tools"]
        test_domain = "ainflue.com"
        
        result = await ainflue_seo_optimization_workflow(test_topic, test_keywords, test_domain)
        
        print("SEO Optimization Workflow Result:")
        print(json.dumps(result, indent=2, default=str))
        
    # Run test
    # asyncio.run(test_search_engines())
    
    print("✅ Search Engines Integration Module loaded successfully")
    print("🔍 Enterprise-grade SEO optimization for Ainflue creators")
    print("📈 Keyword research, ranking monitoring, and content optimization tools ready")