"""Event Status Enumeration

Defines status states for event processing lifecycle management
in the enterprise event system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from enum import Enum
from typing import List, Set

class EventStatus(Enum):
    """
    Event status states for tracking processing lifecycle
    """

    
    PENDING = "pending"
    """Event created but not yet started processing"""

    
    QUEUED = "queued" 
    """Event queued for processing"""

    
    PROCESSING = "processing"
    """Event currently being processed"""

    
    COMPLETED = "completed"
    """Event processing completed successfully"""

    
    FAILED = "failed"
    """Event processing failed with errors"""

    
    CANCELLED = "cancelled"
    """Event processing was cancelled"""

    
    TIMEOUT = "timeout"
    """Event processing exceeded timeout limit"""

    
    RETRY = "retry"
    """Event marked for retry after failure"""

    
    PAUSED = "paused"
    """Event processing temporarily paused"""

    
    ARCHIVED = "archived"
    """Event archived after completion or failure"""
    
    def __str__(self) -> str:
        return self.value
    
    def is_terminal(self) -> bool:
        """
Check if this is a terminal status (no further processing)"""
        terminal_statuses = {
            EventStatus.COMPLETED,
            EventStatus.CANCELLED,
            EventStatus.ARCHIVED
        }
        return self in terminal_statuses
    
    def is_active(self) -> bool:
        """
Check if event is actively being processed"""
        active_statuses = {
            EventStatus.QUEUED,
            EventStatus.PROCESSING,
            EventStatus.RETRY
        }
        return self in active_statuses
    
    def is_error(self) -> bool:
        """
Check if status indicates an error condition"""
        error_statuses = {
            EventStatus.FAILED,
            EventStatus.TIMEOUT
        }
        return self in error_statuses
    
    def can_transition_to(self, new_status: 'EventStatus') -> bool:
        """
Check if transition to new status is valid"""
        # Define valid transitions
        valid_transitions = {
            EventStatus.PENDING: {
                EventStatus.QUEUED,
                EventStatus.CANCELLED
            },
            EventStatus.QUEUED: {
                EventStatus.PROCESSING,
                EventStatus.CANCELLED,
                EventStatus.PAUSED
            },
            EventStatus.PROCESSING: {
                EventStatus.COMPLETED,
                EventStatus.FAILED,
                EventStatus.TIMEOUT,
                EventStatus.PAUSED,
                EventStatus.CANCELLED
            },
            EventStatus.FAILED: {
                EventStatus.RETRY,
                EventStatus.CANCELLED,
                EventStatus.ARCHIVED
            },
            EventStatus.TIMEOUT: {
                EventStatus.RETRY,
                EventStatus.CANCELLED,
                EventStatus.ARCHIVED
            },
            EventStatus.RETRY: {
                EventStatus.QUEUED,
                EventStatus.PROCESSING,
                EventStatus.CANCELLED
            },
            EventStatus.PAUSED: {
                EventStatus.PROCESSING,
                EventStatus.CANCELLED,
                EventStatus.ARCHIVED
            },
            EventStatus.COMPLETED: {
                EventStatus.ARCHIVED
            },
            EventStatus.CANCELLED: {
                EventStatus.ARCHIVED
            },
            EventStatus.ARCHIVED: set()  # Terminal state
        }
        
        allowed_transitions = valid_transitions.get(self, set())
        return new_status in allowed_transitions
    
    def get_description(self) -> str:
        """
Get human-readable description of status"""
        descriptions = {
            EventStatus.PENDING: "Event created and waiting to start",
            EventStatus.QUEUED: "Event queued for processing",
            EventStatus.PROCESSING: "Event is currently being processed",
            EventStatus.COMPLETED: "Event processing completed successfully",
            EventStatus.FAILED: "Event processing failed with errors",
            EventStatus.CANCELLED: "Event processing was cancelled",
            EventStatus.TIMEOUT: "Event processing exceeded time limit",
            EventStatus.RETRY: "Event marked for retry processing",
            EventStatus.PAUSED: "Event processing temporarily suspended",
            EventStatus.ARCHIVED: "Event archived and stored"
        }
        return descriptions.get(self, "Unknown status")

    @classmethod
    def get_all_statuses(cls) -> List['EventStatus']:
        """Get list of all available statuses"""
        return list(cls)
    
    @classmethod
    def get_terminal_statuses(cls) -> Set['EventStatus']:
        """
Get set of terminal statuses"""
        return {status for status in cls if status.is_terminal()}
    
    @classmethod
    def get_active_statuses(cls) -> Set['EventStatus']:
        """
Get set of active processing statuses"""
        return {status for status in cls if status.is_active()}
    
    @classmethod
    def get_error_statuses(cls) -> Set['EventStatus']:
        """
Get set of error statuses"""
        return {status for status in cls if status.is_error()}

# Export enum
__all__ = ['EventStatus']
