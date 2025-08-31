"""Database Module - IA Influencer Agent + Content Protection Platform

This module provides comprehensive database management for the IA Influencer Agent platform,
including content fingerprinting, protection alerts, monetization tracking, and vector operations.

Architecture:
- Multi-database support (PostgreSQL, Redis, MongoDB, Elasticsearch)
- Vector database integration (FAISS, Pinecone)
- Advanced security and encryption
- Real-time monitoring and analytics
- Automated migrations and schema management

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""# Core database components
from .connections import *
from .models import *
from .schemas import *
from .repositories import *
from .migrations import *

# Specialized modules
from .vector_stores import *
from .fingerprinting import *
from .content_protection import *
from .monetization import *
from .ai_engines import *
from .blockchain import *
from .content_distribution import *
from .crawling import *
from .licensing import *
from .notification_systems import *
from .payment_processing import *
from .revenue_tracking import *
from .surveillance import *
from .user_management import *
from .content_types import *
from .collaboration import *
from .audit_logs import *
from .platform_integrations import *
from .legal_compliance import *

# Infrastructure modules
from .security import *
from .monitoring import *
from .indexing import *
from .optimizations import *
from .partitioning import *
from .pools import *
from .replication import *
from .transactions import *
from .authentication import *
from .communication import *
from .analytics import *
from .workflows import *
from .cross_platform_distribution import *

__all__ = [
    # Core components
    "connections",
    "models", 
    "schemas",
    "repositories",
    "migrations",
    # Specialized modules
    "vector_stores",
    "fingerprinting",
    "content_protection", 
    "monetization",
    "ai_engines",
    "blockchain",
    "content_distribution",
    "crawling",
    "licensing",
    "notification_systems",
    "payment_processing",
    "revenue_tracking",
    "surveillance",
    "user_management",
    "content_types",
    "collaboration",
    "audit_logs",
    "platform_integrations",
    "legal_compliance",
    # Infrastructure
    "security",
    "monitoring",
    "indexing",
    "optimizations",
    "partitioning",
    "pools",
    "replication",
    "transactions",
    "authentication",
    "communication",
    "analytics",
    "workflows",
    "cross_platform_distribution"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
