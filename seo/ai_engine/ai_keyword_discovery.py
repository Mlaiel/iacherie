"""
AI Keyword Discovery Engine for Ainflue Platform
===============================================

Advanced AI-powered keyword research and discovery system using machine learning,
natural language processing, and trend analysis for creator economy optimization.

Features:
- GPT-powered keyword expansion and clustering
- Semantic keyword relationship mapping
- Intent-based keyword categorization
- Trend prediction and seasonal analysis
- Long-tail keyword generation with ML
- Competitive keyword gap analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + ML Engineer + Backend Senior expertise applied
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import re
import openai
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import spacy
import requests
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class KeywordDifficulty(Enum):
    """Keyword competition difficulty levels."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"

class KeywordIntent(Enum):
    """Keyword search intent categories."""
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"
    LOCAL = "local"
    BRAND = "brand"

class KeywordTrend(Enum):
    """Keyword trend directions."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    EMERGING = "emerging"

@dataclass
class Keyword:
    """Individual keyword representation."""
    text: str
    search_volume: int
    competition: float
    difficulty: KeywordDifficulty
    intent: KeywordIntent
    trend: KeywordTrend
    cpc: float
    relevance_score: float
    semantic_cluster: int
    related_keywords: List[str]
    long_tail_variants: List[str]

@dataclass
class KeywordCluster:
    """Keyword clustering result."""
    cluster_id: int
    primary_keyword: str
    keywords: List[Keyword]
    cluster_intent: KeywordIntent
    cluster_volume: int
    semantic_similarity: float
    content_opportunities: List[str]

@dataclass
class ExpandedKeywords:
    """Result of keyword expansion process."""
    seed_keywords: List[str]
    expanded_keywords: List[Keyword]
    keyword_clusters: List[KeywordCluster]
    semantic_map: Dict[str, List[str]]
    expansion_metrics: Dict[str, Any]

@dataclass
class IntentKeywords:
    """Intent-based keyword groupings."""
    intent: KeywordIntent
    primary_keywords: List[Keyword]
    supporting_keywords: List[Keyword]
    content_gaps: List[str]
    optimization_opportunities: List[str]

@dataclass
class TrendingKeywords:
    """Trending keyword analysis."""
    industry: str
    timeframe: str
    trending_up: List[Keyword]
    trending_down: List[Keyword]
    seasonal_keywords: List[Keyword]
    emerging_keywords: List[Keyword]
    trend_predictions: Dict[str, float]

@dataclass
class LongTailKeywords:
    """Long-tail keyword generation result."""
    topic: str
    head_term: str
    long_tail_keywords: List[Keyword]
    question_keywords: List[Keyword]
    conversational_keywords: List[Keyword]
    local_variations: List[Keyword]
    content_suggestions: List[str]

class AIKeywordDiscovery:
    """Advanced AI-powered keyword discovery and research engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AI keyword discovery engine.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
# SECURITY: self.openai_api_key = self.config.get('openai_api_key') # MOVED TO ENV
# TODO: Move to environment variables or secure vault
        self.model_name = self.config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
        self.spacy_model = self.config.get('spacy_model', 'en_core_web_sm')
        
        # Initialize models
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.openai_client = None
        
        # Keyword analysis settings
        self.max_keywords_per_request = self.config.get('max_keywords', 100)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.cluster_min_size = self.config.get('cluster_min_size', 3)
        
        # Caching for performance
        self._keyword_cache: Dict[str, List[Keyword]] = {}
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._trend_cache: Dict[str, TrendingKeywords] = {}
        
        logger.info("AIKeywordDiscovery engine initialized")

    async def initialize_models(self) -> None:
        """Initialize AI models and services."""
        try:
            # Initialize OpenAI
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.openai_client = openai
            
            # Load transformer model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Load spaCy model
            self.nlp = spacy.load(self.spacy_model)
            
            logger.info("AI keyword discovery models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise

    async def ai_keyword_expansion(self, seed_keywords: List[str], 
                                 expansion_factor: int = 5) -> ExpandedKeywords:
        """Expand seed keywords using AI and semantic analysis.
        
        Args:
            seed_keywords: Initial keywords to expand
            expansion_factor: Number of related keywords per seed keyword
            
        Returns:
            ExpandedKeywords with expanded keyword set and analysis
        """
        if not self.model:
            await self.initialize_models()
            
        try:
            expanded_keywords = []
            semantic_map = {}
            
            for seed_keyword in seed_keywords:
                # Generate AI-powered expansions
                ai_keywords = await self._generate_ai_keywords(seed_keyword, expansion_factor)
                
                # Generate semantic expansions
                semantic_keywords = await self._generate_semantic_keywords(seed_keyword, expansion_factor)
                
                # Combine and deduplicate
                combined_keywords = self._merge_keyword_lists(ai_keywords, semantic_keywords)
                
                # Analyze each keyword
                analyzed_keywords = []
                for keyword_text in combined_keywords:
                    keyword = await self._analyze_keyword(keyword_text, seed_keyword)
                    analyzed_keywords.append(keyword)
                
                expanded_keywords.extend(analyzed_keywords)
                semantic_map[seed_keyword] = [kw.text for kw in analyzed_keywords]
            
            # Remove duplicates and sort by relevance
            unique_keywords = self._deduplicate_keywords(expanded_keywords)
            
            # Generate keyword clusters
            keyword_clusters = await self._generate_keyword_clusters(unique_keywords)
            
            # Calculate expansion metrics
            expansion_metrics = {
                'total_keywords': len(unique_keywords),
                'clusters_generated': len(keyword_clusters),
                'avg_relevance_score': np.mean([kw.relevance_score for kw in unique_keywords]),
                'high_volume_keywords': len([kw for kw in unique_keywords if kw.search_volume > 1000]),
                'low_competition_keywords': len([kw for kw in unique_keywords if kw.competition < 0.5])
            }
            
            return ExpandedKeywords(
                seed_keywords=seed_keywords,
                expanded_keywords=unique_keywords,
                keyword_clusters=keyword_clusters,
                semantic_map=semantic_map,
                expansion_metrics=expansion_metrics
            )
            
        except Exception as e:
            logger.error(f"Keyword expansion failed: {e}")
            raise

    async def intent_based_keyword_discovery(self, content_intent: str, 
                                           target_audience: Optional[str] = None) -> IntentKeywords:
        """Discover keywords based on content intent and audience.
        
        Args:
            content_intent: The intended purpose/goal of content
            target_audience: Optional target audience description
            
        Returns:
            IntentKeywords grouped by search intent
        """
        try:
            # Analyze content intent to determine keyword intent
            detected_intent = await self._analyze_content_intent(content_intent)
            
            # Generate intent-specific keywords
            primary_keywords = await self._generate_intent_keywords(content_intent, detected_intent, primary=True)
            supporting_keywords = await self._generate_intent_keywords(content_intent, detected_intent, primary=False)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(content_intent, primary_keywords)
            
            # Generate optimization opportunities
            optimization_opportunities = await self._generate_optimization_opportunities(
                detected_intent, primary_keywords, supporting_keywords
            )
            
            return IntentKeywords(
                intent=detected_intent,
                primary_keywords=primary_keywords,
                supporting_keywords=supporting_keywords,
                content_gaps=content_gaps,
                optimization_opportunities=optimization_opportunities
            )
            
        except Exception as e:
            logger.error(f"Intent-based keyword discovery failed: {e}")
            raise

    async def semantic_keyword_clustering(self, keywords: List[str], 
                                        cluster_method: str = 'kmeans') -> List[KeywordCluster]:
        """Cluster keywords based on semantic similarity.
        
        Args:
            keywords: List of keywords to cluster
            cluster_method: Clustering algorithm ('kmeans' or 'dbscan')
            
        Returns:
            List of KeywordCluster objects
        """
        try:
            if len(keywords) < self.cluster_min_size:
                logger.warning(f"Not enough keywords for clustering: {len(keywords)}")
                return []
            
            # Generate embeddings for all keywords
            embeddings = []
            keyword_objects = []
            
            for keyword_text in keywords:
                embedding = await self._generate_embeddings(keyword_text)
                embeddings.append(embedding)
                
                # Create keyword object with basic analysis
                keyword = await self._analyze_keyword(keyword_text)
                keyword_objects.append(keyword)
            
            embeddings_array = np.array(embeddings)
            
            # Perform clustering
            if cluster_method == 'kmeans':
                n_clusters = min(max(len(keywords) // 5, 2), 10)  # Dynamic cluster count
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            else:  # dbscan
                clusterer = DBSCAN(eps=0.3, min_samples=self.cluster_min_size)
            
            cluster_labels = clusterer.fit_predict(embeddings_array)
            
            # Group keywords by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                if label != -1:  # Ignore noise points in DBSCAN
                    clusters[label].append(keyword_objects[i])
            
            # Create KeywordCluster objects
            keyword_clusters = []
            for cluster_id, cluster_keywords in clusters.items():
                if len(cluster_keywords) >= self.cluster_min_size:
                    cluster = await self._create_keyword_cluster(cluster_id, cluster_keywords)
                    keyword_clusters.append(cluster)
            
            return keyword_clusters
            
        except Exception as e:
            logger.error(f"Semantic keyword clustering failed: {e}")
            return []

    async def trend_based_keyword_prediction(self, industry: str, 
                                           timeframe: str = "30d") -> TrendingKeywords:
        """Predict trending keywords for specific industry.
        
        Args:
            industry: Industry or niche to analyze
            timeframe: Analysis timeframe (7d, 30d, 90d, 1y)
            
        Returns:
            TrendingKeywords with trend analysis
        """
# SECURITY: cache_key = f"{industry}_{timeframe}" # MOVED TO ENV
# TODO: Move to environment variables or secure vault
        if cache_key in self._trend_cache:
            return self._trend_cache[cache_key]
            
        try:
            # Generate industry-related keywords
            industry_keywords = await self._generate_industry_keywords(industry)
            
            # Analyze trends for each keyword
            trending_up = []
            trending_down = []
            seasonal_keywords = []
            emerging_keywords = []
            
            for keyword in industry_keywords:
                trend_data = await self._analyze_keyword_trend(keyword, timeframe)
                
                if trend_data['trend'] == KeywordTrend.RISING:
                    trending_up.append(keyword)
                elif trend_data['trend'] == KeywordTrend.DECLINING:
                    trending_down.append(keyword)
                elif trend_data['trend'] == KeywordTrend.SEASONAL:
                    seasonal_keywords.append(keyword)
                elif trend_data['trend'] == KeywordTrend.EMERGING:
                    emerging_keywords.append(keyword)
            
            # Generate trend predictions
            trend_predictions = await self._generate_trend_predictions(industry, industry_keywords)
            
            result = TrendingKeywords(
                industry=industry,
                timeframe=timeframe,
                trending_up=trending_up,
                trending_down=trending_down,
                seasonal_keywords=seasonal_keywords,
                emerging_keywords=emerging_keywords,
                trend_predictions=trend_predictions
            )
            
            # Cache result
            self._trend_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Trend-based keyword prediction failed: {e}")
            raise

    async def long_tail_keyword_generation(self, topic: str, 
                                         target_difficulty: KeywordDifficulty = KeywordDifficulty.EASY) -> LongTailKeywords:
        """Generate long-tail keywords for a specific topic.
        
        Args:
            topic: Main topic for long-tail generation
            target_difficulty: Target keyword difficulty level
            
        Returns:
            LongTailKeywords with various long-tail variations
        """
        try:
            # Extract head term from topic
            head_term = await self._extract_head_term(topic)
            
            # Generate different types of long-tail keywords
            long_tail_keywords = await self._generate_long_tail_variations(topic, head_term)
            question_keywords = await self._generate_question_keywords(topic)
            conversational_keywords = await self._generate_conversational_keywords(topic)
            local_variations = await self._generate_local_variations(topic)
            
            # Filter by target difficulty
            filtered_long_tail = [kw for kw in long_tail_keywords if kw.difficulty == target_difficulty]
            filtered_questions = [kw for kw in question_keywords if kw.difficulty == target_difficulty]
            filtered_conversational = [kw for kw in conversational_keywords if kw.difficulty == target_difficulty]
            filtered_local = [kw for kw in local_variations if kw.difficulty == target_difficulty]
            
            # Generate content suggestions
            content_suggestions = await self._generate_content_suggestions_for_long_tail(
                topic, filtered_long_tail + filtered_questions
            )
            
            return LongTailKeywords(
                topic=topic,
                head_term=head_term,
                long_tail_keywords=filtered_long_tail,
                question_keywords=filtered_questions,
                conversational_keywords=filtered_conversational,
                local_variations=filtered_local,
                content_suggestions=content_suggestions
            )
            
        except Exception as e:
            logger.error(f"Long-tail keyword generation failed: {e}")
            raise

    # Private helper methods

    async def _generate_ai_keywords(self, seed_keyword: str, count: int) -> List[str]:
        """Generate keyword variations using GPT."""
        try:
            if not self.openai_client:
                return []
                
            prompt = f"""Generate {count} related SEO keywords for "{seed_keyword}". 
            Focus on:
            - Semantic variations
            - Long-tail keywords
            - User intent variations
            - Commercial and informational keywords
            
            Return only the keywords, one per line, without numbers or bullets."""
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            keywords = []
            content = response.choices[0].message.content.strip()
            for line in content.split('\n'):
                keyword = line.strip().strip('-•').strip()
                if keyword and len(keyword.split()) <= 5:  # Reasonable keyword length
                    keywords.append(keyword)
            
            return keywords[:count]
            
        except Exception as e:
            logger.warning(f"AI keyword generation failed: {e}")
            return []

    async def _generate_semantic_keywords(self, seed_keyword: str, count: int) -> List[str]:
        """Generate semantically related keywords."""
        try:
            if not self.nlp:
                await self.initialize_models()
                
            doc = self.nlp(seed_keyword)
            keywords = set()
            
            # Use word similarity and context
            for token in doc:
                if token.has_vector and not token.is_stop:
                    # Find similar words (this is a simplified approach)
                    similar_words = []  # Would need word2vec or similar model
                    keywords.update(similar_words[:2])
            
            # Generate variations with common modifiers
            modifiers = [
                'best', 'top', 'how to', 'guide', 'tips', 'review', 'compare',
                'cheap', 'affordable', 'professional', 'expert', 'advanced'
            ]
            
            for modifier in modifiers:
                keywords.add(f"{modifier} {seed_keyword}")
                keywords.add(f"{seed_keyword} {modifier}")
            
            return list(keywords)[:count]
            
        except Exception as e:
            logger.warning(f"Semantic keyword generation failed: {e}")
            return []

    def _merge_keyword_lists(self, list1: List[str], list2: List[str]) -> List[str]:
        """Merge and deduplicate keyword lists."""
        combined = set(list1 + list2)
        return list(combined)

    async def _analyze_keyword(self, keyword_text: str, seed_keyword: str = "") -> Keyword:
        """Analyze individual keyword for SEO metrics."""
        try:
            # Simulate keyword analysis (in production, use real SEO APIs)
            search_volume = self._estimate_search_volume(keyword_text)
            competition = self._estimate_competition(keyword_text)
            difficulty = self._determine_difficulty(competition, search_volume)
            intent = self._determine_intent(keyword_text)
            trend = KeywordTrend.STABLE  # Default
            cpc = self._estimate_cpc(keyword_text, competition)
            
            # Calculate relevance score
            relevance_score = await self._calculate_relevance_score(keyword_text, seed_keyword)
            
            # Generate related keywords
            related_keywords = await self._find_related_keywords(keyword_text)
            
            # Generate long-tail variants
            long_tail_variants = await self._generate_simple_long_tail(keyword_text)
            
            return Keyword(
                text=keyword_text,
                search_volume=search_volume,
                competition=competition,
                difficulty=difficulty,
                intent=intent,
                trend=trend,
                cpc=cpc,
                relevance_score=relevance_score,
                semantic_cluster=0,  # Will be set during clustering
                related_keywords=related_keywords,
                long_tail_variants=long_tail_variants
            )
            
        except Exception as e:
            logger.error(f"Keyword analysis failed for '{keyword_text}': {e}")
            return Keyword(
                text=keyword_text, search_volume=0, competition=0.5,
                difficulty=KeywordDifficulty.MEDIUM, intent=KeywordIntent.INFORMATIONAL,
                trend=KeywordTrend.STABLE, cpc=0.0, relevance_score=0.5,
                semantic_cluster=0, related_keywords=[], long_tail_variants=[]
            )

    def _deduplicate_keywords(self, keywords: List[Keyword]) -> List[Keyword]:
        """Remove duplicate keywords and sort by relevance."""
        seen = set()
        unique_keywords = []
        
        for keyword in keywords:
            if keyword.text.lower() not in seen:
                seen.add(keyword.text.lower())
                unique_keywords.append(keyword)
        
        # Sort by relevance score
        return sorted(unique_keywords, key=lambda k: k.relevance_score, reverse=True)

    async def _generate_keyword_clusters(self, keywords: List[Keyword]) -> List[KeywordCluster]:
        """Generate keyword clusters from analyzed keywords."""
        try:
            if len(keywords) < self.cluster_min_size:
                return []
                
            # Extract keyword texts for clustering
            keyword_texts = [kw.text for kw in keywords]
            
            # Perform semantic clustering
            clusters = await self.semantic_keyword_clustering(keyword_texts)
            
            # Update keyword objects with cluster IDs
            for cluster in clusters:
                for keyword in keywords:
                    if keyword.text in [ck.text for ck in cluster.keywords]:
                        keyword.semantic_cluster = cluster.cluster_id
            
            return clusters
            
        except Exception as e:
            logger.error(f"Keyword cluster generation failed: {e}")
            return []

    async def _create_keyword_cluster(self, cluster_id: int, keywords: List[Keyword]) -> KeywordCluster:
        """Create a KeywordCluster object from grouped keywords."""
        try:
            # Find primary keyword (highest volume or relevance)
            primary_keyword = max(keywords, key=lambda k: k.search_volume * k.relevance_score)
            
            # Determine cluster intent (most common intent)
            intent_counts = Counter([kw.intent for kw in keywords])
            cluster_intent = intent_counts.most_common(1)[0][0]
            
            # Calculate cluster metrics
            cluster_volume = sum([kw.search_volume for kw in keywords])
            semantic_similarity = np.mean([kw.relevance_score for kw in keywords])
            
            # Generate content opportunities
            content_opportunities = await self._generate_cluster_content_opportunities(keywords)
            
            return KeywordCluster(
                cluster_id=cluster_id,
                primary_keyword=primary_keyword.text,
                keywords=keywords,
                cluster_intent=cluster_intent,
                cluster_volume=cluster_volume,
                semantic_similarity=semantic_similarity,
                content_opportunities=content_opportunities
            )
            
        except Exception as e:
            logger.error(f"Keyword cluster creation failed: {e}")
            raise

    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for text."""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
            
        try:
            if not self.model or not self.tokenizer:
                await self.initialize_models()
                
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, 
                                  padding=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            
            self._embedding_cache[text] = embeddings
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return np.zeros(384)

    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword (simplified)."""
        # This is a simplified estimation - in production use real SEO APIs
        word_count = len(keyword.split())
        base_volume = max(1000 - (word_count - 1) * 200, 10)
        
        # Common high-volume patterns
        if any(term in keyword.lower() for term in ['how to', 'what is', 'best']):
            base_volume *= 2
        
        return max(base_volume, 10)

    def _estimate_competition(self, keyword: str) -> float:
        """Estimate keyword competition (simplified)."""
        word_count = len(keyword.split())
        
        # Longer keywords typically have lower competition
        if word_count >= 4:
            return np.random.uniform(0.1, 0.4)
        elif word_count == 3:
            return np.random.uniform(0.3, 0.6)
        else:
            return np.random.uniform(0.5, 0.9)

    def _determine_difficulty(self, competition: float, search_volume: int) -> KeywordDifficulty:
        """Determine keyword difficulty based on competition and volume."""
        difficulty_score = competition * 0.7 + min(search_volume / 10000, 1.0) * 0.3
        
        if difficulty_score < 0.2:
            return KeywordDifficulty.VERY_EASY
        elif difficulty_score < 0.4:
            return KeywordDifficulty.EASY
        elif difficulty_score < 0.6:
            return KeywordDifficulty.MEDIUM
        elif difficulty_score < 0.8:
            return KeywordDifficulty.HARD
        else:
            return KeywordDifficulty.VERY_HARD

    def _determine_intent(self, keyword: str) -> KeywordIntent:
        """Determine search intent for keyword."""
        keyword_lower = keyword.lower()
        
        # Transactional intent indicators
        if any(term in keyword_lower for term in ['buy', 'purchase', 'order', 'download', 'get']):
            return KeywordIntent.TRANSACTIONAL
        
        # Commercial intent indicators
        if any(term in keyword_lower for term in ['best', 'top', 'review', 'compare', 'vs', 'price']):
            return KeywordIntent.COMMERCIAL
        
        # Local intent indicators
        if any(term in keyword_lower for term in ['near', 'local', 'nearby', 'location']):
            return KeywordIntent.LOCAL
        
        # Navigational intent indicators
        if any(term in keyword_lower for term in ['login', 'website', 'official', 'homepage']):
            return KeywordIntent.NAVIGATIONAL
        
        # Default to informational
        return KeywordIntent.INFORMATIONAL

    def _estimate_cpc(self, keyword: str, competition: float) -> float:
        """Estimate cost-per-click for keyword."""
        base_cpc = competition * 2.5
        
        # Commercial keywords typically have higher CPC
        if self._determine_intent(keyword) in [KeywordIntent.COMMERCIAL, KeywordIntent.TRANSACTIONAL]:
            base_cpc *= 1.5
        
        return round(base_cpc, 2)

    async def _calculate_relevance_score(self, keyword: str, seed_keyword: str) -> float:
        """Calculate relevance score between keyword and seed keyword."""
        if not seed_keyword:
            return 0.7  # Default relevance
            
        try:
            keyword_embedding = await self._generate_embeddings(keyword)
            seed_embedding = await self._generate_embeddings(seed_keyword)
            
            similarity = cosine_similarity(
                keyword_embedding.reshape(1, -1),
                seed_embedding.reshape(1, -1)
            )[0][0]
            
            return max(0.0, min(similarity, 1.0))
            
        except Exception:
            return 0.5

    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords for a given keyword."""
        try:
            # Simple related keyword generation
            words = keyword.split()
            related = []
            
            # Add variations with common modifiers
            modifiers = ['best', 'top', 'how to', 'guide', 'tips']
            for modifier in modifiers[:3]:
                related.append(f"{modifier} {keyword}")
            
            return related
            
        except Exception:
            return []

    async def _generate_simple_long_tail(self, keyword: str) -> List[str]:
        """Generate simple long-tail variations."""
        try:
            variations = []
            suffixes = ['guide', 'tips', 'tutorial', 'review', 'comparison']
            
            for suffix in suffixes[:3]:
                variations.append(f"{keyword} {suffix}")
            
            return variations
            
        except Exception:
            return []

    async def _analyze_content_intent(self, content_intent: str) -> KeywordIntent:
        """Analyze content intent to determine keyword intent."""
        intent_lower = content_intent.lower()
        
        if any(term in intent_lower for term in ['sell', 'promote', 'convert', 'purchase']):
            return KeywordIntent.TRANSACTIONAL
        elif any(term in intent_lower for term in ['review', 'compare', 'evaluate']):
            return KeywordIntent.COMMERCIAL
        elif any(term in intent_lower for term in ['educate', 'inform', 'explain', 'teach']):
            return KeywordIntent.INFORMATIONAL
        else:
            return KeywordIntent.INFORMATIONAL

    async def _generate_intent_keywords(self, content_intent: str, intent: KeywordIntent, 
                                      primary: bool = True) -> List[Keyword]:
        """Generate keywords based on content intent."""
        try:
            # Extract main topics from content intent
            if not self.nlp:
                await self.initialize_models()
                
            doc = self.nlp(content_intent)
            topics = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop]
            
            keywords = []
            
            for topic in topics[:5]:  # Limit topics
                # Generate intent-specific keyword variations
                if intent == KeywordIntent.INFORMATIONAL:
                    patterns = [f"what is {topic}", f"how to {topic}", f"{topic} guide", f"{topic} explained"]
                elif intent == KeywordIntent.COMMERCIAL:
                    patterns = [f"best {topic}", f"{topic} review", f"top {topic}", f"{topic} comparison"]
                elif intent == KeywordIntent.TRANSACTIONAL:
                    patterns = [f"buy {topic}", f"{topic} for sale", f"purchase {topic}", f"get {topic}"]
                else:
                    patterns = [topic]
                
                for pattern in patterns:
                    keyword = await self._analyze_keyword(pattern)
                    keywords.append(keyword)
            
            # Sort by relevance and return appropriate count
            keywords.sort(key=lambda k: k.relevance_score, reverse=True)
            return keywords[:10 if primary else 20]
            
        except Exception as e:
            logger.error(f"Intent keyword generation failed: {e}")
            return []

    async def _identify_content_gaps(self, content_intent: str, keywords: List[Keyword]) -> List[str]:
        """Identify content gaps based on intent and keywords."""
        gaps = []
        
        keyword_texts = [kw.text.lower() for kw in keywords]
        
        # Common content gap patterns
        if not any('how to' in text for text in keyword_texts):
            gaps.append("How-to content opportunities")
        
        if not any('best' in text for text in keyword_texts):
            gaps.append("Comparison and review content")
        
        if not any('guide' in text for text in keyword_texts):
            gaps.append("Comprehensive guide content")
        
        return gaps

    async def _generate_optimization_opportunities(self, intent: KeywordIntent, 
                                                 primary: List[Keyword], 
                                                 supporting: List[Keyword]) -> List[str]:
        """Generate optimization opportunities based on keyword analysis."""
        opportunities = []
        
        # Analyze keyword distribution
        total_volume = sum([kw.search_volume for kw in primary + supporting])
        low_competition_count = len([kw for kw in primary + supporting if kw.competition < 0.4])
        
        if low_competition_count > 5:
            opportunities.append("Target low-competition keywords for quick wins")
        
        if total_volume > 50000:
            opportunities.append("High search volume potential - prioritize content creation")
        
        if intent == KeywordIntent.COMMERCIAL:
            opportunities.append("Focus on comparison and review content")
        
        return opportunities

    async def _generate_industry_keywords(self, industry: str) -> List[Keyword]:
        """Generate industry-specific keywords."""
        try:
            # Generate base keywords for industry
            industry_terms = [industry, f"{industry} industry", f"{industry} business", f"{industry} market"]
            
            keywords = []
            for term in industry_terms:
                keyword = await self._analyze_keyword(term)
                keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Industry keyword generation failed: {e}")
            return []

    async def _analyze_keyword_trend(self, keyword: Keyword, timeframe: str) -> Dict[str, Any]:
        """Analyze trend for a specific keyword."""
        # Simplified trend analysis - in production use real trend APIs
        trend_score = np.random.uniform(-0.5, 0.5)
        
        if trend_score > 0.2:
            trend = KeywordTrend.RISING
        elif trend_score < -0.2:
            trend = KeywordTrend.DECLINING
        else:
            trend = KeywordTrend.STABLE
        
        return {
            'trend': trend,
            'score': trend_score,
            'timeframe': timeframe
        }

    async def _generate_trend_predictions(self, industry: str, keywords: List[Keyword]) -> Dict[str, float]:
        """Generate trend predictions for keywords."""
        predictions = {}
        
        for keyword in keywords[:10]:  # Limit predictions
            # Simplified prediction algorithm
            prediction_score = np.random.uniform(0.1, 0.9)
            predictions[keyword.text] = prediction_score
        
        return predictions

    async def _extract_head_term(self, topic: str) -> str:
        """Extract the main head term from a topic."""
        words = topic.split()
        return words[0] if words else topic

    async def _generate_long_tail_variations(self, topic: str, head_term: str) -> List[Keyword]:
        """Generate long-tail keyword variations."""
        try:
            variations = []
            
            # Common long-tail patterns
            patterns = [
                f"best {topic} for beginners",
                f"how to choose {topic}",
                f"{topic} guide 2025",
                f"affordable {topic} options",
                f"{topic} reviews and ratings",
                f"professional {topic} services",
                f"{topic} tips and tricks",
                f"where to buy {topic}",
                f"{topic} vs alternatives",
                f"DIY {topic} solutions"
            ]
            
            for pattern in patterns:
                keyword = await self._analyze_keyword(pattern)
                if keyword.difficulty in [KeywordDifficulty.VERY_EASY, KeywordDifficulty.EASY]:
                    variations.append(keyword)
            
            return variations
            
        except Exception as e:
            logger.error(f"Long-tail variation generation failed: {e}")
            return []

    async def _generate_question_keywords(self, topic: str) -> List[Keyword]:
        """Generate question-based keywords."""
        try:
            question_patterns = [
                f"what is {topic}",
                f"how does {topic} work",
                f"why use {topic}",
                f"when to use {topic}",
                f"where to find {topic}",
                f"how much does {topic} cost",
                f"is {topic} worth it",
                f"how to improve {topic}",
                f"what are the benefits of {topic}",
                f"how to get started with {topic}"
            ]
            
            keywords = []
            for pattern in question_patterns:
                keyword = await self._analyze_keyword(pattern)
                keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Question keyword generation failed: {e}")
            return []

    async def _generate_conversational_keywords(self, topic: str) -> List[Keyword]:
        """Generate conversational/voice search keywords."""
        try:
            conversational_patterns = [
                f"tell me about {topic}",
                f"I need help with {topic}",
                f"looking for {topic}",
                f"find me {topic}",
                f"show me {topic} options",
                f"explain {topic} to me",
                f"help me choose {topic}",
                f"I want to learn {topic}",
                f"searching for {topic}",
                f"recommend {topic}"
            ]
            
            keywords = []
            for pattern in conversational_patterns:
                keyword = await self._analyze_keyword(pattern)
                keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Conversational keyword generation failed: {e}")
            return []

    async def _generate_local_variations(self, topic: str) -> List[Keyword]:
        """Generate local/geographic keyword variations."""
        try:
            locations = ["near me", "local", "in my area", "nearby", "city"]
            
            keywords = []
            for location in locations:
                pattern = f"{topic} {location}"
                keyword = await self._analyze_keyword(pattern)
                keyword.intent = KeywordIntent.LOCAL
                keywords.append(keyword)
            
            return keywords
            
        except Exception as e:
            logger.error(f"Local variation generation failed: {e}")
            return []

    async def _generate_content_suggestions_for_long_tail(self, topic: str, 
                                                        keywords: List[Keyword]) -> List[str]:
        """Generate content suggestions based on long-tail keywords."""
        suggestions = []
        
        # Analyze keyword patterns to suggest content types
        question_count = len([kw for kw in keywords if kw.text.startswith(('what', 'how', 'why', 'when', 'where'))])
        commercial_count = len([kw for kw in keywords if kw.intent == KeywordIntent.COMMERCIAL])
        
        if question_count > 3:
            suggestions.append(f"Create a comprehensive FAQ page about {topic}")
        
        if commercial_count > 2:
            suggestions.append(f"Develop comparison guides and reviews for {topic}")
        
        suggestions.append(f"Write beginner's guide to {topic}")
        suggestions.append(f"Create step-by-step tutorials for {topic}")
        
        return suggestions

    async def _generate_cluster_content_opportunities(self, keywords: List[Keyword]) -> List[str]:
        """Generate content opportunities for a keyword cluster."""
        opportunities = []
        
        # Analyze cluster characteristics
        intent_distribution = Counter([kw.intent for kw in keywords])
        dominant_intent = intent_distribution.most_common(1)[0][0]
        
        if dominant_intent == KeywordIntent.INFORMATIONAL:
            opportunities.append("Educational content and tutorials")
        elif dominant_intent == KeywordIntent.COMMERCIAL:
            opportunities.append("Product comparisons and reviews")
        elif dominant_intent == KeywordIntent.TRANSACTIONAL:
            opportunities.append("Product pages and conversion content")
        
        # Add volume-based opportunities
        high_volume_keywords = [kw for kw in keywords if kw.search_volume > 1000]
        if high_volume_keywords:
            opportunities.append("High-traffic content targeting primary terms")
        
        return opportunities