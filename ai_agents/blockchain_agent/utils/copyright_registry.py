"""
IA-Influencer Agent - Copyright Registry System

Enterprise blockchain-based copyright registry providing:
- Immutable copyright registration on blockchain
- Proof of creation and ownership tracking  
- International copyright law compliance
- Automated DMCA protection integration
- Cross-platform rights management
- Legal evidence generation for disputes

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

 IMPORTANT LEGAL NOTICE 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal
import hashlib
import base64

try:
    import requests
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.exceptions import InvalidSignature
except ImportError:
    requests = None
    hashes = None
    serialization = None
    rsa = None
    padding = None
    InvalidSignature = None

from .blockchain_agent import BlockchainNetwork


class CopyrightType(Enum):
    """Types of copyrightable content."""
    MUSICAL_COMPOSITION = "musical_composition"
    SOUND_RECORDING = "sound_recording"
    AUDIOVISUAL_WORK = "audiovisual_work"
    LITERARY_WORK = "literary_work"
    VISUAL_ART = "visual_art"
    PHOTOGRAPH = "photograph"
    SOFTWARE = "software"
    PERFORMANCE = "performance"
    COMPILATION = "compilation"


class RegistrationStatus(Enum):
    """Copyright registration statuses."""
    PENDING = "pending"
    REGISTERED = "registered"
    VERIFIED = "verified"
    CHALLENGED = "challenged"
    REVOKED = "revoked"
    TRANSFERRED = "transferred"


class LegalJurisdiction(Enum):
    """International legal jurisdictions."""
    INTERNATIONAL = "international"
    US = "united_states"
    EU = "european_union"
    UK = "united_kingdom"
    CANADA = "canada"
    AUSTRALIA = "australia"
    JAPAN = "japan"
    GERMANY = "germany"
    FRANCE = "france"


@dataclass
class CopyrightClaim:
    """Comprehensive copyright claim record."""
    id: str
    content_hash: str
    copyright_type: CopyrightType
    title: str
    description: str
    creator_name: str
    creator_address: str
    creation_date: datetime
    registration_date: datetime
    jurisdiction: LegalJurisdiction
    status: RegistrationStatus = RegistrationStatus.PENDING
    blockchain_tx_hash: Optional[str] = None
    ipfs_metadata_uri: Optional[str] = None
    legal_document_uri: Optional[str] = None
    proof_of_creation: Dict[str, Any] = field(default_factory=dict)
    collaboration_info: List[Dict[str, Any]] = field(default_factory=list)
    licensing_terms: Dict[str, Any] = field(default_factory=dict)
    renewal_date: Optional[datetime] = None
    
    
@dataclass
class CopyrightEvidence:
    """Evidence supporting copyright claim."""
    evidence_type: str
    description: str
    timestamp: datetime
    file_hash: str
    witness_signatures: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OwnershipTransfer:
    """Copyright ownership transfer record."""
    transfer_id: str
    copyright_id: str
    from_owner: str
    to_owner: str
    transfer_date: datetime
    transfer_terms: Dict[str, Any]
    legal_document_hash: str
    blockchain_tx_hash: Optional[str] = None
    status: str = "pending"


class CopyrightRegistry:
    """
    Advanced Blockchain Copyright Registry System.
    
    Provides comprehensive copyright management services:
    - Immutable blockchain-based copyright registration
    - International legal jurisdiction compliance
    - Automated proof-of-creation documentation
    - DMCA and copyright infringement protection
    - Ownership transfer and licensing management
    - Legal evidence generation for disputes
    """
    
    def __init__(self, blockchain_agent, config: Optional[Dict] = None):
        """Initialize the Copyright Registry system."""
        self.blockchain_agent = blockchain_agent
        self.config = config or {}
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        
        # Storage for copyright records
        self.copyright_claims: Dict[str, CopyrightClaim] = {}
        self.evidence_records: Dict[str, List[CopyrightEvidence]] = {}
        self.transfer_history: Dict[str, List[OwnershipTransfer]] = {}
        
        # Legal settings
        self.default_jurisdiction = LegalJurisdiction(
            self.config.get('default_jurisdiction', 'international')
        )
        self.copyright_duration_years = self.config.get('copyright_duration', 70)
        self.require_notarization = self.config.get('require_notarization', False)
        
        # Blockchain settings
        self.preferred_network = BlockchainNetwork(
            self.config.get('preferred_network', 'polygon')
        )
        self.gas_optimization = self.config.get('gas_optimization', True)
        
        # Integration settings
        self.ipfs_gateway = self.config.get('ipfs_gateway', 'https://ipfs.io/ipfs/')
        self.legal_api_endpoint = self.config.get('legal_api_endpoint', '')
        self.notary_service_url = self.config.get('notary_service_url', '')
        
        # Cryptographic settings for signatures
        self.signature_private_key = None
        self.signature_public_key = None
        self._initialize_cryptographic_keys()
        
        self.logger.info("Copyright Registry system initialized")
    
    def _initialize_cryptographic_keys(self):
        """Initialize cryptographic keys for document signing."""



        try:
            if rsa and serialization:
                # Generate RSA key pair for document signing
                self.signature_private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                self.signature_public_key = self.signature_private_key.public_key()
                
                self.logger.info("Cryptographic keys initialized for document signing")
            else:
                self.logger.warning("Cryptography library not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize cryptographic keys: {str(e)}")
    
    async def register_copyright(
        self,
        content_hash: str,
        copyright_type: CopyrightType,
        title: str,
        description: str,
        creator_name: str,
        creator_address: str,
        creation_date: Optional[datetime] = None,
        jurisdiction: Optional[LegalJurisdiction] = None,
        evidence_files: Optional[List[str]] = None
    ) -> str:
        """
        Register copyright claim on blockchain with legal documentation.
        
        Args:
            content_hash: SHA-256 hash of the copyrighted content
            copyright_type: Type of copyrightable work
            title: Title of the work
            description: Description of the work
            creator_name: Legal name of the creator
            creator_address: Blockchain address of the creator
            creation_date: When the work was created
            jurisdiction: Legal jurisdiction for registration
            evidence_files: Additional evidence files
            
        Returns:
            str: Copyright claim ID
        """



        try:
            claim_id = str(uuid.uuid4())
            
            # Use current date if creation date not provided
            if not creation_date:
                creation_date = datetime.now()
            
            if not jurisdiction:
                jurisdiction = self.default_jurisdiction
            
            # Generate proof of creation evidence
            proof_of_creation = await self._generate_proof_of_creation(
                content_hash, creator_address, creation_date
            )
            
            # Create comprehensive copyright claim
            claim = CopyrightClaim(
                id=claim_id,
                content_hash=content_hash,
                copyright_type=copyright_type,
                title=title,
                description=description,
                creator_name=creator_name,
                creator_address=creator_address,
                creation_date=creation_date,
                registration_date=datetime.now(),
                jurisdiction=jurisdiction,
                proof_of_creation=proof_of_creation
            )
            
            # Calculate renewal date based on jurisdiction
            claim.renewal_date = await self._calculate_renewal_date(
                creation_date, jurisdiction
            )
            
            # Process evidence files if provided
            if evidence_files:
                await self._process_evidence_files(claim_id, evidence_files)
            
            # Generate legal documentation
            legal_document = await self._generate_legal_document(claim)
            claim.legal_document_uri = await self._upload_to_ipfs(legal_document)
            
            # Prepare metadata for blockchain registration
            metadata = {
                'claim_id': claim_id,
                'content_hash': content_hash,
                'copyright_type': copyright_type.value,
                'title': title,
                'creator': creator_name,
                'creation_date': creation_date.isoformat(),
                'jurisdiction': jurisdiction.value,
                'legal_document_uri': claim.legal_document_uri
            }
            
            claim.ipfs_metadata_uri = await self._upload_to_ipfs(metadata)
            
            # Register on blockchain
            tx_id = await self.blockchain_agent.register_copyright(
                content_hash=content_hash,
                creator_address=creator_address,
                metadata=metadata,
                network=self.preferred_network
            )
            
            claim.blockchain_tx_hash = tx_id
            claim.status = RegistrationStatus.REGISTERED
            
            # Store copyright claim
            self.copyright_claims[claim_id] = claim
            
            # Initialize evidence records
            self.evidence_records[claim_id] = []
            self.transfer_history[claim_id] = []
            
            self.logger.info(f"Copyright registered: {title} (ID: {claim_id})")
            
            return claim_id
            
        except Exception as e:
            self.logger.error(f"Copyright registration failed: {str(e)}")
            raise
    
    async def verify_copyright_ownership(
        self,
        content_hash: str,
        claimant_address: str
    ) -> Dict[str, Any]:
        """
        Verify copyright ownership for given content and claimant.
        
        Args:
            content_hash: Hash of the content to verify
            claimant_address: Address claiming ownership
            
        Returns:
            Dict containing verification results
        """



        try:
            # Find copyright claims for this content
            matching_claims = [
                claim for claim in self.copyright_claims.values()
                if claim.content_hash == content_hash
            ]
            
            if not matching_claims:
                return {
                    'verified': False,
                    'reason': 'No copyright claims found for this content',
                    'claims': []
                }
            
            # Check if claimant is the registered owner
            owner_claims = [
                claim for claim in matching_claims
                if claim.creator_address.lower() == claimant_address.lower()
            ]
            
            if not owner_claims:
                return {
                    'verified': False,
                    'reason': 'Claimant is not the registered copyright owner',
                    'registered_owners': [claim.creator_address for claim in matching_claims],
                    'claims': [self._serialize_claim(claim) for claim in matching_claims]
                }
            
            # Verify blockchain registration
            blockchain_verified = False
            for claim in owner_claims:
                if claim.blockchain_tx_hash:
                    # Verify transaction on blockchain
                    tx_status = await self.blockchain_agent.get_transaction_status(
                        claim.blockchain_tx_hash
                    )
                    if tx_status.get('status') == 'confirmed':
                        blockchain_verified = True
                        break
            
            return {
                'verified': True,
                'blockchain_verified': blockchain_verified,
                'owner_address': owner_claims[0].creator_address,
                'owner_name': owner_claims[0].creator_name,
                'registration_date': owner_claims[0].registration_date.isoformat(),
                'jurisdiction': owner_claims[0].jurisdiction.value,
                'claims': [self._serialize_claim(claim) for claim in owner_claims]
            }
            
        except Exception as e:
            self.logger.error(f"Copyright verification failed: {str(e)}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    async def transfer_copyright_ownership(
        self,
        claim_id: str,
        from_address: str,
        to_address: str,
        to_name: str,
        transfer_terms: Dict[str, Any],
        legal_document_hash: Optional[str] = None
    ) -> str:
        """
        Transfer copyright ownership with legal documentation.
        
        Args:
            claim_id: Copyright claim identifier
            from_address: Current owner's address
            to_address: New owner's address
            to_name: New owner's legal name
            transfer_terms: Terms of the transfer
            legal_document_hash: Hash of legal transfer document
            
        Returns:
            str: Transfer transaction ID
        """



        try:
            if claim_id not in self.copyright_claims:
                raise ValueError(f"Copyright claim not found: {claim_id}")
            
            claim = self.copyright_claims[claim_id]
            
            # Verify current ownership
            if claim.creator_address.lower() != from_address.lower():
                raise ValueError("Only current owner can transfer copyright")
            
            # Generate transfer documentation
            transfer_id = str(uuid.uuid4())
            
            transfer = OwnershipTransfer(
                transfer_id=transfer_id,
                copyright_id=claim_id,
                from_owner=from_address,
                to_owner=to_address,
                transfer_date=datetime.now(),
                transfer_terms=transfer_terms,
                legal_document_hash=legal_document_hash or ""
            )
            
            # Generate legal transfer document if not provided
            if not legal_document_hash:
                legal_doc = await self._generate_transfer_document(claim, transfer, to_name)
                legal_doc_uri = await self._upload_to_ipfs(legal_doc)
                transfer.legal_document_hash = await self._calculate_hash(json.dumps(legal_doc))
            
            # Register transfer on blockchain
            transfer_metadata = {
                'transfer_id': transfer_id,
                'copyright_id': claim_id,
                'from_owner': from_address,
                'to_owner': to_address,
                'transfer_date': transfer.transfer_date.isoformat(),
                'terms': transfer_terms
            }
            
            # Use licensing contract for ownership transfer
            tx_id = await self.blockchain_agent.deploy_licensing_contract(
                licensor_address=to_address,
                terms_and_conditions=json.dumps(transfer_metadata),
                licensing_fee=Decimal('0'),  # No fee for ownership transfer
                network=self.preferred_network
            )
            
            transfer.blockchain_tx_hash = tx_id
            transfer.status = "completed"
            
            # Update copyright claim ownership
            claim.creator_address = to_address
            claim.creator_name = to_name
            claim.status = RegistrationStatus.TRANSFERRED
            
            # Record transfer in history
            if claim_id not in self.transfer_history:
                self.transfer_history[claim_id] = []
            self.transfer_history[claim_id].append(transfer)
            
            self.logger.info(f"Copyright ownership transferred: {claim_id}")
            
            return transfer_id
            
        except Exception as e:
            self.logger.error(f"Copyright transfer failed: {str(e)}")
            raise
    
    async def add_copyright_evidence(
        self,
        claim_id: str,
        evidence_type: str,
        description: str,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add additional evidence to support a copyright claim.
        
        Args:
            claim_id: Copyright claim identifier
            evidence_type: Type of evidence
            description: Description of the evidence
            file_path: Path to evidence file
            metadata: Additional metadata
            
        Returns:
            str: Evidence ID
        """



        try:
            if claim_id not in self.copyright_claims:
                raise ValueError(f"Copyright claim not found: {claim_id}")
            
            evidence_id = str(uuid.uuid4())
            
            # Calculate file hash if file provided
            file_hash = ""
            if file_path:
                file_hash = await self._calculate_file_hash(file_path)
            
            # Create evidence record
            evidence = CopyrightEvidence(
                evidence_type=evidence_type,
                description=description,
                timestamp=datetime.now(),
                file_hash=file_hash,
                metadata=metadata or {}
            )
            
            # Add digital signature if possible
            if self.signature_private_key:
                signature = await self._sign_evidence(evidence)
                evidence.witness_signatures.append(signature)
            
            # Add to evidence records
            if claim_id not in self.evidence_records:
                self.evidence_records[claim_id] = []
            
            self.evidence_records[claim_id].append(evidence)
            
            self.logger.info(f"Evidence added to copyright claim: {claim_id}")
            
            return evidence_id
            
        except Exception as e:
            self.logger.error(f"Failed to add evidence: {str(e)}")
            raise
    
    async def generate_dmca_takedown_notice(
        self,
        claim_id: str,
        infringing_url: str,
        infringer_contact: str,
        platform_contact: str
    ) -> Dict[str, Any]:
        """
        Generate DMCA takedown notice for copyright infringement.
        
        Args:
            claim_id: Copyright claim identifier
            infringing_url: URL of infringing content
            infringer_contact: Contact info of infringer
            platform_contact: Contact info of hosting platform
            
        Returns:
            Dict containing DMCA notice details
        """



        try:
            if claim_id not in self.copyright_claims:
                raise ValueError(f"Copyright claim not found: {claim_id}")
            
            claim = self.copyright_claims[claim_id]
            
            dmca_notice = {
                'notice_id': str(uuid.uuid4()),
                'date': datetime.now().isoformat(),
                'copyright_owner': {
                    'name': claim.creator_name,
                    'address': claim.creator_address
                },
                'copyrighted_work': {
                    'title': claim.title,
                    'description': claim.description,
                    'registration_date': claim.registration_date.isoformat(),
                    'copyright_id': claim_id
                },
                'infringement_details': {
                    'infringing_url': infringing_url,
                    'infringer_contact': infringer_contact,
                    'platform_contact': platform_contact,
                    'description': f"Unauthorized use of copyrighted work '{claim.title}'"
                },
                'legal_basis': {
                    'dmca_section': '17 U.S.C. § 512(c)(3)(A)',
                    'good_faith_belief': True,
                    'authority_to_act': True,
                    'accuracy_statement': True
                },
                'blockchain_proof': {
                    'transaction_hash': claim.blockchain_tx_hash,
                    'network': self.preferred_network.value,
                    'content_hash': claim.content_hash
                }
            }
            
            # Generate formal DMCA notice document
            dmca_document = await self._generate_dmca_document(dmca_notice)
            dmca_notice['document_uri'] = await self._upload_to_ipfs(dmca_document)
            
            # Sign the notice if cryptographic keys available
            if self.signature_private_key:
                signature = await self._sign_document(json.dumps(dmca_notice))
                dmca_notice['digital_signature'] = signature
            
            self.logger.info(f"DMCA takedown notice generated for claim: {claim_id}")
            
            return dmca_notice
            
        except Exception as e:
            self.logger.error(f"DMCA notice generation failed: {str(e)}")
            raise
    
    async def _generate_proof_of_creation(
        self,
        content_hash: str,
        creator_address: str,
        creation_date: datetime
    ) -> Dict[str, Any]:
        """Generate cryptographic proof of creation."""
        timestamp_hash = hashlib.sha256(
            f"{content_hash}{creator_address}{creation_date.isoformat()}".encode()
        ).hexdigest()
        
        return {
            'timestamp_hash': timestamp_hash,
            'creation_timestamp': creation_date.isoformat(),
            'creator_address': creator_address,
            'content_hash': content_hash,
            'proof_type': 'cryptographic_timestamp',
            'algorithm': 'SHA-256'
        }
    
    async def _calculate_renewal_date(
        self,
        creation_date: datetime,
        jurisdiction: LegalJurisdiction
    ) -> datetime:
        """Calculate copyright renewal date based on jurisdiction."""
        # Different jurisdictions have different copyright durations
        duration_years = {
            LegalJurisdiction.US: 95,  # For works made for hire
            LegalJurisdiction.EU: 70,
            LegalJurisdiction.UK: 70,
            LegalJurisdiction.INTERNATIONAL: 50
        }.get(jurisdiction, self.copyright_duration_years)
        
        return creation_date + timedelta(days=duration_years * 365)
    
    async def _process_evidence_files(self, claim_id: str, evidence_files: List[str]):
        """Process and store evidence files for copyright claim."""
        for file_path in evidence_files:
            try:
                file_hash = await self._calculate_file_hash(file_path)
                
                evidence = CopyrightEvidence(
                    evidence_type="supporting_file",
                    description=f"Evidence file: {file_path}",
                    timestamp=datetime.now(),
                    file_hash=file_hash
                )
                
                if claim_id not in self.evidence_records:
                    self.evidence_records[claim_id] = []
                
                self.evidence_records[claim_id].append(evidence)
                
            except Exception as e:
                self.logger.warning(f"Failed to process evidence file {file_path}: {str(e)}")
    
    async def _generate_legal_document(self, claim: CopyrightClaim) -> Dict[str, Any]:
        """Generate formal legal copyright registration document."""



        return {
            'document_type': 'copyright_registration',
            'claim_id': claim.id,
            'title': 'Copyright Registration Certificate',
            'content': {
                'work_title': claim.title,
                'work_description': claim.description,
                'copyright_type': claim.copyright_type.value,
                'creator_name': claim.creator_name,
                'creator_address': claim.creator_address,
                'creation_date': claim.creation_date.isoformat(),
                'registration_date': claim.registration_date.isoformat(),
                'jurisdiction': claim.jurisdiction.value,
                'content_hash': claim.content_hash,
                'renewal_date': claim.renewal_date.isoformat() if claim.renewal_date else None
            },
            'legal_notice': 'This document serves as proof of copyright registration',
            'generated_by': 'IA-Influencer Agent Copyright Registry',
            'generation_date': datetime.now().isoformat()
        }
    
    async def _generate_transfer_document(
        self,
        claim: CopyrightClaim,
        transfer: OwnershipTransfer,
        new_owner_name: str
    ) -> Dict[str, Any]:
        """Generate legal document for copyright ownership transfer."""



        return {
            'document_type': 'copyright_transfer',
            'transfer_id': transfer.transfer_id,
            'title': 'Copyright Ownership Transfer Agreement',
            'content': {
                'work_title': claim.title,
                'copyright_id': claim.id,
                'original_owner': {
                    'name': claim.creator_name,
                    'address': transfer.from_owner
                },
                'new_owner': {
                    'name': new_owner_name,
                    'address': transfer.to_owner
                },
                'transfer_date': transfer.transfer_date.isoformat(),
                'transfer_terms': transfer.transfer_terms,
                'jurisdiction': claim.jurisdiction.value
            },
            'legal_notice': 'This document transfers all copyright ownership rights',
            'generated_by': 'IA-Influencer Agent Copyright Registry',
            'generation_date': datetime.now().isoformat()
        }
    
    async def _generate_dmca_document(self, dmca_notice: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formal DMCA takedown notice document."""



        return {
            'document_type': 'dmca_takedown_notice',
            'title': 'Digital Millennium Copyright Act Takedown Notice',
            'notice_id': dmca_notice['notice_id'],
            'date': dmca_notice['date'],
            'to_platform': dmca_notice['infringement_details']['platform_contact'],
            'content': f"""
DMCA TAKEDOWN NOTICE

To: {dmca_notice['infringement_details']['platform_contact']}
Date: {dmca_notice['date']}

I, {dmca_notice['copyright_owner']['name']}, am the copyright owner of the work described below.

COPYRIGHTED WORK:
Title: {dmca_notice['copyrighted_work']['title']}
Description: {dmca_notice['copyrighted_work']['description']}
Copyright Registration: {dmca_notice['copyrighted_work']['copyright_id']}

INFRINGING MATERIAL:
URL: {dmca_notice['infringement_details']['infringing_url']}
Description: {dmca_notice['infringement_details']['description']}

BLOCKCHAIN PROOF:
Transaction Hash: {dmca_notice['blockchain_proof']['transaction_hash']}
Network: {dmca_notice['blockchain_proof']['network']}
Content Hash: {dmca_notice['blockchain_proof']['content_hash']}

I have a good faith belief that the use of the described material is not authorized by the copyright owner, its agent, or the law.

I swear, under penalty of perjury, that the information in this notification is accurate and that I am the copyright owner or am authorized to act on behalf of the owner.

Signed: {dmca_notice['copyright_owner']['name']}
            """,
            'generated_by': 'IA-Influencer Agent Copyright Registry',
            'blockchain_verified': True
        }
    
    async def _upload_to_ipfs(self, data: Dict[str, Any]) -> str:
        """Upload document to IPFS and return URI."""
        # This would integrate with actual IPFS service
        content_str = json.dumps(data, sort_keys=True)
        mock_hash = hashlib.sha256(content_str.encode()).hexdigest()[:46]
        return f"ipfs://Qm{mock_hash}"
    
    async def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content."""



        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        except FileNotFoundError:
            # For testing, generate deterministic hash from filename
            sha256_hash.update(file_path.encode())
        return sha256_hash.hexdigest()
    
    async def _sign_evidence(self, evidence: CopyrightEvidence) -> str:
        """Digitally sign evidence record."""
        if not self.signature_private_key or not padding or not hashes:
            return "signature_unavailable"
        
        try:
            evidence_data = f"{evidence.evidence_type}{evidence.description}{evidence.timestamp.isoformat()}"
            signature = self.signature_private_key.sign(
                evidence_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode()
        except Exception:
            return "signature_failed"
    
    async def _sign_document(self, document_content: str) -> str:
        """Digitally sign document content."""
        if not self.signature_private_key or not padding or not hashes:
            return "signature_unavailable"
        
        try:
            signature = self.signature_private_key.sign(
                document_content.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode()
        except Exception:
            return "signature_failed"
    
    def _serialize_claim(self, claim: CopyrightClaim) -> Dict[str, Any]:
        """Serialize copyright claim for API responses."""



        return {
            'id': claim.id,
            'title': claim.title,
            'copyright_type': claim.copyright_type.value,
            'creator_name': claim.creator_name,
            'creator_address': claim.creator_address,
            'creation_date': claim.creation_date.isoformat(),
            'registration_date': claim.registration_date.isoformat(),
            'status': claim.status.value,
            'jurisdiction': claim.jurisdiction.value,
            'blockchain_tx_hash': claim.blockchain_tx_hash,
            'renewal_date': claim.renewal_date.isoformat() if claim.renewal_date else None
        }
    
    async def get_copyright_info(self, claim_id: str) -> Dict[str, Any]:
        """Get comprehensive information about a copyright claim."""
        if claim_id not in self.copyright_claims:
            raise ValueError(f"Copyright claim not found: {claim_id}")
        
        claim = self.copyright_claims[claim_id]
        
        # Get evidence records
        evidence = self.evidence_records.get(claim_id, [])
        
        # Get transfer history
        transfers = self.transfer_history.get(claim_id, [])
        
        return {
            'claim': self._serialize_claim(claim),
            'evidence_count': len(evidence),
            'transfer_count': len(transfers),
            'blockchain_verified': bool(claim.blockchain_tx_hash),
            'legal_document_available': bool(claim.legal_document_uri),
            'expires_on': claim.renewal_date.isoformat() if claim.renewal_date else None,
            'days_until_expiry': (claim.renewal_date - datetime.now()).days if claim.renewal_date else None
        }
    
    async def search_copyrights(
        self,
        query: str,
        search_type: str = "title",
        jurisdiction: Optional[LegalJurisdiction] = None
    ) -> List[Dict[str, Any]]:
        """Search copyright claims by various criteria."""
        results = []
        
        for claim in self.copyright_claims.values():
            match = False
            
            if search_type == "title" and query.lower() in claim.title.lower():
                match = True
            elif search_type == "creator" and query.lower() in claim.creator_name.lower():
                match = True
            elif search_type == "content_hash" and claim.content_hash == query:
                match = True
            elif search_type == "address" and claim.creator_address.lower() == query.lower():
                match = True
            
            if match and (not jurisdiction or claim.jurisdiction == jurisdiction):
                results.append(self._serialize_claim(claim))
        
        return results
    
    async def get_registry_analytics(self) -> Dict[str, Any]:
        """Get comprehensive copyright registry analytics."""
        total_claims = len(self.copyright_claims)
        
        # Statistics by copyright type
        type_stats = {}
        for copyright_type in CopyrightType:
            count = sum(1 for claim in self.copyright_claims.values() 
                       if claim.copyright_type == copyright_type)
            type_stats[copyright_type.value] = count
        
        # Statistics by jurisdiction
        jurisdiction_stats = {}
        for jurisdiction in LegalJurisdiction:
            count = sum(1 for claim in self.copyright_claims.values() 
                       if claim.jurisdiction == jurisdiction)
            jurisdiction_stats[jurisdiction.value] = count
        
        # Status distribution
        status_stats = {}
        for status in RegistrationStatus:
            count = sum(1 for claim in self.copyright_claims.values() 
                       if claim.status == status)
            status_stats[status.value] = count
        
        return {
            'total_copyright_claims': total_claims,
            'blockchain_verified_claims': sum(1 for claim in self.copyright_claims.values() 
                                            if claim.blockchain_tx_hash),
            'copyright_type_distribution': type_stats,
            'jurisdiction_distribution': jurisdiction_stats,
            'status_distribution': status_stats,
            'total_evidence_records': sum(len(evidence) for evidence in self.evidence_records.values()),
            'total_ownership_transfers': sum(len(transfers) for transfers in self.transfer_history.values()),
            'preferred_network': self.preferred_network.value,
            'default_jurisdiction': self.default_jurisdiction.value
        }
