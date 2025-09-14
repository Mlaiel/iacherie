"""MongoDB Feature Store
======================

ML feature store for training and inference pipelines.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pymongo import MongoClient

logger = logging.getLogger(__name__)

@dataclass
class FeatureDefinition:
    """Feature definition metadata."""
    name: str
    data_type: str
    description: str
    category: str
    created_at: datetime
    version: str

class FeatureStore:
    """ML feature store for managing training and inference features."""
    
    def __init__(self, client -> None: MongoClient, database_name -> None: str) -> None:
        """Initialize feature store."""
        self.client = client
        self.database = client[database_name]
        self._features_collection = 'ml_features'
        self._feature_definitions_collection = 'ml_feature_definitions'
    
    def store_features(self, entity_id: str, features: Dict[str, Any],
                      feature_group: str = 'default') -> bool:
        """Store features for an entity.
        
        Args:
            entity_id: Entity identifier (user_id, content_id, etc.)
            features: Feature values
            feature_group: Feature group name
            
        Returns:
            True if successful
        """
        try:
            feature_doc = {
                'entity_id': entity_id,
                'feature_group': feature_group,
                'features': features,
                'timestamp': datetime.utcnow()
            }
            
            # Upsert features
            self.database[self._features_collection].update_one(
                {'entity_id': entity_id, 'feature_group': feature_group},
                {'$set': feature_doc},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store features: {e}")
            return False
    
    def get_features(self, entity_id: str, feature_names: List[str] = None,
                    feature_group: str = 'default') -> Dict[str, Any]:
        """Get features for an entity.
        
        Args:
            entity_id: Entity identifier
            feature_names: Specific features to retrieve
            feature_group: Feature group name
            
        Returns:
            Feature values
        """
        try:
            doc = self.database[self._features_collection].find_one({
                'entity_id': entity_id,
                'feature_group': feature_group
            })
            
            if not doc:
                return {}
            
            features = doc.get('features', {})
            
            if feature_names:
                return {name: features.get(name) for name in feature_names if name in features}
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to get features: {e}")
            return {}
    
    def register_feature_definition(self, definition: FeatureDefinition) -> bool:
        """Register feature definition.
        
        Args:
            definition: Feature definition
            
        Returns:
            True if successful
        """
        try:
            doc = {
                'name': definition.name,
                'data_type': definition.data_type,
                'description': definition.description,
                'category': definition.category,
                'created_at': definition.created_at,
                'version': definition.version
            }
            
            self.database[self._feature_definitions_collection].update_one(
                {'name': definition.name},
                {'$set': doc},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register feature definition: {e}")
            return False

__all__ = ['FeatureStore', 'FeatureDefinition']