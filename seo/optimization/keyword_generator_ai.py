"""Keyword Generator AI - Intelligent Keyword Generation and Research

This module provides AI-powered keyword generation, research, and analysis
for SEO optimization across different platforms and languages.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from collections import Counter

logger = logging.getLogger(__name__)


class KeywordType(Enum):
    """
Types of keywords"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    LONG_TAIL = "long_tail"
    SEMANTIC = "semantic"
    TRENDING = "trending"
    COMPETITOR = "competitor"


class SearchIntent(Enum):
    """Search intent classification"""

    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


@dataclass
class KeywordMetrics:
    """Keyword performance metrics"""
    search_volume: int
    competition_level: float  # 0-1 scale
    cpc: float  # Cost per click
    difficulty: float  # SEO difficulty 0-100
    relevance_score: float  # 0-1 scale
    trend_direction: str  # "up", "down", "stable"


@dataclass
class KeywordSuggestion:
    """Individual keyword suggestion"""
    keyword: str
    keyword_type: KeywordType
    search_intent: SearchIntent
    metrics: KeywordMetrics
    related_terms: List[str]
    confidence_score: float


@dataclass
class KeywordResearchResult:
    """
Complete keyword research result"""
    primary_keywords: List[KeywordSuggestion]
    secondary_keywords: List[KeywordSuggestion]
    long_tail_keywords: List[KeywordSuggestion]
    semantic_keywords: List[KeywordSuggestion]
    trending_keywords: List[KeywordSuggestion]
    competitor_keywords: List[KeywordSuggestion]
    total_keywords: int
    research_metadata: Dict[str, Any]


class KeywordGeneratorAI:
    """
    AI-powered keyword generator that creates comprehensive keyword strategies
    for content optimization and SEO campaigns.
    """
    def __init__(self, language -> None: str = "en", region -> None: str = "US") -> None:
        """
        Initialize the keyword generator.
        
        Args:
            language: Target language for keywords
            region: Target region for search data
        """
        self.language = language
        self.region = region
        self.keyword_database = self._initialize_keyword_database()
        self.stop_words = self._get_stop_words(language)
        self.trending_topics = self._get_trending_topics()

    def generate_keywords(
        self,
        seed_keywords: List[str],
        content: str = "",
        industry: str = "",
        target_audience: str = "",
        platform: str = "general",
        max_keywords: int = 100
    ) -> KeywordResearchResult:
        """
        Generate comprehensive keyword research based on seed keywords and content.
        
        Args:
            seed_keywords: Initial keywords to expand from
            content: Content to analyze for keyword extraction
            industry: Target industry context
            target_audience: Target audience description
            platform: Target platform (affects keyword selection)
            max_keywords: Maximum number of keywords to generate
            
        Returns:
            KeywordResearchResult with categorized keywords
        """
        try:
            logger.info(f"Starting keyword generation for {len(seed_keywords)} seed keywords")
            
            # Extract keywords from content
            content_keywords = self._extract_keywords_from_content(content)
            
            # Generate different types of keywords
            primary_keywords = self._generate_primary_keywords(seed_keywords, industry)
            secondary_keywords = self._generate_secondary_keywords(seed_keywords, content_keywords)
            long_tail_keywords = self._generate_long_tail_keywords(seed_keywords, content)
            semantic_keywords = self._generate_semantic_keywords(seed_keywords, content)
            trending_keywords = self._generate_trending_keywords(seed_keywords, industry)
            competitor_keywords = self._generate_competitor_keywords(seed_keywords, industry)
            
            # Apply platform-specific filtering
            if platform != "general":
                primary_keywords = self._filter_for_platform(primary_keywords, platform)
                secondary_keywords = self._filter_for_platform(secondary_keywords, platform)
                long_tail_keywords = self._filter_for_platform(long_tail_keywords, platform)
            
            # Limit results
            total_generated = (
                len(primary_keywords) + len(secondary_keywords) + 
                len(long_tail_keywords) + len(semantic_keywords) +
                len(trending_keywords) + len(competitor_keywords)
            )
            
            if total_generated > max_keywords:
                # Prioritize and limit
                primary_keywords = primary_keywords[:max(5, max_keywords // 6)]
                secondary_keywords = secondary_keywords[:max(10, max_keywords // 4)]
                long_tail_keywords = long_tail_keywords[:max(15, max_keywords // 3)]
                semantic_keywords = semantic_keywords[:max(10, max_keywords // 6)]
                trending_keywords = trending_keywords[:max(5, max_keywords // 10)]
                competitor_keywords = competitor_keywords[:max(5, max_keywords // 10)]
            
            research_metadata = {
                "seed_keywords": seed_keywords,
                "content_length": len(content.split()) if content else 0,
                "industry": industry,
                "target_audience": target_audience,
                "platform": platform,
                "language": self.language,
                "region": self.region,
                "generation_timestamp": "2025-01-01T00:00:00Z"  # Would use actual timestamp
            }
            
            return KeywordResearchResult(
                primary_keywords=primary_keywords,
                secondary_keywords=secondary_keywords,
                long_tail_keywords=long_tail_keywords,
                semantic_keywords=semantic_keywords,
                trending_keywords=trending_keywords,
                competitor_keywords=competitor_keywords,
                total_keywords=len(primary_keywords) + len(secondary_keywords) + 
                              len(long_tail_keywords) + len(semantic_keywords) +
                              len(trending_keywords) + len(competitor_keywords),
                research_metadata=research_metadata
            )
            
        except Exception as e:
            logger.error(f"Error generating keywords: {str(e)}")
            raise

    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract potential keywords from content"""
        if not content:
            return []
        
        # Clean and tokenize content
        content_lower = content.lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content_lower)
        
        # Remove stop words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count frequency
        word_freq = Counter(filtered_words)
        
        # Generate n-grams (2-4 words)
        phrases = []
        content_words = content.split()
        
        for n in range(2, 5):
            for i in range(len(content_words) - n + 1):
                phrase = ' '.join(content_words[i:i+n]).lower()
                if self._is_valid_phrase(phrase):
                    phrases.append(phrase)
        
        phrase_freq = Counter(phrases)
        
        # Combine single words and phrases
        keywords = []
        
        # Top single words
        for word, freq in word_freq.most_common(10):
            if freq > 1:  # Appears at least twice
                keywords.append(word)
        
        # Top phrases
        for phrase, freq in phrase_freq.most_common(15):
            if freq > 1:
                keywords.append(phrase)
        
        return keywords

    def _is_valid_phrase(self, phrase: str) -> bool:
        """
Check if a phrase is valid for keyword extraction"""
        words = phrase.split()
        
        # Skip if too many stop words
        stop_word_count = sum(1 for word in words if word in self.stop_words)
        if stop_word_count / len(words) > 0.5:
            return False
        
        # Skip if contains numbers or special characters
        if re.search(r'[0-9]', phrase) or re.search(r'[^\w\s]', phrase):
            return False
        
        return True

    def _generate_primary_keywords(self, seed_keywords: List[str], industry: str) -> List[KeywordSuggestion]:
        """
Generate primary keywords from seed keywords"""
        primary_keywords = []
        
        for seed in seed_keywords:
            # Direct seed keyword
            metrics = self._calculate_keyword_metrics(seed, KeywordType.PRIMARY)
            suggestion = KeywordSuggestion(
                keyword=seed,
                keyword_type=KeywordType.PRIMARY,
                search_intent=self._classify_search_intent(seed),
                metrics=metrics,
                related_terms=self._get_related_terms(seed),
                confidence_score=0.9
            )
            primary_keywords.append(suggestion)
            
            # Industry-specific variations
            if industry:
                industry_variations = [
                    f"{seed} {industry}",
                    f"{industry} {seed}",
                    f"best {seed} for {industry}",
                    f"{seed} in {industry}"
                ]
                
                for variation in industry_variations:
                    if len(primary_keywords) < 10:  # Limit primary keywords
                        metrics = self._calculate_keyword_metrics(variation, KeywordType.PRIMARY)
                        suggestion = KeywordSuggestion(
                            keyword=variation,
                            keyword_type=KeywordType.PRIMARY,
                            search_intent=self._classify_search_intent(variation),
                            metrics=metrics,
                            related_terms=self._get_related_terms(variation),
                            confidence_score=0.8
                        )
                        primary_keywords.append(suggestion)
        
        return primary_keywords

    def _generate_secondary_keywords(
        self, 
        seed_keywords: List[str], 
        content_keywords: List[str]
    ) -> List[KeywordSuggestion]:
        """Generate secondary keywords"""
        secondary_keywords = []
        
        # Variations of seed keywords
        for seed in seed_keywords:
            variations = [
                f"how to {seed}",
                f"{seed} tips",
                f"{seed} guide",
                f"{seed} tutorial",
                f"best {seed}",
                f"{seed} examples",
                f"{seed} benefits"
            ]
            
            for variation in variations:
                if len(secondary_keywords) < 20:
                    metrics = self._calculate_keyword_metrics(variation, KeywordType.SECONDARY)
                    suggestion = KeywordSuggestion(
                        keyword=variation,
                        keyword_type=KeywordType.SECONDARY,
                        search_intent=self._classify_search_intent(variation),
                        metrics=metrics,
                        related_terms=self._get_related_terms(variation),
                        confidence_score=0.7
                    )
                    secondary_keywords.append(suggestion)
        
        # Content-derived keywords
        for content_keyword in content_keywords[:10]:
            if content_keyword not in [kw.keyword for kw in secondary_keywords]:
                metrics = self._calculate_keyword_metrics(content_keyword, KeywordType.SECONDARY)
                suggestion = KeywordSuggestion(
                    keyword=content_keyword,
                    keyword_type=KeywordType.SECONDARY,
                    search_intent=self._classify_search_intent(content_keyword),
                    metrics=metrics,
                    related_terms=self._get_related_terms(content_keyword),
                    confidence_score=0.6
                )
                secondary_keywords.append(suggestion)
        
        return secondary_keywords

    def _generate_long_tail_keywords(self, seed_keywords: List[str], content: str) -> List[KeywordSuggestion]:
        """Generate long-tail keywords"""
        long_tail_keywords = []
        
        # Question-based long-tail keywords
        question_starters = [
            "how to", "what is", "why is", "when to", "where to",
            "how do", "what are", "how can", "best way to"
        ]
        
        for seed in seed_keywords:
            for starter in question_starters:
                long_tail = f"{starter} {seed}"
                if len(long_tail.split()) >= 3:
                    metrics = self._calculate_keyword_metrics(long_tail, KeywordType.LONG_TAIL)
                    suggestion = KeywordSuggestion(
                        keyword=long_tail,
                        keyword_type=KeywordType.LONG_TAIL,
                        search_intent=SearchIntent.INFORMATIONAL,
                        metrics=metrics,
                        related_terms=self._get_related_terms(long_tail),
                        confidence_score=0.6
                    )
                    long_tail_keywords.append(suggestion)
        
        # Problem-solution long-tail keywords
        problem_patterns = [
            "problems with {seed}",
            "issues with {seed}",
            "challenges in {seed}",
            "mistakes in {seed}",
            "common {seed} errors"
        ]
        
        for seed in seed_keywords:
            for pattern in problem_patterns:
                long_tail = pattern.format(seed=seed)
                metrics = self._calculate_keyword_metrics(long_tail, KeywordType.LONG_TAIL)
                suggestion = KeywordSuggestion(
                    keyword=long_tail,
                    keyword_type=KeywordType.LONG_TAIL,
                    search_intent=SearchIntent.INFORMATIONAL,
                    metrics=metrics,
                    related_terms=self._get_related_terms(long_tail),
                    confidence_score=0.5
                )
                long_tail_keywords.append(suggestion)
        
        return long_tail_keywords[:25]  # Limit to top 25

    def _generate_semantic_keywords(self, seed_keywords: List[str], content: str) -> List[KeywordSuggestion]:
        """Generate semantically related keywords"""
        semantic_keywords = []
        
        # Use built-in semantic relationships
        for seed in seed_keywords:
            related_terms = self._get_semantic_related_terms(seed)
            
            for term in related_terms[:5]:  # Top 5 per seed
                if term not in [kw.keyword for kw in semantic_keywords]:
                    metrics = self._calculate_keyword_metrics(term, KeywordType.SEMANTIC)
                    suggestion = KeywordSuggestion(
                        keyword=term,
                        keyword_type=KeywordType.SEMANTIC,
                        search_intent=self._classify_search_intent(term),
                        metrics=metrics,
                        related_terms=self._get_related_terms(term),
                        confidence_score=0.7
                    )
                    semantic_keywords.append(suggestion)
        
        return semantic_keywords

    def _generate_trending_keywords(self, seed_keywords: List[str], industry: str) -> List[KeywordSuggestion]:
        """
Generate trending keywords"""
        trending_keywords = []
        
        # Combine seed keywords with trending topics
        for seed in seed_keywords:
            for trend in self.trending_topics[:3]:
                trending_combo = f"{seed} {trend}"
                metrics = self._calculate_keyword_metrics(trending_combo, KeywordType.TRENDING)
                # Boost search volume for trending keywords
                metrics.search_volume = int(metrics.search_volume * 1.5)
                
                suggestion = KeywordSuggestion(
                    keyword=trending_combo,
                    keyword_type=KeywordType.TRENDING,
                    search_intent=self._classify_search_intent(trending_combo),
                    metrics=metrics,
                    related_terms=self._get_related_terms(trending_combo),
                    confidence_score=0.8
                )
                trending_keywords.append(suggestion)
        
        return trending_keywords

    def _generate_competitor_keywords(self, seed_keywords: List[str], industry: str) -> List[KeywordSuggestion]:
        """Generate competitor-based keywords"""
        competitor_keywords = []
        
        # Comparative keywords
        comparative_patterns = [
            "{seed} vs",
            "alternative to {seed}",
            "better than {seed}",
            "{seed} comparison",
            "best {seed} alternative"
        ]
        
        for seed in seed_keywords:
            for pattern in comparative_patterns:
                competitor_kw = pattern.format(seed=seed)
                metrics = self._calculate_keyword_metrics(competitor_kw, KeywordType.COMPETITOR)
                suggestion = KeywordSuggestion(
                    keyword=competitor_kw,
                    keyword_type=KeywordType.COMPETITOR,
                    search_intent=SearchIntent.COMMERCIAL,
                    metrics=metrics,
                    related_terms=self._get_related_terms(competitor_kw),
                    confidence_score=0.6
                )
                competitor_keywords.append(suggestion)
        
        return competitor_keywords[:10]  # Limit to top 10

    def _calculate_keyword_metrics(self, keyword: str, keyword_type: KeywordType) -> KeywordMetrics:
        """Calculate metrics for a keyword (simulated data for demo)"""
        # In a real implementation, this would query actual search data APIs
        
        word_count = len(keyword.split())
        
        # Simulate search volume based on keyword characteristics
        base_volume = 1000
        if keyword_type == KeywordType.PRIMARY:
            search_volume = base_volume * 10
        elif keyword_type == KeywordType.TRENDING:
            search_volume = base_volume * 15
        elif keyword_type == KeywordType.LONG_TAIL:
            search_volume = base_volume // (word_count * 2)
        else:
            search_volume = base_volume * 3
        
        # Simulate competition (longer keywords typically have less competition)
        competition_level = max(0.1, 1.0 - (word_count * 0.15))
        
        # Simulate CPC
        cpc = max(0.5, competition_level * 2.0 + (1.0 / word_count))
        
        # Simulate difficulty
        difficulty = competition_level * 100
        
        # Calculate relevance score
        relevance_score = min(1.0, 0.9 - (word_count * 0.1) + (0.1 if keyword_type == KeywordType.PRIMARY else 0))
        
        # Trend direction (simplified)
        trend_direction = "up" if keyword_type == KeywordType.TRENDING else "stable"
        
        return KeywordMetrics(
            search_volume=int(search_volume),
            competition_level=round(competition_level, 2),
            cpc=round(cpc, 2),
            difficulty=round(difficulty, 1),
            relevance_score=round(relevance_score, 2),
            trend_direction=trend_direction
        )

    def _classify_search_intent(self, keyword: str) -> SearchIntent:
        """Classify the search intent of a keyword"""
        keyword_lower = keyword.lower()
        
        # Informational intent indicators
        if any(word in keyword_lower for word in [
            'how', 'what', 'why', 'when', 'where', 'guide', 'tutorial', 
            'tips', 'learn', 'understand', 'explain'
        ]):
            return SearchIntent.INFORMATIONAL
        
        # Transactional intent indicators
        if any(word in keyword_lower for word in [
            'buy', 'purchase', 'order', 'deal', 'discount', 'price', 
            'cost', 'cheap', 'sale', 'shop'
        ]):
            return SearchIntent.TRANSACTIONAL
        
        # Commercial intent indicators
        if any(word in keyword_lower for word in [
            'best', 'top', 'review', 'compare', 'vs', 'alternative', 
            'recommend', 'choice'
        ]):
            return SearchIntent.COMMERCIAL
        
        # Default to navigational
        return SearchIntent.NAVIGATIONAL

    def _get_related_terms(self, keyword: str) -> List[str]:
        """
Get related terms for a keyword"""
        # Simplified related terms generation
        base_terms = keyword.split()
        related = []
        
        # Synonyms and variations (simplified)
        synonym_map = {
            'marketing': ['advertising', 'promotion', 'branding'],
            'business': ['company', 'enterprise', 'organization'],
            'content': ['material', 'information', 'data'],
            'social': ['community', 'network', 'platform'],
            'media': ['platform', 'channel', 'outlet'],
            'strategy': ['plan', 'approach', 'method'],
            'digital': ['online', 'internet', 'web'],
            'tips': ['advice', 'suggestions', 'recommendations'],
            'guide': ['tutorial', 'manual', 'handbook']
        }
        
        for term in base_terms:
            if term.lower() in synonym_map:
                related.extend(synonym_map[term.lower()])
        
        return related[:5]  # Limit to 5 related terms

    def _get_semantic_related_terms(self, keyword: str) -> List[str]:
        """
Get semantically related terms"""
        # Simplified semantic relationships
        semantic_map = {
            'marketing': ['seo', 'content marketing', 'email marketing', 'social media marketing'],
            'business': ['entrepreneurship', 'startup', 'revenue', 'growth'],
            'content': ['blogging', 'writing', 'storytelling', 'copywriting'],
            'social media': ['instagram', 'facebook', 'twitter', 'linkedin'],
            'seo': ['keywords', 'backlinks', 'ranking', 'optimization'],
            'digital': ['technology', 'online', 'internet', 'software']
        }
        
        keyword_lower = keyword.lower()
        related = []
        
        for key, terms in semantic_map.items():
            if key in keyword_lower:
                related.extend(terms)
        
        return related[:8]

    def _filter_for_platform(self, keywords: List[KeywordSuggestion], platform: str) -> List[KeywordSuggestion]:
        """
Filter keywords for specific platform"""
        platform_keywords = {
            'instagram': ['photo', 'visual', 'story', 'reel', 'hashtag'],
            'youtube': ['video', 'tutorial', 'how to', 'watch', 'channel'],
            'twitter': ['news', 'trending', 'update', 'breaking'],
            'linkedin': ['professional', 'business', 'career', 'industry'],
            'tiktok': ['viral', 'trending', 'challenge', 'creative']
        }
        
        if platform not in platform_keywords:
            return keywords
        
        platform_terms = platform_keywords[platform]
        filtered = []
        
        for keyword_suggestion in keywords:
            keyword = keyword_suggestion.keyword.lower()
            # Boost keywords that contain platform-specific terms
            if any(term in keyword for term in platform_terms):
                keyword_suggestion.confidence_score *= 1.2
                keyword_suggestion.metrics.relevance_score = min(1.0, keyword_suggestion.metrics.relevance_score * 1.1)
            
            filtered.append(keyword_suggestion)
        
        # Sort by relevance and confidence
        filtered.sort(key=lambda x: x.confidence_score * x.metrics.relevance_score, reverse=True)
        return filtered

    def _initialize_keyword_database(self) -> Dict[str, Any]:
        """
Initialize internal keyword database"""
        return {
            'high_volume_terms': [
                'marketing', 'business', 'social media', 'content', 'digital',
                'strategy', 'tips', 'guide', 'best', 'how to'
            ],
            'trending_modifiers': [
                '2025', 'latest', 'new', 'updated', 'modern', 'advanced'
            ]
        }

    def _get_stop_words(self, language: str) -> Set[str]:
        """
Get stop words for the specified language"""
        # Simplified stop words list
        if language == "en":
            return {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'would', 'you', 'your', 'have', 'had',
                'can', 'could', 'should', 'may', 'might', 'must', 'shall', 'this',
                'these', 'those', 'they', 'them', 'their', 'we', 'us', 'our'
            }
        return set()  # Return empty set for other languages

    def _get_trending_topics(self) -> List[str]:
        """Get current trending topics"""
        # Simplified trending topics
        return [
            'ai', 'artificial intelligence', 'machine learning', '2025',
            'sustainability', 'remote work', 'digital transformation',
            'automation', 'innovation', 'technology'
        ]

    def analyze_keyword_competition(self, keyword: str) -> Dict[str, Any]:
        """
Analyze competition for a specific keyword"""
        metrics = self._calculate_keyword_metrics(keyword, KeywordType.PRIMARY)
        
        return {
            'keyword': keyword,
            'competition_level': metrics.competition_level,
            'difficulty_score': metrics.difficulty,
            'estimated_traffic': metrics.search_volume,
            'cpc': metrics.cpc,
            'recommendation': self._get_competition_recommendation(metrics.difficulty)
        }

    def _get_competition_recommendation(self, difficulty: float) -> str:
        """
Get recommendation based on keyword difficulty"""
        if difficulty < 30:
            return "Low competition - Good opportunity for quick ranking"
        elif difficulty < 60:
            return "Medium competition - Achievable with consistent effort"
        elif difficulty < 80:
            return "High competition - Requires strong authority and time"
        else:
            return "Very high competition - Consider long-tail alternatives"

    def export_keywords(self, result: KeywordResearchResult, format: str = "json") -> str:
        """Export keyword research results in specified format"""
        if format == "json":
            return self._export_to_json(result)
        elif format == "csv":
            return self._export_to_csv(result)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_to_json(self, result: KeywordResearchResult) -> str:
        """Export results to JSON format"""
        export_data = {
            'metadata': result.research_metadata,
            'total_keywords': result.total_keywords,
            'primary_keywords': [self._keyword_to_dict(kw) for kw in result.primary_keywords],
            'secondary_keywords': [self._keyword_to_dict(kw) for kw in result.secondary_keywords],
            'long_tail_keywords': [self._keyword_to_dict(kw) for kw in result.long_tail_keywords],
            'semantic_keywords': [self._keyword_to_dict(kw) for kw in result.semantic_keywords],
            'trending_keywords': [self._keyword_to_dict(kw) for kw in result.trending_keywords],
            'competitor_keywords': [self._keyword_to_dict(kw) for kw in result.competitor_keywords]
        }
        return json.dumps(export_data, indent=2)

    def _keyword_to_dict(self, keyword_suggestion: KeywordSuggestion) -> Dict[str, Any]:
        """
Convert KeywordSuggestion to dictionary"""
        return {
            'keyword': keyword_suggestion.keyword,
            'type': keyword_suggestion.keyword_type.value,
            'search_intent': keyword_suggestion.search_intent.value,
            'search_volume': keyword_suggestion.metrics.search_volume,
            'competition': keyword_suggestion.metrics.competition_level,
            'difficulty': keyword_suggestion.metrics.difficulty,
            'cpc': keyword_suggestion.metrics.cpc,
            'relevance_score': keyword_suggestion.metrics.relevance_score,
            'confidence_score': keyword_suggestion.confidence_score,
            'related_terms': keyword_suggestion.related_terms
        }

    def _export_to_csv(self, result: KeywordResearchResult) -> str:
        """
Export results to CSV format"""
        csv_lines = ["Keyword,Type,Search Intent,Search Volume,Competition,Difficulty,CPC,Relevance,Confidence"]
        
        all_keywords = (
            result.primary_keywords + result.secondary_keywords + 
            result.long_tail_keywords + result.semantic_keywords +
            result.trending_keywords + result.competitor_keywords
        )
        
        for kw in all_keywords:
            line = f'"{kw.keyword}",{kw.keyword_type.value},{kw.search_intent.value},' \
                   f'{kw.metrics.search_volume},{kw.metrics.competition_level},' \
                   f'{kw.metrics.difficulty},{kw.metrics.cpc},{kw.metrics.relevance_score},' \
                   f'{kw.confidence_score}'
            csv_lines.append(line)
        
        return '\n'.join(csv_lines)


# Export for module usage
__all__ = [
    "KeywordGeneratorAI", 
    "KeywordType", 
    "SearchIntent", 
    "KeywordMetrics",
    "KeywordSuggestion", 
    "KeywordResearchResult"
]