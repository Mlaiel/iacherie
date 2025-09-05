"""Event System Exceptions

Custom exceptions for the IA Influencer Agent event system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""


class EventProcessingError(Exception):
    """Raised when an error occurs during event processing"""
    pass


class EventValidationError(Exception):
    """Raised when event validation fails"""
    pass


class EventSourcingError(Exception):
    """Raised when an error occurs in event sourcing operations"""
    pass


class HandlerNotFoundError(Exception):
    """Raised when no suitable handler is found for an event"""
    pass


class ProcessingTimeoutError(Exception):
    """Raised when event processing times out"""
    pass


class EventStreamingError(Exception):
    """Raised when an error occurs in event streaming operations"""
    pass


# Export for compatibility
__all__ = [
    'EventProcessingError',
    'EventValidationError', 
    'EventSourcingError',
    'HandlerNotFoundError',
    'ProcessingTimeoutError',
    'EventStreamingError'
]