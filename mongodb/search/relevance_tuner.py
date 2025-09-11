"""MongoDB Relevance Tuner
========================

Search relevance optimization and tuning.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RelevanceTuner:
    """Search relevance optimizer and tuner."""
    
    def __init__(self):
        """Initialize relevance tuner."""
        self._boost_rules = {}
    
    def add_boost_rule(self, field: str, boost_factor: float) -> None:
        """Add field boost rule for relevance scoring."""
        self._boost_rules[field] = boost_factor
        logger.info(f"Added boost rule: {field} -> {boost_factor}")
    
    def calculate_relevance_score(self, document: Dict[str, Any], 
                                base_score: float) -> float:
        """Calculate enhanced relevance score."""
        enhanced_score = base_score
        
        # Apply boost rules
        for field, boost in self._boost_rules.items():
            if field in document:
                enhanced_score *= (1 + boost)
        
        return enhanced_score

__all__ = ['RelevanceTuner']