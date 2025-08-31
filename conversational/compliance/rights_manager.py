"""
Rights Manager - Intellectual Property Rights Management System

This module provides comprehensive rights management for conversational AI content,
including intellectual property protection, copyright compliance, and usage rights verification.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..core.database import DatabaseManager
from ..security.encryption import EncryptionService
from ..ml.similarity_detector import SimilarityDetector
from ..content_protection.fingerprinting import ContentFingerprinter


class RightsViolationType(Enum):
    """Types of rights violations"""
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    PATENT_INFRINGEMENT = "patent_infringement"
    TRADE_SECRET_EXPOSURE = "trade_secret_exposure"
    FAIR_USE_VIOLATION = "fair_use_violation"
    ATTRIBUTION_MISSING = "attribution_missing"
    LICENSING_VIOLATION = "licensing_violation"
    UNAUTHORIZED_REPRODUCTION = "unauthorized_reproduction"


class RightsStatus(Enum):
    """Rights compliance status"""
    COMPLIANT = "compliant"
    VIOLATION_DETECTED = "violation_detected"
    REVIEW_REQUIRED = "review_required"
    FAIR_USE_CLAIMED = "fair_use_claimed"
    LICENSED = "licensed"
    UNKNOWN = "unknown"


class ContentType(Enum):
    """Types of content for rights management"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    CODE = "code"
    MIXED = "mixed"


@dataclass
class RightsViolation:
    """Rights violation structure"""
    violation_type: RightsViolationType
    description: str
    evidence: List[str]
    confidence_score: float
    potential_owner: Optional[str]
    original_work_references: List[str]
    severity: str
    legal_implications: List[str]
    mitigation_actions: List[str]
    fair_use_assessment: Dict[str, Any]


@dataclass
class RightsAssessment:
    """Rights assessment result structure"""
    content_id: str
    content_type: ContentType
    rights_status: RightsStatus
    violations: List[RightsViolation]
    licenses_required: List[str]
    attributions_required: List[str]
    fair_use_factors: Dict[str, Any]
    recommended_actions: List[str]
    legal_warnings: List[str]
    confidence_score: float
    processing_time_ms: int


@dataclass
class ContentLicense:
    """Content license information"""
    license_id: str
    content_reference: str
    license_type: str
    licensor: str
    licensee: str
    permissions: List[str]
    restrictions: List[str]
    attribution_requirements: List[str]
    expiry_date: Optional[datetime]
    territory: List[str]
    usage_limits: Dict[str, Any]


class RightsManager:
    """
    Advanced intellectual property rights management system.
    
    Provides comprehensive rights assessment, violation detection, and compliance
    management for conversational AI content across multiple content types.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        encryption_service: EncryptionService,
        similarity_detector: Optional[SimilarityDetector] = None,
        content_fingerprinter: Optional[ContentFingerprinter] = None
    ):
        self.db_manager = db_manager
        self.encryption_service = encryption_service
        self.similarity_detector = similarity_detector or SimilarityDetector()
        self.content_fingerprinter = content_fingerprinter or ContentFingerprinter()
        self.logger = logging.getLogger(__name__)
        
        # Rights detection patterns
        self.copyright_patterns = self._load_copyright_patterns()
        self.trademark_patterns = self._load_trademark_patterns()
        self.fair_use_factors = self._load_fair_use_factors()
        
        # Rights databases
        self.known_copyrighted_works = {}
        self.registered_trademarks = {}
        self.active_licenses = {}
        
        # Load rights databases
        self._initialize_rights_databases()
        
        self.logger.info("RightsManager initialized with rights protection systems")
    
    def _load_copyright_patterns(self) -> List[Dict[str, Any]]:
        """Load copyright detection patterns"""



        return [
            {
                "pattern": r"©\s*\d{4}",
                "description": "Copyright notice with year",
                "confidence": 0.9
            },
            {
                "pattern": r"copyright\s+\d{4}",
                "description": "Copyright text with year",
                "confidence": 0.8
            },
            {
                "pattern": r"all rights reserved",
                "description": "All rights reserved notice",
                "confidence": 0.7
            },
            {
                "pattern": r"proprietary and confidential",
                "description": "Proprietary content notice",
                "confidence": 0.8
            },
            {
                "pattern": r"trademark|™|®",
                "description": "Trademark indicators",
                "confidence": 0.7
            }
        ]
    
    def _load_trademark_patterns(self) -> List[Dict[str, Any]]:
        """Load trademark detection patterns"""



        return [
            {
                "pattern": r"\b(Apple|Microsoft|Google|Amazon|Facebook|Meta|Tesla|Nike|Coca-Cola)\b",
                "description": "Major brand names",
                "confidence": 0.9
            },
            {
                "pattern": r"\b\w+\s*™|\b\w+\s*®",
                "description": "Trademarked terms",
                "confidence": 0.8
            }
        ]
    
    def _load_fair_use_factors(self) -> Dict[str, Any]:
        """Load fair use assessment factors"""



        return {
            "purpose_and_character": {
                "educational": 0.8,
                "commentary": 0.7,
                "criticism": 0.7,
                "parody": 0.6,
                "news_reporting": 0.8,
                "commercial": 0.2,
                "transformative": 0.8
            },
            "nature_of_work": {
                "factual": 0.7,
                "creative": 0.3,
                "published": 0.6,
                "unpublished": 0.2
            },
            "amount_used": {
                "minimal": 0.8,
                "moderate": 0.5,
                "substantial": 0.2,
                "whole_work": 0.1
            },
            "market_effect": {
                "no_harm": 0.8,
                "minimal_harm": 0.6,
                "moderate_harm": 0.3,
                "significant_harm": 0.1
            }
        }
    
    async def _initialize_rights_databases(self) -> None:
        """Initialize rights databases from various sources"""



        try:
            # Load known copyrighted works from database
            copyrighted_works = await self.db_manager.fetch_all(
                "SELECT * FROM copyrighted_works WHERE active = true"
            )
            
            for work in copyrighted_works:
                self.known_copyrighted_works[work["content_hash"]] = work
            
            # Load registered trademarks
            trademarks = await self.db_manager.fetch_all(
                "SELECT * FROM registered_trademarks WHERE active = true"
            )
            
            for trademark in trademarks:
                self.registered_trademarks[trademark["mark"].lower()] = trademark
            
            # Load active licenses
            licenses = await self.db_manager.fetch_all(
                "SELECT * FROM content_licenses WHERE expiry_date > $1 OR expiry_date IS NULL",
                datetime.now()
            )
            
            for license_data in licenses:
                license_obj = ContentLicense(
                    license_id=license_data["license_id"],
                    content_reference=license_data["content_reference"],
                    license_type=license_data["license_type"],
                    licensor=license_data["licensor"],
                    licensee=license_data["licensee"],
                    permissions=license_data["permissions"],
                    restrictions=license_data["restrictions"],
                    attribution_requirements=license_data["attribution_requirements"],
                    expiry_date=license_data["expiry_date"],
                    territory=license_data["territory"],
                    usage_limits=license_data["usage_limits"]
                )
                self.active_licenses[license_data["content_reference"]] = license_obj
            
            self.logger.info(
                f"Rights databases initialized: {len(self.known_copyrighted_works)} copyrighted works, "
                f"{len(self.registered_trademarks)} trademarks, {len(self.active_licenses)} licenses"
            )
            
        except Exception as e:
            self.logger.error(f"Error initializing rights databases: {str(e)}")
    
    async def validate_rights_compliance(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate rights compliance for conversational content.
        
        Args:
            user_input: User's input text
            ai_response: AI's generated response
            context: Additional context information
            
        Returns:
            Dict containing rights compliance assessment
        """
        start_time = datetime.now()
        
        try:
            self.logger.debug("Starting rights compliance validation")
            
            # Generate content fingerprint
            content_hash = self._generate_content_hash(user_input + ai_response)
            
            # Assess content for rights violations
            assessment = await self._assess_content_rights(
                content_hash, user_input, ai_response, context
            )
            
            # Check for copyright violations
            copyright_violations = await self._detect_copyright_violations(
                user_input, ai_response, context
            )
            assessment.violations.extend(copyright_violations)
            
            # Check for trademark violations
            trademark_violations = await self._detect_trademark_violations(
                user_input, ai_response, context
            )
            assessment.violations.extend(trademark_violations)
            
            # Assess fair use factors
            fair_use_assessment = await self._assess_fair_use(
                user_input, ai_response, context
            )
            assessment.fair_use_factors = fair_use_assessment
            
            # Check existing licenses
            license_coverage = await self._check_license_coverage(
                content_hash, user_input, ai_response
            )
            
            # Update assessment based on license coverage
            if license_coverage["has_valid_license"]:
                assessment.rights_status = RightsStatus.LICENSED
                assessment.attributions_required = license_coverage["attribution_requirements"]
            elif assessment.violations:
                if fair_use_assessment.get("likely_fair_use", False):
                    assessment.rights_status = RightsStatus.FAIR_USE_CLAIMED
                else:
                    assessment.rights_status = RightsStatus.VIOLATION_DETECTED
            else:
                assessment.rights_status = RightsStatus.COMPLIANT
            
            # Generate recommendations
            assessment.recommended_actions = self._generate_rights_recommendations(assessment)
            assessment.legal_warnings = self._generate_legal_warnings(assessment)
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            assessment.processing_time_ms = int(processing_time.total_seconds() * 1000)
            
            # Store assessment results
            await self._store_rights_assessment(assessment)
            
            return {
                "status": assessment.rights_status.value,
                "violations": [
                    {
                        "type": v.violation_type.value,
                        "description": v.description,
                        "confidence": v.confidence_score,
                        "severity": v.severity
                    }
                    for v in assessment.violations
                ],
                "recommendations": assessment.recommended_actions,
                "warnings": assessment.legal_warnings,
                "fair_use_assessment": assessment.fair_use_factors,
                "licenses_required": assessment.licenses_required,
                "attributions_required": assessment.attributions_required
            }
            
        except Exception as e:
            self.logger.error(f"Error in rights compliance validation: {str(e)}")
            return {
                "status": "error",
                "violations": [{"type": "validation_error", "description": str(e)}],
                "recommendations": ["Manual rights review required"],
                "warnings": [f"Rights validation error: {str(e)}"]
            }
    
    async def _assess_content_rights(
        self,
        content_hash: str,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]]
    ) -> RightsAssessment:
        """Assess content for rights compliance"""
        content_type = self._determine_content_type(user_input + ai_response)
        
        assessment = RightsAssessment(
            content_id=content_hash,
            content_type=content_type,
            rights_status=RightsStatus.UNKNOWN,
            violations=[],
            licenses_required=[],
            attributions_required=[],
            fair_use_factors={},
            recommended_actions=[],
            legal_warnings=[],
            confidence_score=1.0,
            processing_time_ms=0
        )
        
        return assessment
    
    async def _detect_copyright_violations(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]]
    ) -> List[RightsViolation]:
        """Detect potential copyright violations"""
        violations = []
        combined_content = user_input + " " + ai_response
        
        # Pattern-based detection
        for pattern_config in self.copyright_patterns:
            pattern = pattern_config["pattern"]
            matches = re.findall(pattern, combined_content, re.IGNORECASE)
            
            if matches:
                violations.append(RightsViolation(
                    violation_type=RightsViolationType.COPYRIGHT_INFRINGEMENT,
                    description=f"Copyright indicators detected: {pattern_config['description']}",
                    evidence=matches,
                    confidence_score=pattern_config["confidence"],
                    potential_owner=None,
                    original_work_references=[],
                    severity="medium",
                    legal_implications=["Potential copyright infringement claim"],
                    mitigation_actions=["Verify copyright status", "Obtain permission", "Remove content"],
                    fair_use_assessment={}
                ))
        
        # Similarity-based detection against known works
        similarity_violations = await self._check_content_similarity(combined_content)
        violations.extend(similarity_violations)
        
        return violations
    
    async def _detect_trademark_violations(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]]
    ) -> List[RightsViolation]:
        """Detect potential trademark violations"""
        violations = []
        combined_content = user_input + " " + ai_response
        
        # Check against registered trademarks
        for trademark, trademark_data in self.registered_trademarks.items():
            if trademark in combined_content.lower():
                # Assess context of usage
                context_assessment = self._assess_trademark_context(combined_content, trademark)
                
                if context_assessment["likely_violation"]:
                    violations.append(RightsViolation(
                        violation_type=RightsViolationType.TRADEMARK_VIOLATION,
                        description=f"Potential trademark violation: {trademark}",
                        evidence=[trademark],
                        confidence_score=context_assessment["confidence"],
                        potential_owner=trademark_data.get("owner"),
                        original_work_references=[],
                        severity=context_assessment["severity"],
                        legal_implications=["Trademark infringement claim", "Unfair competition"],
                        mitigation_actions=["Remove trademark usage", "Add disclaimers", "Verify fair use"],
                        fair_use_assessment={}
                    ))
        
        return violations
    
    async def _check_content_similarity(self, content: str) -> List[RightsViolation]:
        """Check content similarity against known copyrighted works"""
        violations = []
        
        try:
            # Generate content fingerprint
            content_fingerprint = await self.content_fingerprinter.generate_fingerprint(
                content, ContentType.TEXT
            )
            
            # Check similarity against known works
            for known_hash, work_data in self.known_copyrighted_works.items():
                similarity_score = await self.similarity_detector.calculate_similarity(
                    content_fingerprint, work_data["fingerprint"]
                )
                
                if similarity_score > 0.8:  # High similarity threshold
                    violations.append(RightsViolation(
                        violation_type=RightsViolationType.UNAUTHORIZED_REPRODUCTION,
                        description=f"High similarity to copyrighted work: {work_data.get('title', 'Unknown')}",
                        evidence=[f"Similarity score: {similarity_score:.2f}"],
                        confidence_score=similarity_score,
                        potential_owner=work_data.get("owner"),
                        original_work_references=[work_data.get("reference", "")],
                        severity="high" if similarity_score > 0.9 else "medium",
                        legal_implications=["Copyright infringement", "Unauthorized reproduction"],
                        mitigation_actions=["Obtain license", "Use original content", "Cite source"],
                        fair_use_assessment={}
                    ))
            
        except Exception as e:
            self.logger.error(f"Error in content similarity check: {str(e)}")
        
        return violations
    
    def _assess_trademark_context(self, content: str, trademark: str) -> Dict[str, Any]:
        """Assess context of trademark usage"""
        content_lower = content.lower()
        
        # Check for commercial usage indicators
        commercial_indicators = [
            "buy", "sell", "purchase", "order", "shop", "store", "product", "service",
            "brand", "official", "authorized", "genuine", "original"
        ]
        
        commercial_usage = any(indicator in content_lower for indicator in commercial_indicators)
        
        # Check for criticism/commentary indicators
        commentary_indicators = [
            "review", "opinion", "think", "believe", "compare", "analysis", "critique"
        ]
        
        commentary_usage = any(indicator in content_lower for indicator in commentary_indicators)
        
        # Assess likelihood of violation
        if commercial_usage and not commentary_usage:
            likelihood = 0.8
            severity = "high"
        elif commercial_usage and commentary_usage:
            likelihood = 0.5
            severity = "medium"
        elif commentary_usage:
            likelihood = 0.2
            severity = "low"
        else:
            likelihood = 0.3
            severity = "medium"
        
        return {
            "likely_violation": likelihood > 0.6,
            "confidence": likelihood,
            "severity": severity,
            "commercial_usage": commercial_usage,
            "commentary_usage": commentary_usage
        }
    
    async def _assess_fair_use(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess fair use factors for content usage"""
        combined_content = user_input + " " + ai_response
        
        # Purpose and character assessment
        purpose_score = self._assess_purpose_character(combined_content, context)
        
        # Nature of work assessment
        nature_score = self._assess_nature_of_work(combined_content)
        
        # Amount used assessment
        amount_score = self._assess_amount_used(combined_content, context)
        
        # Market effect assessment
        market_score = self._assess_market_effect(combined_content, context)
        
        # Calculate overall fair use likelihood
        overall_score = (purpose_score + nature_score + amount_score + market_score) / 4
        
        return {
            "purpose_and_character": purpose_score,
            "nature_of_work": nature_score,
            "amount_used": amount_score,
            "market_effect": market_score,
            "overall_score": overall_score,
            "likely_fair_use": overall_score > 0.6,
            "assessment_confidence": 0.7  # Moderate confidence in automated assessment
        }
    
    def _assess_purpose_character(self, content: str, context: Optional[Dict[str, Any]]) -> float:
        """Assess purpose and character factor for fair use"""
        content_lower = content.lower()
        
        educational_indicators = ["learn", "teach", "study", "education", "academic", "research"]
        commentary_indicators = ["review", "analysis", "critique", "opinion", "comment"]
        criticism_indicators = ["criticize", "critique", "analyze", "evaluate"]
        news_indicators = ["news", "report", "current", "event", "breaking"]
        commercial_indicators = ["buy", "sell", "profit", "business", "commercial", "advertise"]
        
        scores = []
        
        if any(indicator in content_lower for indicator in educational_indicators):
            scores.append(self.fair_use_factors["purpose_and_character"]["educational"])
        
        if any(indicator in content_lower for indicator in commentary_indicators):
            scores.append(self.fair_use_factors["purpose_and_character"]["commentary"])
        
        if any(indicator in content_lower for indicator in criticism_indicators):
            scores.append(self.fair_use_factors["purpose_and_character"]["criticism"])
        
        if any(indicator in content_lower for indicator in news_indicators):
            scores.append(self.fair_use_factors["purpose_and_character"]["news_reporting"])
        
        if any(indicator in content_lower for indicator in commercial_indicators):
            scores.append(self.fair_use_factors["purpose_and_character"]["commercial"])
        
        return max(scores) if scores else 0.5
    
    def _assess_nature_of_work(self, content: str) -> float:
        """Assess nature of work factor for fair use"""
        # Default to creative work (conservative approach)
        return self.fair_use_factors["nature_of_work"]["creative"]
    
    def _assess_amount_used(self, content: str, context: Optional[Dict[str, Any]]) -> float:
        """Assess amount used factor for fair use"""
        # For conversational AI, typically minimal amounts
        return self.fair_use_factors["amount_used"]["minimal"]
    
    def _assess_market_effect(self, content: str, context: Optional[Dict[str, Any]]) -> float:
        """Assess market effect factor for fair use"""
        content_lower = content.lower()
        
        commercial_indicators = ["buy", "sell", "purchase", "order", "alternative", "substitute"]
        
        if any(indicator in content_lower for indicator in commercial_indicators):
            return self.fair_use_factors["market_effect"]["moderate_harm"]
        
        return self.fair_use_factors["market_effect"]["no_harm"]
    
    async def _check_license_coverage(
        self,
        content_hash: str,
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """Check if content is covered by existing licenses"""
        coverage = {
            "has_valid_license": False,
            "applicable_licenses": [],
            "attribution_requirements": [],
            "usage_restrictions": []
        }
        
        try:
            # Check direct license coverage
            if content_hash in self.active_licenses:
                license_info = self.active_licenses[content_hash]
                coverage["has_valid_license"] = True
                coverage["applicable_licenses"].append(license_info.license_id)
                coverage["attribution_requirements"].extend(license_info.attribution_requirements)
                coverage["usage_restrictions"].extend(license_info.restrictions)
            
            # Check for pattern-based license coverage
            combined_content = user_input + " " + ai_response
            
            for content_ref, license_info in self.active_licenses.items():
                if any(perm in combined_content.lower() for perm in license_info.permissions):
                    # Check if usage falls within license permissions
                    usage_allowed = self._check_usage_permissions(
                        combined_content, license_info
                    )
                    
                    if usage_allowed:
                        coverage["has_valid_license"] = True
                        coverage["applicable_licenses"].append(license_info.license_id)
                        coverage["attribution_requirements"].extend(license_info.attribution_requirements)
            
        except Exception as e:
            self.logger.error(f"Error checking license coverage: {str(e)}")
        
        return coverage
    
    def _check_usage_permissions(self, content: str, license_info: ContentLicense) -> bool:
        """Check if content usage is allowed under license"""
        # Check restrictions
        for restriction in license_info.restrictions:
            if restriction.lower() in content.lower():
                return False
        
        # Check territory restrictions
        # (Would need context about user location)
        
        # Check usage limits
        # (Would need tracking of previous usage)
        
        return True
    
    def _generate_rights_recommendations(self, assessment: RightsAssessment) -> List[str]:
        """Generate rights compliance recommendations"""
        recommendations = []
        
        if assessment.violations:
            recommendations.extend([
                "Review content for potential rights violations",
                "Consider obtaining proper licenses for protected content",
                "Add appropriate attribution for referenced works"
            ])
        
        if assessment.rights_status == RightsStatus.FAIR_USE_CLAIMED:
            recommendations.extend([
                "Document fair use justification",
                "Consider adding fair use disclaimer",
                "Limit usage to fair use purposes"
            ])
        
        if assessment.attributions_required:
            recommendations.extend([
                "Add required attributions to content",
                "Ensure attribution format meets license requirements"
            ])
        
        return recommendations
    
    def _generate_legal_warnings(self, assessment: RightsAssessment) -> List[str]:
        """Generate legal warnings for rights issues"""
        warnings = []
        
        high_risk_violations = [
            v for v in assessment.violations 
            if v.severity in ["high", "critical"]
        ]
        
        if high_risk_violations:
            warnings.append("High-risk rights violations detected - legal review recommended")
        
        if assessment.rights_status == RightsStatus.VIOLATION_DETECTED:
            warnings.append("Rights violation detected - content usage may require permission")
        
        if not assessment.fair_use_factors.get("likely_fair_use", False) and assessment.violations:
            warnings.append("Fair use unlikely - consider removing or licensing content")
        
        return warnings
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content identification"""



        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _determine_content_type(self, content: str) -> ContentType:
        """Determine content type from content analysis"""
        # For conversational AI, primarily text content
        return ContentType.TEXT
    
    async def _store_rights_assessment(self, assessment: RightsAssessment) -> None:
        """Store rights assessment results"""



        try:
            query = """
                INSERT INTO rights_assessments 
                (content_id, content_type, rights_status, violations_count, 
                 confidence_score, processing_time_ms, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            await self.db_manager.execute(
                query,
                assessment.content_id,
                assessment.content_type.value,
                assessment.rights_status.value,
                len(assessment.violations),
                assessment.confidence_score,
                assessment.processing_time_ms,
                datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error storing rights assessment: {str(e)}")
    
    async def add_copyrighted_work(
        self,
        content_hash: str,
        title: str,
        owner: str,
        fingerprint: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add copyrighted work to database"""



        try:
            work_data = {
                "content_hash": content_hash,
                "title": title,
                "owner": owner,
                "fingerprint": fingerprint,
                "metadata": metadata or {},
                "active": True,
                "created_at": datetime.now()
            }
            
            await self.db_manager.execute(
                """
                INSERT INTO copyrighted_works 
                (content_hash, title, owner, fingerprint, metadata, active, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                **work_data
            )
            
            self.known_copyrighted_works[content_hash] = work_data
            self.logger.info(f"Added copyrighted work: {title}")
            
        except Exception as e:
            self.logger.error(f"Error adding copyrighted work: {str(e)}")
    
    async def register_content_license(self, license_info: ContentLicense) -> None:
        """Register a content license"""



        try:
            await self.db_manager.execute(
                """
                INSERT INTO content_licenses 
                (license_id, content_reference, license_type, licensor, licensee,
                 permissions, restrictions, attribution_requirements, expiry_date,
                 territory, usage_limits, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                license_info.license_id,
                license_info.content_reference,
                license_info.license_type,
                license_info.licensor,
                license_info.licensee,
                license_info.permissions,
                license_info.restrictions,
                license_info.attribution_requirements,
                license_info.expiry_date,
                license_info.territory,
                license_info.usage_limits,
                datetime.now()
            )
            
            self.active_licenses[license_info.content_reference] = license_info
            self.logger.info(f"Registered license: {license_info.license_id}")
            
        except Exception as e:
            self.logger.error(f"Error registering license: {str(e)}")
    
    async def get_rights_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get rights management statistics"""



        try:
            stats_query = """
                SELECT 
                    rights_status,
                    COUNT(*) as count,
                    AVG(confidence_score) as avg_confidence
                FROM rights_assessments 
                WHERE created_at >= $1
                GROUP BY rights_status
            """
            
            stats = await self.db_manager.fetch_all(
                stats_query,
                datetime.now() - timedelta(days=days)
            )
            
            return {
                "period_days": days,
                "status_distribution": {stat["rights_status"]: stat["count"] for stat in stats},
                "avg_confidence_by_status": {stat["rights_status"]: stat["avg_confidence"] for stat in stats},
                "total_assessments": sum(stat["count"] for stat in stats),
                "known_copyrighted_works": len(self.known_copyrighted_works),
                "active_licenses": len(self.active_licenses),
                "registered_trademarks": len(self.registered_trademarks)
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching rights statistics: {str(e)}")
            return {}
