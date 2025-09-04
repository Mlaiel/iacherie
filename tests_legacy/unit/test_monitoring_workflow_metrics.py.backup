# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Unit tests for monitoring.workflow_metrics module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime
from monitoring.workflow_metrics import WorkflowMetrics, NotificationService


class TestWorkflowMetrics:
    """Test cases for WorkflowMetrics class"""
    def test_init(self):
        """Test WorkflowMetrics initialization"""
        metrics = WorkflowMetrics()
        assert metrics.metrics == {}

    @pytest.mark.asyncio
    async def test_setup_content_tracking_basic(self):
        """Test basic content tracking setup"""
        metrics = WorkflowMetrics()
        
        config = {
            "workflow_id": "wf_123",
            "content_id": "content_456"
        }
        
        await metrics.setup_content_tracking(config)
        
        assert "wf_123" in metrics.metrics
        tracking_config = metrics.metrics["wf_123"]
        assert tracking_config["workflow_id"] == "wf_123"
        assert tracking_config["content_id"] == "content_456"
        assert tracking_config["tracking_events"] == []
        assert "setup_time" in tracking_config

    @pytest.mark.asyncio
    async def test_setup_content_tracking_with_events(self):
        """Test content tracking setup with tracking events"""
        metrics = WorkflowMetrics()
        
        config = {
            "workflow_id": "wf_789",
            "content_id": "content_abc",
            "tracking_events": ["view", "share", "like"]
        }
        
        await metrics.setup_content_tracking(config)
        
        tracking_config = metrics.metrics["wf_789"]
        assert tracking_config["tracking_events"] == ["view", "share", "like"]

    @pytest.mark.asyncio
    async def test_setup_content_tracking_multiple_workflows(self):
        """Test setting up tracking for multiple workflows"""
        metrics = WorkflowMetrics()
        
        config1 = {"workflow_id": "wf_1", "content_id": "content_1"}
        config2 = {"workflow_id": "wf_2", "content_id": "content_2"}
        
        await metrics.setup_content_tracking(config1)
        await metrics.setup_content_tracking(config2)
        
        assert len(metrics.metrics) == 2
        assert "wf_1" in metrics.metrics
        assert "wf_2" in metrics.metrics

    @pytest.mark.asyncio
    async def test_setup_content_tracking_missing_fields(self):
        """Test content tracking setup with missing fields"""
        metrics = WorkflowMetrics()
        
        config = {"workflow_id": "wf_incomplete"}
        
        await metrics.setup_content_tracking(config)
        
        tracking_config = metrics.metrics["wf_incomplete"]
        assert tracking_config["workflow_id"] == "wf_incomplete"
        assert tracking_config["content_id"] is None
        assert tracking_config["tracking_events"] == []


class TestNotificationService:
    """Test cases for NotificationService class"""
    def test_init(self):
        """Test NotificationService initialization"""
        service = NotificationService()
        assert service.notifications == []

    @pytest.mark.asyncio
    async def test_send_notification_basic(self):
        """Test basic notification sending"""
        service = NotificationService()
        
        notification_data = {
            "workflow_id": "wf_123",
            "creator_id": "user_456",
            "title": "Test Notification",
            "message": "This is a test notification",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        result = await service.send_notification(notification_data)
        
        assert len(service.notifications) == 1
        assert result["id"] == "notif_0"
        assert result["workflow_id"] == "wf_123"
        assert result["creator_id"] == "user_456"
        assert result["title"] == "Test Notification"
        assert result["message"] == "This is a test notification"
        assert result["timestamp"] == "2025-01-01T12:00:00Z"
        assert result["sent"] is True

    @pytest.mark.asyncio
    async def test_send_notification_multiple(self):
        """Test sending multiple notifications"""
        service = NotificationService()
        
        notification1 = {
            "workflow_id": "wf_1",
            "creator_id": "user_1",
            "title": "First Notification",
            "message": "First message"
        }
        
        notification2 = {
            "workflow_id": "wf_2",
            "creator_id": "user_2",
            "title": "Second Notification",
            "message": "Second message"
        }
        
        result1 = await service.send_notification(notification1)
        result2 = await service.send_notification(notification2)
        
        assert len(service.notifications) == 2
        assert result1["id"] == "notif_0"
        assert result2["id"] == "notif_1"
        assert service.notifications[0]["title"] == "First Notification"
        assert service.notifications[1]["title"] == "Second Notification"

    @pytest.mark.asyncio
    async def test_send_notification_missing_fields(self):
        """Test sending notification with missing optional fields"""
        service = NotificationService()
        
        notification_data = {
            "workflow_id": "wf_minimal",
            "creator_id": "user_minimal"
        }
        
        result = await service.send_notification(notification_data)
        
        assert result["workflow_id"] == "wf_minimal"
        assert result["creator_id"] == "user_minimal"
        assert result["title"] is None
        assert result["message"] is None
        assert result["timestamp"] is None
        assert result["sent"] is True

    @pytest.mark.asyncio
    async def test_send_notification_empty_data(self):
        """Test sending notification with empty data"""
        service = NotificationService()
        
        notification_data = {}
        
        result = await service.send_notification(notification_data)
        
        assert result["workflow_id"] is None
        assert result["creator_id"] is None
        assert result["title"] is None
        assert result["message"] is None
        assert result["timestamp"] is None
        assert result["sent"] is True
        assert result["id"] == "notif_0"

    @pytest.mark.asyncio
    async def test_send_notification_incremental_ids(self):
        """Test that notification IDs increment correctly"""
        service = NotificationService()
        
        # Send 5 notifications
        for i in range(5):
            notification_data = {
                "workflow_id": f"wf_{i}",
                "creator_id": f"user_{i}",
                "title": f"Notification {i}"
            }
            result = await service.send_notification(notification_data)
            assert result["id"] == f"notif_{i}"
        
        assert len(service.notifications) == 5

    @pytest.mark.asyncio
    async def test_send_notification_concurrent(self):
        """Test sending notifications concurrently"""
        service = NotificationService()
        
        async def send_test_notification(index):
            notification_data = {
                "workflow_id": f"wf_{index}",
                "creator_id": f"user_{index}",
                "title": f"Concurrent Notification {index}"
            }
            return await service.send_notification(notification_data)
        
        # Send 3 notifications concurrently
        tasks = [send_test_notification(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        assert len(service.notifications) == 3
        assert len(results) == 3
        
        # Verify all notifications were sent
        for result in results:
            assert result["sent"] is True
            assert "notif_" in result["id"]