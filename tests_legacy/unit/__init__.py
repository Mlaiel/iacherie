# -*- coding: utf-8 -*-
"""
Unit Tests Module for Ainflue Platform
=====================================

This module contains unit tests for all core components of the Ainflue platform.
Unit tests are focused on testing individual components in isolation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Test suite components
__all__ = [
    "test_audio_processing",
    "test_ai_models", 
    "test_collaboration",
    "test_monetization",
    "test_gamification",
    "test_distribution",
    "test_security",
    "test_notifications"
]

# Test configuration
TEST_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "test_data_dir": "tests/data",
    "mock_mode": True
}