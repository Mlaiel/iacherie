"""
Mobile Infrastructure Index - Professional Navigation System
Provides comprehensive overview and navigation for all mobile modules

Author: Fahed Mlaiel <mlaiel@live.de>
Business Logic: creators → upload multi-format → AI processing → protection → monetization → collaboration
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import importlib.util
import os


@dataclass
class MobileModuleInfo:
    """Professional mobile module information structure."""
    name: str
    description: str
    file_path: str
    key_classes: List[str]
    key_functions: List[str]
    business_purpose: str
    mobile_platforms: List[str]  # ['android', 'ios', 'react_native']


class MobileModuleIndex:
    """Professional index of all mobile infrastructure modules."""
    
    def __init__(self):
        self.modules = {
            "backend": MobileModuleInfo(
                name="Mobile Backend Core",
                description="Enterprise mobile backend infrastructure with FastAPI integration",
                file_path="mobile.backend",
                key_classes=["MobileAPIServer", "DeviceManager", "MobileAuthManager"],
                key_functions=["create_mobile_app", "register_device", "authenticate_mobile_user"],
                business_purpose="Core mobile backend services for content creator platform access",
                mobile_platforms=["android", "ios", "react_native"]
            ),
            
            "services": MobileModuleInfo(
                name="Mobile Business Services",
                description="Content processing, upload, and collaboration services optimized for mobile",
                file_path="mobile.services",
                key_classes=["MobileContentService", "MobileUploadService", "MobileCollaborationService"],
                key_functions=["process_mobile_upload", "optimize_for_mobile", "sync_mobile_data"],
                business_purpose="Mobile-optimized business logic for content creation workflow",
                mobile_platforms=["android", "ios", "react_native"]
            ),
            
            "security": MobileModuleInfo(
                name="Mobile Security Framework",
                description="Device authentication, biometric auth, and mobile-specific security",
                file_path="mobile.security",
                key_classes=["MobileSecurityManager", "BiometricAuth", "DeviceIntegrity"],
                key_functions=["verify_device", "biometric_authenticate", "encrypt_mobile_data"],
                business_purpose="Secure mobile access and content protection for creators",
                mobile_platforms=["android", "ios", "react_native"]
            ),
            
            "api": MobileModuleInfo(
                name="Mobile API Gateway",
                description="Mobile-optimized API endpoints with offline support and sync",
                file_path="mobile.api",
                key_classes=["MobileAPIRouter", "OfflineSyncManager", "MobileResponseOptimizer"],
                key_functions=["create_mobile_routes", "handle_offline_request", "optimize_response"],
                business_purpose="Efficient mobile API access for content management and collaboration",
                mobile_platforms=["android", "ios", "react_native"]
            ),
            
            "analytics": MobileModuleInfo(
                name="Mobile Analytics Engine",
                description="Mobile usage tracking, performance monitoring, and business insights",
                file_path="mobile.analytics",
                key_classes=["MobileAnalytics", "PerformanceTracker", "UsageMonitor"],
                key_functions=["track_mobile_event", "monitor_performance", "generate_insights"],
                business_purpose="Data-driven insights for mobile creator engagement and platform optimization",
                mobile_platforms=["android", "ios", "react_native"]
            ),
            
            "config": MobileModuleInfo(
                name="Mobile Configuration Management",
                description="Platform-specific configs, feature flags, and environment management",
                file_path="mobile.config",
                key_classes=["MobileConfig", "PlatformSettings", "FeatureFlags"],
                key_functions=["get_mobile_config", "update_feature_flags", "load_platform_settings"],
                business_purpose="Flexible mobile platform configuration for multi-environment deployment",
                mobile_platforms=["android", "ios", "react_native"]
            )
        }
    
    def get_all_modules(self) -> Dict[str, MobileModuleInfo]:
        """Get all mobile modules with their information."""
        return self.modules
    
    def get_module_by_name(self, name: str) -> Optional[MobileModuleInfo]:
        """Get specific mobile module information."""
        return self.modules.get(name)
    
    def find_modules_for_platform(self, platform: str) -> List[MobileModuleInfo]:
        """Find modules supporting specific platform."""
        return [
            module for module in self.modules.values()
            if platform in module.mobile_platforms
        ]
    
    def find_modules_for_purpose(self, purpose_keyword: str) -> List[MobileModuleInfo]:
        """Find modules by business purpose keyword."""
        return [
            module for module in self.modules.values()
            if purpose_keyword.lower() in module.business_purpose.lower()
        ]
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive mobile system overview."""
        return {
            "total_modules": len(self.modules),
            "modules": {
                name: {
                    "description": info.description,
                    "business_purpose": info.business_purpose,
                    "platforms": info.mobile_platforms,
                    "key_components": len(info.key_classes) + len(info.key_functions)
                }
                for name, info in self.modules.items()
            },
            "platform_coverage": {
                "android": len(self.find_modules_for_platform("android")),
                "ios": len(self.find_modules_for_platform("ios")),
                "react_native": len(self.find_modules_for_platform("react_native"))
            },
            "business_workflows": {
                "content_upload": [
                    "Device authentication (security)",
                    "Content validation (services)",
                    "Upload processing (backend)",
                    "Progress tracking (analytics)"
                ],
                "ai_processing": [
                    "Request optimization (api)",
                    "Processing queue (backend)",
                    "Progress monitoring (analytics)",
                    "Result delivery (services)"
                ],
                "collaboration": [
                    "User matching (services)",
                    "Secure communication (security)",
                    "Real-time sync (api)",
                    "Activity tracking (analytics)"
                ],
                "monetization": [
                    "Payment processing (backend)",
                    "Revenue tracking (analytics)",
                    "Configuration management (config)",
                    "Security validation (security)"
                ]
            }
        }


def get_module_index() -> MobileModuleIndex:
    """Get the mobile module index instance."""
    return MobileModuleIndex()


def get_system_overview() -> Dict[str, Any]:
    """Get mobile system overview."""
    index = get_module_index()
    return index.get_system_overview()


def find_modules_for_purpose(purpose: str) -> List[MobileModuleInfo]:
    """Find mobile modules for specific business purpose."""
    index = get_module_index()
    return index.find_modules_for_purpose(purpose)


def find_modules_for_platform(platform: str) -> List[MobileModuleInfo]:
    """Find mobile modules for specific platform."""
    index = get_module_index()
    return index.find_modules_for_platform(platform)


# Module metadata
MOBILE_MODULE_INFO = {
    "name": "Mobile Infrastructure Index",
    "description": "Navigation and discovery system for all mobile modules",
    "version": "1.0.0",
    "author": "Fahed Mlaiel <mlaiel@live.de>",
    "purpose": "Professional mobile module organization and system overview"
}


if __name__ == "__main__":
    # Command-line interface for mobile module exploration
    import sys
    import json
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "overview":
            overview = get_system_overview()
            print(json.dumps(overview, indent=2))
        
        elif command == "modules":
            index = get_module_index()
            for name, info in index.get_all_modules().items():
                print(f"{name}: {info.description}")
        
        elif command == "platform" and len(sys.argv) > 2:
            platform = sys.argv[2]
            modules = find_modules_for_platform(platform)
            for module in modules:
                print(f"{module.name}: {module.business_purpose}")
        
        elif command == "find" and len(sys.argv) > 2:
            purpose = sys.argv[2]
            modules = find_modules_for_purpose(purpose)
            for module in modules:
                print(f"{module.name}: {module.business_purpose}")
        
        else:
            print("Usage: python index.py [overview|modules|platform <name>|find <purpose>]")
    else:
        print("Mobile Infrastructure Index - Use with commands: overview, modules, platform, find")