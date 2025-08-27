"""
🌍 Policy Manager - Ultra-Professional DRM Policy Engine
======================================================

Advanced geographical, device, and temporal policy management system for
comprehensive digital rights enforcement and compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing and usage rights.

🎯 PROJECT TEAM SPECIALTIES:
- Lead AI Developer & Solution Architect: Advanced AI/ML systems and intelligent automation
- Backend Senior Engineer: Enterprise-grade backend architecture and microservices  
- ML Engineer: Machine learning models and predictive analytics
- Database Administrator: High-performance data management and optimization
- Security Engineer: Advanced cybersecurity and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Professional audio processing and analysis
- DevOps Engineer: Advanced deployment and infrastructure automation
- IA Prompt Engineer: Advanced AI prompt engineering and optimization
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import geoip2.database
import geoip2.errors
from user_agents import parse
import re

logger = logging.getLogger(__name__)

class PolicyType(str, Enum):
    """Types of DRM policies."""
    GEOGRAPHICAL = "geographical"
    DEVICE = "device"
    TEMPORAL = "temporal"
    USAGE = "usage"
    NETWORK = "network"
    CONCURRENT = "concurrent"
    QUALITY = "quality"

class PolicyAction(str, Enum):
    """Actions for policy enforcement."""
    ALLOW = "allow"
    DENY = "deny"
    RESTRICT = "restrict"
    REDIRECT = "redirect"
    DEGRADE = "degrade"
    WATERMARK = "watermark"

class DeviceCategory(str, Enum):
    """Device categories for policies."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    TV = "tv"
    GAMING = "gaming"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"

class NetworkType(str, Enum):
    """Network types for policies."""
    CELLULAR = "cellular"
    WIFI = "wifi"
    ETHERNET = "ethernet"
    VPN = "vpn"
    SATELLITE = "satellite"
    UNKNOWN = "unknown"

@dataclass
class GeographicalPolicy:
    """Geographical restriction policy."""
    policy_id: str
    countries_allowed: Set[str] = field(default_factory=set)
    countries_denied: Set[str] = field(default_factory=set)
    regions_allowed: Set[str] = field(default_factory=set)
    regions_denied: Set[str] = field(default_factory=set)
    timezone_restrictions: Dict[str, Any] = field(default_factory=dict)
    vpn_policy: PolicyAction = PolicyAction.ALLOW
    proxy_policy: PolicyAction = PolicyAction.ALLOW
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DevicePolicy:
    """Device restriction policy."""
    policy_id: str
    allowed_categories: Set[DeviceCategory] = field(default_factory=set)
    denied_categories: Set[DeviceCategory] = field(default_factory=set)
    allowed_os: Set[str] = field(default_factory=set)
    denied_os: Set[str] = field(default_factory=set)
    min_os_version: Dict[str, str] = field(default_factory=dict)
    max_os_version: Dict[str, str] = field(default_factory=dict)
    allowed_browsers: Set[str] = field(default_factory=set)
    denied_browsers: Set[str] = field(default_factory=set)
    hardware_requirements: Dict[str, Any] = field(default_factory=dict)
    security_requirements: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalPolicy:
    """Time-based restriction policy."""
    policy_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    time_windows: List[Dict[str, Any]] = field(default_factory=list)
    blackout_periods: List[Dict[str, Any]] = field(default_factory=list)
    timezone: str = "UTC"
    recurring_schedule: Optional[Dict[str, Any]] = None
    embargo_duration: Optional[timedelta] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsagePolicy:
    """Content usage restriction policy."""
    policy_id: str
    max_concurrent_sessions: int = 1
    max_daily_usage: Optional[timedelta] = None
    max_weekly_usage: Optional[timedelta] = None
    max_monthly_usage: Optional[timedelta] = None
    cooldown_period: Optional[timedelta] = None
    quality_restrictions: Dict[str, Any] = field(default_factory=dict)
    feature_restrictions: Set[str] = field(default_factory=set)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyViolation:
    """Policy violation record."""
    violation_id: str
    policy_id: str
    policy_type: PolicyType
    user_id: str
    content_id: str
    violation_details: Dict[str, Any]
    action_taken: PolicyAction
    timestamp: datetime
    severity: str = "medium"
    resolved: bool = False

class PolicyManager:
    """Advanced DRM policy management system."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize policy manager with configuration."""
        self.config = config
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.violations: List[PolicyViolation] = []
        self.geoip_db_path = config.get("geoip_db_path", "/opt/geoip/GeoLite2-City.mmdb")
        self.cache_duration = timedelta(minutes=config.get("cache_minutes", 30))
        self.policy_cache: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize policy manager."""
        try:
            # Load default policies
            await self._load_default_policies()
            
            # Initialize GeoIP database
            await self._initialize_geoip()
            
            logger.info("Policy manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize policy manager: {e}")
            return False
    
    async def _load_default_policies(self) -> None:
        """Load default policy configurations."""
        # Geographical policy
        geo_policy = GeographicalPolicy(
            policy_id="default_geo",
            countries_allowed={"US", "CA", "GB", "DE", "FR", "AU"},
            vpn_policy=PolicyAction.RESTRICT,
            proxy_policy=PolicyAction.RESTRICT
        )
        self.policies["geographical"] = {"default_geo": geo_policy}
        
        # Device policy
        device_policy = DevicePolicy(
            policy_id="default_device",
            allowed_categories={DeviceCategory.MOBILE, DeviceCategory.DESKTOP, DeviceCategory.TABLET},
            min_os_version={"ios": "13.0", "android": "8.0", "windows": "10.0"}
        )
        self.policies["device"] = {"default_device": device_policy}
        
        # Temporal policy
        temporal_policy = TemporalPolicy(
            policy_id="default_temporal",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=365)
        )
        self.policies["temporal"] = {"default_temporal": temporal_policy}
        
        # Usage policy
        usage_policy = UsagePolicy(
            policy_id="default_usage",
            max_concurrent_sessions=3,
            max_daily_usage=timedelta(hours=8)
        )
        self.policies["usage"] = {"default_usage": usage_policy}
    
    async def _initialize_geoip(self) -> None:
        """Initialize GeoIP database."""
        try:
            self.geoip_reader = geoip2.database.Reader(self.geoip_db_path)
        except Exception as e:
            logger.warning(f"GeoIP database not available: {e}")
            self.geoip_reader = None
    
    async def evaluate_policies(
        self,
        content_id: str,
        user_id: str,
        request_context: Dict[str, Any]
    ) -> Tuple[bool, List[PolicyViolation]]:
        """Evaluate all applicable policies for a content access request."""
        violations = []
        access_allowed = True
        
        try:
            # Extract context information
            ip_address = request_context.get("ip_address")
            user_agent = request_context.get("user_agent")
            timestamp = request_context.get("timestamp", datetime.now(timezone.utc))
            
            # Evaluate geographical policies
            geo_violations = await self._evaluate_geographical_policies(
                content_id, user_id, ip_address, timestamp
            )
            violations.extend(geo_violations)
            
            # Evaluate device policies
            device_violations = await self._evaluate_device_policies(
                content_id, user_id, user_agent, timestamp
            )
            violations.extend(device_violations)
            
            # Evaluate temporal policies
            temporal_violations = await self._evaluate_temporal_policies(
                content_id, user_id, timestamp
            )
            violations.extend(temporal_violations)
            
            # Evaluate usage policies
            usage_violations = await self._evaluate_usage_policies(
                content_id, user_id, timestamp
            )
            violations.extend(usage_violations)
            
            # Check if any blocking violations occurred
            blocking_violations = [v for v in violations if v.action_taken == PolicyAction.DENY]
            access_allowed = len(blocking_violations) == 0
            
            # Log violations
            if violations:
                await self._log_violations(violations)
            
            return access_allowed, violations
            
        except Exception as e:
            logger.error(f"Error evaluating policies: {e}")
            return False, []
    
    async def _evaluate_geographical_policies(
        self,
        content_id: str,
        user_id: str,
        ip_address: Optional[str],
        timestamp: datetime
    ) -> List[PolicyViolation]:
        """Evaluate geographical restriction policies."""
        violations = []
        
        if not ip_address:
            return violations
        
        try:
            # Get location information
            location_info = await self._get_location_info(ip_address)
            if not location_info:
                return violations
            
            # Get applicable geographical policies
            geo_policies = self.policies.get("geographical", {})
            
            for policy_id, policy in geo_policies.items():
                if not policy.is_active:
                    continue
                
                country_code = location_info.get("country_code")
                
                # Check country restrictions
                if policy.countries_denied and country_code in policy.countries_denied:
                    violation = PolicyViolation(
                        violation_id=f"geo_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.GEOGRAPHICAL,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "country_code": country_code,
                            "reason": "country_denied"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                elif policy.countries_allowed and country_code not in policy.countries_allowed:
                    violation = PolicyViolation(
                        violation_id=f"geo_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.GEOGRAPHICAL,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "country_code": country_code,
                            "reason": "country_not_allowed"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check VPN/Proxy detection
                if location_info.get("is_vpn") and policy.vpn_policy == PolicyAction.DENY:
                    violation = PolicyViolation(
                        violation_id=f"vpn_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.GEOGRAPHICAL,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={"reason": "vpn_detected"},
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error evaluating geographical policies: {e}")
            return []
    
    async def _evaluate_device_policies(
        self,
        content_id: str,
        user_id: str,
        user_agent: Optional[str],
        timestamp: datetime
    ) -> List[PolicyViolation]:
        """Evaluate device restriction policies."""
        violations = []
        
        if not user_agent:
            return violations
        
        try:
            # Parse user agent
            device_info = await self._parse_device_info(user_agent)
            
            # Get applicable device policies
            device_policies = self.policies.get("device", {})
            
            for policy_id, policy in device_policies.items():
                if not policy.is_active:
                    continue
                
                device_category = device_info.get("category")
                os_name = device_info.get("os_name")
                os_version = device_info.get("os_version")
                browser_name = device_info.get("browser_name")
                
                # Check device category restrictions
                if policy.denied_categories and device_category in policy.denied_categories:
                    violation = PolicyViolation(
                        violation_id=f"device_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.DEVICE,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "device_category": device_category,
                            "reason": "device_category_denied"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                elif policy.allowed_categories and device_category not in policy.allowed_categories:
                    violation = PolicyViolation(
                        violation_id=f"device_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.DEVICE,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "device_category": device_category,
                            "reason": "device_category_not_allowed"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check OS restrictions
                if policy.denied_os and os_name in policy.denied_os:
                    violation = PolicyViolation(
                        violation_id=f"os_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.DEVICE,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "os_name": os_name,
                            "reason": "os_denied"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check OS version requirements
                if os_name in policy.min_os_version:
                    min_version = policy.min_os_version[os_name]
                    if self._compare_versions(os_version, min_version) < 0:
                        violation = PolicyViolation(
                            violation_id=f"os_version_{policy_id}_{timestamp.isoformat()}",
                            policy_id=policy_id,
                            policy_type=PolicyType.DEVICE,
                            user_id=user_id,
                            content_id=content_id,
                            violation_details={
                                "os_version": os_version,
                                "min_required": min_version,
                                "reason": "os_version_too_old"
                            },
                            action_taken=PolicyAction.DENY,
                            timestamp=timestamp
                        )
                        violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error evaluating device policies: {e}")
            return []
    
    async def _evaluate_temporal_policies(
        self,
        content_id: str,
        user_id: str,
        timestamp: datetime
    ) -> List[PolicyViolation]:
        """Evaluate temporal restriction policies."""
        violations = []
        
        try:
            # Get applicable temporal policies
            temporal_policies = self.policies.get("temporal", {})
            
            for policy_id, policy in temporal_policies.items():
                if not policy.is_active:
                    continue
                
                # Check date range
                if policy.start_date and timestamp < policy.start_date:
                    violation = PolicyViolation(
                        violation_id=f"temporal_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.TEMPORAL,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "current_time": timestamp.isoformat(),
                            "start_time": policy.start_date.isoformat(),
                            "reason": "before_start_date"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                if policy.end_date and timestamp > policy.end_date:
                    violation = PolicyViolation(
                        violation_id=f"temporal_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.TEMPORAL,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "current_time": timestamp.isoformat(),
                            "end_time": policy.end_date.isoformat(),
                            "reason": "after_end_date"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check time windows
                if policy.time_windows:
                    allowed_window = await self._check_time_windows(timestamp, policy.time_windows)
                    if not allowed_window:
                        violation = PolicyViolation(
                            violation_id=f"time_window_{policy_id}_{timestamp.isoformat()}",
                            policy_id=policy_id,
                            policy_type=PolicyType.TEMPORAL,
                            user_id=user_id,
                            content_id=content_id,
                            violation_details={
                                "current_time": timestamp.isoformat(),
                                "reason": "outside_allowed_time_window"
                            },
                            action_taken=PolicyAction.DENY,
                            timestamp=timestamp
                        )
                        violations.append(violation)
                
                # Check blackout periods
                if policy.blackout_periods:
                    in_blackout = await self._check_blackout_periods(timestamp, policy.blackout_periods)
                    if in_blackout:
                        violation = PolicyViolation(
                            violation_id=f"blackout_{policy_id}_{timestamp.isoformat()}",
                            policy_id=policy_id,
                            policy_type=PolicyType.TEMPORAL,
                            user_id=user_id,
                            content_id=content_id,
                            violation_details={
                                "current_time": timestamp.isoformat(),
                                "reason": "in_blackout_period"
                            },
                            action_taken=PolicyAction.DENY,
                            timestamp=timestamp
                        )
                        violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error evaluating temporal policies: {e}")
            return []
    
    async def _evaluate_usage_policies(
        self,
        content_id: str,
        user_id: str,
        timestamp: datetime
    ) -> List[PolicyViolation]:
        """Evaluate usage restriction policies."""
        violations = []
        
        try:
            # Get applicable usage policies
            usage_policies = self.policies.get("usage", {})
            
            for policy_id, policy in usage_policies.items():
                if not policy.is_active:
                    continue
                
                # Check concurrent sessions
                current_sessions = await self._get_concurrent_sessions(user_id, content_id)
                if current_sessions >= policy.max_concurrent_sessions:
                    violation = PolicyViolation(
                        violation_id=f"concurrent_{policy_id}_{timestamp.isoformat()}",
                        policy_id=policy_id,
                        policy_type=PolicyType.USAGE,
                        user_id=user_id,
                        content_id=content_id,
                        violation_details={
                            "current_sessions": current_sessions,
                            "max_allowed": policy.max_concurrent_sessions,
                            "reason": "max_concurrent_sessions_exceeded"
                        },
                        action_taken=PolicyAction.DENY,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check daily usage limits
                if policy.max_daily_usage:
                    daily_usage = await self._get_daily_usage(user_id, content_id, timestamp)
                    if daily_usage >= policy.max_daily_usage:
                        violation = PolicyViolation(
                            violation_id=f"daily_usage_{policy_id}_{timestamp.isoformat()}",
                            policy_id=policy_id,
                            policy_type=PolicyType.USAGE,
                            user_id=user_id,
                            content_id=content_id,
                            violation_details={
                                "daily_usage": str(daily_usage),
                                "max_allowed": str(policy.max_daily_usage),
                                "reason": "daily_usage_limit_exceeded"
                            },
                            action_taken=PolicyAction.DENY,
                            timestamp=timestamp
                        )
                        violations.append(violation)
            
            return violations
            
        except Exception as e:
            logger.error(f"Error evaluating usage policies: {e}")
            return []
    
    async def _get_location_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location information for an IP address."""
        try:
            if not self.geoip_reader:
                return None
            
            response = self.geoip_reader.city(ip_address)
            
            return {
                "country_code": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "latitude": float(response.location.latitude or 0),
                "longitude": float(response.location.longitude or 0),
                "is_vpn": self._detect_vpn(ip_address),
                "is_proxy": self._detect_proxy(ip_address)
            }
            
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"IP address not found in GeoIP database: {ip_address}")
            return None
        except Exception as e:
            logger.error(f"Error getting location info: {e}")
            return None
    
    async def _parse_device_info(self, user_agent: str) -> Dict[str, Any]:
        """Parse device information from user agent."""
        try:
            parsed = parse(user_agent)
            
            # Determine device category
            if parsed.is_mobile:
                category = DeviceCategory.MOBILE
            elif parsed.is_tablet:
                category = DeviceCategory.TABLET
            elif parsed.is_pc:
                category = DeviceCategory.DESKTOP
            else:
                category = DeviceCategory.UNKNOWN
            
            return {
                "category": category,
                "os_name": parsed.os.family.lower() if parsed.os.family else "unknown",
                "os_version": parsed.os.version_string or "unknown",
                "browser_name": parsed.browser.family.lower() if parsed.browser.family else "unknown",
                "browser_version": parsed.browser.version_string or "unknown",
                "device_brand": getattr(parsed.device, 'brand', 'unknown'),
                "device_model": getattr(parsed.device, 'model', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error parsing device info: {e}")
            return {
                "category": DeviceCategory.UNKNOWN,
                "os_name": "unknown",
                "os_version": "unknown",
                "browser_name": "unknown",
                "browser_version": "unknown"
            }
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns -1, 0, or 1."""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad with zeros to make equal length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            
            return 0
            
        except Exception:
            return 0
    
    async def _check_time_windows(self, timestamp: datetime, time_windows: List[Dict[str, Any]]) -> bool:
        """Check if timestamp falls within allowed time windows."""
        for window in time_windows:
            start_time = datetime.fromisoformat(window["start"]).time()
            end_time = datetime.fromisoformat(window["end"]).time()
            current_time = timestamp.time()
            
            if start_time <= current_time <= end_time:
                return True
        
        return False
    
    async def _check_blackout_periods(self, timestamp: datetime, blackout_periods: List[Dict[str, Any]]) -> bool:
        """Check if timestamp falls within blackout periods."""
        for period in blackout_periods:
            start_date = datetime.fromisoformat(period["start"])
            end_date = datetime.fromisoformat(period["end"])
            
            if start_date <= timestamp <= end_date:
                return True
        
        return False
    
    async def _get_concurrent_sessions(self, user_id: str, content_id: str) -> int:
        """Get current number of concurrent sessions for user and content."""
        # This would integrate with session management system
        # For now, return a placeholder value
        return 0
    
    async def _get_daily_usage(self, user_id: str, content_id: str, timestamp: datetime) -> timedelta:
        """Get daily usage for user and content."""
        # This would integrate with usage tracking system
        # For now, return a placeholder value
        return timedelta(0)
    
    def _detect_vpn(self, ip_address: str) -> bool:
        """Detect if IP address is from a VPN."""
        # This would integrate with VPN detection service
        # For now, return a placeholder value
        return False
    
    def _detect_proxy(self, ip_address: str) -> bool:
        """Detect if IP address is from a proxy."""
        # This would integrate with proxy detection service
        # For now, return a placeholder value
        return False
    
    async def _log_violations(self, violations: List[PolicyViolation]) -> None:
        """Log policy violations."""
        for violation in violations:
            logger.warning(f"Policy violation: {violation.violation_id} - {violation.violation_details}")
            self.violations.append(violation)
    
    async def create_policy(self, policy_type: str, policy_data: Dict[str, Any]) -> str:
        """Create a new policy."""
        try:
            policy_id = f"{policy_type}_{datetime.now().isoformat()}"
            
            if policy_type not in self.policies:
                self.policies[policy_type] = {}
            
            self.policies[policy_type][policy_id] = policy_data
            
            logger.info(f"Policy created: {policy_id}")
            return policy_id
            
        except Exception as e:
            logger.error(f"Error creating policy: {e}")
            raise
    
    async def update_policy(self, policy_type: str, policy_id: str, policy_data: Dict[str, Any]) -> bool:
        """Update an existing policy."""
        try:
            if policy_type in self.policies and policy_id in self.policies[policy_type]:
                self.policies[policy_type][policy_id].update(policy_data)
                logger.info(f"Policy updated: {policy_id}")
                return True
            else:
                logger.warning(f"Policy not found: {policy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating policy: {e}")
            return False
    
    async def delete_policy(self, policy_type: str, policy_id: str) -> bool:
        """Delete a policy."""
        try:
            if policy_type in self.policies and policy_id in self.policies[policy_type]:
                del self.policies[policy_type][policy_id]
                logger.info(f"Policy deleted: {policy_id}")
                return True
            else:
                logger.warning(f"Policy not found: {policy_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting policy: {e}")
            return False
    
    async def get_violations(
        self,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PolicyViolation]:
        """Get policy violations with optional filters."""
        filtered_violations = self.violations
        
        if user_id:
            filtered_violations = [v for v in filtered_violations if v.user_id == user_id]
        
        if content_id:
            filtered_violations = [v for v in filtered_violations if v.content_id == content_id]
        
        if start_date:
            filtered_violations = [v for v in filtered_violations if v.timestamp >= start_date]
        
        if end_date:
            filtered_violations = [v for v in filtered_violations if v.timestamp <= end_date]
        
        return filtered_violations
    
    async def get_policy_statistics(self) -> Dict[str, Any]:
        """Get policy enforcement statistics."""
        try:
            stats = {
                "total_policies": sum(len(policies) for policies in self.policies.values()),
                "active_policies": sum(
                    len([p for p in policies.values() if getattr(p, 'is_active', True)])
                    for policies in self.policies.values()
                ),
                "total_violations": len(self.violations),
                "violations_by_type": {},
                "violations_by_action": {}
            }
            
            # Count violations by type
            for violation in self.violations:
                policy_type = violation.policy_type.value
                stats["violations_by_type"][policy_type] = stats["violations_by_type"].get(policy_type, 0) + 1
                
                action = violation.action_taken.value
                stats["violations_by_action"][action] = stats["violations_by_action"].get(action, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting policy statistics: {e}")
            return {}

    async def cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if hasattr(self, 'geoip_reader') and self.geoip_reader:
                self.geoip_reader.close()
            
            logger.info("Policy manager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during policy manager cleanup: {e}")
