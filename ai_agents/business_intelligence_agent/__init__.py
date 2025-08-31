"""Business Intelligence Agent - Advanced BI and Analytics

This agent provides comprehensive business intelligence and advanced analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .core.business_intelligence_agent import BusinessIntelligenceAgent
from .models.bi_models import (
    BusinessIntelligenceRequest,
    BusinessIntelligenceResult,
    KPIDashboard,
    BusinessInsight
)

__all__ = [
    'BusinessIntelligenceAgent',
    'BusinessIntelligenceRequest',
    'BusinessIntelligenceResult',
    'KPIDashboard', 
    'BusinessInsight'
]

__version__ = "1.0.0"