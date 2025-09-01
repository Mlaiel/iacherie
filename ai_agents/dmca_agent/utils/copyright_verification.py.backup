"""Copyright Verification - Advanced Copyright Ownership Verification System
=========================================================================

Enterprise-grade copyright verification engine with blockchain integration,
digital signatures, and automated ownership validation for content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import hmac
import base64
from pathlib import Path
import uuid

from ..base import BaseAgent, AgentRequest, AgentResponse
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...utils.blockchain_client import BlockchainClient
from ...utils.digital_signature import DigitalSignatureValidator
from ...utils.copyright_registry import CopyrightRegistryClient
from ...models.copyright import CopyrightRecord, OwnershipProof, VerificationStatus

logger = logging.getLogger(__name__)

class VerificationMethod(Enum):
    """Copyright verification methods"""
    BLOCKCHAIN_PROOF = "blockchain_proof"
    DIGITAL_SIGNATURE = "digital_signature"
    COPYRIGHT_REGISTRY = "copyright_registry"
    CREATION_TIMESTAMP = "creation_timestamp"
    PLATFORM_METADATA = "platform_metadata"
    LEGAL_DOCUMENTATION = "legal_documentation"
    WATERMARK_ANALYSIS = "watermark_analysis"
    FINGERPRINT_MATCHING = "fingerprint_matching"

class OwnershipStrength(Enum):
    """Copyright ownership strength levels"""
    DEFINITIVE = "definitive"      # 95-100% certainty
    STRONG = "strong"              # 85-94% certainty  
    MODERATE = "moderate"          # 70-84% certainty
    WEAK = "weak"                  # 50-69% certainty
    DISPUTED = "disputed"          # Multiple claims
    INVALID = "invalid"            # No valid proof

class CopyrightType(Enum):
    """Types of copyrighted content"""
    MUSICAL_WORK = "musical_work"
    SOUND_RECORDING = "sound_recording"
    LITERARY_WORK = "literary_work"
    VISUAL_ART = "visual_art"
    AUDIOVISUAL_WORK = "audiovisual_work"
    DRAMATIC_WORK = "dramatic_work"
    CHOREOGRAPHIC_WORK = "choreographic_work"
    ARCHITECTURAL_WORK = "architectural_work"

@dataclass
class CopyrightClaim:
    """Copyright ownership claim"""
    claim_id: str
    claimant_name: str
    claimant_email: str
    content_id: str
    content_type: CopyrightType
    creation_date: datetime
    registration_number: Optional[str]
    proof_documents: List[str]
    verification_methods: List[VerificationMethod]
    blockchain_hash: Optional[str]
    digital_signature: Optional[str]
    ownership_percentage: float = 100.0
    
@dataclass
class VerificationResult:
    """Copyright verification result"""
    claim_id: str
    content_id: str
    verification_score: float  # 0-100%
    ownership_strength: OwnershipStrength
    verified_methods: List[VerificationMethod]
    failed_methods: List[VerificationMethod]
    ownership_chain: List[Dict[str, Any]]
    conflicting_claims: List[str]
    recommendations: List[str]
    legal_risks: List[str]
    next_actions: List[str]
    verification_timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

@dataclass
class OwnershipEvidence:
    """Evidence supporting copyright ownership"""
    evidence_id: str
    evidence_type: str
    content: str
    metadata: Dict[str, Any]
    verification_score: float
    created_at: datetime
    verified_by: Optional[str] = None

class CopyrightVerification:
    """
    Enterprise Copyright Verification System
    
    Provides comprehensive copyright ownership verification using multiple
    methods including blockchain, digital signatures, and registry databases.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blockchain_client = BlockchainClient()
        self.signature_validator = DigitalSignatureValidator()
        self.registry_client = CopyrightRegistryClient()
        
        # Verification weights for different methods
        self.method_weights = self._initialize_method_weights()
        
        # Known copyright registries
        self.copyright_registries = self._initialize_registries()
        
        # Verification cache
        self.verification_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        self.logger.info("Copyright Verification initialized successfully")
    
    def _initialize_method_weights(self) -> Dict[VerificationMethod, float]:
        """Initialize verification method weights"""
        return {
            VerificationMethod.BLOCKCHAIN_PROOF: 0.25,
            VerificationMethod.DIGITAL_SIGNATURE: 0.20,
            VerificationMethod.COPYRIGHT_REGISTRY: 0.20,
            VerificationMethod.CREATION_TIMESTAMP: 0.10,
            VerificationMethod.PLATFORM_METADATA: 0.08,
            VerificationMethod.LEGAL_DOCUMENTATION: 0.07,
            VerificationMethod.WATERMARK_ANALYSIS: 0.05,
            VerificationMethod.FINGERPRINT_MATCHING: 0.05
        }
    
    def _initialize_registries(self) -> Dict[str, Dict[str, Any]]:
        """Initialize copyright registry configurations"""
        return {
            "us_copyright_office": {
                "name": "US Copyright Office",
                "api_endpoint": "https://cocatalog.loc.gov/cgi-bin/Pwebrecon.cgi",
                "search_method": "public_catalog",
                "reliability": 0.95
            },
            "uk_ipo": {
                "name": "UK Intellectual Property Office", 
                "api_endpoint": "https://www.gov.uk/government/organisations/intellectual-property-office",
                "search_method": "public_search",
                "reliability": 0.90
            },
            "wipo": {
                "name": "World Intellectual Property Organization",
                "api_endpoint": "https://www.wipo.int/branddb/en/",
                "search_method": "global_brand_database",
                "reliability": 0.85
            },
            "ascap": {
                "name": "ASCAP Repertory",
                "api_endpoint": "https://www.ascap.com/repertory",
                "search_method": "repertory_search",
                "reliability": 0.90
            },
            "bmi": {
                "name": "BMI Repertoire",
                "api_endpoint": "https://repertoire.bmi.com/",
                "search_method": "repertoire_search", 
                "reliability": 0.90
            }
        }
    
    async def verify_copyright_ownership(
        self,
        claim: CopyrightClaim,
        evidence_files: Optional[List[Dict[str, Any]]] = None
    ) -> VerificationResult:
        """
        Comprehensive copyright ownership verification
        
        Args:
            claim: Copyright ownership claim
            evidence_files: Additional evidence files
            
        Returns:
            VerificationResult with detailed verification analysis
        """
        try:
            self.logger.info(f"Starting copyright verification for claim {claim.claim_id}")
            
            # Initialize result
            result = VerificationResult(
                claim_id=claim.claim_id,
                content_id=claim.content_id,
                verification_score=0.0,
                ownership_strength=OwnershipStrength.INVALID,
                verified_methods=[],
                failed_methods=[],
                ownership_chain=[],
                conflicting_claims=[],
                recommendations=[],
                legal_risks=[],
                next_actions=[]
            )
            
            # Check cache first
            cache_key = self._generate_cache_key(claim)
            cached_result = await self._get_cached_verification(cache_key)
            if cached_result:
                return cached_result
            
            # Collect all evidence
            all_evidence = await self._collect_evidence(claim, evidence_files)
            
            # Run verification methods
            method_scores = {}
            
            for method in claim.verification_methods:
                try:
                    score = await self._run_verification_method(method, claim, all_evidence)
                    method_scores[method] = score
                    
                    if score > 0.7:  # 70% threshold for success
                        result.verified_methods.append(method)
                    else:
                        result.failed_methods.append(method)
                        
                except Exception as e:
                    self.logger.warning(f"Verification method {method} failed: {str(e)}")
                    result.failed_methods.append(method)
                    method_scores[method] = 0.0
            
            # Calculate weighted score
            result.verification_score = await self._calculate_weighted_score(method_scores)
            
            # Determine ownership strength
            result.ownership_strength = self._determine_ownership_strength(result.verification_score)
            
            # Build ownership chain
            result.ownership_chain = await self._build_ownership_chain(claim, all_evidence)
            
            # Check for conflicting claims
            result.conflicting_claims = await self._detect_conflicting_claims(claim)
            
            # Generate recommendations and risks
            await self._generate_verification_recommendations(result, claim, method_scores)
            
            # Set expiration
            result.expires_at = datetime.now() + timedelta(hours=24)
            
            # Cache result
            await self._cache_verification_result(cache_key, result)
            
            self.logger.info(f"Copyright verification completed: {result.verification_score:.1f}%")
            return result
            
        except Exception as e:
            self.logger.error(f"Copyright verification failed: {str(e)}")
            raise
    
    async def _collect_evidence(
        self,
        claim: CopyrightClaim,
        evidence_files: Optional[List[Dict[str, Any]]]
    ) -> List[OwnershipEvidence]:
        """Collect all available evidence for copyright claim"""
        evidence_list = []
        
        # Add blockchain evidence
        if claim.blockchain_hash:
            blockchain_evidence = await self._extract_blockchain_evidence(claim)
            if blockchain_evidence:
                evidence_list.append(blockchain_evidence)
        
        # Add digital signature evidence
        if claim.digital_signature:
            signature_evidence = await self._extract_signature_evidence(claim)
            if signature_evidence:
                evidence_list.append(signature_evidence)
        
        # Add registry evidence
        if claim.registration_number:
            registry_evidence = await self._extract_registry_evidence(claim)
            if registry_evidence:
                evidence_list.extend(registry_evidence)
        
        # Add file-based evidence
        if evidence_files:
            file_evidence = await self._extract_file_evidence(evidence_files)
            evidence_list.extend(file_evidence)
        
        # Add platform metadata evidence
        platform_evidence = await self._extract_platform_evidence(claim)
        evidence_list.extend(platform_evidence)
        
        return evidence_list
    
    async def _run_verification_method(
        self,
        method: VerificationMethod,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Run specific verification method"""
        method_evidence = [e for e in evidence if method.value in e.evidence_type]
        
        if method == VerificationMethod.BLOCKCHAIN_PROOF:
            return await self._verify_blockchain_proof(claim, method_evidence)
        
        elif method == VerificationMethod.DIGITAL_SIGNATURE:
            return await self._verify_digital_signature(claim, method_evidence)
        
        elif method == VerificationMethod.COPYRIGHT_REGISTRY:
            return await self._verify_registry_registration(claim, method_evidence)
        
        elif method == VerificationMethod.CREATION_TIMESTAMP:
            return await self._verify_creation_timestamp(claim, method_evidence)
        
        elif method == VerificationMethod.PLATFORM_METADATA:
            return await self._verify_platform_metadata(claim, method_evidence)
        
        elif method == VerificationMethod.LEGAL_DOCUMENTATION:
            return await self._verify_legal_documentation(claim, method_evidence)
        
        elif method == VerificationMethod.WATERMARK_ANALYSIS:
            return await self._verify_watermark_analysis(claim, method_evidence)
        
        elif method == VerificationMethod.FINGERPRINT_MATCHING:
            return await self._verify_fingerprint_matching(claim, method_evidence)
        
        else:
            return 0.0
    
    async def _verify_blockchain_proof(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify blockchain-based copyright proof"""
        try:
            if not claim.blockchain_hash:
                return 0.0
            
            # Verify blockchain transaction
            blockchain_record = await self.blockchain_client.get_transaction(claim.blockchain_hash)
            
            if not blockchain_record:
                return 0.0
            
            # Verify transaction authenticity
            is_authentic = await self.blockchain_client.verify_transaction_authenticity(
                claim.blockchain_hash
            )
            
            if not is_authentic:
                return 0.2  # Low score for invalid blockchain proof
            
            # Check timestamp consistency
            blockchain_timestamp = blockchain_record.get("timestamp")
            if blockchain_timestamp:
                blockchain_date = datetime.fromtimestamp(blockchain_timestamp)
                
                # Blockchain proof should predate or match creation claim
                if blockchain_date <= claim.creation_date + timedelta(days=1):
                    return 0.95  # Very high confidence
                else:
                    return 0.3   # Suspicious timing
            
            return 0.8  # Good blockchain proof without timestamp verification
            
        except Exception as e:
            self.logger.error(f"Blockchain verification failed: {str(e)}")
            return 0.0
    
    async def _verify_digital_signature(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify digital signature authenticity"""
        try:
            if not claim.digital_signature:
                return 0.0
            
            # Verify signature authenticity
            is_valid = await self.signature_validator.verify_signature(
                claim.digital_signature,
                claim.content_id,
                claim.claimant_email
            )
            
            if not is_valid:
                return 0.1  # Invalid signature
            
            # Check certificate chain
            certificate_valid = await self.signature_validator.verify_certificate_chain(
                claim.digital_signature
            )
            
            if not certificate_valid:
                return 0.4  # Valid signature but questionable certificate
            
            # Check timestamp
            signature_timestamp = await self.signature_validator.get_signature_timestamp(
                claim.digital_signature
            )
            
            if signature_timestamp:
                sig_date = datetime.fromtimestamp(signature_timestamp)
                if sig_date <= claim.creation_date + timedelta(hours=24):
                    return 0.9  # Excellent signature proof
                else:
                    return 0.6  # Valid but late signature
            
            return 0.8  # Good signature without timestamp
            
        except Exception as e:
            self.logger.error(f"Digital signature verification failed: {str(e)}")
            return 0.0
    
    async def _verify_registry_registration(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify copyright registry registration"""
        try:
            if not claim.registration_number:
                return 0.0
            
            best_score = 0.0
            
            # Check multiple registries
            for registry_name, registry_config in self.copyright_registries.items():
                try:
                    registration_data = await self.registry_client.search_registration(
                        registry_config,
                        claim.registration_number,
                        claim.claimant_name
                    )
                    
                    if registration_data:
                        # Verify registration details match claim
                        match_score = await self._calculate_registration_match(
                            claim, registration_data
                        )
                        
                        # Weight by registry reliability
                        weighted_score = match_score * registry_config["reliability"]
                        
                        best_score = max(best_score, weighted_score)
                        
                except Exception as e:
                    self.logger.warning(f"Registry {registry_name} search failed: {str(e)}")
                    continue
            
            return best_score
            
        except Exception as e:
            self.logger.error(f"Registry verification failed: {str(e)}")
            return 0.0
    
    async def _verify_creation_timestamp(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify creation timestamp consistency"""
        try:
            creation_evidences = []
            
            # Collect timestamp evidence from various sources
            for evidence_item in evidence:
                if "timestamp" in evidence_item.evidence_type:
                    creation_evidences.append(evidence_item)
            
            if not creation_evidences:
                return 0.0
            
            # Analyze timestamp consistency
            timestamps = []
            for evidence_item in creation_evidences:
                timestamp_data = json.loads(evidence_item.content)
                if "created_at" in timestamp_data:
                    timestamps.append(
                        datetime.fromisoformat(timestamp_data["created_at"])
                    )
            
            if not timestamps:
                return 0.0
            
            # Check consistency with claim
            claim_date = claim.creation_date
            
            consistent_count = 0
            for timestamp in timestamps:
                # Allow 24 hour variance
                if abs((timestamp - claim_date).total_seconds()) <= 86400:
                    consistent_count += 1
            
            consistency_ratio = consistent_count / len(timestamps)
            
            # Score based on consistency and evidence count
            evidence_strength = min(len(timestamps) / 3, 1.0)  # More evidence = stronger
            
            return consistency_ratio * evidence_strength
            
        except Exception as e:
            self.logger.error(f"Timestamp verification failed: {str(e)}")
            return 0.0
    
    async def _verify_platform_metadata(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify platform metadata consistency"""
        try:
            metadata_evidences = [e for e in evidence if "platform_metadata" in e.evidence_type]
            
            if not metadata_evidences:
                return 0.0
            
            total_score = 0.0
            evidence_count = len(metadata_evidences)
            
            for evidence_item in metadata_evidences:
                metadata = json.loads(evidence_item.content)
                
                # Check uploader information
                uploader_match = await self._check_uploader_match(metadata, claim.claimant_email)
                
                # Check upload timestamp
                timestamp_consistency = await self._check_metadata_timestamp(
                    metadata, claim.creation_date
                )
                
                # Check platform verification badges
                verification_badges = await self._check_verification_badges(metadata)
                
                evidence_score = (
                    uploader_match * 0.5 +
                    timestamp_consistency * 0.3 +
                    verification_badges * 0.2
                )
                
                total_score += evidence_score
            
            return total_score / evidence_count if evidence_count > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Platform metadata verification failed: {str(e)}")
            return 0.0
    
    async def _verify_legal_documentation(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify legal documentation"""
        try:
            legal_evidences = [e for e in evidence if "legal_documentation" in e.evidence_type]
            
            if not legal_evidences:
                return 0.0
            
            total_score = 0.0
            
            for evidence_item in legal_evidences:
                doc_data = json.loads(evidence_item.content)
                
                # Analyze document type and authenticity
                doc_score = await self._analyze_legal_document(doc_data, claim)
                total_score += doc_score
            
            # Average score across all legal documents
            return total_score / len(legal_evidences)
            
        except Exception as e:
            self.logger.error(f"Legal documentation verification failed: {str(e)}")
            return 0.0
    
    async def _verify_watermark_analysis(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify digital watermarks in content"""
        try:
            watermark_evidences = [e for e in evidence if "watermark" in e.evidence_type]
            
            if not watermark_evidences:
                return 0.0
            
            # Analyze watermark presence and ownership information
            for evidence_item in watermark_evidences:
                watermark_data = json.loads(evidence_item.content)
                
                # Check if watermark contains claimant information
                if await self._watermark_contains_owner_info(watermark_data, claim):
                    return 0.8  # Strong watermark evidence
            
            return 0.3  # Watermark present but no clear ownership
            
        except Exception as e:
            self.logger.error(f"Watermark verification failed: {str(e)}")
            return 0.0
    
    async def _verify_fingerprint_matching(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> float:
        """Verify content fingerprint matching"""
        try:
            fingerprint_evidences = [e for e in evidence if "fingerprint" in e.evidence_type]
            
            if not fingerprint_evidences:
                return 0.0
            
            # Compare fingerprints with original content
            best_match = 0.0
            
            for evidence_item in fingerprint_evidences:
                fingerprint_data = json.loads(evidence_item.content)
                
                # Calculate similarity score
                similarity = await self._calculate_fingerprint_similarity(
                    fingerprint_data, claim.content_id
                )
                
                best_match = max(best_match, similarity)
            
            # High similarity suggests strong ownership evidence
            if best_match > 0.95:
                return 0.9
            elif best_match > 0.85:
                return 0.7
            elif best_match > 0.75:
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            self.logger.error(f"Fingerprint verification failed: {str(e)}")
            return 0.0
    
    async def _calculate_weighted_score(self, method_scores: Dict[VerificationMethod, float]) -> float:
        """Calculate weighted verification score"""
        total_score = 0.0
        total_weight = 0.0
        
        for method, score in method_scores.items():
            weight = self.method_weights.get(method, 0.0)
            total_score += score * weight
            total_weight += weight
        
        return (total_score / total_weight) * 100 if total_weight > 0 else 0.0
    
    def _determine_ownership_strength(self, verification_score: float) -> OwnershipStrength:
        """Determine ownership strength based on verification score"""
        if verification_score >= 95.0:
            return OwnershipStrength.DEFINITIVE
        elif verification_score >= 85.0:
            return OwnershipStrength.STRONG
        elif verification_score >= 70.0:
            return OwnershipStrength.MODERATE
        elif verification_score >= 50.0:
            return OwnershipStrength.WEAK
        else:
            return OwnershipStrength.INVALID
    
    async def _build_ownership_chain(
        self,
        claim: CopyrightClaim,
        evidence: List[OwnershipEvidence]
    ) -> List[Dict[str, Any]]:
        """Build chain of ownership evidence"""
        chain = []
        
        # Sort evidence by creation date
        sorted_evidence = sorted(evidence, key=lambda e: e.created_at)
        
        for evidence_item in sorted_evidence:
            chain_link = {
                "timestamp": evidence_item.created_at.isoformat(),
                "type": evidence_item.evidence_type,
                "score": evidence_item.verification_score,
                "verified_by": evidence_item.verified_by or "system"
            }
            chain.append(chain_link)
        
        return chain
    
    async def _detect_conflicting_claims(self, claim: CopyrightClaim) -> List[str]:
        """Detect conflicting copyright claims"""
        try:
            # Search for existing claims on the same content
            with get_db_session() as session:
                existing_claims = session.query(CopyrightRecord).filter(
                    CopyrightRecord.content_id == claim.content_id,
                    CopyrightRecord.claim_id != claim.claim_id
                ).all()
                
                return [record.claim_id for record in existing_claims]
                
        except Exception as e:
            self.logger.error(f"Conflicting claims detection failed: {str(e)}")
            return []
    
    async def _generate_verification_recommendations(
        self,
        result: VerificationResult,
        claim: CopyrightClaim,
        method_scores: Dict[VerificationMethod, float]
    ) -> None:
        """Generate verification recommendations and next actions"""
        # Recommendations based on score
        if result.verification_score < 50.0:
            result.recommendations.append("Strengthen copyright evidence before proceeding")
            result.legal_risks.append("Weak ownership proof may lead to failed takedown")
            result.next_actions.append("Collect additional evidence")
        
        elif result.verification_score < 70.0:
            result.recommendations.append("Consider obtaining formal copyright registration")
            result.next_actions.append("Proceed with caution and monitor responses")
        
        elif result.verification_score < 85.0:
            result.recommendations.append("Good ownership evidence, proceed with confidence")
            result.next_actions.append("Execute DMCA takedown")
        
        else:
            result.recommendations.append("Excellent ownership evidence")
            result.next_actions.append("Proceed with full confidence")
        
        # Method-specific recommendations
        for method, score in method_scores.items():
            if score < 0.5:  # Failed method
                if method == VerificationMethod.BLOCKCHAIN_PROOF:
                    result.recommendations.append("Consider blockchain timestamping for future content")
                elif method == VerificationMethod.COPYRIGHT_REGISTRY:
                    result.recommendations.append("Consider formal copyright registration")
                elif method == VerificationMethod.DIGITAL_SIGNATURE:
                    result.recommendations.append("Use digital signatures for content authentication")
        
        # Conflicting claims handling
        if result.conflicting_claims:
            result.legal_risks.append("Multiple ownership claims detected")
            result.next_actions.append("Review conflicting claims before proceeding")
    
    # Helper methods for specific verifications
    async def _extract_blockchain_evidence(self, claim: CopyrightClaim) -> Optional[OwnershipEvidence]:
        """Extract blockchain evidence"""
        try:
            if claim.blockchain_hash:
                blockchain_data = await self.blockchain_client.get_transaction_details(
                    claim.blockchain_hash
                )
                
                if blockchain_data:
                    return OwnershipEvidence(
                        evidence_id=f"blockchain_{claim.blockchain_hash}",
                        evidence_type="blockchain_proof",
                        content=json.dumps(blockchain_data),
                        metadata={"hash": claim.blockchain_hash},
                        verification_score=0.0,  # Will be calculated later
                        created_at=datetime.fromtimestamp(blockchain_data.get("timestamp", 0))
                    )
        except Exception as e:
            self.logger.error(f"Blockchain evidence extraction failed: {str(e)}")
        
        return None
    
    async def _extract_signature_evidence(self, claim: CopyrightClaim) -> Optional[OwnershipEvidence]:
        """Extract digital signature evidence"""
        try:
            if claim.digital_signature:
                signature_data = await self.signature_validator.extract_signature_data(
                    claim.digital_signature
                )
                
                if signature_data:
                    return OwnershipEvidence(
                        evidence_id=f"signature_{hashlib.md5(claim.digital_signature.encode()).hexdigest()}",
                        evidence_type="digital_signature",
                        content=json.dumps(signature_data),
                        metadata={"signature": claim.digital_signature},
                        verification_score=0.0,
                        created_at=signature_data.get("timestamp", datetime.now())
                    )
        except Exception as e:
            self.logger.error(f"Signature evidence extraction failed: {str(e)}")
        
        return None
    
    async def _extract_registry_evidence(self, claim: CopyrightClaim) -> List[OwnershipEvidence]:
        """Extract copyright registry evidence"""
        evidence_list = []
        
        try:
            for registry_name, registry_config in self.copyright_registries.items():
                try:
                    registration_data = await self.registry_client.get_registration_details(
                        registry_config,
                        claim.registration_number
                    )
                    
                    if registration_data:
                        evidence = OwnershipEvidence(
                            evidence_id=f"registry_{registry_name}_{claim.registration_number}",
                            evidence_type="copyright_registry",
                            content=json.dumps(registration_data),
                            metadata={"registry": registry_name, "registration": claim.registration_number},
                            verification_score=0.0,
                            created_at=registration_data.get("registration_date", datetime.now())
                        )
                        evidence_list.append(evidence)
                        
                except Exception as e:
                    self.logger.warning(f"Registry {registry_name} evidence extraction failed: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Registry evidence extraction failed: {str(e)}")
        
        return evidence_list
    
    async def _extract_file_evidence(self, evidence_files: List[Dict[str, Any]]) -> List[OwnershipEvidence]:
        """Extract evidence from uploaded files"""
        evidence_list = []
        
        for file_info in evidence_files:
            try:
                evidence = OwnershipEvidence(
                    evidence_id=f"file_{uuid.uuid4()}",
                    evidence_type=file_info.get("type", "legal_documentation"),
                    content=file_info.get("content", ""),
                    metadata=file_info.get("metadata", {}),
                    verification_score=0.0,
                    created_at=datetime.now()
                )
                evidence_list.append(evidence)
                
            except Exception as e:
                self.logger.warning(f"File evidence extraction failed: {str(e)}")
                continue
        
        return evidence_list
    
    async def _extract_platform_evidence(self, claim: CopyrightClaim) -> List[OwnershipEvidence]:
        """Extract platform metadata evidence"""
        # This would integrate with various platforms to gather metadata
        # Placeholder implementation
        return []
    
    # Additional helper methods
    async def _calculate_registration_match(
        self,
        claim: CopyrightClaim,
        registration_data: Dict[str, Any]
    ) -> float:
        """Calculate how well registration data matches claim"""
        score = 0.0
        
        # Check name match
        registered_name = registration_data.get("owner_name", "").lower()
        claim_name = claim.claimant_name.lower()
        
        if registered_name == claim_name:
            score += 0.4
        elif registered_name in claim_name or claim_name in registered_name:
            score += 0.2
        
        # Check content match
        registered_title = registration_data.get("work_title", "").lower()
        # This would compare with actual content metadata
        
        return min(score, 1.0)
    
    def _generate_cache_key(self, claim: CopyrightClaim) -> str:
        """Generate cache key for verification result"""
        key_data = f"{claim.claim_id}:{claim.content_id}:{claim.claimant_email}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_verification(self, cache_key: str) -> Optional[VerificationResult]:
        """Get cached verification result"""
        if cache_key in self.verification_cache:
            cached_data = self.verification_cache[cache_key]
            if cached_data["expires_at"] > datetime.now():
                return cached_data["result"]
        return None
    
    async def _cache_verification_result(self, cache_key: str, result: VerificationResult) -> None:
        """Cache verification result"""
        self.verification_cache[cache_key] = {
            "result": result,
            "expires_at": datetime.now() + timedelta(seconds=self.cache_ttl)
        }
    
    # Additional verification helper methods (simplified for brevity)
    async def _check_uploader_match(self, metadata: Dict[str, Any], claimant_email: str) -> float:
        """Check if metadata uploader matches claimant"""
        return 0.8 if metadata.get("uploader_email") == claimant_email else 0.0
    
    async def _check_metadata_timestamp(self, metadata: Dict[str, Any], creation_date: datetime) -> float:
        """Check metadata timestamp consistency"""
        return 0.7  # Placeholder
    
    async def _check_verification_badges(self, metadata: Dict[str, Any]) -> float:
        """Check for platform verification badges"""
        return 0.5 if metadata.get("verified_account") else 0.0
    
    async def _analyze_legal_document(self, doc_data: Dict[str, Any], claim: CopyrightClaim) -> float:
        """Analyze legal document authenticity and relevance"""
        return 0.6  # Placeholder
    
    async def _watermark_contains_owner_info(self, watermark_data: Dict[str, Any], claim: CopyrightClaim) -> bool:
        """Check if watermark contains owner information"""
        return False  # Placeholder
    
    async def _calculate_fingerprint_similarity(self, fingerprint_data: Dict[str, Any], content_id: str) -> float:
        """Calculate fingerprint similarity"""
        return 0.9  # Placeholder
    
    async def batch_verify_claims(
        self,
        claims: List[CopyrightClaim],
        evidence_files_list: Optional[List[List[Dict[str, Any]]]] = None
    ) -> List[VerificationResult]:
        """Batch verify multiple copyright claims"""
        max_concurrent = 10
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def verify_single(claim, evidence_files):
            async with semaphore:
                return await self.verify_copyright_ownership(claim, evidence_files)
        
        # Prepare evidence files for each claim
        if evidence_files_list is None:
            evidence_files_list = [None] * len(claims)
        
        tasks = [
            verify_single(claim, evidence_files)
            for claim, evidence_files in zip(claims, evidence_files_list)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch verification failed for claim {i}: {str(result)}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification system statistics"""
        try:
            with get_db_session() as session:
                total_verifications = session.query(CopyrightRecord).count()
                successful_verifications = session.query(CopyrightRecord).filter(
                    CopyrightRecord.verification_status == VerificationStatus.VERIFIED
                ).count()
                
                success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
                
                return {
                    "total_verifications": total_verifications,
                    "successful_verifications": successful_verifications,
                    "success_rate": success_rate,
                    "cache_size": len(self.verification_cache),
                    "supported_methods": len(self.method_weights),
                    "supported_registries": len(self.copyright_registries)
                }
                
        except Exception as e:
            self.logger.error(f"Statistics generation failed: {str(e)}")
            return {}
