"""Event Priority Enumeration

Defines priority levels for event processing to ensure proper handling order
and resource allocation in the enterprise event system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from enum import Enum, IntEnum

class EventPriority(IntEnum):
    """
    Event priority levels for processing order and resource allocation
    
    Higher numeric values indicate higher priority.
    """

    
    LOW = 1
    """
Low priority events - batch processing, analytics, reporting"""

    
    MEDIUM = 2
    """
Medium priority events - standard content processing, routine operations"""

    
    HIGH = 3
    """
High priority events - real-time processing, user-facing operations"""

    
    CRITICAL = 4
    """
Critical priority events - security alerts, system failures, urgent operations"""

    
    EMERGENCY = 5
    """
Emergency priority events - immediate attention required, system-critical"""
    
    def __str__(self) -> str:
        return self.name.lower()
    
    def get_description(self) -> str:
        """
Get human-readable description of priority level"""
        descriptions = {
            EventPriority.LOW: "Low priority - background processing",
            EventPriority.MEDIUM: "Medium priority - standard operations", 
            EventPriority.HIGH: "High priority - real-time processing",
            EventPriority.CRITICAL: "Critical priority - urgent processing",
            EventPriority.EMERGENCY: "Emergency priority - immediate attention"
        }
        return descriptions.get(self, "Unknown priority level")
    
    def get_timeout_seconds(self) -> int:
        """Get recommended timeout for this priority level"""
        timeouts = {
            EventPriority.LOW: 600,      # 10 minutes
            EventPriority.MEDIUM: 300,   # 5 minutes
            EventPriority.HIGH: 60,      # 1 minute
            EventPriority.CRITICAL: 30,  # 30 seconds
            EventPriority.EMERGENCY: 10  # 10 seconds
        }
        return timeouts.get(self, 300)
    
    def get_retry_attempts(self) -> int:
        """
Get recommended retry attempts for this priority level"""
        retries = {
            EventPriority.LOW: 1,
            EventPriority.MEDIUM: 2,
            EventPriority.HIGH: 3,
            EventPriority.CRITICAL: 5,
            EventPriority.EMERGENCY: 3
        }
        return retries.get(self, 2)

# Export enum
__all__ = ['EventPriority']
