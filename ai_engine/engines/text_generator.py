"""Advanced Text Content Generator Engine

Enterprise-grade specialized text content generation engine for the IA-Influencer platform.
Provides ultra-advanced text generation capabilities for multi-format content creators with 
AI-powered SEO optimization, collaboration matching, and monetization strategies.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written consent from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will face legal action under international copyright law.

⚖️ LEGAL NOTICE: THEFT OF IDEAS, CONCEPTS, OR CODE WITHOUT EXPLICIT WRITTEN AUTHORIZATION  
FROM FAHED MLAIEL (mlaiel@live.de) IS STRICTLY FORBIDDEN AND WILL RESULT  
IN IMMEDIATE LEGAL PROSECUTION UNDER INTERNATIONAL COPYRIGHT LAW.

🔒 NO UNAUTHORIZED USE, COPYING, MODIFICATION, OR DISTRIBUTION ALLOWED.

Business Logic: User Upload → AI Processing → Protection → SEO → Collaboration → Distribution
"""
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import re
from pathlib import Path

# Re-export from text_engine for compatibility
from .text_engine import TextGenerationEngine as TextContentGenerator

# Enhanced text generation capabilities
from .base_engine import BaseContentEngine, EngineStatus, ProcessingPriority, ContentType, EngineMetrics


class TextContentStyle(Enum):
    """Advanced text content style types for creators"""    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    SOCIAL_MEDIA = "social_media"
    BLOG_POST = "blog_post"
    NEWS_ARTICLE = "news_article"
    MARKETING_COPY = "marketing_copy"
    STORYTELLING = "storytelling"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    DOCUMENTARY = "documentary"
    INFLUENCER = "influencer"
    BRAND_VOICE = "brand_voice"


class ContentFormat(Enum):
    """Supported content output formats"""    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    STRUCTURED = "structured"
    SOCIAL_POST = "social_post"
    BLOG_ARTICLE = "blog_article"
    NEWSLETTER = "newsletter"
    SCRIPT = "script"
    TRANSCRIPT = "transcript"
    CAPTIONS = "captions"
    DESCRIPTION = "description"
    HASHTAGS = "hashtags"
    KEYWORDS = "keywords"


@dataclass
class TextGenerationRequest:
    """Advanced text generation request configuration"""    content_type: ContentType
    style: TextContentStyle
    format: ContentFormat
    target_length: int
    target_audience: str
    keywords: List[str] = field(default_factory=list)
    tone: str = "neutral"
    language: str = "en"
    seo_optimization: bool = True
    include_hashtags: bool = False
    include_call_to_action: bool = False
    brand_voice: Optional[str] = None
    collaboration_intent: bool = False
    monetization_focus: bool = False
    platform_optimization: List[str] = field(default_factory=list)
    custom_prompt: Optional[str] = None
    creativity_level: float = 0.7
    factual_accuracy: float = 0.9
    engagement_optimization: bool = True


@dataclass
class TextGenerationResult:
    """Comprehensive text generation result with analytics"""    generated_text: str
    style_score: float
    seo_score: float
    engagement_score: float
    readability_score: float
    uniqueness_score: float
    word_count: int
    character_count: int
    estimated_reading_time: int
    suggested_hashtags: List[str]
    extracted_keywords: List[str]
    sentiment_analysis: Dict[str, float]
    monetization_potential: float
    collaboration_opportunities: List[str]
    platform_recommendations: List[str]
    improvement_suggestions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


class AdvancedTextGenerator:
    """    Enterprise-grade text content generator with AI-powered optimization.
    
    Supports advanced text generation for content creators with integrated
    SEO optimization, collaboration matching, and monetization strategies.
    """    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        max_concurrent_requests: int = 10,
        default_temperature: float = 0.7,
        enable_analytics: bool = True
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.max_concurrent_requests = max_concurrent_requests
        self.default_temperature = default_temperature
        self.enable_analytics = enable_analytics
        
        # Performance tracking
        self.metrics = EngineMetrics()
        self.logger = logging.getLogger(__name__)
        
        # Text analysis models
        self._initialize_analysis_models()
        
        # Content templates
        self._load_content_templates()
        
        # SEO optimization rules
        self._initialize_seo_rules()
        
    def _initialize_analysis_models(self):
        """Initialize text analysis and processing models"""        # Sentiment analysis
        self.sentiment_analyzer = None
        
        # Readability assessment
        self.readability_analyzer = None
        
        # SEO analysis
        self.seo_analyzer = None
        
        # Keyword extraction
        self.keyword_extractor = None
        
        # Style classification
        self.style_classifier = None
        
    def _load_content_templates(self):
        """Load content generation templates"""        self.templates = {
            TextContentStyle.SOCIAL_MEDIA: {
                "structure": "hook + content + cta + hashtags",
                "max_length": 280,
                "engagement_focus": True
            },
            TextContentStyle.BLOG_POST: {
                "structure": "title + intro + body + conclusion",
                "min_length": 500,
                "seo_focus": True
            },
            TextContentStyle.MARKETING_COPY: {
                "structure": "headline + benefits + proof + cta",
                "conversion_focus": True
            },
            TextContentStyle.STORYTELLING: {
                "structure": "setup + conflict + resolution",
                "emotion_focus": True
            }
        }
        
    def _initialize_seo_rules(self):
        """Initialize SEO optimization rules"""        self.seo_rules = {
            "keyword_density": {"min": 0.5, "max": 2.5},
            "title_length": {"min": 30, "max": 60},
            "meta_description": {"min": 150, "max": 160},
            "headings": {"h1": 1, "h2_min": 2, "h3_min": 1},
            "internal_links": {"min": 2, "max": 8},
            "external_links": {"min": 1, "max": 3},
            "readability": {"flesch_min": 60, "fog_max": 12}
        }
        
    async def generate_content(
        self,
        request: TextGenerationRequest
    ) -> TextGenerationResult:
        """        Generate advanced text content with comprehensive optimization.
        
        Args:
            request: Text generation configuration and requirements
            
        Returns:
            TextGenerationResult: Complete generation result with analytics
        """        start_time = time.time()
        
        try:
            # Pre-processing and prompt engineering
            optimized_prompt = await self._create_optimized_prompt(request)
            
            # Generate base content
            generated_text = await self._generate_base_content(
                optimized_prompt, request
            )
            
            # Post-processing optimization
            optimized_text = await self._optimize_content(
                generated_text, request
            )
            
            # Comprehensive analysis
            analysis_result = await self._analyze_content(
                optimized_text, request
            )
            
            # Build result
            result = TextGenerationResult(
                generated_text=optimized_text,
                style_score=analysis_result["style_score"],
                seo_score=analysis_result["seo_score"],
                engagement_score=analysis_result["engagement_score"],
                readability_score=analysis_result["readability_score"],
                uniqueness_score=analysis_result["uniqueness_score"],
                word_count=len(optimized_text.split()),
                character_count=len(optimized_text),
                estimated_reading_time=self._calculate_reading_time(optimized_text),
                suggested_hashtags=analysis_result["hashtags"],
                extracted_keywords=analysis_result["keywords"],
                sentiment_analysis=analysis_result["sentiment"],
                monetization_potential=analysis_result["monetization_score"],
                collaboration_opportunities=analysis_result["collaborations"],
                platform_recommendations=analysis_result["platforms"],
                improvement_suggestions=analysis_result["improvements"],
                processing_time=time.time() - start_time
            )
            
            # Update metrics
            self.metrics.total_processed += 1
            self.metrics.successful_processed += 1
            self.metrics.average_processing_time = (
                (self.metrics.average_processing_time * (self.metrics.total_processed - 1) + 
                 result.processing_time) / self.metrics.total_processed
            )
            
            return result
            
        except Exception as e:
            self.metrics.failed_processed += 1
            self.logger.error(f"Text generation failed: {str(e)}")
            raise
            
    async def _create_optimized_prompt(
        self,
        request: TextGenerationRequest
    ) -> str:
        """Create optimized prompt for text generation"""        base_prompt = f"""        Generate {request.content_type.value} content with the following specifications:
        
        Style: {request.style.value}
        Format: {request.format.value}
        Target Length: {request.target_length} words
        Target Audience: {request.target_audience}
        Tone: {request.tone}
        Language: {request.language}
        
        Keywords to include: {', '.join(request.keywords)}
        """        
        if request.seo_optimization:
            base_prompt += "\nOptimize for search engines with natural keyword integration."
            
        if request.include_hashtags:
            base_prompt += "\nInclude relevant hashtags at the end."
            
        if request.include_call_to_action:
            base_prompt += "\nInclude a compelling call-to-action."
            
        if request.brand_voice:
            base_prompt += f"\nMaintain brand voice: {request.brand_voice}"
            
        if request.collaboration_intent:
            base_prompt += "\nInclude collaboration opportunities and networking elements."
            
        if request.monetization_focus:
            base_prompt += "\nFocus on monetization potential and revenue opportunities."
            
        if request.platform_optimization:
            platforms = ', '.join(request.platform_optimization)
            base_prompt += f"\nOptimize for platforms: {platforms}"
            
        if request.custom_prompt:
            base_prompt += f"\n\nAdditional requirements: {request.custom_prompt}"
            
        return base_prompt
        
    async def _generate_base_content(
        self,
        prompt: str,
        request: TextGenerationRequest
    ) -> str:
        """Generate base content using AI model"""        # Implementation would integrate with actual AI model
        # For now, return structured content based on style
        
        template = self.templates.get(request.style, {})
        
        if request.style == TextContentStyle.SOCIAL_MEDIA:
            content = self._generate_social_media_content(request)
        elif request.style == TextContentStyle.BLOG_POST:
            content = self._generate_blog_content(request)
        elif request.style == TextContentStyle.MARKETING_COPY:
            content = self._generate_marketing_content(request)
        else:
            content = self._generate_generic_content(request)
            
        return content
        
    def _generate_social_media_content(self, request: TextGenerationRequest) -> str:
        """Generate optimized social media content"""        hook = f"🚀 {request.target_audience}, this is for you!"
        content = f"Discover amazing {request.keywords[0] if request.keywords else 'content'} that will transform your experience."
        cta = "👇 Share your thoughts in the comments!"
        hashtags = f"#{' #'.join(request.keywords[:5])}" if request.keywords else "#content #creation"
        
        return f"{hook}\n\n{content}\n\n{cta}\n\n{hashtags}"
        
    def _generate_blog_content(self, request: TextGenerationRequest) -> str:
        """Generate SEO-optimized blog content"""        title = f"The Ultimate Guide to {request.keywords[0].title() if request.keywords else 'Content Creation'}"
        intro = f"In today's digital landscape, {request.target_audience} need to understand the importance of {request.keywords[0] if request.keywords else 'quality content'}."
        
        body_sections = []
        for i, keyword in enumerate(request.keywords[:3], 1):
            section = f"\n## {i}. Understanding {keyword.title()}\n\n"
            section += f"When it comes to {keyword}, {request.target_audience} should focus on creating value-driven content that resonates with their audience. "
            section += f"This approach not only improves engagement but also enhances the overall user experience."
            body_sections.append(section)
        
        conclusion = f"\n## Conclusion\n\nMastering {', '.join(request.keywords[:2]) if len(request.keywords) >= 2 else 'content creation'} is essential for {request.target_audience} looking to succeed in the digital space. "
        conclusion += "By implementing these strategies, you'll be well on your way to creating impactful content that drives results."
        
        return f"# {title}\n\n{intro}\n\n{''.join(body_sections)}\n\n{conclusion}"
        
    def _generate_marketing_content(self, request: TextGenerationRequest) -> str:
        """Generate conversion-focused marketing content"""        headline = f"Transform Your {request.keywords[0].title() if request.keywords else 'Business'} Today!"
        benefits = f"✅ Increase engagement\n✅ Boost conversions\n✅ Maximize ROI"
        proof = f"Join thousands of {request.target_audience} who have already achieved success."
        cta = "🚀 Get Started Now - Limited Time Offer!"
        
        return f"{headline}\n\n{benefits}\n\n{proof}\n\n{cta}"
        
    def _generate_generic_content(self, request: TextGenerationRequest) -> str:
        """Generate generic content based on request parameters"""        content = f"Creating exceptional {request.content_type.value} content for {request.target_audience} requires careful consideration of multiple factors. "
        
        if request.keywords:
            content += f"Key areas to focus on include {', '.join(request.keywords[:3])}. "
            
        content += f"By maintaining a {request.tone} tone and targeting the right audience, content creators can achieve remarkable results."
        
        if request.include_call_to_action:
            content += "\n\n📢 Ready to take your content to the next level? Start implementing these strategies today!"
            
        return content
        
    async def _optimize_content(
        self,
        content: str,
        request: TextGenerationRequest
    ) -> str:
        """Optimize generated content for specific requirements"""        optimized = content
        
        # Length optimization
        if request.target_length > 0:
            optimized = self._adjust_content_length(optimized, request.target_length)
            
        # SEO optimization
        if request.seo_optimization:
            optimized = self._apply_seo_optimization(optimized, request)
            
        # Platform optimization
        if request.platform_optimization:
            optimized = self._optimize_for_platforms(optimized, request.platform_optimization)
            
        return optimized
        
    def _adjust_content_length(self, content: str, target_length: int) -> str:
        """Adjust content to target length"""        words = content.split()
        current_length = len(words)
        
        if current_length > target_length:
            # Trim content
            return ' '.join(words[:target_length])
        elif current_length < target_length * 0.8:
            # Expand content
            expansion = " This approach ensures comprehensive coverage of the topic while maintaining quality and relevance for the target audience."
            return content + expansion
            
        return content
        
    def _apply_seo_optimization(self, content: str, request: TextGenerationRequest) -> str:
        """Apply SEO optimization techniques"""        optimized = content
        
        # Ensure keyword presence
        for keyword in request.keywords[:3]:
            if keyword.lower() not in optimized.lower():
                optimized += f" {keyword.title()} is an important consideration for content creators."
                
        return optimized
        
    def _optimize_for_platforms(self, content: str, platforms: List[str]) -> str:
        """Optimize content for specific platforms"""        optimized = content
        
        for platform in platforms:
            if platform.lower() == "twitter":
                # Ensure content fits Twitter character limit
                if len(optimized) > 280:
                    optimized = optimized[:277] + "..."
            elif platform.lower() == "linkedin":
                # Add professional tone
                if not optimized.startswith(("As a", "In my", "I believe")):
                    optimized = "As professionals in the industry, " + optimized.lower()
                    
        return optimized
        
    async def _analyze_content(
        self,
        content: str,
        request: TextGenerationRequest
    ) -> Dict[str, Any]:
        """Perform comprehensive content analysis"""        analysis = {
            "style_score": self._calculate_style_score(content, request),
            "seo_score": self._calculate_seo_score(content, request),
            "engagement_score": self._calculate_engagement_score(content),
            "readability_score": self._calculate_readability_score(content),
            "uniqueness_score": self._calculate_uniqueness_score(content),
            "hashtags": self._extract_hashtags(content, request),
            "keywords": self._extract_keywords(content),
            "sentiment": self._analyze_sentiment(content),
            "monetization_score": self._calculate_monetization_potential(content),
            "collaborations": self._identify_collaboration_opportunities(content),
            "platforms": self._recommend_platforms(content, request),
            "improvements": self._suggest_improvements(content, request)
        }
        
        return analysis
        
    def _calculate_style_score(self, content: str, request: TextGenerationRequest) -> float:
        """Calculate style consistency score"""        # Simplified scoring based on style characteristics
        style_indicators = {
            TextContentStyle.PROFESSIONAL: ["furthermore", "therefore", "consequently"],
            TextContentStyle.CASUAL: ["hey", "awesome", "cool", "great"],
            TextContentStyle.CREATIVE: ["imagine", "discover", "transform", "amazing"],
            TextContentStyle.SOCIAL_MEDIA: ["🚀", "👇", "✅", "#"]
        }
        
        indicators = style_indicators.get(request.style, [])
        matches = sum(1 for indicator in indicators if indicator in content.lower())
        
        return min(1.0, matches / max(1, len(indicators)))
        
    def _calculate_seo_score(self, content: str, request: TextGenerationRequest) -> float:
        """Calculate SEO optimization score"""        score = 0.0
        content_lower = content.lower()
        
        # Keyword presence
        keyword_score = 0
        for keyword in request.keywords:
            if keyword.lower() in content_lower:
                keyword_score += 1
        score += (keyword_score / max(1, len(request.keywords))) * 0.4
        
        # Content length
        word_count = len(content.split())
        if 300 <= word_count <= 1500:
            score += 0.2
        
        # Header presence (simplified)
        if any(marker in content for marker in ["#", "**", "##"]):
            score += 0.2
        
        # Call-to-action presence
        cta_indicators = ["click", "learn more", "get started", "contact", "subscribe"]
        if any(cta in content_lower for cta in cta_indicators):
            score += 0.2
            
        return min(1.0, score)
        
    def _calculate_engagement_score(self, content: str) -> float:
        """Calculate content engagement potential score"""        engagement_indicators = [
            "?", "!", "you", "your", "we", "us", "share", "comment",
            "like", "follow", "subscribe", "join", "discover"
        ]
        
        content_lower = content.lower()
        matches = sum(1 for indicator in engagement_indicators if indicator in content_lower)
        
        return min(1.0, matches / 10)
        
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score"""        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
            
        avg_sentence_length = len(words) / len(sentences)
        
        # Simplified readability score
        if avg_sentence_length <= 15:
            return 1.0
        elif avg_sentence_length <= 20:
            return 0.8
        elif avg_sentence_length <= 25:
            return 0.6
        else:
            return 0.4
            
    def _calculate_uniqueness_score(self, content: str) -> float:
        """Calculate content uniqueness score"""        # Simplified uniqueness calculation
        words = set(content.lower().split())
        unique_ratio = len(words) / max(1, len(content.split()))
        return min(1.0, unique_ratio * 1.2)
        
    def _extract_hashtags(self, content: str, request: TextGenerationRequest) -> List[str]:
        """Extract and suggest relevant hashtags"""        existing_hashtags = re.findall(r'#\w+', content)
        
        # Generate hashtags from keywords
        suggested = []
        for keyword in request.keywords[:5]:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            if hashtag not in existing_hashtags:
                suggested.append(hashtag)
                
        # Add general hashtags based on content type
        general_hashtags = {
            ContentType.AUDIO: ["#audio", "#music", "#sound"],
            ContentType.VIDEO: ["#video", "#content", "#creator"],
            ContentType.IMAGE: ["#photography", "#visual", "#art"],
            ContentType.TEXT: ["#writing", "#content", "#blog"]
        }
        
        for hashtag in general_hashtags.get(request.content_type, [])[:2]:
            if hashtag not in existing_hashtags and hashtag not in suggested:
                suggested.append(hashtag)
                
        return existing_hashtags + suggested[:8]
        
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""        # Simplified keyword extraction
        words = re.findall(r'\b\w{4,}\b', content.lower())
        
        # Filter common words
        stop_words = {
            "that", "this", "with", "have", "will", "from", "they", "been",
            "were", "their", "said", "what", "your", "when", "more", "than"
        }
        
        keywords = [word for word in words if word not in stop_words]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]
        
    def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze content sentiment"""        # Simplified sentiment analysis
        positive_words = ["great", "amazing", "excellent", "good", "best", "love", "awesome"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible"]
        neutral_words = ["okay", "fine", "normal", "standard", "average"]
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        neutral_count = sum(1 for word in neutral_words if word in content_lower)
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return {"positive": 0.6, "negative": 0.2, "neutral": 0.2}
            
        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": neutral_count / total
        }
        
    def _calculate_monetization_potential(self, content: str) -> float:
        """Calculate monetization potential score"""        monetization_indicators = [
            "buy", "purchase", "premium", "subscription", "exclusive",
            "limited", "offer", "discount", "price", "value", "investment"
        ]
        
        content_lower = content.lower()
        matches = sum(1 for indicator in monetization_indicators if indicator in content_lower)
        
        return min(1.0, matches / 5)
        
    def _identify_collaboration_opportunities(self, content: str) -> List[str]:
        """Identify potential collaboration opportunities"""        opportunities = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["partner", "collaborate", "team", "together"]):
            opportunities.append("Content Collaboration")
            
        if any(word in content_lower for word in ["brand", "sponsor", "promotion"]):
            opportunities.append("Brand Partnership")
            
        if any(word in content_lower for word in ["guest", "interview", "feature"]):
            opportunities.append("Guest Appearance")
            
        if any(word in content_lower for word in ["cross", "share", "mutual"]):
            opportunities.append("Cross-Promotion")
            
        return opportunities[:3]
        
    def _recommend_platforms(self, content: str, request: TextGenerationRequest) -> List[str]:
        """Recommend optimal platforms for content"""        platforms = []
        content_lower = content.lower()
        
        # Platform recommendations based on content characteristics
        if len(content) <= 280:
            platforms.append("Twitter")
            
        if request.style == TextContentStyle.PROFESSIONAL:
            platforms.append("LinkedIn")
            
        if request.content_type in [ContentType.IMAGE, ContentType.VIDEO]:
            platforms.extend(["Instagram", "TikTok"])
            
        if request.style == TextContentStyle.BLOG_POST:
            platforms.extend(["Medium", "WordPress"])
            
        if any(word in content_lower for word in ["music", "audio", "sound"]):
            platforms.extend(["Spotify", "SoundCloud"])
            
        return list(set(platforms))[:5]
        
    def _suggest_improvements(self, content: str, request: TextGenerationRequest) -> List[str]:
        """Suggest content improvements"""        suggestions = []
        
        word_count = len(content.split())
        
        if word_count < 50:
            suggestions.append("Expand content with more detailed information")
            
        if not any(char in content for char in "!?"):
            suggestions.append("Add engaging punctuation for better readability")
            
        if request.seo_optimization and not any(keyword.lower() in content.lower() for keyword in request.keywords):
            suggestions.append("Include target keywords naturally in the content")
            
        if request.include_call_to_action and not any(cta in content.lower() for cta in ["click", "subscribe", "follow", "share"]):
            suggestions.append("Add a clear call-to-action")
            
        if len(content.split('.')) < 3:
            suggestions.append("Break content into shorter sentences for better readability")
            
        return suggestions[:5]
        
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in seconds"""        word_count = len(content.split())
        # Average reading speed: 200-250 words per minute
        reading_time_minutes = word_count / 225
        return int(reading_time_minutes * 60)


# Enhanced exports
__all__ = [
    "TextContentGenerator",
    "AdvancedTextGenerator", 
    "TextContentStyle",
    "ContentFormat",
    "TextGenerationRequest",
    "TextGenerationResult"
]
