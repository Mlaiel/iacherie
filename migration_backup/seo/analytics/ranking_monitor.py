"""
Search Ranking Monitor for Ainflue Platform
===========================================

Advanced search ranking monitoring and analysis for creators and content.
Tracks rankings across multiple search engines and provides actionable insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import aiohttp
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
from datetime import datetime, timedelta
import re
from urllib.parse import urlencode, quote
import random
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class SearchEngine(Enum):
    """Supported search engines for ranking monitoring."""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"

class RankingType(Enum):
    """Types of search rankings."""
    ORGANIC = "organic"
    LOCAL = "local"
    FEATURED_SNIPPET = "featured_snippet"
    IMAGE = "image"
    VIDEO = "video"
    NEWS = "news"
    SHOPPING = "shopping"

class TrackingFrequency(Enum):
    """Frequency options for ranking tracking."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    REAL_TIME = "real_time"

@dataclass
class KeywordRanking:
    """Individual keyword ranking data."""
    ranking_id: str
    keyword: str
    search_engine: SearchEngine
    ranking_type: RankingType
    position: Optional[int]
    url: str
    title: str
    description: str
    location: Optional[str]
    device: str
    language: str
    tracked_at: datetime
    previous_position: Optional[int]
    position_change: int
    visibility_score: float
    click_probability: float

@dataclass
class RankingProject:
    """Ranking tracking project configuration."""
    project_id: str
    project_name: str
    website_url: str
    target_keywords: List[str]
    search_engines: List[SearchEngine]
    locations: List[str]
    devices: List[str]
    frequency: TrackingFrequency
    active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class RankingReport:
    """Comprehensive ranking analysis report."""
    report_id: str
    project_id: str
    period_start: datetime
    period_end: datetime
    total_keywords: int
    average_position: float
    visibility_score: float
    top_10_count: int
    top_3_count: int
    position_changes: Dict[str, int]
    new_rankings: List[str]
    lost_rankings: List[str]
    trending_keywords: List[str]
    declining_keywords: List[str]
    recommendations: List[str]
    created_at: datetime

@dataclass
class CompetitorRanking:
    """Competitor ranking analysis."""
    competitor_id: str
    competitor_domain: str
    keyword: str
    position: int
    url: str
    title: str
    visibility_share: float
    tracked_at: datetime

class RankingMonitor:
    """
    Advanced Search Ranking Monitor
    
    Features:
    - Multi-search engine ranking tracking
    - Local and global ranking monitoring
    - Competitor ranking analysis
    - Featured snippet tracking
    - Historical ranking trends
    - Automated ranking reports
    - Mobile vs desktop rankings
    - Voice search ranking tracking
    """
    
    def __init__(self, db_pool: asyncpg.Pool, api_keys: Dict[str, str]):
        self.db_pool = db_pool
        self.api_keys = api_keys
        self.session = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_tracking_project(
        self,
        project_data: Dict[str, Any]
    ) -> RankingProject:
        """
        Create a new ranking tracking project.
        
        Args:
            project_data: Project configuration data
            
        Returns:
            RankingProject object
        """
        try:
            project = RankingProject(
                project_id=project_data['project_id'],
                project_name=project_data['project_name'],
                website_url=project_data['website_url'],
                target_keywords=project_data['target_keywords'],
                search_engines=[SearchEngine(se) for se in project_data['search_engines']],
                locations=project_data.get('locations', ['global']),
                devices=project_data.get('devices', ['desktop', 'mobile']),
                frequency=TrackingFrequency(project_data.get('frequency', 'daily')),
                active=project_data.get('active', True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store project in database
            await self._store_tracking_project(project)
            
            return project
            
        except Exception as e:
            logger.error(f"Error creating tracking project: {e}")
            raise
    
    async def track_keyword_rankings(
        self,
        project_id: str,
        keywords: Optional[List[str]] = None,
        search_engines: Optional[List[SearchEngine]] = None
    ) -> List[KeywordRanking]:
        """
        Track rankings for keywords in a project.
        
        Args:
            project_id: Project identifier
            keywords: Specific keywords to track (optional)
            search_engines: Specific search engines (optional)
            
        Returns:
            List of KeywordRanking objects
        """
        try:
            # Get project configuration
            project = await self._get_tracking_project(project_id)
            if not project:
                raise ValueError(f"Project not found: {project_id}")
            
            # Use project keywords if none specified
            track_keywords = keywords or project.target_keywords
            track_engines = search_engines or project.search_engines
            
            rankings = []
            
            for keyword in track_keywords:
                for engine in track_engines:
                    for location in project.locations:
                        for device in project.devices:
                            try:
                                # Get current ranking
                                ranking = await self._get_keyword_ranking(
                                    keyword, engine, project.website_url,
                                    location, device
                                )
                                
                                if ranking:
                                    rankings.append(ranking)
                                    
                                # Add delay to avoid rate limiting
                                await asyncio.sleep(random.uniform(1, 3))
                                
                            except Exception as e:
                                logger.error(f"Error tracking {keyword} on {engine.value}: {e}")
                                continue
            
            # Store rankings in database
            await self._store_rankings(rankings)
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error tracking keyword rankings: {e}")
            return []
    
    async def analyze_ranking_trends(
        self,
        project_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze ranking trends over a specified period.
        
        Args:
            project_id: Project identifier
            days: Number of days to analyze
            
        Returns:
            Trend analysis results
        """
        try:
            # Get historical ranking data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            rankings = await self._get_historical_rankings(
                project_id, start_date, end_date
            )
            
            if not rankings:
                return {'error': 'No ranking data found for the specified period'}
            
            # Analyze trends
            trends = self._analyze_trends(rankings)
            
            # Calculate key metrics
            metrics = self._calculate_ranking_metrics(rankings)
            
            # Identify opportunities and issues
            opportunities = self._identify_opportunities(rankings)
            issues = self._identify_issues(rankings)
            
            # Generate insights
            insights = self._generate_ranking_insights(trends, metrics, opportunities, issues)
            
            return {
                'project_id': project_id,
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'trends': trends,
                'metrics': metrics,
                'opportunities': opportunities,
                'issues': issues,
                'insights': insights,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ranking trends: {e}")
            return {}
    
    async def track_competitor_rankings(
        self,
        project_id: str,
        competitor_domains: List[str],
        keywords: List[str]
    ) -> List[CompetitorRanking]:
        """
        Track competitor rankings for specific keywords.
        
        Args:
            project_id: Project identifier
            competitor_domains: List of competitor domains
            keywords: Keywords to track
            
        Returns:
            List of CompetitorRanking objects
        """
        try:
            competitor_rankings = []
            
            for keyword in keywords:
                # Get search results for keyword
                search_results = await self._get_search_results(
                    keyword, SearchEngine.GOOGLE
                )
                
                for position, result in enumerate(search_results, 1):
                    result_domain = self._extract_domain(result.get('url', ''))
                    
                    if result_domain in competitor_domains:
                        competitor_ranking = CompetitorRanking(
                            competitor_id=f"{result_domain}_{keyword}_{int(datetime.utcnow().timestamp())}",
                            competitor_domain=result_domain,
                            keyword=keyword,
                            position=position,
                            url=result.get('url', ''),
                            title=result.get('title', ''),
                            visibility_share=self._calculate_visibility_share(position),
                            tracked_at=datetime.utcnow()
                        )
                        competitor_rankings.append(competitor_ranking)
                
                # Add delay between searches
                await asyncio.sleep(random.uniform(2, 4))
            
            # Store competitor rankings
            await self._store_competitor_rankings(competitor_rankings)
            
            return competitor_rankings
            
        except Exception as e:
            logger.error(f"Error tracking competitor rankings: {e}")
            return []
    
    async def generate_ranking_report(
        self,
        project_id: str,
        period_days: int = 30
    ) -> RankingReport:
        """
        Generate comprehensive ranking report.
        
        Args:
            project_id: Project identifier
            period_days: Report period in days
            
        Returns:
            RankingReport object
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get ranking data for the period
            rankings = await self._get_historical_rankings(
                project_id, start_date, end_date
            )
            
            if not rankings:
                raise ValueError("No ranking data available for report generation")
            
            # Calculate report metrics
            total_keywords = len(set(r.keyword for r in rankings))
            average_position = sum(r.position for r in rankings if r.position) / len([r for r in rankings if r.position])
            visibility_score = sum(r.visibility_score for r in rankings) / len(rankings)
            top_10_count = len([r for r in rankings if r.position and r.position <= 10])
            top_3_count = len([r for r in rankings if r.position and r.position <= 3])
            
            # Analyze position changes
            position_changes = self._analyze_position_changes(rankings)
            
            # Identify new and lost rankings
            new_rankings, lost_rankings = await self._identify_ranking_changes(
                project_id, start_date, end_date
            )
            
            # Identify trending keywords
            trending_keywords = self._identify_trending_keywords(rankings)
            declining_keywords = self._identify_declining_keywords(rankings)
            
            # Generate recommendations
            recommendations = self._generate_ranking_recommendations(
                rankings, position_changes, trending_keywords, declining_keywords
            )
            
            report = RankingReport(
                report_id=f"report_{project_id}_{int(datetime.utcnow().timestamp())}",
                project_id=project_id,
                period_start=start_date,
                period_end=end_date,
                total_keywords=total_keywords,
                average_position=average_position,
                visibility_score=visibility_score,
                top_10_count=top_10_count,
                top_3_count=top_3_count,
                position_changes=position_changes,
                new_rankings=new_rankings,
                lost_rankings=lost_rankings,
                trending_keywords=trending_keywords,
                declining_keywords=declining_keywords,
                recommendations=recommendations,
                created_at=datetime.utcnow()
            )
            
            # Store report
            await self._store_ranking_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating ranking report: {e}")
            raise
    
    async def _get_keyword_ranking(
        self,
        keyword: str,
        search_engine: SearchEngine,
        target_url: str,
        location: str,
        device: str
    ) -> Optional[KeywordRanking]:
        """Get current ranking for a specific keyword."""
        try:
            # Get search results
            search_results = await self._get_search_results(
                keyword, search_engine, location, device
            )
            
            # Find target URL in results
            target_domain = self._extract_domain(target_url)
            
            for position, result in enumerate(search_results, 1):
                result_domain = self._extract_domain(result.get('url', ''))
                
                if result_domain == target_domain:
                    # Get previous ranking for comparison
                    previous_position = await self._get_previous_ranking(
                        keyword, search_engine, target_url, location, device
                    )
                    
                    ranking = KeywordRanking(
                        ranking_id=f"{keyword}_{search_engine.value}_{int(datetime.utcnow().timestamp())}",
                        keyword=keyword,
                        search_engine=search_engine,
                        ranking_type=RankingType.ORGANIC,
                        position=position,
                        url=result.get('url', ''),
                        title=result.get('title', ''),
                        description=result.get('description', ''),
                        location=location,
                        device=device,
                        language='en',
                        tracked_at=datetime.utcnow(),
                        previous_position=previous_position,
                        position_change=(previous_position - position) if previous_position else 0,
                        visibility_score=self._calculate_visibility_score(position),
                        click_probability=self._calculate_click_probability(position)
                    )
                    
                    return ranking
            
            # Not found in top results
            return None
            
        except Exception as e:
            logger.error(f"Error getting keyword ranking: {e}")
            return None
    
    async def _get_search_results(
        self,
        keyword: str,
        search_engine: SearchEngine,
        location: str = 'global',
        device: str = 'desktop',
        max_results: int = 100
    ) -> List[Dict[str, str]]:
        """Get search results for a keyword."""
        try:
            if search_engine == SearchEngine.GOOGLE:
                return await self._get_google_results(keyword, location, device, max_results)
            elif search_engine == SearchEngine.BING:
                return await self._get_bing_results(keyword, location, device, max_results)
            else:
                # Fallback to Google for unsupported engines
                return await self._get_google_results(keyword, location, device, max_results)
                
        except Exception as e:
            logger.error(f"Error getting search results: {e}")
            return []
    
    async def _get_google_results(
        self,
        keyword: str,
        location: str,
        device: str,
        max_results: int
    ) -> List[Dict[str, str]]:
        """Get Google search results (simulated - would use real API in production)."""
        try:
            # This would use Google Search API or scraping in production
            # For now, simulate results
            
            results = []
            for i in range(min(max_results, 20)):
                results.append({
                    'position': i + 1,
                    'title': f"Sample Result {i + 1} for {keyword}",
                    'url': f"https://example{i + 1}.com/page",
                    'description': f"Sample description for {keyword} result {i + 1}",
                    'domain': f"example{i + 1}.com"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting Google results: {e}")
            return []
    
    async def _get_bing_results(
        self,
        keyword: str,
        location: str,
        device: str,
        max_results: int
    ) -> List[Dict[str, str]]:
        """Get Bing search results."""
        try:
            # Similar to Google - would use Bing API
            results = []
            for i in range(min(max_results, 20)):
                results.append({
                    'position': i + 1,
                    'title': f"Bing Result {i + 1} for {keyword}",
                    'url': f"https://bing-example{i + 1}.com/page",
                    'description': f"Bing description for {keyword} result {i + 1}",
                    'domain': f"bing-example{i + 1}.com"
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting Bing results: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ''
    
    def _calculate_visibility_score(self, position: int) -> float:
        """Calculate visibility score based on position."""
        if position <= 3:
            return 100.0
        elif position <= 10:
            return 80.0 - (position - 3) * 5
        elif position <= 20:
            return 45.0 - (position - 10) * 2
        elif position <= 50:
            return 25.0 - (position - 20) * 0.5
        else:
            return max(10.0 - (position - 50) * 0.1, 0)
    
    def _calculate_click_probability(self, position: int) -> float:
        """Calculate click-through probability based on position."""
        # Based on industry CTR data
        ctr_rates = {
            1: 28.5, 2: 15.7, 3: 11.0, 4: 8.0, 5: 6.0,
            6: 4.5, 7: 3.5, 8: 2.8, 9: 2.3, 10: 2.0
        }
        
        if position in ctr_rates:
            return ctr_rates[position]
        elif position <= 20:
            return max(1.0 - (position - 10) * 0.05, 0.1)
        else:
            return 0.1
    
    def _calculate_visibility_share(self, position: int) -> float:
        """Calculate visibility share for competitor analysis."""
        return self._calculate_visibility_score(position) / 100.0
    
    async def _get_previous_ranking(
        self,
        keyword: str,
        search_engine: SearchEngine,
        target_url: str,
        location: str,
        device: str
    ) -> Optional[int]:
        """Get previous ranking for position change calculation."""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT position FROM keyword_rankings 
                    WHERE keyword = $1 AND search_engine = $2 AND url LIKE $3
                    AND location = $4 AND device = $5
                    ORDER BY tracked_at DESC 
                    LIMIT 1 OFFSET 1
                """, keyword, search_engine.value, f"%{self._extract_domain(target_url)}%",
                    location, device)
                
                return result['position'] if result else None
                
        except Exception as e:
            logger.error(f"Error getting previous ranking: {e}")
            return None
    
    def _analyze_trends(self, rankings: List[KeywordRanking]) -> Dict[str, Any]:
        """Analyze ranking trends from historical data."""
        trends = {
            'improving_keywords': [],
            'declining_keywords': [],
            'stable_keywords': [],
            'volatile_keywords': []
        }
        
        # Group rankings by keyword
        keyword_rankings = defaultdict(list)
        for ranking in rankings:
            keyword_rankings[ranking.keyword].append(ranking)
        
        for keyword, keyword_data in keyword_rankings.items():
            if len(keyword_data) < 2:
                continue
                
            # Sort by date
            keyword_data.sort(key=lambda x: x.tracked_at)
            
            # Calculate trend
            positions = [r.position for r in keyword_data if r.position]
            if len(positions) >= 2:
                trend_direction = self._calculate_trend_direction(positions)
                volatility = self._calculate_volatility(positions)
                
                if volatility > 5:
                    trends['volatile_keywords'].append(keyword)
                elif trend_direction > 2:
                    trends['improving_keywords'].append(keyword)
                elif trend_direction < -2:
                    trends['declining_keywords'].append(keyword)
                else:
                    trends['stable_keywords'].append(keyword)
        
        return trends
    
    def _calculate_trend_direction(self, positions: List[int]) -> float:
        """Calculate trend direction (negative = improving rank, positive = declining)."""
        if len(positions) < 2:
            return 0
        
        # Simple trend calculation (difference between first and last)
        return positions[0] - positions[-1]
    
    def _calculate_volatility(self, positions: List[int]) -> float:
        """Calculate ranking volatility."""
        if len(positions) < 2:
            return 0
        
        # Calculate standard deviation
        mean_pos = sum(positions) / len(positions)
        variance = sum((p - mean_pos) ** 2 for p in positions) / len(positions)
        return variance ** 0.5
    
    async def _store_tracking_project(self, project: RankingProject):
        """Store tracking project in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO ranking_tracking_projects 
                    (project_id, project_name, website_url, target_keywords, search_engines,
                     locations, devices, frequency, active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (project_id) DO UPDATE SET
                    project_name = EXCLUDED.project_name,
                    website_url = EXCLUDED.website_url,
                    target_keywords = EXCLUDED.target_keywords,
                    search_engines = EXCLUDED.search_engines,
                    locations = EXCLUDED.locations,
                    devices = EXCLUDED.devices,
                    frequency = EXCLUDED.frequency,
                    active = EXCLUDED.active,
                    updated_at = EXCLUDED.updated_at
                """, 
                    project.project_id, project.project_name, project.website_url,
                    json.dumps(project.target_keywords),
                    json.dumps([se.value for se in project.search_engines]),
                    json.dumps(project.locations), json.dumps(project.devices),
                    project.frequency.value, project.active,
                    project.created_at, project.updated_at
                )
        except Exception as e:
            logger.error(f"Error storing tracking project: {e}")
    
    async def _store_rankings(self, rankings: List[KeywordRanking]):
        """Store keyword rankings in database."""
        try:
            async with self.db_pool.acquire() as conn:
                for ranking in rankings:
                    await conn.execute("""
                        INSERT INTO keyword_rankings 
                        (ranking_id, keyword, search_engine, ranking_type, position, url,
                         title, description, location, device, language, tracked_at,
                         previous_position, position_change, visibility_score, click_probability)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    """, 
                        ranking.ranking_id, ranking.keyword, ranking.search_engine.value,
                        ranking.ranking_type.value, ranking.position, ranking.url,
                        ranking.title, ranking.description, ranking.location,
                        ranking.device, ranking.language, ranking.tracked_at,
                        ranking.previous_position, ranking.position_change,
                        ranking.visibility_score, ranking.click_probability
                    )
        except Exception as e:
            logger.error(f"Error storing rankings: {e}")
    
    async def get_ranking_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive ranking dashboard data."""
        try:
            # Get latest rankings
            latest_rankings = await self._get_latest_rankings(project_id)
            
            # Get trend data
            trends = await self.analyze_ranking_trends(project_id, days=30)
            
            # Get competitor data
            competitor_data = await self._get_competitor_summary(project_id)
            
            # Calculate key metrics
            metrics = self._calculate_dashboard_metrics(latest_rankings)
            
            return {
                'project_id': project_id,
                'latest_rankings': [asdict(r) for r in latest_rankings],
                'trends': trends,
                'competitor_data': competitor_data,
                'metrics': metrics,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting ranking dashboard: {e}")
            return {}

# Export classes
__all__ = [
    'RankingMonitor',
    'KeywordRanking',
    'RankingProject', 
    'RankingReport',
    'CompetitorRanking',
    'SearchEngine',
    'RankingType',
    'TrackingFrequency'
]