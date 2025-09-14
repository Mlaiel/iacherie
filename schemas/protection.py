"""Content Protection & Fingerprinting Schemas for IA Influencer Agent Platform
Professional AI-powered content protection, fingerprinting, and rights management schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class ProtectionRequest(BaseSchema):
    """
Content protection request schema."""
    
    content_id: UUID = Field(description="Content to protect")
    protection_level: str = Field(description="Protection level (basic, standard, premium, enterprise)")
    protection_methods: List[str] = Field(description="Protection methods to apply")
    
    # Fingerprinting options
    fingerprint_types: List[str] = Field(
        default_factory=lambda: ["hash", "perceptual", "semantic"],
        description="Types of fingerprints to generate"
    )
    fingerprint_quality: str = Field(default="high", description="Fingerprint quality level")
    
    # Monitoring options
    enable_monitoring: bool = Field(default=True, description="Enable content monitoring")
    monitoring_platforms: List[str] = Field(default_factory=list, description="Platforms to monitor")
    monitoring_frequency: str = Field(default="daily", description="Monitoring frequency")
    
    # Legal options
    enable_dmca: bool = Field(default=True, description="Enable DMCA takedown automation")
    legal_jurisdiction: str = Field(default="international", description="Legal jurisdiction")
    contact_info: Dict[str, str] = Field(default_factory=dict, description="Legal contact information")
    
    @validator('protection_level')
    def validate_protection_level(cls, v) -> None:
        """Validate protection level."""
        allowed_levels = {"basic", "standard", "premium", "enterprise", "custom"}
        if v not in allowed_levels:
            raise ValueError(f'Protection level must be one of: {", ".join(allowed_levels)}')
        return v


class ProtectionOut(UUIDSchema, TimestampSchema):
    """Content protection status and information schema."""
    
    content_id: UUID
    protection_level: str
    protection_methods: List[str]
    protection_status: str = Field(description="Current protection status")
    
    # Fingerprinting information
    fingerprints_generated: int = Field(default=0, ge=0)
    fingerprint_types: List[str] = Field(default_factory=list)
    primary_fingerprint_id: Optional[UUID] = None
    
    # Monitoring information
    monitoring_active: bool = Field(default=False)
    monitored_platforms: List[str] = Field(default_factory=list)
    last_scan_date: Optional[datetime] = None
    next_scan_date: Optional[datetime] = None
    
    # Protection statistics
    violations_detected: int = Field(default=0, ge=0)
    takedowns_issued: int = Field(default=0, ge=0)
    takedowns_successful: int = Field(default=0, ge=0)
    recovered_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    
    # Security features
    watermark_applied: bool = Field(default=False)
    encryption_enabled: bool = Field(default=False)
    blockchain_verified: bool = Field(default=False)
    
    # Performance metrics
    protection_strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    false_positive_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    detection_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    
    @property
    def takedown_success_rate(self) -> float:
        """Calculate takedown success rate."""
        if self.takedowns_issued == 0:
            return 0.0
        return self.takedowns_successful / self.takedowns_issued


class FingerprintCreate(BaseSchema):
    """
Content fingerprint creation request schema."""
    
    content_id: UUID = Field(description="Content to fingerprint")
    fingerprint_type: str = Field(description="Type of fingerprint to generate")
    quality_level: str = Field(default="high", description="Fingerprint quality level")
    
    # Processing options
    processing_priority: int = Field(default=5, ge=1, le=10)
    enable_caching: bool = Field(default=True, description="Cache fingerprint for future use")
    include_metadata: bool = Field(default=True, description="Include content metadata")
    
    # Algorithm options
    algorithm_version: Optional[str] = Field(None, description="Specific algorithm version")
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('fingerprint_type')
    def validate_fingerprint_type(cls, v) -> None:
        """Validate fingerprint type."""
        allowed_types = {
            "audio_chromaprint", "audio_spectral", "video_perceptual", "video_structural",
            "image_perceptual", "image_phash", "text_semantic", "text_syntactic",
            "multimodal_combined", "hash_sha256", "hash_md5"
        }
        if v not in allowed_types:
            raise ValueError(f'Fingerprint type must be one of: {", ".join(allowed_types)}')
        return v


class FingerprintOut(UUIDSchema, TimestampSchema):
    """Content fingerprint information schema."""
    
    content_id: UUID
    fingerprint_type: str
    algorithm_version: str
    quality_level: str
    
    # Fingerprint data (encoded/hashed for security)
    fingerprint_hash: str = Field(description="Primary fingerprint hash")
    fingerprint_signature: str = Field(description="Fingerprint signature")
    vector_dimension: Optional[int] = Field(None, description="Vector fingerprint dimension")
    
    # Technical metadata
    extraction_method: str = Field(description="Extraction method used")
    processing_time_ms: float = Field(ge=0.0, description="Processing time in milliseconds")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Extraction confidence")
    
    # Quality metrics
    uniqueness_score: float = Field(ge=0.0, le=1.0, description="Fingerprint uniqueness")
    robustness_score: float = Field(ge=0.0, le=1.0, description="Fingerprint robustness")
    precision_score: float = Field(ge=0.0, le=1.0, description="Matching precision")
    recall_score: float = Field(ge=0.0, le=1.0, description="Matching recall")
    
    # Storage and indexing
    is_indexed: bool = Field(default=False, description="Indexed in vector database")
    index_location: Optional[str] = Field(None, description="Vector index location")
    storage_path: Optional[str] = Field(None, description="Fingerprint storage path")
    
    # Usage statistics
    match_attempts: int = Field(default=0, ge=0, description="Number of match attempts")
    successful_matches: int = Field(default=0, ge=0, description="Successful matches")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")


class WatermarkRequest(BaseSchema):
    """Digital watermark application request schema."""
    
    content_id: UUID = Field(description="Content to watermark")
    watermark_type: str = Field(description="Type of watermark to apply")
    watermark_strength: str = Field(default="medium", description="Watermark strength")
    
    # Watermark content
    watermark_text: Optional[str] = Field(None, max_length=200, description="Text watermark")
    watermark_image_url: Optional[HttpUrl] = Field(None, description="Image watermark URL")
    copyright_notice: Optional[str] = Field(None, description="Copyright notice")
    
    # Visual watermark options (for images/videos)
    position: str = Field(default="bottom_right", description="Watermark position")
    opacity: float = Field(default=0.5, ge=0.0, le=1.0, description="Watermark opacity")
    size_percentage: float = Field(default=10.0, ge=1.0, le=50.0, description="Size as percentage")
    
    # Audio watermark options
    embed_frequency: Optional[str] = Field(None, description="Frequency range for audio watermark")
    detection_robustness: str = Field(default="high", description="Detection robustness")
    
    # Advanced options
    invisible_watermark: bool = Field(default=True, description="Use invisible watermarking")
    forensic_watermark: bool = Field(default=False, description="Add forensic watermark")
    batch_processing: bool = Field(default=False, description="Process in batch")
    
    @validator('watermark_type')
    def validate_watermark_type(cls, v) -> None:
        """Validate watermark type."""
        allowed_types = {
            "visible_text", "visible_logo", "invisible_digital", "audio_spectral",
            "video_frame", "steganographic", "forensic", "blockchain_hash"
        }
        if v not in allowed_types:
            raise ValueError(f'Watermark type must be one of: {", ".join(allowed_types)}')
        return v


class WatermarkOut(UUIDSchema, TimestampSchema):
    """Digital watermark information schema."""
    
    content_id: UUID
    watermark_type: str
    watermark_strength: str
    application_method: str = Field(description="Method used to apply watermark")
    
    # Watermark detection information
    detection_key: str = Field(description="Key for watermark detection")
    verification_hash: str = Field(description="Verification hash")
    extraction_algorithm: str = Field(description="Algorithm for extraction")
    
    # Quality metrics
    imperceptibility_score: float = Field(ge=0.0, le=1.0, description="Imperceptibility score")
    robustness_score: float = Field(ge=0.0, le=1.0, description="Robustness against attacks")
    detection_accuracy: float = Field(ge=0.0, le=1.0, description="Detection accuracy")
    
    # Status information
    is_active: bool = Field(default=True, description="Watermark active status")
    is_detectable: bool = Field(default=True, description="Watermark detectability status")
    degradation_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Quality degradation")
    
    # Usage tracking
    detection_attempts: int = Field(default=0, ge=0)
    successful_detections: int = Field(default=0, ge=0)
    false_positive_detections: int = Field(default=0, ge=0)


class ViolationReport(UUIDSchema, TimestampSchema):
    """Content violation report schema."""
    
    content_id: UUID = Field(description="Original protected content")
    violation_type: str = Field(description="Type of violation detected")
    severity_level: str = Field(description="Violation severity level")
    
    # Violation details
    violating_url: HttpUrl = Field(description="URL where violation was found")
    violating_platform: str = Field(description="Platform hosting the violation")
    violating_user: Optional[str] = Field(None, description="User/account responsible")
    violation_description: str = Field(description="Description of the violation")
    
    # Detection information
    detection_method: str = Field(description="Method used to detect violation")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Content similarity score")
    fingerprint_match_id: Optional[UUID] = Field(None, description="Matching fingerprint ID")
    
    # Evidence
    evidence_screenshots: List[HttpUrl] = Field(default_factory=list)
    evidence_metadata: Dict[str, Any] = Field(default_factory=dict)
    forensic_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Legal information
    estimated_damages: Optional[Decimal] = Field(None, ge=0)
    jurisdiction: str = Field(default="international")
    applicable_laws: List[str] = Field(default_factory=list)
    
    # Status tracking
    report_status: str = Field(default="pending", description="Current status")
    assigned_to: Optional[UUID] = Field(None, description="Assigned reviewer ID")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    resolved_at: Optional[datetime] = None
    
    @validator('violation_type')
    def validate_violation_type(cls, v) -> None:
        """Validate violation type."""
        allowed_types = {
            "copyright_infringement", "unauthorized_distribution", "piracy",
            "trademark_violation", "counterfeiting", "plagiarism", "deepfake",
            "unauthorized_modification", "commercial_use", "attribution_missing"
        }
        if v not in allowed_types:
            raise ValueError(f'Violation type must be one of: {", ".join(allowed_types)}')
        return v


class TakedownRequest(UUIDSchema, TimestampSchema, AuditSchema):
    """DMCA/Legal takedown request schema."""
    
    violation_report_id: UUID = Field(description="Associated violation report")
    takedown_type: str = Field(description="Type of takedown request")
    legal_basis: str = Field(description="Legal basis for takedown")
    
    # Request details
    target_url: HttpUrl = Field(description="URL to be taken down")
    target_platform: str = Field(description="Platform receiving takedown request")
    request_content: str = Field(description="Takedown request content")
    
    # Legal information
    copyright_holder: str = Field(description="Copyright holder name")
    copyright_holder_contact: Dict[str, str] = Field(description="Copyright holder contact")
    legal_representative: Optional[str] = Field(None, description="Legal representative")
    
    # Supporting documentation
    supporting_documents: List[Dict[str, str]] = Field(default_factory=list)
    proof_of_ownership: List[HttpUrl] = Field(default_factory=list)
    evidence_links: List[HttpUrl] = Field(default_factory=list)
    
    # Takedown status
    request_status: str = Field(default="draft", description="Current request status")
    submitted_at: Optional[datetime] = None
    acknowledgment_received: Optional[datetime] = None
    compliance_deadline: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Response tracking
    platform_response: Optional[str] = Field(None, description="Platform response")
    counter_notice_received: bool = Field(default=False)
    counter_notice_content: Optional[str] = None
    
    # Outcome
    takedown_successful: Optional[bool] = None
    resolution_notes: Optional[str] = None
    follow_up_required: bool = Field(default=False)
    
    @validator('takedown_type')
    def validate_takedown_type(cls, v) -> None:
        """Validate takedown type."""
        allowed_types = {
            "dmca", "european_copyright_directive", "national_copyright",
            "trademark", "privacy", "defamation", "custom_legal"
        }
        if v not in allowed_types:
            raise ValueError(f'Takedown type must be one of: {", ".join(allowed_types)}')
        return v


class LegalAction(UUIDSchema, TimestampSchema, AuditSchema):
    """Legal action tracking schema."""
    
    violation_report_id: UUID
    action_type: str = Field(description="Type of legal action")
    legal_status: str = Field(description="Current legal status")
    jurisdiction: str = Field(description="Legal jurisdiction")
    
    # Legal details
    case_number: Optional[str] = Field(None, description="Court case number")
    law_firm: Optional[str] = Field(None, description="Representing law firm")
    attorney_contact: Optional[Dict[str, str]] = None
    filing_date: Optional[datetime] = None
    
    # Financial information
    estimated_damages: Optional[Decimal] = Field(None, ge=0)
    legal_costs: Optional[Decimal] = Field(None, ge=0)
    settlement_amount: Optional[Decimal] = Field(None, ge=0)
    
    # Case documents
    legal_documents: List[Dict[str, str]] = Field(default_factory=list)
    court_filings: List[Dict[str, str]] = Field(default_factory=list)
    evidence_package: List[HttpUrl] = Field(default_factory=list)
    
    # Timeline and status
    important_dates: List[Dict[str, datetime]] = Field(default_factory=list)
    status_updates: List[Dict[str, str]] = Field(default_factory=list)
    next_action_date: Optional[datetime] = None
    
    # Outcome
    case_resolved: bool = Field(default=False)
    resolution_type: Optional[str] = None
    outcome_description: Optional[str] = None
    damages_awarded: Optional[Decimal] = None


class SecurityScan(UUIDSchema, TimestampSchema):
    """Content security scan results schema."""
    
    content_id: UUID
    scan_type: str = Field(description="Type of security scan")
    scan_scope: str = Field(description="Scope of the scan")
    
    # Scan configuration
    scan_parameters: Dict[str, Any] = Field(default_factory=dict)
    detection_algorithms: List[str] = Field(default_factory=list)
    sensitivity_level: str = Field(default="medium")
    
    # Scan results
    threats_detected: int = Field(default=0, ge=0)
    vulnerabilities_found: List[Dict[str, Any]] = Field(default_factory=list)
    security_score: float = Field(ge=0.0, le=1.0, description="Overall security score")
    
    # Threat categories
    malware_detected: bool = Field(default=False)
    suspicious_patterns: List[str] = Field(default_factory=list)
    policy_violations: List[str] = Field(default_factory=list)
    content_integrity_issues: List[str] = Field(default_factory=list)
    
    # Recommendations
    security_recommendations: List[str] = Field(default_factory=list)
    remediation_steps: List[Dict[str, str]] = Field(default_factory=list)
    priority_actions: List[str] = Field(default_factory=list)
    
    # Performance
    scan_duration_seconds: float = Field(ge=0.0)
    files_scanned: int = Field(default=0, ge=0)
    data_processed_mb: float = Field(default=0.0, ge=0.0)


class ThreatAnalysis(UUIDSchema, TimestampSchema):
    """Advanced threat analysis schema."""
    
    content_id: UUID
    analysis_type: str = Field(description="Type of threat analysis")
    threat_intelligence_sources: List[str] = Field(default_factory=list)
    
    # Threat identification
    identified_threats: List[Dict[str, Any]] = Field(default_factory=list)
    threat_categories: List[str] = Field(default_factory=list)
    severity_levels: Dict[str, int] = Field(default_factory=dict)
    
    # Risk assessment
    overall_risk_score: float = Field(ge=0.0, le=1.0)
    risk_categories: Dict[str, float] = Field(default_factory=dict)
    impact_assessment: Dict[str, str] = Field(default_factory=dict)
    
    # Behavioral analysis
    suspicious_behaviors: List[str] = Field(default_factory=list)
    anomaly_detection_results: Dict[str, Any] = Field(default_factory=dict)
    pattern_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Mitigation recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    long_term_strategies: List[str] = Field(default_factory=list)
    prevention_measures: List[str] = Field(default_factory=list)
    
    # Intelligence sharing
    share_with_community: bool = Field(default=False)
    anonymized_indicators: List[str] = Field(default_factory=list)
    threat_attribution: Optional[str] = None
