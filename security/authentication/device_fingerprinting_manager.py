#!/usr/bin/env python3
"""
🔒 Device Fingerprinting Manager - Advanced Device Security
==========================================================

Ultra-secure device fingerprinting and tracking system with anti-evasion
detection, trusted device management, and Creator Economy specific security.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + ML + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import hashlib
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import ipaddress
from collections import defaultdict
import secrets
import re

# Configure logging
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Device type classifications"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    GAMING_CONSOLE = "gaming_console"
    IOT_DEVICE = "iot_device"
    UNKNOWN = "unknown"


class TrustLevel(Enum):
    """Device trust levels"""
    UNTRUSTED = "untrusted"
    NEW = "new"
    RECOGNIZED = "recognized"
    TRUSTED = "trusted"
    HIGHLY_TRUSTED = "highly_trusted"


class FingerprintComponent(Enum):
    """Components used in device fingerprinting"""
    USER_AGENT = "user_agent"
    SCREEN_RESOLUTION = "screen_resolution"
    TIMEZONE = "timezone"
    LANGUAGE = "language"
    PLATFORM = "platform"
    CANVAS_FINGERPRINT = "canvas_fingerprint"
    WEBGL_FINGERPRINT = "webgl_fingerprint"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    FONTS_LIST = "fonts_list"
    PLUGINS_LIST = "plugins_list"
    HARDWARE_SPECS = "hardware_specs"
    NETWORK_INFO = "network_info"


class SecurityEvent(Enum):
    """Security events related to device fingerprinting"""
    NEW_DEVICE_DETECTED = "new_device_detected"
    DEVICE_CHANGE_DETECTED = "device_change_detected"
    FINGERPRINT_EVASION_ATTEMPT = "fingerprint_evasion_attempt"
    SUSPICIOUS_DEVICE_PATTERN = "suspicious_device_pattern"
    DEVICE_CLONING_DETECTED = "device_cloning_detected"
    TRUSTED_DEVICE_COMPROMISED = "trusted_device_compromised"


@dataclass
class DeviceFingerprint:
    """Complete device fingerprint data"""
    fingerprint_id: str
    user_id: str
    creation_timestamp: datetime
    last_seen: datetime
    
    # Technical fingerprint components
    user_agent: str
    screen_resolution: str
    timezone: str
    language: str
    platform: str
    canvas_hash: Optional[str] = None
    webgl_hash: Optional[str] = None
    audio_hash: Optional[str] = None
    fonts_hash: Optional[str] = None
    plugins_hash: Optional[str] = None
    
    # Hardware and network information
    hardware_specs: Dict[str, Any] = field(default_factory=dict)
    network_info: Dict[str, Any] = field(default_factory=dict)
    
    # Security and trust information
    trust_level: TrustLevel = TrustLevel.NEW
    device_type: DeviceType = DeviceType.UNKNOWN
    is_verified: bool = False
    verification_method: Optional[str] = None
    
    # Behavioral data
    usage_patterns: Dict[str, Any] = field(default_factory=dict)
    location_history: List[Dict[str, str]] = field(default_factory=list)
    
    # Security events
    security_events: List[Dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.5
    
    # Creator Economy specific
    creator_activities: Dict[str, Any] = field(default_factory=dict)
    content_creation_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FingerprintAnalysis:
    """Analysis result of device fingerprint"""
    fingerprint_id: str
    is_new_device: bool
    similarity_score: float
    trust_level: TrustLevel
    risk_assessment: Dict[str, Any]
    detected_changes: List[str]
    security_alerts: List[SecurityEvent]
    recommendations: List[str]
    confidence: float


@dataclass
class DeviceFingerprintingConfig:
    """Configuration for device fingerprinting"""
    fingerprint_expiry_days: int = 365
    similarity_threshold: float = 0.85
    trust_promotion_threshold: int = 10  # Number of successful logins
    max_devices_per_user: int = 20
    enable_canvas_fingerprinting: bool = True
    enable_audio_fingerprinting: bool = True
    enable_webgl_fingerprinting: bool = True
    enable_behavioral_analysis: bool = True
    track_hardware_changes: bool = True
    detect_virtualization: bool = True
    creator_security_mode: bool = True


class DeviceFingerprintingManager:
    """
    🔒 Advanced Device Fingerprinting Manager - Enterprise Security
    
    Features:
    - Multi-dimensional device fingerprinting
    - Canvas, WebGL, and Audio fingerprinting
    - Anti-fingerprinting evasion detection
    - Trusted device management
    - Behavioral pattern analysis
    - Creator Economy specific tracking
    - Hardware change detection
    - Virtualization and emulation detection
    - Device cloning detection
    - Risk-based device assessment
    """
    
    def __init__(self, config: Optional[DeviceFingerprintingConfig] = None):
        self.config = config or DeviceFingerprintingConfig()
        self.device_fingerprints: Dict[str, DeviceFingerprint] = {}
        self.user_devices: Dict[str, Set[str]] = defaultdict(set)
        self.fingerprint_components: Dict[str, Any] = {}
        self.security_events: List[Dict[str, Any]] = []
        
        # Initialize fingerprinting components
        self._initialize_fingerprinting_components()
        
        logger.info("🔒 Device Fingerprinting Manager initialized")
    
    def _initialize_fingerprinting_components(self) -> None:
        """Initialize fingerprinting detection components"""
        try:
            # Canvas fingerprinting patterns
            self.fingerprint_components["canvas_patterns"] = {
                "font_rendering": ["Arial", "Times New Roman", "Courier", "Helvetica"],
                "emoji_rendering": ["😀", "🎵", "🎨", "📱", "💻"],
                "geometric_shapes": ["circles", "rectangles", "bezier_curves"],
                "text_metrics": ["baseline", "width", "height", "advance"]
            }
            
            # WebGL fingerprinting components
            self.fingerprint_components["webgl_parameters"] = [
                "VENDOR", "RENDERER", "VERSION", "SHADING_LANGUAGE_VERSION",
                "MAX_TEXTURE_SIZE", "MAX_VIEWPORT_DIMS", "MAX_VERTEX_ATTRIBS"
            ]
            
            # Audio fingerprinting setup
            self.fingerprint_components["audio_context"] = {
                "sample_rate": 44100,
                "oscillator_types": ["sine", "square", "sawtooth", "triangle"],
                "frequencies": [440, 523, 659, 784]  # A4, C5, E5, G5
            }
            
            # Common font lists for fingerprinting
            self.fingerprint_components["common_fonts"] = [
                "Arial", "Helvetica", "Times New Roman", "Courier", "Verdana",
                "Georgia", "Palatino", "Garamond", "Comic Sans MS", "Trebuchet MS",
                "Arial Black", "Impact", "Tahoma", "Century Gothic", "Lucida Console"
            ]
            
            # Known virtualization indicators
            self.fingerprint_components["virtualization_indicators"] = {
                "vm_vendors": ["VMware", "VirtualBox", "Parallels", "QEMU", "Xen"],
                "vm_hardware": ["Virtual", "VMware", "VBox", "VBOX"],
                "vm_network": ["VMware", "VirtualBox", "Parallels"]
            }
            
            logger.info("✅ Fingerprinting components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize fingerprinting components: {e}")
    
    async def generate_device_fingerprint(
        self,
        user_id: str,
        fingerprint_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> DeviceFingerprint:
        """
        Generate comprehensive device fingerprint
        
        Args:
            user_id: User identifier
            fingerprint_data: Raw fingerprint data from client
            context: Additional context (creator type, risk level, etc.)
        
        Returns:
            DeviceFingerprint: Generated device fingerprint
        """
        try:
            # Generate unique fingerprint ID
            fingerprint_components = [
                fingerprint_data.get("user_agent", ""),
                fingerprint_data.get("screen_resolution", ""),
                fingerprint_data.get("timezone", ""),
                fingerprint_data.get("language", ""),
                fingerprint_data.get("platform", "")
            ]
            
            # Add advanced fingerprinting components
            if self.config.enable_canvas_fingerprinting and fingerprint_data.get("canvas_data"):
                canvas_hash = await self._generate_canvas_fingerprint(fingerprint_data["canvas_data"])
                fingerprint_components.append(canvas_hash)
            else:
                canvas_hash = None
            
            if self.config.enable_webgl_fingerprinting and fingerprint_data.get("webgl_data"):
                webgl_hash = await self._generate_webgl_fingerprint(fingerprint_data["webgl_data"])
                fingerprint_components.append(webgl_hash)
            else:
                webgl_hash = None
            
            if self.config.enable_audio_fingerprinting and fingerprint_data.get("audio_data"):
                audio_hash = await self._generate_audio_fingerprint(fingerprint_data["audio_data"])
                fingerprint_components.append(audio_hash)
            else:
                audio_hash = None
            
            # Generate font and plugin hashes
            fonts_hash = await self._generate_fonts_fingerprint(fingerprint_data.get("fonts", []))
            plugins_hash = await self._generate_plugins_fingerprint(fingerprint_data.get("plugins", []))
            
            # Create master fingerprint ID
            master_string = "|".join(filter(None, fingerprint_components))
            fingerprint_id = hashlib.sha256(master_string.encode()).hexdigest()
            
            # Determine device type
            device_type = self._determine_device_type(fingerprint_data)
            
            # Create fingerprint object
            now = datetime.utcnow()
            fingerprint = DeviceFingerprint(
                fingerprint_id=fingerprint_id,
                user_id=user_id,
                creation_timestamp=now,
                last_seen=now,
                user_agent=fingerprint_data.get("user_agent", ""),
                screen_resolution=fingerprint_data.get("screen_resolution", ""),
                timezone=fingerprint_data.get("timezone", ""),
                language=fingerprint_data.get("language", ""),
                platform=fingerprint_data.get("platform", ""),
                canvas_hash=canvas_hash,
                webgl_hash=webgl_hash,
                audio_hash=audio_hash,
                fonts_hash=fonts_hash,
                plugins_hash=plugins_hash,
                device_type=device_type,
                hardware_specs=fingerprint_data.get("hardware", {}),
                network_info=fingerprint_data.get("network", {})
            )
            
            # Apply Creator Economy specific enhancements
            if context and context.get("creator_type"):
                await self._enhance_creator_fingerprint(fingerprint, context)
            
            # Store fingerprint
            self.device_fingerprints[fingerprint_id] = fingerprint
            self.user_devices[user_id].add(fingerprint_id)
            
            # Limit devices per user
            await self._enforce_device_limits(user_id)
            
            logger.info(f"✅ Generated device fingerprint {fingerprint_id[:8]}... for user {user_id}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"❌ Device fingerprint generation failed: {e}")
            raise RuntimeError(f"Fingerprint generation error: {e}")
    
    async def detect_device_changes(
        self,
        user_id: str,
        current_fingerprint_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> FingerprintAnalysis:
        """
        Detect changes in device fingerprint
        
        Args:
            user_id: User identifier
            current_fingerprint_data: Current fingerprint data
            context: Analysis context
        
        Returns:
            FingerprintAnalysis: Change detection analysis
        """
        try:
            # Generate current fingerprint
            current_fingerprint = await self.generate_device_fingerprint(
                user_id, current_fingerprint_data, context
            )
            
            # Get user's existing devices
            user_device_ids = self.user_devices.get(user_id, set())
            existing_fingerprints = [
                self.device_fingerprints[fid] for fid in user_device_ids
                if fid in self.device_fingerprints
            ]
            
            if not existing_fingerprints:
                # First device for user
                return FingerprintAnalysis(
                    fingerprint_id=current_fingerprint.fingerprint_id,
                    is_new_device=True,
                    similarity_score=0.0,
                    trust_level=TrustLevel.NEW,
                    risk_assessment={"risk_level": "medium", "reason": "first_device"},
                    detected_changes=[],
                    security_alerts=[SecurityEvent.NEW_DEVICE_DETECTED],
                    recommendations=["Verify device ownership"],
                    confidence=1.0
                )
            
            # Find most similar existing device
            best_match = None
            highest_similarity = 0.0
            
            for existing_fp in existing_fingerprints:
                similarity = await self._calculate_fingerprint_similarity(
                    current_fingerprint, existing_fp
                )
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = existing_fp
            
            # Analyze changes
            detected_changes = []
            security_alerts = []
            
            if highest_similarity >= self.config.similarity_threshold:
                # Device recognized - check for changes
                if best_match:
                    changes = await self._detect_component_changes(current_fingerprint, best_match)
                    detected_changes.extend(changes)
                    
                    # Update existing fingerprint
                    best_match.last_seen = datetime.utcnow()
                    await self._update_fingerprint_data(best_match, current_fingerprint)
                    
                is_new_device = False
                trust_level = best_match.trust_level if best_match else TrustLevel.RECOGNIZED
            else:
                # New device detected
                is_new_device = True
                trust_level = TrustLevel.NEW
                security_alerts.append(SecurityEvent.NEW_DEVICE_DETECTED)
            
            # Check for suspicious patterns
            suspicious_patterns = await self._detect_suspicious_patterns(
                current_fingerprint, existing_fingerprints
            )
            security_alerts.extend(suspicious_patterns)
            
            # Check for fingerprint evasion attempts
            evasion_attempts = await self._detect_fingerprint_evasion(
                current_fingerprint, context
            )
            if evasion_attempts:
                security_alerts.append(SecurityEvent.FINGERPRINT_EVASION_ATTEMPT)
                detected_changes.extend(evasion_attempts)
            
            # Risk assessment
            risk_assessment = await self._assess_device_risk(
                current_fingerprint, existing_fingerprints, detected_changes, security_alerts
            )
            
            # Generate recommendations
            recommendations = await self._generate_security_recommendations(
                security_alerts, detected_changes, risk_assessment
            )
            
            # Calculate confidence
            confidence = self._calculate_analysis_confidence(
                len(existing_fingerprints), len(detected_changes), highest_similarity
            )
            
            return FingerprintAnalysis(
                fingerprint_id=current_fingerprint.fingerprint_id,
                is_new_device=is_new_device,
                similarity_score=highest_similarity,
                trust_level=trust_level,
                risk_assessment=risk_assessment,
                detected_changes=detected_changes,
                security_alerts=security_alerts,
                recommendations=recommendations,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"❌ Device change detection failed: {e}")
            raise RuntimeError(f"Device change detection error: {e}")
    
    async def manage_trusted_devices(
        self,
        user_id: str,
        action: str,
        fingerprint_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage trusted devices for a user
        
        Args:
            user_id: User identifier
            action: Management action (list, trust, untrust, remove)
            fingerprint_id: Device fingerprint ID (for specific actions)
            context: Management context
        
        Returns:
            Dict[str, Any]: Management operation result
        """
        try:
            user_device_ids = self.user_devices.get(user_id, set())
            
            if action == "list":
                # List all devices for user
                devices = []
                for fid in user_device_ids:
                    if fid in self.device_fingerprints:
                        fp = self.device_fingerprints[fid]
                        devices.append({
                            "fingerprint_id": fid,
                            "device_type": fp.device_type.value,
                            "trust_level": fp.trust_level.value,
                            "last_seen": fp.last_seen.isoformat(),
                            "platform": fp.platform,
                            "is_verified": fp.is_verified,
                            "risk_score": fp.risk_score
                        })
                
                return {
                    "action": "list",
                    "user_id": user_id,
                    "device_count": len(devices),
                    "devices": devices
                }
            
            elif action == "trust" and fingerprint_id:
                # Mark device as trusted
                if fingerprint_id in self.device_fingerprints:
                    fp = self.device_fingerprints[fingerprint_id]
                    if fp.user_id == user_id:
                        fp.trust_level = TrustLevel.TRUSTED
                        fp.is_verified = True
                        fp.verification_method = context.get("verification_method", "manual")
                        
                        # Log security event
                        await self._log_security_event(
                            user_id, SecurityEvent.NEW_DEVICE_DETECTED,
                            {"fingerprint_id": fingerprint_id, "action": "trusted"}
                        )
                        
                        return {
                            "action": "trust",
                            "fingerprint_id": fingerprint_id,
                            "status": "success",
                            "new_trust_level": fp.trust_level.value
                        }
                
                return {"action": "trust", "status": "failed", "reason": "device_not_found"}
            
            elif action == "untrust" and fingerprint_id:
                # Remove trust from device
                if fingerprint_id in self.device_fingerprints:
                    fp = self.device_fingerprints[fingerprint_id]
                    if fp.user_id == user_id:
                        fp.trust_level = TrustLevel.RECOGNIZED
                        fp.is_verified = False
                        
                        return {
                            "action": "untrust",
                            "fingerprint_id": fingerprint_id,
                            "status": "success",
                            "new_trust_level": fp.trust_level.value
                        }
                
                return {"action": "untrust", "status": "failed", "reason": "device_not_found"}
            
            elif action == "remove" and fingerprint_id:
                # Remove device completely
                if fingerprint_id in self.device_fingerprints:
                    fp = self.device_fingerprints[fingerprint_id]
                    if fp.user_id == user_id:
                        del self.device_fingerprints[fingerprint_id]
                        self.user_devices[user_id].discard(fingerprint_id)
                        
                        return {
                            "action": "remove",
                            "fingerprint_id": fingerprint_id,
                            "status": "success"
                        }
                
                return {"action": "remove", "status": "failed", "reason": "device_not_found"}
            
            else:
                return {"action": action, "status": "failed", "reason": "invalid_action"}
            
        except Exception as e:
            logger.error(f"❌ Trusted device management failed: {e}")
            raise RuntimeError(f"Device management error: {e}")
    
    async def detect_fingerprint_evasion(
        self,
        user_id: str,
        fingerprint_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Detect fingerprint evasion attempts
        
        Args:
            user_id: User identifier
            fingerprint_data: Fingerprint data to analyze
            context: Detection context
        
        Returns:
            List[str]: Detected evasion techniques
        """
        try:
            evasion_indicators = []
            
            # Check for randomized values
            if self._detect_randomized_fingerprint(fingerprint_data):
                evasion_indicators.append("randomized_fingerprint_values")
            
            # Check for virtualization
            if self._detect_virtualization(fingerprint_data):
                evasion_indicators.append("virtualized_environment")
            
            # Check for browser automation tools
            if self._detect_automation_tools(fingerprint_data):
                evasion_indicators.append("browser_automation_detected")
            
            # Check for fingerprint spoofing
            if self._detect_fingerprint_spoofing(fingerprint_data):
                evasion_indicators.append("fingerprint_spoofing_detected")
            
            # Check for proxy/VPN usage patterns
            if self._detect_proxy_vpn_patterns(fingerprint_data):
                evasion_indicators.append("proxy_vpn_usage_detected")
            
            # Check for canvas/WebGL blocking
            if self._detect_fingerprint_blocking(fingerprint_data):
                evasion_indicators.append("fingerprint_blocking_detected")
            
            if evasion_indicators:
                # Log security event
                await self._log_security_event(
                    user_id, SecurityEvent.FINGERPRINT_EVASION_ATTEMPT,
                    {"evasion_techniques": evasion_indicators, "fingerprint_data": fingerprint_data}
                )
                
                logger.warning(f"⚠️ Fingerprint evasion detected for user {user_id}: {evasion_indicators}")
            
            return evasion_indicators
            
        except Exception as e:
            logger.error(f"❌ Fingerprint evasion detection failed: {e}")
            return []
    
    async def _generate_canvas_fingerprint(self, canvas_data: Dict[str, Any]) -> str:
        """Generate canvas fingerprint hash"""
        try:
            # Simulate canvas fingerprinting (in production, process actual canvas data)
            canvas_components = [
                canvas_data.get("text_metrics", ""),
                canvas_data.get("font_rendering", ""),
                canvas_data.get("color_depth", ""),
                canvas_data.get("pixel_data", "")
            ]
            
            canvas_string = "|".join(filter(None, canvas_components))
            return hashlib.md5(canvas_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Canvas fingerprint generation failed: {e}")
            return "canvas_error"
    
    async def _generate_webgl_fingerprint(self, webgl_data: Dict[str, Any]) -> str:
        """Generate WebGL fingerprint hash"""
        try:
            webgl_components = [
                webgl_data.get("vendor", ""),
                webgl_data.get("renderer", ""),
                webgl_data.get("version", ""),
                webgl_data.get("extensions", ""),
                str(webgl_data.get("parameters", {}))
            ]
            
            webgl_string = "|".join(filter(None, webgl_components))
            return hashlib.md5(webgl_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ WebGL fingerprint generation failed: {e}")
            return "webgl_error"
    
    async def _generate_audio_fingerprint(self, audio_data: Dict[str, Any]) -> str:
        """Generate audio context fingerprint hash"""
        try:
            audio_components = [
                str(audio_data.get("sample_rate", "")),
                str(audio_data.get("buffer_size", "")),
                str(audio_data.get("oscillator_data", "")),
                str(audio_data.get("dynamics_compressor", ""))
            ]
            
            audio_string = "|".join(filter(None, audio_components))
            return hashlib.md5(audio_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Audio fingerprint generation failed: {e}")
            return "audio_error"
    
    async def _generate_fonts_fingerprint(self, fonts_list: List[str]) -> str:
        """Generate fonts fingerprint hash"""
        try:
            # Sort fonts for consistent hashing
            sorted_fonts = sorted(set(fonts_list))
            fonts_string = "|".join(sorted_fonts)
            return hashlib.md5(fonts_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Fonts fingerprint generation failed: {e}")
            return "fonts_error"
    
    async def _generate_plugins_fingerprint(self, plugins_list: List[str]) -> str:
        """Generate plugins fingerprint hash"""
        try:
            # Sort plugins for consistent hashing
            sorted_plugins = sorted(set(plugins_list))
            plugins_string = "|".join(sorted_plugins)
            return hashlib.md5(plugins_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Plugins fingerprint generation failed: {e}")
            return "plugins_error"
    
    def _determine_device_type(self, fingerprint_data: Dict[str, Any]) -> DeviceType:
        """Determine device type from fingerprint data"""
        user_agent = fingerprint_data.get("user_agent", "").lower()
        screen_resolution = fingerprint_data.get("screen_resolution", "")
        
        # Mobile detection
        mobile_indicators = ["mobile", "android", "iphone", "ipad", "tablet"]
        if any(indicator in user_agent for indicator in mobile_indicators):
            if "ipad" in user_agent or "tablet" in user_agent:
                return DeviceType.TABLET
            return DeviceType.MOBILE
        
        # TV detection
        tv_indicators = ["tv", "smarttv", "appletv", "roku", "chromecast"]
        if any(indicator in user_agent for indicator in tv_indicators):
            return DeviceType.TV
        
        # Gaming console detection
        console_indicators = ["playstation", "xbox", "nintendo", "steam"]
        if any(indicator in user_agent for indicator in console_indicators):
            return DeviceType.GAMING_CONSOLE
        
        # Desktop/laptop (default)
        return DeviceType.DESKTOP
    
    async def _calculate_fingerprint_similarity(
        self,
        fp1: DeviceFingerprint,
        fp2: DeviceFingerprint
    ) -> float:
        """Calculate similarity between two fingerprints"""
        try:
            similarity_scores = []
            
            # Compare basic components
            basic_components = [
                ("user_agent", fp1.user_agent, fp2.user_agent),
                ("screen_resolution", fp1.screen_resolution, fp2.screen_resolution),
                ("timezone", fp1.timezone, fp2.timezone),
                ("language", fp1.language, fp2.language),
                ("platform", fp1.platform, fp2.platform)
            ]
            
            for name, val1, val2 in basic_components:
                if val1 and val2:
                    similarity = 1.0 if val1 == val2 else 0.0
                    similarity_scores.append(similarity)
            
            # Compare hash components
            hash_components = [
                ("canvas", fp1.canvas_hash, fp2.canvas_hash),
                ("webgl", fp1.webgl_hash, fp2.webgl_hash),
                ("audio", fp1.audio_hash, fp2.audio_hash),
                ("fonts", fp1.fonts_hash, fp2.fonts_hash),
                ("plugins", fp1.plugins_hash, fp2.plugins_hash)
            ]
            
            for name, hash1, hash2 in hash_components:
                if hash1 and hash2:
                    similarity = 1.0 if hash1 == hash2 else 0.0
                    similarity_scores.append(similarity * 1.5)  # Higher weight for stable components
            
            # Calculate weighted average
            if similarity_scores:
                return sum(similarity_scores) / len(similarity_scores)
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"❌ Fingerprint similarity calculation failed: {e}")
            return 0.0
    
    async def _detect_component_changes(
        self,
        current_fp: DeviceFingerprint,
        previous_fp: DeviceFingerprint
    ) -> List[str]:
        """Detect changes between fingerprint components"""
        changes = []
        
        # Check for component changes
        if current_fp.user_agent != previous_fp.user_agent:
            changes.append("user_agent_changed")
        
        if current_fp.screen_resolution != previous_fp.screen_resolution:
            changes.append("screen_resolution_changed")
        
        if current_fp.timezone != previous_fp.timezone:
            changes.append("timezone_changed")
        
        if current_fp.language != previous_fp.language:
            changes.append("language_changed")
        
        if current_fp.canvas_hash != previous_fp.canvas_hash:
            changes.append("canvas_fingerprint_changed")
        
        if current_fp.webgl_hash != previous_fp.webgl_hash:
            changes.append("webgl_fingerprint_changed")
        
        if current_fp.fonts_hash != previous_fp.fonts_hash:
            changes.append("fonts_changed")
        
        if current_fp.plugins_hash != previous_fp.plugins_hash:
            changes.append("plugins_changed")
        
        return changes
    
    async def _detect_suspicious_patterns(
        self,
        current_fp: DeviceFingerprint,
        existing_fps: List[DeviceFingerprint]
    ) -> List[SecurityEvent]:
        """Detect suspicious device patterns"""
        alerts = []
        
        # Check for device cloning (identical fingerprints from different IPs)
        for existing_fp in existing_fps:
            if (current_fp.fingerprint_id == existing_fp.fingerprint_id and
                current_fp.network_info.get("ip") != existing_fp.network_info.get("ip")):
                alerts.append(SecurityEvent.DEVICE_CLONING_DETECTED)
                break
        
        # Check for rapid device changes
        recent_devices = [
            fp for fp in existing_fps
            if (datetime.utcnow() - fp.last_seen).days <= 1
        ]
        if len(recent_devices) > 5:
            alerts.append(SecurityEvent.SUSPICIOUS_DEVICE_PATTERN)
        
        return alerts
    
    def _detect_randomized_fingerprint(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect randomized fingerprint values"""
        # Check for unusual combinations that might indicate randomization
        screen_res = fingerprint_data.get("screen_resolution", "")
        user_agent = fingerprint_data.get("user_agent", "")
        
        # Check for impossible screen resolutions
        if screen_res and "x" in screen_res:
            try:
                width, height = map(int, screen_res.split("x"))
                if width > 10000 or height > 10000:  # Unrealistic resolution
                    return True
            except ValueError:
                return True  # Invalid format
        
        # Check for conflicting user agent information
        if user_agent:
            if "Mobile" in user_agent and "Desktop" in user_agent:
                return True
        
        return False
    
    def _detect_virtualization(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect virtualized environments"""
        user_agent = fingerprint_data.get("user_agent", "").lower()
        hardware = fingerprint_data.get("hardware", {})
        
        # Check user agent for VM indicators
        vm_indicators = self.fingerprint_components["virtualization_indicators"]["vm_vendors"]
        for indicator in vm_indicators:
            if indicator.lower() in user_agent:
                return True
        
        # Check hardware specs for VM indicators
        if hardware:
            gpu = hardware.get("gpu", "").lower()
            cpu = hardware.get("cpu", "").lower()
            
            vm_hardware_indicators = self.fingerprint_components["virtualization_indicators"]["vm_hardware"]
            for indicator in vm_hardware_indicators:
                if indicator.lower() in gpu or indicator.lower() in cpu:
                    return True
        
        return False
    
    def _detect_automation_tools(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect browser automation tools"""
        user_agent = fingerprint_data.get("user_agent", "").lower()
        
        # Check for automation tool indicators
        automation_indicators = [
            "selenium", "puppeteer", "playwright", "chromedriver",
            "phantomjs", "headless", "automation"
        ]
        
        for indicator in automation_indicators:
            if indicator in user_agent:
                return True
        
        # Check for missing expected properties
        if not fingerprint_data.get("plugins") and not fingerprint_data.get("fonts"):
            return True  # Suspicious lack of fingerprint data
        
        return False
    
    def _detect_fingerprint_spoofing(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect fingerprint spoofing attempts"""
        # Check for inconsistent data
        user_agent = fingerprint_data.get("user_agent", "")
        platform = fingerprint_data.get("platform", "")
        
        if user_agent and platform:
            # Check for platform/user agent mismatches
            if "Windows" in user_agent and platform.lower() == "linux":
                return True
            if "Mac" in user_agent and platform.lower() == "windows":
                return True
        
        return False
    
    def _detect_proxy_vpn_patterns(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect proxy/VPN usage patterns"""
        network_info = fingerprint_data.get("network", {})
        
        # Check for known VPN/proxy indicators
        if network_info:
            ip_address = network_info.get("ip", "")
            if ip_address:
                # Check for common VPN/proxy IP ranges (simplified)
                try:
                    ip = ipaddress.ip_address(ip_address)
                    # This is a simplified check - in production, use IP intelligence services
                    if ip.is_private:
                        return False  # Private IPs are not proxies
                except ValueError:
                    pass
        
        return False
    
    def _detect_fingerprint_blocking(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Detect fingerprint blocking attempts"""
        # Check if expected fingerprint data is missing or blocked
        expected_components = ["canvas_data", "webgl_data", "audio_data"]
        missing_components = [
            comp for comp in expected_components
            if not fingerprint_data.get(comp)
        ]
        
        # If most components are missing, likely blocked
        return len(missing_components) >= 2
    
    async def _enhance_creator_fingerprint(
        self,
        fingerprint: DeviceFingerprint,
        context: Dict[str, Any]
    ) -> None:
        """Enhance fingerprint with Creator Economy specific data"""
        creator_type = context.get("creator_type", "")
        
        # Initialize creator-specific tracking
        fingerprint.creator_activities = {
            "creator_type": creator_type,
            "creation_tools": context.get("creation_tools", []),
            "content_types": context.get("content_types", []),
            "high_value_creator": context.get("high_value", False)
        }
        
        # Adjust risk scoring for creators
        if creator_type in ["musician", "artist", "high_earning"]:
            fingerprint.risk_score *= 1.2  # Higher scrutiny for high-value creators
    
    async def _enforce_device_limits(self, user_id: str) -> None:
        """Enforce device limits per user"""
        user_device_ids = self.user_devices.get(user_id, set())
        
        if len(user_device_ids) > self.config.max_devices_per_user:
            # Remove oldest devices
            device_timestamps = [
                (fid, self.device_fingerprints[fid].last_seen)
                for fid in user_device_ids
                if fid in self.device_fingerprints
            ]
            
            # Sort by last seen timestamp
            device_timestamps.sort(key=lambda x: x[1])
            
            # Remove oldest devices beyond limit
            devices_to_remove = len(user_device_ids) - self.config.max_devices_per_user
            for i in range(devices_to_remove):
                fid_to_remove = device_timestamps[i][0]
                self.user_devices[user_id].discard(fid_to_remove)
                if fid_to_remove in self.device_fingerprints:
                    del self.device_fingerprints[fid_to_remove]
            
            logger.info(f"✅ Enforced device limit for user {user_id}: removed {devices_to_remove} old devices")
    
    async def _assess_device_risk(
        self,
        fingerprint: DeviceFingerprint,
        existing_fingerprints: List[DeviceFingerprint],
        changes: List[str],
        alerts: List[SecurityEvent]
    ) -> Dict[str, Any]:
        """Assess device security risk"""
        risk_factors = {
            "new_device": fingerprint.trust_level == TrustLevel.NEW,
            "component_changes": len(changes),
            "security_alerts": len(alerts),
            "virtualization": "virtualized_environment" in changes,
            "automation": "browser_automation_detected" in changes,
            "device_type": fingerprint.device_type.value
        }
        
        # Calculate risk score
        base_risk = 0.3
        
        if risk_factors["new_device"]:
            base_risk += 0.2
        
        base_risk += min(risk_factors["component_changes"] * 0.1, 0.3)
        base_risk += min(risk_factors["security_alerts"] * 0.15, 0.4)
        
        if risk_factors["virtualization"]:
            base_risk += 0.3
        
        if risk_factors["automation"]:
            base_risk += 0.25
        
        # Adjust for device type
        if fingerprint.device_type in [DeviceType.UNKNOWN, DeviceType.IOT_DEVICE]:
            base_risk += 0.1
        
        final_risk = min(base_risk, 1.0)
        fingerprint.risk_score = final_risk
        
        return {
            "risk_score": final_risk,
            "risk_level": "high" if final_risk > 0.7 else "medium" if final_risk > 0.4 else "low",
            "risk_factors": risk_factors,
            "assessment_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _generate_security_recommendations(
        self,
        alerts: List[SecurityEvent],
        changes: List[str],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if SecurityEvent.NEW_DEVICE_DETECTED in alerts:
            recommendations.append("Verify device ownership through secondary authentication")
        
        if SecurityEvent.FINGERPRINT_EVASION_ATTEMPT in alerts:
            recommendations.append("Investigate potential bot or automated access")
        
        if SecurityEvent.DEVICE_CLONING_DETECTED in alerts:
            recommendations.append("Check for unauthorized device duplication")
        
        if "virtualized_environment" in changes:
            recommendations.append("Review virtualization usage policy")
        
        if risk_assessment["risk_score"] > 0.7:
            recommendations.append("Implement additional verification steps")
        
        if len(changes) > 5:
            recommendations.append("Monitor for device tampering")
        
        return recommendations
    
    def _calculate_analysis_confidence(
        self,
        existing_device_count: int,
        change_count: int,
        similarity_score: float
    ) -> float:
        """Calculate confidence in analysis results"""
        # Base confidence on available data
        data_confidence = min(existing_device_count / 5.0, 1.0)
        
        # Adjust for similarity score
        similarity_confidence = similarity_score
        
        # Adjust for change complexity
        change_confidence = max(0.5, 1.0 - (change_count * 0.1))
        
        return (data_confidence + similarity_confidence + change_confidence) / 3.0
    
    async def _update_fingerprint_data(
        self,
        existing_fp: DeviceFingerprint,
        current_fp: DeviceFingerprint
    ) -> None:
        """Update existing fingerprint with current data"""
        # Update timestamps
        existing_fp.last_seen = current_fp.last_seen
        
        # Update network information
        existing_fp.network_info.update(current_fp.network_info)
        
        # Update location history
        if current_fp.location_history:
            existing_fp.location_history.extend(current_fp.location_history)
            # Keep only recent locations
            cutoff = datetime.utcnow() - timedelta(days=30)
            existing_fp.location_history = [
                loc for loc in existing_fp.location_history
                if datetime.fromisoformat(loc.get("timestamp", "2000-01-01")) >= cutoff
            ]
    
    async def _log_security_event(
        self,
        user_id: str,
        event_type: SecurityEvent,
        details: Dict[str, Any]
    ) -> None:
        """Log security event"""
        event = {
            "user_id": user_id,
            "event_type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        self.security_events.append(event)
        
        # Limit event history
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
        
        logger.info(f"🔒 Security event logged: {event_type.value} for user {user_id}")


# Export main classes
__all__ = [
    "DeviceFingerprintingManager",
    "DeviceFingerprint",
    "FingerprintAnalysis",
    "DeviceType",
    "TrustLevel",
    "SecurityEvent",
    "DeviceFingerprintingConfig"
]