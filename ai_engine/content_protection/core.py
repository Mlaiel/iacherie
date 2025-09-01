"""Core Content Protection Engine

Central orchestrator for all content protection functionalities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import hashlib
import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    """Get current UTC datetime using the modern timezone-aware approach"""
    return datetime.now(timezone.utc)

class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ContentType(Enum):
    """Supported content types for protection"""
    AUDIO = "audio"    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"


@dataclass
class ProtectionResult:
    """Result of content protection operation"""
    success: bool    protection_id: str
    protection_level: ProtectionLevel
    watermark_applied: bool
    fingerprint_created: bool
    blockchain_registered: bool
    encryption_applied: bool
    estimated_protection_strength: float  # 0.0 to 1.0
    protection_metadata: Dict[str, Any]
    expires_at: Optional[datetime] = None
    errors: List[str] = None


@dataclass
class ContentItem:
    """Content item to be protected"""
    content_id: str    creator_id: str
    content_type: ContentType
    file_path: Optional[str] = None
    content_data: Optional[bytes] = None
    metadata: Dict[str, Any] = None
    title: Optional[str] = None
    description: Optional[str] = None


class ContentProtector:
    """    Advanced AI-powered content protection system
    
    Provides comprehensive protection including:
    - Digital watermarking
    - Content fingerprinting
    - Blockchain verification
    - Encryption and secure storage
    - Piracy detection and monitoring
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content protector"""
        self.config = config or {}        self.logger = logging.getLogger(__name__)
        
        # Protection components
        self._watermark_engine = None
        self._fingerprinter = None
        self._rights_manager = None
        self._dmca_manager = None
        self._blockchain_verifier = None
        self._piracy_detector = None
        self._encryption_engine = None
        
        # Protection cache
        self._protection_cache = {}
        
        # Metrics
        self.metrics = {
            'protections_applied': 0,
            'piracy_detections': 0,
            'successful_takedowns': 0,
            'protection_strength_avg': 0.0
        }
    
    async def initialize(self) -> bool:
        """Initialize all protection components"""
        try:            self.logger.info("Initializing content protection system...")
            
            # Initialize protection engines
            await self._init_watermark_engine()
            await self._init_fingerprinter()
            await self._init_rights_manager()
            await self._init_dmca_manager()
            await self._init_blockchain_verifier()
            await self._init_piracy_detector()
            await self._init_encryption_engine()
            
            self.logger.info("Content protection system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content protection: {str(e)}")
            return False
    
    async def protect_content(
        self,
        content: ContentItem,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        options: Optional[Dict[str, Any]] = None
    ) -> ProtectionResult:
        """        Apply comprehensive protection to content
        
        Args:
            content: Content item to protect
            protection_level: Level of protection to apply
            options: Additional protection options
            
        Returns:
            ProtectionResult with protection details
        """        try:
            self.logger.info(f"Protecting content {content.content_id} with level {protection_level.value}")
            
            # Generate protection ID
            protection_id = self._generate_protection_id(content)
            
            # Initialize result
            result = ProtectionResult(
                success=False,
                protection_id=protection_id,
                protection_level=protection_level,
                watermark_applied=False,
                fingerprint_created=False,
                blockchain_registered=False,
                encryption_applied=False,
                estimated_protection_strength=0.0,
                protection_metadata={},
                errors=[]
            )
            
            # Apply protection based on level
            protection_tasks = []
            
            # Always apply fingerprinting
            protection_tasks.append(self._apply_fingerprinting(content, result))
            
            # Level-based protection
            if protection_level in [ProtectionLevel.STANDARD, ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                protection_tasks.append(self._apply_watermarking(content, result))
            
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                protection_tasks.append(self._apply_blockchain_verification(content, result))
                protection_tasks.append(self._apply_encryption(content, result))
            
            if protection_level == ProtectionLevel.ENTERPRISE:
                protection_tasks.append(self._register_with_rights_management(content, result))
                protection_tasks.append(self._setup_advanced_monitoring(content, result))
            
            # Execute protection tasks
            await asyncio.gather(*protection_tasks, return_exceptions=True)
            
            # Calculate protection strength
            result.estimated_protection_strength = self._calculate_protection_strength(result)
            
            # Set expiration based on level
            result.expires_at = self._calculate_expiration(protection_level)
            
            # Cache protection result
            self._protection_cache[protection_id] = result
            
            # Update metrics
            self.metrics['protections_applied'] += 1
            self.metrics['protection_strength_avg'] = (
                (self.metrics['protection_strength_avg'] * (self.metrics['protections_applied'] - 1) +
                 result.estimated_protection_strength) / self.metrics['protections_applied']
            )
            
            result.success = len(result.errors) == 0
            
            self.logger.info(f"Content protection completed for {content.content_id}: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content protection failed: {str(e)}")
            return ProtectionResult(
                success=False,
                protection_id="",
                protection_level=protection_level,
                watermark_applied=False,
                fingerprint_created=False,
                blockchain_registered=False,
                encryption_applied=False,
                estimated_protection_strength=0.0,
                protection_metadata={},
                errors=[str(e)]
            )
    
    async def verify_protection(self, protection_id: str) -> Dict[str, Any]:
        """Verify the status and integrity of content protection"""
        try:            if protection_id in self._protection_cache:
                result = self._protection_cache[protection_id]
                
                # Check if protection is still valid
                if result.expires_at and utc_now() > result.expires_at:
                    return {
                        'valid': False,
                        'reason': 'Protection expired',
                        'expires_at': result.expires_at
                    }
                
                # Verify blockchain if applicable
                blockchain_valid = True
                if result.blockchain_registered and self._blockchain_verifier:
                    blockchain_valid = await self._blockchain_verifier.verify_ownership(protection_id)
                
                return {
                    'valid': blockchain_valid,
                    'protection_level': result.protection_level.value,
                    'protection_strength': result.estimated_protection_strength,
                    'expires_at': result.expires_at,
                    'blockchain_verified': blockchain_valid
                }
            
            return {'valid': False, 'reason': 'Protection not found'}
            
        except Exception as e:
            self.logger.error(f"Protection verification failed: {str(e)}")
            return {'valid': False, 'reason': str(e)}
    
    async def detect_unauthorized_use(self, content_id: str) -> Dict[str, Any]:
        """Detect unauthorized use of protected content"""
        try:            if self._piracy_detector:
                detections = await self._piracy_detector.scan_for_unauthorized_use(content_id)
                
                if detections:
                    self.metrics['piracy_detections'] += len(detections)
                    
                    # Automatically initiate takedown for serious violations
                    for detection in detections:
                        if detection.get('severity', 'low') == 'high':
                            await self._initiate_takedown(detection)
                
                return {
                    'unauthorized_uses_found': len(detections),
                    'detections': detections,
                    'scan_timestamp': utc_now().isoformat()
                }
            
            return {'unauthorized_uses_found': 0, 'detections': []}
            
        except Exception as e:
            self.logger.error(f"Unauthorized use detection failed: {str(e)}")
            return {'error': str(e)}
    
    async def get_protection_analytics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics for content protection"""
        try:            analytics = {
                'total_protections': self.metrics['protections_applied'],
                'piracy_detections': self.metrics['piracy_detections'],
                'successful_takedowns': self.metrics['successful_takedowns'],
                'average_protection_strength': self.metrics['protection_strength_avg'],
                'protection_levels_used': {},
                'content_types_protected': {}
            }
            
            # Analyze protection cache for more detailed metrics
            for protection in self._protection_cache.values():
                level = protection.protection_level.value
                analytics['protection_levels_used'][level] = analytics['protection_levels_used'].get(level, 0) + 1
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _generate_protection_id(self, content: ContentItem) -> str:
        """Generate unique protection ID"""
        data = f"{content.content_id}_{content.creator_id}_{utc_now().isoformat()}"        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def _apply_fingerprinting(self, content: ContentItem, result: ProtectionResult):
        """Apply content fingerprinting"""
        try:            if self._fingerprinter:
                fingerprint = await self._fingerprinter.create_fingerprint(content)
                result.fingerprint_created = True
                result.protection_metadata['fingerprint'] = fingerprint
        except Exception as e:
            result.errors.append(f"Fingerprinting failed: {str(e)}")
    
    async def _apply_watermarking(self, content: ContentItem, result: ProtectionResult):
        """Apply digital watermarking"""
        try:            if self._watermark_engine:
                watermark = await self._watermark_engine.apply_watermark(content)
                result.watermark_applied = True
                result.protection_metadata['watermark'] = watermark
        except Exception as e:
            result.errors.append(f"Watermarking failed: {str(e)}")
    
    async def _apply_blockchain_verification(self, content: ContentItem, result: ProtectionResult):
        """Apply blockchain verification"""
        try:            if self._blockchain_verifier:
                proof = await self._blockchain_verifier.register_ownership(content, result.protection_id)
                result.blockchain_registered = True
                result.protection_metadata['blockchain_proof'] = proof
        except Exception as e:
            result.errors.append(f"Blockchain verification failed: {str(e)}")
    
    async def _apply_encryption(self, content: ContentItem, result: ProtectionResult):
        """Apply content encryption"""
        try:            if self._encryption_engine:
                encryption_key = await self._encryption_engine.encrypt_content(content)
                result.encryption_applied = True
                result.protection_metadata['encryption_key'] = encryption_key
        except Exception as e:
            result.errors.append(f"Encryption failed: {str(e)}")
    
    async def _register_with_rights_management(self, content: ContentItem, result: ProtectionResult):
        """Register with rights management system"""
        try:            if self._rights_manager:
                registration = await self._rights_manager.register_content(content, result.protection_id)
                result.protection_metadata['rights_registration'] = registration
        except Exception as e:
            result.errors.append(f"Rights management registration failed: {str(e)}")
    
    async def _setup_advanced_monitoring(self, content: ContentItem, result: ProtectionResult):
        """Setup advanced monitoring for enterprise protection"""
        try:            if self._piracy_detector:
                monitoring = await self._piracy_detector.setup_monitoring(content.content_id)
                result.protection_metadata['monitoring_setup'] = monitoring
        except Exception as e:
            result.errors.append(f"Advanced monitoring setup failed: {str(e)}")
    
    def _calculate_protection_strength(self, result: ProtectionResult) -> float:
        """Calculate overall protection strength"""
        strength = 0.0        
        if result.fingerprint_created:
            strength += 0.2
        if result.watermark_applied:
            strength += 0.3
        if result.blockchain_registered:
            strength += 0.3
        if result.encryption_applied:
            strength += 0.2
        
        return min(strength, 1.0)
    
    def _calculate_expiration(self, protection_level: ProtectionLevel) -> datetime:
        """Calculate protection expiration based on level"""
        days_map = {            ProtectionLevel.BASIC: 30,
            ProtectionLevel.STANDARD: 90,
            ProtectionLevel.PREMIUM: 365,
            ProtectionLevel.ENTERPRISE: 1825  # 5 years
        }
        
        days = days_map.get(protection_level, 90)
        return utc_now() + timedelta(days=days)
    
    async def _initiate_takedown(self, detection: Dict[str, Any]):
        """Initiate DMCA takedown for serious violations"""
        try:            if self._dmca_manager:
                await self._dmca_manager.initiate_takedown(detection)
                self.metrics['successful_takedowns'] += 1
        except Exception as e:
            self.logger.error(f"Takedown initiation failed: {str(e)}")
    
    # Component initialization methods
    
    async def _init_watermark_engine(self):
        """Initialize watermark engine"""
        try:            from .watermarking import WatermarkEngine
            self._watermark_engine = WatermarkEngine(self.config.get('watermark', {}))
            await self._watermark_engine.initialize()
        except ImportError:
            self.logger.warning("Watermark engine not available")
    
    async def _init_fingerprinter(self):
        """Initialize content fingerprinter"""
        try:            from .fingerprinting import ContentFingerprinter
            self._fingerprinter = ContentFingerprinter(self.config.get('fingerprint', {}))
            await self._fingerprinter.initialize()
        except ImportError:
            self.logger.warning("Content fingerprinter not available")
    
    async def _init_rights_manager(self):
        """Initialize rights manager"""
        try:            from .rights_management import RightsManager
            self._rights_manager = RightsManager(self.config.get('rights', {}))
            await self._rights_manager.initialize()
        except ImportError:
            self.logger.warning("Rights manager not available")
    
    async def _init_dmca_manager(self):
        """Initialize DMCA manager"""
        try:            from .dmca import DMCAManager
            self._dmca_manager = DMCAManager(self.config.get('dmca', {}))
            await self._dmca_manager.initialize()
        except ImportError:
            self.logger.warning("DMCA manager not available")
    
    async def _init_blockchain_verifier(self):
        """Initialize blockchain verifier"""
        try:            from .blockchain import BlockchainVerifier
            self._blockchain_verifier = BlockchainVerifier(self.config.get('blockchain', {}))
            await self._blockchain_verifier.initialize()
        except ImportError:
            self.logger.warning("Blockchain verifier not available")
    
    async def _init_piracy_detector(self):
        """Initialize piracy detector"""
        try:            from .detection import PiracyDetector
            self._piracy_detector = PiracyDetector(self.config.get('detection', {}))
            await self._piracy_detector.initialize()
        except ImportError:
            self.logger.warning("Piracy detector not available")
    
    async def _init_encryption_engine(self):
        """Initialize encryption engine"""
        try:            from .encryption import ContentEncryption
            self._encryption_engine = ContentEncryption(self.config.get('encryption', {}))
            await self._encryption_engine.initialize()
        except ImportError:
            self.logger.warning("Encryption engine not available")
