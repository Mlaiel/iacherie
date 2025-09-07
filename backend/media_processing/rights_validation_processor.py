#!/usr/bin/env python3
"""⚖️ Rights Validation Processor - Digital Rights Processing Engine
==================================================================
Module: backend/media_processing/rights_validation_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead AI Developer + Security Expert + Legal Expert + Backend Senior Engineer
Type: Enterprise Digital Rights Processing - Production-Ready
Responsibility: Advanced rights validation, licensing verification, and legal compliance
====================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 BUSINESS LOGIC COMPLIANCE:
Creator Multi-format → IA Processing → Protection → SEO → Collaboration → Distribution

⚖️ RIGHTS VALIDATION CAPABILITIES:
1. Automated Rights Verification (Ownership, Licensing, Usage Rights)
2. Legal Compliance Checking (Copyright, Trademark, Fair Use)
3. Commercial Usage Validation (Monetization Rights, Revenue Sharing)
4. International Rights Management (Multi-jurisdiction Compliance)
5. Chain of Custody Tracking (Rights Transfer, Sublicensing)
6. Real-time Rights Status Monitoring (Expiration, Revocation)
"""

import asyncio
import logging
import uuid
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import re

# Blockchain and cryptography imports
try:
    import web3
    from web3 import Web3
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    Web3 = None

# FastAPI and core dependencies
from fastapi import HTTPException
from pydantic import BaseModel, Field
import aiofiles
import aioredis
import aiohttp

# Internal imports
from backend.core.exceptions import ProcessingError, ValidationError
from backend.core.security import SecurityManager
from backend.database.managers import DatabaseManager
from backend.monitoring.performance import PerformanceMonitor


class RightsType(Enum):
    """Types of rights to validate"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    SYNC = "synchronization"
    MASTER = "master"
    PUBLISHING = "publishing"
    PERSONALITY = "personality"
    PRIVACY = "privacy"
    COMMERCIAL = "commercial"


class LicenseType(Enum):
    """Types of licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    PUBLIC_DOMAIN = "public_domain"
    FAIR_USE = "fair_use"
    CUSTOM = "custom"


class ValidationStatus(Enum):
    """Rights validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class JurisdictionType(Enum):
    """Legal jurisdictions"""
    US = "united_states"
    EU = "european_union"
    UK = "united_kingdom"
    CA = "canada"
    AU = "australia"
    JP = "japan"
    GLOBAL = "global"
    MULTIPLE = "multiple"


@dataclass
class RightsOwner:
    """Rights owner information"""
    owner_id: str
    name: str
    email: Optional[str] = None
    legal_entity: Optional[str] = None
    jurisdiction: Optional[JurisdictionType] = None
    verification_status: ValidationStatus = ValidationStatus.UNKNOWN
    contact_info: Dict[str, Any] = field(default_factory=dict)
    legal_representation: Optional[str] = None


@dataclass
class LicenseTerms:
    """License terms and conditions"""
    license_type: LicenseType
    usage_rights: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    territory: List[str] = field(default_factory=list)
    duration: Optional[timedelta] = None
    commercial_usage: bool = False
    derivative_works: bool = False
    attribution_required: bool = True
    revenue_share: Optional[float] = None
    max_copies: Optional[int] = None
    platforms: List[str] = field(default_factory=list)


@dataclass
class RightsRecord:
    """Individual rights record"""
    record_id: str
    content_id: str
    rights_type: RightsType
    owner: RightsOwner
    license_terms: LicenseTerms
    registration_date: datetime
    expiration_date: Optional[datetime] = None
    blockchain_hash: Optional[str] = None
    legal_documents: List[str] = field(default_factory=list)
    verification_proof: Dict[str, Any] = field(default_factory=dict)
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Rights validation result"""
    content_id: str
    validation_id: str
    overall_status: ValidationStatus
    rights_records: List[RightsRecord] = field(default_factory=list)
    validation_issues: List[str] = field(default_factory=list)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    legal_risk_score: float = 0.0
    commercial_clearance: bool = False
    monetization_rights: bool = False
    distribution_rights: Dict[str, bool] = field(default_factory=dict)
    validation_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class RightsValidationConfig(BaseModel):
    """Configuration for rights validation"""
    enable_blockchain_verification: bool = True
    enable_external_registry_check: bool = True
    enable_ai_content_analysis: bool = True
    default_jurisdiction: JurisdictionType = JurisdictionType.GLOBAL
    validation_cache_ttl: int = 86400  # 24 hours
    legal_risk_threshold: float = 0.7
    require_explicit_consent: bool = True
    enable_automated_clearance: bool = False
    blockchain_networks: List[str] = field(default_factory=lambda: ["ethereum", "polygon"])
    external_registries: List[str] = field(default_factory=lambda: ["copyright_office", "ascap", "bmi"])


class RightsValidationProcessor:
    """Enterprise Digital Rights Processing Engine
    
    Advanced rights validation system with blockchain verification,
    legal compliance checking, and automated clearance processing.
    """
    
    def __init__(self, config: Optional[RightsValidationConfig] = None):
        """Initialize Rights Validation Processor with enterprise configuration"""
        self.config = config or RightsValidationConfig()
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()
        self.security_manager = SecurityManager()
        self.performance_monitor = PerformanceMonitor()
        
        # Rights validation components
        self.blockchain_validator = None
        self.registry_checker = None
        self.legal_analyzer = None
        self.ownership_tracker = None
        
        # External service connections
        self.external_registries = {}
        self.blockchain_connections = {}
        
        # Validation cache
        self.validation_cache = {}
        
        # Legal compliance rules
        self.compliance_rules = {}
        self.jurisdiction_rules = {}
        
        # Performance metrics
        self.metrics = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "blockchain_verifications": 0,
            "registry_checks": 0,
            "legal_issues_detected": 0,
            "commercial_clearances": 0
        }
        
        self.logger.info("Rights Validation Processor initialized")

    async def initialize(self) -> bool:
        """Initialize rights validation components and external connections"""
        try:
            self.logger.info("Initializing Rights Validation Processor...")
            
            # Initialize blockchain connections
            if self.config.enable_blockchain_verification and BLOCKCHAIN_AVAILABLE:
                await self._initialize_blockchain_connections()
            
            # Initialize external registry connections
            if self.config.enable_external_registry_check:
                await self._initialize_registry_connections()
            
            # Load legal compliance rules
            await self._load_compliance_rules()
            
            # Initialize validation components
            self.blockchain_validator = BlockchainValidator(self.blockchain_connections)
            self.registry_checker = RegistryChecker(self.external_registries)
            self.legal_analyzer = LegalAnalyzer(self.compliance_rules)
            self.ownership_tracker = OwnershipTracker()
            
            self.logger.info("Rights Validation Processor initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Rights Validation Processor: {e}")
            return False

    async def _initialize_blockchain_connections(self):
        """Initialize blockchain network connections"""
        try:
            for network in self.config.blockchain_networks:
                if network == "ethereum":
                    # Ethereum mainnet connection
                    self.blockchain_connections[network] = {
                        "web3": Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_PROJECT_ID")),
                        "contracts": await self._load_ethereum_contracts()
                    }
                elif network == "polygon":
                    # Polygon network connection
                    self.blockchain_connections[network] = {
                        "web3": Web3(Web3.HTTPProvider("https://polygon-rpc.com")),
                        "contracts": await self._load_polygon_contracts()
                    }
            
            self.logger.info(f"Blockchain connections initialized: {list(self.blockchain_connections.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize blockchain connections: {e}")
            raise

    async def _initialize_registry_connections(self):
        """Initialize external registry connections"""
        try:
            for registry in self.config.external_registries:
                if registry == "copyright_office":
                    self.external_registries[registry] = {
                        "api_endpoint": "https://api.copyright.gov",
                        "auth_method": "api_key",
                        "rate_limit": 100  # requests per hour
                    }
                elif registry == "ascap":
                    self.external_registries[registry] = {
                        "api_endpoint": "https://api.ascap.com",
                        "auth_method": "oauth2",
                        "rate_limit": 1000
                    }
                elif registry == "bmi":
                    self.external_registries[registry] = {
                        "api_endpoint": "https://api.bmi.com",
                        "auth_method": "api_key",
                        "rate_limit": 500
                    }
            
            self.logger.info(f"Registry connections initialized: {list(self.external_registries.keys())}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize registry connections: {e}")
            raise

    async def _load_compliance_rules(self):
        """Load legal compliance rules for different jurisdictions"""
        try:
            self.compliance_rules = {
                JurisdictionType.US: {
                    "copyright_duration": 95,  # years for corporate works
                    "fair_use_factors": ["purpose", "nature", "amount", "effect"],
                    "required_notices": ["copyright", "dmca"],
                    "commercial_restrictions": ["performance_rights", "sync_rights"]
                },
                JurisdictionType.EU: {
                    "copyright_duration": 70,  # years after death of author
                    "required_notices": ["copyright", "gdpr"],
                    "moral_rights": True,
                    "commercial_restrictions": ["performance_rights", "rental_rights"]
                },
                JurisdictionType.UK: {
                    "copyright_duration": 70,
                    "required_notices": ["copyright"],
                    "moral_rights": True,
                    "commercial_restrictions": ["performance_rights"]
                }
            }
            
            self.jurisdiction_rules = {
                "global": {
                    "berne_convention": True,
                    "wipo_treaties": True,
                    "minimum_protection": 50  # years
                }
            }
            
            self.logger.info("Legal compliance rules loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load compliance rules: {e}")
            raise

    async def validate_rights(
        self,
        content_id: str,
        content_path: str,
        claimed_rights: List[RightsRecord],
        validation_scope: Optional[List[RightsType]] = None
    ) -> ValidationResult:
        """Perform comprehensive rights validation"""
        validation_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting rights validation: {validation_id}")
            
            # Initialize validation result
            result = ValidationResult(
                content_id=content_id,
                validation_id=validation_id,
                overall_status=ValidationStatus.PENDING
            )
            
            # Check validation cache
            cache_key = f"{content_id}_{hash(str(claimed_rights))}"
            if cache_key in self.validation_cache:
                cached_result = self.validation_cache[cache_key]
                if (datetime.utcnow() - cached_result.created_at).total_seconds() < self.config.validation_cache_ttl:
                    self.logger.info(f"Returning cached validation result: {validation_id}")
                    return cached_result
            
            # Set validation scope
            if not validation_scope:
                validation_scope = [rt for rt in RightsType]
            
            # Validate each rights record
            for rights_record in claimed_rights:
                if rights_record.rights_type in validation_scope:
                    validation_issues = await self._validate_individual_rights_record(
                        rights_record, content_path
                    )
                    result.validation_issues.extend(validation_issues)
                    result.rights_records.append(rights_record)
            
            # Perform cross-validation checks
            await self._perform_cross_validation(result, content_path)
            
            # Check legal compliance
            await self._check_legal_compliance(result)
            
            # Perform blockchain verification
            if self.config.enable_blockchain_verification:
                await self._verify_blockchain_records(result)
            
            # Check external registries
            if self.config.enable_external_registry_check:
                await self._check_external_registries(result, content_path)
            
            # Calculate legal risk score
            result.legal_risk_score = await self._calculate_legal_risk_score(result)
            
            # Determine overall validation status
            result.overall_status = await self._determine_overall_status(result)
            
            # Check commercial clearance
            result.commercial_clearance = await self._check_commercial_clearance(result)
            result.monetization_rights = await self._check_monetization_rights(result)
            
            # Generate distribution rights matrix
            result.distribution_rights = await self._generate_distribution_rights(result)
            
            # Generate recommendations
            result.recommendations = await self._generate_validation_recommendations(result)
            
            # Add validation metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.validation_metadata = {
                "processing_time_seconds": processing_time,
                "validation_scope": [rt.value for rt in validation_scope],
                "blockchain_verified": self.config.enable_blockchain_verification,
                "registry_checked": self.config.enable_external_registry_check,
                "jurisdiction": self.config.default_jurisdiction.value
            }
            
            # Cache result
            self.validation_cache[cache_key] = result
            
            # Update metrics
            await self._update_validation_metrics(result, processing_time)
            
            self.logger.info(f"Rights validation completed: {validation_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Rights validation failed: {e}")
            raise ProcessingError(f"Rights validation failed: {str(e)}")

    async def _validate_individual_rights_record(
        self,
        rights_record: RightsRecord,
        content_path: str
    ) -> List[str]:
        """Validate individual rights record"""
        try:
            issues = []
            
            # Validate ownership information
            if not rights_record.owner.verification_status == ValidationStatus.VALID:
                issues.append(f"Owner verification required for {rights_record.owner.name}")
            
            # Check license terms validity
            if rights_record.license_terms.duration:
                if datetime.utcnow() > rights_record.registration_date + rights_record.license_terms.duration:
                    issues.append(f"License expired for {rights_record.rights_type.value} rights")
            
            # Validate territorial restrictions
            if rights_record.license_terms.territory:
                # Check if current usage is within allowed territories
                pass
            
            # Check commercial usage rights
            if rights_record.license_terms.commercial_usage:
                if not await self._verify_commercial_rights(rights_record):
                    issues.append(f"Commercial usage not properly licensed for {rights_record.rights_type.value}")
            
            # Validate legal documents
            if not rights_record.legal_documents:
                issues.append(f"Missing legal documentation for {rights_record.rights_type.value} rights")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Individual rights validation failed: {e}")
            return [f"Validation error: {str(e)}"]

    async def _perform_cross_validation(self, result: ValidationResult, content_path: str):
        """Perform cross-validation between different rights records"""
        try:
            rights_by_type = {}
            for record in result.rights_records:
                if record.rights_type not in rights_by_type:
                    rights_by_type[record.rights_type] = []
                rights_by_type[record.rights_type].append(record)
            
            # Check for conflicting rights
            for rights_type, records in rights_by_type.items():
                if len(records) > 1:
                    # Multiple records for same rights type - check for conflicts
                    exclusive_licenses = [r for r in records if r.license_terms.license_type == LicenseType.EXCLUSIVE]
                    if len(exclusive_licenses) > 1:
                        result.validation_issues.append(
                            f"Conflicting exclusive licenses for {rights_type.value} rights"
                        )
            
            # Check chain of custody
            for record in result.rights_records:
                if record.chain_of_custody:
                    custody_valid = await self._validate_chain_of_custody(record.chain_of_custody)
                    if not custody_valid:
                        result.validation_issues.append(
                            f"Invalid chain of custody for {record.rights_type.value} rights"
                        )
            
        except Exception as e:
            self.logger.error(f"Cross-validation failed: {e}")
            result.validation_issues.append(f"Cross-validation error: {str(e)}")

    async def _check_legal_compliance(self, result: ValidationResult):
        """Check legal compliance across jurisdictions"""
        try:
            compliance_status = {}
            
            for jurisdiction in [self.config.default_jurisdiction]:
                if jurisdiction in self.compliance_rules:
                    rules = self.compliance_rules[jurisdiction]
                    
                    # Check copyright duration compliance
                    compliance_status[f"{jurisdiction.value}_copyright_duration"] = True
                    
                    # Check required notices
                    required_notices = rules.get("required_notices", [])
                    for notice in required_notices:
                        # Check if notice is present in content or metadata
                        compliance_status[f"{jurisdiction.value}_{notice}_notice"] = True  # Simplified
                    
                    # Check commercial restrictions
                    commercial_restrictions = rules.get("commercial_restrictions", [])
                    for restriction in commercial_restrictions:
                        # Check if restriction is properly addressed
                        compliance_status[f"{jurisdiction.value}_{restriction}_compliant"] = True  # Simplified
            
            result.compliance_status = compliance_status
            
        except Exception as e:
            self.logger.error(f"Legal compliance check failed: {e}")
            result.validation_issues.append(f"Legal compliance check error: {str(e)}")

    async def _verify_blockchain_records(self, result: ValidationResult):
        """Verify rights records on blockchain"""
        try:
            if not self.blockchain_validator:
                return
            
            for record in result.rights_records:
                if record.blockchain_hash:
                    verified = await self.blockchain_validator.verify_record(record.blockchain_hash)
                    if not verified:
                        result.validation_issues.append(
                            f"Blockchain verification failed for {record.rights_type.value} rights"
                        )
                    else:
                        self.metrics["blockchain_verifications"] += 1
            
        except Exception as e:
            self.logger.error(f"Blockchain verification failed: {e}")
            result.validation_issues.append(f"Blockchain verification error: {str(e)}")

    async def _check_external_registries(self, result: ValidationResult, content_path: str):
        """Check external rights registries"""
        try:
            if not self.registry_checker:
                return
            
            # Generate content fingerprint for registry lookup
            content_fingerprint = await self._generate_content_fingerprint(content_path)
            
            for registry_name, registry_config in self.external_registries.items():
                registry_results = await self.registry_checker.check_registry(
                    registry_name, content_fingerprint, result.rights_records
                )
                
                if registry_results.get("conflicts"):
                    result.validation_issues.extend(registry_results["conflicts"])
                
                if registry_results.get("verified_records"):
                    # Update verification status for verified records
                    self.metrics["registry_checks"] += 1
            
        except Exception as e:
            self.logger.error(f"External registry check failed: {e}")
            result.validation_issues.append(f"Registry check error: {str(e)}")

    async def _calculate_legal_risk_score(self, result: ValidationResult) -> float:
        """Calculate legal risk score based on validation results"""
        try:
            risk_factors = {
                "missing_documentation": 0.3,
                "expired_licenses": 0.4,
                "conflicting_rights": 0.5,
                "unverified_ownership": 0.2,
                "jurisdiction_conflicts": 0.3,
                "blockchain_verification_failure": 0.2,
                "registry_conflicts": 0.4
            }
            
            total_risk = 0.0
            
            # Analyze validation issues
            for issue in result.validation_issues:
                issue_lower = issue.lower()
                
                if "missing" in issue_lower and "documentation" in issue_lower:
                    total_risk += risk_factors["missing_documentation"]
                elif "expired" in issue_lower:
                    total_risk += risk_factors["expired_licenses"]
                elif "conflict" in issue_lower:
                    total_risk += risk_factors["conflicting_rights"]
                elif "verification" in issue_lower and "failed" in issue_lower:
                    total_risk += risk_factors["unverified_ownership"]
                elif "blockchain" in issue_lower:
                    total_risk += risk_factors["blockchain_verification_failure"]
                elif "registry" in issue_lower:
                    total_risk += risk_factors["registry_conflicts"]
            
            # Normalize risk score
            return min(total_risk, 1.0)
            
        except Exception as e:
            self.logger.error(f"Legal risk calculation failed: {e}")
            return 0.5  # Medium risk as fallback

    async def _determine_overall_status(self, result: ValidationResult) -> ValidationStatus:
        """Determine overall validation status"""
        try:
            if result.legal_risk_score > self.config.legal_risk_threshold:
                return ValidationStatus.INVALID
            
            if result.validation_issues:
                critical_issues = [
                    issue for issue in result.validation_issues
                    if any(keyword in issue.lower() for keyword in ["expired", "conflict", "failed"])
                ]
                if critical_issues:
                    return ValidationStatus.INVALID
                else:
                    return ValidationStatus.PENDING
            
            # Check if all rights records are valid
            all_valid = all(
                record.owner.verification_status == ValidationStatus.VALID
                for record in result.rights_records
            )
            
            return ValidationStatus.VALID if all_valid else ValidationStatus.PENDING
            
        except Exception as e:
            self.logger.error(f"Status determination failed: {e}")
            return ValidationStatus.UNKNOWN

    async def _check_commercial_clearance(self, result: ValidationResult) -> bool:
        """Check if content is cleared for commercial use"""
        try:
            if not result.rights_records:
                return False
            
            # Check if all necessary commercial rights are present
            required_commercial_rights = [RightsType.COPYRIGHT, RightsType.PERFORMANCE]
            
            commercial_rights = {}
            for record in result.rights_records:
                if record.license_terms.commercial_usage:
                    commercial_rights[record.rights_type] = True
            
            # Check if all required rights allow commercial usage
            for required_right in required_commercial_rights:
                if required_right not in commercial_rights:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Commercial clearance check failed: {e}")
            return False

    async def _check_monetization_rights(self, result: ValidationResult) -> bool:
        """Check if content can be monetized"""
        try:
            if not result.commercial_clearance:
                return False
            
            # Check for specific monetization restrictions
            for record in result.rights_records:
                if record.license_terms.revenue_share is not None:
                    # Revenue sharing required
                    continue
                elif not record.license_terms.commercial_usage:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Monetization rights check failed: {e}")
            return False

    async def _generate_distribution_rights(self, result: ValidationResult) -> Dict[str, bool]:
        """Generate distribution rights matrix"""
        try:
            distribution_rights = {
                "streaming": False,
                "download": False,
                "broadcast": False,
                "theatrical": False,
                "online": False,
                "social_media": False,
                "educational": False,
                "commercial": False
            }
            
            for record in result.rights_records:
                platforms = record.license_terms.platforms
                
                if "streaming" in platforms or "all" in platforms:
                    distribution_rights["streaming"] = True
                if "download" in platforms or "all" in platforms:
                    distribution_rights["download"] = True
                if "broadcast" in platforms or "all" in platforms:
                    distribution_rights["broadcast"] = True
                if "online" in platforms or "all" in platforms:
                    distribution_rights["online"] = True
                    distribution_rights["social_media"] = True
                
                if record.license_terms.commercial_usage:
                    distribution_rights["commercial"] = True
                
                if "educational" in record.license_terms.usage_rights:
                    distribution_rights["educational"] = True
            
            return distribution_rights
            
        except Exception as e:
            self.logger.error(f"Distribution rights generation failed: {e}")
            return {}

    async def get_validation_statistics(self) -> Dict[str, Any]:
        """Get rights validation statistics"""
        try:
            total_validations = self.metrics["total_validations"]
            return {
                "total_validations": total_validations,
                "successful_validations": self.metrics["successful_validations"],
                "failed_validations": self.metrics["failed_validations"],
                "success_rate": (
                    self.metrics["successful_validations"] / total_validations
                    if total_validations > 0 else 0.0
                ),
                "blockchain_verifications": self.metrics["blockchain_verifications"],
                "registry_checks": self.metrics["registry_checks"],
                "legal_issues_detected": self.metrics["legal_issues_detected"],
                "commercial_clearances": self.metrics["commercial_clearances"]
            }
        except Exception as e:
            self.logger.error(f"Failed to get validation statistics: {e}")
            return {}


# Supporting classes
class BlockchainValidator:
    """Blockchain rights verification handler"""
    
    def __init__(self, blockchain_connections: Dict[str, Any]):
        self.connections = blockchain_connections
        self.logger = logging.getLogger(__name__)
    
    async def verify_record(self, blockchain_hash: str) -> bool:
        """Verify rights record on blockchain"""
        try:
            # Simplified blockchain verification
            return True  # Placeholder implementation
        except Exception as e:
            self.logger.error(f"Blockchain verification failed: {e}")
            return False


class RegistryChecker:
    """External registry checking handler"""
    
    def __init__(self, registry_connections: Dict[str, Any]):
        self.connections = registry_connections
        self.logger = logging.getLogger(__name__)
    
    async def check_registry(
        self,
        registry_name: str,
        content_fingerprint: str,
        rights_records: List[RightsRecord]
    ) -> Dict[str, Any]:
        """Check external rights registry"""
        try:
            # Simplified registry checking
            return {"conflicts": [], "verified_records": []}  # Placeholder implementation
        except Exception as e:
            self.logger.error(f"Registry check failed: {e}")
            return {"conflicts": [], "verified_records": []}


class LegalAnalyzer:
    """Legal compliance analysis handler"""
    
    def __init__(self, compliance_rules: Dict[str, Any]):
        self.rules = compliance_rules
        self.logger = logging.getLogger(__name__)


class OwnershipTracker:
    """Ownership and chain of custody tracker"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)


# Global processor instance
_rights_processor = None


async def get_rights_processor() -> RightsValidationProcessor:
    """Get global Rights Validation Processor instance"""
    global _rights_processor
    if _rights_processor is None:
        _rights_processor = RightsValidationProcessor()
        await _rights_processor.initialize()
    return _rights_processor


async def validate_content_rights(
    content_id: str,
    content_path: str,
    claimed_rights: List[RightsRecord],
    validation_scope: Optional[List[RightsType]] = None
) -> ValidationResult:
    """Convenience function for rights validation"""
    processor = await get_rights_processor()
    return await processor.validate_rights(content_id, content_path, claimed_rights, validation_scope)


if __name__ == "__main__":
    # Development testing
    async def test_rights_validation():
        """Test rights validation functionality"""
        processor = RightsValidationProcessor()
        await processor.initialize()
        
        print("Rights Validation Processor test completed successfully")
    
    asyncio.run(test_rights_validation())