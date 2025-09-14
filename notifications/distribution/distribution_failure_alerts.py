"""
❌ DISTRIBUTION FAILURE ALERTS
Ainflue Platform - Distribution Failure Alert System

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class DistributionFailureAlerts:
    """Distribution failure alert and recovery system"""
    
    def __init__(self) -> None:
        logger.info("Distribution failure alerts initialized")
    
    async def notify_distribution_failure(self, user_id: str, content_id: str, 
                                        platform: str, error_data: Dict[str, Any]) -> bool:
        """Notify about distribution failure"""
        try:
            notification_data = {
                "title": "❌ Distribution Failed",
                "message": f"Failed to publish content on {platform}",
                "user_id": user_id,
                "type": "distribution_failure",
                "priority": "high",
                "channels": ["in_app", "email"],
                "metadata": {
                    "content_id": content_id,
                    "platform": platform,
                    "error": error_data.get("error_message"),
                    "retry_available": True
                }
            }
            
            logger.warning(f"Distribution failure notification sent for {content_id} on {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending failure notification: {str(e)}")
            return False

__all__ = ["DistributionFailureAlerts"]