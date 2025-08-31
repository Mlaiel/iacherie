"""Blockchain-based Digital Rights Registry Module

Enterprise-grade copyright and intellectual property registry using blockchain
technology for immutable proof of ownership and creation timestamps.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from datetime import datetime
import hashlib
import uuid

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger(__name__)

class RightsType(Enum):
    """Types of digital rights that can be registered."""    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    TRADE_SECRET = "trade_secret"
    PUBLICITY_RIGHTS = "publicity_rights"
    MORAL_RIGHTS = "moral_rights"

class ContentCategory(Enum):
    """Categories of content for rights registration."""    MUSICAL_WORK = "musical_work"
    SOUND_RECORDING = "sound_recording"
    AUDIOVISUAL_WORK = "audiovisual_work"
    LITERARY_WORK = "literary_work"
    VISUAL_ART = "visual_art"
    PHOTOGRAPH = "photograph"
    SOFTWARE = "software"
    PERFORMANCE = "performance"

class RightsStatus(Enum):
    """Status of rights registration."""    PENDING = "pending"
    REGISTERED = "registered"
    DISPUTED = "disputed"
    EXPIRED = "expired"
    TRANSFERRED = "transferred"
    REVOKED = "revoked"

@dataclass
class CreatorInfo:
    """Information about the content creator."""    name: str
    wallet_address: str
    email: Optional[str] = None
    website: Optional[str] = None
    social_media: Optional[Dict[str, str]] = None
    legal_name: Optional[str] = None
    business_entity: Optional[str] = None
    country: Optional[str] = None

@dataclass
class RightsRegistration:
    """Complete rights registration record."""    registration_id: str
    content_hash: str
    content_fingerprint: str
    rights_type: RightsType
    content_category: ContentCategory
    title: str
    description: str
    creator: CreatorInfo
    creation_date: datetime
    registration_date: datetime
    expiration_date: Optional[datetime]
    status: RightsStatus
    blockchain_transaction: str
    block_number: int
    metadata: Dict[str, Any]
    evidence_hashes: List[str]
    prior_registrations: List[str]
    licensing_terms: Optional[Dict[str, Any]] = None

@dataclass
class RightsTransfer:
    """Rights transfer record."""    transfer_id: str
    registration_id: str
    from_owner: str
    to_owner: str
    transfer_type: str  # "sale", "license", "assignment", "inheritance"
    transfer_date: datetime
    consideration: Optional[str]  # Payment or other consideration
    terms: Dict[str, Any]
    blockchain_transaction: str
    is_exclusive: bool

class DigitalSignatureManager:
    """Manager for digital signatures and cryptographic operations."""    
    def __init__(self):
        """Initialize digital signature manager."""        self.key_pairs = {}
        
    def generate_key_pair(self, creator_id: str) -> Dict[str, bytes]:
        """        Generate RSA key pair for a creator.
        
        Args:
            creator_id: Unique identifier for the creator
            
        Returns:
            Dictionary with public and private key bytes
        """        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            self.key_pairs[creator_id] = {
                "private": private_pem,
                "public": public_pem
            }
            
            return {
                "private": private_pem,
                "public": public_pem
            }
            
        except Exception as e:
            logger.error(f"Key pair generation failed: {e}")
            raise
            
    def sign_content(self, creator_id: str, content_hash: str) -> bytes:
        """        Sign content hash with creator's private key.
        
        Args:
            creator_id: Identifier for the creator
            content_hash: Hash of the content to sign
            
        Returns:
            Digital signature bytes
        """        try:
            if creator_id not in self.key_pairs:
                raise ValueError(f"No key pair found for creator {creator_id}")
                
            private_key_pem = self.key_pairs[creator_id]["private"]
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )
            
            signature = private_key.sign(
                content_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return signature
            
        except Exception as e:
            logger.error(f"Content signing failed: {e}")
            raise
            
    def verify_signature(self, public_key_pem: bytes, content_hash: str, signature: bytes) -> bool:
        """        Verify digital signature.
        
        Args:
            public_key_pem: Public key in PEM format
            content_hash: Original content hash
            signature: Digital signature to verify
            
        Returns:
            True if signature is valid
        """        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            
            public_key.verify(
                signature,
                content_hash.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception:
            return False

class CopyrightRegistry:
    """    Blockchain-based copyright and digital rights registry.
    
    Provides immutable registration of digital content ownership,
    creation timestamps, and rights management.
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize the copyright registry.
        
        Args:
            config: Configuration including blockchain settings
        """        self.config = config
        self.signature_manager = DigitalSignatureManager()
        self.registrations = {}  # In production, this would be blockchain storage
        
    async def register_rights(
        self,
        content_hash: str,
        content_fingerprint: str,
        rights_type: RightsType,
        content_category: ContentCategory,
        title: str,
        description: str,
        creator: CreatorInfo,
        metadata: Optional[Dict[str, Any]] = None,
        evidence_files: Optional[List[str]] = None
    ) -> RightsRegistration:
        """        Register digital rights on the blockchain.
        
        Args:
            content_hash: Unique hash of the content
            content_fingerprint: AI-generated fingerprint
            rights_type: Type of rights being registered
            content_category: Category of the content
            title: Title of the work
            description: Description of the work
            creator: Creator information
            metadata: Additional metadata
            evidence_files: List of evidence file hashes
            
        Returns:
            Rights registration record
        """        try:
            logger.info(f"Registering rights for content: {content_hash}")
            
            # Generate registration ID
            registration_id = str(uuid.uuid4())
            
            # Create timestamp
            now = datetime.utcnow()
            
            # Calculate expiration date based on rights type and jurisdiction
            expiration_date = self._calculate_expiration_date(rights_type, now)
            
            # Generate digital signature for authenticity
            signature = self.signature_manager.sign_content(
                creator.wallet_address,
                content_hash
            )
            
            # Prepare blockchain transaction
            tx_result = await self._submit_to_blockchain(
                registration_id,
                content_hash,
                creator.wallet_address,
                rights_type,
                signature
            )
            
            # Create registration record
            registration = RightsRegistration(
                registration_id=registration_id,
                content_hash=content_hash,
                content_fingerprint=content_fingerprint,
                rights_type=rights_type,
                content_category=content_category,
                title=title,
                description=description,
                creator=creator,
                creation_date=now,  # In practice, this might be provided
                registration_date=now,
                expiration_date=expiration_date,
                status=RightsStatus.REGISTERED,
                blockchain_transaction=tx_result["transaction_hash"],
                block_number=tx_result["block_number"],
                metadata=metadata or {},
                evidence_hashes=evidence_files or [],
                prior_registrations=[],
                licensing_terms=None
            )
            
            # Store registration
            self.registrations[registration_id] = registration
            
            logger.info(f"Rights registered successfully: {registration_id}")
            return registration
            
        except Exception as e:
            logger.error(f"Rights registration failed: {e}")
            raise
            
    def _calculate_expiration_date(self, rights_type: RightsType, creation_date: datetime) -> Optional[datetime]:
        """Calculate expiration date based on rights type and jurisdiction."""        # Copyright terms vary by jurisdiction
        # This is a simplified implementation
        if rights_type == RightsType.COPYRIGHT:
            # Typical copyright term: life + 70 years, but we'll use a fixed term for simplicity
            return datetime(creation_date.year + 70, creation_date.month, creation_date.day)
        elif rights_type == RightsType.TRADEMARK:
            # Trademarks can be renewed indefinitely
            return None
        elif rights_type == RightsType.PATENT:
            # Typical patent term: 20 years
            return datetime(creation_date.year + 20, creation_date.month, creation_date.day)
        else:
            return None

    async def _submit_to_blockchain(
        self,
        registration_id: str,
        content_hash: str,
        creator_address: str,
        rights_type: RightsType,
        signature: bytes
    ) -> Dict[str, Any]:
        """Submit rights registration to blockchain."""        try:
            # Import here to avoid circular imports
            from .contracts import SmartContractManager, ContractType
            
            contract_manager = SmartContractManager(self.config)
            
            # Get copyright registry contract
            network = self.config.get("default_network", "polygon_mumbai")
            contract_key = f"{ContractType.COPYRIGHT_REGISTRY.value}_{network}"
            
            # Prepare registration data
            registration_args = [
                registration_id,
                content_hash,
                creator_address,
                rights_type.value,
                signature.hex()
            ]
            
            # Submit to blockchain
            result = await contract_manager.interact_with_contract(
                contract_key=contract_key,
                function_name="registerRights",
                args=registration_args
            )
            
            return {
                "transaction_hash": result["transaction_hash"],
                "block_number": result["block_number"],
                "gas_used": result["gas_used"]
            }
            
        except Exception as e:
            logger.error(f"Blockchain submission failed: {e}")
            raise

    def verify_rights(self, content_hash: str) -> Optional[RightsRegistration]:
        """        Verify rights registration for content.
        
        Args:
            content_hash: Hash of the content to verify
            
        Returns:
            Rights registration if found, None otherwise
        """        try:
            # Search for registration by content hash
            for registration in self.registrations.values():
                if registration.content_hash == content_hash:
                    return registration
                    
            # In production, this would query the blockchain
            return None
            
        except Exception as e:
            logger.error(f"Rights verification failed: {e}")
            return None

    async def transfer_rights(
        self,
        registration_id: str,
        from_owner: str,
        to_owner: str,
        transfer_type: str,
        terms: Dict[str, Any],
        consideration: Optional[str] = None
    ) -> RightsTransfer:
        """        Transfer rights to another party.
        
        Args:
            registration_id: ID of the rights registration
            from_owner: Current owner's address
            to_owner: New owner's address
            transfer_type: Type of transfer (sale, license, etc.)
            terms: Terms of the transfer
            consideration: Payment or other consideration
            
        Returns:
            Rights transfer record
        """        try:
            registration = self.registrations.get(registration_id)
            if not registration:
                raise ValueError(f"Registration {registration_id} not found")
                
            if registration.creator.wallet_address != from_owner:
                raise ValueError("Only the owner can transfer rights")
                
            # Generate transfer ID
            transfer_id = str(uuid.uuid4())
            
            # Submit transfer to blockchain
            tx_result = await self._submit_transfer_to_blockchain(
                transfer_id,
                registration_id,
                from_owner,
                to_owner,
                transfer_type
            )
            
            # Create transfer record
            transfer = RightsTransfer(
                transfer_id=transfer_id,
                registration_id=registration_id,
                from_owner=from_owner,
                to_owner=to_owner,
                transfer_type=transfer_type,
                transfer_date=datetime.utcnow(),
                consideration=consideration,
                terms=terms,
                blockchain_transaction=tx_result["transaction_hash"],
                is_exclusive=(transfer_type in ["sale", "assignment"])
            )
            
            # Update registration if exclusive transfer
            if transfer.is_exclusive:
                registration.creator.wallet_address = to_owner
                registration.status = RightsStatus.TRANSFERRED
                
            logger.info(f"Rights transferred: {transfer_id}")
            return transfer
            
        except Exception as e:
            logger.error(f"Rights transfer failed: {e}")
            raise

    async def _submit_transfer_to_blockchain(
        self,
        transfer_id: str,
        registration_id: str,
        from_owner: str,
        to_owner: str,
        transfer_type: str
    ) -> Dict[str, Any]:
        """Submit rights transfer to blockchain."""        try:
            from .contracts import SmartContractManager, ContractType
            
            contract_manager = SmartContractManager(self.config)
            
            network = self.config.get("default_network", "polygon_mumbai")
            contract_key = f"{ContractType.COPYRIGHT_REGISTRY.value}_{network}"
            
            transfer_args = [
                transfer_id,
                registration_id,
                from_owner,
                to_owner,
                transfer_type
            ]
            
            result = await contract_manager.interact_with_contract(
                contract_key=contract_key,
                function_name="transferRights",
                args=transfer_args
            )
            
            return {
                "transaction_hash": result["transaction_hash"],
                "block_number": result["block_number"],
                "gas_used": result["gas_used"]
            }
            
        except Exception as e:
            logger.error(f"Transfer blockchain submission failed: {e}")
            raise

    def search_registrations(
        self,
        creator_address: Optional[str] = None,
        content_category: Optional[ContentCategory] = None,
        rights_type: Optional[RightsType] = None,
        status: Optional[RightsStatus] = None
    ) -> List[RightsRegistration]:
        """        Search rights registrations by criteria.
        
        Args:
            creator_address: Filter by creator address
            content_category: Filter by content category
            rights_type: Filter by rights type
            status: Filter by registration status
            
        Returns:
            List of matching registrations
        """        try:
            results = []
            
            for registration in self.registrations.values():
                if creator_address and registration.creator.wallet_address != creator_address:
                    continue
                if content_category and registration.content_category != content_category:
                    continue
                if rights_type and registration.rights_type != rights_type:
                    continue
                if status and registration.status != status:
                    continue
                    
                results.append(registration)
                
            return results
            
        except Exception as e:
            logger.error(f"Registration search failed: {e}")
            return []

    def get_registration_by_id(self, registration_id: str) -> Optional[RightsRegistration]:
        """Get registration by ID."""        return self.registrations.get(registration_id)

    def dispute_registration(
        self,
        registration_id: str,
        disputant_address: str,
        evidence: Dict[str, Any]
    ) -> str:
        """        Initiate a dispute over a rights registration.
        
        Args:
            registration_id: ID of the registration to dispute
            disputant_address: Address of the party filing the dispute
            evidence: Evidence supporting the dispute
            
        Returns:
            Dispute ID
        """        try:
            registration = self.registrations.get(registration_id)
            if not registration:
                raise ValueError(f"Registration {registration_id} not found")
                
            # Update registration status
            registration.status = RightsStatus.DISPUTED
            
            # Generate dispute ID
            dispute_id = str(uuid.uuid4())
            
            logger.info(f"Dispute initiated: {dispute_id} for registration {registration_id}")
            return dispute_id
            
        except Exception as e:
            logger.error(f"Dispute initiation failed: {e}")
            raise

# Initialize module exports
__all__ = [
    "CopyrightRegistry",
    "DigitalSignatureManager", 
    "RightsType",
    "ContentCategory",
    "RightsStatus",
    "CreatorInfo",
    "RightsRegistration",
    "RightsTransfer"
]
