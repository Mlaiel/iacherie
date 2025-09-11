"""
Test suite for Ainflue Platform API
Enterprise-grade testing infrastructure for all orchestrators and endpoints

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from typing import AsyncGenerator
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
TEST_CONFIG = {
    "api_base_url": "http://testserver",
    "test_database_url": "sqlite:///./test.db",
    "test_redis_url": "redis://localhost:6379/15",
    "test_mode": True,
}

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"