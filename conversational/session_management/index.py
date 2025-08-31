"""Session Management Index - IA Influencer Agent

Central index for all session management components with unified access
and initialization for enterprise-grade conversation session handling
across multi-platform content creator workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
Unauthorized use prohibited. Contact: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from .session_lifecycle_manager import (
    SessionLifecycleManager,
    SessionCreationHandler,
    SessionTerminationHandler,
    SessionStateTransitionManager,
    SessionConfig,
    SessionMetadata
)

from .multi_platform_session_sync import (
    MultiPlatformSessionSync,
    CrossPlatformStateManager,
    PlatformSessionAdapter,
    SessionSynchronizationEngine
)

from .conversation_session_store import (
    ConversationSessionStore,
    SessionDataPersistence,
    SessionCacheManager,
    DistributedSessionStorage,
    SessionStoreConfig,
    SessionData
)

from .session_security_manager import (
    SessionSecurityManager,
    SessionAuthenticationHandler,
    SessionEncryptionManager,
    SecureSessionTokenGenerator,
    SecurityConfig
)

from .session_analytics_engine import (
    SessionAnalyticsEngine,
    SessionBehaviorTracker,
    ConversationInsightsGenerator,
    SessionPerformanceMonitor
)

from ...core.logging import get_logger
from ...utils.metrics import MetricsCollector
from ...utils.events import EventPublisher

logger = get_logger(__name__)


class SessionManagementIndex:
    """Unified session management system orchestrator"""    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        self.event_publisher = EventPublisher()
        
        # Core components
        self.lifecycle_manager: Optional[SessionLifecycleManager] = None
        self.sync_manager: Optional[MultiPlatformSessionSync] = None
        self.session_store: Optional[ConversationSessionStore] = None
        self.security_manager: Optional[SessionSecurityManager] = None
        self.analytics_engine: Optional[SessionAnalyticsEngine] = None
        
        # Initialization status
        self.is_initialized = False
        self.components_status: Dict[str, bool] = {}
    
    async def initialize(
        self,
        session_config: Optional[SessionConfig] = None,
        store_config: Optional[SessionStoreConfig] = None,
        security_config: Optional[SecurityConfig] = None
    ) -> bool:
        """Initialize all session management components"""        
        try:
            self.logger.info("Initializing Session Management System...")
            
            # Initialize components in order
            await self._initialize_session_store(store_config)
            await self._initialize_security_manager(security_config)
            await self._initialize_lifecycle_manager(session_config)
            await self._initialize_sync_manager()
            await self._initialize_analytics_engine()
            
            # Verify all components are ready
            if all(self.components_status.values()):
                self.is_initialized = True
                
                # Publish initialization event
                await self.event_publisher.publish_event(
                    "session_management.initialized",
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "components": list(self.components_status.keys())
                    }
                )
                
                self.logger.info("Session Management System initialized successfully")
                await self.metrics_collector.increment("session_management.initialization_success")
                
                return True
            else:
                failed_components = [
                    name for name, status in self.components_status.items()
                    if not status
                ]
                self.logger.error(f"Failed to initialize components: {failed_components}")
                return False
                
        except Exception as e:
            self.logger.error(f"Session management initialization failed: {str(e)}")
            await self.metrics_collector.increment("session_management.initialization_failed")
            return False
    
    async def _initialize_session_store(self, config: Optional[SessionStoreConfig]):
        """Initialize session store component"""        
        try:
            self.session_store = ConversationSessionStore(config)
            await self.session_store.initialize()
            self.components_status["session_store"] = True
            self.logger.info("Session Store initialized")
            
        except Exception as e:
            self.logger.error(f"Session Store initialization failed: {str(e)}")
            self.components_status["session_store"] = False
    
    async def _initialize_security_manager(self, config: Optional[SecurityConfig]):
        """Initialize security manager component"""        
        try:
            self.security_manager = SessionSecurityManager(config)
            self.components_status["security_manager"] = True
            self.logger.info("Security Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Security Manager initialization failed: {str(e)}")
            self.components_status["security_manager"] = False
    
    async def _initialize_lifecycle_manager(self, config: Optional[SessionConfig]):
        """Initialize lifecycle manager component"""        
        try:
            self.lifecycle_manager = SessionLifecycleManager()
            self.components_status["lifecycle_manager"] = True
            self.logger.info("Lifecycle Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Lifecycle Manager initialization failed: {str(e)}")
            self.components_status["lifecycle_manager"] = False
    
    async def _initialize_sync_manager(self):
        """Initialize sync manager component"""        
        try:
            self.sync_manager = MultiPlatformSessionSync()
            await self.sync_manager.initialize()
            self.components_status["sync_manager"] = True
            self.logger.info("Sync Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Sync Manager initialization failed: {str(e)}")
            self.components_status["sync_manager"] = False
    
    async def _initialize_analytics_engine(self):
        """Initialize analytics engine component"""        
        try:
            self.analytics_engine = SessionAnalyticsEngine()
            self.components_status["analytics_engine"] = True
            self.logger.info("Analytics Engine initialized")
            
        except Exception as e:
            self.logger.error(f"Analytics Engine initialization failed: {str(e)}")
            self.components_status["analytics_engine"] = False
    
    async def shutdown(self):
        """Gracefully shutdown all components"""        
        try:
            self.logger.info("Shutting down Session Management System...")
            
            # Shutdown components in reverse order
            if self.analytics_engine:
                # Analytics engine doesn't need explicit shutdown
                pass
            
            if self.sync_manager:
                # Stop any background sync tasks
                pass
            
            if self.lifecycle_manager:
                # Terminate any active sessions if needed
                pass
            
            if self.security_manager:
                # Revoke any pending tokens if needed
                pass
            
            if self.session_store:
                await self.session_store.shutdown()
            
            self.is_initialized = False
            self.logger.info("Session Management System shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {str(e)}")
    
    # Unified API methods
    
    async def create_secure_session(
        self,
        user_credentials: Dict[str, Any],
        request_fingerprint: Dict[str, Any],
        metadata: SessionMetadata
    ) -> Dict[str, Any]:
        """Create new secure session with full initialization"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            # Create session
            session_id = await self.lifecycle_manager.create_session(metadata)
            
            # Secure the session
            auth_success, jwt_token = await self.security_manager.authenticate_and_secure_session(
                session_id,
                user_credentials,
                request_fingerprint
            )
            
            if not auth_success:
                # Clean up failed session
                await self.lifecycle_manager.terminate_session(session_id, "authentication_failed")
                return {"success": False, "error": "Authentication failed"}
            
            # Activate session
            await self.lifecycle_manager.activate_session(session_id)
            
            # Start cross-platform sync
            await self.sync_manager.start_session_sync(session_id)
            
            # Begin analytics tracking
            await self.analytics_engine.track_session_event(
                session_id,
                "session_created",
                {"metadata": metadata.dict(), "platform": metadata.platform}
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "jwt_token": jwt_token,
                "expires_at": (datetime.utcnow().timestamp() + 3600)  # 1 hour default
            }
            
        except Exception as e:
            self.logger.error(f"Secure session creation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def validate_session(
        self,
        session_id: str,
        jwt_token: str,
        request_fingerprint: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate session security and status"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            # Validate security
            is_valid = await self.security_manager.validate_session_security(
                session_id,
                jwt_token,
                request_fingerprint
            )
            
            if not is_valid:
                return {"valid": False, "error": "Security validation failed"}
            
            # Get session status
            session_status = await self.lifecycle_manager.get_session_status(session_id)
            
            if not session_status:
                return {"valid": False, "error": "Session not found"}
            
            # Track validation event
            await self.analytics_engine.track_session_event(
                session_id,
                "session_validated",
                {"security_check": "passed"}
            )
            
            return {
                "valid": True,
                "session_status": session_status,
                "sync_status": await self.sync_manager.get_sync_status(session_id)
            }
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def add_conversation_message(
        self,
        session_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """Add message to conversation with analytics tracking"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            # Store message
            success = await self.session_store.add_conversation_message(session_id, message)
            
            if success:
                # Track message event
                await self.analytics_engine.track_session_event(
                    session_id,
                    "message_sent",
                    {
                        "sender": message.get("sender", "unknown"),
                        "content_length": len(message.get("content", "")),
                        "intent": message.get("intent")
                    }
                )
                
                # Sync across platforms
                await self.sync_manager.update_session_state(
                    session_id,
                    {"last_message": message}
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Message addition failed: {str(e)}")
            return False
    
    async def update_session_context(
        self,
        session_id: str,
        context_update: Dict[str, Any]
    ) -> bool:
        """Update session context with sync"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            # Update context in store
            success = await self.session_store.update_context(session_id, context_update)
            
            if success:
                # Sync context update
                await self.sync_manager.update_session_state(
                    session_id,
                    {"context_update": context_update}
                )
                
                # Track context change
                await self.analytics_engine.track_session_event(
                    session_id,
                    "context_updated",
                    {"update_type": context_update.get("type", "unknown")}
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Context update failed: {str(e)}")
            return False
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session analytics"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            return await self.analytics_engine.generate_session_analytics(session_id)
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            return {"session_id": session_id, "error": str(e)}
    
    async def terminate_session(
        self,
        session_id: str,
        reason: str = "user_request",
        save_conversation: bool = True
    ) -> bool:
        """Terminate session with complete cleanup"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            # Generate final analytics
            await self.analytics_engine.generate_session_analytics(session_id)
            
            # Stop sync
            await self.sync_manager.stop_session_sync(session_id)
            
            # Revoke security tokens
            await self.security_manager.revoke_session_token(session_id, reason)
            
            # Terminate session
            success = await self.lifecycle_manager.terminate_session(
                session_id,
                reason,
                save_conversation
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Session termination failed: {str(e)}")
            return False
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user analytics dashboard"""        
        if not self.is_initialized:
            raise RuntimeError("Session management not initialized")
        
        try:
            return await self.analytics_engine.get_analytics_dashboard(user_id)
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {str(e)}")
            return {"user_id": user_id, "error": str(e)}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""        
        try:
            health_status = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_initialized": self.is_initialized,
                "components": self.components_status.copy(),
                "metrics": {},
                "alerts": []
            }
            
            if self.is_initialized:
                # Get storage statistics
                if self.session_store:
                    storage_stats = await self.session_store.get_storage_statistics()
                    health_status["metrics"]["storage"] = storage_stats
                
                # Get security metrics
                if self.security_manager:
                    security_metrics = await self.security_manager.get_security_metrics()
                    health_status["metrics"]["security"] = security_metrics
                
                # Check for alerts
                if self.components_status.get("session_store", False):
                    cache_stats = storage_stats.get("cache", {})
                    if cache_stats.get("hit_ratio", 1.0) < 0.8:
                        health_status["alerts"].append("Low cache hit ratio")
                
                if self.components_status.get("security_manager", False):
                    failed_auths = security_metrics.get("authentication", {}).get("failed_authentications", 0)
                    if failed_auths > 100:  # Threshold
                        health_status["alerts"].append("High authentication failure rate")
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_initialized": False,
                "error": str(e)
            }


# Global session management instance
_session_management_instance: Optional[SessionManagementIndex] = None


async def get_session_management() -> SessionManagementIndex:
    """Get global session management instance"""    
    global _session_management_instance
    
    if _session_management_instance is None:
        _session_management_instance = SessionManagementIndex()
        
        # Initialize with default configurations
        await _session_management_instance.initialize()
    
    return _session_management_instance


async def initialize_session_management(
    session_config: Optional[SessionConfig] = None,
    store_config: Optional[SessionStoreConfig] = None,
    security_config: Optional[SecurityConfig] = None
) -> bool:
    """Initialize global session management with custom configurations"""    
    global _session_management_instance
    
    _session_management_instance = SessionManagementIndex()
    return await _session_management_instance.initialize(
        session_config,
        store_config,
        security_config
    )


async def shutdown_session_management():
    """Shutdown global session management"""    
    global _session_management_instance
    
    if _session_management_instance:
        await _session_management_instance.shutdown()
        _session_management_instance = None


# Convenience functions for common operations

async def create_session(
    user_credentials: Dict[str, Any],
    request_fingerprint: Dict[str, Any],
    metadata: SessionMetadata
) -> Dict[str, Any]:
    """Convenience function to create secure session"""    
    sm = await get_session_management()
    return await sm.create_secure_session(user_credentials, request_fingerprint, metadata)


async def validate_session(
    session_id: str,
    jwt_token: str,
    request_fingerprint: Dict[str, Any]
) -> Dict[str, Any]:
    """Convenience function to validate session"""    
    sm = await get_session_management()
    return await sm.validate_session(session_id, jwt_token, request_fingerprint)


async def add_message(session_id: str, message: Dict[str, Any]) -> bool:
    """Convenience function to add conversation message"""    
    sm = await get_session_management()
    return await sm.add_conversation_message(session_id, message)


async def get_analytics(session_id: str) -> Dict[str, Any]:
    """Convenience function to get session analytics"""    
    sm = await get_session_management()
    return await sm.get_session_analytics(session_id)


async def terminate_session(
    session_id: str,
    reason: str = "user_request"
) -> bool:
    """Convenience function to terminate session"""    
    sm = await get_session_management()
    return await sm.terminate_session(session_id, reason)
