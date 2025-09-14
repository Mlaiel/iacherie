"""Hashtag Intelligence - AI-Powered Hashtag Generation and Analytics

This module provides intelligent hashtag generation, analysis, and optimization
for social media content across different platforms with trend analysis and performance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter
import json

logger = logging.getLogger(__name__)


class HashtagCategory(Enum):
    """
Categories of hashtags"""

    TRENDING = "trending"
    NICHE = "niche"
    BRANDED = "branded"
    COMMUNITY = "community"
    LOCATION = "location"
    SEASONAL = "seasonal"
    DESCRIPTIVE = "descriptive"
    CAMPAIGN = "campaign"


class Platform(Enum):
    """Social media platforms for hashtag optimization"""

    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"


@dataclass
class HashtagMetrics:
    """Performance metrics for hashtags"""
    usage_count: int
    engagement_rate: float
    reach_potential: int
    competition_level: float  # 0-1 scale
    trend_score: float  # 0-100 scale
    relevance_score: float  # 0-1 scale


@dataclass
class HashtagSuggestion:
    """
Individual hashtag suggestion"""
    hashtag: str
    category: HashtagCategory
    metrics: HashtagMetrics
    platforms: List[Platform]
    related_hashtags: List[str]
    confidence_score: float


@dataclass
class HashtagStrategy:
    """
Complete hashtag strategy for content"""
    primary_hashtags: List[HashtagSuggestion]
    secondary_hashtags: List[HashtagSuggestion]
    trending_hashtags: List[HashtagSuggestion]
    niche_hashtags: List[HashtagSuggestion]
    branded_hashtags: List[HashtagSuggestion]
    platform_specific: Dict[Platform, List[str]]
    total_hashtags: int
    strategy_score: float
    recommendations: List[str]


class HashtagIntelligence:
    """
    AI-powered hashtag intelligence system that generates optimized hashtag strategies
    for social media content across multiple platforms.
    """
    def __init__(self, language -> None: str = "en", region -> None: str = "US") -> None:
        """
        Initialize the hashtag intelligence system.
        
        Args:
            language: Target language for hashtags
            region: Target region for localization
        """
        self.language = language
        self.region = region
        self.trending_hashtags = self._initialize_trending_hashtags()
        self.platform_limits = self._get_platform_limits()
        self.banned_hashtags = self._get_banned_hashtags()

    def generate_hashtag_strategy(
        self,
        content: str,
        keywords: List[str],
        target_platforms: List[Platform],
        industry: str = "",
        brand_name: str = "",
        campaign_name: str = "",
        target_audience: str = "",
        location: str = "",
        max_hashtags: int = 30
    ) -> HashtagStrategy:
        """
        Generate comprehensive hashtag strategy for content.
        
        Args:
            content: Content to generate hashtags for
            keywords: Target keywords
            target_platforms: List of target social media platforms
            industry: Industry/niche context
            brand_name: Brand name for branded hashtags
            campaign_name: Campaign name for campaign hashtags
            target_audience: Target audience description
            location: Location for geo-specific hashtags
            max_hashtags: Maximum number of hashtags to generate
            
        Returns:
            HashtagStrategy with categorized hashtag recommendations
        """
        try:
            logger.info(f"Generating hashtag strategy for {len(target_platforms)} platforms")
            
            # Extract hashtags from content
            content_hashtags = self._extract_hashtags_from_content(content)
            
            # Generate different categories of hashtags
            primary_hashtags = self._generate_primary_hashtags(keywords, industry)
            secondary_hashtags = self._generate_secondary_hashtags(content, keywords)
            trending_hashtags = self._generate_trending_hashtags(keywords, industry)
            niche_hashtags = self._generate_niche_hashtags(industry, target_audience)
            branded_hashtags = self._generate_branded_hashtags(brand_name, campaign_name)
            
            # Generate location-based hashtags
            if location:
                location_hashtags = self._generate_location_hashtags(location)
                niche_hashtags.extend(location_hashtags)
            
            # Optimize for specific platforms
            platform_specific = self._optimize_for_platforms(
                primary_hashtags + secondary_hashtags + trending_hashtags + niche_hashtags,
                target_platforms
            )
            
            # Apply limits and filtering
            all_hashtags = (
                primary_hashtags + secondary_hashtags + trending_hashtags + 
                niche_hashtags + branded_hashtags
            )
            
            # Remove duplicates and banned hashtags
            all_hashtags = self._filter_and_deduplicate(all_hashtags)
            
            # Limit total hashtags
            if len(all_hashtags) > max_hashtags:
                all_hashtags = self._prioritize_hashtags(all_hashtags, max_hashtags)
                
                # Redistribute into categories
                primary_hashtags = [h for h in all_hashtags if h.category == HashtagCategory.DESCRIPTIVE][:5]
                secondary_hashtags = [h for h in all_hashtags if h.category == HashtagCategory.NICHE][:10]
                trending_hashtags = [h for h in all_hashtags if h.category == HashtagCategory.TRENDING][:5]
                niche_hashtags = [h for h in all_hashtags if h.category == HashtagCategory.COMMUNITY][:8]
                branded_hashtags = [h for h in all_hashtags if h.category == HashtagCategory.BRANDED][:2]
            
            # Calculate strategy score
            strategy_score = self._calculate_strategy_score(
                primary_hashtags, secondary_hashtags, trending_hashtags, 
                niche_hashtags, branded_hashtags, target_platforms
            )
            
            # Generate recommendations
            recommendations = self._generate_strategy_recommendations(
                all_hashtags, target_platforms, strategy_score
            )
            
            return HashtagStrategy(
                primary_hashtags=primary_hashtags,
                secondary_hashtags=secondary_hashtags,
                trending_hashtags=trending_hashtags,
                niche_hashtags=niche_hashtags,
                branded_hashtags=branded_hashtags,
                platform_specific=platform_specific,
                total_hashtags=len(all_hashtags),
                strategy_score=strategy_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating hashtag strategy: {str(e)}")
            raise

    def _extract_hashtags_from_content(self, content: str) -> List[str]:
        """Extract existing hashtags from content"""
        hashtag_pattern = r'#[a-zA-Z0-9_]+'
        hashtags = re.findall(hashtag_pattern, content)
        return [tag.lower() for tag in hashtags]

    def _generate_primary_hashtags(self, keywords: List[str], industry: str) -> List[HashtagSuggestion]:
        """
Generate primary hashtags from keywords"""
        primary_hashtags = []
        
        for keyword in keywords[:5]:  # Limit to top 5 keywords
            # Direct keyword hashtag
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            
            if self._is_valid_hashtag(hashtag):
                metrics = self._calculate_hashtag_metrics(hashtag, HashtagCategory.DESCRIPTIVE)
                suggestion = HashtagSuggestion(
                    hashtag=hashtag,
                    category=HashtagCategory.DESCRIPTIVE,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN],
                    related_hashtags=self._get_related_hashtags(hashtag),
                    confidence_score=0.9
                )
                primary_hashtags.append(suggestion)
            
            # Industry-specific variations
            if industry:
                variations = [
                    f"#{keyword.replace(' ', '').lower()}{industry.replace(' ', '').lower()}",
                    f"#{industry.replace(' ', '').lower()}{keyword.replace(' ', '').lower()}",
                    f"#{keyword.replace(' ', '').lower()}tips",
                    f"#{keyword.replace(' ', '').lower()}guide"
                ]
                
                for variation in variations:
                    if len(primary_hashtags) < 8 and self._is_valid_hashtag(variation):
                        metrics = self._calculate_hashtag_metrics(variation, HashtagCategory.DESCRIPTIVE)
                        suggestion = HashtagSuggestion(
                            hashtag=variation,
                            category=HashtagCategory.DESCRIPTIVE,
                            metrics=metrics,
                            platforms=[Platform.INSTAGRAM, Platform.TWITTER],
                            related_hashtags=self._get_related_hashtags(variation),
                            confidence_score=0.8
                        )
                        primary_hashtags.append(suggestion)
        
        return primary_hashtags

    def _generate_secondary_hashtags(self, content: str, keywords: List[str]) -> List[HashtagSuggestion]:
        """Generate secondary hashtags from content analysis"""
        secondary_hashtags = []
        
        # Extract meaningful words from content
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = Counter(words)
        
        # Filter out common words and focus on content-specific terms
        stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were', 'about', 'more', 'into', 'after', 'before'}
        meaningful_words = [word for word, freq in word_freq.most_common(20) if word not in stop_words and freq > 1]
        
        for word in meaningful_words[:10]:
            hashtag = f"#{word}"
            
            if self._is_valid_hashtag(hashtag):
                metrics = self._calculate_hashtag_metrics(hashtag, HashtagCategory.NICHE)
                suggestion = HashtagSuggestion(
                    hashtag=hashtag,
                    category=HashtagCategory.NICHE,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.TWITTER],
                    related_hashtags=self._get_related_hashtags(hashtag),
                    confidence_score=0.7
                )
                secondary_hashtags.append(suggestion)
        
        # Add action-based hashtags
        action_hashtags = [
            "#learn", "#discover", "#explore", "#create", "#build",
            "#improve", "#master", "#achieve", "#succeed", "#grow"
        ]
        
        for action_hashtag in action_hashtags:
            if len(secondary_hashtags) < 15:
                metrics = self._calculate_hashtag_metrics(action_hashtag, HashtagCategory.COMMUNITY)
                suggestion = HashtagSuggestion(
                    hashtag=action_hashtag,
                    category=HashtagCategory.COMMUNITY,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.LINKEDIN],
                    related_hashtags=self._get_related_hashtags(action_hashtag),
                    confidence_score=0.6
                )
                secondary_hashtags.append(suggestion)
        
        return secondary_hashtags

    def _generate_trending_hashtags(self, keywords: List[str], industry: str) -> List[HashtagSuggestion]:
        """Generate trending hashtags"""
        trending_hashtags = []
        
        # Get trending hashtags for the industry
        industry_trending = self.trending_hashtags.get(industry.lower(), [])
        
        # Add general trending hashtags
        general_trending = self.trending_hashtags.get("general", [])
        
        all_trending = industry_trending + general_trending
        
        for trending_tag in all_trending[:8]:
            if trending_tag not in [h.hashtag for h in trending_hashtags]:
                metrics = self._calculate_hashtag_metrics(trending_tag, HashtagCategory.TRENDING)
                # Boost metrics for trending hashtags
                metrics.trend_score = min(100, metrics.trend_score * 1.5)
                metrics.reach_potential = int(metrics.reach_potential * 2)
                
                suggestion = HashtagSuggestion(
                    hashtag=trending_tag,
                    category=HashtagCategory.TRENDING,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER],
                    related_hashtags=self._get_related_hashtags(trending_tag),
                    confidence_score=0.8
                )
                trending_hashtags.append(suggestion)
        
        # Combine keywords with trending modifiers
        trending_modifiers = ["2025", "trending", "viral", "popular", "hot", "new"]
        
        for keyword in keywords[:3]:
            for modifier in trending_modifiers[:2]:
                trending_combo = f"#{keyword.replace(' ', '').lower()}{modifier}"
                
                if len(trending_hashtags) < 10 and self._is_valid_hashtag(trending_combo):
                    metrics = self._calculate_hashtag_metrics(trending_combo, HashtagCategory.TRENDING)
                    suggestion = HashtagSuggestion(
                        hashtag=trending_combo,
                        category=HashtagCategory.TRENDING,
                        metrics=metrics,
                        platforms=[Platform.INSTAGRAM, Platform.TIKTOK],
                        related_hashtags=self._get_related_hashtags(trending_combo),
                        confidence_score=0.7
                    )
                    trending_hashtags.append(suggestion)
        
        return trending_hashtags

    def _generate_niche_hashtags(self, industry: str, target_audience: str) -> List[HashtagSuggestion]:
        """Generate niche and community hashtags"""
        niche_hashtags = []
        
        # Industry-specific community hashtags
        if industry:
            industry_communities = {
                "marketing": ["#marketingcommunity", "#digitalmarketers", "#marketingtips", "#marketinglife"],
                "technology": ["#techcommunity", "#developers", "#coding", "#innovation"],
                "business": ["#entrepreneurship", "#startup", "#businessowner", "#leadership"],
                "fitness": ["#fitnesscommunity", "#workout", "#healthy", "#wellness"],
                "food": ["#foodie", "#cooking", "#recipe", "#chef"],
                "travel": ["#wanderlust", "#travel", "#explore", "#adventure"],
                "fashion": ["#fashion", "#style", "#ootd", "#fashionista"],
                "art": ["#artist", "#creative", "#art", "#design"]
            }
            
            communities = industry_communities.get(industry.lower(), [])
            
            for community_tag in communities:
                if len(niche_hashtags) < 8:
                    metrics = self._calculate_hashtag_metrics(community_tag, HashtagCategory.COMMUNITY)
                    suggestion = HashtagSuggestion(
                        hashtag=community_tag,
                        category=HashtagCategory.COMMUNITY,
                        metrics=metrics,
                        platforms=[Platform.INSTAGRAM, Platform.LINKEDIN],
                        related_hashtags=self._get_related_hashtags(community_tag),
                        confidence_score=0.8
                    )
                    niche_hashtags.append(suggestion)
        
        # Audience-specific hashtags
        if target_audience:
            audience_lower = target_audience.lower()
            
            if "entrepreneur" in audience_lower or "business" in audience_lower:
                business_tags = ["#entrepreneur", "#smallbusiness", "#businesstips", "#success"]
                for tag in business_tags:
                    if len(niche_hashtags) < 12:
                        metrics = self._calculate_hashtag_metrics(tag, HashtagCategory.COMMUNITY)
                        suggestion = HashtagSuggestion(
                            hashtag=tag,
                            category=HashtagCategory.COMMUNITY,
                            metrics=metrics,
                            platforms=[Platform.LINKEDIN, Platform.INSTAGRAM],
                            related_hashtags=self._get_related_hashtags(tag),
                            confidence_score=0.7
                        )
                        niche_hashtags.append(suggestion)
            
            elif "creative" in audience_lower or "artist" in audience_lower:
                creative_tags = ["#creative", "#artist", "#design", "#inspiration"]
                for tag in creative_tags:
                    if len(niche_hashtags) < 12:
                        metrics = self._calculate_hashtag_metrics(tag, HashtagCategory.COMMUNITY)
                        suggestion = HashtagSuggestion(
                            hashtag=tag,
                            category=HashtagCategory.COMMUNITY,
                            metrics=metrics,
                            platforms=[Platform.INSTAGRAM, Platform.TWITTER],
                            related_hashtags=self._get_related_hashtags(tag),
                            confidence_score=0.7
                        )
                        niche_hashtags.append(suggestion)
        
        return niche_hashtags

    def _generate_branded_hashtags(self, brand_name: str, campaign_name: str) -> List[HashtagSuggestion]:
        """Generate branded and campaign hashtags"""
        branded_hashtags = []
        
        if brand_name:
            brand_tag = f"#{brand_name.replace(' ', '').lower()}"
            
            if self._is_valid_hashtag(brand_tag):
                metrics = self._calculate_hashtag_metrics(brand_tag, HashtagCategory.BRANDED)
                suggestion = HashtagSuggestion(
                    hashtag=brand_tag,
                    category=HashtagCategory.BRANDED,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN],
                    related_hashtags=[],
                    confidence_score=1.0
                )
                branded_hashtags.append(suggestion)
        
        if campaign_name:
            campaign_tag = f"#{campaign_name.replace(' ', '').lower()}"
            
            if self._is_valid_hashtag(campaign_tag):
                metrics = self._calculate_hashtag_metrics(campaign_tag, HashtagCategory.CAMPAIGN)
                suggestion = HashtagSuggestion(
                    hashtag=campaign_tag,
                    category=HashtagCategory.CAMPAIGN,
                    metrics=metrics,
                    platforms=[Platform.INSTAGRAM, Platform.TWITTER],
                    related_hashtags=[],
                    confidence_score=1.0
                )
                branded_hashtags.append(suggestion)
        
        return branded_hashtags

    def _generate_location_hashtags(self, location: str) -> List[HashtagSuggestion]:
        """Generate location-based hashtags"""
        location_hashtags = []
        
        location_parts = location.replace(',', ' ').split()
        
        for part in location_parts:
            if len(part) > 2:  # Skip very short parts like state abbreviations
                location_tag = f"#{part.lower()}"
                
                if self._is_valid_hashtag(location_tag):
                    metrics = self._calculate_hashtag_metrics(location_tag, HashtagCategory.LOCATION)
                    suggestion = HashtagSuggestion(
                        hashtag=location_tag,
                        category=HashtagCategory.LOCATION,
                        metrics=metrics,
                        platforms=[Platform.INSTAGRAM, Platform.FACEBOOK],
                        related_hashtags=self._get_related_hashtags(location_tag),
                        confidence_score=0.8
                    )
                    location_hashtags.append(suggestion)
        
        return location_hashtags[:3]  # Limit location hashtags

    def _optimize_for_platforms(
        self, 
        hashtags: List[HashtagSuggestion], 
        target_platforms: List[Platform]
    ) -> Dict[Platform, List[str]]:
        """Optimize hashtag selection for specific platforms"""
        
        platform_specific = {}
        
        for platform in target_platforms:
            platform_hashtags = []
            limit = self.platform_limits.get(platform, 30)
            
            # Filter hashtags suitable for this platform
            suitable_hashtags = [
                h for h in hashtags 
                if platform in h.platforms and h.hashtag not in self.banned_hashtags.get(platform, [])
            ]
            
            # Sort by relevance and confidence
            suitable_hashtags.sort(
                key=lambda x: x.confidence_score * x.metrics.relevance_score, 
                reverse=True
            )
            
            # Apply platform-specific optimization
            if platform == Platform.INSTAGRAM:
                # Instagram allows up to 30 hashtags
                platform_hashtags = [h.hashtag for h in suitable_hashtags[:min(limit, 30)]]
                
            elif platform == Platform.TWITTER:
                # Twitter works best with 1-2 hashtags
                platform_hashtags = [h.hashtag for h in suitable_hashtags[:2]]
                
            elif platform == Platform.LINKEDIN:
                # LinkedIn works best with 3-5 professional hashtags
                professional_hashtags = [
                    h for h in suitable_hashtags 
                    if h.category in [HashtagCategory.BRANDED, HashtagCategory.DESCRIPTIVE, HashtagCategory.COMMUNITY]
                ]
                platform_hashtags = [h.hashtag for h in professional_hashtags[:5]]
                
            elif platform == Platform.TIKTOK:
                # TikTok works well with trending hashtags
                trending_focus = [
                    h for h in suitable_hashtags 
                    if h.category == HashtagCategory.TRENDING
                ] + [h for h in suitable_hashtags if h.category != HashtagCategory.TRENDING]
                platform_hashtags = [h.hashtag for h in trending_focus[:10]]
                
            else:
                platform_hashtags = [h.hashtag for h in suitable_hashtags[:limit]]
            
            platform_specific[platform] = platform_hashtags
        
        return platform_specific

    def _filter_and_deduplicate(self, hashtags: List[HashtagSuggestion]) -> List[HashtagSuggestion]:
        """
Filter banned hashtags and remove duplicates"""
        
        seen_hashtags = set()
        filtered_hashtags = []
        
        for hashtag_suggestion in hashtags:
            hashtag = hashtag_suggestion.hashtag.lower()
            
            # Skip if already seen
            if hashtag in seen_hashtags:
                continue
            
            # Skip if banned
            if any(hashtag in banned_list for banned_list in self.banned_hashtags.values()):
                continue
            
            # Skip if invalid
            if not self._is_valid_hashtag(hashtag):
                continue
            
            seen_hashtags.add(hashtag)
            filtered_hashtags.append(hashtag_suggestion)
        
        return filtered_hashtags

    def _prioritize_hashtags(self, hashtags: List[HashtagSuggestion], max_count: int) -> List[HashtagSuggestion]:
        """
Prioritize hashtags when limiting total count"""
        
        # Calculate priority score for each hashtag
        for hashtag in hashtags:
            priority_score = (
                hashtag.confidence_score * 0.3 +
                hashtag.metrics.relevance_score * 0.25 +
                hashtag.metrics.trend_score / 100 * 0.2 +
                (1 - hashtag.metrics.competition_level) * 0.15 +
                hashtag.metrics.engagement_rate * 0.1
            )
            hashtag.priority_score = priority_score
        
        # Sort by priority and return top hashtags
        hashtags.sort(key=lambda x: getattr(x, 'priority_score', 0), reverse=True)
        return hashtags[:max_count]

    def _calculate_hashtag_metrics(self, hashtag: str, category: HashtagCategory) -> HashtagMetrics:
        """
Calculate metrics for a hashtag (simulated data for demo)"""
        
        hashtag_length = len(hashtag)
        
        # Simulate usage count based on hashtag characteristics
        if category == HashtagCategory.TRENDING:
            usage_count = 100000 + (1000 * (20 - hashtag_length))
        elif category == HashtagCategory.BRANDED:
            usage_count = 5000 + (100 * (20 - hashtag_length))
        elif category == HashtagCategory.NICHE:
            usage_count = 50000 + (500 * (20 - hashtag_length))
        else:
            usage_count = 25000 + (300 * (20 - hashtag_length))
        
        # Simulate engagement rate (shorter hashtags often have higher engagement)
        engagement_rate = max(0.01, min(0.15, 0.1 - (hashtag_length * 0.005)))
        
        # Simulate reach potential
        reach_potential = int(usage_count * engagement_rate * 10)
        
        # Simulate competition (popular hashtags have more competition)
        competition_level = min(1.0, usage_count / 100000)
        
        # Simulate trend score
        if category == HashtagCategory.TRENDING:
            trend_score = 85 + (hashtag_length % 15)
        elif category == HashtagCategory.SEASONAL:
            trend_score = 70 + (hashtag_length % 20)
        else:
            trend_score = 40 + (hashtag_length % 30)
        
        # Calculate relevance score
        relevance_score = 0.8 if category in [HashtagCategory.DESCRIPTIVE, HashtagCategory.BRANDED] else 0.6
        
        return HashtagMetrics(
            usage_count=max(1, usage_count),
            engagement_rate=round(engagement_rate, 3),
            reach_potential=max(100, reach_potential),
            competition_level=round(competition_level, 2),
            trend_score=round(trend_score, 1),
            relevance_score=round(relevance_score, 2)
        )

    def _calculate_strategy_score(
        self,
        primary_hashtags: List[HashtagSuggestion],
        secondary_hashtags: List[HashtagSuggestion],
        trending_hashtags: List[HashtagSuggestion],
        niche_hashtags: List[HashtagSuggestion],
        branded_hashtags: List[HashtagSuggestion],
        target_platforms: List[Platform]
    ) -> float:
        """
Calculate overall strategy score"""
        
        score = 0.0
        
        # Diversity score (25 points)
        categories_present = len(set([
            h.category for h in 
            primary_hashtags + secondary_hashtags + trending_hashtags + niche_hashtags + branded_hashtags
        ]))
        score += (categories_present / 6) * 25
        
        # Platform optimization score (20 points)
        score += min(20, len(target_platforms) * 5)
        
        # Trending content score (20 points)
        if trending_hashtags:
            avg_trend_score = sum(h.metrics.trend_score for h in trending_hashtags) / len(trending_hashtags)
            score += (avg_trend_score / 100) * 20
        
        # Relevance score (20 points)
        all_hashtags = primary_hashtags + secondary_hashtags + trending_hashtags + niche_hashtags
        if all_hashtags:
            avg_relevance = sum(h.metrics.relevance_score for h in all_hashtags) / len(all_hashtags)
            score += avg_relevance * 20
        
        # Competition balance score (15 points)
        if all_hashtags:
            avg_competition = sum(h.metrics.competition_level for h in all_hashtags) / len(all_hashtags)
            # Sweet spot is around 0.3-0.7 competition
            if 0.3 <= avg_competition <= 0.7:
                score += 15
            else:
                score += max(0, 15 - abs(avg_competition - 0.5) * 30)
        
        return min(100.0, score)

    def _generate_strategy_recommendations(
        self,
        all_hashtags: List[HashtagSuggestion],
        target_platforms: List[Platform],
        strategy_score: float
    ) -> List[str]:
        """
Generate strategy recommendations"""
        
        recommendations = []
        
        # Strategy score recommendations
        if strategy_score < 60:
            recommendations.append("Hashtag strategy needs improvement. Consider more diverse hashtag categories.")
        
        # Category balance recommendations
        categories = [h.category for h in all_hashtags]
        category_counts = Counter(categories)
        
        if category_counts.get(HashtagCategory.TRENDING, 0) == 0:
            recommendations.append("Add trending hashtags to increase visibility.")
        
        if category_counts.get(HashtagCategory.NICHE, 0) < 3:
            recommendations.append("Add more niche hashtags to reach targeted audiences.")
        
        if category_counts.get(HashtagCategory.BRANDED, 0) == 0:
            recommendations.append("Consider adding branded hashtags for brand recognition.")
        
        # Platform-specific recommendations
        if Platform.INSTAGRAM in target_platforms and len(all_hashtags) < 15:
            recommendations.append("Instagram allows up to 30 hashtags. Consider adding more for better reach.")
        
        if Platform.TWITTER in target_platforms and len(all_hashtags) > 3:
            recommendations.append("Twitter works best with 1-2 focused hashtags. Consider reducing for Twitter.")
        
        if Platform.LINKEDIN in target_platforms:
            professional_hashtags = [h for h in all_hashtags if h.category in [HashtagCategory.DESCRIPTIVE, HashtagCategory.COMMUNITY]]
            if len(professional_hashtags) < 3:
                recommendations.append("Add more professional hashtags for LinkedIn optimization.")
        
        # Competition recommendations
        high_competition = [h for h in all_hashtags if h.metrics.competition_level > 0.8]
        if len(high_competition) > len(all_hashtags) * 0.5:
            recommendations.append("Too many high-competition hashtags. Mix in some niche hashtags.")
        
        return recommendations

    def _is_valid_hashtag(self, hashtag: str) -> bool:
        """Validate hashtag format and content"""
        
        # Must start with #
        if not hashtag.startswith('#'):
            return False
        
        # Remove # for validation
        tag_content = hashtag[1:]
        
        # Must not be empty
        if not tag_content:
            return False
        
        # Must contain only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', tag_content):
            return False
        
        # Length limits (Instagram: 1-100 characters, others similar)
        if len(tag_content) > 100 or len(tag_content) < 1:
            return False
        
        # Must not be all numbers
        if tag_content.isdigit():
            return False
        
        return True

    def _get_related_hashtags(self, hashtag: str) -> List[str]:
        """
Get related hashtags (simplified implementation)"""
        
        # Simple related hashtag generation based on the hashtag content
        related = []
        
        hashtag_lower = hashtag.lower()
        
        # Common related hashtags mapping
        relations = {
            'marketing': ['#digitalmarketing', '#socialmedia', '#content', '#branding'],
            'business': ['#entrepreneur', '#startup', '#success', '#growth'],
            'fitness': ['#workout', '#health', '#wellness', '#motivation'],
            'food': ['#recipe', '#cooking', '#chef', '#delicious'],
            'travel': ['#wanderlust', '#adventure', '#explore', '#vacation'],
            'tech': ['#technology', '#innovation', '#coding', '#digital'],
            'art': ['#creative', '#design', '#artist', '#inspiration']
        }
        
        for key, values in relations.items():
            if key in hashtag_lower:
                related.extend(values[:3])
                break
        
        return related[:5]

    def _initialize_trending_hashtags(self) -> Dict[str, List[str]]:
        """
Initialize trending hashtags database"""
        
        return {
            "general": [
                "#trending", "#viral", "#2025", "#new", "#popular", "#hot",
                "#love", "#instagood", "#photooftheday", "#beautiful", "#happy"
            ],
            "marketing": [
                "#digitalmarketing", "#socialmediamarketing", "#contentmarketing",
                "#marketing2025", "#marketingtips", "#growthhacking"
            ],
            "business": [
                "#entrepreneur", "#startup", "#business2025", "#leadership",
                "#innovation", "#success", "#productivity"
            ],
            "technology": [
                "#ai", "#artificialintelligence", "#tech2025", "#innovation",
                "#automation", "#digitaltransformation", "#futuretech"
            ],
            "fitness": [
                "#fitness2025", "#newyeargoals", "#healthylifestyle",
                "#workoutmotivation", "#wellness", "#fitnesstrend"
            ]
        }

    def _get_platform_limits(self) -> Dict[Platform, int]:
        """Get hashtag limits for each platform"""
        
        return {
            Platform.INSTAGRAM: 30,
            Platform.TWITTER: 2,
            Platform.TIKTOK: 10,
            Platform.LINKEDIN: 5,
            Platform.FACEBOOK: 10,
            Platform.YOUTUBE: 15
        }

    def _get_banned_hashtags(self) -> Dict[Platform, List[str]]:
        """
Get banned hashtags for each platform"""
        
        # Simplified banned hashtags list
        common_banned = ["#followme", "#like4like", "#follow4follow"]
        
        return {
            Platform.INSTAGRAM: common_banned + ["#instagramdown", "#shadowban"],
            Platform.TWITTER: common_banned + ["#twitterdown"],
            Platform.TIKTOK: common_banned + ["#ban", "#blocked"],
            Platform.LINKEDIN: common_banned + ["#unprofessional"],
            Platform.FACEBOOK: common_banned + ["#facebookdown"],
            Platform.YOUTUBE: common_banned + ["#youtubedown"]
        }

    def analyze_hashtag_performance(self, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze performance of given hashtags"""
        
        analysis = {
            "hashtag_count": len(hashtags),
            "valid_hashtags": [],
            "invalid_hashtags": [],
            "category_breakdown": {},
            "platform_suitability": {},
            "recommendations": []
        }
        
        for hashtag in hashtags:
            if self._is_valid_hashtag(hashtag):
                analysis["valid_hashtags"].append(hashtag)
                
                # Determine category (simplified)
                if any(trend in hashtag.lower() for trend in ["trending", "viral", "2025", "new"]):
                    category = HashtagCategory.TRENDING
                elif len(hashtag) > 15:
                    category = HashtagCategory.NICHE
                else:
                    category = HashtagCategory.DESCRIPTIVE
                
                analysis["category_breakdown"][hashtag] = category.value
            else:
                analysis["invalid_hashtags"].append(hashtag)
        
        # Platform suitability analysis
        for platform in Platform:
            suitable_count = len([h for h in analysis["valid_hashtags"] 
                                if h not in self.banned_hashtags.get(platform, [])])
            analysis["platform_suitability"][platform.value] = {
                "suitable_hashtags": suitable_count,
                "within_limit": suitable_count <= self.platform_limits.get(platform, 30)
            }
        
        # Generate recommendations
        if len(analysis["invalid_hashtags"]) > 0:
            analysis["recommendations"].append(f"Remove {len(analysis['invalid_hashtags'])} invalid hashtags")
        
        if len(analysis["valid_hashtags"]) < 5:
            analysis["recommendations"].append("Add more hashtags for better reach")
        
        return analysis

    def export_hashtag_strategy(self, strategy: HashtagStrategy, format: str = "json") -> str:
        """Export hashtag strategy in specified format"""
        
        if format == "json":
            return self._export_strategy_to_json(strategy)
        elif format == "csv":
            return self._export_strategy_to_csv(strategy)
        elif format == "text":
            return self._export_strategy_to_text(strategy)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_strategy_to_json(self, strategy: HashtagStrategy) -> str:
        """Export strategy to JSON format"""
        
        export_data = {
            "strategy_score": strategy.strategy_score,
            "total_hashtags": strategy.total_hashtags,
            "primary_hashtags": [self._hashtag_to_dict(h) for h in strategy.primary_hashtags],
            "secondary_hashtags": [self._hashtag_to_dict(h) for h in strategy.secondary_hashtags],
            "trending_hashtags": [self._hashtag_to_dict(h) for h in strategy.trending_hashtags],
            "niche_hashtags": [self._hashtag_to_dict(h) for h in strategy.niche_hashtags],
            "branded_hashtags": [self._hashtag_to_dict(h) for h in strategy.branded_hashtags],
            "platform_specific": {p.value: hashtags for p, hashtags in strategy.platform_specific.items()},
            "recommendations": strategy.recommendations
        }
        
        return json.dumps(export_data, indent=2)

    def _hashtag_to_dict(self, hashtag_suggestion: HashtagSuggestion) -> Dict[str, Any]:
        """Convert HashtagSuggestion to dictionary"""
        
        return {
            "hashtag": hashtag_suggestion.hashtag,
            "category": hashtag_suggestion.category.value,
            "usage_count": hashtag_suggestion.metrics.usage_count,
            "engagement_rate": hashtag_suggestion.metrics.engagement_rate,
            "reach_potential": hashtag_suggestion.metrics.reach_potential,
            "competition_level": hashtag_suggestion.metrics.competition_level,
            "trend_score": hashtag_suggestion.metrics.trend_score,
            "relevance_score": hashtag_suggestion.metrics.relevance_score,
            "confidence_score": hashtag_suggestion.confidence_score,
            "platforms": [p.value for p in hashtag_suggestion.platforms],
            "related_hashtags": hashtag_suggestion.related_hashtags
        }

    def _export_strategy_to_csv(self, strategy: HashtagStrategy) -> str:
        """Export strategy to CSV format"""
        
        csv_lines = ["Hashtag,Category,Usage Count,Engagement Rate,Competition,Trend Score,Confidence"]
        
        all_hashtags = (
            strategy.primary_hashtags + strategy.secondary_hashtags + 
            strategy.trending_hashtags + strategy.niche_hashtags + strategy.branded_hashtags
        )
        
        for h in all_hashtags:
            line = f'"{h.hashtag}",{h.category.value},{h.metrics.usage_count},' \
                   f'{h.metrics.engagement_rate},{h.metrics.competition_level},' \
                   f'{h.metrics.trend_score},{h.confidence_score}'
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)

    def _export_strategy_to_text(self, strategy: HashtagStrategy) -> str:
        """Export strategy to readable text format"""
        
        lines = []
        lines.append(f"Hashtag Strategy (Score: {strategy.strategy_score:.1f}/100)")
        lines.append("=" * 50)
        
        if strategy.primary_hashtags:
            lines.append("\nPrimary Hashtags:")
            for h in strategy.primary_hashtags:
                lines.append(f"  {h.hashtag}")
        
        if strategy.trending_hashtags:
            lines.append("\nTrending Hashtags:")
            for h in strategy.trending_hashtags:
                lines.append(f"  {h.hashtag}")
        
        if strategy.niche_hashtags:
            lines.append("\nNiche Hashtags:")
            for h in strategy.niche_hashtags:
                lines.append(f"  {h.hashtag}")
        
        if strategy.branded_hashtags:
            lines.append("\nBranded Hashtags:")
            for h in strategy.branded_hashtags:
                lines.append(f"  {h.hashtag}")
        
        lines.append(f"\nPlatform-Specific:")
        for platform, hashtags in strategy.platform_specific.items():
            lines.append(f"  {platform.value}: {' '.join(hashtags[:5])}")
        
        if strategy.recommendations:
            lines.append("\nRecommendations:")
            for rec in strategy.recommendations:
                lines.append(f"  - {rec}")
        
        return '\n'.join(lines)


# Export for module usage
__all__ = [
    "HashtagIntelligence",
    "HashtagCategory",
    "Platform",
    "HashtagMetrics", 
    "HashtagSuggestion",
    "HashtagStrategy"
]