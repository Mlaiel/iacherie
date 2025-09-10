"""
Database Infrastructure Module
=================================
Enterprise database management for Ainflue platform

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue - IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved
"""

from .postgresql_cluster import PostgresqlclusterManager, get_postgresql_cluster_manager
from .redis_cluster import RedisclusterManager, get_redis_cluster_manager
from .mongodb_cluster import MongodbclusterManager, get_mongodb_cluster_manager

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

__all__ = [
    "PostgresqlclusterManager", "get_postgresql_cluster_manager", "RedisclusterManager", "get_redis_cluster_manager", "MongodbclusterManager", "get_mongodb_cluster_manager"
]