#!/usr/bin/env python3
"""
🔒 Device Fingerprinting Manager - Advanced Device Security
===========================================================

Enterprise device fingerprinting system with canvas/WebGL analysis,
hardware detection, and anti-evasion capabilities for robust device tracking.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Frontend + ML + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import base64
import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from collections import defaultdict
import user_agents
import ipaddress

# ML imports for pattern analysis
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


class DeviceType(Enum):
    """Device type classification"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    GAMING_CONSOLE = "gaming_console"
    IOT_DEVICE = "iot_device"
    UNKNOWN = "unknown"


class TrustLevel(Enum):
    """Device trust level"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


class FingerprintComponent(Enum):
    """Fingerprint component types"""
    BROWSER_INFO = "browser_info"
    HARDWARE_INFO = "hardware_info"
    CANVAS_FINGERPRINT = "canvas_fingerprint"
    WEBGL_FINGERPRINT = "webgl_fingerprint"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    SCREEN_INFO = "screen_info"
    TIMEZONE_INFO = "timezone_info"
    PLUGIN_INFO = "plugin_info"
    FONT_INFO = "font_info"
    NETWORK_INFO = "network_info"


@dataclass
class DeviceFingerprint:
    """Comprehensive device fingerprint"""
    fingerprint_id: str
    user_id: str
    created_at: datetime
    last_seen: datetime
    
    # Browser information
    user_agent: str
    browser_family: str
    browser_version: str
    engine_name: str
    engine_version: str
    
    # Operating system
    os_family: str
    os_version: str
    platform: str
    
    # Device information
    device_type: DeviceType
    device_family: str
    is_mobile: bool
    is_tablet: bool
    
    # Hardware fingerprint
    cpu_cores: Optional[int]
    memory_gb: Optional[float]
    gpu_vendor: Optional[str]
    gpu_renderer: Optional[str]
    
    # Display information
    screen_width: int
    screen_height: int
    color_depth: int
    pixel_ratio: float
    
    # Canvas fingerprint
    canvas_hash: Optional[str]
    canvas_data: Optional[str]
    
    # WebGL fingerprint
    webgl_vendor: Optional[str]
    webgl_renderer: Optional[str]
    webgl_hash: Optional[str]
    
    # Audio fingerprint
    audio_hash: Optional[str]
    audio_data: Optional[str]
    
    # System information
    timezone: str
    language: str
    languages: List[str]
    
    # Plugins and extensions
    plugins: List[str]
    fonts: List[str]
    
    # Network information
    ip_address: str
    connection_type: Optional[str]
    
    # Trust and security
    trust_level: TrustLevel
    is_suspicious: bool
    evasion_attempts: int
    
    # Metadata
    fingerprint_hash: str
    similarity_scores: Dict[str, float]


@dataclass
class DeviceChangeEvent:
    """Device change detection result"""
    device_id: str
    change_type: str
    component: FingerprintComponent
    old_value: Any
    new_value: Any
    severity: str
    confidence: float
    timestamp: datetime


@dataclass
class EvasionAttempt:
    """Fingerprint evasion attempt detection"""
    device_id: str
    evasion_type: str
    detection_method: str
    confidence: float
    evidence: Dict[str, Any]
    timestamp: datetime


class DeviceFingerprintingManager:
    """
    🔒 Enterprise Device Fingerprinting Manager
    
    Advanced device fingerprinting with multi-vector analysis,
    anti-evasion detection, and ML-powered device classification.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize device fingerprinting manager"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/device_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Device storage
        self.device_fingerprints: Dict[str, DeviceFingerprint] = {}
        self.user_devices: Dict[str, Set[str]] = defaultdict(set)
        
        # Change detection
        self.change_history: List[DeviceChangeEvent] = []
        self.evasion_attempts: List[EvasionAttempt] = []
        
        # ML components
        self.scaler = StandardScaler()
        self.clustering_model = DBSCAN(eps=0.3, min_samples=3)
        self.pca = PCA(n_components=20)
        
        # Component weights for fingerprint calculation
        self.component_weights = {
            FingerprintComponent.CANVAS_FINGERPRINT: 0.25,
            FingerprintComponent.WEBGL_FINGERPRINT: 0.25,
            FingerprintComponent.HARDWARE_INFO: 0.20,
            FingerprintComponent.BROWSER_INFO: 0.15,
            FingerprintComponent.SCREEN_INFO: 0.10,
            FingerprintComponent.AUDIO_FINGERPRINT: 0.05
        }
        
        # Known evasion patterns
        self.evasion_patterns = self._load_evasion_patterns()
        
        # Suspicious thresholds
        self.similarity_threshold = 0.95
        self.change_threshold = 0.8
    
    async def generate_device_fingerprint(
        self,
        user_id: str,
        fingerprint_data: Dict[str, Any],
        ip_address: str
    ) -> DeviceFingerprint:
        """
        Generate comprehensive device fingerprint
        
        Args:
            user_id: User identifier
            fingerprint_data: Raw fingerprint data from client
            ip_address: Client IP address
            
        Returns:
            Generated device fingerprint
        """
        try:
            # Parse user agent
            ua = user_agents.parse(fingerprint_data.get("userAgent", ""))
            
            # Generate fingerprint ID
            fingerprint_id = await self._generate_fingerprint_id(fingerprint_data)
            
            # Create device fingerprint
            fingerprint = DeviceFingerprint(
                fingerprint_id=fingerprint_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                
                # Browser info
                user_agent=fingerprint_data.get("userAgent", ""),
                browser_family=ua.browser.family,
                browser_version=ua.browser.version_string,
                engine_name=getattr(ua.browser, "engine", "unknown"),
                engine_version=getattr(ua.browser, "engine_version", "unknown"),
                
                # OS info
                os_family=ua.os.family,
                os_version=ua.os.version_string,
                platform=fingerprint_data.get("platform", ""),
                
                # Device info
                device_type=self._classify_device_type(fingerprint_data, ua),
                device_family=ua.device.family,
                is_mobile=ua.is_mobile,
                is_tablet=ua.is_tablet,
                
                # Hardware info
                cpu_cores=fingerprint_data.get("cpuCores"),
                memory_gb=fingerprint_data.get("memoryGB"),
                gpu_vendor=fingerprint_data.get("gpuVendor"),
                gpu_renderer=fingerprint_data.get("gpuRenderer"),
                
                # Display info
                screen_width=fingerprint_data.get("screenWidth", 0),
                screen_height=fingerprint_data.get("screenHeight", 0),
                color_depth=fingerprint_data.get("colorDepth", 0),
                pixel_ratio=fingerprint_data.get("pixelRatio", 1.0),
                
                # Canvas fingerprint
                canvas_hash=await self._generate_canvas_hash(fingerprint_data),
                canvas_data=fingerprint_data.get("canvasData"),
                
                # WebGL fingerprint
                webgl_vendor=fingerprint_data.get("webglVendor"),
                webgl_renderer=fingerprint_data.get("webglRenderer"),
                webgl_hash=await self._generate_webgl_hash(fingerprint_data),
                
                # Audio fingerprint
                audio_hash=await self._generate_audio_hash(fingerprint_data),
                audio_data=fingerprint_data.get("audioData"),
                
                # System info
                timezone=fingerprint_data.get("timezone", ""),
                language=fingerprint_data.get("language", ""),
                languages=fingerprint_data.get("languages", []),
                
                # Plugins and fonts
                plugins=fingerprint_data.get("plugins", []),
                fonts=fingerprint_data.get("fonts", []),
                
                # Network info
                ip_address=ip_address,
                connection_type=fingerprint_data.get("connectionType"),
                
                # Security attributes
                trust_level=TrustLevel.UNTRUSTED,
                is_suspicious=False,
                evasion_attempts=0,
                
                # Generate hash
                fingerprint_hash="",  # Will be set below
                similarity_scores={}
            )
            
            # Generate comprehensive hash
            fingerprint.fingerprint_hash = await self._generate_comprehensive_hash(fingerprint)
            
            # Detect evasion attempts
            evasion_detected = await self._detect_evasion_attempts(fingerprint, fingerprint_data)
            if evasion_detected:
                fingerprint.is_suspicious = True
                fingerprint.evasion_attempts += 1
            
            # Calculate similarity to existing fingerprints
            await self._calculate_similarity_scores(fingerprint)
            
            # Store fingerprint
            self.device_fingerprints[fingerprint_id] = fingerprint
            self.user_devices[user_id].add(fingerprint_id)
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Fingerprint generation error: {e}")
            raise
    
    async def detect_device_changes(
        self,
        fingerprint_id: str,
        new_fingerprint_data: Dict[str, Any]
    ) -> List[DeviceChangeEvent]:
        """
        Detect changes in device fingerprint
        
        Args:
            fingerprint_id: Existing fingerprint ID
            new_fingerprint_data: New fingerprint data
            
        Returns:
            List of detected changes
        """
        try:
            existing_fingerprint = self.device_fingerprints.get(fingerprint_id)
            if not existing_fingerprint:
                return []
            
            changes = []
            
            # Check browser changes
            new_ua = user_agents.parse(new_fingerprint_data.get("userAgent", ""))
            if new_ua.browser.family != existing_fingerprint.browser_family:
                changes.append(DeviceChangeEvent(
                    device_id=fingerprint_id,
                    change_type="browser_change",
                    component=FingerprintComponent.BROWSER_INFO,
                    old_value=existing_fingerprint.browser_family,
                    new_value=new_ua.browser.family,
                    severity="medium",
                    confidence=0.9,
                    timestamp=datetime.utcnow()
                ))
            
            # Check screen resolution changes
            new_width = new_fingerprint_data.get("screenWidth", 0)
            new_height = new_fingerprint_data.get("screenHeight", 0)
            if (new_width != existing_fingerprint.screen_width or 
                new_height != existing_fingerprint.screen_height):
                changes.append(DeviceChangeEvent(
                    device_id=fingerprint_id,
                    change_type="screen_change",
                    component=FingerprintComponent.SCREEN_INFO,
                    old_value=f"{existing_fingerprint.screen_width}x{existing_fingerprint.screen_height}",
                    new_value=f"{new_width}x{new_height}",
                    severity="low",
                    confidence=0.8,
                    timestamp=datetime.utcnow()
                ))
            
            # Check canvas fingerprint changes
            new_canvas_hash = await self._generate_canvas_hash(new_fingerprint_data)
            if new_canvas_hash != existing_fingerprint.canvas_hash:
                changes.append(DeviceChangeEvent(
                    device_id=fingerprint_id,
                    change_type="canvas_change",
                    component=FingerprintComponent.CANVAS_FINGERPRINT,
                    old_value=existing_fingerprint.canvas_hash,
                    new_value=new_canvas_hash,
                    severity="high",
                    confidence=0.95,
                    timestamp=datetime.utcnow()
                ))
            
            # Check WebGL changes
            new_webgl_hash = await self._generate_webgl_hash(new_fingerprint_data)
            if new_webgl_hash != existing_fingerprint.webgl_hash:
                changes.append(DeviceChangeEvent(
                    device_id=fingerprint_id,
                    change_type="webgl_change",
                    component=FingerprintComponent.WEBGL_FINGERPRINT,
                    old_value=existing_fingerprint.webgl_hash,
                    new_value=new_webgl_hash,
                    severity="high",
                    confidence=0.95,
                    timestamp=datetime.utcnow()
                ))
            
            # Check hardware changes
            new_gpu_vendor = new_fingerprint_data.get("gpuVendor")
            if new_gpu_vendor != existing_fingerprint.gpu_vendor:
                changes.append(DeviceChangeEvent(
                    device_id=fingerprint_id,
                    change_type="hardware_change",
                    component=FingerprintComponent.HARDWARE_INFO,
                    old_value=existing_fingerprint.gpu_vendor,
                    new_value=new_gpu_vendor,
                    severity="critical",
                    confidence=0.99,
                    timestamp=datetime.utcnow()
                ))
            
            # Store change events
            self.change_history.extend(changes)
            
            # Update fingerprint if changes are legitimate
            if changes:
                await self._update_fingerprint_with_changes(
                    existing_fingerprint, new_fingerprint_data, changes
                )
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Change detection error: {e}")
            return []
    
    async def manage_trusted_devices(
        self,
        user_id: str,
        fingerprint_id: str,
        action: str,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Manage trusted device status
        
        Args:
            user_id: User identifier
            fingerprint_id: Device fingerprint ID
            action: Action to perform (trust, untrust, verify)
            verification_data: Additional verification data
            
        Returns:
            Action result
        """
        try:
            fingerprint = self.device_fingerprints.get(fingerprint_id)
            if not fingerprint or fingerprint.user_id != user_id:
                return {
                    "success": False,
                    "error": "Device not found or access denied"
                }
            
            if action == "trust":
                # Verify device before trusting
                verification_result = await self._verify_device_authenticity(
                    fingerprint, verification_data
                )
                
                if verification_result["verified"]:
                    fingerprint.trust_level = TrustLevel.VERIFIED
                    fingerprint.is_suspicious = False
                    
                    return {
                        "success": True,
                        "message": "Device marked as trusted",
                        "trust_level": fingerprint.trust_level.value,
                        "verification_score": verification_result["score"]
                    }
                else:
                    return {
                        "success": False,
                        "error": "Device verification failed",
                        "verification_result": verification_result
                    }
            
            elif action == "untrust":
                fingerprint.trust_level = TrustLevel.UNTRUSTED
                fingerprint.is_suspicious = True
                
                return {
                    "success": True,
                    "message": "Device marked as untrusted",
                    "trust_level": fingerprint.trust_level.value
                }
            
            elif action == "verify":
                verification_result = await self._verify_device_authenticity(
                    fingerprint, verification_data
                )
                
                # Update trust level based on verification
                if verification_result["score"] > 0.8:
                    fingerprint.trust_level = TrustLevel.HIGH
                elif verification_result["score"] > 0.6:
                    fingerprint.trust_level = TrustLevel.MEDIUM
                else:
                    fingerprint.trust_level = TrustLevel.LOW
                
                return {
                    "success": True,
                    "verification_result": verification_result,
                    "trust_level": fingerprint.trust_level.value
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            self.logger.error(f"Trusted device management error: {e}")
            return {
                "success": False,
                "error": f"Operation failed: {e}"
            }
    
    async def detect_fingerprint_evasion(
        self,
        fingerprint_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[EvasionAttempt]:
        """
        Detect fingerprint evasion attempts
        
        Args:
            fingerprint_data: Raw fingerprint data
            context: Additional context for analysis
            
        Returns:
            List of detected evasion attempts
        """
        try:
            evasion_attempts = []
            
            # Check for randomized canvas fingerprints
            canvas_evasion = await self._detect_canvas_randomization(fingerprint_data)
            if canvas_evasion:
                evasion_attempts.append(canvas_evasion)
            
            # Check for WebGL spoofing
            webgl_evasion = await self._detect_webgl_spoofing(fingerprint_data)
            if webgl_evasion:
                evasion_attempts.append(webgl_evasion)
            
            # Check for user agent spoofing
            ua_evasion = await self._detect_user_agent_spoofing(fingerprint_data)
            if ua_evasion:
                evasion_attempts.append(ua_evasion)
            
            # Check for screen resolution inconsistencies
            screen_evasion = await self._detect_screen_spoofing(fingerprint_data)
            if screen_evasion:
                evasion_attempts.append(screen_evasion)
            
            # Check for timezone manipulation
            timezone_evasion = await self._detect_timezone_manipulation(fingerprint_data)
            if timezone_evasion:
                evasion_attempts.append(timezone_evasion)
            
            # Check for browser extension interference
            extension_evasion = await self._detect_extension_interference(fingerprint_data)
            if extension_evasion:
                evasion_attempts.append(extension_evasion)
            
            # ML-based evasion detection
            ml_evasion = await self._ml_evasion_detection(fingerprint_data, context)
            evasion_attempts.extend(ml_evasion)
            
            # Store evasion attempts
            self.evasion_attempts.extend(evasion_attempts)
            
            return evasion_attempts
            
        except Exception as e:
            self.logger.error(f"Evasion detection error: {e}")
            return []
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load device fingerprinting configuration"""
        default_config = {
            "fingerprint_expiry_days": 90,
            "change_detection_threshold": 0.8,
            "similarity_threshold": 0.95,
            "trust_decay_days": 30,
            "max_devices_per_user": 10
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def _load_evasion_patterns(self) -> Dict[str, Any]:
        """Load known evasion patterns"""
        return {
            "canvas_randomization": {
                "entropy_threshold": 0.9,
                "pixel_variance_threshold": 100
            },
            "webgl_spoofing": {
                "vendor_renderer_mismatch": True,
                "suspicious_extensions": ["WEBGL_debug_renderer_info"]
            },
            "user_agent_spoofing": {
                "inconsistent_features": True,
                "outdated_versions": True
            }
        }
    
    async def _generate_fingerprint_id(self, fingerprint_data: Dict[str, Any]) -> str:
        """Generate unique fingerprint ID"""
        # Combine stable components for ID generation
        components = [
            fingerprint_data.get("userAgent", ""),
            str(fingerprint_data.get("screenWidth", 0)),
            str(fingerprint_data.get("screenHeight", 0)),
            fingerprint_data.get("timezone", ""),
            fingerprint_data.get("language", ""),
            str(fingerprint_data.get("colorDepth", 0))
        ]
        
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    async def _generate_canvas_hash(self, fingerprint_data: Dict[str, Any]) -> Optional[str]:
        """Generate hash from canvas fingerprint data"""
        canvas_data = fingerprint_data.get("canvasData")
        if not canvas_data:
            return None
        
        return hashlib.sha256(canvas_data.encode()).hexdigest()
    
    async def _generate_webgl_hash(self, fingerprint_data: Dict[str, Any]) -> Optional[str]:
        """Generate hash from WebGL fingerprint data"""
        webgl_components = [
            fingerprint_data.get("webglVendor", ""),
            fingerprint_data.get("webglRenderer", ""),
            str(fingerprint_data.get("webglVersion", "")),
            str(fingerprint_data.get("webglExtensions", []))
        ]
        
        if not any(webgl_components):
            return None
        
        combined = "|".join(webgl_components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def _generate_audio_hash(self, fingerprint_data: Dict[str, Any]) -> Optional[str]:
        """Generate hash from audio fingerprint data"""
        audio_data = fingerprint_data.get("audioData")
        if not audio_data:
            return None
        
        return hashlib.sha256(audio_data.encode()).hexdigest()
    
    async def _generate_comprehensive_hash(self, fingerprint: DeviceFingerprint) -> str:
        """Generate comprehensive fingerprint hash"""
        components = [
            fingerprint.user_agent,
            f"{fingerprint.screen_width}x{fingerprint.screen_height}",
            str(fingerprint.color_depth),
            fingerprint.timezone,
            fingerprint.language,
            fingerprint.canvas_hash or "",
            fingerprint.webgl_hash or "",
            fingerprint.audio_hash or "",
            fingerprint.gpu_vendor or "",
            fingerprint.gpu_renderer or "",
            "|".join(sorted(fingerprint.plugins)),
            "|".join(sorted(fingerprint.fonts))
        ]
        
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _classify_device_type(
        self,
        fingerprint_data: Dict[str, Any],
        ua: user_agents.UserAgent
    ) -> DeviceType:
        """Classify device type based on fingerprint data"""
        if ua.is_mobile:
            return DeviceType.MOBILE
        elif ua.is_tablet:
            return DeviceType.TABLET
        
        # Check for gaming console patterns
        user_agent_lower = fingerprint_data.get("userAgent", "").lower()
        if any(console in user_agent_lower for console in ["playstation", "xbox", "nintendo"]):
            return DeviceType.GAMING_CONSOLE
        
        # Check for smart TV patterns
        if any(tv in user_agent_lower for tv in ["smart-tv", "webos", "tizen"]):
            return DeviceType.SMART_TV
        
        # Default to desktop for PC-like devices
        if ua.is_pc or fingerprint_data.get("screenWidth", 0) > 1024:
            return DeviceType.DESKTOP
        
        return DeviceType.UNKNOWN
    
    async def _detect_evasion_attempts(
        self,
        fingerprint: DeviceFingerprint,
        fingerprint_data: Dict[str, Any]
    ) -> bool:
        """Detect if fingerprint shows signs of evasion"""
        evasion_indicators = 0
        
        # Check for inconsistent user agent
        if await self._is_user_agent_inconsistent(fingerprint_data):
            evasion_indicators += 1
        
        # Check for canvas randomization
        if await self._has_canvas_randomization(fingerprint_data):
            evasion_indicators += 1
        
        # Check for WebGL spoofing
        if await self._has_webgl_spoofing(fingerprint_data):
            evasion_indicators += 1
        
        # Check for timezone inconsistencies
        if await self._has_timezone_inconsistency(fingerprint_data):
            evasion_indicators += 1
        
        # Threshold for suspicion
        return evasion_indicators >= 2
    
    async def _calculate_similarity_scores(self, fingerprint: DeviceFingerprint):
        """Calculate similarity scores to existing fingerprints"""
        user_fingerprints = [
            fp for fp_id in self.user_devices.get(fingerprint.user_id, set())
            for fp in [self.device_fingerprints.get(fp_id)]
            if fp and fp.fingerprint_id != fingerprint.fingerprint_id
        ]
        
        for existing_fp in user_fingerprints:
            similarity = await self._calculate_fingerprint_similarity(
                fingerprint, existing_fp
            )
            fingerprint.similarity_scores[existing_fp.fingerprint_id] = similarity
    
    async def _calculate_fingerprint_similarity(
        self,
        fp1: DeviceFingerprint,
        fp2: DeviceFingerprint
    ) -> float:
        """Calculate similarity between two fingerprints"""
        similarities = []
        
        # Browser similarity
        if fp1.browser_family == fp2.browser_family:
            similarities.append(1.0)
        else:
            similarities.append(0.0)
        
        # Screen similarity
        screen_sim = 1.0 - abs(fp1.screen_width - fp2.screen_width) / max(fp1.screen_width, fp2.screen_width, 1)
        similarities.append(screen_sim)
        
        # Canvas similarity
        if fp1.canvas_hash and fp2.canvas_hash:
            canvas_sim = 1.0 if fp1.canvas_hash == fp2.canvas_hash else 0.0
            similarities.append(canvas_sim)
        
        # WebGL similarity
        if fp1.webgl_hash and fp2.webgl_hash:
            webgl_sim = 1.0 if fp1.webgl_hash == fp2.webgl_hash else 0.0
            similarities.append(webgl_sim)
        
        # Hardware similarity
        if fp1.gpu_vendor and fp2.gpu_vendor:
            gpu_sim = 1.0 if fp1.gpu_vendor == fp2.gpu_vendor else 0.0
            similarities.append(gpu_sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _verify_device_authenticity(
        self,
        fingerprint: DeviceFingerprint,
        verification_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify device authenticity for trust establishment"""
        score = 0.0
        evidence = []
        
        # Check fingerprint consistency
        if not fingerprint.is_suspicious:
            score += 0.3
            evidence.append("No suspicious activity detected")
        
        # Check evasion attempts
        if fingerprint.evasion_attempts == 0:
            score += 0.2
            evidence.append("No evasion attempts detected")
        
        # Check stability over time
        age_days = (datetime.utcnow() - fingerprint.created_at).days
        if age_days > 7:
            score += 0.2
            evidence.append(f"Device stable for {age_days} days")
        
        # Check verification data if provided
        if verification_data:
            if verification_data.get("email_verified"):
                score += 0.1
                evidence.append("Email verification completed")
            
            if verification_data.get("sms_verified"):
                score += 0.1
                evidence.append("SMS verification completed")
            
            if verification_data.get("totp_verified"):
                score += 0.1
                evidence.append("TOTP verification completed")
        
        return {
            "verified": score >= 0.7,
            "score": min(1.0, score),
            "evidence": evidence,
            "recommendation": "trust" if score >= 0.7 else "require_additional_verification"
        }
    
    # Evasion detection methods
    
    async def _detect_canvas_randomization(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect canvas fingerprint randomization"""
        canvas_data = fingerprint_data.get("canvasData")
        if not canvas_data:
            return None
        
        # Check for high entropy indicating randomization
        entropy = self._calculate_entropy(canvas_data)
        if entropy > self.evasion_patterns["canvas_randomization"]["entropy_threshold"]:
            return EvasionAttempt(
                device_id="",  # Will be set by caller
                evasion_type="canvas_randomization",
                detection_method="entropy_analysis",
                confidence=min(1.0, entropy),
                evidence={
                    "entropy": entropy,
                    "threshold": self.evasion_patterns["canvas_randomization"]["entropy_threshold"]
                },
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _detect_webgl_spoofing(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect WebGL fingerprint spoofing"""
        vendor = fingerprint_data.get("webglVendor", "")
        renderer = fingerprint_data.get("webglRenderer", "")
        
        # Check for vendor/renderer mismatches
        known_mismatches = [
            ("Intel", "NVIDIA"),
            ("AMD", "Intel"),
            ("NVIDIA", "AMD")
        ]
        
        for vendor_pattern, renderer_pattern in known_mismatches:
            if vendor_pattern in vendor and renderer_pattern in renderer:
                return EvasionAttempt(
                    device_id="",
                    evasion_type="webgl_spoofing", 
                    detection_method="vendor_renderer_mismatch",
                    confidence=0.9,
                    evidence={
                        "vendor": vendor,
                        "renderer": renderer,
                        "mismatch_detected": f"{vendor_pattern}/{renderer_pattern}"
                    },
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    async def _detect_user_agent_spoofing(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect user agent spoofing"""
        user_agent = fingerprint_data.get("userAgent", "")
        
        # Parse user agent
        ua = user_agents.parse(user_agent)
        
        # Check for inconsistencies with other data
        screen_width = fingerprint_data.get("screenWidth", 0)
        
        # Mobile user agent with desktop screen resolution
        if ua.is_mobile and screen_width > 1200:
            return EvasionAttempt(
                device_id="",
                evasion_type="user_agent_spoofing",
                detection_method="mobile_desktop_inconsistency",
                confidence=0.8,
                evidence={
                    "user_agent": user_agent,
                    "is_mobile": ua.is_mobile,
                    "screen_width": screen_width
                },
                timestamp=datetime.utcnow()
            )
        
        return None
    
    async def _detect_screen_spoofing(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect screen resolution spoofing"""
        screen_width = fingerprint_data.get("screenWidth", 0)
        screen_height = fingerprint_data.get("screenHeight", 0)
        pixel_ratio = fingerprint_data.get("pixelRatio", 1.0)
        
        # Check for impossible combinations
        if screen_width > 0 and screen_height > 0:
            aspect_ratio = screen_width / screen_height
            
            # Unusual aspect ratios that might indicate spoofing
            if aspect_ratio < 0.5 or aspect_ratio > 4.0:
                return EvasionAttempt(
                    device_id="",
                    evasion_type="screen_spoofing",
                    detection_method="unusual_aspect_ratio",
                    confidence=0.7,
                    evidence={
                        "screen_width": screen_width,
                        "screen_height": screen_height,
                        "aspect_ratio": aspect_ratio
                    },
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    async def _detect_timezone_manipulation(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect timezone manipulation"""
        timezone = fingerprint_data.get("timezone", "")
        language = fingerprint_data.get("language", "")
        
        # Check for timezone/language mismatches
        common_mismatches = {
            "America/New_York": ["zh", "ja", "ko"],  # Asian languages with US timezone
            "Europe/London": ["zh", "ja", "ar"],     # Non-European languages with EU timezone
            "Asia/Tokyo": ["en", "es", "fr"]         # Western languages with Asian timezone
        }
        
        for tz, suspicious_langs in common_mismatches.items():
            if tz in timezone and any(lang in language for lang in suspicious_langs):
                return EvasionAttempt(
                    device_id="",
                    evasion_type="timezone_manipulation",
                    detection_method="timezone_language_mismatch",
                    confidence=0.6,
                    evidence={
                        "timezone": timezone,
                        "language": language,
                        "mismatch_pattern": f"{tz}/{language}"
                    },
                    timestamp=datetime.utcnow()
                )
        
        return None
    
    async def _detect_extension_interference(
        self,
        fingerprint_data: Dict[str, Any]
    ) -> Optional[EvasionAttempt]:
        """Detect browser extension interference"""
        plugins = fingerprint_data.get("plugins", [])
        
        # Known privacy/spoofing extensions
        suspicious_plugins = [
            "Chameleon",
            "Privacy Badger",
            "Canvas Blocker",
            "WebGL Fingerprint Defender",
            "User-Agent Switcher"
        ]
        
        for plugin in plugins:
            for suspicious in suspicious_plugins:
                if suspicious.lower() in plugin.lower():
                    return EvasionAttempt(
                        device_id="",
                        evasion_type="extension_interference",
                        detection_method="suspicious_plugin_detection",
                        confidence=0.8,
                        evidence={
                            "detected_plugin": plugin,
                            "suspicious_pattern": suspicious,
                            "all_plugins": plugins
                        },
                        timestamp=datetime.utcnow()
                    )
        
        return None
    
    async def _ml_evasion_detection(
        self,
        fingerprint_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> List[EvasionAttempt]:
        """ML-based evasion detection"""
        # This would implement advanced ML models for evasion detection
        # For now, return empty list as it requires training data
        return []
    
    # Helper methods
    
    def _calculate_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in data:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        data_len = len(data)
        entropy = 0.0
        for count in char_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    async def _is_user_agent_inconsistent(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Check if user agent is inconsistent with other data"""
        # Simplified check - in production, implement comprehensive validation
        user_agent = fingerprint_data.get("userAgent", "")
        screen_width = fingerprint_data.get("screenWidth", 0)
        
        ua = user_agents.parse(user_agent)
        
        # Basic inconsistency check
        return ua.is_mobile and screen_width > 1200
    
    async def _has_canvas_randomization(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Check for canvas randomization"""
        canvas_data = fingerprint_data.get("canvasData")
        if not canvas_data:
            return False
        
        entropy = self._calculate_entropy(canvas_data)
        return entropy > 0.9
    
    async def _has_webgl_spoofing(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Check for WebGL spoofing"""
        vendor = fingerprint_data.get("webglVendor", "")
        renderer = fingerprint_data.get("webglRenderer", "")
        
        # Check for suspicious patterns
        return "fake" in vendor.lower() or "spoof" in renderer.lower()
    
    async def _has_timezone_inconsistency(self, fingerprint_data: Dict[str, Any]) -> bool:
        """Check for timezone inconsistencies"""
        timezone = fingerprint_data.get("timezone", "")
        language = fingerprint_data.get("language", "")
        
        # Simplified check
        return ("America" in timezone and "zh" in language) or \
               ("Asia" in timezone and "en" in language and "US" in timezone)
    
    async def _update_fingerprint_with_changes(
        self,
        fingerprint: DeviceFingerprint,
        new_data: Dict[str, Any],
        changes: List[DeviceChangeEvent]
    ):
        """Update fingerprint with detected changes"""
        fingerprint.last_seen = datetime.utcnow()
        
        # Update fields based on changes
        for change in changes:
            if change.component == FingerprintComponent.SCREEN_INFO:
                fingerprint.screen_width = new_data.get("screenWidth", fingerprint.screen_width)
                fingerprint.screen_height = new_data.get("screenHeight", fingerprint.screen_height)
            
            # Add more update logic as needed
        
        # Recalculate fingerprint hash
        fingerprint.fingerprint_hash = await self._generate_comprehensive_hash(fingerprint)


# Export main classes
__all__ = [
    "DeviceFingerprintingManager",
    "DeviceFingerprint",
    "DeviceType",
    "TrustLevel",
    "FingerprintComponent",
    "DeviceChangeEvent",
    "EvasionAttempt"
]