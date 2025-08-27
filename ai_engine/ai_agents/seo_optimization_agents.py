"""
SEO Optimization AI Agents

Specialized agents for SEO optimization, content discoverability, and search ranking improvement.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

This module contains AI agents specialized in SEO optimization, keyword research,
content discoverability, and search engine ranking improvement for creators.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import re
import numpy as np
from dataclasses import dataclass

from .base_agent import BaseAIAgent
from ..neural_networks.optimization_networks import SEOOptimizationNetwork


@dataclass
class SEOAnalysis:
    """SEO analysis results"""
    seo_score: float
    keyword_performance: Dict[str, float]
    optimization_opportunities: List[str]
    ranking_potential: float
    competitor_analysis: Dict[str, Any]
    technical_issues: List[str]
    content_recommendations: List[str]


@dataclass
class KeywordOpportunity:
    """Keyword opportunity structure"""
    keyword: str
    search_volume: int
    competition: float
    difficulty: float
    relevance_score: float
    potential_traffic: int
    content_gap_score: float
    recommended_action: str


class SEOOptimizerAgent(BaseAIAgent):
    """
    AI agent specialized in SEO optimization and content discoverability.
    
    Provides comprehensive SEO analysis, keyword research, content optimization
    recommendations, and search ranking improvement strategies.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id="seo_optimizer", config=config)
        self.seo_network = SEOOptimizationNetwork()
        self.keyword_database = {}
        self.competitor_data = {}
        
        # SEO optimization parameters
        self.ranking_factors = [
            "keyword_relevance", "content_quality", "engagement_metrics",
            "technical_seo", "backlink_profile", "user_experience",
            "content_freshness", "social_signals", "mobile_optimization"
        ]
        
        self.content_types = [
            "video_titles", "video_descriptions", "thumbnails", "tags",
            "channel_description", "playlists", "community_posts", "shorts"
        ]
        
        # SEO scoring weights
        self.seo_weights = {
            "keyword_optimization": 0.25,
            "content_structure": 0.20,
            "engagement_signals": 0.20,
            "technical_factors": 0.15,
            "competitive_positioning": 0.10,
            "social_proof": 0.10
        }
        
        logging.info(f"SEOOptimizerAgent initialized with {len(self.ranking_factors)} ranking factors")

    async def analyze_content_seo(self, content_data: Dict[str, Any]) -> SEOAnalysis:
        """
        Analyze content for SEO performance and optimization opportunities.
        
        Args:
            content_data: Content metadata, performance, and SEO data
            
        Returns:
            Comprehensive SEO analysis
        """
        try:
            content_type = content_data.get('type', 'video')
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            tags = content_data.get('tags', [])
            performance_data = content_data.get('performance', {})
            
            # Analyze current SEO performance
            seo_scores = {}
            
            # Keyword optimization analysis
            keyword_analysis = await self._analyze_keyword_optimization(
                title, description, tags
            )
            seo_scores['keyword_optimization'] = keyword_analysis['score']
            
            # Content structure analysis
            structure_score = self._analyze_content_structure(title, description)
            seo_scores['content_structure'] = structure_score
            
            # Engagement signals analysis
            engagement_score = self._analyze_engagement_signals(performance_data)
            seo_scores['engagement_signals'] = engagement_score
            
            # Technical SEO factors
            technical_score = self._analyze_technical_factors(content_data)
            seo_scores['technical_factors'] = technical_score
            
            # Competitive positioning
            competitive_score = await self._analyze_competitive_positioning(
                keyword_analysis['primary_keywords'], content_data.get('niche', 'general')
            )
            seo_scores['competitive_positioning'] = competitive_score['score']
            
            # Calculate overall SEO score
            overall_seo_score = sum(
                seo_scores[factor] * weight 
                for factor, weight in self.seo_weights.items()
                if factor in seo_scores
            )
            
            # Identify optimization opportunities
            optimization_opportunities = self._identify_seo_opportunities(
                seo_scores, keyword_analysis, competitive_score
            )
            
            # Analyze ranking potential
            ranking_potential = self._calculate_ranking_potential(
                seo_scores, performance_data, competitive_score
            )
            
            # Identify technical issues
            technical_issues = self._identify_technical_issues(content_data)
            
            # Generate content recommendations
            content_recommendations = self._generate_content_recommendations(
                keyword_analysis, seo_scores, content_type
            )
            
            return SEOAnalysis(
                seo_score=overall_seo_score,
                keyword_performance=keyword_analysis['keyword_scores'],
                optimization_opportunities=optimization_opportunities,
                ranking_potential=ranking_potential,
                competitor_analysis=competitive_score,
                technical_issues=technical_issues,
                content_recommendations=content_recommendations
            )
            
        except Exception as e:
            logging.error(f"Error in SEO analysis: {e}")
            return SEOAnalysis(
                seo_score=0.0,
                keyword_performance={},
                optimization_opportunities=["SEO analysis failed - manual review needed"],
                ranking_potential=0.0,
                competitor_analysis={},
                technical_issues=["Unable to analyze technical factors"],
                content_recommendations=["Professional SEO audit recommended"]
            )

    async def research_keyword_opportunities(self, creator_profile: Dict[str, Any],
                                           target_topics: List[str]) -> List[KeywordOpportunity]:
        """
        Research keyword opportunities for content creation.
        
        Args:
            creator_profile: Creator's niche, audience, and current content
            target_topics: Topics the creator wants to target
            
        Returns:
            List of keyword opportunities ranked by potential
        """
        try:
            niche = creator_profile.get('niche', 'general')
            audience_demographics = creator_profile.get('audience_demographics', {})
            current_keywords = creator_profile.get('current_top_keywords', [])
            
            opportunities = []
            
            for topic in target_topics:
                # Generate keyword variations
                keyword_variations = await self._generate_keyword_variations(topic, niche)
                
                for keyword in keyword_variations:
                    # Skip if already targeting this keyword
                    if keyword.lower() in [kw.lower() for kw in current_keywords]:
                        continue
                    
                    # Analyze keyword metrics
                    search_volume = await self._get_search_volume(keyword, niche)
                    competition = await self._analyze_keyword_competition(keyword, niche)
                    difficulty = self._calculate_keyword_difficulty(keyword, competition)
                    relevance = self._calculate_keyword_relevance(keyword, creator_profile)
                    
                    # Estimate potential traffic
                    potential_traffic = self._estimate_potential_traffic(
                        search_volume, competition, creator_profile.get('authority_score', 0.5)
                    )
                    
                    # Analyze content gap
                    content_gap_score = await self._analyze_content_gap(keyword, creator_profile)
                    
                    # Determine recommended action
                    recommended_action = self._determine_keyword_action(
                        difficulty, relevance, content_gap_score, potential_traffic
                    )
                    
                    opportunity = KeywordOpportunity(
                        keyword=keyword,
                        search_volume=search_volume,
                        competition=competition,
                        difficulty=difficulty,
                        relevance_score=relevance,
                        potential_traffic=potential_traffic,
                        content_gap_score=content_gap_score,
                        recommended_action=recommended_action
                    )
                    
                    opportunities.append(opportunity)
            
            # Sort opportunities by potential value
            opportunities.sort(
                key=lambda x: (x.relevance_score * x.potential_traffic * x.content_gap_score) / max(x.difficulty, 0.1),
                reverse=True
            )
            
            return opportunities[:15]  # Return top 15 opportunities
            
        except Exception as e:
            logging.error(f"Error in keyword research: {e}")
            return []

    async def optimize_content_elements(self, content_data: Dict[str, Any],
                                      target_keywords: List[str]) -> Dict[str, Any]:
        """
        Optimize specific content elements for SEO.
        
        Args:
            content_data: Current content data
            target_keywords: Keywords to optimize for
            
        Returns:
            Optimized content recommendations
        """
        try:
            content_type = content_data.get('type', 'video')
            current_title = content_data.get('title', '')
            current_description = content_data.get('description', '')
            current_tags = content_data.get('tags', [])
            
            optimization_results = {
                "optimized_title": await self._optimize_title(current_title, target_keywords),
                "optimized_description": await self._optimize_description(
                    current_description, target_keywords, content_type
                ),
                "optimized_tags": self._optimize_tags(current_tags, target_keywords),
                "thumbnail_recommendations": self._generate_thumbnail_recommendations(
                    target_keywords, content_type
                ),
                "content_structure_recommendations": self._optimize_content_structure(
                    content_data, target_keywords
                ),
                "call_to_action_optimization": self._optimize_call_to_actions(
                    current_description, target_keywords
                )
            }
            
            # Add platform-specific optimizations
            if content_type == 'youtube_video':
                optimization_results.update({
                    "chapter_recommendations": self._generate_video_chapters(
                        content_data, target_keywords
                    ),
                    "end_screen_optimization": self._optimize_end_screens(target_keywords),
                    "card_recommendations": self._generate_card_recommendations(target_keywords)
                })
            elif content_type == 'tiktok_video':
                optimization_results.update({
                    "hashtag_optimization": self._optimize_tiktok_hashtags(target_keywords),
                    "trend_integration": await self._integrate_trending_elements(target_keywords)
                })
            
            # Calculate expected SEO improvement
            expected_improvement = self._calculate_expected_improvement(
                content_data, optimization_results
            )
            optimization_results["expected_seo_improvement"] = expected_improvement
            
            return optimization_results
            
        except Exception as e:
            logging.error(f"Error optimizing content elements: {e}")
            return {
                "error": "Content optimization failed",
                "recommendation": "Manual SEO optimization required"
            }

    async def monitor_seo_performance(self, creator_profile: Dict[str, Any],
                                    monitoring_period: str = "30_days") -> Dict[str, Any]:
        """
        Monitor SEO performance and track improvements over time.
        
        Args:
            creator_profile: Creator's profile and content portfolio
            monitoring_period: Period to analyze ("7_days", "30_days", "90_days")
            
        Returns:
            SEO performance monitoring report
        """
        try:
            content_portfolio = creator_profile.get('content_portfolio', [])
            
            monitoring_report = {
                "period": monitoring_period,
                "overall_seo_trend": "improving",  # improving, stable, declining
                "keyword_performance": {},
                "ranking_changes": {},
                "traffic_analysis": {},
                "content_performance": [],
                "recommendations": [],
                "competitor_movements": {}
            }
            
            # Analyze keyword performance trends
            for content in content_portfolio:
                content_keywords = content.get('target_keywords', [])
                for keyword in content_keywords:
                    current_ranking = await self._get_current_ranking(keyword, content.get('content_id'))
                    historical_ranking = await self._get_historical_ranking(
                        keyword, content.get('content_id'), monitoring_period
                    )
                    
                    ranking_change = current_ranking - historical_ranking if historical_ranking else 0
                    
                    monitoring_report["keyword_performance"][keyword] = {
                        "current_ranking": current_ranking,
                        "ranking_change": ranking_change,
                        "trend": "up" if ranking_change > 0 else "down" if ranking_change < 0 else "stable"
                    }
            
            # Analyze overall traffic trends
            monitoring_report["traffic_analysis"] = await self._analyze_traffic_trends(
                creator_profile, monitoring_period
            )
            
            # Identify top performing content
            top_performers = sorted(
                content_portfolio,
                key=lambda x: x.get('seo_score', 0) * x.get('organic_views', 0),
                reverse=True
            )[:5]
            
            for content in top_performers:
                monitoring_report["content_performance"].append({
                    "content_id": content.get('content_id'),
                    "title": content.get('title'),
                    "seo_score": content.get('seo_score', 0),
                    "organic_traffic": content.get('organic_views', 0),
                    "ranking_keywords": content.get('ranking_keywords', [])
                })
            
            # Generate recommendations based on performance
            monitoring_report["recommendations"] = self._generate_monitoring_recommendations(
                monitoring_report
            )
            
            # Analyze competitor movements
            monitoring_report["competitor_movements"] = await self._analyze_competitor_movements(
                creator_profile, monitoring_period
            )
            
            return monitoring_report
            
        except Exception as e:
            logging.error(f"Error in SEO performance monitoring: {e}")
            return {
                "error": "SEO monitoring failed",
                "period": monitoring_period,
                "recommendation": "Manual performance review required"
            }

    async def _analyze_keyword_optimization(self, title: str, description: str,
                                          tags: List[str]) -> Dict[str, Any]:
        """Analyze keyword optimization in content"""
        # Extract potential keywords
        text_content = f"{title} {description} {' '.join(tags)}".lower()
        
        # Simple keyword extraction (in production, use more sophisticated NLP)
        words = re.findall(r'\b\w+\b', text_content)
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Identify primary keywords (most frequent meaningful words)
        primary_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        primary_keywords = [kw[0] for kw in primary_keywords]
        
        # Calculate keyword optimization score
        title_keyword_presence = sum(1 for kw in primary_keywords if kw in title.lower()) / max(len(primary_keywords), 1)
        description_keyword_presence = sum(1 for kw in primary_keywords if kw in description.lower()) / max(len(primary_keywords), 1)
        tags_keyword_presence = sum(1 for kw in primary_keywords if any(kw in tag.lower() for tag in tags)) / max(len(primary_keywords), 1)
        
        keyword_score = (title_keyword_presence * 0.5 + description_keyword_presence * 0.3 + tags_keyword_presence * 0.2)
        
        # Score individual keywords
        keyword_scores = {}
        for keyword in primary_keywords:
            in_title = keyword in title.lower()
            in_description = keyword in description.lower()
            in_tags = any(keyword in tag.lower() for tag in tags)
            
            score = (in_title * 0.5 + in_description * 0.3 + in_tags * 0.2)
            keyword_scores[keyword] = score
        
        return {
            "score": keyword_score,
            "primary_keywords": primary_keywords,
            "keyword_scores": keyword_scores,
            "title_optimization": title_keyword_presence,
            "description_optimization": description_keyword_presence,
            "tags_optimization": tags_keyword_presence
        }

    def _analyze_content_structure(self, title: str, description: str) -> float:
        """Analyze content structure for SEO"""
        score = 0.0
        
        # Title analysis
        title_length = len(title)
        if 40 <= title_length <= 70:  # Optimal title length
            score += 0.25
        elif 30 <= title_length <= 80:  # Acceptable length
            score += 0.15
        
        # Title starts with keyword (assuming first word is important)
        if title and title[0].isupper():  # Proper capitalization
            score += 0.1
        
        # Description analysis
        desc_length = len(description)
        if desc_length >= 125:  # Minimum description length
            score += 0.2
            if desc_length >= 200:  # Good description length
                score += 0.1
        
        # Description structure (has call to action, links, etc.)
        if 'http' in description.lower():  # Has links
            score += 0.1
        if any(cta in description.lower() for cta in ['subscribe', 'like', 'comment', 'share']):
            score += 0.1
        
        # Paragraph structure (line breaks for readability)
        if description.count('\n') >= 2:  # Has paragraph breaks
            score += 0.1
        
        return min(score, 1.0)

    def _analyze_engagement_signals(self, performance_data: Dict[str, Any]) -> float:
        """Analyze engagement signals that affect SEO"""
        if not performance_data:
            return 0.5  # Default score
        
        views = performance_data.get('views', 0)
        likes = performance_data.get('likes', 0)
        comments = performance_data.get('comments', 0)
        shares = performance_data.get('shares', 0)
        watch_time = performance_data.get('avg_watch_time', 0)
        
        if views == 0:
            return 0.0
        
        # Calculate engagement metrics
        like_rate = likes / views
        comment_rate = comments / views
        share_rate = shares / views
        
        # Normalize scores (these are rough benchmarks)
        like_score = min(like_rate / 0.02, 1.0)    # 2% like rate is good
        comment_score = min(comment_rate / 0.005, 1.0)  # 0.5% comment rate is good
        share_score = min(share_rate / 0.001, 1.0)       # 0.1% share rate is good
        
        # Watch time score (if available)
        watch_time_score = 0.5
        if watch_time > 0:
            # Assume 60% watch time is good
            watch_time_score = min(watch_time / 60, 1.0)
        
        # Weighted average
        engagement_score = (like_score * 0.3 + comment_score * 0.3 + 
                          share_score * 0.2 + watch_time_score * 0.2)
        
        return engagement_score

    def _analyze_technical_factors(self, content_data: Dict[str, Any]) -> float:
        """Analyze technical SEO factors"""
        score = 0.0
        
        # Thumbnail quality
        if content_data.get('has_custom_thumbnail'):
            score += 0.3
        
        # Video quality
        video_quality = content_data.get('video_quality', 'standard')
        if video_quality in ['hd', '4k']:
            score += 0.2
        elif video_quality == 'standard':
            score += 0.1
        
        # Audio quality
        audio_quality = content_data.get('audio_quality', 'standard')
        if audio_quality == 'high':
            score += 0.1
        
        # Captions/subtitles
        if content_data.get('has_captions'):
            score += 0.2
        
        # Mobile optimization (assume good if recent upload)
        upload_date = content_data.get('upload_date')
        if upload_date:
            try:
                upload_datetime = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                if (datetime.now() - upload_datetime.replace(tzinfo=None)).days < 365:
                    score += 0.2  # Recent uploads are likely mobile optimized
            except:
                score += 0.1  # Default mobile score
        
        return min(score, 1.0)

    async def _analyze_competitive_positioning(self, keywords: List[str], 
                                             niche: str) -> Dict[str, Any]:
        """Analyze competitive positioning for keywords"""
        # Simulate competitive analysis
        # In production, this would query actual search results and competitor data
        
        competitor_analysis = {
            "score": 0.6,  # Default competitive position score
            "top_competitors": [
                {"name": f"Top {niche.title()} Creator", "ranking_strength": 0.9},
                {"name": f"{niche.title()} Expert", "ranking_strength": 0.8},
                {"name": f"Popular {niche.title()} Channel", "ranking_strength": 0.7}
            ],
            "keyword_competition": {},
            "content_gaps": [],
            "opportunities": []
        }
        
        for keyword in keywords[:3]:  # Analyze top 3 keywords
            # Simulate competition level
            competition_level = np.random.uniform(0.3, 0.9)
            competitor_analysis["keyword_competition"][keyword] = {
                "competition_level": competition_level,
                "ranking_difficulty": competition_level * 0.8 + 0.2,
                "content_saturation": competition_level
            }
        
        # Identify opportunities
        low_competition_keywords = [kw for kw, data in competitor_analysis["keyword_competition"].items() 
                                  if data["competition_level"] < 0.6]
        
        if low_competition_keywords:
            competitor_analysis["opportunities"].extend([
                f"Low competition opportunity: {kw}" for kw in low_competition_keywords[:2]
            ])
        
        competitor_analysis["opportunities"].extend([
            "Long-tail keyword variations",
            "Local/regional content opportunities",
            "Trending topic integration"
        ])
        
        return competitor_analysis

    def _identify_seo_opportunities(self, seo_scores: Dict[str, float],
                                  keyword_analysis: Dict[str, Any],
                                  competitive_analysis: Dict[str, Any]) -> List[str]:
        """Identify specific SEO optimization opportunities"""
        opportunities = []
        
        # Low-hanging fruit opportunities
        if seo_scores.get('keyword_optimization', 0) < 0.6:
            opportunities.append("Improve keyword optimization in titles and descriptions")
        
        if seo_scores.get('content_structure', 0) < 0.7:
            opportunities.append("Optimize content structure and formatting")
        
        if seo_scores.get('technical_factors', 0) < 0.8:
            opportunities.append("Address technical SEO issues (thumbnails, captions, quality)")
        
        # Keyword-specific opportunities
        if keyword_analysis.get('title_optimization', 0) < 0.5:
            opportunities.append("Include primary keywords in video titles")
        
        if keyword_analysis.get('tags_optimization', 0) < 0.6:
            opportunities.append("Optimize tags with relevant keywords")
        
        # Competitive opportunities
        comp_opportunities = competitive_analysis.get('opportunities', [])
        opportunities.extend(comp_opportunities[:2])  # Add top 2 competitive opportunities
        
        # Engagement opportunities
        if seo_scores.get('engagement_signals', 0) < 0.5:
            opportunities.append("Improve content engagement through better hooks and CTAs")
        
        return opportunities[:8]  # Return top 8 opportunities

    def _calculate_ranking_potential(self, seo_scores: Dict[str, float],
                                   performance_data: Dict[str, Any],
                                   competitive_analysis: Dict[str, Any]) -> float:
        """Calculate potential for ranking improvement"""
        # Base potential from current SEO score
        base_potential = 1.0 - sum(seo_scores.values()) / len(seo_scores)
        
        # Adjust for competitive landscape
        avg_competition = np.mean([
            data.get('competition_level', 0.5) 
            for data in competitive_analysis.get('keyword_competition', {}).values()
        ]) if competitive_analysis.get('keyword_competition') else 0.5
        
        competition_factor = 1.0 - avg_competition
        
        # Adjust for current performance
        views = performance_data.get('views', 0)
        performance_factor = min(views / 10000, 1.0)  # Views up to 10k give full performance factor
        
        # Calculate overall ranking potential
        ranking_potential = (base_potential * 0.5 + competition_factor * 0.3 + performance_factor * 0.2)
        
        return min(max(ranking_potential, 0.0), 1.0)

    def _identify_technical_issues(self, content_data: Dict[str, Any]) -> List[str]:
        """Identify technical SEO issues"""
        issues = []
        
        if not content_data.get('has_custom_thumbnail'):
            issues.append("Missing custom thumbnail")
        
        if not content_data.get('has_captions'):
            issues.append("Missing captions/subtitles for accessibility")
        
        video_quality = content_data.get('video_quality', 'standard')
        if video_quality not in ['hd', '4k']:
            issues.append("Video quality could be improved (HD/4K recommended)")
        
        description = content_data.get('description', '')
        if len(description) < 125:
            issues.append("Description too short (minimum 125 characters recommended)")
        
        if not content_data.get('tags'):
            issues.append("Missing or insufficient tags")
        
        # Check for mobile optimization indicators
        upload_date = content_data.get('upload_date')
        if upload_date:
            try:
                upload_datetime = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                if (datetime.now() - upload_datetime.replace(tzinfo=None)).days > 365:
                    issues.append("Content may need mobile optimization review")
            except:
                pass
        
        return issues

    def _generate_content_recommendations(self, keyword_analysis: Dict[str, Any],
                                        seo_scores: Dict[str, float],
                                        content_type: str) -> List[str]:
        """Generate specific content optimization recommendations"""
        recommendations = []
        
        primary_keywords = keyword_analysis.get('primary_keywords', [])
        
        if primary_keywords:
            recommendations.append(f"Focus content around primary keywords: {', '.join(primary_keywords[:3])}")
        
        if seo_scores.get('content_structure', 0) < 0.7:
            recommendations.extend([
                "Create clear content sections with descriptive headings",
                "Add compelling call-to-actions throughout the content",
                "Include relevant links and resources in description"
            ])
        
        if content_type == 'video':
            recommendations.extend([
                "Create engaging hook in first 15 seconds",
                "Use pattern interrupts to maintain viewer attention",
                "End with strong call-to-action for next video"
            ])
        
        # Keyword-specific recommendations
        if keyword_analysis.get('title_optimization', 0) < 0.6:
            recommendations.append("Include target keywords naturally in the title")
        
        if keyword_analysis.get('description_optimization', 0) < 0.6:
            recommendations.append("Expand description with keyword-rich, valuable content")
        
        return recommendations[:8]  # Return top 8 recommendations

    async def _generate_keyword_variations(self, topic: str, niche: str) -> List[str]:
        """Generate keyword variations for a topic"""
        base_variations = [
            topic,
            f"{topic} tutorial",
            f"how to {topic}",
            f"{topic} guide",
            f"{topic} tips",
            f"best {topic}",
            f"{topic} for beginners",
            f"{topic} explained",
            f"{niche} {topic}",
            f"{topic} {niche}"
        ]
        
        # Add niche-specific variations
        if niche == 'gaming':
            base_variations.extend([
                f"{topic} gameplay",
                f"{topic} review",
                f"{topic} walkthrough"
            ])
        elif niche == 'tech':
            base_variations.extend([
                f"{topic} review",
                f"{topic} unboxing",
                f"{topic} comparison"
            ])
        elif niche == 'education':
            base_variations.extend([
                f"{topic} course",
                f"learn {topic}",
                f"{topic} lesson"
            ])
        
        return base_variations[:12]  # Return top 12 variations

    async def _get_search_volume(self, keyword: str, niche: str) -> int:
        """Get estimated search volume for keyword"""
        # Simulate search volume estimation
        # In production, this would use actual search volume APIs
        
        base_volume = len(keyword.split()) * 1000  # Longer keywords = lower volume
        niche_multiplier = {
            'gaming': 2.0,
            'tech': 1.8,
            'lifestyle': 1.5,
            'education': 1.3,
            'music': 1.2,
            'fitness': 1.1
        }.get(niche, 1.0)
        
        # Add randomness to simulate real data
        volume = int(base_volume * niche_multiplier * np.random.uniform(0.5, 2.0))
        return max(volume, 100)  # Minimum volume

    async def _analyze_keyword_competition(self, keyword: str, niche: str) -> float:
        """Analyze competition level for keyword"""
        # Simulate competition analysis
        # In production, this would analyze actual SERP data
        
        word_count = len(keyword.split())
        
        # Longer keywords typically have less competition
        base_competition = max(0.1, 1.0 - (word_count - 1) * 0.2)
        
        # Add niche-based competition adjustment
        niche_competition = {
            'gaming': 0.8,
            'tech': 0.9,
            'lifestyle': 0.7,
            'education': 0.6,
            'music': 0.8,
            'fitness': 0.7
        }.get(niche, 0.6)
        
        competition = (base_competition + niche_competition) / 2
        return min(max(competition, 0.1), 1.0)

    def _calculate_keyword_difficulty(self, keyword: str, competition: float) -> float:
        """Calculate keyword ranking difficulty"""
        # Basic difficulty calculation
        word_count = len(keyword.split())
        
        # Shorter keywords are typically harder to rank for
        length_factor = max(0.3, 1.0 - (word_count - 1) * 0.15)
        
        # Combine with competition
        difficulty = (competition * 0.7 + length_factor * 0.3)
        
        return min(max(difficulty, 0.1), 1.0)

    def _calculate_keyword_relevance(self, keyword: str, creator_profile: Dict[str, Any]) -> float:
        """Calculate keyword relevance to creator's content"""
        niche = creator_profile.get('niche', 'general')
        content_themes = creator_profile.get('content_themes', [])
        
        relevance = 0.5  # Base relevance
        
        # Check if keyword relates to niche
        if niche.lower() in keyword.lower():
            relevance += 0.3
        
        # Check if keyword relates to content themes
        for theme in content_themes:
            if theme.lower() in keyword.lower():
                relevance += 0.2
                break
        
        return min(relevance, 1.0)

    def _estimate_potential_traffic(self, search_volume: int, competition: float, 
                                  authority_score: float) -> int:
        """Estimate potential traffic from ranking for keyword"""
        # Click-through rates by position (simplified)
        ctr_by_position = {1: 0.32, 2: 0.24, 3: 0.18, 4: 0.12, 5: 0.09}
        
        # Estimate ranking position based on competition and authority
        estimated_position = max(1, int(5 * competition / max(authority_score, 0.1)))
        estimated_position = min(estimated_position, 5)
        
        # Calculate potential traffic
        ctr = ctr_by_position.get(estimated_position, 0.05)
        potential_traffic = int(search_volume * ctr * 0.1)  # Conservative estimate
        
        return max(potential_traffic, 10)  # Minimum traffic estimate

    async def _analyze_content_gap(self, keyword: str, creator_profile: Dict[str, Any]) -> float:
        """Analyze content gap for keyword opportunity"""
        existing_content = creator_profile.get('content_portfolio', [])
        
        # Check if creator already has content targeting this keyword
        for content in existing_content:
            content_keywords = content.get('target_keywords', [])
            if keyword.lower() in [kw.lower() for kw in content_keywords]:
                return 0.2  # Low gap score if already covered
        
        # Check if keyword aligns with creator's content strategy
        niche = creator_profile.get('niche', 'general')
        content_types = creator_profile.get('preferred_content_types', [])
        
        gap_score = 0.8  # High gap score by default
        
        # Reduce score if keyword doesn't align well with niche
        if niche.lower() not in keyword.lower() and keyword.lower() not in niche.lower():
            gap_score -= 0.2
        
        return gap_score

    def _determine_keyword_action(self, difficulty: float, relevance: float,
                                content_gap: float, potential_traffic: int) -> str:
        """Determine recommended action for keyword"""
        score = (relevance * 0.4 + content_gap * 0.3 + 
                (1 - difficulty) * 0.2 + min(potential_traffic / 1000, 1) * 0.1)
        
        if score > 0.8 and difficulty < 0.6:
            return "High priority - create content immediately"
        elif score > 0.6 and difficulty < 0.8:
            return "Medium priority - plan content for next month"
        elif score > 0.4:
            return "Long-term target - build authority first"
        else:
            return "Low priority - consider alternative keywords"

    async def _optimize_title(self, current_title: str, target_keywords: List[str]) -> str:
        """Optimize title for SEO"""
        if not target_keywords:
            return current_title
        
        primary_keyword = target_keywords[0]
        
        # If title already contains primary keyword, return as is
        if primary_keyword.lower() in current_title.lower():
            return current_title
        
        # Try to naturally integrate primary keyword
        if len(current_title) + len(primary_keyword) + 3 <= 70:  # YouTube title limit
            # Add keyword at the beginning if it makes sense
            if current_title.lower().startswith(('how', 'what', 'why', 'when', 'where')):
                return f"{current_title} - {primary_keyword.title()}"
            else:
                return f"{primary_keyword.title()}: {current_title}"
        
        return current_title  # Return original if can't optimize without exceeding limits

    async def _optimize_description(self, current_description: str, 
                                  target_keywords: List[str], content_type: str) -> str:
        """Optimize description for SEO"""
        if not target_keywords:
            return current_description
        
        optimized_desc = current_description
        
        # Add keyword-rich opening if description is too short
        if len(current_description) < 125:
            keyword_intro = f"In this {content_type}, we explore {target_keywords[0]} and related topics. "
            optimized_desc = keyword_intro + current_description
        
        # Ensure primary keywords appear in description
        for keyword in target_keywords[:3]:  # Top 3 keywords
            if keyword.lower() not in optimized_desc.lower():
                optimized_desc += f"\n\nLearn more about {keyword} and discover advanced techniques."
        
        # Add call-to-action if missing
        cta_phrases = ['subscribe', 'like', 'comment', 'share']
        if not any(phrase in optimized_desc.lower() for phrase in cta_phrases):
            optimized_desc += "\n\n👍 Like this video and subscribe for more content!"
        
        return optimized_desc

    def _optimize_tags(self, current_tags: List[str], target_keywords: List[str]) -> List[str]:
        """Optimize tags for SEO"""
        optimized_tags = current_tags.copy()
        
        # Add target keywords as tags if not already present
        for keyword in target_keywords:
            if keyword not in optimized_tags:
                optimized_tags.append(keyword)
        
        # Generate related tags
        for keyword in target_keywords[:2]:  # Top 2 keywords
            keyword_variations = [
                f"{keyword} tutorial",
                f"how to {keyword}",
                f"{keyword} guide"
            ]
            
            for variation in keyword_variations:
                if len(optimized_tags) < 15 and variation not in optimized_tags:  # YouTube tag limit
                    optimized_tags.append(variation)
        
        return optimized_tags[:15]  # YouTube allows up to 15 tags

    def _generate_thumbnail_recommendations(self, target_keywords: List[str], 
                                          content_type: str) -> List[str]:
        """Generate thumbnail optimization recommendations"""
        recommendations = []
        
        if target_keywords:
            primary_keyword = target_keywords[0]
            recommendations.append(f"Include text overlay with '{primary_keyword.title()}'")
        
        recommendations.extend([
            "Use high contrast colors (bright background, dark text or vice versa)",
            "Include human face with emotional expression if applicable",
            "Keep text large and readable on mobile devices",
            "Use consistent branding elements (colors, fonts, style)",
            "Create curiosity with before/after or comparison elements",
            "Ensure thumbnail is clear and recognizable at small sizes"
        ])
        
        return recommendations[:5]

    def _optimize_content_structure(self, content_data: Dict[str, Any], 
                                  target_keywords: List[str]) -> List[str]:
        """Optimize content structure recommendations"""
        recommendations = []
        
        content_type = content_data.get('type', 'video')
        
        if content_type == 'video':
            recommendations.extend([
                "Start with hook mentioning primary keyword within first 15 seconds",
                "Create clear sections/chapters with keyword-rich titles",
                "Include keyword naturally 2-3 times throughout content",
                "End with keyword-focused summary and call-to-action"
            ])
        
        recommendations.extend([
            "Structure content with clear beginning, middle, and end",
            "Use pattern interrupts every 2-3 minutes to maintain attention",
            "Include visual elements that reinforce keyword topics",
            "Add interactive elements (polls, questions) related to keywords"
        ])
        
        return recommendations

    def _optimize_call_to_actions(self, current_description: str, 
                                target_keywords: List[str]) -> List[str]:
        """Optimize call-to-action recommendations"""
        cta_recommendations = []
        
        if target_keywords:
            primary_keyword = target_keywords[0]
            cta_recommendations.extend([
                f"Subscribe for more {primary_keyword} content",
                f"Comment your {primary_keyword} questions below",
                f"Share if this {primary_keyword} guide helped you"
            ])
        
        # Check what's missing from current description
        if 'subscribe' not in current_description.lower():
            cta_recommendations.append("Add subscribe call-to-action")
        
        if 'like' not in current_description.lower():
            cta_recommendations.append("Include like request")
        
        if 'comment' not in current_description.lower():
            cta_recommendations.append("Encourage comments with specific question")
        
        return cta_recommendations[:5]

    def _generate_video_chapters(self, content_data: Dict[str, Any], 
                               target_keywords: List[str]) -> List[str]:
        """Generate video chapter recommendations"""
        chapters = []
        
        duration = content_data.get('duration', 600)  # Default 10 minutes
        
        if target_keywords:
            primary_keyword = target_keywords[0]
            chapters.extend([
                f"0:00 - Introduction to {primary_keyword.title()}",
                f"{int(duration*0.2)//60}:{int(duration*0.2)%60:02d} - {primary_keyword.title()} Basics",
                f"{int(duration*0.5)//60}:{int(duration*0.5)%60:02d} - Advanced {primary_keyword.title()} Techniques",
                f"{int(duration*0.8)//60}:{int(duration*0.8)%60:02d} - {primary_keyword.title()} Examples",
                f"{int(duration*0.95)//60}:{int(duration*0.95)%60:02d} - Summary & Next Steps"
            ])
        
        return chapters

    def _optimize_end_screens(self, target_keywords: List[str]) -> List[str]:
        """Optimize end screen recommendations"""
        recommendations = []
        
        if target_keywords:
            primary_keyword = target_keywords[0]
            recommendations.extend([
                f"Feature related {primary_keyword} videos",
                f"Promote {primary_keyword} playlist"
            ])
        
        recommendations.extend([
            "Include subscribe button with notification bell reminder",
            "Feature most popular related video",
            "Promote relevant playlist for binge-watching"
        ])
        
        return recommendations

    def _generate_card_recommendations(self, target_keywords: List[str]) -> List[str]:
        """Generate video card recommendations"""
        recommendations = []
        
        if target_keywords:
            recommendations.append(f"Add cards to related {target_keywords[0]} content at relevant moments")
        
        recommendations.extend([
            "Use polls cards to increase engagement",
            "Add video cards at natural transition points",
            "Include link cards to relevant external resources"
        ])
        
        return recommendations

    def _optimize_tiktok_hashtags(self, target_keywords: List[str]) -> List[str]:
        """Optimize TikTok hashtags"""
        hashtags = []
        
        for keyword in target_keywords[:3]:
            # Convert to hashtag format
            hashtag = "#" + keyword.replace(" ", "").lower()
            hashtags.append(hashtag)
        
        # Add trending TikTok hashtags
        hashtags.extend([
            "#fyp", "#viral", "#trending", "#educational", "#tutorial"
        ])
        
        return hashtags[:10]  # TikTok optimal hashtag count

    async def _integrate_trending_elements(self, target_keywords: List[str]) -> List[str]:
        """Integrate trending elements for better discoverability"""
        trending_elements = []
        
        # Simulate trending elements
        trending_elements.extend([
            "Use trending audio/music in background",
            "Incorporate popular visual effects or filters",
            "Reference current events or viral memes appropriately",
            "Use trending hashtags alongside keyword hashtags"
        ])
        
        if target_keywords:
            trending_elements.append(f"Create trending challenge related to {target_keywords[0]}")
        
        return trending_elements

    def _calculate_expected_improvement(self, content_data: Dict[str, Any],
                                      optimization_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate expected SEO improvement from optimizations"""
        current_seo_score = content_data.get('seo_score', 0.5)
        
        # Estimate improvement based on optimizations
        improvement_factors = {
            "title_optimization": 0.15,
            "description_optimization": 0.12,
            "tags_optimization": 0.08,
            "structure_optimization": 0.10,
            "technical_improvements": 0.05
        }
        
        total_improvement = sum(improvement_factors.values())
        expected_new_score = min(current_seo_score + total_improvement, 1.0)
        
        return {
            "current_score": current_seo_score,
            "expected_score": expected_new_score,
            "improvement_percentage": (expected_new_score - current_seo_score) / current_seo_score * 100,
            "ranking_improvement_estimate": "15-25% increase in organic visibility"
        }

    async def _get_current_ranking(self, keyword: str, content_id: str) -> int:
        """Get current ranking position for keyword"""
        # Simulate ranking data
        # In production, this would query actual search results
        return np.random.randint(1, 20)  # Random ranking between 1-20

    async def _get_historical_ranking(self, keyword: str, content_id: str, period: str) -> int:
        """Get historical ranking for comparison"""
        # Simulate historical data
        current_ranking = await self._get_current_ranking(keyword, content_id)
        # Add some variation for historical data
        return current_ranking + np.random.randint(-3, 4)

    async def _analyze_traffic_trends(self, creator_profile: Dict[str, Any],
                                    period: str) -> Dict[str, Any]:
        """Analyze traffic trends over period"""
        # Simulate traffic analysis
        return {
            "organic_traffic_change": np.random.uniform(-0.2, 0.3),  # -20% to +30%
            "search_impressions_change": np.random.uniform(-0.1, 0.4),
            "click_through_rate_change": np.random.uniform(-0.05, 0.15),
            "average_position_change": np.random.uniform(-2, 3),
            "top_performing_keywords": ["keyword1", "keyword2", "keyword3"]
        }

    def _generate_monitoring_recommendations(self, monitoring_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on monitoring results"""
        recommendations = []
        
        keyword_performance = monitoring_report.get("keyword_performance", {})
        declining_keywords = [kw for kw, data in keyword_performance.items() 
                            if data.get("trend") == "down"]
        
        if declining_keywords:
            recommendations.append(f"Optimize content for declining keywords: {', '.join(declining_keywords[:3])}")
        
        traffic_analysis = monitoring_report.get("traffic_analysis", {})
        traffic_change = traffic_analysis.get("organic_traffic_change", 0)
        
        if traffic_change < -0.1:  # More than 10% decline
            recommendations.append("Investigate and address organic traffic decline")
        elif traffic_change > 0.2:  # More than 20% growth
            recommendations.append("Scale successful content strategies that drove traffic growth")
        
        recommendations.extend([
            "Continue monitoring keyword rankings weekly",
            "Analyze top-performing content for replication strategies",
            "Update older content with current SEO best practices"
        ])
        
        return recommendations

    async def _analyze_competitor_movements(self, creator_profile: Dict[str, Any],
                                          period: str) -> Dict[str, Any]:
        """Analyze competitor SEO movements"""
        # Simulate competitor analysis
        return {
            "new_competitors_identified": 2,
            "competitor_ranking_changes": {
                "competitor_1": "moved_up_3_positions",
                "competitor_2": "moved_down_1_position"
            },
            "competitor_content_strategies": [
                "Increased long-form content production",
                "Focus on trending keywords",
                "Improved video thumbnails and titles"
            ],
            "opportunities_from_competitor_gaps": [
                "Untapped keyword: advanced tutorials",
                "Content format gap: short-form explanations"
            ]
        }
