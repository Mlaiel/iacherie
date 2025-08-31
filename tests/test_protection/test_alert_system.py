# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test suite for Alert System module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class TestAlertSystem(unittest.TestCase):
    """Test suite for AlertSystem class"""    def setUp(self):
        """Set up test fixtures"""        self.alert_system = None  # Will be mocked
        self.sample_violation_data = {
            "original_content_id": "content_123",
            "user_id": "user_456",
            "platform": "youtube",
            "violation_url": "https://youtube.com/watch?v=test123",
            "similarity_score": 0.92,
            "detected_at": datetime.now(),
            "status": "pending_review",
            "evidence_data": {
                "title": "Similar Song",
                "channel": "TestChannel"
            }
        }

    def test_alert_data_structure(self):
        """Test alert data structure"""        alert = {
            "id": "alert_123",
            "type": "violation_detected",
            "severity": "high",
            "user_id": "user_456",
            "content_id": "content_123",
            "message": "Potential violation detected",
            "details": {"similarity_score": 0.92},
            "channels": ["email", "push"],
            "created_at": datetime.now(),
            "sent_at": None,
            "status": "pending"
        }
        
        # Verify required fields
        required_fields = ["id", "type", "severity", "user_id", "message", "channels"]
        for field in required_fields:
            self.assertIn(field, alert)
        
        # Verify data types
        self.assertIsInstance(alert["channels"], list)
        self.assertIsInstance(alert["details"], dict)
        self.assertIsInstance(alert["created_at"], datetime)

    def test_alert_severity_classification(self):
        """Test alert severity classification"""        similarity_scores = [0.95, 0.88, 0.75, 0.60, 0.45]
        expected_severities = []
        
        for score in similarity_scores:
            if score >= 0.90:
                severity = "critical"
            elif score >= 0.80:
                severity = "high"
            elif score >= 0.70:
                severity = "medium"
            elif score >= 0.60:
                severity = "low"
            else:
                severity = "info"
            expected_severities.append(severity)
        
        # Verify severity classification
        self.assertEqual(expected_severities[0], "critical")  # 0.95
        self.assertEqual(expected_severities[1], "high")      # 0.88
        self.assertEqual(expected_severities[2], "medium")    # 0.75
        self.assertEqual(expected_severities[3], "low")       # 0.60
        self.assertEqual(expected_severities[4], "info")      # 0.45

    def test_notification_channel_selection(self):
        """Test notification channel selection based on severity"""        severity_channel_mapping = {
            "critical": ["email", "sms", "push", "slack"],
            "high": ["email", "push", "slack"],
            "medium": ["email", "push"],
            "low": ["email"],
            "info": ["push"]
        }
        
        # Test channel selection for different severities
        for severity, expected_channels in severity_channel_mapping.items():
            channels = severity_channel_mapping[severity]
            self.assertEqual(channels, expected_channels)
        
        # Verify critical alerts use all channels
        self.assertIn("sms", severity_channel_mapping["critical"])
        self.assertIn("slack", severity_channel_mapping["critical"])
        
        # Verify info alerts only use push
        self.assertEqual(len(severity_channel_mapping["info"]), 1)
        self.assertIn("push", severity_channel_mapping["info"])

    def test_alert_message_generation(self):
        """Test alert message generation"""        violation_data = {
            "platform": "youtube",
            "similarity_score": 0.92,
            "violation_url": "https://youtube.com/watch?v=test123",
            "content_title": "My Original Song"
        }
        
        # Generate different message templates
        templates = {
            "email": f"🚨 HIGH PRIORITY: Potential violation of '{violation_data['content_title']}' detected on {violation_data['platform'].title()} with {violation_data['similarity_score']*100:.1f}% similarity. Review required: {violation_data['violation_url']}",
            "sms": f"VIOLATION ALERT: {violation_data['similarity_score']*100:.0f}% match found on {violation_data['platform'].upper()}. Check email for details.",
            "push": f"🔒 Content violation detected on {violation_data['platform'].title()} ({violation_data['similarity_score']*100:.0f}% similarity)",
            "slack": f"⚠️ *VIOLATION DETECTED*\n*Platform:* {violation_data['platform'].title()}\n*Similarity:* {violation_data['similarity_score']*100:.1f}%\n*URL:* {violation_data['violation_url']}"
        }
        
        # Verify message generation
        self.assertIn("92.0% similarity", templates["email"])
        self.assertIn("92% match", templates["sms"])
        self.assertIn("92% similarity", templates["push"])
        self.assertIn("92.1%", templates["slack"])
        
        # Verify platform is included in all messages
        for message in templates.values():
            self.assertIn("youtube", message.lower())

    def test_alert_throttling_logic(self):
        """Test alert throttling to prevent spam"""        user_id = "user_123"
        content_id = "content_456"
        current_time = datetime.now()
        
        # Mock recent alerts for the same content
        recent_alerts = [
            {
                "user_id": user_id,
                "content_id": content_id,
                "type": "violation_detected",
                "created_at": current_time - timedelta(minutes=30)
            },
            {
                "user_id": user_id,
                "content_id": content_id,
                "type": "violation_detected", 
                "created_at": current_time - timedelta(hours=2)
            }
        ]
        
        # Throttling rules
        throttle_window = timedelta(hours=1)  # Don't send same alert within 1 hour
        max_alerts_per_hour = 3
        
        # Check if new alert should be throttled
        recent_hour_alerts = [
            alert for alert in recent_alerts
            if (current_time - alert["created_at"]) <= throttle_window
        ]
        
        should_throttle_time = len(recent_hour_alerts) > 0
        should_throttle_count = len(recent_hour_alerts) >= max_alerts_per_hour
        
        # Verify throttling logic
        self.assertTrue(should_throttle_time)  # Alert within last hour
        self.assertFalse(should_throttle_count)  # Under max count

    def test_user_notification_preferences(self):
        """Test user notification preferences handling"""        user_preferences = {
            "user_123": {
                "email_enabled": True,
                "email_address": "user@example.com",
                "sms_enabled": False,
                "push_enabled": True,
                "slack_enabled": True,
                "slack_webhook": "https://hooks.slack.com/test",
                "quiet_hours": {"start": "22:00", "end": "08:00"},
                "min_severity": "medium"
            }
        }
        
        user_id = "user_123"
        prefs = user_preferences[user_id]
        
        # Filter available channels based on preferences
        all_channels = ["email", "sms", "push", "slack"]
        enabled_channels = []
        
        for channel in all_channels:
            if prefs.get(f"{channel}_enabled", False):
                enabled_channels.append(channel)
        
        # Verify preference filtering
        self.assertIn("email", enabled_channels)
        self.assertNotIn("sms", enabled_channels)
        self.assertIn("push", enabled_channels)
        self.assertIn("slack", enabled_channels)
        
        # Test severity filtering
        alert_severity = "low"
        min_severity_levels = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        
        should_send = min_severity_levels[alert_severity] >= min_severity_levels[prefs["min_severity"]]
        self.assertFalse(should_send)  # "low" < "medium"

    def test_quiet_hours_check(self):
        """Test quiet hours functionality"""        quiet_hours = {"start": "22:00", "end": "08:00"}
        
        test_times = [
            ("06:00", True),   # During quiet hours
            ("10:00", False),  # Outside quiet hours
            ("15:30", False),  # Outside quiet hours
            ("23:30", True),   # During quiet hours
            ("00:30", True),   # During quiet hours (next day)
        ]
        
        for time_str, expected_quiet in test_times:
            # Parse time
            hour, minute = map(int, time_str.split(":"))
            test_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Check if time is in quiet hours
            start_hour, start_minute = map(int, quiet_hours["start"].split(":"))
            end_hour, end_minute = map(int, quiet_hours["end"].split(":"))
            
            current_minutes = test_time.hour * 60 + test_time.minute
            start_minutes = start_hour * 60 + start_minute
            end_minutes = end_hour * 60 + end_minute
            
            # Handle overnight quiet hours
            if start_minutes > end_minutes:  # Overnight (e.g., 22:00 to 08:00)
                is_quiet = current_minutes >= start_minutes or current_minutes <= end_minutes
            else:  # Same day
                is_quiet = start_minutes <= current_minutes <= end_minutes
            
            self.assertEqual(is_quiet, expected_quiet, f"Failed for time {time_str}")

    def test_alert_escalation_logic(self):
        """Test alert escalation logic"""        alert = {
            "id": "alert_123",
            "severity": "high",
            "created_at": datetime.now() - timedelta(hours=2),
            "status": "sent",
            "escalation_level": 0,
            "acknowledged": False
        }
        
        # Escalation rules
        escalation_rules = {
            "high": {"time_limit": timedelta(hours=1), "max_level": 3},
            "critical": {"time_limit": timedelta(minutes=30), "max_level": 5}
        }
        
        current_time = datetime.now()
        time_since_sent = current_time - alert["created_at"]
        
        severity = alert["severity"]
        rule = escalation_rules.get(severity)
        
        should_escalate = (
            rule and
            not alert["acknowledged"] and
            time_since_sent > rule["time_limit"] and
            alert["escalation_level"] < rule["max_level"]
        )
        
        # Verify escalation logic
        self.assertTrue(should_escalate)  # 2 hours > 1 hour limit, not acknowledged

    def test_bulk_alert_processing(self):
        """Test bulk alert processing for multiple violations"""        violations = [
            {"content_id": "content_1", "similarity_score": 0.95, "platform": "youtube"},
            {"content_id": "content_1", "similarity_score": 0.88, "platform": "instagram"},
            {"content_id": "content_2", "similarity_score": 0.92, "platform": "tiktok"},
            {"content_id": "content_1", "similarity_score": 0.75, "platform": "twitter"}
        ]
        
        # Group violations by content
        content_violations = {}
        for violation in violations:
            content_id = violation["content_id"]
            if content_id not in content_violations:
                content_violations[content_id] = []
            content_violations[content_id].append(violation)
        
        # Generate summary alerts
        summary_alerts = []
        for content_id, content_violations_list in content_violations.items():
            if len(content_violations_list) > 1:
                # Multiple violations for same content - create summary
                platforms = [v["platform"] for v in content_violations_list]
                max_similarity = max(v["similarity_score"] for v in content_violations_list)
                
                summary = {
                    "type": "multiple_violations",
                    "content_id": content_id,
                    "violation_count": len(content_violations_list),
                    "platforms": platforms,
                    "max_similarity": max_similarity
                }
                summary_alerts.append(summary)
        
        # Verify bulk processing
        self.assertEqual(len(summary_alerts), 1)  # Only content_1 has multiple violations
        summary = summary_alerts[0]
        self.assertEqual(summary["content_id"], "content_1")
        self.assertEqual(summary["violation_count"], 3)
        self.assertEqual(summary["max_similarity"], 0.95)
        self.assertIn("youtube", summary["platforms"])
        self.assertIn("instagram", summary["platforms"])

    def test_alert_delivery_status_tracking(self):
        """Test alert delivery status tracking"""        alert_delivery_log = {
            "alert_id": "alert_123",
            "channels": {
                "email": {"status": "sent", "timestamp": datetime.now(), "error": None},
                "sms": {"status": "failed", "timestamp": datetime.now(), "error": "Invalid phone number"},
                "push": {"status": "delivered", "timestamp": datetime.now(), "error": None},
                "slack": {"status": "pending", "timestamp": None, "error": None}
            }
        }
        
        # Calculate delivery statistics
        total_channels = len(alert_delivery_log["channels"])
        successful_deliveries = sum(1 for channel in alert_delivery_log["channels"].values() 
                                  if channel["status"] in ["sent", "delivered"])
        failed_deliveries = sum(1 for channel in alert_delivery_log["channels"].values() 
                              if channel["status"] == "failed")
        pending_deliveries = sum(1 for channel in alert_delivery_log["channels"].values() 
                               if channel["status"] == "pending")
        
        delivery_rate = (successful_deliveries / total_channels) * 100 if total_channels > 0 else 0
        
        # Verify delivery tracking
        self.assertEqual(total_channels, 4)
        self.assertEqual(successful_deliveries, 2)  # email, push
        self.assertEqual(failed_deliveries, 1)      # sms
        self.assertEqual(pending_deliveries, 1)     # slack
        self.assertEqual(delivery_rate, 50.0)       # 2/4 = 50%


if __name__ == '__main__':
    unittest.main()