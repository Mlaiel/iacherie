"""Twitter SEO Engine - Advanced Twitter/X Platform Optimization
Comprehensive SEO optimization for Twitter/X content including hashtag optimization,
thread optimization, engagement maximization, and viral content prediction.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

logger = logging.getLogger(__name__)


class TwitterContentType(Enum):
    """Twitter content types"""
    TWEET = "tweet"
    THREAD = "thread"
    REPLY = "reply"
    RETWEET = "retweet"
    QUOTE_TWEET = "quote_tweet"
    SPACES = "spaces"
    FLEETS = "fleets"


class EngagementMetric(Enum):
    """Twitter engagement metrics"""
    LIKES = "likes"
    RETWEETS = "retweets"
    REPLIES = "replies"
    QUOTE_TWEETS = "quote_tweets"
    BOOKMARKS = "bookmarks"
    PROFILE_CLICKS = "profile_clicks"
    LINK_CLICKS = "link_clicks"
    IMPRESSIONS = "impressions"
    REACH = "reach"


class TwitterAudience(Enum):
    """Twitter audience types"""
    GENERAL = "general"
    TECH = "tech"
    CREATORS = "creators"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"


@dataclass
class TwitterHashtag:
    """Twitter hashtag analysis"""
    hashtag: str
    popularity_score: float
    engagement_rate: float
    competition_level: str
    trending_status: bool
    related_hashtags: List[str] = field(default_factory=list)
    optimal_times: List[str] = field(default_factory=list)
    audience_segments: List[TwitterAudience] = field(default_factory=list)


@dataclass
class TwitterOptimization:
    """Twitter content optimization"""
    original_content: str
    optimized_content: str
    optimal_hashtags: List[TwitterHashtag]
    optimal_posting_time: datetime
    engagement_score: float
    viral_potential: float
    character_optimization: Dict[str, Any]
    thread_structure: Optional[Dict[str, Any]] = None
    media_recommendations: List[str] = field(default_factory=list)


@dataclass
class TwitterAnalytics:
    """Twitter analytics data"""
    tweet_id: str
    impressions: int
    engagements: int
    engagement_rate: float
    likes: int
    retweets: int
    replies: int
    profile_clicks: int
    link_clicks: int
    hashtag_performance: Dict[str, float]
    optimal_performance_time: datetime
    audience_insights: Dict[str, Any]


@dataclass
class TwitterSEOScore:
    """Comprehensive Twitter SEO score"""
    overall_score: float
    content_score: float
    hashtag_score: float
    timing_score: float
    engagement_score: float
    virality_score: float
    audience_targeting_score: float
    improvements: List[str] = field(default_factory=list)


class TwitterSEOEngine:
    """Advanced Twitter/X SEO optimization engine"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Twitter SEO engine
        
        Args:
            config: Configuration including API keys, audience data
        """
        self.config = config
        self.hashtag_database = {}
        self.engagement_patterns = {}
        self.trending_topics = []
        self.audience_insights = {}
        self.character_limit = 280
        self.optimal_hashtag_count = 3  # Twitter best practice
        
    async def optimize_tweet(self, content: str, 
                           target_audience: TwitterAudience = TwitterAudience.GENERAL,
                           content_type: TwitterContentType = TwitterContentType.TWEET) -> TwitterOptimization:
        """Optimize a tweet for maximum engagement and reach
        
        Args:
            content: Original tweet content
            target_audience: Target audience segment
            content_type: Type of Twitter content
            
        Returns:
            Optimized Twitter content
        """
        try:
            # Analyze current content
            content_analysis = await self._analyze_content(content)
            
            # Optimize content structure
            optimized_content = await self._optimize_content_structure(
                content, content_analysis, target_audience
            )
            
            # Find optimal hashtags
            optimal_hashtags = await self._find_optimal_hashtags(
                content, target_audience, content_analysis
            )
            
            # Determine optimal posting time
            optimal_time = await self._find_optimal_posting_time(target_audience)
            
            # Calculate engagement score
            engagement_score = await self._calculate_engagement_score(
                optimized_content, optimal_hashtags, target_audience
            )
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(
                optimized_content, optimal_hashtags, content_analysis
            )
            
            # Character optimization analysis
            char_optimization = await self._analyze_character_optimization(
                content, optimized_content
            )
            
            # Thread structure (if applicable)
            thread_structure = None
            if content_type == TwitterContentType.THREAD:
                thread_structure = await self._optimize_thread_structure(content)
            
            # Media recommendations
            media_recommendations = await self._generate_media_recommendations(
                content_analysis, target_audience
            )
            
            return TwitterOptimization(
                original_content=content,
                optimized_content=optimized_content,
                optimal_hashtags=optimal_hashtags,
                optimal_posting_time=optimal_time,
                engagement_score=engagement_score,
                viral_potential=viral_potential,
                character_optimization=char_optimization,
                thread_structure=thread_structure,
                media_recommendations=media_recommendations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing tweet: {str(e)}")
            raise
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze tweet content for optimization opportunities"""
        try:
            analysis = {
                'character_count': len(content),
                'word_count': len(content.split()),
                'hashtag_count': len(re.findall(r'#\w+', content)),
                'mention_count': len(re.findall(r'@\w+', content)),
                'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)),
                'has_emoji': bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
                'sentiment': await self._analyze_sentiment(content),
                'readability': await self._calculate_readability(content),
                'keywords': await self._extract_keywords(content),
                'entities': await self._extract_entities(content),
                'topics': await self._identify_topics(content),
                'call_to_action': await self._detect_call_to_action(content),
                'urgency_words': await self._detect_urgency_words(content),
                'question_format': '?' in content,
                'exclamation_format': '!' in content
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {}
    
    async def _optimize_content_structure(self, 
                                        content: str,
                                        analysis: Dict[str, Any],
                                        audience: TwitterAudience) -> str:
        """Optimize content structure for engagement"""
        try:
            optimized = content
            
            # Ensure optimal character count (leave room for hashtags)
            max_content_length = self.character_limit - (self.optimal_hashtag_count * 15)  # ~15 chars per hashtag
            
            if len(optimized) > max_content_length:
                # Trim content while preserving meaning
                optimized = await self._smart_trim_content(optimized, max_content_length)
            
            # Add engaging elements based on audience
            if audience == TwitterAudience.TECH:
                optimized = await self._add_tech_optimization(optimized, analysis)
            elif audience == TwitterAudience.CREATORS:
                optimized = await self._add_creator_optimization(optimized, analysis)
            elif audience == TwitterAudience.BUSINESS:
                optimized = await self._add_business_optimization(optimized, analysis)
            
            # Ensure proper formatting
            optimized = await self._format_for_engagement(optimized, analysis)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error optimizing content structure: {str(e)}")
            return content
    
    async def _find_optimal_hashtags(self, 
                                   content: str,
                                   audience: TwitterAudience,
                                   analysis: Dict[str, Any]) -> List[TwitterHashtag]:
        """Find optimal hashtags for maximum reach and engagement"""
        try:
            # Extract existing hashtags
            existing_hashtags = re.findall(r'#\w+', content)
            
            # Generate hashtag candidates
            candidates = await self._generate_hashtag_candidates(content, analysis, audience)
            
            # Score hashtags
            scored_hashtags = []
            
            for hashtag in candidates:
                # Skip if already exists
                if hashtag in existing_hashtags:
                    continue
                
                score = await self._score_hashtag(hashtag, analysis, audience)
                
                if score['total_score'] > 0.5:  # Minimum threshold
                    twitter_hashtag = TwitterHashtag(
                        hashtag=hashtag,
                        popularity_score=score['popularity'],
                        engagement_rate=score['engagement_rate'],
                        competition_level=score['competition'],
                        trending_status=score['trending'],
                        related_hashtags=score['related'],
                        optimal_times=score['optimal_times'],
                        audience_segments=score['audiences']
                    )
                    scored_hashtags.append(twitter_hashtag)
            
            # Sort by score and return top hashtags
            scored_hashtags.sort(key=lambda x: x.popularity_score * x.engagement_rate, reverse=True)
            
            return scored_hashtags[:self.optimal_hashtag_count]
            
        except Exception as e:
            logger.error(f"Error finding optimal hashtags: {str(e)}")
            return []
    
    async def _generate_hashtag_candidates(self, 
                                         content: str,
                                         analysis: Dict[str, Any],
                                         audience: TwitterAudience) -> List[str]:
        """Generate hashtag candidates based on content analysis"""
        candidates = []
        
        # From keywords
        for keyword in analysis.get('keywords', []):
            # Convert to hashtag format
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            candidates.append(hashtag)
        
        # From topics
        for topic in analysis.get('topics', []):
            hashtag = f"#{topic.replace(' ', '').lower()}"
            candidates.append(hashtag)
        
        # Audience-specific hashtags
        audience_hashtags = {
            TwitterAudience.TECH: ['#tech', '#coding', '#programming', '#AI', '#ML', '#innovation'],
            TwitterAudience.CREATORS: ['#creators', '#content', '#creative', '#art', '#design'],
            TwitterAudience.BUSINESS: ['#business', '#entrepreneur', '#startup', '#marketing'],
            TwitterAudience.ENTERTAINMENT: ['#entertainment', '#fun', '#viral', '#trending'],
            TwitterAudience.NEWS: ['#news', '#breaking', '#update', '#current'],
            TwitterAudience.EDUCATION: ['#education', '#learning', '#knowledge', '#tips'],
            TwitterAudience.LIFESTYLE: ['#lifestyle', '#life', '#motivation', '#inspiration']
        }
        
        candidates.extend(audience_hashtags.get(audience, []))
        
        # Trending hashtags
        candidates.extend(await self._get_trending_hashtags())
        
        return list(set(candidates))  # Remove duplicates
    
    async def _score_hashtag(self, 
                           hashtag: str,
                           analysis: Dict[str, Any],
                           audience: TwitterAudience) -> Dict[str, Any]:
        """Score a hashtag for effectiveness"""
        try:
            # Mock scoring (would use real Twitter API data)
            base_score = 0.5
            
            # Popularity score (based on usage volume)
            popularity = min(1.0, len(hashtag) / 20)  # Shorter hashtags often more popular
            
            # Engagement rate (mock calculation)
            engagement_rate = 0.7 if len(hashtag) < 15 else 0.5
            
            # Competition level
            competition = "MEDIUM"
            if popularity > 0.8:
                competition = "HIGH"
            elif popularity < 0.3:
                competition = "LOW"
            
            # Trending status
            trending = hashtag in await self._get_trending_hashtags()
            
            # Related hashtags
            related = await self._find_related_hashtags(hashtag)
            
            # Optimal times
            optimal_times = ["09:00", "15:00", "19:00"]  # Peak engagement times
            
            # Audience segments
            audiences = [audience]
            
            total_score = (popularity + engagement_rate) / 2
            if trending:
                total_score *= 1.2  # Boost for trending
            
            return {
                'total_score': total_score,
                'popularity': popularity,
                'engagement_rate': engagement_rate,
                'competition': competition,
                'trending': trending,
                'related': related,
                'optimal_times': optimal_times,
                'audiences': audiences
            }
            
        except Exception as e:
            logger.error(f"Error scoring hashtag: {str(e)}")
            return {'total_score': 0}
    
    async def _find_optimal_posting_time(self, audience: TwitterAudience) -> datetime:
        """Find optimal posting time for target audience"""
        try:
            # Audience-specific optimal times
            optimal_hours = {
                TwitterAudience.GENERAL: [9, 15, 19],
                TwitterAudience.TECH: [8, 14, 20],
                TwitterAudience.CREATORS: [10, 16, 21],
                TwitterAudience.BUSINESS: [9, 13, 17],
                TwitterAudience.ENTERTAINMENT: [19, 20, 21],
                TwitterAudience.NEWS: [7, 12, 18],
                TwitterAudience.EDUCATION: [8, 14, 19],
                TwitterAudience.LIFESTYLE: [10, 16, 20]
            }
            
            hours = optimal_hours.get(audience, [9, 15, 19])
            
            # Select best hour based on current time and audience patterns
            now = datetime.now()
            best_hour = min(hours, key=lambda h: abs(h - now.hour))
            
            # Calculate optimal posting time
            optimal_time = now.replace(hour=best_hour, minute=0, second=0, microsecond=0)
            
            # If the time has passed today, schedule for tomorrow
            if optimal_time < now:
                optimal_time += timedelta(days=1)
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Error finding optimal posting time: {str(e)}")
            return datetime.now()
    
    async def _calculate_engagement_score(self, 
                                        content: str,
                                        hashtags: List[TwitterHashtag],
                                        audience: TwitterAudience) -> float:
        """Calculate predicted engagement score"""
        try:
            score = 0.5  # Base score
            
            # Content factors
            if len(content) < 100:
                score += 0.1  # Shorter content often performs better
            
            if '?' in content:
                score += 0.15  # Questions drive engagement
            
            if '!' in content:
                score += 0.1  # Exclamation adds enthusiasm
            
            # Hashtag factors
            hashtag_score = sum(h.engagement_rate for h in hashtags) / len(hashtags) if hashtags else 0
            score += hashtag_score * 0.3
            
            # Audience alignment
            score += 0.2  # Assuming good audience targeting
            
            # Ensure score is between 0 and 1
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.5
    
    async def _calculate_viral_potential(self, 
                                       content: str,
                                       hashtags: List[TwitterHashtag],
                                       analysis: Dict[str, Any]) -> float:
        """Calculate viral potential score"""
        try:
            score = 0.0
            
            # Content virality factors
            if analysis.get('sentiment', 'neutral') == 'positive':
                score += 0.2
            
            if analysis.get('has_emoji'):
                score += 0.1
            
            if analysis.get('call_to_action'):
                score += 0.15
            
            if analysis.get('urgency_words'):
                score += 0.1
            
            # Hashtag virality
            trending_count = sum(1 for h in hashtags if h.trending_status)
            score += (trending_count / len(hashtags)) * 0.3 if hashtags else 0
            
            # Content format factors
            if analysis.get('question_format'):
                score += 0.1
            
            if len(content) < 80:  # Very short, punchy content
                score += 0.05
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating viral potential: {str(e)}")
            return 0.0
    
    async def optimize_thread(self, thread_content: List[str]) -> Dict[str, Any]:
        """Optimize a Twitter thread for maximum engagement"""
        try:
            optimized_thread = []
            
            for i, tweet in enumerate(thread_content):
                if i == 0:
                    # First tweet - hook and setup
                    optimized = await self._optimize_thread_starter(tweet)
                elif i == len(thread_content) - 1:
                    # Last tweet - conclusion and CTA
                    optimized = await self._optimize_thread_conclusion(tweet)
                else:
                    # Middle tweets - maintain flow
                    optimized = await self._optimize_thread_middle(tweet, i)
                
                optimized_thread.append(optimized)
            
            # Add thread numbering if not present
            for i, tweet in enumerate(optimized_thread):
                if not re.search(r'\d+/\d+', tweet) and len(optimized_thread) > 1:
                    tweet = f"{i+1}/{len(optimized_thread)} {tweet}"
                    optimized_thread[i] = tweet
            
            return {
                'original_thread': thread_content,
                'optimized_thread': optimized_thread,
                'thread_metrics': await self._analyze_thread_metrics(optimized_thread),
                'engagement_prediction': await self._predict_thread_engagement(optimized_thread)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing thread: {str(e)}")
            return {}
    
    async def analyze_twitter_performance(self, tweet_data: Dict[str, Any]) -> TwitterAnalytics:
        """Analyze Twitter performance data"""
        try:
            analytics = TwitterAnalytics(
                tweet_id=tweet_data['tweet_id'],
                impressions=tweet_data.get('impressions', 0),
                engagements=tweet_data.get('engagements', 0),
                engagement_rate=tweet_data.get('engagement_rate', 0.0),
                likes=tweet_data.get('likes', 0),
                retweets=tweet_data.get('retweets', 0),
                replies=tweet_data.get('replies', 0),
                profile_clicks=tweet_data.get('profile_clicks', 0),
                link_clicks=tweet_data.get('link_clicks', 0),
                hashtag_performance=tweet_data.get('hashtag_performance', {}),
                optimal_performance_time=datetime.fromisoformat(
                    tweet_data.get('posted_at', datetime.now().isoformat())
                ),
                audience_insights=tweet_data.get('audience_insights', {})
            )
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error analyzing Twitter performance: {str(e)}")
            raise
    
    async def calculate_twitter_seo_score(self, content: str, 
                                        hashtags: List[str],
                                        audience: TwitterAudience) -> TwitterSEOScore:
        """Calculate comprehensive Twitter SEO score"""
        try:
            # Analyze content
            analysis = await self._analyze_content(content)
            
            # Score components
            content_score = await self._score_content_quality(content, analysis)
            hashtag_score = await self._score_hashtag_optimization(hashtags, analysis)
            timing_score = 0.8  # Would be based on posting time analysis
            engagement_score = await self._calculate_engagement_score(content, [], audience)
            virality_score = await self._calculate_viral_potential(content, [], analysis)
            audience_score = await self._score_audience_targeting(content, audience)
            
            # Calculate overall score
            weights = {
                'content': 0.25,
                'hashtag': 0.20,
                'timing': 0.15,
                'engagement': 0.15,
                'virality': 0.15,
                'audience': 0.10
            }
            
            overall_score = (
                content_score * weights['content'] +
                hashtag_score * weights['hashtag'] +
                timing_score * weights['timing'] +
                engagement_score * weights['engagement'] +
                virality_score * weights['virality'] +
                audience_score * weights['audience']
            )
            
            # Generate improvements
            improvements = await self._generate_twitter_improvements(
                content_score, hashtag_score, timing_score, 
                engagement_score, virality_score, audience_score
            )
            
            return TwitterSEOScore(
                overall_score=overall_score,
                content_score=content_score,
                hashtag_score=hashtag_score,
                timing_score=timing_score,
                engagement_score=engagement_score,
                virality_score=virality_score,
                audience_targeting_score=audience_score,
                improvements=improvements
            )
            
        except Exception as e:
            logger.error(f"Error calculating Twitter SEO score: {str(e)}")
            raise
    
    # Helper methods
    async def _analyze_sentiment(self, content: str) -> str:
        """Analyze sentiment of content"""
        # Simple sentiment analysis (would use ML model in production)
        positive_words = ['great', 'awesome', 'amazing', 'love', 'excited', 'happy']
        negative_words = ['bad', 'terrible', 'hate', 'angry', 'sad', 'disappointed']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculate readability score"""
        # Simple readability calculation
        words = content.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        # Higher score for shorter average word length (easier to read)
        return max(0.0, 1.0 - (avg_word_length - 4) / 10)
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction (would use NLP in production)
        words = re.findall(r'\b\w+\b', content.lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        return list(set(keywords))[:5]  # Return top 5 unique keywords
    
    async def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content"""
        # Simple entity extraction (would use NER in production)
        entities = []
        
        # Find mentions
        mentions = re.findall(r'@\w+', content)
        entities.extend(mentions)
        
        # Find hashtags
        hashtags = re.findall(r'#\w+', content)
        entities.extend(hashtags)
        
        return entities
    
    async def _identify_topics(self, content: str) -> List[str]:
        """Identify topics in content"""
        # Simple topic identification (would use topic modeling in production)
        topics = []
        
        tech_keywords = ['AI', 'ML', 'code', 'programming', 'tech', 'software']
        business_keywords = ['business', 'startup', 'entrepreneur', 'marketing', 'sales']
        creative_keywords = ['art', 'design', 'creative', 'photography', 'music']
        
        content_lower = content.lower()
        
        if any(keyword.lower() in content_lower for keyword in tech_keywords):
            topics.append('technology')
        if any(keyword.lower() in content_lower for keyword in business_keywords):
            topics.append('business')
        if any(keyword.lower() in content_lower for keyword in creative_keywords):
            topics.append('creative')
        
        return topics
    
    async def _detect_call_to_action(self, content: str) -> bool:
        """Detect if content has call to action"""
        cta_words = ['follow', 'retweet', 'like', 'share', 'comment', 'reply', 'check out', 'visit', 'click']
        return any(word in content.lower() for word in cta_words)
    
    async def _detect_urgency_words(self, content: str) -> bool:
        """Detect urgency words in content"""
        urgency_words = ['now', 'today', 'urgent', 'breaking', 'limited', 'exclusive', 'deadline']
        return any(word in content.lower() for word in urgency_words)
    
    async def _get_trending_hashtags(self) -> List[str]:
        """Get current trending hashtags"""
        # Mock trending hashtags (would use Twitter API in production)
        return ['#trending', '#viral', '#popular', '#hot', '#breaking']
    
    async def _find_related_hashtags(self, hashtag: str) -> List[str]:
        """Find related hashtags"""
        # Mock related hashtags (would use hashtag analysis in production)
        return [f"{hashtag}2", f"{hashtag}related", f"related{hashtag}"]
    
    async def _smart_trim_content(self, content: str, max_length: int) -> str:
        """Smart content trimming while preserving meaning"""
        if len(content) <= max_length:
            return content
        
        # Try to trim at sentence boundaries
        sentences = content.split('. ')
        if len(sentences) > 1:
            trimmed = sentences[0]
            for sentence in sentences[1:]:
                if len(trimmed + '. ' + sentence) <= max_length:
                    trimmed += '. ' + sentence
                else:
                    break
            if trimmed != sentences[0]:
                return trimmed + '.'
        
        # Trim at word boundaries
        words = content.split()
        trimmed = ''
        for word in words:
            if len(trimmed + ' ' + word) <= max_length - 3:  # Leave room for '...'
                trimmed += ' ' + word if trimmed else word
            else:
                break
        
        return trimmed + '...' if len(trimmed) < len(content) else trimmed
    
    async def _add_tech_optimization(self, content: str, analysis: Dict[str, Any]) -> str:
        """Add tech-specific optimizations"""
        # Add tech emojis if not present
        if not analysis.get('has_emoji'):
            content = f"💻 {content}"
        return content
    
    async def _add_creator_optimization(self, content: str, analysis: Dict[str, Any]) -> str:
        """Add creator-specific optimizations"""
        if not analysis.get('has_emoji'):
            content = f"🎨 {content}"
        return content
    
    async def _add_business_optimization(self, content: str, analysis: Dict[str, Any]) -> str:
        """Add business-specific optimizations"""
        if not analysis.get('has_emoji'):
            content = f"💼 {content}"
        return content
    
    async def _format_for_engagement(self, content: str, analysis: Dict[str, Any]) -> str:
        """Format content for maximum engagement"""
        # Ensure proper spacing and formatting
        content = re.sub(r'\s+', ' ', content)  # Remove extra spaces
        content = content.strip()
        
        # Add engaging elements if missing
        if not analysis.get('question_format') and not analysis.get('call_to_action'):
            if len(content) < 200:  # Have room for addition
                content += " What do you think?"
        
        return content
    
    async def _optimize_thread_starter(self, tweet: str) -> str:
        """Optimize the first tweet in a thread"""
        if not tweet.endswith('🧵') and not tweet.endswith('👇'):
            tweet = f"{tweet} 🧵"
        return tweet
    
    async def _optimize_thread_conclusion(self, tweet: str) -> str:
        """Optimize the last tweet in a thread"""
        if 'follow' not in tweet.lower() and 'retweet' not in tweet.lower():
            tweet = f"{tweet}\n\nIf this was helpful, please follow for more insights! 🙏"
        return tweet
    
    async def _optimize_thread_middle(self, tweet: str, index: int) -> str:
        """Optimize middle tweets in a thread"""
        # Ensure good flow and engagement
        return tweet
    
    async def _analyze_thread_metrics(self, thread: List[str]) -> Dict[str, Any]:
        """Analyze thread metrics"""
        return {
            'total_tweets': len(thread),
            'total_characters': sum(len(tweet) for tweet in thread),
            'avg_tweet_length': sum(len(tweet) for tweet in thread) / len(thread),
            'hashtag_count': sum(len(re.findall(r'#\w+', tweet)) for tweet in thread),
            'mention_count': sum(len(re.findall(r'@\w+', tweet)) for tweet in thread)
        }
    
    async def _predict_thread_engagement(self, thread: List[str]) -> float:
        """Predict thread engagement score"""
        # Mock prediction (would use ML model in production)
        base_score = 0.6
        
        # Longer threads tend to have lower engagement per tweet
        length_penalty = max(0, (len(thread) - 5) * 0.05)
        
        # Threads with good hooks perform better
        hook_bonus = 0.1 if '🧵' in thread[0] or '👇' in thread[0] else 0
        
        return max(0.1, base_score - length_penalty + hook_bonus)
    
    async def _score_content_quality(self, content: str, analysis: Dict[str, Any]) -> float:
        """Score content quality"""
        score = 0.5
        
        # Character count optimization
        if 50 <= len(content) <= 200:
            score += 0.2
        
        # Readability
        score += analysis.get('readability', 0) * 0.2
        
        # Engagement elements
        if analysis.get('question_format'):
            score += 0.1
        if analysis.get('has_emoji'):
            score += 0.1
        
        return min(1.0, score)
    
    async def _score_hashtag_optimization(self, hashtags: List[str], analysis: Dict[str, Any]) -> float:
        """Score hashtag optimization"""
        if not hashtags:
            return 0.3  # Low score for no hashtags
        
        score = 0.5
        
        # Optimal hashtag count
        if 1 <= len(hashtags) <= 3:
            score += 0.3
        elif len(hashtags) > 5:
            score -= 0.2  # Penalty for too many hashtags
        
        # Hashtag relevance (mock scoring)
        score += 0.2  # Assume hashtags are relevant
        
        return min(1.0, score)
    
    async def _score_audience_targeting(self, content: str, audience: TwitterAudience) -> float:
        """Score audience targeting effectiveness"""
        # Mock scoring based on audience alignment
        return 0.8  # Assume good targeting
    
    async def _generate_twitter_improvements(self, *scores) -> List[str]:
        """Generate improvement recommendations"""
        improvements = []
        
        content_score, hashtag_score, timing_score, engagement_score, virality_score, audience_score = scores
        
        if content_score < 0.7:
            improvements.append("Optimize content length and structure for better readability")
        
        if hashtag_score < 0.6:
            improvements.append("Use 2-3 relevant, trending hashtags for better discoverability")
        
        if engagement_score < 0.6:
            improvements.append("Add questions or call-to-action to drive engagement")
        
        if virality_score < 0.5:
            improvements.append("Include trending topics or urgent language for viral potential")
        
        return improvements