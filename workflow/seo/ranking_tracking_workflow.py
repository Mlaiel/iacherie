"""Ranking Tracking Workflow

AI-powered keyword ranking tracking and monitoring workflow for SEO optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from ..core.exceptions import WorkflowError
from ..utils.metrics import MetricsCollector
from ..utils.caching import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class KeywordRanking:
    """Keyword ranking data"""
    keyword: str
    position: int
    url: str
    search_volume: int
    difficulty: float
    ctr: float
    impressions: int
    clicks: int
    tracked_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RankingReport:
    """Ranking tracking report"""
    report_id: str
    rankings: List[KeywordRanking]
    period_start: datetime
    period_end: datetime
    total_keywords: int
    average_position: float
    improved_rankings: int
    declined_rankings: int
    new_rankings: int
    lost_rankings: int
    visibility_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class RankingTrackingWorkflow:
    """AI-powered ranking tracking workflow"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager()
        self.ranking_history: Dict[str, List[KeywordRanking]] = {}
        self.tracking_keywords: List[str] = []
        
    async def track_keyword_rankings(
        self,
        keywords: List[str],
        domain: str,
        search_engine: str = "google",
        location: str = "global"
    ) -> RankingReport:
        """
        Track keyword rankings and generate report
        
        Args:
            keywords: Keywords to track
            domain: Domain to track rankings for
            search_engine: Search engine to track (google, bing, etc.)
            location: Geographic location for tracking
            
        Returns:
            RankingReport with current rankings and changes
        """
        try:
            start_time = datetime.utcnow()
            report_id = f"ranking_report_{int(start_time.timestamp())}"
            
            logger.info(f"Starting ranking tracking for {len(keywords)} keywords")
            
            # Get current rankings
            current_rankings = []
            for keyword in keywords:
                ranking = await self._get_keyword_ranking(keyword, domain, search_engine, location)
                current_rankings.append(ranking)
            
            # Compare with historical data
            period_start = start_time - timedelta(days=7)  # Weekly comparison
            period_end = start_time
            
            # Calculate ranking changes
            ranking_changes = await self._calculate_ranking_changes(current_rankings, period_start)
            
            # Generate report metrics
            total_keywords = len(current_rankings)
            average_position = sum(r.position for r in current_rankings) / total_keywords if total_keywords > 0 else 0
            improved_rankings = len([r for r in ranking_changes if r.get("change", 0) < 0])  # Position decreased (improved)
            declined_rankings = len([r for r in ranking_changes if r.get("change", 0) > 0])  # Position increased (declined)
            new_rankings = len([r for r in ranking_changes if r.get("is_new", False)])
            lost_rankings = len([r for r in ranking_changes if r.get("is_lost", False)])
            
            # Calculate visibility score
            visibility_score = await self._calculate_visibility_score(current_rankings)
            
            # Create report
            report = RankingReport(
                report_id=report_id,
                rankings=current_rankings,
                period_start=period_start,
                period_end=period_end,
                total_keywords=total_keywords,
                average_position=average_position,
                improved_rankings=improved_rankings,
                declined_rankings=declined_rankings,
                new_rankings=new_rankings,
                lost_rankings=lost_rankings,
                visibility_score=visibility_score
            )
            
            # Store rankings in history
            for ranking in current_rankings:
                if ranking.keyword not in self.ranking_history:
                    self.ranking_history[ranking.keyword] = []
                self.ranking_history[ranking.keyword].append(ranking)
            
            # Cache report
            await self._cache_ranking_report(report)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_metric("ranking_tracking_duration", duration)
            await self.metrics_collector.record_metric("average_keyword_position", average_position)
            await self.metrics_collector.record_metric("visibility_score", visibility_score)
            
            logger.info(f"Ranking tracking completed. Average position: {average_position:.1f}")
            return report
            
        except Exception as e:
            logger.error(f"Ranking tracking failed: {e}")
            raise WorkflowError(f"Ranking tracking failed: {e}")
    
    async def _get_keyword_ranking(self, keyword: str, domain: str, search_engine: str, location: str) -> KeywordRanking:
        """Get current ranking for a keyword"""
        # Simulate ranking data retrieval
        import random
        
        # Generate realistic ranking data
        position = random.randint(1, 100)
        search_volume = random.randint(100, 10000)
        difficulty = random.uniform(0.1, 1.0)
        ctr = max(0.01, 0.3 - (position * 0.01))  # CTR decreases with position
        impressions = int(search_volume * (0.5 - position * 0.005))
        clicks = int(impressions * ctr)
        
        ranking = KeywordRanking(
            keyword=keyword,
            position=position,
            url=f"https://{domain}/page-for-{keyword.replace(' ', '-')}",
            search_volume=search_volume,
            difficulty=difficulty,
            ctr=ctr,
            impressions=impressions,
            clicks=clicks
        )
        
        return ranking
    
    async def _calculate_ranking_changes(self, current_rankings: List[KeywordRanking], period_start: datetime) -> List[Dict[str, Any]]:
        """Calculate ranking changes from historical data"""
        changes = []
        
        for current_ranking in current_rankings:
            keyword = current_ranking.keyword
            change_data = {"keyword": keyword, "current_position": current_ranking.position}
            
            # Get historical data for comparison
            if keyword in self.ranking_history:
                historical_rankings = [
                    r for r in self.ranking_history[keyword] 
                    if r.tracked_date >= period_start
                ]
                
                if historical_rankings:
                    previous_position = historical_rankings[0].position
                    change = current_ranking.position - previous_position
                    change_data.update({
                        "previous_position": previous_position,
                        "change": change,
                        "change_direction": "improved" if change < 0 else "declined" if change > 0 else "stable"
                    })
                else:
                    change_data["is_new"] = True
            else:
                change_data["is_new"] = True
            
            changes.append(change_data)
        
        return changes
    
    async def _calculate_visibility_score(self, rankings: List[KeywordRanking]) -> float:
        """Calculate overall visibility score based on rankings and search volumes"""
        if not rankings:
            return 0.0
        
        total_weighted_score = 0
        total_weight = 0
        
        for ranking in rankings:
            # Weight by search volume and position
            position_score = max(0, (101 - ranking.position) / 100)  # Higher score for better positions
            weight = ranking.search_volume
            
            total_weighted_score += position_score * weight
            total_weight += weight
        
        visibility_score = total_weighted_score / total_weight if total_weight > 0 else 0
        return min(visibility_score, 1.0)
    
    async def _cache_ranking_report(self, report: RankingReport):
        """Cache ranking report for quick access"""
        cache_key = f"ranking_report_{report.report_id}"
        await self.cache_manager.set(cache_key, report, ttl=3600)  # Cache for 1 hour
    
    async def add_tracking_keywords(self, keywords: List[str]):
        """Add keywords to tracking list"""
        new_keywords = [kw for kw in keywords if kw not in self.tracking_keywords]
        self.tracking_keywords.extend(new_keywords)
        logger.info(f"Added {len(new_keywords)} new keywords to tracking")
    
    async def remove_tracking_keywords(self, keywords: List[str]):
        """Remove keywords from tracking list"""
        removed_count = 0
        for keyword in keywords:
            if keyword in self.tracking_keywords:
                self.tracking_keywords.remove(keyword)
                removed_count += 1
        logger.info(f"Removed {removed_count} keywords from tracking")
    
    async def get_keyword_history(self, keyword: str, days: int = 30) -> List[KeywordRanking]:
        """Get ranking history for a specific keyword"""
        if keyword not in self.ranking_history:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            ranking for ranking in self.ranking_history[keyword]
            if ranking.tracked_date >= cutoff_date
        ]
    
    async def generate_ranking_insights(self, rankings: List[KeywordRanking]) -> Dict[str, Any]:
        """Generate insights from ranking data"""
        if not rankings:
            return {"error": "No ranking data available"}
        
        # Top performing keywords
        top_performers = sorted(rankings, key=lambda r: r.position)[:5]
        
        # Keywords needing attention
        poor_performers = sorted(rankings, key=lambda r: r.position, reverse=True)[:5]
        
        # High opportunity keywords (low position, high search volume)
        opportunities = sorted(
            [r for r in rankings if r.position > 10],
            key=lambda r: r.search_volume,
            reverse=True
        )[:5]
        
        insights = {
            "summary": {
                "total_keywords": len(rankings),
                "average_position": sum(r.position for r in rankings) / len(rankings),
                "top_10_count": len([r for r in rankings if r.position <= 10]),
                "top_3_count": len([r for r in rankings if r.position <= 3])
            },
            "top_performers": [
                {
                    "keyword": r.keyword,
                    "position": r.position,
                    "search_volume": r.search_volume,
                    "clicks": r.clicks
                } for r in top_performers
            ],
            "improvement_opportunities": [
                {
                    "keyword": r.keyword,
                    "position": r.position,
                    "search_volume": r.search_volume,
                    "potential_traffic": int(r.search_volume * 0.3) if r.position <= 10 else int(r.search_volume * 0.1)
                } for r in opportunities
            ],
            "attention_needed": [
                {
                    "keyword": r.keyword,
                    "position": r.position,
                    "search_volume": r.search_volume
                } for r in poor_performers
            ],
            "recommendations": [
                "Focus on improving rankings for high-volume keywords currently in positions 11-20",
                "Optimize content for keywords that dropped in rankings recently", 
                "Create new content targeting keyword gaps identified in competitor analysis",
                "Improve page load speed and user experience for top-performing pages",
                "Build quality backlinks to pages ranking in positions 4-10 to push into top 3"
            ]
        }
        
        return insights
    
    async def track_competitor_rankings(self, competitor_domain: str, keywords: List[str]) -> Dict[str, Any]:
        """Track competitor rankings for comparison"""
        competitor_rankings = []
        
        for keyword in keywords:
            ranking = await self._get_keyword_ranking(keyword, competitor_domain, "google", "global")
            competitor_rankings.append(ranking)
        
        # Compare with our rankings
        comparison = {
            "competitor_domain": competitor_domain,
            "competitor_rankings": competitor_rankings,
            "opportunities": [],
            "threats": []
        }
        
        for comp_ranking in competitor_rankings:
            keyword = comp_ranking.keyword
            our_rankings = [r for r in self.ranking_history.get(keyword, []) if r.tracked_date >= datetime.utcnow() - timedelta(days=1)]
            
            if our_rankings:
                our_position = our_rankings[-1].position
                if comp_ranking.position < our_position:
                    comparison["threats"].append({
                        "keyword": keyword,
                        "our_position": our_position,
                        "competitor_position": comp_ranking.position,
                        "gap": our_position - comp_ranking.position
                    })
                elif comp_ranking.position > our_position + 5:
                    comparison["opportunities"].append({
                        "keyword": keyword,
                        "our_position": our_position,
                        "competitor_position": comp_ranking.position,
                        "advantage": comp_ranking.position - our_position
                    })
        
        return comparison