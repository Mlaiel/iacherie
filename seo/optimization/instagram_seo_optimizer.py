"""
Instagram SEO Optimizer for Ainflue Platform
============================================

Advanced Instagram optimization for content discovery and engagement.
Optimizes content for Instagram's algorithm and search functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import hashlib
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class InstagramContentType(Enum):
    """Instagram content types."""
    POST = "post"
    REEL = "reel"
    STORY = "story"
    IGTV = "igtv"
    LIVE = "live"
    CAROUSEL = "carousel"
    VIDEO = "video"

class InstagramAudience(Enum):
    """Instagram audience categories."""
    MILLENNIALS = "millennials"
    GEN_Z = "gen_z"
    PARENTS = "parents"
    CREATORS = "creators"
    BUSINESSES = "businesses"
    ARTISTS = "artists"
    INFLUENCERS = "influencers"

class ContentPillar(Enum):
    """Instagram content pillars."""
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    BEHIND_SCENES = "behind_scenes"
    USER_GENERATED = "user_generated"

@dataclass
class InstagramHashtagAnalysis:
    """Instagram hashtag analysis result."""
    hashtag: str
    posts_count: int
    engagement_rate: float
    difficulty_score: float
    reach_potential: int
    trending_status: str
    related_hashtags: List[str]
    best_post_times: List[str]
    audience_demographics: Dict[str, float]
    competition_level: str
    growth_trend: str

@dataclass
class InstagramContentOptimization:
    """Instagram content optimization result."""
    optimization_id: str
    content_id: str
    content_type: InstagramContentType
    optimized_caption: str
    optimized_hashtags: List[str]
    alt_text_suggestions: List[str]
    posting_schedule: Dict[str, str]
    engagement_predictions: Dict[str, float]
    reach_estimate: int
    content_score: float
    optimization_tips: List[str]
    created_at: datetime

class InstagramSEOOptimizer:
    """
    Advanced Instagram SEO Optimizer
    
    Features:
    - Hashtag research and optimization
    - Caption optimization for discovery
    - Alt text generation for accessibility
    - Content timing optimization
    - Audience targeting strategies
    - Reel optimization for viral potential
    - Story optimization for engagement
    - IGTV optimization for long-form content
    """
    
    def __init__(self, db_pool=None) -> None:
        self.db_pool = db_pool
        
        # Instagram-specific optimization data
        self.hashtag_categories = self._load_hashtag_categories()
        self.engagement_factors = self._load_engagement_factors()
        self.viral_patterns = self._load_viral_patterns()
        
    def _load_hashtag_categories(self) -> Dict[str, List[str]]:
        """Load Instagram hashtag categories."""
        return {
            'fitness': [
                'fitness', 'workout', 'gym', 'health', 'fitnessmotivation',
                'exercise', 'training', 'muscle', 'cardio', 'strength'
            ],
            'fashion': [
                'fashion', 'style', 'outfit', 'ootd', 'fashionista',
                'trendy', 'fashionblogger', 'styleinspo', 'look', 'clothing'
            ],
            'food': [
                'food', 'foodie', 'cooking', 'recipe', 'foodlover',
                'chef', 'delicious', 'yummy', 'foodporn', 'instafood'
            ],
            'travel': [
                'travel', 'wanderlust', 'explore', 'adventure', 'vacation',
                'travelgram', 'instatravel', 'travelblogger', 'trip', 'journey'
            ],
            'photography': [
                'photography', 'photo', 'photographer', 'photoshoot',
                'portrait', 'landscape', 'art', 'creative', 'beautiful', 'capture'
            ],
            'business': [
                'business', 'entrepreneur', 'marketing', 'success',
                'motivation', 'hustle', 'growth', 'leadership', 'innovation', 'startup'
            ]
        }
    
    def _load_engagement_factors(self) -> Dict[str, float]:
        """Load Instagram engagement factors and weights."""
        return {
            'likes': 0.25,
            'comments': 0.30,
            'shares': 0.20,
            'saves': 0.15,
            'reach': 0.10
        }
    
    def _load_viral_patterns(self) -> Dict[str, List[str]]:
        """Load viral content patterns for Instagram."""
        return {
            'hook_phrases': [
                'Swipe to see', 'Wait for it', 'This changed everything',
                'You need to save this', 'Screenshot this', 'Tag someone who',
                'Here\'s what nobody tells you', 'Plot twist'
            ],
            'call_to_actions': [
                'Save this post', 'Share with friends', 'Tag someone',
                'Follow for more', 'Comment below', 'DM for details',
                'Link in bio', 'Swipe for more'
            ],
            'trending_formats': [
                'Before & After', 'Step by step', 'Behind the scenes',
                'Day in my life', 'Get ready with me', 'Tutorial',
                'Transformation', 'Tips & tricks'
            ]
        }
    
    def optimize_instagram_content(
        self,
        content_id: str,
        caption: str,
        content_type: InstagramContentType,
        target_audience: InstagramAudience,
        niche: str,
        images: Optional[List[str]] = None
    ) -> InstagramContentOptimization:
        """
        Optimize content for Instagram discovery and engagement.
        
        Args:
            content_id: Content identifier
            caption: Original caption
            content_type: Type of Instagram content
            target_audience: Target audience
            niche: Content niche
            images: List of image descriptions for alt text
            
        Returns:
            InstagramContentOptimization object
        """
        try:
            optimization_id = f"ig_opt_{content_id}_{int(datetime.utcnow().timestamp())}"
            
            # Research optimal hashtags
            optimized_hashtags = self._research_instagram_hashtags(
                niche, target_audience, content_type
            )
            
            # Optimize caption
            optimized_caption = self._optimize_instagram_caption(
                caption, optimized_hashtags, content_type, target_audience
            )
            
            # Generate alt text suggestions
            alt_text_suggestions = []
            if images:
                alt_text_suggestions = self._generate_alt_text_suggestions(images, niche)
            
            # Calculate optimal posting schedule
            posting_schedule = self._calculate_optimal_posting_time(
                target_audience, content_type
            )
            
            # Predict engagement metrics
            engagement_predictions = self._predict_instagram_engagement(
                optimized_caption, optimized_hashtags, content_type, target_audience
            )
            
            # Estimate reach
            reach_estimate = self._estimate_content_reach(
                optimized_hashtags, content_type, engagement_predictions
            )
            
            # Calculate content score
            content_score = self._calculate_content_score(
                optimized_caption, optimized_hashtags, content_type, engagement_predictions
            )
            
            # Generate optimization tips
            optimization_tips = self._generate_instagram_optimization_tips(
                caption, optimized_caption, content_type, content_score
            )
            
            optimization = InstagramContentOptimization(
                optimization_id=optimization_id,
                content_id=content_id,
                content_type=content_type,
                optimized_caption=optimized_caption,
                optimized_hashtags=optimized_hashtags,
                alt_text_suggestions=alt_text_suggestions,
                posting_schedule=posting_schedule,
                engagement_predictions=engagement_predictions,
                reach_estimate=reach_estimate,
                content_score=content_score,
                optimization_tips=optimization_tips,
                created_at=datetime.utcnow()
            )
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing Instagram content: {e}")
            raise
    
    def research_instagram_hashtags(
        self,
        seed_keywords: List[str],
        niche: str,
        target_audience: InstagramAudience,
        analysis_depth: str = "standard"
    ) -> List[InstagramHashtagAnalysis]:
        """
        Research optimal hashtags for Instagram content.
        
        Args:
            seed_keywords: Base keywords to expand
            niche: Content niche
            target_audience: Target audience
            analysis_depth: Depth of analysis
            
        Returns:
            List of InstagramHashtagAnalysis objects
        """
        try:
            hashtag_analyses = []
            
            # Generate hashtag variations
            hashtag_variations = self._generate_hashtag_variations(
                seed_keywords, niche, target_audience
            )
            
            for hashtag in hashtag_variations:
                # Simulate hashtag metrics (would use real Instagram API in production)
                posts_count = self._simulate_posts_count(hashtag, niche)
                engagement_rate = self._simulate_engagement_rate(hashtag, target_audience)
                difficulty_score = self._calculate_hashtag_difficulty(posts_count, engagement_rate)
                reach_potential = self._calculate_reach_potential(posts_count, engagement_rate)
                trending_status = self._determine_trending_status(hashtag, niche)
                
                # Find related hashtags
                related_hashtags = self._find_related_hashtags(hashtag, niche)
                
                # Determine best posting times
                best_post_times = self._get_optimal_posting_times(target_audience)
                
                # Analyze audience demographics
                audience_demographics = self._analyze_hashtag_audience(hashtag, target_audience)
                
                # Assess competition level
                competition_level = self._assess_competition_level(difficulty_score, posts_count)
                
                # Determine growth trend
                growth_trend = self._analyze_growth_trend(hashtag, niche)
                
                analysis = InstagramHashtagAnalysis(
                    hashtag=hashtag,
                    posts_count=posts_count,
                    engagement_rate=engagement_rate,
                    difficulty_score=difficulty_score,
                    reach_potential=reach_potential,
                    trending_status=trending_status,
                    related_hashtags=related_hashtags,
                    best_post_times=best_post_times,
                    audience_demographics=audience_demographics,
                    competition_level=competition_level,
                    growth_trend=growth_trend
                )
                
                hashtag_analyses.append(analysis)
            
            # Sort by optimization potential
            hashtag_analyses.sort(
                key=lambda h: h.reach_potential * h.engagement_rate / max(h.difficulty_score, 0.1),
                reverse=True
            )
            
            return hashtag_analyses[:30]  # Return top 30 hashtags
            
        except Exception as e:
            logger.error(f"Error researching Instagram hashtags: {e}")
            return []
    
    def _research_instagram_hashtags(
        self,
        niche: str,
        target_audience: InstagramAudience,
        content_type: InstagramContentType
    ) -> List[str]:
        """Research optimal hashtags for specific content."""
        # Get niche-specific hashtags
        niche_hashtags = self.hashtag_categories.get(niche.lower(), [niche.lower()])
        
        # Add audience-specific hashtags
        audience_hashtags = self._get_audience_hashtags(target_audience)
        
        # Add content type hashtags
        content_type_hashtags = self._get_content_type_hashtags(content_type)
        
        # Combine and select best hashtags
        all_hashtags = niche_hashtags + audience_hashtags + content_type_hashtags
        
        # Remove duplicates and limit to Instagram's 30 hashtag limit
        unique_hashtags = list(set(all_hashtags))
        
        # Return optimized selection (mix of high, medium, and low competition)
        return self._select_optimal_hashtag_mix(unique_hashtags)[:30]
    
    def _get_audience_hashtags(self, audience: InstagramAudience) -> List[str]:
        """Get hashtags targeting specific audience."""
        audience_maps = {
            InstagramAudience.MILLENNIALS: ['millennials', 'adulting', 'nostalgia', '90skid'],
            InstagramAudience.GEN_Z: ['genz', 'viral', 'trending', 'aesthetic', 'mood'],
            InstagramAudience.PARENTS: ['parenting', 'momlife', 'dadlife', 'family', 'kids'],
            InstagramAudience.CREATORS: ['creator', 'contentcreator', 'creative', 'artist'],
            InstagramAudience.BUSINESSES: ['business', 'entrepreneur', 'smallbusiness', 'marketing'],
            InstagramAudience.ARTISTS: ['art', 'artist', 'creative', 'artwork', 'design'],
            InstagramAudience.INFLUENCERS: ['influencer', 'lifestyle', 'inspiration', 'motivation']
        }
        
        return audience_maps.get(audience, ['lifestyle', 'inspiration'])
    
    def _get_content_type_hashtags(self, content_type: InstagramContentType) -> List[str]:
        """Get hashtags specific to content type."""
        type_maps = {
            InstagramContentType.REEL: ['reels', 'reelsinstagram', 'viral', 'trending'],
            InstagramContentType.STORY: ['stories', 'instastory', 'behindthescenes'],
            InstagramContentType.IGTV: ['igtv', 'longform', 'video', 'tutorial'],
            InstagramContentType.CAROUSEL: ['carousel', 'swipe', 'photoset'],
            InstagramContentType.POST: ['post', 'instagram', 'content'],
            InstagramContentType.LIVE: ['live', 'golive', 'livestream']
        }
        
        return type_maps.get(content_type, ['instagram', 'content'])
    
    def _optimize_instagram_caption(
        self,
        caption: str,
        hashtags: List[str],
        content_type: InstagramContentType,
        target_audience: InstagramAudience
    ) -> str:
        """Optimize caption for Instagram engagement."""
        # Add hook if not present
        if not any(hook in caption for hook in self.viral_patterns['hook_phrases']):
            hook = self._select_appropriate_hook(content_type, target_audience)
            caption = f"{hook} {caption}"
        
        # Add call-to-action if not present
        if not any(cta in caption.lower() for cta in 
                   [phrase.lower() for phrase in self.viral_patterns['call_to_actions']]):
            cta = self._select_appropriate_cta(content_type, target_audience)
            caption = f"{caption}\n\n{cta}"
        
        # Add line breaks for readability
        caption = self._format_caption_for_readability(caption)
        
        # Add hashtags
        hashtag_string = ' '.join([f'#{tag}' for tag in hashtags])
        optimized_caption = f"{caption}\n\n{hashtag_string}"
        
        return optimized_caption
    
    def _select_appropriate_hook(
        self,
        content_type: InstagramContentType,
        target_audience: InstagramAudience
    ) -> str:
        """Select appropriate hook for content."""
        hooks_by_type = {
            InstagramContentType.REEL: ['Wait for it', 'Swipe to see', 'You need to save this'],
            InstagramContentType.CAROUSEL: ['Swipe to see', 'Screenshot this', 'Save this post'],
            InstagramContentType.STORY: ['Swipe up', 'Tag someone who', 'DM me if']
        }
        
        hooks = hooks_by_type.get(content_type, self.viral_patterns['hook_phrases'])
        return hooks[0] if hooks else "Check this out:"
    
    def _select_appropriate_cta(
        self,
        content_type: InstagramContentType,
        target_audience: InstagramAudience
    ) -> str:
        """Select appropriate call-to-action."""
        ctas_by_audience = {
            InstagramAudience.CREATORS: ['Save this for later', 'Share with fellow creators'],
            InstagramAudience.BUSINESSES: ['Follow for business tips', 'Share with your team'],
            InstagramAudience.ARTISTS: ['Tag an artist friend', 'Save for inspiration']
        }
        
        ctas = ctas_by_audience.get(target_audience, self.viral_patterns['call_to_actions'])
        return ctas[0] if ctas else "Follow for more!"
    
    def _format_caption_for_readability(self, caption: str) -> str:
        """Format caption for better readability."""
        # Add line breaks every 2-3 sentences
        sentences = caption.split('. ')
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            formatted_sentences.append(sentence)
            if (i + 1) % 2 == 0 and i < len(sentences) - 1:
                formatted_sentences.append('\n')
        
        return '. '.join(formatted_sentences)
    
    def _generate_alt_text_suggestions(
        self,
        images: List[str],
        niche: str
    ) -> List[str]:
        """Generate alt text suggestions for accessibility."""
        alt_texts = []
        
        for i, image_desc in enumerate(images):
            # Create descriptive alt text
            alt_text = f"Image {i+1}: {image_desc}"
            
            # Add context based on niche
            if niche.lower() == 'fashion':
                alt_text += " - Fashion and style content"
            elif niche.lower() == 'food':
                alt_text += " - Food and cooking content"
            elif niche.lower() == 'fitness':
                alt_text += " - Fitness and wellness content"
            
            alt_texts.append(alt_text)
        
        return alt_texts
    
    def _calculate_optimal_posting_time(
        self,
        target_audience: InstagramAudience,
        content_type: InstagramContentType
    ) -> Dict[str, str]:
        """Calculate optimal posting schedule."""
        # Base posting times by audience
        audience_times = {
            InstagramAudience.MILLENNIALS: {'weekday': '11:00-13:00', 'weekend': '10:00-12:00'},
            InstagramAudience.GEN_Z: {'weekday': '19:00-21:00', 'weekend': '14:00-16:00'},
            InstagramAudience.PARENTS: {'weekday': '08:00-10:00', 'weekend': '09:00-11:00'},
            InstagramAudience.BUSINESSES: {'weekday': '09:00-11:00', 'weekend': '10:00-12:00'},
            InstagramAudience.CREATORS: {'weekday': '15:00-17:00', 'weekend': '13:00-15:00'},
            InstagramAudience.ARTISTS: {'weekday': '16:00-18:00', 'weekend': '14:00-16:00'}
        }
        
        # Adjust for content type
        base_times = audience_times.get(target_audience, {'weekday': '11:00-13:00', 'weekend': '10:00-12:00'})
        
        if content_type == InstagramContentType.REEL:
            # Reels perform better in evening
            base_times['weekday'] = '18:00-20:00'
            base_times['weekend'] = '19:00-21:00'
        elif content_type == InstagramContentType.STORY:
            # Stories perform well throughout the day
            base_times['weekday'] = '10:00-22:00'
            base_times['weekend'] = '09:00-23:00'
        
        return base_times
    
    def _predict_instagram_engagement(
        self,
        caption: str,
        hashtags: List[str],
        content_type: InstagramContentType,
        target_audience: InstagramAudience
    ) -> Dict[str, float]:
        """Predict engagement metrics."""
        # Base engagement rates by content type
        base_rates = {
            InstagramContentType.REEL: {'likes': 5.2, 'comments': 0.8, 'shares': 1.1, 'saves': 0.6},
            InstagramContentType.POST: {'likes': 3.5, 'comments': 0.5, 'shares': 0.3, 'saves': 0.4},
            InstagramContentType.CAROUSEL: {'likes': 4.1, 'comments': 0.7, 'shares': 0.5, 'saves': 0.8},
            InstagramContentType.STORY: {'likes': 2.8, 'comments': 0.3, 'shares': 0.9, 'saves': 0.2}
        }
        
        base_engagement = base_rates.get(content_type, base_rates[InstagramContentType.POST])
        
        # Apply multipliers based on optimization
        multiplier = 1.0
        
        # Caption optimization bonus
        if any(hook in caption for hook in self.viral_patterns['hook_phrases']):
            multiplier += 0.2
        
        if any(cta in caption for cta in self.viral_patterns['call_to_actions']):
            multiplier += 0.15
        
        # Hashtag optimization bonus
        if len(hashtags) >= 10:
            multiplier += 0.1
        if len(hashtags) >= 20:
            multiplier += 0.1
        
        # Apply multiplier
        predicted_engagement = {}
        for metric, rate in base_engagement.items():
            predicted_engagement[metric] = rate * multiplier
        
        return predicted_engagement
    
    def _calculate_content_score(
        self,
        caption: str,
        hashtags: List[str],
        content_type: InstagramContentType,
        engagement_predictions: Dict[str, float]
    ) -> float:
        """Calculate overall content optimization score."""
        score = 0.0
        
        # Caption score (30%)
        caption_score = 0
        if any(hook in caption for hook in self.viral_patterns['hook_phrases']):
            caption_score += 10
        if any(cta in caption for cta in self.viral_patterns['call_to_actions']):
            caption_score += 10
        if 50 <= len(caption.split()) <= 150:  # Optimal caption length
            caption_score += 10
        
        score += caption_score * 0.3
        
        # Hashtag score (25%)
        hashtag_score = min(len(hashtags) * 2, 30)  # Up to 30 hashtags
        score += hashtag_score * 0.25
        
        # Content type optimization (20%)
        content_type_scores = {
            InstagramContentType.REEL: 25,
            InstagramContentType.CAROUSEL: 23,
            InstagramContentType.POST: 20,
            InstagramContentType.STORY: 18
        }
        score += content_type_scores.get(content_type, 15) * 0.20
        
        # Engagement prediction score (25%)
        avg_engagement = sum(engagement_predictions.values()) / len(engagement_predictions)
        score += avg_engagement * 5 * 0.25  # Scale to 0-25 range
        
        return min(score, 100.0)
    
    def _select_optimal_hashtag_mix(self, hashtags: List[str]) -> List[str]:
        """Select optimal mix of high, medium, and low competition hashtags."""
        # Simulate competition levels
        high_competition = hashtags[:5]  # Popular hashtags
        medium_competition = hashtags[5:15]  # Moderately popular
        low_competition = hashtags[15:25]  # Niche hashtags
        
        # Optimal mix: 30% high, 50% medium, 20% low competition
        optimal_mix = (
            high_competition[:2] +  # 2 high competition
            medium_competition[:5] +  # 5 medium competition  
            low_competition[:3]  # 3 low competition
        )
        
        return optimal_mix
    
    def _simulate_posts_count(self, hashtag: str, niche: str) -> int:
        """Simulate posts count for hashtag (would use real API in production)."""
        # Generate realistic posts count based on hashtag
        base_count = len(hashtag) * 1000
        niche_modifier = 1.5 if niche.lower() in ['fashion', 'food', 'fitness'] else 1.0
        return int(base_count * niche_modifier)
    
    def _simulate_engagement_rate(self, hashtag: str, audience: InstagramAudience) -> float:
        """Simulate engagement rate for hashtag."""
        # Base engagement rate between 1-8%
        base_rate = 2.0 + (hash(hashtag) % 6)
        
        # Audience modifier
        audience_modifiers = {
            InstagramAudience.GEN_Z: 1.2,
            InstagramAudience.CREATORS: 1.1,
            InstagramAudience.ARTISTS: 1.15,
            InstagramAudience.MILLENNIALS: 1.0,
            InstagramAudience.BUSINESSES: 0.9,
            InstagramAudience.PARENTS: 0.95
        }
        
        modifier = audience_modifiers.get(audience, 1.0)
        return base_rate * modifier

# Export classes
__all__ = [
    'InstagramSEOOptimizer',
    'InstagramContentOptimization',
    'InstagramHashtagAnalysis',
    'InstagramContentType',
    'InstagramAudience',
    'ContentPillar'
]