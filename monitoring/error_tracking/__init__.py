"""
Error Tracking Module for Ainflue Platform
Comprehensive error tracking and reporting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .sentry_integration import SentryErrorTracker, ErrorContext, capture_business_error, capture_ai_processing_error
from .error_aggregator import ErrorAggregator
from .error_analyzer import ErrorAnalyzer

__all__ = [
    'SentryErrorTracker',
    'ErrorContext',
    'ErrorAggregator', 
    'ErrorAnalyzer',
    'capture_business_error',
    'capture_ai_processing_error'
]