"""MongoDB Autocomplete Engine
============================

Fast autocomplete and type-ahead search functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

@dataclass
class AutocompleteResult:
    """Autocomplete suggestion result."""
    text: str
    score: float
    category: str
    metadata: Dict[str, Any] = None

class AutocompleteEngine:
    """Fast autocomplete engine with intelligent suggestions."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize autocomplete engine.
        
        Args:
            client: MongoDB client instance
            database_name: Target database name
        """
        self.client = client
        self.database = client[database_name]
        
        # Autocomplete configuration
        self._suggestions_collection = 'autocomplete_suggestions'
        self._min_query_length = 2
        self._max_suggestions = 10
        
        # Initialize suggestions collection
        self._initialize_suggestions_collection()
    
    def suggest(self, query: str, categories: List[str] = None,
               limit: int = None) -> List[AutocompleteResult]:
        """Get autocomplete suggestions.
        
        Args:
            query: Partial query text
            categories: Filter by categories
            limit: Maximum number of suggestions
            
        Returns:
            List of autocomplete suggestions
        """
        if len(query) < self._min_query_length:
            return []
        
        limit = limit or self._max_suggestions
        suggestions = []
        
        try:
            # Build query for suggestions collection
            search_query = {
                'text': {'$regex': f'^{query}', '$options': 'i'}
            }
            
            if categories:
                search_query['category'] = {'$in': categories}
            
            # Search suggestions
            cursor = self.database[self._suggestions_collection].find(search_query)
            cursor = cursor.sort([('score', -1), ('frequency', -1)]).limit(limit)
            
            for doc in cursor:
                suggestion = AutocompleteResult(
                    text=doc['text'],
                    score=doc.get('score', 0.0),
                    category=doc.get('category', 'general'),
                    metadata=doc.get('metadata', {})
                )
                suggestions.append(suggestion)
                
        except Exception as e:
            logger.error(f"Autocomplete suggestion failed: {e}")
        
        return suggestions
    
    def build_suggestions_from_collection(self, collection_name: str,
                                        text_fields: List[str],
                                        category: str = 'general') -> int:
        """Build autocomplete suggestions from collection data.
        
        Args:
            collection_name: Source collection
            text_fields: Fields to extract text from
            category: Suggestion category
            
        Returns:
            Number of suggestions created
        """
        collection = self.database[collection_name]
        suggestions_set: Set[str] = set()
        
        try:
            # Extract text from specified fields
            for doc in collection.find():
                for field in text_fields:
                    if field in doc:
                        value = doc[field]
                        if isinstance(value, str):
                            # Extract words and phrases
                            words = self._extract_suggestions(value)
                            suggestions_set.update(words)
            
            # Insert suggestions
            suggestions_count = 0
            for suggestion_text in suggestions_set:
                if len(suggestion_text) >= self._min_query_length:
                    self._upsert_suggestion(suggestion_text, category)
                    suggestions_count += 1
            
            logger.info(f"Built {suggestions_count} suggestions from collection '{collection_name}'")
            return suggestions_count
            
        except Exception as e:
            logger.error(f"Failed to build suggestions from collection: {e}")
            return 0
    
    def record_suggestion_usage(self, suggestion_text: str) -> None:
        """Record that a suggestion was used to boost its ranking.
        
        Args:
            suggestion_text: Suggestion that was used
        """
        try:
            self.database[self._suggestions_collection].update_one(
                {'text': suggestion_text},
                {'$inc': {'frequency': 1, 'score': 0.1}}
            )
        except Exception as e:
            logger.debug(f"Failed to record suggestion usage: {e}")
    
    def _initialize_suggestions_collection(self) -> None:
        """Initialize autocomplete suggestions collection."""
        try:
            # Create index for fast prefix matching
            self.database[self._suggestions_collection].create_index([
                ('text', 1),
                ('category', 1),
                ('score', -1)
            ])
            
            logger.debug("Initialized autocomplete suggestions collection")
            
        except Exception as e:
            logger.warning(f"Failed to initialize suggestions collection: {e}")
    
    def _extract_suggestions(self, text: str) -> Set[str]:
        """Extract potential autocomplete suggestions from text."""
        suggestions = set()
        
        # Clean and normalize text
        text = text.lower().strip()
        
        # Extract individual words
        words = text.split()
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) >= self._min_query_length:
                suggestions.add(clean_word)
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            clean_phrase = ''.join(c for c in phrase if c.isalnum() or c.isspace()).strip()
            if len(clean_phrase) >= self._min_query_length:
                suggestions.add(clean_phrase)
        
        return suggestions
    
    def _upsert_suggestion(self, text: str, category: str) -> None:
        """Insert or update suggestion."""
        try:
            self.database[self._suggestions_collection].update_one(
                {'text': text, 'category': category},
                {
                    '$set': {
                        'text': text,
                        'category': category,
                        'updated_at': 'now'
                    },
                    '$inc': {'frequency': 1},
                    '$setOnInsert': {'score': 1.0, 'created_at': 'now'}
                },
                upsert=True
            )
        except Exception as e:
            logger.debug(f"Failed to upsert suggestion: {e}")

__all__ = ['AutocompleteEngine', 'AutocompleteResult']