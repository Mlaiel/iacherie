"""Platform Integration Repository Module

Enterprise-grade repository for managing platform integrations with OAuth,
API management, health monitoring, and automated synchronization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import uuid
import json
from ..models.platform_integrations import (
    PlatformIntegration,
    Platform,
    IntegrationStatus,
    IntegrationType,
    AuthMethod,
    DataSyncStatus,
    HealthStatus,
    RateLimitStatus
)
from .base_repository import BaseRepository, RepositoryException
import logging

logger = logging.getLogger(__name__)

class PlatformIntegrationRepository(BaseRepository[PlatformIntegration]):
    """
    Repository for platform integration operations with comprehensive OAuth management,
    API health monitoring, rate limiting, and automated synchronization capabilities.
    """
    
    def __init__(self, db_session: Session):
        """Initialize platform integration repository"""
        super().__init__(db_session, PlatformIntegration)
        
    def create_integration(self,
                          user_id: int,
                          platform: Platform,
                          integration_type: IntegrationType,
                          auth_method: AuthMethod,
                          access_token: str,
                          refresh_token: Optional[str] = None,
                          token_expires_at: Optional[datetime] = None,
                          scopes: Optional[List[str]] = None,
                          platform_user_id: Optional[str] = None,
                          platform_username: Optional[str] = None,
                          configuration: Optional[Dict[str, Any]] = None) -> PlatformIntegration:
        """
        Create platform integration with secure token management
        
        Args:
            user_id: User ID
            platform: Platform to integrate with
            integration_type: Type of integration
            auth_method: Authentication method used
            access_token: OAuth access token (encrypted)
            refresh_token: OAuth refresh token (encrypted)
            token_expires_at: Token expiration time
            scopes: OAuth scopes granted
            platform_user_id: User ID on the platform
            platform_username: Username on the platform
            configuration: Platform-specific configuration
            
        Returns:
            Created PlatformIntegration instance
        """
        try:
            # Check for existing integration
            existing = self.get_user_platform_integration(user_id, platform)
            if existing and existing.status == IntegrationStatus.ACTIVE:
                raise RepositoryException(
                    f"Active integration already exists for {platform.value}"
                )
            
            # Generate integration ID
            integration_id = str(uuid.uuid4())
            
            integration_data = {
                'user_id': user_id,
                'platform': platform,
                'integration_type': integration_type,
                'auth_method': auth_method,
                'access_token': self._encrypt_token(access_token),
                'refresh_token': self._encrypt_token(refresh_token) if refresh_token else None,
                'token_expires_at': token_expires_at,
                'scopes': scopes or [],
                'platform_user_id': platform_user_id,
                'platform_username': platform_username,
                'status': IntegrationStatus.ACTIVE,
                'health_status': HealthStatus.HEALTHY,
                'data_sync_status': DataSyncStatus.PENDING,
                'rate_limit_status': RateLimitStatus.NORMAL,
                'configuration': configuration or {},
                'integration_id': integration_id,
                'last_sync_at': None,
                'next_sync_at': self._calculate_next_sync(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            integration = self.create(**integration_data)
            
            self.logger.info(
                f"Created {platform.value} integration for user {user_id} using {auth_method.value}"
            )
            
            return integration
            
        except Exception as e:
            self.logger.error(f"Failed to create platform integration: {str(e)}")
            raise RepositoryException(f"Integration creation failed: {str(e)}")
            
    def _encrypt_token(self, token: str) -> str:
        """
        Encrypt token for secure storage (placeholder implementation)
        
        Args:
            token: Token to encrypt
            
        Returns:
            Encrypted token string
        """
        # In production, use proper encryption (AES-256, Fernet, etc.)
        # This is a placeholder implementation
        import base64
        return base64.b64encode(token.encode()).decode()
        
    def _decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt token for use (placeholder implementation)
        
        Args:
            encrypted_token: Encrypted token
            
        Returns:
            Decrypted token string
        """
        # In production, use proper decryption
        # This is a placeholder implementation
        import base64
        return base64.b64decode(encrypted_token.encode()).decode()
        
    def _calculate_next_sync(self) -> datetime:
        """
        Calculate next synchronization time
        
        Returns:
            Next sync datetime
        """
        # Default to sync every hour
        return datetime.utcnow() + timedelta(hours=1)
        
    def get_user_platform_integration(self,
                                    user_id: int,
                                    platform: Platform) -> Optional[PlatformIntegration]:
        """
        Get user's integration for a specific platform
        
        Args:
            user_id: User ID
            platform: Platform to get integration for
            
        Returns:
            PlatformIntegration instance or None
        """
        try:
            return self.db_session.query(PlatformIntegration).filter(
                and_(
                    PlatformIntegration.user_id == user_id,
                    PlatformIntegration.platform == platform,
                    PlatformIntegration.status != IntegrationStatus.DELETED
                )
            ).order_by(PlatformIntegration.created_at.desc()).first()
            
        except Exception as e:
            self.logger.error(f"Failed to get platform integration: {str(e)}")
            return None
            
    def get_user_integrations(self,
                            user_id: int,
                            status: Optional[IntegrationStatus] = None,
                            health_status: Optional[HealthStatus] = None,
                            include_tokens: bool = False) -> List[PlatformIntegration]:
        """
        Get all integrations for a user with filtering
        
        Args:
            user_id: User ID
            status: Optional status filter
            health_status: Optional health status filter
            include_tokens: Whether to decrypt and include tokens
            
        Returns:
            List of PlatformIntegration instances
        """
        try:
            query = self.db_session.query(PlatformIntegration).filter(
                PlatformIntegration.user_id == user_id
            )
            
            if status:
                query = query.filter(PlatformIntegration.status == status)
            if health_status:
                query = query.filter(PlatformIntegration.health_status == health_status)
            
            query = query.order_by(PlatformIntegration.created_at.desc())
            
            integrations = query.all()
            
            # Decrypt tokens if requested
            if include_tokens:
                for integration in integrations:
                    if integration.access_token:
                        integration.decrypted_access_token = self._decrypt_token(
                            integration.access_token
                        )
                    if integration.refresh_token:
                        integration.decrypted_refresh_token = self._decrypt_token(
                            integration.refresh_token
                        )
            
            self.logger.debug(
                f"Retrieved {len(integrations)} integrations for user {user_id}"
            )
            
            return integrations
            
        except Exception as e:
            self.logger.error(f"Failed to get user integrations: {str(e)}")
            return []
            
    def update_tokens(self,
                     integration_id: int,
                     access_token: Optional[str] = None,
                     refresh_token: Optional[str] = None,
                     token_expires_at: Optional[datetime] = None,
                     scopes: Optional[List[str]] = None) -> Optional[PlatformIntegration]:
        """
        Update OAuth tokens for an integration
        
        Args:
            integration_id: Integration ID
            access_token: New access token
            refresh_token: New refresh token
            token_expires_at: New token expiration time
            scopes: Updated scopes
            
        Returns:
            Updated PlatformIntegration instance
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return None
            
            update_data = {
                'updated_at': datetime.utcnow()
            }
            
            if access_token:
                update_data['access_token'] = self._encrypt_token(access_token)
            if refresh_token:
                update_data['refresh_token'] = self._encrypt_token(refresh_token)
            if token_expires_at:
                update_data['token_expires_at'] = token_expires_at
            if scopes is not None:
                update_data['scopes'] = scopes
            
            # Update metadata with token refresh history
            metadata = integration.metadata or {}
            metadata['token_refresh_history'] = metadata.get('token_refresh_history', [])
            metadata['token_refresh_history'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'expires_at': token_expires_at.isoformat() if token_expires_at else None,
                'scopes_count': len(scopes) if scopes else 0
            })
            
            update_data['metadata'] = metadata
            
            updated_integration = self.update(integration_id, **update_data)
            
            self.logger.info(
                f"Updated tokens for {integration.platform.value} integration {integration_id}"
            )
            
            return updated_integration
            
        except Exception as e:
            self.logger.error(f"Failed to update tokens: {str(e)}")
            raise RepositoryException(f"Token update failed: {str(e)}")
            
    def update_sync_status(self,
                          integration_id: int,
                          sync_status: DataSyncStatus,
                          last_sync_error: Optional[str] = None,
                          next_sync_at: Optional[datetime] = None) -> Optional[PlatformIntegration]:
        """
        Update synchronization status for an integration
        
        Args:
            integration_id: Integration ID
            sync_status: New synchronization status
            last_sync_error: Optional error message
            next_sync_at: Optional next sync time
            
        Returns:
            Updated PlatformIntegration instance
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return None
            
            update_data = {
                'data_sync_status': sync_status,
                'last_sync_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            if next_sync_at:
                update_data['next_sync_at'] = next_sync_at
            else:
                # Calculate next sync based on status
                if sync_status == DataSyncStatus.COMPLETED:
                    update_data['next_sync_at'] = datetime.utcnow() + timedelta(hours=1)
                elif sync_status == DataSyncStatus.FAILED:
                    update_data['next_sync_at'] = datetime.utcnow() + timedelta(minutes=30)
            
            # Update metadata with sync history
            metadata = integration.metadata or {}
            metadata['sync_history'] = metadata.get('sync_history', [])
            metadata['sync_history'].append({
                'status': sync_status.value,
                'timestamp': datetime.utcnow().isoformat(),
                'error': last_sync_error
            })
            
            # Keep only last 50 sync history entries
            metadata['sync_history'] = metadata['sync_history'][-50:]
            
            if last_sync_error:
                metadata['last_sync_error'] = last_sync_error
            elif sync_status == DataSyncStatus.COMPLETED:
                metadata.pop('last_sync_error', None)
            
            update_data['metadata'] = metadata
            
            updated_integration = self.update(integration_id, **update_data)
            
            self.logger.info(
                f"Updated sync status for {integration.platform.value} integration: {sync_status.value}"
            )
            
            return updated_integration
            
        except Exception as e:
            self.logger.error(f"Failed to update sync status: {str(e)}")
            raise RepositoryException(f"Sync status update failed: {str(e)}")
            
    def update_health_status(self,
                           integration_id: int,
                           health_status: HealthStatus,
                           health_details: Optional[Dict[str, Any]] = None) -> Optional[PlatformIntegration]:
        """
        Update health status for an integration
        
        Args:
            integration_id: Integration ID
            health_status: New health status
            health_details: Optional health check details
            
        Returns:
            Updated PlatformIntegration instance
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return None
            
            update_data = {
                'health_status': health_status,
                'last_health_check': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Update metadata with health history
            metadata = integration.metadata or {}
            metadata['health_history'] = metadata.get('health_history', [])
            metadata['health_history'].append({
                'status': health_status.value,
                'timestamp': datetime.utcnow().isoformat(),
                'details': health_details
            })
            
            # Keep only last 100 health history entries
            metadata['health_history'] = metadata['health_history'][-100:]
            
            if health_details:
                metadata['last_health_details'] = health_details
            
            update_data['metadata'] = metadata
            
            updated_integration = self.update(integration_id, **update_data)
            
            self.logger.info(
                f"Updated health status for {integration.platform.value} integration: {health_status.value}"
            )
            
            return updated_integration
            
        except Exception as e:
            self.logger.error(f"Failed to update health status: {str(e)}")
            raise RepositoryException(f"Health status update failed: {str(e)}")
            
    def get_integrations_for_sync(self,
                                platform: Optional[Platform] = None,
                                limit: Optional[int] = None) -> List[PlatformIntegration]:
        """
        Get integrations that are due for synchronization
        
        Args:
            platform: Optional platform filter
            limit: Optional limit on number of results
            
        Returns:
            List of integrations due for sync
        """
        try:
            current_time = datetime.utcnow()
            
            query = self.db_session.query(PlatformIntegration).filter(
                and_(
                    PlatformIntegration.status == IntegrationStatus.ACTIVE,
                    PlatformIntegration.health_status.in_([
                        HealthStatus.HEALTHY, 
                        HealthStatus.WARNING
                    ]),
                    or_(
                        PlatformIntegration.next_sync_at <= current_time,
                        PlatformIntegration.next_sync_at.is_(None)
                    )
                )
            )
            
            if platform:
                query = query.filter(PlatformIntegration.platform == platform)
            
            # Order by next sync time (oldest first)
            query = query.order_by(
                PlatformIntegration.next_sync_at.asc().nullsfirst()
            )
            
            if limit:
                query = query.limit(limit)
            
            integrations = query.all()
            
            self.logger.debug(f"Found {len(integrations)} integrations due for sync")
            
            return integrations
            
        except Exception as e:
            self.logger.error(f"Failed to get integrations for sync: {str(e)}")
            return []
            
    def get_unhealthy_integrations(self) -> List[PlatformIntegration]:
        """
        Get integrations with health issues
        
        Returns:
            List of unhealthy integrations
        """
        try:
            integrations = self.db_session.query(PlatformIntegration).filter(
                and_(
                    PlatformIntegration.status == IntegrationStatus.ACTIVE,
                    PlatformIntegration.health_status.in_([
                        HealthStatus.DEGRADED,
                        HealthStatus.UNHEALTHY
                    ])
                )
            ).order_by(PlatformIntegration.last_health_check.asc()).all()
            
            self.logger.debug(f"Found {len(integrations)} unhealthy integrations")
            
            return integrations
            
        except Exception as e:
            self.logger.error(f"Failed to get unhealthy integrations: {str(e)}")
            return []
            
    def get_expiring_tokens(self, hours_ahead: int = 24) -> List[PlatformIntegration]:
        """
        Get integrations with tokens expiring soon
        
        Args:
            hours_ahead: Number of hours ahead to check
            
        Returns:
            List of integrations with expiring tokens
        """
        try:
            expiry_threshold = datetime.utcnow() + timedelta(hours=hours_ahead)
            
            integrations = self.db_session.query(PlatformIntegration).filter(
                and_(
                    PlatformIntegration.status == IntegrationStatus.ACTIVE,
                    PlatformIntegration.token_expires_at <= expiry_threshold,
                    PlatformIntegration.refresh_token.isnot(None)
                )
            ).order_by(PlatformIntegration.token_expires_at.asc()).all()
            
            self.logger.debug(
                f"Found {len(integrations)} integrations with tokens expiring in {hours_ahead} hours"
            )
            
            return integrations
            
        except Exception as e:
            self.logger.error(f"Failed to get expiring tokens: {str(e)}")
            return []
            
    def get_integration_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive integration statistics
        
        Args:
            user_id: Optional user ID to filter statistics
            
        Returns:
            Dictionary containing integration statistics
        """
        try:
            base_query = self.db_session.query(PlatformIntegration)
            
            if user_id:
                base_query = base_query.filter(PlatformIntegration.user_id == user_id)
            
            # Total counts
            total_integrations = base_query.count()
            active_integrations = base_query.filter(
                PlatformIntegration.status == IntegrationStatus.ACTIVE
            ).count()
            
            # Platform distribution
            platform_stats = {}
            for platform in Platform:
                count = base_query.filter(PlatformIntegration.platform == platform).count()
                platform_stats[platform.value] = count
            
            # Status distribution
            status_stats = {}
            for status in IntegrationStatus:
                count = base_query.filter(PlatformIntegration.status == status).count()
                status_stats[status.value] = count
            
            # Health distribution
            health_stats = {}
            for health in HealthStatus:
                count = base_query.filter(PlatformIntegration.health_status == health).count()
                health_stats[health.value] = count
            
            # Sync status distribution
            sync_stats = {}
            for sync_status in DataSyncStatus:
                count = base_query.filter(
                    PlatformIntegration.data_sync_status == sync_status
                ).count()
                sync_stats[sync_status.value] = count
            
            # Recent activity
            recent_syncs = base_query.filter(
                PlatformIntegration.last_sync_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
            
            # Token health
            expiring_soon = len(self.get_expiring_tokens(hours_ahead=24))
            
            statistics = {
                'total_integrations': total_integrations,
                'active_integrations': active_integrations,
                'platform_distribution': platform_stats,
                'status_distribution': status_stats,
                'health_distribution': health_stats,
                'sync_status_distribution': sync_stats,
                'recent_activity': {
                    'syncs_last_24h': recent_syncs,
                    'tokens_expiring_24h': expiring_soon
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Failed to get integration statistics: {str(e)}")
            return {'error': str(e)}
            
    def deactivate_integration(self,
                             integration_id: int,
                             reason: Optional[str] = None) -> Optional[PlatformIntegration]:
        """
        Deactivate an integration
        
        Args:
            integration_id: Integration ID
            reason: Optional reason for deactivation
            
        Returns:
            Updated PlatformIntegration instance
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return None
            
            # Update metadata with deactivation info
            metadata = integration.metadata or {}
            metadata['deactivation_history'] = metadata.get('deactivation_history', [])
            metadata['deactivation_history'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'reason': reason,
                'previous_status': integration.status.value
            })
            
            update_data = {
                'status': IntegrationStatus.INACTIVE,
                'health_status': HealthStatus.UNHEALTHY,
                'metadata': metadata,
                'updated_at': datetime.utcnow()
            }
            
            updated_integration = self.update(integration_id, **update_data)
            
            self.logger.info(
                f"Deactivated {integration.platform.value} integration {integration_id}: {reason}"
            )
            
            return updated_integration
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate integration: {str(e)}")
            raise RepositoryException(f"Integration deactivation failed: {str(e)}")

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
