"""MongoDB Search Suggester
=========================

Intelligent search suggestions and query expansion.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SearchSuggester:
    """Intelligent search suggester with query expansion."""
    
    def __init__(self):
        """Initialize search suggester."""
        self._synonym_map = {
            'user': ['customer', 'client', 'member'],
            'content': ['post', 'article', 'material'],
            'video': ['clip', 'recording', 'footage']
        }
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest query improvements."""
        suggestions = []
        
        # Add synonym-based suggestions
        words = query.lower().split()
        for word in words:
            if word in self._synonym_map:
                for synonym in self._synonym_map[word]:
                    suggested_query = query.replace(word, synonym)
                    suggestions.append(suggested_query)
        
        return suggestions
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms."""
        expanded_queries = [query]  # Include original
        
        # Add suggestions
        suggestions = self.suggest_query_improvements(query)
        expanded_queries.extend(suggestions)
        
        return expanded_queries

__all__ = ['SearchSuggester']