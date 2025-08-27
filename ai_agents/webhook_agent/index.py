#!/usr/bin/env python3
"""
Webhook Agent Index Module
Main entry point for the webhook agent system

This module provides the primary interface for webhook operations,
including registration, management, and execution of webhook handlers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.

Project Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Database Administrator  
- Security Expert & Microservices Architect
- Audio Processing Specialist & DevOps Engineer
- AI Prompt Engineer & Platform Integration Expert
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone

from .core.webhook_manager import WebhookManager
from .core.event_processor import WebhookEventProcessor
from .handlers.platform_handlers import PlatformWebhookHandlers
from .handlers.notification_handlers import NotificationWebhookHandlers
from .handlers.monitoring_handlers import MonitoringWebhookHandlers
from .handlers.payment_handlers import PaymentWebhookHandlers
from .security.webhook_security import WebhookSecurityManager
from .monitoring.webhook_monitor import WebhookMonitor
from .utils.webhook_utils import WebhookUtils
from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class WebhookAgentIndex(BaseAgent):
    """
    Main webhook agent index class providing unified access to all webhook operations.
    
    This class acts as the primary interface for webhook management, routing,
    and processing within the IA Influencer platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the webhook agent index.
        
        Args:
            config: Configuration dictionary for webhook operations
        """
        super().__init__(agent_type="webhook", config=config)
        
        # Initialize core components
        self.webhook_manager = WebhookManager(config)
        self.event_processor = WebhookEventProcessor(config)
        self.security_manager = WebhookSecurityManager(config)
        self.monitor = WebhookMonitor(config)
        self.utils = WebhookUtils()
        
        # Initialize handlers
        self.platform_handlers = PlatformWebhookHandlers(config)
        self.notification_handlers = NotificationWebhookHandlers(config)
        self.monitoring_handlers = MonitoringWebhookHandlers(config)
        self.payment_handlers = PaymentWebhookHandlers(config)
        
        # Webhook registry
        self.webhook_registry: Dict[str, Callable] = {}
        self.active_webhooks: Dict[str, Dict[str, Any]] = {}
        
        # Initialize webhook routes
        self._initialize_webhook_routes()
        
        logger.info("Webhook Agent Index initialized successfully")
    
    async def initialize(self) -> bool:
        """
        Initialize all webhook agent components.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize security manager
            await self.security_manager.initialize()
            
            # Initialize webhook manager
            await self.webhook_manager.initialize()
            
            # Initialize event processor
            await self.event_processor.initialize()
            
            # Initialize monitoring
            await self.monitor.initialize()
            
            # Initialize handlers
            await self.platform_handlers.initialize()
            await self.notification_handlers.initialize()
            await self.monitoring_handlers.initialize()
            await self.payment_handlers.initialize()
            
            # Start webhook monitoring
            await self.monitor.start_monitoring()
            
            logger.info("Webhook Agent fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize webhook agent: {e}")
            return False
    
    def _initialize_webhook_routes(self) -> None:
        """Initialize webhook routing configuration."""
        
        # Platform webhooks
        self.webhook_registry.update({
            # YouTube webhooks
            'youtube/upload_complete': self.platform_handlers.handle_youtube_upload,
            'youtube/monetization_update': self.platform_handlers.handle_youtube_monetization,
            'youtube/analytics_update': self.platform_handlers.handle_youtube_analytics,
            
            # Instagram webhooks  
            'instagram/post_published': self.platform_handlers.handle_instagram_post,
            'instagram/story_published': self.platform_handlers.handle_instagram_story,
            'instagram/reel_published': self.platform_handlers.handle_instagram_reel,
            
            # TikTok webhooks
            'tiktok/video_published': self.platform_handlers.handle_tiktok_video,
            'tiktok/live_started': self.platform_handlers.handle_tiktok_live,
            'tiktok/analytics_update': self.platform_handlers.handle_tiktok_analytics,
            
            # Spotify webhooks
            'spotify/track_uploaded': self.platform_handlers.handle_spotify_upload,
            'spotify/playlist_updated': self.platform_handlers.handle_spotify_playlist,
            'spotify/royalty_update': self.platform_handlers.handle_spotify_royalty,
            
            # Notification webhooks
            'notification/email_sent': self.notification_handlers.handle_email_notification,
            'notification/sms_sent': self.notification_handlers.handle_sms_notification,
            'notification/push_sent': self.notification_handlers.handle_push_notification,
            
            # Monitoring webhooks
            'monitor/system_alert': self.monitoring_handlers.handle_system_alert,
            'monitor/performance_threshold': self.monitoring_handlers.handle_performance_alert,
            'monitor/security_incident': self.monitoring_handlers.handle_security_alert,
            
            # Payment webhooks
            'payment/transaction_complete': self.payment_handlers.handle_transaction_complete,
            'payment/subscription_updated': self.payment_handlers.handle_subscription_update,
            'payment/payout_processed': self.payment_handlers.handle_payout_processed,
        })
    
    async def register_webhook(
        self,
        webhook_id: str,
        webhook_url: str,
        platform: str,
        event_type: str,
        secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a new webhook endpoint.
        
        Args:
            webhook_id: Unique identifier for the webhook
            webhook_url: URL endpoint for the webhook
            platform: Platform name (youtube, instagram, etc.)
            event_type: Type of event to listen for
            secret: Optional webhook secret for verification
            headers: Optional custom headers
            metadata: Optional metadata
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Security validation
            if not await self.security_manager.validate_webhook_registration(
                webhook_url, platform, event_type
            ):
                logger.warning(f"Security validation failed for webhook {webhook_id}")
                return False
            
            # Register with webhook manager
            webhook_config = {
                'id': webhook_id,
                'url': webhook_url,
                'platform': platform,
                'event_type': event_type,
                'secret': secret,
                'headers': headers or {},
                'metadata': metadata or {},
                'created_at': datetime.now(timezone.utc).isoformat(),
                'status': 'active'
            }
            
            success = await self.webhook_manager.register_webhook(webhook_config)
            
            if success:
                self.active_webhooks[webhook_id] = webhook_config
                logger.info(f"Webhook {webhook_id} registered successfully")
                
                # Log webhook registration event
                await self.monitor.log_webhook_event(
                    webhook_id, 'registered', {'platform': platform, 'event_type': event_type}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register webhook {webhook_id}: {e}")
            return False
    
    async def process_webhook(
        self,
        webhook_id: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        source_ip: str
    ) -> Dict[str, Any]:
        """
        Process an incoming webhook request.
        
        Args:
            webhook_id: Webhook identifier
            payload: Webhook payload data
            headers: Request headers
            source_ip: Source IP address
            
        Returns:
            Dict containing processing results
        """
        try:
            # Security verification
            if not await self.security_manager.verify_webhook_signature(
                webhook_id, payload, headers
            ):
                logger.warning(f"Invalid signature for webhook {webhook_id}")
                return {
                    'success': False,
                    'error': 'Invalid signature',
                    'status_code': 401
                }
            
            # Rate limiting check
            if not await self.security_manager.check_rate_limit(webhook_id, source_ip):
                logger.warning(f"Rate limit exceeded for webhook {webhook_id}")
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'status_code': 429
                }
            
            # Get webhook configuration
            webhook_config = self.active_webhooks.get(webhook_id)
            if not webhook_config:
                logger.error(f"Webhook {webhook_id} not found")
                return {
                    'success': False,
                    'error': 'Webhook not found',
                    'status_code': 404
                }
            
            # Process webhook event
            result = await self.event_processor.process_event(
                webhook_id, webhook_config, payload, headers
            )
            
            # Log successful processing
            await self.monitor.log_webhook_event(
                webhook_id, 'processed', {
                    'payload_size': len(str(payload)),
                    'success': result.get('success', False)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process webhook {webhook_id}: {e}")
            
            # Log error event
            await self.monitor.log_webhook_event(
                webhook_id, 'error', {'error': str(e)}
            )
            
            return {
                'success': False,
                'error': str(e),
                'status_code': 500
            }
    
    async def get_webhook_stats(self, webhook_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get webhook statistics.
        
        Args:
            webhook_id: Optional specific webhook ID
            
        Returns:
            Dict containing webhook statistics
        """
        try:
            return await self.monitor.get_webhook_statistics(webhook_id)
            
        except Exception as e:
            logger.error(f"Failed to get webhook stats: {e}")
            return {}
    
    async def update_webhook(
        self,
        webhook_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update webhook configuration.
        
        Args:
            webhook_id: Webhook identifier
            updates: Updates to apply
            
        Returns:
            bool: True if update successful
        """
        try:
            if webhook_id not in self.active_webhooks:
                return False
            
            # Update webhook configuration
            success = await self.webhook_manager.update_webhook(webhook_id, updates)
            
            if success:
                self.active_webhooks[webhook_id].update(updates)
                self.active_webhooks[webhook_id]['updated_at'] = datetime.now(timezone.utc).isoformat()
                
                # Log update event
                await self.monitor.log_webhook_event(
                    webhook_id, 'updated', {'updates': list(updates.keys())}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update webhook {webhook_id}: {e}")
            return False
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook identifier
            
        Returns:
            bool: True if deletion successful
        """
        try:
            success = await self.webhook_manager.delete_webhook(webhook_id)
            
            if success:
                self.active_webhooks.pop(webhook_id, None)
                
                # Log deletion event
                await self.monitor.log_webhook_event(
                    webhook_id, 'deleted', {}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete webhook {webhook_id}: {e}")
            return False
    
    async def list_webhooks(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List registered webhooks.
        
        Args:
            platform: Optional platform filter
            status: Optional status filter
            
        Returns:
            List of webhook configurations
        """
        try:
            webhooks = list(self.active_webhooks.values())
            
            # Apply filters
            if platform:
                webhooks = [w for w in webhooks if w.get('platform') == platform]
            
            if status:
                webhooks = [w for w in webhooks if w.get('status') == status]
            
            return webhooks
            
        except Exception as e:
            logger.error(f"Failed to list webhooks: {e}")
            return []
    
    async def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        Test a webhook endpoint.
        
        Args:
            webhook_id: Webhook identifier
            
        Returns:
            Dict containing test results
        """
        try:
            webhook_config = self.active_webhooks.get(webhook_id)
            if not webhook_config:
                return {
                    'success': False,
                    'error': 'Webhook not found'
                }
            
            # Generate test payload
            test_payload = self.utils.generate_test_payload(
                webhook_config['platform'],
                webhook_config['event_type']
            )
            
            # Send test webhook
            result = await self.webhook_manager.send_webhook(
                webhook_config['url'],
                test_payload,
                webhook_config.get('headers', {}),
                webhook_config.get('secret')
            )
            
            # Log test event
            await self.monitor.log_webhook_event(
                webhook_id, 'tested', {'success': result.get('success', False)}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to test webhook {webhook_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_webhook_logs(
        self,
        webhook_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get webhook logs.
        
        Args:
            webhook_id: Webhook identifier
            limit: Maximum number of logs to return
            offset: Offset for pagination
            
        Returns:
            List of webhook log entries
        """
        try:
            return await self.monitor.get_webhook_logs(webhook_id, limit, offset)
            
        except Exception as e:
            logger.error(f"Failed to get webhook logs for {webhook_id}: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Shutdown the webhook agent gracefully."""
        try:
            logger.info("Shutting down webhook agent...")
            
            # Stop monitoring
            await self.monitor.stop_monitoring()
            
            # Shutdown handlers
            await self.platform_handlers.shutdown()
            await self.notification_handlers.shutdown()
            await self.monitoring_handlers.shutdown()
            await self.payment_handlers.shutdown()
            
            # Shutdown core components
            await self.event_processor.shutdown()
            await self.webhook_manager.shutdown()
            await self.security_manager.shutdown()
            
            logger.info("Webhook agent shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during webhook agent shutdown: {e}")


# Global webhook agent instance
webhook_agent = None


async def get_webhook_agent(config: Optional[Dict[str, Any]] = None) -> WebhookAgentIndex:
    """
    Get or create the global webhook agent instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        WebhookAgentIndex instance
    """
    global webhook_agent
    
    if webhook_agent is None:
        webhook_agent = WebhookAgentIndex(config)
        await webhook_agent.initialize()
    
    return webhook_agent


async def process_webhook_request(
    webhook_id: str,
    payload: Dict[str, Any],
    headers: Dict[str, str],
    source_ip: str
) -> Dict[str, Any]:
    """
    Process a webhook request using the global agent.
    
    Args:
        webhook_id: Webhook identifier
        payload: Webhook payload
        headers: Request headers
        source_ip: Source IP address
        
    Returns:
        Dict containing processing results
    """
    agent = await get_webhook_agent()
    return await agent.process_webhook(webhook_id, payload, headers, source_ip)


# Export main classes and functions
__all__ = [
    'WebhookAgentIndex',
    'get_webhook_agent',
    'process_webhook_request',
    'webhook_agent'
]


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        """Main function for testing the webhook agent."""
        import json
        
        # Initialize webhook agent
        agent = await get_webhook_agent()
        
        # Register a test webhook
        success = await agent.register_webhook(
            webhook_id="test_youtube_upload",
            webhook_url="https://example.com/webhooks/youtube",
            platform="youtube",
            event_type="upload_complete",
            secret="test_secret_123"
        )
        
        print(f"Webhook registration: {'Success' if success else 'Failed'}")
        
        # Test webhook processing
        test_payload = {
            "event": "upload_complete",
            "video_id": "test_video_123",
            "title": "Test Video",
            "duration": 300,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        result = await agent.process_webhook(
            webhook_id="test_youtube_upload",
            payload=test_payload,
            headers={"Content-Type": "application/json"},
            source_ip="127.0.0.1"
        )
        
        print(f"Webhook processing result: {json.dumps(result, indent=2)}")
        
        # Get webhook statistics
        stats = await agent.get_webhook_stats()
        print(f"Webhook statistics: {json.dumps(stats, indent=2)}")
        
        # List webhooks
        webhooks = await agent.list_webhooks()
        print(f"Active webhooks: {len(webhooks)}")
        
        # Shutdown
        await agent.shutdown()
    
    # Run the main function
    asyncio.run(main())
