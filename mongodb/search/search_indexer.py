"""MongoDB Search Indexer
=======================

Search index management and optimization for MongoDB collections.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional
from pymongo import MongoClient, TEXT
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

class SearchIndexer:
    """Advanced search index manager for MongoDB collections."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize search indexer."""
        self.client = client
        self.database = client[database_name]
    
    def create_comprehensive_search_index(self, collection_name: str,
                                        text_fields: List[str],
                                        weights: Dict[str, int] = None) -> bool:
        """Create comprehensive search index for collection.
        
        Args:
            collection_name: Target collection
            text_fields: Fields to include in text index
            weights: Field weights for relevance
            
        Returns:
            True if successful
        """
        try:
            collection = self.database[collection_name]
            
            # Create text index
            index_spec = [(field, TEXT) for field in text_fields]
            
            options = {
                'default_language': 'english',
                'weights': weights or {}
            }
            
            collection.create_index(index_spec, **options)
            
            logger.info(f"Created search index for collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create search index: {e}")
            return False

__all__ = ['SearchIndexer']