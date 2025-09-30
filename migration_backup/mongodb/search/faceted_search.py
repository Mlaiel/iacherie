"""MongoDB Faceted Search
=======================

Faceted search implementation for filtering and aggregated results.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class FacetedSearch:
    """Faceted search with aggregation-based filtering."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize faceted search."""
        self.client = client
        self.database = client[database_name]
    
    def search_with_facets(self, collection_name: str, query: Dict[str, Any],
                          facet_fields: List[str]) -> Dict[str, Any]:
        """Perform faceted search with aggregated filters.
        
        Args:
            collection_name: Target collection
            query: Search query
            facet_fields: Fields to create facets for
            
        Returns:
            Search results with facet counts
        """
        collection = self.database[collection_name]
        
        # Build aggregation pipeline
        pipeline = []
        
        # Match stage
        if query:
            pipeline.append({"$match": query})
        
        # Facet stage
        facet_stage = {"$facet": {}}
        
        # Add results
        facet_stage["$facet"]["results"] = [
            {"$limit": 100}  # Limit results
        ]
        
        # Add facet counts
        for field in facet_fields:
            facet_stage["$facet"][f"{field}_counts"] = [
                {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
        
        pipeline.append(facet_stage)
        
        # Execute aggregation
        result = list(collection.aggregate(pipeline))
        
        if result:
            return result[0]
        else:
            return {"results": [], "facets": {}}

__all__ = ['FacetedSearch']