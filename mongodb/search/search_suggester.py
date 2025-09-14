"""Enterprise Search Suggestion and Query Enhancement System
=========================================================

Advanced search suggestion engine with machine learning-driven query expansion,
intelligent autocomplete, and contextual search optimization for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTATION:
- Lead Dev IA: AI-driven search optimization and personalization
- Backend Senior: High-performance suggestion algorithms and caching
- ML Engineer: Machine learning models for query understanding
- DBA: Optimized search index management and analytics
- Security: Safe query processing and injection prevention
"""

import asyncio
import logging
import re
import json
import time
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import hashlib

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    # Mock classes for compatibility
    class TfidfVectorizer:
    """TfidfVectorizer: class implementation"""
        def fit_transform(self, docs) -> None: return [[]]
        def transform(self, docs) -> None: return [[]]
    class cosine_similarity:
    """cosine_similarity: class implementation"""
        def __call__(self, a, b) -> None: return [[0.0]]

logger = logging.getLogger(__name__)

@dataclass
class QuerySuggestion:
    """Search query suggestion with metadata."""
    suggestion: str
    confidence: float
    suggestion_type: str  # 'autocomplete', 'synonym', 'trending', 'personalized'
    frequency: int = 0
    last_used: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchContext:
    """Search context for personalized suggestions."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    search_history: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    current_filters: Dict[str, Any] = field(default_factory=dict)
    content_type: Optional[str] = None

@dataclass
class QueryAnalytics:
    """Query analytics and performance metrics."""
    query: str
    timestamp: datetime
    user_id: Optional[str]
    result_count: int
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    session_duration: float = 0.0
    filters_used: List[str] = field(default_factory=list)

class SearchSuggester:
    """Enterprise search suggestion engine with AI-powered query enhancement."""
    
    def __init__(self, database_connection=None, cache_backend=None) -> None:
        """Initialize search suggester.
        
        Args:
            database_connection: MongoDB connection for analytics storage
            cache_backend: Redis cache for high-performance suggestions
        """
        self.db = database_connection
        self.cache = cache_backend
        self.logger = logger
        
        # Core suggestion data
        self._synonym_map: Dict[str, List[str]] = {}
        self._trending_queries: List[Tuple[str, float]] = []
        self._query_frequency: Counter = Counter()
        self._query_analytics: List[QueryAnalytics] = []
        
        # ML-powered suggestion models
        self._tfidf_vectorizer = TfidfVectorizer(max_features=10000, stop_words='english') if ML_AVAILABLE else None
        self._query_embeddings: Dict[str, Any] = {}
        self._user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Performance optimization
        self._suggestion_cache: Dict[str, List[QuerySuggestion]] = {}
        self._cache_ttl = 3600  # 1 hour
        self._max_suggestions = 10
        
        # Security and validation
        self._blocked_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'document\.',
            r'window\.'
        ]
        
        # Initialize with default synonyms and trending data
        self._initialize_default_data()
    
    def initialize_with_corpus(self, search_corpus: List[str]) -> bool:
        """Initialize suggestion engine with search corpus for ML training.
        
        Args:
            search_corpus: List of search queries and content for training
            
        Returns:
            bool: Success status
        """
        try:
            if not ML_AVAILABLE:
                self.logger.warning("ML libraries not available, using basic suggestions only")
                return True
            
            # Train TF-IDF model on corpus
            if search_corpus and self._tfidf_vectorizer:
                self.logger.info(f"Training suggestion model on {len(search_corpus)} documents")
                self._tfidf_vectorizer.fit(search_corpus)
                
                # Build query embeddings for similarity search
                self._build_query_embeddings(search_corpus[:1000])  # Limit for performance
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing with corpus: {e}")
            return False
    
    async def get_suggestions(self, partial_query: str, context: SearchContext = None, max_suggestions: int = None) -> List[QuerySuggestion]:
        """Get intelligent search suggestions for partial query.
        
        Args:
            partial_query: Partial search query
            context: Search context for personalization
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            list: List of query suggestions
        """
        try:
            # Validate and sanitize input
            if not self._is_safe_query(partial_query):
                self.logger.warning(f"Unsafe query detected: {partial_query}")
                return []
            
            partial_query = partial_query.strip().lower()
            if len(partial_query) < 2:
                return []
            
            max_suggestions = max_suggestions or self._max_suggestions
            
            # Check cache first
            cache_key = self._generate_cache_key(partial_query, context)
            cached_suggestions = await self._get_cached_suggestions(cache_key)
            if cached_suggestions:
                return cached_suggestions[:max_suggestions]
            
            # Generate suggestions from multiple sources
            suggestions = []
            
            # 1. Autocomplete suggestions
            autocomplete_suggestions = await self._get_autocomplete_suggestions(partial_query)
            suggestions.extend(autocomplete_suggestions)
            
            # 2. Synonym-based suggestions
            synonym_suggestions = await self._get_synonym_suggestions(partial_query)
            suggestions.extend(synonym_suggestions)
            
            # 3. Trending query suggestions
            trending_suggestions = await self._get_trending_suggestions(partial_query)
            suggestions.extend(trending_suggestions)
            
            # 4. Personalized suggestions (if context provided)
            if context and context.user_id:
                personalized_suggestions = await self._get_personalized_suggestions(partial_query, context)
                suggestions.extend(personalized_suggestions)
            
            # 5. ML-powered similar query suggestions
            if ML_AVAILABLE:
                ml_suggestions = await self._get_ml_suggestions(partial_query, context)
                suggestions.extend(ml_suggestions)
            
            # Deduplicate and rank suggestions
            final_suggestions = self._rank_and_deduplicate_suggestions(suggestions, partial_query)
            
            # Cache results
            await self._cache_suggestions(cache_key, final_suggestions)
            
            return final_suggestions[:max_suggestions]
            
        except Exception as e:
            self.logger.error(f"Error getting suggestions for '{partial_query}': {e}")
            return []
    
    async def record_query_analytics(self, analytics: QueryAnalytics) -> bool:
        """Record query analytics for improving suggestions.
        
        Args:
            analytics: Query analytics data
            
        Returns:
            bool: Success status
        """
        try:
            # Store analytics
            self._query_analytics.append(analytics)
            
            # Update query frequency
            self._query_frequency[analytics.query.lower()] += 1
            
            # Update trending queries
            await self._update_trending_queries()
            
            # Store in database
            if self.db:
                await self._store_query_analytics(analytics)
            
            # Update user profile if user_id provided
            if analytics.user_id:
                await self._update_user_profile(analytics.user_id, analytics)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording query analytics: {e}")
            return False
    
    async def add_synonym_mapping(self, term: str, synonyms: List[str]) -> bool:
        """Add synonym mappings for query expansion.
        
        Args:
            term: Primary term
            synonyms: List of synonymous terms
            
        Returns:
            bool: Success status
        """
        try:
            self._synonym_map[term.lower()] = [s.lower() for s in synonyms]
            
            # Store in database
            if self.db:
                await self._store_synonym_mapping(term, synonyms)
            
            # Clear related cache
            await self._clear_suggestion_cache(term)
            
            self.logger.info(f"Added synonym mapping: {term} -> {synonyms}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding synonym mapping: {e}")
            return False
    
    async def get_query_expansion(self, query: str, context: SearchContext = None) -> Dict[str, Any]:
        """Get query expansion with related terms and filters.
        
        Args:
            query: Original search query
            context: Search context
            
        Returns:
            dict: Query expansion results
        """
        try:
            if not self._is_safe_query(query):
                return {"error": "Invalid query"}
            
            query = query.strip().lower()
            
            expansion_result = {
                "original_query": query,
                "expanded_terms": [],
                "synonym_expansions": [],
                "filter_suggestions": [],
                "related_queries": [],
                "boost_terms": []
            }
            
            # Extract and expand terms
            query_terms = self._extract_query_terms(query)
            
            # Add synonym expansions
            for term in query_terms:
                if term in self._synonym_map:
                    expansion_result["synonym_expansions"].extend(self._synonym_map[term])
            
            # Add contextual filter suggestions
            if context:
                filter_suggestions = await self._get_filter_suggestions(query, context)
                expansion_result["filter_suggestions"] = filter_suggestions
            
            # Add related queries based on analytics
            related_queries = await self._get_related_queries(query)
            expansion_result["related_queries"] = related_queries
            
            # ML-powered term expansion
            if ML_AVAILABLE:
                ml_expansions = await self._get_ml_term_expansions(query)
                expansion_result["expanded_terms"].extend(ml_expansions)
            
            # Identify boost terms (important terms that should be weighted higher)
            boost_terms = await self._identify_boost_terms(query, context)
            expansion_result["boost_terms"] = boost_terms
            
            return expansion_result
            
        except Exception as e:
            self.logger.error(f"Error expanding query '{query}': {e}")
            return {"error": str(e)}
    
    async def get_search_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get search analytics and performance metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            dict: Search analytics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Filter recent analytics
            recent_analytics = [
                a for a in self._query_analytics
                if a.timestamp >= cutoff_time
            ]
            
            if not recent_analytics:
                return {"error": "No analytics data available"}
            
            # Calculate metrics
            total_queries = len(recent_analytics)
            unique_queries = len(set(a.query for a in recent_analytics))
            avg_ctr = sum(a.click_through_rate for a in recent_analytics) / total_queries
            avg_conversion = sum(a.conversion_rate for a in recent_analytics) / total_queries
            
            # Most popular queries
            query_counts = Counter(a.query for a in recent_analytics)
            popular_queries = query_counts.most_common(10)
            
            # Performance by query length
            query_lengths = [len(a.query.split()) for a in recent_analytics]
            avg_query_length = sum(query_lengths) / len(query_lengths)
            
            # Filter usage analysis
            filter_usage = Counter()
            for analytics in recent_analytics:
                filter_usage.update(analytics.filters_used)
            
            return {
                "analysis_period_days": days,
                "total_queries": total_queries,
                "unique_queries": unique_queries,
                "average_click_through_rate": avg_ctr,
                "average_conversion_rate": avg_conversion,
                "average_query_length": avg_query_length,
                "popular_queries": popular_queries,
                "popular_filters": filter_usage.most_common(5),
                "trending_queries": self._trending_queries[:10],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting search analytics: {e}")
            return {"error": str(e)}
    
    async def _get_autocomplete_suggestions(self, partial_query: str) -> List[QuerySuggestion]:
        """Get autocomplete suggestions based on query frequency."""
        suggestions = []
        
        # Find queries that start with the partial query
        for query, frequency in self._query_frequency.most_common(100):
            if query.startswith(partial_query) and query != partial_query:
                confidence = min(frequency / 100.0, 1.0)  # Normalize confidence
                suggestions.append(QuerySuggestion(
                    suggestion=query,
                    confidence=confidence,
                    suggestion_type="autocomplete",
                    frequency=frequency
                ))
        
        return suggestions[:5]  # Limit autocomplete suggestions
    
    async def _get_synonym_suggestions(self, partial_query: str) -> List[QuerySuggestion]:
        """Get synonym-based suggestions."""
        suggestions = []
        
        query_terms = self._extract_query_terms(partial_query)
        
        for term in query_terms:
            if term in self._synonym_map:
                for synonym in self._synonym_map[term]:
                    suggested_query = partial_query.replace(term, synonym)
                    suggestions.append(QuerySuggestion(
                        suggestion=suggested_query,
                        confidence=0.7,
                        suggestion_type="synonym",
                        metadata={"original_term": term, "synonym": synonym}
                    ))
        
        return suggestions
    
    async def _get_trending_suggestions(self, partial_query: str) -> List[QuerySuggestion]:
        """Get trending query suggestions."""
        suggestions = []
        
        for trending_query, score in self._trending_queries:
            # Check if trending query is relevant to partial query
            if self._calculate_query_similarity(partial_query, trending_query) > 0.5:
                suggestions.append(QuerySuggestion(
                    suggestion=trending_query,
                    confidence=score,
                    suggestion_type="trending",
                    metadata={"trend_score": score}
                ))
        
        return suggestions[:3]  # Limit trending suggestions
    
    async def _get_personalized_suggestions(self, partial_query: str, context: SearchContext) -> List[QuerySuggestion]:
        """Get personalized suggestions based on user context."""
        suggestions = []
        
        if not context.user_id or context.user_id not in self._user_profiles:
            return suggestions
        
        user_profile = self._user_profiles[context.user_id]
        
        # Get suggestions based on user's search history
        for past_query in context.search_history[-10:]:  # Last 10 searches
            if self._calculate_query_similarity(partial_query, past_query) > 0.6:
                suggestions.append(QuerySuggestion(
                    suggestion=past_query,
                    confidence=0.8,
                    suggestion_type="personalized",
                    metadata={"source": "search_history"}
                ))
        
        # Get suggestions based on user preferences
        if "preferred_categories" in user_profile:
            for category in user_profile["preferred_categories"]:
                if category.lower() in partial_query or len(partial_query) < 3:
                    category_query = f"{partial_query} {category}".strip()
                    suggestions.append(QuerySuggestion(
                        suggestion=category_query,
                        confidence=0.6,
                        suggestion_type="personalized",
                        metadata={"source": "preferences", "category": category}
                    ))
        
        return suggestions[:3]  # Limit personalized suggestions
    
    async def _get_ml_suggestions(self, partial_query: str, context: SearchContext = None) -> List[QuerySuggestion]:
        """Get ML-powered suggestions using semantic similarity."""
        if not ML_AVAILABLE or not self._query_embeddings:
            return []
        
        suggestions = []
        
        try:
            # Transform partial query to vector space
            query_vector = self._tfidf_vectorizer.transform([partial_query])
            
            # Find similar queries
            similarities = []
            for stored_query, embedding in list(self._query_embeddings.items())[:100]:  # Limit for performance
                if stored_query != partial_query:
                    similarity = cosine_similarity(query_vector, [embedding])[0][0]
                    if similarity > 0.3:  # Minimum similarity threshold
                        similarities.append((stored_query, similarity))
            
            # Sort by similarity and create suggestions
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            for query, similarity in similarities[:5]:
                suggestions.append(QuerySuggestion(
                    suggestion=query,
                    confidence=similarity,
                    suggestion_type="semantic",
                    metadata={"similarity_score": similarity}
                ))
            
        except Exception as e:
            self.logger.error(f"Error getting ML suggestions: {e}")
        
        return suggestions
    
    def _rank_and_deduplicate_suggestions(self, suggestions: List[QuerySuggestion], partial_query: str) -> List[QuerySuggestion]:
        """Rank and deduplicate suggestions."""
        # Remove duplicates while preserving the highest confidence
        seen_suggestions = {}
        for suggestion in suggestions:
            key = suggestion.suggestion.lower()
            if key not in seen_suggestions or suggestion.confidence > seen_suggestions[key].confidence:
                seen_suggestions[key] = suggestion
        
        # Convert back to list and sort by confidence and relevance
        unique_suggestions = list(seen_suggestions.values())
        
        # Calculate relevance scores
        for suggestion in unique_suggestions:
            relevance_score = self._calculate_suggestion_relevance(suggestion, partial_query)
            suggestion.confidence = (suggestion.confidence + relevance_score) / 2
        
        # Sort by confidence (which now includes relevance)
        unique_suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return unique_suggestions
    
    def _calculate_suggestion_relevance(self, suggestion: QuerySuggestion, partial_query: str) -> float:
        """Calculate relevance score for a suggestion."""
        query_lower = partial_query.lower()
        suggestion_lower = suggestion.suggestion.lower()
        
        # Exact prefix match gets highest score
        if suggestion_lower.startswith(query_lower):
            return 1.0
        
        # Contains partial query gets medium score
        if query_lower in suggestion_lower:
            return 0.8
        
        # Word-level similarity
        query_words = set(query_lower.split())
        suggestion_words = set(suggestion_lower.split())
        
        if query_words and suggestion_words:
            intersection = len(query_words.intersection(suggestion_words))
            union = len(query_words.union(suggestion_words))
            jaccard_similarity = intersection / union if union > 0 else 0
            return jaccard_similarity * 0.6
        
        return 0.1
    
    def _calculate_query_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries."""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from query."""
        # Simple term extraction (can be enhanced with NLP)
        terms = re.findall(r'\b\w+\b', query.lower())
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [term for term in terms if term not in stop_words and len(term) > 2]
    
    def _is_safe_query(self, query: str) -> bool:
        """Check if query is safe (no malicious content)."""
        query_lower = query.lower()
        
        for pattern in self._blocked_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False
        
        return True
    
    def _generate_cache_key(self, partial_query: str, context: SearchContext = None) -> str:
        """Generate cache key for suggestions."""
        key_parts = [partial_query]
        
        if context:
            if context.user_id:
                key_parts.append(f"user:{context.user_id}")
            if context.content_type:
                key_parts.append(f"type:{context.content_type}")
            if context.current_filters:
                filter_str = json.dumps(context.current_filters, sort_keys=True)
                key_parts.append(f"filters:{hashlib.md5(filter_str.encode()).hexdigest()}")
        
        cache_key = "|".join(key_parts)
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    async def _get_cached_suggestions(self, cache_key: str) -> Optional[List[QuerySuggestion]]:
        """Get suggestions from cache."""
        if cache_key in self._suggestion_cache:
            cached_time, suggestions = self._suggestion_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                return suggestions
            else:
                del self._suggestion_cache[cache_key]
        
        # Try Redis cache if available
        if self.cache:
            try:
                cached_data = await self.cache.get(f"suggestions:{cache_key}")
                if cached_data:
                    suggestions_data = json.loads(cached_data)
                    suggestions = [
                        QuerySuggestion(
                            suggestion=s["suggestion"],
                            confidence=s["confidence"],
                            suggestion_type=s["suggestion_type"],
                            frequency=s.get("frequency", 0),
                            metadata=s.get("metadata", {})
                        )
                        for s in suggestions_data
                    ]
                    return suggestions
            except Exception as e:
                self.logger.error(f"Error reading from cache: {e}")
        
        return None
    
    async def _cache_suggestions(self, cache_key: str, suggestions: List[QuerySuggestion]) -> None:
        """Cache suggestions."""
        # Local cache
        self._suggestion_cache[cache_key] = (time.time(), suggestions)
        
        # Redis cache if available
        if self.cache:
            try:
                suggestions_data = [
                    {
                        "suggestion": s.suggestion,
                        "confidence": s.confidence,
                        "suggestion_type": s.suggestion_type,
                        "frequency": s.frequency,
                        "metadata": s.metadata
                    }
                    for s in suggestions
                ]
                await self.cache.setex(
                    f"suggestions:{cache_key}",
                    self._cache_ttl,
                    json.dumps(suggestions_data)
                )
            except Exception as e:
                self.logger.error(f"Error writing to cache: {e}")
    
    async def _clear_suggestion_cache(self, term: str) -> None:
        """Clear suggestion cache for related terms."""
        # Clear local cache entries containing the term
        keys_to_remove = [
            key for key in self._suggestion_cache.keys()
            if term.lower() in key.lower()
        ]
        
        for key in keys_to_remove:
            del self._suggestion_cache[key]
    
    def _initialize_default_data(self) -> None:
        """Initialize with default synonym mappings and trending data."""
        # Content creation synonyms
        self._synonym_map.update({
            'video': ['clip', 'recording', 'footage', 'content'],
            'music': ['audio', 'song', 'track', 'sound'],
            'photo': ['image', 'picture', 'pic', 'shot'],
            'creator': ['influencer', 'artist', 'producer', 'content maker'],
            'collaboration': ['collab', 'partnership', 'teamwork', 'joint project'],
            'trending': ['viral', 'popular', 'hot', 'buzzing'],
            'monetize': ['earn', 'profit', 'revenue', 'income'],
            'audience': ['followers', 'fans', 'viewers', 'subscribers'],
            'engagement': ['interaction', 'involvement', 'participation'],
            'brand': ['company', 'business', 'organization', 'corp']
        })
        
        # Initialize trending queries (would be updated from real data)
        self._trending_queries = [
            ('viral videos', 0.9),
            ('collaboration opportunities', 0.8),
            ('music production', 0.7),
            ('content monetization', 0.6),
            ('social media marketing', 0.5)
        ]
    
    def _build_query_embeddings(self, queries: List[str]) -> None:
        """Build query embeddings for similarity search."""
        if not ML_AVAILABLE or not self._tfidf_vectorizer:
            return
        
        try:
            # Transform queries to vectors
            query_vectors = self._tfidf_vectorizer.transform(queries)
            
            # Store embeddings
            for i, query in enumerate(queries):
                if query not in self._query_embeddings:
                    self._query_embeddings[query] = query_vectors[i].toarray()[0]
            
            self.logger.info(f"Built embeddings for {len(self._query_embeddings)} queries")
            
        except Exception as e:
            self.logger.error(f"Error building query embeddings: {e}")
    
    async def _update_trending_queries(self) -> None:
        """Update trending queries based on recent analytics."""
        try:
            # Calculate trending score based on recent frequency and growth
            current_time = datetime.utcnow()
            recent_cutoff = current_time - timedelta(hours=24)
            
            recent_queries = [
                a.query for a in self._query_analytics
                if a.timestamp >= recent_cutoff
            ]
            
            if recent_queries:
                recent_counts = Counter(recent_queries)
                
                # Calculate trend scores (simplified)
                trending_scores = []
                for query, count in recent_counts.most_common(20):
                    # Normalize by total frequency
                    total_count = self._query_frequency.get(query, count)
                    trend_score = count / max(total_count, 1)
                    trending_scores.append((query, min(trend_score, 1.0)))
                
                self._trending_queries = trending_scores
            
        except Exception as e:
            self.logger.error(f"Error updating trending queries: {e}")
    
    async def _get_filter_suggestions(self, query: str, context: SearchContext) -> List[str]:
        """Get contextual filter suggestions."""
        suggestions = []
        
        # Content type filters
        if 'video' in query:
            suggestions.extend(['duration:short', 'duration:medium', 'duration:long', 'quality:hd'])
        elif 'music' in query:
            suggestions.extend(['genre:pop', 'genre:rock', 'genre:electronic', 'duration:short'])
        elif 'photo' in query:
            suggestions.extend(['orientation:landscape', 'orientation:portrait', 'resolution:high'])
        
        # Time-based filters
        suggestions.extend(['time:today', 'time:week', 'time:month'])
        
        # Popularity filters
        suggestions.extend(['sort:popular', 'sort:recent', 'sort:trending'])
        
        return suggestions[:5]
    
    async def _get_related_queries(self, query: str) -> List[str]:
        """Get related queries based on analytics."""
        related = []
        
        # Find queries with similar terms
        query_terms = set(self._extract_query_terms(query))
        
        for analytics in self._query_analytics[-1000:]:  # Check recent analytics
            other_terms = set(self._extract_query_terms(analytics.query))
            
            # Calculate term overlap
            if query_terms and other_terms:
                overlap = len(query_terms.intersection(other_terms))
                if overlap > 0 and analytics.query != query:
                    related.append(analytics.query)
        
        # Return most frequent related queries
        related_counts = Counter(related)
        return [query for query, count in related_counts.most_common(5)]
    
    async def _get_ml_term_expansions(self, query: str) -> List[str]:
        """Get ML-powered term expansions."""
        # This would typically use word embeddings or language models
        # For now, return basic expansions
        expansions = []
        
        terms = self._extract_query_terms(query)
        for term in terms:
            if term in self._synonym_map:
                expansions.extend(self._synonym_map[term][:2])  # Limit expansions
        
        return expansions
    
    async def _identify_boost_terms(self, query: str, context: SearchContext = None) -> List[str]:
        """Identify terms that should be boosted in search."""
        boost_terms = []
        
        # Boost terms based on context
        if context and context.content_type:
            boost_terms.append(context.content_type)
        
        # Boost terms that appear in trending queries
        for trending_query, score in self._trending_queries:
            trending_terms = self._extract_query_terms(trending_query)
            query_terms = self._extract_query_terms(query)
            
            common_terms = set(trending_terms).intersection(set(query_terms))
            boost_terms.extend(list(common_terms))
        
        return list(set(boost_terms))  # Remove duplicates
    
    async def _update_user_profile(self, user_id: str, analytics: QueryAnalytics) -> None:
        """Update user profile based on search analytics."""
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = {
                "preferred_categories": [],
                "search_patterns": [],
                "avg_session_duration": 0.0,
                "total_searches": 0
            }
        
        profile = self._user_profiles[user_id]
        profile["total_searches"] += 1
        
        # Update average session duration
        profile["avg_session_duration"] = (
            (profile["avg_session_duration"] * (profile["total_searches"] - 1) + analytics.session_duration) /
            profile["total_searches"]
        )
        
        # Extract categories from query (simplified)
        query_terms = self._extract_query_terms(analytics.query)
        for term in query_terms:
            if term in ['video', 'music', 'photo', 'art', 'gaming', 'food', 'travel', 'tech']:
                if term not in profile["preferred_categories"]:
                    profile["preferred_categories"].append(term)
    
    async def _store_query_analytics(self, analytics: QueryAnalytics) -> None:
        """Store query analytics in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "query": analytics.query,
                "timestamp": analytics.timestamp,
                "user_id": analytics.user_id,
                "result_count": analytics.result_count,
                "click_through_rate": analytics.click_through_rate,
                "conversion_rate": analytics.conversion_rate,
                "session_duration": analytics.session_duration,
                "filters_used": analytics.filters_used
            }
            
            await self.db.search_analytics.insert_one(doc)
            
        except Exception as e:
            self.logger.error(f"Error storing query analytics: {e}")
    
    async def _store_synonym_mapping(self, term: str, synonyms: List[str]) -> None:
        """Store synonym mapping in database."""
        if not self.db:
            return
        
        try:
            doc = {
                "term": term,
                "synonyms": synonyms,
                "created_at": datetime.utcnow()
            }
            
            await self.db.search_synonyms.replace_one(
                {"term": term},
                doc,
                upsert=True
            )
            
        except Exception as e:
            self.logger.error(f"Error storing synonym mapping: {e}")

__all__ = ['SearchSuggester', 'QuerySuggestion', 'SearchContext', 'QueryAnalytics']