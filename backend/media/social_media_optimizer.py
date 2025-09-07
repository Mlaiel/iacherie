"""Social Media Optimizer - Platform-Specific Content Optimization

Enterprise-grade social media optimization system for maximizing engagement
and reach across different social media platforms with AI-driven insights.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import hashlib
import uuid

# AI and NLP imports with graceful fallbacks
try:
    import transformers
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available - using basic text processing")

try:
    import nltk
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logging.warning("NLTK not available - using basic sentiment analysis")

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logging.warning("TextBlob not available - using basic text analysis")


class SocialPlatform(Enum):
    """Supported social media platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"


class ContentType(Enum):
    """Content types for optimization"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    LIVE = "live"
    TWEET = "tweet"
    THREAD = "thread"


class OptimizationGoal(Enum):
    """Optimization goals"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    FOLLOWERS = "followers"
    BRAND_AWARENESS = "brand_awareness"
    SALES = "sales"


@dataclass
class PlatformRules:
    """Platform-specific optimization rules"""
    platform: SocialPlatform
    character_limits: Dict[str, int] = field(default_factory=dict)
    hashtag_limits: Dict[str, int] = field(default_factory=dict)
    image_specs: Dict[str, Any] = field(default_factory=dict)
    video_specs: Dict[str, Any] = field(default_factory=dict)
    best_posting_times: List[str] = field(default_factory=list)
    engagement_factors: Dict[str, float] = field(default_factory=dict)
    content_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HashtagAnalysis:
    """Hashtag analysis and recommendations"""
    recommended_hashtags: List[str] = field(default_factory=list)
    trending_hashtags: List[str] = field(default_factory=list)
    niche_hashtags: List[str] = field(default_factory=list)
    banned_hashtags: List[str] = field(default_factory=list)
    hashtag_score: float = 0.0
    estimated_reach: int = 0
    competition_level: str = "medium"


@dataclass
class ContentAnalysis:
    """Content analysis results"""
    sentiment_score: float = 0.0
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    readability_score: float = 0.0
    engagement_prediction: float = 0.0
    keyword_density: Dict[str, float] = field(default_factory=dict)
    content_quality_score: float = 0.0
    tone_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationSuggestions:
    """Optimization suggestions for content"""
    title_suggestions: List[str] = field(default_factory=list)
    caption_suggestions: List[str] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    posting_time_suggestions: List[str] = field(default_factory=list)
    content_improvements: List[str] = field(default_factory=list)
    cta_suggestions: List[str] = field(default_factory=list)
    visual_suggestions: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """Result of social media optimization"""
    platform: SocialPlatform
    content_type: ContentType
    original_content: Dict[str, Any]
    optimized_content: Dict[str, Any]
    analysis: ContentAnalysis
    hashtag_analysis: HashtagAnalysis
    suggestions: OptimizationSuggestions
    optimization_score: float = 0.0
    estimated_performance: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationJob:
    """Social media optimization job"""
    job_id: str
    content: Dict[str, Any]
    target_platforms: List[SocialPlatform]
    content_type: ContentType
    optimization_goals: List[OptimizationGoal]
    target_audience: Dict[str, Any] = field(default_factory=dict)
    brand_guidelines: Dict[str, Any] = field(default_factory=dict)
    custom_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Job tracking
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "pending"
    results: List[OptimizationResult] = field(default_factory=list)


class SocialMediaOptimizer:
    """Enterprise social media optimization system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI models
        self._initialize_ai_models()
        
        # Platform rules database
        self.platform_rules = self._initialize_platform_rules()
        
        # Active optimization jobs
        self.active_jobs: Dict[str, OptimizationJob] = {}
        
        # Optimization statistics
        self.optimization_stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "average_score_improvement": 0.0,
            "platforms_optimized": {},
            "popular_hashtags": {},
            "engagement_trends": {}
        }
        
        # Load external data sources
        self._load_trending_data()
        
        self.logger.info("Social Media Optimizer initialized")
    
    def _initialize_ai_models(self) -> None:
        """Initialize AI models for content analysis"""
        
        self.sentiment_analyzer = None
        self.emotion_analyzer = None
        self.summarizer = None
        
        if HAS_TRANSFORMERS:
            try:
                # Initialize sentiment analysis
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                
                # Initialize emotion analysis
                self.emotion_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base"
                )
                
                # Initialize summarizer
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
                
                self.logger.info("AI models initialized successfully")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize AI models: {e}")
        else:
            self.logger.warning("Transformers not available - using fallback analysis")
    
    def _initialize_platform_rules(self) -> Dict[SocialPlatform, PlatformRules]:
        """Initialize platform-specific optimization rules"""
        
        rules = {}
        
        # Instagram rules
        rules[SocialPlatform.INSTAGRAM] = PlatformRules(
            platform=SocialPlatform.INSTAGRAM,
            character_limits={
                "caption": 2200,
                "bio": 150,
                "story_text": 80
            },
            hashtag_limits={
                "posts": 30,
                "stories": 10,
                "reels": 30
            },
            image_specs={
                "feed": {"width": 1080, "height": 1080, "aspect_ratio": "1:1"},
                "story": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"},
                "reel": {"width": 1080, "height": 1920, "aspect_ratio": "9:16"}
            },
            best_posting_times=[
                "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"
            ],
            engagement_factors={
                "hashtags": 0.25,
                "posting_time": 0.20,
                "caption_quality": 0.30,
                "visual_quality": 0.25
            },
            content_preferences={
                "carousel_posts": 1.3,
                "reels": 1.5,
                "user_generated_content": 1.2,
                "behind_the_scenes": 1.1
            }
        )
        
        # TikTok rules
        rules[SocialPlatform.TIKTOK] = PlatformRules(
            platform=SocialPlatform.TIKTOK,
            character_limits={
                "caption": 150,
                "bio": 80
            },
            hashtag_limits={
                "videos": 100  # Character limit for hashtags
            },
            video_specs={
                "resolution": "1080x1920",
                "aspect_ratio": "9:16",
                "duration_range": [15, 180],
                "optimal_duration": 30
            },
            best_posting_times=[
                "06:00", "10:00", "16:00", "19:00", "21:00"
            ],
            engagement_factors={
                "trending_sounds": 0.35,
                "hashtags": 0.20,
                "posting_time": 0.15,
                "video_quality": 0.30
            },
            content_preferences={
                "trending_challenges": 1.8,
                "original_sounds": 1.4,
                "quick_cuts": 1.3,
                "text_overlays": 1.2
            }
        )
        
        # YouTube rules
        rules[SocialPlatform.YOUTUBE] = PlatformRules(
            platform=SocialPlatform.YOUTUBE,
            character_limits={
                "title": 100,
                "description": 5000,
                "channel_description": 1000
            },
            hashtag_limits={
                "videos": 15
            },
            video_specs={
                "thumbnail": {"width": 1280, "height": 720},
                "optimal_duration": [600, 1800],  # 10-30 minutes
                "resolution": "1920x1080"
            },
            best_posting_times=[
                "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
            ],
            engagement_factors={
                "title_optimization": 0.30,
                "thumbnail_quality": 0.25,
                "description_seo": 0.20,
                "posting_time": 0.15,
                "tags": 0.10
            }
        )
        
        # Add more platform rules
        self._add_additional_platform_rules(rules)
        
        return rules
    
    def _add_additional_platform_rules(self, rules: Dict[SocialPlatform, PlatformRules]) -> None:
        """Add additional platform rules"""
        
        # Twitter rules
        rules[SocialPlatform.TWITTER] = PlatformRules(
            platform=SocialPlatform.TWITTER,
            character_limits={
                "tweet": 280,
                "bio": 160,
                "thread": 280  # per tweet
            },
            hashtag_limits={
                "tweets": 2  # Recommended maximum
            },
            best_posting_times=[
                "08:00", "09:00", "12:00", "13:00", "17:00", "18:00"
            ],
            engagement_factors={
                "timing": 0.25,
                "hashtags": 0.15,
                "mentions": 0.20,
                "content_quality": 0.40
            }
        )
        
        # LinkedIn rules
        rules[SocialPlatform.LINKEDIN] = PlatformRules(
            platform=SocialPlatform.LINKEDIN,
            character_limits={
                "post": 3000,
                "headline": 220,
                "summary": 2000
            },
            hashtag_limits={
                "posts": 5
            },
            best_posting_times=[
                "07:45", "08:45", "12:00", "13:00", "17:00", "18:00"
            ],
            engagement_factors={
                "professional_tone": 0.35,
                "industry_relevance": 0.25,
                "posting_time": 0.20,
                "hashtags": 0.20
            }
        )
        
        # Facebook rules
        rules[SocialPlatform.FACEBOOK] = PlatformRules(
            platform=SocialPlatform.FACEBOOK,
            character_limits={
                "post": 63206,
                "recommended_post": 80  # For better engagement
            },
            hashtag_limits={
                "posts": 5  # Recommended maximum
            },
            best_posting_times=[
                "09:00", "13:00", "15:00", "18:00", "20:00"
            ],
            engagement_factors={
                "post_length": 0.20,
                "visual_content": 0.30,
                "engagement_bait": -0.15,  # Negative factor
                "timing": 0.25
            }
        )
    
    def _load_trending_data(self) -> None:
        """Load trending hashtags and content data"""
        
        # In a real implementation, this would fetch from APIs
        self.trending_hashtags = {
            SocialPlatform.INSTAGRAM: [
                "#trending", "#viral", "#explore", "#reels", "#instagood",
                "#photooftheday", "#love", "#beautiful", "#happy", "#picoftheday"
            ],
            SocialPlatform.TIKTOK: [
                "#fyp", "#foryou", "#viral", "#trending", "#tiktok",
                "#duet", "#dance", "#comedy", "#music", "#trend"
            ],
            SocialPlatform.YOUTUBE: [
                "#youtube", "#youtuber", "#subscribe", "#viral", "#trending",
                "#shorts", "#gaming", "#music", "#comedy", "#tutorial"
            ]
        }
        
        self.banned_hashtags = {
            SocialPlatform.INSTAGRAM: [
                "#follow4follow", "#like4like", "#followforfollow", "#likeforlike"
            ],
            SocialPlatform.TIKTOK: [
                "#followforfollow", "#like4like"
            ]
        }
    
    async def create_optimization_job(
        self,
        content: Dict[str, Any],
        target_platforms: List[SocialPlatform],
        content_type: ContentType,
        optimization_goals: List[OptimizationGoal],
        **kwargs
    ) -> str:
        """Create a new social media optimization job"""
        
        job_id = str(uuid.uuid4())
        
        job = OptimizationJob(
            job_id=job_id,
            content=content,
            target_platforms=target_platforms,
            content_type=content_type,
            optimization_goals=optimization_goals,
            target_audience=kwargs.get("target_audience", {}),
            brand_guidelines=kwargs.get("brand_guidelines", {}),
            custom_preferences=kwargs.get("custom_preferences", {})
        )
        
        self.active_jobs[job_id] = job
        
        self.logger.info(f"Created optimization job {job_id} for {len(target_platforms)} platforms")
        
        return job_id
    
    async def process_optimization_job(self, job_id: str) -> List[OptimizationResult]:
        """Process a social media optimization job"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        job.status = "processing"
        
        try:
            self.logger.info(f"Processing optimization job {job_id}")
            
            # Process each target platform
            for platform in job.target_platforms:
                try:
                    result = await self._optimize_for_platform(
                        job.content,
                        platform,
                        job.content_type,
                        job.optimization_goals,
                        job.target_audience,
                        job.brand_guidelines
                    )
                    
                    if result:
                        job.results.append(result)
                        self.optimization_stats["successful_optimizations"] += 1
                        
                        # Update platform stats
                        platform_name = platform.value
                        if platform_name not in self.optimization_stats["platforms_optimized"]:
                            self.optimization_stats["platforms_optimized"][platform_name] = 0
                        self.optimization_stats["platforms_optimized"][platform_name] += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to optimize for {platform.value}: {str(e)}")
            
            # Update job completion
            job.completed_at = datetime.now()
            job.status = "completed"
            
            # Update statistics
            self.optimization_stats["total_optimizations"] += 1
            
            if job.results:
                avg_score = sum(r.optimization_score for r in job.results) / len(job.results)
                self.optimization_stats["average_score_improvement"] = (
                    (self.optimization_stats["average_score_improvement"] * 
                     (self.optimization_stats["total_optimizations"] - 1) + avg_score) /
                    self.optimization_stats["total_optimizations"]
                )
            
            self.logger.info(
                f"Completed optimization job {job_id} with {len(job.results)} optimizations"
            )
            
            return job.results
            
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            self.logger.error(f"Error processing optimization job {job_id}: {str(e)}")
            raise
    
    async def _optimize_for_platform(
        self,
        content: Dict[str, Any],
        platform: SocialPlatform,
        content_type: ContentType,
        optimization_goals: List[OptimizationGoal],
        target_audience: Dict[str, Any],
        brand_guidelines: Dict[str, Any]
    ) -> Optional[OptimizationResult]:
        """Optimize content for a specific platform"""
        
        if platform not in self.platform_rules:
            self.logger.warning(f"No rules found for platform: {platform.value}")
            return None
        
        rules = self.platform_rules[platform]
        
        try:
            # Analyze original content
            analysis = await self._analyze_content(content)
            
            # Generate hashtag analysis
            hashtag_analysis = await self._analyze_hashtags(
                content.get("hashtags", []),
                platform,
                content_type
            )
            
            # Generate optimized content
            optimized_content = await self._generate_optimized_content(
                content, platform, rules, optimization_goals, target_audience
            )
            
            # Generate optimization suggestions
            suggestions = await self._generate_suggestions(
                content, platform, rules, analysis, optimization_goals
            )
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                content, optimized_content, analysis, platform, rules
            )
            
            # Estimate performance
            estimated_performance = self._estimate_performance(
                optimized_content, platform, analysis, hashtag_analysis
            )
            
            return OptimizationResult(
                platform=platform,
                content_type=content_type,
                original_content=content,
                optimized_content=optimized_content,
                analysis=analysis,
                hashtag_analysis=hashtag_analysis,
                suggestions=suggestions,
                optimization_score=optimization_score,
                estimated_performance=estimated_performance
            )
            
        except Exception as e:
            self.logger.error(f"Error optimizing for {platform.value}: {str(e)}")
            return None
    
    async def _analyze_content(self, content: Dict[str, Any]) -> ContentAnalysis:
        """Analyze content for optimization insights"""
        
        text_content = content.get("text", "") or content.get("caption", "") or content.get("title", "")
        
        analysis = ContentAnalysis()
        
        # Sentiment analysis
        if text_content:
            analysis.sentiment_score = await self._analyze_sentiment(text_content)
            analysis.emotion_scores = await self._analyze_emotions(text_content)
            analysis.readability_score = self._calculate_readability(text_content)
            analysis.keyword_density = self._analyze_keyword_density(text_content)
            analysis.tone_analysis = self._analyze_tone(text_content)
        
        # Content quality score
        analysis.content_quality_score = self._calculate_content_quality(content, analysis)
        
        # Engagement prediction (simplified)
        analysis.engagement_prediction = min(1.0, 
            0.3 * analysis.sentiment_score + 
            0.2 * analysis.readability_score + 
            0.5 * analysis.content_quality_score
        )
        
        return analysis
    
    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze text sentiment"""
        
        if self.sentiment_analyzer and text:
            try:
                result = self.sentiment_analyzer(text[:512])  # Limit text length
                
                # Convert to normalized score (-1 to 1)
                if result[0]["label"] == "POSITIVE":
                    return result[0]["score"]
                elif result[0]["label"] == "NEGATIVE":
                    return -result[0]["score"]
                else:
                    return 0.0
                    
            except Exception as e:
                self.logger.warning(f"Sentiment analysis failed: {e}")
        
        # Fallback sentiment analysis
        if HAS_TEXTBLOB:
            try:
                blob = TextBlob(text)
                return blob.sentiment.polarity
            except Exception:
                pass
        
        # Basic keyword-based sentiment
        positive_words = ["good", "great", "amazing", "awesome", "love", "best", "happy"]
        negative_words = ["bad", "worst", "hate", "terrible", "awful", "sad", "angry"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotional content of text"""
        
        if self.emotion_analyzer and text:
            try:
                results = self.emotion_analyzer(text[:512])
                emotions = {}
                
                for result in results:
                    emotions[result["label"].lower()] = result["score"]
                
                return emotions
                
            except Exception as e:
                self.logger.warning(f"Emotion analysis failed: {e}")
        
        # Fallback emotion analysis
        return {
            "joy": 0.5,
            "sadness": 0.1,
            "anger": 0.1,
            "fear": 0.1,
            "surprise": 0.1,
            "disgust": 0.1
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score"""
        
        if not text:
            return 0.0
        
        # Simple readability calculation
        sentences = len(re.split(r'[.!?]+', text))
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simplified Flesch Reading Ease
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale
        return max(0.0, min(1.0, flesch_score / 100))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_keyword_density(self, text: str) -> Dict[str, float]:
        """Analyze keyword density in text"""
        
        if not text:
            return {}
        
        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only count words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Calculate density and return top keywords
        keyword_density = {
            word: count / total_words 
            for word, count in word_counts.items()
        }
        
        # Return top 10 keywords
        return dict(sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_tone(self, text: str) -> Dict[str, Any]:
        """Analyze tone of the content"""
        
        # Simple tone analysis based on keywords and structure
        formal_indicators = ["therefore", "however", "furthermore", "consequently"]
        casual_indicators = ["lol", "omg", "btw", "gonna", "wanna"]
        
        text_lower = text.lower()
        
        formal_score = sum(1 for indicator in formal_indicators if indicator in text_lower)
        casual_score = sum(1 for indicator in casual_indicators if indicator in text_lower)
        
        # Determine primary tone
        if formal_score > casual_score:
            primary_tone = "formal"
        elif casual_score > formal_score:
            primary_tone = "casual"
        else:
            primary_tone = "neutral"
        
        return {
            "primary_tone": primary_tone,
            "formality_score": formal_score / (formal_score + casual_score + 1),
            "casualness_score": casual_score / (formal_score + casual_score + 1),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "emoji_count": len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
        }
    
    def _calculate_content_quality(self, content: Dict[str, Any], analysis: ContentAnalysis) -> float:
        """Calculate overall content quality score"""
        
        score = 0.0
        factors = 0
        
        # Text quality
        if content.get("text") or content.get("caption"):
            text = content.get("text", "") or content.get("caption", "")
            if text:
                score += analysis.readability_score * 0.3
                score += max(0, analysis.sentiment_score) * 0.2  # Positive sentiment is generally better
                factors += 0.5
        
        # Visual content
        if content.get("image_url") or content.get("video_url"):
            score += 0.8  # Assume good quality for now
            factors += 0.3
        
        # Structure and formatting
        if content.get("hashtags"):
            hashtag_quality = min(1.0, len(content["hashtags"]) / 10)  # Optimal around 10 hashtags
            score += hashtag_quality * 0.2
            factors += 0.2
        
        return score / max(1, factors)
    
    async def _analyze_hashtags(
        self,
        hashtags: List[str],
        platform: SocialPlatform,
        content_type: ContentType
    ) -> HashtagAnalysis:
        """Analyze and optimize hashtags for the platform"""
        
        analysis = HashtagAnalysis()
        
        # Get platform-specific trending hashtags
        trending = self.trending_hashtags.get(platform, [])
        banned = self.banned_hashtags.get(platform, [])
        
        # Filter out banned hashtags
        safe_hashtags = [tag for tag in hashtags if tag.lower() not in [b.lower() for b in banned]]
        
        # Categorize hashtags
        analysis.trending_hashtags = [tag for tag in safe_hashtags if tag in trending]
        analysis.niche_hashtags = [tag for tag in safe_hashtags if tag not in trending]
        analysis.banned_hashtags = [tag for tag in hashtags if tag in banned]
        
        # Generate recommendations
        analysis.recommended_hashtags = self._generate_hashtag_recommendations(
            hashtags, platform, content_type
        )
        
        # Calculate hashtag score
        analysis.hashtag_score = self._calculate_hashtag_score(safe_hashtags, platform)
        
        # Estimate reach (simplified)
        analysis.estimated_reach = self._estimate_hashtag_reach(safe_hashtags, platform)
        
        return analysis
    
    def _generate_hashtag_recommendations(
        self,
        current_hashtags: List[str],
        platform: SocialPlatform,
        content_type: ContentType
    ) -> List[str]:
        """Generate hashtag recommendations"""
        
        recommendations = []
        
        # Add trending hashtags for the platform
        trending = self.trending_hashtags.get(platform, [])
        recommendations.extend(trending[:5])
        
        # Add content-type specific hashtags
        content_hashtags = {
            ContentType.VIDEO: ["#video", "#content", "#creator"],
            ContentType.IMAGE: ["#photography", "#visual", "#art"],
            ContentType.POST: ["#post", "#social", "#engagement"],
            ContentType.STORY: ["#story", "#behindthescenes", "#daily"],
            ContentType.REEL: ["#reels", "#short", "#viral"]
        }
        
        if content_type in content_hashtags:
            recommendations.extend(content_hashtags[content_type])
        
        # Remove duplicates and current hashtags
        current_lower = [tag.lower() for tag in current_hashtags]
        recommendations = [tag for tag in recommendations if tag.lower() not in current_lower]
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _calculate_hashtag_score(self, hashtags: List[str], platform: SocialPlatform) -> float:
        """Calculate hashtag optimization score"""
        
        if not hashtags:
            return 0.0
        
        score = 0.0
        
        # Check hashtag count (optimal range varies by platform)
        optimal_counts = {
            SocialPlatform.INSTAGRAM: (10, 30),
            SocialPlatform.TIKTOK: (3, 5),
            SocialPlatform.TWITTER: (1, 2),
            SocialPlatform.LINKEDIN: (3, 5),
            SocialPlatform.FACEBOOK: (1, 3)
        }
        
        if platform in optimal_counts:
            min_optimal, max_optimal = optimal_counts[platform]
            count = len(hashtags)
            
            if min_optimal <= count <= max_optimal:
                score += 0.5
            else:
                # Penalty for too few or too many hashtags
                if count < min_optimal:
                    score += 0.5 * (count / min_optimal)
                else:
                    score += 0.5 * (max_optimal / count)
        
        # Check for trending hashtags
        trending = self.trending_hashtags.get(platform, [])
        trending_count = sum(1 for tag in hashtags if tag in trending)
        score += min(0.3, trending_count * 0.1)
        
        # Check hashtag diversity
        if len(set(hashtags)) == len(hashtags):  # No duplicates
            score += 0.2
        
        return min(1.0, score)
    
    def _estimate_hashtag_reach(self, hashtags: List[str], platform: SocialPlatform) -> int:
        """Estimate potential reach based on hashtags"""
        
        # Simplified reach estimation
        base_reach = {
            SocialPlatform.INSTAGRAM: 100,
            SocialPlatform.TIKTOK: 500,
            SocialPlatform.YOUTUBE: 50,
            SocialPlatform.TWITTER: 200,
            SocialPlatform.LINKEDIN: 80
        }
        
        reach = base_reach.get(platform, 100)
        
        # Multiply by hashtag count (with diminishing returns)
        hashtag_multiplier = min(10, len(hashtags)) * 1.5
        
        # Add trending hashtag bonus
        trending = self.trending_hashtags.get(platform, [])
        trending_bonus = sum(1 for tag in hashtags if tag in trending) * 100
        
        return int(reach * hashtag_multiplier + trending_bonus)
    
    async def _generate_optimized_content(
        self,
        content: Dict[str, Any],
        platform: SocialPlatform,
        rules: PlatformRules,
        optimization_goals: List[OptimizationGoal],
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimized content for the platform"""
        
        optimized = content.copy()
        
        # Optimize text content
        if "text" in content or "caption" in content:
            text_key = "text" if "text" in content else "caption"
            original_text = content[text_key]
            
            optimized_text = await self._optimize_text(
                original_text, platform, rules, optimization_goals
            )
            optimized[text_key] = optimized_text
        
        # Optimize title
        if "title" in content:
            optimized["title"] = await self._optimize_title(
                content["title"], platform, rules, optimization_goals
            )
        
        # Optimize hashtags
        if "hashtags" in content:
            optimized["hashtags"] = await self._optimize_hashtags(
                content["hashtags"], platform, rules
            )
        
        # Add platform-specific optimizations
        optimized = await self._apply_platform_specific_optimizations(
            optimized, platform, rules, optimization_goals
        )
        
        return optimized
    
    async def _optimize_text(
        self,
        text: str,
        platform: SocialPlatform,
        rules: PlatformRules,
        optimization_goals: List[OptimizationGoal]
    ) -> str:
        """Optimize text content for the platform"""
        
        optimized_text = text
        
        # Apply character limits
        char_limit = rules.character_limits.get("caption") or rules.character_limits.get("post")
        if char_limit and len(optimized_text) > char_limit:
            # Truncate while preserving meaning
            optimized_text = self._smart_truncate(optimized_text, char_limit)
        
        # Add platform-specific formatting
        if platform == SocialPlatform.INSTAGRAM:
            # Add line breaks for better readability
            optimized_text = self._format_for_instagram(optimized_text)
        elif platform == SocialPlatform.TWITTER:
            # Optimize for Twitter's format
            optimized_text = self._format_for_twitter(optimized_text)
        elif platform == SocialPlatform.LINKEDIN:
            # Professional formatting
            optimized_text = self._format_for_linkedin(optimized_text)
        
        return optimized_text
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """Intelligently truncate text while preserving meaning"""
        
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence) <= max_length - 3:  # Leave room for "..."
                truncated += sentence + ". "
            else:
                break
        
        if not truncated:
            # If no complete sentences fit, cut at word boundary
            words = text.split()
            truncated = ""
            for word in words:
                if len(truncated + word) <= max_length - 3:
                    truncated += word + " "
                else:
                    break
        
        return truncated.strip() + "..." if truncated else text[:max_length-3] + "..."
    
    def _format_for_instagram(self, text: str) -> str:
        """Format text for Instagram"""
        
        # Add line breaks for better readability
        sentences = text.split('. ')
        formatted = ""
        
        for i, sentence in enumerate(sentences):
            formatted += sentence
            if i < len(sentences) - 1:
                formatted += ".\n\n"
        
        return formatted
    
    def _format_for_twitter(self, text: str) -> str:
        """Format text for Twitter"""
        
        # Keep it concise and punchy
        return text.replace('\n\n', '\n')
    
    def _format_for_linkedin(self, text: str) -> str:
        """Format text for LinkedIn with professional tone"""
        
        # Add professional structure
        if not text.startswith(('I', 'We', 'This', 'Today', 'Recently')):
            # Add a professional opening if needed
            pass
        
        return text
    
    async def _optimize_title(
        self,
        title: str,
        platform: SocialPlatform,
        rules: PlatformRules,
        optimization_goals: List[OptimizationGoal]
    ) -> str:
        """Optimize title for the platform"""
        
        optimized_title = title
        
        # Apply character limits
        char_limit = rules.character_limits.get("title", 100)
        if len(optimized_title) > char_limit:
            optimized_title = self._smart_truncate(optimized_title, char_limit)
        
        # Add engagement-driving elements
        if OptimizationGoal.ENGAGEMENT in optimization_goals:
            optimized_title = self._add_engagement_elements(optimized_title, platform)
        
        return optimized_title
    
    def _add_engagement_elements(self, title: str, platform: SocialPlatform) -> str:
        """Add elements to drive engagement"""
        
        # Add question marks for questions
        engagement_starters = [
            "Did you know", "Have you ever", "What if", "Why do", "How to"
        ]
        
        # Check if title already has engagement elements
        has_question = "?" in title
        has_exclamation = "!" in title
        has_engagement_starter = any(starter in title for starter in engagement_starters)
        
        if not (has_question or has_exclamation or has_engagement_starter):
            # Could add engagement elements, but keep original for now
            pass
        
        return title
    
    async def _optimize_hashtags(
        self,
        hashtags: List[str],
        platform: SocialPlatform,
        rules: PlatformRules
    ) -> List[str]:
        """Optimize hashtags for the platform"""
        
        optimized_hashtags = hashtags.copy()
        
        # Get platform hashtag limits
        hashtag_limit = rules.hashtag_limits.get("posts", 30)
        
        # Remove banned hashtags
        banned = self.banned_hashtags.get(platform, [])
        optimized_hashtags = [tag for tag in optimized_hashtags if tag.lower() not in [b.lower() for b in banned]]
        
        # Add trending hashtags if space allows
        trending = self.trending_hashtags.get(platform, [])
        for tag in trending:
            if len(optimized_hashtags) < hashtag_limit and tag not in optimized_hashtags:
                optimized_hashtags.append(tag)
        
        # Trim to platform limits
        return optimized_hashtags[:hashtag_limit]
    
    async def _apply_platform_specific_optimizations(
        self,
        content: Dict[str, Any],
        platform: SocialPlatform,
        rules: PlatformRules,
        optimization_goals: List[OptimizationGoal]
    ) -> Dict[str, Any]:
        """Apply platform-specific optimizations"""
        
        optimized = content.copy()
        
        if platform == SocialPlatform.YOUTUBE:
            # Add YouTube-specific optimizations
            if "description" in content:
                # Optimize description for SEO
                optimized["description"] = self._optimize_youtube_description(content["description"])
        
        elif platform == SocialPlatform.TIKTOK:
            # Add TikTok-specific optimizations
            optimized["use_trending_sounds"] = True
            optimized["add_text_overlay"] = True
        
        elif platform == SocialPlatform.INSTAGRAM:
            # Add Instagram-specific optimizations
            optimized["use_stories"] = True
            optimized["enable_shopping_tags"] = True
        
        return optimized
    
    def _optimize_youtube_description(self, description: str) -> str:
        """Optimize YouTube description for SEO"""
        
        # Add common YouTube SEO elements
        if "subscribe" not in description.lower():
            description += "\n\nDon't forget to subscribe for more content!"
        
        if "comment" not in description.lower():
            description += "\nLet us know your thoughts in the comments below!"
        
        return description
    
    async def _generate_suggestions(
        self,
        content: Dict[str, Any],
        platform: SocialPlatform,
        rules: PlatformRules,
        analysis: ContentAnalysis,
        optimization_goals: List[OptimizationGoal]
    ) -> OptimizationSuggestions:
        """Generate optimization suggestions"""
        
        suggestions = OptimizationSuggestions()
        
        # Title suggestions
        if "title" in content:
            suggestions.title_suggestions = self._generate_title_suggestions(
                content["title"], platform, optimization_goals
            )
        
        # Caption suggestions
        text_content = content.get("text", "") or content.get("caption", "")
        if text_content:
            suggestions.caption_suggestions = self._generate_caption_suggestions(
                text_content, platform, analysis
            )
        
        # Hashtag suggestions
        current_hashtags = content.get("hashtags", [])
        suggestions.hashtag_suggestions = self._generate_hashtag_recommendations(
            current_hashtags, platform, ContentType.POST
        )
        
        # Posting time suggestions
        suggestions.posting_time_suggestions = rules.best_posting_times
        
        # Content improvement suggestions
        suggestions.content_improvements = self._generate_content_improvements(
            content, analysis, platform
        )
        
        # CTA suggestions
        suggestions.cta_suggestions = self._generate_cta_suggestions(platform, optimization_goals)
        
        # Visual suggestions
        suggestions.visual_suggestions = self._generate_visual_suggestions(platform, content)
        
        return suggestions
    
    def _generate_title_suggestions(
        self,
        current_title: str,
        platform: SocialPlatform,
        optimization_goals: List[OptimizationGoal]
    ) -> List[str]:
        """Generate title suggestions"""
        
        suggestions = []
        
        # Add question format
        if "?" not in current_title:
            suggestions.append(f"What if {current_title.lower()}?")
        
        # Add how-to format
        if not current_title.lower().startswith("how to"):
            suggestions.append(f"How to {current_title.lower()}")
        
        # Add numbered list format
        if not any(char.isdigit() for char in current_title):
            suggestions.append(f"5 Ways to {current_title.lower()}")
        
        return suggestions[:3]
    
    def _generate_caption_suggestions(
        self,
        current_caption: str,
        platform: SocialPlatform,
        analysis: ContentAnalysis
    ) -> List[str]:
        """Generate caption suggestions"""
        
        suggestions = []
        
        # Suggest adding emojis if none present
        if analysis.tone_analysis.get("emoji_count", 0) == 0:
            suggestions.append("Add relevant emojis to increase engagement")
        
        # Suggest adding questions
        if analysis.tone_analysis.get("question_count", 0) == 0:
            suggestions.append("Add a question to encourage comments")
        
        # Suggest call-to-action
        cta_words = ["comment", "share", "like", "follow", "tag", "save"]
        if not any(word in current_caption.lower() for word in cta_words):
            suggestions.append("Add a clear call-to-action")
        
        return suggestions
    
    def _generate_content_improvements(
        self,
        content: Dict[str, Any],
        analysis: ContentAnalysis,
        platform: SocialPlatform
    ) -> List[str]:
        """Generate content improvement suggestions"""
        
        improvements = []
        
        # Readability improvements
        if analysis.readability_score < 0.6:
            improvements.append("Simplify language for better readability")
        
        # Sentiment improvements
        if analysis.sentiment_score < 0:
            improvements.append("Consider using more positive language")
        
        # Length improvements
        text_content = content.get("text", "") or content.get("caption", "")
        if len(text_content) < 50:
            improvements.append("Consider adding more detailed content")
        
        return improvements
    
    def _generate_cta_suggestions(
        self,
        platform: SocialPlatform,
        optimization_goals: List[OptimizationGoal]
    ) -> List[str]:
        """Generate call-to-action suggestions"""
        
        ctas = []
        
        if OptimizationGoal.ENGAGEMENT in optimization_goals:
            ctas.extend([
                "What's your opinion on this?",
                "Tag someone who needs to see this!",
                "Double tap if you agree!",
                "Save this for later!"
            ])
        
        if OptimizationGoal.FOLLOWERS in optimization_goals:
            ctas.extend([
                "Follow for more content like this!",
                "Turn on notifications to never miss a post!"
            ])
        
        if OptimizationGoal.CONVERSIONS in optimization_goals:
            ctas.extend([
                "Link in bio for more information!",
                "Swipe up to learn more!",
                "Check out our story for details!"
            ])
        
        return ctas[:5]
    
    def _generate_visual_suggestions(
        self,
        platform: SocialPlatform,
        content: Dict[str, Any]
    ) -> List[str]:
        """Generate visual content suggestions"""
        
        suggestions = []
        
        if platform == SocialPlatform.INSTAGRAM:
            suggestions.extend([
                "Use bright, high-contrast colors",
                "Include faces in your photos",
                "Create carousel posts for better engagement",
                "Add text overlays to images"
            ])
        
        elif platform == SocialPlatform.TIKTOK:
            suggestions.extend([
                "Use trending audio tracks",
                "Add captions/subtitles to videos",
                "Include quick cuts and transitions",
                "Film in vertical format (9:16)"
            ])
        
        elif platform == SocialPlatform.YOUTUBE:
            suggestions.extend([
                "Create eye-catching thumbnails",
                "Use consistent branding",
                "Add end screens and annotations",
                "Include good lighting and audio quality"
            ])
        
        return suggestions
    
    def _calculate_optimization_score(
        self,
        original_content: Dict[str, Any],
        optimized_content: Dict[str, Any],
        analysis: ContentAnalysis,
        platform: SocialPlatform,
        rules: PlatformRules
    ) -> float:
        """Calculate optimization score"""
        
        score = 0.0
        factors = 0
        
        # Text optimization score
        original_text = original_content.get("text", "") or original_content.get("caption", "")
        optimized_text = optimized_content.get("text", "") or optimized_content.get("caption", "")
        
        if original_text and optimized_text:
            # Character count optimization
            char_limit = rules.character_limits.get("caption") or rules.character_limits.get("post", 1000)
            if len(optimized_text) <= char_limit:
                score += 0.2
            factors += 0.2
        
        # Hashtag optimization score
        original_hashtags = original_content.get("hashtags", [])
        optimized_hashtags = optimized_content.get("hashtags", [])
        
        if optimized_hashtags:
            hashtag_score = self._calculate_hashtag_score(optimized_hashtags, platform)
            score += hashtag_score * 0.3
            factors += 0.3
        
        # Content quality score
        score += analysis.content_quality_score * 0.3
        factors += 0.3
        
        # Engagement prediction
        score += analysis.engagement_prediction * 0.2
        factors += 0.2
        
        return score / max(1, factors)
    
    def _estimate_performance(
        self,
        content: Dict[str, Any],
        platform: SocialPlatform,
        analysis: ContentAnalysis,
        hashtag_analysis: HashtagAnalysis
    ) -> Dict[str, Any]:
        """Estimate content performance"""
        
        base_metrics = {
            SocialPlatform.INSTAGRAM: {
                "likes": 100,
                "comments": 10,
                "shares": 5,
                "saves": 8
            },
            SocialPlatform.TIKTOK: {
                "views": 1000,
                "likes": 50,
                "comments": 5,
                "shares": 10
            },
            SocialPlatform.YOUTUBE: {
                "views": 500,
                "likes": 25,
                "comments": 8,
                "subscribers": 2
            }
        }
        
        platform_base = base_metrics.get(platform, {
            "engagement": 50,
            "reach": 200
        })
        
        # Apply multipliers based on analysis
        multiplier = 1.0
        multiplier += analysis.engagement_prediction * 0.5
        multiplier += hashtag_analysis.hashtag_score * 0.3
        multiplier += analysis.content_quality_score * 0.2
        
        # Apply estimated performance
        estimated = {}
        for metric, base_value in platform_base.items():
            estimated[metric] = int(base_value * multiplier)
        
        estimated["estimated_reach"] = hashtag_analysis.estimated_reach
        estimated["confidence"] = min(0.95, 0.6 + analysis.content_quality_score * 0.35)
        
        return estimated
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an optimization job"""
        
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "target_platforms": [p.value for p in job.target_platforms],
            "content_type": job.content_type.value,
            "optimization_goals": [g.value for g in job.optimization_goals],
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results_count": len(job.results),
            "results": [
                {
                    "platform": r.platform.value,
                    "optimization_score": r.optimization_score,
                    "estimated_performance": r.estimated_performance
                } for r in job.results
            ]
        }
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization system statistics"""
        
        return {
            **self.optimization_stats,
            "active_jobs": len(self.active_jobs),
            "supported_platforms": len(self.platform_rules),
            "ai_models_available": HAS_TRANSFORMERS
        }


# Global instance for easy access
_social_media_optimizer = None

def get_social_media_optimizer(config: Optional[Dict[str, Any]] = None) -> SocialMediaOptimizer:
    """Get or create global social media optimizer instance"""
    global _social_media_optimizer
    
    if _social_media_optimizer is None:
        _social_media_optimizer = SocialMediaOptimizer(config)
    
    return _social_media_optimizer


# Example usage and testing
if __name__ == "__main__":
    async def example_usage():
        """Example usage of the Social Media Optimizer"""
        
        # Initialize the system
        optimizer = get_social_media_optimizer()
        
        # Example content to optimize
        content = {
            "title": "Amazing Travel Experience",
            "caption": "Just had the most incredible travel experience! The views were breathtaking and the culture was so rich. Definitely recommend visiting this place!",
            "hashtags": ["#travel", "#adventure", "#culture", "#amazing"],
            "image_url": "https://example.com/travel-photo.jpg"
        }
        
        # Create optimization job
        job_id = await optimizer.create_optimization_job(
            content=content,
            target_platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK],
            content_type=ContentType.POST,
            optimization_goals=[OptimizationGoal.ENGAGEMENT, OptimizationGoal.REACH]
        )
        
        print(f"Created optimization job: {job_id}")
        
        # Process the job
        results = await optimizer.process_optimization_job(job_id)
        
        print(f"Optimization completed with {len(results)} results:")
        for result in results:
            print(f"\n{result.platform.value}:")
            print(f"  Optimization Score: {result.optimization_score:.2f}")
            print(f"  Estimated Performance: {result.estimated_performance}")
            print(f"  Hashtag Suggestions: {result.hashtag_analysis.recommended_hashtags[:5]}")
        
        # Get statistics
        stats = optimizer.get_optimization_statistics()
        print(f"\nOptimization statistics: {json.dumps(stats, indent=2)}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())