"""
API Versioning Management
Enterprise API versioning for Ainflue infrastructure

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VersioningStrategy(Enum):
    """API versioning strategies"""
    URL_PATH = "url_path"  # /v1/api/users
    QUERY_PARAM = "query_param"  # /api/users?version=1
    HEADER = "header"  # X-API-Version: 1
    ACCEPT_HEADER = "accept_header"  # Accept: application/vnd.api+json;version=1


@dataclass
class APIVersion:
    """API version configuration"""
    version: str
    strategy: VersioningStrategy = VersioningStrategy.URL_PATH
    deprecated: bool = False
    sunset_date: Optional[datetime] = None
    supported_features: List[str] = field(default_factory=list)
    migration_guide: Optional[str] = None
    backwards_compatible: bool = True


class APIVersionManager:
    """API versioning management for Ainflue APIs"""
    
    def __init__(self):
        """Initialize API version manager"""
        self.versions = {}
        self.routing_rules = {}
        
        # Ainflue API versions
        self.ainflue_versions = {
            "v1": APIVersion(
                version="v1",
                strategy=VersioningStrategy.URL_PATH,
                deprecated=False,
                supported_features=["creator_management", "content_upload", "basic_analytics"]
            ),
            "v2": APIVersion(
                version="v2", 
                strategy=VersioningStrategy.URL_PATH,
                deprecated=False,
                supported_features=["creator_management", "content_upload", "ai_analysis", "collaboration", "advanced_analytics"]
            ),
            "v3": APIVersion(
                version="v3",
                strategy=VersioningStrategy.URL_PATH,
                deprecated=False,
                supported_features=["all_v2_features", "real_time_collaboration", "revenue_optimization", "enterprise_features"]
            )
        }
        
        for version_name, version in self.ainflue_versions.items():
            self.add_version(version)
            
        logger.info("API version manager initialized")
        
    def add_version(self, version: APIVersion) -> bool:
        """Add new API version"""
        try:
            self.versions[version.version] = version
            logger.info(f"Added API version: {version.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to add API version {version.version}: {e}")
            return False
            
    def deprecate_version(self, version: str, sunset_date: datetime) -> bool:
        """Deprecate API version with sunset date"""
        try:
            if version not in self.versions:
                raise ValueError(f"Version {version} not found")
                
            self.versions[version].deprecated = True
            self.versions[version].sunset_date = sunset_date
            
            logger.info(f"Deprecated API version {version} with sunset date {sunset_date}")
            return True
        except Exception as e:
            logger.error(f"Failed to deprecate version {version}: {e}")
            return False
            
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get version information"""
        if version not in self.versions:
            return {'error': f'Version {version} not found'}
            
        version_obj = self.versions[version]
        return {
            'version': version_obj.version,
            'strategy': version_obj.strategy.value,
            'deprecated': version_obj.deprecated,
            'sunset_date': version_obj.sunset_date.isoformat() if version_obj.sunset_date else None,
            'supported_features': version_obj.supported_features,
            'backwards_compatible': version_obj.backwards_compatible
        }