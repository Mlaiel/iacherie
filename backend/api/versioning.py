"""Versioning - API Versioning and Compatibility
Consolidated API versioning functionality for backward compatibility.

This module consolidates versioning from:
- API version management and routing
- Backward compatibility handling
- Version deprecation and migration
- Client SDK version compatibility
- Breaking change detection and management
- API evolution and upgrade paths

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import re
import json
try:
    from packaging import version
except ImportError:
    # Fallback for basic version comparison
    class version:
        @staticmethod
        def parse(v):
            return tuple(map(int, v.split('.')))
        
        def __init__(self, v):
            self.version_tuple = tuple(map(int, v.split('.')))
        
        def __lt__(self, other):
            return self.version_tuple < other.version_tuple
        
        def __gt__(self, other):
            return self.version_tuple > other.version_tuple

from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

# ========================================
# VERSIONING ENUMS
# ========================================

class VersionStatus(str, Enum):
    """API version status"""
    DEVELOPMENT = "development"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class CompatibilityLevel(str, Enum):
    """API compatibility levels"""
    BREAKING = "breaking"        # Major version change required
    DEPRECATING = "deprecating"  # Minor version with deprecation warnings
    COMPATIBLE = "compatible"    # Fully backward compatible
    ENHANCED = "enhanced"        # New features, fully compatible

class ChangeType(str, Enum):
    """Types of API changes"""
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    ENDPOINT_ADDED = "endpoint_added"
    ENDPOINT_REMOVED = "endpoint_removed"
    ENDPOINT_CHANGED = "endpoint_changed"
    PARAMETER_ADDED = "parameter_added"
    PARAMETER_REMOVED = "parameter_removed"
    RESPONSE_FORMAT_CHANGED = "response_format_changed"

# ========================================
# VERSION MODELS
# ========================================

@dataclass
class APIVersion:
    """API version information"""
    major: int
    minor: int
    patch: int
    status: VersionStatus
    release_date: datetime
    end_of_life: Optional[datetime] = None
    changelog: List[str] = None
    breaking_changes: List[str] = None
    
    def __post_init__(self):
        if self.changelog is None:
            self.changelog = []
        if self.breaking_changes is None:
            self.breaking_changes = []
    
    @property
    def version_string(self) -> str:
        """Get semantic version string"""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @property
    def is_supported(self) -> bool:
        """Check if version is still supported"""
        if self.status == VersionStatus.RETIRED:
            return False
        if self.end_of_life and datetime.now() > self.end_of_life:
            return False
        return True
    
    @property
    def days_until_eol(self) -> Optional[int]:
        """Days until end of life"""
        if not self.end_of_life:
            return None
        delta = self.end_of_life - datetime.now()
        return max(0, delta.days)

class VersionCompatibility(BaseModel):
    """Version compatibility information"""
    current_version: str = Field(..., description="Current API version")
    requested_version: str = Field(..., description="Requested API version")
    compatibility_level: CompatibilityLevel = Field(..., description="Compatibility level")
    warnings: List[str] = Field(default_factory=list, description="Compatibility warnings")
    upgrade_path: Optional[str] = Field(None, description="Recommended upgrade path")
    sunset_date: Optional[datetime] = Field(None, description="Version sunset date")

class ChangelogEntry(BaseModel):
    """Changelog entry model"""
    version: str = Field(..., description="Version number")
    date: datetime = Field(..., description="Release date")
    change_type: ChangeType = Field(..., description="Type of change")
    description: str = Field(..., description="Change description")
    breaking: bool = Field(default=False, description="Is breaking change")
    migration_guide: Optional[str] = Field(None, description="Migration guide URL")

# ========================================
# VERSION MANAGER
# ========================================

class APIVersionManager:
    """Manages API versions and compatibility"""
    
    def __init__(self):
        self.versions: Dict[str, APIVersion] = {}
        self.current_version = "2.0.0"
        self.changelog: List[ChangelogEntry] = []
        self._init_versions()
    
    def _init_versions(self):
        """Initialize version registry"""
        # Version 1.0.0 - Legacy
        self.versions["1.0.0"] = APIVersion(
            major=1, minor=0, patch=0,
            status=VersionStatus.DEPRECATED,
            release_date=datetime(2024, 1, 1),
            end_of_life=datetime(2025, 6, 30),
            changelog=[
                "Initial API release",
                "Basic content management",
                "Simple authentication"
            ]
        )
        
        # Version 1.1.0 - Enhanced
        self.versions["1.1.0"] = APIVersion(
            major=1, minor=1, patch=0,
            status=VersionStatus.DEPRECATED,
            release_date=datetime(2024, 6, 1),
            end_of_life=datetime(2025, 6, 30),
            changelog=[
                "Added collaboration features",
                "Enhanced analytics",
                "Improved error handling"
            ]
        )
        
        # Version 2.0.0 - Current
        self.versions["2.0.0"] = APIVersion(
            major=2, minor=0, patch=0,
            status=VersionStatus.STABLE,
            release_date=datetime(2025, 1, 1),
            end_of_life=datetime(2027, 1, 1),
            changelog=[
                "Complete API redesign",
                "GraphQL support added",
                "Advanced AI features",
                "Enhanced security",
                "Real-time WebSocket support"
            ],
            breaking_changes=[
                "Authentication endpoint changes",
                "Response format standardization",
                "Field name updates"
            ]
        )
        
        # Version 2.1.0 - Future
        self.versions["2.1.0"] = APIVersion(
            major=2, minor=1, patch=0,
            status=VersionStatus.DEVELOPMENT,
            release_date=datetime(2025, 6, 1),
            changelog=[
                "Enhanced AI capabilities",
                "New collaboration features",
                "Performance improvements"
            ]
        )
    
    def get_version(self, version_string: str) -> Optional[APIVersion]:
        """Get version information"""
        return self.versions.get(version_string)
    
    def get_supported_versions(self) -> List[APIVersion]:
        """Get all supported versions"""
        return [v for v in self.versions.values() if v.is_supported]
    
    def get_latest_version(self) -> APIVersion:
        """Get latest stable version"""
        stable_versions = [
            v for v in self.versions.values() 
            if v.status == VersionStatus.STABLE
        ]
        return max(stable_versions, key=lambda v: (v.major, v.minor, v.patch))
    
    def check_compatibility(self, requested_version: str) -> VersionCompatibility:
        """Check compatibility between versions"""
        current = self.get_version(self.current_version)
        requested = self.get_version(requested_version)
        
        if not requested:
            raise ValueError(f"Unknown API version: {requested_version}")
        
        if not requested.is_supported:
            return VersionCompatibility(
                current_version=self.current_version,
                requested_version=requested_version,
                compatibility_level=CompatibilityLevel.BREAKING,
                warnings=[f"Version {requested_version} is no longer supported"],
                upgrade_path=f"Please upgrade to version {self.current_version}",
                sunset_date=requested.end_of_life
            )
        
        # Compare version numbers
        current_ver = version.parse(self.current_version)
        requested_ver = version.parse(requested_version)
        
        warnings = []
        compatibility_level = CompatibilityLevel.COMPATIBLE
        
        if requested_ver < current_ver:
            if requested_ver.major < current_ver.major:
                compatibility_level = CompatibilityLevel.BREAKING
                warnings.append(f"Major version difference detected. Breaking changes may exist.")
            elif requested.status == VersionStatus.DEPRECATED:
                compatibility_level = CompatibilityLevel.DEPRECATING
                warnings.append(f"Version {requested_version} is deprecated")
                if requested.days_until_eol:
                    warnings.append(f"End of life in {requested.days_until_eol} days")
            else:
                compatibility_level = CompatibilityLevel.COMPATIBLE
                warnings.append(f"Using older version {requested_version}")
        
        elif requested_ver > current_ver:
            compatibility_level = CompatibilityLevel.ENHANCED
            warnings.append(f"Requested version {requested_version} has additional features")
        
        return VersionCompatibility(
            current_version=self.current_version,
            requested_version=requested_version,
            compatibility_level=compatibility_level,
            warnings=warnings,
            upgrade_path=f"Consider upgrading to {self.current_version}" if warnings else None,
            sunset_date=requested.end_of_life
        )
    
    def add_changelog_entry(self, entry: ChangelogEntry):
        """Add changelog entry"""
        self.changelog.append(entry)
        self.changelog.sort(key=lambda x: x.date, reverse=True)
    
    def get_changelog(self, version: str = None, limit: int = 50) -> List[ChangelogEntry]:
        """Get changelog entries"""
        if version:
            return [entry for entry in self.changelog if entry.version == version]
        return self.changelog[:limit]

# ========================================
# VERSION MIDDLEWARE
# ========================================

class VersioningMiddleware:
    """Middleware for API versioning"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
    
    async def __call__(self, request: Request, call_next):
        """Process versioning for requests"""
        # Extract version from header or URL
        api_version = self._extract_version(request)
        
        # Set default version if none specified
        if not api_version:
            api_version = self.version_manager.current_version
        
        # Check compatibility
        try:
            compatibility = self.version_manager.check_compatibility(api_version)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Add version info to request state
        request.state.api_version = api_version
        request.state.compatibility = compatibility
        
        # Process request
        response = await call_next(request)
        
        # Add version headers to response
        response.headers["X-API-Version"] = api_version
        response.headers["X-API-Current-Version"] = self.version_manager.current_version
        
        # Add deprecation warnings
        if compatibility.warnings:
            response.headers["X-API-Warnings"] = "; ".join(compatibility.warnings)
        
        if compatibility.sunset_date:
            response.headers["X-API-Sunset"] = compatibility.sunset_date.isoformat()
        
        return response
    
    def _extract_version(self, request: Request) -> Optional[str]:
        """Extract API version from request"""
        # Check header first
        version_header = request.headers.get("X-API-Version")
        if version_header:
            return version_header
        
        # Check Accept header
        accept_header = request.headers.get("Accept", "")
        version_match = re.search(r'version=([0-9]+\.[0-9]+\.[0-9]+)', accept_header)
        if version_match:
            return version_match.group(1)
        
        # Check URL path
        path = request.url.path
        version_match = re.search(r'/v([0-9]+)/', path)
        if version_match:
            major_version = version_match.group(1)
            # Map major version to full version
            version_mapping = {
                "1": "1.1.0",  # Latest v1
                "2": "2.0.0"   # Latest v2
            }
            return version_mapping.get(major_version)
        
        return None

# ========================================
# VERSION ROUTING
# ========================================

class VersionedRouter:
    """Router that handles multiple API versions"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
        self.routes: Dict[str, Dict[str, APIRoute]] = {}  # version -> path -> route
    
    def add_versioned_route(
        self, 
        version: str, 
        path: str, 
        endpoint: Callable,
        methods: List[str] = None,
        **kwargs
    ):
        """Add route for specific version"""
        if version not in self.routes:
            self.routes[version] = {}
        
        if methods is None:
            methods = ["GET"]
        
        route = APIRoute(
            path=path,
            endpoint=endpoint,
            methods=methods,
            **kwargs
        )
        
        self.routes[version][path] = route
    
    def get_route_for_version(self, version: str, path: str) -> Optional[APIRoute]:
        """Get route for specific version and path"""
        if version in self.routes and path in self.routes[version]:
            return self.routes[version][path]
        
        # Fallback to compatible version
        compatibility = self.version_manager.check_compatibility(version)
        if compatibility.compatibility_level in [CompatibilityLevel.COMPATIBLE, CompatibilityLevel.ENHANCED]:
            current_version = self.version_manager.current_version
            if current_version in self.routes and path in self.routes[current_version]:
                return self.routes[current_version][path]
        
        return None

# ========================================
# VERSION TRANSFORMERS
# ========================================

class ResponseTransformer:
    """Transform responses for different API versions"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
        self.transformers: Dict[str, Dict[str, Callable]] = {}
    
    def register_transformer(self, from_version: str, to_version: str, transformer: Callable):
        """Register response transformer"""
        if from_version not in self.transformers:
            self.transformers[from_version] = {}
        self.transformers[from_version][to_version] = transformer
    
    def transform_response(self, data: Any, from_version: str, to_version: str) -> Any:
        """Transform response data between versions"""
        if from_version == to_version:
            return data
        
        # Direct transformation
        if (from_version in self.transformers and 
            to_version in self.transformers[from_version]):
            transformer = self.transformers[from_version][to_version]
            return transformer(data)
        
        # Default transformations based on version comparison
        from_ver = version.parse(from_version)
        to_ver = version.parse(to_version)
        
        if from_ver < to_ver:
            return self._upgrade_response(data, from_version, to_version)
        else:
            return self._downgrade_response(data, from_version, to_version)
    
    def _upgrade_response(self, data: Any, from_version: str, to_version: str) -> Any:
        """Upgrade response format to newer version"""
        if isinstance(data, dict):
            # Add new fields with default values
            if from_version.startswith("1.") and to_version.startswith("2."):
                # v1 to v2 transformation
                if "success" not in data:
                    data["success"] = True
                if "timestamp" not in data:
                    data["timestamp"] = datetime.now().isoformat()
        
        return data
    
    def _downgrade_response(self, data: Any, from_version: str, to_version: str) -> Any:
        """Downgrade response format to older version"""
        if isinstance(data, dict):
            # Remove fields not supported in older version
            if from_version.startswith("2.") and to_version.startswith("1."):
                # v2 to v1 transformation
                v1_data = data.copy()
                # Remove v2-specific fields
                v1_data.pop("timestamp", None)
                v1_data.pop("request_id", None)
                return v1_data
        
        return data

# ========================================
# VERSION ENDPOINTS
# ========================================

class VersioningEndpoints:
    """Endpoints for version information"""
    
    def __init__(self, version_manager: APIVersionManager):
        self.version_manager = version_manager
    
    async def get_versions(self) -> Dict[str, Any]:
        """Get all API versions"""
        return {
            "current_version": self.version_manager.current_version,
            "supported_versions": [
                {
                    "version": v.version_string,
                    "status": v.status.value,
                    "release_date": v.release_date.isoformat(),
                    "end_of_life": v.end_of_life.isoformat() if v.end_of_life else None,
                    "days_until_eol": v.days_until_eol
                }
                for v in self.version_manager.get_supported_versions()
            ]
        }
    
    async def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get specific version information"""
        api_version = self.version_manager.get_version(version)
        if not api_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} not found"
            )
        
        return {
            "version": api_version.version_string,
            "status": api_version.status.value,
            "release_date": api_version.release_date.isoformat(),
            "end_of_life": api_version.end_of_life.isoformat() if api_version.end_of_life else None,
            "changelog": api_version.changelog,
            "breaking_changes": api_version.breaking_changes,
            "is_supported": api_version.is_supported,
            "days_until_eol": api_version.days_until_eol
        }
    
    async def get_changelog(self, version: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get changelog entries"""
        entries = self.version_manager.get_changelog(version, limit)
        return [
            {
                "version": entry.version,
                "date": entry.date.isoformat(),
                "change_type": entry.change_type.value,
                "description": entry.description,
                "breaking": entry.breaking,
                "migration_guide": entry.migration_guide
            }
            for entry in entries
        ]
    
    async def check_compatibility(self, requested_version: str) -> VersionCompatibility:
        """Check version compatibility"""
        return self.version_manager.check_compatibility(requested_version)

# ========================================
# VERSIONING SERVICE
# ========================================

class VersioningService:
    """Main versioning service"""
    
    def __init__(self):
        self.version_manager = APIVersionManager()
        self.middleware = VersioningMiddleware(self.version_manager)
        self.router = VersionedRouter(self.version_manager)
        self.transformer = ResponseTransformer(self.version_manager)
        self.endpoints = VersioningEndpoints(self.version_manager)
        self.feature_flags = FeatureFlagManager()
        self.semantic_versioning = SemanticVersionManager()
    
    def setup_versioning(self, app: FastAPI):
        """Setup versioning for FastAPI app"""
        # Add middleware
        app.middleware("http")(self.middleware)
        
        # Add version endpoints
        app.add_api_route("/api/versions", self.endpoints.get_versions, methods=["GET"])
        app.add_api_route("/api/versions/{version}", self.endpoints.get_version_info, methods=["GET"])
        app.add_api_route("/api/changelog", self.endpoints.get_changelog, methods=["GET"])
        app.add_api_route("/api/compatibility/{requested_version}", self.endpoints.check_compatibility, methods=["GET"])
        
        # Add feature flag endpoints
        app.add_api_route("/api/features", self.endpoints.get_feature_flags, methods=["GET"])
        app.add_api_route("/api/features/{feature_name}", self.endpoints.get_feature_status, methods=["GET"])


# ========================================
# ENTERPRISE SEMANTIC VERSIONING
# ========================================

class SemanticVersionManager:
    """Enterprise semantic versioning with automated version management"""
    
    def __init__(self):
        self.version_pattern = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$')
        self.release_channels = {
            "stable": {"prefix": "", "auto_promote": True},
            "beta": {"prefix": "beta", "auto_promote": False},
            "alpha": {"prefix": "alpha", "auto_promote": False},
            "rc": {"prefix": "rc", "auto_promote": False}
        }
    
    def parse_version(self, version_string: str) -> Dict[str, Any]:
        """Parse semantic version string"""
        match = self.version_pattern.match(version_string)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_string}")
        
        major, minor, patch, prerelease, build = match.groups()
        
        return {
            "major": int(major),
            "minor": int(minor),
            "patch": int(patch),
            "prerelease": prerelease,
            "build": build,
            "raw": version_string,
            "is_prerelease": prerelease is not None,
            "release_channel": self._determine_release_channel(prerelease)
        }
    
    def generate_next_version(
        self,
        current_version: str,
        change_type: ChangeType,
        release_channel: str = "stable"
    ) -> str:
        """Generate next semantic version based on change type"""
        parsed = self.parse_version(current_version)
        
        # Remove prerelease/build metadata for base version calculation
        major, minor, patch = parsed["major"], parsed["minor"], parsed["patch"]
        
        if change_type == ChangeType.BREAKING:
            major += 1
            minor = 0
            patch = 0
        elif change_type == ChangeType.FEATURE:
            minor += 1
            patch = 0
        elif change_type == ChangeType.BUGFIX:
            patch += 1
        
        # Build new version string
        base_version = f"{major}.{minor}.{patch}"
        
        if release_channel != "stable":
            channel_config = self.release_channels.get(release_channel, {})
            prefix = channel_config.get("prefix", release_channel)
            # Add prerelease identifier
            base_version += f"-{prefix}.1"
        
        return base_version
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """Compare two semantic versions (-1, 0, 1)"""
        try:
            v1 = self.parse_version(version1)
            v2 = self.parse_version(version2)
            
            # Compare major.minor.patch
            for component in ["major", "minor", "patch"]:
                if v1[component] < v2[component]:
                    return -1
                elif v1[component] > v2[component]:
                    return 1
            
            # Handle prerelease versions
            if not v1["is_prerelease"] and v2["is_prerelease"]:
                return 1  # 1.0.0 > 1.0.0-alpha.1
            elif v1["is_prerelease"] and not v2["is_prerelease"]:
                return -1  # 1.0.0-alpha.1 < 1.0.0
            elif v1["is_prerelease"] and v2["is_prerelease"]:
                # Compare prerelease versions lexically
                if v1["prerelease"] < v2["prerelease"]:
                    return -1
                elif v1["prerelease"] > v2["prerelease"]:
                    return 1
            
            return 0
            
        except ValueError:
            # Fallback to string comparison for non-semantic versions
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            return 0
    
    def is_compatible(self, requested: str, available: str) -> bool:
        """Check if requested version is compatible with available version"""
        try:
            req = self.parse_version(requested)
            avail = self.parse_version(available)
            
            # Major version must match for compatibility
            if req["major"] != avail["major"]:
                return False
            
            # Available version must be >= requested version for minor/patch
            if avail["minor"] < req["minor"]:
                return False
            
            if avail["minor"] == req["minor"] and avail["patch"] < req["patch"]:
                return False
            
            return True
            
        except ValueError:
            return False
    
    def _determine_release_channel(self, prerelease: Optional[str]) -> str:
        """Determine release channel from prerelease identifier"""
        if not prerelease:
            return "stable"
        
        for channel, config in self.release_channels.items():
            prefix = config.get("prefix", "")
            if prefix and prerelease.startswith(prefix):
                return channel
        
        return "unknown"


# ========================================
# ENTERPRISE FEATURE FLAG MANAGER
# ========================================

class FeatureFlagManager:
    """Enterprise feature flag management with gradual rollouts"""
    
    def __init__(self):
        self.feature_flags = {}
        self.rollout_strategies = {
            "percentage": PercentageRolloutStrategy(),
            "user_segments": UserSegmentRolloutStrategy(),
            "geographic": GeographicRolloutStrategy(),
            "time_based": TimeBasedRolloutStrategy(),
            "canary": CanaryRolloutStrategy()
        }
        self.feature_analytics = FeatureFlagAnalytics()
    
    def register_feature(
        self,
        feature_name: str,
        description: str,
        default_enabled: bool = False,
        rollout_strategy: str = "percentage",
        rollout_config: Dict[str, Any] = None
    ) -> None:
        """Register a new feature flag"""
        self.feature_flags[feature_name] = {
            "name": feature_name,
            "description": description,
            "default_enabled": default_enabled,
            "rollout_strategy": rollout_strategy,
            "rollout_config": rollout_config or {},
            "created_at": datetime.utcnow().isoformat(),
            "last_modified": datetime.utcnow().isoformat(),
            "usage_analytics": {
                "total_checks": 0,
                "enabled_count": 0,
                "disabled_count": 0
            }
        }
    
    async def is_feature_enabled(
        self,
        feature_name: str,
        user_context: Dict[str, Any] = None
    ) -> bool:
        """Check if feature is enabled for given context"""
        feature = self.feature_flags.get(feature_name)
        if not feature:
            return False
        
        # Update analytics
        feature["usage_analytics"]["total_checks"] += 1
        
        # Apply rollout strategy
        strategy = self.rollout_strategies.get(feature["rollout_strategy"])
        if strategy:
            enabled = await strategy.is_enabled(feature, user_context or {})
        else:
            enabled = feature["default_enabled"]
        
        # Update analytics
        if enabled:
            feature["usage_analytics"]["enabled_count"] += 1
        else:
            feature["usage_analytics"]["disabled_count"] += 1
        
        # Record analytics
        await self.feature_analytics.record_feature_check(feature_name, enabled, user_context)
        
        return enabled
    
    def update_feature_rollout(
        self,
        feature_name: str,
        rollout_config: Dict[str, Any]
    ) -> bool:
        """Update feature rollout configuration"""
        if feature_name not in self.feature_flags:
            return False
        
        feature = self.feature_flags[feature_name]
        feature["rollout_config"].update(rollout_config)
        feature["last_modified"] = datetime.utcnow().isoformat()
        
        return True
    
    def get_feature_status(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive feature status"""
        feature = self.feature_flags.get(feature_name)
        if not feature:
            return None
        
        return {
            **feature,
            "rollout_percentage": self._calculate_rollout_percentage(feature),
            "performance_impact": self.feature_analytics.get_performance_impact(feature_name),
            "usage_trends": self.feature_analytics.get_usage_trends(feature_name)
        }
    
    def list_all_features(self) -> List[Dict[str, Any]]:
        """List all registered features with their status"""
        return [self.get_feature_status(name) for name in self.feature_flags.keys()]
    
    def _calculate_rollout_percentage(self, feature: Dict[str, Any]) -> float:
        """Calculate current rollout percentage"""
        strategy = feature["rollout_strategy"]
        config = feature["rollout_config"]
        
        if strategy == "percentage":
            return config.get("percentage", 0.0)
        elif strategy == "user_segments":
            # Estimate based on segment sizes
            return config.get("estimated_percentage", 0.0)
        else:
            # For other strategies, estimate based on usage
            total = feature["usage_analytics"]["total_checks"]
            enabled = feature["usage_analytics"]["enabled_count"]
            return (enabled / total * 100) if total > 0 else 0.0


# ========================================
# ROLLOUT STRATEGIES
# ========================================

class PercentageRolloutStrategy:
    """Percentage-based feature rollout"""
    
    async def is_enabled(self, feature: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        percentage = feature["rollout_config"].get("percentage", 0.0)
        
        # Use user ID for consistent rollout
        user_id = user_context.get("user_id", "anonymous")
        hash_value = hash(f"{feature['name']}:{user_id}") % 100
        
        return hash_value < percentage


class UserSegmentRolloutStrategy:
    """User segment-based feature rollout"""
    
    async def is_enabled(self, feature: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        enabled_segments = feature["rollout_config"].get("enabled_segments", [])
        user_segment = user_context.get("segment", "default")
        
        return user_segment in enabled_segments


class GeographicRolloutStrategy:
    """Geographic-based feature rollout"""
    
    async def is_enabled(self, feature: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        enabled_regions = feature["rollout_config"].get("enabled_regions", [])
        user_region = user_context.get("region", "unknown")
        
        return user_region in enabled_regions


class TimeBasedRolloutStrategy:
    """Time-based feature rollout"""
    
    async def is_enabled(self, feature: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        start_time = feature["rollout_config"].get("start_time")
        end_time = feature["rollout_config"].get("end_time")
        
        if not start_time:
            return feature.get("default_enabled", False)
        
        current_time = datetime.utcnow().isoformat()
        
        if start_time <= current_time:
            if not end_time or current_time <= end_time:
                return True
        
        return False


class CanaryRolloutStrategy:
    """Canary deployment-based feature rollout"""
    
    async def is_enabled(self, feature: Dict[str, Any], user_context: Dict[str, Any]) -> bool:
        canary_users = feature["rollout_config"].get("canary_users", [])
        user_id = user_context.get("user_id")
        
        return user_id in canary_users


class FeatureFlagAnalytics:
    """Analytics for feature flag usage and performance"""
    
    def __init__(self):
        self.usage_data = defaultdict(list)
        self.performance_data = defaultdict(list)
    
    async def record_feature_check(
        self,
        feature_name: str,
        enabled: bool,
        user_context: Dict[str, Any]
    ) -> None:
        """Record feature flag check for analytics"""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "enabled": enabled,
            "user_id": user_context.get("user_id"),
            "user_segment": user_context.get("segment"),
            "region": user_context.get("region")
        }
        
        self.usage_data[feature_name].append(record)
    
    def get_performance_impact(self, feature_name: str) -> Dict[str, Any]:
        """Get performance impact analysis for feature"""
        # Mock implementation - would analyze actual performance metrics
        return {
            "avg_response_time_ms": 45.2,
            "error_rate_percent": 0.05,
            "resource_usage_increase_percent": 2.1,
            "user_satisfaction_score": 8.7
        }
    
    def get_usage_trends(self, feature_name: str) -> Dict[str, Any]:
        """Get usage trends for feature"""
        usage_records = self.usage_data.get(feature_name, [])
        
        if not usage_records:
            return {"total_checks": 0, "enabled_rate": 0.0}
        
        total_checks = len(usage_records)
        enabled_checks = sum(1 for record in usage_records if record["enabled"])
        
        return {
            "total_checks": total_checks,
            "enabled_rate": enabled_checks / total_checks * 100,
            "last_24h_checks": len([r for r in usage_records[-100:]]),  # Simplified
            "trending": "stable"  # Would calculate actual trend
        }


# Add missing imports
import re
from collections import defaultdict

# Create global instances
semantic_version_manager = SemanticVersionManager()
feature_flag_manager = FeatureFlagManager()

# ========================================
# DEPENDENCY FUNCTIONS
# ========================================

def get_api_version(request: Request) -> str:
    """Get API version from request"""
    return getattr(request.state, "api_version", "2.0.0")

def get_compatibility_info(request: Request) -> VersionCompatibility:
    """Get compatibility information from request"""
    return getattr(request.state, "compatibility", None)

async def is_feature_enabled(feature_name: str, request: Request = None) -> bool:
    """Check if feature is enabled for current request context"""
    user_context = {}
    if request:
        user_context = {
            "user_id": getattr(request.state, "user_id", None),
            "segment": getattr(request.state, "user_segment", "default"),
            "region": getattr(request.state, "user_region", "unknown")
        }
    
    return await feature_flag_manager.is_feature_enabled(feature_name, user_context)

# ========================================
# EXPORTS
# ========================================

__all__ = [
    "VersionStatus",
    "CompatibilityLevel",
    "ChangeType",
    "APIVersion",
    "VersionCompatibility",
    "ChangelogEntry",
    "APIVersionManager",
    "VersioningMiddleware",
    "VersionedRouter",
    "ResponseTransformer",
    "VersioningEndpoints",
    "VersioningService",
    "SemanticVersionManager",
    "FeatureFlagManager",
    "PercentageRolloutStrategy",
    "UserSegmentRolloutStrategy",
    "GeographicRolloutStrategy",
    "TimeBasedRolloutStrategy",
    "CanaryRolloutStrategy",
    "FeatureFlagAnalytics",
    "semantic_version_manager",
    "feature_flag_manager",
    "get_api_version",
    "get_compatibility_info",
    "is_feature_enabled"
]