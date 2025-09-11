"""Data Transformer for MongoDB Migrations
=======================================

Data transformation utilities for migration operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, Callable, List

logger = logging.getLogger(__name__)

class DataTransformer:
    """Data transformation utilities for migrations."""
    
    def __init__(self):
        """Initialize data transformer."""
        self._transformers: Dict[str, Callable] = {}
    
    def register_transformer(self, name: str, transformer: Callable):
        """Register a data transformer function."""
        self._transformers[name] = transformer
        logger.info(f"Registered transformer: {name}")
    
    def transform_document(self, document: Dict[str, Any], transformer_name: str) -> Dict[str, Any]:
        """Transform a document using named transformer."""
        if transformer_name not in self._transformers:
            raise ValueError(f"Transformer not found: {transformer_name}")
        
        return self._transformers[transformer_name](document)
    
    def batch_transform(self, documents: List[Dict[str, Any]], transformer_name: str) -> List[Dict[str, Any]]:
        """Transform multiple documents."""
        return [self.transform_document(doc, transformer_name) for doc in documents]

_default_transformer: Optional[DataTransformer] = None

def get_data_transformer() -> DataTransformer:
    global _default_transformer
    if _default_transformer is None:
        _default_transformer = DataTransformer()
    return _default_transformer

__all__ = ['DataTransformer', 'get_data_transformer']