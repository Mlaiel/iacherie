"""Enterprise Platform Configuration Manager

Advanced configuration management for platform-specific crawling
with dynamic settings and intelligent optimization.

PROTECTION NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert
Copyright: All rights reserved
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, text
from uuid import uuid4
import json
from enum import Enum

from ..core.base import DatabaseManager
from ..models.crawling_models import (
    PlatformConfig,
    ConfigScope,
    ConfigType
)
from ..core.exceptions import (
    DatabaseError,
    ValidationError,
    ConfigurationError
)


class PlatformType(Enum):
    """Supported crawling platforms."""    YOUTUBE = 'youtube'
    TIKTOK = 'tiktok'
    INSTAGRAM = 'instagram'
    TWITTER = 'twitter'
    GENERIC = 'generic'


class DefaultConfigurations:
    """Default configurations for each platform."""    
    YOUTUBE = {
        'api_version': 'v3',
        'rate_limit_requests_per_hour': 10000,
        'rate_limit_requests_per_day': 100000,
        'concurrent_sessions': 5,
        'request_timeout': 30,
        'retry_attempts': 3,
        'retry_backoff_factor': 2,
        'user_agent_rotation': True,
        'proxy_required': False,
        'javascript_required': True,
        'anti_detection_measures': {
            'random_delays': True,
            'min_delay': 1,
            'max_delay': 5,
            'vary_request_headers': True,
            'cookie_persistence': True
        },
        'content_selectors': {
            'video_title': 'h1.title',
            'video_description': '#description',
            'view_count': '.view-count',
            'like_count': '.like-button .count',
            'channel_name': '.channel-name'
        },
        'api_endpoints': {
            'search': 'https://www.googleapis.com/youtube/v3/search',
            'videos': 'https://www.googleapis.com/youtube/v3/videos',
            'channels': 'https://www.googleapis.com/youtube/v3/channels'
        }
    }
    
    TIKTOK = {
        'rate_limit_requests_per_hour': 1000,
        'rate_limit_requests_per_day': 10000,
        'concurrent_sessions': 3,
        'request_timeout': 45,
        'retry_attempts': 5,
        'retry_backoff_factor': 3,
        'user_agent_rotation': True,
        'proxy_required': True,
        'javascript_required': True,
        'browser_emulation': True,
        'anti_detection_measures': {
            'random_delays': True,
            'min_delay': 3,
            'max_delay': 10,
            'vary_request_headers': True,
            'cookie_persistence': True,
            'fingerprint_randomization': True,
            'viewport_randomization': True
        },
        'content_selectors': {
            'video_description': '[data-e2e="video-desc"]',
            'author_name': '[data-e2e="video-author"]',
            'like_count': '[data-e2e="like-count"]',
            'share_count': '[data-e2e="share-count"]',
            'comment_count': '[data-e2e="comment-count"]'
        },
        'scroll_behavior': {
            'enabled': True,
            'scroll_pause_time': 2,
            'max_scrolls': 10
        }
    }
    
    INSTAGRAM = {
        'api_version': 'latest',
        'rate_limit_requests_per_hour': 5000,
        'rate_limit_requests_per_day': 50000,
        'concurrent_sessions': 4,
        'request_timeout': 25,
        'retry_attempts': 3,
        'retry_backoff_factor': 2,
        'user_agent_rotation': True,
        'proxy_required': False,
        'javascript_required': True,
        'anti_detection_measures': {
            'random_delays': True,
            'min_delay': 2,
            'max_delay': 8,
            'vary_request_headers': True,
            'cookie_persistence': True,
            'session_rotation': True
        },
        'content_selectors': {
            'post_caption': 'article span',
            'like_count': 'article section button span',
            'comment_count': 'article section a span',
            'username': 'article header a',
            'timestamp': 'article time'
        },
        'api_endpoints': {
            'basic_display': 'https://graph.instagram.com',
            'graph_api': 'https://graph.facebook.com'
        }
    }
    
    TWITTER = {
        'api_version': 'v2',
        'rate_limit_requests_per_hour': 15000,
        'rate_limit_requests_per_day': 150000,
        'concurrent_sessions': 6,
        'request_timeout': 20,
        'retry_attempts': 3,
        'retry_backoff_factor': 2,
        'user_agent_rotation': True,
        'proxy_required': False,
        'javascript_required': False,
        'anti_detection_measures': {
            'random_delays': True,
            'min_delay': 1,
            'max_delay': 3,
            'vary_request_headers': True,
            'bearer_token_rotation': True
        },
        'api_endpoints': {
            'tweets_search': 'https://api.twitter.com/2/tweets/search/recent',
            'users_lookup': 'https://api.twitter.com/2/users',
            'tweets_lookup': 'https://api.twitter.com/2/tweets'
        },
        'request_fields': {
            'tweet_fields': 'author_id,created_at,public_metrics,text',
            'user_fields': 'created_at,description,public_metrics',
            'expansions': 'author_id'
        }
    }
    
    GENERIC = {
        'rate_limit_requests_per_hour': 3600,
        'rate_limit_requests_per_day': 36000,
        'concurrent_sessions': 2,
        'request_timeout': 30,
        'retry_attempts': 3,
        'retry_backoff_factor': 2,
        'user_agent_rotation': True,
        'proxy_required': False,
        'javascript_required': False,
        'anti_detection_measures': {
            'random_delays': True,
            'min_delay': 1,
            'max_delay': 5,
            'vary_request_headers': True,
            'respect_robots_txt': True
        },
        'crawling_behavior': {
            'follow_redirects': True,
            'max_redirects': 5,
            'verify_ssl': True,
            'allow_redirects': True
        }
    }


class PlatformConfigManager(DatabaseManager):
    """    Enterprise-grade platform configuration manager.
    
    Handles:
    - Platform-specific crawling configurations
    - Dynamic configuration updates
    - Performance optimization settings
    - Anti-detection measures
    - Configuration versioning and rollback
    """    
    def __init__(self, db_session: Session):
        """        Initialize platform configuration manager.
        
        Args:
            db_session: SQLAlchemy database session
        """        super().__init__(db_session)
        self.table = PlatformConfig
        self.default_configs = {
            PlatformType.YOUTUBE.value: DefaultConfigurations.YOUTUBE,
            PlatformType.TIKTOK.value: DefaultConfigurations.TIKTOK,
            PlatformType.INSTAGRAM.value: DefaultConfigurations.INSTAGRAM,
            PlatformType.TWITTER.value: DefaultConfigurations.TWITTER,
            PlatformType.GENERIC.value: DefaultConfigurations.GENERIC
        }
    
    async def get_config(
        self,
        platform: str,
        config_overrides: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Get comprehensive configuration for platform with overrides.
        
        Args:
            platform: Target platform
            config_overrides: Optional configuration overrides
            user_id: Optional user-specific configurations
            
        Returns:
            Dict containing complete platform configuration
            
        Raises:
            ValidationError: If platform not supported
            ConfigurationError: If configuration invalid
        """        try:
            # Validate platform
            if platform not in [p.value for p in PlatformType]:
                raise ValidationError(f"Unsupported platform: {platform}")
            
            # Start with default configuration
            config = self.default_configs[platform].copy()
            
            # Apply stored platform configurations
            stored_config = await self._get_stored_platform_config(platform)
            if stored_config:
                config = self._deep_merge_configs(config, stored_config)
            
            # Apply user-specific configurations
            if user_id:
                user_config = await self._get_user_platform_config(platform, user_id)
                if user_config:
                    config = self._deep_merge_configs(config, user_config)
            
            # Apply runtime overrides
            if config_overrides:
                config = self._deep_merge_configs(config, config_overrides)
            
            # Validate final configuration
            await self._validate_configuration(platform, config)
            
            # Add metadata
            config['_metadata'] = {
                'platform': platform,
                'generated_at': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'has_overrides': bool(config_overrides),
                'config_version': await self._get_config_version(platform)
            }
            
            return config
            
        except Exception as e:
            if isinstance(e, (ValidationError, ConfigurationError)):
                raise
            raise ConfigurationError(f"Failed to get configuration: {str(e)}")
    
    async def _get_stored_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """        Get stored platform configuration from database.
        
        Args:
            platform: Target platform
            
        Returns:
            Dict containing stored configuration or None
        """        try:
            result = await self.db.execute(
                text("""                SELECT config_data FROM platform_configs
                WHERE platform = :platform
                  AND scope = :platform_scope
                  AND is_active = true
                ORDER BY version DESC
                LIMIT 1
                """),
                {
                    'platform': platform,
                    'platform_scope': ConfigScope.PLATFORM.value
                }
            )
            
            config_row = result.first()
            if config_row and config_row.config_data:
                return json.loads(config_row.config_data)
            
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get stored platform config: {str(e)}")
    
    async def _get_user_platform_config(
        self,
        platform: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """        Get user-specific platform configuration.
        
        Args:
            platform: Target platform
            user_id: User identifier
            
        Returns:
            Dict containing user configuration or None
        """        try:
            result = await self.db.execute(
                text("""                SELECT config_data FROM platform_configs
                WHERE platform = :platform
                  AND scope = :user_scope
                  AND user_id = :user_id
                  AND is_active = true
                ORDER BY version DESC
                LIMIT 1
                """),
                {
                    'platform': platform,
                    'user_scope': ConfigScope.USER.value,
                    'user_id': user_id
                }
            )
            
            config_row = result.first()
            if config_row and config_row.config_data:
                return json.loads(config_row.config_data)
            
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get user platform config: {str(e)}")
    
    def _deep_merge_configs(
        self,
        base_config: Dict[str, Any],
        override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Recursively merge configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Override configuration
            
        Returns:
            Merged configuration
        """        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def _validate_configuration(
        self,
        platform: str,
        config: Dict[str, Any]
    ) -> None:
        """        Validate platform configuration for completeness and correctness.
        
        Args:
            platform: Target platform
            config: Configuration to validate
            
        Raises:
            ConfigurationError: If configuration is invalid
        """        try:
            # Required fields for all platforms
            required_fields = [
                'rate_limit_requests_per_hour',
                'rate_limit_requests_per_day',
                'concurrent_sessions',
                'request_timeout',
                'retry_attempts'
            ]
            
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise ConfigurationError(
                    f"Missing required fields for {platform}: {missing_fields}"
                )
            
            # Validate numeric ranges
            if config['concurrent_sessions'] < 1 or config['concurrent_sessions'] > 20:
                raise ConfigurationError("concurrent_sessions must be between 1 and 20")
            
            if config['request_timeout'] < 5 or config['request_timeout'] > 300:
                raise ConfigurationError("request_timeout must be between 5 and 300 seconds")
            
            if config['retry_attempts'] < 0 or config['retry_attempts'] > 10:
                raise ConfigurationError("retry_attempts must be between 0 and 10")
            
            # Platform-specific validations
            if platform == PlatformType.YOUTUBE.value:
                if 'api_endpoints' not in config:
                    raise ConfigurationError("YouTube config requires api_endpoints")
            
            elif platform == PlatformType.TIKTOK.value:
                if 'anti_detection_measures' not in config:
                    raise ConfigurationError("TikTok config requires anti_detection_measures")
            
            elif platform == PlatformType.TWITTER.value:
                if 'api_endpoints' not in config:
                    raise ConfigurationError("Twitter config requires api_endpoints")
                
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")
    
    async def _get_config_version(self, platform: str) -> str:
        """        Get current configuration version for platform.
        
        Args:
            platform: Target platform
            
        Returns:
            Configuration version string
        """        try:
            result = await self.db.execute(
                text("""                SELECT MAX(version) as latest_version
                FROM platform_configs
                WHERE platform = :platform
                  AND scope = :platform_scope
                """),
                {
                    'platform': platform,
                    'platform_scope': ConfigScope.PLATFORM.value
                }
            )
            
            version_row = result.first()
            return str(version_row.latest_version or 1)
            
        except Exception as e:
            return "1"  # Default version
    
    async def update_platform_config(
        self,
        platform: str,
        config_updates: Dict[str, Any],
        user_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """        Update platform configuration with new settings.
        
        Args:
            platform: Target platform
            config_updates: Configuration updates to apply
            user_id: Optional user for user-specific config
            description: Optional description of changes
            
        Returns:
            Configuration ID
            
        Raises:
            ValidationError: If platform or updates invalid
        """        try:
            # Validate platform
            if platform not in [p.value for p in PlatformType]:
                raise ValidationError(f"Unsupported platform: {platform}")
            
            # Get current configuration
            current_config = await self.get_config(platform, user_id=user_id)
            
            # Apply updates
            updated_config = self._deep_merge_configs(current_config, config_updates)
            
            # Remove metadata from storage
            if '_metadata' in updated_config:
                del updated_config['_metadata']
            
            # Validate updated configuration
            await self._validate_configuration(platform, updated_config)
            
            # Determine scope and version
            scope = ConfigScope.USER.value if user_id else ConfigScope.PLATFORM.value
            version = await self._get_next_version(platform, scope, user_id)
            
            # Create configuration record
            config_id = str(uuid4())
            config_data = {
                'config_id': config_id,
                'platform': platform,
                'scope': scope,
                'user_id': user_id,
                'config_type': ConfigType.CRAWLING.value,
                'version': version,
                'config_data': json.dumps(updated_config),
                'description': description,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Deactivate previous versions
            await self._deactivate_previous_versions(platform, scope, user_id)
            
            # Insert new configuration
            platform_config = PlatformConfig(**config_data)
            self.db.add(platform_config)
            await self.db.commit()
            
            return config_id
            
        except Exception as e:
            await self.db.rollback()
            if isinstance(e, (ValidationError, ConfigurationError)):
                raise
            raise DatabaseError(f"Failed to update platform config: {str(e)}")
    
    async def _get_next_version(
        self,
        platform: str,
        scope: str,
        user_id: Optional[str]
    ) -> int:
        """        Get next version number for configuration.
        
        Args:
            platform: Target platform
            scope: Configuration scope
            user_id: Optional user identifier
            
        Returns:
            Next version number
        """        try:
            query_params = {
                'platform': platform,
                'scope': scope
            }
            
            query = """            SELECT MAX(version) as latest_version
            FROM platform_configs
            WHERE platform = :platform AND scope = :scope
            """            
            if user_id:
                query += " AND user_id = :user_id"
                query_params['user_id'] = user_id
            else:
                query += " AND user_id IS NULL"
            
            result = await self.db.execute(text(query), query_params)
            version_row = result.first()
            
            return (version_row.latest_version or 0) + 1
            
        except Exception as e:
            return 1  # Default to version 1
    
    async def _deactivate_previous_versions(
        self,
        platform: str,
        scope: str,
        user_id: Optional[str]
    ) -> None:
        """        Deactivate previous configuration versions.
        
        Args:
            platform: Target platform
            scope: Configuration scope
            user_id: Optional user identifier
        """        try:
            query_params = {
                'platform': platform,
                'scope': scope,
                'now': datetime.utcnow()
            }
            
            query = """            UPDATE platform_configs 
            SET is_active = false, updated_at = :now
            WHERE platform = :platform AND scope = :scope AND is_active = true
            """            
            if user_id:
                query += " AND user_id = :user_id"
                query_params['user_id'] = user_id
            else:
                query += " AND user_id IS NULL"
            
            await self.db.execute(text(query), query_params)
            
        except Exception as e:
            raise DatabaseError(f"Failed to deactivate previous versions: {str(e)}")
    
    async def get_configuration_history(
        self,
        platform: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """        Get configuration change history for platform.
        
        Args:
            platform: Target platform
            user_id: Optional user filter
            limit: Maximum number of records to return
            
        Returns:
            List of configuration history records
        """        try:
            query_params = {
                'platform': platform,
                'limit': limit
            }
            
            query = """            SELECT config_id, version, description, is_active,
                   created_at, updated_at, scope, user_id
            FROM platform_configs
            WHERE platform = :platform
            """            
            if user_id:
                query += " AND user_id = :user_id"
                query_params['user_id'] = user_id
            
            query += " ORDER BY created_at DESC LIMIT :limit"
            
            result = await self.db.execute(text(query), query_params)
            
            return [
                {
                    'config_id': row.config_id,
                    'version': row.version,
                    'description': row.description,
                    'is_active': row.is_active,
                    'scope': row.scope,
                    'user_id': row.user_id,
                    'created_at': row.created_at.isoformat(),
                    'updated_at': row.updated_at.isoformat()
                }
                for row in result
            ]
            
        except Exception as e:
            raise DatabaseError(f"Failed to get configuration history: {str(e)}")
    
    async def rollback_configuration(
        self,
        platform: str,
        target_version: int,
        user_id: Optional[str] = None
    ) -> bool:
        """        Rollback configuration to specific version.
        
        Args:
            platform: Target platform
            target_version: Version to rollback to
            user_id: Optional user for user-specific config
            
        Returns:
            bool indicating success
        """        try:
            scope = ConfigScope.USER.value if user_id else ConfigScope.PLATFORM.value
            
            # Get target configuration
            query_params = {
                'platform': platform,
                'scope': scope,
                'version': target_version
            }
            
            query = """            SELECT config_data FROM platform_configs
            WHERE platform = :platform AND scope = :scope AND version = :version
            """            
            if user_id:
                query += " AND user_id = :user_id"
                query_params['user_id'] = user_id
            else:
                query += " AND user_id IS NULL"
            
            result = await self.db.execute(text(query), query_params)
            config_row = result.first()
            
            if not config_row:
                raise ValidationError(f"Configuration version {target_version} not found")
            
            # Create new configuration with rolled back data
            rollback_config = json.loads(config_row.config_data)
            
            return await self.update_platform_config(
                platform=platform,
                config_updates=rollback_config,
                user_id=user_id,
                description=f"Rollback to version {target_version}"
            ) is not None
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise DatabaseError(f"Failed to rollback configuration: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """        Perform health check of configuration system.
        
        Returns:
            Dict containing health status
        """        try:
            # Check configuration completeness for all platforms
            platform_status = {}
            
            for platform in PlatformType:
                try:
                    config = await self.get_config(platform.value)
                    platform_status[platform.value] = 'healthy'
                except Exception:
                    platform_status[platform.value] = 'unhealthy'
            
            # Check recent configuration updates
            recent_updates = await self.db.query(func.count(PlatformConfig.config_id)).filter(
                PlatformConfig.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).scalar()
            
            # Determine overall health
            unhealthy_platforms = sum(1 for status in platform_status.values() if status == 'unhealthy')
            overall_status = 'healthy' if unhealthy_platforms == 0 else 'degraded'
            
            return {
                'status': overall_status,
                'platform_status': platform_status,
                'unhealthy_platforms': unhealthy_platforms,
                'recent_updates_24h': recent_updates,
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }


# Export main class
__all__ = ['PlatformConfigManager', 'PlatformType', 'DefaultConfigurations']
