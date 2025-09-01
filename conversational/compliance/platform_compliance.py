"""Platform Compliance Manager - Multi-Platform Legal Compliance System

This module manages compliance requirements across multiple content distribution platforms
including YouTube, TikTok, Instagram, Spotify, and other social media platforms.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

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
import json
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..security.encryption import EncryptionService
from ..utils.http_client import HTTPClient
from ..models.platform_models import PlatformCompliance, ContentSubmission, PlatformPolicy


class Platform(Enum):
    """
Supported platforms"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    DISCORD = "discord"


class ComplianceStatus(Enum):
    """Platform compliance status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_UPDATE = "requires_update"
    SUSPENDED = "suspended"


class ContentRating(Enum):
    """Content rating classifications"""

    GENERAL = "general"
    TEEN = "teen"
    MATURE = "mature"
    EXPLICIT = "explicit"
    EDUCATIONAL = "educational"


class PolicyViolationType(Enum):
    """Types of policy violations"""

    COPYRIGHT = "copyright"
    CONTENT_GUIDELINES = "content_guidelines"
    COMMUNITY_STANDARDS = "community_standards"
    SPAM = "spam"
    HARASSMENT = "harassment"
    VIOLENCE = "violence"
    ADULT_CONTENT = "adult_content"
    MISINFORMATION = "misinformation"


@dataclass
class PlatformRequirements:
    """Platform-specific compliance requirements"""
    platform: Platform
    content_guidelines: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    monetization_policies: Dict[str, Any]
    copyright_policies: Dict[str, Any]
    community_guidelines: Dict[str, Any]
    api_compliance: Dict[str, Any]
    last_updated: datetime


@dataclass
class ComplianceAssessment:
    """
Compliance assessment result"""
    platform: Platform
    content_id: str
    compliance_status: ComplianceStatus
    compliance_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    auto_fixable: bool
    assessment_time: datetime


@dataclass
class ContentSubmissionResult:
    """
Content submission result"""
    submission_id: str
    platform: Platform
    content_id: str
    status: str
    platform_content_id: Optional[str]
    warnings: List[str]
    errors: List[str]
    compliance_check: ComplianceAssessment


class PlatformComplianceManager:
    """
    Multi-Platform Compliance Management System
    
    Manages compliance requirements across multiple content distribution platforms,
    ensuring content meets platform-specific guidelines and policies.
    """
    
    def __init__(self, 
                 db_manager: DatabaseManager,
                 cache_manager: CacheManager,
                 encryption_service: EncryptionService,
                 http_client: HTTPClient):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.encryption_service = encryption_service
        self.http_client = http_client
        self.logger = logging.getLogger(__name__)
        
        # Platform configurations
        self.platform_configs = {}
        self.compliance_rules = {}
        
        # Initialize platform requirements
        asyncio.create_task(self._initialize_platform_requirements())
    
    async def assess_platform_compliance(self, 
                                       content_id: str, 
                                       platform: Platform,
                                       content_metadata: Dict[str, Any]) -> ComplianceAssessment:
        """
        Assess content compliance with platform-specific requirements
        
        Args:
            content_id: Content identifier
            platform: Target platform
            content_metadata: Content metadata and details
            
        Returns:
            ComplianceAssessment: Detailed compliance assessment
        """
        try:
            assessment_start = datetime.now()
            
            # Get platform requirements
            requirements = await self._get_platform_requirements(platform)
            
            if not requirements:
                return ComplianceAssessment(
                    platform=platform,
                    content_id=content_id,
                    compliance_status=ComplianceStatus.PENDING_REVIEW,
                    compliance_score=0.0,
                    violations=[{"type": "system_error", "message": "Platform requirements not available"}],
                    recommendations=["Contact support for platform requirements"],
                    auto_fixable=False,
                    assessment_time=assessment_start
                )
            
            violations = []
            compliance_score = 100.0
            recommendations = []
            
            # Check content guidelines
            content_violations = await self._check_content_guidelines(
                content_metadata, requirements.content_guidelines
            )
            violations.extend(content_violations)
            
            # Check technical requirements
            technical_violations = await self._check_technical_requirements(
                content_metadata, requirements.technical_requirements
            )
            violations.extend(technical_violations)
            
            # Check monetization eligibility
            monetization_violations = await self._check_monetization_compliance(
                content_metadata, requirements.monetization_policies
            )
            violations.extend(monetization_violations)
            
            # Check copyright compliance
            copyright_violations = await self._check_copyright_compliance(
                content_metadata, requirements.copyright_policies
            )
            violations.extend(copyright_violations)
            
            # Check community guidelines
            community_violations = await self._check_community_guidelines(
                content_metadata, requirements.community_guidelines
            )
            violations.extend(community_violations)
            
            # Calculate compliance score
            if violations:
                violation_penalty = min(100.0, len(violations) * 15.0)
                severity_penalty = sum([v.get("severity_weight", 10) for v in violations])
                compliance_score = max(0.0, 100.0 - violation_penalty - severity_penalty)
            
            # Determine compliance status
            if compliance_score >= 90.0:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 70.0:
                status = ComplianceStatus.REQUIRES_UPDATE
            elif compliance_score >= 50.0:
                status = ComplianceStatus.PENDING_REVIEW
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                violations, platform, content_metadata
            )
            
            # Check if violations are auto-fixable
            auto_fixable = all(v.get("auto_fixable", False) for v in violations)
            
            assessment = ComplianceAssessment(
                platform=platform,
                content_id=content_id,
                compliance_status=status,
                compliance_score=compliance_score / 100.0,
                violations=violations,
                recommendations=recommendations,
                auto_fixable=auto_fixable,
                assessment_time=assessment_start
            )
            
            # Cache assessment result
            cache_key = f"compliance_assessment:{platform.value}:{content_id}"
            await self.cache_manager.set(cache_key, assessment.__dict__, ttl=1800)
            
            self.logger.info(f"Compliance assessment completed: {platform.value} - {status.value}")
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing platform compliance: {str(e)}")
            return ComplianceAssessment(
                platform=platform,
                content_id=content_id,
                compliance_status=ComplianceStatus.PENDING_REVIEW,
                compliance_score=0.0,
                violations=[{"type": "assessment_error", "message": str(e)}],
                recommendations=["Manual review required"],
                auto_fixable=False,
                assessment_time=datetime.now()
            )
    
    async def submit_content_to_platform(self, 
                                       content_id: str,
                                       platform: Platform,
                                       content_data: Dict[str, Any],
                                       submission_options: Dict[str, Any] = None) -> ContentSubmissionResult:
        """
        Submit content to platform with compliance verification
        
        Args:
            content_id: Content identifier
            platform: Target platform
            content_data: Content data and metadata
            submission_options: Platform-specific submission options
            
        Returns:
            ContentSubmissionResult: Submission result with compliance status
        """
        try:
            submission_id = str(uuid.uuid4())
            
            # Pre-submission compliance check
            compliance_assessment = await self.assess_platform_compliance(
                content_id, platform, content_data
            )
            
            # Block submission if non-compliant
            if compliance_assessment.compliance_status == ComplianceStatus.NON_COMPLIANT:
                return ContentSubmissionResult(
                    submission_id=submission_id,
                    platform=platform,
                    content_id=content_id,
                    status="rejected",
                    platform_content_id=None,
                    warnings=[],
                    errors=["Content does not meet platform compliance requirements"],
                    compliance_check=compliance_assessment
                )
            
            # Apply auto-fixes if available
            if compliance_assessment.auto_fixable and compliance_assessment.violations:
                content_data = await self._apply_auto_fixes(
                    content_data, compliance_assessment.violations, platform
                )
            
            # Get platform API client
            api_client = await self._get_platform_api_client(platform)
            
            if not api_client:
                return ContentSubmissionResult(
                    submission_id=submission_id,
                    platform=platform,
                    content_id=content_id,
                    status="failed",
                    platform_content_id=None,
                    warnings=[],
                    errors=["Platform API not available"],
                    compliance_check=compliance_assessment
                )
            
            # Prepare submission payload
            submission_payload = await self._prepare_submission_payload(
                content_data, platform, submission_options or {}
            )
            
            # Submit to platform
            submission_result = await api_client.submit_content(submission_payload)
            
            # Process platform response
            if submission_result.get("success"):
                status = "submitted"
                platform_content_id = submission_result.get("content_id")
                warnings = submission_result.get("warnings", [])
                errors = []
            else:
                status = "failed"
                platform_content_id = None
                warnings = submission_result.get("warnings", [])
                errors = submission_result.get("errors", ["Submission failed"])
            
            # Store submission record
            await self._store_submission_record(
                submission_id, platform, content_id, status, submission_result
            )
            
            result = ContentSubmissionResult(
                submission_id=submission_id,
                platform=platform,
                content_id=content_id,
                status=status,
                platform_content_id=platform_content_id,
                warnings=warnings,
                errors=errors,
                compliance_check=compliance_assessment
            )
            
            self.logger.info(f"Content submitted to {platform.value}: {status}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error submitting content to platform: {str(e)}")
            return ContentSubmissionResult(
                submission_id=str(uuid.uuid4()),
                platform=platform,
                content_id=content_id,
                status="error",
                platform_content_id=None,
                warnings=[],
                errors=[str(e)],
                compliance_check=ComplianceAssessment(
                    platform=platform,
                    content_id=content_id,
                    compliance_status=ComplianceStatus.PENDING_REVIEW,
                    compliance_score=0.0,
                    violations=[],
                    recommendations=[],
                    auto_fixable=False,
                    assessment_time=datetime.now()
                )
            )
    
    async def monitor_platform_policies(self) -> Dict[str, Any]:
        """
        Monitor platform policy changes and update compliance rules
        
        Returns:
            Dict: Policy monitoring results
        """
        try:
            policy_updates = {}
            
            for platform in Platform:
                try:
                    # Check for policy updates
                    current_policies = await self._fetch_current_platform_policies(platform)
                    cached_policies = await self._get_cached_platform_policies(platform)
                    
                    if current_policies != cached_policies:
                        # Policy change detected
                        changes = await self._analyze_policy_changes(
                            cached_policies, current_policies, platform
                        )
                        
                        # Update cached policies
                        await self._update_cached_platform_policies(platform, current_policies)
                        
                        policy_updates[platform.value] = {
                            "updated": True,
                            "changes": changes,
                            "last_update": datetime.now().isoformat()
                        }
                        
                        # Notify affected users
                        await self._notify_policy_changes(platform, changes)
                    else:
                        policy_updates[platform.value] = {
                            "updated": False,
                            "last_check": datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    policy_updates[platform.value] = {
                        "error": str(e),
                        "last_check": datetime.now().isoformat()
                    }
            
            self.logger.info(f"Platform policy monitoring completed: {len(policy_updates)} platforms checked")
            
            return {
                "monitoring_results": policy_updates,
                "total_platforms": len(Platform),
                "updated_platforms": len([p for p in policy_updates.values() if p.get("updated")]),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring platform policies: {str(e)}")
            return {"error": str(e)}
    
    async def get_compliance_recommendations(self, 
                                           content_id: str,
                                           target_platforms: List[Platform]) -> Dict[str, Any]:
        """
        Get compliance recommendations for multiple platforms
        
        Args:
            content_id: Content identifier
            target_platforms: List of target platforms
            
        Returns:
            Dict: Compliance recommendations for each platform
        """
        try:
            # Get content metadata
            content_metadata = await self._get_content_metadata(content_id)
            
            if not content_metadata:
                return {
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            platform_recommendations = {}
            
            for platform in target_platforms:
                try:
                    # Assess compliance
                    assessment = await self.assess_platform_compliance(
                        content_id, platform, content_metadata
                    )
                    
                    # Generate detailed recommendations
                    detailed_recommendations = await self._generate_detailed_recommendations(
                        assessment, platform, content_metadata
                    )
                    
                    platform_recommendations[platform.value] = {
                        "compliance_status": assessment.compliance_status.value,
                        "compliance_score": assessment.compliance_score,
                        "violations_count": len(assessment.violations),
                        "auto_fixable": assessment.auto_fixable,
                        "recommendations": detailed_recommendations,
                        "estimated_fix_time": self._estimate_fix_time(assessment.violations),
                        "priority_level": self._calculate_priority_level(assessment)
                    }
                    
                except Exception as e:
                    platform_recommendations[platform.value] = {
                        "error": str(e),
                        "compliance_status": "unknown"
                    }
            
            # Generate cross-platform optimization suggestions
            optimization_suggestions = await self._generate_cross_platform_optimizations(
                platform_recommendations, content_metadata
            )
            
            return {
                "content_id": content_id,
                "platform_recommendations": platform_recommendations,
                "cross_platform_optimizations": optimization_suggestions,
                "overall_readiness": self._calculate_overall_readiness(platform_recommendations),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting compliance recommendations: {str(e)}")
            return {
                "error": str(e),
                "content_id": content_id
            }
    
    async def _initialize_platform_requirements(self):
        """Initialize platform-specific requirements and policies"""
        try:
            # YouTube requirements
            self.platform_configs[Platform.YOUTUBE] = {
                "content_guidelines": {
                    "max_duration": 43200,  # 12 hours
                    "min_duration": 1,
                    "supported_formats": ["mp4", "avi", "mov", "wmv"],
                    "max_file_size": 137438953472,  # 128 GB
                    "prohibited_content": ["violence", "hate_speech", "spam"],
                    "age_restrictions": True
                },
                "technical_requirements": {
                    "video_codecs": ["H.264", "H.265"],
                    "audio_codecs": ["AAC", "MP3"],
                    "max_resolution": "8K",
                    "frame_rates": [24, 25, 30, 48, 50, 60]
                },
                "monetization_policies": {
                    "min_subscribers": 1000,
                    "min_watch_hours": 4000,
                    "advertiser_friendly": True,
                    "copyright_claims": 0
                }
            }
            
            # TikTok requirements
            self.platform_configs[Platform.TIKTOK] = {
                "content_guidelines": {
                    "max_duration": 180,  # 3 minutes
                    "min_duration": 3,
                    "supported_formats": ["mp4", "mov"],
                    "max_file_size": 287334400,  # 274 MB
                    "vertical_preferred": True,
                    "prohibited_content": ["adult_content", "violence", "misinformation"]
                },
                "technical_requirements": {
                    "aspect_ratio": "9:16",
                    "min_resolution": "720x1280",
                    "max_resolution": "1080x1920",
                    "frame_rate": 30
                }
            }
            
            # Instagram requirements
            self.platform_configs[Platform.INSTAGRAM] = {
                "content_guidelines": {
                    "max_duration": 900,  # 15 minutes for IGTV
                    "min_duration": 1,
                    "supported_formats": ["mp4", "jpg", "png"],
                    "max_file_size": 4294967296,  # 4 GB
                    "prohibited_content": ["nudity", "violence", "spam", "hate_speech"]
                },
                "technical_requirements": {
                    "aspect_ratios": ["1:1", "4:5", "9:16"],
                    "min_resolution": "600x600",
                    "max_resolution": "1080x1080",
                    "frame_rates": [23, 25, 30]
                }
            }
            
            # Spotify requirements
            self.platform_configs[Platform.SPOTIFY] = {
                "content_guidelines": {
                    "supported_formats": ["mp3", "wav", "flac"],
                    "min_duration": 7,
                    "max_file_size": 52428800,  # 50 MB
                    "audio_quality": "320kbps",
                    "prohibited_content": ["hate_speech", "explicit_violence"]
                },
                "technical_requirements": {
                    "sample_rate": 44100,
                    "bit_depth": 16,
                    "channels": 2
                },
                "metadata_requirements": {
                    "title": "required",
                    "artist": "required",
                    "album": "required",
                    "genre": "required",
                    "isrc": "recommended"
                }
            }
            
            self.logger.info("Platform requirements initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing platform requirements: {str(e)}")
    
    async def _check_content_guidelines(self, 
                                      content_metadata: Dict[str, Any],
                                      guidelines: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check content against platform content guidelines"""
        violations = []
        
        try:
            # Check duration limits
            duration = content_metadata.get("duration")
            if duration:
                if "max_duration" in guidelines and duration > guidelines["max_duration"]:
                    violations.append({
                        "type": PolicyViolationType.CONTENT_GUIDELINES.value,
                        "message": f"Content duration ({duration}s) exceeds maximum allowed ({guidelines['max_duration']}s)",
                        "severity_weight": 20,
                        "auto_fixable": True,
                        "fix_suggestion": "Trim content to fit duration requirements"
                    })
                
                if "min_duration" in guidelines and duration < guidelines["min_duration"]:
                    violations.append({
                        "type": PolicyViolationType.CONTENT_GUIDELINES.value,
                        "message": f"Content duration ({duration}s) below minimum required ({guidelines['min_duration']}s)",
                        "severity_weight": 15,
                        "auto_fixable": False,
                        "fix_suggestion": "Add content to meet minimum duration"
                    })
            
            # Check file format
            file_format = content_metadata.get("format")
            if file_format and "supported_formats" in guidelines:
                if file_format not in guidelines["supported_formats"]:
                    violations.append({
                        "type": PolicyViolationType.CONTENT_GUIDELINES.value,
                        "message": f"File format '{file_format}' not supported. Supported formats: {guidelines['supported_formats']}",
                        "severity_weight": 25,
                        "auto_fixable": True,
                        "fix_suggestion": f"Convert to supported format: {guidelines['supported_formats'][0]}"
                    })
            
            # Check file size
            file_size = content_metadata.get("file_size")
            if file_size and "max_file_size" in guidelines:
                if file_size > guidelines["max_file_size"]:
                    violations.append({
                        "type": PolicyViolationType.CONTENT_GUIDELINES.value,
                        "message": f"File size ({file_size} bytes) exceeds maximum allowed ({guidelines['max_file_size']} bytes)",
                        "severity_weight": 20,
                        "auto_fixable": True,
                        "fix_suggestion": "Compress content to reduce file size"
                    })
            
            # Check prohibited content
            content_analysis = content_metadata.get("content_analysis", {})
            prohibited_content = guidelines.get("prohibited_content", [])
            
            for prohibited in prohibited_content:
                if content_analysis.get(prohibited, 0) > 0.7:  # 70% confidence threshold
                    violations.append({
                        "type": PolicyViolationType.CONTENT_GUIDELINES.value,
                        "message": f"Content may contain prohibited material: {prohibited}",
                        "severity_weight": 50,
                        "auto_fixable": False,
                        "fix_suggestion": f"Review and remove {prohibited} content"
                    })
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error checking content guidelines: {str(e)}")
            return [{"type": "system_error", "message": str(e)}]
    
    async def get_platform_status_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive platform compliance dashboard"""
        try:
            dashboard_data = {}
            
            for platform in Platform:
                try:
                    # Get platform statistics
                    stats = await self._get_platform_statistics(platform)
                    
                    # Get recent submissions
                    recent_submissions = await self._get_recent_submissions(platform, days=7)
                    
                    # Get compliance metrics
                    compliance_metrics = await self._get_compliance_metrics(platform)
                    
                    dashboard_data[platform.value] = {
                        "status": "active",
                        "statistics": stats,
                        "recent_submissions": len(recent_submissions),
                        "compliance_rate": compliance_metrics.get("compliance_rate", 0),
                        "average_score": compliance_metrics.get("average_score", 0),
                        "last_policy_update": compliance_metrics.get("last_policy_update"),
                        "api_health": await self._check_api_health(platform)
                    }
                    
                except Exception as e:
                    dashboard_data[platform.value] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            return {
                "platforms": dashboard_data,
                "overall_health": self._calculate_overall_health(dashboard_data),
                "total_platforms": len(Platform),
                "active_platforms": len([p for p in dashboard_data.values() if p.get("status") == "active"]),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating platform status dashboard: {str(e)}")
            return {"error": str(e)}
