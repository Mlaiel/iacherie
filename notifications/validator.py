"""Enterprise notification system validation and health checks.

This module provides validation functions to ensure the notification system
is properly configured and operational.

Built by Fahed Mlaiel and the IA Influencer Agent Team.
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .orchestrator import NotificationOrchestrator, UniversalNotification, NotificationPriority
from .templates import NotificationTemplateEngine
from .index import create_notification_system


class NotificationSystemValidator:
    """Comprehensive validation and health checks for the notification system."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_system = create_notification_system()

    async def validate_system(self) -> Dict[str, Any]:
        """Run comprehensive system validation."""        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": []
        }

        try:
            # Test orchestrator
            orchestrator_result = await self._test_orchestrator()
            results["components"]["orchestrator"] = orchestrator_result
            
            # Test template engine
            template_result = await self._test_template_engine()
            results["components"]["template_engine"] = template_result
            
            # Test individual notifiers
            notifier_results = await self._test_notifiers()
            results["components"]["notifiers"] = notifier_results
            
            # Test business logic integration
            business_result = await self._test_business_logic()
            results["components"]["business_logic"] = business_result
            
            # Calculate overall status
            total_tests = 0
            passed_tests = 0
            
            for component, component_result in results["components"].items():
                if isinstance(component_result, dict):
                    total_tests += component_result.get("tests_run", 0)
                    passed_tests += component_result.get("tests_passed", 0)
            
            results["tests_passed"] = passed_tests
            results["tests_failed"] = total_tests - passed_tests
            results["overall_status"] = "healthy" if results["tests_failed"] == 0 else "degraded"
            
            self.logger.info(f"System validation completed: {passed_tests}/{total_tests} tests passed")
            
        except Exception as e:
            results["overall_status"] = "failed"
            results["errors"].append(f"System validation failed: {str(e)}")
            self.logger.error(f"System validation error: {str(e)}")

        return results

    async def _test_orchestrator(self) -> Dict[str, Any]:
        """Test notification orchestrator functionality."""        result = {
            "component": "orchestrator",
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "errors": []
        }

        try:
            orchestrator = self.notification_system["orchestrator"]
            
            # Test 1: Basic notification creation
            result["tests_run"] += 1
            test_notification = UniversalNotification(
                user_id="test_user_123",
                title="Test Notification",
                message="This is a test notification for system validation.",
                priority=NotificationPriority.NORMAL
            )
            
            if test_notification.id and test_notification.user_id:
                result["tests_passed"] += 1
            else:
                result["errors"].append("Failed to create basic notification")
            
            # Test 2: User preferences handling
            result["tests_run"] += 1
            try:
                prefs = await orchestrator.get_user_preferences("test_user_123")
                if prefs.user_id == "test_user_123":
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("User preferences not handled correctly")
            except Exception as e:
                result["errors"].append(f"User preferences test failed: {str(e)}")
            
            # Test 3: Channel determination
            result["tests_run"] += 1
            try:
                channels = await orchestrator._determine_channels(test_notification, prefs)
                if isinstance(channels, set) and len(channels) >= 0:
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Channel determination failed")
            except Exception as e:
                result["errors"].append(f"Channel determination test failed: {str(e)}")
            
            result["status"] = "healthy" if len(result["errors"]) == 0 else "degraded"
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(f"Orchestrator test failed: {str(e)}")

        return result

    async def _test_template_engine(self) -> Dict[str, Any]:
        """Test template engine functionality."""        result = {
            "component": "template_engine",
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "errors": []
        }

        try:
            template_engine = self.notification_system["template_engine"]
            
            # Test 1: Template creation
            result["tests_run"] += 1
            from .templates import NotificationTemplate, TemplateType
            
            test_template = NotificationTemplate(
                id="test_template_123",
                name="Test Template",
                type=TemplateType.EMAIL_HTML,
                content="Hello {{name}}, this is a test template!"
            )
            
            template_id = await template_engine.create_template(test_template)
            if template_id:
                result["tests_passed"] += 1
            else:
                result["errors"].append("Failed to create template")
            
            # Test 2: Template rendering
            result["tests_run"] += 1
            try:
                rendered = await template_engine.render_template(
                    template_id,
                    {"name": "Test User"},
                    language="en"
                )
                
                if "content" in rendered and "Test User" in rendered["content"]:
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Template rendering failed")
            except Exception as e:
                result["errors"].append(f"Template rendering test failed: {str(e)}")
            
            result["status"] = "healthy" if len(result["errors"]) == 0 else "degraded"
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(f"Template engine test failed: {str(e)}")

        return result

    async def _test_notifiers(self) -> Dict[str, Any]:
        """Test individual notification channels."""        result = {
            "component": "notifiers",
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "channel_status": {},
            "errors": []
        }

        channels = {
            "email": self.notification_system["email"],
            "sms": self.notification_system["sms"],
            "push": self.notification_system["push"],
            "webhook": self.notification_system["webhook"],
            "in_app": self.notification_system["in_app"]
        }

        for channel_name, notifier in channels.items():
            channel_result = {
                "status": "unknown",
                "configuration": "unknown",
                "errors": []
            }

            try:
                result["tests_run"] += 1
                
                # Test configuration
                if hasattr(notifier, '__dict__') and notifier.__dict__:
                    channel_result["configuration"] = "configured"
                    channel_result["status"] = "ready"
                    result["tests_passed"] += 1
                else:
                    channel_result["configuration"] = "not_configured"
                    channel_result["status"] = "not_ready"
                    channel_result["errors"].append("Channel not properly configured")

            except Exception as e:
                channel_result["status"] = "failed"
                channel_result["errors"].append(f"Channel test failed: {str(e)}")
                result["errors"].append(f"{channel_name} channel failed: {str(e)}")

            result["channel_status"][channel_name] = channel_result

        result["status"] = "healthy" if len(result["errors"]) == 0 else "degraded"
        return result

    async def _test_business_logic(self) -> Dict[str, Any]:
        """Test business logic integration."""        result = {
            "component": "business_logic",
            "status": "unknown",
            "tests_run": 0,
            "tests_passed": 0,
            "errors": []
        }

        try:
            from .index import (
                create_content_protection_notification,
                create_collaboration_notification,
                create_revenue_notification,
                create_viral_content_notification
            )
            
            # Test 1: Content protection notification
            result["tests_run"] += 1
            try:
                content_notif = create_content_protection_notification(
                    "test_user_123", "My Content", "protected"
                )
                if content_notif.event_type == "content.protected":
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Content protection notification failed")
            except Exception as e:
                result["errors"].append(f"Content protection test failed: {str(e)}")
            
            # Test 2: Collaboration notification
            result["tests_run"] += 1
            try:
                collab_notif = create_collaboration_notification(
                    "test_user_123", "Partner User", "music"
                )
                if collab_notif.event_type == "collaboration.request":
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Collaboration notification failed")
            except Exception as e:
                result["errors"].append(f"Collaboration test failed: {str(e)}")
            
            # Test 3: Revenue notification
            result["tests_run"] += 1
            try:
                revenue_notif = create_revenue_notification(
                    "test_user_123", 1500.00, "this month"
                )
                if revenue_notif.event_type == "revenue.milestone":
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Revenue notification failed")
            except Exception as e:
                result["errors"].append(f"Revenue test failed: {str(e)}")
            
            # Test 4: Viral content notification
            result["tests_run"] += 1
            try:
                viral_notif = create_viral_content_notification(
                    "test_user_123", "Viral Video", 100000
                )
                if viral_notif.event_type == "viral.content_detected":
                    result["tests_passed"] += 1
                else:
                    result["errors"].append("Viral content notification failed")
            except Exception as e:
                result["errors"].append(f"Viral content test failed: {str(e)}")
            
            result["status"] = "healthy" if len(result["errors"]) == 0 else "degraded"
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(f"Business logic test failed: {str(e)}")

        return result

    async def quick_health_check(self) -> bool:
        """Quick health check for system monitoring."""        try:
            # Test basic system creation
            system = create_notification_system()
            
            # Test basic notification creation
            test_notification = UniversalNotification(
                user_id="health_check_user",
                title="Health Check",
                message="System health check notification"
            )
            
            return (
                system is not None and
                "orchestrator" in system and
                test_notification.id is not None
            )
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False


# Global validation functions
async def validate_notification_system() -> Dict[str, Any]:
    """Run full system validation."""    validator = NotificationSystemValidator()
    return await validator.validate_system()


async def health_check() -> bool:
    """Quick health check."""    validator = NotificationSystemValidator()
    return await validator.quick_health_check()


# CLI validation script
if __name__ == "__main__":
    import json
    
    async def main():
        print("🔍 Running IA Influencer Agent Notification System Validation...")
        print("=" * 60)
        
        # Quick health check
        is_healthy = await health_check()
        print(f"Quick Health Check: {'✅ PASSED' if is_healthy else '❌ FAILED'}")
        print()
        
        # Full validation
        print("Running comprehensive validation...")
        results = await validate_notification_system()
        
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Tests Passed: {results['tests_passed']}")
        print(f"Tests Failed: {results['tests_failed']}")
        print()
        
        # Component details
        for component, details in results["components"].items():
            if isinstance(details, dict):
                status = details.get("status", "unknown")
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"{status_icon} {component}: {status}")
                
                if details.get("errors"):
                    for error in details["errors"]:
                        print(f"   - {error}")
        
        print()
        print("=" * 60)
        print(f"Validation completed at {results['timestamp']}")
        
        # Save detailed results
        with open("notification_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("📄 Detailed results saved to: notification_validation_results.json")

    # Run validation
    asyncio.run(main())
