"""
Advanced Content Analysis Engine
Intelligent content analysis, SEO optimization, and platform recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
from collections import Counter

# NLP and ML imports
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch

# Text analysis
import textstat
from textblob import TextBlob
import yake

from ..config import settings
from ..core.logging import logger


class SEOAnalyzer:
    """Advanced SEO analysis and optimization"""
    
    def __init__(self):
        self.target_platforms = {
            "youtube": {
                "title_max_length": 100,
                "description_max_length": 5000,
                "tags_max_count": 500,
                "optimal_title_length": 60,
                "keywords_in_title": True,
                "keywords_in_description": True
            },
            "instagram": {
                "caption_max_length": 2200,
                "hashtags_max_count": 30,
                "optimal_hashtags": 11,
                "first_sentence_important": True,
                "emoji_friendly": True
            },
            "tiktok": {
                "caption_max_length": 300,
                "hashtags_max_count": 100,
                "trending_hashtags": True,
                "short_engaging_text": True
            },
            "twitter": {
                "text_max_length": 280,
                "hashtags_max_count": 2,
                "concise_messaging": True,
                "thread_friendly": True
            }
        }
    
    async def analyze_content_seo(self, content_data: Dict[str, Any], 
                                target_platforms: List[str]) -> Dict[str, Any]:
        """Comprehensive SEO analysis for content"""



        try:
            seo_analysis = {
                "platform_optimizations": {},
                "keyword_analysis": {},
                "content_quality": {},
                "recommendations": []
            }
            
            # Extract text content for analysis
            text_content = await self._extract_text_for_seo(content_data)
            
            # Keyword analysis
            seo_analysis["keyword_analysis"] = await self._analyze_keywords(text_content)
            
            # Content quality analysis
            seo_analysis["content_quality"] = await self._analyze_content_quality(text_content)
            
            # Platform-specific optimizations
            for platform in target_platforms:
                if platform in self.target_platforms:
                    optimization = await self._analyze_platform_seo(text_content, platform)
                    seo_analysis["platform_optimizations"][platform] = optimization
            
            # Generate recommendations
            seo_analysis["recommendations"] = await self._generate_seo_recommendations(
                seo_analysis, target_platforms
            )
            
            return seo_analysis
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            return {}
    
    async def _extract_text_for_seo(self, content_data: Dict[str, Any]) -> str:
        """Extract relevant text content for SEO analysis"""
        text_parts = []
        
        # Get title if available
        if "title" in content_data:
            text_parts.append(content_data["title"])
        
        # Get description if available
        if "description" in content_data:
            text_parts.append(content_data["description"])
        
        # Get content preview for text content
        if "content_preview" in content_data:
            text_parts.append(content_data["content_preview"])
        
        # Get tags if available
        if "tags" in content_data:
            text_parts.extend(content_data["tags"])
        
        return " ".join(text_parts)
    
    async def _analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze keywords in content"""
        if not text:
            return {}
        
        # Extract keywords using YAKE
        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,  # 3-gram keywords
            dedupLim=0.7,
            top=20
        )
        
        keywords = kw_extractor.extract_keywords(text)
        
        # Calculate keyword density
        words = text.lower().split()
        word_count = len(words)
        word_freq = Counter(words)
        
        return {
            "extracted_keywords": [{"keyword": kw[1], "score": kw[0]} for kw in keywords[:10]],
            "word_frequency": dict(word_freq.most_common(20)),
            "total_words": word_count,
            "unique_words": len(word_freq),
            "keyword_density": {word: (count / word_count) * 100 
                             for word, count in word_freq.most_common(10)}
        }
    
    async def _analyze_content_quality(self, text: str) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        if not text:
            return {}
        
        # Readability metrics
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        
        # Sentiment analysis
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Structure analysis
        sentences = text.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        return {
            "readability": {
                "flesch_reading_ease": flesch_reading_ease,
                "flesch_kincaid_grade": flesch_kincaid_grade,
                "reading_level": self._get_reading_level(flesch_reading_ease)
            },
            "sentiment": {
                "polarity": sentiment.polarity,
                "subjectivity": sentiment.subjectivity,
                "classification": self._classify_sentiment(sentiment.polarity)
            },
            "structure": {
                "sentence_count": len([s for s in sentences if s.strip()]),
                "average_sentence_length": avg_sentence_length,
                "paragraph_count": text.count('\n\n') + 1
            }
        }
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Convert Flesch score to reading level"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _classify_sentiment(self, polarity: float) -> str:
        """Classify sentiment based on polarity"""
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    async def _analyze_platform_seo(self, text: str, platform: str) -> Dict[str, Any]:
        """Analyze SEO for specific platform"""
        platform_config = self.target_platforms[platform]
        analysis = {}
        
        if platform == "youtube":
            analysis = {
                "title_optimization": self._check_title_optimization(text, platform_config),
                "description_optimization": self._check_description_optimization(text, platform_config),
                "tag_recommendations": await self._generate_tag_recommendations(text)
            }
        elif platform == "instagram":
            analysis = {
                "caption_optimization": self._check_caption_optimization(text, platform_config),
                "hashtag_recommendations": await self._generate_instagram_hashtags(text),
                "engagement_potential": self._assess_engagement_potential(text)
            }
        elif platform == "tiktok":
            analysis = {
                "caption_optimization": self._check_tiktok_caption(text, platform_config),
                "trending_potential": await self._assess_trending_potential(text),
                "hashtag_recommendations": await self._generate_tiktok_hashtags(text)
            }
        
        return analysis
    
    def _check_title_optimization(self, text: str, config: Dict) -> Dict[str, Any]:
        """Check title optimization for platform"""
        # Extract potential title (first sentence or first 100 chars)
        potential_title = text.split('.')[0][:config["optimal_title_length"]]
        
        return {
            "length": len(potential_title),
            "optimal_length": config["optimal_title_length"],
            "within_limits": len(potential_title) <= config["title_max_length"],
            "recommendations": self._generate_title_recommendations(potential_title, config)
        }
    
    def _check_description_optimization(self, text: str, config: Dict) -> Dict[str, Any]:
        """Check description optimization"""



        return {
            "length": len(text),
            "max_length": config["description_max_length"],
            "within_limits": len(text) <= config["description_max_length"],
            "keyword_presence": True  # Simplified check
        }
    
    async def _generate_tag_recommendations(self, text: str) -> List[str]:
        """Generate tag recommendations for content"""
        # Extract keywords and convert to tags
        kw_extractor = yake.KeywordExtractor(lan="en", n=2, top=15)
        keywords = kw_extractor.extract_keywords(text)
        
        tags = []
        for score, keyword in keywords:
            # Convert to hashtag format
            tag = keyword.replace(" ", "").lower()
            if len(tag) > 2:  # Only meaningful tags
                tags.append(tag)
        
        return tags[:10]
    
    async def _generate_instagram_hashtags(self, text: str) -> List[str]:
        """Generate Instagram-specific hashtags"""
        base_tags = await self._generate_tag_recommendations(text)
        
        # Add Instagram-specific formatting
        instagram_tags = []
        for tag in base_tags:
            instagram_tags.append(f"#{tag}")
        
        # Add some generic engagement hashtags
        engagement_tags = ["#content", "#creator", "#viral", "#trending"]
        instagram_tags.extend(engagement_tags[:5])
        
        return instagram_tags[:11]  # Instagram optimal
    
    async def _generate_tiktok_hashtags(self, text: str) -> List[str]:
        """Generate TikTok-specific hashtags"""
        base_tags = await self._generate_tag_recommendations(text)
        
        # Add TikTok-specific formatting and trending tags
        tiktok_tags = [f"#{tag}" for tag in base_tags[:5]]
        trending_tags = ["#fyp", "#viral", "#trending", "#foryou"]
        tiktok_tags.extend(trending_tags)
        
        return tiktok_tags[:8]
    
    async def _generate_seo_recommendations(self, analysis: Dict[str, Any], 
                                          platforms: List[str]) -> List[str]:
        """Generate comprehensive SEO recommendations"""
        recommendations = []
        
        # Content quality recommendations
        quality = analysis.get("content_quality", {})
        if quality:
            readability = quality.get("readability", {})
            if readability.get("flesch_reading_ease", 0) < 60:
                recommendations.append("Consider simplifying language for better readability")
            
            sentiment = quality.get("sentiment", {})
            if sentiment.get("classification") == "Negative":
                recommendations.append("Consider adding more positive language to improve engagement")
        
        # Platform-specific recommendations
        for platform in platforms:
            platform_data = analysis.get("platform_optimizations", {}).get(platform, {})
            
            if platform == "youtube":
                title_opt = platform_data.get("title_optimization", {})
                if not title_opt.get("within_limits", True):
                    recommendations.append(f"Shorten title for YouTube (max 100 characters)")
            
            elif platform == "instagram":
                hashtag_recs = platform_data.get("hashtag_recommendations", [])
                if len(hashtag_recs) < 11:
                    recommendations.append("Add more hashtags for Instagram (optimal: 11)")
        
        # Keyword recommendations
        keywords = analysis.get("keyword_analysis", {})
        if keywords.get("total_words", 0) < 50:
            recommendations.append("Add more descriptive content for better SEO")
        
        return recommendations


class ContentQualityAnalyzer:
    """Analyze content quality and engagement potential"""
    
    def __init__(self):
        # Load sentiment analysis pipeline
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.emotion_analyzer = pipeline("text-classification", 
                                            model="j-hartmann/emotion-english-distilroberta-base")
        except:
            self.sentiment_analyzer = None
            self.emotion_analyzer = None
            logger.warning("Sentiment analysis models not available")
    
    async def analyze_content_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content quality analysis"""



        try:
            analysis = {
                "engagement_score": 0.0,
                "viral_potential": 0.0,
                "audience_appeal": {},
                "content_metrics": {},
                "recommendations": []
            }
            
            # Analyze based on content type
            content_type = content_data.get("content_type", "unknown")
            
            if content_type == "audio":
                analysis.update(await self._analyze_audio_quality(content_data))
            elif content_type == "video":
                analysis.update(await self._analyze_video_quality(content_data))
            elif content_type == "image":
                analysis.update(await self._analyze_image_quality(content_data))
            elif content_type == "text":
                analysis.update(await self._analyze_text_quality(content_data))
            
            # Calculate overall scores
            analysis["engagement_score"] = await self._calculate_engagement_score(analysis)
            analysis["viral_potential"] = await self._calculate_viral_potential(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {str(e)}")
            return {}
    
    async def _analyze_audio_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio content quality"""
        features = content_data.get("features", {})
        
        quality_score = 0.0
        factors = []
        
        # Check audio clarity (RMS energy)
        rms_energy = features.get("rms_energy", 0)
        if rms_energy > 0.1:
            quality_score += 20
            factors.append("Good audio energy")
        
        # Check tempo (for music)
        tempo = features.get("tempo", 0)
        if 60 <= tempo <= 180:  # Typical music tempo range
            quality_score += 15
            factors.append("Good tempo range")
        
        # Check spectral centroid (brightness)
        spectral_centroid = features.get("spectral_centroid", 0)
        if 1000 <= spectral_centroid <= 4000:
            quality_score += 15
            factors.append("Balanced frequency content")
        
        return {
            "audio_quality_score": min(quality_score, 100),
            "quality_factors": factors,
            "technical_metrics": {
                "clarity": "High" if rms_energy > 0.1 else "Medium",
                "frequency_balance": "Good" if 1000 <= spectral_centroid <= 4000 else "Needs adjustment"
            }
        }
    
    async def _analyze_video_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content quality"""
        features = content_data.get("features", {})
        
        quality_score = 0.0
        factors = []
        
        # Check visual quality
        avg_brightness = features.get("average_brightness", 0)
        if 50 <= avg_brightness <= 200:  # Good brightness range
            quality_score += 20
            factors.append("Good brightness levels")
        
        # Check edge density (detail level)
        avg_edge_density = features.get("average_edge_density", 0)
        if avg_edge_density > 0.1:
            quality_score += 15
            factors.append("Good detail level")
        
        # Check if has audio
        if features.get("has_audio", False):
            quality_score += 10
            factors.append("Has audio track")
        
        # Check duration
        duration = features.get("duration", 0)
        if 15 <= duration <= 300:  # 15 seconds to 5 minutes is good for social
            quality_score += 15
            factors.append("Good duration for social media")
        
        return {
            "video_quality_score": min(quality_score, 100),
            "quality_factors": factors,
            "visual_metrics": {
                "brightness": "Optimal" if 50 <= avg_brightness <= 200 else "Needs adjustment",
                "detail_level": "High" if avg_edge_density > 0.1 else "Medium"
            }
        }
    
    async def _analyze_image_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image content quality"""
        features = content_data.get("features", {})
        
        quality_score = 0.0
        factors = []
        
        # Check image resolution
        width = content_data.get("width", 0)
        height = content_data.get("height", 0)
        if width >= 1080 or height >= 1080:
            quality_score += 25
            factors.append("High resolution")
        
        # Check sharpness
        sharpness = features.get("sharpness", 0)
        if sharpness > 100:  # Good sharpness threshold
            quality_score += 20
            factors.append("Sharp image")
        
        # Check contrast
        contrast = features.get("contrast", 0)
        if contrast > 50:
            quality_score += 15
            factors.append("Good contrast")
        
        # Check brightness
        brightness = features.get("brightness", 0)
        if 50 <= brightness <= 200:
            quality_score += 15
            factors.append("Good brightness")
        
        return {
            "image_quality_score": min(quality_score, 100),
            "quality_factors": factors,
            "visual_metrics": {
                "resolution": f"{width}x{height}",
                "sharpness": "High" if sharpness > 100 else "Medium",
                "contrast": "Good" if contrast > 50 else "Low"
            }
        }
    
    async def _analyze_text_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text content quality"""
        features = content_data.get("features", {})
        text_content = content_data.get("content_preview", "")
        
        quality_score = 0.0
        factors = []
        
        # Check length
        word_count = features.get("word_count", 0)
        if 50 <= word_count <= 2000:  # Good range for most platforms
            quality_score += 20
            factors.append("Appropriate length")
        
        # Check readability
        lexical_diversity = features.get("lexical_diversity", 0)
        if lexical_diversity > 0.5:
            quality_score += 15
            factors.append("Good vocabulary diversity")
        
        # Sentiment analysis
        if self.sentiment_analyzer and text_content:
            sentiment_result = self.sentiment_analyzer(text_content[:512])
            sentiment_score = sentiment_result[0]["score"]
            if sentiment_score > 0.8:
                quality_score += 15
                factors.append("Strong emotional tone")
        
        # Structure check
        sentence_count = features.get("sentence_count", 0)
        if sentence_count > 3:
            quality_score += 10
            factors.append("Well-structured text")
        
        return {
            "text_quality_score": min(quality_score, 100),
            "quality_factors": factors,
            "language_metrics": {
                "readability": "Good" if lexical_diversity > 0.5 else "Basic",
                "structure": "Well-structured" if sentence_count > 3 else "Simple"
            }
        }
    
    async def _calculate_engagement_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall engagement potential score"""
        # Base score from content quality
        quality_scores = [
            analysis.get("audio_quality_score", 0),
            analysis.get("video_quality_score", 0),
            analysis.get("image_quality_score", 0),
            analysis.get("text_quality_score", 0)
        ]
        
        # Get the highest quality score (since content is one type)
        base_score = max([score for score in quality_scores if score > 0])
        
        # Adjust based on other factors
        engagement_score = base_score * 0.7  # Base quality contributes 70%
        
        # Add bonus for multiple quality factors
        all_factors = []
        for key in ["quality_factors"]:
            if key in analysis:
                all_factors.extend(analysis[key])
        
        if len(all_factors) >= 3:
            engagement_score += 10  # Bonus for multiple quality factors
        
        return min(engagement_score, 100.0)
    
    async def _calculate_viral_potential(self, analysis: Dict[str, Any]) -> float:
        """Calculate viral potential score"""
        viral_score = 0.0
        
        # High engagement score contributes to viral potential
        engagement_score = analysis.get("engagement_score", 0)
        viral_score += engagement_score * 0.4
        
        # Quality factors that boost viral potential
        all_factors = []
        for key in ["quality_factors"]:
            if key in analysis:
                all_factors.extend(analysis[key])
        
        viral_factors = [
            "High resolution", "Good tempo range", "Sharp image", 
            "Strong emotional tone", "Good duration for social media"
        ]
        
        matching_factors = len([f for f in all_factors if f in viral_factors])
        viral_score += matching_factors * 8
        
        return min(viral_score, 100.0)


class PlatformRecommendationEngine:
    """Recommend optimal platforms for content distribution"""
    
    def __init__(self):
        self.platform_characteristics = {
            "youtube": {
                "preferred_content": ["video", "audio"],
                "audience_age": "25-54",
                "content_length": "long",
                "discovery_method": "search",
                "monetization": "high"
            },
            "instagram": {
                "preferred_content": ["image", "video"],
                "audience_age": "18-34",
                "content_length": "short",
                "discovery_method": "hashtags",
                "monetization": "medium"
            },
            "tiktok": {
                "preferred_content": ["video"],
                "audience_age": "16-24",
                "content_length": "very_short",
                "discovery_method": "algorithm",
                "monetization": "growing"
            },
            "twitter": {
                "preferred_content": ["text", "image"],
                "audience_age": "25-49",
                "content_length": "micro",
                "discovery_method": "trending",
                "monetization": "low"
            },
            "linkedin": {
                "preferred_content": ["text", "image"],
                "audience_age": "25-54",
                "content_length": "medium",
                "discovery_method": "professional",
                "monetization": "medium"
            }
        }
    
    async def recommend_platforms(self, content_data: Dict[str, Any], 
                                user_goals: List[str] = None) -> List[Dict[str, Any]]:
        """Recommend optimal platforms for content"""



        try:
            content_type = content_data.get("content_type", "unknown")
            recommendations = []
            
            for platform, characteristics in self.platform_characteristics.items():
                score = await self._calculate_platform_score(
                    content_data, characteristics, user_goals or []
                )
                
                if score > 30:  # Minimum threshold
                    recommendation = {
                        "platform": platform,
                        "suitability_score": score,
                        "reasons": await self._get_recommendation_reasons(
                            content_data, platform, characteristics
                        ),
                        "optimization_tips": await self._get_optimization_tips(
                            content_data, platform
                        )
                    }
                    recommendations.append(recommendation)
            
            # Sort by suitability score
            recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Platform recommendation failed: {str(e)}")
            return []
    
    async def _calculate_platform_score(self, content_data: Dict[str, Any], 
                                      characteristics: Dict[str, str],
                                      user_goals: List[str]) -> float:
        """Calculate how well content matches platform"""
        score = 0.0
        
        # Content type match
        content_type = content_data.get("content_type", "")
        if content_type in characteristics["preferred_content"]:
            score += 40
        
        # Content length match
        duration = content_data.get("duration_seconds", 0)
        length_match = await self._check_length_match(duration, characteristics["content_length"])
        score += length_match * 20
        
        # Quality score bonus
        quality_score = content_data.get("quality_score", 0)
        score += (quality_score / 100) * 20
        
        # User goals alignment
        if "monetization" in user_goals and characteristics["monetization"] == "high":
            score += 10
        if "reach" in user_goals and characteristics["discovery_method"] == "algorithm":
            score += 10
        if "professional" in user_goals and characteristics["audience_age"] == "25-54":
            score += 10
        
        return min(score, 100.0)
    
    async def _check_length_match(self, duration: float, preferred_length: str) -> float:
        """Check if content length matches platform preference"""
        if preferred_length == "very_short" and duration <= 60:
            return 1.0
        elif preferred_length == "short" and 60 < duration <= 300:
            return 1.0
        elif preferred_length == "medium" and 300 < duration <= 600:
            return 1.0
        elif preferred_length == "long" and duration > 600:
            return 1.0
        elif preferred_length == "micro":  # For text/images
            return 1.0
        else:
            return 0.5  # Partial match
    
    async def _get_recommendation_reasons(self, content_data: Dict[str, Any], 
                                        platform: str, characteristics: Dict[str, str]) -> List[str]:
        """Generate reasons for platform recommendation"""
        reasons = []
        
        content_type = content_data.get("content_type", "")
        if content_type in characteristics["preferred_content"]:
            reasons.append(f"Platform optimized for {content_type} content")
        
        if characteristics["monetization"] == "high":
            reasons.append("High monetization potential")
        
        if characteristics["discovery_method"] == "algorithm":
            reasons.append("Algorithm-driven discovery for better reach")
        
        return reasons
    
    async def _get_optimization_tips(self, content_data: Dict[str, Any], 
                                   platform: str) -> List[str]:
        """Generate platform-specific optimization tips"""
        tips = []
        
        if platform == "youtube":
            tips.extend([
                "Create compelling thumbnails",
                "Optimize title with keywords",
                "Use detailed descriptions",
                "Add closed captions"
            ])
        elif platform == "instagram":
            tips.extend([
                "Use 11 relevant hashtags",
                "Post during peak hours",
                "Create visually appealing content",
                "Engage with comments quickly"
            ])
        elif platform == "tiktok":
            tips.extend([
                "Use trending sounds",
                "Hook viewers in first 3 seconds",
                "Add trending hashtags",
                "Keep videos under 60 seconds"
            ])
        
        return tips


class ContentAnalyzer:
    """Main content analysis orchestrator"""
    
    def __init__(self):
        self.seo_analyzer = SEOAnalyzer()
        self.quality_analyzer = ContentQualityAnalyzer()
        self.platform_recommender = PlatformRecommendationEngine()
    
    async def analyze_content(self, content_data: Dict[str, Any], 
                            target_platforms: List[str] = None,
                            user_goals: List[str] = None) -> Dict[str, Any]:
        """Comprehensive content analysis"""



        try:
            analysis_result = {
                "content_id": content_data.get("content_id", "unknown"),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "seo_analysis": {},
                "quality_analysis": {},
                "platform_recommendations": [],
                "overall_score": 0.0,
                "actionable_insights": []
            }
            
            # SEO Analysis
            if target_platforms:
                seo_analysis = await self.seo_analyzer.analyze_content_seo(
                    content_data, target_platforms
                )
                analysis_result["seo_analysis"] = seo_analysis
            
            # Quality Analysis
            quality_analysis = await self.quality_analyzer.analyze_content_quality(content_data)
            analysis_result["quality_analysis"] = quality_analysis
            
            # Platform Recommendations
            platform_recs = await self.platform_recommender.recommend_platforms(
                content_data, user_goals
            )
            analysis_result["platform_recommendations"] = platform_recs
            
            # Calculate overall score
            analysis_result["overall_score"] = await self._calculate_overall_score(
                analysis_result
            )
            
            # Generate actionable insights
            analysis_result["actionable_insights"] = await self._generate_insights(
                analysis_result
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {}
    
    async def _calculate_overall_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall content performance score"""
        scores = []
        
        # Quality score
        quality_analysis = analysis_result.get("quality_analysis", {})
        engagement_score = quality_analysis.get("engagement_score", 0)
        scores.append(engagement_score)
        
        # Platform suitability (average of top 3 platforms)
        platform_recs = analysis_result.get("platform_recommendations", [])
        if platform_recs:
            top_platform_scores = [rec["suitability_score"] for rec in platform_recs[:3]]
            avg_platform_score = np.mean(top_platform_scores)
            scores.append(avg_platform_score)
        
        return np.mean(scores) if scores else 0.0
    
    async def _generate_insights(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from analysis"""
        insights = []
        
        # Quality insights
        quality_analysis = analysis_result.get("quality_analysis", {})
        engagement_score = quality_analysis.get("engagement_score", 0)
        
        if engagement_score < 50:
            insights.append("Consider improving content quality to increase engagement potential")
        elif engagement_score > 80:
            insights.append("High-quality content with excellent engagement potential")
        
        # Platform insights
        platform_recs = analysis_result.get("platform_recommendations", [])
        if platform_recs:
            best_platform = platform_recs[0]["platform"]
            insights.append(f"Best suited for {best_platform} - focus optimization efforts here")
        
        # SEO insights
        seo_analysis = analysis_result.get("seo_analysis", {})
        seo_recommendations = seo_analysis.get("recommendations", [])
        insights.extend(seo_recommendations[:3])  # Top 3 SEO recommendations
        
        return insights


# Global content analyzer instance
content_analyzer = ContentAnalyzer()