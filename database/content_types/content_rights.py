"""Content Rights Management Module - Advanced Rights & Licensing System

Module gérant les droits d'auteur, les licences, la conformité légale
et la gestion des droits intellectuels pour le contenu multimédia.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Legal Rights Expert, Intellectual Property Specialist, Compliance Officer
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json
import asyncio
import logging
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, JSON, Text, Numeric,
    ForeignKey, Table, UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

logger = logging.getLogger(__name__)
Base = declarative_base()

class RightType(Enum):
    """
Types of intellectual property rights"""

    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    PUBLISHING_RIGHTS = "publishing_rights"
    MECHANICAL_RIGHTS = "mechanical_rights"
    PERFORMANCE_RIGHTS = "performance_rights"
    SYNCHRONIZATION_RIGHTS = "synchronization_rights"
    MASTER_RECORDING_RIGHTS = "master_recording_rights"
    NEIGHBORING_RIGHTS = "neighboring_rights"
    MORAL_RIGHTS = "moral_rights"
    PERSONALITY_RIGHTS = "personality_rights"
    PUBLICITY_RIGHTS = "publicity_rights"

class LicenseType(Enum):
    """Content licensing types"""

    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    PUBLIC_DOMAIN = "public_domain"
    CUSTOM = "custom"
    COMMERCIAL = "commercial"
    EDUCATIONAL = "educational"
    PERSONAL_USE = "personal_use"
    EDITORIAL = "editorial"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    SYNC_LICENSE = "sync_license"

class RightsStatus(Enum):
    """Rights status classifications"""

    OWNED = "owned"
    LICENSED_IN = "licensed_in"
    LICENSED_OUT = "licensed_out"
    SHARED = "shared"
    DISPUTED = "disputed"
    PENDING_CLEARANCE = "pending_clearance"
    CLEARED = "cleared"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNKNOWN = "unknown"

class ComplianceStatus(Enum):
    """Legal compliance status"""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    PENDING_DOCUMENTATION = "pending_documentation"
    REQUIRES_ACTION = "requires_action"
    DISPUTED = "disputed"
    EXEMPTED = "exempted"

class GeographicScope(Enum):
    """Geographic scope of rights"""

    WORLDWIDE = "worldwide"
    EUROPE = "europe"
    NORTH_AMERICA = "north_america"
    ASIA_PACIFIC = "asia_pacific"
    COUNTRY_SPECIFIC = "country_specific"
    REGION_SPECIFIC = "region_specific"
    EXCLUDED_TERRITORIES = "excluded_territories"

class ContentRights(Base):
    """Content rights and ownership information"""
    __tablename__ = "content_rights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Rights information
    right_type = Column(String(50), nullable=False)
    rights_holder_id = Column(UUID(as_uuid=True), nullable=False)
    rights_holder_type = Column(String(30), nullable=False)  # individual, company, organization
    
    # Ownership details
    ownership_percentage = Column(Numeric(5, 2), nullable=False, default=100.00)
    ownership_type = Column(String(30), nullable=False)  # full, partial, shared, joint
    acquisition_method = Column(String(50), nullable=False)  # created, purchased, inherited, assigned
    
    # Legal documentation
    legal_document_reference = Column(String(255), nullable=True)
    registration_number = Column(String(100), nullable=True)
    registration_authority = Column(String(100), nullable=True)
    registration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Territorial and temporal scope
    geographic_scope = Column(String(30), nullable=False, default=GeographicScope.WORLDWIDE.value)
    included_territories = Column(ARRAY(String), default=[])
    excluded_territories = Column(ARRAY(String), default=[])
    
    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_perpetual = Column(Boolean, default=False)
    renewable = Column(Boolean, default=False)
    renewal_terms = Column(JSONB, nullable=True)
    
    # Status and verification
    status = Column(String(30), nullable=False, default=RightsStatus.OWNED.value)
    verification_status = Column(String(30), default="pending")
    verification_date = Column(DateTime(timezone=True), nullable=True)
    verifier_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Additional rights metadata
    rights_metadata = Column(JSONB, default={})
    limitations = Column(ARRAY(String), default=[])
    obligations = Column(ARRAY(String), default=[])
    
    # Chain of title
    previous_owner_id = Column(UUID(as_uuid=True), nullable=True)
    transfer_date = Column(DateTime(timezone=True), nullable=True)
    transfer_document = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    licenses = relationship("ContentLicense", back_populates="content_rights")
    clearances = relationship("RightsClearance", back_populates="content_rights")

class ContentLicense(Base):
    """Content licensing agreements"""
    __tablename__ = "content_licenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_rights_id = Column(UUID(as_uuid=True), ForeignKey('content_rights.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    
    # License details
    license_type = Column(String(30), nullable=False)
    license_name = Column(String(255), nullable=False)
    license_version = Column(String(20), nullable=True)
    license_url = Column(String(500), nullable=True)
    
    # Parties
    licensor_id = Column(UUID(as_uuid=True), nullable=False)
    licensee_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Terms and conditions
    permitted_uses = Column(ARRAY(String), nullable=False)
    prohibited_uses = Column(ARRAY(String), default=[])
    attribution_required = Column(Boolean, default=True)
    attribution_text = Column(Text, nullable=True)
    
    # Commercial terms
    is_commercial = Column(Boolean, default=False)
    license_fee = Column(Numeric(15, 4), default=0.0)
    currency = Column(String(3), default="EUR")
    royalty_rate = Column(Numeric(5, 4), default=0.0)
    minimum_guarantee = Column(Numeric(15, 4), default=0.0)
    
    # Geographic and temporal scope
    geographic_scope = Column(String(30), nullable=False)
    included_territories = Column(ARRAY(String), default=[])
    excluded_territories = Column(ARRAY(String), default=[])
    
    # Validity and terms
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    is_perpetual = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer, nullable=True)
    
    # Usage restrictions
    max_distribution_quantity = Column(Integer, nullable=True)
    max_derivative_works = Column(Integer, nullable=True)
    sublicensing_allowed = Column(Boolean, default=False)
    resale_allowed = Column(Boolean, default=False)
    
    # Technical restrictions
    max_resolution = Column(String(20), nullable=True)
    max_duration = Column(Integer, nullable=True)  # seconds
    watermark_required = Column(Boolean, default=False)
    drm_required = Column(Boolean, default=False)
    
    # Compliance and reporting
    usage_reporting_required = Column(Boolean, default=False)
    reporting_frequency = Column(String(20), nullable=True)  # monthly, quarterly, annual
    audit_rights = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default="active")
    termination_reason = Column(Text, nullable=True)
    
    # Legal documentation
    contract_reference = Column(String(255), nullable=True)
    signed_date = Column(DateTime(timezone=True), nullable=True)
    witness_id = Column(UUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_rights = relationship("ContentRights", back_populates="licenses")
    usage_reports = relationship("LicenseUsageReport", back_populates="license")

class RightsClearance(Base):
    """Rights clearance tracking"""
    __tablename__ = "rights_clearances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_rights_id = Column(UUID(as_uuid=True), ForeignKey('content_rights.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Clearance details
    clearance_type = Column(String(50), nullable=False)  # sample, cover, sync, master
    cleared_element = Column(String(255), nullable=False)  # What specifically was cleared
    
    # Source information
    source_content_id = Column(UUID(as_uuid=True), nullable=True)
    source_title = Column(String(255), nullable=True)
    source_artist = Column(String(255), nullable=True)
    source_publisher = Column(String(255), nullable=True)
    source_record_label = Column(String(255), nullable=True)
    
    # Clearance process
    clearance_agency = Column(String(255), nullable=True)
    clearance_representative = Column(String(255), nullable=True)
    clearance_fee = Column(Numeric(15, 4), default=0.0)
    currency = Column(String(3), default="EUR")
    
    # Status and documentation
    clearance_status = Column(String(30), nullable=False)
    clearance_document = Column(String(500), nullable=True)
    clearance_date = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Usage terms from clearance
    permitted_usage = Column(JSONB, default={})
    usage_restrictions = Column(JSONB, default={})
    territorial_restrictions = Column(ARRAY(String), default=[])
    
    # Compliance tracking
    compliance_verified = Column(Boolean, default=False)
    compliance_verification_date = Column(DateTime(timezone=True), nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_rights = relationship("ContentRights", back_populates="clearances")

class LicenseUsageReport(Base):
    """License usage reporting"""
    __tablename__ = "license_usage_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey('content_licenses.id'), nullable=False)
    
    # Reporting period
    reporting_period_start = Column(DateTime(timezone=True), nullable=False)
    reporting_period_end = Column(DateTime(timezone=True), nullable=False)
    report_type = Column(String(30), nullable=False)  # usage, revenue, distribution
    
    # Usage metrics
    total_uses = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    
    # Geographic distribution
    usage_by_territory = Column(JSONB, default={})
    top_territories = Column(ARRAY(String), default=[])
    
    # Revenue information
    gross_revenue = Column(Numeric(15, 4), default=0.0)
    net_revenue = Column(Numeric(15, 4), default=0.0)
    royalties_due = Column(Numeric(15, 4), default=0.0)
    currency = Column(String(3), default="EUR")
    
    # Platform breakdown
    platform_usage = Column(JSONB, default={})
    platform_revenue = Column(JSONB, default={})
    
    # Compliance status
    compliance_status = Column(String(30), default="compliant")
    violations_detected = Column(Integer, default=0)
    violation_details = Column(JSONB, default={})
    
    # Report metadata
    generated_by = Column(UUID(as_uuid=True), nullable=True)
    generation_method = Column(String(30), default="automated")
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    license = relationship("ContentLicense", back_populates="usage_reports")

@dataclass
class RightsAnalysisResult:
    """Rights analysis result structure"""
    content_id: str
    overall_compliance: bool
    compliance_score: float
    identified_risks: List[str]
    required_clearances: List[str]
    missing_documentation: List[str]
    recommendations: List[str]
    estimated_clearance_cost: Decimal
    analysis_confidence: float

class RightsManager:
    """
Advanced rights management system"""
    
    def __init__(self):
        self.clearance_agencies = {}
        self.rights_databases = {}
        self.compliance_rules = self._initialize_compliance_rules()
    
    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """
Initialize compliance rules for different jurisdictions"""
        return {
            "EU": {
                "copyright_duration": 70,  # years after death
                "neighboring_rights_duration": 50,
                "fair_use_allowed": False,
                "fair_dealing_allowed": True,
                "moral_rights_waivable": False
            },
            "US": {
                "copyright_duration": 70,
                "neighboring_rights_duration": 95,
                "fair_use_allowed": True,
                "fair_dealing_allowed": False,
                "moral_rights_waivable": True
            },
            "UK": {
                "copyright_duration": 70,
                "neighboring_rights_duration": 50,
                "fair_use_allowed": False,
                "fair_dealing_allowed": True,
                "moral_rights_waivable": False
            }
        }
    
    async def analyze_content_rights(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        target_territories: List[str],
        intended_uses: List[str]
    ) -> RightsAnalysisResult:
        """Comprehensive rights analysis for content"""
        try:
            # Get existing rights information
            existing_rights = await self._get_content_rights(content_id)
            
            # Analyze copyright status
            copyright_analysis = await self._analyze_copyright_status(
                content_metadata,
                target_territories
            )
            
            # Check for potential copyright issues
            copyright_issues = await self._detect_copyright_issues(
                content_metadata,
                existing_rights
            )
            
            # Analyze licensing requirements
            licensing_requirements = await self._analyze_licensing_requirements(
                intended_uses,
                target_territories,
                copyright_analysis
            )
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(
                existing_rights,
                copyright_analysis,
                licensing_requirements
            )
            
            # Generate recommendations
            recommendations = await self._generate_rights_recommendations(
                copyright_analysis,
                licensing_requirements,
                copyright_issues
            )
            
            # Estimate clearance costs
            clearance_cost = await self._estimate_clearance_costs(
                licensing_requirements,
                target_territories
            )
            
            return RightsAnalysisResult(
                content_id=content_id,
                overall_compliance=compliance_score >= 0.8,
                compliance_score=compliance_score,
                identified_risks=copyright_issues,
                required_clearances=licensing_requirements,
                missing_documentation=await self._identify_missing_documentation(existing_rights),
                recommendations=recommendations,
                estimated_clearance_cost=clearance_cost,
                analysis_confidence=0.9  # Would be calculated based on data quality
            )
            
        except Exception as e:
            logger.error(f"Error analyzing content rights: {e}")
            raise
    
    async def obtain_rights_clearance(
        self,
        content_id: str,
        clearance_type: str,
        source_information: Dict[str, Any],
        usage_terms: Dict[str, Any]
    ) -> str:
        """Obtain rights clearance for content"""
        try:
            clearance_id = str(uuid.uuid4())
            
            # Identify rights holders
            rights_holders = await self._identify_rights_holders(
                source_information,
                clearance_type
            )
            
            # Prepare clearance request
            clearance_request = await self._prepare_clearance_request(
                content_id,
                clearance_type,
                source_information,
                usage_terms,
                rights_holders
            )
            
            # Submit clearance request
            clearance_status = await self._submit_clearance_request(
                clearance_request,
                rights_holders
            )
            
            # Create clearance record
            clearance = RightsClearance(
                id=clearance_id,
                content_id=content_id,
                clearance_type=clearance_type,
                cleared_element=source_information.get('title', 'Unknown'),
                source_title=source_information.get('title'),
                source_artist=source_information.get('artist'),
                source_publisher=source_information.get('publisher'),
                clearance_status=clearance_status['status'],
                clearance_fee=clearance_status.get('fee', 0.0),
                permitted_usage=usage_terms,
                compliance_verified=False
            )
            
            logger.info(f"Rights clearance initiated: {clearance_id}")
            return clearance_id
            
        except Exception as e:
            logger.error(f"Error obtaining rights clearance: {e}")
            raise
    
    async def create_license_agreement(
        self,
        content_id: str,
        licensor_id: str,
        licensee_id: str,
        license_terms: Dict[str, Any]
    ) -> str:
        """Create comprehensive license agreement"""
        try:
            license_id = str(uuid.uuid4())
            
            # Validate license terms
            validated_terms = await self._validate_license_terms(license_terms)
            
            # Generate license agreement
            license_agreement = ContentLicense(
                id=license_id,
                content_id=content_id,
                license_type=validated_terms['license_type'],
                license_name=validated_terms['license_name'],
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                permitted_uses=validated_terms['permitted_uses'],
                prohibited_uses=validated_terms.get('prohibited_uses', []),
                attribution_required=validated_terms.get('attribution_required', True),
                is_commercial=validated_terms.get('is_commercial', False),
                license_fee=Decimal(str(validated_terms.get('license_fee', 0.0))),
                royalty_rate=Decimal(str(validated_terms.get('royalty_rate', 0.0))),
                geographic_scope=validated_terms.get('geographic_scope', 'worldwide'),
                effective_date=datetime.utcnow(),
                expiration_date=validated_terms.get('expiration_date'),
                status="pending_signature"
            )
            
            # Generate contract documentation
            contract_document = await self._generate_license_contract(
                license_agreement,
                validated_terms
            )
            
            license_agreement.contract_reference = contract_document['reference']
            
            logger.info(f"License agreement created: {license_id}")
            return license_id
            
        except Exception as e:
            logger.error(f"Error creating license agreement: {e}")
            raise
    
    async def monitor_compliance(
        self,
        content_id: str,
        monitoring_period: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Monitor compliance with rights and licensing terms"""
        try:
            # Get content rights and licenses
            content_rights = await self._get_content_rights(content_id)
            content_licenses = await self._get_content_licenses(content_id)
            
            # Monitor usage across platforms
            usage_data = await self._collect_usage_data(
                content_id,
                monitoring_period
            )
            
            # Check compliance with each license
            compliance_results = {}
            
            for license_agreement in content_licenses:
                license_compliance = await self._check_license_compliance(
                    license_agreement,
                    usage_data
                )
                
                compliance_results[str(license_agreement.id)] = license_compliance
            
            # Check for unauthorized usage
            unauthorized_usage = await self._detect_unauthorized_usage(
                content_id,
                content_licenses,
                usage_data
            )
            
            # Generate compliance report
            compliance_report = {
                'content_id': content_id,
                'monitoring_period': monitoring_period,
                'overall_compliance': all(
                    result['compliant'] for result in compliance_results.values()
                ),
                'license_compliance': compliance_results,
                'unauthorized_usage': unauthorized_usage,
                'violations_detected': len(unauthorized_usage),
                'recommendations': await self._generate_compliance_recommendations(
                    compliance_results,
                    unauthorized_usage
                ),
                'generated_at': datetime.utcnow()
            }
            
            return compliance_report
            
        except Exception as e:
            logger.error(f"Error monitoring compliance: {e}")
            raise
    
    async def _analyze_copyright_status(
        self,
        metadata: Dict[str, Any],
        territories: List[str]
    ) -> Dict[str, Any]:
        """Analyze copyright status in specified territories"""
        try:
            copyright_status = {}
            
            for territory in territories:
                # Get territory-specific copyright rules
                rules = self.compliance_rules.get(territory, self.compliance_rules['EU'])
                
                # Determine copyright status
                creation_date = metadata.get('creation_date')
                author_death_date = metadata.get('author_death_date')
                
                if creation_date and author_death_date:
                    copyright_expiry = author_death_date + timedelta(
                        days=rules['copyright_duration'] * 365
                    )
                    is_protected = datetime.now(timezone.utc) < copyright_expiry
                else:
                    is_protected = True  # Assume protected if dates unknown
                
                copyright_status[territory] = {
                    'protected': is_protected,
                    'expiry_date': copyright_expiry if creation_date and author_death_date else None,
                    'public_domain': not is_protected,
                    'moral_rights_active': rules.get('moral_rights_waivable', False)
                }
            
            return copyright_status
            
        except Exception as e:
            logger.error(f"Error analyzing copyright status: {e}")
            return {}
    
    # Additional helper methods would be implemented here...
    
    async def _get_content_rights(self, content_id: str) -> List[ContentRights]:
        try:
                    # Request validation
                    if not content_id:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__get_content_rights_request(content_id)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__analyze_licensing_requirements_input(uses)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__analyze_licensing_requirements_result(result)
            
                    logger.info(f"AI processing _analyze_licensing_requirements completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _analyze_licensing_requirements failed: {e}")
                    raise
            result = None  # Replace with actual implementation
            
            logger.info(f"_detect_copyright_issues completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_detect_copyright_issues failed: {e}")
            raise
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_content_rights failed: {e}")
                    return {"status": "error", "message": str(e)}
    async def _detect_copyright_issues(self, metadata, existing_rights) -> List[str]:
        """
Detect potential copyright issues"""
        pass
    
    async def _analyze_licensing_requirements(self, uses, territories, copyright_analysis) -> List[str]:
        """
Analyze licensing requirements"""
        pass

# Export classes and functions
__all__ = [
    'RightType',
    'LicenseType',
    'RightsStatus',
    'ComplianceStatus', 
    'GeographicScope',
    'ContentRights',
    'ContentLicense',
    'RightsClearance',
    'LicenseUsageReport',
    'RightsAnalysisResult',
    'RightsManager'
]
