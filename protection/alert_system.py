"""Alert System for Content Protection
Real-time alert management and notification system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

from ..core.database import database_manager
from ..core.logging import logger


class AlertSystem:
    """
Advanced alert system for content protection violations"""
    
    def __init__(self):
        self.alert_channels = ["email", "push", "webhook"]
        self.severity_levels = ["low", "medium", "high", "critical"]
    
    async def send_violation_alert(self, user_id: str, violation_data: Dict[str, Any]):
        """Send alert for content protection violation"""
        try:
            # Determine alert severity
            similarity_score = violation_data.get("similarity_score", 0.0)
            severity = self._calculate_severity(similarity_score)
            
            # Create alert message
            alert_message = self._create_alert_message(violation_data, severity)
            
            # Get user notification preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Send alerts through enabled channels
            for channel in preferences.get("enabled_channels", ["email"]):
                await self._send_alert_via_channel(
                    channel, user_id, alert_message, severity
                )
            
            # Store alert in database
            await self._store_alert(user_id, violation_data, alert_message, severity)
            
            logger.info(f"Violation alert sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to send violation alert: {str(e)}")
    
    def _calculate_severity(self, similarity_score: float) -> str:
        """Calculate alert severity based on similarity score"""
        if similarity_score >= 0.95:
            return "critical"
        elif similarity_score >= 0.90:
            return "high"
        elif similarity_score >= 0.85:
            return "medium"
        else:
            return "low"
    
    def _create_alert_message(self, violation_data: Dict[str, Any], severity: str) -> Dict[str, Any]:
        """Create structured alert message"""
        return {
            "title": f"Content Protection Alert - {severity.upper()}",
            "message": f"Potential violation detected on {violation_data['platform']}",
            "details": {
                "platform": violation_data["platform"],
                "url": violation_data["violation_url"],
                "similarity": f"{violation_data['similarity_score']:.2%}",
                "detected_at": violation_data["detected_at"].isoformat()
            },
            "severity": severity,
            "action_required": True if severity in ["high", "critical"] else False
        }
    
    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        # Default preferences
        return {
            "enabled_channels": ["email"],
            "severity_threshold": "medium",
            "immediate_alerts": True
        }
    
    async def _send_alert_via_channel(self, channel: str, user_id: str, 
                                    message: Dict[str, Any], severity: str):
        """Send alert through specific channel"""
        try:
            if channel == "email":
                await self._send_email_alert(user_id, message)
            elif channel == "push":
                await self._send_push_alert(user_id, message)
            elif channel == "webhook":
                await self._send_webhook_alert(user_id, message)
        
        except Exception as e:
            logger.error(f"Failed to send alert via {channel}: {str(e)}")
    
    async def _send_email_alert(self, user_id: str, message: Dict[str, Any]):
        """Send email alert"""
        # Implementation would integrate with email service
        logger.info(f"Email alert would be sent to user {user_id}")
    
    async def _send_push_alert(self, user_id: str, message: Dict[str, Any]):
        """Send push notification"""
        # Implementation would integrate with push notification service
        logger.info(f"Push alert would be sent to user {user_id}")
    
    async def _send_webhook_alert(self, user_id: str, message: Dict[str, Any]):
        """Send webhook alert"""
        # Implementation would call user's webhook URL
        logger.info(f"Webhook alert would be sent to user {user_id}")
    
    async def _store_alert(self, user_id: str, violation_data: Dict[str, Any], 
                         message: Dict[str, Any], severity: str):
        """Store alert in database"""
        try:
            async with database_manager.get_postgres_session() as session:
                await session.execute(
                    """
                    INSERT INTO user_alerts 
                    (user_id, alert_type, severity, message, related_violation_id, 
                     created_at, read_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, "violation", severity, json.dumps(message),
                     violation_data.get("violation_id"), datetime.utcnow(), None)
                )
        except Exception as e:
            logger.error(f"Failed to store alert: {str(e)}")


# Global alert system instance
alert_system = AlertSystem()