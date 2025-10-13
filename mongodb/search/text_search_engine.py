"""MongoDB Text Search Engine
===========================

Advanced full-text search capabilities with ranking and relevance scoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pymongo import MongoClient, TEXT
from pymongo.collection import Collection
from pymongo.errors import OperationFailure
import math

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    document: Dict[str, Any]
    score: float
    highlights: List[str]
    collection_name: str
    matched_fields: List[str]

@dataclass
class SearchQuery:
    """Search query configuration."""
    text: str
    collections: List[str] = None
    fields: List[str] = None
    filters: Dict[str, Any] = None
    limit: int = 10
    skip: int = 0
    sort_by_relevance: bool = True
    include_highlights: bool = True
    fuzzy_matching: bool = False
    boost_fields: Dict[str, float] = None

class TextSearchEngine:
    """Advanced MongoDB text search engine with relevance scoring and highlighting."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize text search engine.
        
        Args:
            client: MongoDB client instance
            database_name: Target database name
        """
        self.client = client
        self.database = client[database_name]
        
        # Search configuration
        self._default_language = 'english'
        self._stop_words = self._load_stop_words()
        self._text_indexes: Dict[str, Dict[str, Any]] = {}
        
        # Analytics tracking
        self._search_analytics = {
            'total_searches': 0,
            'avg_response_time_ms': 0.0,
            'top_queries': {},
            'zero_result_queries': [],
            'popular_collections': {}
        }
        
        # Cache for common queries
        self._query_cache: Dict[str, List[SearchResult]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Initialize text indexes
        self._discover_text_indexes()
    
    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform text search across collections.
        
        Args:
            query: Search query configuration
            
        Returns:
            List of search results with relevance scores
        """
        import time
        start_time = time.time()
        
        # Update analytics
        self._search_analytics['total_searches'] += 1
        
        # Check cache first
        cache_key = self._generate_cache_key(query)
        if cache_key in self._query_cache:
            cached_results = self._query_cache[cache_key]
            logger.debug(f"Returning cached results for query: {query.text}")
            return cached_results
        
        results = []
        
        try:
            # Determine target collections
            target_collections = query.collections or list(self._text_indexes.keys())
            
            # Search each collection
            for collection_name in target_collections:
                if collection_name in self._text_indexes:
                    collection_results = self._search_collection(
                        collection_name, query
                    )
                    results.extend(collection_results)
            
            # Sort by relevance score
            if query.sort_by_relevance:
                results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply pagination
            if query.skip > 0:
                results = results[query.skip:]
            if query.limit > 0:
                results = results[:query.limit]
            
            # Cache results
            self._query_cache[cache_key] = results
            
            # Update analytics
            execution_time = (time.time() - start_time) * 1000
            self._update_search_analytics(query, results, execution_time)
            
            logger.debug(f"Search completed: {len(results)} results in {execution_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Track zero results
            self._search_analytics['zero_result_queries'].append(query.text)
        
        return results
    
    def create_text_index(self, collection_name: str, fields: Dict[str, Union[str, int]],
                         language: str = None, weights: Dict[str, int] = None) -> bool:
        """Create text index on collection.
        
        Args:
            collection_name: Collection name
            fields: Fields to index (field_name: "text")
            language: Index language (default: english)
            weights: Field weights for relevance scoring
            
        Returns:
            True if index created successfully
        """
        try:
            collection = self.database[collection_name]
            
            # Prepare index specification
            index_spec = [(field, TEXT) for field in fields.keys()]
            
            # Index options
            options = {
                'default_language': language or self._default_language
            }
            
            if weights:
                options['weights'] = weights
            
            # Create index
            collection.create_index(index_spec, **options)
            
            # Update local tracking
            self._text_indexes[collection_name] = {
                'fields': list(fields.keys()),
                'language': language or self._default_language,
                'weights': weights or {}
            }
            
            logger.info(f"Created text index on collection '{collection_name}' for fields: {list(fields.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create text index: {e}")
            return False
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest query improvements for better search results.
        
        Args:
            query: Original search query
            
        Returns:
            List of suggested improvements
        """
        suggestions = []
        
        # Check query length
        if len(query.split()) < 2:
            suggestions.append("Try using more specific keywords")
        
        # Check for stop words only
        query_words = query.lower().split()
        non_stop_words = [word for word in query_words if word not in self._stop_words]
        if len(non_stop_words) == 0:
            suggestions.append("Try using more descriptive keywords instead of common words")
        
        # Check for special characters
        if re.search(r'[^a-zA-Z0-9\s]', query):
            suggestions.append("Consider removing special characters for better matching")
        
        # Suggest fuzzy matching for typos
        if len(query_words) > 0 and any(len(word) > 6 for word in query_words):
            suggestions.append("Enable fuzzy matching to handle potential typos")
        
        return suggestions
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics and statistics.
        
        Returns:
            Search analytics data
        """
        # Clean up old zero result queries (keep only last 100)
        if len(self._search_analytics['zero_result_queries']) > 100:
            self._search_analytics['zero_result_queries'] = \
                self._search_analytics['zero_result_queries'][-100:]
        
        return self._search_analytics.copy()
    
    def optimize_collection_search(self, collection_name: str) -> Dict[str, Any]:
        """Analyze and optimize search performance for collection.
        
        Args:
            collection_name: Collection to optimize
            
        Returns:
            Optimization recommendations
        """
        if collection_name not in self._text_indexes:
            return {"error": "No text index found for collection"}
        
        collection = self.database[collection_name]
        
        # Analyze collection size
        doc_count = collection.estimated_document_count()
        
        # Check index stats
        index_stats = {}
        try:
            stats = list(collection.aggregate([{"$indexStats": {}}]))
            for stat in stats:
                if 'textScore' in str(stat.get('key', {})):
                    index_stats = stat
                    break
        except Exception:
            pass
        
        recommendations = []
        
        # Size-based recommendations
        if doc_count > 1000000:  # 1M documents
            recommendations.append("Consider sharding this collection for better search performance")
        
        if doc_count > 100000:  # 100K documents
            recommendations.append("Consider using compound indexes for filtered searches")
        
        # Index usage recommendations
        if index_stats:
            access_count = index_stats.get('accesses', {}).get('ops', 0)
            if access_count < 10:
                recommendations.append("Text index may be underutilized - review search patterns")
        
        return {
            'collection_name': collection_name,
            'document_count': doc_count,
            'text_index_info': self._text_indexes[collection_name],
            'index_stats': index_stats,
            'recommendations': recommendations
        }
    
    def _search_collection(self, collection_name: str, query: SearchQuery) -> List[SearchResult]:
        """Search within a specific collection."""
        collection = self.database[collection_name]
        results = []
        
        try:
            # Build MongoDB text search query
            search_filter = {"$text": {"$search": query.text}}
            
            # Add additional filters
            if query.filters:
                search_filter.update(query.filters)
            
            # Add projection to include text score
            projection = {"score": {"$meta": "textScore"}}
            
            # Execute search
            cursor = collection.find(search_filter, projection)
            
            # Sort by text score if relevance sorting is enabled
            if query.sort_by_relevance:
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
            
            # Process results
            for doc in cursor:
                # Extract text score
                text_score = doc.pop('score', 0.0)
                
                # Calculate enhanced relevance score
                relevance_score = self._calculate_relevance_score(
                    doc, query, text_score, collection_name
                )
                
                # Generate highlights
                highlights = []
                if query.include_highlights:
                    highlights = self._generate_highlights(doc, query.text)
                
                # Identify matched fields
                matched_fields = self._identify_matched_fields(doc, query.text)
                
                result = SearchResult(
                    document=doc,
                    score=relevance_score,
                    highlights=highlights,
                    collection_name=collection_name,
                    matched_fields=matched_fields
                )
                
                results.append(result)
                
        except OperationFailure as e:
            logger.warning(f"Text search failed for collection '{collection_name}': {e}")
        
        return results
    
    def _calculate_relevance_score(self, document: Dict[str, Any], query: SearchQuery,
                                 text_score: float, collection_name: str) -> float:
        """Calculate enhanced relevance score."""
        base_score = text_score
        
        # Apply field boost factors
        if query.boost_fields:
            boost_factor = 1.0
            for field, boost in query.boost_fields.items():
                if field in document:
                    field_value = str(document[field]).lower()
                    if query.text.lower() in field_value:
                        boost_factor += boost
            base_score *= boost_factor
        
        # Apply collection-specific boosting
        index_info = self._text_indexes.get(collection_name, {})
        weights = index_info.get('weights', {})
        
        if weights:
            weight_boost = sum(weights.values()) / len(weights)
            base_score *= (1 + weight_boost / 10)
        
        # Apply document freshness boost (if document has timestamp)
        if 'createdAt' in document or 'updatedAt' in document:
            timestamp_field = document.get('updatedAt') or document.get('createdAt')
            if timestamp_field:
                try:
                    from datetime import datetime
                    if isinstance(timestamp_field, datetime):
                        age_days = (datetime.utcnow() - timestamp_field).days
                        freshness_boost = max(0, 1 - (age_days / 365))  # Decay over a year
                        base_score *= (1 + freshness_boost * 0.2)  # Up to 20% boost
                except Exception:
                    pass
        
        return base_score
    
    def _generate_highlights(self, document: Dict[str, Any], query_text: str) -> List[str]:
        """Generate search result highlights."""
        highlights = []
        query_terms = query_text.lower().split()
        
        for field, value in document.items():
            if isinstance(value, str):
                # Find matches in text
                value_lower = value.lower()
                for term in query_terms:
                    if term in value_lower and term not in self._stop_words:
                        # Extract context around the match
                        start_idx = value_lower.find(term)
                        if start_idx != -1:
                            # Get 50 characters before and after
                            context_start = max(0, start_idx - 50)
                            context_end = min(len(value), start_idx + len(term) + 50)
                            
                            context = value[context_start:context_end]
                            # Highlight the term
                            highlighted = context.replace(
                                value[start_idx:start_idx + len(term)],
                                f"**{value[start_idx:start_idx + len(term)]}**"
                            )
                            
                            if highlighted not in highlights:
                                highlights.append(highlighted)
        
        return highlights[:5]  # Limit to 5 highlights
    
    def _identify_matched_fields(self, document: Dict[str, Any], query_text: str) -> List[str]:
        """Identify which fields matched the search query."""
        matched_fields = []
        query_terms = query_text.lower().split()
        
        for field, value in document.items():
            if isinstance(value, str):
                value_lower = value.lower()
                if any(term in value_lower for term in query_terms):
                    matched_fields.append(field)
        
        return matched_fields
    
    def _discover_text_indexes(self) -> None:
        """Discover existing text indexes in the database."""
        try:
            for collection_name in self.database.list_collection_names():
                collection = self.database[collection_name]
                
                # Check for text indexes
                for index_info in collection.list_indexes():
                    index_key = index_info.get('key', {})
                    
                    # Look for text indexes
                    text_fields = [field for field, index_type in index_key.items() if index_type == 'text']
                    
                    if text_fields:
                        weights = index_info.get('weights', {})
                        language = index_info.get('default_language', 'english')
                        
                        self._text_indexes[collection_name] = {
                            'fields': text_fields,
                            'language': language,
                            'weights': weights
                        }
                        
                        logger.debug(f"Discovered text index on '{collection_name}': {text_fields}")
                        
        except Exception as e:
            logger.warning(f"Failed to discover text indexes: {e}")
    
    def _load_stop_words(self) -> set:
        """Load stop words for the default language."""
        # Basic English stop words
        english_stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'two', 'more',
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did',
            'get', 'come', 'made', 'may', 'part'
        }
        
        return english_stop_words
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for query."""
        import hashlib
        import json
        
        # Create deterministic string from query
        query_dict = asdict(query)
        query_str = json.dumps(query_dict, sort_keys=True)
        
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _update_search_analytics(self, query: SearchQuery, results: List[SearchResult],
                               execution_time_ms: float) -> None:
        """Update search analytics."""
        # Update average response time
        total_searches = self._search_analytics['total_searches']
        current_avg = self._search_analytics['avg_response_time_ms']
        
        new_avg = ((current_avg * (total_searches - 1)) + execution_time_ms) / total_searches
        self._search_analytics['avg_response_time_ms'] = new_avg
        
        # Track popular queries
        query_text = query.text.lower()
        if query_text in self._search_analytics['top_queries']:
            self._search_analytics['top_queries'][query_text] += 1
        else:
            self._search_analytics['top_queries'][query_text] = 1
        
        # Track zero results
        if len(results) == 0:
            self._search_analytics['zero_result_queries'].append(query_text)
        
        # Track popular collections
        for result in results:
            collection_name = result.collection_name
            if collection_name in self._search_analytics['popular_collections']:
                self._search_analytics['popular_collections'][collection_name] += 1
            else:
                self._search_analytics['popular_collections'][collection_name] = 1

# Global search engine instance
_default_search_engine: Optional[TextSearchEngine] = None

def get_text_search_engine(client: MongoClient, database_name: str) -> TextSearchEngine:
    """Get or create default text search engine."""
    global _default_search_engine
    if _default_search_engine is None:
        _default_search_engine = TextSearchEngine(client, database_name)
    return _default_search_engine

__all__ = ['TextSearchEngine', 'SearchResult', 'SearchQuery', 'get_text_search_engine']