"""MongoDB AI Prediction Cache
=============================

Caching system for AI model predictions and inference results.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class PredictionCache:
    """High-performance cache for AI model predictions."""
    
    def __init__(self, client: MongoClient, database_name: str, 
                 default_ttl_hours: int = 24):
        """Initialize prediction cache.
        
        Args:
            client: MongoDB client instance
            database_name: Target database name
            default_ttl_hours: Default TTL for cached predictions
        """
        self.client = client
        self.database = client[database_name]
        self._cache_collection = 'ai_prediction_cache'
        self.default_ttl_hours = default_ttl_hours
        
        # Initialize TTL index
        self._initialize_ttl_index()
    
    def cache_prediction(self, model_id: str, input_data: Dict[str, Any],
                        prediction: Any, ttl_hours: int = None) -> str:
        """Cache model prediction.
        
        Args:
            model_id: Model identifier
            input_data: Input data used for prediction
            prediction: Prediction result
            ttl_hours: TTL in hours (uses default if None)
            
        Returns:
            Cache key
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(model_id, input_data)
            
            ttl = ttl_hours or self.default_ttl_hours
            expires_at = datetime.utcnow() + timedelta(hours=ttl)
            
            cache_doc = {
                'cache_key': cache_key,
                'model_id': model_id,
                'input_data': input_data,
                'prediction': prediction,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at
            }
            
            # Upsert cache entry
            self.database[self._cache_collection].update_one(
                {'cache_key': cache_key},
                {'$set': cache_doc},
                upsert=True
            )
            
            logger.debug(f"Cached prediction for model {model_id}")
            return cache_key
            
        except Exception as e:
            logger.error(f"Failed to cache prediction: {e}")
            return ""
    
    def get_cached_prediction(self, model_id: str, input_data: Dict[str, Any]) -> Optional[Any]:
        """Get cached prediction.
        
        Args:
            model_id: Model identifier
            input_data: Input data
            
        Returns:
            Cached prediction or None if not found
        """
        try:
            cache_key = self._generate_cache_key(model_id, input_data)
            
            doc = self.database[self._cache_collection].find_one({
                'cache_key': cache_key,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            
            if doc:
                logger.debug(f"Cache HIT for model {model_id}")
                return doc['prediction']
            else:
                logger.debug(f"Cache MISS for model {model_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get cached prediction: {e}")
            return None
    
    def invalidate_model_cache(self, model_id: str) -> int:
        """Invalidate all cached predictions for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Number of entries invalidated
        """
        try:
            result = self.database[self._cache_collection].delete_many({
                'model_id': model_id
            })
            
            count = result.deleted_count
            logger.info(f"Invalidated {count} cache entries for model {model_id}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to invalidate model cache: {e}")
            return 0
    
    def _generate_cache_key(self, model_id: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key from model ID and input data."""
        # Create deterministic string from input data
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        
        # Generate hash
        key_string = f"{model_id}:{input_str}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _initialize_ttl_index(self) -> None:
        """Initialize TTL index for automatic cache expiration."""
        try:
            self.database[self._cache_collection].create_index(
                'expires_at',
                expireAfterSeconds=0
            )
            
            # Create index for fast lookups
            self.database[self._cache_collection].create_index('cache_key')
            self.database[self._cache_collection].create_index('model_id')
            
            logger.debug("Initialized prediction cache indexes")
            
        except Exception as e:
            logger.warning(f"Failed to initialize prediction cache indexes: {e}")

__all__ = ['PredictionCache']