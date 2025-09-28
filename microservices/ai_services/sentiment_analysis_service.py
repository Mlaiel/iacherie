"""
🎭 Sentiment Analysis Service
Advanced sentiment analysis and emotion detection

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


class SentimentAnalysisService:
    """Advanced sentiment analysis service for content and user emotions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sentiment_cache: Dict[str, Dict[str, Any]] = {}
        self.emotion_patterns: Dict[str, List[str]] = {}
        
        # Initialize emotion patterns
        self._initialize_emotion_patterns()
        
        self.logger.info("✅ SentimentAnalysisService initialized")
    
    def _initialize_emotion_patterns(self):
        """Initialize emotion detection patterns"""
        self.emotion_patterns = {
            "joy": ["happy", "joy", "excited", "thrilled", "delighted", "amazing", "wonderful", "fantastic", "love", "great"],
            "sadness": ["sad", "depressed", "disappointed", "upset", "down", "heartbroken", "miserable", "grief"],
            "anger": ["angry", "mad", "furious", "annoyed", "irritated", "rage", "hate", "frustrated", "outraged"],
            "fear": ["scared", "afraid", "terrified", "anxious", "worried", "nervous", "panic", "frightened"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "stunned", "wow", "incredible", "unbelievable"],
            "disgust": ["disgusted", "gross", "yuck", "awful", "terrible", "horrible", "nasty", "revolting"]
        }
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze sentiment of given text"""
        try:
            # Check cache first
            text_hash = str(hash(text))
            if text_hash in self.sentiment_cache:
                return self.sentiment_cache[text_hash]
            
            # Basic sentiment analysis
            sentiment_result = await self._calculate_sentiment_score(text)
            
            # Emotion detection
            emotions = await self._detect_emotions(text)
            
            # Confidence calculation
            confidence = await self._calculate_confidence(sentiment_result, emotions)
            
            # Subjectivity analysis
            subjectivity = await self._analyze_subjectivity(text)
            
            result = {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": sentiment_result["sentiment"],
                "score": sentiment_result["score"],
                "confidence": confidence,
                "emotions": emotions,
                "subjectivity": subjectivity,
                "language": language,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "word_count": len(text.split())
            }
            
            # Cache result
            self.sentiment_cache[text_hash] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                "error": "Analysis failed",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _calculate_sentiment_score(self, text: str) -> Dict[str, Any]:
        """Calculate basic sentiment score"""
        # Positive and negative word lists
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "best", "perfect",
            "awesome", "brilliant", "outstanding", "superb", "magnificent", "incredible", "marvelous",
            "beautiful", "happy", "joy", "pleased", "satisfied", "delighted", "thrilled", "excited"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "hate", "worst", "horrible", "disappointing", "sad", "angry",
            "frustrated", "annoyed", "upset", "disgusted", "furious", "miserable", "pathetic", "useless",
            "stupid", "ridiculous", "boring", "dull", "weak", "poor", "failed", "disaster"
        ]
        
        # Intensifiers
        intensifiers = ["very", "extremely", "incredibly", "absolutely", "totally", "completely", "really"]
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_score = 0
        negative_score = 0
        
        for i, word in enumerate(words):
            # Check for intensifiers
            intensity_multiplier = 1.0
            if i > 0 and words[i-1] in intensifiers:
                intensity_multiplier = 1.5
            
            if word in positive_words:
                positive_score += 1 * intensity_multiplier
            elif word in negative_words:
                negative_score += 1 * intensity_multiplier
        
        # Calculate final score
        total_words = len(words)
        if total_words == 0:
            return {"sentiment": "neutral", "score": 0.0}
        
        net_score = (positive_score - negative_score) / total_words
        
        # Determine sentiment
        if net_score > 0.1:
            sentiment = "positive"
        elif net_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Normalize score to -1 to 1 range
        normalized_score = max(-1.0, min(1.0, net_score * 5))
        
        return {
            "sentiment": sentiment,
            "score": round(normalized_score, 3),
            "positive_indicators": positive_score,
            "negative_indicators": negative_score
        }
    
    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text"""
        text_lower = text.lower()
        emotions_detected = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            # Normalize score
            if score > 0:
                emotions_detected[emotion] = min(1.0, score * 0.3)
        
        # If no emotions detected, add neutral
        if not emotions_detected:
            emotions_detected["neutral"] = 0.8
        
        return emotions_detected
    
    async def _calculate_confidence(self, sentiment_result: Dict[str, Any], emotions: Dict[str, float]) -> float:
        """Calculate confidence in sentiment analysis"""
        base_confidence = 0.5
        
        # Higher confidence with stronger sentiment scores
        score_abs = abs(sentiment_result.get("score", 0))
        if score_abs > 0.5:
            base_confidence += 0.3
        elif score_abs > 0.2:
            base_confidence += 0.2
        
        # Higher confidence with more emotion indicators
        emotion_count = len(emotions)
        if emotion_count > 1:
            base_confidence += 0.1
        
        # Higher confidence with more sentiment indicators
        total_indicators = sentiment_result.get("positive_indicators", 0) + sentiment_result.get("negative_indicators", 0)
        if total_indicators > 2:
            base_confidence += 0.1
        
        return min(1.0, round(base_confidence, 2))
    
    async def _analyze_subjectivity(self, text: str) -> Dict[str, Any]:
        """Analyze text subjectivity (objective vs subjective)"""
        subjective_indicators = [
            "i think", "i believe", "i feel", "in my opinion", "personally", "i guess",
            "it seems", "probably", "maybe", "perhaps", "likely", "suppose"
        ]
        
        objective_indicators = [
            "according to", "research shows", "data indicates", "studies prove",
            "statistics show", "experts say", "reported", "confirmed", "verified"
        ]
        
        text_lower = text.lower()
        
        subjective_score = sum(1 for indicator in subjective_indicators if indicator in text_lower)
        objective_score = sum(1 for indicator in objective_indicators if indicator in text_lower)
        
        if subjective_score > objective_score:
            subjectivity = "subjective"
            score = min(1.0, subjective_score * 0.3)
        elif objective_score > subjective_score:
            subjectivity = "objective"
            score = min(1.0, objective_score * 0.3)
        else:
            subjectivity = "mixed"
            score = 0.5
        
        return {
            "type": subjectivity,
            "score": round(score, 2),
            "subjective_indicators": subjective_score,
            "objective_indicators": objective_score
        }
    
    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts for sentiment"""
        try:
            results = []
            for text in texts:
                result = await self.analyze_sentiment(text)
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch sentiment analysis failed: {str(e)}")
            return []
    
    async def get_sentiment_trends(self, texts: List[str], time_window: str = "daily") -> Dict[str, Any]:
        """Analyze sentiment trends over time"""
        try:
            results = await self.analyze_batch(texts)
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_score = 0
            emotions_summary = {}
            
            for result in results:
                if "sentiment" in result:
                    sentiment_counts[result["sentiment"]] += 1
                    total_score += result.get("score", 0)
                    
                    # Aggregate emotions
                    for emotion, score in result.get("emotions", {}).items():
                        emotions_summary[emotion] = emotions_summary.get(emotion, 0) + score
            
            total_texts = len(results)
            if total_texts > 0:
                avg_score = total_score / total_texts
                
                # Calculate percentages
                sentiment_percentages = {
                    sentiment: (count / total_texts) * 100
                    for sentiment, count in sentiment_counts.items()
                }
                
                # Normalize emotion scores
                emotions_avg = {
                    emotion: round(score / total_texts, 2)
                    for emotion, score in emotions_summary.items()
                }
            else:
                avg_score = 0
                sentiment_percentages = {"positive": 0, "negative": 0, "neutral": 0}
                emotions_avg = {}
            
            return {
                "time_window": time_window,
                "total_analyzed": total_texts,
                "average_sentiment_score": round(avg_score, 3),
                "sentiment_distribution": sentiment_percentages,
                "emotion_averages": emotions_avg,
                "overall_mood": "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sentiment trends analysis failed: {str(e)}")
            return {"error": "Trends analysis failed"}
    
    def clear_cache(self):
        """Clear sentiment analysis cache"""
        self.sentiment_cache.clear()
        self.logger.info("Sentiment analysis cache cleared")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "SentimentAnalysisService",
            "status": "healthy",
            "cache_size": len(self.sentiment_cache),
            "emotions_supported": len(self.emotion_patterns),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['SentimentAnalysisService']