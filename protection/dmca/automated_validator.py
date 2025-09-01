"""🤖 DMCA Automated Validation Engine
==================================

AI-powered validation system for DMCA claims with legal compliance checking.
Validates evidence strength, legal basis, and automated quality assurance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚠️  LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION ⚠️
====================================================
This software and all associated concepts, algorithms, and implementations are the
exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).

Any unauthorized use, reproduction, distribution, or derivation of this work without
explicit written permission from Fahed Mlaiel is strictly prohibited and may result in:
- Immediate legal action under German and International copyright law
- Claims for damages and lost profits
- Injunctive relief to prevent further infringement
- Criminal prosecution where applicable

Contact: mlaiel@live.de for licensing inquiries.

Project Team Specialties:
- Lead AI Developer & Architect: Advanced ML/AI systems
- Backend Senior Engineer: Enterprise Python/FastAPI systems
- DevOps Engineer: Kubernetes/Cloud infrastructure  
- Security Specialist: Cybersecurity & legal compliance
- Audio Processing Engineer: Digital signal processing
- Database Administrator: High-performance data systems
- Microservices Architect: Distributed systems design
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum
import json
import re
import hashlib
import uuid
from urllib.parse import urlparse, parse_qs
import aiohttp

from pydantic import BaseModel, Field, validator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import (
    DMCAStatus, DMCAPriority, ContentType, PlatformType, 
    EvidenceType, LegalJurisdiction, DMCAEvidence, 
    DMCAContentInfo, DMCAInfringement
)

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """
Validation outcome classifications"""

    APPROVED = "approved"              # Strong case, proceed with confidence
    CONDITIONAL = "conditional"        # Good case, minor issues to address
    REVIEW_REQUIRED = "review_required"  # Manual review needed
    INSUFFICIENT = "insufficient"      # Weak case, need more evidence
    REJECTED = "rejected"              # Invalid case, do not proceed


class LegalRiskLevel(IntEnum):
    """Legal risk assessment levels"""

    MINIMAL = 1        # < 5% risk of counter-claim
    LOW = 2           # 5-15% risk
    MODERATE = 3      # 15-30% risk
    HIGH = 4          # 30-50% risk
    SEVERE = 5        # > 50% risk


@dataclass
class ValidationReport:
    """
Comprehensive validation assessment report"""
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    result: ValidationResult = ValidationResult.REVIEW_REQUIRED
    confidence_score: float = 0.0  # 0.0 to 1.0
    legal_risk: LegalRiskLevel = LegalRiskLevel.MODERATE
    
    # Detailed scores
    evidence_strength: float = 0.0
    legal_compliance: float = 0.0
    fair_use_risk: float = 0.0
    commercial_use_evidence: float = 0.0
    
    # Issues and recommendations
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Evidence analysis
    evidence_summary: Dict[str, Any] = field(default_factory=dict)
    similarity_analysis: Dict[str, float] = field(default_factory=dict)
    
    # Legal assessment
    jurisdiction_compliance: Dict[str, bool] = field(default_factory=dict)
    statutory_damages_estimate: Optional[Tuple[float, float]] = None
    success_probability: float = 0.0


class DMCAAutomatedValidator:
    """
Enterprise-grade automated DMCA validation engine"""
    
    def __init__(self):
        self.text_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.validation_cache: Dict[str, ValidationReport] = {}
        self.legal_precedents: Dict[str, Any] = self._load_legal_precedents()
        
    def _load_legal_precedents(self) -> Dict[str, Any]:
        """
Load legal precedents and guidelines for validation"""
        return {
            'fair_use_keywords': [
                'parody', 'criticism', 'review', 'comment', 'news reporting',
                'teaching', 'scholarship', 'research', 'educational'
            ],
            'commercial_indicators': [
                'advertisement', 'sponsored', 'promotional', 'monetized',
                'commercial', 'business', 'profit', 'revenue'
            ],
            'minimum_similarity_thresholds': {
                ContentType.AUDIO: 0.80,
                ContentType.VIDEO: 0.75,
                ContentType.IMAGE: 0.85,
                ContentType.TEXT: 0.70
            },
            'platform_response_rates': {
                PlatformType.YOUTUBE: 0.92,
                PlatformType.INSTAGRAM: 0.88,
                PlatformType.TIKTOK: 0.85,
                PlatformType.FACEBOOK: 0.90,
                PlatformType.TWITTER: 0.78,
                PlatformType.GENERIC_WEB: 0.65
            }
        }
    
    async def validate_dmca_claim(self,
                                  original_content: DMCAContentInfo,
                                  infringement: DMCAInfringement,
                                  jurisdiction: LegalJurisdiction = LegalJurisdiction.US_FEDERAL
                                  ) -> ValidationReport:
        """
        Comprehensive automated validation of DMCA claim
        
        Args:
            original_content: Original copyrighted content
            infringement: Alleged infringing content
            jurisdiction: Legal jurisdiction for compliance
            
        Returns:
            ValidationReport: Detailed validation assessment
        """
        logger.info(f"Starting automated validation for infringement {infringement.infringement_id}")
        
        # Generate cache key
        cache_key = self._generate_cache_key(original_content, infringement)
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        # Initialize validation report
        report = ValidationReport()
        
        try:
            # 1. Evidence strength analysis
            evidence_score = await self._analyze_evidence_strength(infringement.evidence_list)
            report.evidence_strength = evidence_score
            
            # 2. Similarity analysis
            similarity_scores = await self._analyze_content_similarity(
                original_content, infringement
            )
            report.similarity_analysis = similarity_scores
            
            # 3. Legal compliance check
            compliance_score = await self._check_legal_compliance(
                original_content, infringement, jurisdiction
            )
            report.legal_compliance = compliance_score
            
            # 4. Fair use risk assessment
            fair_use_risk = await self._assess_fair_use_risk(
                original_content, infringement
            )
            report.fair_use_risk = fair_use_risk
            
            # 5. Commercial use evidence
            commercial_score = await self._analyze_commercial_use(infringement)
            report.commercial_use_evidence = commercial_score
            
            # 6. Calculate overall confidence
            report.confidence_score = self._calculate_confidence_score(
                evidence_score, max(similarity_scores.values()) if similarity_scores else 0.0,
                compliance_score, fair_use_risk, commercial_score
            )
            
            # 7. Determine validation result
            report.result = self._determine_validation_result(report)
            
            # 8. Assess legal risk
            report.legal_risk = self._assess_legal_risk(report)
            
            # 9. Generate recommendations
            await self._generate_recommendations(report, original_content, infringement)
            
            # 10. Calculate success probability
            report.success_probability = self._calculate_success_probability(
                report, infringement.platform
            )
            
            # 11. Estimate statutory damages
            report.statutory_damages_estimate = self._estimate_statutory_damages(
                report, commercial_score > 0.7
            )
            
            # Cache the result
            self.validation_cache[cache_key] = report
            
            logger.info(f"Validation completed: {report.result.value} (confidence: {report.confidence_score:.2f})")
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            report.result = ValidationResult.REJECTED
            report.critical_issues.append(f"Validation error: {str(e)}")
        
        return report
    
    async def _analyze_evidence_strength(self, evidence_list: List[DMCAEvidence]) -> float:
        """Analyze the strength of provided evidence"""
        if not evidence_list:
            return 0.0
        
        evidence_weights = {
            EvidenceType.AUDIO_FINGERPRINT: 0.25,
            EvidenceType.VIDEO_FINGERPRINT: 0.25,
            EvidenceType.IMAGE_HASH: 0.20,
            EvidenceType.TEXT_SIMILARITY: 0.15,
            EvidenceType.COPYRIGHT_REGISTRATION: 0.30,
            EvidenceType.TIMESTAMP_PROOF: 0.20,
            EvidenceType.METADATA_ANALYSIS: 0.15,
            EvidenceType.USAGE_ANALYTICS: 0.10,
            EvidenceType.REVENUE_IMPACT: 0.15,
            EvidenceType.SCREENSHOT: 0.05,
            EvidenceType.VIDEO_CAPTURE: 0.10
        }
        
        total_weight = 0.0
        weighted_score = 0.0
        
        for evidence in evidence_list:
            weight = evidence_weights.get(evidence.evidence_type, 0.05)
            total_weight += weight
            
            # Score based on similarity and verification status
            evidence_score = 0.0
            if evidence.similarity_score:
                evidence_score = evidence.similarity_score
            
            if evidence.verification_status == "verified":
                evidence_score *= 1.2
            elif evidence.verification_status == "pending":
                evidence_score *= 0.8
            
            if evidence.legal_admissible:
                evidence_score *= 1.1
            
            weighted_score += evidence_score * weight
        
        return min(1.0, weighted_score / max(0.1, total_weight))
    
    async def _analyze_content_similarity(self,
                                          original: DMCAContentInfo,
                                          infringement: DMCAInfringement
                                          ) -> Dict[str, float]:
        """Analyze similarity between original and infringing content"""
        similarities = {}
        
        # Title similarity
        if original.title and infringement.content_title:
            title_sim = self._calculate_text_similarity(
                original.title, infringement.content_title
            )
            similarities['title'] = title_sim
        
        # Fingerprint similarity (if available in evidence)
        for evidence in infringement.evidence_list:
            if evidence.similarity_score and evidence.similarity_score > 0:
                similarities[evidence.evidence_type.value] = evidence.similarity_score
        
        # Metadata similarity
        if original.metadata and infringement.similarity_analysis:
            metadata_sim = self._compare_metadata(
                original.metadata, infringement.similarity_analysis
            )
            similarities['metadata'] = metadata_sim
        
        return similarities
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            corpus = [text1.lower(), text2.lower()]
            tfidf_matrix = self.text_vectorizer.fit_transform(corpus)
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except Exception:
            return 0.0
    
    def _compare_metadata(self, original_meta: Dict[str, Any], 
                         infringement_meta: Dict[str, Any]) -> float:
        """
Compare metadata between original and infringing content"""
        common_keys = set(original_meta.keys()) & set(infringement_meta.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if original_meta[key] == infringement_meta[key]:
                matches += 1
        
        return matches / len(common_keys)
    
    async def _check_legal_compliance(self,
                                      original: DMCAContentInfo,
                                      infringement: DMCAInfringement,
                                      jurisdiction: LegalJurisdiction
                                      ) -> float:
        """
Check legal compliance requirements"""
        compliance_score = 0.0
        total_checks = 0
        
        # Check copyright registration (if applicable)
        total_checks += 1
        if original.registration_number or original.copyright_notice:
            compliance_score += 0.3
        
        # Check creation date proof
        total_checks += 1
        if original.creation_date and original.creation_date < infringement.discovery_date:
            compliance_score += 0.2
        
        # Check evidence admissibility
        total_checks += 1
        admissible_evidence = sum(1 for e in infringement.evidence_list if e.legal_admissible)
        if admissible_evidence > 0:
            compliance_score += min(0.3, admissible_evidence * 0.1)
        
        # Check platform-specific requirements
        total_checks += 1
        if self._check_platform_requirements(infringement.platform):
            compliance_score += 0.2
        
        return compliance_score
    
    def _check_platform_requirements(self, platform: PlatformType) -> bool:
        """
Check platform-specific DMCA requirements"""
        # Each platform has specific requirements
        platform_reqs = {
            PlatformType.YOUTUBE: True,  # Generally DMCA compliant
            PlatformType.INSTAGRAM: True,
            PlatformType.FACEBOOK: True,
            PlatformType.TIKTOK: True,
            PlatformType.TWITTER: True,
            PlatformType.GENERIC_WEB: False  # Need to verify manually
        }
        return platform_reqs.get(platform, False)
    
    async def _assess_fair_use_risk(self,
                                    original: DMCAContentInfo,
                                    infringement: DMCAInfringement
                                    ) -> float:
        """
Assess risk of fair use defense"""
        risk_factors = 0.0
        
        # Check for fair use keywords in title/description
        content_text = (infringement.content_title or "").lower()
        
        fair_use_indicators = 0
        for keyword in self.legal_precedents['fair_use_keywords']:
            if keyword in content_text:
                fair_use_indicators += 1
        
        if fair_use_indicators > 0:
            risk_factors += min(0.4, fair_use_indicators * 0.1)
        
        # Educational or non-commercial use
        if not infringement.commercial_use:
            risk_factors += 0.2
        
        # Short clips (for video/audio)
        if original.content_type in [ContentType.AUDIO, ContentType.VIDEO]:
            if original.duration and original.duration > 300:  # 5 minutes
                risk_factors += 0.1
        
        return min(1.0, risk_factors)
    
    async def _analyze_commercial_use(self, infringement: DMCAInfringement) -> float:
        """Analyze evidence of commercial use"""
        commercial_score = 0.0
        
        # Check commercial indicators in content
        content_text = (infringement.content_title or "").lower()
        commercial_indicators = sum(
            1 for indicator in self.legal_precedents['commercial_indicators']
            if indicator in content_text
        )
        
        if commercial_indicators > 0:
            commercial_score += min(0.3, commercial_indicators * 0.1)
        
        # View count and revenue estimates
        if infringement.view_count and infringement.view_count > 10000:
            commercial_score += 0.2
        
        if infringement.revenue_estimate and infringement.revenue_estimate > 0:
            commercial_score += 0.3
        
        # Platform monetization
        if infringement.commercial_use:
            commercial_score += 0.2
        
        return min(1.0, commercial_score)
    
    def _calculate_confidence_score(self, evidence: float, similarity: float,
                                   compliance: float, fair_use_risk: float,
                                   commercial: float) -> float:
        """Calculate overall confidence score"""
        # Weighted average with risk adjustment
        weights = {
            'evidence': 0.30,
            'similarity': 0.25,
            'compliance': 0.20,
            'commercial': 0.15,
            'fair_use_risk': -0.10  # Negative weight (risk factor)
        }
        
        confidence = (
            evidence * weights['evidence'] +
            similarity * weights['similarity'] +
            compliance * weights['compliance'] +
            commercial * weights['commercial'] +
            (1 - fair_use_risk) * abs(weights['fair_use_risk'])
        )
        
        return max(0.0, min(1.0, confidence))
    
    def _determine_validation_result(self, report: ValidationReport) -> ValidationResult:
        """
Determine final validation result based on scores"""
        confidence = report.confidence_score
        
        if confidence >= 0.85 and report.fair_use_risk <= 0.2:
            return ValidationResult.APPROVED
        elif confidence >= 0.70 and report.fair_use_risk <= 0.4:
            return ValidationResult.CONDITIONAL
        elif confidence >= 0.50:
            return ValidationResult.REVIEW_REQUIRED
        elif confidence >= 0.30:
            return ValidationResult.INSUFFICIENT
        else:
            return ValidationResult.REJECTED
    
    def _assess_legal_risk(self, report: ValidationReport) -> LegalRiskLevel:
        """
Assess legal risk level"""
        risk_score = (
            (1 - report.confidence_score) * 0.4 +
            report.fair_use_risk * 0.3 +
            (1 - report.legal_compliance) * 0.3
        )
        
        if risk_score <= 0.15:
            return LegalRiskLevel.MINIMAL
        elif risk_score <= 0.30:
            return LegalRiskLevel.LOW
        elif risk_score <= 0.50:
            return LegalRiskLevel.MODERATE
        elif risk_score <= 0.70:
            return LegalRiskLevel.HIGH
        else:
            return LegalRiskLevel.SEVERE
    
    async def _generate_recommendations(self, report: ValidationReport,
                                       original: DMCAContentInfo,
                                       infringement: DMCAInfringement):
        """
Generate actionable recommendations"""
        if report.evidence_strength < 0.7:
            report.recommendations.append(
                "Gather additional evidence to strengthen the claim"
            )
        
        if report.legal_compliance < 0.8:
            report.recommendations.append(
                "Ensure all legal requirements are met before proceeding"
            )
        
        if report.fair_use_risk > 0.4:
            report.warnings.append(
                "High risk of fair use defense - consider legal review"
            )
        
        if report.confidence_score < 0.5:
            report.critical_issues.append(
                "Insufficient evidence for strong DMCA claim"
            )
        
        # Platform-specific recommendations
        platform_response_rate = self.legal_precedents['platform_response_rates'].get(
            infringement.platform, 0.5
        )
        
        if platform_response_rate < 0.8:
            report.recommendations.append(
                f"Consider alternative enforcement methods for {infringement.platform.value}"
            )
    
    def _calculate_success_probability(self, report: ValidationReport,
                                      platform: PlatformType) -> float:
        """Calculate probability of successful DMCA takedown"""
        base_probability = self.legal_precedents['platform_response_rates'].get(
            platform, 0.5
        )
        
        # Adjust based on validation scores
        adjustment = (
            report.confidence_score * 0.3 +
            report.evidence_strength * 0.2 +
            report.legal_compliance * 0.2 +
            report.commercial_use_evidence * 0.1 +
            (1 - report.fair_use_risk) * 0.2
        )
        
        return min(0.95, base_probability * (0.5 + adjustment))
    
    def _estimate_statutory_damages(self, report: ValidationReport,
                                   commercial_use: bool) -> Tuple[float, float]:
        """
Estimate potential statutory damages range"""
        base_min = 750.0
        base_max = 30000.0
        
        # Adjust based on evidence strength
        if report.evidence_strength >= 0.9:
            base_max = 50000.0
        elif report.evidence_strength < 0.6:
            base_max = 15000.0
        
        # Commercial use increases damages
        if commercial_use:
            base_min *= 2
            base_max = min(150000.0, base_max * 3)
        
        # Willful infringement (high commercial score)
        if report.commercial_use_evidence > 0.8:
            base_max = min(150000.0, base_max * 2)
        
        return (base_min, base_max)
    
    def _generate_cache_key(self, original: DMCAContentInfo,
                           infringement: DMCAInfringement) -> str:
        """
Generate cache key for validation results"""
        content_hash = hashlib.md5(
            f"{original.content_id}{infringement.infringement_id}".encode()
        ).hexdigest()
        return f"validation_{content_hash}"
    
    async def batch_validate_claims(self,
                                   claims: List[Tuple[DMCAContentInfo, DMCAInfringement]]
                                   ) -> List[ValidationReport]:
        """Batch validate multiple DMCA claims"""
        tasks = [
            self.validate_dmca_claim(original, infringement)
            for original, infringement in claims
        ]
        
        return await asyncio.gather(*tasks)
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """
Get validation engine statistics"""
        if not self.validation_cache:
            return {"total_validations": 0}
        
        reports = list(self.validation_cache.values())
        
        return {
            "total_validations": len(reports),
            "approval_rate": len([r for r in reports if r.result == ValidationResult.APPROVED]) / len(reports),
            "average_confidence": sum(r.confidence_score for r in reports) / len(reports),
            "high_risk_cases": len([r for r in reports if r.legal_risk >= LegalRiskLevel.HIGH]),
            "success_probability_avg": sum(r.success_probability for r in reports) / len(reports)
        }


# Export main classes
__all__ = [
    'ValidationResult',
    'LegalRiskLevel', 
    'ValidationReport',
    'DMCAAutomatedValidator'
]
