"""
🔍 Content Analysis Service
Advanced content analysis and intelligence system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
import re
import json

logger = logging.getLogger(__name__)


class ContentAnalysisService:
    """Content Analysis Service for comprehensive content intelligence"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        self.content_metrics: Dict[str, Any] = {}
        self.sentiment_cache: Dict[str, str] = {}
        
        # Initialize content categories
        self.content_categories = [
            "technology", "lifestyle", "business", "entertainment",
            "education", "health", "travel", "food", "fashion", "sports"
        ]
        
        self.logger.info("✅ ContentAnalysisService initialized")
    
    async def analyze_content(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """Analyze content for various metrics and insights"""
        try:
            analysis_id = f"analysis_{datetime.utcnow().timestamp()}"
            
            # Basic content analysis
            word_count = len(content.split())
            char_count = len(content)
            
            # Sentiment analysis (simple implementation)
            sentiment = await self._analyze_sentiment(content)
            
            # Category detection
            category = await self._detect_category(content)
            
            # Readability score (Flesch-like simple calculation)
            readability = await self._calculate_readability(content)
            
            # Engagement prediction
            engagement_score = await self._predict_engagement(content, content_type)
            
            # Keywords extraction
            keywords = await self._extract_keywords(content)
            
            analysis_result = {
                "analysis_id": analysis_id,
                "content_type": content_type,
                "metrics": {
                    "word_count": word_count,
                    "character_count": char_count,
                    "sentence_count": content.count('.') + content.count('!') + content.count('?'),
                    "paragraph_count": content.count('\n\n') + 1
                },
                "sentiment": sentiment,
                "category": category,
                "readability_score": readability,
                "engagement_prediction": engagement_score,
                "keywords": keywords,
                "quality_score": self._calculate_quality_score(word_count, sentiment, readability),
                "recommendations": await self._generate_recommendations(content, sentiment, category),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.analysis_results[analysis_id] = analysis_result
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                "error": "Analysis failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Simple sentiment analysis"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "disappointing"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
    
    async def _detect_category(self, content: str) -> Dict[str, Any]:
        """Detect content category"""
        content_lower = content.lower()
        
        category_keywords = {
            "technology": ["tech", "ai", "software", "computer", "digital", "innovation"],
            "lifestyle": ["life", "personal", "daily", "routine", "habit", "wellness"],
            "business": ["business", "marketing", "sales", "strategy", "profit", "company"],
            "entertainment": ["fun", "movie", "music", "game", "celebrity", "entertainment"],
            "education": ["learn", "education", "study", "knowledge", "course", "tutorial"],
            "health": ["health", "fitness", "diet", "exercise", "medical", "wellness"],
            "travel": ["travel", "trip", "vacation", "destination", "journey", "adventure"],
            "food": ["food", "recipe", "cooking", "restaurant", "cuisine", "delicious"],
            "fashion": ["fashion", "style", "clothing", "trend", "outfit", "design"],
            "sports": ["sport", "game", "team", "player", "competition", "athletic"]
        }
        
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(0.9, category_scores[best_category] * 0.2)
        else:
            best_category = "general"
            confidence = 0.5
        
        return {
            "primary_category": best_category,
            "confidence": confidence,
            "all_scores": category_scores
        }
    
    async def _calculate_readability(self, content: str) -> Dict[str, Any]:
        """Calculate readability score"""
        words = content.split()
        sentences = content.count('.') + content.count('!') + content.count('?') + 1
        
        if len(words) == 0 or sentences == 0:
            return {"score": 0, "level": "unreadable"}
        
        avg_words_per_sentence = len(words) / sentences
        avg_syllables = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease formula
        flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables)
        flesch_score = max(0, min(100, flesch_score))
        
        if flesch_score >= 90:
            level = "very_easy"
        elif flesch_score >= 80:
            level = "easy"
        elif flesch_score >= 70:
            level = "fairly_easy"
        elif flesch_score >= 60:
            level = "standard"
        elif flesch_score >= 50:
            level = "fairly_difficult"
        elif flesch_score >= 30:
            level = "difficult"
        else:
            level = "very_difficult"
        
        return {
            "score": round(flesch_score, 2),
            "level": level,
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_syllables_per_word": round(avg_syllables, 2)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counting"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        
        if word[0] in vowels:
            count += 1
        
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        
        if word.endswith("e"):
            count -= 1
        
        if count == 0:
            count += 1
        
        return count
    
    async def _predict_engagement(self, content: str, content_type: str) -> Dict[str, Any]:
        """Predict engagement potential"""
        word_count = len(content.split())
        
        # Engagement factors
        has_question = '?' in content
        has_call_to_action = any(phrase in content.lower() for phrase in 
                               ["comment", "like", "share", "subscribe", "follow", "click"])
        has_emojis = bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content))
        
        base_score = 0.5
        
        # Adjust based on word count (sweet spot around 150-300 words for social media)
        if content_type == "social":
            if 50 <= word_count <= 150:
                base_score += 0.2
            elif 150 < word_count <= 300:
                base_score += 0.1
        
        # Engagement enhancers
        if has_question:
            base_score += 0.15
        if has_call_to_action:
            base_score += 0.1
        if has_emojis:
            base_score += 0.1
        
        engagement_score = min(1.0, base_score)
        
        return {
            "engagement_score": round(engagement_score, 2),
            "factors": {
                "word_count_optimal": 50 <= word_count <= 300 if content_type == "social" else word_count > 100,
                "has_question": has_question,
                "has_call_to_action": has_call_to_action,
                "has_emojis": has_emojis
            },
            "predicted_metrics": {
                "likes": int(engagement_score * 100),
                "comments": int(engagement_score * 20),
                "shares": int(engagement_score * 10)
            }
        }
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extract key keywords from content"""
        # Simple keyword extraction
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return [word for word, freq in keywords]
    
    def _calculate_quality_score(self, word_count: int, sentiment: Dict[str, Any], readability: Dict[str, Any]) -> float:
        """Calculate overall content quality score"""
        score = 0.5  # Base score
        
        # Word count factor
        if 100 <= word_count <= 1000:
            score += 0.2
        elif word_count > 50:
            score += 0.1
        
        # Sentiment factor
        if sentiment.get("sentiment") == "positive":
            score += 0.15
        elif sentiment.get("sentiment") == "neutral":
            score += 0.05
        
        # Readability factor
        readability_score = readability.get("score", 0)
        if 60 <= readability_score <= 80:
            score += 0.15
        elif 40 <= readability_score < 90:
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    async def _generate_recommendations(self, content: str, sentiment: Dict[str, Any], category: Dict[str, Any]) -> List[str]:
        """Generate content improvement recommendations"""
        recommendations = []
        
        word_count = len(content.split())
        
        if word_count < 50:
            recommendations.append("Consider expanding your content - longer posts tend to perform better")
        
        if sentiment.get("sentiment") == "negative":
            recommendations.append("Try adding more positive language to improve engagement")
        
        if sentiment.get("confidence", 0) < 0.6:
            recommendations.append("Consider making your tone more clear and definitive")
        
        if '?' not in content:
            recommendations.append("Add questions to encourage audience interaction")
        
        if not any(phrase in content.lower() for phrase in ["comment", "like", "share", "subscribe"]):
            recommendations.append("Include a clear call-to-action to boost engagement")
        
        if category.get("primary_category") == "general":
            recommendations.append("Focus on a specific topic or niche for better targeting")
        
        return recommendations
    
    async def get_content_insights(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed insights for analyzed content"""
        if analysis_id in self.analysis_results:
            return self.analysis_results[analysis_id]
        return {"error": "Analysis not found"}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "ContentAnalysisService",
            "status": "healthy",
            "analyses_performed": len(self.analysis_results),
            "categories_supported": len(self.content_categories),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['ContentAnalysisService']