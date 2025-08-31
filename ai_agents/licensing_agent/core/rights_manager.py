"""Rights Manager - Comprehensive Digital Rights Management System

Advanced rights management, ownership tracking, and copyright protection system
for multi-format content across all digital platforms and territories.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal

try:
    from core.exceptions import RightsError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    RightsError, ValidationError = globals().get('RightsError, ValidationError', Exception)
from ...database.models import Content, Rights, Ownership, Territory
from ...integrations.copyright.registries import CopyrightRegistryAPI
from ...integrations.blockchain.rights_chain import RightsBlockchain
from ...utils.territory_validator import TerritoryValidator
from ...security.rights_encryption import RightsEncryption

logger = logging.getLogger(__name__)

class RightsType(Enum):
    """Types of content rights"""    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    SYNCHRONIZATION = "synchronization"
    MASTER = "master"
    PUBLISHING = "publishing"
    DISTRIBUTION = "distribution"
    REPRODUCTION = "reproduction"
    PUBLIC_DISPLAY = "public_display"
    DIGITAL_TRANSMISSION = "digital_transmission"
    MORAL_RIGHTS = "moral_rights"
    NEIGHBORING_RIGHTS = "neighboring_rights"

class OwnershipType(Enum):
    """Types of ownership structures"""    SOLE = "sole"
    JOINT = "joint"
    COLLECTIVE = "collective"
    CORPORATE = "corporate"
    ESTATE = "estate"
    TRUST = "trust"
    SOCIETY = "collecting_society"

class RightsStatus(Enum):
    """Rights registration status"""    PENDING = "pending"
    REGISTERED = "registered"
    RENEWED = "renewed"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    TRANSFERRED = "transferred"
    REVOKED = "revoked"

class TerritoryScope(Enum):
    """Territory scope definitions"""    WORLDWIDE = "worldwide"
    REGIONAL = "regional"
    NATIONAL = "national"
    SUBNATIONAL = "subnational"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"

@dataclass
class RightsOwner:
    """Rights owner information"""    owner_id: str
    name: str
    email: str
    ownership_percentage: Decimal
    ownership_type: OwnershipType
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    contact_info: Dict[str, Any] = field(default_factory=dict)
    legal_entity_type: str = "individual"
    tax_id: Optional[str] = None
    address: Dict[str, str] = field(default_factory=dict)

@dataclass
class RightsRecord:
    """Comprehensive rights record"""    rights_id: str
    content_id: str
    rights_type: RightsType
    owners: List[RightsOwner]
    territory: List[str]
    territory_scope: TerritoryScope
    status: RightsStatus
    registration_date: datetime
    expiry_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    registration_number: Optional[str] = None
    registrar: Optional[str] = None
    previous_owners: List[RightsOwner] = field(default_factory=list)
    encumbrances: List[Dict[str, Any]] = field(default_factory=list)
    blockchain_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RightsTransfer:
    """Rights transfer record"""    transfer_id: str
    rights_id: str
    from_owner: RightsOwner
    to_owner: RightsOwner
    transfer_type: str  # "assignment", "license", "inheritance", "sale"
    percentage_transferred: Decimal
    effective_date: datetime
    consideration: Optional[Decimal] = None
    conditions: List[str] = field(default_factory=list)
    legal_documents: List[str] = field(default_factory=list)
    blockchain_tx: Optional[str] = None

class RightsManager:
    """    Ultra-Advanced Digital Rights Management System
    
    Provides comprehensive rights tracking, ownership verification, and blockchain-secured
    rights management for all content types across global territories.
    """    
    def __init__(self):
        self.copyright_registry = CopyrightRegistryAPI()
        self.rights_blockchain = RightsBlockchain()
        self.territory_validator = TerritoryValidator()
        self.rights_encryption = RightsEncryption()
        
        # Performance metrics
        self.metrics = {
            "rights_registered": 0,
            "ownership_verified": 0,
            "transfers_processed": 0,
            "disputes_resolved": 0
        }

    async def register_rights(
        self,
        content_id: str,
        rights_type: RightsType,
        owners: List[RightsOwner],
        territory: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Register comprehensive rights for content with blockchain verification
        
        Args:
            content_id: Content identifier
            rights_type: Type of rights to register
            owners: List of rights owners
            territory: Territory coverage
            metadata: Additional rights metadata
            
        Returns:
            Registration result with blockchain verification
        """        try:
            # Validate ownership percentages
            total_percentage = sum(owner.ownership_percentage for owner in owners)
            if total_percentage != Decimal("100.0"):
                raise ValidationError(f"Ownership percentages must total 100%, got {total_percentage}%")
            
            # Validate territories
            territory_validation = await self.territory_validator.validate_territories(territory)
            if not territory_validation["valid"]:
                raise ValidationError(f"Invalid territories: {territory_validation['errors']}")
            
            # Create rights record
            rights_record = RightsRecord(
                rights_id=str(uuid.uuid4()),
                content_id=content_id,
                rights_type=rights_type,
                owners=owners,
                territory=territory,
                territory_scope=self._determine_territory_scope(territory),
                status=RightsStatus.PENDING,
                registration_date=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Register with copyright authorities
            if rights_type in [RightsType.COPYRIGHT, RightsType.PUBLISHING]:
                registry_result = await self._register_with_copyright_office(rights_record)
                rights_record.registration_number = registry_result.get("registration_number")
                rights_record.registrar = registry_result.get("registrar")
            
            # Create blockchain record
            blockchain_result = await self.rights_blockchain.create_rights_record(rights_record)
            rights_record.blockchain_hash = blockchain_result["transaction_hash"]
            rights_record.status = RightsStatus.REGISTERED
            
            # Store encrypted record
            encrypted_record = await self.rights_encryption.encrypt_rights_record(rights_record)
            await self._store_rights_record(encrypted_record)
            
            # Update metrics
            self.metrics["rights_registered"] += 1
            
            return {
                "success": True,
                "rights_id": rights_record.rights_id,
                "registration_number": rights_record.registration_number,
                "blockchain_hash": rights_record.blockchain_hash,
                "status": rights_record.status.value,
                "territory_scope": rights_record.territory_scope.value
            }
            
        except Exception as e:
            logger.error(f"Error registering rights: {str(e)}")
            raise RightsError(f"Rights registration failed: {str(e)}")

    async def verify_ownership(
        self,
        content_id: str,
        claimed_owner: str,
        rights_type: Optional[RightsType] = None
    ) -> Dict[str, Any]:
        """        Verify ownership claims with multi-source validation
        
        Args:
            content_id: Content to verify ownership for
            claimed_owner: ID of claimed owner
            rights_type: Specific rights type to verify
            
        Returns:
            Ownership verification result
        """        try:
            # Get all rights records for content
            rights_records = await self._get_content_rights(content_id)
            
            verification_results = []
            total_ownership = Decimal("0.0")
            
            for record in rights_records:
                if rights_type and record.rights_type != rights_type:
                    continue
                    
                # Check if claimed owner is in this record
                for owner in record.owners:
                    if owner.owner_id == claimed_owner:
                        # Verify blockchain record
                        blockchain_valid = await self.rights_blockchain.verify_ownership(
                            record.blockchain_hash,
                            claimed_owner,
                            owner.ownership_percentage
                        )
                        
                        verification_results.append({
                            "rights_id": record.rights_id,
                            "rights_type": record.rights_type.value,
                            "ownership_percentage": float(owner.ownership_percentage),
                            "blockchain_verified": blockchain_valid,
                            "registration_verified": bool(record.registration_number),
                            "territory": record.territory,
                            "status": record.status.value
                        })
                        
                        total_ownership += owner.ownership_percentage
            
            # Overall verification status
            is_verified = (
                len(verification_results) > 0 and
                all(result["blockchain_verified"] for result in verification_results) and
                total_ownership > Decimal("0.0")
            )
            
            # Update metrics
            if is_verified:
                self.metrics["ownership_verified"] += 1
            
            return {
                "verified": is_verified,
                "total_ownership_percentage": float(total_ownership),
                "verification_details": verification_results,
                "verification_date": datetime.utcnow(),
                "confidence_score": self._calculate_confidence_score(verification_results)
            }
            
        except Exception as e:
            logger.error(f"Error verifying ownership: {str(e)}")
            raise RightsError(f"Ownership verification failed: {str(e)}")

    async def transfer_rights(
        self,
        rights_transfer: RightsTransfer
    ) -> Dict[str, Any]:
        """        Execute secure rights transfer with legal documentation
        
        Args:
            rights_transfer: Transfer details
            
        Returns:
            Transfer execution result
        """        try:
            # Validate transfer
            validation_result = await self._validate_rights_transfer(rights_transfer)
            if not validation_result["valid"]:
                raise ValidationError(f"Transfer validation failed: {validation_result['errors']}")
            
            # Get current rights record
            current_rights = await self._get_rights_by_id(rights_transfer.rights_id)
            if not current_rights:
                raise RightsError("Rights record not found")
            
            # Create transfer on blockchain
            blockchain_transfer = await self.rights_blockchain.execute_transfer(rights_transfer)
            rights_transfer.blockchain_tx = blockchain_transfer["transaction_id"]
            
            # Update ownership structure
            updated_owners = await self._update_ownership_structure(
                current_rights.owners,
                rights_transfer
            )
            
            # Create new rights record with updated ownership
            new_rights_record = RightsRecord(
                rights_id=str(uuid.uuid4()),
                content_id=current_rights.content_id,
                rights_type=current_rights.rights_type,
                owners=updated_owners,
                territory=current_rights.territory,
                territory_scope=current_rights.territory_scope,
                status=RightsStatus.TRANSFERRED,
                registration_date=datetime.utcnow(),
                previous_owners=current_rights.owners,
                metadata={
                    **current_rights.metadata,
                    "transfer_history": current_rights.metadata.get("transfer_history", []) + [
                        {
                            "transfer_id": rights_transfer.transfer_id,
                            "date": rights_transfer.effective_date,
                            "type": rights_transfer.transfer_type
                        }
                    ]
                }
            )
            
            # Register new record on blockchain
            blockchain_result = await self.rights_blockchain.create_rights_record(new_rights_record)
            new_rights_record.blockchain_hash = blockchain_result["transaction_hash"]
            
            # Store updated record
            encrypted_record = await self.rights_encryption.encrypt_rights_record(new_rights_record)
            await self._store_rights_record(encrypted_record)
            
            # Generate transfer documentation
            transfer_docs = await self._generate_transfer_documentation(rights_transfer, new_rights_record)
            
            # Send notifications to all parties
            await self._send_transfer_notifications(rights_transfer, new_rights_record)
            
            # Update metrics
            self.metrics["transfers_processed"] += 1
            
            return {
                "success": True,
                "transfer_id": rights_transfer.transfer_id,
                "new_rights_id": new_rights_record.rights_id,
                "blockchain_tx": rights_transfer.blockchain_tx,
                "blockchain_hash": new_rights_record.blockchain_hash,
                "transfer_documents": transfer_docs,
                "effective_date": rights_transfer.effective_date
            }
            
        except Exception as e:
            logger.error(f"Error transferring rights: {str(e)}")
            raise RightsError(f"Rights transfer failed: {str(e)}")

    async def resolve_rights_dispute(
        self,
        dispute_id: str,
        evidence: Dict[str, Any],
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Resolve rights disputes with blockchain-verified evidence
        
        Args:
            dispute_id: Dispute identifier
            evidence: Evidence supporting resolution
            resolution: Dispute resolution details
            
        Returns:
            Dispute resolution result
        """        try:
            # Get dispute details
            dispute = await self._get_dispute_by_id(dispute_id)
            if not dispute:
                raise RightsError("Dispute not found")
            
            # Validate evidence on blockchain
            evidence_validation = await self.rights_blockchain.validate_evidence(evidence)
            if not evidence_validation["valid"]:
                raise ValidationError("Evidence validation failed")
            
            # Apply resolution
            if resolution["action"] == "ownership_change":
                # Execute ownership change
                transfer_result = await self._execute_dispute_resolution_transfer(
                    dispute,
                    resolution
                )
                resolution["transfer_result"] = transfer_result
            
            elif resolution["action"] == "rights_split":
                # Split rights between parties
                split_result = await self._execute_rights_split(dispute, resolution)
                resolution["split_result"] = split_result
            
            elif resolution["action"] == "compensation":
                # Arrange compensation
                compensation_result = await self._execute_compensation(dispute, resolution)
                resolution["compensation_result"] = compensation_result
            
            # Record resolution on blockchain
            resolution_record = await self.rights_blockchain.record_dispute_resolution(
                dispute_id,
                evidence,
                resolution
            )
            
            # Update dispute status
            await self._update_dispute_status(dispute_id, "resolved", resolution)
            
            # Generate resolution documentation
            resolution_docs = await self._generate_resolution_documentation(
                dispute,
                evidence,
                resolution
            )
            
            # Send notifications
            await self._send_resolution_notifications(dispute, resolution)
            
            # Update metrics
            self.metrics["disputes_resolved"] += 1
            
            return {
                "success": True,
                "dispute_id": dispute_id,
                "resolution_action": resolution["action"],
                "blockchain_record": resolution_record["transaction_hash"],
                "resolution_documents": resolution_docs,
                "resolution_date": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error resolving dispute: {str(e)}")
            raise RightsError(f"Dispute resolution failed: {str(e)}")

    def _determine_territory_scope(self, territories: List[str]) -> TerritoryScope:
        """Determine territory scope based on coverage"""        if "WORLDWIDE" in territories or len(territories) > 50:
            return TerritoryScope.WORLDWIDE
        elif len(territories) > 10:
            return TerritoryScope.REGIONAL
        else:
            return TerritoryScope.NATIONAL

    async def _register_with_copyright_office(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Register rights with relevant copyright offices"""        registration_results = []
        
        for territory in rights_record.territory:
            if territory in self.copyright_registry.supported_territories:
                result = await self.copyright_registry.register_copyright(
                    content_id=rights_record.content_id,
                    rights_type=rights_record.rights_type.value,
                    owners=[owner.__dict__ for owner in rights_record.owners],
                    territory=territory
                )
                registration_results.append(result)
        
        # Return primary registration
        primary_registration = registration_results[0] if registration_results else {}
        return {
            "registration_number": primary_registration.get("registration_number"),
            "registrar": primary_registration.get("registrar"),
            "all_registrations": registration_results
        }

    async def _validate_rights_transfer(self, transfer: RightsTransfer) -> Dict[str, Any]:
        """Validate rights transfer parameters"""        errors = []
        
        # Validate ownership percentage
        if transfer.percentage_transferred <= 0 or transfer.percentage_transferred > 100:
            errors.append("Invalid ownership percentage")
        
        # Validate effective date
        if transfer.effective_date < datetime.utcnow():
            errors.append("Effective date cannot be in the past")
        
        # Validate transfer type
        valid_types = ["assignment", "license", "inheritance", "sale", "gift"]
        if transfer.transfer_type not in valid_types:
            errors.append(f"Invalid transfer type: {transfer.transfer_type}")
        
        return {"valid": len(errors) == 0, "errors": errors}

    async def _update_ownership_structure(
        self,
        current_owners: List[RightsOwner],
        transfer: RightsTransfer
    ) -> List[RightsOwner]:
        """Update ownership structure after transfer"""        updated_owners = []
        
        for owner in current_owners:
            if owner.owner_id == transfer.from_owner.owner_id:
                # Reduce transferring owner's percentage
                new_percentage = owner.ownership_percentage - transfer.percentage_transferred
                if new_percentage > 0:
                    owner.ownership_percentage = new_percentage
                    updated_owners.append(owner)
                # Note: If percentage becomes 0, owner is removed
            else:
                updated_owners.append(owner)
        
        # Add or update receiving owner
        receiving_owner_found = False
        for owner in updated_owners:
            if owner.owner_id == transfer.to_owner.owner_id:
                owner.ownership_percentage += transfer.percentage_transferred
                receiving_owner_found = True
                break
        
        if not receiving_owner_found:
            transfer.to_owner.ownership_percentage = transfer.percentage_transferred
            updated_owners.append(transfer.to_owner)
        
        return updated_owners

    def _calculate_confidence_score(self, verification_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for ownership verification"""        if not verification_results:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        for result in verification_results:
            weight = float(result["ownership_percentage"]) / 100.0
            
            # Blockchain verification adds high confidence
            if result["blockchain_verified"]:
                score += 0.8 * weight
            
            # Registration verification adds medium confidence
            if result["registration_verified"]:
                score += 0.6 * weight
            
            # Active status adds confidence
            if result["status"] in ["registered", "active"]:
                score += 0.4 * weight
            
            total_weight += weight
        
        return min(score / total_weight if total_weight > 0 else 0.0, 1.0)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get rights management metrics"""        return {
            **self.metrics,
            "timestamp": datetime.utcnow(),
            "blockchain_sync_status": await self.rights_blockchain.get_sync_status(),
            "registry_connections": await self.copyright_registry.get_connection_status()
        }


class CopyrightProtector:
    """    Advanced copyright protection and infringement detection system
    """    
    def __init__(self):
        self.rights_manager = RightsManager()
        
    async def detect_infringement(
        self,
        content_id: str,
        suspected_infringement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Detect and analyze potential copyright infringement
        
        Args:
            content_id: Original content ID
            suspected_infringement: Details of suspected infringement
            
        Returns:
            Infringement analysis result
        """        try:
            # Verify original rights
            rights_verification = await self.rights_manager.verify_ownership(
                content_id,
                suspected_infringement.get("claimed_owner_id", "")
            )
            
            if not rights_verification["verified"]:
                return {
                    "infringement_detected": True,
                    "confidence": 0.95,
                    "reason": "No verified ownership of original content",
                    "recommended_action": "immediate_takedown"
                }
            
            # Analyze similarity and usage context
            similarity_score = await self._calculate_similarity_score(
                content_id,
                suspected_infringement
            )
            
            usage_analysis = await self._analyze_usage_context(suspected_infringement)
            
            # Determine infringement probability
            infringement_probability = self._calculate_infringement_probability(
                similarity_score,
                usage_analysis,
                rights_verification
            )
            
            return {
                "infringement_detected": infringement_probability > 0.7,
                "confidence": infringement_probability,
                "similarity_score": similarity_score,
                "usage_analysis": usage_analysis,
                "rights_verification": rights_verification,
                "recommended_action": self._determine_recommended_action(infringement_probability)
            }
            
        except Exception as e:
            logger.error(f"Error detecting infringement: {str(e)}")
            raise RightsError(f"Infringement detection failed: {str(e)}")

    async def _calculate_similarity_score(
        self,
        original_content_id: str,
        suspected_content: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive content similarity score using advanced AI algorithms"""        try:
            # Get original content fingerprint and metadata
            original_fingerprint = await self._get_content_fingerprint(original_content_id)
            if not original_fingerprint:
                logger.warning(f"Could not retrieve fingerprint for original content {original_content_id}")
                return 0.0
                
            # Determine content type for appropriate similarity analysis
            content_type = suspected_content.get("content_type", "unknown")
            similarity_scores = {}
            
            # Audio content similarity
            if content_type in ["audio", "music", "sound"]:
                audio_similarity = await self._calculate_audio_similarity(
                    original_fingerprint["audio"], 
                    suspected_content.get("audio_fingerprint", {})
                )
                similarity_scores["audio"] = audio_similarity
                
            # Visual content similarity  
            if content_type in ["image", "video", "visual"]:
                visual_similarity = await self._calculate_visual_similarity(
                    original_fingerprint["visual"],
                    suspected_content.get("visual_fingerprint", {})
                )
                similarity_scores["visual"] = visual_similarity
                
            # Text content similarity
            if content_type in ["text", "lyrics", "script"]:
                text_similarity = await self._calculate_text_similarity(
                    original_fingerprint["text"],
                    suspected_content.get("text_content", "")
                )
                similarity_scores["text"] = text_similarity
                
            # Metadata similarity (titles, descriptions, tags)
            metadata_similarity = await self._calculate_metadata_similarity(
                original_fingerprint["metadata"],
                suspected_content.get("metadata", {})
            )
            similarity_scores["metadata"] = metadata_similarity
            
            # Calculate weighted overall similarity
            weights = {
                "audio": 0.4,
                "visual": 0.3, 
                "text": 0.2,
                "metadata": 0.1
            }
            
            # Only use weights for available similarity scores
            available_scores = {k: v for k, v in similarity_scores.items() if v is not None}
            if not available_scores:
                return 0.0
                
            # Normalize weights based on available scores
            total_weight = sum(weights[k] for k in available_scores.keys() if k in weights)
            normalized_weights = {k: weights.get(k, 0) / total_weight for k in available_scores.keys()}
            
            # Calculate weighted similarity
            overall_similarity = sum(
                score * normalized_weights.get(score_type, 0) 
                for score_type, score in available_scores.items()
            )
            
            # Apply confidence adjustments based on content quality and completeness
            confidence_factor = self._calculate_confidence_factor(
                original_fingerprint, suspected_content
            )
            
            adjusted_similarity = overall_similarity * confidence_factor
            
            # Log similarity calculation details for audit
            logger.info(f"Content similarity calculated: {adjusted_similarity:.3f} (raw: {overall_similarity:.3f}, confidence: {confidence_factor:.3f})")
            
            return min(max(adjusted_similarity, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating similarity score: {str(e)}")
            return 0.0

    async def _analyze_usage_context(self, suspected_infringement: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the context of suspected infringing usage"""        return {
            "commercial_use": suspected_infringement.get("is_commercial", False),
            "attribution_provided": suspected_infringement.get("has_attribution", False),
            "platform": suspected_infringement.get("platform", "unknown"),
            "audience_size": suspected_infringement.get("audience_size", 0),
            "revenue_generated": suspected_infringement.get("revenue", 0)
        }

    def _calculate_infringement_probability(
        self,
        similarity_score: float,
        usage_analysis: Dict[str, Any],
        rights_verification: Dict[str, Any]
    ) -> float:
        """Calculate probability of infringement"""        base_probability = similarity_score
        
        # Adjust based on usage context
        if usage_analysis["commercial_use"]:
            base_probability += 0.2
        
        if not usage_analysis["attribution_provided"]:
            base_probability += 0.1
        
        if usage_analysis["revenue_generated"] > 0:
            base_probability += 0.15
        
        # Adjust based on rights verification
        if rights_verification["verified"]:
            base_probability += 0.1
        
        return min(base_probability, 1.0)

    def _determine_recommended_action(self, probability: float) -> str:
        """Determine recommended action based on infringement probability"""        if probability > 0.9:
            return "immediate_legal_action"
        elif probability > 0.7:
            return "takedown_notice"
        elif probability > 0.5:
            return "warning_notice"
        else:
            return "monitor"

class RightsStatus(Enum):
    """Status of rights"""    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    TRANSFERRED = "transferred"
    REVOKED = "revoked"

@dataclass
class RightsOwnership:
    """Rights ownership information"""    owner_id: str
    owner_name: str
    owner_type: str  # individual, company, organization
    ownership_percentage: Decimal
    ownership_type: OwnershipType
    rights_types: List[RightsType]
    territories: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    registration_number: Optional[str] = None
    documentation: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RightsRecord:
    """Complete rights record for content"""    content_id: str
    content_type: str
    rights_id: str
    title: str
    creators: List[str]
    ownerships: List[RightsOwnership]
    rights_chain: List[Dict[str, Any]]
    registration_info: Dict[str, Any]
    territorial_rights: Dict[str, List[RightsType]]
    status: RightsStatus
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class RightsManager:
    """    Comprehensive Digital Rights Management System
    
    Manages all aspects of digital rights including ownership tracking,
    territorial rights, copyright registration, and rights chain documentation.
    """    
    def __init__(self):
        self.copyright_api = CopyrightRegistryAPI()
        self.rights_blockchain = RightsBlockchain()
        self.territory_validator = TerritoryValidator()
        self.rights_encryption = RightsEncryption()
        
        # Rights databases
        self.rights_registry = {}
        self.ownership_chain = {}
        self.territorial_rights = {}
        
        # Performance metrics
        self.metrics = {
            "rights_registered": 0,
            "ownership_transfers": 0,
            "copyright_registrations": 0,
            "disputes_resolved": 0
        }

    async def register_content_rights(
        self,
        content_id: str,
        content_metadata: Dict[str, Any],
        initial_ownership: List[RightsOwnership]
    ) -> Dict[str, Any]:
        """        Register comprehensive rights for content
        
        Args:
            content_id: Content identifier
            content_metadata: Content information and metadata
            initial_ownership: Initial ownership structure
            
        Returns:
            Complete rights registration result
        """        try:
            # Validate content and ownership data
            validation_result = await self._validate_rights_data(content_metadata, initial_ownership)
            if not validation_result["valid"]:
                raise RightsError(f"Rights validation failed: {validation_result['errors']}")
            
            # Generate rights record
            rights_record = RightsRecord(
                content_id=content_id,
                content_type=content_metadata.get("type", "unknown"),
                rights_id=str(uuid.uuid4()),
                title=content_metadata.get("title", "Unknown"),
                creators=content_metadata.get("creators", []),
                ownerships=initial_ownership,
                rights_chain=[{
                    "action": "initial_registration",
                    "timestamp": datetime.utcnow(),
                    "details": {"registered_by": "system"}
                }],
                registration_info={},
                territorial_rights=await self._calculate_territorial_rights(initial_ownership),
                status=RightsStatus.PENDING,
                metadata=content_metadata
            )
            
            # Register with copyright authorities
            copyright_result = await self._register_copyright(rights_record)
            rights_record.registration_info.update(copyright_result)
            
            # Record on blockchain
            blockchain_result = await self._record_on_blockchain(rights_record)
            rights_record.metadata["blockchain_tx"] = blockchain_result["transaction_id"]
            
            # Store rights record
            self.rights_registry[rights_record.rights_id] = rights_record
            self.ownership_chain[content_id] = rights_record.rights_id
            
            # Update territorial rights index
            await self._update_territorial_index(rights_record)
            
            # Set status to active
            rights_record.status = RightsStatus.ACTIVE
            rights_record.updated_at = datetime.utcnow()
            
            # Update metrics
            self.metrics["rights_registered"] += 1
            
            return {
                "success": True,
                "rights_id": rights_record.rights_id,
                "copyright_registration": copyright_result,
                "blockchain_transaction": blockchain_result["transaction_id"],
                "territorial_coverage": list(rights_record.territorial_rights.keys())
            }
            
        except Exception as e:
            logger.error(f"Error registering content rights: {str(e)}")
            raise RightsError(f"Failed to register rights: {str(e)}")

    async def transfer_ownership(
        self,
        rights_id: str,
        transfer_details: Dict[str, Any],
        authorization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Transfer ownership of rights between parties
        
        Args:
            rights_id: Rights record identifier
            transfer_details: Transfer information
            authorization: Authorization and signatures
            
        Returns:
            Transfer completion result
        """        try:
            # Get existing rights record
            rights_record = self.rights_registry.get(rights_id)
            if not rights_record:
                raise RightsError(f"Rights record not found: {rights_id}")
            
            # Validate transfer authorization
            auth_result = await self._validate_transfer_authorization(rights_record, authorization)
            if not auth_result["valid"]:
                raise RightsError(f"Transfer authorization failed: {auth_result['errors']}")
            
            # Process ownership transfer
            transfer_result = await self._execute_ownership_transfer(
                rights_record, 
                transfer_details, 
                authorization
            )
            
            # Update rights chain
            rights_record.rights_chain.append({
                "action": "ownership_transfer",
                "timestamp": datetime.utcnow(),
                "from_owner": transfer_details["from_owner_id"],
                "to_owner": transfer_details["to_owner_id"],
                "percentage": transfer_details.get("percentage", 100.0),
                "consideration": transfer_details.get("consideration"),
                "authorization_hash": authorization.get("signature_hash")
            })
            
            # Update territorial rights if needed
            if transfer_details.get("territories"):
                await self._update_territorial_rights(rights_record, transfer_details["territories"])
            
            # Record transfer on blockchain
            blockchain_result = await self._record_transfer_on_blockchain(
                rights_record, 
                transfer_result
            )
            
            # Notify copyright authorities
            await self._notify_copyright_transfer(rights_record, transfer_result)
            
            # Update record
            rights_record.updated_at = datetime.utcnow()
            
            # Update metrics
            self.metrics["ownership_transfers"] += 1
            
            return {
                "success": True,
                "transfer_id": transfer_result["transfer_id"],
                "blockchain_transaction": blockchain_result["transaction_id"],
                "new_ownership_structure": [own.__dict__ for own in rights_record.ownerships],
                "effective_date": transfer_result["effective_date"]
            }
            
        except Exception as e:
            logger.error(f"Error transferring ownership: {str(e)}")
            raise RightsError(f"Failed to transfer ownership: {str(e)}")

    async def verify_rights_ownership(
        self,
        content_id: str,
        claiming_party: str,
        rights_types: List[RightsType],
        territory: str = None
    ) -> Dict[str, Any]:
        """        Verify rights ownership for specific party and usage
        
        Args:
            content_id: Content identifier
            claiming_party: Party claiming rights
            rights_types: Types of rights being claimed
            territory: Specific territory (optional)
            
        Returns:
            Verification result with ownership details
        """        try:
            # Get rights record
            rights_id = self.ownership_chain.get(content_id)
            if not rights_id:
                return {
                    "verified": False,
                    "reason": "No rights record found for content"
                }
            
            rights_record = self.rights_registry[rights_id]
            
            # Check ownership for each rights type
            ownership_details = {}
            verified_rights = []
            
            for rights_type in rights_types:
                ownership = await self._check_rights_ownership(
                    rights_record,
                    claiming_party,
                    rights_type,
                    territory
                )
                
                if ownership["owns_rights"]:
                    verified_rights.append(rights_type)
                    ownership_details[rights_type.value] = ownership
            
            # Calculate overall verification result
            verification_score = len(verified_rights) / len(rights_types) if rights_types else 0
            
            return {
                "verified": verification_score >= 1.0,  # All rights must be owned
                "partial_rights": verification_score > 0 and verification_score < 1.0,
                "verification_score": verification_score,
                "verified_rights": [rt.value for rt in verified_rights],
                "ownership_details": ownership_details,
                "rights_record_id": rights_id,
                "verification_timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error verifying rights ownership: {str(e)}")
            return {
                "verified": False,
                "error": str(e),
                "verification_timestamp": datetime.utcnow()
            }

    async def generate_rights_certificate(
        self,
        rights_id: str,
        certificate_type: str = "ownership"
    ) -> Dict[str, Any]:
        """        Generate official rights certificate
        
        Args:
            rights_id: Rights record identifier
            certificate_type: Type of certificate to generate
            
        Returns:
            Generated certificate data
        """        try:
            rights_record = self.rights_registry.get(rights_id)
            if not rights_record:
                raise RightsError(f"Rights record not found: {rights_id}")
            
            # Generate certificate data
            certificate_data = {
                "certificate_id": str(uuid.uuid4()),
                "certificate_type": certificate_type,
                "issued_to": "rights_holder",
                "content_id": rights_record.content_id,
                "content_title": rights_record.title,
                "rights_types": [rt.value for ownership in rights_record.ownerships for rt in ownership.rights_types],
                "territorial_coverage": list(rights_record.territorial_rights.keys()),
                "ownership_structure": [own.__dict__ for own in rights_record.ownerships],
                "registration_info": rights_record.registration_info,
                "issue_date": datetime.utcnow(),
                "valid_until": None,  # Permanent unless specified
                "issuing_authority": "IA Influencer Agent Rights Management System",
                "certificate_hash": None
            }
            
            # Generate certificate hash
            certificate_hash = await self._generate_certificate_hash(certificate_data)
            certificate_data["certificate_hash"] = certificate_hash
            
            # Sign certificate
            signature = await self.rights_encryption.sign_certificate(certificate_data)
            certificate_data["digital_signature"] = signature
            
            # Generate PDF certificate
            pdf_certificate = await self._generate_pdf_certificate(certificate_data)
            
            return {
                "success": True,
                "certificate": certificate_data,
                "pdf_content": pdf_certificate,
                "certificate_url": f"/certificates/{certificate_data['certificate_id']}.pdf"
            }
            
        except Exception as e:
            logger.error(f"Error generating rights certificate: {str(e)}")
            raise RightsError(f"Failed to generate certificate: {str(e)}")

    async def track_rights_usage(
        self,
        content_id: str,
        usage_details: Dict[str, Any],
        platform_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """        Track and record rights usage for royalty and compliance purposes
        
        Args:
            content_id: Content identifier
            usage_details: Details of content usage
            platform_info: Platform where content is used
            
        Returns:
            Usage tracking result
        """        try:
            # Get rights record
            rights_id = self.ownership_chain.get(content_id)
            if not rights_id:
                raise RightsError(f"No rights record found for content: {content_id}")
            
            rights_record = self.rights_registry[rights_id]
            
            # Validate usage against rights
            usage_validation = await self._validate_usage_rights(
                rights_record,
                usage_details,
                platform_info
            )
            
            if not usage_validation["authorized"]:
                return {
                    "success": False,
                    "authorized": False,
                    "violations": usage_validation["violations"],
                    "required_permissions": usage_validation["required_permissions"]
                }
            
            # Record usage
            usage_record = {
                "usage_id": str(uuid.uuid4()),
                "content_id": content_id,
                "rights_id": rights_id,
                "usage_type": usage_details["type"],
                "platform": platform_info["name"],
                "territory": usage_details.get("territory", "unknown"),
                "usage_metrics": usage_details.get("metrics", {}),
                "timestamp": datetime.utcnow(),
                "duration": usage_details.get("duration"),
                "audience_size": usage_details.get("audience_size"),
                "revenue_generated": usage_details.get("revenue", 0)
            }
            
            # Store usage record
            await self._store_usage_record(usage_record)
            
            # Calculate royalties if applicable
            royalty_calculation = None
            if usage_details.get("revenue", 0) > 0:
                royalty_calculation = await self._calculate_usage_royalties(
                    rights_record,
                    usage_record
                )
            
            return {
                "success": True,
                "authorized": True,
                "usage_id": usage_record["usage_id"],
                "royalties": royalty_calculation,
                "compliance_status": "compliant"
            }
            
        except Exception as e:
            logger.error(f"Error tracking rights usage: {str(e)}")
            raise RightsError(f"Failed to track usage: {str(e)}")

    async def _validate_rights_data(
        self,
        content_metadata: Dict[str, Any],
        ownership: List[RightsOwnership]
    ) -> Dict[str, Any]:
        """Validate rights registration data"""        errors = []
        
        # Comprehensive content validation with business logic
        if not content_metadata.get("title") or not content_metadata["title"].strip():
            errors.append("Content title is required and cannot be empty")
        
        if not content_metadata.get("creators") or not isinstance(content_metadata["creators"], list):
            errors.append("At least one creator must be specified in a valid list format")
        elif not any(creator.get("name") for creator in content_metadata["creators"]):
            errors.append("All creators must have valid names")
            
        # Validate content type and format
        if not content_metadata.get("content_type"):
            errors.append("Content type must be specified (audio, video, image, text, etc.)")
        
        # Validate creation date
        if not content_metadata.get("creation_date"):
            errors.append("Content creation date is required")
        elif isinstance(content_metadata["creation_date"], str):
            try:
                datetime.fromisoformat(content_metadata["creation_date"].replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid creation date format - use ISO format")
        
        # Validate duration/size depending on content type
        content_type = content_metadata.get("content_type", "").lower()
        if content_type in ["audio", "video"] and not content_metadata.get("duration_seconds"):
            errors.append("Duration is required for audio/video content")
        elif content_type == "image" and not content_metadata.get("dimensions"):
            errors.append("Image dimensions are required for image content")
        elif content_type == "text" and not content_metadata.get("word_count"):
            errors.append("Word count is required for text content")
        
        # Ownership validation
        if not ownership:
            errors.append("At least one ownership record is required")
        
        total_percentage = sum(own.ownership_percentage for own in ownership)
        if total_percentage != Decimal("100.0"):
            errors.append(f"Total ownership percentage must equal 100%, got {total_percentage}%")
        
        return {"valid": len(errors) == 0, "errors": errors}

    async def _calculate_territorial_rights(
        self,
        ownerships: List[RightsOwnership]
    ) -> Dict[str, List[RightsType]]:
        """Calculate territorial rights coverage"""        territorial_rights = {}
        
        for ownership in ownerships:
            for territory in ownership.territories:
                if territory not in territorial_rights:
                    territorial_rights[territory] = []
                territorial_rights[territory].extend(ownership.rights_types)
        
        # Remove duplicates
        for territory in territorial_rights:
            territorial_rights[territory] = list(set(territorial_rights[territory]))
        
        return territorial_rights

    async def _register_copyright(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Register copyright with relevant authorities"""        registration_data = {
            "title": rights_record.title,
            "creators": rights_record.creators,
            "content_type": rights_record.content_type,
            "creation_date": rights_record.metadata.get("creation_date"),
            "first_publication": rights_record.metadata.get("first_publication"),
            "territories": list(rights_record.territorial_rights.keys())
        }
        
        # Register with copyright authorities
        registrations = {}
        for territory in registration_data["territories"]:
            try:
                reg_result = await self.copyright_api.register_copyright(
                    territory, registration_data
                )
                registrations[territory] = reg_result
            except Exception as e:
                logger.warning(f"Copyright registration failed for {territory}: {str(e)}")
                registrations[territory] = {"status": "failed", "error": str(e)}
        
        self.metrics["copyright_registrations"] += len([r for r in registrations.values() if r.get("status") == "success"])
        
        return {
            "registrations": registrations,
            "registration_date": datetime.utcnow(),
            "status": "completed"
        }

    async def _record_on_blockchain(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Record rights on blockchain"""        blockchain_data = {
            "rights_id": rights_record.rights_id,
            "content_id": rights_record.content_id,
            "ownership_hash": await self._generate_ownership_hash(rights_record.ownerships),
            "territorial_rights": rights_record.territorial_rights,
            "timestamp": datetime.utcnow()
        }
        
        return await self.rights_blockchain.record_rights(blockchain_data)

    async def _generate_ownership_hash(self, ownerships: List[RightsOwnership]) -> str:
        """Generate cryptographic hash of ownership structure"""        ownership_data = json.dumps(
            [own.__dict__ for own in ownerships], 
            sort_keys=True, 
            default=str
        )
        import hashlib
        return hashlib.sha256(ownership_data.encode()).hexdigest()


class CopyrightProtector:
    """    Specialized copyright protection and enforcement system
    """    
    def __init__(self, rights_manager: RightsManager):
        self.rights_manager = rights_manager
        self.violation_detector = None  # Will be initialized with AI models
        self.enforcement_engine = None
        
    async def detect_copyright_violations(
        self,
        content_id: str,
        monitoring_platforms: List[str]
    ) -> Dict[str, Any]:
        """Detect copyright violations across platforms using AI-powered detection"""        try:
            violations_found = []
            platform_results = {}
            
            # Get original content fingerprint
            original_fingerprint = await self._get_content_fingerprint(content_id)
            if not original_fingerprint:
                logger.error(f"Could not generate fingerprint for content {content_id}")
                return {"success": False, "error": "Fingerprint generation failed"}
            
            # Search across each platform
            for platform in monitoring_platforms:
                try:
                    # Platform-specific violation detection
                    platform_violations = await self._detect_violations_on_platform(
                        platform, content_id, original_fingerprint
                    )
                    
                    platform_results[platform] = {
                        "violations_count": len(platform_violations),
                        "violations": platform_violations
                    }
                    
                    violations_found.extend(platform_violations)
                    
                except Exception as e:
                    logger.error(f"Error detecting violations on {platform}: {str(e)}")
                    platform_results[platform] = {"error": str(e)}
            
            # Generate violation report
            violation_report = {
                "content_id": content_id,
                "scan_timestamp": datetime.now(timezone.utc).isoformat(),
                "total_violations": len(violations_found),
                "platforms_scanned": len(monitoring_platforms),
                "platform_results": platform_results,
                "violations": violations_found,
                "severity_level": self._calculate_violation_severity(violations_found)
            }
            
            # Store violation report for future reference
            await self._store_violation_report(violation_report)
            
            return {
                "success": True,
                "violation_report": violation_report,
                "immediate_action_required": len(violations_found) > 0
            }
            
        except Exception as e:
            logger.error(f"Error in copyright violation detection: {str(e)}")
            return {"success": False, "error": str(e)}
        
    async def generate_takedown_notice(
        self,
        violation_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive DMCA takedown notice with legal compliance"""        try:
            # Validate violation details
            required_fields = ["content_id", "violation_url", "platform", "infringer_info"]
            missing_fields = [field for field in required_fields if field not in violation_details]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Get content information
            content_info = await self._get_content_details(violation_details["content_id"])
            if not content_info:
                return {"success": False, "error": "Content information not found"}
            
            # Generate unique notice ID
            notice_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)
            
            # Construct takedown notice
            takedown_notice = {
                "notice_id": notice_id,
                "generation_timestamp": timestamp.isoformat(),
                "notice_type": "DMCA_TAKEDOWN",
                "legal_basis": "Digital Millennium Copyright Act (DMCA) Section 512(c)",
                
                # Copyright owner information
                "copyright_owner": {
                    "name": content_info["owner_name"],
                    "email": content_info["owner_email"], 
                    "address": content_info.get("owner_address", ""),
                    "authorized_agent": True
                },
                
                # Original work identification
                "original_work": {
                    "title": content_info["title"],
                    "description": content_info["description"],
                    "creation_date": content_info["creation_date"],
                    "registration_number": content_info.get("copyright_registration"),
                    "original_url": content_info.get("original_url")
                },
                
                # Infringing content details
                "infringing_content": {
                    "platform": violation_details["platform"],
                    "infringing_url": violation_details["violation_url"],
                    "infringer_info": violation_details["infringer_info"],
                    "violation_type": violation_details.get("violation_type", "unauthorized_use"),
                    "evidence_urls": violation_details.get("evidence_urls", [])
                },
                
                # Legal statements
                "legal_statements": {
                    "good_faith_belief": "I have a good faith belief that use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.",
                    "accuracy_statement": "The information in this notification is accurate, and under penalty of perjury, I am authorized to act on behalf of the copyright owner.",
                    "sworn_statement": "I swear, under penalty of perjury, that the information in the notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed."
                },
                
                # Contact information for counter-notices
                "contact_info": {
                    "email": content_info["owner_email"],
                    "phone": content_info.get("owner_phone"),
                    "address": content_info.get("owner_address")
                }
            }
            
            # Generate formatted documents
            formatted_documents = await self._format_takedown_documents(takedown_notice)
            
            # Store takedown notice
            await self._store_takedown_notice(takedown_notice)
            
            return {
                "success": True,
                "notice_id": notice_id,
                "takedown_notice": takedown_notice,
                "formatted_documents": formatted_documents,
                "delivery_instructions": self._get_platform_delivery_instructions(
                    violation_details["platform"]
                )
            }
            
        except Exception as e:
            logger.error(f"Error generating takedown notice: {str(e)}")
            return {"success": False, "error": str(e)}
