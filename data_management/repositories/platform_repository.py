"""
🌐 Platform Repository - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/repositories/platform_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .base_repository import BaseRepository, AsyncBaseRepository, OperationType
from ..models.platform_model import PlatformModel, IntegrationModel

class PlatformRepository(BaseRepository[PlatformModel]):
    """Repository for platform management"""
    
    def __init__(self, db_session, cache_manager=None, vector_store=None):
        super().__init__(db_session, cache_manager, vector_store)
        self.model_class = PlatformModel
        self.table_name = "platforms"
        self.logger = logging.getLogger(__name__)

class AsyncPlatformRepository(AsyncBaseRepository[PlatformModel]):
    """Async repository for platform management"""
    
    def __init__(self, db_session, cache_manager=None, vector_store=None):
        super().__init__(db_session, cache_manager, vector_store)
        self.model_class = PlatformModel
        self.table_name = "platforms"
        self.logger = logging.getLogger(__name__)