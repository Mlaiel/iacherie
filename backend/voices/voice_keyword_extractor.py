"""Voice Keyword Extractor - Advanced Voice Content SEO Keyword Extraction Engine

Sophisticated keyword extraction and SEO optimization system for voice content.
Analyzes voice content to extract relevant keywords, trending terms, and optimization opportunities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import re
from collections import Counter, defaultdict
import math

class KeywordType(Enum):
    """Keyword classification types"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    LONG_TAIL = "long_tail"
    BRANDED = "branded"
    TRENDING = "trending"
    SEASONAL = "seasonal"
    LOCATION = "location"
    TOPIC = "topic"
    EMOTION = "emotion"
    GENRE = "genre"
    TECHNICAL = "technical"

class ExtractionMethod(Enum):
    """Keyword extraction methods"""
    TRANSCRIPT_ANALYSIS = "transcript_analysis"
    AUDIO_RECOGNITION = "audio_recognition"
    METADATA_MINING = "metadata_mining"
    CONTEXT_ANALYSIS = "context_analysis"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    TREND_ANALYSIS = "trend_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"

class SearchVolume(Enum):
    """Search volume categories"""
    VERY_LOW = "very_low"      # < 100 searches/month
    LOW = "low"                # 100-1000 searches/month
    MEDIUM = "medium"          # 1000-10000 searches/month
    HIGH = "high"              # 10000-100000 searches/month
    VERY_HIGH = "very_high"    # > 100000 searches/month

class CompetitionLevel(Enum):
    """Keyword competition levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class TrendDirection(Enum):
    """Keyword trend directions"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    BREAKOUT = "breakout"

@dataclass
class KeywordMetrics:
    """Keyword performance metrics"""
    search_volume: int
    competition_score: float  # 0.0 to 1.0
    cpc_usd: float  # Cost per click
    trend_score: float  # -1.0 to 1.0 (declining to rising)
    difficulty_score: float  # 0.0 to 1.0
    opportunity_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    voice_specific_score: float  # 0.0 to 1.0

@dataclass
class ExtractedKeyword:
    """Extracted keyword with metadata"""
    keyword: str
    keyword_type: KeywordType
    extraction_method: ExtractionMethod
    frequency: int
    position_in_content: List[int]
    context_snippets: List[str]
    confidence_score: float  # 0.0 to 1.0
    metrics: Optional[KeywordMetrics] = None
    related_keywords: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    semantic_cluster: Optional[str] = None

@dataclass
class VoiceContentAnalysis:
    """Voice content analysis result"""
    content_id: str
    content_type: str  # podcast, audiobook, music, etc.
    duration_seconds: int
    language: str
    transcript: Optional[str]
    extracted_keywords: List[ExtractedKeyword]
    keyword_density: Dict[str, float]
    topic_clusters: Dict[str, List[str]]
    sentiment_keywords: Dict[str, List[str]]
    technical_quality_keywords: List[str]
    brand_keywords: List[str]
    trending_opportunities: List[str]
    seo_recommendations: List[str]
    analysis_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CompetitorKeywordData:
    """Competitor keyword analysis data"""
    competitor_id: str
    competitor_name: str
    keywords: List[str]
    ranking_positions: Dict[str, int]  # keyword -> position
    content_volume: int
    engagement_metrics: Dict[str, float]
    gap_opportunities: List[str]  # Keywords they rank for that we don't

@dataclass
class KeywordTrend:
    """Keyword trend analysis"""
    keyword: str
    trend_direction: TrendDirection
    search_volume_history: List[Tuple[datetime, int]]
    competition_history: List[Tuple[datetime, float]]
    seasonal_patterns: Dict[str, float]  # month -> relative_volume
    related_trending_terms: List[str]
    growth_rate: float  # percentage change
    forecast_data: Dict[str, Any]

class VoiceKeywordExtractor:
    """Advanced Voice Content Keyword Extraction Engine
    
    Comprehensive system for extracting, analyzing, and optimizing keywords
    from voice content for SEO and discoverability enhancement.
    """
    
    def __init__(self):
        """Initialize voice keyword extractor"""
        self.stopwords: Set[str] = set()
        self.voice_specific_terms: Dict[str, float] = {}
        self.trending_keywords: Dict[str, KeywordTrend] = {}
        self.competitor_data: Dict[str, CompetitorKeywordData] = {}
        self.semantic_clusters: Dict[str, List[str]] = {}
        self.keyword_database: Dict[str, KeywordMetrics] = {}
        
        self._initialize_stopwords()
        self._initialize_voice_terms()
        self._initialize_semantic_clusters()
    
    def _initialize_stopwords(self):
        """Initialize stopwords for keyword filtering"""
        self.stopwords = {
            # Common English stopwords
            "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
            "to", "was", "were", "will", "with", "the", "this", "but", "they",
            "have", "had", "what", "said", "each", "which", "their", "time",
            "if", "up", "out", "many", "then", "them", "these", "so", "some",
            "her", "would", "make", "like", "into", "him", "has", "two", "more",
            "very", "what", "know", "just", "first", "get", "over", "think",
            "also", "your", "work", "life", "only", "can", "still", "should",
            "after", "being", "now", "made", "before", "here", "through",
            "when", "where", "much", "go", "me", "back", "with", "well",
            "were", "been", "have", "there", "could", "see", "other", "than",
            "then", "them", "these", "way", "she", "may", "say", "says", "said",
            "each", "which", "do", "how", "their", "if", "will", "up", "other",
            "about", "out", "many", "then", "them", "these", "so", "some", "her",
            "would", "make", "like", "into", "time", "has", "look", "two", "more",
            "write", "go", "see", "number", "no", "way", "could", "people",
            "my", "than", "first", "water", "been", "call", "who", "oil", "its",
            "now", "find", "long", "down", "day", "did", "get", "come", "made",
            "may", "part"
        }
    
    def _initialize_voice_terms(self):
        """Initialize voice-specific terminology weights"""
        self.voice_specific_terms = {
            # Audio quality terms
            "audio": 1.5, "sound": 1.4, "voice": 2.0, "vocal": 1.8, "singing": 1.7,
            "microphone": 1.3, "recording": 1.6, "studio": 1.4, "acoustics": 1.3,
            
            # Musical terms
            "music": 1.8, "song": 1.7, "melody": 1.5, "harmony": 1.6, "rhythm": 1.5,
            "beat": 1.4, "tempo": 1.3, "pitch": 1.6, "tone": 1.5, "chord": 1.4,
            
            # Podcast terms
            "podcast": 2.0, "episode": 1.8, "interview": 1.6, "discussion": 1.4,
            "talk": 1.5, "conversation": 1.5, "host": 1.6, "guest": 1.4,
            
            # Performance terms
            "performance": 1.7, "live": 1.6, "concert": 1.5, "show": 1.4,
            "audience": 1.5, "stage": 1.3, "entertainment": 1.4,
            
            # Technical terms
            "frequency": 1.2, "amplitude": 1.1, "compression": 1.2, "equalizer": 1.1,
            "reverb": 1.2, "echo": 1.1, "distortion": 1.1, "filter": 1.1
        }
    
    def _initialize_semantic_clusters(self):
        """Initialize semantic keyword clusters"""
        self.semantic_clusters = {
            "music_production": [
                "recording", "mixing", "mastering", "studio", "producer", "engineer",
                "track", "album", "single", "demo", "composition", "arrangement"
            ],
            "vocal_techniques": [
                "singing", "vocal", "breathing", "projection", "resonance", "vibrato",
                "falsetto", "chest voice", "head voice", "vocal range", "pitch control"
            ],
            "podcast_content": [
                "podcast", "episode", "interview", "host", "guest", "discussion",
                "talk show", "series", "season", "subscriber", "listener"
            ],
            "audio_technology": [
                "microphone", "headphones", "speakers", "audio interface", "preamp",
                "compressor", "equalizer", "reverb", "delay", "distortion"
            ],
            "music_genres": [
                "pop", "rock", "jazz", "classical", "electronic", "hip hop", "country",
                "folk", "blues", "reggae", "metal", "punk", "indie", "alternative"
            ],
            "content_creation": [
                "creator", "content", "upload", "publish", "share", "viral", "trending",
                "engagement", "followers", "subscribers", "views", "likes"
            ]
        }
    
    async def extract_keywords_from_voice_content(
        self,
        content_id: str,
        audio_file_path: Optional[str] = None,
        transcript: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        extraction_methods: List[ExtractionMethod] = None
    ) -> VoiceContentAnalysis:
        """Extract keywords from voice content using multiple methods"""
        
        if not extraction_methods:
            extraction_methods = [
                ExtractionMethod.TRANSCRIPT_ANALYSIS,
                ExtractionMethod.METADATA_MINING,
                ExtractionMethod.CONTEXT_ANALYSIS,
                ExtractionMethod.SEMANTIC_ANALYSIS
            ]
        
        # Initialize analysis result
        analysis = VoiceContentAnalysis(
            content_id=content_id,
            content_type=metadata.get("content_type", "unknown") if metadata else "unknown",
            duration_seconds=metadata.get("duration", 0) if metadata else 0,
            language=metadata.get("language", "en") if metadata else "en",
            transcript=transcript,
            extracted_keywords=[],
            keyword_density={},
            topic_clusters={},
            sentiment_keywords={},
            technical_quality_keywords=[],
            brand_keywords=[],
            trending_opportunities=[],
            seo_recommendations=[]
        )
        
        all_keywords = []
        
        # Extract keywords using different methods
        for method in extraction_methods:
            keywords = await self._extract_by_method(
                method, audio_file_path, transcript, metadata
            )
            all_keywords.extend(keywords)
        
        # Consolidate and rank keywords
        consolidated_keywords = self._consolidate_keywords(all_keywords)
        
        # Enrich with metrics and additional data
        enriched_keywords = []
        for keyword in consolidated_keywords:
            enriched_keyword = await self._enrich_keyword(keyword)
            enriched_keywords.append(enriched_keyword)
        
        analysis.extracted_keywords = enriched_keywords
        
        # Calculate keyword density
        analysis.keyword_density = self._calculate_keyword_density(
            enriched_keywords, transcript
        )
        
        # Perform additional analysis
        analysis.topic_clusters = self._identify_topic_clusters(enriched_keywords)
        analysis.sentiment_keywords = self._extract_sentiment_keywords(transcript)
        analysis.technical_quality_keywords = self._extract_technical_keywords(enriched_keywords)
        analysis.brand_keywords = self._extract_brand_keywords(enriched_keywords, metadata)
        analysis.trending_opportunities = await self._identify_trending_opportunities(enriched_keywords)
        analysis.seo_recommendations = await self._generate_seo_recommendations(analysis)
        
        return analysis
    
    async def _extract_by_method(
        self,
        method: ExtractionMethod,
        audio_file_path: Optional[str],
        transcript: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> List[ExtractedKeyword]:
        """Extract keywords using specific method"""
        
        if method == ExtractionMethod.TRANSCRIPT_ANALYSIS:
            return await self._extract_from_transcript(transcript)
        elif method == ExtractionMethod.METADATA_MINING:
            return await self._extract_from_metadata(metadata)
        elif method == ExtractionMethod.CONTEXT_ANALYSIS:
            return await self._extract_from_context(transcript, metadata)
        elif method == ExtractionMethod.SEMANTIC_ANALYSIS:
            return await self._extract_semantic_keywords(transcript)
        elif method == ExtractionMethod.AUDIO_RECOGNITION:
            return await self._extract_from_audio(audio_file_path)
        elif method == ExtractionMethod.TREND_ANALYSIS:
            return await self._extract_trending_keywords(transcript, metadata)
        else:
            return []
    
    async def _extract_from_transcript(self, transcript: Optional[str]) -> List[ExtractedKeyword]:
        """Extract keywords from transcript text"""
        
        if not transcript:
            return []
        
        keywords = []
        
        # Clean and tokenize transcript
        cleaned_text = self._clean_text(transcript)
        words = self._tokenize(cleaned_text)
        
        # Extract single words
        word_freq = Counter(words)
        for word, freq in word_freq.most_common(50):  # Top 50 words
            if (len(word) > 2 and 
                word.lower() not in self.stopwords and
                freq > 1):
                
                keyword = ExtractedKeyword(
                    keyword=word,
                    keyword_type=KeywordType.PRIMARY if freq > 5 else KeywordType.SECONDARY,
                    extraction_method=ExtractionMethod.TRANSCRIPT_ANALYSIS,
                    frequency=freq,
                    position_in_content=self._find_word_positions(word, transcript),
                    context_snippets=self._extract_context_snippets(word, transcript),
                    confidence_score=min(1.0, freq / 10.0)
                )
                keywords.append(keyword)
        
        # Extract phrases (2-3 words)
        phrases = self._extract_phrases(words, 2, 3)
        phrase_freq = Counter(phrases)
        
        for phrase, freq in phrase_freq.most_common(20):  # Top 20 phrases
            if freq > 1:
                keyword = ExtractedKeyword(
                    keyword=" ".join(phrase),
                    keyword_type=KeywordType.LONG_TAIL,
                    extraction_method=ExtractionMethod.TRANSCRIPT_ANALYSIS,
                    frequency=freq,
                    position_in_content=self._find_phrase_positions(phrase, transcript),
                    context_snippets=self._extract_context_snippets(" ".join(phrase), transcript),
                    confidence_score=min(1.0, freq / 5.0)
                )
                keywords.append(keyword)
        
        return keywords
    
    async def _extract_from_metadata(self, metadata: Optional[Dict[str, Any]]) -> List[ExtractedKeyword]:
        """Extract keywords from content metadata"""
        
        if not metadata:
            return []
        
        keywords = []
        
        # Extract from title
        if "title" in metadata:
            title_keywords = self._extract_from_text(
                metadata["title"], KeywordType.PRIMARY
            )
            keywords.extend(title_keywords)
        
        # Extract from description
        if "description" in metadata:
            desc_keywords = self._extract_from_text(
                metadata["description"], KeywordType.SECONDARY
            )
            keywords.extend(desc_keywords)
        
        # Extract from tags
        if "tags" in metadata and isinstance(metadata["tags"], list):
            for tag in metadata["tags"]:
                keyword = ExtractedKeyword(
                    keyword=tag,
                    keyword_type=KeywordType.TOPIC,
                    extraction_method=ExtractionMethod.METADATA_MINING,
                    frequency=1,
                    position_in_content=[0],
                    context_snippets=[f"Tagged as: {tag}"],
                    confidence_score=0.9
                )
                keywords.append(keyword)
        
        # Extract from genre/category
        if "genre" in metadata:
            keyword = ExtractedKeyword(
                keyword=metadata["genre"],
                keyword_type=KeywordType.GENRE,
                extraction_method=ExtractionMethod.METADATA_MINING,
                frequency=1,
                position_in_content=[0],
                context_snippets=[f"Genre: {metadata['genre']}"],
                confidence_score=0.95
            )
            keywords.append(keyword)
        
        return keywords
    
    async def _extract_from_context(
        self, 
        transcript: Optional[str], 
        metadata: Optional[Dict[str, Any]]
    ) -> List[ExtractedKeyword]:
        """Extract keywords from contextual analysis"""
        
        keywords = []
        
        if not transcript:
            return keywords
        
        # Extract emotional context
        emotion_keywords = self._extract_emotional_keywords(transcript)
        keywords.extend(emotion_keywords)
        
        # Extract temporal context
        temporal_keywords = self._extract_temporal_keywords(transcript)
        keywords.extend(temporal_keywords)
        
        # Extract location context
        location_keywords = self._extract_location_keywords(transcript)
        keywords.extend(location_keywords)
        
        return keywords
    
    async def _extract_semantic_keywords(self, transcript: Optional[str]) -> List[ExtractedKeyword]:
        """Extract keywords using semantic analysis"""
        
        if not transcript:
            return []
        
        keywords = []
        
        # Find semantically related terms
        for cluster_name, cluster_terms in self.semantic_clusters.items():
            found_terms = []
            for term in cluster_terms:
                if term.lower() in transcript.lower():
                    found_terms.append(term)
            
            if found_terms:
                # Create cluster-based keyword
                keyword = ExtractedKeyword(
                    keyword=cluster_name,
                    keyword_type=KeywordType.TOPIC,
                    extraction_method=ExtractionMethod.SEMANTIC_ANALYSIS,
                    frequency=len(found_terms),
                    position_in_content=[0],
                    context_snippets=[f"Related terms: {', '.join(found_terms)}"],
                    confidence_score=min(1.0, len(found_terms) / len(cluster_terms)),
                    related_keywords=found_terms,
                    semantic_cluster=cluster_name
                )
                keywords.append(keyword)
        
        return keywords
    
    async def _extract_from_audio(self, audio_file_path: Optional[str]) -> List[ExtractedKeyword]:
        """Extract keywords from audio analysis"""
        
        if not audio_file_path:
            return []
        
        # Simulate audio analysis
        # In real implementation would use audio processing libraries
        keywords = []
        
        # Example: detect music vs speech
        # This would be done through actual audio analysis
        audio_type_keyword = ExtractedKeyword(
            keyword="music",  # or "speech", "podcast", etc.
            keyword_type=KeywordType.TECHNICAL,
            extraction_method=ExtractionMethod.AUDIO_RECOGNITION,
            frequency=1,
            position_in_content=[0],
            context_snippets=["Detected from audio analysis"],
            confidence_score=0.8
        )
        keywords.append(audio_type_keyword)
        
        return keywords
    
    async def _extract_trending_keywords(
        self, 
        transcript: Optional[str], 
        metadata: Optional[Dict[str, Any]]
    ) -> List[ExtractedKeyword]:
        """Extract trending keywords and opportunities"""
        
        keywords = []
        
        # Check against trending keyword database
        if transcript:
            words = self._tokenize(self._clean_text(transcript))
            for word in words:
                if word in self.trending_keywords:
                    trend_data = self.trending_keywords[word]
                    if trend_data.trend_direction in [TrendDirection.RISING, TrendDirection.BREAKOUT]:
                        keyword = ExtractedKeyword(
                            keyword=word,
                            keyword_type=KeywordType.TRENDING,
                            extraction_method=ExtractionMethod.TREND_ANALYSIS,
                            frequency=transcript.lower().count(word.lower()),
                            position_in_content=self._find_word_positions(word, transcript),
                            context_snippets=self._extract_context_snippets(word, transcript),
                            confidence_score=0.9
                        )
                        keywords.append(keyword)
        
        return keywords
    
    def _consolidate_keywords(self, keywords: List[ExtractedKeyword]) -> List[ExtractedKeyword]:
        """Consolidate duplicate keywords from different extraction methods"""
        
        keyword_map = {}
        
        for keyword in keywords:
            key = keyword.keyword.lower()
            
            if key in keyword_map:
                # Merge with existing keyword
                existing = keyword_map[key]
                existing.frequency += keyword.frequency
                existing.position_in_content.extend(keyword.position_in_content)
                existing.context_snippets.extend(keyword.context_snippets)
                existing.confidence_score = max(existing.confidence_score, keyword.confidence_score)
                
                # Merge related keywords
                existing.related_keywords.extend(keyword.related_keywords)
                existing.synonyms.extend(keyword.synonyms)
                
                # Remove duplicates
                existing.related_keywords = list(set(existing.related_keywords))
                existing.synonyms = list(set(existing.synonyms))
                existing.context_snippets = list(set(existing.context_snippets))
                existing.position_in_content = sorted(list(set(existing.position_in_content)))
                
            else:
                keyword_map[key] = keyword
        
        # Sort by confidence score and frequency
        consolidated = list(keyword_map.values())
        consolidated.sort(
            key=lambda k: (k.confidence_score, k.frequency), 
            reverse=True
        )
        
        return consolidated
    
    async def _enrich_keyword(self, keyword: ExtractedKeyword) -> ExtractedKeyword:
        """Enrich keyword with additional metrics and data"""
        
        # Get keyword metrics from database or API
        metrics = await self._get_keyword_metrics(keyword.keyword)
        keyword.metrics = metrics
        
        # Find related keywords and synonyms
        related = await self._find_related_keywords(keyword.keyword)
        keyword.related_keywords.extend(related)
        keyword.related_keywords = list(set(keyword.related_keywords))
        
        # Find synonyms
        synonyms = await self._find_synonyms(keyword.keyword)
        keyword.synonyms.extend(synonyms)
        keyword.synonyms = list(set(keyword.synonyms))
        
        # Apply voice-specific scoring
        voice_score = self._calculate_voice_relevance_score(keyword.keyword)
        if keyword.metrics:
            keyword.metrics.voice_specific_score = voice_score
        
        return keyword
    
    async def _get_keyword_metrics(self, keyword: str) -> KeywordMetrics:
        """Get keyword performance metrics"""
        
        # Check local database first
        if keyword in self.keyword_database:
            return self.keyword_database[keyword]
        
        # Simulate keyword metrics
        # In real implementation would call keyword research APIs
        base_volume = len(keyword) * 1000  # Simplified
        
        metrics = KeywordMetrics(
            search_volume=base_volume,
            competition_score=random.uniform(0.3, 0.8),
            cpc_usd=random.uniform(0.1, 2.0),
            trend_score=random.uniform(-0.3, 0.5),
            difficulty_score=random.uniform(0.2, 0.9),
            opportunity_score=random.uniform(0.4, 0.9),
            relevance_score=random.uniform(0.6, 1.0),
            voice_specific_score=0.0  # Will be calculated separately
        )
        
        # Cache metrics
        self.keyword_database[keyword] = metrics
        
        return metrics
    
    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords"""
        
        related = []
        
        # Check semantic clusters
        for cluster_name, terms in self.semantic_clusters.items():
            if keyword.lower() in [term.lower() for term in terms]:
                related.extend([term for term in terms if term.lower() != keyword.lower()])
        
        # Add voice-specific related terms
        if keyword.lower() in self.voice_specific_terms:
            # Find other terms with high voice relevance
            related.extend([
                term for term, score in self.voice_specific_terms.items() 
                if score > 1.3 and term != keyword.lower()
            ])
        
        return related[:10]  # Limit to top 10
    
    async def _find_synonyms(self, keyword: str) -> List[str]:
        """Find keyword synonyms"""
        
        # Simplified synonym mapping
        synonym_map = {
            "music": ["audio", "sound", "track", "song"],
            "voice": ["vocal", "speech", "narration"],
            "podcast": ["audio show", "talk show", "radio show"],
            "recording": ["audio", "track", "session"],
            "singing": ["vocals", "voice", "vocal performance"]
        }
        
        return synonym_map.get(keyword.lower(), [])
    
    def _calculate_voice_relevance_score(self, keyword: str) -> float:
        """Calculate voice-specific relevance score"""
        
        base_score = 0.5
        
        # Check voice-specific terms
        if keyword.lower() in self.voice_specific_terms:
            weight = self.voice_specific_terms[keyword.lower()]
            base_score = min(1.0, weight / 2.0)
        
        # Check semantic clusters
        for cluster_name in self.semantic_clusters:
            if keyword.lower() in [term.lower() for term in self.semantic_clusters[cluster_name]]:
                base_score += 0.2
        
        return min(1.0, base_score)
    
    def _calculate_keyword_density(
        self, 
        keywords: List[ExtractedKeyword], 
        transcript: Optional[str]
    ) -> Dict[str, float]:
        """Calculate keyword density in content"""
        
        if not transcript:
            return {}
        
        total_words = len(self._tokenize(self._clean_text(transcript)))
        density = {}
        
        for keyword in keywords:
            keyword_words = len(keyword.keyword.split())
            density[keyword.keyword] = (keyword.frequency * keyword_words) / total_words
        
        return density
    
    def _identify_topic_clusters(self, keywords: List[ExtractedKeyword]) -> Dict[str, List[str]]:
        """Identify topic clusters from extracted keywords"""
        
        clusters = defaultdict(list)
        
        for keyword in keywords:
            if keyword.semantic_cluster:
                clusters[keyword.semantic_cluster].append(keyword.keyword)
            elif keyword.keyword_type == KeywordType.TOPIC:
                clusters["topics"].append(keyword.keyword)
            elif keyword.keyword_type == KeywordType.GENRE:
                clusters["genres"].append(keyword.keyword)
            elif keyword.keyword_type == KeywordType.TECHNICAL:
                clusters["technical"].append(keyword.keyword)
        
        return dict(clusters)
    
    def _extract_sentiment_keywords(self, transcript: Optional[str]) -> Dict[str, List[str]]:
        """Extract sentiment-related keywords"""
        
        if not transcript:
            return {}
        
        sentiment_keywords = {
            "positive": [],
            "negative": [],
            "neutral": []
        }
        
        # Simplified sentiment analysis
        positive_words = [
            "amazing", "great", "excellent", "wonderful", "fantastic", "beautiful",
            "love", "enjoy", "happy", "excited", "thrilled", "impressed"
        ]
        
        negative_words = [
            "terrible", "awful", "bad", "horrible", "disappointed", "frustrated",
            "angry", "sad", "upset", "annoying", "boring", "difficult"
        ]
        
        words = self._tokenize(self._clean_text(transcript))
        
        for word in words:
            if word.lower() in positive_words:
                sentiment_keywords["positive"].append(word)
            elif word.lower() in negative_words:
                sentiment_keywords["negative"].append(word)
        
        return sentiment_keywords
    
    def _extract_technical_keywords(self, keywords: List[ExtractedKeyword]) -> List[str]:
        """Extract technical quality keywords"""
        
        technical_keywords = []
        
        for keyword in keywords:
            if (keyword.keyword_type == KeywordType.TECHNICAL or
                keyword.keyword.lower() in self.voice_specific_terms):
                technical_keywords.append(keyword.keyword)
        
        return technical_keywords
    
    def _extract_brand_keywords(
        self, 
        keywords: List[ExtractedKeyword], 
        metadata: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Extract brand-related keywords"""
        
        brand_keywords = []
        
        # Check for branded keywords
        for keyword in keywords:
            if keyword.keyword_type == KeywordType.BRANDED:
                brand_keywords.append(keyword.keyword)
        
        # Check metadata for brand information
        if metadata:
            if "creator" in metadata:
                brand_keywords.append(metadata["creator"])
            if "brand" in metadata:
                brand_keywords.append(metadata["brand"])
        
        return brand_keywords
    
    async def _identify_trending_opportunities(self, keywords: List[ExtractedKeyword]) -> List[str]:
        """Identify trending keyword opportunities"""
        
        opportunities = []
        
        for keyword in keywords:
            if keyword.keyword_type == KeywordType.TRENDING:
                opportunities.append(keyword.keyword)
            elif keyword.metrics and keyword.metrics.trend_score > 0.3:
                opportunities.append(keyword.keyword)
        
        # Add related trending terms
        for keyword in keywords:
            if keyword.keyword in self.trending_keywords:
                trend_data = self.trending_keywords[keyword.keyword]
                opportunities.extend(trend_data.related_trending_terms)
        
        return list(set(opportunities))
    
    async def _generate_seo_recommendations(self, analysis: VoiceContentAnalysis) -> List[str]:
        """Generate SEO optimization recommendations"""
        
        recommendations = []
        
        # Keyword density recommendations
        high_density_keywords = [
            kw for kw, density in analysis.keyword_density.items() 
            if density > 0.03  # More than 3%
        ]
        
        if high_density_keywords:
            recommendations.append(
                f"Reduce keyword density for: {', '.join(high_density_keywords[:3])}"
            )
        
        # Long-tail keyword recommendations
        long_tail_count = len([
            kw for kw in analysis.extracted_keywords 
            if kw.keyword_type == KeywordType.LONG_TAIL
        ])
        
        if long_tail_count < 5:
            recommendations.append(
                "Add more long-tail keywords to improve specific search targeting"
            )
        
        # Trending keyword recommendations
        if analysis.trending_opportunities:
            recommendations.append(
                f"Consider incorporating trending terms: {', '.join(analysis.trending_opportunities[:3])}"
            )
        
        # Technical keyword recommendations
        if len(analysis.technical_quality_keywords) < 3:
            recommendations.append(
                "Add more technical quality keywords to improve audio content discoverability"
            )
        
        # Semantic cluster recommendations
        cluster_count = len(analysis.topic_clusters)
        if cluster_count < 3:
            recommendations.append(
                "Expand content to cover more topic clusters for broader keyword coverage"
            )
        
        return recommendations
    
    # Utility methods
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove special characters, normalize whitespace
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return [word.lower() for word in text.split() if len(word) > 1]
    
    def _extract_phrases(self, words: List[str], min_length: int, max_length: int) -> List[Tuple[str, ...]]:
        """Extract phrases of specified length"""
        phrases = []
        
        for length in range(min_length, max_length + 1):
            for i in range(len(words) - length + 1):
                phrase = tuple(words[i:i + length])
                # Filter out phrases with stopwords
                if not any(word in self.stopwords for word in phrase):
                    phrases.append(phrase)
        
        return phrases
    
    def _find_word_positions(self, word: str, text: str) -> List[int]:
        """Find positions of word in text"""
        positions = []
        start = 0
        
        while True:
            pos = text.lower().find(word.lower(), start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        return positions
    
    def _find_phrase_positions(self, phrase: Tuple[str, ...], text: str) -> List[int]:
        """Find positions of phrase in text"""
        phrase_str = " ".join(phrase)
        return self._find_word_positions(phrase_str, text)
    
    def _extract_context_snippets(self, keyword: str, text: str, context_length: int = 50) -> List[str]:
        """Extract context snippets around keyword"""
        snippets = []
        positions = self._find_word_positions(keyword, text)
        
        for pos in positions[:3]:  # Max 3 snippets
            start = max(0, pos - context_length)
            end = min(len(text), pos + len(keyword) + context_length)
            snippet = text[start:end].strip()
            if snippet:
                snippets.append(snippet)
        
        return snippets
    
    def _extract_from_text(self, text: str, keyword_type: KeywordType) -> List[ExtractedKeyword]:
        """Extract keywords from text with specified type"""
        keywords = []
        words = self._tokenize(self._clean_text(text))
        
        for word in words:
            if len(word) > 2 and word not in self.stopwords:
                keyword = ExtractedKeyword(
                    keyword=word,
                    keyword_type=keyword_type,
                    extraction_method=ExtractionMethod.METADATA_MINING,
                    frequency=1,
                    position_in_content=[0],
                    context_snippets=[text],
                    confidence_score=0.8
                )
                keywords.append(keyword)
        
        return keywords
    
    def _extract_emotional_keywords(self, transcript: str) -> List[ExtractedKeyword]:
        """Extract emotion-related keywords"""
        emotional_terms = [
            "excited", "happy", "sad", "angry", "frustrated", "joy", "fear",
            "surprise", "love", "hate", "calm", "anxious", "confident"
        ]
        
        keywords = []
        words = self._tokenize(self._clean_text(transcript))
        
        for word in words:
            if word in emotional_terms:
                keyword = ExtractedKeyword(
                    keyword=word,
                    keyword_type=KeywordType.EMOTION,
                    extraction_method=ExtractionMethod.CONTEXT_ANALYSIS,
                    frequency=transcript.lower().count(word),
                    position_in_content=self._find_word_positions(word, transcript),
                    context_snippets=self._extract_context_snippets(word, transcript),
                    confidence_score=0.7
                )
                keywords.append(keyword)
        
        return keywords
    
    def _extract_temporal_keywords(self, transcript: str) -> List[ExtractedKeyword]:
        """Extract time-related keywords"""
        temporal_terms = [
            "today", "yesterday", "tomorrow", "morning", "evening", "night",
            "week", "month", "year", "season", "summer", "winter", "spring", "fall"
        ]
        
        keywords = []
        words = self._tokenize(self._clean_text(transcript))
        
        for word in words:
            if word in temporal_terms:
                keyword = ExtractedKeyword(
                    keyword=word,
                    keyword_type=KeywordType.SEASONAL,
                    extraction_method=ExtractionMethod.CONTEXT_ANALYSIS,
                    frequency=transcript.lower().count(word),
                    position_in_content=self._find_word_positions(word, transcript),
                    context_snippets=self._extract_context_snippets(word, transcript),
                    confidence_score=0.6
                )
                keywords.append(keyword)
        
        return keywords
    
    def _extract_location_keywords(self, transcript: str) -> List[ExtractedKeyword]:
        """Extract location-related keywords"""
        # Simplified location detection
        # In real implementation would use NER (Named Entity Recognition)
        location_indicators = ["city", "country", "state", "street", "avenue", "road"]
        
        keywords = []
        words = self._tokenize(self._clean_text(transcript))
        
        for word in words:
            if word in location_indicators:
                keyword = ExtractedKeyword(
                    keyword=word,
                    keyword_type=KeywordType.LOCATION,
                    extraction_method=ExtractionMethod.CONTEXT_ANALYSIS,
                    frequency=transcript.lower().count(word),
                    position_in_content=self._find_word_positions(word, transcript),
                    context_snippets=self._extract_context_snippets(word, transcript),
                    confidence_score=0.5
                )
                keywords.append(keyword)
        
        return keywords
    
    async def analyze_competitor_keywords(
        self,
        competitor_content: List[Dict[str, Any]]
    ) -> Dict[str, CompetitorKeywordData]:
        """Analyze competitor keyword strategies"""
        
        competitor_analysis = {}
        
        for content in competitor_content:
            competitor_id = content.get("creator_id", "unknown")
            
            if competitor_id not in competitor_analysis:
                competitor_analysis[competitor_id] = CompetitorKeywordData(
                    competitor_id=competitor_id,
                    competitor_name=content.get("creator_name", "Unknown"),
                    keywords=[],
                    ranking_positions={},
                    content_volume=0,
                    engagement_metrics={},
                    gap_opportunities=[]
                )
            
            # Extract keywords from competitor content
            comp_analysis = await self.extract_keywords_from_voice_content(
                content_id=content.get("content_id", ""),
                transcript=content.get("transcript"),
                metadata=content.get("metadata")
            )
            
            competitor_data = competitor_analysis[competitor_id]
            competitor_data.content_volume += 1
            
            for keyword in comp_analysis.extracted_keywords:
                if keyword.keyword not in competitor_data.keywords:
                    competitor_data.keywords.append(keyword.keyword)
        
        return competitor_analysis
    
    async def get_keyword_trends(
        self,
        keywords: List[str],
        time_range_days: int = 30
    ) -> Dict[str, KeywordTrend]:
        """Get keyword trend analysis"""
        
        trends = {}
        
        for keyword in keywords:
            # Simulate trend data
            # In real implementation would use trend analysis APIs
            
            search_volume_history = []
            for i in range(time_range_days):
                date = datetime.now() - timedelta(days=i)
                volume = random.randint(100, 10000)
                search_volume_history.append((date, volume))
            
            trend = KeywordTrend(
                keyword=keyword,
                trend_direction=random.choice(list(TrendDirection)),
                search_volume_history=search_volume_history,
                competition_history=[],
                seasonal_patterns={},
                related_trending_terms=[],
                growth_rate=random.uniform(-20.0, 50.0),
                forecast_data={}
            )
            
            trends[keyword] = trend
        
        return trends


# Import random for simulations
import random

# Export classes for external use
__all__ = [
    'VoiceKeywordExtractor',
    'KeywordType',
    'ExtractionMethod',
    'SearchVolume',
    'CompetitionLevel',
    'TrendDirection',
    'KeywordMetrics',
    'ExtractedKeyword',
    'VoiceContentAnalysis',
    'CompetitorKeywordData',
    'KeywordTrend'
]