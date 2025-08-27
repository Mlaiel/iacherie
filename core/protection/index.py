"""
Content Protection System - Main Index

This file provides a centralized access point to all protection system components
and serves as the main entry point for the content protection module.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Import all protection components
from .protection_manager import ProtectionManager, ProtectionConfiguration, ProtectionLevel
from .fingerprint_engine import FingerprintEngine
from .content_monitor import ContentMonitor
from .violation_detector import ViolationDetector
from .revenue_tracker import RevenueTracker
from .platform_crawlers import CrawlerManager
from .legal_automation import LegalAutomation
from .analytics_engine import ProtectionAnalytics
from .notification_system import NotificationManager
from .alert_manager import AlertManager
from .dmca_handler import DMCAHandler
from .evidence_collector import EvidenceCollector
from .verification_service import VerificationService

# Internal imports
from ...utils.logging import get_logger
from ...config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ContentProtectionSystem:
    """
    Unified Content Protection System
    
    This is the main orchestrator that coordinates all protection components
    and provides a simplified interface for content protection operations.
    """
    
    def __init__(self):
        """Initialize the complete protection system"""
        # Core components
        self.fingerprint_engine = FingerprintEngine()
        self.protection_manager = ProtectionManager()
        self.content_monitor = ContentMonitor()
        self.violation_detector = ViolationDetector()
        self.verification_service = VerificationService()
        
        # Advanced components
        self.revenue_tracker = RevenueTracker()
        self.crawler_manager = CrawlerManager()
        self.legal_automation = LegalAutomation()
        self.analytics_engine = ProtectionAnalytics()
        self.notification_manager = NotificationManager()
        
        # Support components
        self.alert_manager = AlertManager()
        self.dmca_handler = DMCAHandler()
        self.evidence_collector = EvidenceCollector()
        
        logger.info("Content Protection System initialized with all components")
    
    async def protect_content(self, user_id: str, content_path: str, 
                            protection_config: Optional[ProtectionConfiguration] = None) -> Dict[str, Any]:
        """
        Complete content protection workflow
        
        Args:
            user_id: User identifier
            content_path: Path to content file
            protection_config: Protection configuration (optional)
            
        Returns:
            Protection result with fingerprint and monitoring setup
        """
        try:
            logger.info(f"Starting content protection for user {user_id}: {content_path}")
            
            # Step 1: Create fingerprint
            fingerprint_result = await self.fingerprint_engine.create_fingerprint(content_path)
            if not fingerprint_result:
                return {"error": "Failed to create content fingerprint"}
            
            # Step 2: Set up protection
            protection_result = await self.protection_manager.start_protection(
                user_id=user_id,
                content_fingerprint=fingerprint_result,
                config=protection_config
            )
            
            # Step 3: Start monitoring
            monitoring_result = await self.content_monitor.start_monitoring(
                fingerprint_result.fingerprint_hash,
                protection_config
            )
            
            # Step 4: Initialize crawlers if configured
            if protection_config and protection_config.monitoring_platforms:
                await self.crawler_manager.start_monitoring_all([fingerprint_result])
            
            result = {
                "success": True,
                "content_id": fingerprint_result.content_id,
                "fingerprint_hash": fingerprint_result.fingerprint_hash,
                "protection_id": protection_result.get("protection_id"),
                "monitoring_active": monitoring_result.get("active", False),
                "protected_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Content protection completed for {content_path}")
            return result
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            return {"error": str(e)}
    
    async def detect_violations(self, user_id: str, content_id: str) -> List[Dict[str, Any]]:
        """
        Detect violations for protected content
        
        Args:
            user_id: User identifier
            content_id: Protected content identifier
            
        Returns:
            List of detected violations
        """
        try:
            logger.info(f"Detecting violations for content {content_id}")
            
            # Get content fingerprint
            fingerprint = await self.fingerprint_engine.get_fingerprint(content_id)
            if not fingerprint:
                return []
            
            # Run violation detection
            violations = await self.violation_detector.detect_violations(fingerprint)
            
            # Send alerts for high-priority violations
            for violation in violations:
                if violation.get('similarity_score', 0) > 0.8:
                    await self.notification_manager.send_violation_alert(violation, user_id)
            
            logger.info(f"Found {len(violations)} violations for content {content_id}")
            return violations
            
        except Exception as e:
            logger.error(f"Violation detection failed: {e}")
            return []
    
    async def process_takedown_request(self, user_id: str, violation_id: str) -> Dict[str, Any]:
        """
        Process DMCA takedown request for a violation
        
        Args:
            user_id: User identifier
            violation_id: Violation identifier
            
        Returns:
            Takedown processing result
        """
        try:
            logger.info(f"Processing takedown request for violation {violation_id}")
            
            # Get violation details
            violation = await self.violation_detector.get_violation_details(violation_id)
            if not violation:
                return {"error": "Violation not found"}
            
            # Generate DMCA takedown notice
            copyright_info = await self._get_user_copyright_info(user_id)
            violation_details = await self._convert_violation_to_legal_format(violation)
            
            dmca_result = await self.legal_automation.generate_dmca_takedown(
                copyright_info, violation_details
            )
            
            if not dmca_result:
                return {"error": "Failed to generate DMCA notice"}
            
            # Submit takedown request
            platform = violation.get('platform', '')
            submission_result = await self.legal_automation.submit_dmca_takedown(
                dmca_result, platform
            )
            
            # Send notification about takedown status
            await self.notification_manager.send_takedown_update(
                violation, user_id, submission_result
            )
            
            result = {
                "success": submission_result,
                "takedown_id": dmca_result.get('document_id'),
                "submitted_at": datetime.utcnow().isoformat(),
                "platform": platform
            }
            
            logger.info(f"Takedown request processed for violation {violation_id}")
            return result
            
        except Exception as e:
            logger.error(f"Takedown request processing failed: {e}")
            return {"error": str(e)}
    
    async def generate_protection_report(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate comprehensive protection analytics report
        
        Args:
            user_id: User identifier
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Comprehensive protection report
        """
        try:
            logger.info(f"Generating protection report for user {user_id}")
            
            # Generate comprehensive report
            report = await self.analytics_engine.generate_comprehensive_report(
                user_id, start_date, end_date
            )
            
            # Add revenue data
            revenue_report = await self.revenue_tracker.generate_revenue_report(
                user_id, start_date.date(), end_date.date()
            )
            
            # Combine reports
            combined_report = {
                "protection_analytics": report.__dict__,
                "revenue_analytics": revenue_report,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Protection report generated for user {user_id}")
            return combined_report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e)}
    
    async def get_real_time_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get real-time dashboard data
        
        Args:
            user_id: User identifier
            
        Returns:
            Real-time dashboard data
        """
        try:
            # Get real-time analytics
            dashboard_data = await self.analytics_engine.generate_real_time_dashboard_data(user_id)
            
            # Add protection status
            protection_status = await self.protection_manager.get_protection_status(user_id)
            dashboard_data['protection_status'] = protection_status
            
            # Add recent revenue data
            recent_revenue = await self.revenue_tracker.calculate_licensing_fees(
                user_id, {"recent_activity": True}
            )
            dashboard_data['recent_revenue'] = {
                "total_licensing_fees": sum(t.fee_amount for t in recent_revenue),
                "transactions_count": len(recent_revenue)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            return {"error": str(e)}
    
    async def setup_user_protection(self, user_id: str, 
                                  protection_level: ProtectionLevel = ProtectionLevel.STANDARD) -> Dict[str, Any]:
        """
        Set up complete protection system for a user
        
        Args:
            user_id: User identifier
            protection_level: Level of protection to enable
            
        Returns:
            Setup result
        """
        try:
            logger.info(f"Setting up protection for user {user_id} at level {protection_level.value}")
            
            # Create protection configuration
            config = await self._create_protection_config(user_id, protection_level)
            
            # Initialize user protection
            setup_result = await self.protection_manager.initialize_user_protection(user_id, config)
            
            # Set up crawlers based on protection level
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                await self._setup_crawlers_for_user(user_id, config)
            
            # Send welcome notification
            await self.notification_manager.send_notification(
                notification_type="protection_setup_complete",
                user_id=user_id,
                data={"protection_level": protection_level.value}
            )
            
            result = {
                "success": True,
                "protection_level": protection_level.value,
                "setup_completed_at": datetime.utcnow().isoformat(),
                "features_enabled": await self._get_enabled_features(protection_level)
            }
            
            logger.info(f"Protection setup completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Protection setup failed: {e}")
            return {"error": str(e)}
    
    async def cleanup_user_data(self, user_id: str) -> bool:
        """
        Clean up all user protection data (GDPR compliance)
        
        Args:
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Cleaning up protection data for user {user_id}")
            
            # Stop all monitoring
            await self.content_monitor.stop_all_monitoring(user_id)
            
            # Clean up fingerprints
            await self.fingerprint_engine.delete_user_fingerprints(user_id)
            
            # Clean up crawler data
            await self.crawler_manager.cleanup_user_data(user_id)
            
            # Clean up analytics data
            await self.analytics_engine.cleanup_user_data(user_id)
            
            # Clean up notifications
            await self.notification_manager.cleanup_user_data(user_id)
            
            logger.info(f"User data cleanup completed for {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"User data cleanup failed: {e}")
            return False
    
    # Helper methods
    async def _get_user_copyright_info(self, user_id: str):
        """Get user copyright information for legal documents"""
        # This would fetch from user profile/database
        pass
    
    async def _convert_violation_to_legal_format(self, violation: Dict[str, Any]):
        """Convert violation data to legal document format"""
        # This would convert the violation data structure
        pass
    
    async def _create_protection_config(self, user_id: str, protection_level: ProtectionLevel) -> ProtectionConfiguration:
        """Create protection configuration based on user and level"""
        # This would create appropriate configuration
        pass
    
    async def _setup_crawlers_for_user(self, user_id: str, config: ProtectionConfiguration):
        """Set up crawlers for user based on configuration"""
        # This would configure and start crawlers
        pass
    
    async def _get_enabled_features(self, protection_level: ProtectionLevel) -> List[str]:
        """Get list of enabled features for protection level"""
        features_map = {
            ProtectionLevel.BASIC: ["fingerprinting", "basic_monitoring"],
            ProtectionLevel.STANDARD: ["fingerprinting", "monitoring", "alerts"],
            ProtectionLevel.PREMIUM: ["fingerprinting", "monitoring", "alerts", "crawlers", "analytics"],
            ProtectionLevel.ENTERPRISE: ["fingerprinting", "monitoring", "alerts", "crawlers", "analytics", "legal_automation", "revenue_tracking"]
        }
        return features_map.get(protection_level, [])


# Module-level functions for convenience
async def protect_content(user_id: str, content_path: str, 
                         protection_level: ProtectionLevel = ProtectionLevel.STANDARD) -> Dict[str, Any]:
    """Convenience function to protect content"""
    system = ContentProtectionSystem()
    config = ProtectionConfiguration(protection_level=protection_level)
    return await system.protect_content(user_id, content_path, config)


async def detect_violations(user_id: str, content_id: str) -> List[Dict[str, Any]]:
    """Convenience function to detect violations"""
    system = ContentProtectionSystem()
    return await system.detect_violations(user_id, content_id)


async def generate_report(user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Convenience function to generate protection report"""
    system = ContentProtectionSystem()
    return await system.generate_protection_report(user_id, start_date, end_date)


# Export main system class
__all__ = ['ContentProtectionSystem', 'protect_content', 'detect_violations', 'generate_report']
