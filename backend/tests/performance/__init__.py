"""
Performance Tests Package
========================

This package contains performance and load testing modules for the Ainflue platform:
- Load scenario testing
- Concurrent user testing  
- Upload performance testing
- AI processing speed testing

All tests use the @pytest.mark.performance marker and are compatible with asyncio.
"""

__version__ = "1.0.0"
__author__ = "Ainflue Performance Team"

# Performance test categories
LOAD_SCENARIOS = "load_scenarios"
CONCURRENT_USERS = "concurrent_users"
UPLOAD_PERFORMANCE = "upload_performance"
AI_PROCESSING_SPEED = "ai_processing_speed"

# Common performance thresholds
PERFORMANCE_THRESHOLDS = {
    "api_response_time_ms": 100,
    "upload_response_time_ms": 5000,
    "ai_processing_time_ms": 2000,
    "concurrent_users_max": 1000,
    "success_rate_min": 0.95
}