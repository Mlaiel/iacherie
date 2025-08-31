"""Social Media Scraper - IA-Influencer-Agent
==========================================

Specialized scraper for social media platforms.
Optimized for social content discovery and engagement tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import json
from urllib.parse import urlparse, parse_qs

from .platform_scraper import PlatformScraper, PlatformContent, PlatformProfile

@dataclass
class SocialMetrics:
    """Social media engagement metrics."""
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    saves: int = 0
    reactions: Dict[str, int] = None
    engagement_rate: float = 0.0
    reach: int = 0
    impressions: int = 0

@dataclass
class InfluencerProfile:
    """Enhanced influencer profile data."""
    platform: str
    username: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    post_count: int
    verified: bool
    category: str
    engagement_rate: float
    average_likes: float
    average_comments: float
    top_hashtags: List[str]
    collaboration_history: List[str]
    contact_info: Dict[str, str]
    brand_mentions: List[str]
    posting_frequency: Dict[str, int]
    best_posting_times: List[str]

@dataclass
class TrendingTopic:
    """Trending topic or hashtag data."""
    platform: str
    topic: str
    hashtag: str
    volume: int
    growth_rate: float
    sentiment: str
    related_topics: List[str]
    top_posts: List[str]
    influencers: List[str]
    timestamp: datetime

class SocialScraper:
    """
    Specialized social media scraper.
    
    Features:
    - Multi-platform social content extraction
    - Influencer discovery and analysis
    - Trending topic monitoring
    - Engagement metrics tracking
    - Hashtag analysis
    - Brand mention tracking
    - Collaboration opportunity detection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform_scraper = PlatformScraper()
        
    async def discover_influencers(self, platform: str, niche: str, 
                                 min_followers: int = 1000,
                                 max_followers: int = 1000000,
                                 engagement_threshold: float = 2.0) -> List[InfluencerProfile]:
        """Discover influencers in specific niche."""
        self.logger.info(f"Discovering influencers in {niche} on {platform}")
        
        # Search for content in niche
        search_terms = [niche, f"#{niche}", f"{niche}influencer"]
        all_influencers = []
        
        for term in search_terms:
            try:
                content_results = await self.platform_scraper.search_content(
                    platform, term, limit=100
                )
                
                # Extract unique authors
                authors = {}
                for content in content_results:
                    if content.author and content.author not in authors:
                        authors[content.author] = content
                        
                # Analyze each author
                for author, sample_content in authors.items():
                    try:
                        profile = await self._analyze_influencer_profile(
                            platform, author, sample_content
                        )
                        
                        # Filter by criteria
                        if (min_followers <= profile.follower_count <= max_followers and
                            profile.engagement_rate >= engagement_threshold):
                            all_influencers.append(profile)
                            
                    except Exception as e:
                        self.logger.debug(f"Failed to analyze {author}: {e}")
                        
            except Exception as e:
                self.logger.error(f"Search failed for {term}: {e}")
                
        # Remove duplicates and sort by engagement
        unique_influencers = {}
        for inf in all_influencers:
            key = f"{inf.platform}_{inf.username}"
            if key not in unique_influencers:
                unique_influencers[key] = inf
                
        return sorted(
            unique_influencers.values(),
            key=lambda x: x.engagement_rate,
            reverse=True
        )
        
    async def _analyze_influencer_profile(self, platform: str, username: str,
                                        sample_content: PlatformContent) -> InfluencerProfile:
        """Analyze influencer profile and metrics."""
        # Get recent content
        recent_content = await self.platform_scraper.monitor_user(
            platform, username, limit=20
        )
        
        if not recent_content:
            recent_content = [sample_content]
            
        # Calculate engagement metrics
        total_likes = sum(c.engagement.get('likes', 0) for c in recent_content)
        total_comments = sum(c.engagement.get('comments', 0) for c in recent_content)
        total_followers = sample_content.author_followers or 0
        
        avg_likes = total_likes / len(recent_content) if recent_content else 0
        avg_comments = total_comments / len(recent_content) if recent_content else 0
        
        engagement_rate = 0
        if total_followers > 0:
            engagement_rate = ((total_likes + total_comments) / len(recent_content)) / total_followers * 100
            
        # Extract hashtags
        all_hashtags = []
        for content in recent_content:
            all_hashtags.extend(content.hashtags)
            
        hashtag_freq = {}
        for tag in all_hashtags:
            hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
            
        top_hashtags = sorted(hashtag_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_hashtags = [tag for tag, freq in top_hashtags]
        
        # Analyze posting patterns
        posting_times = [c.created_at for c in recent_content if c.created_at]
        posting_frequency = self._analyze_posting_frequency(posting_times)
        best_times = self._find_best_posting_times(recent_content)
        
        # Detect brand mentions
        brand_mentions = self._extract_brand_mentions(recent_content)
        
        return InfluencerProfile(
            platform=platform,
            username=username,
            display_name=sample_content.author,
            bio="",  # Would need profile scraping
            follower_count=total_followers,
            following_count=0,  # Would need profile scraping
            post_count=len(recent_content),
            verified=False,  # Would need profile scraping
            category=self._categorize_influencer(recent_content),
            engagement_rate=engagement_rate,
            average_likes=avg_likes,
            average_comments=avg_comments,
            top_hashtags=top_hashtags,
            collaboration_history=[],  # Would need deeper analysis
            contact_info={},
            brand_mentions=brand_mentions,
            posting_frequency=posting_frequency,
            best_posting_times=best_times
        )
        
    def _analyze_posting_frequency(self, posting_times: List[datetime]) -> Dict[str, int]:
        """Analyze posting frequency patterns."""
        if not posting_times:
            return {}
            
        # Group by day of week
        day_counts = {}
        for dt in posting_times:
            day = dt.strftime('%A')
            day_counts[day] = day_counts.get(day, 0) + 1
            
        return day_counts
        
    def _find_best_posting_times(self, content: List[PlatformContent]) -> List[str]:
        """Find best posting times based on engagement."""
        if not content:
            return []
            
        # Analyze engagement by hour
        hour_engagement = {}
        for c in content:
            if c.created_at:
                hour = c.created_at.hour
                engagement = c.engagement.get('likes', 0) + c.engagement.get('comments', 0)
                
                if hour not in hour_engagement:
                    hour_engagement[hour] = []
                hour_engagement[hour].append(engagement)
                
        # Calculate average engagement per hour
        avg_engagement = {}
        for hour, engagements in hour_engagement.items():
            avg_engagement[hour] = sum(engagements) / len(engagements)
            
        # Sort by engagement and return top hours
        sorted_hours = sorted(avg_engagement.items(), key=lambda x: x[1], reverse=True)
        return [f"{hour:02d}:00" for hour, _ in sorted_hours[:3]]
        
    def _categorize_influencer(self, content: List[PlatformContent]) -> str:
        """Categorize influencer based on content."""
        # Analyze hashtags and content for category
        all_text = " ".join([c.title + " " + c.description for c in content])
        all_hashtags = []
        for c in content:
            all_hashtags.extend(c.hashtags)
            
        # Category keywords
        categories = {
            'fashion': ['fashion', 'style', 'outfit', 'ootd', 'clothing', 'designer'],
            'beauty': ['beauty', 'makeup', 'skincare', 'cosmetics', 'beauty'],
            'fitness': ['fitness', 'workout', 'gym', 'health', 'training'],
            'food': ['food', 'recipe', 'cooking', 'foodie', 'restaurant'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'wanderlust'],
            'lifestyle': ['lifestyle', 'daily', 'life', 'motivation', 'inspiration'],
            'tech': ['tech', 'technology', 'gadget', 'app', 'digital'],
            'gaming': ['gaming', 'gamer', 'game', 'stream', 'esports'],
            'music': ['music', 'song', 'artist', 'musician', 'audio'],
            'photography': ['photography', 'photo', 'photographer', 'camera']
        }
        
        # Score each category
        category_scores = {}
        text_lower = all_text.lower()
        hashtags_lower = [h.lower() for h in all_hashtags]
        
        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                score += text_lower.count(keyword)
                score += hashtags_lower.count(keyword) * 2  # Hashtags weighted more
                
            category_scores[category] = score
            
        # Return highest scoring category
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'general'
        
    def _extract_brand_mentions(self, content: List[PlatformContent]) -> List[str]:
        """Extract brand mentions from content."""
        brand_patterns = [
            r'@(\w+)',  # @mentions
            r'#(\w+brand|\w+official)',  # Brand hashtags
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:brand|official|store)\b'  # Brand names
        ]
        
        brands = set()
        for content_item in content:
            text = content_item.title + " " + content_item.description
            
            for pattern in brand_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                brands.update(matches)
                
        return list(brands)[:20]  # Limit to top 20
        
    async def track_hashtag_performance(self, platform: str, hashtag: str,
                                      days: int = 7) -> Dict[str, Any]:
        """Track hashtag performance over time."""
        self.logger.info(f"Tracking #{hashtag} performance on {platform}")
        
        # Search for hashtag content
        content = await self.platform_scraper.search_content(
            platform, f"#{hashtag}", limit=200
        )
        
        if not content:
            return {}
            
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_content = [c for c in content if c.created_at and c.created_at >= cutoff_date]
        
        # Calculate metrics
        total_engagement = sum(
            c.engagement.get('likes', 0) + 
            c.engagement.get('comments', 0) + 
            c.engagement.get('shares', 0)
            for c in recent_content
        )
        
        # Group by day
        daily_metrics = {}
        for c in recent_content:
            if c.created_at:
                day = c.created_at.date()
                if day not in daily_metrics:
                    daily_metrics[day] = {'posts': 0, 'engagement': 0}
                    
                daily_metrics[day]['posts'] += 1
                daily_metrics[day]['engagement'] += (
                    c.engagement.get('likes', 0) + 
                    c.engagement.get('comments', 0) + 
                    c.engagement.get('shares', 0)
                )
                
        # Find top posts
        top_posts = sorted(
            recent_content,
            key=lambda x: x.engagement.get('likes', 0) + x.engagement.get('comments', 0),
            reverse=True
        )[:10]
        
        # Find top creators
        creator_engagement = {}
        for c in recent_content:
            if c.author:
                if c.author not in creator_engagement:
                    creator_engagement[c.author] = 0
                creator_engagement[c.author] += (
                    c.engagement.get('likes', 0) + 
                    c.engagement.get('comments', 0)
                )
                
        top_creators = sorted(creator_engagement.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'hashtag': hashtag,
            'platform': platform,
            'period_days': days,
            'total_posts': len(recent_content),
            'total_engagement': total_engagement,
            'average_engagement_per_post': total_engagement / len(recent_content) if recent_content else 0,
            'daily_metrics': {str(k): v for k, v in daily_metrics.items()},
            'top_posts': [
                {
                    'url': p.url,
                    'author': p.author,
                    'engagement': p.engagement.get('likes', 0) + p.engagement.get('comments', 0),
                    'created_at': p.created_at.isoformat() if p.created_at else None
                }
                for p in top_posts
            ],
            'top_creators': [{'username': u, 'engagement': e} for u, e in top_creators]
        }
        
    async def find_collaboration_opportunities(self, platform: str, content_type: str,
                                            target_audience: str, budget_range: str) -> List[Dict[str, Any]]:
        """Find collaboration opportunities with influencers."""
        self.logger.info(f"Finding collaboration opportunities for {content_type} on {platform}")
        
        # Define search terms based on content type
        search_terms = {
            'music': ['music', 'musician', 'artist', 'song', 'audio'],
            'video': ['video', 'content', 'creator', 'filmmaker'],
            'photography': ['photography', 'photographer', 'photo'],
            'gaming': ['gaming', 'gamer', 'stream', 'esports'],
            'lifestyle': ['lifestyle', 'influencer', 'content']
        }
        
        terms = search_terms.get(content_type, ['content', 'creator'])
        
        # Search for relevant influencers
        opportunities = []
        for term in terms:
            try:
                content_results = await self.platform_scraper.search_content(
                    platform, f"{term} collaboration", limit=50
                )
                
                for content_item in content_results:
                    # Analyze for collaboration indicators
                    collab_score = self._calculate_collaboration_score(content_item, target_audience)
                    
                    if collab_score > 0.6:  # Threshold for good match
                        opportunity = {
                            'influencer': content_item.author,
                            'follower_estimate': content_item.author_followers,
                            'platform': platform,
                            'content_type': content_item.content_type,
                            'collaboration_score': collab_score,
                            'recent_content_url': content_item.url,
                            'engagement_rate': self._estimate_engagement_rate(content_item),
                            'estimated_cost': self._estimate_collaboration_cost(
                                content_item.author_followers, budget_range
                            ),
                            'contact_suggestions': self._suggest_contact_methods(content_item)
                        }
                        opportunities.append(opportunity)
                        
            except Exception as e:
                self.logger.error(f"Search failed for {term}: {e}")
                
        # Sort by collaboration score
        opportunities.sort(key=lambda x: x['collaboration_score'], reverse=True)
        return opportunities[:20]  # Return top 20 opportunities
        
    def _calculate_collaboration_score(self, content: PlatformContent, target_audience: str) -> float:
        """Calculate collaboration suitability score."""
        score = 0.0
        
        # Check content relevance
        text = (content.title + " " + content.description).lower()
        if target_audience.lower() in text:
            score += 0.3
            
        # Check engagement quality
        likes = content.engagement.get('likes', 0)
        comments = content.engagement.get('comments', 0)
        
        if likes > 100:
            score += 0.2
        if comments > 10:
            score += 0.2
            
        # Check for collaboration keywords
        collab_keywords = ['collab', 'partnership', 'sponsor', 'brand', 'work with']
        for keyword in collab_keywords:
            if keyword in text:
                score += 0.1
                break
                
        # Check follower count (sweet spot for collaborations)
        followers = content.author_followers or 0
        if 1000 <= followers <= 100000:
            score += 0.2
        elif 100000 <= followers <= 1000000:
            score += 0.1
            
        return min(score, 1.0)
        
    def _estimate_engagement_rate(self, content: PlatformContent) -> float:
        """Estimate engagement rate from content."""
        followers = content.author_followers or 1
        engagement = content.engagement.get('likes', 0) + content.engagement.get('comments', 0)
        return (engagement / followers) * 100 if followers > 0 else 0
        
    def _estimate_collaboration_cost(self, followers: int, budget_range: str) -> str:
        """Estimate collaboration cost."""
        if not followers:
            return "Unknown"
            
        # Rough estimates per post (in USD)
        if followers < 1000:
            return "$50-100"
        elif followers < 10000:
            return "$100-500"
        elif followers < 100000:
            return "$500-2000"
        elif followers < 1000000:
            return "$2000-10000"
        else:
            return "$10000+"
            
    def _suggest_contact_methods(self, content: PlatformContent) -> List[str]:
        """Suggest contact methods for influencer."""
        suggestions = []
        
        # Check for contact info in bio/description
        text = content.description.lower()
        
        if 'email' in text or '@' in text:
            suggestions.append("Email mentioned in bio")
        if 'dm' in text or 'message' in text:
            suggestions.append("Direct message on platform")
        if 'business' in text:
            suggestions.append("Business inquiries welcome")
            
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Direct message on platform",
                "Comment on recent posts",
                "Check bio for contact info"
            ]
            
        return suggestions
