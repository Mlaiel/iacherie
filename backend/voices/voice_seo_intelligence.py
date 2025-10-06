"""
🔍 Voice SEO Intelligence - SEO Optimization for Voice Content
Metadata, keywords, search optimization, discoverability for voice

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class SEOMetadata:
    """SEO metadata structure"""
    title: str
    description: str
    keywords: List[str]
    tags: List[str]
    category: str
    language: str
    duration_seconds: Optional[float] = None
    transcript: Optional[str] = None


@dataclass
class SEOScore:
    """SEO score analysis"""
    overall_score: float  # 0-100
    title_score: float
    description_score: float
    keywords_score: float
    metadata_completeness: float
    recommendations: List[str] = field(default_factory=list)


class VoiceSEOIntelligence:
    """
    SEO intelligence for voice content
    """
    
    def __init__(self):
        """Initialize SEO intelligence"""
        self.trending_keywords: Set[str] = set()
        self.optimization_history: List[Dict[str, Any]] = []
        
        logger.info("🔍 Voice SEO Intelligence initialized")
    
    def analyze_seo(self, metadata: SEOMetadata) -> SEOScore:
        """
        Analyze SEO quality of voice content
        
        Args:
            metadata: Voice metadata
            
        Returns:
            SEOScore: SEO analysis score
        """
        title_score = self._score_title(metadata.title)
        description_score = self._score_description(metadata.description)
        keywords_score = self._score_keywords(metadata.keywords)
        completeness = self._score_completeness(metadata)
        
        overall = (title_score + description_score + keywords_score + completeness) / 4
        
        recommendations = self._generate_recommendations(metadata, title_score, 
                                                        description_score, keywords_score)
        
        score = SEOScore(
            overall_score=overall,
            title_score=title_score,
            description_score=description_score,
            keywords_score=keywords_score,
            metadata_completeness=completeness,
            recommendations=recommendations
        )
        
        logger.info(f"📊 SEO Score: {overall:.1f}/100")
        return score
    
    def optimize_metadata(self, metadata: SEOMetadata) -> SEOMetadata:
        """
        Optimize metadata for SEO
        
        Args:
            metadata: Original metadata
            
        Returns:
            SEOMetadata: Optimized metadata
        """
        optimized = SEOMetadata(
            title=self._optimize_title(metadata.title),
            description=self._optimize_description(metadata.description),
            keywords=self._optimize_keywords(metadata.keywords),
            tags=self._optimize_tags(metadata.tags),
            category=metadata.category,
            language=metadata.language,
            duration_seconds=metadata.duration_seconds,
            transcript=metadata.transcript
        )
        
        logger.info("✨ Metadata optimized for SEO")
        return optimized
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to analyze
            max_keywords: Maximum keywords to extract
            
        Returns:
            List[str]: Extracted keywords
        """
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Split into words
        words = text.split()
        
        # Filter stop words (simplified)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                     'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        counter = Counter(keywords)
        
        # Return most common
        return [word for word, _ in counter.most_common(max_keywords)]
    
    def suggest_tags(self, metadata: SEOMetadata) -> List[str]:
        """
        Suggest tags based on content
        
        Args:
            metadata: Voice metadata
            
        Returns:
            List[str]: Suggested tags
        """
        suggestions = set()
        
        # Extract from title and description
        all_text = f"{metadata.title} {metadata.description}"
        keywords = self.extract_keywords(all_text, max_keywords=5)
        suggestions.update(keywords)
        
        # Add category as tag
        suggestions.add(metadata.category.lower())
        
        # Add language tag
        suggestions.add(f"lang_{metadata.language}")
        
        # Add duration-based tag
        if metadata.duration_seconds:
            if metadata.duration_seconds < 30:
                suggestions.add("short")
            elif metadata.duration_seconds < 180:
                suggestions.add("medium")
            else:
                suggestions.add("long")
        
        logger.info(f"💡 Suggested {len(suggestions)} tags")
        return list(suggestions)
    
    def _score_title(self, title: str) -> float:
        """Score title quality (0-100)"""
        score = 0.0
        
        # Length check (optimal 30-60 chars)
        if 30 <= len(title) <= 60:
            score += 40
        elif len(title) < 30:
            score += 20
        else:
            score += 10
        
        # Capital letters check
        if title[0].isupper():
            score += 20
        
        # Word count (optimal 4-8 words)
        word_count = len(title.split())
        if 4 <= word_count <= 8:
            score += 40
        elif word_count < 4:
            score += 20
        
        return min(100, score)
    
    def _score_description(self, description: str) -> float:
        """Score description quality (0-100)"""
        score = 0.0
        
        # Length check (optimal 120-160 chars)
        if 120 <= len(description) <= 160:
            score += 50
        elif 80 <= len(description) < 120:
            score += 30
        elif len(description) < 80:
            score += 10
        
        # Sentence count
        sentences = description.count('.') + description.count('!') + description.count('?')
        if 2 <= sentences <= 3:
            score += 30
        elif sentences == 1:
            score += 15
        
        # Has call-to-action words
        cta_words = ['listen', 'hear', 'discover', 'explore', 'learn']
        if any(word in description.lower() for word in cta_words):
            score += 20
        
        return min(100, score)
    
    def _score_keywords(self, keywords: List[str]) -> float:
        """Score keywords quality (0-100)"""
        score = 0.0
        
        # Keyword count (optimal 5-10)
        if 5 <= len(keywords) <= 10:
            score += 50
        elif 3 <= len(keywords) < 5:
            score += 30
        elif len(keywords) < 3:
            score += 10
        
        # Keyword length (average 2-3 words optimal)
        avg_words = sum(len(k.split()) for k in keywords) / len(keywords) if keywords else 0
        if 2 <= avg_words <= 3:
            score += 30
        elif avg_words < 2:
            score += 15
        
        # No duplicate keywords
        if len(keywords) == len(set(keywords)):
            score += 20
        
        return min(100, score)
    
    def _score_completeness(self, metadata: SEOMetadata) -> float:
        """Score metadata completeness (0-100)"""
        score = 0.0
        
        required_fields = [
            metadata.title,
            metadata.description,
            metadata.keywords,
            metadata.category,
            metadata.language
        ]
        
        # Each required field = 15 points
        filled = sum(1 for field in required_fields if field)
        score += filled * 15
        
        # Optional fields bonus
        if metadata.tags:
            score += 10
        if metadata.transcript:
            score += 10
        if metadata.duration_seconds:
            score += 5
        
        return min(100, score)
    
    def _generate_recommendations(self, metadata: SEOMetadata, title_score: float,
                                 description_score: float, keywords_score: float) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        if title_score < 60:
            recommendations.append("📝 Improve title: Aim for 30-60 characters with 4-8 words")
        
        if description_score < 60:
            recommendations.append("📄 Improve description: Use 120-160 characters with clear call-to-action")
        
        if keywords_score < 60:
            recommendations.append("🔑 Add more keywords: Target 5-10 relevant keywords")
        
        if not metadata.tags:
            recommendations.append("🏷️ Add tags: Include relevant tags for better discoverability")
        
        if not metadata.transcript:
            recommendations.append("📝 Add transcript: Transcripts improve searchability")
        
        return recommendations
    
    def _optimize_title(self, title: str) -> str:
        """Optimize title for SEO"""
        # Capitalize first letter
        if title and not title[0].isupper():
            title = title.capitalize()
        
        # Trim if too long
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def _optimize_description(self, description: str) -> str:
        """Optimize description for SEO"""
        # Trim if too long
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def _optimize_keywords(self, keywords: List[str]) -> List[str]:
        """Optimize keywords list"""
        # Remove duplicates
        keywords = list(set(keywords))
        
        # Limit to 10 keywords
        keywords = keywords[:10]
        
        return keywords
    
    def _optimize_tags(self, tags: List[str]) -> List[str]:
        """Optimize tags list"""
        # Convert to lowercase
        tags = [tag.lower() for tag in tags]
        
        # Remove duplicates
        tags = list(set(tags))
        
        return tags


class SEOAnalyzer:
    """Analyze SEO performance"""
    
    def __init__(self):
        logger.info("📊 SEO Analyzer initialized")


class KeywordResearch:
    """Research keywords for voice content"""
    
    def __init__(self):
        logger.info("🔍 Keyword Research initialized")


class TrendAnalysis:
    """Analyze trending topics"""
    
    def __init__(self):
        logger.info("📈 Trend Analysis initialized")


class SearchOptimizer:
    """Optimize for search engines"""
    
    def __init__(self):
        logger.info("🎯 Search Optimizer initialized")


class MetadataGenerator:
    """Generate optimized metadata"""
    
    def __init__(self):
        logger.info("✨ Metadata Generator initialized")


class DiscoverabilityEngine:
    """Improve content discoverability"""
    
    def __init__(self):
        logger.info("🔦 Discoverability Engine initialized")


# Global instance
_seo_intelligence: Optional[VoiceSEOIntelligence] = None


def get_seo_intelligence() -> VoiceSEOIntelligence:
    """Get global SEO intelligence"""
    global _seo_intelligence
    if _seo_intelligence is None:
        _seo_intelligence = VoiceSEOIntelligence()
    return _seo_intelligence


# Auto-initialize
_seo_intelligence = VoiceSEOIntelligence()

logger.info("🔍 Voice SEO Intelligence module initialized")
