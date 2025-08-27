"""
Copyright Protection Engine - Comprehensive Copyright Management System

This module provides advanced copyright protection mechanisms including content fingerprinting,
automated rights verification, license management, and infringement detection for multi-format content.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  WARNING: Unauthorized use, reproduction, or distribution of this code is strictly prohibited.
    This system is proprietary and protected by international copyright laws.
    Violations will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import uuid
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..security.encryption import EncryptionService
from ..ai.fingerprinting import FingerprintEngine
from ..models.copyright_models import CopyrightClaim, ProtectedContent, LicenseAgreement


class ContentType(Enum):
    """Types of protected content"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"


class ProtectionLevel(Enum):
    """Content protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class LicenseType(Enum):
    """Copyright license types"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"


class InfringementSeverity(Enum):
    """Infringement severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CopyrightMetadata:
    """Copyright metadata structure"""
    content_id: str
    owner_id: int
    title: str
    description: str
    creation_date: datetime
    registration_number: Optional[str]
    license_type: LicenseType
    protection_level: ProtectionLevel
    content_type: ContentType
    fingerprints: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InfringementReport:
    """Copyright infringement report structure"""
    report_id: str
    original_content_id: str
    infringing_content_id: str
    infringing_url: str
    platform: str
    similarity_score: float
    severity: InfringementSeverity
    evidence: Dict[str, Any]
    detected_at: datetime
    confidence_score: float
    automated_detection: bool = True


@dataclass
class LicenseVerification:
    """License verification result"""
    content_id: str
    user_id: int
    license_valid: bool
    license_type: LicenseType
    usage_rights: List[str]
    restrictions: List[str]
    expiry_date: Optional[datetime]
    verification_score: float


class CopyrightProtectionEngine:
    """
    Comprehensive Copyright Protection Engine
    
    Provides multi-format content protection, automated infringement detection,
    license management, and copyright enforcement capabilities.
    """
    
    def __init__(self, 
                 db_manager: DatabaseManager,
                 cache_manager: CacheManager,
                 encryption_service: EncryptionService,
                 fingerprint_engine: FingerprintEngine):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.encryption_service = encryption_service
        self.fingerprint_engine = fingerprint_engine
        self.logger = logging.getLogger(__name__)
        
        # Protection configuration
        self.config = {
            "similarity_threshold": {
                "audio": 0.85,
                "video": 0.80,
                "image": 0.90,
                "text": 0.75
            },
            "monitoring_platforms": [
                "youtube", "tiktok", "instagram", "twitter", 
                "facebook", "spotify", "soundcloud", "twitch"
            ],
            "protection_levels": {
                "basic": {"monitoring_frequency": 24, "features": ["fingerprinting"]},
                "standard": {"monitoring_frequency": 12, "features": ["fingerprinting", "watermarking"]},
                "premium": {"monitoring_frequency": 6, "features": ["fingerprinting", "watermarking", "real_time"]},
                "enterprise": {"monitoring_frequency": 1, "features": ["fingerprinting", "watermarking", "real_time", "legal_support"]}
            },
            "automated_actions": {
                "takedown_threshold": 0.90,
                "warning_threshold": 0.75,
                "monitoring_threshold": 0.60
            }
        }
        
        # Active protection registry
        self.protected_content = {}
        self.active_monitors = {}
    
    async def register_content_protection(self, metadata: CopyrightMetadata) -> Dict[str, Any]:
        """
        Register content for copyright protection with fingerprinting
        
        Args:
            metadata: Copyright metadata and content information
            
        Returns:
            Dict: Registration result with protection details
        """
        try:
            # Generate content fingerprints
            fingerprints = await self._generate_content_fingerprints(metadata)
            
            # Create protection record
            protection_id = await self._create_protection_record(metadata, fingerprints)
            
            # Initialize monitoring
            monitoring_config = await self._setup_content_monitoring(metadata)
            
            # Store in active registry
            self.protected_content[metadata.content_id] = {
                "protection_id": protection_id,
                "metadata": metadata,
                "fingerprints": fingerprints,
                "monitoring": monitoring_config,
                "registered_at": datetime.now()
            }
            
            # Schedule monitoring tasks
            await self._schedule_monitoring_tasks(metadata.content_id, metadata.protection_level)
            
            result = {
                "success": True,
                "protection_id": protection_id,
                "content_id": metadata.content_id,
                "fingerprints_generated": len(fingerprints),
                "monitoring_active": True,
                "protection_level": metadata.protection_level.value,
                "estimated_coverage": self._calculate_protection_coverage(metadata)
            }
            
            self.logger.info(f"Content protection registered: {metadata.content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error registering content protection: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content_id": metadata.content_id
            }
    
    async def detect_copyright_infringement(self, 
                                          suspicious_content: Dict[str, Any],
                                          platform: str) -> Optional[InfringementReport]:
        """
        Detect potential copyright infringement using AI fingerprinting
        
        Args:
            suspicious_content: Content data to analyze
            platform: Platform where content was found
            
        Returns:
            InfringementReport: Infringement details if detected
        """
        try:
            # Generate fingerprint for suspicious content
            suspect_fingerprint = await self.fingerprint_engine.generate_fingerprint(
                content=suspicious_content["content"],
                content_type=suspicious_content["type"]
            )
            
            # Search for similar protected content
            matches = await self._search_protected_content(
                fingerprint=suspect_fingerprint,
                content_type=suspicious_content["type"]
            )
            
            if not matches:
                return None
            
            # Analyze best match
            best_match = max(matches, key=lambda x: x["similarity_score"])
            
            # Check if similarity exceeds threshold
            threshold = self.config["similarity_threshold"][suspicious_content["type"]]
            
            if best_match["similarity_score"] < threshold:
                return None
            
            # Determine infringement severity
            severity = self._calculate_infringement_severity(
                similarity_score=best_match["similarity_score"],
                content_type=suspicious_content["type"],
                platform=platform
            )
            
            # Generate infringement report
            report = InfringementReport(
                report_id=str(uuid.uuid4()),
                original_content_id=best_match["content_id"],
                infringing_content_id=suspicious_content.get("id", "unknown"),
                infringing_url=suspicious_content.get("url", ""),
                platform=platform,
                similarity_score=best_match["similarity_score"],
                severity=severity,
                evidence={
                    "fingerprint_match": best_match,
                    "detection_method": "automated_fingerprinting",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "suspect_metadata": suspicious_content.get("metadata", {})
                },
                detected_at=datetime.now(),
                confidence_score=self._calculate_confidence_score(best_match),
                automated_detection=True
            )
            
            # Store infringement report
            await self._store_infringement_report(report)
            
            # Trigger automated response if applicable
            await self._handle_infringement_response(report)
            
            self.logger.warning(f"Copyright infringement detected: {report.report_id}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error detecting copyright infringement: {str(e)}")
            return None
    
    async def verify_content_license(self, 
                                   content_id: str, 
                                   user_id: int,
                                   intended_use: str) -> LicenseVerification:
        """
        Verify user's license to use specific content
        
        Args:
            content_id: Content to verify license for
            user_id: User requesting verification
            intended_use: Intended use case
            
        Returns:
            LicenseVerification: License verification result
        """
        try:
            # Get content protection details
            protected_content = await self._get_protected_content(content_id)
            
            if not protected_content:
                return LicenseVerification(
                    content_id=content_id,
                    user_id=user_id,
                    license_valid=False,
                    license_type=LicenseType.EXCLUSIVE,
                    usage_rights=[],
                    restrictions=["Content not found or not protected"],
                    expiry_date=None,
                    verification_score=0.0
                )
            
            # Check user's licenses
            user_licenses = await self._get_user_licenses(user_id, content_id)
            
            # Verify license validity
            valid_license = None
            for license_agreement in user_licenses:
                if await self._is_license_valid(license_agreement, intended_use):
                    valid_license = license_agreement
                    break
            
            if not valid_license:
                return LicenseVerification(
                    content_id=content_id,
                    user_id=user_id,
                    license_valid=False,
                    license_type=LicenseType.EXCLUSIVE,
                    usage_rights=[],
                    restrictions=["No valid license found for intended use"],
                    expiry_date=None,
                    verification_score=0.0
                )
            
            # Extract usage rights and restrictions
            usage_rights = valid_license.usage_rights or []
            restrictions = valid_license.restrictions or []
            
            # Calculate verification score
            verification_score = self._calculate_license_score(valid_license, intended_use)
            
            verification = LicenseVerification(
                content_id=content_id,
                user_id=user_id,
                license_valid=True,
                license_type=LicenseType(valid_license.license_type),
                usage_rights=usage_rights,
                restrictions=restrictions,
                expiry_date=valid_license.expiry_date,
                verification_score=verification_score
            )
            
            # Cache verification result
            cache_key = f"license_verification:{content_id}:{user_id}:{intended_use}"
            await self.cache_manager.set(cache_key, verification.__dict__, ttl=1800)
            
            return verification
            
        except Exception as e:
            self.logger.error(f"Error verifying content license: {str(e)}")
            return LicenseVerification(
                content_id=content_id,
                user_id=user_id,
                license_valid=False,
                license_type=LicenseType.EXCLUSIVE,
                usage_rights=[],
                restrictions=[f"Verification error: {str(e)}"],
                expiry_date=None,
                verification_score=0.0
            )
    
    async def create_license_agreement(self, 
                                     content_id: str,
                                     licensee_id: int,
                                     license_terms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new license agreement for protected content
        
        Args:
            content_id: Content to license
            licensee_id: User receiving license
            license_terms: License terms and conditions
            
        Returns:
            Dict: License creation result
        """
        try:
            # Validate content ownership
            content_owner = await self._get_content_owner(content_id)
            if not content_owner:
                return {
                    "success": False,
                    "error": "Content not found or not protected"
                }
            
            # Generate license agreement
            license_id = str(uuid.uuid4())
            
            with self.db_manager.get_session() as session:
                license_agreement = LicenseAgreement(
                    id=license_id,
                    content_id=content_id,
                    licensor_id=content_owner["owner_id"],
                    licensee_id=licensee_id,
                    license_type=license_terms["type"],
                    usage_rights=license_terms.get("usage_rights", []),
                    restrictions=license_terms.get("restrictions", []),
                    financial_terms=self.encryption_service.encrypt(
                        json.dumps(license_terms.get("financial_terms", {}))
                    ),
                    start_date=license_terms.get("start_date", datetime.now()),
                    expiry_date=license_terms.get("expiry_date"),
                    auto_renewal=license_terms.get("auto_renewal", False),
                    status="active",
                    created_at=datetime.now()
                )
                
                session.add(license_agreement)
                session.commit()
            
            # Generate license certificate
            certificate = await self._generate_license_certificate(license_agreement)
            
            # Send notifications
            await self._send_license_notifications(license_agreement)
            
            result = {
                "success": True,
                "license_id": license_id,
                "content_id": content_id,
                "licensee_id": licensee_id,
                "certificate": certificate,
                "start_date": license_agreement.start_date.isoformat(),
                "expiry_date": license_agreement.expiry_date.isoformat() if license_agreement.expiry_date else None
            }
            
            self.logger.info(f"License agreement created: {license_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating license agreement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def monitor_platform_infringement(self, platform: str) -> List[InfringementReport]:
        """
        Monitor specific platform for copyright infringement
        
        Args:
            platform: Platform to monitor
            
        Returns:
            List[InfringementReport]: Detected infringements
        """
        try:
            infringement_reports = []
            
            # Get platform-specific crawler
            crawler = await self._get_platform_crawler(platform)
            
            if not crawler:
                self.logger.warning(f"No crawler available for platform: {platform}")
                return []
            
            # Get recent content from platform
            recent_content = await crawler.get_recent_content(
                limit=1000,
                content_types=["audio", "video", "image"]
            )
            
            # Analyze each piece of content
            for content in recent_content:
                infringement = await self.detect_copyright_infringement(
                    suspicious_content=content,
                    platform=platform
                )
                
                if infringement:
                    infringement_reports.append(infringement)
            
            # Update monitoring statistics
            await self._update_monitoring_stats(platform, len(recent_content), len(infringement_reports))
            
            self.logger.info(f"Platform monitoring completed: {platform} - {len(infringement_reports)} infringements detected")
            
            return infringement_reports
            
        except Exception as e:
            self.logger.error(f"Error monitoring platform infringement: {str(e)}")
            return []
    
    async def generate_copyright_report(self, 
                                      owner_id: int, 
                                      period_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive copyright protection report
        
        Args:
            owner_id: Content owner ID
            period_days: Reporting period in days
            
        Returns:
            Dict: Comprehensive copyright report
        """
        try:
            start_date = datetime.now() - timedelta(days=period_days)
            
            with self.db_manager.get_session() as session:
                # Get protected content
                protected_content = session.query(ProtectedContent).filter(
                    ProtectedContent.owner_id == owner_id
                ).all()
                
                # Get infringement reports
                infringement_reports = []
                for content in protected_content:
                    reports = session.query(CopyrightClaim).filter(
                        and_(
                            CopyrightClaim.original_content_id == content.id,
                            CopyrightClaim.detected_at >= start_date
                        )
                    ).all()
                    infringement_reports.extend(reports)
                
                # Calculate metrics
                total_protected = len(protected_content)
                total_infringements = len(infringement_reports)
                
                # Group by severity
                severity_breakdown = {}
                for report in infringement_reports:
                    severity = report.severity
                    severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
                
                # Group by platform
                platform_breakdown = {}
                for report in infringement_reports:
                    platform = report.platform
                    platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
                
                # Calculate protection effectiveness
                protection_score = self._calculate_protection_effectiveness(
                    protected_content, infringement_reports
                )
                
                report = {
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": datetime.now().isoformat(),
                        "days": period_days
                    },
                    "content_protection": {
                        "total_protected_content": total_protected,
                        "content_types": self._analyze_content_types(protected_content),
                        "protection_levels": self._analyze_protection_levels(protected_content)
                    },
                    "infringement_detection": {
                        "total_infringements": total_infringements,
                        "severity_breakdown": severity_breakdown,
                        "platform_breakdown": platform_breakdown,
                        "detection_rate": total_infringements / total_protected if total_protected > 0 else 0
                    },
                    "protection_effectiveness": {
                        "overall_score": protection_score,
                        "coverage_percentage": self._calculate_coverage_percentage(protected_content),
                        "response_time_avg": self._calculate_avg_response_time(infringement_reports)
                    },
                    "financial_impact": {
                        "potential_losses_prevented": self._calculate_potential_losses(infringement_reports),
                        "enforcement_costs": self._calculate_enforcement_costs(infringement_reports),
                        "licensing_revenue": await self._calculate_licensing_revenue(owner_id, start_date)
                    },
                    "recommendations": await self._generate_protection_recommendations(
                        owner_id, protected_content, infringement_reports
                    ),
                    "generated_at": datetime.now().isoformat()
                }
                
                return report
                
        except Exception as e:
            self.logger.error(f"Error generating copyright report: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_content_fingerprints(self, metadata: CopyrightMetadata) -> Dict[str, str]:
        """Generate fingerprints for different content aspects"""
        fingerprints = {}
        
        try:
            # Audio fingerprint
            if metadata.content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.PODCAST]:
                audio_fingerprint = await self.fingerprint_engine.generate_audio_fingerprint(
                    metadata.content_id
                )
                fingerprints["audio"] = audio_fingerprint
            
            # Visual fingerprint
            if metadata.content_type in [ContentType.VIDEO, ContentType.IMAGE]:
                visual_fingerprint = await self.fingerprint_engine.generate_visual_fingerprint(
                    metadata.content_id
                )
                fingerprints["visual"] = visual_fingerprint
            
            # Text fingerprint
            if metadata.content_type in [ContentType.TEXT, ContentType.MIXED_MEDIA]:
                text_fingerprint = await self.fingerprint_engine.generate_text_fingerprint(
                    metadata.content_id
                )
                fingerprints["text"] = text_fingerprint
            
            # Metadata fingerprint
            metadata_fingerprint = await self.fingerprint_engine.generate_metadata_fingerprint(
                metadata.metadata
            )
            fingerprints["metadata"] = metadata_fingerprint
            
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Error generating content fingerprints: {str(e)}")
            return {}
    
    async def _create_protection_record(self, 
                                      metadata: CopyrightMetadata, 
                                      fingerprints: Dict[str, str]) -> str:
        """Create database record for protected content"""
        try:
            protection_id = str(uuid.uuid4())
            
            with self.db_manager.get_session() as session:
                protected_content = ProtectedContent(
                    id=protection_id,
                    content_id=metadata.content_id,
                    owner_id=metadata.owner_id,
                    title=metadata.title,
                    description=metadata.description,
                    content_type=metadata.content_type.value,
                    protection_level=metadata.protection_level.value,
                    license_type=metadata.license_type.value,
                    creation_date=metadata.creation_date,
                    registration_number=metadata.registration_number,
                    fingerprints=json.dumps(fingerprints),
                    metadata=json.dumps(metadata.metadata),
                    status="active",
                    created_at=datetime.now()
                )
                
                session.add(protected_content)
                session.commit()
                
                return protection_id
                
        except Exception as e:
            self.logger.error(f"Error creating protection record: {str(e)}")
            raise
    
    async def get_protection_status(self, content_id: str) -> Dict[str, Any]:
        """Get comprehensive protection status for content"""
        try:
            # Check if content is in active registry
            if content_id in self.protected_content:
                active_protection = self.protected_content[content_id]
                
                # Get recent infringement reports
                recent_reports = await self._get_recent_infringement_reports(content_id, days=7)
                
                # Calculate protection metrics
                metrics = await self._calculate_protection_metrics(content_id)
                
                return {
                    "content_id": content_id,
                    "protection_active": True,
                    "protection_level": active_protection["metadata"].protection_level.value,
                    "registered_at": active_protection["registered_at"].isoformat(),
                    "fingerprints_count": len(active_protection["fingerprints"]),
                    "recent_infringements": len(recent_reports),
                    "protection_metrics": metrics,
                    "monitoring_status": "active",
                    "last_scan": datetime.now().isoformat()
                }
            
            # Check database for inactive protection
            with self.db_manager.get_session() as session:
                protected = session.query(ProtectedContent).filter(
                    ProtectedContent.content_id == content_id
                ).first()
                
                if protected:
                    return {
                        "content_id": content_id,
                        "protection_active": False,
                        "protection_level": protected.protection_level,
                        "registered_at": protected.created_at.isoformat(),
                        "status": protected.status,
                        "monitoring_status": "inactive"
                    }
                
                return {
                    "content_id": content_id,
                    "protection_active": False,
                    "protected": False,
                    "message": "Content not registered for protection"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting protection status: {str(e)}")
            return {
                "content_id": content_id,
                "error": str(e)
            }
