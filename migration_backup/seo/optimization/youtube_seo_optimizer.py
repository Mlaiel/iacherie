"""
YouTube SEO Optimizer for Ainflue Platform
Advanced YouTube-specific SEO optimization for video content creators

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Tuple, Union, Set
import re
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math


@dataclass
class YouTubeVideoMetadata:
    """YouTube video metadata structure"""
    title: str
    description: str
    tags: List[str]
    category: str
    thumbnail_url: str
    duration: int  # seconds
    language: str
    captions: bool
    custom_thumbnail: bool


@dataclass
class YouTubeChannelMetadata:
    """YouTube channel metadata structure"""
    name: str
    description: str
    keywords: List[str]
    category: str
    subscriber_count: int
    video_count: int
    custom_url: str
    verified: bool


@dataclass
class YouTubeOptimizationReport:
    """YouTube SEO optimization report"""
    video_id: str
    overall_score: float
    title_score: float
    description_score: float
    tags_score: float
    thumbnail_score: float
    engagement_potential: float
    recommendations: List[str]
    keyword_opportunities: List[str]
    competitor_insights: Dict[str, Union[str, float]]


class YouTubeSEOOptimizer:
    """
    Advanced YouTube SEO optimization engine
    Provides comprehensive YouTube-specific SEO recommendations and optimization
    """
    
    def __init__(self):
        self.youtube_ranking_factors = self._initialize_youtube_ranking_factors()
        self.category_guidelines = self._load_category_guidelines()
        self.title_patterns = self._load_title_patterns()
        self.description_templates = self._load_description_templates()
        self.tag_strategies = self._load_tag_strategies()
        
    def _initialize_youtube_ranking_factors(self) -> Dict[str, float]:
        """Initialize YouTube-specific ranking factors"""
        return {
            # Content Quality (40%)
            'title_optimization': 0.12,
            'description_quality': 0.10,
            'tags_relevance': 0.08,
            'thumbnail_quality': 0.06,
            'video_quality': 0.04,
            
            # Engagement Signals (35%)
            'click_through_rate': 0.15,
            'watch_time': 0.10,
            'engagement_rate': 0.06,
            'comments_ratio': 0.02,
            'likes_ratio': 0.02,
            
            # Channel Authority (15%)
            'channel_authority': 0.08,
            'subscriber_engagement': 0.04,
            'upload_consistency': 0.03,
            
            # Technical Factors (10%)
            'video_length_optimization': 0.03,
            'captions_availability': 0.02,
            'video_freshness': 0.03,
            'mobile_optimization': 0.02
        }
        
    def _load_category_guidelines(self) -> Dict[str, Dict]:
        """Load category-specific optimization guidelines"""
        return {
            'music': {
                'optimal_length': (180, 300),  # 3-5 minutes
                'title_keywords': ['music', 'song', 'official', 'video', 'audio'],
                'description_sections': ['lyrics', 'credits', 'social_links', 'streaming_links'],
                'tags_focus': ['genre', 'mood', 'instrument', 'artist_name'],
                'thumbnail_style': 'artistic'
            },
            'education': {
                'optimal_length': (600, 1200),  # 10-20 minutes
                'title_keywords': ['how to', 'tutorial', 'guide', 'learn', 'tips'],
                'description_sections': ['timestamps', 'resources', 'related_videos'],
                'tags_focus': ['skill', 'level', 'topic', 'method'],
                'thumbnail_style': 'educational'
            },
            'entertainment': {
                'optimal_length': (300, 600),  # 5-10 minutes
                'title_keywords': ['funny', 'epic', 'amazing', 'compilation', 'reaction'],
                'description_sections': ['context', 'social_links', 'related_content'],
                'tags_focus': ['genre', 'mood', 'trend', 'audience'],
                'thumbnail_style': 'expressive'
            },
            'technology': {
                'optimal_length': (480, 900),  # 8-15 minutes
                'title_keywords': ['review', 'unboxing', 'test', 'comparison', 'tech'],
                'description_sections': ['specs', 'links', 'timestamps', 'disclosure'],
                'tags_focus': ['brand', 'model', 'feature', 'category'],
                'thumbnail_style': 'product_focused'
            }
        }
        
    def _load_title_patterns(self) -> Dict[str, List[str]]:
        """Load effective title patterns for different content types"""
        return {
            'tutorial': [
                "How to {action} in {timeframe}",
                "{number} Ways to {action}",
                "Complete Guide to {topic}",
                "{topic} Tutorial for Beginners",
                "Master {skill} in {timeframe}"
            ],
            'review': [
                "{product} Review: Is it Worth It?",
                "Honest {product} Review After {timeframe}",
                "{product} vs {competitor}: Which is Better?",
                "Why {product} is {adjective}",
                "{product} - The Good, Bad & Ugly"
            ],
            'music': [
                "{song_title} - {artist} (Official {type})",
                "{artist} - {song_title} [{genre}]",
                "{song_title} by {artist} | {mood} Music",
                "{artist} - {song_title} (Lyrics Video)",
                "New Music: {artist} - {song_title}"
            ],
            'gaming': [
                "{game} - {achievement} Gameplay",
                "{number} Tips for {game}",
                "{game} {character} Build Guide",
                "Beating {game} {difficulty}",
                "{game} Secret {discovery}"
            ]
        }
        
    def _load_description_templates(self) -> Dict[str, str]:
        """Load description templates for different content types"""
        return {
            'music': """
🎵 {song_title} by {artist}

{song_description}

🎼 Lyrics:
{lyrics_snippet}

📱 Listen on all platforms:
• Spotify: {spotify_link}
• Apple Music: {apple_music_link}
• YouTube Music: {youtube_music_link}

👨‍🎤 Follow {artist}:
• Instagram: {instagram}
• Twitter: {twitter}
• Website: {website}

🏷️ Tags: {tags}

#music #{genre} #{artist}
            """.strip(),
            'tutorial': """
📚 In this tutorial, you'll learn {main_topic}

⏰ Timestamps:
{timestamps}

📋 What you'll need:
{requirements}

🔗 Resources mentioned:
{resources}

💬 Questions? Leave a comment below!

👍 Like this video if it helped you
🔔 Subscribe for more {topic} tutorials

🏷️ Tags: {tags}

#{main_topic} #tutorial #howto
            """.strip(),
            'review': """
📦 {product} Review - Full breakdown after {usage_period}

⭐ Overall Rating: {rating}/10

✅ Pros:
{pros}

❌ Cons:
{cons}

💰 Current Price: {price}
🛒 Where to buy: {purchase_links}

⏰ Timestamps:
{timestamps}

💬 What do you think? Leave your thoughts below!

🏷️ Tags: {tags}

#{product} #review #{category}
            """.strip()
        }
        
    def _load_tag_strategies(self) -> Dict[str, Dict]:
        """Load tag strategies for different purposes"""
        return {
            'broad_reach': {
                'primary_tags': 3,  # Highly competitive, broad terms
                'secondary_tags': 5,  # Medium competition
                'long_tail_tags': 7,  # Low competition, specific
                'branded_tags': 2   # Channel/creator specific
            },
            'niche_targeting': {
                'primary_tags': 1,
                'secondary_tags': 4,
                'long_tail_tags': 10,
                'branded_tags': 3
            },
            'viral_potential': {
                'primary_tags': 5,
                'secondary_tags': 6,
                'long_tail_tags': 4,
                'branded_tags': 1
            }
        }
        
    def optimize_video_title(self, title: str, target_keywords: List[str], 
                           category: str = None, competitor_titles: List[str] = None) -> Dict:
        """Optimize YouTube video title for SEO and engagement"""
        
        optimization_report = {
            'original_title': title,
            'optimized_title': title,
            'score': 0,
            'improvements': [],
            'keyword_placement': {},
            'length_analysis': {},
            'engagement_factors': {}
        }
        
        # Length optimization
        title_length = len(title)
        if title_length > 70:
            optimization_report['improvements'].append("Shorten title to under 70 characters for full visibility")
            optimization_report['score'] -= 15
        elif title_length < 30:
            optimization_report['improvements'].append("Consider making title more descriptive (30+ characters)")
            optimization_report['score'] -= 5
        else:
            optimization_report['score'] += 10
            
        optimization_report['length_analysis'] = {
            'current_length': title_length,
            'optimal_range': '30-70 characters',
            'mobile_truncation': title_length > 45
        }
        
        # Keyword optimization
        title_lower = title.lower()
        keywords_found = []
        keyword_positions = {}
        
        for keyword in target_keywords:
            if keyword.lower() in title_lower:
                keywords_found.append(keyword)
                position = title_lower.find(keyword.lower())
                keyword_positions[keyword] = position
                
                # Bonus for keywords at the beginning
                if position <= 10:
                    optimization_report['score'] += 8
                elif position <= 30:
                    optimization_report['score'] += 5
                else:
                    optimization_report['score'] += 2
                    
        if not keywords_found:
            optimization_report['improvements'].append("Include at least one target keyword in the title")
            optimization_report['score'] -= 20
            
        optimization_report['keyword_placement'] = {
            'keywords_found': keywords_found,
            'positions': keyword_positions,
            'primary_keyword_first': len(keyword_positions) > 0 and min(keyword_positions.values()) <= 10
        }
        
        # Engagement factors
        engagement_score = 0
        engagement_factors = []
        
        # Numbers in title
        if re.search(r'\d+', title):
            engagement_score += 5
            engagement_factors.append('contains_numbers')
            
        # Power words
        power_words = ['amazing', 'ultimate', 'complete', 'secret', 'proven', 'best', 'new', 'free']
        power_words_found = [word for word in power_words if word in title_lower]
        if power_words_found:
            engagement_score += len(power_words_found) * 2
            engagement_factors.append(f'power_words: {power_words_found}')
            
        # Emotional triggers
        emotional_words = ['love', 'hate', 'amazing', 'shocking', 'incredible', 'unbelievable']
        emotional_words_found = [word for word in emotional_words if word in title_lower]
        if emotional_words_found:
            engagement_score += len(emotional_words_found) * 3
            engagement_factors.append(f'emotional_triggers: {emotional_words_found}')
            
        # Brackets or parentheses (often improve CTR)
        if re.search(r'[\[\(].*[\]\)]', title):
            engagement_score += 3
            engagement_factors.append('brackets_parentheses')
            
        optimization_report['engagement_factors'] = {
            'score': engagement_score,
            'factors': engagement_factors
        }
        optimization_report['score'] += engagement_score
        
        # Generate optimized title if needed
        if optimization_report['score'] < 70:
            optimized_title = self._generate_optimized_title(title, target_keywords, category)
            optimization_report['optimized_title'] = optimized_title
            optimization_report['improvements'].append(f"Suggested optimized title: {optimized_title}")
            
        # Category-specific recommendations
        if category and category in self.category_guidelines:
            guidelines = self.category_guidelines[category]
            category_keywords = guidelines.get('title_keywords', [])
            
            missing_category_keywords = [kw for kw in category_keywords if kw not in title_lower]
            if missing_category_keywords:
                optimization_report['improvements'].append(
                    f"Consider adding {category} keywords: {missing_category_keywords[:3]}"
                )
                
        optimization_report['score'] = max(0, min(100, optimization_report['score']))
        
        return optimization_report
        
    def optimize_video_description(self, description: str, target_keywords: List[str],
                                 video_metadata: YouTubeVideoMetadata) -> Dict:
        """Optimize YouTube video description for SEO"""
        
        optimization_report = {
            'original_description': description,
            'score': 0,
            'improvements': [],
            'keyword_analysis': {},
            'structure_analysis': {},
            'call_to_action_analysis': {}
        }
        
        # Length analysis
        desc_length = len(description)
        if desc_length < 200:
            optimization_report['improvements'].append("Expand description to at least 200 characters")
            optimization_report['score'] -= 10
        elif desc_length > 2000:
            optimization_report['improvements'].append("Consider shortening description for better readability")
            optimization_report['score'] -= 5
        else:
            optimization_report['score'] += 10
            
        # Keyword optimization
        desc_lower = description.lower()
        keyword_density = {}
        total_words = len(description.split())
        
        for keyword in target_keywords:
            count = desc_lower.count(keyword.lower())
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_density[keyword] = {
                'count': count,
                'density': density
            }
            
            # Optimal keyword density: 1-3%
            if 1 <= density <= 3:
                optimization_report['score'] += 5
            elif density > 3:
                optimization_report['improvements'].append(f"Reduce keyword density for '{keyword}' (currently {density:.1f}%)")
                optimization_report['score'] -= 3
            elif count == 0:
                optimization_report['improvements'].append(f"Include keyword '{keyword}' in description")
                optimization_report['score'] -= 5
                
        optimization_report['keyword_analysis'] = keyword_density
        
        # Structure analysis
        structure_elements = {
            'timestamps': bool(re.search(r'\d{1,2}:\d{2}', description)),
            'links': bool(re.search(r'https?://', description)),
            'social_media': bool(re.search(r'@\w+|instagram|twitter|facebook', description, re.I)),
            'hashtags': bool(re.search(r'#\w+', description)),
            'sections': len(re.findall(r'\n\n', description)) > 2
        }
        
        structure_score = sum(structure_elements.values()) * 4
        optimization_report['score'] += structure_score
        optimization_report['structure_analysis'] = structure_elements
        
        # Call-to-action analysis
        cta_patterns = [
            r'like.*video', r'subscribe', r'comment', r'share',
            r'hit.*bell', r'notification', r'turn on'
        ]
        
        cta_found = []
        for pattern in cta_patterns:
            if re.search(pattern, desc_lower):
                cta_found.append(pattern)
                
        if len(cta_found) >= 2:
            optimization_report['score'] += 8
        elif len(cta_found) == 1:
            optimization_report['score'] += 4
        else:
            optimization_report['improvements'].append("Add call-to-action elements (like, subscribe, comment)")
            optimization_report['score'] -= 5
            
        optimization_report['call_to_action_analysis'] = {
            'cta_count': len(cta_found),
            'cta_types': cta_found
        }
        
        # First 125 characters optimization (shown in search)
        first_125 = description[:125]
        if not any(keyword.lower() in first_125.lower() for keyword in target_keywords):
            optimization_report['improvements'].append("Include main keyword in first 125 characters")
            optimization_report['score'] -= 8
            
        optimization_report['score'] = max(0, min(100, optimization_report['score']))
        
        return optimization_report
        
    def optimize_video_tags(self, current_tags: List[str], target_keywords: List[str],
                          category: str = None, strategy: str = 'broad_reach') -> Dict:
        """Optimize YouTube video tags for maximum reach and relevance"""
        
        optimization_report = {
            'current_tags': current_tags,
            'optimized_tags': [],
            'score': 0,
            'tag_analysis': {},
            'recommendations': []
        }
        
        # Tag count analysis
        tag_count = len(current_tags)
        optimal_range = (10, 15)
        
        if tag_count < optimal_range[0]:
            optimization_report['recommendations'].append(f"Add more tags (current: {tag_count}, optimal: {optimal_range[0]}-{optimal_range[1]})")
            optimization_report['score'] -= 10
        elif tag_count > optimal_range[1]:
            optimization_report['recommendations'].append(f"Consider reducing tags (current: {tag_count}, optimal: {optimal_range[0]}-{optimal_range[1]})")
            optimization_report['score'] -= 5
        else:
            optimization_report['score'] += 10
            
        # Tag strategy application
        strategy_config = self.tag_strategies.get(strategy, self.tag_strategies['broad_reach'])
        
        # Generate optimized tag list
        optimized_tags = []
        
        # Primary tags (high competition, broad reach)
        primary_tags = target_keywords[:strategy_config['primary_tags']]
        optimized_tags.extend(primary_tags)
        
        # Secondary tags (medium competition)
        secondary_tags = self._generate_secondary_tags(target_keywords, category)
        optimized_tags.extend(secondary_tags[:strategy_config['secondary_tags']])
        
        # Long-tail tags (low competition, specific)
        long_tail_tags = self._generate_long_tail_tags(target_keywords, category)
        optimized_tags.extend(long_tail_tags[:strategy_config['long_tail_tags']])
        
        # Branded tags
        branded_tags = self._generate_branded_tags(category)
        optimized_tags.extend(branded_tags[:strategy_config['branded_tags']])
        
        # Remove duplicates while preserving order
        optimized_tags = list(dict.fromkeys(optimized_tags))
        
        optimization_report['optimized_tags'] = optimized_tags
        
        # Analyze tag relevance
        relevant_tags = []
        irrelevant_tags = []
        
        for tag in current_tags:
            relevance_score = self._calculate_tag_relevance(tag, target_keywords)
            if relevance_score > 0.3:
                relevant_tags.append(tag)
                optimization_report['score'] += 2
            else:
                irrelevant_tags.append(tag)
                optimization_report['score'] -= 1
                
        optimization_report['tag_analysis'] = {
            'relevant_tags': relevant_tags,
            'irrelevant_tags': irrelevant_tags,
            'relevance_ratio': len(relevant_tags) / len(current_tags) if current_tags else 0
        }
        
        if irrelevant_tags:
            optimization_report['recommendations'].append(f"Remove irrelevant tags: {irrelevant_tags[:3]}")
            
        optimization_report['score'] = max(0, min(100, optimization_report['score']))
        
        return optimization_report
        
    def analyze_youtube_competition(self, target_keyword: str, competitor_videos: List[Dict]) -> Dict:
        """Analyze YouTube competition for target keywords"""
        
        competition_analysis = {
            'keyword': target_keyword,
            'competition_level': 'medium',
            'top_performers': [],
            'common_patterns': {},
            'opportunities': [],
            'difficulty_score': 50
        }
        
        if not competitor_videos:
            return competition_analysis
            
        # Analyze top performing videos
        sorted_videos = sorted(competitor_videos, key=lambda x: x.get('views', 0), reverse=True)
        competition_analysis['top_performers'] = sorted_videos[:5]
        
        # Analyze common patterns
        title_patterns = []
        description_patterns = []
        tag_patterns = []
        
        for video in competitor_videos:
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            tags = video.get('tags', [])
            
            # Title pattern analysis
            if 'how to' in title:
                title_patterns.append('how_to')
            if re.search(r'\d+', title):
                title_patterns.append('numbers')
            if any(word in title for word in ['best', 'top', 'ultimate']):
                title_patterns.append('superlatives')
                
            # Common tags
            tag_patterns.extend([tag.lower() for tag in tags])
            
        # Find most common patterns
        title_pattern_counts = Counter(title_patterns)
        tag_pattern_counts = Counter(tag_patterns)
        
        competition_analysis['common_patterns'] = {
            'title_patterns': dict(title_pattern_counts.most_common(5)),
            'common_tags': dict(tag_pattern_counts.most_common(10))
        }
        
        # Calculate difficulty score
        avg_views = sum(video.get('views', 0) for video in competitor_videos) / len(competitor_videos)
        avg_subscribers = sum(video.get('channel_subscribers', 0) for video in competitor_videos) / len(competitor_videos)
        
        difficulty_score = min(100, (avg_views / 10000) + (avg_subscribers / 1000))
        competition_analysis['difficulty_score'] = difficulty_score
        
        if difficulty_score < 30:
            competition_analysis['competition_level'] = 'low'
        elif difficulty_score > 70:
            competition_analysis['competition_level'] = 'high'
            
        # Identify opportunities
        opportunities = []
        
        # Check for gaps in title patterns
        if title_pattern_counts.get('how_to', 0) < len(competitor_videos) * 0.3:
            opportunities.append("Consider 'How to' title format - underutilized")
            
        # Check for content length opportunities
        avg_duration = sum(video.get('duration', 0) for video in competitor_videos) / len(competitor_videos)
        if avg_duration < 300:  # 5 minutes
            opportunities.append("Opportunity for longer, more comprehensive content")
        elif avg_duration > 900:  # 15 minutes
            opportunities.append("Opportunity for shorter, more digestible content")
            
        competition_analysis['opportunities'] = opportunities
        
        return competition_analysis
        
    def generate_youtube_optimization_report(self, video_metadata: YouTubeVideoMetadata,
                                           target_keywords: List[str],
                                           category: str = None) -> YouTubeOptimizationReport:
        """Generate comprehensive YouTube SEO optimization report"""
        
        # Optimize individual components
        title_optimization = self.optimize_video_title(video_metadata.title, target_keywords, category)
        description_optimization = self.optimize_video_description(video_metadata.description, target_keywords, video_metadata)
        tags_optimization = self.optimize_video_tags(video_metadata.tags, target_keywords, category)
        
        # Calculate component scores
        title_score = title_optimization['score']
        description_score = description_optimization['score']
        tags_score = tags_optimization['score']
        
        # Thumbnail analysis (simplified)
        thumbnail_score = self._analyze_thumbnail_optimization(video_metadata)
        
        # Calculate overall score
        overall_score = (
            title_score * 0.3 +
            description_score * 0.25 +
            tags_score * 0.25 +
            thumbnail_score * 0.2
        )
        
        # Generate comprehensive recommendations
        recommendations = []
        recommendations.extend(title_optimization.get('improvements', []))
        recommendations.extend(description_optimization.get('improvements', []))
        recommendations.extend(tags_optimization.get('recommendations', []))
        
        # Calculate engagement potential
        engagement_potential = self._calculate_engagement_potential(video_metadata, target_keywords)
        
        # Find keyword opportunities
        keyword_opportunities = self._find_keyword_opportunities(target_keywords, category)
        
        return YouTubeOptimizationReport(
            video_id=getattr(video_metadata, 'video_id', 'unknown'),
            overall_score=round(overall_score, 1),
            title_score=title_score,
            description_score=description_score,
            tags_score=tags_score,
            thumbnail_score=thumbnail_score,
            engagement_potential=engagement_potential,
            recommendations=recommendations[:10],  # Top 10 recommendations
            keyword_opportunities=keyword_opportunities,
            competitor_insights={}
        )
        
    # Utility methods
    def _generate_optimized_title(self, original_title: str, keywords: List[str], category: str = None) -> str:
        """Generate an optimized title suggestion"""
        
        if not keywords:
            return original_title
            
        primary_keyword = keywords[0]
        
        # Use category-specific patterns if available
        if category and category in self.title_patterns:
            patterns = self.title_patterns[category]
            # Simple pattern matching - in practice, this would be more sophisticated
            if 'tutorial' in category or 'how to' in original_title.lower():
                return f"How to {primary_keyword} - Complete Guide"
            elif 'review' in original_title.lower():
                return f"{primary_keyword} Review: Is it Worth It?"
                
        # Default optimization
        if len(original_title) > 60:
            # Shorten and add primary keyword at beginning
            return f"{primary_keyword}: {original_title[:40]}..."
        else:
            # Add primary keyword if not present
            if primary_keyword.lower() not in original_title.lower():
                return f"{primary_keyword} - {original_title}"
                
        return original_title
        
    def _generate_secondary_tags(self, keywords: List[str], category: str = None) -> List[str]:
        """Generate secondary tags based on keywords and category"""
        
        secondary_tags = []
        
        for keyword in keywords:
            # Add plural forms
            if not keyword.endswith('s'):
                secondary_tags.append(keyword + 's')
                
            # Add related terms
            if 'music' in keyword.lower():
                secondary_tags.extend(['song', 'audio', 'melody'])
            elif 'video' in keyword.lower():
                secondary_tags.extend(['footage', 'clip', 'recording'])
            elif 'tutorial' in keyword.lower():
                secondary_tags.extend(['guide', 'howto', 'learn'])
                
        # Category-specific tags
        if category and category in self.category_guidelines:
            guidelines = self.category_guidelines[category]
            secondary_tags.extend(guidelines.get('tags_focus', []))
            
        return list(set(secondary_tags))  # Remove duplicates
        
    def _generate_long_tail_tags(self, keywords: List[str], category: str = None) -> List[str]:
        """Generate long-tail tags for specific targeting"""
        
        long_tail_tags = []
        
        for keyword in keywords:
            # Add question forms
            long_tail_tags.append(f"how to {keyword}")
            long_tail_tags.append(f"what is {keyword}")
            long_tail_tags.append(f"best {keyword}")
            
            # Add year for freshness
            current_year = datetime.now().year
            long_tail_tags.append(f"{keyword} {current_year}")
            
            # Add beginner/advanced variations
            long_tail_tags.append(f"{keyword} for beginners")
            long_tail_tags.append(f"advanced {keyword}")
            
        return long_tail_tags
        
    def _generate_branded_tags(self, category: str = None) -> List[str]:
        """Generate branded/channel-specific tags"""
        
        # These would typically be customized per channel
        branded_tags = [
            'ainflue',
            'ainflue platform',
            'creator content',
            'content creator'
        ]
        
        if category:
            branded_tags.append(f'ainflue {category}')
            
        return branded_tags
        
    def _calculate_tag_relevance(self, tag: str, keywords: List[str]) -> float:
        """Calculate relevance score for a tag against target keywords"""
        
        tag_lower = tag.lower()
        relevance_score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Exact match
            if tag_lower == keyword_lower:
                relevance_score += 1.0
            # Partial match
            elif keyword_lower in tag_lower or tag_lower in keyword_lower:
                relevance_score += 0.7
            # Word overlap
            else:
                tag_words = set(tag_lower.split())
                keyword_words = set(keyword_lower.split())
                overlap = len(tag_words & keyword_words)
                total_words = len(tag_words | keyword_words)
                if total_words > 0:
                    relevance_score += (overlap / total_words) * 0.5
                    
        return min(1.0, relevance_score / len(keywords))
        
    def _analyze_thumbnail_optimization(self, video_metadata: YouTubeVideoMetadata) -> float:
        """Analyze thumbnail optimization (simplified)"""
        
        score = 50  # Base score
        
        # Custom thumbnail bonus
        if video_metadata.custom_thumbnail:
            score += 30
        else:
            score -= 20
            
        # Category-specific recommendations would go here
        # For now, return the basic score
        
        return min(100, max(0, score))
        
    def _calculate_engagement_potential(self, video_metadata: YouTubeVideoMetadata, keywords: List[str]) -> float:
        """Calculate potential engagement based on metadata"""
        
        engagement_score = 50  # Base score
        
        # Duration optimization
        duration = video_metadata.duration
        if 180 <= duration <= 600:  # 3-10 minutes optimal for most content
            engagement_score += 15
        elif duration < 60:
            engagement_score -= 10
        elif duration > 1200:
            engagement_score -= 5
            
        # Captions availability
        if video_metadata.captions:
            engagement_score += 10
            
        # Custom thumbnail
        if video_metadata.custom_thumbnail:
            engagement_score += 15
            
        # Keyword density in title and description
        combined_text = f"{video_metadata.title} {video_metadata.description}".lower()
        keyword_mentions = sum(combined_text.count(kw.lower()) for kw in keywords)
        if keyword_mentions >= 2:
            engagement_score += 10
            
        return min(100, max(0, engagement_score))
        
    def _find_keyword_opportunities(self, keywords: List[str], category: str = None) -> List[str]:
        """Find additional keyword opportunities"""
        
        opportunities = []
        
        # Add category-specific opportunities
        if category and category in self.category_guidelines:
            guidelines = self.category_guidelines[category]
            opportunities.extend(guidelines.get('title_keywords', []))
            
        # Add trending variations
        for keyword in keywords:
            opportunities.extend([
                f"{keyword} 2024",
                f"new {keyword}",
                f"latest {keyword}",
                f"{keyword} trends"
            ])
            
        # Remove duplicates and limit
        return list(set(opportunities))[:10]


# Integration utilities
def create_ainflue_youtube_optimizer() -> YouTubeSEOOptimizer:
    """Create configured YouTube SEO optimizer for Ainflue"""
    return YouTubeSEOOptimizer()


if __name__ == "__main__":
    # Example usage
    optimizer = create_ainflue_youtube_optimizer()
    
    # Sample video metadata
    video_metadata = YouTubeVideoMetadata(
        title="How to Create Amazing Music with AI",
        description="Learn how to create professional music using AI tools...",
        tags=["music", "AI", "tutorial", "production"],
        category="music",
        thumbnail_url="https://example.com/thumb.jpg",
        duration=480,  # 8 minutes
        language="en",
        captions=True,
        custom_thumbnail=True
    )
    
    target_keywords = ["AI music", "music creation", "AI tools"]
    
    # Generate optimization report
    report = optimizer.generate_youtube_optimization_report(
        video_metadata, target_keywords, "music"
    )
    
    print(f"YouTube SEO Optimization Report")
    print(f"Overall Score: {report.overall_score}/100")
    print(f"Title Score: {report.title_score}/100")
    print(f"Description Score: {report.description_score}/100")
    print(f"Tags Score: {report.tags_score}/100")
    print(f"Engagement Potential: {report.engagement_potential}/100")
    
    print("\nTop Recommendations:")
    for i, rec in enumerate(report.recommendations[:5], 1):
        print(f"{i}. {rec}")
        
    print("\nKeyword Opportunities:")
    for kw in report.keyword_opportunities[:5]:
        print(f"- {kw}")