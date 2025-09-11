"""MongoDB Search Analytics
=========================

Search analytics and performance monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchAnalytics:
    """Search analytics and performance tracking."""
    
    def __init__(self):
        """Initialize search analytics."""
        self._analytics_data = {
            'total_searches': 0,
            'popular_queries': {},
            'zero_result_queries': [],
            'avg_response_time': 0.0
        }
    
    def record_search(self, query: str, result_count: int, response_time_ms: float) -> None:
        """Record search analytics."""
        self._analytics_data['total_searches'] += 1
        
        # Track popular queries
        if query in self._analytics_data['popular_queries']:
            self._analytics_data['popular_queries'][query] += 1
        else:
            self._analytics_data['popular_queries'][query] = 1
        
        # Track zero results
        if result_count == 0:
            self._analytics_data['zero_result_queries'].append(query)
        
        # Update response time
        total = self._analytics_data['total_searches']
        current_avg = self._analytics_data['avg_response_time']
        new_avg = ((current_avg * (total - 1)) + response_time_ms) / total
        self._analytics_data['avg_response_time'] = new_avg
    
    def get_analytics_report(self) -> Dict[str, Any]:
        """Get comprehensive analytics report."""
        return self._analytics_data.copy()

__all__ = ['SearchAnalytics']