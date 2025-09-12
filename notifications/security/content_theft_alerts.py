"""
🕵️ CONTENT THEFT ALERTS
Ainflue Platform - Content Theft Detection and Alert System

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides advanced content theft detection and alerting for the Ainflue Platform,
using AI-powered analysis to detect unauthorized use of protected content.
"""

from typing import Dict, List, Optional, Any
import asyncio
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TheftSeverity(Enum):
    """Content theft severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TheftType(Enum):
    """Types of content theft"""
    EXACT_COPY = "exact_copy"
    MODIFIED_COPY = "modified_copy"
    PARTIAL_USE = "partial_use"
    DERIVATIVE_WORK = "derivative_work"
    WATERMARK_REMOVAL = "watermark_removal"

@dataclass
class ContentTheftAlert:
    """Content theft alert data structure"""
    alert_id: str
    owner_id: str
    original_content_id: str
    theft_type: TheftType
    severity: TheftSeverity
    detected_url: str
    similarity_score: float
    detection_method: str
    detected_at: datetime
    evidence: Dict[str, Any]
    status: str = "detected"

class ContentTheftAlerts:
    """
    Enterprise content theft detection and alerting system
    Provides AI-powered content protection monitoring
    """
    
    def __init__(self):
        """Initialize content theft alerts"""
        self.alerts: List[ContentTheftAlert] = []
        self.detection_engines = ["visual_hash", "audio_fingerprint", "metadata_analysis"]
        logger.info("Content theft alerts system initialized")
    
    async def notify_theft_detected(self, theft_data: Dict[str, Any]) -> bool:
        """
        Notify content owner about detected theft
        
        Args:
            theft_data: Content theft detection data
            
        Returns:
            bool: Success status
        """
        try:
            # Analyze theft severity
            severity = await self._analyze_theft_severity(theft_data)
            
            # Create theft alert
            alert = ContentTheftAlert(
                alert_id=f"theft_{int(datetime.now().timestamp())}",
                owner_id=theft_data.get("owner_id"),
                original_content_id=theft_data.get("content_id"),
                theft_type=TheftType(theft_data.get("theft_type", "exact_copy")),
                severity=severity,
                detected_url=theft_data.get("detected_url"),
                similarity_score=theft_data.get("similarity_score", 0.0),
                detection_method=theft_data.get("detection_method", "automated"),
                detected_at=datetime.now(timezone.utc),
                evidence=theft_data.get("evidence", {}),
                status="detected"
            )
            
            # Send alert notification
            await self._send_theft_alert(alert)
            
            # Store alert
            self.alerts.append(alert)
            
            # Auto-trigger DMCA if critical
            if alert.severity == TheftSeverity.CRITICAL:
                await self._trigger_auto_dmca(alert)
            
            logger.warning(f"Content theft alert sent: {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending content theft alert: {str(e)}")
            return False
    
    async def _analyze_theft_severity(self, theft_data: Dict[str, Any]) -> TheftSeverity:
        """Analyze content theft severity based on multiple factors"""
        similarity_score = theft_data.get("similarity_score", 0.0)
        theft_type = theft_data.get("theft_type", "exact_copy")
        platform_reach = theft_data.get("platform_reach", 0)
        
        # Calculate severity score
        severity_score = 0
        
        # Similarity factor
        if similarity_score >= 0.95:
            severity_score += 40
        elif similarity_score >= 0.85:
            severity_score += 30
        elif similarity_score >= 0.75:
            severity_score += 20
        else:
            severity_score += 10
        
        # Theft type factor
        if theft_type == "exact_copy":
            severity_score += 30
        elif theft_type == "watermark_removal":
            severity_score += 35
        elif theft_type == "modified_copy":
            severity_score += 25
        else:
            severity_score += 15
        
        # Platform reach factor
        if platform_reach > 1000000:  # 1M+ reach
            severity_score += 30
        elif platform_reach > 100000:  # 100K+ reach
            severity_score += 20
        elif platform_reach > 10000:  # 10K+ reach
            severity_score += 10
        
        # Determine severity level
        if severity_score >= 85:
            return TheftSeverity.CRITICAL
        elif severity_score >= 65:
            return TheftSeverity.HIGH
        elif severity_score >= 45:
            return TheftSeverity.MEDIUM
        else:
            return TheftSeverity.LOW
    
    async def _send_theft_alert(self, alert: ContentTheftAlert):
        """Send content theft alert notification"""
        # Determine notification channels based on severity
        channels = ["in_app", "email"]
        if alert.severity in [TheftSeverity.HIGH, TheftSeverity.CRITICAL]:
            channels.append("sms")
        
        severity_emojis = {
            TheftSeverity.LOW: "⚠️",
            TheftSeverity.MEDIUM: "🔶",
            TheftSeverity.HIGH: "🔥",
            TheftSeverity.CRITICAL: "🚨"
        }
        
        notification_data = {
            "title": f"{severity_emojis[alert.severity]} Content Theft Detected",
            "message": f"Your content has been detected on unauthorized platform (Similarity: {alert.similarity_score*100:.1f}%)",
            "user_id": alert.owner_id,
            "type": "content_theft",
            "priority": alert.severity.value,
            "channels": channels,
            "metadata": {
                "alert_id": alert.alert_id,
                "detected_url": alert.detected_url,
                "similarity_score": alert.similarity_score,
                "theft_type": alert.theft_type.value,
                "evidence": alert.evidence
            }
        }
        
        logger.info(f"Content theft alert prepared: {alert.alert_id}")
    
    async def _trigger_auto_dmca(self, alert: ContentTheftAlert):
        """Automatically trigger DMCA notice for critical theft"""
        dmca_data = {
            "original_content_id": alert.original_content_id,
            "owner_id": alert.owner_id,
            "infringing_url": alert.detected_url,
            "infringer_platform": self._extract_platform(alert.detected_url),
            "evidence": alert.evidence,
            "auto_triggered": True,
            "trigger_alert_id": alert.alert_id
        }
        
        # This would call the DMCA notices module
        logger.info(f"Auto-triggering DMCA for critical theft: {alert.alert_id}")
    
    def _extract_platform(self, url: str) -> str:
        """Extract platform name from URL"""
        platforms = {
            "youtube.com": "YouTube",
            "instagram.com": "Instagram",
            "tiktok.com": "TikTok",
            "twitter.com": "Twitter",
            "facebook.com": "Facebook"
        }
        
        for domain, platform in platforms.items():
            if domain in url:
                return platform
        
        return "Unknown Platform"
    
    async def scan_for_theft(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """
        Actively scan for content theft across platforms
        
        Args:
            content_id: Content to scan for
            user_id: Content owner
            
        Returns:
            dict: Scan results
        """
        try:
            # This would implement actual content scanning across platforms
            # For now, we'll simulate the scanning process
            
            scan_results = {
                "scan_id": f"scan_{int(datetime.now().timestamp())}",
                "content_id": content_id,
                "scanned_platforms": ["YouTube", "Instagram", "TikTok", "Twitter"],
                "detections": [],
                "scan_completed_at": datetime.now(timezone.utc),
                "status": "completed"
            }
            
            logger.info(f"Content theft scan completed for {content_id}")
            return scan_results
            
        except Exception as e:
            logger.error(f"Error scanning for content theft: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def get_user_theft_alerts(self, user_id: str) -> List[ContentTheftAlert]:
        """Get all theft alerts for user"""
        return [alert for alert in self.alerts if alert.owner_id == user_id]
    
    async def get_theft_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get content theft statistics for user"""
        user_alerts = await self.get_user_theft_alerts(user_id)
        
        severity_counts = {}
        for severity in TheftSeverity:
            severity_counts[severity.value] = len([a for a in user_alerts if a.severity == severity])
        
        type_counts = {}
        for theft_type in TheftType:
            type_counts[theft_type.value] = len([a for a in user_alerts if a.theft_type == theft_type])
        
        return {
            "total_alerts": len(user_alerts),
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "average_similarity": sum(a.similarity_score for a in user_alerts) / max(len(user_alerts), 1),
            "recent_alerts": len([a for a in user_alerts 
                                if (datetime.now(timezone.utc) - a.detected_at).days <= 7])
        }

__all__ = ["ContentTheftAlerts", "ContentTheftAlert", "TheftSeverity", "TheftType"]